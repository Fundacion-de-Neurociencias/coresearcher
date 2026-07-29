"""
Scientific Artifact Schema - Sprint 28
Primary scientific object for CoResearcher Observer.
"""

from __future__ import annotations

from dataclasses import dataclass, field, asdict
from datetime import datetime
from typing import Optional


@dataclass
class Contributor:
    name: str
    orcid: Optional[str] = None
    github: Optional[str] = None
    affiliation: Optional[str] = None

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class ScientificArtifact:
    artifact_id: str
    type: str  # software_release | paper | dataset | preprint | protocol | registered_study
    doi: Optional[str] = None
    title: str = ""
    github_repo: Optional[str] = None
    github_release: Optional[str] = None
    publication: Optional[str] = None
    contributors: list[Contributor] = field(default_factory=list)
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    updated_at: str = field(default_factory=lambda: datetime.now().isoformat())
    evidence_sources: list[str] = field(default_factory=list)
    citations: Optional[int] = None
    zenodo_record_id: Optional[str] = None
    openalex_work_id: Optional[str] = None
    crossref_doi: Optional[str] = None
    arxiv_id: Optional[str] = None
    osf_url: Optional[str] = None
    notes: str = ""

    def to_dict(self) -> dict:
        data = asdict(self)
        data["contributors"] = [c.to_dict() for c in self.contributors]
        return data

    @staticmethod
    def from_dict(data: dict) -> ScientificArtifact:
        contributors_data = data.get("contributors", [])
        contributors = []
        for c in contributors_data:
            if isinstance(c, dict):
                contributors.append(Contributor(**c))
            else:
                contributors.append(c)
        data["contributors"] = contributors
        return ScientificArtifact(**data)
