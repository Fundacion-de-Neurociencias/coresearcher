"""
Proyecto Atlas - Sprint 15
Extracción masiva de claims científicos.
Integra PubMed API real con el Claim Registry.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import List, Optional

# Add path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "python"))

from knowledge import ClaimRegistry, HypothesisRegistry, EvidenceRegistry
from knowledge.ontology import CSOConcept, OntologyManager
from agents.pubmed_agent import PubMedAgent
from agents.claim_extractor import ClaimExtractor, batch_extract_claims


class AtlasExtractor:
    """
    Extracción masiva de claims desde fuentes científicas.
    
    Objetivo: 100,000 claims verificables.
    Pipeline: PubMed → Abstract → ClaimExtractor → ClaimRegistry
    """
    
    SOURCES = [
        "PubMed",
        "OpenAlex", 
        "EuropePMC",
        "ClinicalTrials",
    ]
    
    TARGET_DOMAINS = [
        "neurodiagnosis",
        "genomics",
        "clinical_evidence",
    ]
    
    # High-value queries for neurodegeneration (target: 10,000 claims)
    NEURODEGENERATION_QUERIES = [
        "plasma pTau217 Alzheimer",
        "plasma NfL neurodegeneration",
        "CSF Aβ42 biomarker",
        "plasma Aβ42 prediction",
        "tau PET SUVR",
        "amyloid PET centiloid",
        "MMSE cognitive assessment",
        "CDR dementia rating",
        "ADCS MCI assessment",
        "APOE4 Alzheimer risk",
        "MAPT mutation frontotemporal",
        "SNCA synucleinopathy",
        "TDP-43 ALS biomarker",
        "neurofilament light chain",
        "phosphorylated tau biomarker",
    ]

    def __init__(self, email: str = "coresearcher@example.com"):
        self.pubmed = PubMedAgent(email=email)
        self.extractor = ClaimExtractor()
        self.claims = ClaimRegistry()
        self.hypotheses = HypothesisRegistry()
        self.evidence = EvidenceRegistry()
        self.ontology = OntologyManager()
        self.extraction_stats = {
            "papers_processed": 0,
            "claims_extracted": 0,
            "evidence_registered": 0,
            "errors": 0,
        }

    def extract_from_pubmed(self, query: str, max_papers: int = 500) -> int:
        """
        Real extraction pipeline: PubMed → ClaimRegistry.
        
        Returns:
            Number of claims registered
        """
        print(f"\n📊 Extracting from PubMed: '{query}'")
        
        # Step 1: Search PubMed
        try:
            search_result = self.pubmed.search(query, max_results=max_papers)
            papers = search_result.get("results", [])
            total_found = search_result.get("total", 0)
            
            print(f"   Found {total_found} papers, retrieving abstracts...")
            
            # Step 2: Fetch abstracts and extract claims
            extracted_count = 0
            for paper in papers:
                pmid = paper.get("pmid")
                if not pmid:
                    continue
                
                # Get full metadata with abstract
                metadata = self.pubmed.get_metadata(pmid)
                title = metadata.get("title", "")
                abstract = metadata.get("abstract", "")
                doi = metadata.get("doi")
                
                if not abstract:
                    continue
                
                # Step 3: Extract claims from paper
                claims = self.extractor.extract_claims(
                    text=f"{title}. {abstract}",
                    source_pmid=pmid,
                    source_doi=doi,
                )
                
                # Step 4: Register claims
                for claim_data in claims:
                    try:
                        claim_id = self.claims.register(
                            text=claim_data["statement"],
                            evidence_score=claim_data["confidence"],
                            supporting_papers=[pmid] if pmid else [],
                            domain=claim_data.get("domain", "neurodegeneration"),
                            entities=claim_data.get("entities", []),
                            metadata={
                                "claim_type": claim_data.get("type"),
                                "extracted_evidence": claim_data.get("evidence", []),
                                "source_title": title[:200],
                            },
                        )
                        extracted_count += 1
                        self.extraction_stats["claims_extracted"] += 1
                        
                        # Register associated evidence
                        for ev in claim_data.get("evidence", []):
                            if isinstance(ev, dict):
                                self.evidence.register(
                                    value=ev.get("value", ""),
                                    evidence_type=ev.get("type", "observational"),
                                    quality_score=claim_data["confidence"],
                                    paper_doi=doi,
                                    claim_id=claim_id,
                                )
                                self.extraction_stats["evidence_registered"] += 1
                        
                    except Exception as e:
                        self.extraction_stats["errors"] += 1
                        if self.extraction_stats["errors"] <= 5:  # Only show first 5 errors
                            print(f"   Error registering claim: {e}")
                
                self.extraction_stats["papers_processed"] += 1
                
                # Progress indicator
                if self.extraction_stats["papers_processed"] % 25 == 0:
                    print(f"   Processed {self.extraction_stats['papers_processed']} papers, {extracted_count} claims extracted...")
            
            print(f"   ✅ Complete: {extracted_count} claims from {len(papers)} papers")
            return extracted_count
            
        except Exception as e:
            self.extraction_stats["errors"] += 1
            print(f"   ❌ Error in PubMed extraction: {e}")
            return 0

    def run_atlas(self, target_claims: int = 100000, domain: str = "neurodegeneration") -> dict:
        """
        Run full Atlas extraction pipeline.
        
        Args:
            target_claims: Target number of claims to extract
            domain: Domain to focus on (neurodegeneration, genomics, etc.)
        """
        print("=" * 70)
        print("🚀 Proyecto Atlas - Scientific Claims Extraction")
        print(f"   Target: {target_claims} claims | Domain: {domain}")
        print("=" * 70)
        
        queries = []
        
        if domain == "neurodegeneration":
            queries = self.NEURODEGENERATION_QUERIES
        elif domain == "genomics":
            queries = [
                "APOE gene Alzheimer risk",
                "MAPT tauopathy genetics",
                "SNCA synuclein genetics",
                "PSEN1 Alzheimer mutation",
                "tau protein phosphorylation",
            ]
        elif domain == "oncology":
            queries = [
                "cancer biomarker liquid biopsy",
                "oncogene mutation EGFR",
                "tumor mutation burden",
            ]
        else:
            queries = [f"{domain} biomarker", f"{domain} genetics"]
        
        for query in queries:
            self.extract_from_pubmed(query, max_papers=100)
        
        print("\n" + "=" * 70)
        print("📈 Extraction Complete")
        print(f"  Papers processed: {self.extraction_stats['papers_processed']}")
        print(f"  Claims extracted: {self.extraction_stats['claims_extracted']}")
        print(f"  Evidence registered: {self.extraction_stats['evidence_registered']}")
        print(f"  Errors: {self.extraction_stats['errors']}")
        print("=" * 70)
        
        return self.extraction_stats

    def run_demo(self, small_scale: bool = True) -> dict:
        """
        Run a smaller demo extraction for testing.
        
        Args:
            small_scale: If True, only 5 papers per query
        """
        print("=" * 70)
        print("🔬 Atlas Extractor Demo Mode")
        print("=" * 70)
        
        max_papers = 5 if small_scale else 100
        
        # Use first 3 queries for demo
        for query in self.NEURODEGENERATION_QUERIES[:3]:
            self.extract_from_pubmed(query, max_papers=max_papers)
        
        print("\n" + "=" * 70)
        print(f"Demo complete: {self.extraction_stats['claims_extracted']} claims")
        print("=" * 70)
        
        return self.extraction_stats


# =============================================================================
# Atlas Statistics
# =============================================================================

class AtlasStats:
    """
    Statistics for the Atlas project.
    """
    
    def __init__(self):
        self.claims = ClaimRegistry()
    
    def get_progress(self) -> dict:
        """Get extraction progress."""
        all_claims = self.claims.list()
        
        return {
            "total_claims": len(all_claims),
            "by_domain": {},
            "by_status": {
                "supported": 0,
                "contradicted": 0,
                "unvalidated": 0,
            },
            "target": 100000,
            "progress": len(all_claims) / 100000 * 100,
        }


if __name__ == "__main__":
    import argparse

# Security tier: PRIVATE — DO NOT MODIFY
# See python/_tiers.py for classification
SECURITY_TIER = "PRIVATE"

    
    parser = argparse.ArgumentParser(description="Atlas Extractor - Scientific Claims Extraction")
    parser.add_argument("--demo", action="store_true", help="Run in demo mode (small scale)")
    parser.add_argument("--query", type=str, help="Run single query")
    parser.add_argument("--max-papers", type=int, default=50, help="Max papers per query")
    parser.add_argument("--domain", type=str, default="neurodegeneration", help="Domain to extract")
    
    args = parser.parse_args()
    
    if args.demo:
        atlas = AtlasExtractor()
        stats = atlas.run_demo(small_scale=True)
    elif args.query:
        atlas = AtlasExtractor()
        atlas.extract_from_pubmed(args.query, max_papers=args.max_papers)
        print(f"\nExtracted {atlas.extraction_stats['claims_extracted']} claims")
    else:
        # Interactive mode
        print("=" * 70)
        print("🚀 Atlas Extractor - Interactive Mode")
        print("=" * 70)
        print("\nAvailable commands:")
        print("  python scripts/atlas_extractor.py --demo")
        print("  python scripts/atlas_extractor.py --query 'plasma pTau217 Alzheimer'")
        print("  python scripts/atlas_extractor.py --domain neurodegeneration")
        print("\nStarting demo extraction...")
        
        atlas = AtlasExtractor()
        stats = atlas.run_demo(small_scale=True)
        
        print(f"\n✅ Demo complete!")
        print(f"   Claims extracted: {stats['claims_extracted']}")