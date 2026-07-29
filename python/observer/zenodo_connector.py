"""
Zenodo Connector for Scientific Artifacts
Discovers DOI-linked scientific software and datasets.
"""

import requests
from typing import List, Dict, Optional


ZENODO_API = "https://zenodo.org/api"


def search_zenodo_by_concept(concept: str, page: int = 1, size: int = 20) -> List[Dict]:
    """
    Search Zenodo for scientific artifacts in a domain.
    """
    url = f"{ZENODO_API}/records"
    params = {
        "q": concept,
        "page": page,
        "size": size,
        "sort": "bestmatch",  # Could use "mostrecent" or sort by citations
    }
    
    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        records = []
        for record in data.get("hits", {}).get("hits", []):
            records.append({
                "doi": record.get("doi"),
                "conceptdoi": record.get("conceptdoi"),
                "title": record.get("metadata", {}).get("title"),
                "description": record.get("metadata", {}).get("description"),
                "creators": [c.get("name") for c in record.get("metadata", {}).get("creators", [])],
                "publication_date": record.get("metadata", {}).get("publication_date"),
                "version": record.get("metadata", {}).get("version"),
                "files": [f.get("key") for f in record.get("files", [])],
                "links": {
                    "html": record.get("links", {}).get("html"),
                    "self": record.get("links", {}).get("self"),
                }
            })
        
        return records
    except Exception as e:
        print(f"Error querying Zenodo: {e}")
        return []


def get_zenodo_record(record_id: str) -> Optional[Dict]:
    """
    Get detailed information about a Zenodo record.
    """
    url = f"{ZENODO_API}/records/{record_id}"
    
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"Error fetching Zenodo record: {e}")
        return None


def get_related_records(record_id: str) -> List[Dict]:
    """
    Get records that cite or are cited by this record.
    """
    url = f"{ZENODO_API}/records/{record_id}"
    
    try:
        # Get the record first to find related
        record = get_zenodo_record(record_id)
        if not record:
            return []
        
        related = record.get("metadata", {}).get("relations", {}).get("is identical to", [])
        return [{"record_id": r.split("/")[-1] for r in related}]
    except Exception as e:
        print(f"Error fetching related records: {e}")
        return []


def zenodo_score(record: Dict) -> float:
    """
    Score a Zenodo record for priority.
    DOI + version + files are strong signals.
    """
    score = 0.0
    
    # Has DOI (primary scientific artifact)
    if record.get("doi"):
        score += 0.4
    
    # Has version (indicates software/dataset maturity)
    if record.get("version"):
        score += 0.2
    
    # Has files (actual artifact present)
    if record.get("files"):
        score += 0.2
    
    # Recent publication (<= 5 years)
    pub_date = record.get("publication_date", "")
    if pub_date:
        year = int(pub_date[:4]) if pub_date else 0
        if year >= 2020:
            score += 0.2
    
    return round(score, 2)


def discover_neuroscience_artifacts() -> List[Dict]:
    """
    Discover Zenodo artifacts in neuroscience domains.
    """
    queries = ["neuroscience", "alzheimer", "parkinson", "neuroimaging", "brain"]
    all_records = []
    
    for query in queries:
        records = search_zenodo_by_concept(query, size=10)
        for record in records:
            record["search_query"] = query
            record["zenodo_score"] = zenodo_score(record)
            all_records.append(record)
    
    # Sort by zenodo score
    all_records.sort(key=lambda x: x["zenodo_score"], reverse=True)
    
    return all_records


if __name__ == "__main__":
    print("=" * 70)
    print("ZENODO SCIENTIFIC ARTIFACT DISCOVERY")
    print("=" * 70)
    
    records = discover_neuroscience_artifacts()
    
    print(f"\nFound {len(records)} scientific artifacts")
    print("\nTop 10 by Zenodo score:")
    
    for record in records[:10]:
        print(f"  [{record['zenodo_score']:.2f}] {record['title'][:50]}...")
        print(f"         DOI: {record['doi']}")
        print(f"         Files: {len(record['files'])}")