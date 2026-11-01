"""
python/discovery/formal_pipeline.py - The formal pipeline as one reproducible computation (ADR-DISCOVERY-068).

`compute(request, ...)` is the whole formal layer behind `coresearcher formal run` and `coresearcher formal analyze`:

    prose -> formalizer samples -> self-consistency gate -> accepted formal object      (only when prose is given)
    formal object -> evaluation, comparison with each rival, entailment of each consequence, optional Lean statement

Phase 1 (`run`) calls it with live formalizer clients. Phase 2 (`analyze`) calls it with the raw model outputs stored by
phase 1 and no clients, so it never reaches a model or the network, and must reproduce phase 1's verdict exactly: the
same code computes both.

Every non-verdict becomes a `formal_status` (formal_status.FormalStatus) with a reason, never a verdict: a solver
timeout is UNDECIDED, a missing model or threshold is BLOCKED, a malformed object is INVALID_INPUT, a disagreeing
formalizer is FORMALIZATION_AMBIGUOUS.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from python.discovery import formal_status
from python.discovery.formal_hypothesis import FormalHypothesisError, HypothesisEvaluator, hypothesis_from_dict
from python.discovery.formal_status import CapabilityUnavailable, FormalStatus

REQUEST_SCHEMA = "coresearcher.formal.request/v1"
RESPONSE_SCHEMA = "coresearcher.formal.response/v1"


def make_request(
    hypothesis: Optional[Dict[str, Any]] = None,
    prose: Optional[str] = None,
    hypothesis_id: str = "H",
    variable_schema: Optional[List[Dict[str, Any]]] = None,
    rivals: Optional[List[Dict[str, Any]]] = None,
    consequences: Optional[List[str]] = None,
    observations: Optional[List[Dict[str, Any]]] = None,
    max_examples: int = 5,
    backend: str = "auto",
    samples: Optional[int] = None,
    include_lean: bool = False,
    default_probes: bool = False,
    claim_evidence: Optional[Dict[str, Dict[str, Any]]] = None,
    citations: Optional[List[Dict[str, Any]]] = None,
    fidelity_spec: Optional[Dict[str, Any]] = None,
    freeze: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """A formal request. Exactly one of `hypothesis` (a formal object) and `prose` must be given.

    `default_probes` and `claim_evidence` (ADR-DISCOVERY-080) are recorded only when set, so requests that do not use
    them are byte-identical to earlier ones. So are the ADR-DISCOVERY-085 fields: `citations` (resolved uses of cited
    results, each with its registry entry inline, `hypothesis_ledger.resolve_citations`), `fidelity_spec` (paper range
    vs formal range, ADR-070) and `freeze` (a frozen-criteria reference with its record, `FreezeStore.reference`), so
    `formal analyze` can re-check all of them offline.
    """
    if (hypothesis is None) == (prose is None):
        raise ValueError("Give exactly one of a formal hypothesis and prose.")
    extra: Dict[str, Any] = {}
    if default_probes:
        extra["default_probes"] = True
    if claim_evidence:
        extra["claim_evidence"] = claim_evidence
    if citations:
        extra["citations"] = citations
    if fidelity_spec:
        extra["fidelity_spec"] = fidelity_spec
    if freeze:
        extra["freeze"] = freeze
    return {
        "schema": REQUEST_SCHEMA,
        "input_kind": "formal" if hypothesis is not None else "prose",
        "hypothesis": hypothesis,
        "prose": prose,
        "hypothesis_id": hypothesis_id,
        "variable_schema": variable_schema,
        "rivals": rivals or [],
        "consequences": consequences or [],
        "observations": observations or [],
        "max_examples": max_examples,
        "backend": backend,
        "samples": samples,
        "include_lean": include_lean,
        **extra,
    }


def make_fidelity_request(
    spec: Dict[str, Any], integer_values: Optional[Dict[str, List[int]]] = None
) -> Dict[str, Any]:
    """A statement-fidelity request: paper range vs formal range of one theorem (ADR-070, ADR-080)."""
    if not isinstance(spec, dict):
        raise ValueError("A fidelity spec must be a JSON object.")
    return {"schema": REQUEST_SCHEMA, "input_kind": "fidelity", "spec": spec, "integer_values": integer_values}


def make_lint_request(source: str, file: str, reviews: Optional[List[Dict[str, Any]]] = None) -> Dict[str, Any]:
    """A junk-value lint request for one Lean statement file (ADR-070, ADR-080). The source is stored in full."""
    return {
        "schema": REQUEST_SCHEMA,
        "input_kind": "lean_lint",
        "source": source,
        "file": file,
        "reviews": reviews or [],
    }


def make_manuscript_request(
    files: Dict[str, str],
    registry: Optional[List[Dict[str, Any]]] = None,
    manuscript_status: Optional[Dict[str, str]] = None,
    collection: Optional[List[str]] = None,
    claim: str = "",
) -> Dict[str, Any]:
    """A manuscript audit request: citation gate and import obligations over LaTeX sources (ADR-077, ADR-082).
    The sources are stored in full, so `formal analyze` can re-derive the report offline."""
    if not isinstance(files, dict) or not files:
        raise ValueError("A manuscript audit needs a non-empty {path: text} map of sources.")
    return {
        "schema": REQUEST_SCHEMA,
        "input_kind": "manuscript_audit",
        "files": files,
        "registry": registry or [],
        "manuscript_status": manuscript_status or {},
        "collection": collection,
        "claim": claim,
    }


def _parse(data: Any, what: str):
    try:
        return hypothesis_from_dict(data)
    except FormalHypothesisError:
        raise  # Keeps SolverUndecided and ThresholdExceeded distinguishable.
    except (TypeError, ValueError) as exc:
        raise FormalHypothesisError(f"The {what} is not a valid formal hypothesis: {exc}") from exc


def _formalize(request: Dict[str, Any], clients, raw_outputs, specs):
    """The gate, from live clients (phase 1) or from stored raw outputs (phase 2)."""
    from python.discovery import formal_thresholds
    from python.discovery.formalization_gate import SampleSpec, gate, sampling_schedule
    from python.discovery.formalizer import parse_formalization

    hid, schema = request["hypothesis_id"], request["variable_schema"]
    gate_request = {"prose": request["prose"], "hypothesis_id": hid, "variable_schema": schema}
    if raw_outputs is not None:
        spec_objs = [SampleSpec(**s) for s in specs]
        samples = [parse_formalization(text, hid, schema) for text in raw_outputs]
        return gate(samples, spec_objs, gate_request)
    if not clients:
        raise CapabilityUnavailable(
            "formalizer model", "set FORMALIZER_MODEL (and FORMALIZER_BASE_URL) or pass a formal object"
        )
    n = request["samples"] if request["samples"] is not None else formal_thresholds.get("gate_samples")
    n = max(1, min(formal_thresholds.get("gate_max_samples"), int(n)))
    spec_objs = sampling_schedule(list(clients), n)
    from python.discovery.formalizer import build_messages

    messages = build_messages(request["prose"], schema)
    samples = []
    for spec in spec_objs:
        try:
            text = clients[spec.model].complete(messages, temperature=spec.temperature, seed=spec.seed)
        except Exception as exc:  # Transport and HTTP errors from the model endpoint.
            raise CapabilityUnavailable("formalizer endpoint", type(exc).__name__, endpoint=True) from exc
        samples.append(parse_formalization(text, hid, schema))
    return gate(samples, spec_objs, gate_request)


def formalize(request: Dict[str, Any], clients=None, raw_outputs=None, specs=None):
    """The formalizer gate alone (ADR-064) for a prose request: live clients, or stored raw outputs offline. Used by
    the verification chain (ADR-085), which freezes the criteria of the accepted reading before evaluating it."""
    return _formalize(request, clients, raw_outputs, specs)


def compute(
    request: Dict[str, Any],
    clients: Optional[Dict[str, Any]] = None,
    raw_outputs: Optional[List[str]] = None,
    specs: Optional[List[Dict[str, Any]]] = None,
) -> Dict[str, Any]:
    """The response to a formal request. Never raises for a non-verdict: it returns it, with `formal_status`.

    Exceptions that are not a known non-verdict (a bug) still raise; they are not turned into a status either.
    """
    response: Dict[str, Any] = {
        "schema": RESPONSE_SCHEMA,
        "formal_status": FormalStatus.DECIDED.value,
        "reason": "",
        "formalizer": None,
        "formalization_gate": None,
        "formal_hypothesis": request.get("hypothesis"),
        "reports": {"evaluation": None, "comparisons": [], "consequences": []},
        "lean": [],
        "mandatory_relays": [],
    }
    relay_codes: List[str] = []
    if request["input_kind"] in ("fidelity", "lean_lint", "manuscript_audit"):
        return _compute_statement_check(request, response)
    try:
        if request["input_kind"] == "prose":
            result = _formalize(request, clients, raw_outputs, specs)
            response["formalizer"] = {
                "specs": [s.to_dict() for s in result.specs],
                "raw_outputs": [s.raw_output for s in result.samples],
            }
            response["formalization_gate"] = result.to_dict()
            relay_codes += [r["code"] for r in result.mandatory_relays]
            if not result.passes:
                response["formal_status"] = result.formal_status.value
                response["reason"] = result.reason
                response["formal_hypothesis"] = None
                response["mandatory_relays"] = formal_status.relays(relay_codes)
                return response
            response["formal_hypothesis"] = result.formalization.data
        hypothesis = _parse(response["formal_hypothesis"], "formal hypothesis")
        if request.get("freeze"):
            from python.discovery import freeze_service

            response["freeze_check"] = freeze_service.check_reference(
                request["freeze"], response["formal_hypothesis"], request["rivals"]
            )
            freeze_service.require_verified(response["freeze_check"])
            relay_codes.append("CRITERIA_FROZEN")
        n, backend = request["max_examples"], request["backend"]
        evaluation = HypothesisEvaluator.evaluate(
            hypothesis,
            request["observations"],
            max_examples=n,
            backend=backend,
            default_probes=bool(request.get("default_probes", False)),
        )
        response["reports"]["evaluation"] = evaluation.to_dict()
        relay_codes += [r["code"] for r in evaluation.mandatory_relays]
        for rival in request["rivals"]:
            report = HypothesisEvaluator.compare(hypothesis, _parse(rival, "rival"), n, backend)
            response["reports"]["comparisons"].append(report.to_dict())
            relay_codes += [r["code"] for r in report.mandatory_relays]
        for consequence in request["consequences"]:
            report = HypothesisEvaluator.entails(hypothesis, consequence, n, backend)
            response["reports"]["consequences"].append(report.to_dict())
            relay_codes += [r["code"] for r in report.mandatory_relays]
            if request["include_lean"]:
                from python.discovery.formal_lean import consequence_theorem

                response["lean"].append(
                    {
                        "consequence": consequence,
                        "theorem": consequence_theorem(hypothesis, consequence),
                        "status": FormalStatus.NOT_KERNEL_CHECKED.value,
                    }
                )
                relay_codes.append("LEAN_NOT_KERNEL_CHECKED")
        _seam_and_fidelity_reports(request, response)
    except Exception as exc:
        status = formal_status.classify(exc)  # Re-raises anything that is not a known non-verdict.
        response["formal_status"] = status.value
        response["reason"] = f"{type(exc).__name__}: {exc}"
        response["reports"] = {"evaluation": None, "comparisons": [], "consequences": []}
        response["lean"] = []
        response["_exception"] = exc  # Removed before writing; lets the caller pick the exit code.
    response["mandatory_relays"] = formal_status.relays(relay_codes)
    return response


def _seam_and_fidelity_reports(request: Dict[str, Any], response: Dict[str, Any]) -> None:
    """ADR-085: each cited result's use (ADR-083 cite_check) and the prose fidelity (ADR-070), only when requested."""
    if request.get("citations"):
        from python.discovery import hypothesis_ledger

        response["reports"]["citations"] = hypothesis_ledger.check_citations(
            response["formal_hypothesis"], request["citations"]
        )
    if request.get("fidelity_spec"):
        from python.discovery import fidelity_service

        response["reports"]["prose_fidelity"] = fidelity_service.compare(request["fidelity_spec"])


def _compute_statement_check(request: Dict[str, Any], response: Dict[str, Any]) -> Dict[str, Any]:
    """Fidelity, lint and manuscript-audit requests: one sealed report under `reports[kind]`; the other report slots
    stay empty."""
    from python.discovery import fidelity_service

    kind = request["input_kind"]
    response["reports"][kind] = None
    try:
        if kind == "fidelity":
            report = fidelity_service.compare(request["spec"], request.get("integer_values"))
        elif kind == "manuscript_audit":
            from python.discovery import manuscript_audit

            report = manuscript_audit.audit(
                request["files"],
                request.get("registry"),
                request.get("manuscript_status"),
                request.get("collection"),
                request.get("claim") or "",
            )
        else:
            report = fidelity_service.lean_lint(
                request["source"], request.get("file") or "<string>", request["reviews"]
            )
        response["reports"][kind] = report
        response["formal_status"] = report["formal_status"]
        if report["formal_status"] != FormalStatus.DECIDED.value:
            response["reason"] = "; ".join(report.get("undecided_reasons") or []) or "The solver did not decide."
        response["mandatory_relays"] = list(report["mandatory_relays"])
    except Exception as exc:
        status = formal_status.classify(exc)
        response["formal_status"] = status.value
        response["reason"] = f"{type(exc).__name__}: {exc}"
        response["_exception"] = exc
    return response


def verdict(response: Dict[str, Any]) -> Dict[str, Any]:
    """The decided results of a response, in one small block (empty when nothing was decided)."""
    out: Dict[str, Any] = {}
    gate = response.get("formalization_gate")
    if gate:
        out["gate_status"] = gate["status"]
    reports = response["reports"]
    if reports["evaluation"]:
        out["content_verdict"] = reports["evaluation"]["content_verdict"]
        out["is_refuted"] = reports["evaluation"]["is_refuted"]
        probe = reports["evaluation"].get("intent_probe")
        if probe is not None:  # Only when non-witnesses were probed, so earlier verdict blocks are unchanged.
            out["intent"] = {
                "base_verdict": probe["base_verdict"],
                "declared_non_witnesses_satisfied": probe["declared_non_witnesses_satisfied"],
                "default_probes_satisfied": probe["default_probes_satisfied"],
            }
    if reports.get("fidelity"):
        out["fidelity"] = reports["fidelity"]["relation"]
    if reports.get("lean_lint"):
        out["lean_lint"] = {"open": reports["lean_lint"]["open"], "discharged": reports["lean_lint"]["discharged"]}
    audit = reports.get("manuscript_audit")
    if audit:
        out["manuscript_audit"] = {
            "citation_gate": audit["citation_gate"]["status"],
            "unresolved_citations": len(audit["citation_gate"]["unresolved"]),
            "open_obligations": audit["open_obligations"],
        }
    if response.get("freeze_check"):  # ADR-085 fields appear only when requested, so earlier blocks are unchanged.
        out["freeze"] = response["freeze_check"]["status"]
    if reports.get("citations"):
        out["citations"] = [c["outcome"] for c in reports["citations"]]
    if reports.get("prose_fidelity"):
        out["prose_fidelity"] = reports["prose_fidelity"]["relation"]
    if reports["comparisons"]:
        out["relations"] = {c["hypothesis_b"]: c["relation"] for c in reports["comparisons"]}
    if reports["consequences"]:
        out["consequences"] = {
            c["consequence"]: {k: c[k] for k in ("entailed", "follows_from_claims", "vacuous")}
            for c in reports["consequences"]
        }
    return out


def metrics(response: Dict[str, Any]) -> Dict[str, Any]:
    """Numbers behind the verdict, for the `.analysis.json` record."""
    out: Dict[str, Any] = {}
    gate = response.get("formalization_gate")
    if gate:
        out["gate"] = {
            "n_samples": gate["n_samples"],
            "agreement": gate["agreement"],
            "n_classes": len(gate["classes"]),
        }
    ev = response["reports"]["evaluation"]
    if ev:
        out["evaluation"] = {
            k: ev[k]
            for k in (
                "backend",
                "omega_size",
                "applicable_states",
                "forbidden_states",
                "excluded_fraction_of_omega",
                "excluded_fraction_of_applicable",
                "observations_checked",
            )
        }
        out["evaluation"]["claims_with_content"] = len(ev["claims_with_content"])
        out["evaluation"]["certain_counterexamples"] = len(ev["certain_counterexamples"])
        out["evaluation"]["possible_counterexamples"] = len(ev["possible_counterexamples"])
    if response["reports"]["comparisons"]:
        out["comparisons"] = [
            {k: c[k] for k in ("hypothesis_b", "forbidden_only_by_a", "forbidden_only_by_b", "forbidden_by_both")}
            for c in response["reports"]["comparisons"]
        ]
    if response["reports"]["consequences"]:
        out["consequences"] = [
            {"consequence": c["consequence"], "counterexamples": len(c["counterexamples"])}
            for c in response["reports"]["consequences"]
        ]
    fidelity = response["reports"].get("fidelity")
    if fidelity:
        out["fidelity"] = {
            "method": fidelity["method"],
            "division_hazards": len(fidelity["division_hazards"]),
            "quantities": len(fidelity["quantities"]),
        }
    lint = response["reports"].get("lean_lint")
    if lint:
        out["lean_lint"] = {"declarations": len(lint["declarations"]), "sites": len(lint["sites"])}
    audit = response["reports"].get("manuscript_audit")
    if audit:
        out["manuscript_audit"] = {
            "source_lines": audit["source_lines"],
            "citations": audit["citation_gate"]["citations"],
            "import_counts": audit["import_counts"],
            "hypothesis_outcomes": audit["hypothesis_outcomes"],
        }
    return out


def report_digests(response: Dict[str, Any]) -> List[Dict[str, Any]]:
    """(name, input_sha256, output_sha256, threshold set) of every report, for run/analyze comparison."""
    out = []
    gate = response.get("formalization_gate")
    named = [("formalization_gate", gate)] if gate else []
    reports = response["reports"]
    if reports["evaluation"]:
        named.append(("evaluation", reports["evaluation"]))
    named += [(f"comparison[{i}]", c) for i, c in enumerate(reports["comparisons"])]
    named += [(f"consequence[{i}]", c) for i, c in enumerate(reports["consequences"])]
    named += [(kind, reports[kind]) for kind in ("fidelity", "lean_lint", "manuscript_audit") if reports.get(kind)]
    named += [(f"citation[{i}]", c) for i, c in enumerate(reports.get("citations") or [])]
    if reports.get("prose_fidelity"):
        named.append(("prose_fidelity", reports["prose_fidelity"]))
    for name, report in named:
        p = report["provenance"]
        out.append(
            {
                "report": name,
                "input_sha256": p["input_sha256"],
                "output_sha256": p["output_sha256"],
                "threshold_set": p["threshold_set"],
                "thresholds_applied": p["thresholds_applied"],
            }
        )
    return out
