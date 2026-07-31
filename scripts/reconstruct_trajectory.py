#!/usr/bin/env python3
"""
SPRINT 60C: Reconstruct trajectory graph from decisions and edges.
Produces EvidenceGraph-compatible output with DecisionNodes.
"""
import json
from typing import Dict, List

class TrajectoryReconstructor:
    """Reconstruct trajectory graph from decisions and edges."""
    
    def __init__(self, repository: str):
        self.repository = repository
        self.nodes = []
        self.edges = []
        self.node_map = {}
    
    def add_decisions(self, decisions: List[Dict]):
        """Add decision nodes to graph."""
        for d in decisions:
            node = {
                "id": d["decision_id"],
                "type": "Decision",
                "decision": d.get("decision", ""),
                "actor": d.get("actor", ""),
                "timestamp": d.get("timestamp", ""),
                "rationale": d.get("rationale", ""),
                "outcome": d.get("outcome", "unknown"),
                "confidence": d.get("confidence", 0.5),
                "classification": d.get("classification", "derivable"),
                "evidence": d.get("evidence", []),
                "repository": self.repository
            }
            self.nodes.append(node)
            self.node_map[d["decision_id"]] = node
    
    def add_edges(self, edges: List[Dict]):
        """Add edges to graph."""
        for edge in edges:
            self.edges.append({
                "from": edge["from"],
                "to": edge["to"],
                "type": edge["type"],
                "weight": edge.get("confidence", 0.5),
                "timestamp": "",
                "evidence": edge.get("evidence", [])
            })
    
    def build_graph(self) -> Dict:
        """Build complete EvidenceGraph."""
        # Calculate metrics
        total = len(self.nodes)
        outcomes = [n.get("outcome") for n in self.nodes]
        
        metrics = {
            "total_decisions": total,
            "abandoned_decisions": sum(1 for o in outcomes if o == "abandoned"),
            "successful_decisions": sum(1 for o in outcomes if o == "success"),
            "superseded_decisions": sum(1 for o in outcomes if o == "superseded"),
            "failed_decisions": sum(1 for o in outcomes if o == "failure"),
            "edges_count": len(self.edges),
            "avg_confidence": round(sum(n.get("confidence", 0.5) for n in self.nodes) / total, 2) if total > 0 else 0.0
        }
        
        graph = {
            "graph_id": "",  # Assigned by caller
            "request_id": "",  # Assigned by caller
            "nodes": self.nodes,
            "edges": self.edges,
            "metrics": metrics,
            "provenance": {
                "generated_by": "sprint60c-trajectory-reconstructor",
                "timestamp": "",  # Assigned by caller
                "repository": self.repository,
                "processing_notes": [
                    f"Reconstructed {total} decisions and {len(self.edges)} edges",
                    f"Outcomes: {metrics['successful_decisions']} success, {metrics['abandoned_decisions']} abandoned"
                ]
            }
        }
        
        return graph
    
    def to_evidence_graph(self, trajectory: Dict) -> Dict:
        """Convert trajectory to EvidenceGraph format."""
        # Transform decision nodes into EvidenceGraph node format
        eg_nodes = []
        for node in trajectory.get("nodes", []):
            eg_nodes.append({
                "id": node["id"],
                "type": "Decision",
                "decision": node.get("decision", ""),
                "actor": node.get("actor", ""),
                "timestamp": node.get("timestamp", ""),
                "outcome": node.get("outcome", ""),
                "confidence": node.get("confidence", 0.5),
                "classification": node.get("classification", "derivable")
            })
        
        eg_edges = []
        for edge in trajectory.get("edges", []):
            eg_edges.append({
                "from": edge["from"],
                "to": edge["to"],
                "type": edge["type"],
                "weight": edge.get("weight", 0.5)
            })
        
        return {
            "graph_id": trajectory.get("graph_id", ""),
            "request_id": trajectory.get("request_id", ""),
            "nodes": eg_nodes,
            "edges": eg_edges,
            "provenance": trajectory.get("provenance", {})
        }


def main():
    import argparse
    parser = argparse.ArgumentParser(description="SPRINT 60C: Reconstruct trajectory")
    parser.add_argument("--decisions", required=True, help="Input decisions JSONL")
    parser.add_argument("--edges", required=True, help="Input edges JSONL")
    parser.add_argument("--output", required=True, help="Output trajectory JSON")
    parser.add_argument("--repository", required=True, help="Repository name")
    parser.add_argument("--graph-id", default="EG-000001", help="Graph ID")
    parser.add_argument("--request-id", default="ER-000001", help="Request ID")
    args = parser.parse_args()
    
    # Load decisions
    decisions = []
    with open(args.decisions, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                decisions.append(json.loads(line))
    
    # Load edges
    edges = []
    with open(args.edges, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                edges.append(json.loads(line))
    
    # Reconstruct
    reconstructor = TrajectoryReconstructor(args.repository)
    reconstructor.add_decisions(decisions)
    reconstructor.add_edges(edges)
    
    trajectory = reconstructor.build_graph()
    trajectory["graph_id"] = args.graph_id
    trajectory["request_id"] = args.request_id
    trajectory["provenance"]["timestamp"] = __import__("datetime").datetime.now(__import__("datetime").timezone.utc).isoformat()
    
    evidence_graph = reconstructor.to_evidence_graph(trajectory)
    
    with open(args.output, "w", encoding="utf-8") as f:
        json.dump(evidence_graph, f, indent=2, default=str)
    
    print(f"Reconstructed trajectory: {len(decisions)} decisions, {len(edges)} edges")
    print(f"Output: {args.output}")


if __name__ == "__main__":
    main()