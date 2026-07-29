"""
Neo4j Client for CoResearcher OS
Real connector that persists Paper → Claim → Evidence → Concept graphs.
Supports both live Neo4j and Cypher-only (dry-run) modes.
"""

import json
import os
import sys
from typing import Optional

try:
    from neo4j import GraphDatabase, basic_auth
    NEO4J_AVAILABLE = True
except ImportError:
    NEO4J_AVAILABLE = False


class Neo4jClient:
    """
    Neo4j client that stores papers, claims, evidence, and concepts
    as a knowledge graph for scientific discovery.
    """

    def __init__(
        self,
        uri: Optional[str] = None,
        user: Optional[str] = None,
        password: Optional[str] = None,
        dry_run: bool = False,
    ):
        self.dry_run = dry_run
        self._driver = None
        self._generated_cypher: list[str] = []

        if dry_run:
            return

        uri = uri or os.environ.get("NEO4J_URI", "bolt://localhost:7687")
        user = user or os.environ.get("NEO4J_USER", "neo4j")
        password = password or os.environ.get("NEO4J_PASSWORD", "coresearcher_dev")

        if not NEO4J_AVAILABLE:
            print("[Neo4j] neo4j driver not installed, falling back to dry-run mode", file=sys.stderr)
            self.dry_run = True
            return

        try:
            self._driver = GraphDatabase.driver(uri, auth=basic_auth(user, password))
            self._driver.verify_connectivity()
            print(f"[Neo4j] Connected to {uri}", file=sys.stderr)
        except Exception as e:
            print(f"[Neo4j] Cannot connect to {uri}: {e}", file=sys.stderr)
            print("[Neo4j] Falling back to Cypher-only (dry-run) mode", file=sys.stderr)
            self.dry_run = True

    def close(self):
        if self._driver:
            self._driver.close()

    def _run(self, query: str, params: dict = None) -> list:
        """Execute a Cypher query against Neo4j or collect it for dry-run."""
        if self.dry_run:
            self._generated_cypher.append(query)
            return []

        if not self._driver:
            return []

        with self._driver.session() as session:
            result = session.run(query, params or {})
            return [r.data() for r in result]

    def initialize_schema(self):
        """Create constraints and indexes for the knowledge graph."""
        queries = [
            "CREATE CONSTRAINT paper_id IF NOT EXISTS FOR (p:Paper) REQUIRE p.id IS UNIQUE",
            "CREATE CONSTRAINT claim_id IF NOT EXISTS FOR (c:Claim) REQUIRE c.id IS UNIQUE",
            "CREATE CONSTRAINT concept_name IF NOT EXISTS FOR (c:Concept) REQUIRE c.name IS UNIQUE",
            "CREATE INDEX paper_title_index IF NOT EXISTS FOR (p:Paper) ON (p.title)",
            "CREATE INDEX paper_doi_index IF NOT EXISTS FOR (p:Paper) ON (p.doi)",
            "CREATE INDEX claim_text_index IF NOT EXISTS FOR (c:Claim) ON (c.text)",
            "CREATE FULLTEXT INDEX paper_fulltext IF NOT EXISTS FOR (p:Paper) ON EACH [p.title, p.abstract]",
            "CREATE FULLTEXT INDEX claim_fulltext IF NOT EXISTS FOR (c:Claim) ON EACH [c.text]",
        ]
        for q in queries:
            self._run(q)
        print("[Neo4j] Schema initialized", file=sys.stderr)

    def ingest_pipeline_result(self, pipeline_result: dict) -> dict:
        """
        Store full pipeline result into Neo4j.
        
        Creates:
          - (:Paper {id, title, doi, pmid, source, processedAt})
          - (:Claim {id, text, confidence, type, domain})
          - (:Evidence {value, type})
          - (:Concept {name, domain})
          - Relationships: (Paper)-[:PRODUCES]->(Claim),
                           (Claim)-[:SUPPORTED_BY]->(Evidence),
                           (Paper)-[:MENTIONS]->(Concept),
                           (Claim)-[:ABOUT]->(Concept)
        """
        papers_created = 0
        claims_created = 0
        evidence_created = 0
        concepts_created = 0

        for paper_data in pipeline_result.get("papers", []):
            source = paper_data.get("source", {})
            pmid = source.get("pmid", "")
            doi = source.get("doi", "")
            title = source.get("title", "")

            paper_id = pmid or doi or f"unknown-{hash(title)}"

            # Create Paper node
            self._run(
                """
                MERGE (p:Paper {id: $id})
                SET p.title = $title,
                    p.pmid = $pmid,
                    p.doi = $doi,
                    p.processedAt = datetime()
                ON CREATE SET p.createdAt = datetime()
                """,
                {"id": paper_id, "title": title[:200], "pmid": pmid or "", "doi": doi or ""},
            )
            papers_created += 1

            # Create Claim nodes and relationships
            for claim in paper_data.get("claims", []):
                statement = claim.get("statement", "")
                claim_id = f"C{abs(hash(statement)) % 10**12}"
                self._run(
                    """
                    MERGE (c:Claim {id: $id})
                    SET c.text = $text,
                        c.confidence = $confidence,
                        c.type = $type,
                        c.domain = $domain
                    MERGE (p:Paper {id: $paper_id})-[:PRODUCES]->(c)
                    """,
                    {
                        "id": claim_id,
                        "text": statement[:500],
                        "confidence": claim.get("confidence", 0.5),
                        "type": claim.get("type", "finding"),
                        "domain": claim.get("domain", "general_biomedical"),
                        "paper_id": paper_id,
                    },
                )
                claims_created += 1

                # Create Evidence and link to Claim
                for evidence in claim.get("evidence", []):
                    ev_value = evidence.get("value", "")[:200]
                    ev_id = f"E{abs(hash(str(evidence))) % 10**12}"
                    self._run(
                        """
                        MERGE (e:Evidence {id: $id})
                        SET e.value = $value, e.type = $type
                        MERGE (c:Claim {id: $claim_id})-[:SUPPORTED_BY]->(e)
                        """,
                        {
                            "id": ev_id,
                            "value": ev_value,
                            "type": evidence.get("type", "statistical"),
                            "claim_id": claim_id,
                        },
                    )
                    evidence_created += 1

                # Create Concept nodes and link Paper/Claim to them
                for entity in claim.get("entities", []):
                    domain = claim.get("domain", "general_biomedical")
                    self._run(
                        """
                        MERGE (con:Concept {name: $name})
                        SET con.domain = $domain
                        MERGE (p:Paper {id: $paper_id})-[:MENTIONS]->(con)
                        MERGE (c:Claim {id: $claim_id})-[:ABOUT]->(con)
                        """,
                        {"name": entity, "domain": domain, "paper_id": paper_id, "claim_id": claim_id},
                    )
                    concepts_created += 1

        summary = {
            "papers_created": papers_created,
            "claims_created": claims_created,
            "evidence_created": evidence_created,
            "concepts_created": concepts_created,
            "mode": "dry_run" if self.dry_run else "live",
            "total_cypher_queries": len(self._generated_cypher),
        }

        print(f"[Neo4j] Ingestion complete: {json.dumps(summary)}", file=sys.stderr)
        return summary

    def get_generated_cypher(self) -> str:
        """Return all generated Cypher queries as a string (for export)."""
        return ";\n".join(self._generated_cypher) + ";"

    def query_claims_by_domain(self, domain: str, limit: int = 50) -> list:
        """Query claims for a specific biomedical domain."""
        return self._run(
            """
            MATCH (c:Claim {domain: $domain})
            RETURN c.text AS statement, c.confidence AS confidence, c.type AS type
            ORDER BY c.confidence DESC
            LIMIT $limit
            """,
            {"domain": domain, "limit": limit},
        )

    def query_papers_by_entity(self, entity: str) -> list:
        """Find papers mentioning a specific entity (gene, protein, biomarker)."""
        return self._run(
            """
            MATCH (p:Paper)-[:MENTIONS]->(con:Concept {name: $entity})
            RETURN p.title AS title, p.doi AS doi, p.pmid AS pmid
            """,
            {"entity": entity},
        )

    def query_claim_network(self, entity: str, max_depth: int = 2) -> list:
        """Get the claim network around an entity."""
        return self._run(
            """
            MATCH (con:Concept {name: $entity})<-[:ABOUT]-(c:Claim)<-[:PRODUCES]-(p:Paper)
            OPTIONAL MATCH (c)-[:SUPPORTED_BY]->(e:Evidence)
            RETURN c.text AS claim, c.confidence AS confidence,
                   p.title AS paper, e.value AS evidence
            ORDER BY c.confidence DESC
            """,
            {"entity": entity},
        )


if __name__ == "__main__":
    import sys

# Security tier: PUBLIC — DO NOT MODIFY
# See python/_tiers.py for classification
SECURITY_TIER = "PUBLIC"


    client = Neo4jClient(dry_run=True)

    if len(sys.argv) > 1 and sys.argv[1] == "test":
        # Quick test with sample data
        sample_result = {
            "query": "Alzheimer tau PET biomarker",
            "source": "pubmed",
            "total_papers": 1,
            "total_claims": 2,
            "papers": [
                {
                    "source": {
                        "pmid": "38273008",
                        "doi": "10.1016/S1474-4422(22)00168-5",
                        "title": "Tau biomarkers in Alzheimer's disease: towards implementation in clinical practice",
                    },
                    "claims": [
                        {
                            "statement": "Plasma pTau217 is significantly associated with cognitive decline in patients with MCI",
                            "type": "association",
                            "confidence": 0.85,
                            "domain": "neurodegeneration",
                            "evidence": [{"type": "statistical", "value": "p<0.001"}],
                            "entities": ["pTau217", "MCI", "Alzheimer"],
                        }
                    ],
                    "claim_count": 1,
                }
            ],
        }
        summary = client.ingest_pipeline_result(sample_result)
        print(json.dumps(summary, indent=2))
        print("\n--- Generated Cypher ---")
        print(client.get_generated_cypher())