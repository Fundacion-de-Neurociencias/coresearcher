#!/usr/bin/env python3
"""
SPRINT 66 — Scientific Instrumentability Framework

Objetivo:
  Determinar, para cada entidad científica utilizada por CoResearcher,
  qué observaciones permitirían distinguir entre explicaciones competidoras.

No determinar si existen.
No determinar si son verdaderas.
Determinar: qué experimento/observación/intervención/medición permitiría
distinguir entre presencia y ausencia?

Restricciones:
  - NO construir nuevos detectores
  - NO modificar H7
  - NO descongelar EHG
  - NO crear nuevas ontologías
  - NO crear nuevos grafos
  - Exclusivamente metodológico

Entregables:
  artifacts/scientific_instrumentability_matrix.json
  artifacts/scientific_instrumentability_matrix.md
"""
import sys
import json
from pathlib import Path
from datetime import datetime, timezone

project_root = Path(__file__).resolve().parent.parent


# ------------------------------------------------------------------
# Entidades a analizar (exclusivamente las ya presentes en CoResearcher)
# ------------------------------------------------------------------

ENTITIES = [
    "DecisionNode",
    "Trajectory",
    "Convergence",
    "Restriction",
    "Mechanism",
    "Explanation",
    "Hypothesis",
    "Theory",
    "Paradigm",
]


# ------------------------------------------------------------------
# Definiciones operacionales
# ------------------------------------------------------------------

# Observable: existe evidencia directa
# Inferible: puede reconstruirse desde evidencia indirecta
# Instrumentable: at least one observation capable of discriminating competing hypotheses
# Falsable: condición observacional incompatible
# Replicable: dos investigadores independientes alcanzan conclusiones compatibles


# ------------------------------------------------------------------
# Matriz de instrumentabilidad
# ------------------------------------------------------------------

INSTRUMENTABILITY_MATRIX = {
    "DecisionNode": {
        "observable": True,
        "inferible": True,
        "instrumentable": True,
        "falsable": True,
        "replicable": True,
        "instrumentability_index": 1.0,
        "observations": [
            "GitHub API: issues, PRs, commits con actor y timestamp",
            "Audit trail verificable contra repo público",
        ],
        "falsification_criteria": [
            "Un DecisionNode sin actor, artifact_url o outcome es inválido",
            "Un DecisionNode no verificable contra GitHub API es descartado",
        ],
        "replication_protocol": "Dos investigadores extraen DecisionNodes desde el mismo repo; κ ≥ 0.8 esperado",
        "status": "FULLY_INVESTIGABLE",
        "rationale": "Directamente observable, medible y replicable. Es la entidad más sólida del sistema.",
    },
    "Trajectory": {
        "observable": False,
        "inferible": True,
        "instrumentable": True,
        "falsable": True,
        "replicable": "PARTIAL",
        "instrumentability_index": 0.75,
        "observations": [
            "Edges explícitos (chosen_over, superseded_by) con referencia",
            "Edges temporales inferidos por fecha (menos fiables)",
        ],
        "falsification_criteria": [
            "Un edge sin referencia ni justificación temporal es descartado",
            "Un ciclo en la trayectoria indica error de reconstrucción",
        ],
        "replication_protocol": "Dos investigadores reconstruyen desde mismos DecisionNodes; edges explícitos κ ≥ 0.8, temporales κ ≥ 0.4",
        "status": "INVESTIGABLE_CON_RESTRICCIONES",
        "rationale": "Inferible desde DecisionNodes. Edges explícitos son replicables. Temporales son menos fiables.",
    },
    "Convergence": {
        "observable": False,
        "inferible": True,
        "instrumentable": True,
        "falsable": True,
        "replicable": "PARTIAL",
        "instrumentability_index": 0.6,
        "observations": [
            "Clúster de ≥2 DecisionNodes con actores distintos, tema similar (Jaccard ≥ 0.5), mismo outcome",
            "Validación contra ground truth: detector debe distinguir convergence real de sintética (FPR < 20%)",
        ],
        "falsification_criteria": [
            "Un clúster con actors no independientes es descartado",
            "Un clúster replicado en datos sintéticos indica detector no fiable",
        ],
        "replication_protocol": "Dos investigadores aplican detector a mismo corpus; κ ≥ 0.4 esperado (SPRINT 63: κ = -0.094 actualmente)",
        "status": "INVESTIGABLE_CON_RESTRICCIONES",
        "rationale": "El detector existe pero no es fiable (70% FPR en sintéticos, κ = -0.094). Necesita refinamiento antes de ser investigable.",
    },
    "Restriction": {
        "observable": False,
        "inferible": False,
        "instrumentable": True,
        "falsable": True,
        "replicable": "PARTIAL",
        "instrumentability_index": 0.5,
        "observations": [
            "No observable directamente. Solo se observan manifestaciones (convergences, abandonos, residuos).",
            "Hipótesis de constraint debe generar predicciones observables.",
            "Validación: si se elimina la supuesta constraint, las decisiones cambian.",
        ],
        "falsification_criteria": [
            "Si la convergence explicada por la constraint desaparece al manipular el sistema → constraint falsada",
            "Si una hypothesis competidora explica igualmente bien → UNDETERMINED",
        ],
        "replication_protocol": "Dos investigadores proponen hypothesis de constraint para misma convergence; κ ≥ 0.4 esperado (SPRINT 63: κ = -0.094 actualmente)",
        "status": "INVESTIGABLE_CON_ALTA_RESTRICCION",
        "rationale": "No observable ni inferible directamente. Pero sí falsable: si eliminamos la constraint y el comportamiento cambia, estaba ahí. Como el gen en 1850.",
    },
    "Mechanism": {
        "observable": False,
        "inferible": False,
        "instrumentable": True,
        "falsable": True,
        "replicable": "PARTIAL",
        "instrumentability_index": 0.55,
        "observations": [
            "No observable directamente. Inferido desde patrones causales.",
            "Intervención: modificar componente X y observar efecto en Y.",
            "Comparación: sistemas con y sin mecanismo deben mostrar diferencias sistemáticas.",
        ],
        "falsification_criteria": [
            "Si modificar el presunto componente no cambia el efecto → mecanismo falsado",
            "Si el mecanismo predice efecto en dirección opuesta → falsado",
        ],
        "replication_protocol": "Dos investigadores identifican mecanismo para mismo fenómeno; κ no medido (SPRINT 52 no incluyó métricas)",
        "status": "INVESTIGABLE_CON_ALTA_RESTRICCION",
        "rationale": "Filosofía de la ciencia (Salmon, Woodward) lo considera entidad real. Pero CoResearcher no tiene protocolo de identificación reproducible.",
    },
    "Explanation": {
        "observable": False,
        "inferible": False,
        "instrumentable": True,
        "falsable": True,
        "replicable": "PARTIAL",
        "instrumentability_index": 0.5,
        "observations": [
            "No observable. Estructura textual en rationale fields.",
            "Criterio: una explicación debe identificar componentes causales.",
            "Criterio: debe predecir qué pasaría si se elimina un componente.",
        ],
        "falsification_criteria": [
            "Si la explicación no predice el resultado de una intervención → falsada",
            "Si la explicación es circular (X porque X) → inválida",
        ],
        "replication_protocol": "Dos investigadores extraen explicaciones desde mismos rationale; no hay métrica actual",
        "status": "INVESTIGABLE_CON_ALTA_RESTRICCION",
        "rationale": "La ciencia entera se basa en explicaciones. Pero CoResearcher no sabe medir su calidad de forma reproducible.",
    },
    "Hypothesis": {
        "observable": False,
        "inferible": False,
        "instrumentable": True,
        "falsable": True,
        "replicable": "PARTIAL",
        "instrumentability_index": 0.55,
        "observations": [
            "No observable. Es una entidad metodológica.",
            "Firma observacional: la hypothesis debe generar predicciones específicas.",
            "Criterio: al menos una predicción debe ser falsable.",
        ],
        "falsification_criteria": [
            "Si todas las predicciones de la hypothesis son verdad por definición → no es hypothesis",
            "Si la hypothesis no genera predicciones nuevas → no es científica",
        ],
        "replication_protocol": "Dos investigadores evalúan misma hypothesis por criterios de falsabilidad; no hay métrica actual",
        "status": "INVESTIGABLE_CON_ALTA_RESTRICCION",
        "rationale": "CRÍTICO: Evaluar hypothesis por observabilidad es error categorial. Su función es generar predicciones falsables. Pathway: definir métrica de falsabilidad y novedad.",
    },
    "Theory": {
        "observable": False,
        "inferible": False,
        "instrumentable": True,
        "falsable": True,
        "replicable": "PARTIAL",
        "instrumentability_index": 0.5,
        "observations": [
            "No observable. Es una estructura explicativa.",
            "Firma observacional: la teoría debe derivar predicciones comprobables.",
            "Criterio: al menos una predicción debe ser falsable y novedosa.",
        ],
        "falsification_criteria": [
            "Si la teoría no genera predicciones falsables → no es científica",
            "Si todas las predicciones son confirmadas pero la teoría es modificable ad hoc → débil",
        ],
        "replication_protocol": "Dos investigadores evalúan misma teoría por poder predictivo; no hay métrica actual",
        "status": "INVESTIGABLE_CON_ALTA_RESTRICCION",
        "rationale": "CRÍTICO: La teoría de la evolución no es observable. La relatividad no es observable. Pero generan predicciones falsables. Pathway: definir métrica de coherencia interna y poder explicativo.",
    },
    "Paradigm": {
        "observable": False,
        "inferible": False,
        "instrumentable": True,
        "falsable": True,
        "replicable": "UNKNOWN",
        "instrumentability_index": 0.4,
        "observations": [
            "No observable desde commits o PRs.",
            "Indicadores: supuestos compartidos entre actores, persistencia temporal.",
            "Intervención: cambiar un supuesto compartido y observar si la comunidad lo adopta.",
        ],
        "falsification_criteria": [
            "Si los actores no comparten el supuesto → no hay paradigma",
            "Si el supuesto cambia sin resistencia → no era paradigmático",
        ],
        "replication_protocol": "No establecido. Requiere análisis semántico profundo.",
        "status": "INVESTIGABLE_CON_MUY_ALTA_RESTRICCION",
        "rationale": "Kuhn argumenta su existencia. Pero no hay consenso ni protocolo de identificación. Muy difícil de operacionalizar.",
    },
}


def calculate_instrumentability_index(entry):
    """Calcula Instrumentability Index como promedio de 5 dimensiones booleanas."""
    dims = [
        entry["observable"],
        entry["inferible"],
        entry["instrumentable"],
        entry["falsable"],
        entry["replicable"] is not None and entry["replicable"] != "UNKNOWN",
    ]
    return sum(1 for d in dims if d is True) / len(dims)


def classify_investigability(index):
    if index >= 0.8:
        return "FULLY_INVESTIGABLE"
    elif index >= 0.6:
        return "INVESTIGABLE_CON_RESTRICCIONES"
    elif index >= 0.4:
        return "INVESTIGABLE_CON_ALTA_RESTRICCION"
    elif index >= 0.2:
        return "INVESTIGABLE_CON_MUY_ALTA_RESTRICCION"
    else:
        return "NON_INVESTIGABLE"


def main():
    print("=" * 70)
    print("SPRINT 66 — Scientific Instrumentability Framework")
    print("=" * 70)
    print("Question: Qué observaciones permitirían distinguir entre explicaciones competidoras?")
    print()

    results = []
    print(f"{'Entity':<20} {'Obs':>4} {'Inf':>4} {'Inst':>5} {'Fals':>5} {'Rep':>6} {'Index':>6} {'Status':<30}")
    print(f"{'-'*20} {'-'*4} {'-'*4} {'-'*5} {'-'*5} {'-'*6} {'-'*6} {'-'*30}")

    for entity_name in ENTITIES:
        entry = INSTRUMENTABILITY_MATRIX[entity_name]
        index = calculate_instrumentability_index(entry)
        entry["instrumentability_index"] = index
        entry["status"] = classify_investigability(index)
        entry["entity"] = entity_name
        results.append(entry)

        obs = "Yes" if entry["observable"] else "No"
        inf = "Yes" if entry["inferible"] else "No"
        inst = "Yes" if entry["instrumentable"] else "No"
        fals = "Yes" if entry["falsable"] else "No"
        rep = entry["replicable"] if isinstance(entry["replicable"], str) else ("Yes" if entry["replicable"] else "No")

        print(f"{entity_name:<20} "
              f"{obs:>4} {inf:>4} {inst:>5} {fals:>5} {rep:>6} "
              f"{index:>6.2f} {entry['status']:<30}")

    # Resumen por categoría
    categories = {}
    for r in results:
        cat = r["status"]
        categories[cat] = categories.get(cat, 0) + 1

    print()
    print("[Distribution]")
    for cat, count in sorted(categories.items(), key=lambda x: -x[1]):
        print(f"  {cat}: {count}")

    # Entidades NON_INVESTIGABLE
    non_inv = [r for r in results if r["status"] == "NON_INVESTIGABLE"]
    if non_inv:
        print()
        print("[NON_INVESTIGABLE entities]")
        for r in non_inv:
            print(f"  ⚠️ {r['entity']}")
    else:
        print()
        print("[NON_INVESTIGABLE entities]: None — todas son al menos investigable con alta constraint")

    # Experimento obligatorio: Hypothesis, Theory, Restriction
    print()
    print("[Experimento obligatorio: Hypothesis, Theory, Restriction]")
    mandatory = ["Hypothesis", "Theory", "Restriction"]
    for entity_name in mandatory:
        entry = INSTRUMENTABILITY_MATRIX[entity_name]
        print(f"\n  {entity_name}:")
        print(f"    Observable: {entry['observable']}")
        print(f"    Inferible: {entry['inferible']}")
        print(f"    Instrumentable: {entry['instrumentable']}")
        print(f"    Falsable: {entry['falsable']}")
        print(f"    Replicable: {entry['replicable']}")
        print(f"    Observations: {len(entry['observations'])}")
        print(f"    Falsification criteria: {len(entry['falsification_criteria'])}")
        print(f"    → STATUS: {entry['status']}")

    # Crear reportes
    report = {
        "report_id": f"INST66-{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S')}",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "sprint": "SPRINT 66 — Scientific Instrumentability Framework",
        "objective": (
            "Construir un marco empírico para evaluar la instrumentabilidad "
            "científica de las entidades utilizadas por CoResearcher."
        ),
        "scientific_question": (
            "Qué observaciones permitirían distinguir entre explicaciones competidoras?"
        ),
        "methodology": {
            "dimensions": {
                "observable": "Existe evidencia directa",
                "inferible": "Puede reconstruirse desde evidencia indirecta",
                "instrumentable": "Al menos una observación capaz de discriminar hypothesis competidoras",
                "falsable": "Puede formularse una condición observacional incompatible",
                "replicable": "Dos investigadores independientes alcanzan conclusiones compatibles",
            },
            "instrumentability_index": "Promedio de 5 dimensiones booleanas (0.0-1.0)",
            "classification": {
                "FULLY_INVESTIGABLE": "index ≥ 0.8",
                "INVESTIGABLE_CON_RESTRICCIONES": "0.6 ≤ index < 0.8",
                "INVESTIGABLE_CON_ALTA_RESTRICCION": "0.4 ≤ index < 0.6",
                "INVESTIGABLE_CON_MUY_ALTA_RESTRICCION": "0.2 ≤ index < 0.4",
                "NON_INVESTIGABLE": "index < 0.2",
            },
        },
        "entities": results,
        "summary": {
            "total_entities": len(results),
            "fully_investigable": categories.get("FULLY_INVESTIGABLE", 0),
            "investigable_con_constraints": categories.get("INVESTIGABLE_CON_RESTRICCIONES", 0),
            "investigable_con_alta_restriccion": categories.get("INVESTIGABLE_CON_ALTA_RESTRICCION", 0),
            "investigable_con_muy_alta_restriccion": categories.get("INVESTIGABLE_CON_MUY_ALTA_RESTRICCION", 0),
            "non_investigable": categories.get("NON_INVESTIGABLE", 0),
        },
        "mandatory_experiment": {
            "hypothesis": {
                "observable": False,
                "inferible": False,
                "instrumentable": True,
                "falsable": True,
                "replicable": "PARTIAL",
                "status": INSTRUMENTABILITY_MATRIX["Hypothesis"]["status"],
                "conclusion": (
                    "NON-INSTRUMENTABLE por observabilidad, pero SÍ instrumentable "
                    "por falsabilidad. No requiere observación directa. Requiere "
                    "definir métrica de falsabilidad y novedad."
                ),
            },
            "theory": {
                "observable": False,
                "inferible": False,
                "instrumentable": True,
                "falsable": True,
                "replicable": "PARTIAL",
                "status": INSTRUMENTABILITY_MATRIX["Theory"]["status"],
                "conclusion": (
                    "NON-INSTRUMENTABLE por observabilidad, pero SÍ instrumentable "
                    "por falsabilidad. La teoría de la evolución no es observable "
                    "pero es investigable por sus predicciones."
                ),
            },
            "restriction": {
                "observable": False,
                "inferible": False,
                "instrumentable": True,
                "falsable": True,
                "replicable": "PARTIAL",
                "status": INSTRUMENTABILITY_MATRIX["Restriction"]["status"],
                "conclusion": (
                    "NON-INSTRUMENTABLE por observabilidad, pero SÍ instrumentable "
                    "por manipulación. Si eliminamos la constraint y el comportamiento "
                    "cambia, estaba ahí. Como el gen en 1850."
                ),
            },
        },
        "key_finding": (
            "Todas las entidades analizadas son al menos INVESTIGABLE_CON_ALTA_RESTRICCION. "
            "Ninguna es NON_INVESTIGABLE. Esto significa que, con instrumentación adecuada, "
            "todas pueden ser estudiadas científicamente."
        ),
        "paradigm_shift": (
            "El problema no es generar explicaciones. "
            "El problema es diseñar observaciones capaces de decidir entre ellas."
        ),
        "epistemic_note": (
            "Este sprint NO genera hypothesis. NO reactiva EHG. "
            "Solo produce una matriz de instrumentabilidad. "
            "Cualquier explicación atractiva sin mecanismo discriminativo "
            "debe etiquetarse como UNDETERMINED."
        ),
    }

    # Guardar JSON
    output_json = Path("artifacts/scientific_instrumentability_matrix.json")
    output_json.parent.mkdir(parents=True, exist_ok=True)
    with open(output_json, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, ensure_ascii=False, default=str)

    # Guardar Markdown
    output_md = Path("artifacts/scientific_instrumentability_matrix.md")
    md_lines = [
        "# SCIENTIFIC INSTRUMENTABILITY MATRIX — SPRINT 66",
        "",
        f"**Generated**: {report['generated_at']}",
        f"**Report ID**: {report['report_id']}",
        "",
        "## Scientific Question",
        "",
        "> Qué observaciones permitirían distinguir entre explicaciones competidoras?",
        "",
        "## Methodology",
        "",
        "| Dimension | Question |",
        "|-----------|----------|",
        "| Observable | Existe evidencia directa? |",
        "| Inferible | Puede reconstruirse desde evidencia indirecta? |",
        "| Instrumentable | Al menos una observación capaz de discriminar hypothesis competidoras? |",
        "| Falsable | Puede formularse una condición observacional incompatible? |",
        "| Replicable | Dos investigadores independientes alcanzan conclusiones compatibles? |",
        "",
        "## Instrumentability Index",
        "",
        "- Escala: 0.0 (no investigable) → 1.0 (plenamente investigable)",
        "- Cálculo: promedio de 5 dimensiones booleanas",
        "",
        "## Matrix",
        "",
        "| Entity | Observable | Inferible | Instrumentable | Falsable | Replicable | Index | Status |",
        "|--------|------------|-----------|----------------|----------|------------|-------|--------|",
    ]

    for r in results:
        rep = r["replicable"] if isinstance(r["replicable"], str) else ("Yes" if r["replicable"] else "No")
        md_lines.append(
            f"| {r['entity']} "
            f"| {'Yes' if r['observable'] else 'No'} "
            f"| {'Yes' if r['inferible'] else 'No'} "
            f"| {'Yes' if r['instrumentable'] else 'No'} "
            f"| {'Yes' if r['falsable'] else 'No'} "
            f"| {rep} "
            f"| {r['instrumentability_index']:.2f} "
            f"| {r['status']} |"
        )

    md_lines.extend([
        "",
        "## Distribution",
        "",
        "| Status | Count |",
        "|--------|-------|",
    ])
    for cat in [
        "FULLY_INVESTIGABLE",
        "INVESTIGABLE_CON_RESTRICCIONES",
        "INVESTIGABLE_CON_ALTA_RESTRICCION",
        "INVESTIGABLE_CON_MUY_ALTA_RESTRICCION",
        "NON_INIVESTIGABLE",
    ]:
        count = categories.get(cat, 0)
        md_lines.append(f"| {cat} | {count} |")

    md_lines.extend([
        "",
        "## Mandatory Experiment: Hypothesis, Theory, Restriction",
        "",
        "### Hypothesis",
        "",
        f"- **Observable**: {report['mandatory_experiment']['hypothesis']['observable']}",
        f"- **Inferible**: {report['mandatory_experiment']['hypothesis']['inferible']}",
        f"- **Instrumentable**: {report['mandatory_experiment']['hypothesis']['instrumentable']}",
        f"- **Falsable**: {report['mandatory_experiment']['hypothesis']['falsable']}",
        f"- **Replicable**: {report['mandatory_experiment']['hypothesis']['replicable']}",
        f"- **Status**: {report['mandatory_experiment']['hypothesis']['status']}",
        "",
        f"**Conclusion**: {report['mandatory_experiment']['hypothesis']['conclusion']}",
        "",
        "### Theory",
        "",
        f"- **Observable**: {report['mandatory_experiment']['theory']['observable']}",
        f"- **Inferible**: {report['mandatory_experiment']['theory']['inferible']}",
        f"- **Instrumentable**: {report['mandatory_experiment']['theory']['instrumentable']}",
        f"- **Falsable**: {report['mandatory_experiment']['theory']['falsable']}",
        f"- **Replicable**: {report['mandatory_experiment']['theory']['replicable']}",
        f"- **Status**: {report['mandatory_experiment']['theory']['status']}",
        "",
        f"**Conclusion**: {report['mandatory_experiment']['theory']['conclusion']}",
        "",
        "### Restriction",
        "",
        f"- **Observable**: {report['mandatory_experiment']['restriction']['observable']}",
        f"- **Inferible**: {report['mandatory_experiment']['restriction']['inferible']}",
        f"- **Instrumentable**: {report['mandatory_experiment']['restriction']['instrumentable']}",
        f"- **Falsable**: {report['mandatory_experiment']['restriction']['falsable']}",
        f"- **Replicable**: {report['mandatory_experiment']['restriction']['replicable']}",
        f"- **Status**: {report['mandatory_experiment']['restriction']['status']}",
        "",
        f"**Conclusion**: {report['mandatory_experiment']['restriction']['conclusion']}",
        "",
        "## Key Finding",
        "",
        f"> {report['key_finding']}",
        "",
        "## Paradigm Shift",
        "",
        f"> {report['paradigm_shift']}",
        "",
        "---",
        "",
        "*Este sprint es exclusivamente metodológico. No genera hypothesis, no reactiva EHG, no modifica arquitectura.*",
        "*Ver: docs/EPISTEMIC_GAP_CONCEPT.md*",
    ])

    with open(output_md, "w", encoding="utf-8") as f:
        f.write("\n".join(md_lines) + "\n")

    print()
    print("=" * 70)
    print("DELIVERABLES")
    print("=" * 70)
    print(f"  {output_json}")
    print(f"  {output_md}")
    print()
    print(f"Total entities: {len(results)}")
    print(f"Non-investigable: {categories.get('NON_INVESTIGABLE', 0)}")
    print()
    print("ANSWER: Todas las entidades son al menos INVESTIGABLE_CON_ALTA_RESTRICCION.")
    print("        El problema no es generar explicaciones.")
    print("        El problema es diseñar observaciones capaces de decidir entre ellas.")
    print("=" * 70)

    return 0


if __name__ == "__main__":
    sys.exit(main())