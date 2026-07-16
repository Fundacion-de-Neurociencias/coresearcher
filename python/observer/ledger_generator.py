"""
Ledger Generator
Creates navigable scientific ledger from extracted evidence
"""

from typing import Dict, List
from pathlib import Path


def generate_ledger(
    objectives: List[Dict],
    evidence: Dict[str, List[Dict]],
    artifacts: List[Dict],
    contributors: List[str]
) -> str:
    """Generate markdown ledger for a project."""
    
    lines = [
        "# Scientific Activity Ledger",
        "",
        "## Objectives",
        "",
    ]
    
    for obj in objectives:
        lines.extend([
            f"### {obj.get('id', 'OBJECTIVE')}",
            "",
            f"**Period:** {obj.get('period', 'unknown')}",
            "",
            f"**Hypothesis:** {obj.get('hypothesis', 'unspecified')}",
            "",
            "**Evidence commits:**",
            "",
        ])
        for commit in obj.get("evidence", []):
            lines.append(f"- `{commit}`")
        lines.append("")
    
    lines.extend([
        "## Scientific Evidence",
        "",
        f"**Total scientific commits:** {len(evidence.get('scientific', []))}",
        "",
        "### Timeline",
        "",
    ])
    
    for ev in evidence.get("scientific", [])[:20]:  # Last 20
        lines.append(f"- {ev.get('date', '')}: {ev.get('text', '')[:60]}...")
    
    lines.extend([
        "",
        "## Engineering Activity",
        "",
        f"**Total engineering commits:** {len(evidence.get('engineering', []))}",
        "",
    ])
    
    lines.extend([
        "## Artifacts",
        "",
    ])
    
    for artifact in artifacts:
        lines.append(f"- {artifact.get('type', 'unknown')}: {artifact.get('name', 'unnamed')}")
    
    lines.extend([
        "",
        "## Contributors",
        "",
    ])
    
    for contributor in contributors[:10]:
        lines.append(f"- {contributor}")
    
    return "\n".join(lines)


def save_ledger(content: str, output_path: str = "ledger.md"):
    """Save ledger to file."""
    Path(output_path).write_text(content)


def generate_ledger_json(
    objectives: List[Dict],
    evidence: Dict[str, List[Dict]],
    artifacts: List[Dict]
) -> Dict:
    """Generate JSON format of ledger."""
    
    return {
        "objectives": objectives,
        "evidence": evidence,
        "artifacts": artifacts,
        "summary": {
            "total_objectives": len(objectives),
            "total_scientific_evidence": len(evidence.get("scientific", [])),
            "total_engineering_evidence": len(evidence.get("engineering", [])),
            "total_artifacts": len(artifacts)
        }
    }


if __name__ == "__main__":
    # Test ledger generation
    test_data = {
        "objectives": [
            {"id": "OBJECTIVE-001", "period": "2024-01 → 2024-02", "hypothesis": "Biomarker ontology development", "evidence": ["abc123", "def456", "ghi789"]}
        ],
        "evidence": {
            "scientific": [{"date": "2024-01-15", "text": "feat: add biomarker ontology"}, {"date": "2024-01-17", "text": "add: hypothesis on APOE4"}],
            "engineering": [{"date": "2024-01-16", "text": "fix: parser bug"}]
        },
        "artifacts": [{"type": "ontology", "name": "Neurodiagnoses biomarker ontology"}]
    }
    
    ledger = generate_ledger(
        test_data["objectives"],
        test_data["evidence"],
        test_data["artifacts"],
        ["Manuel", "Claude", "Cline"]
    )
    
    print(ledger[:500])