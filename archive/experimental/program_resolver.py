"""
Program Resolver - Sprint 29
Groups ScientificArtifacts into coherent scientific programs.
"""

from __future__ import annotations

from typing import List, Dict, Optional
from collections import defaultdict

from observer.scientific_artifact import ScientificArtifact
from observer.program import Program, Workstream, Contributor


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


def group_artifacts(artifacts: List[ScientificArtifact]) -> Dict[str, List[ScientificArtifact]]:
    by_repo: Dict[str, List[ScientificArtifact]] = defaultdict(list)
    ungrouped: List[ScientificArtifact] = []
    for a in artifacts:
        repo = a.github_repo
        if repo:
            by_repo[repo].append(a)
        else:
            ungrouped.append(a)
    if ungrouped:
        by_repo["ungrouped"] = ungrouped
    return dict(by_repo)


def build_program(program_id: str, artifacts: List[ScientificArtifact]) -> Program:
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
            signals = _extract_signals(a.title + " " + (a.notes or ""))
            for s in signals:
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
        f"{name} is a scientific software project with "
        f"{len(software_releases)} software releases, "
        f"{len(papers)} papers, and "
        f"{len(datasets)} datasets. "
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


def resolve_programs(artifacts: List[ScientificArtifact]) -> List[Program]:
    grouped = group_artifacts(artifacts)
    programs = []
    for program_id, group in grouped.items():
        programs.append(build_program(program_id, group))
    return programs