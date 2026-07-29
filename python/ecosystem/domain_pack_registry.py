"""
Domain Pack Registry - CoResearcher OS Sprint 6
Central registry for domain packs in the ecosystem.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Optional, List
from datetime import datetime

# Security tier: PUBLIC — DO NOT MODIFY
# See python/_tiers.py for classification
SECURITY_TIER = "PUBLIC"


# Registry storage
REGISTRY_DIR = Path("ecosystem/registry")
REGISTRY_DIR.mkdir(parents=True, exist_ok=True)
PACKS_FILE = REGISTRY_DIR / "domain_packs.json"


class DomainPackRegistry:
    """
    Central registry for domain packs.
    
    Tracks:
    - Registered domain packs
    - Pack dependencies
    - Pack capabilities
    - Pack lifecycle (register, unregister, resolve)
    """
    
    def __init__(self):
        self._packs: dict = self._load()
        self._capability_index: dict = {}
    
    def _load(self) -> dict:
        """Load registry from disk."""
        if PACKS_FILE.exists():
            with open(PACKS_FILE, 'r') as f:
                return json.load(f)
        return {"packs": {}, "next_id": 1}
    
    def _save(self):
        """Save registry to disk."""
        with open(PACKS_FILE, 'w') as f:
            json.dump(self._packs, f, indent=2)
    
    def register(self, pack: dict) -> str:
        """
        Register a domain pack.
        
        Returns:
            Pack ID
        """
        pack_id = pack.get("id") or f"pack_{self._packs['next_id']}"
        
        # Validate pack structure
        required_fields = ["id", "name", "version", "entities", "relationships", "workflows", "prompts"]
        for field in required_fields:
            if field not in pack:
                raise ValueError(f"Missing required field: {field}")
        
        # Ensure id is set
        pack["id"] = pack_id
        pack["registered_at"] = datetime.now().isoformat()
        
        self._packs["packs"][pack_id] = pack
        self._packs["next_id"] += 1
        self._save()
        
        # Update capability index
        self._rebuild_capability_index()
        
        return pack_id
    
    def unregister(self, pack_id: str) -> bool:
        """Unregister a domain pack."""
        if pack_id in self._packs["packs"]:
            del self._packs["packs"][pack_id]
            self._save()
            self._rebuild_capability_index()
            return True
        return False
    
    def get(self, pack_id: str) -> Optional[dict]:
        """Get a domain pack by ID."""
        return self._packs["packs"].get(pack_id)
    
    def list(self) -> List[dict]:
        """List all registered domain packs."""
        return list(self._packs["packs"].values())
    
    def list_by_capability(self, capability: str) -> List[dict]:
        """List packs that provide a capability."""
        return self._capability_index.get(capability, [])
    
    def _rebuild_capability_index(self):
        """Rebuild the capability index from registered packs."""
        self._capability_index = {}
        for pack_id, pack in self._packs["packs"].items():
            # Infer capabilities from pack structure
            for workflow in pack.get("workflows", []):
                wf_id = workflow.get("id", "")
                # Map workflow IDs to capabilities
                cap_map = {
                    "research_scout": "Discovery",
                    "hypothesis_discovery": "Discovery",
                    "grant_writer": "GrantWriting",
                    "literature_review": "LiteratureReview",
                    "clinical_evidence": "ClinicalEvidence",
                    "drug_discovery": "DrugDiscovery",
                    "biomarker_discovery": "BiomarkerDiscovery",
                    "genomics_analysis": "GenomicsAnalysis",
                    "protein_analysis": "ProteinAnalysis",
                    "regulatory_analysis": "RegulatoryAnalysis",
                }
                capability = cap_map.get(wf_id)
                if capability:
                    if capability not in self._capability_index:
                        self._capability_index[capability] = []
                    self._capability_index[capability].append(pack)
    
    def resolve_dependencies(self, pack_id: str) -> List[dict]:
        """
        Resolve all dependencies for a pack.
        
        Returns transitive dependencies in order.
        """
        pack = self.get(pack_id)
        if not pack:
            return []
        
        # Get direct dependencies
        direct_deps = pack.get("depends_on", [])
        
        # Find extends pack
        extends = pack.get("extends")
        if extends:
            direct_deps.append(extends)
        
        # Resolve transitive
        all_deps = []
        for dep_id in direct_deps:
            dep_pack = self.get(dep_id)
            if dep_pack:
                all_deps.append(dep_pack)
                # Recurse for nested deps
                nested = self.resolve_dependencies(dep_id)
                for n in nested:
                    if n["id"] not in [d["id"] for d in all_deps]:
                        all_deps.append(n)
        
        return all_deps


# =============================================================================
# Built-in Domain Packs
# =============================================================================

NEURODIAGNOSES_PACK = {
    "id": "neurodiagnoses",
    "name": "Neurodiagnoses Pack",
    "version": "0.1.0",
    "entities": [
        {"type": "Biomarker", "label": "Biomarker", "description": "Neurological biomarker"},
        {"type": "Mechanism", "label": "Mechanism", "description": "Disease mechanism"},
        {"type": "Axis0", "label": "Axis 0 - Syndrome", "description": "Clinical syndrome"},
        {"type": "Axis1", "label": "Axis 1 - Etiology", "description": "Disease etiology"},
        {"type": "Axis2", "label": "Axis 2 - Impairment", "description": "Functional impairment"},
    ],
    "relationships": [
        {"type": "INFLUENCES", "from": "Biomarker/Mechanism", "to": "Axis1/axis2"},
        {"type": "CAUSES", "from": "Mechanism", "to": "Axis0"},
        {"type": "PREDICTS", "from": "Biomarker", "to": "Axis0"},
        {"type": "HAS_AXIS0", "from": "Entity", "to": "Axis0"},
        {"type": "HAS_AXIS1", "from": "Entity", "to": "Axis1"},
        {"type": "HAS_AXIS2", "from": "Entity", "to": "Axis2"},
    ],
    "depends_on": ["clinical_evidence", "genomics"],
    "workflows": [
        {"id": "research_scout", "name": "Research Scout", "entrypoint": "workflows.research_scout"},
        {"id": "hypothesis_discovery", "name": "Hypothesis Discovery", "entrypoint": "workflows.hypothesis_discovery"},
        {"id": "biomarker_discovery", "name": "Biomarker Discovery", "entrypoint": "workflows.biomarker_discovery"},
    ],
    "prompts": [
        {"id": "neuro_triage_prompt", "name": "Neuro Triage", "template": "You are a neurologist..."},
        {"id": "biomarker_prompt", "name": "Biomarker Analysis", "template": "Analyze biomarkers..."},
    ],
}

GENOMICS_PACK = {
    "id": "genomics",
    "name": "Genomics Pack",
    "version": "0.1.0",
    "entities": [
        {"type": "GENE", "label": "Gene", "description": "Gene entity"},
        {"type": "VARIANT", "label": "Variant", "description": "Genetic variant"},
        {"type": "PATHWAY", "label": "Pathway", "description": "Biological pathway"},
        {"type": "PROTEIN", "label": "Protein", "description": "Protein product"},
        {"type": "PRS", "label": "PolygenicRiskScore", "description": "Polygenic risk score"},
    ],
    "relationships": [
        {"type": "ASSOCIATED_WITH", "from": "Gene", "to": "Disease/Phenotype"},
        {"type": "CAUSES", "from": "Variant", "to": "Disease"},
        {"type": "REGULATES", "from": "Gene", "to": "Gene/Pathway"},
        {"type": "ENCODES", "from": "Gene", "to": "Protein"},
    ],
    "workflows": [
        {"id": "genomics_analysis", "name": "Genomics Analysis", "entrypoint": "workflows.genomics_analysis"},
    ],
    "prompts": [
        {"id": "gene_drug_prompt", "name": "Gene-Drug Analysis", "template": "Analyze gene-drug interactions..."},
    ],
}

CLINICAL_EVIDENCE_PACK = {
    "id": "clinical_evidence",
    "name": "Clinical Evidence Pack",
    "version": "0.1.0",
    "entities": [
        {"type": "ClinicalTrial", "label": "Clinical Trial"},
        {"type": "PatientCohort", "label": "Patient Cohort"},
        {"type": "Outcome", "label": "Clinical Outcome"},
    ],
    "relationships": [
        {"type": "VALIDATES", "from": "ClinicalTrial", "to": "Evidence"},
        {"type": "STUDIES", "from": "ClinicalTrial", "to": "Hypothesis"},
    ],
    "workflows": [
        {"id": "clinical_evidence", "name": "Clinical Evidence", "entrypoint": "workflows.clinical_evidence"},
    ],
    "prompts": [],
}

GENE_FORGE_PACK = {
    "id": "geneforge",
    "name": "GeneForge Pack",
    "version": "0.1.0",
    "entities": [
        {"type": "Target", "label": "Drug Target"},
        {"type": "Interaction", "label": "Molecular Interaction"},
        {"type": "Validation", "label": "Experimental Validation"},
    ],
    "relationships": [
        {"type": "TARGETS", "from": "Drug", "to": "Gene/Protein"},
        {"type": "VALIDATES", "from": "Experiment", "to": "Hypothesis"},
    ],
    "depends_on": ["genomics"],
    "workflows": [
        {"id": "drug_discovery", "name": "Drug Discovery", "entrypoint": "workflows.drug_discovery"},
    ],
    "prompts": [],
}

MEDICALIA_PACK = {
    "id": "medicalia",
    "name": "Medicalia Pack",
    "version": "0.1.0",
    "entities": [
        {"type": "ClinicalCase", "label": "Clinical Case"},
        {"type": "Treatment", "label": "Treatment"},
        {"type": "Response", "label": "Treatment Response"},
    ],
    "relationships": [
        {"type": "TREATS", "from": "Treatment", "to": "Disease"},
        {"type": "RESPONDS_TO", "from": "Patient", "to": "Treatment"},
    ],
    "depends_on": ["clinical_evidence"],
    "workflows": [
        {"id": "treatment_optimization", "name": "Treatment Optimization", "entrypoint": "workflows.treatment_optimization"},
    ],
    "prompts": [],
}


# =============================================================================
# CLI Test
# =============================================================================

if __name__ == "__main__":
    print("=" * 70)
    print("Domain Pack Registry - Sprint 6")
    print("=" * 70)
    
    registry = DomainPackRegistry()
    
    # Register built-in packs
    registry.register(NEURODIAGNOSES_PACK)
    registry.register(GENOMICS_PACK)
    registry.register(CLINICAL_EVIDENCE_PACK)
    registry.register(GENE_FORGE_PACK)
    registry.register(MEDICALIA_PACK)
    
    print(f"\nRegistered packs: {len(registry.list())}")
    
    # Test dependency resolution
    print("\n" + "=" * 70)
    print("Dependency Resolution:")
    print("=" * 70)
    
    neuro_deps = registry.resolve_dependencies("neurodiagnoses")
    print(f"\nNeurodiagnoses depends on: {[d['id'] for d in neuro_deps]}")
    
    forge_deps = registry.resolve_dependencies("geneforge")
    print(f"GeneForge depends on: {[d['id'] for d in forge_deps]}")
    
    # Test capability indexing
    print("\n" + "=" * 70)
    print("Capability Index:")
    print("=" * 70)
    
    for cap in ["Discovery", "LiteratureReview", "GenomicsAnalysis"]:
        packs = registry.list_by_capability(cap)
        print(f"\n{cap}: {[p['id'] for p in packs]}")