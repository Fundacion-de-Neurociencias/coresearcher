"""
OpenAlex Connector - Sprint 28
Minimal connector returning ScientificArtifact objects.
"""

from __future__ import annotations

import requests
from typing import List, Dict, Optional

from observer.scientific_artifact import ScientificArtifact, Contributor

BASE = "https://api.openalex.org/works"


def search(query: str, per_page: int = 20) -> List[Dict]:
    try:
        r = requests.get(BASE, params={"search": query, "per_page": per_page}, timeout=10)
        r.raise_for_status()
        return r.json().get("results", [])
    except Exception:
        return []


def get_by_doi(doi: str) -> Optional[Dict]:
    try:
        r = requests.get(f"{BASE}/doi:{doi}", timeout=10)
        if r.status_code == 200:
            return r.json()
    except Exception:
        pass
    return None


def map_work(work: Dict) -> ScientificArtifact:
    doi = work.get("doi")
    title = work.get("title") or ""
    publication_year = work.get("publication_year")
    cited_by_count = work.get("cited_by_count")
    authors = [
        Contributor(
            name=a.get("author", {}).get("display_name", ""),
            orcid=a.get("author", {}).get("orcid"),
        )
        for a in work.get("authorships", [])[:20]
    ]
    concepts = [c.get("display_name", "") for c in work.get("concepts", [])[:10]]

    return ScientificArtifact(
        artifact_id=f"openalex:{work.get('id', '')}",
        type="paper",
        doi=doi,
        title=title,
        contributors=authors,
        created_at=str(publication_year) if publication_year else "",
        updated_at="",
        evidence_sources=["openalex"],
        openalex_work_id=work.get("id", ""),
        citations=cited_by_count,
        notes=",".join(concepts),
    )


def search_and_map(query: str, per_page: int = 10) -> List[ScientificArtifact]:
    results = search(query, per_page=per_page)
    return [map_work(w) for w in results]