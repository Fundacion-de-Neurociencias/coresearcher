"""
Ledger Generator - Sprint 33
Generates Scientific Activity Ledger from artifacts and workstreams.
"""

from __future__ import annotations

from datetime import datetime
from typing import List, Dict, Optional

from observer.scientific_artifact import ScientificArtifact
from observer.scientific_ledger import ScientificLedger, LedgerWorkstream, LedgerContributor
from observer.workstream_resolver import infer_workstreams
from observer.intellectual_extractor import run_cheap_gate, GateVerdict, build_extraction_prompt


def build_ledger(artifacts: List[ScientificArtifact], ledger_id: str, name: str = "", description: str = "") -> ScientificLedger:
    if not name:
        name = ledger_id
    if not description and artifacts:
        description = artifacts[0].title or name

    # Intellectual History Extraction Pipeline (Cheap Gate + LLM Prompt)
    for a in artifacts:
        gate = run_cheap_gate(
            title=a.title or "",
            body=a.body or "",
            metadata={"comments": 0} # Simplified for now
        )
        if gate.verdict in (GateVerdict.LIKELY, GateVerdict.AMBIGUOUS):
            a.metadata["intellectual_history_gate"] = gate.verdict.value
            a.metadata["intellectual_history_prompt"] = build_extraction_prompt(
                title=a.title or "",
                body=a.body or "",
                metadata={}
            )
            # Future: LLM Call goes here to populate a.metadata["intellectual_entities"]

    workstreams = infer_workstreams(artifacts)
    ledger_workstreams = []
    for ws in workstreams:
        ledger_workstreams.append(LedgerWorkstream(
            workstream_id=ws.workstream_id,
            name=ws.name,
            signals=ws.signals[:10],
            related_artifact_count=len(ws.related_artifact_ids),
            contributor_count=len(ws.contributors),
        ))

    contributors_map = {}
    for a in artifacts:
        for c in a.contributors:
            key = (c.name or "").strip().lower()
            if not key:
                continue
            if key not in contributors_map:
                contributors_map[key] = {
                    "name": c.name.strip(),
                    "github": c.github,
                    "orcid": c.orcid,
                    "affiliation": c.affiliation,
                    "count": 0,
                }
            contributors_map[key]["count"] += 1

    contributors = []
    for key, data in sorted(contributors_map.items(), key=lambda x: x[1]["count"], reverse=True)[:100]:
        contributors.append(LedgerContributor(
            name=data["name"],
            github=data["github"],
            orcid=data["orcid"],
            affiliation=data["affiliation"],
            contribution_count=data["count"],
        ))

    start_year = None
    latest_activity = ""
    milestones = []
    for a in artifacts:
        if a.created_at:
            try:
                year = int(str(a.created_at)[:4])
                if start_year is None or year < start_year:
                    start_year = year
                if not latest_activity or str(a.created_at) > latest_activity:
                    latest_activity = str(a.created_at)
            except Exception:
                pass
        if a.github_release and a.github_release not in milestones:
            milestones.append(a.github_release)

    timeline = {
        "start_year": start_year or 0,
        "latest_activity": latest_activity,
        "milestones": milestones[:20],
    }

    summary = (
        f"{name} is a scientific project with "
        f"{len(artifacts)} artifacts, "
        f"{len(ledger_workstreams)} workstreams, and "
        f"{len(contributors)} contributors. "
        f"Active since {start_year or 'unknown'}."
    )

    return ScientificLedger(
        ledger_id=ledger_id,
        name=name,
        description=description,
        timeline=timeline,
        artifacts=[a.to_dict() for a in artifacts],
        workstreams=ledger_workstreams,
        contributors=contributors,
        comprehension_summary=summary,
    )