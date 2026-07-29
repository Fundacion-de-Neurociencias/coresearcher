"""
Failed Prediction Registry - Sprint 21: Einstein Generator
Failed predictions as learning assets for discovery.
"""

from __future__ import annotations
import json
from pathlib import Path
from typing import Optional, List
from datetime import datetime

# Security tier: COMMUNITY — DO NOT MODIFY
# See python/_tiers.py for classification
SECURITY_TIER = "COMMUNITY"


REGISTRY_DIR = Path("knowledge/registry")
REGISTRY_DIR.mkdir(parents=True, exist_ok=True)
FAILURES_FILE = REGISTRY_DIR / "failed_predictions.json"


class FailedPredictionRegistry:
    FAILURE_TYPES = [
        "hypothesis_falsified", "model_miscalibration",
        "replication_failure", "clinical_trial_failure",
        "observational_mismatch",
    ]

    def __init__(self):
        self._data: dict = self._load()

    def _load(self) -> dict:
        if FAILURES_FILE.exists():
            with open(FAILURES_FILE, 'r') as f:
                return json.load(f)
        return {"failures": {}, "next_id": 1}

    def _save(self):
        with open(FAILURES_FILE, 'w') as f:
            json.dump(self._data, f, indent=2)

    def register(self, failure_type: str, hypothesis_id: str,
                 hypothesis_text: str, predicted_outcome: str,
                 actual_outcome: str, discrepancy: str,
                 domain: str = "general", severity: float = 0.5,
                 derived_insights: List[str] = None,
                 metadata: dict = None) -> str:
        fid = f"FAILEDPRED-{self._data['next_id']:06d}"
        entry = {
            "id": fid, "type": failure_type,
            "hypothesisId": hypothesis_id,
            "hypothesisText": hypothesis_text,
            "predictedOutcome": predicted_outcome,
            "actualOutcome": actual_outcome,
            "discrepancy": discrepancy,
            "domain": domain, "severity": severity,
            "status": "active",
            "derivedInsights": derived_insights or [],
            "generated_questions": [],
            "createdAt": datetime.now().isoformat(),
            "updatedAt": datetime.now().isoformat(),
            "metadata": metadata or {},
        }
        self._data["failures"][fid] = entry
        self._data["next_id"] += 1
        self._save()
        return fid

    def get(self, fid: str) -> Optional[dict]:
        return self._data["failures"].get(fid)

    def list(self) -> List[dict]:
        return list(self._data["failures"].values())

    def list_by_domain(self, domain: str) -> List[dict]:
        return [f for f in self._data["failures"].values()
                if f.get("domain", "").lower() == domain.lower()]

    def add_insight(self, fid: str, insight: str):
        f = self._data["failures"].get(fid)
        if f and insight not in f.get("derivedInsights", []):
            f["derivedInsights"].append(insight)
            f["updatedAt"] = datetime.now().isoformat()
            self._save()

    def link_question(self, fid: str, question_id: str):
        f = self._data["failures"].get(fid)
        if f and question_id not in f.get("generated_questions", []):
            f["generated_questions"].append(question_id)
            f["updatedAt"] = datetime.now().isoformat()
            self._save()


if __name__ == "__main__":
    r = FailedPredictionRegistry()
    fid = r.register("clinical_trial_failure", "HYP-001",
                     "Amyloid reduction improves cognition",
                     "Cognitive improvement in 18 months",
                     "No significant cognitive improvement",
                     "Therapy cleared amyloid but cognition did not improve",
                     domain="neurodegeneration", severity=0.95)
    print(f"Registered {fid}")
    r.add_insight(fid, "Amyloid may be necessary but not sufficient for cognitive decline")