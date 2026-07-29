"""
Mechanism Registry - Sprint 23 Foundation
The core asset for Scientific Discovery OS.

Why mechanisms matter:
- Claims are observations: "pTau217 predicts AD"
- Findings are distillations: "pTau217 → amyloid (r=0.78)"
- Mechanisms are explanations: "pTau217 mediates neuronal stress response that triggers amyloid deposition through unknown pathway X"

This is where true discovery lives.
"""

import json
from pathlib import Path
from typing import Optional, List, Dict
from datetime import datetime

REGISTRY_DIR = Path("knowledge/registry")
REGISTRY_DIR.mkdir(parents=True, exist_ok=True)
MECHANISM_FILE = REGISTRY_DIR / "mechanisms.json"


class MechanismRegistry:
    """
    Registry for scientific mechanisms.
    
    A mechanism explains HOW something works, not just THAT it works.
    
    Structure:
    {
        "id": "MECH-000001",
        "name": "Neuronal Stress-Mediated Amyloid Deposition",
        "description": "Unknown pathway linking neuronal stress to amyloid production",
        "entities": ["pTau217", "stress response", "amyloid-beta"],
        "arrows": ["stress -> MECH-X -> amyloid"],
        "type": "causal_chain",  # causal_chain, feedback, threshold, compensatory
        "confidence": 0.3,  # Low for novel mechanisms
        "derived_from": ["FIND-00123", "CLAIM-00456"],
        "contradicts": ["MECH-000002"],
        "supports": ["MECH-000003"],
        "replications": 0,
        "challenges": 0,
        "institution_count": 0,
    }
    """
    
    def __init__(self):
        self._mechanisms: dict = self._load()
    
    def _load(self) -> dict:
        """Load mechanisms from disk."""
        if MECHANISM_FILE.exists():
            with open(MECHANISM_FILE, 'r') as f:
                return json.load(f)
        return {"mechanisms": {}, "next_id": 1}
    
    def _save(self):
        """Save mechanisms to disk."""
        with open(MECHANISM_FILE, 'w') as f:
            json.dump(self._mechanisms, f, indent=2)
    
    def register(
        self,
        name: str,
        description: str,
        entities: List[str],
        arrows: List[str],
        mechanism_type: str = "unknown",
        confidence: float = 0.5,
        derived_from: List[str] = None,
        metadata: dict = None
    ) -> str:
        """
        Register a mechanism.
        
        Returns:
            Mechanism ID (MECH-XXXXXX)
        """
        mechanism_id = f"MECH-{self._mechanisms['next_id']:06d}"
        
        mechanism = {
            "id": mechanism_id,
            "name": name,
            "description": description,
            "entities": entities,
            "arrows": arrows,
            "type": mechanism_type,  # causal_chain, feedback, threshold, compensatory, emergent
            "confidence": confidence,
            "derived_from": derived_from or [],
            "contradicts": [],
            "supports": [],
            "replications": 0,
            "challenges": 0,
            "institution_count": 0,
            "createdAt": datetime.now().isoformat(),
            "updatedAt": datetime.now().isoformat(),
            "metadata": metadata or {},
            "trust_score": 0.5,  # Based on participation signals
        }
        
        self._mechanisms["mechanisms"][mechanism_id] = mechanism
        self._mechanisms["next_id"] += 1
        self._save()
        
        return mechanism_id
    
    def get(self, mechanism_id: str) -> Optional[dict]:
        """Get a mechanism by ID."""
        return self._mechanisms["mechanisms"].get(mechanism_id)
    
    def list(self) -> List[dict]:
        """List all mechanisms."""
        return list(self._mechanisms["mechanisms"].values())
    
    def find_by_entity(self, entity: str) -> List[dict]:
        """Find mechanisms involving an entity."""
        return [
            m for m in self._mechanisms["mechanisms"].values()
            if entity.lower() in [e.lower() for e in m.get("entities", [])]
        ]
    
    def find_by_type(self, mech_type: str) -> List[dict]:
        """Find mechanisms by type (causal_chain, feedback, threshold, etc.)."""
        return [
            m for m in self._mechanisms["mechanisms"].values()
            if m.get("type") == mech_type
        ]
    
    def link_support(self, mechanism_id: str, support_mech_id: str):
        """Link two mechanisms as supporting each other."""
        if mechanism_id in self._mechanisms["mechanisms"]:
            mech = self._mechanisms["mechanisms"][mechanism_id]
            if support_mech_id not in mech["supports"]:
                mech["supports"].append(support_mech_id)
                self._save()
    
    def link_contradiction(self, mechanism_id: str, contradict_mech_id: str):
        """Link two mechanisms as contradicting each other."""
        if mechanism_id in self._mechanisms["mechanisms"]:
            mech = self._mechanisms["mechanisms"][mechanism_id]
            if contradict_mech_id not in mech["contradicts"]:
                mech["contradicts"].append(contradict_mech_id)
                self._save()


class MechanismDiscoveryEngine:
    """
    Engine for discovering mechanisms from findings.
    
    Core question: What connects observations?
    
    Methods:
    - Find hidden mediators between entities
    - Identify threshold effects
    - Discover feedback loops
    - Detect compensatory pathways
    """
    
    MECHANISM_PATTERNS = {
        "threshold": ["threshold", "tipping point", "critical level", "switch", "bistable"],
        "feedback": ["feedback", "loop", "cycle", "autoregulatory", "self-reinforcing"],
        "mediator": ["mediator", "through", "via", "intermediate", "hidden"],
        "compensatory": ["compensatory", "adaptive", "protective", "reserve"],
        "emergent": ["emergent", "collective", "system-level", "nonlinear"]
    }
    
    def __init__(self):
        self.mechanisms = MechanismRegistry()
        self.findings = None  # Lazy load
    
    def _load_findings(self):
        """Lazy load finding registry."""
        if self.findings is None:
            from .finding_registry import FindingRegistry
            self.findings = FindingRegistry()
    
    def discover_from_findings(self, finding_ids: List[str]) -> List[str]:
        """
        Discover potential mechanisms from a set of findings.
        
        Returns:
            List of mechanism IDs
        """
        self._load_findings()
        
        mechanism_ids = []
        
        # Look for mediator patterns
        for fid in finding_ids:
            finding = self.findings.get(fid)
            if not finding:
                continue
            
            # Extract potential mechanism
            subject = finding.get("subject", "")
            predicate = finding.get("predicate", "")
            obj = finding.get("object", "")
            
            # Create mechanism hypothesis
            mech_id = self.mechanisms.register(
                name=f"{subject}-{predicate}-{obj} pathway",
                description=f"Unknown mechanism connecting {subject} to {obj}",
                entities=[subject, obj],
                arrows=[f"{subject} -> MECH-X -> {obj}"],
                mechanism_type="unknown",
                confidence=0.3,
                derived_from=[fid],
                metadata={
                    "discovered_from": fid,
                    "predicate": predicate
                }
            )
            mechanism_ids.append(mech_id)
        
        return mechanism_ids


if __name__ == "__main__":
    print("=" * 70)
    print("Sprint 23: Mechanism Registry Foundation")
    print("=" * 70)
    
    registry = MechanismRegistry()
    
    # Example: Alzheimer mechanism
    mech_id = registry.register(
        name="Neuronal Stress-Mediated Amyloid Deposition",
        description="Unknown pathway linking neuronal stress to amyloid production through pTau217",
        entities=["pTau217", "neuronal stress", "amyloid-beta"],
        arrows=["stress -> pTau217 upregulation -> amyloid aggregation"],
        mechanism_type="threshold",
        confidence=0.3,
        derived_from=["FIND-000001"],
        metadata={
            "domain": "neurodegeneration",
            "question": "What drives amyloid deposition?"
        }
    )
    
    print(f"\nRegistered mechanism: {mech_id}")
    
    # List all mechanisms
    print(f"\nTotal mechanisms: {len(registry.list())}")
    
    print("\n" + "=" * 70)
    print("This is where Discovery lives.")
    print("Finding -> Mechanism -> Hypothesis")
    print("=" * 70)