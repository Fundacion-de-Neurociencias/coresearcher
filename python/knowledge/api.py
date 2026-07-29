"""
Scientific Knowledge API - Sprint 12
Computable scientific knowledge for agents.
"""

from __future__ import annotations

from typing import Optional, List
import sys
from pathlib import Path

# Add path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))


class ScientificKnowledgeAPI:
    """
    API for computable scientific knowledge.
    
    Transforms papers into machine-readable knowledge.
    """
    
    def __init__(self):
        from .claim_registry import ClaimRegistry, HypothesisRegistry, EvidenceRegistry
        from .trust_framework import ClaimTrustFramework
        from .researcher_registry import ResearcherRegistry, ConsensusEngine

# Security tier: COMMUNITY — DO NOT MODIFY
# See python/_tiers.py for classification
SECURITY_TIER = "COMMUNITY"

        
        self.claims = ClaimRegistry()
        self.hypotheses = HypothesisRegistry()
        self.evidence = EvidenceRegistry()
        self.trust = ClaimTrustFramework()
        self.researchers = ResearcherRegistry()
        self.consensus = ConsensusEngine(self.claims, self.researchers, self.trust)
    
    # =========================================================================
    # Claim Endpoints
    # =========================================================================
    
    def get_claim(self, claim_id: str) -> dict:
        """
        GET /claim/{claim_id}
        
        Returns computable claim with all metadata.
        """
        claim = self.claims.get(claim_id)
        if not claim:
            return {"error": "Claim not found", "id": claim_id}
        
        trust_report = self.trust.get_trust_report(claim_id)
        consensus = self.consensus.generate_consensus(claim_id)
        
        return {
            "claim_id": claim["id"],
            "statement": claim["text"],
            "trust": trust_report["trust_index"],
            "consensus": consensus.get("consensus_level", "Unvalidated").lower().replace(" ", "_"),
            "evidence_count": len(claim.get("supportingPapers", [])),
            "contradictions": len(claim.get("contradictingPapers", [])),
            "supporting_papers": claim.get("supportingPapers", []),
            "contradicting_papers": claim.get("contradictingPapers", []),
            "entities": claim.get("entities", []),
            "domain": claim.get("domain"),
            "last_updated": claim.get("updatedAt"),
            "uri": f"https://cso.coresearcher.org/claim/{claim_id}",
        }
    
    # =========================================================================
    # Consensus Endpoints
    # =========================================================================
    
    def get_consensus_by_domain(self, domain: str, topic: str = None) -> List[dict]:
        """
        GET /consensus/{domain}/{topic}
        
        Returns ranked claims by consensus level.
        """
        # Get all claims in domain
        domain_claims = self.claims.list_by_domain(domain)
        
        # Calculate consensus for each
        results = []
        for claim in domain_claims:
            consensus = self.consensus.generate_consensus(claim["id"])
            trust = self.trust.get_trust_report(claim["id"])
            
            # Filter by topic if provided
            if topic and topic.lower() not in claim.get("text", "").lower():
                continue
            
            results.append({
                "claim_id": claim["id"],
                "statement": claim["text"][:100] + "...",
                "trust": trust["trust_index"],
                "consensus": consensus.get("consensus_level", "").lower(),
                "evidence_count": consensus.get("evidence_count", 0),
                "replications": consensus.get("replications", 0),
            })
        
        # Sort by trust index
        return sorted(results, key=lambda x: x["trust"], reverse=True)
    
    # =========================================================================
    # Entity Endpoints (Gene, Biomarker, etc.)
    # =========================================================================
    
    def get_gene(self, gene_symbol: str) -> dict:
        """
        GET /gene/{symbol}
        
        Returns all claims related to a gene.
        """
        # Search claims by entity
        all_claims = self.claims.list()
        gene_claims = [
            c for c in all_claims
            if gene_symbol.upper() in [e.upper() for e in c.get("entities", [])]
        ]
        
        return {
            "entity_type": "gene",
            "symbol": gene_symbol,
            "related_claims": [c["id"] for c in gene_claims],
            "claim_count": len(gene_claims),
        }
    
    def get_biomarker(self, biomarker: str) -> dict:
        """
        GET /biomarker/{name}
        """
        all_claims = self.claims.list()
        bio_claims = [
            c for c in all_claims
            if biomarker.lower() in c.get("text", "").lower()
        ]
        
        return {
            "entity_type": "biomarker",
            "name": biomarker,
            "related_claims": [c["id"] for c in bio_claims],
            "claim_count": len(bio_claims),
            "top_claim": bio_claims[0]["id"] if bio_claims else None,
        }
    
    # =========================================================================
    # Evidence Endpoints
    # =========================================================================
    
    def get_evidence(self, claim_id: str = None) -> List[dict]:
        """
        GET /evidence?claim={claim_id}
        
        Returns evidence for a claim.
        """
        if claim_id:
            all_evidence = self.evidence.list()
            return [
                {
                    "evidence_id": e["id"],
                    "value": e["value"],
                    "quality_score": e["qualityScore"],
                    "sample_size": e.get("sampleSize"),
                    "p_value": e.get("pValue"),
                    "effect_size": e.get("effectSize"),
                }
                for e in all_evidence
                if e.get("claimId") == claim_id
            ]
        
        return [{"error": "claim_id required"}]
    
    # =========================================================================
    # Citation Resolver
    # =========================================================================
    
    def resolve_citation(self, citation: str) -> dict:
        """
        Resolve a scientific citation to claim/hypothesis.
        """
        # Could be DOI, PMID, or claim ID
        if citation.startswith("CLAIM-"):
            return self.get_claim(citation)
        
        return {"error": "Citation type not supported"}


# =============================================================================
# Example API Usage
# =============================================================================

if __name__ == "__main__":
    print("=" * 70)
    print("Scientific Knowledge API - Sprint 12")
    print("=" * 70)
    
    api = ScientificKnowledgeAPI()
    
    # Example query
    print("\nExample queries:")
    print("\n  GET /claim/CLAIM-000001")
    print("  GET /consensus/neurodiagnosis/biomarkers")
    print("  GET /biomarker/pTau217")
    print("  GET /gene/APOE")
    print("  GET /evidence?claim=CLAIM-000001")
    
    print("\n" + "=" * 70)
    print("API would return machine-readable knowledge without any LLM reasoning")
    print("=" * 70)