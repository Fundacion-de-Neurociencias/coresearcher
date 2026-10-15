"""
Sprint 31 Validation - Scientific Network Resolution
Validates network-based program discovery on BIDS ecosystem.
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
from observer.network_resolver import resolve_programs_from_network
from observer.network_extractor import extract_network

TARGETS = [
    "bids-standard/bids-specification",
    "bids-standard/pybids",
    "bids-standard/bids-examples",
]

REPORT_PATH = Path("artifacts/sprint31_network_resolution_validation.md")


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


def render_report(programs: list, input_count: int, network: dict) -> str:
    lines = [
        "# Sprint 31: Scientific Network Resolution Validation",
        "",
        "Validation date: 2026-07-17",
        "Target: BIDS ecosystem",
        "Method: network-neighborhood clustering instead of artifact similarity",
        "",
        "---",
        "",
        "## Input",
        "",
        f"- Total artifacts: {input_count}",
        f"- Programs resolved: {len(programs)}",
        f"- Network nodes: {len(network.get('nodes', []))}",
        f"- Network edges: {len(network.get('edges', []))}",
        "",
        "## Inferred Programs",
        "",
    ]
    for p in programs:
        lines.append(f"### {p.name}")
        lines.append("")
        lines.append(f"- Program ID: `{p.program_id}`")
        lines.append(f"- Description: {p.description}")
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
        "- Did the resolver group BIDS repos together? - pending manual review",
        "- Did network neighborhoods produce coherent programs? - pending manual review",
        "- Is this better than artifact-similarity grouping? - to be compared with Sprint 30",
        "",
        "## Precision / Recall / Compression / Priority Coverage",
        "",
        "- Precision: not measured (manual verificaiton pending)",
        "- Recall: not measured (manual verificaiton pending)",
        "- Compression: to be measured",
        "- Priority coverage: pending DOI traceability to priority ledger",
        "",
        "## Next Steps",
        "",
        "1. Manual expert review of inferred BIDS program.",
        "2. Compare network-resolution results with artifact-similarity results.",
        "3. If valid, extend to OpenNeuro and AllenSDK.",
        "",
    ])
    return "\n".join(lines)


def main():
    artifacts = []
    for repo in TARGETS:
        artifacts.extend(build_artifacts(repo))
    resolved = resolve_artifacts(artifacts)
    merged = resolved["merged_artifacts"]
    programs = resolve_programs_from_network(merged)
    network = extract_network(merged, "bids-validation").to_dict()
    report = render_report(programs, resolved["total_input"], network)
    REPORT_PATH.write_text(report, encoding="utf-8")
    print(f"Saved: {REPORT_PATH}")
    for p in programs:
        print(f"Program: {p.name} | contributors={len(p.contributors)} | workstreams={len(p.workstreams)}")


if __name__ == "__main__":
    main()