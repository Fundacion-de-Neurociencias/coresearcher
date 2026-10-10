#!/usr/bin/env python3
"""
SPRINT 72 — Context Pack Compiler

Compiles a Context Pack (current_state.md + current_state.json) from
existing CoResearcher data artifacts. This is NOT memory — it is
compiled operational state injected at session start to reduce
the reasoning burden on the agent.

Sources compiled (read-only, no new entities):
  - knowledge/registry/claims.json         (CLAIM-XXXXXX)
  - knowledge/registry/findings.json       (FIND-XXXXXX)
  - knowledge/registry/questions.json      (QUESTION-XXXXXX)
  - knowledge/registry/combined_models.json (MODEL-XXXXXX)
  - knowledge/contracts/                   (consumer contracts)
  - ecosystem/registry/capabilities.json   (capability registrations)
  - ecosystem/registry/connectors.json     (connector registrations)
  - sessions/VS001/*                       (active session data)
  - memory/neurodegeneration_memory.json   (hypotheses/experiments/lessons)
  - artifacts/                             (sprint outputs, survival table, etc.)
  - data/trajectories/                     (langgraph trajectory graph)
  - docs/                                  (README, constitution docs)
  - git log                                (last N commits)

Output:
  - artifacts/context_pack/current_state.md
  - artifacts/context_pack/current_state.json
"""
import json
import os
import subprocess
import datetime
from pathlib import Path
from typing import Any

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


def git_last_commits(n: int = 10):
    """Get last N git commits. Returns list of dicts or empty list on failure."""
    try:
        result = subprocess.run(
            ["git", "log", "--oneline", f"-{n}"],
            capture_output=True, text=True, cwd=str(PROJECT_ROOT), timeout=10
        )
        commits = []
        for line in result.stdout.strip().split("\n"):
            if line:
                parts = line.split(" ", 1)
                commits.append({
                    "hash": parts[0],
                    "message": parts[1] if len(parts) > 1 else ""
                })
        return commits
    except Exception:
        return []


def compile_context_pack() -> dict:
    now = datetime.datetime.now(datetime.timezone.utc).isoformat()

    # ---- 1. Claims registry ----
    claims_data = load_json(PROJECT_ROOT / "knowledge" / "registry" / "claims.json")
    claims = claims_data.get("claims", {}) if claims_data else {}
    total_claims = len(claims)
    claim_by_status = {}
    claim_by_type = {}
    for c in claims.values():
        status = c.get("status", "unknown")
        claim_by_status[status] = claim_by_status.get(status, 0) + 1
        ctype = c.get("metadata", {}).get("claim_type", "unknown")
        claim_by_type[ctype] = claim_by_type.get(ctype, 0) + 1

    # ---- 2. Findings registry ----
    findings_data = load_json(PROJECT_ROOT / "knowledge" / "registry" / "findings.json")
    findings = findings_data.get("findings", {}) if findings_data else {}
    total_findings = len(findings)
    findings_by_quality = {}
    for f in findings.values():
        qs = f.get("quality_score", 0)
        bucket = "high (>=0.7)" if qs >= 0.7 else "medium (0.4-0.7)" if qs >= 0.4 else "low (<0.4)"
        findings_by_quality[bucket] = findings_by_quality.get(bucket, 0) + 1

    # ---- 3. Questions registry ----
    questions_data = load_json(PROJECT_ROOT / "knowledge" / "registry" / "questions.json")
    questions = questions_data.get("questions", {}) if questions_data else {}
    total_questions = len(questions)
    active_questions = sum(1 for q in questions.values() if q.get("status") == "active")

    # ---- 4. Combined models ----
    models_data = load_json(PROJECT_ROOT / "knowledge" / "registry" / "combined_models.json")
    models = models_data.get("models", {}) if models_data else {}
    total_models = len(models)

    # ---- 5. Consumer contracts ----
    contracts_dir = PROJECT_ROOT / "knowledge" / "contracts"
    contracts = []
    if contracts_dir.exists():
        for f in contracts_dir.glob("*.json"):
            c = load_json(f)
            if c:
                contracts.append({"file": f.name, "consumer_id": c.get("consumer_id"), "domain": c.get("domain")})

    # ---- 6. Ecosystem registries ----
    cap_data = load_json(PROJECT_ROOT / "ecosystem" / "registry" / "capabilities.json")
    total_caps = len(cap_data.get("registrations", {})) if cap_data else 0

    conn_data = load_json(PROJECT_ROOT / "ecosystem" / "registry" / "connectors.json")
    connectors = {}
    if conn_data:
        for c in conn_data.get("registrations", {}).values():
            src = c.get("source", "unknown")
            connectors[src] = connectors.get(src, 0) + 1

    # ---- 7. Active session (VS001) ----
    session_dir = PROJECT_ROOT / "sessions" / "VS001"
    session_files = {}
    if session_dir.exists():
        for f in session_dir.iterdir():
            if f.is_file():
                session_files[f.name] = f.stat().st_size

    # ---- 8. Memory (hypotheses/experiments/lessons) ----
    memory_data = load_json(PROJECT_ROOT / "memory" / "neurodegeneration_memory.json")
    hypotheses_count = len(memory_data.get("hypotheses", [])) if memory_data else 0
    experiments_count = len(memory_data.get("experiments", [])) if memory_data else 0
    failures_count = len(memory_data.get("failures", [])) if memory_data else 0
    lessons_count = len(memory_data.get("lessons", [])) if memory_data else 0

    # ---- 9. Key artifacts ----
    artifacts_dir = PROJECT_ROOT / "artifacts"
    recent_artifacts = []
    if artifacts_dir.exists():
        for f in sorted(artifacts_dir.glob("*.json"), key=lambda x: x.stat().st_mtime, reverse=True)[:10]:
            recent_artifacts.append({"file": f.name, "size": f.stat().st_size})
        for f in sorted(artifacts_dir.glob("*.md"), key=lambda x: x.stat().st_mtime, reverse=True)[:10]:
            recent_artifacts.append({"file": f.name, "size": f.stat().st_size})

    # ---- 10. Trajectory data ----
    traj_graph = load_json(PROJECT_ROOT / "data" / "trajectories" / "langchain_ai_langgraph" / "trajectory_graph.json")
    traj_nodes = len(traj_graph.get("nodes", [])) if traj_graph else 0
    traj_edges = len(traj_graph.get("edges", [])) if traj_graph else 0

    eval_metrics = load_json(PROJECT_ROOT / "data" / "trajectories" / "langchain_ai_langgraph" / "evaluation_metrics.json")

    # ---- 11. Cross-repo metrics ----
    cross_repo = load_json(PROJECT_ROOT / "artifacts" / "cross_repo_metrics.json")

    # ---- 12. Survival table ----
    survival = load_json(PROJECT_ROOT / "artifacts" / "sprint70_survival_table.json")

    # ---- 13. Convergence review ----
    conv = load_json(PROJECT_ROOT / "artifacts" / "convergence_review.json")

    # ---- 14. Git history ----
    git_commits = git_last_commits(10)

    # ---- 15. Compression ledger ----
    compression = load_json(PROJECT_ROOT / "artifacts" / "compression_ledger.json")

    # ---- 16. Active goals / objectives ----
    # From SPRINT 60C validation report and SPRINT 60C bridge
    active_goals = []
    # H6 validation is the primary active goal
    active_goals.append({
        "id": "H6",
        "text": "Decision Reconstruction — validate ≥70% reconstruction rate on real GitHub repos via authenticated pipeline",
        "source": "docs/SPRINT_60C_BRIDGE_H6_H7_EHG.md",
        "status": "pending_validated"
    })

    # ---- Compile current_state ----
    context = {
        "generated_at": now,
        "compiled_by": "sprint72_context_pack_compiler.py",
        "classification_legend": {
            "OBSERVED": "Direct, verifiable data from project artifacts",
            "DERIVED": "Logically inferred from observed data",
            "INFERRED": "Hypothesis beyond current evidence — explicitly marked",
            "UNKNOWN": "Cannot be determined from available data"
        },
        "active_goals": active_goals,
        "knowledge_registry": {
            "total_claims": total_claims,
            "claims_by_status": claim_by_status,
            "claims_by_type": claim_by_type,
            "total_findings": total_findings,
            "findings_by_quality": findings_by_quality,
            "total_questions": total_questions,
            "active_questions": active_questions,
            "total_models": total_models,
            "total_hypotheses": hypotheses_count,
            "total_experiments": experiments_count,
            "total_failures": failures_count,
            "total_lessons": lessons_count,
        },
        "ecosystem": {
            "consumer_contracts": contracts,
            "total_capability_registrations": total_caps,
            "connector_sources": connectors,
        },
        "session_vs001": {
            "files": session_files,
        },
        "trajectory_data": {
            "repository": "langchain-ai/langgraph",
            "nodes": traj_nodes,
            "edges": traj_edges,
            "metrics": eval_metrics,
        },
        "cross_repo_metrics": cross_repo,
        "survival_table_summary": {
            "total_claims": len(survival.get("table", [])) if survival else 0,
            "survived": sum(1 for r in survival.get("table", []) if r.get("estado_actual") == "SURVIVED") if survival else 0,
            "falsified": sum(1 for r in survival.get("table", []) if r.get("estado_actual") == "FALSIFIED") if survival else 0,
            "survival_rates": survival.get("survival_rates", {}) if survival else {},
        } if survival else {},
        "convergence_review_summary": {
            "total_convergences": conv.get("summary", {}).get("total_converges", 0) if conv else 0,
            "classified_real": conv.get("summary", {}).get("classified_real", 0) if conv else 0,
            "all_have_3_hypotheses": conv.get("summary", {}).get("all_real_have_3_hypotheses", False) if conv else False,
        } if conv else {},
        "compression_ledger": compression.get("ledger", []) if compression else [],
        "git_recent_commits": git_commits,
        "recent_artifacts": recent_artifacts,
    }

    return context


def render_markdown(ctx: dict) -> str:
    lines = []
    lines.append("# Current State — Context Pack")
    lines.append(f"**Generated**: {ctx['generated_at']}")
    lines.append(f"**Compiled by**: `{ctx['compiled_by']}`")
    lines.append("")
    lines.append("---")
    lines.append("")

    # Classification legend
    lines.append("## Epistemic Classification Legend")
    lines.append("")
    leg = ctx["classification_legend"]
    for k, v in leg.items():
        lines.append(f"- **{k}**: {v}")
    lines.append("")

    # Active goals
    lines.append("## Active Goals")
    lines.append("")
    for g in ctx["active_goals"]:
        lines.append(f"- **{g['id']}**: {g['text']}")
        lines.append(f"  - Source: `{g['source']}`")
        lines.append(f"  - Status: {g['status']}")
    lines.append("")

    # Knowledge registry
    kr = ctx["knowledge_registry"]
    lines.append("## Knowledge Registry")
    lines.append("")
    lines.append(f"- **Claims**: {kr['total_claims']} total")
    lines.append(f"  - By status: {kr['claims_by_status']}")
    lines.append(f"  - By type: {kr['claims_by_type']}")
    lines.append(f"- **Findings**: {kr['total_findings']} total")
    lines.append(f"  - By quality: {kr['findings_by_quality']}")
    lines.append(f"- **Questions**: {kr['total_questions']} total ({kr['active_questions']} active)")
    lines.append(f"- **Combined Models**: {kr['total_models']}")
    lines.append(f"- **Memory (Neurodegeneration)**:")
    lines.append(f"  - Hypotheses: {kr['total_hypotheses']}")
    lines.append(f"  - Experiments: {kr['total_experiments']}")
    lines.append(f"  - Failures: {kr['total_failures']}")
    lines.append(f"  - Lessons: {kr['total_lessons']}")
    lines.append("")

    # Ecosystem
    ec = ctx["ecosystem"]
    lines.append("## Ecosystem")
    lines.append("")
    if ec["consumer_contracts"]:
        lines.append("### Consumer Contracts")
        for c in ec["consumer_contracts"]:
            lines.append(f"- **{c['consumer_id']}** ({c['file']}): domain={c['domain']}, trust_threshold={c.get('trust_threshold', 'N/A')}")
        lines.append("")
    lines.append(f"- **Capability registrations**: {ec['total_capability_registrations']}")
    lines.append("")
    if ec["connector_sources"]:
        lines.append("### Connector Sources")
        for src, count in ec["connector_sources"].items():
            lines.append(f"- {src}: {count} registration(s)")
        lines.append("")

    # Session
    sv = ctx["session_vs001"]
    lines.append("## Active Session: VS001")
    lines.append("")
    for fname, fsize in sv["files"].items():
        lines.append(f"- `{fname}` ({fsize} bytes)")
    lines.append("")

    # Trajectory
    td = ctx["trajectory_data"]
    lines.append("## Trajectory Data (langchain-ai/langgraph)")
    lines.append("")
    lines.append(f"- Nodes: {td['nodes']}")
    lines.append(f"- Edges: {td['edges']}")
    if td["metrics"]:
        m = td["metrics"]
        lines.append(f"- Total decisions: {m.get('total_decisions', 'N/A')}")
        lines.append(f"- Outcomes: {m.get('outcomes', {})}")
        lines.append(f"- Avg confidence: {m.get('avg_confidence', 'N/A')}")
        lines.append(f"- Evidence coverage: {m.get('evidence_coverage', 'N/A')}")
    lines.append("")

    # Cross-repo
    cr = ctx["cross_repo_metrics"]
    if cr:
        lines.append("## Cross-Repository Metrics")
        lines.append("")
        lines.append("| Repo | Total Claims | Observable Ratio | Evidence Coverage |")
        lines.append("|------|-------------|-----------------|-------------------|")
        for r in cr:
            lines.append(f"| {r['repo']} | {r['total_claims']} | {r['observable_ratio']} | {r['evidence_coverage']} |")
        lines.append("")

    # Survival table
    st = ctx["survival_table_summary"]
    if st:
        lines.append("## SPRINT 70 Survival Table Summary")
        lines.append("")
        lines.append(f"- Total claims audited: {st['total_claims']}")
        lines.append(f"- Survived: {st['survived']}")
        lines.append(f"- Falsified: {st['falsified']}")
        for status, rates in st["survival_rates"].items():
            lines.append(f"  - {status}: survival_rate={rates['survival_rate']}, falsification_rate={rates['falsification_rate']}")
        lines.append("")

    # Convergence review
    cv = ctx["convergence_review_summary"]
    if cv:
        lines.append("## Convergence Review Summary")
        lines.append("")
        lines.append(f"- Total convergences: {cv['total_convergences']}")
        lines.append(f"- Classified as real: {cv['classified_real']}")
        lines.append(f"- All have ≥3 competing hypotheses: {cv['all_have_3_hypotheses']}")
        lines.append("")

    # Compression ledger
    cl = ctx["compression_ledger"]
    if cl:
        lines.append("## SPRINT 71 Compression Ledger")
        lines.append("")
        lines.append("| Transformation | Input → Output | Ratio | Info Loss % |")
        lines.append("|---------------|----------------|-------|-------------|")
        for entry in cl:
            lines.append(f"| {entry['transformation']} | {entry['input_count']} → {entry['output_count']} | {entry['compression_ratio']} | {entry['information_loss_pct']}% |")
        lines.append("")

    # Git history
    gh = ctx["git_recent_commits"]
    lines.append("## Recent Git History")
    lines.append("")
    for c in gh:
        lines.append(f"- `{c['hash']}` — {c['message']}")
    lines.append("")

    # Recent artifacts
    ra = ctx["recent_artifacts"]
    lines.append("## Recent Artifacts")
    lines.append("")
    for a in ra:
        lines.append(f"- `{a['file']}` ({a['size']} bytes)")
    lines.append("")

    lines.append("---")
    lines.append("")
    lines.append("> This Context Pack is compiled automatically from existing project artifacts.")
    lines.append("> No new entities, schemas, or graphs are created. All data is OBSERVED or DERIVED from source files.")
    lines.append("")

    return "\n".join(lines)


def main():
    ctx = compile_context_pack()

    output_dir = PROJECT_ROOT / "artifacts" / "context_pack"
    output_dir.mkdir(parents=True, exist_ok=True)

    # Write JSON
    json_path = output_dir / "current_state.json"
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(ctx, f, indent=2, ensure_ascii=False, default=str)

    # Write Markdown
    md = render_markdown(ctx)
    md_path = output_dir / "current_state.md"
    with open(md_path, "w", encoding="utf-8") as f:
        f.write(md)

    print("=" * 60)
    print("SPRINT 72 — Context Pack Compiler")
    print("=" * 60)
    print(f"  Claims: {ctx['knowledge_registry']['total_claims']}")
    print(f"  Findings: {ctx['knowledge_registry']['total_findings']}")
    print(f"  Questions: {ctx['knowledge_registry']['total_questions']}")
    print(f"  Trajectory nodes: {ctx['trajectory_data']['nodes']}")
    print(f"  Trajectory edges: {ctx['trajectory_data']['edges']}")
    print(f"  Git commits: {len(ctx['git_recent_commits'])}")
    print(f"  Recent artifacts: {len(ctx['recent_artifacts'])}")
    print()
    print(f"  JSON: {json_path}")
    print(f"  MD:   {md_path}")
    print("=" * 60)


if __name__ == "__main__":
    main()
