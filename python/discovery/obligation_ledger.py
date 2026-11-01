"""
python/discovery/obligation_ledger.py - Obligation ledger for claimed mathematical results (ADR-DISCOVERY-076).

A claimed result rests on obligations: identities, inequalities, analytic steps, imported theorems. The ledger records
each obligation, who discharged it, how, and over what scope, and rolls the statuses up to the claim. The roll-up is
the weakest link: a claim is never stronger than its least-checked obligation.

Statuses, strongest first. Only the first three are proofs.

- DISCHARGED_FORMAL: proved in a proof assistant whose kernel check was run.
- DISCHARGED_SYMBOLIC: an exact identity or decision procedure (CAS, SMT) proved it for all inputs in its domain.
- DISCHARGED_INTERVAL: rigorous interval arithmetic (outward rounding, branch and bound) proved it on the whole
  domain stated in the obligation. It rests on the correctness of the interval library.
- CHECKED_NUMERIC: independently evaluated on a bounded sample of its domain, with no violation found. Evidence, not a
  proof; the scope (ranges, resolution, precision) is mandatory.
- CERTIFIED_BY_AUTHOR: the source supplies its own certificate (program, appendix) that this ledger did not re-run.
- OPEN: no check recorded.
- REFUTED: a check found a violation. A refuted obligation refutes the claim as stated.

The ledger never converts CHECKED_NUMERIC or CERTIFIED_BY_AUTHOR into a proof status.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional


class Status(str, Enum):
    DISCHARGED_FORMAL = "DISCHARGED_FORMAL"
    DISCHARGED_SYMBOLIC = "DISCHARGED_SYMBOLIC"
    DISCHARGED_INTERVAL = "DISCHARGED_INTERVAL"
    CHECKED_NUMERIC = "CHECKED_NUMERIC"
    CERTIFIED_BY_AUTHOR = "CERTIFIED_BY_AUTHOR"
    OPEN = "OPEN"
    REFUTED = "REFUTED"


PROOF_STATUSES = {Status.DISCHARGED_FORMAL, Status.DISCHARGED_SYMBOLIC, Status.DISCHARGED_INTERVAL}
# Strength order for the weakest-link roll-up (REFUTED is handled separately: it dominates).
_RANK = [
    Status.DISCHARGED_FORMAL,
    Status.DISCHARGED_SYMBOLIC,
    Status.DISCHARGED_INTERVAL,
    Status.CHECKED_NUMERIC,
    Status.CERTIFIED_BY_AUTHOR,
    Status.OPEN,
]


@dataclass
class Discharge:
    status: Status
    method: str  # e.g. "sympy simplify", "mpmath 60+0.9x^2 digits on a grid"
    scope: str  # what exactly was covered; mandatory for CHECKED_NUMERIC
    by: str  # "CoResearcher" or the author
    margin: Optional[float] = None  # smallest observed slack, for numeric checks
    detail: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if self.status == Status.CHECKED_NUMERIC and not self.scope.strip():
            raise ValueError("a numeric check needs an explicit scope")


@dataclass
class Obligation:
    id: str
    statement: str
    source: str  # where the claim states it (section, label)
    kind: str  # identity | pointwise inequality | segment inequality | analytic step | import
    discharges: List[Discharge] = field(default_factory=list)

    @property
    def status(self) -> Status:
        if any(d.status == Status.REFUTED for d in self.discharges):
            return Status.REFUTED
        if not self.discharges:
            return Status.OPEN
        return min((d.status for d in self.discharges), key=_RANK.index)

    @property
    def independent(self) -> bool:
        """True when someone other than the author produced the strongest discharge."""
        best = self.status
        return any(d.status == best and d.by != "author" for d in self.discharges)

    def to_dict(self) -> Dict[str, Any]:
        return {
            **{k: v for k, v in asdict(self).items() if k != "discharges"},
            "status": self.status.value,
            "independent": self.independent,
            "discharges": [{**asdict(d), "status": d.status.value} for d in self.discharges],
        }


@dataclass
class Claim:
    id: str
    statement: str
    source: str
    obligations: List[Obligation] = field(default_factory=list)

    @property
    def status(self) -> Status:
        statuses = [o.status for o in self.obligations]
        if Status.REFUTED in statuses:
            return Status.REFUTED
        if not statuses:
            return Status.OPEN
        return max(statuses, key=_RANK.index)  # weakest link

    @property
    def is_proved(self) -> bool:
        return self.status in PROOF_STATUSES

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "statement": self.statement,
            "source": self.source,
            "status": self.status.value,
            "is_proved": self.is_proved,
            "obligations": [o.to_dict() for o in self.obligations],
            "counts": {s.value: sum(o.status == s for o in self.obligations) for s in Status},
        }
