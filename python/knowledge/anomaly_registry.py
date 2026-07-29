"""
Anomaly Registry - Sprint 21: Einstein Generator
Scientific anomalies as primary discovery assets.

An anomaly is a pattern that deviates from expected scientific consensus:
- High-trust claim + Low-trust claim about the same entity
- Unexpected correlation or missing correlation
- Statistical outlier in meta-analysis
- Result that contradicts established theory
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Optional, List, Dict
from datetime import datetime

# Security tier: COMMUNITY — DO NOT MODIFY
# See python/_tiers.py for classification
SECURITY_TIER = "COMMUNITY"


REGISTRY_DIR = Path("knowledge/registry")
REGISTRY_DIR.mkdir(parents=True, exist_ok=True)
ANOMALIES_FILE = REGISTRY_DIR / "anomalies.json"


class AnomalyRegistry:
    """
    Registry for scientific anomalies.
    
    Anomalies are the raw material for discovery:
    Anomaly → Contradiction → Thought Experiment → Hypothesis
    
    Example:
    {
        "id": "ANOMALY-000001",
        "type": "trust_gap",
        "entity": "pTau217",
        "high_trust_claim": "CLAIM-000001",
        "low_trust_claim": "CLAIM-000002",
        "trust_gap": 0.65,
        "domain": "neurodegeneration",
        "status": "active",
        "generated_hypotheses": ["HYP-001"],
        "createdAt": "..."
    }
    """
    
    ANOMALY_TYPES = [
        "trust_gap",           # High trust + Low trust on same entity
        "statistical_outlier",  # Result far from expected distribution
        "missing_correlation",  # Expected correlation not found
        "unexpected_correlation", # Unexpected correlation found
        "replication_failure",  # Known result failed to replicate
        "population_effect",    # Effect only in specific subpopulation
        "temporal_anomaly",     # Trend changes over time
    ]
    
    def __init__(self):
        self._anomalies: dict = self._load()
    
    def _load(self) -> dict:
        """Load anomalies from disk."""
        if ANOMALIES_FILE.exists():
            with open(ANOMALIES_FILE, 'r') as f:
                return json.load(f)
        return {"anomalies": {}, "next_id": 1}
    
    def _save(self):
        """Save anomalies to disk."""
        with open(ANOMALIES_FILE, 'w') as f:
            json.dump(self._anomalies, f, indent=2)
    
    def register(self,
                 anomaly_type: str,
                 entity: str,
                 description: str,
                 high_trust_claim: str = None,
                 low_trust_claim: str = None,
                 trust_gap: float = None,
                 domain: str = "general",
                 evidence: List[dict] = None,
                 severity: float = 0.5,
                 metadata: dict = None) -> str:
        """
        Register a scientific anomaly.
        
        Returns:
            Anomaly ID (ANOMALY-XXXXXX)
        """
        anomaly_id = f"ANOMALY-{self._anomalies['next_id']:06d}"
        
        anomaly = {
            "id": anomaly_id,
            "type": anomaly_type,
            "entity": entity,
            "description": description,
            "highTrustClaim": high_trust_claim,
            "lowTrustClaim": low_trust_claim,
            "trustGap": trust_gap,
            "domain": domain,
            "evidence": evidence or [],
            "severity": severity,
            "status": "active",
            "generated_hypotheses": [],
            "generated_questions": [],
            "createdAt": datetime.now().isoformat(),
            "updatedAt": datetime.now().isoformat(),
            "metadata": metadata or {},
        }
        
        self._anomalies["anomalies"][anomaly_id] = anomaly
        self._anomalies["next_id"] += 1
        self._save()
        
        return anomaly_id
    
    def get(self, anomaly_id: str) -> Optional[dict]:
        """Get an anomaly by ID."""
        return self._anomalies["anomalies"].get(anomaly_id)
    
    def list(self) -> List[dict]:
        """List all anomalies."""
        return list(self._anomalies["anomalies"].values())
    
    def list_by_type(self, anomaly_type: str) -> List[dict]:
        """List anomalies by type."""
        return [
            a for a in self._anomalies["anomalies"].values()
            if a.get("type") == anomaly_type
        ]
    
    def list_by_domain(self, domain: str) -> List[dict]:
        """List anomalies by domain."""
        return [
            a for a in self._anomalies["anomalies"].values()
            if a.get("domain", "").lower() == domain.lower()
        ]
    
    def list_by_entity(self, entity: str) -> List[dict]:
        """List anomalies by entity."""
        return [
            a for a in self._anomalies["anomalies"].values()
            if a.get("entity", "").lower() == entity.lower()
        ]
    
    def link_hypothesis(self, anomaly_id: str, hypothesis_id: str):
        """Link a hypothesis generated from this anomaly."""
        anomaly = self._anomalies["anomalies"].get(anomaly_id)
        if anomaly:
            if hypothesis_id not in anomaly.get("generated_hypotheses", []):
                anomaly["generated_hypotheses"].append(hypothesis_id)
                anomaly["updatedAt"] = datetime.now().isoformat()
                self._save()
    
    def link_question(self, anomaly_id: str, question_id: str):
        """Link a question generated from this anomaly."""
        anomaly = self._anomalies["anomalies"].get(anomaly_id)
        if anomaly:
            if question_id not in anomaly.get("generated_questions", []):
                anomaly["generated_questions"].append(question_id)
                anomaly["updatedAt"] = datetime.now().isoformat()
                self._save()
    
    def resolve(self, anomaly_id: str, resolution: str):
        """Mark an anomaly as resolved with explanation."""
        anomaly = self._anomalies["anomalies"].get(anomaly_id)
        if anomaly:
            anomaly["status"] = "resolved"
            anomaly["resolution"] = resolution
            anomaly["updatedAt"] = datetime.now().isoformat()
            self._save()


# =============================================================================
# CLI Test
# =============================================================================

if __name__ == "__main__":
    print("=" * 70)
    print("Sprint 21: Anomaly Registry - Discovery Assets")
    print("=" * 70)
    
    registry = AnomalyRegistry()
    
    sample_anomalies = [
        {
            "anomaly_type": "trust_gap",
            "entity": "pTau217",
            "description": "pTau217 shows high predictive value in cohort studies but low replication in diverse populations",
            "high_trust_claim": "CLAIM-000001",
            "low_trust_claim": "CLAIM-000002",
            "trust_gap": 0.65,
            "domain": "neurodegeneration",
        },
        {
            "anomaly_type": "missing_correlation",
            "entity": "APOE4",
            "description": "APOE4 strongly predicts AD risk but shows no correlation with tau PET in some populations",
            "domain": "neurodegeneration",
        },
    ]
    
    for a in sample_anomalies:
        aid = registry.register(**a)
        print(f"\nRegistered: {aid}")
        print(f"  Type: {a['anomaly_type']}")
        print(f"  Entity: {a['entity']}")
    
    anomalies = registry.list()
    print(f"\n" + "=" * 70)
    print(f"Total anomalies: {len(anomalies)}")
    print("=" * 70)