"""
Extended Zenodo Connector - Sprint 28
Maps Zenodo records to ScientificArtifact objects.
"""

from __future__ import annotations

import requests
from typing import List, Dict, Optional

from observer.scientific_artifact import ScientificArtifact, Contributor

ZENODO_API = "https://zenodo.org/api"


def search_by_query(query: str, page: int = 1, size: int = 20) -> List[Dict]:
    url = f"{ZENODO_API}/records"
    params = {"q": query, "page": page, "size": size, "sort": "bestmatch"}
    try:
        r = requests.get(url, params=params, timeout=10)
        r.raise_for_status()
        return r.json().get("hits", {}).get("hits", [])
    except Exception:
        return []


def get_record(record_id: str) -> Optional[Dict]:
    url = f"{ZENODO_API}/records/{record_id}"
    try:
        r = requests.get(url, timeout=10)
        r.raise_for_status()
        return r.json()
    except Exception:
        return None


def map_record_to_artifact(record: Dict) -> ScientificArtifact:
    meta = record.get("metadata", {})
    doi = record.get("doi")
    conceptdoi = record.get("conceptdoi")
    title = meta.get("title", "")
    publication_date = meta.get("publication_date")
    version = meta.get("version")
    creators = [
        Contributor(name=c.get("name"), affiliation=c.get("affiliation"))
        for c in meta.get("creators", [])
    ]
    files = [f.get("key") for f in record.get("files", [])]

    relations = (
        meta.get("relations", {}).get("isVersionOf", [])
        + meta.get("relations", {}).get("isPartOf", [])
    )
    related_identifiers = [
        r.get("identifier") for r in relations if r.get("identifier")
    ]

    artifact_id = f"zenodo:{conceptdoi or doi or record.get('id', '')}"
    artifact = ScientificArtifact(
        artifact_id=artifact_id,
        type="dataset",
        doi=doi,
        title=title,
        contributors=creators,
        created_at=publication_date or "",
        updated_at=record.get("updated", ""),
        evidence_sources=["zenodo"],
        zenodo_record_id=str(record.get("id", "")),
        notes=f"Zenodo record {record.get('id', '')}",
    )
    return artifact