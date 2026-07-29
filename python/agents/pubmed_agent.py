"""
PubMed Scientific Agent
Real MCP tool that queries NCBI E-utilities API for biomedical literature.
"""

import json
import sys
from typing import Any, Optional
from urllib.request import urlopen, Request
from urllib.parse import urlencode

# Security tier: COMMUNITY — DO NOT MODIFY
# See python/_tiers.py for classification
SECURITY_TIER = "COMMUNITY"



class PubMedAgent:
    """Real PubMed connector using NCBI E-utilities API."""

    BASE_URL = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils"
    SEARCH_URL = f"{BASE_URL}/esearch.fcgi"
    SUMMARY_URL = f"{BASE_URL}/esummary.fcgi"
    FETCH_URL = f"{BASE_URL}/efetch.fcgi"

    def __init__(self, email: str = "coresearcher@example.com"):
        self.email = email

    def search(self, query: str, max_results: int = 20, sort: str = "relevance") -> dict:
        """Real search against PubMed."""
        params = {
            "db": "pubmed",
            "term": query,
            "retmax": str(max_results),
            "retmode": "json",
            "sort": sort,
            "email": self.email,
        }
        url = f"{self.SEARCH_URL}?{urlencode(params)}"
        req = Request(url, headers={"User-Agent": "CoResearcherOS/0.1"})
        
        with urlopen(req, timeout=30) as resp:
            data = json.loads(resp.read().decode())
        
        id_list = data.get("esearchresult", {}).get("idlist", [])
        
        if not id_list:
            return {"query": query, "total": 0, "results": []}

        # Fetch metadata for found IDs
        summary_params = {
            "db": "pubmed",
            "id": ",".join(id_list),
            "retmode": "json",
            "email": self.email,
        }
        summary_url = f"{self.SUMMARY_URL}?{urlencode(summary_params)}"
        req = Request(summary_url, headers={"User-Agent": "CoResearcherOS/0.1"})

        with urlopen(req, timeout=30) as resp:
            summary_data = json.loads(resp.read().decode())

        results = summary_data.get("result", {})
        papers = []
        for pmid in id_list:
            paper = results.get(pmid, {})
            papers.append({
                "pmid": pmid,
                "title": paper.get("title", ""),
                "source": paper.get("source", ""),
                "pubdate": paper.get("pubdate", ""),
                "authors": [
                    a.get("name", "") for a in paper.get("authors", [])
                    if isinstance(a, dict)
                ],
                "doi": next(
                    (a.get("value", "") for a in paper.get("articleids", [])
                     if isinstance(a, dict) and a.get("idtype") == "doi"),
                    None,
                ),
                "abstract": None,  # Requires efetch
            })
        
        return {
            "query": query,
            "total": int(data.get("esearchresult", {}).get("count", 0)),
            "results": papers,
        }

    def get_abstract(self, pmid: str) -> Optional[str]:
        """Fetch real abstract for a PMID."""
        params = {
            "db": "pubmed",
            "id": pmid,
            "retmode": "xml",
            "rettype": "abstract",
            "email": self.email,
        }
        url = f"{self.FETCH_URL}?{urlencode(params)}"
        req = Request(url, headers={"User-Agent": "CoResearcherOS/0.1"})

        try:
            with urlopen(req, timeout=30) as resp:
                data = resp.read().decode()
                # Simple XML parsing for abstract text
                start = data.find("<AbstractText")
                if start == -1:
                    return None
                end = data.find("</AbstractText>", start)
                if end == -1:
                    return None
                
                abstract = data[start:end]
                # Extract text between tags
                text_start = abstract.find(">") + 1
                if text_start > 0:
                    abstract = abstract[text_start:]
                return abstract.strip()
        except Exception as e:
            return f"Error fetching abstract: {str(e)}"

    def get_metadata(self, pmid: str) -> dict:
        """Get full metadata for a PMID."""
        params = {
            "db": "pubmed",
            "id": pmid,
            "retmode": "json",
            "email": self.email,
        }
        url = f"{self.SUMMARY_URL}?{urlencode(params)}"
        req = Request(url, headers={"User-Agent": "CoResearcherOS/0.1"})

        with urlopen(req, timeout=30) as resp:
            data = json.loads(resp.read().decode())

        result = data.get("result", {}).get(pmid, {})
        
        # Get abstract separately
        abstract = self.get_abstract(pmid)
        
        return {
            "pmid": pmid,
            "title": result.get("title", ""),
            "abstract": abstract,
            "source": result.get("source", ""),
            "pubdate": result.get("pubdate", ""),
            "authors": [
                a.get("name", "") for a in result.get("authors", [])
                if isinstance(a, dict)
            ],
            "doi": next(
                (a.get("value", "") for a in result.get("articleids", [])
                 if isinstance(a, dict) and a.get("idtype") == "doi"),
                None,
            ),
            "keywords": result.get("keywords", []),
            "mesh_terms": [
                t.get("term", "") for t in result.get("meshterms", [])
                if isinstance(t, dict)
            ],
            "citation_count": None,  # Requires iCite API
        }


def handle_mcp_request(request: dict) -> dict:
    """Handle MCP JSON-RPC requests for PubMed tools."""
    agent = PubMedAgent()
    method = request.get("method", "")
    params = request.get("params", {})

    try:
        if method == "search_pubmed":
            query = params.get("query", "")
            max_results = params.get("max_results", 20)
            result = agent.search(query, max_results)
            return {"jsonrpc": "2.0", "id": request.get("id"), "result": result}
        
        elif method == "get_pubmed_abstract":
            pmid = params.get("pmid", "")
            result = agent.get_abstract(pmid)
            return {
                "jsonrpc": "2.0",
                "id": request.get("id"),
                "result": {"pmid": pmid, "abstract": result},
            }
        
        elif method == "get_pubmed_metadata":
            pmid = params.get("pmid", "")
            result = agent.get_metadata(pmid)
            return {"jsonrpc": "2.0", "id": request.get("id"), "result": result}
        
        else:
            return {
                "jsonrpc": "2.0",
                "id": request.get("id"),
                "error": {"code": -32601, "message": f"Method not found: {method}"},
            }
    except Exception as e:
        return {
            "jsonrpc": "2.0",
            "id": request.get("id"),
            "error": {"code": -32603, "message": str(e)},
        }


if __name__ == "__main__":
    # CLI mode for testing
    if len(sys.argv) > 1:
        cmd = sys.argv[1]
        agent = PubMedAgent()
        if cmd == "search":
            query = sys.argv[2] if len(sys.argv) > 2 else "Alzheimer biomarker"
            result = agent.search(query)
            print(json.dumps(result, indent=2))
        elif cmd == "abstract":
            pmid = sys.argv[2] if len(sys.argv) > 2 else "38273008"
            result = agent.get_abstract(pmid)
            print(result)
        elif cmd == "metadata":
            pmid = sys.argv[2] if len(sys.argv) > 2 else "38273008"
            result = agent.get_metadata(pmid)
            print(json.dumps(result, indent=2))
    else:
        # MCP stdin/stdout mode
        for line in sys.stdin:
            try:
                request = json.loads(line.strip())
                response = handle_mcp_request(request)
                sys.stdout.write(json.dumps(response) + "\n")
                sys.stdout.flush()
            except json.JSONDecodeError:
                error = {
                    "jsonrpc": "2.0",
                    "id": None,
                    "error": {"code": -32700, "message": "Parse error"},
                }
                sys.stdout.write(json.dumps(error) + "\n")
                sys.stdout.flush()