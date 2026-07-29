"""
Crossref Connector - Sprint 28
Minimal connector returning ScientificArtifact objects.
"""

from __future__ import annotations

import requests
from typing import List, Dict, Optional

from observer.scientific_artifact import ScientificArtifact, Contributor

BASE = "https://api.crossref.org/works"


def search(query: str, per_page: int = 20) -> List[Dict]:
    try:
        r = requests.get(BASE, params={"query": query, "rows": per_page}, timeout=10)
        r.raise_for_status()
        items = r.json().get("message", {}).get("items", [])
        return items
    except Exception:
        return []


def get_by_doi(doi: str) -> Optional[Dict]:
    try:
        r = requests.get(f"{BASE}/{doi}", timeout=10)
        if r.status_code == 200:
            return r.json().get("message")
    except Exception:
        pass
    return None


def map_message(item: Dict) -> ScientificArtifact:
    doi = item.get("DOI")
    title = " ".join(item.get("title", [])) if item.get("title") else ""
    published_online = item.get("published-online", {}).get("date-parts", [[None]])[0]
    published_print = item.get("published-print", {}).get("date-parts", [[None]])[0]
    year = published_online[0] or published_print[0] if (published_online or published_print) else None
    authors = []
    for a in item.get("author", [])[:20]:
        authors.append(Contributor(
            name=" ".join(filter(None, [a.get("given"), a.get("family")])),
            orcid=a.get("ORCID"),
        ))
    count = item.get("is-referenced-by-count")
    rtype = item.get("type", "other")

    return ScientificArtifact(
        artifact_id=f"crossref:{doi}",
        type=rtype,
        doi=doi,
        title=title,
        contributors=authors,
        created_at=str(year) if year else "",
        updated_at="",
        evidence_sources=["crossref"],
        crossref_doi=doi,
        citations=count,
        notes=f"Crossref type: {rtype}",
    )


def search_and_map(query: str, per_page: int = 10) -> List[ScientificArtifact]:
    results = search(query, per_page=per_page)
    return [map_message(item) for item in results]