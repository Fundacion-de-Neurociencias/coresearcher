#!/usr/bin/env python3
"""
SPRINT 64 — Reality of Scientific Constructs

Auditar la realidad epistemológica de cada concepto usado por CoResearcher.

Pregunta central:
  Qué entidades utilizadas por científicos existen realmente como variables
  observables y cuáles son simplemente construcciones explicativas útiles?

Para cada entidad evaluar:
  A. Observabilidad — es directamente observable?
  B. Reproducibilidad — produce acuerdo interobservador?
  C. Falsabilidad — genera predicciones falsables?
  D. Narratividad — es etiqueta retrospectiva?

Entregable: artifacts/scientific_constructs_reality.json
"""
import sys
import json
from pathlib import Path
from datetime import datetime, timezone

project_root = Path(__file__).resolve().parent.parent


# ------------------------------------------------------------------
# Entidades a auditar
# ------------------------------------------------------------------
# Cada entidad se evalúa contra 4 dimensiones:
# - observability: Alta/Media/Baja/Muy baja
# - reproducibility: Alta/Media/Baja/Desconocida
# - falsifiability: Alta/Media/Baja/Nula
# - narrative_label: True/False (es etiqueta retrospectiva?)
#
# Basado en evidencia empírica de SPRINT 60C-63

ENTITIES = [
    {
        "entity": "DecisionNode",
        "description": "Una decision observable tomada por un actor",
        "evidence": "301 decisiones extraídas de langgraph, auditadas",
        "sprint_origin": "SPRINT 60C",
        "dimensions": {
            "observability": "Alta",
            "reproducibility": "Alta",
            "falsifiability": "Alta",
            "narrative_label": False,
        },
        "operational_definition": (
            "Un evento con: actor, artifact_url, outcome, rationale. "
            "Verificable contra GitHub API."
        ),
        "empirical_evidence": (
            "301 nodos extraídos. Métricas de precisión calculadas. "
            "Auditabilidad score = 1.0."
        ),
        "kappa_evidence": "No medido directamente, pero extracción es reproducible",
        "status": "VALIDATED",
    },
    {
        "entity": "Trajectory",
        "description": "Secuencia de decisiones conectadas por edges",
        "evidence": "426 edges reconstruidos (231 explícitos + 195 temporales)",
        "sprint_origin": "SPRINT 60C",
        "dimensions": {
            "observability": "Media",
            "reproducibility": "Media",
            "falsifiability": "Media",
            "narrative_label": False,
        },
        "operational_definition": (
            "Grafo dirigido de DecisionNodes conectados por edges "
            "tipados (chosen_over, abandoned_for, superseded_by, temporal)."
        ),
        "empirical_evidence": (
            "426 edges. 231 explícitos (con referencia). "
            "195 temporales (inferidos por fecha)."
        ),
        "kappa_evidence": "No medido. Los edges temporales son menos fiables.",
        "status": "PROMISING",
    },
    {
        "entity": "Convergence",
        "description": "Múltiples trayectorias independientes que chocan contra la misma barrera",
        "evidence": "4 convergences detectadas en langgraph",
        "sprint_origin": "SPRINT 60C (detector v1.1)",
        "dimensions": {
            "observability": "Media",
            "reproducibility": "Baja",
            "falsifiability": "Media",
            "narrative_label": False,
        },
        "operational_definition": (
            "Cluster de ≥2 DecisionNodes con: actores distintos, "
            "tema similar (Jaccard ≥ 0.5), mismo outcome (abandoned/failure)."
        ),
        "empirical_evidence": (
            "4 barrier convergences. Pero FALSIFICATION EXPERIMENT (SPRINT 61) "
            "mostró 70% false positive rate en datos sintéticos."
        ),
        "kappa_evidence": "κ = -0.030 (SPRINT 61 FASE 2). Peor que azar.",
        "status": "OBSERVED_BUT_UNRELIABLE",
    },
    {
        "entity": "Restriction",
        "description": "Supuesto implícito compartido que limita el espacio de posibilidades",
        "evidence": "12 hypothesis generadas, 6 OPERATIONAL (SPRINT 62)",
        "sprint_origin": "SPRINT 60C (concepto), SPRINT 62 (operacionalización)",
        "dimensions": {
            "observability": "Baja",
            "reproducibility": "Baja",
            "falsifiability": "Media",
            "narrative_label": True,
        },
        "operational_definition": (
            "Una constraint existe si: (1) genera predicciones observables, "
            "(2) explica >1 trayectoria, (3) su eliminación cambia decisiones, "
            "(4) puede ser falsada."
        ),
        "empirical_evidence": (
            "6/12 hypothesis cumplen 4 criterios (SPRINT 62). "
            "Pero κ = -0.094 en stress test (SPRINT 63). "
            "La variable es PARTIALLY_OPERATIONAL."
        ),
        "kappa_evidence": "κ = -0.094 (SPRINT 63 FASE 4). No estable.",
        "status": "UNDETERMINED",
    },
    {
        "entity": "Paradigm",
        "description": "Marco conceptual dominante en una comunidad",
        "evidence": "0 paradigm residues detectados (SPRINT 60C)",
        "sprint_origin": "SPRINT 60C (concepto)",
        "dimensions": {
            "observability": "Muy baja",
            "reproducibility": "Desconocida",
            "falsifiability": "Baja",
            "narrative_label": True,
        },
        "operational_definition": (
            "No definida operacionalmente. El detector de paradigm residues "
            "encontró 0 resultados. No hay criterios observables."
        ),
        "empirical_evidence": (
            "0 paradigm residues. Limitación documentada: "
            "'un paradigma no vive en commits. Vive en supuestos.'"
        ),
        "kappa_evidence": "No medido. No hay datos suficientes.",
        "status": "UNTESTED",
    },
    {
        "entity": "Hypothesis",
        "description": "Propuesta explicativa generada desde gaps o constraints",
        "evidence": "EHG CONGELADO — 0 hypothesis generadas",
        "sprint_origin": "SPRINT 42 (concepto), congelado en SPRINT 60C",
        "dimensions": {
            "observability": "Muy baja",
            "reproducibility": "Muy baja",
            "falsifiability": "Media",
            "narrative_label": True,
        },
        "operational_definition": (
            "No definida operacionalmente. EHG congelado hasta que "
            "las constraints sean validadas (precisión ≥80%)."
        ),
        "empirical_evidence": (
            "0 hypothesis generadas. EHG correctamente congelado."
        ),
        "kappa_evidence": "No medido. EHG congelado.",
        "status": "FROZEN",
    },
    {
        "entity": "Epistemic Gap",
        "description": "Región del espacio de conocimiento donde la ignorancia es clasificable",
        "evidence": "155 gaps detectados y clasificados (A/B/C/D)",
        "sprint_origin": "SPRINT 60C (detector v1.1)",
        "dimensions": {
            "observability": "Alta",
            "reproducibility": "Media",
            "falsifiability": "Alta",
            "narrative_label": False,
        },
        "operational_definition": (
            "Gap detectado por señales heurísticas: pending sin edges, "
            "abandoned sin rationale, low confidence. Clasificado A/B/C/D."
        ),
        "empirical_evidence": (
            "155 gaps. 113 empíricos, 42 causales, 0 matemáticos. "
            "Audit status: PENDING_AUDIT."
        ),
        "kappa_evidence": "No medido directamente. Pero detección es reproducible.",
        "status": "OBSERVED",
    },
    {
        "entity": "Explanation",
        "description": "Narrativa que conecta observaciones con causas",
        "evidence": "Usada implícitamente en auditorías pero nunca auditada",
        "sprint_origin": "Implícita en todos los sprints",
        "dimensions": {
            "observability": "Muy baja",
            "reproducibility": "Muy baja",
            "falsifiability": "Baja",
            "narrative_label": True,
        },
        "operational_definition": (
            "No definida operacionalmente. Las explicaciones aparecen "
            "en rationale fields pero nunca se auditan como entidades."
        ),
        "empirical_evidence": (
            "Las explicaciones aparecen en rationale de DecisionNodes "
            "pero su calidad nunca se midió de forma reproducible."
        ),
        "kappa_evidence": "No medido.",
        "status": "NARRATIVE",
    },
    {
        "entity": "Mechanism",
        "description": "Proceso causal que produce un fenómeno observado",
        "evidence": "Buscado en SPRINT 52 (Explanatory Mechanism Audit)",
        "sprint_origin": "SPRINT 52",
        "dimensions": {
            "observability": "Baja",
            "reproducibility": "Baja",
            "falsifiability": "Media",
            "narrative_label": True,
        },
        "operational_definition": (
            "No definida operacionalmente de forma reproducible. "
            "SPRINT 52 buscó mecanismos pero sin criterios formales."
        ),
        "empirical_evidence": (
            "SPRINT 52 auditó mecanismos explicativos pero sin "
            "medir acuerdo interobservador."
        ),
        "kappa_evidence": "No medido.",
        "status": "NARRATIVE",
    },
    {
        "entity": "Theory",
        "description": "Sistema coherente de explicaciones que genera predicciones",
        "evidence": "No existe en CoResearcher — nunca se generó una teoría",
        "sprint_origin": "N/A",
        "dimensions": {
            "observability": "Muy baja",
            "reproducibility": "Desconocida",
            "falsifiability": "Media",
            "narrative_label": True,
        },
        "operational_definition": (
            "No definida. CoResearcher no genera teorías."
        ),
        "empirical_evidence": "0 teorías generadas.",
        "kappa_evidence": "No medido.",
        "status": "UNTESTED",
    },
]


def score_entity(entity):
    """Calcula un score numérico para cada dimensión."""
    scores = {"Alta": 3, "Media": 2, "Baja": 1, "Muy baja": 0, "Desconocida": 0, "Nula": 0}
    dims = entity["dimensions"]
    return {
        "observability_score": scores.get(dims["observability"], 0),
        "reproducibility_score": scores.get(dims["reproducibility"], 0),
        "falsifiability_score": scores.get(dims["falsifiability"], 0),
        "narrative_penalty": 2 if dims["narrative_label"] else 0,
        "total_reality_score": (
            scores.get(dims["observability"], 0)
            + scores.get(dims["reproducibility"], 0)
            + scores.get(dims["falsifiability"], 0)
            - (2 if dims["narrative_label"] else 0)
        ),
    }


def classify_reality(entity, scores):
    """
    Clasifica la estabilidad operacional de una entidad dentro de CoResearcher.

    IMPORTANTE: Esta clasificación NO afirma si una entidad "existe" o no
    como objeto científico. Solo evalúa si CoResearcher puede operacionalizarla
    de forma robusta con sus herramientas actuales.

    Una puntuación baja significa "nuestro sistema aún no sabe operacionalizar
    esta entidad de forma reproducible", NO "esta entidad no existe".

    Contraejemplo: el "gen" en 1850 tenía observabilidad = 0 pero era real.
    La observabilidad directa no determina ontología.
    """
    total = scores["total_reality_score"]
    max_possible = 9  # 3+3+3

    if total >= 7:
        return "OPERATIONAL — CoResearcher puede medirlo de forma robusta"
    elif total >= 4:
        return "PARTIALLY_OPERATIONAL — algunas dimensiones funcionan"
    elif total >= 1:
        return "NOT_YET_OPERATIONAL — requiere formalización antes de usar"
    else:
        return "UNOPERATIONALIZED — CoResearcher no sabe medirlo todavía"


def main():
    print("=" * 70)
    print("SPRINT 64 — Reality of Scientific Constructs")
    print("=" * 70)
    print("Question: Qué entidades existen realmente como variables observables?")
    print()

    # Evaluar cada entidad
    results = []
    for entity in ENTITIES:
        scores = score_entity(entity)
        reality_class = classify_reality(entity, scores)
        entity_result = {**entity, "scores": scores, "reality_class": reality_class}
        results.append(entity_result)

        print(f"  {entity['entity']:<20} → {reality_class}")
        print(f"    obs={scores['observability_score']} "
              f"repro={scores['reproducibility_score']} "
              f"fals={scores['falsifiability_score']} "
              f"narr=-{scores['narrative_penalty']} "
              f"total={scores['total_reality_score']}/9")

    # Tabla resumen
    print()
    print("=" * 70)
    print("REALITY TABLE")
    print("=" * 70)
    print(f"{'Entity':<20} {'Obs':>4} {'Repro':>5} {'Fals':>4} {'Narr':>4} {'Total':>5} {'Status':<30}")
    print(f"{'-'*20} {'-'*4} {'-'*5} {'-'*4} {'-'*4} {'-'*5} {'-'*30}")

    for r in results:
        s = r["scores"]
        print(f"{r['entity']:<20} "
              f"{s['observability_score']:>4} "
              f"{s['reproducibility_score']:>5} "
              f"{s['falsifiability_score']:>4} "
              f"{'Yes' if r['dimensions']['narrative_label'] else 'No':>4} "
              f"{s['total_reality_score']:>5} "
              f"{r['reality_class']:<30}")

    # Contar por categoría
    categories = {}
    for r in results:
        cat = r["reality_class"].split(" — ")[0]
        categories[cat] = categories.get(cat, 0) + 1

    print()
    print("Summary by reality category:")
    for cat, count in sorted(categories.items(), key=lambda x: -x[1]):
        print(f"  {cat}: {count}")

    # Hallazgo clave
    real_count = categories.get("REAL", 0)
    partial_count = categories.get("PARTIALLY_REAL", 0)
    narrative_count = categories.get("NARRATIVE", 0)
    metaphor_count = categories.get("METAPHOR", 0)

    if real_count >= len(results) * 0.5:
        verdict = "GREEN — most entities are operationalizable"
    elif real_count + partial_count >= len(results) * 0.5:
        verdict = "YELLOW — some entities operational, some need work"
    else:
        verdict = "RED — most entities not yet operationalized by CoResearcher"

    print()
    print(f"VERDICT: {verdict}")

    # Crear reporte
    report = {
        "report_id": f"REALITY64-{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S')}",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "sprint": "SPRINT 64 — Reality of Scientific Constructs",
        "objective": (
            "Auditar la realidad epistemológica de cada concepto usado "
            "por CoResearcher. Qué entidades existen realmente como "
            "variables observables y cuáles son construcciones explicativas?"
        ),
        "central_question": (
            "Qué entidades utilizadas por científicos existen realmente "
            "como variables observables y cuáles son simplemente "
            "construcciones explicativas útiles?"
        ),
        "methodology": {
            "dimensions": {
                "A_observability": "Es directamente observable?",
                "B_reproducibility": "Produce acuerdo interobservador?",
                "C_falsifiability": "Genera predicciones falsables?",
                "D_narrative_label": "Es etiqueta retrospectiva?",
            },
            "scoring": "Alta=3, Media=2, Baja=1, Muy baja=0. Narrative penalty: -2",
            "classification": {
                "REAL": "total ≥ 7 (observable, reproducible, falsable)",
                "PARTIALLY_REAL": "total 4-6 (algunas dimensiones funcionan)",
                "NARRATIVE": "total 1-3 (útil como etiqueta, no como variable)",
                "METAPHOR": "total ≤ 0 (construcción sin base empírica)",
            },
        },
        "entities": results,
        "summary": {
            "total_entities": len(results),
            "real": real_count,
            "partially_real": partial_count,
            "narrative": narrative_count,
            "metaphor": metaphor_count,
            "categories": categories,
        },
        "verdict": verdict,
        "key_finding": (
            "Bajo el esquema actual de observabilidad, reproducibilidad y "
            "falsabilidad empleado por CoResearcher, los constructos más "
            "robustos son DecisionNode y Epistemic Gap. Otros constructos "
            "tradicionales de la práctica científica (hypothesis, theory, "
            "explanation, paradigm) muestran baja estabilidad operacional "
            "y requieren una formalización más rigurosa antes de poder "
            "utilizarse como unidades observacionales dentro del sistema."
        ),
        "critical_caveat": (
            "IMPORTANTE: Una puntuación baja NO significa que la entidad "
            "no exista como objeto científico. Significa que CoResearcher "
            "aún no sabe operacionalizarla de forma reproducible. "
            "Contraejemplo: el 'gen' en 1850 tenía observabilidad = 0 "
            "pero era real. La observabilidad directa no determina ontología. "
            "Una hypothesis no es un objeto físico — es una entidad "
            "metodológica cuya función es generar predicciones falsables. "
            "Una teoría no es observable — es una estructura explicativa. "
            "Evaluarlas con criterios diseñados para objetos observables "
            "produce un falso negativo conceptual."
        ),
        "implication_for_EHG": (
            "El EHG no puede revivir hasta que las entidades que usa "
            "(hypothesis, restriction, mechanism) alcancen estabilidad "
            "interobservador. Actualmente son NARRATIVE o UNTESTED."
        ),
        "implication_for_coresearcher": (
            "CoResearcher está evolucionando de generador de hypothesis "
            "a auditor computacional de epistemología científica. "
            "Esa dirección produce resultados más sólidos que la "
            "búsqueda prematura de hypothesis."
        ),
        "parallel_with_LRM": {
            "description": (
                "El paralelismo con el artículo sobre LRM es brutal: "
                "Chain of Thought ↔ Restricción compartida. "
                "Ambas parecen explicar. Ambas no son observables "
                "directamente. Ambas tienen baja fidelidad/estabilidad. "
                "Ambas son fáciles de antropomorfizar/reificar."
            ),
            "table": {
                "LRM": ["Chain of Thought", "Parece explicar", "No observable", "Baja fidelidad", "Fácil antropomorfizar"],
                "CoResearcher": ["Restricción compartida", "Parece explicar", "No observable", "Baja estabilidad", "Fácil reificar"],
            },
        },
        "epistemic_note": (
            "Este sprint NO construye nada. Solo audita. "
            "La pregunta no es 'cuál es la hypothesis correcta?' "
            "sino 'puede CoResearcher operacionalizar la categoría "
            "hypothesis de forma reproducible?'. "
            "La respuesta actual es: no todavía. "
            "Eso no significa que las hypothesis no existan — significa "
            "que nuestro sistema necesita formalización adicional."
        ),
    }

    # Guardar
    output_path = Path("artifacts/scientific_constructs_reality.json")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, ensure_ascii=False, default=str)

    print()
    print(f"Output: {output_path}")
    print("=" * 70)

    return 0


if __name__ == "__main__":
    sys.exit(main())