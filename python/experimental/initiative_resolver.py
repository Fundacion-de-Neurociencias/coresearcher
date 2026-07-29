"""
Initiative Resolver - Sprint 32
Infers initiatives from workstreams and shared network signals.
"""

from __future__ import annotations

from typing import List, Dict, Set
from collections import defaultdict

from observer.workstream import Workstream, Initiative
from observer.scientific_artifact import ScientificArtifact


def infer_initiatives(workstreams: List[Workstream], artifacts: List[ScientificArtifact]) -> List[Initiative]:
    # Group workstreams by shared repositories
    repo_to_workstreams: Dict[str, List[Workstream]] = defaultdict(list)
    for ws in workstreams:
        for repo in ws.repositories:
            repo_to_workstreams[repo].append(ws)

    # Also group by shared contributors across workstreams
    contributor_to_workstreams: Dict[str, List[Workstream]] = defaultdict(list)
    for ws in workstreams:
        for contrib in ws.contributors:
            contributor_to_workstreams[contrib].append(ws)

    # Build initiatives from dominant repo/workstream clusters
    initiatives = []
    seen_repos = set()
    for repo, ws_list in sorted(repo_to_workstreams.items(), key=lambda x: len(x[1]), reverse=True):
        if not repo or repo in seen_repos:
            continue
        seen_repos.add(repo)
        name = repo.split("/")[-1] if "/" in repo else repo
        initiative = Initiative(
            initiative_id=repo,
            name=name,
            description=f"Initiative inferred from repository {repo}",
            workstreams=ws_list[:10],
            contributors=sorted({c for ws in ws_list for c in ws.contributors})[:50],
            repositories=[repo],
        )
        initiatives.append(initiative)

    # For workstreams without a clear repo, cluster by shared contributors
    orphan_ws = [ws for ws in workstreams if not ws.repositories]
    if orphan_ws:
        contrib_to_orphan: Dict[str, List[Workstream]] = defaultdict(list)
        for ws in orphan_ws:
            for c in ws.contributors:
                contrib_to_orphan[c].append(ws)
        seen_contribs = set()
        for contrib, ws_list in sorted(contrib_to_orphan.items(), key=lambda x: len(x[1]), reverse=True):
            if not contrib or contrib in seen_contribs:
                continue
            seen_contribs.add(contrib)
            initiative = Initiative(
                initiative_id=f"initiative:{contrib}",
                name=f"Initiative by {contrib}",
                description="Initiative inferred from shared contributors",
                workstreams=ws_list[:10],
                contributors=sorted({c for ws in ws_list for c in ws.contributors})[:50],
                repositories=[],
            )
            initiatives.append(initiative)

    return initiatives