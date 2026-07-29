"""
Capability Registry - CoResearcher OS Sprint 6
Registry for scientific capabilities across domain packs.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Optional, List
from enum import Enum
from datetime import datetime

# Security tier: PUBLIC — DO NOT MODIFY
# See python/_tiers.py for classification
SECURITY_TIER = "PUBLIC"


# Registry storage
REGISTRY_DIR = Path("ecosystem/registry")
REGISTRY_DIR.mkdir(parents=True, exist_ok=True)
CAPABILITIES_FILE = REGISTRY_DIR / "capabilities.json"


class Capability(Enum):
    """Scientific capabilities in the ecosystem."""
    DISCOVERY = "Discovery"
    LITERATURE_REVIEW = "LiteratureReview"
    GRANT_WRITING = "GrantWriting"
    CLINICAL_EVIDENCE = "ClinicalEvidence"
    DRUG_DISCOVERY = "DrugDiscovery"
    BIOMARKER_DISCOVERY = "BiomarkerDiscovery"
    GENOMICS_ANALYSIS = "GenomicsAnalysis"
    PROTEIN_ANALYSIS = "ProteinAnalysis"
    REGULATORY_ANALYSIS = "RegulatoryAnalysis"
    KNOWLEDGE_RETRIEVAL = "KnowledgeRetrieval"


class CapabilityRegistry:
    """
    Registry for scientific capabilities.
    
    Maps capabilities to:
    - Domain packs that provide them
    - Workflows that implement them
    - Agents that can execute them
    - Priority for routing
    """
    
    def __init__(self):
        self._capabilities: dict = self._load()
    
    def _load(self) -> dict:
        """Load capabilities from disk."""
        if CAPABILITIES_FILE.exists():
            with open(CAPABILITIES_FILE, 'r') as f:
                return json.load(f)
        return {"registrations": {}, "next_id": 1}
    
    def _save(self):
        """Save capabilities to disk."""
        with open(CAPABILITIES_FILE, 'w') as f:
            json.dump(self._capabilities, f, indent=2)
    
    def register(self, capability: str, pack_id: str, 
                 workflow_ids: list[str] = None,
                 agent_ids: list[str] = None,
                 priority: int = 50,
                 config: dict = None) -> str:
        """
        Register a capability for a pack.
        
        Returns:
            Registration ID
        """
        reg_id = f"reg_{self._capabilities['next_id']}"
        
        registration = {
            "id": reg_id,
            "capability": capability,
            "pack_id": pack_id,
            "workflow_ids": workflow_ids or [],
            "agent_ids": agent_ids or [],
            "priority": priority,
            "config": config or {},
            "registered_at": datetime.now().isoformat(),
        }
        
        self._capabilities["registrations"][reg_id] = registration
        self._capabilities["next_id"] += 1
        self._save()
        
        return reg_id
    
    def unregister(self, capability: str, pack_id: str) -> bool:
        """Unregister a capability for a pack."""
        for reg_id, reg in list(self._capabilities["registrations"].items()):
            if reg["capability"] == capability and reg["pack_id"] == pack_id:
                del self._capabilities["registrations"][reg_id]
                self._save()
                return True
        return False
    
    def get(self, capability: str) -> list[dict]:
        """Get all registrations for a capability."""
        return [
            reg for reg in self._capabilities["registrations"].values()
            if reg["capability"] == capability
        ]
    
    def list(self) -> list[str]:
        """List all capabilities in the ecosystem."""
        return list(set(
            reg["capability"] for reg in self._capabilities["registrations"].values()
        ))
    
    def get_best_pack(self, capability: str) -> Optional[str]:
        """Get the highest priority pack for a capability."""
        registrations = self.get(capability)
        if not registrations:
            return None
        
        # Sort by priority (highest first)
        sorted_regs = sorted(registrations, key=lambda r: r["priority"], reverse=True)
        return sorted_regs[0]["pack_id"]
    
    def get_workflows(self, capability: str) -> list[str]:
        """Get all workflows that provide a capability."""
        workflow_ids = []
        for reg in self.get(capability):
            workflow_ids.extend(reg["workflow_ids"])
        return workflow_ids
    
    def get_agents(self, capability: str) -> list[str]:
        """Get all agents that can execute a capability."""
        agent_ids = []
        for reg in self.get(capability):
            agent_ids.extend(reg["agent_ids"])
        return agent_ids


# =============================================================================
# CLI Test
# =============================================================================

if __name__ == "__main__":
    print("=" * 70)
    print("Capability Registry - Sprint 6")
    print("=" * 70)
    
    registry = CapabilityRegistry()
    
    # Register capabilities for packs
    registrations = [
        ("Discovery", "neurodiagnoses", ["research_scout", "hypothesis_discovery"], ["co-scientist"]),
        ("Discovery", "geneforge", ["drug_discovery"], ["autoscientist"], 40),
        ("LiteratureReview", "neurodiagnoses", ["literature_review"], ["reviewer"]),
        ("GrantWriting", "neurodiagnoses", ["grant_writer"], ["co-scientist"]),
        ("ClinicalEvidence", "clinical_evidence", ["clinical_evidence"], ["reviewer"]),
        ("DrugDiscovery", "geneforge", ["drug_discovery"], ["autoscientist"]),
        ("BiomarkerDiscovery", "neurodiagnoses", ["biomarker_discovery"], ["co-scientist"]),
        ("GenomicsAnalysis", "genomics", ["genomics_analysis"], ["co-scientist"]),
    ]
    
    for cap, pack, workflows, agents, *rest in registrations:
        priority = rest[0] if rest else 50
        registry.register(cap, pack, workflows, agents, priority)
    
    print(f"\nRegistered capabilities: {len(registry.list())}")
    
    # Test capability lookups
    print("\n" + "=" * 70)
    print("Capability Lookups:")
    print("=" * 70)
    
    for cap in ["Discovery", "DrugDiscovery", "GenomicsAnalysis", "GrantWriting"]:
        best = registry.get_best_pack(cap)
        workflows = registry.get_workflows(cap)
        print(f"\n{cap}:")
        print(f"  Best pack: {best}")
        print(f"  Workflows: {workflows}")
    
    print("\n" + "=" * 70)
    print("Capability Registry complete!")
    print("=" * 70)