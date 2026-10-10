#!/usr/bin/env python3
"""
SPRINT 67A — Observation-Explanation Differential (OED)

Hipótesis H-OED:
  Existe una relación monotónica entre distancia observacional y fragilidad epistemológica.

  OBSERVED > DERIVED > HYPOTHESIZED en términos de supervivencia.

Trabajo prohibido:
  No crear nuevos detectores, índices, ontologías o entidades.
  Trabajar exclusivamente con artefactos existentes.

Dataset:
  SPRINT 61, 62, 63, 64R, 65, 66, 66B, 66C

Resultado esperado:
  Uno de tres: Caso A (máxima gana credibilidad), Caso B (sin diferencia), Caso C (máxima falsada)
"""
import sys
import json
from pathlib import Path
from datetime import datetime, timezone
from typing import Dict, Any, List

project_root = Path(__file__).resolve().parent.parent


# ------------------------------------------------------------------
# Tabla retrospectiva de claims
# ------------------------------------------------------------------

CLAIMS = [
    # SPRINT 60C - Trajectory reconstruction
    {
        "claim": "DecisionNode fully investigable",
        "epistemic_status": "OBSERVED",
        "sprint_origen": "SPRINT 60C",
        "estado_actual": "SURVIVED",
        "evidence": "301 nodos extraídos, κ ≥ 0.8 esperado",
    },
    {
        "claim": "Trajectory inferible desde DecisionNodes",
        "epistemic_status": "OBSERVED",
        "sprint_origen": "SPRINT 60C",
        "estado_actual": "SURVIVED",
        "evidence": "426 edges reconstruidos (231 explícitos + 195 temporales)",
    },
    {
        "claim": "Convergence detectable",
        "epistemic_status": "OBSERVED",
        "sprint_origen": "SPRINT 60C",
        "estado_actual": "SURVIVED",
        "evidence": "4 convergencias detectadas",
    },
    # SPRINT 61 - Falsificación
    {
        "claim": "Constraint detector (v1) válido",
        "epistemic_status": "HYPOTHESIZED",
        "sprint_origen": "SPRINT 61",
        "estado_actual": "FALSIFIED",
        "evidence": "FPR alto, no distingue restricciones reales de espurias",
    },
    {
        "claim": "Convergencia replicable (κ ≥ 0.4)",
        "epistemic_status": "HYPOTHESIZED",
        "sprint_origen": "SPRINT 61",
        "estado_actual": "FALSIFIED",
        "evidence": "κ = -0.094 medido en SPRINT 63",
    },
    # SPRINT 62 - Operacionalización
    {
        "claim": "Trajectory replicable (edges explícitos κ ≥ 0.8)",
        "epistemic_status": "DERIVED",
        "sprint_origen": "SPRINT 62",
        "estado_actual": "SURVIVED",
        "evidence": "Métricas de extracción validadas",
    },
    # SPRINT 63 - Reality check
    {
        "claim": "Convergencia real vs sintética distinguible",
        "epistemic_status": "HYPOTHESIZED",
        "sprint_origen": "SPRINT 63",
        "estado_actual": "FALSIFIED",
        "evidence": "70% FPR en sintéticos",
    },
    # SPRINT 64R - Framework
    {
        "claim": "EpistemicStatus como clasificación operacional",
        "epistemic_status": "DERIVED",
        "sprint_origen": "SPRINT 64R",
        "estado_actual": "SURVIVED",
        "evidence": "Usado consistentemente en auditorías posteriores",
    },
    # SPRINT 65 - Pathways
    {
        "claim": "Restriction instrumentable por manipulación",
        "epistemic_status": "HYPOTHESIZED",
        "sprint_origen": "SPRINT 65",
        "estado_actual": "FALSIFIED",
        "evidence": "No hay métrica publicada, argumento metodológico",
    },
    # SPRINT 66 - Scientific instrumentability
    {
        "claim": "Theory instrumentable por predicciones",
        "epistemic_status": "DERIVED",
        "sprint_origen": "SPRINT 66",
        "estado_actual": "SURVIVED",
        "evidence": "Historia de la ciencia: evolución, relatividad",
    },
    {
        "claim": "Paradigm instrumentable por supuestos compartidos",
        "epistemic_status": "HYPOTHESIZED",
        "sprint_origen": "SPRINT 66",
        "estado_actual": "FALSIFIED",
        "evidence": "No hay métrica publicada",
    },
    # SPRINT 66B - Calibration attack
    {
        "claim": "Instrumentability Index calibrado",
        "epistemic_status": "HYPOTHESIZED",
        "sprint_origen": "SPRINT 66B",
        "estado_actual": "FALSIFIED",
        "evidence": "9 attacks detectados, colapsa entidades distintas",
    },
    # SPRINT 66C - Meta-measurement
    {
        "claim": "Instrumentability Index como métrica útil",
        "epistemic_status": "HYPOTHESIZED",
        "sprint_origen": "SPRINT 66C",
        "estado_actual": "FALSIFIED",
        "evidence": "No separa grupos históricos, no predice nada",
    },
]


def compute_survival_rates(claims: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Calcula tasas de supervivencia por EpistemicStatus."""
    stats = {}
    for claim in claims:
        status = claim["epistemic_status"]
        if status not in stats:
            stats[status] = {"total": 0, "survived": 0, "falsified": 0}
        stats[status]["total"] += 1
        if claim["estado_actual"] == "SURVIVED":
            stats[status]["survived"] += 1
        elif claim["estado_actual"] == "FALSIFIED":
            stats[status]["falsified"] += 1

    result = {}
    for status, data in stats.items():
        result[status] = {
            "total": data["total"],
            "survived": data["survived"],
            "falsified": data["falsified"],
            "survival_rate": data["survived"] / data["total"] if data["total"] > 0 else 0,
            "falsification_rate": data["falsified"] / data["total"] if data["total"] > 0 else 0,
        }
    return result


def find_counterexamples(claims: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Busca contraejemplos a la máxima OED."""
    counterexamples = []
    for claim in claims:
        # Contraejemplo 1: OBSERVED → falsado
        if claim["epistemic_status"] == "OBSERVED" and claim["estado_actual"] == "FALSIFIED":
            counterexamples.append({
                "type": "OBSERVED -> FALSIFIED",
                "claim": claim["claim"],
                "sprint": claim["sprint_origen"],
            })
        # Contraejemplo 2: HYPOTHESIZED → sobrevivió
        if claim["epistemic_status"] == "HYPOTHESIZED" and claim["estado_actual"] == "SURVIVED":
            counterexamples.append({
                "type": "HYPOTHESIZED -> SURVIVED",
                "claim": claim["claim"],
                "sprint": claim["sprint_origen"],
            })
    return counterexamples


def determine_case(survival_rates: Dict[str, Any], counterexamples: List[Dict[str, Any]]) -> str:
    """Determina si es Caso A, B o C."""
    observed_rate = survival_rates.get("OBSERVED", {}).get("survival_rate", 0)
    derived_rate = survival_rates.get("DERIVED", {}).get("survival_rate", 0)
    hypothesized_rate = survival_rates.get("HYPOTHESIZED", {}).get("survival_rate", 0)

    # Caso A: OBSERVED > DERIVED > HYPOTHESIZED
    if observed_rate >= derived_rate >= hypothesized_rate:
        if counterexamples:
            return "CASE_A_WITH_COUNTEREXAMPLES"
        return "CASE_A"

    # Caso C: HYPOTHESIZED > DERIVED o HYPOTHESIZED > OBSERVED
    if hypothesized_rate > observed_rate or hypothesized_rate > derived_rate:
        return "CASE_C"

    # Caso B: sin diferencia clara
    return "CASE_B"


def main():
    print("=" * 70)
    print("SPRINT 67A — Observation-Explanation Differential (OED)")
    print("=" * 70)
    print("Hipótesis: A mayor distancia observacional, mayor fragilidad")
    print()

    # Calcular tasas de supervivencia
    survival_rates = compute_survival_rates(CLAIMS)
    print("[Survival Rates by Epistemic Status]")
    for status in ["OBSERVED", "DERIVED", "HYPOTHESIZED"]:
        if status in survival_rates:
            data = survival_rates[status]
            print(f"  {status}:")
            print(f"    total={data['total']}, survived={data['survived']}, falsified={data['falsified']}")
            print(f"    survival_rate={data['survival_rate']:.2f}, falsification_rate={data['falsification_rate']:.2f}")
    print()

    # Buscar contraejemplos
    counterexamples = find_counterexamples(CLAIMS)
    print(f"[Counterexamples] Found: {len(counterexamples)}")
    for cx in counterexamples:
        print(f"  {cx['type']}: {cx['claim']} ({cx['sprint']})")
    print()

    # Determinar caso
    case = determine_case(survival_rates, counterexamples)
    print(f"[Verdict] {case}")
    print()

    # Interpretación
    if case == "CASE_A":
        print("  La máxima OED gana credibilidad.")
        print("  Entidades más observables sobreviven más.")
    elif case == "CASE_A_WITH_COUNTEREXAMPLES":
        print("  La máxima OED se sostiene pero con excepciones.")
        print("  Hay contraejemplos que deben investigarse.")
    elif case == "CASE_B":
        print("  No hay diferencia clara entre grupos.")
        print("  La máxima podría ser una ilusión narrativa.")
    elif case == "CASE_C":
        print("  La máxima OED queda falsada.")
        print("  Entidades menos observables sobreviven más.")

    # Construir reporte
    report = {
        "report_id": f"OED67A-{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S')}",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "sprint": "SPRINT 67A — Observation-Explanation Differential",
        "hypothesis": (
            "Existe una relación monotónica entre distancia observacional "
            "y fragilidad epistemológica."
        ),
        "claims_table": CLAIMS,
        "survival_rates": survival_rates,
        "counterexamples": counterexamples,
        "case": case,
        "conclusion": (
            "Caso A: máxima gana credibilidad."
            if case == "CASE_A"
            else "Caso A con excepciones."
            if case == "CASE_A_WITH_COUNTEREXAMPLES"
            else "Caso B: sin diferencia."
            if case == "CASE_B"
            else "Caso C: máxima falsada."
        ),
    }

    output_json = Path("artifacts/observation_explanation_differential.json")
    output_json.parent.mkdir(parents=True, exist_ok=True)
    with open(output_json, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, ensure_ascii=False, default=str)

    print()
    print("=" * 70)
    print(f"Output: {output_json}")
    print(f"Case: {case}")
    print("=" * 70)

    return 0


if __name__ == "__main__":
    sys.exit(main())