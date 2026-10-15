"""
Objective Inferrer for Scientific Programs
Groups development evidence into scientific objectives.
"""

from typing import List, Dict
import re


def group_commits_into_evidence(commits: List[Dict]) -> List[Dict]:
    """Group commits into evidence units, not treat each commit as separate."""
    
    # Cluster commits by topic/time
    evidence = []
    current_cluster = []
    
    for commit in commits:
        msg = commit.get("message", "")
        
        # Start new cluster on major topic shift
        if is_scientific_boundary(msg):
            if current_cluster:
                evidence.append({
                    "id": f"EVIDENCE-{len(evidence)+1:06d}",
                    "type": "development",
                    "commits": [c["hash"][:7] for c in current_cluster],
                    "description": summarize_cluster(current_cluster),
                    "date": current_cluster[-1]["date"]
                })
                current_cluster = []
        
        current_cluster.append(commit)
    
    # Don't forget last cluster
    if current_cluster:
        evidence.append({
            "id": f"EVIDENCE-{len(evidence)+1:06d}",
            "type": "development",
            "commits": [c["hash"][:7] for c in current_cluster],
            "description": summarize_cluster(current_cluster),
            "date": current_cluster[-1]["date"]
        })
    
    return evidence


def is_scientific_boundary(message: str) -> bool:
    """Detect if commit message indicates a scientific objective boundary."""
    boundary_patterns = [
        r"paper",
        r"ontology",
        r"framework",
        r"mechanism",
        r"hypothesis",
        r"validation",
        r"figure",
        r"results",
        r"conclusion",
        r"split",
        r"refactor.*into",
        r"new.*approach"
    ]
    
    return any(re.search(p, message, re.I) for p in boundary_patterns)


def summarize_cluster(commits: List[Dict]) -> str:
    """Summarize a cluster of commits into a development activity."""
    if not commits:
        return "no activity"
    
    # Extract key actions
    actions = []
    for commit in commits:
        msg = commit.get("message", "")
        # Extract first meaningful line
        if len(msg) > 20:
            actions.append(msg[:50])
    
    return f"Development sequence: {' + '.join(actions[:3])}"


def infer_objectives(evidence: List[Dict]) -> List[Dict]:
    """Infer research objectives from evidence clusters."""
    
    objectives = []
    
    # Look for evidence patterns that indicate objectives
    for ev in evidence:
        desc = ev.get("description", "").lower()
        
        if "ontology" in desc:
            objectives.append({
                "id": f"OBJECTIVE-{len(objectives)+1:06d}",
                "text": "Develop scientific ontology",
                "evidence": [ev["id"]],
                "date": ev["date"]
            })
        elif "paper" in desc or "manuscrito" in desc:
            objectives.append({
                "id": f"OBJECTIVE-{len(objectives)+1:06d}",
                "text": "Write scientific paper",
                "evidence": [ev["id"]],
                "date": ev["date"]
            })
        elif "mechanism" in desc or "framework" in desc:
            objectives.append({
                "id": f"OBJECTIVE-{len(objectives)+1:06d}",
                "text": "Develop mechanism or framework",
                "evidence": [ev["id"]],
                "date": ev["date"]
            })
    
    # Merge related evidence into objectives
    for obj in objectives:
        # Find related evidence within 2 weeks
        related = find_related_evidence(obj, evidence)
        obj["evidence"].extend([e["id"] for e in related])
    
    return objectives


def find_related_evidence(objective: Dict, all_evidence: List[Dict]) -> List[Dict]:
    """Find evidence temporally related to an objective."""
    # Simple temporal proximity for now
    return []


def build_scientific_ledger(evidence: List[Dict], objectives: List[Dict]) -> Dict:
    """Build the scientific ledger organized by objectives."""
    
    # Group evidence by objective
    for obj in objectives:
        obj["evidence_count"] = len(obj["evidence"])
    
    return {
        "objectives": objectives,
        "evidence": evidence,
        "summary": {
            "total_objectives": len(objectives),
            "total_evidence": len(evidence),
            "coverage": f"{len(objectives)} objectives from {len(evidence)} evidence units"
        }
    }


if __name__ == "__main__":
    # Test with sample data
    sample_commits = [
        {"hash": "abc123", "date": "2024-01-15", "message": "feat: create GWAS parser module"},
        {"hash": "def456", "date": "2024-01-16", "message": "fix: parser bug for chromosome 21"},
        {"hash": "ghi789", "date": "2024-01-17", "message": "add: tests for parser"},
        {"hash": "jkl012", "date": "2024-01-20", "message": "feat: generate ROC figure for biomarker validation"},
        {"hash": "mno345", "date": "2024-01-21", "message": "docs: add results section to manuscript"}
    ]
    
    evidence = group_commits_into_evidence(sample_commits)
    objectives = infer_objectives(evidence)
    ledger = build_scientific_ledger(evidence, objectives)
    
    print("=" * 70)
    print("SCIENTIFIC LEDGER (by Objectives)")
    print("=" * 70)
    
    for obj in objectives:
        print(f"\n{obj['id']}: {obj['text']}")
        print(f"  Evidence units: {obj['evidence_count']}")