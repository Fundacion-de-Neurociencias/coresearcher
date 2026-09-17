#!/usr/bin/env python3
"""
SPRINT 64R — Operationalization Framework

Formalizar la distinción entre:
1. Existencia ontológica
2. Operacionalización
3. Observabilidad
4. Medición

Tarea 1: artifacts/operationalization_framework.md
Tarea 2: Matriz 4-dimensional (no puntuación única)
Tarea 3: Detectar false_negative_risk
Tarea 4: artifacts/operationalization_counterexamples.md

Pregunta científica:
  Are we measuring construct reality?
  o
  Are we merely measuring our current capacity to operationalize them?
"""
import sys
import json
from pathlib import Path
from datetime import datetime, timezone

project_root = Path(__file__).resolve().parent.parent


# ------------------------------------------------------------------
# Tarea 2: Matriz 4-dimensional (NO puntuación única)
# ------------------------------------------------------------------
# Cada entidad se evalúa en 4 dimensiones SEPARADAS:
# - ontological_status: UNKNOWN / PLAUSIBLE / ESTABLISHED / QUESTIONED
# - operational_status: OPERATIONAL / PARTIALLY_OPERATIONAL / NOT_YET_OPERATIONAL / UNOPERATIONALIZED
# - observability: DIRECT / INDIRECT / NONE
# - measurement: YES / PARTIAL / NO

ENTITIES_MATRIX = [
    {
        "entity": "DecisionNode",
        "ontological_status": "ESTABLISHED",
        "ontological_rationale": "Eventos verificables contra GitHub API. Existencia independiente de CoResearcher.",
        "operational_status": "OPERATIONAL",
        "operational_rationale": "301 nodos extraídos, auditabilidad 1.0",
        "observability": "DIRECT",
        "observability_rationale": "Visible en GitHub issues/PRs",
        "measurement": "YES",
        "measurement_rationale": "Métricas de precisión calculadas",
        "false_negative_risk": False,
    },
    {
        "entity": "Trajectory",
        "ontological_status": "PLAUSIBLE",
        "ontological_rationale": "Secuencias de decisiones existen como historial de cambios",
        "operational_status": "PARTIALLY_OPERATIONAL",
        "operational_rationale": "426 edges, pero 195 temporales son inferidos",
        "observability": "INDIRECT",
        "observability_rationale": "Edges explícitos son directos; temporales son inferidos",
        "measurement": "PARTIAL",
        "measurement_rationale": "Métricas parciales; edges temporales no validados",
        "false_negative_risk": False,
    },
    {
        "entity": "Convergence",
        "ontological_status": "PLAUSIBLE",
        "ontological_rationale": "Múltiples actores chocando contra la misma barrera es un fenómeno real",
        "operational_status": "PARTIALLY_OPERATIONAL",
        "operational_rationale": "4 detectadas, pero 70% FPR en sintéticos",
        "observability": "INDIRECT",
        "observability_rationale": "Inferida desde clustering de títulos, no observada directamente",
        "measurement": "PARTIAL",
        "measurement_rationale": "Detector funciona pero no distingue real de sintético",
        "false_negative_risk": False,
    },
    {
        "entity": "Restriction",
        "ontological_status": "UNKNOWN",
        "ontological_rationale": "Podría existir como variable latente real, pero no ha sido observada directamente. Similar al gen en 1850.",
        "operational_status": "NOT_YET_OPERATIONAL",
        "operational_rationale": "6/12 hypothesis operational, κ = -0.094",
        "observability": "NONE",
        "observability_rationale": "Solo observamos manifestaciones (convergences), no la constraint",
        "measurement": "NO",
        "measurement_rationale": "No hay métrica reproducible",
        "false_negative_risk": True,
        "false_negative_risk_rationale": (
            "Descartar 'restriction' por baja observabilidad sería como descartar "
            "'gen' en 1850. La constraint puede ser real pero no observable "
            "con las herramientas actuales."
        ),
    },
    {
        "entity": "Paradigm",
        "ontological_status": "UNKNOWN",
        "ontological_rationale": "Kuhn argumentó que los paradigmas existen como marcos compartidos. Pero su estatus ontológico es debatido.",
        "operational_status": "UNOPERATIONALIZED",
        "operational_rationale": "0 paradigm residues detectados. Sin criterios observables.",
        "observability": "NONE",
        "observability_rationale": "No observable desde commits o PRs",
        "measurement": "NO",
        "measurement_rationale": "No hay métrica",
        "false_negative_risk": True,
        "false_negative_risk_rationale": (
            "Descartar 'paradigm' por baja observabilidad ignora que Kuhn, Lakatos "
            "y Feyerabend argumentaron su existencia como marcos reales."
        ),
    },
    {
        "entity": "Hypothesis",
        "ontological_status": "ESTABLISHED",
        "ontological_rationale": "Las hypothesis son entidades metodológicas establecidas. Su función es generar predicciones falsables, no ser observables.",
        "operational_status": "UNOPERATIONALIZED",
        "operational_rationale": "EHG congelado. 0 hypothesis generadas.",
        "observability": "NONE",
        "observability_rationale": "Una hypothesis no es un objeto observable — es una propuesta metodológica",
        "measurement": "NO",
        "measurement_rationale": "No hay métrica de calidad de hypothesis",
        "false_negative_risk": True,
        "false_negative_risk_rationale": (
            "CRÍTICO: Evaluar 'hypothesis' por observabilidad es un error categorial. "
            "Una hypothesis no pretende ser observable. Pretende ser falsable. "
            "Descartarla por baja observabilidad es como descartar una ecuación "
            "por no tener color."
        ),
    },
    {
        "entity": "Epistemic Gap",
        "ontological_status": "ESTABLISHED",
        "ontological_rationale": "Regiones de ignorancia clasificable son entidades metodológicas válidas",
        "operational_status": "OPERATIONAL",
        "operational_rationale": "155 gaps detectados y clasificados A/B/C/D",
        "observability": "DIRECT",
        "observability_rationale": "Detectable desde señales heurísticas en datos",
        "measurement": "YES",
        "measurement_rationale": "Gap density, by_type, by_characterization",
        "false_negative_risk": False,
    },
    {
        "entity": "Explanation",
        "ontological_status": "PLAUSIBLE",
        "ontological_rationale": "Las explicaciones existen como construcciones cognitivas. Su estatus ontológico es debatido pero plausible.",
        "operational_status": "UNOPERATIONALIZED",
        "operational_rationale": "Aparecen en rationale fields pero nunca auditadas",
        "observability": "INDIRECT",
        "observability_rationale": "Visible en texto de rationale pero no estructurada",
        "measurement": "NO",
        "measurement_rationale": "No hay métrica de calidad explicativa",
        "false_negative_risk": True,
        "false_negative_risk_rationale": (
            "Descartar 'explanation' por baja medición ignora que la ciencia "
            "entera se basa en explicaciones. El problema es que CoResearcher "
            "no sabe medirlas, no que no existan."
        ),
    },
    {
        "entity": "Mechanism",
        "ontological_status": "PLAUSIBLE",
        "ontological_rationale": "Los mecanismos causales son entidades centrales en filosofía de la ciencia (Salmon, Woodward)",
        "operational_status": "NOT_YET_OPERATIONAL",
        "operational_rationale": "SPRINT 52 buscó mecanismos sin criterios formales",
        "observability": "INDIRECT",
        "observability_rationale": "Inferido desde patrones, no observado directamente",
        "measurement": "NO",
        "measurement_rationale": "No hay métrica reproducible",
        "false_negative_risk": True,
        "false_negative_risk_rationale": (
            "Descartar 'mechanism' por baja observabilidad ignora décadas "
            "de filosofía de la ciencia sobre mecanismos causales."
        ),
    },
    {
        "entity": "Theory",
        "ontological_status": "ESTABLISHED",
        "ontological_rationale": "Las teorías científicas son entidades metodológicas establecidas. Popper, Lakatos, Kuhn las tratan como reales.",
        "operational_status": "UNOPERATIONALIZED",
        "operational_rationale": "CoResearcher no genera teorías",
        "observability": "NONE",
        "observability_rationale": "Una teoría no es observable — es una estructura explicativa",
        "measurement": "NO",
        "measurement_rationale": "No hay métrica",
        "false_negative_risk": True,
        "false_negative_risk_rationale": (
            "CRÍTICO: Evaluar 'theory' por observabilidad es un error categorial. "
            "La teoría de la evolución no es observable. La teoría de la relatividad "
            "no es observable. Pero generan predicciones falsables. "
            "Descartarlas por baja observabilidad eliminaría gran parte de la ciencia."
        ),
    },
]


# ------------------------------------------------------------------
# Tarea 4: Contraejemplos
# ------------------------------------------------------------------

COUNTEREXAMPLES = [
    {
        "entity": "Gen",
        "year": 1865,
        "scientist": "Mendel",
        "observability_at_time": "NONE",
        "operational_status_at_time": "UNOPERATIONALIZED",
        "current_status": "ESTABLISHED — observable via DNA sequencing",
        "lesson": "Una entidad con observabilidad = 0 puede ser real. La observabilidad depende de la tecnología disponible, no de la ontología.",
    },
    {
        "entity": "Microbio",
        "year": 1670,
        "scientist": "Leeuwenhoek",
        "observability_at_time": "NONE (pre-microscopio)",
        "operational_status_at_time": "UNOPERATIONALIZED",
        "current_status": "ESTABLISHED — observable via microscopio",
        "lesson": "La falta de observabilidad era una limitación tecnológica, no ontológica. Los microbios existían antes de que los pudiéramos ver.",
    },
    {
        "entity": "Tectónica de placas",
        "year": 1912,
        "scientist": "Wegener",
        "observability_at_time": "INDIRECT (fósiles, costas)",
        "operational_status_at_time": "NOT_YET_OPERATIONAL",
        "current_status": "ESTABLISHED — observable via GPS y sismología",
        "lesson": "La deriva continental fue rechazada por falta de mecanismo observable. El mecanismo existía pero no podíamos medirlo.",
    },
    {
        "entity": "Ondas gravitacionales",
        "year": 1916,
        "scientist": "Einstein",
        "observability_at_time": "NONE",
        "operational_status_at_time": "UNOPERATIONALIZED",
        "current_status": "ESTABLISHED — observadas en 2015 (LIGO)",
        "lesson": "100 años entre predicción y observación. La entidad era real durante todo ese tiempo. La observabilidad era una limitación tecnológica.",
    },
    {
        "entity": "Neutrino",
        "year": 1930,
        "scientist": "Pauli",
        "observability_at_time": "NONE",
        "operational_status_at_time": "UNOPERATIONALIZED",
        "current_status": "ESTABLISHED — detectado en 1956 (Cowan-Reines)",
        "lesson": "Pauli propuso el neutrino para explicar la conservación de energía. No era observable. Era real. 26 años hasta detección.",
    },
    {
        "entity": "Campo magnético",
        "year": 1600,
        "scientist": "Gilbert",
        "observability_at_time": "INDIRECT (brújula)",
        "operational_status_at_time": "PARTIALLY_OPERATIONAL",
        "current_status": "ESTABLISHED — observable y medible",
        "lesson": "El campo magnético no es visible pero es real. Su observabilidad mejoró con la tecnología.",
    },
]


def main():
    print("=" * 70)
    print("SPRINT 64R — Operationalization Framework")
    print("=" * 70)
    print()

    # Tarea 1: Framework document
    print("[Tarea 1] Creating operationalization framework...")

    framework_md = """# Operationalization Framework — SPRINT 64R

**Fecha**: 2026-08-01
**Origen**: Corrección al salto inferencial detectado en SPRINT 64
**Objetivo**: Formalizar la distinción entre ontología, operacionalización, observabilidad y medición

---

## La pregunta científica

> Are we measuring construct reality?
> o
> Are we merely measuring our current capacity to operationalize them?

---

## 1. Ontological Status

**Pregunta**: La entidad podría existir independientemente de nuestra capacidad de medirla?

| Estado | Significado |
|--------|-------------|
| ESTABLISHED | Existencia aceptada por la comunidad científica |
| PLAUSIBLE | Existencia debatida pero argumentable |
| UNKNOWN | No sabemos si existe independientemente de nuestra medición |
| QUESTIONED | Evidencia sugiere que podría no existir como entidad |

**Ejemplos**:
- Gen (1850): UNKNOWN → ESTABLISHED (con DNA)
- Campo gravitatorio: ESTABLISHED
- Inteligencia: PLAUSIBLE (debate sobre qué es)
- Éter luminífero: QUESTIONED → falsado

---

## 2. Operational Status

**Pregunta**: CoResearcher dispone actualmente de un procedimiento reproducible para identificarla?

| Estado | Significado |
|--------|-------------|
| OPERATIONAL | Procedimiento reproducible validado |
| PARTIALLY_OPERATIONAL | Algunas dimensiones funcionan |
| NOT_YET_OPERATIONAL | Requiere formalización |
| UNOPERATIONALIZED | Sin procedimiento |

**CRÍTICO**: Este estado mide la capacidad de CoResearcher, NO la existencia de la entidad.

---

## 3. Observability

**Pregunta**: Existe una observación directa o indirecta?

| Estado | Significado |
|--------|-------------|
| DIRECT | Observable sin inferencia |
| INDIRECT | Observable via inferencia desde observables |
| NONE | No observable con tecnología actual |

**CRÍTICO**: Observabilidad baja ≠ inexistencia. Ver contraejemplos (gen, microbio, neutrino).

---

## 4. Measurement

**Pregunta**: Existe una métrica reproducible?

| Estado | Significado |
|--------|-------------|
| YES | Métrica reproducible validada |
| PARTIAL | Métrica parcial o no validada |
| NO | Sin métrica |

---

## 5. Regla fundamental

> NUNCA inferir inexistencia ontológica desde baja operacionalización.
> NUNCA inferir inexistencia ontológica desde baja observabilidad.
> NUNCA inferir inexistencia ontológica desde falta de medición.

Una entidad puede ser:
- Ontológicamente ESTABLISHED pero operacionalmente UNOPERATIONALIZED
- Ejemplo: "Theory" es ontológicamente establecida pero CoResearcher no sabe operacionalizarla

---

## 6. False Negative Risk

Una entidad tiene `false_negative_risk = True` cuando:
- Su baja puntuación en operacionalización/observabilidad podría llevar a descartarla
- Pero su estatus ontológico es ESTABLISHED o PLAUSIBLE
- Y existen contraejemplos históricos de entidades similares que resultaron ser reales

**Acción**: Las entidades con false_negative_risk deben tratarse como "requieren mejor instrumentación", no como "no existen".

---

*Este framework existe para que el error de SPRINT 64 no se repita.*
*Confundir operacionalización con ontología es el mismo error que confundir Chain of Thought con razonamiento.*
"""
    framework_path = Path("artifacts/operationalization_framework.md")
    framework_path.parent.mkdir(parents=True, exist_ok=True)
    with open(framework_path, "w", encoding="utf-8") as f:
        f.write(framework_md)
    print(f"  Created: {framework_path}")

    # Tarea 2: Matriz 4-dimensional
    print()
    print("[Tarea 2] Reevaluating entities with 4 separate dimensions...")

    print(f"\n{'Entity':<20} {'Ont':<15} {'Oper':<25} {'Obs':<10} {'Meas':<8} {'FNR':>4}")
    print(f"{'-'*20} {'-'*15} {'-'*25} {'-'*10} {'-'*8} {'-'*4}")

    for e in ENTITIES_MATRIX:
        fnr = "⚠️" if e["false_negative_risk"] else ""
        print(f"{e['entity']:<20} "
              f"{e['ontological_status']:<15} "
              f"{e['operational_status']:<25} "
              f"{e['observability']:<10} "
              f"{e['measurement']:<8} "
              f"{fnr:>4}")

    # Tarea 3: Detectar false negative risks
    print()
    print("[Tarea 3] Detecting false negative risks...")
    fnr_entities = [e for e in ENTITIES_MATRIX if e["false_negative_risk"]]
    print(f"  Entities with false_negative_risk: {len(fnr_entities)}")
    for e in fnr_entities:
        print(f"  ⚠️  {e['entity']}: {e['false_negative_risk_rationale'][:80]}...")

    # Tarea 4: Contraejemplos
    print()
    print("[Tarea 4] Creating counterexamples catalog...")

    counterexamples_md = """# Operationalization Counterexamples — SPRINT 64R

**Fecha**: 2026-08-01
**Objetivo**: Demostrar que observabilidad baja ≠ inexistencia

---

## Contraejemplos históricos

| Entidad | Año | Observabilidad inicial | Estado actual | Lección |
|---------|-----|----------------------|---------------|---------|
"""
    for ce in COUNTEREXAMPLES:
        counterexamples_md += (
            f"| {ce['entity']} | {ce['year']} | {ce['observability_at_time']} | "
            f"{ce['current_status']} | {ce['lesson'][:60]}... |\n"
        )

    counterexamples_md += """
---

## Lección fundamental

> La observabilidad depende de la tecnología disponible, no de la ontología.
> Una entidad puede existir durante décadas o siglos antes de ser observable.
> Descartar una entidad por baja observabilidad es cometer el error del gen en 1850.

---

## Aplicación a CoResearcher

Las siguientes entidades tienen false_negative_risk = True:

"""
    for e in fnr_entities:
        counterexamples_md += f"### {e['entity']}\n\n"
        counterexamples_md += f"- **Ontological Status**: {e['ontological_status']}\n"
        counterexamples_md += f"- **Operational Status**: {e['operational_status']}\n"
        counterexamples_md += f"- **Riesgo**: {e['false_negative_risk_rationale']}\n\n"

    counterexamples_md += """---

*Estos contraejemplos existen para recordar que nuestra incapacidad de medir no es evidencia de inexistencia.*
"""
    counterexamples_path = Path("artifacts/operationalization_counterexamples.md")
    with open(counterexamples_path, "w", encoding="utf-8") as f:
        f.write(counterexamples_md)
    print(f"  Created: {counterexamples_path}")

    # Crear reporte JSON
    report = {
        "report_id": f"OPFRAME-{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S')}",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "sprint": "SPRINT 64R — Operationalization Framework",
        "objective": (
            "Formalizar la distinción entre ontología, operacionalización, "
            "observabilidad y medición para evitar errores ontológicos."
        ),
        "scientific_question": (
            "Are we measuring construct reality? "
            "o estamos midiendo únicamente nuestra capacidad actual "
            "para operacionalizarlos?"
        ),
        "answer": (
            "Estamos midiendo nuestra capacidad actual para operacionalizarlos. "
            "La realidad ontológica de los constructos es una pregunta separada "
            "que no puede responderse solo desde la operacionalización."
        ),
        "tasks": {
            "task1_framework": str(framework_path),
            "task2_matrix": "4-dimensional evaluation (no single score)",
            "task3_false_negative_risk": f"{len(fnr_entities)} entities at risk",
            "task4_counterexamples": str(counterexamples_path),
        },
        "matrix": ENTITIES_MATRIX,
        "false_negative_risks": [
            {
                "entity": e["entity"],
                "ontological_status": e["ontological_status"],
                "operational_status": e["operational_status"],
                "rationale": e["false_negative_risk_rationale"],
            }
            for e in fnr_entities
        ],
        "counterexamples": COUNTEREXAMPLES,
        "key_rule": (
            "NUNCA inferir inexistencia ontológica desde baja operacionalización. "
            "NUNCA inferir inexistencia ontológica desde baja observabilidad. "
            "NUNCA inferir inexistencia ontológica desde falta de medición."
        ),
        "critical_entities": {
            "hypothesis": (
                "CRÍTICO: Evaluar 'hypothesis' por observabilidad es un error categorial. "
                "Una hypothesis no pretende ser observable. Pretende ser falsable."
            ),
            "theory": (
                "CRÍTICO: La teoría de la evolución no es observable. "
                "La teoría de la relatividad no es observable. "
                "Pero generan predicciones falsables."
            ),
        },
    }

    output_path = Path("artifacts/operationalization_framework.json")
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, ensure_ascii=False, default=str)

    print()
    print("=" * 70)
    print("DELIVERABLES")
    print("=" * 70)
    print(f"  {framework_path}")
    print(f"  {counterexamples_path}")
    print(f"  {output_path}")
    print()
    print(f"False negative risks: {len(fnr_entities)} entities")
    print(f"Counterexamples: {len(COUNTEREXAMPLES)} historical cases")
    print()
    print("ANSWER: Estamos midiendo nuestra capacidad actual para")
    print("        operacionalizarlos, NO la realidad de los constructos.")
    print("=" * 70)

    return 0


if __name__ == "__main__":
    sys.exit(main())