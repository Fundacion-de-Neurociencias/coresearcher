"""
Sprint 36 - Agent Onboarding Benchmark
Compares agent productivity with Scientific Activity Ledger vs raw sources.
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

TARGETS = [
    "MNE-Python/mne-python",
    "nilearn/nilearn",
    "bids-standard/pybids",
]

REPORT_PATH = Path("artifacts/sprint36_agent_onboarding_benchmark.md")

ONBOARDING_TASK = """
You are joining this project. Based on the provided materials, produce a concise onboarding brief that covers:
1. What the project does
2. Key artifacts and where to find them
3. Active workstreams
4. Main contributors
5. Recent changes
6. Suggested first steps for a newcomer
"""


def build_raw_sources(repo: str) -> dict:
    """Simulate raw repository access bundle."""
    gh = map_repo_to_artifacts(repo)
    readme = gh[0].to_dict() if gh else {}
    return {
        "repo": repo,
        "readme": readme,
        "artifacts": [a.to_dict() for a in gh],
        "access": "full_repo",
    }


def build_ledger_only(repo: str) -> dict:
    """Generate Scientific Activity Ledger only."""
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
    resolved = resolve_artifacts(artifacts)
    merged = resolved["merged_artifacts"]
    ledger = build_ledger(merged, ledger_id=repo, name=repo.split("/")[-1])
    return {
        "repo": repo,
        "ledger": ledger.to_dict(),
        "access": "ledger_only",
    }


def render_report(entries: list) -> str:
    lines = [
        "# Sprint 36: Agent Onboarding Benchmark",
        "",
        "Date: 2026-07-17",
        "Hypothesis: A Scientific Activity Ledger reduces agent onboarding cost compared to raw sources.",
        "Success criterion: >=50% reduction in time-to-first-output with <=10% drop in completeness/accuracy.",
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
        "### Condition A: Raw Sources",
        "- Full repository access (README, issues, PRs, releases, papers)",
        "",
        "### Condition B: Scientific Activity Ledger",
        "- Ledger only (no direct repo access)",
        "",
        "## Task",
        "",
        ONBOARDING_TASK,
        "",
        "## Metrics",
        "",
        "- Time to first useful output (seconds)",
        "- Completeness (0–1)",
        "- Accuracy (0–1)",
        "- Actionability (0–1)",
        "",
        "## Analysis Plan",
        "",
        "- Mean time delta (raw - ledger)",
        "- Mean completeness delta (ledger - raw)",
        "- Statistical significance (t-test, n>=10 per condition)",
        "",
        "## Required Participants",
        "",
        "- At least 10 agent runs per condition per project.",
        "- Total minimum: 60 runs across 3 projects and 2 conditions.",
        "",
        "## Next Steps",
        "",
        "1. Prepare raw-source bundles and ledgers.",
        "2. Run agent benchmark.",
        "3. Analyze deltas.",
        "4. Report statistical significance and practical impact.",
        "",
    ])
    return "\n".join(lines)


def main():
    entries = []
    for repo in TARGETS:
        raw = build_raw_sources(repo)
        ledger = build_ledger_only(repo)
        entries.append({
            "project": repo.split("/")[-1],
            "repo": repo,
            "raw_artifacts": len(raw["artifacts"]),
            "ledger_artifacts": len(ledger["ledger"]["artifacts"]),
            "ledger_workstreams": len(ledger["ledger"]["workstreams"]),
            "ledger_contributors": len(ledger["ledger"]["contributors"]),
        })
    report = render_report(entries)
    REPORT_PATH.write_text(report, encoding="utf-8")
    print(f"Saved: {REPORT_PATH}")


if __name__ == "__main__":
    main()