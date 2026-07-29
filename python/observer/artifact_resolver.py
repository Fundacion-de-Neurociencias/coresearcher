"""
Artifact Resolver - Sprint 28
Merges and links ScientificArtifact objects across evidence sources.
"""

from __future__ import annotations

from typing import List, Dict, Optional
from collections import defaultdict

from observer.scientific_artifact import ScientificArtifact, Contributor


def normalize_doi(doi: Optional[str]) -> Optional[str]:
    if not doi:
        return None
    d = doi.strip().lower()
    if d.startswith("https://doi.org/"):
        d = d[len("https://doi.org/"):]
    if d.startswith("http://doi.org/"):
        d = d[len("http://doi.org/"):]
    return d or None


def merge_artifacts(artifacts: List[ScientificArtifact]) -> List[ScientificArtifact]:
    """Merge artifacts sharing the same DOI into a canonical record."""
    by_doi: Dict[Optional[str], List[ScientificArtifact]] = defaultdict(list)
    no_doi: List[ScientificArtifact] = []

    for a in artifacts:
        doi = normalize_doi(a.doi)
        if doi:
            by_doi[doi].append(a)
        else:
            no_doi.append(a)

    merged: List[ScientificArtifact] = []
    for doi, group in by_doi.items():
        best = group[0]
        for a in group[1:]:
            if len(a.evidence_sources) > len(best.evidence_sources):
                best = a
            if not best.title and a.title:
                best = a
        best.doi = doi
        best.contributors = _dedupe_contributors([c for a in group for c in a.contributors])
        sources = []
        for a in group:
            for s in a.evidence_sources:
                if s not in sources:
                    sources.append(s)
        best.evidence_sources = sources
        merged.append(best)

    merged.extend(no_doi)
    return merged


def _dedupe_contributors(contributors: List[Contributor]) -> List[Contributor]:
    seen = set()
    out = []
    for c in contributors:
        key = (c.name or "").strip().lower()
        if key in seen:
            continue
        seen.add(key)
        out.append(c)
    return out


def link_related(merged: List[ScientificArtifact]) -> Dict[str, List[str]]:
    """Return adjacency of artifact_id -> related artifact_ids via shared GitHub repo."""
    related = {}
    by_repo = defaultdict(list)
    for a in merged:
        if a.github_repo:
            by_repo[a.github_repo].append(a.artifact_id)
    for ids in by_repo.values():
        for aid in ids:
            related[aid] = [x for x in ids if x != aid]
    return related


def resolve(artifacts: List[ScientificArtifact]) -> Dict:
    merged = merge_artifacts(artifacts)
    related = link_related(merged)
    return {
        "merged_artifacts": merged,
        "related": related,
        "total_merged": len(merged),
        "total_input": len(artifacts),
    }