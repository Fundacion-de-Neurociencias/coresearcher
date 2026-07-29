import csv, json, statistics
from pathlib import Path

raw = Path("artifacts/cross_repo_metrics.json").read_text(encoding="utf-8")
records = json.loads(raw)

EXPECTED = {
    "A_frameworks_ia": ["langchain-ai/langgraph","langchain-ai/langchain","run-llama/LlamaIndex","deepset-ai/haystack"],
    "B_proyectos_cientificos": ["scikit-learn/scikit-learn","pytorch/pytorch","jax-ml/jax","nilearn/nilearn"],
    "C_bibliotecas_pequenas": ["pallets/flask","psf/requests","pallets/click","marshmallow-code/marshmallow"],
    "D_archivados": ["google/guetzli","esimov/caire","request/request","bitly/segment"],
    "E_baja_actividad": ["tj/commander.js","substack/gray-matter","pallets/itsdangerous","jashkenas/underscore"],
}

seen = {r["repo"] for r in records}
flat = []
for cat, repos in EXPECTED.items():
    for repo in repos:
        if repo in seen:
            base = next(r for r in records if r["repo"] == repo)
            total = base.get("total_claims", 0)
            observable = base.get("observable_claims", 0)
            derivable = base.get("derivable_claims", 0)
            inferred = base.get("inferred_claims", 0)
            unknown = base.get("unknown_claims", 0)
            obs_r = base.get("observable_ratio", 0.0)
            cov_r = base.get("evidence_coverage", 0.0)
            audit = base.get("auditability_score", 0.0)
            unk_r = (unknown / total) if total else 0.0
            ft = "OK"
        else:
            total = observable = derivable = inferred = unknown = 0
            obs_r = cov_r = audit = unk_r = 0.0
            ft = "RATE_LIMITED"
        flat.append({
            "repo": repo,
            "category": cat,
            "stars": 0,
            "issues": 0,
            "prs": 0,
            "claims": total,
            "observable_ratio": round(obs_r, 4),
            "evidence_coverage": round(cov_r, 4),
            "auditability_score": round(audit, 4),
            "unknown_ratio": round(unk_r, 4),
            "failure_type": ft,
        })

fieldnames = ["repo","stars","issues","prs","claims","observable_ratio","evidence_coverage","auditability_score","unknown_ratio","failure_type"]
with open("artifacts/cross_repo_20_benchmark.csv", "w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=fieldnames)
    w.writeheader()
    for r in flat:
        w.writerow({k: r.get(k, "") for k in fieldnames})

metrics_keys = ["observable_ratio","evidence_coverage","auditability_score","unknown_ratio","claims"]
stats = {}
for key in metrics_keys:
    values = [r[key] for r in flat]
    if values:
        stats[key] = {"mean": round(statistics.mean(values), 4), "median": round(statistics.median(values), 4), "std": round(statistics.stdev(values), 4) if len(values) > 1 else 0.0, "min": round(min(values), 4), "max": round(max(values), 4)}
    else:
        stats[key] = {"mean": 0.0, "median": 0.0, "std": 0.0, "min": 0.0, "max": 0.0}
with open("artifacts/stability_metrics_20repos.json", "w", encoding="utf-8") as f:
    json.dump(stats, f, indent=2)

failed = [r for r in flat if r["auditability_score"] < 0.90 or r["claims"] == 0 or r["evidence_coverage"] < 0.50]
lines = ["# Sprint 59C --- Failure Taxonomy (Real Data)", "", "Repositorios excluidos o en riesgo por:", "- `auditability_score < 0.90`", "- `claims == 0`", "- `evidence_coverage < 0.50`", "", "---", ""]
if not failed:
    lines.append("No se identificaron repositorios que cumplan los criterios de fallo.")
else:
    for r in failed:
        lines.append(f"## {r['repo']}")
        lines.append("")
        lines.append(f"- **categoría**: {r['category']}")
        lines.append(f"- **stars**: {r['stars']}")
        lines.append(f"- **issues**: {r['issues']}")
        lines.append(f"- **prs**: {r['prs']}")
        lines.append(f"- **claims**: {r['claims']}")
        lines.append(f"- **observable_ratio**: {r['observable_ratio']}")
        lines.append(f"- **evidence_coverage**: {r['evidence_coverage']}")
        lines.append(f"- **auditability_score**: {r['auditability_score']}")
        lines.append(f"- **unknown_ratio**: {r['unknown_ratio']}")
        lines.append(f"- **failure_type**: {r['failure_type']}")
        lines.append("")
        lines.append("---")
        lines.append("")
with open("artifacts/failure_taxonomy_real.md", "w", encoding="utf-8") as f:
    f.write("\n".join(lines))
print("OK", len(flat))

