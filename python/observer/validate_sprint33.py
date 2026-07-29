"""
Sprint 33 Validation - Scientific Activity Ledger
Validates ledger generation and comprehension metric on MNE-Python and BIDS.
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
from observer.ledger_generator import build_ledger

TARGETS = [
    "MNE-Python/mne-python",
    "bids-standard/bids-specification",
    "bids-standard/pybids",
]

REPORT_PATH = Path("artifacts/sprint33_scientific_ledger_validation.md")


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


def render_report(entries: list) -> str:
    lines = [
        "# Sprint 33: Scientific Activity Ledger Validation",
        "",
        "Validation date: 2026-07-17",
        "Targets: MNE-Python, BIDS ecosystem",
        "Goal: navigable, verifiable ledger reducing comprehension time",
        "",
        "---",
        "",
        "## Ledger Summaries",
        "",
    ]
    for entry in entries:
        ledger = entry["ledger"]
        lines.append(f"### {ledger.name}")
        lines.append("")
        lines.append(f"- Ledger ID: `{ledger.ledger_id}`")
        lines.append(f"- Description: {ledger.description}")
        lines.append(f"- Timeline: {ledger.timeline}")
        lines.append(f"- Artifacts: {len(ledger.artifacts)}")
        lines.append(f"- Workstreams: {len(ledger.workstreams)}")
        lines.append(f"- Contributors: {len(ledger.contributors)}")
        lines.append("")
        lines.append("**Comprehension Summary:**")
        lines.append("")
        lines.append(ledger.comprehension_summary)
        lines.append("")

    lines.extend([
        "## Validation Checklist",
        "",
        "- [ ] All major artifact types present (software_release, paper, dataset)",
        "- [ ] Workstreams reflect recognizable scientific activity",
        "- [ ] Contributors deduplicated and ordered by frequency",
        "- [ ] Timeline coherent with project history",
        "- [ ] Comprehension summary accurate for expert review",
        "",
        "## Precision / Recall / Compression / Priority Coverage",
        "",
        "- Precision: to be measured after manual expert review",
        "- Recall: to be measured after manual expert review",
        "- Compression: to be estimated from time-to-comprehension",
        "- Priority coverage: pending DOI traceability to priority ledger",
        "",
        "## Next Steps",
        "",
        "1. Manual expert review of MNE-Python and BIDS ledgers.",
        "2. Estimate time-to-comprehension before/after ledger.",
        "3. If valid, integrate ledger generation into Observer pipeline.",
        "",
    ])
    return "\n".join(lines)


def main():
    entries = []
    for repo in TARGETS:
        artifacts = build_artifacts(repo)
        resolved = resolve_artifacts(artifacts)
        merged = resolved["merged_artifacts"]
        ledger = build_ledger(merged, ledger_id=repo, name=repo.split("/")[-1])
        entries.append({
            "repo": repo,
            "ledger": ledger,
        })
    report = render_report(entries)
    REPORT_PATH.write_text(report, encoding="utf-8")
    print(f"Saved: {REPORT_PATH}")


if __name__ == "__main__":
    main()