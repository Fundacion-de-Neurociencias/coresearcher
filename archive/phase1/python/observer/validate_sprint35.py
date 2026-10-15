"""
Sprint 35 - Comprehension Experiment Protocol
Compares Scientific Activity Ledger vs raw repository for newcomer comprehension.
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import List, Dict

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from observer.github_connector_extended import map_repo_to_artifacts
from observer.zenodo_connector_extended import search_by_query, map_record_to_artifact
from observer.openalex_connector import search_and_map as openalex_search
from observer.crossref_connector import search_and_map as crossref_search
from observer.artifact_resolver import resolve as resolve_artifacts
from observer.ledger_generator import build_ledger

QUESTIONNAIRE = [
    "What is the main purpose of this project?",
    "What problem does it solve?",
    "What artifacts exist? (papers, datasets, software releases)",
    "What workstreams or lines of activity are visible?",
    "Who are the main contributors?",
    "What changed recently (last 3 months)?",
    "What appears unfinished or in progress?",
    "What are the major outputs or results?",
    "What standards or protocols does it adopt?",
    "What should a newcomer read first?",
]

TARGETS = [
    "MNE-Python/mne-python",
    "nilearn/nilearn",
    "bids-standard/pybids",
]

REPORT_PATH = Path("artifacts/sprint35_comprehension_experiment.md")


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


def generate_ledger(repo: str):
    artifacts = build_artifacts(repo)
    resolved = resolve_artifacts(artifacts)
    merged = resolved["merged_artifacts"]
    ledger = build_ledger(merged, ledger_id=repo, name=repo.split("/")[-1])
    return ledger


def render_experiment(entries: list) -> str:
    lines = [
        "# Sprint 35: Comprehension Experiment Protocol",
        "",
        "Date: 2026-07-17",
        "Hypothesis: A Scientific Activity Ledger reduces comprehension cost compared to raw repository access.",
        "Success criterion: >=50% reduction in time with no significant loss of accuracy.",
        "",
        "---",
        "",
        "## Projects",
        "",
    ]
    for e in entries:
        lines.append(f"- {e['project']}: {e['repo']}")

    lines.extend([
        "",
        "## Conditions",
        "",
        "### Condition A: Raw Repository",
        "- Participant accesses only the GitHub repository.",
        "- Answers the 10 comprehension questions.",
        "- Time and accuracy recorded.",
        "",
        "### Condition B: Scientific Activity Ledger",
        "- Participant accesses only the generated Ledger (no repository).",
        "- Answers the same 10 comprehension questions.",
        "- Time and accuracy recorded.",
        "",
        "## Questionnaire",
        "",
    ])
    for q in QUESTIONNAIRE:
        lines.append(f"- {q}")

    lines.extend([
        "",
        "## Metrics",
        "",
        "- Time per question (seconds)",
        "- Total time (seconds)",
        "- Accuracy (0-1 per question)",
        "- Confidence (1-5 Likert per question)",
        "",
        "## Analysis",
        "",
        "- Mean time delta (raw - ledger)",
        "- Mean accuracy delta (ledger - raw)",
        "- Statistical significance (t-test, n>=10 participants per condition)",
        "",
        "## Required Participants",
        "",
        "- At least 10 per condition per project.",
        "- Total minimum: 60 participants across 3 projects and 2 conditions.",
        "",
        "## Output",
        "",
        "- Markdown report with delta table and statistical test results.",
        "",
    ])
    return "\n".join(lines)


def main():
    entries = []
    for repo in TARGETS:
        ledger = generate_ledger(repo)
        entries.append({
            "project": repo.split("/")[-1],
            "repo": repo,
            "artifacts": len(ledger.artifacts),
            "workstreams": len(ledger.workstreams),
            "contributors": len(ledger.contributors),
            "summary": ledger.comprehension_summary,
        })
    report = render_experiment(entries)
    REPORT_PATH.write_text(report, encoding="utf-8")
    print(f"Saved: {REPORT_PATH}")


if __name__ == "__main__":
    main()