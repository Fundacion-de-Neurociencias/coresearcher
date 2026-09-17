#!/usr/bin/env python3
"""
SPRINT 71 — Compression Ledger

Builds the compression ledger: measures input_count, output_count,
compression_ratio, and information_loss for each transformation in
the CoResearcher pipeline.

No new entities. No new schemas. No new graphs.
Read-only analysis over existing data artifacts.
"""
import json
import os
from collections import Counter
from pathlib import Path

# ------------------------------------------------------------------
# Data paths (all existing artifacts)
# ------------------------------------------------------------------
PROJECT_ROOT = Path(__file__).resolve().parent.parent
TRAJECTORY_GRAPH = PROJECT_ROOT / "data/trajectories/langchain_ai_langgraph/trajectory_graph.json"
DECISIONS_RAW = PROJECT_ROOT / "data/trajectories/langchain_ai_langgraph/decisions_raw.jsonl"
CONVERGENCE_REVIEW = PROJECT_ROOT / "artifacts/convergence_review.json"
EPISTEMIC_GAP_REPORT = PROJECT_ROOT / "artifacts/epistemic_gap_report.json"
CROSS_REPO_METRICS = PROJECT_ROOT / "artifacts/cross_repo_metrics.json"
OBSERVABLE_SIGNATURE = PROJECT_ROOT / "artifacts/observable_signature.json"

# ------------------------------------------------------------------
# Helper: count JSONL lines
# ------------------------------------------------------------------
def count_jsonl(path):
    if not path.exists():
        return 0
    with open(path, "r", encoding="utf-8") as f:
        return sum(1 for line in f if line.strip())

# ------------------------------------------------------------------
# Build ledger
# ------------------------------------------------------------------
def build_ledger():
    ledger = []

    # Load trajectory graph
    with open(TRAJECTORY_GRAPH, "r", encoding="utf-8") as f:
        tg = json.load(f)
    nodes = tg.get("nodes", [])
    edges = tg.get("edges", [])

    # Load raw decisions
    raw_count = count_jsonl(DECISIONS_RAW)

    # Load convergences
    with open(CONVERGENCE_REVIEW, "r", encoding="utf-8") as f:
        conv = json.load(f)
    conv_count = len(conv.get("items", []))

    # Load gaps report
    with open(EPISTEMIC_GAP_REPORT, "r", encoding="utf-8") as f:
        gaps_report = json.load(f)
    gap_count = gaps_report["metrics"]["total_gaps"]
    gap_density = gaps_report["metrics"]["gap_density"]

    # Load cross-repo metrics
    with open(CROSS_REPO_METRICS, "r", encoding="utf-8") as f:
        cross_repo = json.load(f)

    # ------------------------------------------------------------------
    # Transformation 1: Raw Evidence → DecisionNode
    # ------------------------------------------------------------------
    # Raw evidence = extracted artifacts (issues/PRs/commits that signal decisions)
    # Output = classified DecisionNodes
    edge_types = Counter(e.get("type", "") for e in edges)
    outcomes = Counter(n.get("outcome", "") for n in nodes)
    actors = set(n.get("actor", "") for n in nodes)
    artifact_types = Counter(n.get("artifact_type", "") for n in nodes)

    # Information loss: nodes with pending outcome (no observable result)
    pending_count = outcomes.get("pending", 0)
    info_loss_1 = pending_count  # decisions with no observable outcome

    ledger.append({
        "transformation": "Raw Evidence → DecisionNode",
        "input_count": raw_count,
        "output_count": len(nodes),
        "compression_ratio": round(len(nodes) / raw_count, 4) if raw_count > 0 else 0,
        "information_loss": info_loss_1,
        "information_loss_pct": round(info_loss_1 / len(nodes) * 100, 2) if len(nodes) > 0 else 0,
        "details": {
            "node_outcomes": dict(outcomes),
            "unique_actors": len(actors),
            "artifact_types": dict(artifact_types),
        },
        "source_artifacts": [
            "data/trajectories/langchain_ai_langgraph/decisions_raw.jsonl",
            "data/trajectories/langchain_ai_langgraph/trajectory_graph.json",
        ],
    })

    # ------------------------------------------------------------------
    # Transformation 2: DecisionNode → Trajectory (edge reconstruction)
    # ------------------------------------------------------------------
    # Input = DecisionNodes, Output = edges (relationships reconstructed)
    # Information loss: DecisionNodes that have no edges (isolated)
    nodes_with_edges = set()
    for e in edges:
        nodes_with_edges.add(e.get("from", ""))
        nodes_with_edges.add(e.get("to", ""))
    isolated_nodes = len(nodes) - len(nodes_with_edges)
    info_loss_2 = isolated_nodes

    # Compression ratio: edges per node
    edges_per_node = round(len(edges) / len(nodes), 4) if len(nodes) > 0 else 0

    ledger.append({
        "transformation": "DecisionNode → Trajectory (edge reconstruction)",
        "input_count": len(nodes),
        "output_count": len(edges),
        "compression_ratio": edges_per_node,
        "information_loss": info_loss_2,
        "information_loss_pct": round(info_loss_2 / len(nodes) * 100, 2) if len(nodes) > 0 else 0,
        "details": {
            "edge_types": dict(edge_types),
            "isolated_nodes": isolated_nodes,
            "nodes_with_edges": len(nodes_with_edges),
        },
        "source_artifacts": [
            "data/trajectories/langchain_ai_langgraph/trajectory_graph.json",
        ],
    })

    # ------------------------------------------------------------------
    # Transformation 3: Trajectory → Convergence
    # ------------------------------------------------------------------
    # Input = DecisionNodes with edges, Output = convergences
    # Information loss: all DecisionNodes that do NOT form a convergence
    convergence_node_ids = set()
    for item in conv.get("items", []):
        for d in item.get("decisions", []):
            convergence_node_ids.add(d)
    non_convergence_nodes = len(nodes) - len(convergence_node_ids)
    info_loss_3 = non_convergence_nodes  # nodes not part of any convergence

    ledger.append({
        "transformation": "Trajectory → Convergence (clustering)",
        "input_count": len(nodes),
        "output_count": conv_count,
        "compression_ratio": round(conv_count / len(nodes), 4) if len(nodes) > 0 else 0,
        "information_loss": info_loss_3,
        "information_loss_pct": round(info_loss_3 / len(nodes) * 100, 2) if len(nodes) > 0 else 0,
        "details": {
            "convergence_themes": [item.get("theme", "") for item in conv.get("items", [])],
            "convergence_types": [item.get("type", "") for item in conv.get("items", [])],
            "convergence_actors_per": [len(item.get("actors", [])) for item in conv.get("items", [])],
            "nodes_in_convergences": len(convergence_node_ids),
        },
        "source_artifacts": [
            "artifacts/convergence_review.json",
        ],
    })

    # ------------------------------------------------------------------
    # Transformation 4: Evidence → Gap (gap detection)
    # ------------------------------------------------------------------
    # Input = DecisionNodes, Output = gaps
    # Information loss: nodes without gaps (not all nodes have gaps)
    gap_locations = set()
    for g in gaps_report.get("gaps", []):
        gap_locations.add(g.get("location", ""))
    nodes_without_gaps = len(nodes) - len(gap_locations)
    info_loss_4 = nodes_without_gaps

    ledger.append({
        "transformation": "Evidence → Gap (detection)",
        "input_count": len(nodes),
        "output_count": gap_count,
        "compression_ratio": round(gap_count / len(nodes), 4) if len(nodes) > 0 else 0,
        "information_loss": info_loss_4,
        "information_loss_pct": round(info_loss_4 / len(nodes) * 100, 2) if len(nodes) > 0 else 0,
        "details": {
            "gap_by_type": gaps_report["metrics"]["by_type"],
            "gap_by_severity": gaps_report["metrics"]["by_severity"],
            "gap_by_characterization": gaps_report["metrics"]["by_characterization"],
            "gap_density": gap_density,
            "nodes_with_gaps": len(gap_locations),
        },
        "source_artifacts": [
            "artifacts/epistemic_gap_report.json",
        ],
    })

    # ------------------------------------------------------------------
    # Cross-repo compression snapshot
    # ------------------------------------------------------------------
    cross_repo_summary = []
    for r in cross_repo:
        total = r["total_claims"]
        observable = r["observable_claims"]
        derivable = r["derivable_claims"]
        unknown = r["unknown_claims"]
        anchored = observable + derivable
        ratio = anchored / total if total > 0 else 0
        cross_repo_summary.append({
            "repo": r["repo"],
            "total_claims": total,
            "anchored_claims": anchored,
            "unanchored_claims": unknown,
            "anchoring_ratio": round(ratio, 4),
            "observable_ratio": r["observable_ratio"],
            "gaps": r["total_gaps"],
        })

    return {
        "report_id": f"SPRINT71-LEDGER-{int(__import__('datetime').datetime.now().timestamp())}",
        "sprint": "SPRINT 71 — Search Space Compression Audit",
        "phase": "FASE 1 — Compression Ledger",
        "methodology": "Measure input_count, output_count, compression_ratio, information_loss for each transformation. No new entities introduced.",
        "repository": "langchain-ai/langgraph",
        "ledger": ledger,
        "cross_repo_compression": cross_repo_summary,
        "pipeline_summary": {
            "step_1": "Raw Evidence → DecisionNode",
            "step_2": "DecisionNode → Trajectory",
            "step_3": "Trajectory → Convergence",
            "final_compression": {
                "input_nodes": len(nodes),
                "output_convergences": conv_count,
                "compression_ratio": round(conv_count / len(nodes), 4) if len(nodes) > 0 else 0,
            },
        },
        "epistemic_note": "Compression is observable. Information loss is measurable. No interpretation introduced. All metrics trace to existing data artifacts.",
    }


def main():
    report = build_ledger()

    output_json = PROJECT_ROOT / "artifacts" / "compression_ledger.json"
    output_json.parent.mkdir(parents=True, exist_ok=True)
    with open(output_json, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, ensure_ascii=False, default=str)

    # Console summary
    print("=" * 70)
    print("SPRINT 71 — Compression Ledger (FASE 1)")
    print("=" * 70)
    print()
    for entry in report["ledger"]:
        print(f"  {entry['transformation']}")
        print(f"    input={entry['input_count']} → output={entry['output_count']}")
        print(f"    ratio={entry['compression_ratio']}, info_loss={entry['information_loss']} ({entry['information_loss_pct']}%)")
        if entry.get("details"):
            for k, v in entry["details"].items():
                print(f"    {k}: {v}")
        print()

    print("  Cross-repo compression:")
    for r in report["cross_repo_compression"]:
        print(f"    {r['repo']}: {r['total_claims']} → {r['anchored_claims']} anchored ({r['anchoring_ratio']:.3f})")

    print()
    print(f"  Pipeline: {report['pipeline_summary']['final_compression']['input_nodes']} nodes → {report['pipeline_summary']['final_compression']['output_convergences']} convergences (ratio={report['pipeline_summary']['final_compression']['compression_ratio']})")
    print()
    print(f"  Output: {output_json}")
    print("=" * 70)


if __name__ == "__main__":
    main()
