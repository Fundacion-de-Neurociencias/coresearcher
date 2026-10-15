"""
Initiative and Workstream Schemas - Sprint 32
Precise terminology for scientific activity reconstruction.
"""

from __future__ import annotations

from dataclasses import dataclass, field, asdict
from datetime import datetime
from typing import Optional, List, Dict


@dataclass
class Workstream:
    workstream_id: str
    name: str = ""
    description: str = ""
    signals: List[str] = field(default_factory=list)
    related_artifact_ids: List[str] = field(default_factory=list)
    contributors: List[str] = field(default_factory=list)
    repositories: List[str] = field(default_factory=list)
    updated_at: str = field(default_factory=lambda: datetime.now().isoformat())

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class Initiative:
    initiative_id: str
    name: str = ""
    description: str = ""
    mission: str = ""
    workstreams: List[Workstream] = field(default_factory=list)
    contributors: List[str] = field(default_factory=list)
    repositories: List[str] = field(default_factory=list)
    updated_at: str = field(default_factory=lambda: datetime.now().isoformat())

    def to_dict(self) -> dict:
        data = asdict(self)
        data["workstreams"] = [w.to_dict() for w in self.workstreams]
        return data