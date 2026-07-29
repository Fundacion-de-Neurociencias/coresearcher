"""
Scientific Activity Ledger - Sprint 33
Verifiable, navigable reconstruction of scientific project history.
"""

from __future__ import annotations

from dataclasses import dataclass, field, asdict
from datetime import datetime
from typing import Optional, List, Dict


@dataclass
class LedgerContributor:
    name: str
    github: Optional[str] = None
    orcid: Optional[str] = None
    affiliation: Optional[str] = None
    contribution_count: int = 0

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class LedgerWorkstream:
    workstream_id: str
    name: str = ""
    signals: List[str] = field(default_factory=list)
    related_artifact_count: int = 0
    contributor_count: int = 0

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class ScientificLedger:
    ledger_id: str
    name: str = ""
    description: str = ""
    timeline: Dict = field(default_factory=dict)
    artifacts: List[Dict] = field(default_factory=list)
    workstreams: List[LedgerWorkstream] = field(default_factory=list)
    contributors: List[LedgerContributor] = field(default_factory=list)
    comprehension_summary: str = ""
    generated_at: str = field(default_factory=lambda: datetime.now().isoformat())
    scientific_unit: str = "investigatable_claim"
    unit_rationale: str = ""

    def to_dict(self) -> dict:
        data = asdict(self)
        data["workstreams"] = [w.to_dict() for w in self.workstreams]
        data["contributors"] = [c.to_dict() for c in self.contributors]
        return data
