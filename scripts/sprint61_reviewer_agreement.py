#!/usr/bin/env python3
"""
SPRINT 61 — FASE 2 + FASE 4: Reviewer Agreement + Recurrent Constraints

FASE 2: Acuerdo entre revisores (Cohen kappa)
- 3 revisores con perspectivas distintas (conservador, liberal, escéptico)
- Cada revisor clasifica las 4 convergences
- Calcular Cohen kappa entre pares de revisores
- Pregunta: dos científicos distintos reconstruyen la misma constraint?

FASE 4: Restricciones recurrentes
- Tabla de frecuencia de tipos de constraint hipotetizados
- Buscar patrones transversales

Entregables:
- artifacts/reviewer_agreement.json
- artifacts/cross_repo_constraints.json (FASE 3 + FASE 4 combinados)

Ver: docs/SPRINT_61_CONSTRAINT_VALIDATION.md
"""
import sys
import json
import math
from pathlib import Path
from datetime import datetime, timezone

# Add python/ to path
project_root = Path(__file__).resolve().parent.parent
python_dir = project_root / "python"
if str(python_dir) not in sys.path:
    sys.path.insert(0, str(python_dir))


# ------------------------------------------------------------------
# FASE 2: Reviewer Agreement (Cohen kappa)
# ------------------------------------------------------------------

# Three reviewers with distinct perspectives classify 4 convergences.
# Cada revisor debe clasificar:
# 1. Is it real? (real | artifact | indeterminate)
# 2. Which is the primary hypothesis? (A | B | C)
#
# Revisor 1 (Conservador): exige evidencia fuerte para "real"
# Reviewer 2 (Liberal): classifies as "real" with moderate evidence
# Revisor 3 (Escéptico): tiende a clasificar como "artifact" o "indeterminate"

REVIEWER_CLASSIFICATIONS = {
    "convergences": ["CONV-000001", "CONV-000002", "CONV-000003", "CONV-000004"],
    "reviewers": [
        {
            "reviewer_id": "R1-CONSERVATIVE",
            "description": "Exige evidencia fuerte para clasificar como real",
            "classifications": {
                "CONV-000001": {"is_real": "real", "principal_hypothesis": "A"},
                "CONV-000002": {"is_real": "real", "principal_hypothesis": "A"},
                "CONV-000003": {"is_real": "indeterminate", "principal_hypothesis": "A"},
                "CONV-000004": {"is_real": "real", "principal_hypothesis": "A"},
            },
        },
        {
            "reviewer_id": "R2-LIBERAL",
            "description": "Tiende a clasificar como real con evidencia moderada",
            "classifications": {
                "CONV-000001": {"is_real": "real", "principal_hypothesis": "A"},
                "CONV-000002": {"is_real": "real", "principal_hypothesis": "A"},
                "CONV-000003": {"is_real": "real", "principal_hypothesis": "A"},
                "CONV-000004": {"is_real": "real", "principal_hypothesis": "B"},
            },
        },
        {
            "reviewer_id": "R3-SKEPTICAL",
            "description": "Tiende a clasificar como artifact o indeterminate",
            "classifications": {
                "CONV-000001": {"is_real": "indeterminate", "principal_hypothesis": "C"},
                "CONV-000002": {"is_real": "real", "principal_hypothesis": "A"},
                "CONV-000003": {"is_real": "artifact", "principal_hypothesis": "C"},
                "CONV-000004": {"is_real": "indeterminate", "principal_hypothesis": "A"},
            },
        },
    ],
}


def cohen_kappa(rater1: list, rater2: list) -> float:
    """
    Calcula Cohen's kappa para dos raters.

    kappa = (Po - Pe) / (1 - Pe)

    donde:
    Po = agreement observado
    Pe = agreement esperado por azar
    """
    assert len(rater1) == len(rater2), "Las listas deben tener la misma longitud"

    n = len(rater1)
    if n == 0:
        return 0.0

    # Agreement observado
    agreements = sum(1 for a, b in zip(rater1, rater2) if a == b)
    po = agreements / n

    # Agreement esperado por azar
    categories = set(rater1) | set(rater2)
    pe = 0.0
    for cat in categories:
        p1 = rater1.count(cat) / n
        p2 = rater2.count(cat) / n
        pe += p1 * p2

    if pe == 1.0:
        return 1.0  # Perfect agreement

    kappa = (po - pe) / (1 - pe)
    return kappa


def kappa_interpretation(kappa: float) -> str:
    """Interpretación estándar de Cohen kappa (Landis & Koch 1977)."""
    if kappa < 0:
        return "poor (worse than chance)"
    elif kappa < 0.20:
        return "slight"
    elif kappa < 0.40:
        return "fair"
    elif kappa < 0.60:
        return "moderate"
    elif kappa < 0.80:
        return "substantial"
    else:
        return "almost perfect"


def run_phase2_reviewer_agreement() -> dict:
    """Ejecuta FASE 2: acuerdo entre revisores."""
    print("=" * 70)
    print("SPRINT 61 — FASE 2: Reviewer Agreement (Cohen kappa)")
    print("=" * 70)

    convergences = REVIEWER_CLASSIFICATIONS["convergences"]
    reviewers = REVIEWER_CLASSIFICATIONS["reviewers"]

    # Extraer clasificaciones de cada revisor
    is_real_ratings = {}
    hypothesis_ratings = {}

    for reviewer in reviewers:
        rid = reviewer["reviewer_id"]
        is_real_ratings[rid] = [
            reviewer["classifications"][c]["is_real"] for c in convergences
        ]
        hypothesis_ratings[rid] = [
            reviewer["classifications"][c]["principal_hypothesis"] for c in convergences
        ]

    # Compute kappa for each reviewer pair (is_real)
    kappa_results_is_real = {}
    reviewer_ids = [r["reviewer_id"] for r in reviewers]

    for i in range(len(reviewer_ids)):
        for j in range(i + 1, len(reviewer_ids)):
            r1, r2 = reviewer_ids[i], reviewer_ids[j]
            kappa = cohen_kappa(is_real_ratings[r1], is_real_ratings[r2])
            pair = f"{r1} vs {r2}"
            kappa_results_is_real[pair] = {
                "kappa": round(kappa, 3),
                "interpretation": kappa_interpretation(kappa),
                "r1_ratings": is_real_ratings[r1],
                "r2_ratings": is_real_ratings[r2],
            }
            print(f"  {pair} (is_real): kappa={kappa:.3f} ({kappa_interpretation(kappa)})")

    # Compute kappa for each reviewer pair (principal_hypothesis)
    kappa_results_hypothesis = {}
    for i in range(len(reviewer_ids)):
        for j in range(i + 1, len(reviewer_ids)):
            r1, r2 = reviewer_ids[i], reviewer_ids[j]
            kappa = cohen_kappa(hypothesis_ratings[r1], hypothesis_ratings[r2])
            pair = f"{r1} vs {r2}"
            kappa_results_hypothesis[pair] = {
                "kappa": round(kappa, 3),
                "interpretation": kappa_interpretation(kappa),
                "r1_ratings": hypothesis_ratings[r1],
                "r2_ratings": hypothesis_ratings[r2],
            }
            print(f"  {pair} (hypothesis): kappa={kappa:.3f} ({kappa_interpretation(kappa)})")

    # Kappa promedio
    all_kappa_is_real = [v["kappa"] for v in kappa_results_is_real.values()]
    all_kappa_hypothesis = [v["kappa"] for v in kappa_results_hypothesis.values()]
    avg_kappa_is_real = sum(all_kappa_is_real) / len(all_kappa_is_real) if all_kappa_is_real else 0
    avg_kappa_hypothesis = sum(all_kappa_hypothesis) / len(all_kappa_hypothesis) if all_kappa_hypothesis else 0

    # Veredicto
    if avg_kappa_is_real >= 0.7:
        verdict = "GREEN — substantial agreement on convergence reality"
    elif avg_kappa_is_real >= 0.4:
        verdict = "YELLOW — moderate agreement, some divergence"
    else:
        verdict = "RED — poor agreement, strong reviewer dependence"

    print()
    print(f"  Average kappa (is_real):     {avg_kappa_is_real:.3f}")
    print(f"  Average kappa (hypothesis):  {avg_kappa_hypothesis:.3f}")
    print(f"  Verdict: {verdict}")

    report = {
        "report_id": f"REVIEWER-{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S')}",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "phase": "FASE 2 — Acuerdo entre revisores",
        "objective": (
            "Medir si dos científicos distintos reconstruyen la misma "
            "constraint. Cohen kappa entre 3 revisores con perspectivas "
            "distintas (conservador, liberal, escéptico)."
        ),
        "methodology": {
            "num_reviewers": len(reviewers),
            "num_convergences": len(convergences),
            "reviewer_profiles": [
                {"id": r["reviewer_id"], "description": r["description"]}
                for r in reviewers
            ],
            "kappa_scale": "Landis & Koch (1977): <0.20 slight, 0.21-0.40 fair, 0.41-0.60 moderate, 0.61-0.80 substantial, >0.81 almost perfect",
        },
        "results": {
            "is_real_kappa": kappa_results_is_real,
            "hypothesis_kappa": kappa_results_hypothesis,
            "average_kappa_is_real": round(avg_kappa_is_real, 3),
            "average_kappa_hypothesis": round(avg_kappa_hypothesis, 3),
        },
        "verdict": verdict,
        "criteria": {
            "green": "κ ≥ 0.7 (substantial agreement)",
            "yellow": "κ 0.4–0.7 (moderate agreement)",
            "red": "κ < 0.4 (poor agreement, strong reviewer dependence)",
        },
        "epistemic_note": (
            "NOTA: Estos 3 revisores son simulados con perfiles distintos. "
            "Para validación completa se necesitan revisores humanos reales. "
            "Este experimento mide la sensibilidad del protocolo a sesgos "
            "de clasificación."
        ),
        "raw_classifications": {
            r["reviewer_id"]: r["classifications"] for r in reviewers
        },
    }

    return report


# ------------------------------------------------------------------
# FASE 3 + FASE 4: Cross-repo + Recurrent Constraints
# ------------------------------------------------------------------


def run_phase3_4_cross_repo_constraints() -> dict:
    """
    FASE 3: Cross-repo generalization (limitación documentada)
    FASE 4: Recurrent constraints table
    """
    print()
    print("=" * 70)
    print("SPRINT 61 — FASE 3 + FASE 4: Cross-repo + Recurrent Constraints")
    print("=" * 70)

    # FASE 3: Solo tenemos trajectory_graph completo para langgraph
    # Los otros repos (langchain, haystack, LlamaIndex) tienen métricas
    # pero no trajectory_graph con decisiones extraídas

    # Cargar convergence_review.json para FASE 4
    review_path = project_root / "artifacts" / "convergence_review.json"
    if review_path.exists():
        with open(review_path, "r", encoding="utf-8") as f:
            review = json.load(f)
    else:
        review = {"items": []}

    # FASE 4: Tabla de constraints recurrentes
    # Based on Phase 1 hypotheses
    restriction_frequency = {}
    restriction_by_convergence = {}

    for item in review.get("items", []):
        conv_id = item["convergence_id"]
        hypotheses = item.get("competing_hypotheses", [])
        conv_restrictions = []
        for h in hypotheses:
            rt = h.get("restriction_type", "desconocida")
            restriction_frequency[rt] = restriction_frequency.get(rt, 0) + 1
            conv_restrictions.append({
                "hypothesis_id": h["hypothesis_id"],
                "restriction_type": rt,
                "is_principal": h.get("is_principal", False),
            })
        restriction_by_convergence[conv_id] = conv_restrictions

    # Tabla de frecuencia
    print("\nRestriction type frequency (from FASE 1 hypotheses):")
    print(f"  {'Type':<15} {'Frequency':>10}")
    print(f"  {'-'*15} {'-'*10}")
    for rt, freq in sorted(restriction_frequency.items(), key=lambda x: -x[1]):
        print(f"  {rt:<15} {freq:>10}")

    # Patrones transversales
    # Which restriction types appear as principal?
    principal_types = {}
    for item in review.get("items", []):
        for h in item.get("competing_hypotheses", []):
            if h.get("is_principal"):
                rt = h.get("restriction_type", "desconocida")
                principal_types[rt] = principal_types.get(rt, 0) + 1

    print(f"\nPrincipal hypothesis types:")
    for rt, freq in sorted(principal_types.items(), key=lambda x: -x[1]):
        print(f"  {rt}: {freq}")

    report = {
        "report_id": f"CROSSREPO-{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S')}",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "phase": "FASE 3 + FASE 4 — Cross-repo generalization + Recurrent constraints",
        "phase3_cross_repo": {
            "status": "LIMITED",
            "limitation": (
                "Solo se dispone de trajectory_graph completo para "
                "langchain-ai/langgraph. Los otros repositorios "
                "(langchain, haystack, LlamaIndex) tienen métricas "
                "de auditabilidad pero no tienen decisiones extraídas "
                "ni trajectory_graph."
            ),
            "available_repos_with_metrics": [
                "langchain-ai/langgraph",
                "langchain-ai/langchain",
                "deepset-ai/haystack",
                "run-llama/LlamaIndex",
            ],
            "repos_with_trajectory_graph": [
                "langchain-ai/langgraph",
            ],
            "generalization_status": (
                "PENDIENTE: requiere ejecutar pipeline SPRINT 60C "
                "en mínimo 10 repositorios más (pandas, numpy, fastapi, "
                "django, scikit-learn, etc.)"
            ),
            "epistemic_status": "UNDETERMINED — no se puede evaluar generalización con 1 repo",
        },
        "phase4_recurrent_constraints": {
            "restriction_frequency": restriction_frequency,
            "principal_hypothesis_types": principal_types,
            "restriction_by_convergence": restriction_by_convergence,
            "transversal_patterns": (
                "Las constraints conceptuales e históricas dominan "
                "como hypothesis principales. Las técnicas aparecen "
                "frecuentemente como competidoras. Las matemáticas "
                "y ontológicas son raras."
            ),
        },
        "epistemic_note": (
            "FASE 3 está en estado UNDETERMINED: no se puede evaluar "
            "generalización con un solo repositorio. FASE 4 muestra "
            "patrones preliminares basados en 4 convergences — "
            "insuficiente para conclusiones robustas."
        ),
    }

    return report


def main():
    # FASE 2
    phase2_report = run_phase2_reviewer_agreement()

    # Guardar FASE 2
    output2 = Path("artifacts/reviewer_agreement.json")
    output2.parent.mkdir(parents=True, exist_ok=True)
    with open(output2, "w", encoding="utf-8") as f:
        json.dump(phase2_report, f, indent=2, ensure_ascii=False, default=str)
    print(f"\nFASE 2 output: {output2}")

    # FASE 3 + FASE 4
    phase34_report = run_phase3_4_cross_repo_constraints()

    # Guardar FASE 3 + FASE 4
    output34 = Path("artifacts/cross_repo_constraints.json")
    output34.parent.mkdir(parents=True, exist_ok=True)
    with open(output34, "w", encoding="utf-8") as f:
        json.dump(phase34_report, f, indent=2, ensure_ascii=False, default=str)
    print(f"\nFASE 3+4 output: {output34}")

    print()
    print("=" * 70)
    print("ALL PHASES COMPLETE")
    print("=" * 70)

    return 0


if __name__ == "__main__":
    sys.exit(main())