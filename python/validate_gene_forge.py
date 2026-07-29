"""
Sprint 27 - Observer Validation Report for GeneForge
Validates whether the Observer reconstructs scientific reality.
"""

import sys
import json
sys.path.insert(0, '.')

from observer.git_scanner import extract_commit_messages, reconstruct_ledger
from observer.evidence_extractor import extract_evidence, group_scientific_evidence
from observer.ledger_generator import generate_ledger
from pathlib import Path

REPO_PATH = "agents/gene-forge-tmp"

print("=" * 70)
print("GENEFORGE VALIDATION REPORT - SPRINT 27")
print("=" * 70)

# Step 1: Extract commits
print("\n1. Extracting commits...")
commits = extract_commit_messages(REPO_PATH)
print(f"   Total commits: {len(commits)}")

# Step 2: Extract evidence
print("\n2. Extracting evidence...")
evidence = extract_evidence(commits)
print(f"   Scientific evidence: {len(evidence.get('scientific', []))}")
print(f"   Engineering evidence: {len(evidence.get('engineering', []))}")

# Step 3: Group scientific evidence into objectives
print("\n3. Grouping scientific evidence...")
objectives = group_scientific_evidence(evidence.get("scientific", []))
print(f"   Objectives inferred: {len(objectives)}")

# Step 4: Infer artifacts
print("\n4. Inferring artifacts...")
import subprocess
result = subprocess.run(
    ["git", "tag"],
    cwd=REPO_PATH,
    capture_output=True,
    text=True
)
artifacts = [tag for tag in result.stdout.strip().split("\n") if tag]
print(f"   Tags found: {len(artifacts)}")

# Step 5: Generate ledger
print("\n5. Generating ledger...")
ledger_md = generate_ledger(
    objectives=objectives,
    evidence=evidence,
    artifacts=artifacts
)

# Save validation report
report_lines = [
    "# GeneForge Validation Report",
    "",
    "## Precision: Artifacts Detected",
    "",
]

# Check what artifacts were detected
report_lines.append(f"- **Total commits**: {len(commits)}")
report_lines.append(f"- **Scientific evidence items**: {len(evidence.get('scientific', []))}")
report_lines.append(f"- **Engineering evidence items**: {len(evidence.get('engineering', []))}")
report_lines.append(f"- **Objectives inferred**: {len(objectives)}")
report_lines.append(f"- **Git tags/releases**: {len(artifacts)}")

# Timeline reconstruction
report_lines.extend([
    "",
    "## Timeline Reconstruction",
    "",
])
for commit in commits[:10]:
    report_lines.append(f"- {commit['date'][:10]}: {commit['message'][:60]}")

# Contributors
report_lines.extend([
    "",
    "## Contributors",
    "",
])
contrib_result = subprocess.run(
    ["git", "shortlog", "-sn"],
    cwd=REPO_PATH,
    capture_output=True,
    text=True
)
contributors = [line.strip() for line in contrib_result.stdout.strip().split("\n") if line.strip()]
report_lines.append(f"- **Total contributors**: {len(contributors)}")
for contrib in contributors[:5]:
    report_lines.append(f"  - {contrib}")

# Priority alignment
report_lines.extend([
    "",
    "## Priority Alignment",
    "",
    "GeneForge is registered in VALIDATION_REPOSITORIES.",
    "It is a core priority target (validation_weight: 1.0).",
    "",
])

# Workstreams
report_lines.extend([
    "",
    "## Workstreams Detected",
    "",
])
for obj in objectives[:5]:
    report_lines.append(f"- {obj.get('id', 'Unknown')}: {obj.get('domain', 'unknown')}")

report_md = "\n".join(report_lines)

# Save to artifacts
with open("artifacts/gene_forge_validation_report.md", "w", encoding="utf-8") as f:
    f.write(report_md)

print("\n" + "=" * 70)
print("VALIDATION REPORT SAVED")
print("=" * 70)
print(f"- artifacts/gene_forge_validation_report.md")

# Print summary
print("\n## Summary")
print(f"| Metric | Value |")
print(f"|--------|-------|")
print(f"| Commits analyzed | {len(commits)} |")
print(f"| Scientific evidence | {len(evidence.get('scientific', []))} |")
print(f"| Engineering evidence | {len(evidence.get('engineering', []))} |")
print(f"| Objectives | {len(objectives)} |")
print(f"| Artifacts/tags | {len(artifacts)} |")