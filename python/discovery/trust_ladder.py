"""
python/discovery/trust_ladder.py - Trust-ladder statuses for announced formal results (ADR-DISCOVERY-081).

An announced result climbs five rungs. Each rung records what has been checked about the formal claim, never
whether the result is important or who deserves credit:

| Rung                     | Meaning                                                                       |
|--------------------------|-------------------------------------------------------------------------------|
| CLAIMED                  | Announced; no formal statement is public.                                     |
| STATEMENT_PUBLIC         | The formal statement is public and pinned (location and SHA-256).            |
| STATEMENT_AUDITED        | The statement was audited against a frozen checklist (`preregistration`).    |
| KERNEL_CHECKED           | A proof assistant kernel checked the proof here, with the axioms recorded.   |
| INDEPENDENTLY_REPRODUCED | A party other than the claimant reproduced the check or the construction.   |

Rules:
- A claim climbs one rung at a time, and each step needs its evidence (`REQUIRED_EVIDENCE`). Missing evidence is
  refused, not defaulted.
- STATEMENT_AUDITED records that the audit ran, not that it passed. Its outcome (for example
  VACUOUS_RELATIVE_TO_INTENT, or coverage rows marked OBJECT_DIFFERS) travels with the step.
- Below KERNEL_CHECKED the ADR-068 relay LEAN_NOT_KERNEL_CHECKED applies to any Lean theorem attached to the claim.
- A claim can move down (a withdrawn statement, a failed kernel check). The step is recorded with its reason; the
  history is never rewritten.
- The ladder is orthogonal to the obligation ledger (ADR-076): the ledger grades the proof's obligations, the
  ladder grades how far the formal claim itself has been checked.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from enum import Enum
from typing import Any, Dict, List

from python.discovery import formal_status


class Rung(str, Enum):
    CLAIMED = "CLAIMED"
    STATEMENT_PUBLIC = "STATEMENT_PUBLIC"
    STATEMENT_AUDITED = "STATEMENT_AUDITED"
    KERNEL_CHECKED = "KERNEL_CHECKED"
    INDEPENDENTLY_REPRODUCED = "INDEPENDENTLY_REPRODUCED"


ORDER = list(Rung)

REQUIRED_EVIDENCE: Dict[Rung, List[str]] = {
    Rung.CLAIMED: ["announcement", "announcement_sha256"],
    Rung.STATEMENT_PUBLIC: ["statement_location", "statement_sha256"],
    Rung.STATEMENT_AUDITED: ["checklist", "checklist_sha256", "audit_report", "audit_outcome"],
    Rung.KERNEL_CHECKED: ["toolchain", "axioms", "kernel_log_sha256", "checked_by"],
    Rung.INDEPENDENTLY_REPRODUCED: ["reproduced_by", "method", "record_sha256"],
}


class LadderError(ValueError):
    """A step skips a rung, lacks evidence, or claims independence it does not have."""


@dataclass
class Step:
    rung: str
    date: str  # ISO date of the step.
    reason: str
    evidence: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ClaimRecord:
    id: str
    claim: str  # The claim as announced, in the claimant's terms; it is not judged here.
    claimant: str
    scope_note: str = "Formal statement fidelity only; not credit, news or correctness of the proof."
    history: List[Step] = field(default_factory=list)

    @property
    def rung(self) -> Rung:
        if not self.history:
            raise LadderError("A claim record starts with a CLAIMED step.")
        return Rung(self.history[-1].rung)

    @property
    def formal_status(self) -> str:
        """ADR-068 status of any Lean theorem attached to the claim at this rung."""
        if ORDER.index(self.rung) < ORDER.index(Rung.KERNEL_CHECKED):
            return formal_status.FormalStatus.NOT_KERNEL_CHECKED.value
        return formal_status.FormalStatus.DECIDED.value

    @property
    def mandatory_relays(self) -> List[Dict[str, str]]:
        if self.formal_status == formal_status.FormalStatus.NOT_KERNEL_CHECKED.value:
            return [formal_status.relay("LEAN_NOT_KERNEL_CHECKED")]
        return []

    def _check_evidence(self, rung: Rung, evidence: Dict[str, Any]) -> None:
        missing = [k for k in REQUIRED_EVIDENCE[rung] if not evidence.get(k)]
        if missing:
            raise LadderError(f"{rung.value} needs evidence {missing}.")
        if rung is Rung.INDEPENDENTLY_REPRODUCED and evidence["reproduced_by"].strip() == self.claimant.strip():
            raise LadderError("Reproduction by the claimant is not independent.")

    def start(self, date: str, reason: str, evidence: Dict[str, Any]) -> "ClaimRecord":
        if self.history:
            raise LadderError("The record already has a history.")
        self._check_evidence(Rung.CLAIMED, evidence)
        self.history.append(Step(Rung.CLAIMED.value, date, reason, dict(evidence)))
        return self

    def climb(self, rung: Rung, date: str, reason: str, evidence: Dict[str, Any]) -> "ClaimRecord":
        if ORDER.index(rung) != ORDER.index(self.rung) + 1:
            raise LadderError(f"From {self.rung.value} the next rung is not {rung.value}; rungs are not skipped.")
        self._check_evidence(rung, evidence)
        self.history.append(Step(rung.value, date, reason, dict(evidence)))
        return self

    def descend(self, rung: Rung, date: str, reason: str) -> "ClaimRecord":
        if ORDER.index(rung) >= ORDER.index(self.rung):
            raise LadderError("descend() only moves down; use climb().")
        if not reason.strip():
            raise LadderError("A downgrade needs a reason.")
        self.history.append(Step(rung.value, date, reason, {"downgrade_from": self.rung.value}))
        return self

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "claim": self.claim,
            "claimant": self.claimant,
            "scope_note": self.scope_note,
            "rung": self.rung.value,
            "formal_status": self.formal_status,
            "mandatory_relays": self.mandatory_relays,
            "next_rung": ORDER[ORDER.index(self.rung) + 1].value if self.rung is not ORDER[-1] else None,
            "next_rung_needs": REQUIRED_EVIDENCE[ORDER[ORDER.index(self.rung) + 1]] if self.rung is not ORDER[-1] else [],
            "history": [asdict(s) for s in self.history],
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ClaimRecord":
        """Replays the history through start/climb/descend, so a stored record obeys the same rules."""
        record = cls(data["id"], data["claim"], data["claimant"], data.get("scope_note", cls.scope_note))
        for i, step in enumerate(data["history"]):
            rung = Rung(step["rung"])
            if i == 0:
                record.start(step["date"], step["reason"], step["evidence"])
            elif ORDER.index(rung) < ORDER.index(record.rung):
                record.descend(rung, step["date"], step["reason"])
            else:
                record.climb(rung, step["date"], step["reason"], step["evidence"])
        return record
