"""
Scientific Activity Ledger - Sprint 33
Verifiable, navigable reconstruction of scientific project history.
"""

from __future__ import annotations

import hashlib
import json
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

    def record_epistemic_verdict(
        self,
        artifact_id: str,
        verdict_type: str,
        status: str,
        som_merkle_hash: str,
        details: Optional[Dict] = None,
        author: str = "CoResearcher Epistemic Engine",
    ) -> Dict:
        """
        Bridges the epistemic discovery engines (ADR-043 through ADR-049)
        directly with the Scientific Activity Ledger.
        Records an immutable epistemic verdict entry into the ledger's timeline and artifacts.
        """
        now_iso = datetime.now().isoformat()
        entry = {
            "artifact_id": artifact_id,
            "verdict_type": verdict_type,
            "status": status,
            "som_merkle_hash": som_merkle_hash,
            "author": author,
            "recorded_at": now_iso,
            "details": details or {},
        }
        self.artifacts.append(entry)

        # Update timeline
        date_key = now_iso.split("T")[0]
        if date_key not in self.timeline:
            self.timeline[date_key] = []
        self.timeline[date_key].append({
            "type": verdict_type,
            "id": artifact_id,
            "status": status,
            "hash": som_merkle_hash,
        })
        return entry

    def record_event(self, event_type: str, payload: Optional[Dict] = None) -> Dict:
        """Records a generic engine event as a ledger entry (used by the tournament, ERA and Socratic engines)."""
        body = payload or {}
        digest = hashlib.sha256(json.dumps(body, sort_keys=True, default=str).encode("utf-8")).hexdigest()
        artifact_id = str(body.get("tournament_id") or body.get("campaign_id") or body.get("question_id") or event_type)
        return self.record_epistemic_verdict(
            artifact_id=artifact_id,
            verdict_type=event_type,
            status="RECORDED",
            som_merkle_hash=f"sha256:{digest}",
            details=body,
        )

    def to_dict(self) -> dict:
        data = asdict(self)
        data["workstreams"] = [w.to_dict() for w in self.workstreams]
        data["contributors"] = [c.to_dict() for c in self.contributors]
        return data
