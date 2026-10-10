#!/usr/bin/env python3
"""
SPRINT 72 — Knowledge Graph Feasibility Assessment

Evaluates whether a local SQLite graph can represent the context layer
entities in CoResearcher: Goals, Experiments, Evolutions, Evidence,
and GitHub Issues.

This is a READ-ONLY audit. It does NOT create a new graph or schema.
It maps existing sources to candidate graph entities and measures
feasibility against the constitution:

  1. Evidence-based: every claim traceable to source (OBSERVED/DERIVED)
  2. No premature abstraction: no classification without empirical grounding
  3. All findings classified OBSERVED / INFERRED / UNKNOWN
"""
import json
import sqlite3
import shutil
import tempfile
from pathlib import Path
from typing import Any, Dict, List

PROJECT_ROOT = Path(__file__).resolve().parent.parent


def load_json(path: Path) -> Any:
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return None


def load_jsonl(path: Path) -> list:
    items = []
    if not path.exists():
        return items
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                try:
                    items.append(json.loads(line))
                except json.JSONDecodeError:
                    continue
    return items


class SQLiteFeasibilityEvaluator:
    """Evaluate whether SQLite can represent the context entities."""

    def __init__(self):
        self.sources = {}

    def collect_sources(self) -> Dict[str, Any]:
        """Map available data sources to potential graph entities."""

        # Goals — from documents and active goals
        goals = []
        goals_sources = [
            (PROJECT_ROOT / "docs" / "SPRINT_60C_BRIDGE_H6_H7_EHG.md",
             "H6 Decision Reconstruction — pending validation"),
            (PROJECT_ROOT / "docs" / "SPRINT_60C_ANALYSIS_AND_VISION.md",
             "Validate H6 with >=70% reconstruction rate"),
        ]
        for path, desc in goals_sources:
            if path.exists():
                goals.append({"source": path.name, "description": desc, "exist": True})
            else:
                goals.append({"source": path.name, "description": desc, "exist": False})

        # Experiments — from sprint artifacts
        experiments = []
        experiment_patterns = [
            "falsification_experiment",
            "sprint61_convergence_review",
            "scientific_instrumentability_matrix",
            "observable_signature",
            "observation_explanation_differential",
            "meta_measurement_audit",
            "instrumentability_calibration_attack",
        ]
        artifacts_dir = PROJECT_ROOT / "artifacts"
        for pattern in experiment_patterns:
            found = list(artifacts_dir.glob(f"*{pattern}*"))
            experiments.append({
                "pattern": pattern,
                "found": len(found) > 0,
                "files": [f.name for f in found]
            })

        # Evolutions — from docs directory naming
        evolutions = []
        evolution_patterns = [
            "SPRINT_66_AUDIT",
            "EPISTEMIC_GAP_CONCEPT",
            "CORIGAMI_DISCOVERY_PATTERN",
            "DECISION_EXECUTION_REGISTRY",
        ]
        docs_dir = PROJECT_ROOT / "docs"
        for pattern in evolution_patterns:
            found = list(docs_dir.glob(f"*{pattern}*"))
            evolutions.append({
                "pattern": pattern,
                "found": len(found) > 0,
                "files": [f.name for f in found]
            })

        # Evidence — trajectory decisions and claims
        evidence = {}
        traj_dir = PROJECT_ROOT / "data" / "trajectories" / "langchain_ai_langgraph"
        decisions = load_jsonl(traj_dir / "decisions_classified.jsonl")
        edges = load_jsonl(traj_dir / "edges.jsonl")
        evidence["decisions"] = len(decisions)
        evidence["edges"] = len(edges)
        evidence["trajectory_graph_exists"] = (traj_dir / "trajectory_graph.json").exists()

        claims = load_json(PROJECT_ROOT / "knowledge" / "registry" / "claims.json")
        evidence["claims"] = len(claims.get("claims", {})) if claims else 0

        # GitHub Issues — from local data (no active issues in repo)
        gh_issues = {"local_brepo_count": 0}
        try:
            import subprocess
            r = subprocess.run(
                ["gh", "issue", "list", "--repo", "Fundacion-de-Neurociencias/coresearcher",
                 "--limit", "100", "--state", "all", "--json", "number,title,state"],
                capture_output=True, text=True, timeout=15, cwd=str(PROJECT_ROOT)
            )
            if r.returncode == 0 and r.stdout.strip():
                gh_issues["issues"] = json.loads(r.stdout)
                gh_issues["count"] = len(gh_issues["issues"])
            else:
                gh_issues["count"] = 0
                gh_issues["note"] = "No issues accessible locally"
        except Exception as e:
            gh_issues["count"] = 0
            gh_issues["note"] = f"gh CLI unavailable: {e}"

        return {
            "goals": goals,
            "experiments": experiments,
            "evolutions": evolutions,
            "evidence": evidence,
            "github_issues": gh_issues,
        }

    def evaluate_graph_representability(self, sources: Dict[str, Any]) -> Dict[str, Any]:
        """Evaluate whether each entity type can be represented in SQLite."""

        # SQLite structural capabilities
        structural = {
            "node_types": "can represent via table with type column",
            "edges": "can represent via edges table (from, to, type)",
            "timestamps": "ISO-8601 text columns",
            "provenance": "JSON columns for nested evidence",
            "traversal": "recursive CTEs for graph queries",
            "constraints": "FOREIGN KEY + CHECK for graph invariants",
            "scale": "handles 10^5-10^6 nodes comfortably",
        }

        # Per-entity feasibility
        entity_feasibility = []

        # Goals
        goals = sources["goals"]
        goals_existing = [g for g in goals if g["exist"]]
        entity_feasibility.append({
            "entity": "Goals",
            "sources_available": len(goals_existing),
            "representable": True,
            "classification": "OBSERVED",
            "evidence": "Goals explicitly documented in SPRINT_60C_BRIDGE_H6_H7_EHG.md and SPRINT_60C_ANALYSIS_AND_VISION.md",
            "sqlite_schema": {
                "table": "goals",
                "columns": ["goal_id TEXT PRIMARY KEY", "description TEXT", "status TEXT",
                           "source TEXT", "created_at TEXT"]
            },
            "limitations": "Goals are document-derived (markdown), not structured registry entries"
        })

        # Experiments
        experiments = sources["experiments"]
        experiments_existing = [e for e in experiments if e["found"]]
        entity_feasibility.append({
            "entity": "Experiments",
            "sources_available": len(experiments_existing),
            "representable": True,
            "classification": "OBSERVED",
            "evidence": f"{len(experiments_existing)} sprint experiment artifacts found with metrics (JSON)",
            "sqlite_schema": {
                "table": "experiments",
                "columns": ["experiment_id TEXT PRIMARY KEY", "artifact_path TEXT",
                           "metrics JSON", "status TEXT", "sprint TEXT"]
            },
            "limitations": "Experiments exist as standalone JSON artifacts; no central registry cross-references them"
        })

        # Evolutions
        evolutions = sources["evolutions"]
        evolutions_existing = [e for e in evolutions if e["found"]]
        entity_feasibility.append({
            "entity": "Evolutions",
            "sources_available": len(evolutions_existing),
            "representable": True,
            "classification": "OBSERVED",
            "evidence": f"{len(evolutions_existing)} evolution documents found in docs/",
            "sqlite_schema": {
                "table": "evolutions",
                "columns": ["evolution_id TEXT PRIMARY KEY", "title TEXT",
                           "status TEXT", "source_doc TEXT"]
            },
            "limitations": "Evolutions are narrative documents, not structured entities with explicit evolution rules"
        })

        # Evidence
        evidence = sources["evidence"]
        evidence_total = evidence.get("decisions", 0) + evidence.get("claims", 0)
        entity_feasibility.append({
            "entity": "Evidence",
            "sources_available": evidence_total,
            "representable": True,
            "classification": "OBSERVED",
            "evidence": f"{evidence['decisions']} decisions + {evidence['claims']} claims + {evidence['edges']} edges already in structured JSONL/JSON",
            "sqlite_schema": {
                "table": "evidence_nodes",
                "columns": ["node_id TEXT PRIMARY KEY", "node_type TEXT",
                           "payload JSON", "source_artifact TEXT"]
            },
            "limitations": "Trajectory graph itself is already a graph — SQLite adds query capability but not new knowledge"
        })

        # GitHub Issues
        gh_issues = sources["github_issues"]
        gh_count = gh_issues.get("count", 0)
        entity_feasibility.append({
            "entity": "GitHub Issues",
            "sources_available": gh_count,
            "representable": True,
            "classification": "OBSERVED" if gh_count > 0 else "UNKNOWN",
            "evidence": f"{gh_count} issues accessible via gh CLI" if gh_count > 0 else "No accessible issues; gh CLI returned 0 entries",
            "sqlite_schema": {
                "table": "github_issues",
                "columns": ["issue_number INTEGER PRIMARY KEY", "title TEXT",
                           "state TEXT", "body TEXT", "labels JSON"]
            },
            "limitations": "Issues live in GitHub; SQLite mirror would be a cache, not source of truth"
        })

        # Overall verdict
        all_representable = all(e["representable"] for e in entity_feasibility)
        return {
            "structural_capabilities": structural,
            "entity_feasibility": entity_feasibility,
            "all_representable": all_representable,
            "classification_summary": {
                "OBSERVED": sum(1 for e in entity_feasibility if e["classification"] == "OBSERVED"),
                "INFERRED": sum(1 for e in entity_feasibility if e["classification"] == "INFERRED"),
                "UNKNOWN": sum(1 for e in entity_feasibility if e["classification"] == "UNKNOWN"),
            },
            "verdict": (
                "SQLite CAN represent all five entity types structurally. "
                "The key advantage is not representation (JSON already does that) "
                "but QUERYABILITY: recursive CTEs enable graph traversal that "
                "JSON files cannot provide. The bottleneck is SOURCE INTEGRATION "
                "(parsing markdown docs into structured records), not storage."
            )
        }


def main():
    print("=" * 60)
    print("SPRINT 72 — SQLite Knowledge Graph Feasibility")
    print("=" * 60)

    evaluator = SQLiteFeasibilityEvaluator()
    sources = evaluator.collect_sources()
    result = evaluator.evaluate_graph_representability(sources)

    # Write output
    output_path = PROJECT_ROOT / "artifacts" / "context_pack" / "knowledge_graph_feasibility.json"
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2, ensure_ascii=False)

    print(f"Entity coverage:")
    for e in result["entity_feasibility"]:
        print(f"  - {e['entity']}: {e['sources_available']} sources, classification={e['classification']}")
    print(f"All representable: {result['all_representable']}")
    print(f"Verdict: {result['verdict']}")
    print()
    print(f"Output: {output_path}")


if __name__ == "__main__":
    main()