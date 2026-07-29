"""
Contradiction Registry - Sprint 21: Einstein Generator
Scientific contradictions as discovery signals.

A contradiction occurs when two claims about the same entity cannot both be true.
Contradictions are the seed for thought experiments and hypothesis generation.

Example:
{
    "id": "CONT-000001",
    "entity": "pTau217",
    "claimA": "CLAIM-000001",  # "High predictive value"
    "claimB": "CLAIM-000002",  # "Poor replication in diverse populations"
    "domain": "neurodegeneration",
    "type": "trust_gap_contradiction",
    "resolution": null,
}
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Optional, List, Dict
from datetime import datetime

# Security tier: PRIVATE — DO NOT MODIFY
# See python/_tiers.py for classification
SECURITY_TIER = "PRIVATE"


REGISTRY_DIR = Path("knowledge/registry")
REGISTRY_DIR.mkdir(parents=True, exist_ok=True)
CONTRADICTIONS_FILE = REGISTRY_DIR / "contradictions.json"


class ContradictionRegistry:
    """
    Registry for scientific contradictions.
    
    Contradictions are detected when claims conflict or have trust gaps.
    They serve as starting points for thought experiments.
    
    Flow:
    Contradiction → Thought Experiment → Hypothesis
    """
    
    CONTRA_TYPE_CHOICES = [
        "trust_gap_contradiction",    # One claim high trust, one low trust
        "direct_contradiction",       # Claims directly oppose each other
        "methodological_conflict",    # Different methods give different results
        "population_specific",          # Effect only in certain populations
        "temporal_conflict",          # Effect changes over time
    ]
    
    def __init__(self):
        self._contradictions: dict = self._load()
    
    def _load(self) -> dict:
        """Load contradictions from disk."""
        if CONTRADICTIONS_FILE.exists():
            with open(CONTRADICTIONS_FILE, 'r') as f:
                return json.load(f)
        return {"contradictions": {}, "next_id": 1}
    
    def _save(self):
        """Save contradictions to disk."""
        with open(CONTRADICTIONS_FILE, 'w') as f:
            json.dump(self._contradictions, f, indent=2)
    
    def register(self,
                 entity: str,
                 claim_a: str = None,
                 claim_b: str = None,
                 contradiction_type: str = "trust_gap_contradiction",
                 domain: str = "general",
                 description: str = None,
                 severity: float = 0.5,
                 metadata: dict = None) -> str:
        """
        Register a scientific contradiction.
        
        Returns:
            Contradiction ID (CONT-XXXXXX)
        """
        cont_id = f"CONT-{self._contradictions['next_id']:06d}"
        
        contradiction = {
            "id": cont_id,
            "entity": entity,
            "claimA": claim_a,
            "claimB": claim_b,
            "type": contradiction_type,
            "domain": domain,
            "description": description,
            "severity": severity,
            "status": "active",
            "resolved": False,
            "generated_hypotheses": [],
            "createdAt": datetime.now().isoformat(),
            "updatedAt": datetime.now().isoformat(),
            "metadata": metadata or {},
        }
        
        self._contradictions["contradictions"][cont_id] = contradiction
        self._contradictions["next_id"] += 1
        self._save()
        
        return cont_id
    
    def get(self, cont_id: str) -> Optional[dict]:
        """Get a contradiction by ID."""
        return self._contradictions["contradictions"].get(cont_id)
    
    def list(self) -> List[dict]:
        """List all contradictions."""
        return list(self._contradictions["contradictions"].values())
    
    def list_by_entity(self, entity: str) -> List[dict]:
        """List contradictions by entity."""
        return [
            c for c in self._contradictions["contradictions"].values()
            if c.get("entity", "").lower() == entity.lower()
        ]
    
    def list_by_domain(self, domain: str) -> List[dict]:
        """List contradictions by domain."""
        return [
            c for c in self._contradictions["contradictions"].values()
            if c.get("domain", "").lower() == domain.lower()
        ]
    
    def link_hypothesis(self, cont_id: str, hypothesis_id: str):
        """Link a hypothesis generated from this contradiction."""
        contradiction = self._contradictions["contradictions"].get(cont_id)
        if contradiction:
            if hypothesis_id not in contradiction.get("generated_hypotheses", []):
                contradiction["generated_hypotheses"].append(hypothesis_id)
                contradiction["updatedAt"] = datetime.now().isoformat()
                self._save()
    
    def resolve(self, cont_id: str, resolution: str, hypothesis_id: str = None):
        """Mark a contradiction as resolved with explanation."""
        contradiction = self._contradictions["contradictions"].get(cont_id)
        if contradiction:
            contradiction["status"] = "resolved"
            contradiction["resolved"] = True
            contradiction["resolution"] = resolution
            if hypothesis_id:
                contradiction["resolution_hypothesis"] = hypothesis_id
            contradiction["updatedAt"] = datetime.now().isoformat()
            self._save()


# =============================================================================
# CLI Test
# =============================================================================

if __name__ == "__main__":
    print("=" * 70)
    print("Sprint 21: Contradiction Registry - Discovery Signals")
    print("=" * 70)
    
    registry = ContradictionRegistry()
    
    sample_contradictions = [
        {
            "entity": "pTau217",
            "claim_a": "CLAIM-000001",
            "claim_b": "CLAIM-000002",
            "contradiction_type": "trust_gap_contradiction",
            "domain": "neurodegeneration",
            "description": "pTau217 shows high predictive value in cohort studies but poor replication in diverse populations",
            "severity": 0.75,
        },
        {
            "entity": "APOE4",
            "contradiction_type": "population_specific",
            "domain": "genomics",
            "description": "APOE4 effect on AD risk varies dramatically across ethnic groups",
            "severity": 0.6,
        },
    ]
    
    for cont in sample_contradictions:
        cid = registry.register(**cont)
        print(f"\nRegistered: {cid}")
        print(f"  Entity: {cont['entity']}")
        print(f"  Type: {cont['contradiction_type']}")
    
    contradictions = registry.list()
    print(f"\n" + "=" * 70)
    print(f"Total contradictions: {len(contradictions)}")
    print("=" * 70)