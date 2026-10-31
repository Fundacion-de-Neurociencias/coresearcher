"""
python/discovery/fidelity_service.py - Statement fidelity as a service (ADR-DISCOVERY-080, on ADR-070 and ADR-068).

Two checks of ADR-070, packaged as sealed reports with the status, relays and provenance of ADR-068, so the API
(`POST /api/fidelity/compare`, `POST /api/fidelity/lean-lint`), the two-phase CLI (`coresearcher formal fidelity`,
`coresearcher formal lean-lint`, then `coresearcher formal analyze`) and the trust ladder share one computation:

- `compare(spec)`: the paper range against the formal range of one theorem, decided by z3. The relation is the
  strength of the formal statement: EQUIVALENT, STRONGER, WEAKER or INCOMPARABLE, each non-empty difference with a
  witness; UNDECIDED is a non-verdict (formal_status UNDECIDED), never a relation.
- `lean_lint(source)`: every junk-value site in a Lean statement file, DISCHARGED (with the text that discharges it)
  or OPEN (a human decides).

Both are deterministic: the same request gives the same `output_sha256` under the same thresholds.
"""

from __future__ import annotations

import contextlib
import threading
from typing import Any, Dict, Iterator, List, Optional, Sequence

from python.discovery import formal_provenance, formal_status, formal_thresholds
from python.discovery.formal_hypothesis import FormalHypothesisError
from python.discovery.formal_status import FormalStatus

MAX_LEAN_SOURCE_CHARS = 400_000
_Z3_LOCK = threading.RLock()


@contextlib.contextmanager
def _fresh_z3_context() -> Iterator[None]:
    """Runs a decision in a fresh z3 main context, one at a time.

    z3 picks a model by its internal term order, which depends on every query made earlier in the process. A witness
    must not depend on that history, or the same request would get a different `output_sha256` (ADR-068). Expressions
    made before the reset keep their own context; nothing made inside is used after it.
    """
    import z3

    with _Z3_LOCK:
        z3.z3._main_ctx = None  # main_ctx() builds a new context on its next call.
        yield


def _number_or_none(value: Any, what: str) -> Optional[float]:
    if value is None:
        return None
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise FormalHypothesisError(f"{what} must be a number or null.")
    return value


def spec_from_dict(data: Dict[str, Any]):
    """A `statement_fidelity.RangeSpec` from its JSON form (the API schema and the CLI spec file share it)."""
    from python.discovery.statement_fidelity import Parameter, Quantity, RangeSpec

    if not isinstance(data, dict):
        raise FormalHypothesisError("A fidelity spec must be a JSON object.")
    for key in ("theorem", "paper", "lean"):
        if not isinstance(data.get(key), str) or not data[key].strip():
            raise FormalHypothesisError(f"A fidelity spec needs a non-empty string {key!r}.")
    raw = data.get("parameters")
    if not isinstance(raw, list) or not raw:
        raise FormalHypothesisError("'parameters' must be a non-empty list.")
    parameters = []
    for p in raw:
        if not isinstance(p, dict) or not isinstance(p.get("name"), str) or not p["name"].isidentifier():
            raise FormalHypothesisError("Each parameter needs a 'name' that is a valid identifier.")
        parameters.append(
            Parameter(
                p["name"],
                integer=bool(p.get("integer", False)),
                lower=_number_or_none(p.get("lower"), f"lower bound of {p['name']!r}"),
                upper=_number_or_none(p.get("upper"), f"upper bound of {p['name']!r}"),
            )
        )
    if len({p.name for p in parameters}) != len(parameters):
        raise FormalHypothesisError("Parameter names must be unique.")
    quantities = []
    for q in data.get("quantities") or []:
        if not isinstance(q, dict) or not all(isinstance(q.get(k), str) for k in ("name", "paper", "lean")):
            raise FormalHypothesisError("Each quantity needs string 'name', 'paper' and 'lean'.")
        quantities.append(Quantity(q["name"], q["paper"], q["lean"]))
    encoding = data.get("encoding") or []
    if not isinstance(encoding, list) or not all(isinstance(e, str) for e in encoding):
        raise FormalHypothesisError("'encoding' must be a list of strings.")
    return RangeSpec(
        theorem=data["theorem"],
        parameters=parameters,
        paper=data["paper"],
        lean=data["lean"],
        domain=str(data.get("domain") or "True"),
        paper_source=str(data.get("paper_source") or ""),
        lean_source=str(data.get("lean_source") or ""),
        encoding=list(encoding),
        quantities=quantities,
    )


def spec_to_dict(spec) -> Dict[str, Any]:
    return {
        "theorem": spec.theorem,
        "parameters": [
            {"name": p.name, "integer": p.integer, "lower": p.lower, "upper": p.upper} for p in spec.parameters
        ],
        "paper": spec.paper,
        "lean": spec.lean,
        "domain": spec.domain,
        "paper_source": spec.paper_source,
        "lean_source": spec.lean_source,
        "encoding": list(spec.encoding),
        "quantities": [{"name": q.name, "paper": q.paper, "lean": q.lean} for q in spec.quantities],
    }


def _relay_codes(*codes: str) -> List[str]:
    out = list(codes)
    if any(src != "default" for src in formal_thresholds.active().sources().values()):
        out.append("THRESHOLDS_OVERRIDDEN")
    return out


def compare(spec_data: Dict[str, Any], integer_values: Optional[Dict[str, Sequence[int]]] = None) -> Dict[str, Any]:
    """Paper range vs formal range: the sealed fidelity report.

    `integer_values` (optional) also re-decides the question through `HypothesisEvaluator.compare` with the integer
    parameters fixed to those values (`cross_check`); agreement is evidence for the encoding, nothing more.
    Raises FormalHypothesisError for a malformed spec.
    """
    from python.discovery import statement_fidelity

    spec = spec_from_dict(spec_data)
    if integer_values:
        missing = [p.name for p in spec.parameters if p.integer and p.name not in integer_values]
        if missing:
            raise FormalHypothesisError(f"integer_values must give values for every integer parameter: {missing}.")
    try:
        with _fresh_z3_context():
            result = statement_fidelity.compare_ranges(spec)
            body = result.to_dict()
            if integer_values:
                body["cross_check"] = statement_fidelity.cross_check(spec, integer_values)
    except SyntaxError as exc:
        raise FormalHypothesisError(f"A range is not a valid predicate: {exc.msg}") from exc
    undecided = result.relation == statement_fidelity.Fidelity.UNDECIDED
    status = FormalStatus.UNDECIDED if undecided else FormalStatus.DECIDED
    inputs = {"spec": spec_to_dict(spec)}
    if integer_values:
        inputs["integer_values"] = {k: list(v) for k, v in integer_values.items()}
    return {
        **body,
        "formal_status": status.value,
        "mandatory_relays": formal_status.relays(_relay_codes("FORMAL_NOT_EMPIRICAL", "FIDELITY_RANGE_ONLY")),
        "provenance": formal_provenance.build("fidelity_compare", inputs, body, "smt"),
    }


def _reviews(raw: Any) -> Dict[tuple, str]:
    if raw is None:
        return {}
    if not isinstance(raw, list):
        raise FormalHypothesisError("'reviews' must be a list of {theorem, kind, line, note}.")
    out = {}
    for r in raw:
        if not (
            isinstance(r, dict)
            and isinstance(r.get("theorem"), str)
            and isinstance(r.get("kind"), str)
            and isinstance(r.get("line"), int)
            and isinstance(r.get("note"), str)
        ):
            raise FormalHypothesisError("Each review needs string 'theorem', 'kind', 'note' and an integer 'line'.")
        out[(r["theorem"], r["kind"], r["line"])] = r["note"]
    return out


def lean_lint(source: str, file: str = "<string>", reviews: Optional[List[Dict[str, Any]]] = None) -> Dict[str, Any]:
    """Junk-value findings of a Lean statement file, each DISCHARGED or OPEN: the sealed lint report."""
    from python.discovery import formal_trust
    from python.discovery.lean_junk_lint import lint

    if not isinstance(source, str) or not source.strip():
        raise FormalHypothesisError("The Lean source is empty.")
    if len(source) > MAX_LEAN_SOURCE_CHARS:
        raise FormalHypothesisError(f"The Lean source exceeds {MAX_LEAN_SOURCE_CHARS} characters.")
    report = lint(source, file=file, reviews=_reviews(reviews))
    body = {
        **report.to_dict(),
        "statement_sha256": formal_trust.statement_sha256(source),
        "theorems": sorted({f.theorem for f in report.findings}),
        "discharged": sum(1 for f in report.findings if f.status == "DISCHARGED"),
    }
    inputs = {"source": source, "file": file, "reviews": list(reviews or [])}
    return {
        **body,
        "formal_status": FormalStatus.DECIDED.value,
        "mandatory_relays": formal_status.relays(_relay_codes("LINT_IS_SYNTACTIC", "LEAN_NOT_KERNEL_CHECKED")),
        "provenance": formal_provenance.build("lean_lint", inputs, body, None),
    }
