"""
python/discovery/hypothesis_ledger.py - The obligation ledger as the standard path for a submitted hypothesis
(ADR-DISCOVERY-085, on ADR-076).

Method M5 of docs/architecture/VERIFICATION_METHODOLOGY.md: decompose into named obligations and discharge each one
independently. Every hypothesis evaluation (`POST /api/hypotheses/evaluate`, `coresearcher formal run` and
`formal analyze`, the verification chain) returns, beside its report, an ADR-076 ledger with these obligations:

| Obligation      | Statement                                                                   | Discharged by          |
|-----------------|-----------------------------------------------------------------------------|------------------------|
| fidelity        | The formal object says what the scientist's prose says (ADR-080)            | fidelity compare (z3)  |
| vacuity         | No declared non-witness satisfies the claims (ADR-080 intent probe)         | evaluator (exact)      |
| claim[i]        | Claim i is consistent with the rest and forbids some applicable state       | evaluator (exact)      |
| observations    | No recorded observation contradicts the hypothesis (only when given)        | evaluator (exact)      |
| cite[i]         | The i-th cited result is used validly: hypotheses entailed, conventions     | cite_check (ADR-083)   |
|                 | matched, entry active                                                       |                        |
| consequence[i]  | The i-th stated consequence or prediction is entailed by the hypothesis     | entailment (exact)     |

Statuses are those of ADR-076. Exact enumeration over the declared domains and z3 are decision procedures, so a
decided obligation is DISCHARGED_SYMBOLIC (in its stated scope) or REFUTED. A statement audit supplied by the caller
and not re-run here is CERTIFIED_BY_AUTHOR. Anything not decided stays OPEN with the reason: a missing fidelity spec,
no declared non-witness, an UNDECIDED solver, a formalization that did not pass its gate. A non-answer is never turned
into a discharge (ADR-068).

The roll-up is the weakest link (ADR-076): the ledger's claim, "the hypothesis as submitted is formally sound", is
never stronger than its weakest obligation. It is reported on the trust ladder (ADR-080) as the lowest rung of the
hypothesis's claims, capped at CLAIMED while a cited premise is retracted or downgraded (ADR-083).

The ledger is a view computed beside the reports, like `claim_trust`: it never changes a report's bytes, so stored
runs still reproduce. Scope: formal soundness only; provenance never decides validity.
"""

from __future__ import annotations

from dataclasses import asdict
from typing import Any, Dict, List, Optional, Tuple

from python.discovery import formal_status, formal_trust
from python.discovery.obligation_ledger import PROOF_STATUSES, Claim, Discharge, Obligation, Status

SCHEMA = "coresearcher.hypothesis_ledger/v1"
BY = "CoResearcher"
SOUND_CLAIM = "The hypothesis, as submitted, is formally sound"


# ---------------------------------------------------------------------------
# Citations: resolve once, check against the hypothesis's own context
# ---------------------------------------------------------------------------


def citing_context(hypothesis: Dict[str, Any], item: Dict[str, Any]) -> Dict[str, Any]:
    """Where the hypothesis uses a cited result: its variables and assumptions (and scope), unless the item gives one.

    The item's `conventions` are the hypothesis's conventions for that use (units, assay, population, sign, ...).
    """
    if isinstance(item.get("context"), dict):
        return dict(item["context"])
    assumptions = list(hypothesis.get("assumptions") or [])
    if hypothesis.get("scope"):
        assumptions.append(hypothesis["scope"])
    return {
        "variables": list(hypothesis.get("variables") or []),
        "assumptions": assumptions,
        "conventions": dict(item.get("conventions") or {}),
        "text": str(hypothesis.get("statement") or ""),
    }


def resolve_citations(items: List[Dict[str, Any]], registry) -> List[Dict[str, Any]]:
    """Replaces each `entry_id` (and optional `version`) by the registry entry itself, so the use can be re-checked
    offline. Items that already carry an `entry` are kept as they are."""
    resolved = []
    for i, item in enumerate(items or []):
        if not isinstance(item, dict):
            raise ValueError(f"citation {i} must be an object")
        out = {k: v for k, v in item.items() if k not in ("entry_id", "version")}
        if "entry" not in item:
            if not item.get("entry_id"):
                raise ValueError(f"citation {i} needs an entry_id or an inline entry")
            if registry is None:
                raise ValueError(f"citation {i} names {item['entry_id']!r} but no registry is available")
            out["entry"] = asdict(registry.get(item["entry_id"], item.get("version")))
        out.setdefault("source", f"citation {i}")
        resolved.append(out)
    return resolved


def check_citations(hypothesis: Dict[str, Any], items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """One ADR-083 cite_check per resolved citation, in order."""
    from python.discovery import cited_registry

    return [
        cited_registry.cite_check(cited_registry.RegistryEntry(**item["entry"]), citing_context(hypothesis, item))
        for item in items
    ]


# ---------------------------------------------------------------------------
# Obligations
# ---------------------------------------------------------------------------


def _scope(evaluation: Optional[Dict[str, Any]]) -> str:
    if evaluation and evaluation.get("backend") == "smt":
        return "the declared variables and bounds, decided by z3"
    return "the declared finite domains, by exhaustive enumeration"


def _discharge(status: Status, method: str, scope: str, report: Optional[Dict[str, Any]] = None,
               by: str = BY, **detail) -> Discharge:
    if report is not None and isinstance(report.get("provenance"), dict):
        detail["report_output_sha256"] = report["provenance"].get("output_sha256")
    return Discharge(status=status, method=method, scope=scope, by=by, detail=detail)


def _fidelity(fidelity: Optional[Dict[str, Any]], claim_trust: List[Dict[str, Any]], not_run: str) -> Obligation:
    ob = Obligation("fidelity", "The formal object says what the scientist's prose says (ADR-080)",
                    "the scientist's prose and the formal object", "fidelity")
    if fidelity is not None:
        if fidelity.get("formal_status") != formal_status.FormalStatus.DECIDED.value:
            ob.discharges.append(_discharge(Status.OPEN, "fidelity compare (ADR-070)", "the hypothesis range",
                                            fidelity, reason=f"fidelity is {fidelity.get('formal_status')}"))
            return ob
        relation = fidelity.get("relation")
        status = Status.DISCHARGED_SYMBOLIC if relation in formal_trust.AUDIT_ACCEPTS else Status.REFUTED
        ob.discharges.append(_discharge(status, "fidelity compare (ADR-070), z3", "the hypothesis range only "
                                        "(conclusions are not compared)", fidelity, relation=relation))
        return ob
    audited = [t for t in claim_trust if any(r["rung"] == "STATEMENT_AUDITED" and r["met"] for r in t["rungs"])]
    if claim_trust and len(audited) == len(claim_trust):
        ob.discharges.append(_discharge(
            Status.CERTIFIED_BY_AUTHOR, "statement audit records supplied with the request (not re-run here)",
            "every claim", by="caller", claims=[t["claim"] for t in audited]))
        return ob
    ob.discharges.append(_discharge(Status.OPEN, "none", "", reason=not_run or (
        "no fidelity spec and no statement audit; the scientist must confirm the formal object says what the prose "
        "meant")))
    return ob


def _vacuity(evaluation: Dict[str, Any]) -> Obligation:
    ob = Obligation("vacuity", "No state the hypothesis declares as a non-witness satisfies its claims (ADR-080)",
                    "hypothesis.non_witnesses", "intent probe")
    probe = evaluation.get("intent_probe") or {}
    declared = [p for p in probe.get("probes", []) if p.get("origin") == "declared"]
    defaults = probe.get("default_probes_satisfied") or []
    if evaluation["content_verdict"] == "VACUOUS_RELATIVE_TO_INTENT":
        ob.discharges.append(_discharge(Status.REFUTED, "intent probe (exact)", _scope(evaluation), evaluation,
                                        satisfied=probe.get("declared_non_witnesses_satisfied")))
    elif declared and not probe.get("declared_non_witnesses_satisfied"):
        ob.discharges.append(_discharge(Status.DISCHARGED_SYMBOLIC, "intent probe (exact)", _scope(evaluation),
                                        evaluation, probes=[p["label"] for p in declared],
                                        default_probes_satisfied=defaults))
    elif declared:
        # A declared non-witness is satisfied but the verdict was VACUOUS or SELF_CONTRADICTORY, a stronger finding
        # that the claim obligations already record.
        ob.discharges.append(_discharge(Status.OPEN, "intent probe (exact)", _scope(evaluation), evaluation,
                                        reason=f"superseded by the verdict {evaluation['content_verdict']}"))
    else:
        ob.discharges.append(_discharge(Status.OPEN, "none", "", reason=(
            "no non-witnesses declared; only the author knows which trivial objects the claims must exclude"),
            default_probes_satisfied=defaults))
    return ob


def _claims(hypothesis: Dict[str, Any], evaluation: Dict[str, Any]) -> List[Obligation]:
    verdict = (evaluation.get("intent_probe") or {}).get("base_verdict") or evaluation["content_verdict"]
    out = []
    for i, claim in enumerate(hypothesis.get("claims") or []):
        ob = Obligation(f"claim[{i}]", f"Claim {claim!r} is consistent with the other claims, the scope and the "
                        "assumptions, and forbids at least one applicable state", f"hypothesis.claims[{i}]",
                        "consistency and falsifiability")
        if verdict == "VACUOUS":
            ob.discharges.append(_discharge(Status.REFUTED, "exact evaluation", _scope(evaluation), evaluation,
                                            reason="no state satisfies the scope and assumptions",
                                            conflicts=evaluation.get("conflicting_assumption_sets")))
        elif verdict == "SELF_CONTRADICTORY":
            ob.discharges.append(_discharge(Status.REFUTED, "exact evaluation", _scope(evaluation), evaluation,
                                            reason="every applicable state violates some claim"))
        elif claim not in (evaluation.get("claims_with_content") or []):
            ob.discharges.append(_discharge(Status.REFUTED, "exact evaluation", _scope(evaluation), evaluation,
                                            reason="the claim forbids no applicable state: no observation could "
                                            "refute it. It holds wherever the scope and assumptions hold, so it "
                                            "follows from them; a guarantee derived from premises belongs in "
                                            "`consequences`, with the premises as claims"))
        else:
            ob.discharges.append(_discharge(Status.DISCHARGED_SYMBOLIC, "exact evaluation", _scope(evaluation),
                                            evaluation, forbids=(evaluation.get("claim_exclusions") or {}).get(claim)))
        out.append(ob)
    return out


def _observations(evaluation: Dict[str, Any]) -> Optional[Obligation]:
    if not evaluation.get("observations_checked"):
        return None
    ob = Obligation("observations", "No recorded observation contradicts the hypothesis", "request.observations",
                    "observation check")
    scope = "the recorded observations, as given (their truth is not judged here)"
    if evaluation.get("is_refuted"):
        ob.discharges.append(_discharge(Status.REFUTED, "exact evaluation", scope, evaluation,
                                        counterexamples=len(evaluation.get("certain_counterexamples") or [])))
    elif evaluation.get("possible_counterexamples"):
        ob.discharges.append(_discharge(Status.OPEN, "exact evaluation", scope, evaluation,
                                        reason="a partial observation has a completion the hypothesis forbids"))
    else:
        ob.discharges.append(_discharge(Status.DISCHARGED_SYMBOLIC, "exact evaluation", scope, evaluation))
    return ob


def _citation(i: int, check: Dict[str, Any], source: str) -> Obligation:
    from python.discovery import cited_registry

    ob = cited_registry.to_obligation(check, f"cite[{i}]", source)
    if not ob.discharges:
        ob.discharges.append(_discharge(Status.OPEN, "cite_check (ADR-083)", "the citing context", check,
                                        outcome=check["outcome"], findings=check["findings"], open=check["open"]))
    return ob


def _consequence(i: int, report: Dict[str, Any]) -> Obligation:
    ob = Obligation(f"consequence[{i}]", f"The prediction {report['consequence']!r} is entailed by the hypothesis",
                    f"request.consequences[{i}]", "entailment")
    scope = _scope(report)
    if report["vacuous"]:
        ob.discharges.append(_discharge(Status.OPEN, "exact entailment", scope, report,
                                        reason="entailed only vacuously: no applicable state is allowed"))
    elif report["entailed"]:
        ob.discharges.append(_discharge(Status.DISCHARGED_SYMBOLIC, "exact entailment", scope, report,
                                        follows_from_claims=report["follows_from_claims"]))
    else:
        ob.discharges.append(_discharge(Status.REFUTED, "exact entailment", scope, report,
                                        counterexamples=report["counterexamples"][:3]))
    return ob


def _open_all(ids: List[Tuple[str, str]], reason: str) -> List[Obligation]:
    out = []
    for oid, statement in ids:
        ob = Obligation(oid, statement, "request", "not evaluated")
        ob.discharges.append(_discharge(Status.OPEN, "none", "", reason=reason))
        out.append(ob)
    return out


def dag(obligations: List[Obligation]) -> Dict[str, Any]:
    """Dependency edges between obligations, checked acyclic with no missing premise (M5)."""
    ids = [o.id for o in obligations]
    claims = [i for i in ids if i.startswith("claim[")]
    edges = [[o, c] for o in ids if o == "vacuity" or o == "observations" or o.startswith(("consequence[", "probe:"))
             for c in claims]
    # A mechanistic chain (ADR-086): compatibility rests on every link and every link's sign.
    edges += [["mechanism:compatibility", i] for i in ids if i.startswith(("link[", "link_sign["))
              and "mechanism:compatibility" in ids]
    missing = sorted({b for _, b in edges if b not in ids})
    indegree = {i: 0 for i in ids}
    for a, _ in edges:
        indegree[a] += 1
    ready = [i for i, n in indegree.items() if n == 0]
    seen = 0
    while ready:
        node = ready.pop()
        seen += 1
        for a, b in edges:
            if b == node:
                indegree[a] -= 1
                if indegree[a] == 0:
                    ready.append(a)
    return {"edges": edges, "acyclic": seen == len(ids), "missing": missing}


# ---------------------------------------------------------------------------
# The ledger
# ---------------------------------------------------------------------------


def _rung(claim_trust: List[Dict[str, Any]], citations: List[Dict[str, Any]]) -> Tuple[str, List[str]]:
    caps = []
    rung = min((formal_trust.LADDER.index(formal_trust.TrustRung(t["rung"])) for t in claim_trust), default=0)
    fallen = [c["entry_id"] for c in citations if c.get("entry_status") != "ACTIVE"]
    if fallen:
        caps.append(f"capped at CLAIMED: cited premise(s) {fallen} are retracted or downgraded (ADR-083)")
        rung = 0
    return formal_trust.LADDER[rung].value, caps


def build(
    hypothesis: Optional[Dict[str, Any]],
    evaluation: Optional[Dict[str, Any]],
    consequences: Optional[List[Dict[str, Any]]] = None,
    citations: Optional[List[Dict[str, Any]]] = None,
    citation_sources: Optional[List[str]] = None,
    fidelity: Optional[Dict[str, Any]] = None,
    claim_trust: Optional[List[Dict[str, Any]]] = None,
    status: str = formal_status.FormalStatus.DECIDED.value,
    reason: str = "",
    requested_consequences: Optional[List[str]] = None,
    extra: Optional[List[Obligation]] = None,
) -> Dict[str, Any]:
    """The ADR-076 ledger of one hypothesis evaluation, with its weakest-link roll-up on the trust ladder.

    `extra` holds domain obligations decided elsewhere (the biomedical checks and mechanism links of ADR-086).
    With a non-verdict `status` (or no evaluation), every obligation is OPEN with that reason: nothing that was not
    decided is recorded as decided.
    """
    hypothesis = hypothesis or {}
    claim_trust = claim_trust or []
    consequences = consequences or []
    citations = citations or []
    sources = list(citation_sources or [])
    sources += [f"citation {i}" for i in range(len(sources), len(citations))]
    decided = status == formal_status.FormalStatus.DECIDED.value and evaluation is not None
    if decided:
        obligations = [_fidelity(fidelity, claim_trust, ""), _vacuity(evaluation), *_claims(hypothesis, evaluation)]
        observed = _observations(evaluation)
        if observed is not None:
            obligations.append(observed)
        obligations += [_citation(i, c, sources[i]) for i, c in enumerate(citations)]
        obligations += [_consequence(i, r) for i, r in enumerate(consequences)]
        obligations += list(extra or [])
    else:
        why = f"not evaluated: {status}" + (f" ({reason})" if reason else "")
        ids = [("fidelity", "The formal object says what the scientist's prose says (ADR-080)"),
               ("vacuity", "No state the hypothesis declares as a non-witness satisfies its claims (ADR-080)")]
        ids += [(f"claim[{i}]", f"Claim {c!r} is consistent and falsifiable")
                for i, c in enumerate(hypothesis.get("claims") or [])]
        ids += [(f"cite[{i}]", f"Use of {source} is valid") for i, source in enumerate(sources)]
        ids += [(f"consequence[{i}]", f"The prediction {c!r} is entailed by the hypothesis")
                for i, c in enumerate(requested_consequences or [])]
        ids += [(o.id, o.statement) for o in extra or []]
        obligations = _open_all(ids, why)
    claim = Claim(f"{hypothesis.get('hypothesis_id') or 'H'}:sound", SOUND_CLAIM, "the submitted hypothesis",
                  obligations)
    rolled = claim.status
    rung, caps = _rung(claim_trust, citations)
    weakest = [o.id for o in obligations if o.status == rolled]
    graph = dag(obligations)
    relays = [] if claim.is_proved else [formal_status.relay("LEDGER_NOT_PROVED")]
    return {
        "schema": SCHEMA,
        "hypothesis_id": hypothesis.get("hypothesis_id"),
        "formal_status": status if not decided else formal_status.FormalStatus.DECIDED.value,
        "claim": claim.to_dict(),
        "dag": graph,
        "rollup": {
            "status": rolled.value,
            "is_proved": claim.is_proved,
            "weakest": weakest,
            "refuted": [o.id for o in obligations if o.status == Status.REFUTED],
            "open": [o.id for o in obligations if o.status == Status.OPEN],
            "proved": [o.id for o in obligations if o.status in PROOF_STATUSES],
            "trust_rung": rung,
            "trust_caps": caps,
        },
        "mandatory_relays": relays,
        "scope_note": "Formal soundness of the submitted hypothesis only; sources and provenance never decide "
                      "validity, and a discharged obligation is about the formal object, not the world.",
    }


def for_response(request: Dict[str, Any], response: Dict[str, Any],
                 claim_trust: Optional[List[Dict[str, Any]]] = None,
                 extra: Optional[List[Obligation]] = None) -> Optional[Dict[str, Any]]:
    """The ledger of a formal pipeline response (`formal run`, `formal analyze`); None for statement checks."""
    if request.get("input_kind") not in ("formal", "prose"):
        return None
    reports = response.get("reports") or {}
    citations = reports.get("citations") or []
    sources = [c.get("source", f"citation {i}") for i, c in enumerate(request.get("citations") or [])]
    return build(
        response.get("formal_hypothesis") or request.get("hypothesis"),
        reports.get("evaluation"),
        reports.get("consequences"),
        citations,
        sources,
        reports.get("prose_fidelity"),
        claim_trust,
        response.get("formal_status", formal_status.FormalStatus.DECIDED.value),
        response.get("reason", ""),
        request.get("consequences"),
        extra,
    )

__all__ = ["build", "for_response", "check_citations", "resolve_citations", "citing_context", "dag", "SCHEMA"]
