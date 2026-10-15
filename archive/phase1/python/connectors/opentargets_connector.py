"""
Open Targets Connector - CoResearcher OS Sprint 21

Real connector for Open Targets Platform GraphQL API.
Queries target-disease associations, drug targets, and genomics evidence.

Domain-agnostic infrastructure. No medical/neurodiagnoses logic.
"""

from __future__ import annotations

import json
from typing import Any, Optional
from urllib.request import urlopen, Request

from .base_connector import ScientificConnector, ConnectorResult, EvidenceItem


class OpenTargetsConnector(ScientificConnector):
    """
    Connector for Open Targets Platform GraphQL API.

    Provides access to:
    - Target-disease associations
    - Drug-target interactions
    - Genomics evidence (GWAS, mutations, pathways)
    - Known drugs and clinical precedence
    """

    SOURCE_NAME = "opentargets"

    # API endpoint
    API_URL = "https://api.platform.opentargets.org/api/v4/graphql"

    # GraphQL query templates
    SEARCH_QUERY = """
    query searchTargets($query: String!, $size: Int!) {
      search(queryString: $query, entityNames: ["target", "disease"], page: {index: 0, size: $size}) {
        hits {
          id
          name
          entity
          description
          score
        }
        total
      }
    }
    """

    TARGET_QUERY = """
    query getTarget($id: String!) {
      target(ensemblId: $id) {
        id
        approvedSymbol
        approvedName
        biotype
        functionDescriptions
        subcellularLocations {
          location
        }
        proteinAnnotations {
          id
          functions {
            name
          }
        }
        associatedDiseases {
          count
          rows {
            disease {
              id
              name
              description
            }
            score
            datatypeScores {
              id
              score
            }
          }
        }
      }
    }
    """

    DISEASE_ASSOCIATIONS_QUERY = """
    query getDiseaseAssociations($id: String!, $size: Int!) {
      disease(efoId: $id) {
        id
        name
        description
        associatedTargets(page: {index: 0, size: $size}) {
          count
          rows {
            target {
              id
              approvedSymbol
              approvedName
            }
            score
            evidenceCount
          }
        }
      }
    }
    """

    EVIDENCE_QUERY = """
    query getEvidence($ensemblId: String!, $efoId: String!, $size: Int!) {
      evidence(targetId: $ensemblId, diseaseId: $efoId, page: {index: 0, size: $size}) {
        count
        rows {
          id
          score
          clinicalSignificances
          literature
          studyId
          sourceDatabase
          study {
            traitReported
            pubmedId
          }
        }
      }
    }
    """

    def _graphql_request(self, query: str, variables: dict) -> dict:
        """Execute a GraphQL request and return the JSON response."""
        payload = json.dumps({"query": query, "variables": variables}).encode()
        req = Request(
            self.API_URL,
            data=payload,
            headers={
                "Content-Type": "application/json",
                "User-Agent": "CoResearcherOS/0.1",
            },
        )
        with urlopen(req, timeout=30) as resp:
            return json.loads(resp.read().decode())

    def search(self, query: str, max_results: int = 20, **filters) -> ConnectorResult:
        """
        Search Open Targets for targets and diseases.

        Args:
            query: Search term (gene, disease, drug name).
        """
        cache_key = f"search:{query}:{max_results}"
        cached = self._check_cache(cache_key)
        if cached:
            return cached

        try:
            data = self._graphql_request(self.SEARCH_QUERY, {
                "query": query,
                "size": min(max_results, 50),
            })

            search_data = data.get("data", {}).get("search", {})
            hits = search_data.get("hits", [])
            total = search_data.get("total", 0)

            items = []
            for hit in hits:
                items.append({
                    "id": hit.get("id", ""),
                    "source": self.SOURCE_NAME,
                    "title": hit.get("name", ""),
                    "description": hit.get("description", ""),
                    "url": f"https://platform.opentargets.org/target/{hit.get('id', '')}",
                    "entity_type": hit.get("entity", ""),
                    "score": hit.get("score", 0),
                })

            result = ConnectorResult(
                source=self.SOURCE_NAME,
                operation="search",
                query=query,
                total=total,
                items=items,
            )

        except Exception as e:
            result = self._error_result("search", query, str(e))

        self._set_cache(cache_key, result)
        self._log_provenance("search", query, result)
        return result

    def get(self, identifier: str) -> ConnectorResult:
        """
        Get a target by Ensembl ID or disease by EFO ID.

        Args:
            identifier: Ensembl gene ID (e.g. "ENSG00000130234") or EFO ID.
        """
        cache_key = f"get:{identifier}"
        cached = self._check_cache(cache_key)
        if cached:
            return cached

        try:
            # Try as target first
            data = self._graphql_request(self.TARGET_QUERY, {"id": identifier})
            target = data.get("data", {}).get("target")

            if target:
                diseases = target.get("associatedDiseases", {})
                items = [{
                    "id": target.get("id", identifier),
                    "source": self.SOURCE_NAME,
                    "title": target.get("approvedSymbol", ""),
                    "description": target.get("approvedName", ""),
                    "url": f"https://platform.opentargets.org/target/{target.get('id', '')}",
                    "biotype": target.get("biotype", ""),
                    "functions": target.get("functionDescriptions", []),
                    "subcellular_locations": [
                        loc.get("location", "") for loc in target.get("subcellularLocations", [])
                    ],
                    "associated_disease_count": diseases.get("count", 0),
                    "associated_diseases": [
                        {
                            "id": row.get("disease", {}).get("id", ""),
                            "name": row.get("disease", {}).get("name", ""),
                            "score": row.get("score", 0),
                        }
                        for row in diseases.get("rows", [])[:10]
                    ],
                }]

                result = ConnectorResult(
                    source=self.SOURCE_NAME,
                    operation="get",
                    query=identifier,
                    total=1,
                    items=items,
                )
            else:
                # Try as disease
                disease_data = self._graphql_request(
                    self.DISEASE_ASSOCIATIONS_QUERY,
                    {"id": identifier, "size": 5},
                )
                disease = disease_data.get("data", {}).get("disease")

                if disease:
                    items = [{
                        "id": disease.get("id", identifier),
                        "source": self.SOURCE_NAME,
                        "title": disease.get("name", ""),
                        "description": disease.get("description", ""),
                        "url": f"https://platform.opentargets.org/disease/{disease.get('id', '')}",
                        "associated_targets": [
                            {
                                "id": row.get("target", {}).get("id", ""),
                                "symbol": row.get("target", {}).get("approvedSymbol", ""),
                                "score": row.get("score", 0),
                            }
                            for row in disease.get("associatedTargets", {}).get("rows", [])
                        ],
                    }]

                    result = ConnectorResult(
                        source=self.SOURCE_NAME,
                        operation="get",
                        query=identifier,
                        total=1,
                        items=items,
                    )
                else:
                    result = self._error_result("get", identifier,
                                                f"No target or disease found: {identifier}")

        except Exception as e:
            result = self._error_result("get", identifier, str(e))

        self._set_cache(cache_key, result)
        self._log_provenance("get", identifier, result)
        return result

    def related(self, identifier: str, max_results: int = 10) -> ConnectorResult:
        """
        Find related targets or diseases.

        For a target, returns associated diseases.
        For a disease, returns associated targets.
        """
        # Fetch the entity
        entity = self.get(identifier)
        if entity.error or not entity.items:
            return self._error_result("related", identifier,
                                      f"Cannot find entity: {identifier}")

        item = entity.items[0]

        # Return associated entities
        related_items = []
        if "associated_diseases" in item:
            related_items = item["associated_diseases"]
        elif "associated_targets" in item:
            related_items = item["associated_targets"]

        result = ConnectorResult(
            source=self.SOURCE_NAME,
            operation="related",
            query=identifier,
            total=len(related_items),
            items=related_items[:max_results],
        )

        self._log_provenance("related", identifier, result)
        return result

    def evidence(self, claim_or_concept: str, max_results: int = 20) -> ConnectorResult:
        """
        Find target-disease evidence for a claim or concept.

        Searches Open Targets for associations and returns evidence.
        """
        search_result = self.search(claim_or_concept, max_results=5)

        evidence_items = []
        for item in search_result.items:
            entity_id = item["id"]
            entity_type = item.get("entity_type", "")

            if entity_type == "target":
                # Get target details with disease associations
                target = self.get(entity_id)
                if not target.error and target.items:
                    for disease in target.items[0].get("associated_diseases", []):
                        evidence_items.append(EvidenceItem(
                            id=f"{entity_id}|{disease['id']}",
                            source=self.SOURCE_NAME,
                            title=f"{item['title']} ↔ {disease['name']}",
                            description=f"Target-Disease association score: {disease.get('score', 0):.3f}",
                            url=f"https://platform.opentargets.org/evidence/{entity_id}/{disease['id']}",
                            relevance_score=disease.get("score", 0),
                            metadata={
                                "target_id": entity_id,
                                "disease_id": disease["id"],
                                "association_score": disease.get("score"),
                            },
                        ))

        # Deduplicate by ID
        seen: set[str] = set()
        deduped = []
        for ev in evidence_items:
            if ev.id not in seen:
                seen.add(ev.id)
                deduped.append(ev.to_dict())

        result = ConnectorResult(
            source=self.SOURCE_NAME,
            operation="evidence",
            query=claim_or_concept,
            total=len(deduped),
            items=deduped[:max_results],
        )

        self._log_provenance("evidence", claim_or_concept, result)
        return result


# =============================================================================
# CLI Test
# =============================================================================

if __name__ == "__main__":
    import sys

# Security tier: PUBLIC — DO NOT MODIFY
# See python/_tiers.py for classification
SECURITY_TIER = "PUBLIC"


    connector = OpenTargetsConnector()

    if len(sys.argv) > 1:
        cmd = sys.argv[1]

        if cmd == "search":
            query = sys.argv[2] if len(sys.argv) > 2 else "APOE"
            result = connector.search(query)
            print(json.dumps(result.to_dict(), indent=2))

        elif cmd == "get":
            ident = sys.argv[2] if len(sys.argv) > 2 else "ENSG00000130234"
            result = connector.get(ident)
            print(json.dumps(result.to_dict(), indent=2))

        elif cmd == "related":
            ident = sys.argv[2] if len(sys.argv) > 2 else "ENSG00000130234"
            result = connector.related(ident)
            print(json.dumps(result.to_dict(), indent=2))

        elif cmd == "evidence":
            claim = sys.argv[2] if len(sys.argv) > 2 else "APOE Alzheimer"
            result = connector.evidence(claim)
            print(json.dumps(result.to_dict(), indent=2))

        else:
            print(f"Unknown command: {cmd}")
    else:
        # Demo mode
        print("=" * 70)
        print("Open Targets Connector - Sprint 21")
        print("=" * 70)

        print("\n--- Search: APOE ---")
        result = connector.search("APOE", max_results=3)
        print(f"  Total: {result.total}")
        for item in result.items[:3]:
            print(f"  - [{item.get('entity_type', '?')}] {item['title']}")

        print("\n--- Get target: ENSG00000130234 (APOE) ---")
        target = connector.get("ENSG00000130234")
        if not target.error and target.items:
            print(f"  Symbol: {target.items[0]['title']}")
            print(f"  Associated diseases: {target.items[0].get('associated_disease_count', 0)}")

        print("\n--- Evidence: APOE Alzheimer ---")
        ev = connector.evidence("APOE Alzheimer", max_results=3)
        print(f"  Total evidence items: {ev.total}")
        for item in ev.items[:3]:
            print(f"  - {item['title']} (score: {item.get('relevance_score', 0):.2f})")

        print("\n--- Provenance ---")
        for entry in connector.get_provenance_log():
            print(f"  {entry['operation']}: {entry['query']} → {entry['total_results']} results")

        print("\nDone.")