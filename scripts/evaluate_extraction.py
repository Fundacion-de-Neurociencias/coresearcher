#!/usr/bin/env python3
"""
SPRINT 60C: Evaluate extraction quality metrics.
Calculates precision, recall, coverage against validation criteria.
"""
import json
from typing import Dict, List

def load_jsonl(path: str) -> List[Dict]:
    items = []
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                items.append(json.loads(line))
    return items

def calculate_metrics(decisions_path: str, trajectory_path: str) -> Dict:
    """Calculate extraction quality metrics."""
    decisions = load_jsonl(decisions_path)
    
    with open(trajectory_path, "r", encoding="utf-8") as f:
        trajectory = json.load(f)
    
    total = len(decisions)
    if total == 0:
        return {"error": "No decisions extracted"}
    
    # Outcome distribution
    outcomes = {"success": 0, "abandoned": 0, "superseded": 0, "failure": 0, "pending": 0, "unknown": 0}
    for d in decisions:
        outcomes[d.get("outcome", "unknown")] = outcomes.get(d.get("outcome", "unknown"), 0) + 1
    
    # Confidence distribution
    confidences = [d.get("confidence", 0.0) for d in decisions]
    avg_confidence = sum(confidences) / len(confidences) if confidences else 0.0
    
    # Classification distribution
    classifications = {"observable": 0, "derivable": 0, "inferred": 0}
    for d in decisions:
        cls = d.get("classification", "derivable")
        classifications[cls] = classifications.get(cls, 0) + 1
    
    # Evidence coverage
    with_evidence = sum(1 for d in decisions if d.get("evidence"))
    evidence_coverage = with_evidence / total if total > 0 else 0.0
    
    # Artifact type distribution
    artifact_types = {}
    for d in decisions:
        atype = d.get("artifact_type", "unknown")
        artifact_types[atype] = artifact_types.get(atype, 0) + 1
    
    metrics = {
        "total_decisions": total,
        "outcomes": outcomes,
        "avg_confidence": round(avg_confidence, 3),
        "classifications": classifications,
        "evidence_coverage": round(evidence_coverage, 3),
        "artifact_types": artifact_types,
        "edges_count": len(trajectory.get("edges", [])),
        "nodes_count": len(trajectory.get("nodes", []))
    }
    
    return metrics

def main():
    import argparse
    parser = argparse.ArgumentParser(description="SPRINT 60C: Evaluate extraction")
    parser.add_argument("--decisions", required=True, help="Decisions JSONL")
    parser.add_argument("--trajectories", required=True, help="Trajectory JSON")
    parser.add_argument("--output", required=True, help="Output metrics JSON")
    args = parser.parse_args()
    
    metrics = calculate_metrics(args.decisions, args.trajectories)
    
    with open(args.output, "w", encoding="utf-8") as f:
        json.dump(metrics, f, indent=2)
    
    print(f"Metrics calculated and saved to {args.output}")
    print(json.dumps(metrics, indent=2))

if __name__ == "__main__":
    main()