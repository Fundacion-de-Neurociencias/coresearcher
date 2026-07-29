"""
OpenAlex Scientific Agent
Real MCP tool that queries the OpenAlex API for papers, authors, and concepts.
"""

import json
import sys
from typing import Optional
from urllib.request import urlopen, Request
from urllib.parse import urlencode


class OpenAlexAgent:
    """Real OpenAlex connector. 250M+ scientific papers, authors, institutions, concepts."""

    BASE_URL = "https://api.openalex.org"

    def __init__(self, email: str = "coresearcher@example.com"):
        self.headers = {
            "User-Agent": f"CoResearcherOS/0.1 (mailto:{email})",
            "Accept": "application/json",
        }

    def _get(self, endpoint: str, params: dict) -> dict:
        url = f"{self.BASE_URL}{endpoint}?{urlencode(params)}"
        req = Request(url, headers=self.headers)
        with urlopen(req, timeout=30) as resp:
            return json.loads(resp.read().decode())

    def search_papers(
        self, query: str, max_results: int = 20, sort: str = "relevance_score:desc"
    ) -> dict:
        """Real search against OpenAlex works endpoint."""
        params = {
            "search": query,
            "per_page": str(min(max_results, 200)),
            "sort": sort,
            "mailto": self.headers["User-Agent"].split("mailto:")[1].rstrip(")"),
        }
        data = self._get("/works", params)
        
        results = []
        for work in data.get("results", []):
            results.append({
                "id": work.get("id", ""),
                "doi": work.get("doi", ""),
                "title": work.get("title", ""),
                "publication_year": work.get("publication_year"),
                "type": work.get("type", ""),
                "cited_by_count": work.get("cited_by_count", 0),
                "authorships": [
                    {
                        "author": a.get("author", {}).get("display_name", ""),
                        "author_id": a.get("author", {}).get("id", ""),
                        "institutions": [
                            i.get("display_name", "") for i in a.get("institutions", [])
                        ],
                    }
                    for a in work.get("authorships", [])
                ],
                "concepts": [
                    {
                        "name": c.get("display_name", ""),
                        "score": c.get("score", 0),
                        "level": c.get("level", 0),
                    }
                    for c in work.get("concepts", [])
                    if c.get("score", 0) > 0.3
                ],
                "keywords": [k.get("keyword", "") for k in work.get("keywords", [])],
                "abstract_inverted_index": work.get("abstract_inverted_index"),
                "source": work.get("primary_location", {}).get("source", {}).get("display_name"),
            })
        
        return {
            "query": query,
            "total": data.get("meta", {}).get("count", 0),
            "results": results,
        }

    def search_authors(self, query: str, max_results: int = 20) -> dict:
        """Search authors by name."""
        params = {"search": query, "per_page": str(max_results)}
        data = self._get("/authors", params)
        
        results = []
        for author in data.get("results", []):
            results.append({
                "id": author.get("id", ""),
                "name": author.get("display_name", ""),
                "orcid": author.get("orcid"),
                "h_index": author.get("summary_stats", {}).get("h_index"),
                "cited_by_count": author.get("cited_by_count", 0),
                "works_count": author.get("works_count", 0),
                "last_known_institutions": [
                    i.get("display_name", "")
                    for i in author.get("last_known_institutions", [])
                ],
                "topics": [
                    t.get("display_name", "")
                    for t in author.get("topics", [])
                    if t.get("count", 0) > 0
                ][:5],
            })
        
        return {"query": query, "total": data.get("meta", {}).get("count", 0), "results": results}

    def search_concepts(self, query: str, max_results: int = 10) -> dict:
        """Search scientific concepts."""
        params = {"search": query, "per_page": str(max_results)}
        data = self._get("/concepts", params)
        
        results = []
        for concept in data.get("results", []):
            results.append({
                "id": concept.get("id", ""),
                "name": concept.get("display_name", ""),
                "description": concept.get("description", ""),
                "level": concept.get("level", 0),
                "works_count": concept.get("works_count", 0),
                "cited_by_count": concept.get("cited_by_count", 0),
                "related_concepts": [
                    {"name": c.get("display_name", ""), "score": c.get("score", 0)}
                    for c in concept.get("related_concepts", [])
                    if c.get("score", 0) > 0.5
                ][:5],
            })
        
        return {"query": query, "total": data.get("meta", {}).get("count", 0), "results": results}

    def get_citation_graph(self, work_id: str, direction: str = "both", depth: int = 1) -> dict:
        """Get citation graph for a paper."""
        if not work_id.startswith("https://"):
            work_id = f"https://openalex.org/W{work_id}"
        
        params = {"mailto": self.headers["User-Agent"].split("mailto:")[1].rstrip(")")}
        data = self._get(f"/works/{work_id.replace(self.BASE_URL, '')}", params)
        
        result = {
            "work": {
                "id": data.get("id"),
                "title": data.get("title"),
                "cited_by_count": data.get("cited_by_count", 0),
            },
            "referenced_works": [],
            "cited_by_works": [],
        }
        
        if direction in ("outgoing", "both"):
            ref_ids = data.get("referenced_works", [])[:20]
            for ref_id in ref_ids:
                try:
                    ref = self._get(ref_id.replace(self.BASE_URL, ""), params)
                    result["referenced_works"].append({
                        "id": ref.get("id"),
                        "title": ref.get("title"),
                        "cited_by_count": ref.get("cited_by_count", 0),
                        "publication_year": ref.get("publication_year"),
                    })
                except Exception:
                    result["referenced_works"].append({"id": ref_id})
        
        if direction in ("incoming", "both"):
            cited_params = {
                "filter": f"cites:{work_id}",
                "per_page": "20",
                "mailto": params["mailto"],
            }
            cited = self._get("/works", cited_params)
            for work in cited.get("results", []):
                result["cited_by_works"].append({
                    "id": work.get("id"),
                    "title": work.get("title"),
                    "cited_by_count": work.get("cited_by_count", 0),
                    "publication_year": work.get("publication_year"),
                })
        
        return result


if __name__ == "__main__":
    import sys

# Security tier: COMMUNITY — DO NOT MODIFY
# See python/_tiers.py for classification
SECURITY_TIER = "COMMUNITY"

    agent = OpenAlexAgent()
    
    if len(sys.argv) > 1:
        cmd = sys.argv[1]
        if cmd == "search_papers":
            q = sys.argv[2] if len(sys.argv) > 2 else "Alzheimer tau PET"
            print(json.dumps(agent.search_papers(q), indent=2))
        elif cmd == "search_authors":
            q = sys.argv[2] if len(sys.argv) > 2 else "John Hardy"
            print(json.dumps(agent.search_authors(q), indent=2))
        elif cmd == "search_concepts":
            q = sys.argv[2] if len(sys.argv) > 2 else "neurodegenerative disease"
            print(json.dumps(agent.search_concepts(q), indent=2))
        elif cmd == "citation_graph":
            wid = sys.argv[2] if len(sys.argv) > 2 else "https://openalex.org/W2741809807"
            print(json.dumps(agent.get_citation_graph(wid), indent=2))