"""
python/discovery/verification_chain.py - The composed verification chain for a submitted hypothesis (ADR-DISCOVERY-085).

Section 3 of docs/architecture/VERIFICATION_METHODOLOGY.md, run end to end as one flow:

    1. freeze        (M3)  freeze the acceptance criteria, or verify a freeze made earlier
    2. formalize     (M2)  prose -> independent readings that must agree (ADR-064); a formal object is SUPPLIED
    3. fidelity      (M1)  the formal object against the scientist's prose (ADR-070, ADR-080)
    4. vacuity       (M4)  declared non-witnesses (ADR-080)
    5. obligations   (M5)  the ADR-076 ledger, with its dependency DAG checked acyclic
    6. seams         (M6)  each cited result's use (ADR-083 cite_check)
    7. discharge     (M8)  every obligation discharged by the strongest exact tool, or left OPEN
    8. trust ladder  (M7)  the weakest-link roll-up, on the trust ladder

Every step reports a `state`: DONE (decided), OPEN (nothing decided, nothing failed), NOT_APPLICABLE, NOT_RUN, or a
non-verdict of the shared vocabulary (BLOCKED, UNDECIDED, INVALID_INPUT, FORMALIZATION_AMBIGUOUS,
FORMALIZATION_FAILED). A non-verdict stops the chain: the later steps are NOT_RUN and the chain's `formal_status` is
that non-verdict. No step turns a non-answer into an answer (M8).

Biomedical hypotheses (ADR-086). A request may carry a `mechanism` instead of a hypothesis or prose: nodes and signed
links, or a sentence of the controlled language ("A raises B, which drives C, which predicts D"), compiled by
`mechanistic_chain` into a two-world hypothesis whose end-to-end prediction is a consequence (formalize: COMPILED; a
sentence outside the grammar is FORMALIZATION_FAILED). A `biomedical` block adds units, conventions and domain probes
(`biomedical_domain`). Their obligations join the ledger: the probes are reported by the vacuity step, units and the
validated population by the seams step, the mechanism's links by the obligations step. A citation inherits the
hypothesis's conventions and the unit of the variable it names.

The freeze comes first. A freeze made earlier (`freeze.freeze_id`) is verified against the hypothesis and rivals that
are about to be evaluated, and a mismatch is BLOCKED. Without one, the chain freezes the criteria itself, before any
evaluation and without observations; the relay CRITERIA_FROZEN_IN_SAME_RUN says that this is weaker than a freeze on
an earlier date. For prose, the prose is frozen first as a document and the discriminating states of the accepted
reading are frozen right after the gate, still before evaluation.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from python.discovery import (
    biomedical_domain,
    formal_pipeline,
    formal_provenance,
    formal_status,
    formal_trust,
    freeze_service,
    hypothesis_ledger,
    mechanistic_chain,
    research_lifecycle,
)
from python.discovery.formal_hypothesis import FormalHypothesisError
from python.discovery.formal_status import FormalStatus

SCHEMA = "coresearcher.verification_chain/v1"
STEPS = (
    ("freeze", "M3"),
    ("formalize", "M2"),
    ("fidelity", "M1"),
    ("vacuity", "M4"),
    ("obligations", "M5"),
    ("seams", "M6"),
    ("discharge", "M8"),
    ("trust_ladder", "M7"),
)
DONE, OPEN, NOT_APPLICABLE, NOT_RUN = "DONE", "OPEN", "NOT_APPLICABLE", "NOT_RUN"
_NON_VERDICTS = {s.value for s in formal_status.NON_VERDICT}


class ChainInputError(ValueError):
    """The chain request is malformed (HTTP 422, CLI exit 9)."""


def _step(name: str, state: str, outcome: str, **detail) -> Dict[str, Any]:
    method = dict(STEPS)[name]
    return {"step": [n for n, _ in STEPS].index(name) + 1, "name": name, "method": method, "state": state,
            "outcome": outcome, "detail": detail}


def _ledger_state(status: str) -> str:
    return OPEN if status == "OPEN" else DONE


def _formal_request(spec: Dict[str, Any], hypothesis: Dict[str, Any], citations, freeze_ref) -> Dict[str, Any]:
    return formal_pipeline.make_request(
        hypothesis=hypothesis,
        hypothesis_id=spec.get("hypothesis_id") or "H",
        rivals=spec.get("rivals") or [],
        consequences=spec.get("consequences") or [],
        observations=spec.get("observations") or [],
        max_examples=int(spec.get("max_examples", 5)),
        backend=spec.get("backend", "auto"),
        default_probes=bool(spec.get("default_probes", False)),
        claim_evidence=spec.get("claim_evidence") or None,
        citations=citations or None,
        fidelity_spec=spec.get("fidelity_spec") or None,
        freeze=freeze_ref,
    )


def _freeze_step(ref: Dict[str, Any], check: Dict[str, Any]) -> Dict[str, Any]:
    state = DONE if check["status"] == freeze_service.VERIFIED else FormalStatus.BLOCKED.value
    return _step("freeze", state, check["status"], mode="preregistered", check=check,
                 record_sha256=(ref.get("record") or {}).get("sha256"))


def run(
    spec: Dict[str, Any],
    freezes: freeze_service.FreezeStore,
    registry=None,
    clients: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """Runs the chain on one hypothesis. Raises ChainInputError for a malformed request; returns non-verdicts."""
    if not isinstance(spec, dict) or sum(spec.get(k) is not None for k in ("hypothesis", "prose", "mechanism")) != 1:
        raise ChainInputError("Give exactly one of a formal hypothesis, prose and a mechanism.")
    try:
        domain_spec = biomedical_domain.validate(spec.get("biomedical"))
    except biomedical_domain.DomainSpecError as exc:
        raise ChainInputError(f"biomedical: {exc}") from exc
    compiled, not_in_grammar = None, None
    if spec.get("mechanism") is not None:
        try:
            compiled = mechanistic_chain.compile_mechanism(spec["mechanism"])
        except mechanistic_chain.ProseNotInGrammar as exc:
            not_in_grammar = exc
        except (mechanistic_chain.MechanismError, FormalHypothesisError) as exc:
            raise ChainInputError(f"mechanism: {exc}") from exc
        if compiled is not None:
            spec = dict(spec, hypothesis=compiled["hypothesis"],
                        consequences=list(spec.get("consequences") or []) + compiled["consequences"])
    try:
        citations = hypothesis_ledger.resolve_citations(
            biomedical_domain.fill_citations(spec.get("citations") or [], domain_spec), registry)
    except Exception as exc:  # Unknown entry, malformed item: the request is refused, nothing is evaluated.
        raise ChainInputError(f"citations: {exc}") from exc
    pre = spec.get("freeze") or {}
    author = (spec.get("author") or "").strip()
    if not pre.get("freeze_id") and not author:
        raise ChainInputError("Name the author of the acceptance criteria, or reference a freeze made earlier.")
    rivals = spec.get("rivals") or []
    steps: List[Dict[str, Any]] = []
    relays: List[str] = []
    freeze_ref: Optional[Dict[str, Any]] = None
    response: Optional[Dict[str, Any]] = None
    domain: Optional[Dict[str, Any]] = None
    hypothesis = spec.get("hypothesis")

    def stop(state: str, reason: str, ledger=None, claim_trust=None) -> Dict[str, Any]:
        done = {s["name"] for s in steps}
        for name, _ in STEPS:
            if name not in done:
                steps.append(_step(name, NOT_RUN, f"not run: an earlier step is {state}"))
        return _result(spec, steps, state, reason, freeze_ref, response, ledger, claim_trust, relays, domain)

    # 1. Freeze (and, for prose, 2. formalize, then freeze the accepted reading's criteria).
    try:
        if pre.get("freeze_id"):
            try:
                freeze_ref = freezes.reference(pre["freeze_id"], pre.get("expected_sha256"))
            except freeze_service.FreezeError as exc:
                steps.append(_step("freeze", FormalStatus.BLOCKED.value, freeze_service.UNKNOWN, mode="preregistered",
                                   reason=str(exc)))
                return stop(FormalStatus.BLOCKED.value, str(exc))
            if hypothesis is not None:
                check = freeze_service.check_reference(freeze_ref, hypothesis, rivals)
            else:  # The subject is checked once the prose has a formal reading.
                check = freeze_service.verify_embedded(freeze_ref["record"], freeze_ref["expected_sha256"])
            steps.append(_freeze_step(freeze_ref, check))
            if check["status"] != freeze_service.VERIFIED:
                return stop(FormalStatus.BLOCKED.value, "; ".join(check["problems"]))
            relays.append("CRITERIA_FROZEN")
        elif hypothesis is not None:
            record = freezes.freeze_hypothesis(hypothesis, rivals, author, spec.get("label", ""),
                                               spec.get("stated_criteria"), int(spec.get("max_examples", 5)),
                                               spec.get("backend", "auto"))
            freeze_ref = freezes.reference(record["id"])
            steps.append(_step("freeze", DONE, "FROZEN", mode="same_run", freeze_id=record["id"],
                               sha256=record["sha256"], author=record["author"], frozen_at=record["frozen_at"],
                               already_frozen=record["already_frozen"]))
            relays += ["CRITERIA_FROZEN", "CRITERIA_FROZEN_IN_SAME_RUN"]
        else:
            # Prose, or a mechanism whose sentence is outside the controlled language: frozen as a document.
            keys = ("prose", "hypothesis_id", "variable_schema", "rivals", "consequences", "stated_criteria")
            if not_in_grammar is not None:
                keys += ("mechanism",)
            document = research_lifecycle.canonical_bytes({k: spec.get(k) for k in keys})
            record = freezes.freeze_document(document, author, spec.get("label", ""), name="chain prose request")
            steps.append(_step("freeze", DONE, "FROZEN", mode="same_run_document", freeze_id=record["id"],
                               sha256=record["sha256"], author=record["author"], frozen_at=record["frozen_at"],
                               already_frozen=record["already_frozen"]))
            relays += ["CRITERIA_FROZEN_IN_SAME_RUN"]
    except freeze_service.FreezeError as exc:
        raise ChainInputError(str(exc)) from exc
    except Exception as exc:
        state = formal_status.classify(exc).value  # Re-raises anything that is not a known non-verdict.
        steps.append(_step("freeze", state, "not frozen", reason=f"{type(exc).__name__}: {exc}"))
        return stop(state, f"{type(exc).__name__}: {exc}")

    # 2. Formalize.
    if not_in_grammar is not None:
        state = FormalStatus.FORMALIZATION_FAILED.value
        steps.append(_step("formalize", state, "NOT_IN_GRAMMAR", reason=str(not_in_grammar)))
        return stop(state, str(not_in_grammar))
    if compiled is not None:
        steps.append(_step("formalize", DONE, "COMPILED", encoding=compiled["encoding"],
                           reader=(compiled["parse"] or {}).get("reader", "structured links (no prose to read)"),
                           links=[[link["from"], link["to"], s["sign"]] for link, s in
                                  zip(compiled["links"], compiled["link_signs"])],
                           prediction=compiled["consequences"],
                           note="a deterministic compilation of the stated links; fidelity to the scientist's "
                                "intent still needs a fidelity spec or a statement audit"))
    elif hypothesis is not None:
        steps.append(_step("formalize", DONE, "SUPPLIED",
                           note="the caller supplied the formal object; there are no readings to compare"))
    else:
        gate_request = formal_pipeline.make_request(prose=spec["prose"], hypothesis_id=spec.get("hypothesis_id") or "H",
                                                    variable_schema=spec.get("variable_schema"),
                                                    samples=spec.get("samples"))
        try:
            gate = formal_pipeline.formalize(gate_request, clients)
        except Exception as exc:
            state = formal_status.classify(exc).value
            steps.append(_step("formalize", state, "no reading", reason=f"{type(exc).__name__}: {exc}"))
            return stop(state, f"{type(exc).__name__}: {exc}")
        gate_dict = gate.to_dict()
        if not gate.passes:
            state = gate.formal_status.value
            steps.append(_step("formalize", state, gate_dict["status"], gate=gate_dict))
            return stop(state, gate.reason)
        hypothesis = gate.formalization.data
        relays += [r["code"] for r in gate.mandatory_relays]
        detail: Dict[str, Any] = {"gate": gate_dict}
        try:
            if freeze_ref is not None:  # A freeze made earlier: the accepted reading must be the frozen subject.
                check = freeze_service.check_reference(freeze_ref, hypothesis, rivals)
                detail["freeze_check"] = check
                if check["status"] != freeze_service.VERIFIED:
                    steps.append(_step("formalize", FormalStatus.BLOCKED.value, "READING_NOT_FROZEN", **detail))
                    return stop(FormalStatus.BLOCKED.value, "; ".join(check["problems"]))
            else:
                record = freezes.freeze_hypothesis(hypothesis, rivals, author, spec.get("label", ""),
                                                   spec.get("stated_criteria"), int(spec.get("max_examples", 5)),
                                                   spec.get("backend", "auto"))
                freeze_ref = freezes.reference(record["id"])
                detail["criteria_freeze"] = {"freeze_id": record["id"], "sha256": record["sha256"]}
                relays.append("CRITERIA_FROZEN")
        except Exception as exc:
            state = formal_status.classify(exc).value
            steps.append(_step("formalize", state, gate_dict["status"], reason=f"{type(exc).__name__}: {exc}"))
            return stop(state, f"{type(exc).__name__}: {exc}")
        steps.append(_step("formalize", DONE, gate_dict["status"], **detail))

    # Evaluation, consequences, citations and fidelity: one formal pipeline computation, which re-verifies the freeze.
    if freeze_ref is not None and freeze_ref["record"]["kind"] != freeze_service.HYPOTHESIS:
        freeze_ref = None  # A document freeze has no subject the evaluator can compare.
    try:
        request = _formal_request(spec, hypothesis, citations, freeze_ref)
    except ValueError as exc:
        raise ChainInputError(str(exc)) from exc
    response = formal_pipeline.compute(request)
    response.pop("_exception", None)
    location = None
    if spec.get("hypothesis") is not None and response["reports"]["evaluation"]:
        location = f"verification chain, input_sha256 {response['reports']['evaluation']['provenance']['input_sha256']}"
    claim_trust = formal_trust.for_claims(list(hypothesis.get("claims") or []), location, spec.get("claim_evidence"))
    extra = []
    if response["formal_status"] == FormalStatus.DECIDED.value and (spec.get("biomedical") or compiled):
        try:
            extra, domain = biomedical_domain.check(hypothesis, domain_spec, request["consequences"],
                                                    spec.get("backend", "auto"), compiled)
        except (biomedical_domain.DomainSpecError, FormalHypothesisError) as exc:
            raise ChainInputError(f"biomedical: {exc}") from exc
    ledger = hypothesis_ledger.for_response(request, response, claim_trust, extra)
    if response["formal_status"] != FormalStatus.DECIDED.value:
        steps.append(_step("fidelity", response["formal_status"], "not evaluated", reason=response["reason"]))
        return stop(response["formal_status"], response["reason"], ledger, claim_trust)

    obligations = {o["id"]: o for o in ledger["claim"]["obligations"]}
    reports = response["reports"]
    fid = obligations["fidelity"]
    fid_state = _ledger_state(fid["status"])
    if reports.get("prose_fidelity") and reports["prose_fidelity"]["formal_status"] != FormalStatus.DECIDED.value:
        fid_state = reports["prose_fidelity"]["formal_status"]
    steps.append(_step("fidelity", fid_state, fid["status"], discharges=fid["discharges"]))
    if fid_state in _NON_VERDICTS:
        return stop(fid_state, "fidelity was not decided", ledger, claim_trust)
    vac = obligations["vacuity"]
    probes = [o for i, o in obligations.items() if i.startswith("probe:") and i != "probe:population"]
    if not probes:
        steps.append(_step("vacuity", _ledger_state(vac["status"]), vac["status"], discharges=vac["discharges"]))
    else:
        statuses = [vac["status"]] + [o["status"] for o in probes]
        state = DONE if "REFUTED" in statuses or "OPEN" not in statuses else OPEN
        steps.append(_step("vacuity", state, "; ".join([f"vacuity {vac['status']}"] +
                                                        [f"{o['id']} {o['status']}" for o in probes]),
                           discharges=vac["discharges"], probes={o["id"]: o for o in probes}))
    graph = ledger["dag"]
    graph_ok = graph["acyclic"] and not graph["missing"]
    mech = {i: o["status"] for i, o in obligations.items() if i.startswith(("link[", "link_sign[", "mechanism:"))}
    steps.append(_step("obligations", DONE if graph_ok else FormalStatus.INVALID_INPUT.value,
                       f"{len(obligations)} obligations; DAG {'acyclic, no missing premise' if graph_ok else 'invalid'}",
                       ids=list(obligations), dag=graph, **({"mechanism": mech} if mech else {})))
    if not graph_ok:
        return stop(FormalStatus.INVALID_INPUT.value, "the obligation graph is not a DAG", ledger, claim_trust)
    cites = reports.get("citations") or []
    domain_seams = [i for i in ("units", "probe:population") if i in obligations]
    if not cites and not domain_seams:
        steps.append(_step("seams", NOT_APPLICABLE, "no cited results declared"))
    else:
        outcomes = [c["outcome"] for c in cites]
        undecided = "INCOMPLETE" in outcomes
        detail: Dict[str, Any] = {"checks": [{k: c[k] for k in ("entry_id", "entry_version", "entry_status",
                                                               "outcome", "findings", "open")} for c in cites]}
        if "units" in domain_seams:
            unit_outcome = domain["units"]["outcome"]
            outcomes.append(f"units {unit_outcome}")
            undecided = undecided or unit_outcome == "INCOMPLETE"
            detail["units"] = domain["units"]
        if "probe:population" in domain_seams:
            pop = domain["population"]
            outcomes.append(f"population {pop.get('outcome')}")
            undecided = undecided or pop.get("outcome") not in ("APPLIES_OUTSIDE_VALIDATED_POPULATION",
                                                                "INSIDE_VALIDATED_POPULATION")
            detail["population"] = pop
        steps.append(_step("seams", OPEN if undecided else DONE, ", ".join(outcomes), **detail))
    counts = {k: v for k, v in ledger["claim"]["counts"].items() if v}
    steps.append(_step("discharge", DONE, ", ".join(f"{v} {k}" for k, v in counts.items()), counts=counts,
                       refuted=ledger["rollup"]["refuted"], open=ledger["rollup"]["open"]))
    roll = ledger["rollup"]
    steps.append(_step("trust_ladder", DONE, f"{roll['status']} at {roll['trust_rung']}", rollup=roll))
    return _result(spec, steps, FormalStatus.DECIDED.value, "", freeze_ref, response, ledger, claim_trust, relays,
                   domain)


def _result(spec, steps, status, reason, freeze_ref, response, ledger, claim_trust, relays, domain=None
            ) -> Dict[str, Any]:
    codes = list(relays)
    if response is not None:
        codes += [r["code"] for r in response.get("mandatory_relays", [])]
    if claim_trust:
        codes += [r["code"] for r in formal_trust.relays(claim_trust)]
    if ledger is not None:
        codes += [r["code"] for r in ledger["mandatory_relays"]]
    steps = sorted(steps, key=lambda s: s["step"])
    body = {
        "schema": SCHEMA,
        "formal_status": status,
        "reason": reason,
        # The weakest-link roll-up; with a non-verdict it is OPEN, never a verdict.
        "outcome": ledger["rollup"]["status"] if ledger else None,
        "trust_rung": ledger["rollup"]["trust_rung"] if ledger else None,
        "steps": steps,
        "freeze": freeze_ref,
        "response": response,
        "obligation_ledger": ledger,
        "claim_trust": claim_trust,
        **({"domain": domain} if domain is not None else {}),
        "mandatory_relays": formal_status.relays(codes),
        "scope_note": "Formal soundness only. A freeze fixes the criteria; it does not judge them. Provenance and "
                      "sources never decide validity.",
    }
    body["provenance"] = formal_provenance.build("verification_chain", {"chain": spec}, dict(body), backend=None)
    return body


def summary(result: Dict[str, Any]) -> str:
    """One line per step, for the CLI."""
    lines = [f"{s['step']}. {s['name']} ({s['method']}): {s['state']} - {s['outcome']}" for s in result["steps"]]
    lines.append(f"chain: {result['formal_status']}; outcome {result.get('outcome')}; rung {result.get('trust_rung')}")
    return "\n".join(lines)


__all__ = ["run", "summary", "ChainInputError", "STEPS", "SCHEMA"]
