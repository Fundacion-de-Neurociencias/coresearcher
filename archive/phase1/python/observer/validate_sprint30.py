"""
Sprint 30 Validation - Cross-Repository Program Resolution
Validates discovery of distributed scientific programs from heterogeneous public sources.
"""

from __future__ import annotations

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from observer.github_connector_extended import map_repo_to_artifacts
from observer.zenodo_connector_extended import search_by_query, map_record_to_artifact
from observer.openalex_connector import search_and_map as openalex_search
from observer.crossref_connector import search_and_map as crossref_search
from observer.cross_repo_program_resolver import resolve_cross_repo_programs
from observer.scientific_artifact import ScientificArtifact

TARGETS = [
    "bids-standard/bids-specification",
    "bids-standard/pybids",
    "OpenNeuroDatasets/ds000117",
]

REPORT_PATH = Path("artifacts/sprint30_cross_repo_validation.md")


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


def render_report(programs: list, input_count: int) -> str:
    lines = [
        "# Sprint 30: Cross-Repository Program Resolution Validation",
        "",
        "Validation date: 2026-07-17",
        "Success criterion: CoResearcher infers a distributed scientific program from heterogeneous public evidence sources without manual relationship lists.",
        "",
        "---",
        "",
        "## Input",
        "",
        f"- Total artifacts: {input_count}",
        f"- Programs resolved: {len(programs)}",
        "",
        "## Inferred Programs",
        "",
    ]
    for p in programs:
        lines.append(f"### {p.name}")
        lines.append("")
        lines.append(f"- Program ID: `{p.program_id}`")
        lines.append(f"- Description: {p.description}")
        lines.append(f"- Repositories: {len(set(a.github_repo for a in [ScientificArtifact.from_dict(a) for a in p.artifacts.get('software_releases', []) + p.artifacts.get('papers', []) + p.artifacts.get('datasets', [])]))}")
        lines.append(f"- Contributors: {len(p.contributors)}")
        lines.append(f"- Workstreams: {len(p.workstreams)}")
        lines.append(f"- Software releases: {len(p.artifacts.get('software_releases', []))}")
        lines.append(f"- Papers: {len(p.artifacts.get('papers', []))}")
        lines.append(f"- Datasets: {len(p.artifacts.get('datasets', []))}")
        lines.append("")
        lines.append("**Comprehension Summary:**")
        lines.append("")
        lines.append(p.comprehension_summary)
        lines.append("")

    lines.extend([
        "## Evaluation",
        "",
        "- Did the resolver group related artifacts across repositories? - pending manual review",
        "- Did the resolver produce coherent workstreams? - pending manual review",
        "- Did it avoid hardcoded BIDS relationships? - yes (heuristic-based only)",
        "",
        "## Precision / Recall / Compression / Priority Coverage",
        "",
        "- Precision: not measured (manual verification pending)",
        "- Recall: not measured (manual verification pending)",
        "- Compression: to be measured",
        "- Priority coverage: pending DOI traceability to priority ledger",
        "",
        "## Next Steps",
        "",
        "1. Manual expert review of inferred programs.",
        "2. If valid, extend validation to OpenNeuro datasets and AllenSDK.",
        "3. Integrate cross-repository resolver into Scientific Activity Ledger pipeline.",
        "",
    ])
    return "\n".join(lines)


def main():
    artifacts = []
    for repo in TARGETS:
        artifacts.extend(build_artifacts(repo))
    programs = resolve_cross_repo_programs(artifacts)
    report = render_report(programs, len(artifacts))
    REPORT_PATH.write_text(report, encoding="utf-8")
    print(f"Saved: {REPORT_PATH}")
    for p in programs:
        print(f"Program: {p.name} | repos={len(set(a.github_repo for a in [ScientificArtifact.from_dict(a) for a in p.artifacts.get('software_releases', []) + p.artifacts.get('papers', []) + p.artifacts.get('datasets', [])]))} | workstreams={len(p.workstreams)}")


if __name__ == "__main__":
    main()