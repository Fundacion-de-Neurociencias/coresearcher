"""
python/discovery/formal_trust.py - The trust ladder: how far each formal claim has been checked (ADR-DISCOVERY-080).

"Formalized" is a per-claim status, not a label for a paper. Each claim stands on one of five rungs:

| Rung                     | Mechanical rule (each rung also needs every rung below it)                               |
|--------------------------|------------------------------------------------------------------------------------------|
| CLAIMED                  | Always: a claim exists. No formal statement is on record.                                |
| STATEMENT_PUBLIC         | A formal statement is on record: non-empty `text`, a `location`, and `sha256` equal to   |
|                          | the SHA-256 of the UTF-8 text.                                                           |
| STATEMENT_AUDITED        | An audit of that exact statement (`statement_sha256` matches) found the formal range     |
|                          | EQUIVALENT to or STRONGER than the paper's (ADR-070), with no unreviewed OPEN junk-value |
|                          | finding (`lint_open_unreviewed == 0`).                                                   |
| KERNEL_CHECKED           | A recorded Lean check of that statement: `status` exactly KERNEL_CHECKED (never          |
|                          | NOT_KERNEL_CHECKED), a `toolchain`, a 64-hex `file_sha256`, the matching                 |
|                          | `statement_sha256`, and `axioms` drawn only from the permitted set.                     |
| INDEPENDENTLY_REPRODUCED | A second recorded check that meets the same rules, by a named `checker` other than the   |
|                          | first one's.                                                                             |

The rules read only fields and digests, so the same evidence always gives the same rung, and the report says which
rule failed. A rung is never inferred from a related status: NOT_KERNEL_CHECKED, UNDECIDED or a missing field keeps
a claim where it is. Rungs are not skipped: a kernel check of a statement nobody audited stays at STATEMENT_PUBLIC.

This module grades evidence that is handed to it; it never runs Lean. It is complementary to a hand-kept claim
history (`trust_ladder.ClaimRecord`, ADR-081, where it exists): that one records dated steps for an announced
result, this one recomputes the rung of every claim from its evidence, for formal reports and the evidence graph.
"""

from __future__ import annotations

import re
from enum import Enum
from typing import Any, Dict, Iterable, List, Optional

from python.discovery import formal_provenance, formal_status

SCHEMA = "coresearcher.trust/v1"


class TrustRung(str, Enum):
    CLAIMED = "CLAIMED"
    STATEMENT_PUBLIC = "STATEMENT_PUBLIC"
    STATEMENT_AUDITED = "STATEMENT_AUDITED"
    KERNEL_CHECKED = "KERNEL_CHECKED"
    INDEPENDENTLY_REPRODUCED = "INDEPENDENTLY_REPRODUCED"


LADDER: List[TrustRung] = list(TrustRung)
# Lean's standard axioms. `sorryAx` (a `sorry`) and any project axiom keep a check below KERNEL_CHECKED.
PERMITTED_AXIOMS = ("propext", "Quot.sound", "Classical.choice")
# Fidelity relations that let a statement pass the audit: the formal statement asserts at least what the paper does.
AUDIT_ACCEPTS = ("EQUIVALENT", "STRONGER")
_HEX64 = re.compile(r"^[0-9a-f]{64}$")


def statement_sha256(text: str) -> str:
    """The digest a statement is pinned by: SHA-256 of its UTF-8 text."""
    return formal_provenance.sha256_bytes(text.encode("utf-8"))


def _nonempty_str(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def _statement_reasons(statement: Any) -> List[str]:
    if not isinstance(statement, dict):
        return ["no formal statement is on record"]
    reasons = []
    if not _nonempty_str(statement.get("text")):
        reasons.append("statement.text is missing")
    if not _nonempty_str(statement.get("location")):
        reasons.append("statement.location is missing")
    digest = statement.get("sha256")
    if not isinstance(digest, str) or not _HEX64.match(digest):
        reasons.append("statement.sha256 is missing or not a SHA-256")
    elif _nonempty_str(statement.get("text")) and digest != statement_sha256(statement["text"]):
        reasons.append("statement.sha256 does not match the statement text")
    return reasons


def _audit_reasons(audit: Any, pinned: Optional[str]) -> List[str]:
    if not isinstance(audit, dict):
        return ["no statement audit is on record"]
    reasons = []
    if audit.get("statement_sha256") != pinned:
        reasons.append("statement_audit.statement_sha256 does not match the pinned statement")
    fidelity = audit.get("fidelity")
    if fidelity not in AUDIT_ACCEPTS:
        reasons.append(f"statement_audit.fidelity is {fidelity!r}; the audit needs one of {list(AUDIT_ACCEPTS)}")
    open_findings = audit.get("lint_open_unreviewed")
    if isinstance(open_findings, bool) or not isinstance(open_findings, int):
        reasons.append("statement_audit.lint_open_unreviewed is missing (run the junk-value lint)")
    elif open_findings != 0:
        reasons.append(f"{open_findings} junk-value finding(s) are OPEN without a review note")
    return reasons


def kernel_check_reasons(check: Any, pinned: Optional[str], what: str = "kernel_check") -> List[str]:
    """Why a recorded Lean check does not count as a kernel check of the pinned statement (empty when it does)."""
    if not isinstance(check, dict):
        return [f"no {what} is on record"]
    reasons = []
    status = check.get("status")
    if status != TrustRung.KERNEL_CHECKED.value:
        if status == formal_status.FormalStatus.NOT_KERNEL_CHECKED.value:
            reasons.append(f"{what}.status is NOT_KERNEL_CHECKED: a stated theorem is not a kernel check")
        else:
            reasons.append(f"{what}.status is {status!r}, not KERNEL_CHECKED")
    if not _nonempty_str(check.get("toolchain")):
        reasons.append(f"{what}.toolchain is missing")
    digest = check.get("file_sha256")
    if not isinstance(digest, str) or not _HEX64.match(digest):
        reasons.append(f"{what}.file_sha256 is missing or not a SHA-256")
    if check.get("statement_sha256") != pinned:
        reasons.append(f"{what}.statement_sha256 does not match the pinned statement")
    axioms = check.get("axioms")
    if not isinstance(axioms, list) or not all(isinstance(a, str) for a in axioms):
        reasons.append(f"{what}.axioms is missing (record the output of #print axioms, even when empty)")
    else:
        extra = sorted(set(axioms) - set(PERMITTED_AXIOMS))
        if extra:
            reasons.append(f"{what} depends on axioms outside {list(PERMITTED_AXIOMS)}: {extra}")
    return reasons


def _reproduction_reasons(evidence: Dict[str, Any], pinned: Optional[str]) -> List[str]:
    first = (evidence.get("kernel_check") or {}).get("checker")
    if not _nonempty_str(first):
        return ["kernel_check.checker is missing, so independence cannot be decided"]
    reproductions = evidence.get("reproductions") or []
    if not isinstance(reproductions, list) or not reproductions:
        return ["no reproduction is on record"]
    reasons: List[str] = []
    for i, item in enumerate(reproductions):
        what = f"reproductions[{i}]"
        own = kernel_check_reasons(item, pinned, what)
        checker = item.get("checker") if isinstance(item, dict) else None
        if not _nonempty_str(checker):
            own.append(f"{what}.checker is missing")
        elif checker.strip() == first.strip():
            own.append(f"{what} was run by the first checker ({first!r}); it is not independent")
        if not own:
            return []
        reasons += own
    return reasons


def assess(evidence: Dict[str, Any]) -> Dict[str, Any]:
    """The rung of one claim from its evidence, with the rule that stopped it and what the next rung needs."""
    if not isinstance(evidence, dict) or not _nonempty_str(evidence.get("claim")):
        raise ValueError("Trust evidence needs a non-empty 'claim'.")
    statement = evidence.get("statement")
    pinned = statement.get("sha256") if isinstance(statement, dict) else None
    checks = {
        TrustRung.CLAIMED: [],
        TrustRung.STATEMENT_PUBLIC: _statement_reasons(statement),
        TrustRung.STATEMENT_AUDITED: _audit_reasons(evidence.get("statement_audit"), pinned),
        TrustRung.KERNEL_CHECKED: kernel_check_reasons(evidence.get("kernel_check"), pinned),
        TrustRung.INDEPENDENTLY_REPRODUCED: _reproduction_reasons(evidence, pinned),
    }
    rungs = []
    reached = TrustRung.CLAIMED
    blocked = False
    for rung in LADDER:
        reasons = list(checks[rung])
        if blocked:
            reasons = [f"needs {reached_next(reached).value} first"] + reasons
        met = not reasons
        rungs.append({"rung": rung.value, "met": met, "reasons": reasons})
        if met:
            reached = rung
        else:
            blocked = True
    following = reached_next(reached)
    lean_status = (
        formal_status.FormalStatus.DECIDED.value
        if LADDER.index(reached) >= LADDER.index(TrustRung.KERNEL_CHECKED)
        else formal_status.FormalStatus.NOT_KERNEL_CHECKED.value
    )
    return {
        "schema": SCHEMA,
        "claim": evidence["claim"],
        "rung": reached.value,
        "lean_status": lean_status,
        "next_rung": following.value if following is not reached else None,
        "next_rung_missing": checks[following] if following is not reached else [],
        "rungs": rungs,
        "statement_sha256": pinned,
    }


def reached_next(rung: TrustRung) -> TrustRung:
    """The rung above `rung` (the top rung is its own successor)."""
    index = LADDER.index(rung)
    return LADDER[min(index + 1, len(LADDER) - 1)]


def relays(assessments: Iterable[Dict[str, Any]]) -> List[Dict[str, str]]:
    """CLAIM_BELOW_KERNEL_CHECKED whenever some claim is below KERNEL_CHECKED."""
    below = [a for a in assessments if LADDER.index(TrustRung(a["rung"])) < LADDER.index(TrustRung.KERNEL_CHECKED)]
    return [formal_status.relay("CLAIM_BELOW_KERNEL_CHECKED")] if below else []


def audit_record(statement_text: str, fidelity: Dict[str, Any], lint: Optional[Dict[str, Any]]) -> Dict[str, Any]:
    """A `statement_audit` entry from a fidelity result and a lint report of the same statement (ADR-070).

    `fidelity` is a compare result (`relation`, `formal_status`); `lint` is a lint report whose OPEN findings without a
    review note are counted. Without a lint report the count is missing, so the audit does not pass.
    """
    record: Dict[str, Any] = {
        "statement_sha256": statement_sha256(statement_text),
        "fidelity": fidelity.get("relation"),
        "fidelity_output_sha256": (fidelity.get("provenance") or {}).get("output_sha256"),
    }
    if lint is not None:
        record["lint_open_unreviewed"] = sum(
            1 for f in lint.get("findings", []) if f.get("status") == "OPEN" and not f.get("review")
        )
        record["lint_output_sha256"] = (lint.get("provenance") or {}).get("output_sha256")
    return record


def for_claims(
    claims: Iterable[str],
    location: Optional[str],
    claim_evidence: Optional[Dict[str, Dict[str, Any]]] = None,
) -> List[Dict[str, Any]]:
    """Trust of the claims of a formal object CoResearcher evaluated.

    With a `location` (the formal object was supplied, and is pinned by the request digest), each claim's statement is
    its predicate text, pinned by its own SHA-256, so it starts at STATEMENT_PUBLIC. Without one (a formalizer draft),
    there is no statement of record and the claim stays CLAIMED. `claim_evidence` maps a claim to the audit, kernel
    check and reproductions recorded for it elsewhere; they are graded by the same rules.
    """
    out = []
    for claim in claims:
        evidence: Dict[str, Any] = {"claim": claim}
        if location:
            evidence["statement"] = {"text": claim, "location": location, "sha256": statement_sha256(claim)}
        extra = (claim_evidence or {}).get(claim) or {}
        for key in ("statement_audit", "kernel_check", "reproductions"):
            if key in extra:
                evidence[key] = extra[key]
        out.append(assess(evidence))
    return out


def for_response(request: Dict[str, Any], response: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Per-claim trust of a formal pipeline response (formal_pipeline.compute); empty when nothing was evaluated.

    Lean theorems the pipeline states are NOT_KERNEL_CHECKED, so they never lift a claim; only `claim_evidence` given
    in the request can.
    """
    evaluation = (response.get("reports") or {}).get("evaluation")
    hypothesis = response.get("formal_hypothesis")
    if not evaluation or not isinstance(hypothesis, dict):
        return []
    location = None
    if request.get("input_kind") == "formal":
        location = f"formal request, input_sha256 {evaluation['provenance']['input_sha256']}"
    return for_claims(hypothesis.get("claims", []), location, request.get("claim_evidence"))
