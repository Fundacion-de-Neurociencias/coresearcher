"""
Network Resolver - Sprint 31
Clusters artifacts into programs using network neighborhoods.
"""

from __future__ import annotations

from typing import List, Dict, Set
from collections import defaultdict

from observer.scientific_artifact import ScientificArtifact
from observer.scientific_network import ScientificNetwork, NetworkNode, NetworkEdge
from observer.network_extractor import artifact_neighborhoods
from observer.program import Program, Workstream, Contributor


def _jaccard(a: Set[str], b: Set[str]) -> float:
    if not a and not b:
        return 0.0
    intersection = a & b
    union = a | b
    return len(intersection) / len(union)


def resolve_programs_from_network(artifacts: List[ScientificArtifact]) -> List[Program]:
    neighborhoods = artifact_neighborhoods(artifacts)
    n = len(artifacts)
    ids = [a.artifact_id for a in artifacts]

    graph = defaultdict(list)
    for i in range(n):
        for j in range(i + 1, n):
            sim = _jaccard(neighborhoods[ids[i]], neighborhoods[ids[j]])
            if sim > 0.0:
                graph[i].append(j)
                graph[j].append(i)

    visited = set()
    clusters = []
    for i in range(n):
        if i in visited:
            continue
        stack = [i]
        cluster = []
        while stack:
            node = stack.pop()
            if node in visited:
                continue
            visited.add(node)
            cluster.append(node)
            for neighbor in graph.get(node, []):
                if neighbor not in visited:
                    stack.append(neighbor)
        if cluster:
            clusters.append(cluster)

    programs = []
    for idx, cluster in enumerate(clusters):
        group = [artifacts[i] for i in cluster]
        repos = sorted({a.github_repo for a in group if a.github_repo})
        program_id = repos[0] if repos else f"program-{idx}"
        programs.append(_build_program(program_id, group, repos))

    return programs


def _build_program(program_id: str, artifacts: List[ScientificArtifact], repos: List[str]) -> Program:
    name = program_id.split("/")[-1] if "/" in program_id else program_id
    description = ""
    latest_activity = ""
    start_year = None
    contributors = []
    workstream_signals = defaultdict(int)
    software_releases = []
    papers = []
    datasets = []
    key_milestones = []
    seen_contributors = set()

    for a in artifacts:
        if not description and a.title:
            description = a.title
        if a.github_release and a.github_release not in key_milestones:
            key_milestones.append(a.github_release)
        if a.created_at:
            try:
                year = int(str(a.created_at)[:4])
                if start_year is None or year < start_year:
                    start_year = year
                if not latest_activity or str(a.created_at) > latest_activity:
                    latest_activity = str(a.created_at)
            except Exception:
                pass
        if a.type == "software_release":
            software_releases.append(a.to_dict())
        elif a.type == "paper":
            papers.append(a.to_dict())
            for s in _extract_signals(a.title + " " + (a.notes or "")):
                workstream_signals[s] += 1
        elif a.type == "dataset":
            datasets.append(a.to_dict())
        for c in a.contributors:
            key = (c.name or "").strip().lower()
            if key and key not in seen_contributors:
                seen_contributors.add(key)
                contributors.append(c)

    workstreams = []
    for signal, count in sorted(workstream_signals.items(), key=lambda x: x[1], reverse=True)[:10]:
        workstreams.append(Workstream(name=signal, signals=[signal], related_artifact_ids=[]))

    timeline = {
        "start_year": start_year or 0,
        "latest_activity": latest_activity,
        "key_milestones": key_milestones[:10],
    }

    summary = (
        f"{name} is a distributed scientific program spanning {len(repos)} repositories. "
        f"It includes {len(software_releases)} software releases, {len(papers)} papers, "
        f"and {len(datasets)} datasets. "
        f"Primary workstreams: {', '.join(w.name for w in workstreams[:5])}. "
        f"Active since {start_year or 'unknown'}."
    )

    return Program(
        program_id=program_id,
        name=name,
        description=description,
        timeline=timeline,
        artifacts={
            "software_releases": software_releases,
            "papers": papers,
            "datasets": datasets,
        },
        contributors=contributors,
        workstreams=workstreams,
        comprehension_summary=summary,
    )


def _extract_signals(text: str) -> List[str]:
    signals = []
    keywords = [
        "meg", "eeg", "meg/", "eeg/", "source localization", "forward", "inverse",
        "ica", "time-frequency", "tfr", "evoked", "epochs", "raw",
        "decoding", "connectivity", "graph", "statistical", "plotting",
        "preprocessing", "artifact", "reject", "filter", "resample",
        "bids", "layout", "dataset", "fetch", "read",
        "annotation", "label", "auditory", "visual", "motor",
        "stimulation", "neuroimaging", "fmri", "mri",
    ]
    lower = text.lower()
    for kw in keywords:
        if kw in lower:
            signals.append(kw)
    return signals