"""
Cross-Repository Program Resolver - Sprint 30
Groups artifacts from multiple repos/DOIs/orgs into distributed scientific programs.
"""

from __future__ import annotations

from typing import List, Dict, Optional
from collections import defaultdict

from observer.scientific_artifact import ScientificArtifact
from observer.program import Program, Workstream, Contributor
from observer.artifact_resolver import resolve as resolve_artifacts


def _normalized_dois(artifacts: List[ScientificArtifact]) -> set:
    dois = set()
    for a in artifacts:
        if a.doi:
            dois.add(a.doi.strip().lower())
    return dois


def _contributor_keys(artifacts: List[ScientificArtifact]) -> Dict[str, List[ScientificArtifact]]:
    by_name: Dict[str, List[ScientificArtifact]] = defaultdict(list)
    for a in artifacts:
        for c in a.contributors:
            key = (c.name or "").strip().lower()
            if key:
                by_name[key].append(a)
    return dict(by_name)


def _title_similarity(a: ScientificArtifact, b: ScientificArtifact) -> float:
    if not a.title or not b.title:
        return 0.0
    ta = set(a.title.lower().split())
    tb = set(b.title.lower().split())
    if not ta or not tb:
        return 0.0
    intersection = ta & tb
    union = ta | tb
    return len(intersection) / len(union)


def _build_similarity_graph(artifacts: List[ScientificArtifact]) -> Dict[int, List[int]]:
    graph = defaultdict(list)
    dois = {}
    for i, a in enumerate(artifacts):
        dois[i] = _normalized_dois([a])
    for i in range(len(artifacts)):
        for j in range(i + 1, len(artifacts)):
            score = 0.0
            if dois[i] & dois[j]:
                score += 0.8
            ca = _contributor_keys([artifacts[i]])
            cb = _contributor_keys([artifacts[j]])
            shared = set(ca.keys()) & set(cb.keys())
            if shared:
                score += 0.3
            sim = _title_similarity(artifacts[i], artifacts[j])
            if sim > 0.2:
                score += 0.2
            if score >= 0.8:
                graph[i].append(j)
                graph[j].append(i)
    return dict(graph)


def _cluster_graph(n: int, graph: Dict[int, List[int]]) -> List[List[int]]:
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
    return clusters


def resolve_cross_repo_programs(artifacts: List[ScientificArtifact]) -> List[Program]:
    resolved = resolve_artifacts(artifacts)
    merged = resolved["merged_artifacts"]
    graph = _build_similarity_graph(merged)
    clusters = _cluster_graph(len(merged), graph)
    programs = []
    for idx, cluster in enumerate(clusters):
        group = [merged[i] for i in cluster]
        repos = sorted({a.github_repo for a in group if a.github_repo})
        program_id = repos[0] if repos else f"program-{idx}"
        program = _build_program_from_group(program_id, group, repos)
        programs.append(program)
    return programs


def _build_program_from_group(program_id: str, artifacts: List[ScientificArtifact], repos: List[str]) -> Program:
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