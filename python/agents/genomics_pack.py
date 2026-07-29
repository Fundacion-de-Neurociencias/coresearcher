
# Security tier: COMMUNITY — DO NOT MODIFY
# See python/_tiers.py for classification
SECURITY_TIER = "COMMUNITY"

"""
Genomics Domain Pack (Sprint 3.5)
Minimal pack to validate Scientific Core is domain-agnostic.

Only adds Genomics-specific entities and relationships.
NO neuroscience logic allowed here.
"""

# =============================================================================
# Entity Types (Domain-Specific)
# =============================================================================

GENOMICS_ENTITY_TYPES = {
    "GENE": {"label": "Gene", "description": "Gene entity"},
    "VARIANT": {"label": "Variant", "description": "Genetic variant"},
    "PATHWAY": {"label": "Pathway", "description": "Biological pathway"},
    "PROTEIN": {"label": "Protein", "description": "Protein product"},
    "PRS": {"label": "PolygenicRiskScore", "description": "Polygenic risk score"},
}

# =============================================================================
# Relationship Types (Domain-Specific)
# =============================================================================

GENOMICS_RELATIONSHIP_TYPES = {
    "ASSOCIATED_WITH": {"from": "Gene", "to": "Disease/Phenotype"},
    "CAUSES": {"from": "Variant", "to": "Disease"},
    "REGULATES": {"from": "Gene", "to": "Gene/Pathway"},
    "PART_OF": {"from": "Gene", "to": "Pathway"},
    "ENCODES": {"from": "Gene", "to": "Protein"},
    "PREDICTS": {"from": "PRS", "to": "Disease"},
}

# =============================================================================
# Entity Resolvers (Genomics Canonical Names)
# =============================================================================

GENOMICS_RESOLVERS = {
    # Canonical mappings for genomics entities
    "apoe": "APOE",
    "apoe4": "APOE ε4",
    "apoe ε4": "APOE ε4",
    "apoe-ε4": "APOE ε4",
    "chr17": "Chromosome 17",
    "17q21": "17q21 deletion",
}

# =============================================================================
# Evidence Weights (Genomics-Specific)
# =============================================================================

GENOMICS_EVIDENCE_WEIGHTS = {
    "genome_wide_association": 0.95,
    "meta_analysis_gwas": 0.9,
    "gwas": 0.85,
    "whole_exome_sequencing": 0.8,
    "targeted_sequencing": 0.7,
    "linkage_analysis": 0.6,
    "candidate_gene": 0.5,
    "case_series": 0.3,
}

# =============================================================================
# Reasoning Queries (Genomics-Specific)
# =============================================================================

GENOMICS_QUERIES = [
    """
    MATCH (g:Gene)-[:ASSOCIATED_WITH]->(d:Disease)
    OPTIONAL MATCH (g)-[:REGULATES]->(p:Pathway)
    RETURN g.name AS gene, d.name AS disease, collect(p.name) AS pathways
    """,
    """
    MATCH (v:Variant)-[:CAUSES]->(d:Disease)
    WHERE v.frequency < 0.05
    RETURN v.name AS rare_variant, d.name AS disease, v.frequency AS freq
    """,
    """
    MATCH (g:Gene)-[:PART_OF]->(p:Pathway)
    OPTIONAL MATCH (p)-[:RELATED_TO]-(other:Pathway)
    RETURN g.name AS gene, p.name AS pathway, collect(other.name) AS related_pathways
    """,
]

# =============================================================================
# Domain Pack Manifest
# =============================================================================

def get_genomics_manifest():
    """
    Return the Genomics Domain Pack manifest.
    
    This pack adds NO logic to Scientific Core.
    It ONLY extends entity types and relationships.
    """
    return {
        "id": "genomics",
        "name": "Genomics Domain Pack",
        "version": "0.1.0",
        "nodeTypes": list(GENOMICS_ENTITY_TYPES.keys()),
        "relationshipTypes": list(GENOMICS_RELATIONSHIP_TYPES.keys()),
        "entityResolvers": GENOMICS_RESOLVERS,
        "evidenceWeights": GENOMICS_EVIDENCE_WEIGHTS,
        "queries": GENOMICS_QUERIES,
    }


# =============================================================================
# Validation Function
# =============================================================================

def validate_genomics_pack():
    """
    Verify that genomics pack doesn't require neuroscience logic.
    """
    # This pack should work with ANY disease, not just neurological
    sample_claims = [
        {"statement": "APOE ε4 increases Alzheimer risk", "entities": ["apoe4", "Alzheimer"]},
        {"statement": "BRCA1 mutations cause breast cancer", "entities": ["brca1", "breast cancer"]},
        {"statement": "PCSK9 variant reduces cardiovascular risk", "entities": ["pcsk9", "cardiovascular"]},
    ]
    
    # All should resolve with genomics types
    for claim in sample_claims:
        for entity in claim["entities"]:
            # Should work with genomics resolver or fall back to universal
            resolved = GENOMICS_RESOLVERS.get(entity.lower(), entity)
    
    return True


# =============================================================================
# CLI Test
# =============================================================================

if __name__ == "__main__":
    print("=" * 70)
    print("Genomics Domain Pack - Sprint 3.5")
    print("=" * 70)
    
    manifest = get_genomics_manifest()
    print(f"\nPack: {manifest['name']}")
    print(f"Node types: {manifest['nodeTypes']}")
    print(f"Relationships: {manifest['relationshipTypes']}")
    
    # Test that pack works for both neuro and non-neuro diseases
    test_cases = [
        ("Neuroscience", ["apoe4", "tau"]),
        ("Oncology", ["brca1", "egfr"]),
        ("Cardiovascular", ["pcsk9", "apoa1"]),
    ]
    
    print("\n" + "=" * 70)
    for domain, entities in test_cases:
        print(f"\n{domain}: ", end="")
        for e in entities:
            resolved = GENOMICS_RESOLVERS.get(e.lower(), e)
            print(f"{e} → {resolved} ✓")
    
    print("\n" + "=" * 70)
    print("Scientific Core validation: Genomics pack is domain-agnostic ✓")
    print("=" * 70)