"""
Scientific Program Schema - Sprint 29
Represents a coherent scientific program from grouped artifacts.
"""

from __future__ import annotations

from dataclasses import dataclass, field, asdict
from datetime import datetime
from typing import Optional, List, Dict


@dataclass
class Contributor:
    name: str
    orcid: Optional[str] = None
    github: Optional[str] = None
    affiliation: Optional[str] = None

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class Workstream:
    name: str
    signals: List[str] = field(default_factory=list)
    related_artifact_ids: List[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class Program:
    program_id: str
    name: str = ""
    description: str = ""
    timeline: Dict = field(default_factory=dict)
    artifacts: Dict = field(default_factory=dict)
    contributors: List[Contributor] = field(default_factory=list)
    workstreams: List[Workstream] = field(default_factory=list)
    comprehension_summary: str = ""
    updated_at: str = field(default_factory=lambda: datetime.now().isoformat())

    def to_dict(self) -> dict:
        data = asdict(self)
        data["contributors"] = [c.to_dict() for c in self.contributors]
        data["workstreams"] = [w.to_dict() for w in self.workstreams]
        return data