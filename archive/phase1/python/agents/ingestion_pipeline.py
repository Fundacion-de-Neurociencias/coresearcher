"""
Knowledge Ingestion Pipeline
Connects PubMed → Claim Extraction → Neo4j storage in one automated pipeline.
This is the core differentiator for CoResearcher OS.
"""

import json
import sys
from pubmed_agent import PubMedAgent
from openalex_agent import OpenAlexAgent
from crossref_agent import CrossrefAgent
from claim_extractor import ClaimExtractor, batch_extract_claims
from neo4j_client import Neo4jClient


class IngestionPipeline:
    """
    Automated pipeline that:
    1. Searches PubMed/OpenAlex for papers on a topic
    2. Fetches abstracts and metadata
    3. Extracts structured claims
    4. Persists to Neo4j knowledge graph
    """

    def __init__(self, neo4j_uri=None, neo4j_user=None, neo4j_password=None, dry_run=False):
        self.pubmed = PubMedAgent()
        self.openalex = OpenAlexAgent()
        self.crossref = CrossrefAgent()
        self.extractor = ClaimExtractor()
        self.neo4j = Neo4jClient(
            uri=neo4j_uri,
            user=neo4j_user,
            password=neo4j_password,
            dry_run=dry_run,
        )
        self.dry_run = dry_run

    def run_pubmed_pipeline(self, query: str, max_papers: int = 20) -> dict:
        """
        Full pipeline: PubMed search → Abstract fetch → Claim extraction.
        
        Returns structured data ready for Neo4j ingestion.
        """
        # Step 1: Search PubMed
        print(f"[Pipeline] Searching PubMed: {query}", file=sys.stderr)
        search_results = self.pubmed.search(query, max_results=max_papers)
        papers = search_results.get("results", [])

        if not papers:
            return {
                "query": query,
                "source": "pubmed",
                "total_papers": 0,
                "total_claims": 0,
                "papers": [],
            }

        print(f"[Pipeline] Found {len(papers)} papers. Fetching abstracts...", file=sys.stderr)

        # Step 2: Fetch abstracts for each paper
        for paper in papers:
            pmid = paper.get("pmid")
            if pmid:
                abstract = self.pubmed.get_abstract(pmid)
                paper["abstract"] = abstract
                
                # Get full metadata for DOIs
                metadata = self.pubmed.get_metadata(pmid)
                if metadata.get("doi"):
                    paper["doi"] = metadata.get("doi")
                paper["pubdate"] = metadata.get("pubdate", paper.get("pubdate"))
                paper["mesh_terms"] = metadata.get("mesh_terms", [])

        print(f"[Pipeline] Extracting claims from {len(papers)} papers...", file=sys.stderr)

        # Step 3: Extract claims from all papers
        claim_results = batch_extract_claims(papers)
        
        total_claims = sum(r["claim_count"] for r in claim_results)
        print(f"[Pipeline] Extracted {total_claims} claims from {len(papers)} papers", file=sys.stderr)

        return {
            "query": query,
            "source": "pubmed",
            "total_papers": len(papers),
            "total_claims": total_claims,
            "papers": claim_results,
        }

    def run_openalex_pipeline(self, query: str, max_papers: int = 20) -> dict:
        """
        Full pipeline: OpenAlex search → Claim extraction.
        OpenAlex includes abstracts in inverted index format.
        """
        print(f"[Pipeline] Searching OpenAlex: {query}", file=sys.stderr)
        search_results = self.openalex.search_papers(query, max_results=max_papers)
        papers = search_results.get("results", [])

        if not papers:
            return {
                "query": query,
                "source": "openalex",
                "total_papers": 0,
                "total_claims": 0,
                "papers": [],
            }

        print(f"[Pipeline] Found {len(papers)} papers. Reconstructing abstracts...", file=sys.stderr)

        # Reconstruct abstracts from inverted index
        formatted_papers = []
        for paper in papers:
            abstract = self._reconstruct_abstract(paper.get("abstract_inverted_index"))
            
            formatted_papers.append({
                "pmid": None,  # OpenAlex doesn't always return PMID
                "doi": paper.get("doi", "").replace("https://doi.org/", ""),
                "title": paper.get("title", ""),
                "abstract": abstract or "",
                "source": paper.get("source", ""),
                "authors": [
                    a.get("author", "") for a in paper.get("authorships", [])
                ],
                "concepts": [c.get("name", "") for c in paper.get("concepts", [])],
                "keywords": paper.get("keywords", []),
            })

        print(f"[Pipeline] Extracting claims from {len(formatted_papers)} papers...", file=sys.stderr)

        claim_results = batch_extract_claims(formatted_papers)
        total_claims = sum(r["claim_count"] for r in claim_results)

        return {
            "query": query,
            "source": "openalex",
            "total_papers": len(formatted_papers),
            "total_claims": total_claims,
            "papers": claim_results,
        }

    def _reconstruct_abstract(self, inverted_index: dict) -> str:
        """Reconstruct abstract text from OpenAlex inverted index."""
        if not inverted_index:
            return ""
        
        # Create a list of (position, word) tuples
        word_positions = []
        for word, positions in inverted_index.items():
            for pos in positions:
                word_positions.append((pos, word))
        
        # Sort by position and join
        word_positions.sort(key=lambda x: x[0])
        words = [wp[1] for wp in word_positions]
        
        return " ".join(words)

    def neuro_pipeline(self, condition: str, max_papers: int = 50) -> dict:
        """
        Specialized pipeline for neurodegenerative disease literature.
        
        Searches both PubMed and OpenAlex for maximum coverage.
        """
        # Build targeted query for neurodegeneration
        queries = [
            f"{condition} biomarker diagnosis",
            f"{condition} biomarker progression",
            f"{condition} tau amyloid PET",
            f"{condition} clinical trial",
        ]
        
        all_papers = []
        all_claims = []
        
        for query in queries:
            # PubMed
            pubmed_result = self.run_pubmed_pipeline(query, max_papers=max_papers // len(queries))
            all_papers.extend(pubmed_result.get("papers", []))
            all_claims.extend(
                [c for p in pubmed_result.get("papers", []) for c in p.get("claims", [])]
            )
            
            # OpenAlex
            openalex_result = self.run_openalex_pipeline(query, max_papers=max_papers // len(queries))
            all_papers.extend(openalex_result.get("papers", []))
            all_claims.extend(
                [c for p in openalex_result.get("papers", []) for c in p.get("claims", [])]
            )

        return {
            "condition": condition,
            "total_papers": len(all_papers),
            "total_claims": len(all_claims),
            "papers": all_papers,
            "claims_summary": self._summarize_claims(all_claims),
        }

    def _summarize_claims(self, claims: list) -> dict:
        """Generate a summary of claims data."""
        from collections import Counter
        
        types = Counter(c.get("type", "unknown") for c in claims)
        domains = Counter(c.get("domain", "unknown") for c in claims)
        confidences = [c.get("confidence", 0) for c in claims if c.get("confidence")]
        
        return {
            "total_claims": len(claims),
            "by_type": dict(types),
            "by_domain": dict(domains),
            "avg_confidence": round(sum(confidences) / len(confidences), 2) if confidences else 0,
            "high_confidence": len([c for c in claims if c.get("confidence", 0) >= 0.8]),
            "has_evidence": len([c for c in claims if c.get("evidence")]),
        }

    def ingest_to_neo4j(self, pipeline_result: dict) -> dict:
        """
        Ingest pipeline results into Neo4j knowledge graph.
        
        Returns summary of what was created.
        """
        return self.neo4j.ingest_pipeline_result(pipeline_result)

    def run_and_ingest(self, query: str, max_papers: int = 20, source: str = "pubmed") -> dict:
        """
        Run full pipeline and persist results to Neo4j.
        
        Pipeline: Search → Abstract fetch → Claim extraction → Neo4j storage
        """
        if source == "pubmed":
            result = self.run_pubmed_pipeline(query, max_papers)
        elif source == "openalex":
            result = self.run_openalex_pipeline(query, max_papers)
        else:
            raise ValueError(f"Unknown source: {source}")

        if result.get("total_papers", 0) > 0:
            ingest_summary = self.ingest_to_neo4j(result)
            result["neo4j_ingestion"] = ingest_summary

        return result

    def generate_neo4j_cypher(self, pipeline_result: dict) -> str:
        """
        Generate Cypher queries to insert pipeline results into Neo4j.
        
        Creates:
        - (:Paper {pmid, doi, title, ...})
        - (:Claim {statement, type, confidence, ...})
        - (:Evidence {type, value})
        - (:Concept {name, domain})
        - Relationships: (Paper)-[:PRODUCES]->(Claim), 
                         (Claim)-[:HAS_EVIDENCE]->(Evidence),
                         (Paper)-[:MENTIONS]->(Concept)
        """
        cypher = []
        cypher.append("// Auto-generated by CoResearcher OS Ingestion Pipeline")
        cypher.append(f"// Query: {pipeline_result.get('query', 'unknown')}")
        cypher.append(f"// Source: {pipeline_result.get('source', 'unknown')}")
        cypher.append(f"// Papers: {pipeline_result.get('total_papers', 0)}, Claims: {pipeline_result.get('total_claims', 0)}")
        cypher.append("")
        
        for paper_data in pipeline_result.get("papers", []):
            source = paper_data.get("source", {})
            pmid = source.get("pmid", "") or f"unknown-{hash(str(source))}" 
            doi = source.get("doi", "")
            title = source.get("title", "").replace("'", "\\'")
            
            if not pmid and not doi:
                continue
            
            node_id = f"p_{pmid.replace('-', '_') if pmid else doi.replace('.', '_').replace('/', '_')}"
            
            # Create Paper node
            cypher.append(f"""
// Paper: {title[:80]}
MERGE (p:Paper {{id: '{pmid or doi}'}})
SET p.title = '{title[:200]}',
    p.pmid = '{pmid or ''}',
    p.doi = '{doi or ''}',
    p.processedAt = datetime()
ON CREATE SET p.createdAt = datetime()
""")
            
            # Create Claim nodes and relationships
            for claim in paper_data.get("claims", []):
                claim_id = f"C{hash(claim.get('statement', '')) % 1000000000}"
                statement = claim.get("statement", "").replace("'", "\\'")[:500]
                claim_type = claim.get("type", "finding")
                confidence = claim.get("confidence", 0.5)
                
                cypher.append(f"""
MERGE (c:Claim {{id: '{claim_id}'}})
SET c.text = '{statement}',
    c.confidence = {confidence},
    c.type = '{claim_type}'
MERGE (p)-[:PRODUCES]->(c)
""")
                
                # Create Evidence relationships
                for evidence in claim.get("evidence", []):
                    ev_id = f"E{hash(str(evidence)) % 1000000000}"
                    ev_value = evidence.get("value", "").replace("'", "\\'")[:200]
                    cypher.append(f"""
MERGE (e:Evidence {{id: '{ev_id}'}})
SET e.value = '{ev_value}',
    e.type = '{evidence.get('type', 'statistical')}'
MERGE (c)-[:SUPPORTED_BY]->(e)
""")
                
                # Create Concept nodes for entities
                for entity in claim.get("entities", []):
                    entity_name = entity.replace("'", "\\'")
                    domain = claim.get("domain", "general_biomedical")
                    cypher.append(f"""
MERGE (con:Concept {{name: '{entity_name}'}})
SET con.domain = '{domain}'
MERGE (p)-[:MENTIONS]->(con)
MERGE (c)-[:ABOUT]->(con)
""")
        
        return "\n".join(cypher)


if __name__ == "__main__":
    import sys

# Security tier: COMMUNITY — DO NOT MODIFY
# See python/_tiers.py for classification
SECURITY_TIER = "COMMUNITY"

    
    # Parse --dry-run flag
    dry_run = "--dry-run" in sys.argv
    if dry_run:
        sys.argv.remove("--dry-run")
    
    pipeline = IngestionPipeline(dry_run=dry_run)
    
    if len(sys.argv) > 1:
        cmd = sys.argv[1]
        
        if cmd == "pubmed":
            query = sys.argv[2] if len(sys.argv) > 2 else "Alzheimer tau PET biomarker"
            result = pipeline.run_pubmed_pipeline(query)
            print(json.dumps(result, indent=2, default=str))
        
        elif cmd == "openalex":
            query = sys.argv[2] if len(sys.argv) > 2 else "Alzheimer tau PET biomarker"
            result = pipeline.run_openalex_pipeline(query)
            print(json.dumps(result, indent=2, default=str))
        
        elif cmd == "neuro":
            condition = sys.argv[2] if len(sys.argv) > 2 else "Alzheimer disease"
            result = pipeline.neuro_pipeline(condition)
            print(json.dumps(result, indent=2, default=str))
        
        elif cmd == "cypher":
            # Generate Cypher from existing JSON file
            with open(sys.argv[2], 'r') as f:
                data = json.load(f)
            cypher = pipeline.generate_neo4j_cypher(data)
            print(cypher)
        
        elif cmd == "full":
            # Full pipeline: search → extract → cypher
            query = sys.argv[2] if len(sys.argv) > 2 else "Alzheimer tau PET biomarker"
            result = pipeline.run_pubmed_pipeline(query)
            cypher = pipeline.generate_neo4j_cypher(result)
            print("=== DATA ===")
            print(json.dumps(result, indent=2, default=str)[:5000])
            print("...")
            print("\n=== CYPHER ===")
            print(cypher)
        
        elif cmd == "ingest":
            # Run pipeline and persist to Neo4j
            query = sys.argv[2] if len(sys.argv) > 2 else "Alzheimer tau PET biomarker"
            source = sys.argv[3] if len(sys.argv) > 3 else "pubmed"
            max_papers = int(sys.argv[4]) if len(sys.argv) > 4 else 5
            result = pipeline.run_and_ingest(query, max_papers, source)
            print(json.dumps(result, indent=2, default=str))
        
        elif cmd == "run":
            # Run neuro pipeline and persist to Neo4j
            condition = sys.argv[2] if len(sys.argv) > 2 else "Alzheimer disease"
            max_papers = int(sys.argv[3]) if len(sys.argv) > 3 else 20
            result = pipeline.neuro_pipeline(condition, max_papers)
            ingest_summary = pipeline.ingest_to_neo4j(result)
            result["neo4j_ingestion"] = ingest_summary
            print(json.dumps(result, indent=2, default=str))
        
        else:
            print(f"Unknown command: {cmd}")
            sys.exit(1)
    else:
        print("Usage: python ingestion_pipeline.py <pubmed|openalex|neuro|cypher|full|ingest|run> [query] [source] [max_papers]")
        print("")
        print("Commands:")
        print("  pubmed   Search PubMed and extract claims")
        print("  openalex Search OpenAlex and extract claims")
        print("  neuro    Multi-source pipeline for neurodegenerative diseases")
        print("  cypher   Generate Cypher from existing JSON file")
        print("  full     Full pipeline: search → extract → cypher")
        print("  ingest   Run pipeline and persist to Neo4j")
        print("  run      Run neuro pipeline and persist to Neo4j")
        print("")
        print("Options:")
        print("  --dry-run  Generate Cypher but don't connect to Neo4j")
        print("")
        print("Examples:")
        print("  python ingestion_pipeline.py pubmed 'Alzheimer biomarker'")
        print("  python ingestion_pipeline.py neuro 'Parkinson disease'")
        print("  python ingestion_pipeline.py ingest 'tau PET' pubmed 5 --dry-run")
        print("  python ingestion_pipeline.py run 'Alzheimer disease' 20 --dry-run")