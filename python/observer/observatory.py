"""
Scientific Observatory — Sprint 38A.1
Observes external assets and extracts Learnings.
"""

from __future__ import annotations

from dataclasses import dataclass, field, asdict
from datetime import datetime
from typing import Optional, List


@dataclass
class ScientificObservation:
    """Observation of an external scientific asset."""
    observation_id: str
    asset_id: str
    observation_type: str  # longitudinal_cohort, benchmark, standard, publication, etc.
    signal: str  # short description of what was observed
    evidence: str  # raw evidence (URL, excerpt, metric)
    observed_at: str = field(default_factory=lambda: datetime.now().isoformat())
    notes: str = ""

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class ScientificLearning:
    """Knowledge extracted from observations."""
    learning_id: str
    observation_id: str
    insight: str  # what we learned
    architectural_impact: str  # how it shapes CoResearcher
    inspired_by: List[str] = field(default_factory=list)  # other learnings/assets
    applies_to: List[str] = field(default_factory=list)  # modules/systems affected
    recorded_at: str = field(default_factory=lambda: datetime.now().isoformat())

    def to_dict(self) -> dict:
        return asdict(self)