"""
Workstream Resolver - Sprint 32
Infers workstreams from artifact clusters with shared signals.
"""

from __future__ import annotations

from typing import List, Dict, Set
from collections import defaultdict

from observer.scientific_artifact import ScientificArtifact
from observer.workstream import Workstream


def _extract_signals(text: str) -> Set[str]:
    signals = set()
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
            signals.add(kw)
    return signals


def infer_workstreams(artifacts: List[ScientificArtifact]) -> List[Workstream]:
    signal_to_artifacts: Dict[str, List[ScientificArtifact]] = defaultdict(list)
    for a in artifacts:
        text = a.title + " " + (a.notes or "")
        for signal in _extract_signals(text):
            signal_to_artifacts[signal].append(a)

    workstreams = []
    for signal, related in sorted(signal_to_artifacts.items(), key=lambda x: len(x[1]), reverse=True)[:15]:
        workstreams.append(Workstream(
            workstream_id=f"workstream:{signal}",
            name=signal,
            description=f"Workstream inferred from {len(related)} artifacts",
            signals=[signal],
            related_artifact_ids=[a.artifact_id for a in related[:20]],
            contributors=sorted({c.name for a in related for c in a.contributors if c.name})[:20],
            repositories=sorted({a.github_repo for a in related if a.github_repo}),
        ))
    return workstreams