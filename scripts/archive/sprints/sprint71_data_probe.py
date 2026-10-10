#!/usr/bin/env python3
"""SPRINT 71 — Data probe: extract counts for compression ledger, attractor geometry."""
import json, os
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

# 1. Raw evidence count
raw_path = ROOT / "data/trajectories/langchain_ai_langgraph/decisions_raw.jsonl"
if raw_path.exists():
    with open(raw_path) as f:
        raw_lines = [l for l in f if l.strip()]
    print(f"decisions_raw.jsonl: {len(raw_lines)} lines")
    if raw_lines:
        d = json.loads(raw_lines[0])
        print(f"  keys: {list(d.keys())[:10]}")
else:
    print(f"decisions_raw.jsonl NOT found at {raw_path}")

# 2. langgraph_raw.json top-level structure
raw_size = os.path.getsize(ROOT / "data/langgraph_raw.json")
print(f"\nlanggraph_raw.json: {raw_size} bytes")
with open(ROOT / "data/langgraph_raw.json") as f:
    raw = json.load(f)
if isinstance(raw, dict):
    print(f"  top-level keys: {list(raw.keys())[:10]}")
    for k, v in raw.items():
        if isinstance(v, list):
            print(f"  {k}: {len(v)} items")
        elif isinstance(v, dict):
            print(f"  {k}: dict with {len(v)} keys")

# 3. Trajectory graph connectivity
tg_path = ROOT / "data/trajectories/langchain_ai_langgraph/trajectory_graph.json"
with open(tg_path) as f:
    tg = json.load(f)
nodes = tg["nodes"]
edges = tg["edges"]

node_ids = set(n.get("decision_id", "") for n in nodes if n.get("decision_id"))
edge_node_ids = set()
for e in edges:
    edge_node_ids.add(e.get("from", ""))
    edge_node_ids.add(e.get("to", ""))

print(f"\n=== Trajectory Graph ===")
print(f"Nodes: {len(nodes)}")
print(f"Edges: {len(edges)}")
print(f"Node IDs: {len(node_ids)}")
print(f"Edge-referenced IDs: {len(edge_node_ids)}")
print(f"Edge IDs not in node list: {len(edge_node_ids - node_ids)}")
print(f"Node IDs not in any edge: {len(node_ids - edge_node_ids)}")

# Sample edge and node format
sample_edge = edges[0] if edges else {}
print(f"\nSample edge keys: {list(sample_edge.keys())}")
print(f"Sample edge: {json.dumps(sample_edge)[:400]}")
sample_node = nodes[0] if nodes else {}
print(f"Sample node keys: {list(sample_node.keys())}")
print(f"Sample node decision_id: {sample_node.get('decision_id', 'NOT FOUND')}")

edge_types = Counter(e.get("type", "") for e in edges)
print(f"\nEdge types: {dict(edge_types)}")

outcomes = Counter(n.get("outcome", "") for n in nodes)
print(f"Outcomes: {dict(outcomes)}")

# 4. Node-level connectivity for attractor geometry
# Build fan_in/fan_out per node
fan_in = Counter()
fan_out = Counter()
for e in edges:
    src = e.get("from", "")
    tgt = e.get("to", "")
    fan_in[tgt] += 1
    fan_out[src] += 1

# Find nodes with highest fan_in (attractors)
top_fan_in = sorted(fan_in.items(), key=lambda x: x[1], reverse=True)[:10]
top_fan_out = sorted(fan_out.items(), key=lambda x: x[1], reverse=True)[:10]

print(f"\n=== Attractor Geometry (top 10) ===")
print(f"Top fan_in (convergence points):")
for nid, count in top_fan_in:
    print(f"  {nid}: fan_in={count}")

print(f"\nTop fan_out (source points):")
for nid, count in top_fan_out:
    print(f"  {nid}: fan_out={count}")

# Convergence node IDs
with open(ROOT / "artifacts/convergence_review.json") as f:
    conv = json.load(f)
conv_node_ids = set()
for item in conv.get("items", []):
    for d in item.get("decisions", []):
        conv_node_ids.add(d)

print(f"\nConvergence node IDs: {conv_node_ids}")
for nid in conv_node_ids:
    print(f"  {nid}: fan_in={fan_in.get(nid, 0)}, fan_out={fan_out.get(nid, 0)}")

# 5. Path density: what fraction of possible edges exist?
n = len(nodes)
possible_edges = n * (n-1)  # directed, no self-loops
actual_edges = len(edges)
path_density = actual_edges / possible_edges if possible_edges > 0 else 0
print(f"\nPath density: {actual_edges}/{possible_edges} = {path_density:.6f}")

# 6. Cross-repo compression
with open(ROOT / "artifacts/cross_repo_metrics.json") as f:
    cross = json.load(f)
print(f"\n=== Cross-repo ===")
for r in cross:
    total = r["total_claims"]
    obs = r["observable_claims"]
    der = r["derivable_claims"]
    unk = r["unknown_claims"]
    anchored = obs + der
    print(f"  {r['repo']}: {total} → {anchored} anchored, {unk} unanchored, ratio={anchored/total if total>0 else 0:.3f}")

# 7. Gap locations overlap with convergence nodes
with open(ROOT / "artifacts/epistemic_gap_report.json") as f:
    gaps = json.load(f)
gap_locations = set(g.get("location", "") for g in gaps.get("gaps", []))
conv_gap_overlap = gap_locations & conv_node_ids
print(f"\nGaps overlapping convergence nodes: {len(conv_gap_overlap)} / {len(gap_locations)} gap locations, {len(conv_node_ids)} convergence nodes")
print(f"Overlap: {conv_gap_overlap}")
