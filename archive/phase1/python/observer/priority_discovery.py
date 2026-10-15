"""
Priority Discovery for Scientific Observation
Integrates OpenAlex, Zenodo, and ecosystem sources to identify high-priority research objects.

Strategy: Observe the most influential science first.
Scarcity is computational attention, not storage.
"""

import requests
from typing import List, Dict, Optional
import re
import sys
from pathlib import Path

# Add parent to path for imports
sys.path.append(str(Path(__file__).parent))

# Import connectors
from zenodo_connector import search_zenodo_by_concept, zenodo_score


# OpenAlex API base
OPENALEX_API = "https://api.openalex.org"

# Priority Score Formula (from OBSERVER_PRIORITY_STRATEGY.md)
# Priority Score = 0.4 × Citations + 0.3 × GitHub stars + 0.2 × Contributors + 0.1 × Recent activity

# Target concepts based on scientific relevance
CONCEPT_QUERIES = [
    "Alzheimer disease",
    "Parkinson disease",
    "Neuroimaging",
    "Bioinformatics",
    "Genetics",
    "Neuroscience",
]

# Ecosystem repositories with known scientific significance
ECOSYSTEM_REPOS = {
    # Neurociencia - strong open science culture
    "BIDS": {"repo": "bids-standard/bids-specification", "domain": "Neuroscience"},
    "OpenNeuro": {"repo": "openneuro/openneuro", "domain": "Neuroscience"},
    "NeuroVault": {"repo": "brainybackup/NeuroVault", "domain": "Neuroscience"},
    "Nilearn": {"repo": "nilearn/nilearn", "domain": "Neuroscience"},
    "MNE-Python": {"repo": "mne-tools/mne-python", "domain": "Neuroscience"},

    # Bioinformática - strong open science culture
    "Bioconductor": {"repo": "Bioconductor/Bioconductor", "domain": "Bioinformatics"},
    "Scanpy": {"repo": "scverse/scanpy", "domain": "Bioinformatics"},
    "AnnData": {"repo": "scverse/anndata", "domain": "Bioinformatics"},
    "Nextflow": {"repo": "nextflow-io/nextflow", "domain": "Bioinformatics"},

    # IA biomédica - strong open science culture
    "MONAI": {"repo": "Project-MONAI/MONAI", "domain": "Medical AI"},
    "DeepChem": {"repo": "deepchem/deepchem", "domain": "Medical AI"},
}


def priority_score(
    citations: int = 0,
    stars: int = 0,
    contributors: int = 0,
    recent_activity: int = 0,
    max_citations: int = 10000,
    max_stars: int = 10000,
    max_contributors: int = 100,
    max_activity: int = 12
) -> float:
    """
    Calculate priority score for observation.

    Priority Score =
    0.4 × Citations (scientific impact) +
    0.3 × GitHub stars (adoption signal) +
    0.2 × Contributors (community) +
    0.1 × Recent activity (momentum)

    All values are normalized to 0-1 range.
    """
    normalized_citations = min(citations / max_citations, 1.0)
    normalized_stars = min(stars / max_stars, 1.0)
    normalized_contributors = min(contributors / max_contributors, 1.0)
    normalized_activity = min(recent_activity / max_activity, 1.0)

    score = (
        0.4 * normalized_citations +
        0.3 * normalized_stars +
        0.2 * normalized_contributors +
        0.1 * normalized_activity
    )

    return round(score, 4)


def query_openalex_works(search_term: str, per_page: int = 20) -> List[Dict]:
    """
    Query OpenAlex for top cited works by search term.

    Returns works sorted by citation count.
    Primary axis: Paper → DOI → Citations.
    """
    url = f"{OPENALEX_API}/works"
    params = {
        "search": search_term,
        "sort": "cited_by_count:desc",
        "per_page": per_page
    }

    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()

        works = []
        for work in data.get("results", []):
            concepts_raw = work.get("concepts", []) or []
            concepts = []
            for c in concepts_raw[:5]:
                if isinstance(c, dict) and "display_name" in c:
                    concepts.append(c["display_name"])

            works.append({
                "doi": work.get("doi"),
                "title": work.get("title"),
                "citations": work.get("cited_by_count", 0),
                "publication_year": work.get("publication_year"),
                "concepts": concepts,
                "github_url": extract_github_url(work),
            })

        return works
    except Exception as e:
        print(f"Error querying OpenAlex: {e}")
        return []


def extract_github_url(work: Dict) -> Optional[str]:
    """Extract GitHub repository URL from work metadata."""
    locations = work.get("locations") or []
    for loc in locations:
        if isinstance(loc, dict):
            url = loc.get("landing_page_url", "")
            if url and "github.com" in url:
                return url

    best_oa = work.get("best_oa_location") or {}
    if best_oa and isinstance(best_oa, dict):
        url = best_oa.get("landing_page_url", "")
        if url and "github.com" in url:
            return url

    return None


def fetch_github_metadata(repo: str) -> Dict:
    """Fetch GitHub metadata for a repository."""
    url = f"https://api.github.com/repos/{repo}"

    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            data = response.json()
            return {
                "stars": data.get("stargazers_count", 0),
                "contributors": len(get_github_contributors(repo)),
                "updated_at": data.get("updated_at"),
                "description": data.get("description"),
            }
    except Exception as e:
        print(f"Error fetching GitHub metadata: {e}")

    return {"stars": 0, "contributors": 0, "updated_at": None, "description": None}


def get_github_contributors(repo: str) -> List[str]:
    """Get list of contributors for a GitHub repository."""
    url = f"https://api.github.com/repos/{repo}/contributors"

    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            return [c["login"] for c in response.json()]
    except:
        pass

    return []


def discover_from_openalex() -> List[Dict]:
    """
    Tier 1: OpenAlex → Code discovery.
    Flow: Paper → GitHub → Zenodo → Dataset
    """
    priority_objects = []

    for query in CONCEPT_QUERIES:
        works = query_openalex_works(query, per_page=20)
        for work in works:
            score = priority_score(
                citations=work["citations"],
                stars=0,  # Will be enriched if GitHub URL found
                contributors=0,
                recent_activity=1
            )

            priority_objects.append({
                "type": "paper",
                "source": "openalex",
                "query": query,
                "doi": work["doi"],
                "title": work["title"],
                "citations": work["citations"],
                "score": score,
                "github_url": work["github_url"],
                "concepts": work["concepts"],
                "year": work["publication_year"],
            })

    return priority_objects


def discover_from_zenodo() -> List[Dict]:
    """
    Tier 2: Zenodo → DOI-first discovery.
    Flow: DOI → Software/Dataset → Repository

    Zenodo records are closer to scientific artifacts than commits:
    - datasets
    - software
    - workflows
    - models
    All with DOIs for traceability.
    """
    priority_objects = []

    queries = ["alzheimer", "parkinson", "neuroimaging", "bioinformatics", "neuroscience"]

    for query in queries:
        records = search_zenodo_by_concept(query, size=15)
        for record in records:
            # Zenodo score provides DOI-based scoring
            base_score = zenodo_score(record)

            priority_objects.append({
                "type": "zenodo_record",
                "source": "zenodo",
                "search_query": query,
                "doi": record.get("doi"),
                "title": record.get("title"),
                "description": record.get("description"),
                "version": record.get("version"),
                "files": record.get("files", []),
                "creators": record.get("creators", []),
                "publication_date": record.get("publication_date"),
                "zenodo_score": base_score,
                # Estimate citations contribution from score
                "score": base_score,
            })

    return priority_objects


def discover_from_ecosystems() -> List[Dict]:
    """
    Tier 3: Ecosystem foci.
    Scientific domains with strong open science culture.
    """
    priority_objects = []

    for name, info in ECOSYSTEM_REPOS.items():
        # Baseline score for known ecosystems
        # These are known high-impact projects
        priority_objects.append({
            "type": "ecosystem",
            "source": "ecosystem",
            "name": name,
            "repo": info["repo"],
            "domain": info["domain"],
            # High baseline - ecosystems are pre-validated for scientific value
            "score": 0.85,
        })

    return priority_objects


def compute_final_score(obj: Dict) -> float:
    """
    Compute final priority score with all available metadata.
    Enriches scores by fetching GitHub metadata where available.
    """
    if obj["type"] == "ecosystem" and "repo" in obj:
        metadata = fetch_github_metadata(obj["repo"])
        return priority_score(
            citations=0,
            stars=metadata["stars"],
            contributors=metadata["contributors"],
            recent_activity=1 if metadata["updated_at"] else 0
        )

    elif obj["type"] == "paper" and obj.get("github_url"):
        match = re.search(r"github\.com/([^/]+/[^/?]+)", obj["github_url"])
        if match:
            repo = match.group(1).rstrip("/")
            metadata = fetch_github_metadata(repo)
            return priority_score(
                citations=obj["citations"],
                stars=metadata["stars"],
                contributors=metadata["contributors"],
                recent_activity=1 if metadata["updated_at"] else 0
            )

    return obj["score"]


def get_top_scientific_objects(
    queries: List[str] = None,
    limit: int = 100,
    include_metadata: bool = False
) -> List[Dict]:
    """
    Get top priority scientific objects across all sources.

    Combines:
    - OpenAlex papers (citations-driven)
    - Zenodo records (DOI-first artifacts)
    - Ecosystem repositories (pre-validated)

    Strategy: Observe the most influential science first.
    Returns only top N objects above threshold.
    """
    all_objects = []

    # Tier 1: OpenAlex papers
    openalex_objects = discover_from_openalex()
    all_objects.extend(openalex_objects)

    # Tier 2: Zenodo records
    zenodo_objects = discover_from_zenodo()
    all_objects.extend(zenodo_objects)

    # Tier 3: Ecosystem repositories
    ecosystem_objects = discover_from_ecosystems()
    all_objects.extend(ecosystem_objects)

    # Enrich scores with GitHub metadata if requested
    if include_metadata:
        for obj in all_objects:
            obj["final_score"] = compute_final_score(obj)
        all_objects.sort(key=lambda x: x.get("final_score", 0), reverse=True)
    else:
        for obj in all_objects:
            obj["final_score"] = obj["score"]

    # Apply priority threshold
    threshold = 0.1
    priority_objects = [o for o in all_objects if o["final_score"] > threshold]

    # Sort by final score
    priority_objects.sort(key=lambda x: x["final_score"], reverse=True)

    # Return top limit
    return priority_objects[:limit]


def generate_priority_ledger(fetch_metadata: bool = False) -> Dict:
    """
    Generate complete priority discovery ledger with unified scoring.
    """
    objects = get_top_scientific_objects(include_metadata=fetch_metadata)

    return {
        "total_objects": len(objects),
        "by_type": {
            "papers": len([o for o in objects if o["type"] == "paper"]),
            "zenodo_records": len([o for o in objects if o["type"] == "zenodo_record"]),
            "ecosystems": len([o for o in objects if o["type"] == "ecosystem"]),
        },
        "top_20": objects[:20],
        "observation_queue": [o for o in objects if o.get("final_score", 0) > 0.1],
        "sources": ["openalex", "zenodo", "ecosystem"],
        "scoring_formula": "0.4 × citations + 0.3 × stars + 0.2 × contributors + 0.1 × activity",
    }


def generate_top_100_priority_list() -> Dict:
    """
    Generate the initial 100-priority object list.
    This is the core function for strategic observation planning.
    """
    # Get objects without metadata fetch first (for speed)
    objects = get_top_scientific_objects(include_metadata=False)

    # Now enrich only top objects (performance optimization)
    top_enrich = [o for o in objects if o["final_score"] > 0.3][:20]
    for obj in top_enrich:
        if obj["type"] == "ecosystem" and "repo" in obj:
            metadata = fetch_github_metadata(obj["repo"])
            obj["stars"] = metadata["stars"]
            obj["contributors"] = metadata["contributors"]
            obj["enriched_score"] = compute_final_score(obj)

    return {
        "strategy": "Observe the most influential science first",
        "total_queued": len(objects),
        "top_enriched": top_enrich,
        "by_source": {
            "openalex": [o for o in objects if o["source"] == "openalex"],
            "zenodo": [o for o in objects if o["source"] == "zenodo"],
            "ecosystem": [o for o in objects if o["source"] == "ecosystem"],
        }
    }


if __name__ == "__main__":
    print("=" * 70)
    print("CORESEARCHER PRIORITY DISCOVERY")
    print("Strategy: Observe the most influential science first")
    print("=" * 70)

    # Generate top 100 priority list
    top_list = generate_top_100_priority_list()

    print(f"\nTotal objects queued: {top_list['total_queued']}")
    print(f"\nBy source:")
    for source, objs in top_list["by_source"].items():
        print(f"  - {source}: {len(objs)}")

    print("\nTop 10 Priority Objects for Observation:")
    print("=" * 70)

    for i, obj in enumerate(top_list["top_enriched"][:10], 1):
        source = obj["source"]
        if obj["type"] == "paper":
            print(f"{i}. [{obj['final_score']:.2f}] {obj['title'][:50]}...")
            print(f"   Source: OpenAlex | Citations: {obj['citations']} | Year: {obj.get('year', 'N/A')}")
        elif obj["type"] == "zenodo_record":
            print(f"{i}. [{obj['final_score']:.2f}] {obj['title'][:50]}...")
            print(f"   Source: Zenodo | DOI: {obj.get('doi', 'N/A')[:30]}")
        else:
            print(f"{i}. [{obj['final_score']:.2f}] {obj['name']} ({obj['domain']})")
            print(f"   Source: Ecosystem | Repo: {obj['repo']}")