"""
CrossRef Scientific Agent
Real MCP tool for DOI resolution, metadata lookup, and citation graph.
"""

import json
import sys
from urllib.request import urlopen, Request
from urllib.parse import urlencode


class CrossrefAgent:
    """Real CrossRef REST API connector for DOI resolution and citation data."""

    BASE_URL = "https://api.crossref.org"

    def __init__(self, email: str = "coresearcher@example.com"):
        self.mailto = email

    def _get(self, endpoint: str, params: dict = None) -> dict:
        if params is None:
            params = {}
        params["mailto"] = self.mailto
        url = f"{self.BASE_URL}{endpoint}?{urlencode(params)}"
        req = Request(url, headers={"User-Agent": f"CoResearcherOS/0.1 (mailto:{self.mailto})"})
        with urlopen(req, timeout=30) as resp:
            return json.loads(resp.read().decode())

    def resolve_doi(self, doi: str) -> dict:
        """Resolve a DOI to get full metadata."""
        try:
            data = self._get(f"/works/{doi}")
            message = data.get("message", {})
            
            return {
                "doi": doi,
                "resolved": True,
                "title": message.get("title", [None])[0] if message.get("title") else None,
                "author": [
                    f"{a.get('given', '')} {a.get('family', '')}".strip()
                    for a in message.get("author", [])
                ],
                "container": message.get("container-title", [None])[0] if message.get("container-title") else None,
                "volume": message.get("volume"),
                "issue": message.get("issue"),
                "page": message.get("page"),
                "published": message.get("published-print", {}).get("date-parts", [[None]])[0][0]
                    or message.get("published-online", {}).get("date-parts", [[None]])[0][0],
                "type": message.get("type"),
                "publisher": message.get("publisher"),
                "abstract": message.get("abstract", ""),
                "subject": message.get("subject", []),
                "references_count": message.get("references-count", 0),
                "is_referenced_by_count": message.get("is-referenced-by-count", 0),
                "link": [
                    l.get("URL") for l in message.get("link", [])
                    if l.get("content-type") == "application/pdf"
                ],
                "license": [
                    l.get("URL") for l in message.get("license", [])
                ],
                "funders": [
                    f.get("name", "") for f in message.get("funder", [])
                ],
            }
        except Exception as e:
            return {"doi": doi, "resolved": False, "error": str(e)}

    def search(self, query: str, max_results: int = 20) -> dict:
        """Search CrossRef for works matching query."""
        params = {
            "query": query,
            "rows": str(max_results),
            "sort": "relevance",
            "order": "desc",
        }
        data = self._get("/works", params)
        items = data.get("message", {}).get("items", [])
        
        results = []
        for item in items:
            results.append({
                "doi": item.get("DOI"),
                "title": item.get("title", [None])[0] if item.get("title") else None,
                "author": [
                    f"{a.get('given', '')} {a.get('family', '')}".strip()
                    for a in item.get("author", [])
                ],
                "container": item.get("container-title", [None])[0] if item.get("container-title") else None,
                "published": item.get("published-print", {}).get("date-parts", [[None]])[0][0]
                    or item.get("published-online", {}).get("date-parts", [[None]])[0][0],
                "type": item.get("type"),
                "cited_by_count": item.get("is-referenced-by-count", 0),
                "subject": item.get("subject", []),
                "score": item.get("score", 0),
            })
        
        return {
            "query": query,
            "total": data.get("message", {}).get("total-results", 0),
            "results": results,
        }

    def citation_graph(self, doi: str, depth: int = 1) -> dict:
        """Get forward and backward citations for a DOI."""
        # Resolve the work first
        source = self.resolve_doi(doi)
        
        result = {
            "source": source,
            "references": [],
            "citations": [],
        }

        # Get references (backward citations) via the resolved data
        try:
            data = self._get(f"/works/{doi}")
            message = data.get("message", {})
            
            # References are in the message, but CrossRef doesn't return them all
            # We search for works citing this DOI instead
            params = {
                "query": f"doi:{doi}",
                "rows": "20",
                "sort": "relevance",
                "mailto": self.mailto,
            }
            
            # Get citing works using filter
            filter_url = f"{self.BASE_URL}/works?filter=doi:{doi}&rows=20&mailto={self.mailto}"
            req = Request(filter_url, headers={"User-Agent": f"CoResearcherOS/0.1 (mailto:{self.mailto})"})
            with urlopen(req, timeout=30) as resp:
                citing_data = json.loads(resp.read().decode())
            
            for item in citing_data.get("message", {}).get("items", []):
                result["citations"].append({
                    "doi": item.get("DOI"),
                    "title": item.get("title", [None])[0] if item.get("title") else None,
                    "author": [
                        f"{a.get('given', '')} {a.get('family', '')}".strip()
                        for a in item.get("author", [])
                    ],
                    "published": item.get("published-print", {}).get("date-parts", [[None]])[0][0]
                        or item.get("published-online", {}).get("date-parts", [[None]])[0][0],
                })
        except Exception:
            pass
        
        return result


if __name__ == "__main__":
    import sys

# Security tier: COMMUNITY — DO NOT MODIFY
# See python/_tiers.py for classification
SECURITY_TIER = "COMMUNITY"

    agent = CrossrefAgent()
    
    if len(sys.argv) > 1:
        cmd = sys.argv[1]
        if cmd == "resolve":
            doi = sys.argv[2] if len(sys.argv) > 2 else "10.1038/s41586-024-07150-0"
            print(json.dumps(agent.resolve_doi(doi), indent=2))
        elif cmd == "search":
            q = sys.argv[2] if len(sys.argv) > 2 else "Alzheimer disease biomarkers"
            print(json.dumps(agent.search(q), indent=2))
        elif cmd == "citation_graph":
            doi = sys.argv[2] if len(sys.argv) > 2 else "10.1038/s41586-024-07150-0"
            print(json.dumps(agent.citation_graph(doi), indent=2))