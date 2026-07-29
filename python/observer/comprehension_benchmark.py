"""
Comprehension Benchmark - Sprint 34
Measures time-to-understanding for Scientific Activity Ledger vs raw repository.
"""

from __future__ import annotations

import sys
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Optional

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from observer.github_connector_extended import map_repo_to_artifacts
from observer.zenodo_connector_extended import search_by_query, map_record_to_artifact
from observer.openalex_connector import search_and_map as openalex_search
from observer.crossref_connector import search_and_map as crossref_search
from observer.artifact_resolver import resolve as resolve_artifacts
from observer.ledger_generator import build_ledger

QUESTIONNAIRE = [
    "What is the main purpose of this project?",
    "What are the primary artifacts? (papers, datasets, software releases)",
    "Who are the main contributors?",
    "What workstreams or lines of activity are visible?",
    "When did the project start? What is the latest activity?",
    "What happened in the last 3 months?",
    "What appears to be unfinished or in progress?",
    "How is the project organized? (if inferable)",
    "What standards or protocols does it adopt?",
    "What would you read first to understand the project?",
]

TARGETS = [
    "MNE-Python/mne-python",
    "bids-standard/bids-specification",
    "bids-standard/pybids",
]

REPORT_PATH = Path("artifacts/sprint34_comprehension_benchmark.md")


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
        "# Sprint 34: Comprehension Benchmark",
        "",
        "Validation date: 2026-07-17",
        "Metric: time_to_understand(project)",
        "Protocol: compare raw repository vs Scientific Activity Ledger",
        "",
        "---",
        "",
        "## Projects Evaluated",
        "",
    ]
    for entry in entries:
        lines.append(f"### {entry['project']}")
        lines.append("")
        lines.append(f"- Repository: {entry['repo']}")
        lines.append(f"- Ledger artifacts: {entry['artifact_count']}")
        lines.append(f"- Ledger workstreams: {entry['workstream_count']}")
        lines.append(f"- Ledger contributors: {entry['contributor_count']}")
        lines.append(f"- Estimated comprehension time with ledger: {entry['estimated_minutes']} minutes")
        lines.append("")
        lines.append("**Questionnaire:**")
        lines.append("")
        for q in QUESTIONNAIRE:
            lines.append(f"- {q}")
        lines.append("")
        lines.append("**Ledger Summary:**")
        lines.append("")
        lines.append(entry['ledger_summary'])
        lines.append("")

    lines.extend([
        "## Benchmark Protocol",
        "",
        "### Condition A: Raw Repository",
        "- Participant accesses the GitHub repository directly.",
        "- Time to answer each questionnaire question is recorded.",
        "- Completeness of answers is scored.",
        "",
        "### Condition B: Scientific Activity Ledger",
        "- Participant accesses only the generated Ledger.",
        "- Time to answer each questionnaire question is recorded.",
        "- Completeness of answers is scored.",
        "",
        "## Expected Outcome",
        "",
        "- Ledger condition: shorter time, equal or higher completeness.",
        "- Raw repo condition: longer time, variable completeness.",
        "",
        "## Next Steps",
        "",
        "1. Recruit participants for pilot study.",
        "2. Run Condition A and Condition B for each project.",
        "3. Analyze time-to-comprehension delta.",
        "4. Report statistical significance.",
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
            "project": repo.split("/")[-1],
            "repo": repo,
            "artifact_count": len(ledger.artifacts),
            "workstream_count": len(ledger.workstreams),
            "contributor_count": len(ledger.contributors),
            "estimated_minutes": max(5, min(20, len(ledger.artifacts) // 3)),
            "ledger_summary": ledger.comprehension_summary,
        })
    report = render_report(entries)
    REPORT_PATH.write_text(report, encoding="utf-8")
    print(f"Saved: {REPORT_PATH}")


if __name__ == "__main__":
    main()