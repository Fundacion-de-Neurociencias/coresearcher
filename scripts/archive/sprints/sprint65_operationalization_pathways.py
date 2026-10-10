#!/usr/bin/env python3
"""
SPRINT 65 — Operationalization Pathways

Mejoras sobre SPRINT 64R:
1. Criterios explícitos para Ontological Status
2. false_negative_risk como métrica graduada (LOW/MEDIUM/HIGH/CRITICAL)
3. Pathways: qué transformaciones convertirían UNOPERATIONALIZED → PARTIALLY_OPERATIONAL?

Pregunta central:
  Qué procedimiento permitiría operacionalizar una entidad
  actualmente no operacionalizada?

Entregable: artifacts/operationalization_pathways.json
"""
import sys
import json
from pathlib import Path
from datetime import datetime, timezone

project_root = Path(__file__).resolve().parent.parent


# ------------------------------------------------------------------
# Mejora 1: Criterios explícitos para Ontological Status
# ------------------------------------------------------------------

ONTOLOGICAL_CRITERIA = {
    "ESTABLISHED": {
        "rule": (
            "La entidad es aceptada como real por la comunidad científica "
            "relevante. Existen referencias canónicas (textbooks, Nobel prizes, "
            "consenso filosófico) que la tratan como objeto legítimo."
        ),
        "required_evidence": [
            "Al menos una referencia canónica que la trata como real",
            "Uso extendido en literatura científica revisada por pares",
            "No existe debate activo sobre su existencia (solo sobre sus propiedades)",
        ],
    },
    "PLAUSIBLE": {
        "rule": (
            "La entidad es argumentable pero debatida. Existen defensores "
            "y críticos. Su estatus ontológico no está resuelto."
        ),
        "required_evidence": [
            "Al menos un argumento serio a favor de su existencia",
            "Debate activo en la literatura",
            "No hay consenso pero hay uso productivo",
        ],
    },
    "UNKNOWN": {
        "rule": (
            "No sabemos si la entidad existe independientemente de nuestra "
            "capacidad de medirla. No hay evidencia suficiente ni a favor ni en contra."
        ),
        "required_evidence": [
            "No hay referencias canónicas que la traten como real",
            "No hay debate activo (porque no se ha planteado la pregunta)",
            "Su existencia depende de supuestos no verificados",
        ],
    },
    "QUESTIONED": {
        "rule": (
            "Evidencia sugiere que la entidad podría no existir como categoría "
            "natural. Ha sido falsada o abandonada."
        ),
        "required_evidence": [
            "Evidencia de falsación o abandono",
            "Referencias que cuestionan su existencia",
        ],
    },
}


# ------------------------------------------------------------------
# Mejora 2: false_negative_risk como métrica graduada
# ------------------------------------------------------------------

def calculate_fnr_level(ontological_status, operational_status, observability, has_counterexample):
    """
    Calcula el nivel de false_negative_risk.

    CRITICAL: Entidad ESTABLISHED con UNOPERATIONALIZED + NONE + contraejemplos
    HIGH: Entidad PLAUSIBLE con UNOPERATIONALIZED + NONE
    MEDIUM: Entidad PLAUSIBLE/UNKNOWN con NOT_YET_OPERATIONAL + INDIRECT
    LOW: Entidad ESTABLISHED con PARTIALLY_OPERATIONAL
    NONE: Entidad OPERATIONAL con DIRECT
    """
    if operational_status == "OPERATIONAL" and observability == "DIRECT":
        return "NONE"
    if ontological_status == "ESTABLISHED" and operational_status == "UNOPERATIONALIZED" and has_counterexample:
        return "CRITICAL"
    if ontological_status in ("ESTABLISHED", "PLAUSIBLE") and operational_status == "UNOPERATIONALIZED":
        return "HIGH"
    if ontological_status in ("PLAUSIBLE", "UNKNOWN") and operational_status == "NOT_YET_OPERATIONAL":
        return "MEDIUM"
    if operational_status == "PARTIALLY_OPERATIONAL":
        return "LOW"
    return "LOW"


# ------------------------------------------------------------------
# Mejora 3: Operationalization Pathways
# ------------------------------------------------------------------

PATHWAYS = [
    {
        "entity": "Hypothesis",
        "current_status": "UNOPERATIONALIZED",
        "ontological_status": "ESTABLISHED",
        "fnr_level": "CRITICAL",
        "fnr_rationale": (
            "Las hypothesis son entidades metodológicas establecidas. "
            "Evaluarlas por observabilidad es un error categorial. "
            "Su función es generar predicciones falsables, no ser observables."
        ),
        "ontological_criteria_applied": (
            "ESTABLISHED porque: (1) Popper, Lakatos, Kuhn tratan las hypothesis "
            "como entidades metodológicas reales. (2) Uso extendido en toda la "
            "literatura científica. (3) No hay debate sobre si las hypothesis "
            "'existen' — solo sobre cuáles son correctas."
        ),
        "pathway_to_partially_operational": {
            "step_1": "Definir firma observacional: qué observaciones distinguirían una buena hypothesis de una mala?",
            "step_2": "Definir métrica de falsabilidad: qué proporción de predicciones son falsables?",
            "step_3": "Definir métrica de novedad: la hypothesis predice algo que no se sabía?",
            "required_observables": [
                "Predicciones generadas por la hypothesis",
                "Evidencia que falsaría cada predicción",
                "Evidencia que confirmaría cada predicción",
            ],
            "estimated_difficulty": "HIGH — requiere definir calidad de hypothesis de forma reproducible",
        },
    },
    {
        "entity": "Theory",
        "current_status": "UNOPERATIONALIZED",
        "ontological_status": "ESTABLISHED",
        "fnr_level": "CRITICAL",
        "fnr_rationale": (
            "Las teorías científicas son entidades metodológicas establecidas. "
            "La teoría de la evolución no es observable. La teoría de la relatividad "
            "no es observable. Pero generan predicciones falsables."
        ),
        "ontological_criteria_applied": (
            "ESTABLISHED porque: (1) Popper, Lakatos, Kuhn tratan las teorías "
            "como entidades metodológicas reales. (2) Toda la ciencia se basa "
            "en teorías. (3) No hay debate sobre si las teorías 'existen' — "
            "solo sobre cuáles son correctas."
        ),
        "pathway_to_partially_operational": {
            "step_1": "Definir predicciones derivables: qué predice la teoría?",
            "step_2": "Definir coherencia interna: las predicciones son lógicamente consistentes?",
            "step_3": "Definir poder explicativo: cuántos fenómenos explica?",
            "required_observables": [
                "Conjunto de predicciones derivadas de la teoría",
                "Evidencia que falsaría cada predicción",
                "Conteo de fenómenos explicados",
            ],
            "estimated_difficulty": "HIGH — requiere definir estructura teórica de forma reproducible",
        },
    },
    {
        "entity": "Explanation",
        "current_status": "UNOPERATIONALIZED",
        "ontological_status": "PLAUSIBLE",
        "fnr_level": "HIGH",
        "fnr_rationale": (
            "Las explicaciones existen como construcciones cognitivas. "
            "La ciencia entera se basa en explicaciones. El problema es "
            "que CoResearcher no sabe medirlas, no que no existan."
        ),
        "ontological_criteria_applied": (
            "PLAUSIBLE porque: (1) Salmon, Woodward argumentan que las explicaciones "
            "son entidades reales. (2) Uso extendido en ciencia. (3) Pero hay debate "
            "activo sobre qué constituye una explicación (DN model, causal, unification)."
        ),
        "pathway_to_partially_operational": {
            "step_1": "Definir estructura causal mínima: qué componentes tiene una explicación?",
            "step_2": "Definir métrica de completitud: la explicación cubre todos los factores relevantes?",
            "step_3": "Definir métrica de parsimonia: la explicación es la más simple posible?",
            "required_observables": [
                "Componentes causales identificados en la explicación",
                "Factores cubiertos vs no cubiertos",
                "Complejidad de la explicación",
            ],
            "estimated_difficulty": "MEDIUM — requiere estructurar texto explicativo",
        },
    },
    {
        "entity": "Paradigm",
        "current_status": "UNOPERATIONALIZED",
        "ontological_status": "UNKNOWN",
        "fnr_level": "HIGH",
        "fnr_rationale": (
            "Kuhn argumentó que los paradigmas existen como marcos compartidos. "
            "Pero su estatus ontológico es debatido."
        ),
        "ontological_criteria_applied": (
            "UNKNOWN porque: (1) Kuhn argumenta su existencia pero no hay consenso. "
            "(2) Debate activo sobre si los paradigmas son reales o heurísticas. "
            "(3) No hay referencias canónicas fuera de Kuhn que los traten como reales."
        ),
        "pathway_to_partially_operational": {
            "step_1": "Definir indicadores observables: qué señales indicarían un paradigma?",
            "step_2": "Definir métrica de shared assumptions: cuántos supuestos comparten los actores?",
            "step_3": "Definir métrica de estabilidad temporal: el paradigma persiste en el tiempo?",
            "required_observables": [
                "Supuestos compartidos entre actores",
                "Persistencia temporal de supuestos",
                "Cambios de paradigma identificables",
            ],
            "estimated_difficulty": "VERY HIGH — requiere análisis semántico profundo",
        },
    },
    {
        "entity": "Restriction",
        "current_status": "NOT_YET_OPERATIONAL",
        "ontological_status": "UNKNOWN",
        "fnr_level": "MEDIUM",
        "fnr_rationale": (
            "Podría existir como variable latente real, pero no ha sido observada "
            "directamente. Similar al gen en 1850."
        ),
        "ontological_criteria_applied": (
            "UNKNOWN porque: (1) No hay referencias canónicas que traten 'constraint "
            "compartida' como entidad científica establecida. (2) Es un concepto "
            "introducido por CoResearcher. (3) Su existencia depende de que las "
            "convergences reflejen barreras reales."
        ),
        "pathway_to_partially_operational": {
            "step_1": "Mejorar detector de convergences (FPR < 20%)",
            "step_2": "Validar hypothesis de constraint contra código fuente",
            "step_3": "Medir κ con revisores humanos reales (κ ≥ 0.4)",
            "required_observables": [
                "Convergencias validadas como reales (no sintéticas)",
                "Restricciones verificadas contra código",
                "Acuerdo interobservador ≥ 0.4",
            ],
            "estimated_difficulty": "MEDIUM — el detector existe, necesita refinamiento",
        },
    },
    {
        "entity": "Mechanism",
        "current_status": "NOT_YET_OPERATIONAL",
        "ontological_status": "PLAUSIBLE",
        "fnr_level": "MEDIUM",
        "fnr_rationale": (
            "Los mecanismos causales son entidades centrales en filosofía "
            "de la ciencia (Salmon, Woodward)."
        ),
        "ontological_criteria_applied": (
            "PLAUSIBLE porque: (1) Salmon y Woodward argumentan que los mecanismos "
            "son reales. (2) Uso extendido en biología, medicina, ciencias sociales. "
            "(3) Pero hay debate sobre qué constituye un mecanismo."
        ),
        "pathway_to_partially_operational": {
            "step_1": "Definir componentes del mecanismo: qué partes lo componen?",
            "step_2": "Definir conexiones causales: cómo se relacionan las partes?",
            "step_3": "Definir métrica de completitud: el mecanismo explica todo el fenómeno?",
            "required_observables": [
                "Componentes identificados del mecanismo",
                "Conexiones causales entre componentes",
                "Cobertura del fenómeno explicado",
            ],
            "estimated_difficulty": "HIGH — requiere análisis causal profundo",
        },
    },
]


def main():
    print("=" * 70)
    print("SPRINT 65 — Operationalization Pathways")
    print("=" * 70)
    print("Question: Qué transformaciones convertirían UNOPERATIONALIZED → PARTIALLY_OPERATIONAL?")
    print()

    # Mostrar criterios ontológicos
    print("[Criterios Ontológicos]")
    for status, criteria in ONTOLOGICAL_CRITERIA.items():
        print(f"  {status}: {criteria['rule'][:70]}...")
    print()

    # Mostrar pathways
    print("[Pathways]")
    print(f"{'Entity':<20} {'Current':<25} {'Ont':<15} {'FNR':<10} {'Difficulty':<15}")
    print(f"{'-'*20} {'-'*25} {'-'*15} {'-'*10} {'-'*15}")

    for p in PATHWAYS:
        difficulty = p["pathway_to_partially_operational"]["estimated_difficulty"]
        print(f"{p['entity']:<20} "
              f"{p['current_status']:<25} "
              f"{p['ontological_status']:<15} "
              f"{p['fnr_level']:<10} "
              f"{difficulty:<15}")

    # Resumen FNR
    print()
    fnr_counts = {}
    for p in PATHWAYS:
        level = p["fnr_level"]
        fnr_counts[level] = fnr_counts.get(level, 0) + 1

    print("[False Negative Risk Distribution]")
    for level in ["CRITICAL", "HIGH", "MEDIUM", "LOW", "NONE"]:
        count = fnr_counts.get(level, 0)
        if count > 0:
            print(f"  {level}: {count}")

    # Crear reporte
    report = {
        "report_id": f"OPPATH-{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S')}",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "sprint": "SPRINT 65 — Operationalization Pathways",
        "objective": (
            "Qué transformaciones serían necesarias para convertir cada "
            "entidad UNOPERATIONALIZED en PARTIALLY_OPERATIONAL?"
        ),
        "improvements_over_64r": {
            "1_ontological_criteria": (
                "Criterios explícitos y reproducibles para asignar "
                "ESTABLISHED / PLAUSIBLE / UNKNOWN / QUESTIONED"
            ),
            "2_graded_fnr": (
                "false_negative_risk ahora es métrica graduada: "
                "NONE / LOW / MEDIUM / HIGH / CRITICAL"
            ),
            "3_pathways": (
                "Para cada entidad UNOPERATIONALIZED, se define "
                "el pathway concreto hacia PARTIALLY_OPERATIONAL"
            ),
        },
        "ontological_criteria": ONTOLOGICAL_CRITERIA,
        "fnr_scale": {
            "NONE": "Entidad OPERATIONAL con DIRECT observability",
            "LOW": "Entidad PARTIALLY_OPERATIONAL",
            "MEDIUM": "Entidad PLAUSIBLE/UNKNOWN con NOT_YET_OPERATIONAL + INDIRECT",
            "HIGH": "Entidad PLAUSIBLE/ESTABLISHED con UNOPERATIONALIZED + NONE",
            "CRITICAL": "Entidad ESTABLISHED con UNOPERATIONALIZED + NONE + contraejemplos históricos",
        },
        "pathways": PATHWAYS,
        "fnr_distribution": fnr_counts,
        "key_finding": (
            "Las entidades CRITICAL (Hypothesis, Theory) no necesitan "
            "mejor observabilidad — necesitan mejor instrumentación metodológica. "
            "Su función no es ser observables sino ser falsables. "
            "El pathway correcto es definir firmas observacionales de sus predicciones, "
            "no intentar observarlas directamente."
        ),
        "paradigm_shift": (
            "Antes: 'No lo puedo medir → No existe'. "
            "Ahora: 'No lo puedo medir → No sé si existe → Qué instrumentación lo haría medible?'"
        ),
        "epistemic_note": (
            "Este sprint NO genera hypothesis. NO reactiva EHG. "
            "Solo define pathways de operacionalización. "
            "Cada pathway es un plan, no una implementación."
        ),
    }

    # Guardar
    output_path = Path("artifacts/operationalization_pathways.json")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, ensure_ascii=False, default=str)

    print()
    print("=" * 70)
    print(f"Output: {output_path}")
    print()
    print("KEY FINDING: Las entidades CRITICAL no necesitan observabilidad.")
    print("             Necesitan instrumentación metodológica.")
    print("             Su función es ser falsables, no observables.")
    print("=" * 70)

    return 0


if __name__ == "__main__":
    sys.exit(main())