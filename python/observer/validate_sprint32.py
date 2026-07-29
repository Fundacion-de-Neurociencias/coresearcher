"""
Sprint 32 Validation - Initiative and Workstream Resolution
Validates refined terminology and grouping on BIDS ecosystem and MNE-Python.
"""

from __future__ import annotations

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from observer.github_connector_extended import map_repo_to_artifacts
from observer.zenodo_connector_extended import search_by_query, map_record_to_artifact
from observer.openalex_connector import search_and_map as openalex_search
from observer.crossref_connector import search_and_map as crossref_search
from observer.artifact_resolver import resolve as resolve_artifacts
from observer.workstream_resolver import infer_workstreams
from observer.initiative_resolver import infer_initiatives

TARGETS = [
    "MNE-Python/mne-python",
    "bids-standard/bids-specification",
    "bids-standard/pybids",
    "bids-standard/bids-examples",
]

REPORT_PATH = Path("artifacts/sprint32_initiative_workstream_validation.md")


def build_artifacts(repo: str) -> list:
    artifacts = []
    artifacts.extend(map_repo_to_artifacts(repo))
    query = repo.split("/")[-1].replace("-", " ")
    for rec in search_by_query(query, size=10):
        artifacts.append(map_record_to_artifact(rec))
    for a in openalex_search(query, per_page=10):
        a.github_repo = repo
        artifacts.append(a)
    for a in crossref_search(query, per_page=10):
        a.github_repo = repo
        artifacts.append(a)
    return artifacts


def render_report(entries: list, input_count: int) -> str:
    lines = [
        "# Sprint 32: Initiative and Workstream Resolution Validation",
        "",
        "Validation date: 2026-07-17",
        "Targets: MNE-Python, BIDS ecosystem",
        "Terminology: Initiative/Workstream replacing Program",
        "",
        "---",
        "",
        "## Input",
        "",
        f"- Total artifacts: {input_count}",
        f"- Repositories evaluated: {len(TARGETS)}",
        "",
        "## Results by Repository",
        "",
    ]
    for entry in entries:
        lines.append(f"### {entry['repo']}")
        lines.append("")
        lines.append(f"- Workstreams: {len(entry['workstreams'])}")
        lines.append(f"- Initiatives: {len(entry['initiatives'])}")
        lines.append("")
        for ws in entry["workstreams"][:10]:
            lines.append(f"- Workstream `{ws.get('name','')}` | artifacts={len(ws.get('related_artifact_ids', []))} | repos={len(ws.get('repositories', []))}")
        for ini in entry["initiatives"][:5]:
            lines.append(f"- Initiative `{ini.get('name','')}` | workstreams={len(ini.get('workstreams', []))} | repos={len(ini.get('repositories', []))}")
        lines.append("")

    lines.extend([
        "## Evaluation",
        "",
        "- Does Initiative/Workstream terminology eliminate ambiguity? - pending review",
        "- Are MNE workstreams coherent? - pending review",
        "- Are BIDS initiatives coherent? - pending review",
        "",
        "## Precision / Recall / Compression / Priority Coverage",
        "",
        "- Precision: not measured",
        "- Recall: not measured",
        "- Compression: to be measured",
        "- Priority coverage: pending DOI traceability to priority ledger",
        "",
        "## Next Steps",
        "",
        "1. Manual expert review of inferred workstreams and initiatives.",
        "2. If terminology is validated, replace remaining Program objects across codebase.",
        "3. Integrate Initiative/Workstream into Scientific Activity Ledger.",
        "",
    ])
    return "\n".join(lines)


def main():
    entries = []
    total_input = 0
    for repo in TARGETS:
        artifacts = build_artifacts(repo)
        resolved = resolve_artifacts(artifacts)
        merged = resolved["merged_artifacts"]
        total_input += resolved["total_input"]
        workstreams = infer_workstreams(merged)
        initiatives = infer_initiatives(workstreams, merged)
        entries.append({
            "repo": repo,
            "workstreams": [ws.to_dict() for ws in workstreams],
            "initiatives": [ini.to_dict() for ini in initiatives],
        })
    report = render_report(entries, total_input)
    REPORT_PATH.write_text(report, encoding="utf-8")
    print(f"Saved: {REPORT_PATH}")


if __name__ == "__main__":
    main()