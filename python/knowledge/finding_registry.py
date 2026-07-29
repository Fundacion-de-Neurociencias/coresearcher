"""
Finding Registry - Sprint 16
Knowledge Distillation Engine.
Transforms extracted claims into structured findings.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Optional, List, Dict
from datetime import datetime

REGISTRY_DIR = Path("knowledge/registry")
REGISTRY_DIR.mkdir(parents=True, exist_ok=True)
FINDINGS_FILE = REGISTRY_DIR / "findings.json"


class FindingRegistry:
    """
    Registry for distilled scientific findings.
    
    A finding is the primary knowledge contribution of a paper -
    distilling multiple claims into a single, structured insight.
    
    Example:
    {
        "subject": "pTau217",
        "predicate": "predicts", 
        "object": "Amyloid pathology",
        "population": "preclinical AD",
        "evidence_type": "cohort study",
        "effect_size": 0.78,
        "p_value": 0.001,
        "sample_size": 1254
    }
    """
    
    def __init__(self):
        self._findings: dict = self._load()
    
    def _load(self) -> dict:
        """Load findings from disk."""
        if FINDINGS_FILE.exists():
            with open(FINDINGS_FILE, 'r') as f:
                return json.load(f)
        return {"findings": {}, "next_id": 1}
    
    def _save(self):
        """Save findings to disk."""
        with open(FINDINGS_FILE, 'w') as f:
            json.dump(self._findings, f, indent=2)
    
    def register(self, 
                 subject: str,
                 predicate: str,
                 object: str,
                 population: str = None,
                 evidence_type: str = "observational",
                 effect_size: float = None,
                 p_value: float = None,
                 sample_size: int = None,
                 quality_score: float = 0.5,
                 derived_from: List[str] = None,
                 domain: str = None,
                 metadata: dict = None) -> str:
        """
        Register a distilled finding.
        
        Returns:
            Finding ID (FIND-XXXXXX)
        """
        finding_id = f"FIND-{self._findings['next_id']:06d}"
        
        finding = {
            "id": finding_id,
            "subject": subject,
            "predicate": predicate,
            "object": object,
            "population": population,
            "evidence_type": evidence_type,
            "effect_size": effect_size,
            "p_value": p_value,
            "sample_size": sample_size,
            "quality_score": quality_score,
            "derivedFrom": derived_from or [],
            "domain": domain,
            "createdAt": datetime.now().isoformat(),
            "updatedAt": datetime.now().isoformat(),
            "metadata": metadata or {},
        }
        
        self._findings["findings"][finding_id] = finding
        self._findings["next_id"] += 1
        self._save()
        
        return finding_id
    
    def get(self, finding_id: str) -> Optional[dict]:
        """Get a finding by ID."""
        return self._findings["findings"].get(finding_id)
    
    def list(self) -> List[dict]:
        """List all findings."""
        return list(self._findings["findings"].values())
    
    def list_by_subject(self, subject: str) -> List[dict]:
        """List findings by subject entity."""
        return [
            f for f in self._findings["findings"].values()
            if f.get("subject", "").lower() == subject.lower()
        ]
    
    def list_by_predicate(self, predicate: str) -> List[dict]:
        """List findings by predicate type."""
        return [
            f for f in self._findings["findings"].values()
            if f.get("predicate", "").lower() == predicate.lower()
        ]


# =============================================================================
# Knowledge Distillation Engine
# =============================================================================

class KnowledgeDistillationEngine:
    """
    Transform extracted claims into distilled findings.
    
    Pipeline:
    Paper → Claims → Evidence → Finding
    """
    
    # Predicate patterns for normalization
    PREDICATE_PATTERNS = {
        "predicts": ["predict", "predicts", "prediction", "prognostic", "forecast"],
        "associated_with": ["associate", "associated", "correlat", "linked"],
        "causes": ["cause", "causes", "lead to", "mediated", "regulated"],
        "increases": ["increase", "elevated", "upregulat", "risk factor"],
        "decreases": ["decrease", "reduce", "lower", "downregulat"],
        "diagnoses": ["diagnos", "biomarker", "marker", "detect"],
        "treats": ["treat", "therapy", "efficacy", "intervention"],
        "mechanistic": ["mechanism", "pathway", "process", "function"],
    }
    
    # Subject/object normalizations for neurodegeneration
    ENTITY_SYNONYMS = {
        "ptau217": ["ptau217", "phosphorylated tau 217", "tau217"],
        "ptau181": ["ptau181", "phosphorylated tau 181", "tau181"],
        "nfl": ["nfl", "neurofilament light", "neurofilament"],
        "amyloid": ["abeta", "aβ", "amyloid", "amyloid-beta"],
        "tau": ["tau", "gallyas", "neurofibrillary"],
        "apoe4": ["apoe4", "apoe ε4", "apoe epsilon 4"],
        "csf": ["csf", "cerebrospinal fluid"],
    }
    
    def __init__(self):
        self.findings = FindingRegistry()
        self.claims = None  # Lazy load
    
    def _load_claims(self):
        """Lazy load claim registry."""
        if self.claims is None:
            from .claim_registry import ClaimRegistry
            self.claims = ClaimRegistry()
    
    def extract_predicate(self, text: str) -> str:
        """Extract the main predicate from claim text."""
        text_lower = text.lower()
        
        for predicate, patterns in self.PREDICATE_PATTERNS.items():
            for pattern in patterns:
                if pattern in text_lower:
                    return predicate
        
        return "related_to"
    
    def normalize_entity(self, entity: str) -> str:
        """Normalize entity to canonical form."""
        entity_lower = entity.lower().strip()
        
        for canonical, synonyms in self.ENTITY_SYNONYMS.items():
            if entity_lower in synonyms or entity_lower == canonical:
                return canonical
        
        return entity_lower
    
    def extract_subject_object(self, text: str, entities: List[str]) -> tuple:
        """Extract subject and object from claim text."""
        # Simple heuristic: first capitalized entity is often subject
        if entities:
            subject = self.normalize_entity(entities[0])
            # Look for object in text after predicate
            text_lower = text.lower()
            
            # Common patterns
            if "predicts" in text_lower:
                object = "outcome"
            elif "associated" in text_lower or "correlat" in text_lower:
                object = "associated_variable"
            elif "biomarker" in text_lower or "marker" in text_lower:
                object = "biomarker"
            else:
                object = "unknown"
            
            return subject, object
        
        return "unknown", "unknown"
    
    def extract_population(self, text: str, metadata: dict) -> str:
        """Extract population context."""
        text_lower = text.lower()
        
        populations = [
            "preclinical", "mild cognitive impairment", "mci", 
            "alzheimer", "dementia", "als", "parkinson",
            "frontotemporal", "cognitively unimpaired",
        ]
        
        for pop in populations:
            if pop in text_lower:
                return pop
        
        return "general"
    
    def extract_effect_size(self, metadata: dict) -> tuple:
        """Extract effect size and p-value from evidence metadata."""
        evidence = metadata.get("extracted_evidence", [])
        
        effect_size = None
        p_value = None
        
        for ev in evidence:
            if isinstance(ev, dict):
                val = ev.get("value", "")
                if "p<" in val or "p =" in val:
                    try:
                        p_value = float(val.split("<")[-1].split()[0])
                    except:
                        pass
                elif "r =" in val or "r≈" in val:
                    try:
                        effect_size = float(val.split("r")[-1].replace("=", "").replace("≈", ""))
                    except:
                        pass
                elif "auc" in val:
                    try:
                        effect_size = float(val.split("auc")[-1].replace("=", "").replace("≈", ""))
                    except:
                        pass
        
        return effect_size, p_value
    
    def distill_from_claim(self, claim: dict) -> str:
        """
        Distill a claim into a structured finding.
        
        Returns:
            Finding ID
        """
        self._load_claims()
        
        text = claim.get("text", "")
        entities = claim.get("entities", [])
        metadata = claim.get("metadata", {})
        domain = claim.get("domain", "general_biomedical")
        
        predicate = self.extract_predicate(text)
        subject, object = self.extract_subject_object(text, entities)
        population = self.extract_population(text, metadata)
        effect_size, p_value = self.extract_effect_size(metadata)
        
        finding_id = self.findings.register(
            subject=subject,
            predicate=predicate,
            object=object,
            population=population,
            evidence_type="extracted",
            effect_size=effect_size,
            p_value=p_value,
            sample_size=None,  # Could extract from metadata
            quality_score=claim.get("evidenceScore", 0.5),
            derived_from=[claim.get("id")],
            domain=domain,
            metadata={
                "original_text": text[:200],
                "extracted_entities": entities,
            },
        )
        
        return finding_id
    
    def distill_from_paper(self, paper_data: dict) -> List[str]:
        """
        Distill all claims from a paper into findings.
        
        Args:
            paper_data: Dict with 'pmid', 'title', 'abstract', 'claims'
        
        Returns:
            List of Finding IDs
        """
        from .claim_registry import ClaimRegistry
        
        self._load_claims()
        claim_registry = self.claims
        
        # Get or create claims for this paper
        claims = paper_data.get("claims", [])
        if not claims:
            pmid = paper_data.get("pmid")
            if pmid:
                # Search for claims derived from this paper
                all_claims = claim_registry.list()
                claims = [
                    c for c in all_claims
                    if pmid in c.get("supportingPapers", [])
                ]
        
        finding_ids = []
        for claim in claims:
            finding_id = self.distill_from_claim(claim)
            finding_ids.append(finding_id)
        
        return finding_ids
    
    def get_consensus_candidates(self, subject: str = None, predicate: str = None) -> List[dict]:
        """
        Get findings that could form consensus.
        """
        findings = self.findings.list()
        
        if subject:
            findings = self.findings.list_by_subject(subject)
        elif predicate:
            findings = self.findings.list_by_predicate(predicate)
        
        return findings


# =============================================================================
# CLI Test
# =============================================================================

if __name__ == "__main__":
    import sys
    sys.path.insert(0, str(Path(__file__).parent.parent.parent))
    
    print("=" * 70)
    print("Sprint 16: Knowledge Distillation Engine - Finding Registry")
    print("=" * 70)
    
    # Import directly to avoid relative import issues
    from claim_registry import ClaimRegistry

# Security tier: COMMUNITY — DO NOT MODIFY
# See python/_tiers.py for classification
SECURITY_TIER = "COMMUNITY"

    
    engine = KnowledgeDistillationEngine()
    engine.claims = ClaimRegistry()
    
    # Test distillation
    sample_claim = {
        "id": "CLAIM-TEST",
        "text": "Plasma pTau217 predicts continuous brain amyloid levels in preclinical Alzheimer's disease.",
        "entities": ["pTau217", "Alzheimer"],
        "evidenceScore": 0.82,
        "domain": "neurodegeneration",
        "metadata": {
            "extracted_evidence": [{"value": "r=0.78"}],
        },
    }
    
    finding_id = engine.distill_from_claim(sample_claim)
    print(f"\nDistilled finding: {finding_id}")
    
    finding = engine.findings.get(finding_id)
    if finding:
        print(f"  Subject: {finding['subject']}")
        print(f"  Predicate: {finding['predicate']}")
        print(f"  Object: {finding['object']}")
        print(f"  Population: {finding['population']}")
        print(f"  Effect size: {finding['effect_size']}")
    
    print("\n" + "=" * 70)
    print(f"Total findings: {len(engine.findings.list())}")
    print("=" * 70)