"""
UniProt Connector - CoResearcher OS Sprint 21

Real connector for UniProt REST API (RESTful v2).
Queries protein knowledgebase data, sequences, functions, and annotations.

Domain-agnostic infrastructure. No medical/neurodiagnoses logic.
"""

from __future__ import annotations

import json
from typing import Any, Optional
from urllib.request import urlopen, Request
from urllib.parse import urlencode, quote

from .base_connector import ScientificConnector, ConnectorResult, EvidenceItem


class UniProtConnector(ScientificConnector):
    """
    Connector for UniProt REST API.

    Provides access to:
    - Protein sequence and function data
    - Protein-protein interactions
    - Subcellular locations and pathways
    - Post-translational modifications
    - Disease-associated variants
    """

    SOURCE_NAME = "uniprot"

    # API base URLs
    API_URL = "https://rest.uniprot.org/uniprotkb"
    SEARCH_URL = f"{API_URL}/search"
    ACCESS_URL = f"{API_URL}"
    BETA_URL = "https://rest.uniprot.org/beta"

    def _request(self, url: str, params: dict = None) -> dict:
        """Make a request to the UniProt API and return JSON."""
        if params:
            url = f"{url}?{urlencode(params)}"
        req = Request(url, headers={
            "Accept": "application/json",
            "User-Agent": "CoResearcherOS/0.1",
        })
        with urlopen(req, timeout=30) as resp:
            return json.loads(resp.read().decode())

    def search(self, query: str, max_results: int = 20, **filters) -> ConnectorResult:
        """
        Search UniProt for proteins matching *query*.

        Args:
            query: Search term (protein name, gene name, organism, etc.).
        """
        cache_key = f"search:{query}:{max_results}"
        cached = self._check_cache(cache_key)
        if cached:
            return cached

        try:
            params = {
                "query": query,
                "size": str(min(max_results, 50)),
                "format": "json",
            }

            data = self._request(self.SEARCH_URL, params)
            results = data.get("results", [])
            total = data.get("totalCount", data.get("pageInfo", {}).get("total", len(results)))

            items = []
            for protein in results:
                protein_id = protein.get("primaryAccession", "")
                organism = protein.get("organism", {})
                genes = protein.get("genes", [])
                gene_names = []
                for gene in genes:
                    gene_name = gene.get("geneName", {}).get("value", "")
                    if gene_name:
                        gene_names.append(gene_name)

                items.append({
                    "id": protein_id,
                    "source": self.SOURCE_NAME,
                    "title": protein.get("proteinDescription", {}).get(
                        "recommendedName", {}).get("fullName", {}).get("value", protein_id),
                    "description": ", ".join(gene_names) if gene_names else "",
                    "url": f"https://www.uniprot.org/uniprot/{protein_id}",
                    "gene_names": gene_names,
                    "organism": organism.get("scientificName", "") if organism else "",
                    "taxon_id": organism.get("taxonId") if organism else None,
                    "protein_length": protein.get("sequence", {}).get("length"),
                    "mass": protein.get("sequence", {}).get("molWeight"),
                    "annotation_score": protein.get("annotationScore"),
                    "protein_existence": protein.get("proteinExistence"),
                    "reviewed": protein.get("entryType") == "UniProtKB reviewed (Swiss-Prot)",
                })

            result = ConnectorResult(
                source=self.SOURCE_NAME,
                operation="search",
                query=query,
                total=total if isinstance(total, int) else len(items),
                items=items,
            )

        except Exception as e:
            result = self._error_result("search", query, str(e))

        self._set_cache(cache_key, result)
        self._log_provenance("search", query, result)
        return result

    def get(self, identifier: str) -> ConnectorResult:
        """
        Get a protein by UniProt accession or entry ID.

        Args:
            identifier: UniProt accession (e.g. "P02649" for APOE).
        """
        cache_key = f"get:{identifier}"
        cached = self._check_cache(cache_key)
        if cached:
            return cached

        try:
            url = f"{self.ACCESS_URL}/{quote(identifier)}"
            data = self._request(url)

            if not data or data.get("url") is None and not data.get("primaryAccession"):
                result = self._error_result("get", identifier,
                                            f"No protein found: {identifier}")
            else:
                protein = data
                protein_id = protein.get("primaryAccession", identifier)
                organism = protein.get("organism", {})
                genes = protein.get("genes", [])
                gene_names = []
                for gene in genes:
                    gene_name = gene.get("geneName", {}).get("value", "")
                    if gene_name:
                        gene_names.append(gene_name)

                comments = protein.get("comments", [])
                functions = [
                    c.get("texts", [{}])[0].get("value", "")
                    for c in comments
                    if c.get("commentType") == "FUNCTION"
                ]

                subcellular_locations = []
                for c in comments:
                    if c.get("commentType") == "SUBCELLULAR LOCATION":
                        for loc in c.get("subcellularLocations", []):
                            val = loc.get("location", {}).get("value", "")
                            if val:
                                subcellular_locations.append(val)

                features = protein.get("features", [])
                domains = [
                    f for f in features
                    if f.get("type") in ("DOMAIN", "ZINC_FINGER", "DNA_BIND")
                ]

                # Get related proteins by gene name
                related = []
                for gn in gene_names[:3]:
                    try:
                        rel = self.search(gn, max_results=5)
                        if not rel.error:
                            for r in rel.items:
                                if r["id"] != protein_id:
                                    related.append({
                                        "id": r["id"],
                                        "name": r["title"],
                                        "gene": gn,
                                    })
                    except Exception:
                        continue

                items = [{
                    "id": protein_id,
                    "source": self.SOURCE_NAME,
                    "title": protein.get("proteinDescription", {}).get(
                        "recommendedName", {}).get("fullName", {}).get("value", protein_id),
                    "description": ", ".join(gene_names) if gene_names else "",
                    "url": f"https://www.uniprot.org/uniprot/{protein_id}",
                    "gene_names": gene_names,
                    "organism": organism.get("scientificName", "") if organism else "",
                    "taxon_id": organism.get("taxonId") if organism else None,
                    "sequence": protein.get("sequence", {}).get("value", ""),
                    "protein_length": protein.get("sequence", {}).get("length"),
                    "mass": protein.get("sequence", {}).get("molWeight"),
                    "annotation_score": protein.get("annotationScore"),
                    "reviewed": protein.get("entryType") == "UniProtKB reviewed (Swiss-Prot)",
                    "functions": functions,
                    "subcellular_locations": subcellular_locations,
                    "domains": [
                        {
                            "type": d.get("type"),
                            "description": d.get("description", ""),
                            "start": d.get("location", {}).get("start", {}).get("value"),
                            "end": d.get("location", {}).get("end", {}).get("value"),
                        }
                        for d in domains
                    ],
                    "keywords": [
                        kw.get("name", "") for kw in protein.get("keywords", [])
                    ],
                    "go_terms": [
                        {
                            "id": go.get("goId", ""),
                            "term": go.get("term", {}).get("value", ""),
                            "category": go.get("category", ""),
                        }
                        for go in protein.get("uniProtKBCrossReferences", [])
                        if go.get("database") == "GO"
                    ][:10],
                    "related_proteins": related[:10],
                }]

                result = ConnectorResult(
                    source=self.SOURCE_NAME,
                    operation="get",
                    query=identifier,
                    total=1,
                    items=items,
                )

        except Exception as e:
            result = self._error_result("get", identifier, str(e))

        self._set_cache(cache_key, result)
        self._log_provenance("get", identifier, result)
        return result

    def related(self, identifier: str, max_results: int = 10) -> ConnectorResult:
        """
        Find related proteins by shared gene name or sequence similarity.

        Args:
            identifier: UniProt accession.
        """
        protein = self.get(identifier)
        if protein.error or not protein.items:
            return self._error_result("related", identifier,
                                      f"Cannot find protein: {identifier}")

        related_proteins = protein.items[0].get("related_proteins", [])
        result = ConnectorResult(
            source=self.SOURCE_NAME,
            operation="related",
            query=identifier,
            total=len(related_proteins),
            items=related_proteins[:max_results],
        )

        self._log_provenance("related", identifier, result)
        return result

    def evidence(self, claim_or_concept: str, max_results: int = 20) -> ConnectorResult:
        """
        Find protein evidence for a claim or concept.

        Searches UniProt and returns protein annotations as evidence items.
        """
        search_result = self.search(claim_or_concept, max_results=5)

        evidence_items = []
        for item in search_result.items:
            protein_id = item["id"]
            protein = self.get(protein_id)

            if not protein.error and protein.items:
                p = protein.items[0]

                # Function as evidence
                for func in p.get("functions", []):
                    evidence_items.append(EvidenceItem(
                        id=f"{protein_id}|function",
                        source=self.SOURCE_NAME,
                        title=f"{p['title']} - Function",
                        description=func,
                        url=p["url"],
                        relevance_score=0.7,
                        metadata={
                            "protein_id": protein_id,
                            "evidence_type": "function",
                            "gene_names": p.get("gene_names", []),
                        },
                    ))

                # Subcellular location as evidence
                for loc in p.get("subcellular_locations", []):
                    evidence_items.append(EvidenceItem(
                        id=f"{protein_id}|location|{loc}",
                        source=self.SOURCE_NAME,
                        title=f"{p['title']} - Location",
                        description=f"Subcellular location: {loc}",
                        url=p["url"],
                        relevance_score=0.5,
                        metadata={
                            "protein_id": protein_id,
                            "evidence_type": "subcellular_location",
                            "location": loc,
                        },
                    ))

                # Domains as evidence
                for domain in p.get("domains", []):
                    evidence_items.append(EvidenceItem(
                        id=f"{protein_id}|domain|{domain.get('description', '')}",
                        source=self.SOURCE_NAME,
                        title=f"{p['title']} - Domain: {domain.get('description', '')}",
                        description=f"Residues {domain.get('start', '?')}-{domain.get('end', '?')}",
                        url=p["url"],
                        relevance_score=0.6,
                        metadata={
                            "protein_id": protein_id,
                            "evidence_type": "domain",
                            "domain": domain.get("description"),
                        },
                    ))

        # Deduplicate
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


    connector = UniProtConnector()

    if len(sys.argv) > 1:
        cmd = sys.argv[1]

        if cmd == "search":
            query = sys.argv[2] if len(sys.argv) > 2 else "APOE human"
            result = connector.search(query)
            print(json.dumps(result.to_dict(), indent=2))

        elif cmd == "get":
            ident = sys.argv[2] if len(sys.argv) > 2 else "P02649"
            result = connector.get(ident)
            print(json.dumps(result.to_dict(), indent=2))

        elif cmd == "related":
            ident = sys.argv[2] if len(sys.argv) > 2 else "P02649"
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
        print("UniProt Connector - Sprint 21")
        print("=" * 70)

        print("\n--- Search: APOE human ---")
        result = connector.search("APOE human", max_results=3)
        print(f"  Total: {result.total}")
        for item in result.items[:3]:
            print(f"  - {item['title'][:60]} ({item['id']})")

        print("\n--- Get P02649 (APOE) ---")
        target = connector.get("P02649")
        if not target.error and target.items:
            print(f"  Name: {target.items[0]['title'][:60]}")
            print(f"  Gene: {', '.join(target.items[0].get('gene_names', []))}")
            print(f"  Length: {target.items[0].get('protein_length')} aa")
            print(f"  Functions: {len(target.items[0].get('functions', []))}")
            print(f"  Domains: {len(target.items[0].get('domains', []))}")
            print(f"  Related proteins: {len(target.items[0].get('related_proteins', []))}")

        print("\n--- Evidence for 'APOE lipid transport' ---")
        ev = connector.evidence("APOE lipid transport", max_results=5)
        print(f"  Total evidence: {ev.total}")
        for item in ev.items[:3]:
            print(f"  - {item['title'][:60]}")

        print("\n--- Provenance ---")
        for entry in connector.get_provenance_log():
            print(f"  {entry['operation']}: {entry['query']} → {entry['total_results']} results")

        print("\nDone.")