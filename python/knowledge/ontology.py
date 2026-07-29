"""
CoResearcher Scientific Ontology (CSO) - Sprint 9
Versioned, open, citable scientific ontology.
"""

from __future__ import annotations

from enum import Enum
from typing import List, Dict

# Security tier: PUBLIC — DO NOT MODIFY
# See python/_tiers.py for classification
SECURITY_TIER = "PUBLIC"



# =============================================================================
# Core Scientific Concepts (Version 0.1.0)
# =============================================================================

class CSOConcept(Enum):
    """Core scientific concepts in the CSO ontology."""
    
    # Knowledge primitives
    CLAIM = "cso:Claim"
    EVIDENCE = "cso:Evidence"
    HYPOTHESIS = "cso:Hypothesis"
    EXPERIMENT = "cso:Experiment"
    FINDING = "cso:Finding"
    CONTRADICTION = "cso:Contradiction"
    CONSNET = "cso:Consensus"
    
    # Relationships
    SUPPORTED_BY = "cso:supportedBy"
    CONTRADICTS = "cso:contradicts"
    DERIVES_FROM = "cso:derivesFrom"
    TESTS = "cso:tests"
    VALIDATES = "cso:validates"
    
    # Qualifiers
    QUALITY_SCORE = "cso:qualityScore"
    EVIDENCE_SCORE = "cso:evidenceScore"
    CONFIDENCE = "cso:confidence"
    SAMPLE_SIZE = "cso:sampleSize"
    P_VALUE = "cso:pValue"
    EFFECT_SIZE = "cso:effectSize"


CSO_VERSION = "0.1.0"


# =============================================================================
# Concept Definitions
# =============================================================================

CONCEPT_DEFINITIONS: Dict[str, dict] = {
    CSOConcept.CLAIM.value: {
        "label": "Claim",
        "description": "A scientific assertion extracted from literature",
        "properties": [
            "id", "text", "evidenceScore", "status", "supportingPapers",
            "contradictingPapers", "domain", "entities"
        ],
        "uri_template": "https://cso.coresearcher.org/claim/{id}",
    },
    CSOConcept.EVIDENCE.value: {
        "label": "Evidence",
        "description": "Empirical support for a claim",
        "properties": [
            "id", "value", "type", "qualityScore", "sampleSize",
            "pValue", "effectSize", "paperDoi"
        ],
        "uri_template": "https://cso.coresearcher.org/evidence/{id}",
    },
    CSOConcept.HYPOTHESIS.value: {
        "label": "Hypothesis",
        "description": "A testable scientific proposition",
        "properties": [
            "id", "statement", "evidenceScore", "criticScore",
            "eloRating", "status", "derivedFrom"
        ],
        "uri_template": "https://cso.coresearcher.org/hypothesis/{id}",
    },
    CSOConcept.EXPERIMENT.value: {
        "label": "Experiment",
        "description": "A designed test of a hypothesis",
        "properties": [
            "id", "design", "method", "hypothesisId", "status"
        ],
        "uri_template": "https://cso.coresearcher.org/experiment/{id}",
    },
    CSOConcept.FINDING.value: {
        "label": "Finding",
        "description": "An observed result",
        "properties": ["id", "outcome", "supportsHypothesis", "evidence"],
        "uri_template": "https://cso.coresearcher.org/finding/{id}",
    },
}


# =============================================================================
# Ontology Functions
# =============================================================================

def get_concept_uri(concept: str, identifier: str) -> str:
    """Generate a citable URI for a concept instance."""
    if concept in CONCEPT_DEFINITIONS:
        template = CONCEPT_DEFINITIONS[concept]["uri_template"]
        return template.format(id=identifier)
    return f"https://cso.coresearcher.org/unknown/{identifier}"


def get_concept_definition(concept: str) -> dict:
    """Get the definition for a concept."""
    return CONCEPT_DEFINITIONS.get(concept, {})


def list_concepts() -> List[str]:
    """List all concepts in the ontology."""
    return list(CONCEPT_DEFINITIONS.keys())


def validate_claim_structure(claim: dict) -> bool:
    """Validate that a claim follows CSO structure."""
    required = ["id", "text", "evidenceScore"]
    return all(k in claim for k in required)


def validate_hypothesis_structure(hypothesis: dict) -> bool:
    """Validate that a hypothesis follows CSO structure."""
    required = ["id", "statement", "evidenceScore"]
    return all(k in hypothesis for k in required)


# =============================================================================
# Citation Format
# =============================================================================

def format_citation(claim_id: str) -> str:
    """Format a citation for a registered claim."""
    uri = get_concept_uri(CSOConcept.CLAIM.value, claim_id)
    return f"CoResearcher Scientific Ontology. {claim_id}. {uri}"


def format_hypothesis_citation(hyp_id: str) -> str:
    """Format a citation for a registered hypothesis."""
    uri = get_concept_uri(CSOConcept.HYPOTHESIS.value, hyp_id)
    return f"CoResearcher Scientific Ontology. {hyp_id}. {uri}"


# =============================================================================
# Ontology Manager
# =============================================================================

class OntologyManager:
    """
    Manage CSO concepts and entity alignment.
    Used by Atlas Extractor to align extracted entities with known concepts.
    """
    
    # Known entities in neurodegeneration domain
    KNOWN_ENTITIES = {
        "ptau217": {"canonical": "Plasma pTau217", "type": "biomarker", "aliases": ["pTau217", "phosphorylated tau 217"]},
        "nfl": {"canonical": "Neurofilament Light Chain", "type": "biomarker", "aliases": ["NfL", "neurofilament light"]},
        "abeta42": {"canonical": "Aβ42", "type": "biomarker", "aliases": ["Aβ42", "amyloid beta 42", "beta amyloid 42"]},
        "apoe4": {"canonical": "APOE ε4", "type": "gene_variant", "aliases": ["APOE4", "APOE epsilon 4"]},
        "apoe": {"canonical": "APOE", "type": "gene", "aliases": ["APOE"]},
        "tau": {"canonical": "Tau Protein", "type": "protein", "aliases": ["tau", "MAPT"]},
        "alpha-synuclein": {"canonical": "Alpha-Synuclein", "type": "protein", "aliases": ["SNCA", "α-synuclein"]},
        "tdp-43": {"canonical": "TDP-43", "type": "protein", "aliases": ["TDP43", "TARDBP"]},
        "mmse": {"canonical": "MMSE", "type": "assessment", "aliases": ["Mini-Mental State Examination"]},
        "cdr": {"canonical": "CDR", "type": "assessment", "aliases": ["Clinical Dementia Rating"]},
    }
    
    def __init__(self):
        self.version = CSO_VERSION
    
    def normalize_entity(self, entity: str) -> dict:
        """Normalize an entity to canonical form."""
        entity_lower = entity.lower().strip()
        
        for key, info in self.KNOWN_ENTITIES.items():
            if entity_lower in [a.lower() for a in info.get("aliases", [])] or entity_lower == key:
                return {"canonical": info["canonical"], "type": info["type"]}
        
        return {"canonical": entity, "type": "unknown", "aliases": [entity]}
    
    def get_concept_for_claim(self, claim_text: str) -> str:
        """Get the best matching CSO concept for a claim."""
        claim_lower = claim_text.lower()
        
        if "biomarker" in claim_lower or "predict" in claim_lower:
            return CSOConcept.CLAIM.value
        if "mechanism" in claim_lower or "pathway" in claim_lower:
            return CSOConcept.HYPOTHESIS.value
        if "trial" in claim_lower or "therapy" in claim_lower:
            return CSOConcept.EXPERIMENT.value
        
        return CSOConcept.CLAIM.value


# =============================================================================
# CLI Test
# =============================================================================

if __name__ == "__main__":
    print("=" * 70)
    print(f"CoResearcher Scientific Ontology (CSO) v{CSO_VERSION}")
    print("=" * 70)
    
    print("\nCore Concepts:")
    for concept in list_concepts():
        definition = get_concept_definition(concept)
        print(f"\n  {concept.split(':')[-1]}:")
        print(f"    {definition['description']}")
        print(f"    URI: {definition['uri_template']}")
    
    print("\n" + "=" * 70)
    print("Example Citations:")
    print("=" * 70)
    
    print(f"\n  Claim: {format_citation('CLAIM-000001')}")
    print(f"  Hypothesis: {format_hypothesis_citation('HYP-000001')}")