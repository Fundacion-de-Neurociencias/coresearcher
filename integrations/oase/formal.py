# Copyright 2026 Fundación de Neurociencias
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Formal soundness of hypotheses, decided by CoResearcher (z3 or exhaustive enumeration).

Two phases (docs/tool-design-guidance.md §3):

  run     — phase 1. Reads one hypothesis (a hypex ``H-NNNN.json`` or one
            candidate of an adopted ``oase.hypothesis-set.v1``) and a formal
            object for it, or formalizes its statement with the configured
            model. Calls CoResearcher in-process (``--transport package``) or
            over HTTP (``--transport http``), and writes
            ``raw/formal/fm-<id>.request.json``, ``.response.json`` and the
            ``.meta.json`` sidecar.
  analyze — phase 2. Offline. Checks the sidecar checksums, re-runs the
            verdict locally with z3 from the stored formal object (and the
            formalization gate from the stored raw model outputs), compares it
            with the run report by report, applies the ``formal@1.0``
            threshold set and writes ``fm-<id>.analysis.json``.
  doctor  — which formal capabilities are present (engine, z3, Lean, model).

Scope: formal soundness only. Whether the formal object is vacuous,
self-contradictory, unfalsifiable or falsifiable; how it relates to a rival
(equivalent, stronger, weaker, incomparable, contradictory) and on which states
they disagree; whether a stated consequence follows. Nothing here reads, grades
or checks evidence, citations, data or sources: the hypex ``evidence`` field is
deliberately never read.

A non-verdict is never a negative. UNDECIDED (the solver gave up), BLOCKED (a
capability or threshold is missing) and an ambiguous formalization each get
their own exit code and an AR mapping of ``execution_outcome: blocked`` /
``evidence_status: not_assessed``; only a DECIDED defect is ``contradicted``.
"""

from __future__ import annotations

import contextlib
import json
import os
import re
import shutil
import socket
import subprocess
import sys
from pathlib import Path
from typing import Any

import click

from ..common import (
    AppState,
    beside_or_out,
    load_thresholds,
    out_option,
    output_options,
    pass_state,
    resolve_artifact,
)
from ..core import provenance
from ..core.errors import (
    ArtifactError,
    DependencyError,
    EndpointUnavailable,
    OASEError,
    PhaseContractError,
    Refusal,
    SchemaError,
    ThresholdError,
    UsageError,
)
from ..core.output import Emitter
from ..core.paths import is_safe_to_open

TOOL = "formal"
ARTIFACT_CLASS = "formal"
THRESHOLD_SET = "formal"
REQUEST_SCHEMA = "oase.formal-request.v1"
RESPONSE_SCHEMA = "oase.formal-response.v1"
EVIDENCE_TYPE = "formal-soundness"
MAX_INPUT_BYTES = 5 * 1024 * 1024

_HYPEX_ID = re.compile(r"^H-[0-9]{4}$")
_SAFE_ID = re.compile(r"[^A-Za-z0-9._-]+")

#: CoResearcher content verdicts that are defects of the hypothesis itself.
DEFECT_VERDICTS = (
    "VACUOUS",
    "SELF_CONTRADICTORY",
    "UNFALSIFIABLE",
    "VACUOUS_RELATIVE_TO_INTENT",
)

#: Thresholds that belong to the CoResearcher engine (they bound the
#: computation). The decision thresholds of formal@1.0 are applied here.
ENGINE_THRESHOLDS = (
    "max_states",
    "max_assumptions_for_conflict_search",
    "solver_timeout_ms",
    "gate_samples",
    "gate_max_samples",
    "gate_temperature",
    "gate_majority_fraction",
    "formalizer_temperature",
    "formalizer_seed",
)


class FormalUndecided(OASEError):
    """z3 returned unknown. Not an answer, not a refusal: nothing was decided.

    OASE's taxonomy has no code for "the decision procedure gave up", and
    folding it into 0 (answer) or 9 (refusal) would each send the caller the
    wrong way. Raising the solver timeout or simplifying the object can help;
    the same input under the same thresholds will not.
    """

    exit_code = 10


class FormalNotReproduced(OASEError):
    """`formal analyze` recomputed a different result under the same thresholds."""

    exit_code = 12


# ---------------------------------------------------------------------------
# The CoResearcher engine
# ---------------------------------------------------------------------------


def _engine() -> dict[str, Any]:
    """Import CoResearcher's formal layer, or raise DependencyError.

    ``CORESEARCHER_HOME`` names a CoResearcher checkout to import from when
    the package is not installed into this environment.
    """
    home = os.environ.get("CORESEARCHER_HOME")
    if home and home not in sys.path:
        sys.path.insert(0, home)
    try:
        from python.cli import formal as cr_cli
        from python.discovery import (
            formal_pipeline,
            formal_provenance,
            formal_status,
            formal_thresholds,
        )
    except ImportError as exc:
        raise DependencyError(
            "the CoResearcher formal engine is not importable",
            detail=f"{type(exc).__name__}: {exc}",
            remedy="install CoResearcher into the tools environment, or set "
            "CORESEARCHER_HOME to a CoResearcher checkout",
        ) from exc
    return {
        "cli": cr_cli,
        "pipeline": formal_pipeline,
        "provenance": formal_provenance,
        "status": formal_status,
        "thresholds": formal_thresholds,
    }


def _engine_thresholds(cr: dict[str, Any], ts: Any) -> Any:
    """The CoResearcher threshold set equivalent to the OASE set in force.

    Only values that differ from CoResearcher's own defaults are passed as
    overrides, so a run under unmodified formal@1.0 is a run under the
    engine's versioned defaults and carries no THRESHOLDS_OVERRIDDEN relay.
    """
    base = cr["thresholds"].FORMAL_DEFAULTS
    overrides: dict[str, Any] = {}
    for key in ENGINE_THRESHOLDS:
        try:
            value = ts.get(key)
        except ThresholdError:
            # UNRESOLVED in the OASE set: the engine must not substitute its default.
            overrides[key] = None
            continue
        if value != base.values.get(key):
            overrides[key] = value
    if not overrides:
        return base
    sources = ts.sources()
    origin = ", ".join(f"{k}={sources.get(k, 'unresolved')}" for k in sorted(overrides))
    return base.with_overrides(
        overrides, "oase", f"OASE threshold set {ts.tag} ({origin})"
    )


# ---------------------------------------------------------------------------
# Relays: CoResearcher codes into the OASE registry namespace
# ---------------------------------------------------------------------------


def _oase_code(coresearcher_code: str) -> str:
    """The registered OASE relay code for a CoResearcher relay code.

    An unmapped code raises: a caveat CoResearcher attached must not be
    dropped on its way into OASE because nobody registered it here.
    """
    mapping = {
        "FORMAL_NOT_EMPIRICAL": "formal.not_empirical",
        "SMT_FIXED_SIZE_ONLY": "formal.smt_fixed_size_only",
        "ENUMERATION_DECLARED_DOMAINS_ONLY": "formal.enumeration_declared_domains_only",
        "LEAN_NOT_KERNEL_CHECKED": "formal.lean_not_kernel_checked",
        "FORMALIZATION_IS_DRAFT": "formal.formalization_is_draft",
        "GATE_SINGLE_SAMPLE": "formal.gate_single_sample",
        "VACUOUS_ENTAILMENT": "formal.vacuous_entailment",
        "ENTAILED_BY_ASSUMPTIONS_ALONE": "formal.entailed_by_assumptions_alone",
        "THRESHOLDS_OVERRIDDEN": "formal.thresholds_overridden",
        "FORMALIZATION_AMBIGUOUS": "formal.formalization_ambiguous",
        "FORMALIZATION_FAILED": "formal.formalization_failed",
        "UNDECIDED": "formal.undecided",
        "BLOCKED": "formal.blocked",
        "VACUOUS_RELATIVE_TO_INTENT": "formal.vacuous_relative_to_intent",
        "TRIVIAL_WITNESS_SATISFIES_CLAIMS": "formal.trivial_witness_satisfies_claims",
        "CLAIM_BELOW_KERNEL_CHECKED": "formal.claim_below_kernel_checked",
        "FIDELITY_RANGE_ONLY": "formal.fidelity_range_only",
        "LINT_IS_SYNTACTIC": "formal.lint_is_syntactic",
    }
    if coresearcher_code not in mapping:
        raise SchemaError(
            f"CoResearcher emitted relay {coresearcher_code!r}, which has no OASE mapping",
            remedy="map it in integrations/oase/formal.py and register it in "
            "provenance.RELAY_CODES (integrations/oase/apply.sh)",
        )
    return mapping[coresearcher_code]


def _relays_from(response: dict[str, Any]) -> list[dict[str, str]]:
    """The OASE relays a CoResearcher response obliges, deduplicated, in order.

    Every relay CoResearcher attached is carried, then the status relay for
    a non-verdict. The OASE message is the registered obligation; the
    engine's own message and code ride along so a reviewer can trace it.
    """
    out: list[dict[str, str]] = []

    def add(cr_code: str, detail: str) -> None:
        code = _oase_code(cr_code)
        if any(r["code"] == code for r in out):
            return
        message = provenance.RELAY_CODES[code] + (f" ({detail})" if detail else "")
        record = provenance.relay(code, message)
        record["coresearcher_code"] = cr_code
        out.append(record)

    for item in response.get("mandatory_relays") or []:
        add(item["code"], "")
    status = response.get("formal_status")
    if status in (
        "UNDECIDED",
        "BLOCKED",
        "FORMALIZATION_AMBIGUOUS",
        "FORMALIZATION_FAILED",
    ):
        add(status, response.get("reason") or "")
    return out


# ---------------------------------------------------------------------------
# Inputs
# ---------------------------------------------------------------------------


def _read_input(path: Path, what: str) -> Any:
    if not is_safe_to_open(path):
        raise Refusal(f"refusing to read {what} through a symlink: {path}")
    if path.stat().st_size > MAX_INPUT_BYTES:
        raise Refusal(
            f"{what} is larger than {MAX_INPUT_BYTES} bytes: {path}",
            remedy="a hypothesis or formal object is small; check the path",
        )
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        raise ArtifactError(
            f"{what} is not readable JSON: {path}", detail=str(exc)
        ) from exc


def _locate(state: AppState, raw: str, what: str) -> Path:
    """Foreign input: resolved against the current directory, then the project root.

    The same rule as `oase hypothesis adopt`: the file has not entered the
    project yet. Nothing is searched beyond these two places.
    """
    candidate = Path(raw).expanduser()
    if candidate.is_absolute():
        options = [candidate]
    else:
        options = [Path.cwd() / candidate, state.project().root / candidate]
    for option in options:
        if option.is_file():
            return option
    raise ArtifactError(
        f"{what} not found: {raw}",
        detail="looked in " + ", ".join(str(o) for o in options),
        remedy="pass an absolute path",
    )


def _hypothesis_from(data: Any, path: Path, candidate: str | None) -> dict[str, Any]:
    """Identity and statement of the hypothesis to verify.

    Only `id`, `title` and `statement` are read. `evidence`, citations and
    reviews are out of scope for a formal check and are never looked at.
    """
    if not isinstance(data, dict):
        raise SchemaError(f"{path.name} is not a JSON object")
    if data.get("schema") == "oase.hypothesis-set.v1":
        candidates = data.get("candidates") or []
        if candidate is None:
            raise UsageError(
                f"{path.name} is an adopted hypothesis set with {len(candidates)} candidate(s)",
                remedy="name one with --candidate <candidate_id>",
            )
        matches = [c for c in candidates if str(c.get("candidate_id")) == candidate]
        if len(matches) != 1:
            raise Refusal(
                f"--candidate {candidate!r} matches {len(matches)} candidate(s) in {path.name}",
                detail="known candidate_ids: "
                + ", ".join(str(c.get("candidate_id")) for c in candidates),
            )
        stem = path.name.split(".")[0]
        hid = _SAFE_ID.sub("-", f"{stem}-c{candidate}")
        return {
            "kind": "adopted-candidate",
            "id": hid,
            "title": "",
            "statement": matches[0].get("statement") or "",
        }
    if candidate is not None:
        raise UsageError("--candidate applies only to an adopted hypothesis set")
    hid = data.get("id")
    if not isinstance(hid, str) or not _HYPEX_ID.match(hid):
        raise SchemaError(
            f"{path.name} is neither a hypex hypothesis (id H-NNNN) nor an "
            "oase.hypothesis-set.v1 artifact",
            detail=f"id: {hid!r}",
        )
    statement = data.get("statement")
    if not isinstance(statement, str) or not statement.strip():
        raise SchemaError(f"{path.name} has no statement")
    return {
        "kind": "hypex",
        "id": hid,
        "title": data.get("title") or "",
        "statement": statement,
    }


def _formal_object(data: Any, path: Path, expected_id: str | None) -> dict[str, Any]:
    """A formal object, its identity checked rather than assumed."""
    if not isinstance(data, dict):
        raise SchemaError(f"{path.name} is not a formal hypothesis object")
    found = data.get("hypothesis_id")
    if expected_id is not None:
        if found is None:
            data = {**data, "hypothesis_id": expected_id}
        elif found != expected_id:
            raise Refusal(
                f"{path.name} formalizes {found!r}, not {expected_id!r}",
                detail="the formal object and the hypothesis name different ids; "
                "the tool will not guess which one is meant",
                remedy="set hypothesis_id in the formal object to the hypothesis id",
            )
    elif not isinstance(found, str) or not found:
        raise SchemaError(f"{path.name} has no hypothesis_id; a rival must name itself")
    return data


# ---------------------------------------------------------------------------
# Transports
# ---------------------------------------------------------------------------


def _formalizer_clients(cr: dict[str, Any]) -> dict[str, Any]:
    try:
        return cr["cli"].formalizer_clients()
    except ValueError:
        return {}


def _run_package(
    cr: dict[str, Any], request: dict[str, Any], cr_set: Any
) -> dict[str, Any]:
    clients = None
    if request["input_kind"] == "prose":
        from python.discovery.formalizer import build_messages

        request["formalizer_messages"] = build_messages(
            request["prose"], request["variable_schema"]
        )
        clients = _formalizer_clients(cr)
    with cr["thresholds"].using(cr_set):
        return cr["pipeline"].compute(request, clients=clients)


def _http_base() -> str:
    base = os.environ.get("CORESEARCHER_URL")
    if not base:
        raise DependencyError(
            "--transport http needs CORESEARCHER_URL",
            remedy="set CORESEARCHER_URL to the CoResearcher API, or use --transport package",
        )
    return base.rstrip("/")


def _run_http(
    cr: dict[str, Any], request: dict[str, Any]
) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    """Formal objects over the CoResearcher API: /evaluate, /compare, /entails.

    Prose is refused on this transport: only the in-process transport keeps
    the raw model outputs that let `analyze` re-run the formalization gate
    offline, and a formalization that cannot be re-checked is not one this
    tool will record.
    """
    from ..core import http

    if request["input_kind"] != "formal":
        raise Refusal(
            "--transport http accepts formal objects only",
            detail="prose needs the package transport, which stores the raw "
            "model outputs for offline re-analysis",
            remedy="pass --formal, or use --transport package",
        )
    base = _http_base()
    headers = {"X-API-Key": os.environ.get("CORESEARCHER_API_KEY", "")}
    exchanges: list[dict[str, Any]] = []

    def post(route: str, payload: dict[str, Any]) -> dict[str, Any] | None:
        resp = http.request(
            "POST",
            f"{base}{route}",
            json=payload,
            headers=headers,
            tolerate_status={422},
        )
        body = resp.json()
        exchanges.append(
            {
                "route": route,
                "request": payload,
                "status": resp.status_code,
                "response": body,
            }
        )
        return None if resp.status_code == 422 else body

    hyp, n = request["hypothesis"], request["max_examples"]
    out: dict[str, Any] = {
        "schema": cr["pipeline"].RESPONSE_SCHEMA,
        "formal_status": "DECIDED",
        "reason": "",
        "formalizer": None,
        "formalization_gate": None,
        "formal_hypothesis": hyp,
        "reports": {"evaluation": None, "comparisons": [], "consequences": []},
        "lean": [],
        "mandatory_relays": [],
    }
    codes: list[str] = []
    evaluation = post(
        "/api/hypotheses/evaluate",
        {"hypothesis": hyp, "observations": request["observations"], "max_examples": n},
    )
    calls = [] if evaluation is None else [("evaluation", evaluation)]
    if evaluation is not None:
        for rival in request["rivals"]:
            body = post(
                "/api/hypotheses/compare", {"a": hyp, "b": rival, "max_examples": n}
            )
            if body is None:
                break
            calls.append(("comparison", body))
        for consequence in request["consequences"]:
            body = post(
                "/api/hypotheses/entails",
                {
                    "hypothesis": hyp,
                    "consequence": consequence,
                    "max_examples": n,
                    "include_lean": request["include_lean"],
                },
            )
            if body is None:
                break
            calls.append(("consequence", body))
    if any(e["status"] == 422 for e in exchanges):
        failed = next(e for e in exchanges if e["status"] == 422)
        out["formal_status"] = "INVALID_INPUT"
        out["reason"] = f"{failed['route']}: {failed['response'].get('detail')}"
        out["reports"] = {"evaluation": None, "comparisons": [], "consequences": []}
        return out, exchanges
    for kind, body in calls:
        codes += [r["code"] for r in body.get("mandatory_relays") or []]
        if kind == "consequence" and "lean_theorem" in body:
            out["lean"].append(
                {
                    "consequence": body["consequence"],
                    "theorem": body.pop("lean_theorem"),
                    "status": body.pop("lean_status"),
                }
            )
            body["mandatory_relays"] = [
                r
                for r in body["mandatory_relays"]
                if r["code"] != "LEAN_NOT_KERNEL_CHECKED"
            ]
        if kind == "evaluation":
            out["reports"]["evaluation"] = body
        else:
            out["reports"][
                "comparisons" if kind == "comparison" else "consequences"
            ].append(body)
    out["mandatory_relays"] = cr["status"].relays(codes)
    return out, exchanges


# ---------------------------------------------------------------------------
# Verdict, criteria and the AR mapping
# ---------------------------------------------------------------------------


def _criteria(response: dict[str, Any], ts: Any) -> dict[str, Any]:
    """formal@1.0 applied to a recomputed response.

    `met` is null whenever nothing was decided or the threshold is
    UNRESOLVED. It is never false for a reason other than a decided defect.
    """
    decided = response["formal_status"] == "DECIDED"
    evaluation = response["reports"]["evaluation"] if decided else None
    content = evaluation["content_verdict"] if evaluation else None
    defects = [content] if content in DEFECT_VERDICTS else []
    out: dict[str, Any] = {"content_verdict": content, "defects": defects}

    try:
        cap = ts.get("max_formal_defects")
    except ThresholdError:
        cap = None
    out["max_formal_defects"] = {
        "metric": "defect_count",
        "value": len(defects) if evaluation else None,
        "comparison": "value <= threshold",
        "threshold": cap,
        "met": (len(defects) <= cap) if (evaluation and cap is not None) else None,
    }

    try:
        floor = ts.get("min_excluded_fraction_of_applicable")
    except ThresholdError:
        floor = None
    excluded = evaluation.get("excluded_fraction_of_applicable") if evaluation else None
    out["min_excluded_fraction_of_applicable"] = {
        "metric": "excluded_fraction_of_applicable",
        "value": excluded,
        "comparison": "value >= threshold",
        "threshold": floor,
        "met": (
            (excluded >= floor)
            if (excluded is not None and floor is not None)
            else None
        ),
        "unresolved": floor is None,
    }
    return out


def _evidence_mapping(
    response: dict[str, Any],
    criteria: dict[str, Any],
    ts: Any,
    source: str,
    source_sha256: str,
) -> dict[str, Any]:
    """How an `oase.evidence-assessment.v1` record (AR) cites this analysis.

    DECIDED with no defect -> supported; DECIDED with a defect ->
    contradicted. Every non-verdict -> execution_outcome blocked,
    evidence_status not_assessed: an engine that gave up has assessed
    nothing, and recording it as contradicted would invent a negative.
    """
    status = response["formal_status"]
    evaluation = response["reports"]["evaluation"]
    if status == "DECIDED" and evaluation is not None:
        execution, evidence = "completed", (
            "contradicted" if criteria["defects"] else "supported"
        )
        method = f"coresearcher-{evaluation['backend']}"
    else:
        execution, evidence, method = "blocked", "not_assessed", None
    return {
        "execution_outcome": execution,
        "evidence_status": evidence,
        "evidence": {
            "artifact_path": source,
            "artifact_sha256": source_sha256,
            "evidence_type": EVIDENCE_TYPE,
            "metric_name": "defect_count",
            "metric_value": criteria["max_formal_defects"]["value"],
            "metric_units": "count",
            "threshold_set": ts.tag,
            "method": method,
            "context": f"formal_status={status}",
        },
    }


def _verdict_line(response: dict[str, Any]) -> str:
    reports = response["reports"]
    if response["formal_status"] != "DECIDED":
        return f"{response['formal_status']}: {response.get('reason') or 'no verdict'}"
    parts = [reports["evaluation"]["content_verdict"]]
    for c in reports["comparisons"]:
        parts.append(f"{c['relation']} vs {c['hypothesis_b']}")
    entailed = sum(1 for c in reports["consequences"] if c["entailed"])
    if reports["consequences"]:
        parts.append(
            f"{entailed}/{len(reports['consequences'])} consequence(s) entailed"
        )
    return ", ".join(parts)


def _raise_for(response: dict[str, Any], exception_name: str | None) -> None:
    """The OASE exit for a non-verdict. Raised after the artifacts are written."""
    status = response["formal_status"]
    reason = response.get("reason") or status
    if status == "DECIDED":
        return
    if status == "UNDECIDED":
        raise FormalUndecided(
            f"UNDECIDED: {reason}",
            remedy="raise solver_timeout_ms for this run or simplify the formal object; "
            "nothing was decided, so nothing may be reported as refuted",
        )
    if status in ("FORMALIZATION_AMBIGUOUS", "FORMALIZATION_FAILED"):
        raise Refusal(
            f"{status}: {reason}",
            remedy="supply a formal object with --formal, or a --variable-schema; "
            "the tool does not pick one reading among disagreeing ones",
        )
    if status == "INVALID_INPUT":
        raise Refusal(f"INVALID_INPUT: {reason}", remedy="fix the formal object")
    if exception_name in ("ThresholdError", "ThresholdExceeded"):
        raise ThresholdError(f"BLOCKED: {reason}")
    if "endpoint" in reason or exception_name == "EndpointUnavailable":
        raise EndpointUnavailable(f"BLOCKED: {reason}")
    raise DependencyError(f"BLOCKED: {reason}")


# ---------------------------------------------------------------------------
# Commands
# ---------------------------------------------------------------------------


@click.group()
def formal() -> None:
    """Formal soundness of hypotheses (CoResearcher): vacuity, contradiction, falsifiability, rivals."""


def _threshold_flags(**flags: Any) -> dict[str, Any]:
    return {k: v for k, v in flags.items() if v is not None}


@formal.command()
@click.argument("hypothesis")
@click.option(
    "--candidate", default=None, help="candidate_id, when HYPOTHESIS is an adopted set."
)
@click.option(
    "--formal",
    "formal_path",
    default=None,
    help="Formal object for the hypothesis (JSON).",
)
@click.option(
    "--variable-schema", default=None, help="Variables the formalizer must use (JSON)."
)
@click.option(
    "--rival", "rivals", multiple=True, help="Rival formal object (JSON); repeatable."
)
@click.option(
    "--consequence",
    "consequences",
    multiple=True,
    help="Predicate to check for entailment; repeatable.",
)
@click.option(
    "--observations",
    default=None,
    help="Observations to check against the object (JSON list).",
)
@click.option(
    "--samples",
    type=int,
    default=None,
    help="Formalizer samples for the self-consistency gate.",
)
@click.option("--max-examples", type=int, default=5, show_default=True)
@click.option(
    "--lean",
    is_flag=True,
    help="Also state each consequence as a Lean 4 theorem (not kernel-checked).",
)
@click.option(
    "--transport",
    type=click.Choice(["package", "http"]),
    default="package",
    show_default=True,
)
@click.option("--solver-timeout-ms", type=int, default=None, help="Override threshold.")
@click.option("--max-states", type=int, default=None, help="Override threshold.")
@click.option(
    "--overwrite", is_flag=True, help="Replace an existing run for a different request."
)
@out_option
@output_options
@pass_state
def run(
    state: AppState,
    hypothesis: str,
    candidate: str | None,
    formal_path: str | None,
    variable_schema: str | None,
    rivals: tuple[str, ...],
    consequences: tuple[str, ...],
    observations: str | None,
    samples: int | None,
    max_examples: int,
    lean: bool,
    transport: str,
    solver_timeout_ms: int | None,
    max_states: int | None,
    overwrite: bool,
    out: str | None,
    as_json: bool,
    quiet: bool,
) -> None:
    """Verify one hypothesis formally and record request, response and sidecar.

    HYPOTHESIS is a hypex H-NNNN.json, or an adopted hypothesis set with
    --candidate. Without --formal, its statement is formalized by the
    configured model (package transport only) and gated for self-consistency.
    """
    project = state.project()
    cr = _engine()
    source = _locate(state, hypothesis, "hypothesis")
    hyp = _hypothesis_from(_read_input(source, "hypothesis"), source, candidate)

    formal_obj = None
    if formal_path:
        fpath = _locate(state, formal_path, "formal object")
        formal_obj = _formal_object(
            _read_input(fpath, "formal object"), fpath, hyp["id"]
        )
        formal_obj.setdefault("statement", hyp["statement"])
    rival_objs = []
    for raw in rivals:
        rpath = _locate(state, raw, "rival formal object")
        obj = _formal_object(_read_input(rpath, "rival formal object"), rpath, None)
        if obj["hypothesis_id"] == hyp["id"]:
            raise Refusal(
                f"rival {rpath.name} has the hypothesis's own id {hyp['id']!r}"
            )
        rival_objs.append(obj)
    schema = None
    if variable_schema:
        spath = _locate(state, variable_schema, "variable schema")
        schema = _read_input(spath, "variable schema")
    obs = []
    if observations:
        opath = _locate(state, observations, "observations")
        obs = _read_input(opath, "observations")

    ts = load_thresholds(
        state,
        THRESHOLD_SET,
        _threshold_flags(solver_timeout_ms=solver_timeout_ms, max_states=max_states),
    )
    cr_set = _engine_thresholds(cr, ts)
    try:
        cr_request = cr["pipeline"].make_request(
            hypothesis=formal_obj,
            prose=None if formal_obj is not None else hyp["statement"],
            hypothesis_id=hyp["id"],
            variable_schema=schema,
            rivals=rival_objs,
            consequences=list(consequences),
            observations=obs,
            max_examples=max_examples,
            backend="auto",
            samples=samples,
            include_lean=lean,
        )
    except ValueError as exc:
        raise UsageError(str(exc)) from exc

    stem = "fm-" + _SAFE_ID.sub("-", hyp["id"])
    if rival_objs:
        stem += "_vs_" + "_".join(
            _SAFE_ID.sub("-", r["hypothesis_id"]) for r in rival_objs
        )
    target = project.artifact_dir(ARTIFACT_CLASS, out)
    paths = {k: target / f"{stem}.{k}.json" for k in ("request", "response", "meta")}

    request_record = {
        "schema": REQUEST_SCHEMA,
        "transport": transport,
        "hypothesis": {
            "kind": hyp["kind"],
            "id": hyp["id"],
            "title": hyp["title"],
            "statement": hyp["statement"],
            "source": project.relative(source),
            "source_sha256": provenance.sha256_file(source),
        },
        "coresearcher_request": cr_request,
    }
    if paths["meta"].exists() and not overwrite:
        existing = (
            provenance.read_json(paths["request"], "existing request")
            if paths["request"].is_file()
            else None
        )
        if existing == json.loads(json.dumps(request_record)):
            emit = Emitter(as_json=as_json, quiet=quiet)
            emit.data("cached", True)
            for kind in ("request", "response", "meta"):
                emit.path(project.relative(paths[kind]), kind)
            emit.flush()
            return
        raise Refusal(
            f"{paths['meta'].name} already records a different request",
            remedy="pass --overwrite to replace it, or --out to write beside it",
        )

    exchanges: list[dict[str, Any]] = []
    if transport == "package":
        response = _run_package(cr, cr_request, cr_set)
        request_record["coresearcher_request"] = (
            cr_request  # now with formalizer_messages
        )
    else:
        response, exchanges = _run_http(cr, cr_request)
        request_record["http"] = {
            "base_url": _http_base(),
            "routes": [e["route"] for e in exchanges],
        }
    exception = response.pop("_exception", None)
    exception_name = type(exception).__name__ if exception is not None else None
    if exception is not None and getattr(exception, "endpoint", False):
        exception_name = "EndpointUnavailable"

    response_record = {
        "schema": RESPONSE_SCHEMA,
        "transport": transport,
        "formal_status": response["formal_status"],
        "exception": exception_name,
        "coresearcher_response": response,
    }
    if exchanges:
        response_record["http_exchanges"] = exchanges
    for kind, record in (("request", request_record), ("response", response_record)):
        if not is_safe_to_open(paths[kind]):
            raise Refusal(f"refusing to write through a symlink: {paths[kind]}")
        paths[kind].write_text(
            json.dumps(record, indent=2, default=str) + "\n", encoding="utf-8"
        )

    endpoint = None
    if transport == "http":
        endpoint = _http_base()
    elif cr_request["input_kind"] == "prose":
        endpoint = (
            os.environ.get("FORMALIZER_BASE_URL") or "http://localhost:11434/v1"
        ).rstrip("/")
    sidecar = provenance.Sidecar(
        tool=TOOL,
        subcommand="run",
        endpoint=endpoint,
        parameters={
            "hypothesis": project.relative(source),
            "candidate": candidate,
            "formal": formal_path,
            "rivals": [r["hypothesis_id"] for r in rival_objs],
            "consequences": list(consequences),
            "observations": len(obs),
            "samples": samples,
            "max_examples": max_examples,
            "lean": lean,
            "transport": transport,
        },
    )
    sidecar.add_output(paths["request"])
    sidecar.add_output(paths["response"])
    sidecar.note("hypothesis_id", hyp["id"])
    sidecar.note("formal_status", response["formal_status"])
    sidecar.note("threshold_set", ts.tag)
    sidecar.note("thresholds_applied", ts.applied())
    sidecar.note("threshold_sources", ts.sources())
    sidecar.note(
        "coresearcher",
        {
            "engine_version": cr["provenance"].engine_version(),
            "z3_version": cr["provenance"].z3_version(),
            **cr_set.record(),
        },
    )
    sidecar.set_capability_state(_capability_state(cr))
    for item in _relays_from(response):
        sidecar.warn(item["message"], code=item["code"])
    meta = sidecar.write(paths["meta"])

    emit = Emitter(as_json=as_json, quiet=quiet)
    emit.data("formal_status", response["formal_status"])
    emit.data("mandatory_relays", sidecar.relays)
    for kind in ("request", "response"):
        emit.path(project.relative(paths[kind]), kind)
    emit.path(project.relative(meta), "sidecar")
    emit.flush()
    _raise_for(response, exception_name)


@contextlib.contextmanager
def _sockets_refused():
    """Phase 2 must reach nothing: refuse raw sockets too, not only OASE's client.

    enforce_phase_two latches oase.core.http; the engine has its own HTTP
    client (the formalizer), which that latch cannot see.
    """

    def refuse(*_a: Any, **_k: Any) -> None:
        raise PhaseContractError(
            "`formal analyze` attempted a network connection",
            detail="phase 2 re-runs the verdict from stored artifacts only",
        )

    saved = (socket.socket.connect, socket.socket.connect_ex, socket.create_connection)
    socket.socket.connect = socket.socket.connect_ex = socket.create_connection = refuse  # type: ignore[assignment]
    try:
        yield
    finally:
        socket.socket.connect, socket.socket.connect_ex, socket.create_connection = (
            saved
        )


#: Engine stamps inside each report's provenance. They say which engine build
#: produced the report, like OASE's env_version, and are compared as an
#: environment change, never as a disagreement: the verdict is compared through
#: input_sha256 and output_sha256, which do not depend on them.
ENGINE_STAMPS = ("engine_version", "z3_version")


def _split_engine_stamps(response: Any, found: set[tuple[str, Any]]) -> Any:
    """A copy of `response` without engine stamps; the stamps go into `found`."""
    if isinstance(response, dict):
        out = {}
        for key, value in response.items():
            if key == "provenance" and isinstance(value, dict):
                found.update((k, value.get(k)) for k in ENGINE_STAMPS if k in value)
                value = {k: v for k, v in value.items() if k not in ENGINE_STAMPS}
            out[key] = _split_engine_stamps(value, found)
        return out
    if isinstance(response, list):
        return [_split_engine_stamps(v, found) for v in response]
    return response


def _compare(cr: dict[str, Any], run_response: dict, response: dict) -> dict:
    """Run vs recomputed response, verdict by verdict; engine stamps reported apart."""
    before: set[tuple[str, Any]] = set()
    after: set[tuple[str, Any]] = set()
    old = _split_engine_stamps(run_response, before)
    new = _split_engine_stamps(response, after)
    try:
        comparison = cr["cli"]._compare_with_run(old, new)
    except Exception as exc:  # CoResearcher's CliError on a malformed response.
        raise ArtifactError(f"the run's response is not comparable: {exc}") from exc
    comparison["engine_changes"] = [
        {
            "field": key,
            "run": sorted(str(v) for k, v in before if k == key),
            "analyze": sorted(str(v) for k, v in after if k == key),
        }
        for key in ENGINE_STAMPS
        if {v for k, v in before if k == key} != {v for k, v in after if k == key}
    ]
    return comparison


def _meta_for(path: Path) -> Path:
    for suffix in (".meta.json", ".response.json", ".request.json", ".analysis.json"):
        if path.name.endswith(suffix):
            return path.with_name(path.name[: -len(suffix)] + ".meta.json")
    return path.with_name(path.name + ".meta.json")


@formal.command()
@click.argument("artifact")
@click.option("--solver-timeout-ms", type=int, default=None, help="Override threshold.")
@click.option("--max-states", type=int, default=None, help="Override threshold.")
@click.option(
    "--max-formal-defects", type=int, default=None, help="Override threshold."
)
@click.option(
    "--min-excluded-fraction-of-applicable",
    type=float,
    default=None,
    help="Override threshold.",
)
@out_option
@output_options
@pass_state
def analyze(
    state: AppState,
    artifact: str,
    solver_timeout_ms: int | None,
    max_states: int | None,
    max_formal_defects: int | None,
    min_excluded_fraction_of_applicable: float | None,
    out: str | None,
    as_json: bool,
    quiet: bool,
) -> None:
    """Re-run the formal verdict offline and apply formal@1.0.

    ARTIFACT is the run's .meta.json (or its .response.json).
    """
    project = state.project()
    cr = _engine()
    given = resolve_artifact(state, artifact, "formal run artifact")
    meta_path = _meta_for(given)
    if not meta_path.is_file():
        raise ArtifactError(
            f"sidecar not found: {meta_path}", remedy="run `oase formal run` first"
        )
    sidecar = provenance.read_json(meta_path, "formal sidecar")
    if sidecar.get("tool") != TOOL or sidecar.get("subcommand") != "run":
        raise SchemaError(f"{meta_path.name} is not an `oase formal run` sidecar")
    files: dict[str, Path] = {}
    for entry in sidecar.get("outputs") or []:
        path = meta_path.parent / entry["path"]
        if not path.is_file():
            raise ArtifactError(f"declared output is missing: {path}")
        digest = provenance.sha256_file(path)
        if digest != entry["sha256"]:
            raise ArtifactError(
                f"{path.name} does not match its recorded sha256",
                detail=f"{digest} != {entry['sha256']}; it changed after `run`",
            )
        files[path.name.rsplit(".", 2)[-2]] = path
    if set(files) != {"request", "response"}:
        raise ArtifactError(
            f"{meta_path.name} must declare one request and one response"
        )
    request_record = provenance.read_json(files["request"], "formal request")
    response_record = provenance.read_json(files["response"], "formal response")
    if (
        request_record.get("schema") != REQUEST_SCHEMA
        or response_record.get("schema") != RESPONSE_SCHEMA
    ):
        raise SchemaError("formal run artifacts carry an unexpected schema")

    ts = load_thresholds(
        state,
        THRESHOLD_SET,
        _threshold_flags(
            solver_timeout_ms=solver_timeout_ms,
            max_states=max_states,
            max_formal_defects=max_formal_defects,
            min_excluded_fraction_of_applicable=min_excluded_fraction_of_applicable,
        ),
    )
    cr_set = _engine_thresholds(cr, ts)
    cr_request = request_record["coresearcher_request"]
    run_response = response_record["coresearcher_response"]
    stored = run_response.get("formalizer") or {}

    recomputed = True
    if cr_request.get("input_kind") == "prose" and not stored.get("raw_outputs"):
        # The run stopped before the gate (no model, endpoint down): there is
        # nothing to re-run offline. The run's non-verdict stands, recorded as such.
        response, exception_name, recomputed = (
            dict(run_response),
            response_record.get("exception"),
            False,
        )
    else:
        with cr["thresholds"].using(cr_set), _sockets_refused():
            response = cr["pipeline"].compute(
                cr_request,
                clients=None,
                raw_outputs=stored.get("raw_outputs"),
                specs=stored.get("specs"),
            )
        exception = response.pop("_exception", None)
        exception_name = type(exception).__name__ if exception is not None else None
        if exception is not None and getattr(exception, "endpoint", False):
            exception_name = "EndpointUnavailable"

    if recomputed:
        comparison = _compare(cr, run_response, response)
    else:
        comparison = {
            "reproduces_run": None,
            "reports_compared": 0,
            "mismatches": [],
            "engine_changes": [],
        }
    comparison["thresholds_match_run"] = (
        sidecar.get("thresholds_applied") == ts.applied()
    )

    relays = _relays_from(response)
    if comparison["reproduces_run"] is False:
        relays.append(
            provenance.relay(
                "formal.not_reproduced",
                provenance.RELAY_CODES["formal.not_reproduced"]
                + " Mismatches: "
                + "; ".join(comparison["mismatches"][:5]),
            )
        )

    source_rel = project.relative(files["response"])
    source_sha = provenance.sha256_file(files["response"])
    criteria = _criteria(response, ts)
    metrics = cr["pipeline"].metrics(response)
    metrics["defect_count"] = criteria["max_formal_defects"]["value"]
    assessment = {
        "formal_status": response["formal_status"],
        "reason": response.get("reason") or "",
        "hypothesis_id": request_record["hypothesis"]["id"],
        "transport": request_record.get("transport"),
        "verdict": cr["pipeline"].verdict(response),
        "criteria": criteria,
        "evidence_assessment": _evidence_mapping(
            response, criteria, ts, source_rel, source_sha
        ),
        "reproduction": comparison,
        "reports": response["reports"],
        "formalization_gate": response.get("formalization_gate"),
        "formal_hypothesis": response.get("formal_hypothesis"),
        "lean": response.get("lean") or [],
        "coresearcher": {
            "engine_version": cr["provenance"].engine_version(),
            "z3_version": cr["provenance"].z3_version(),
            **cr_set.record(),
        },
    }

    analysis_path = beside_or_out(
        state, meta_path, meta_path.name.replace(".meta.json", ".analysis.json"), out
    )
    provenance.write_analysis(
        analysis_path,
        source=files["response"],
        threshold_set=ts.tag,
        thresholds_applied=ts.applied(),
        threshold_sources=ts.sources(),
        threshold_provenance=ts.provenance,
        unresolved=ts.unresolved(),
        metrics=metrics,
        assessment=assessment,
        mandatory_relays=relays,
        suppress_warnings=as_json,
        capability_state=_capability_state(cr),
    )

    emit = Emitter(as_json=as_json, quiet=quiet)
    emit.data(
        "assessment",
        {
            k: assessment[k]
            for k in (
                "formal_status",
                "verdict",
                "criteria",
                "evidence_assessment",
                "reproduction",
            )
        },
    )
    emit.data("metrics", metrics)
    emit.data("mandatory_relays", relays)
    emit.data("threshold_set", ts.tag)
    emit.line(f"Hypothesis: {assessment['hypothesis_id']}  [threshold_set {ts.tag}]")
    emit.line(f"Verdict: {_verdict_line(response)}")
    gate = criteria["max_formal_defects"]
    emit.line(
        f"max_formal_defects: met={gate['met']} (defects={criteria['defects'] or 'none'})"
    )
    mapping = assessment["evidence_assessment"]
    emit.line(f"AR: {mapping['execution_outcome']} / {mapping['evidence_status']}")
    emit.line(f"Reproduces run: {comparison['reproduces_run']}")
    for change in comparison["engine_changes"]:
        emit.line(
            f"Engine changed since run: {change['field']} "
            f"{', '.join(change['run'])} -> {', '.join(change['analyze'])}"
        )
    if relays:
        emit.line(f"Relays: {', '.join(r['code'] for r in relays)}")
    emit.path(project.relative(analysis_path), "analysis")
    emit.flush()

    if comparison["reproduces_run"] is False and comparison["thresholds_match_run"]:
        raise FormalNotReproduced(
            "the analysis does not reproduce the run under the same thresholds",
            detail="; ".join(comparison["mismatches"][:3]),
            remedy="treat the run's verdict as unverified; re-run `oase formal run`",
        )
    _raise_for(response, exception_name)


# ---------------------------------------------------------------------------
# Capabilities (also reported by `oase doctor`)
# ---------------------------------------------------------------------------


def _capability_state(cr: dict[str, Any] | None) -> dict[str, str]:
    if cr is None:
        return {"coresearcher": "unavailable"}
    state = cr["cli"].capability_state()
    state["coresearcher"] = "available"
    return state


def capability_checks() -> list[tuple[str, bool, str, str, str]]:
    """(name, ok, detail, remedy, kind) for each formal capability.

    kind is "capability" when its absence makes a command refuse, and
    "caveat" when the command runs but the result reads differently.
    """
    checks: list[tuple[str, bool, str, str, str]] = []
    try:
        cr = _engine()
    except DependencyError as exc:
        checks.append(
            (
                "formal: coresearcher engine",
                False,
                exc.detail or exc.message,
                exc.remedy or "",
                "capability",
            )
        )
        return checks
    checks.append(
        (
            "formal: coresearcher engine",
            True,
            f"version {cr['provenance'].engine_version()}",
            "",
            "capability",
        )
    )
    z3_ok, detail = False, "z3-solver is not importable"
    try:
        import z3

        solver = z3.Solver()
        x = z3.Real("x")
        solver.add(x > 0, x < 1)
        z3_ok = solver.check() == z3.sat
        detail = f"z3 {z3.get_version_string()} ({'round trip ok' if z3_ok else 'round trip failed'})"
    except ImportError:
        pass
    checks.append(
        (
            "formal: z3 solver",
            z3_ok,
            detail,
            "" if z3_ok else "install z3-solver into the tools environment",
            "capability",
        )
    )
    lean = shutil.which("lean") or shutil.which("lake")
    lean_detail = "no Lean binary on PATH"
    if lean:
        try:
            result = subprocess.run(
                [lean, "--version"], capture_output=True, text=True, timeout=30
            )
            lean_detail = (result.stdout or result.stderr).strip().splitlines()[0]
        except (OSError, subprocess.SubprocessError, IndexError) as exc:
            lean_detail = f"{lean} could not run ({type(exc).__name__})"
    checks.append(
        (
            "formal: lean",
            bool(lean),
            lean_detail + "; theorems are stated, never kernel-checked by this tool",
            "",
            "caveat",
        )
    )
    configured = bool(
        os.environ.get("FORMALIZER_MODEL") or os.environ.get("FORMALIZER_GATE_MODELS")
    )
    checks.append(
        (
            "formal: formalizer model",
            configured,
            (
                "configured"
                if configured
                else "unconfigured: prose input is BLOCKED; --formal still works"
            ),
            "" if configured else "set FORMALIZER_MODEL (and FORMALIZER_BASE_URL)",
            "capability",
        )
    )
    url = os.environ.get("CORESEARCHER_URL")
    checks.append(
        (
            "formal: http transport",
            bool(url),
            url
            or "CORESEARCHER_URL unset: --transport http unavailable; package transport works",
            "",
            "caveat",
        )
    )
    return checks


@formal.command()
@output_options
def doctor(as_json: bool, quiet: bool) -> None:
    """Report the formal engine, z3, Lean and formalizer availability."""
    checks = capability_checks()
    emit = Emitter(as_json=as_json, quiet=quiet)
    emit.data(
        "checks",
        [
            {"name": n, "ok": ok, "detail": d, "remedy": r, "kind": k}
            for n, ok, d, r, k in checks
        ],
    )
    for name, ok, detail, _remedy, _kind in checks:
        emit.line(f"{'ok  ' if ok else 'warn'} {name}: {detail}")
    emit.flush()
    required = {"formal: coresearcher engine", "formal: z3 solver"}
    if not all(ok for name, ok, *_ in checks if name in required):
        raise DependencyError(
            "the formal engine cannot decide anything here",
            remedy="see the lines above",
        )
