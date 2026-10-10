#!/usr/bin/env python3
"""
SPRINT 62 — Operationalization of Constraints

Evalúa las 12 hypothesis de SPRINT 61 contra los 4 criterios operacionales:

1. Genera predicciones observables
2. Explica más de una trayectoria
3. Su eliminación cambia el espacio de decisiones
4. Puede ser falsada

Entregable: artifacts/constraint_operationalization.json

Ver: docs/SPRINT_62_OPERATIONALIZATION.md
"""
import sys
import json
from pathlib import Path
from datetime import datetime, timezone

# Add python/ to path
project_root = Path(__file__).resolve().parent.parent
python_dir = project_root / "python"
if str(python_dir) not in sys.path:
    sys.path.insert(0, str(python_dir))

from discovery.epistemic_gap_detector import EpistemicStatus


# 12 hypotheses of SPRINT 61 evaluated against 4 operational criteria
# Cada hypothesis se evalúa honestamente: Does it satisfy each criterion or not?

HYPOTHESES_EVALUATION = [
    # === CONV-000001: langgraph-api Python 3.14 ===
    {
        "convergence_id": "CONV-000001",
        "hypothesis_id": "A",
        "description": "Restricción histórica: compatibilidad hacia atrás con langgraph-api",
        "restriction_type": "historica",
        "criteria": {
            "c1_observable_predictions": {
                "met": True,
                "prediction": "Encontraremos version constraints en setup.py/pyproject.toml que excluyen 0.7.67",
                "evidence_needed": "Examinar el historial de setup.py/pyproject.toml",
            },
            "c2_explains_multiple_trajectories": {
                "met": True,
                "explanation": "Explica por qué 2 actores distintos chocaron con la misma barrera de versión",
                "num_trajectories_explained": 2,
            },
            "c3_elimination_changes_decisions": {
                "met": True,
                "counterfactual": "Si no hubiera constraint de versión, los PRs no serían necesarios",
                "evidence_needed": "Verificar que el constraint existe y fue eliminado posteriormente",
            },
            "c4_falsifiable": {
                "met": True,
                "falsification": "Si no existe constraint de versión inferior en el historial → falsada",
            },
        },
        "criteria_met_count": 4,
        "operational_status": "OPERATIONAL",
    },
    {
        "convergence_id": "CONV-000001",
        "hypothesis_id": "B",
        "description": "Limitación técnica: Python 3.14 introdujo cambios que rompían langgraph-api",
        "restriction_type": "tecnica",
        "criteria": {
            "c1_observable_predictions": {
                "met": True,
                "prediction": "Python 3.14 changelog mencionará breaking changes relevantes",
                "evidence_needed": "Examinar Python 3.14 changelog",
            },
            "c2_explains_multiple_trajectories": {
                "met": True,
                "explanation": "Explica por qué múltiples actores tuvieron el mismo problema",
                "num_trajectories_explained": 2,
            },
            "c3_elimination_changes_decisions": {
                "met": False,
                "counterfactual": "Si Python 3.14 no tuviera breaking changes, los PRs no serían necesarios",
                "evidence_needed": "Pero esto no se puede verificar sin acceso al changelog",
                "issue": "El contrafactual es especulativo — no sabemos si los PRs eran por breaking changes o por otra razón",
            },
            "c4_falsifiable": {
                "met": True,
                "falsification": "Si Python 3.14 no tiene breaking changes relevantes → falsada",
            },
        },
        "criteria_met_count": 3,
        "operational_status": "PARTIALLY_OPERATIONAL",
    },
    {
        "convergence_id": "CONV-000001",
        "hypothesis_id": "C",
        "description": "Artefacto del linker: PRs generados por bots de dependencia",
        "restriction_type": "tecnica",
        "criteria": {
            "c1_observable_predictions": {
                "met": True,
                "prediction": "Los autores de los PRs serán bots (dependabot, renovate, etc.)",
                "evidence_needed": "Examinar los perfiles de GitHub de los autores",
            },
            "c2_explains_multiple_trajectories": {
                "met": True,
                "explanation": "Explica por qué múltiples PRs similares existen — son automáticos",
                "num_trajectories_explained": 2,
            },
            "c3_elimination_changes_decisions": {
                "met": False,
                "counterfactual": "Si los PRs no fueran automáticos, no existirían",
                "issue": "Esto no es un contrafactual sobre constraint — es sobre el origen del PR",
            },
            "c4_falsifiable": {
                "met": True,
                "falsification": "Si los actores son humanos reales → falsada",
            },
        },
        "criteria_met_count": 3,
        "operational_status": "PARTIALLY_OPERATIONAL",
    },
    # === CONV-000002: stacklevel warnings.warn() ===
    {
        "convergence_id": "CONV-000002",
        "hypothesis_id": "A",
        "description": "Restricción conceptual: la semántica de warnings debe preservarse",
        "restriction_type": "conceptual",
        "criteria": {
            "c1_observable_predictions": {
                "met": True,
                "prediction": "Los PRs mencionarán que el warning aparece en el lugar equivocado",
                "evidence_needed": "Examinar el cuerpo de los 5 PRs",
            },
            "c2_explains_multiple_trajectories": {
                "met": True,
                "explanation": "Explica por qué 5 actores distintos chocaron con la misma barrera",
                "num_trajectories_explained": 5,
            },
            "c3_elimination_changes_decisions": {
                "met": True,
                "counterfactual": "Si warnings.warn() tuviera stacklevel=2 por defecto, estos PRs no serían necesarios",
                "evidence_needed": "Verificar que Python's default es stacklevel=1",
            },
            "c4_falsifiable": {
                "met": True,
                "falsification": "Si los PRs no mencionan la semántica de warnings → falsada",
            },
        },
        "criteria_met_count": 4,
        "operational_status": "OPERATIONAL",
    },
    {
        "convergence_id": "CONV-000002",
        "hypothesis_id": "B",
        "description": "Limitación técnica: warnings.warn() requiere stacklevel explícito",
        "restriction_type": "tecnica",
        "criteria": {
            "c1_observable_predictions": {
                "met": True,
                "prediction": "La documentación de Python mostrará que stacklevel=1 es el default",
                "evidence_needed": "Examinar Python docs para warnings.warn()",
            },
            "c2_explains_multiple_trajectories": {
                "met": True,
                "explanation": "Explica por qué es fácil olvidar stacklevel — es un default incorrecto",
                "num_trajectories_explained": 5,
            },
            "c3_elimination_changes_decisions": {
                "met": True,
                "counterfactual": "Si Python cambiara el default a stacklevel=2, la constraint desaparece",
                "evidence_needed": "Verificar que esto no ha cambiado en Python 3.14",
            },
            "c4_falsifiable": {
                "met": True,
                "falsification": "Si Python cambiara el default → la constraint desaparece",
            },
        },
        "criteria_met_count": 4,
        "operational_status": "OPERATIONAL",
    },
    {
        "convergence_id": "CONV-000002",
        "hypothesis_id": "C",
        "description": "Coste de refactorización: añadir stacklevel requiere tocar muchas llamadas",
        "restriction_type": "historica",
        "criteria": {
            "c1_observable_predictions": {
                "met": True,
                "prediction": "Los PRs abandonados fueron cerrados por conflictos de merge o scope",
                "evidence_needed": "Examinar los motivos de cierre de los PRs",
            },
            "c2_explains_multiple_trajectories": {
                "met": True,
                "explanation": "Explica por qué los PRs fueron abandonados — no por la idea, sino por el coste",
                "num_trajectories_explained": 5,
            },
            "c3_elimination_changes_decisions": {
                "met": False,
                "counterfactual": "Si el coste de refactorización fuera menor, los PRs se habrían mergeado",
                "issue": "El contrafactual es especulativo — no podemos medir 'coste de refactorización' objetivamente",
            },
            "c4_falsifiable": {
                "met": True,
                "falsification": "Si los PRs fueron cerrados por otras razones (no conflictos) → falsada",
            },
        },
        "criteria_met_count": 3,
        "operational_status": "PARTIALLY_OPERATIONAL",
    },
    # === CONV-000003: mutable container from_checkpoint ===
    {
        "convergence_id": "CONV-000003",
        "hypothesis_id": "A",
        "description": "Restricción conceptual: modelo de mutabilidad asume inmutabilidad pero copia superficial",
        "restriction_type": "conceptual",
        "criteria": {
            "c1_observable_predictions": {
                "met": True,
                "prediction": "from_checkpoint usa shallow copy (= o .copy()) en lugar de deepcopy",
                "evidence_needed": "Examinar el código de from_checkpoint",
            },
            "c2_explains_multiple_trajectories": {
                "met": True,
                "explanation": "Explica por qué 2 actores distintos encontraron el mismo bug de mutabilidad",
                "num_trajectories_explained": 2,
            },
            "c3_elimination_changes_decisions": {
                "met": True,
                "counterfactual": "Si from_checkpoint usara deepcopy, estos PRs no serían necesarios",
                "evidence_needed": "Verificar que el fix usa deepcopy",
            },
            "c4_falsifiable": {
                "met": True,
                "falsification": "Si from_checkpoint ya hace deep copy → falsada",
            },
        },
        "criteria_met_count": 4,
        "operational_status": "OPERATIONAL",
    },
    {
        "convergence_id": "CONV-000003",
        "hypothesis_id": "B",
        "description": "Limitación técnica: Python no distingue copia superficial de profunda por defecto",
        "restriction_type": "tecnica",
        "criteria": {
            "c1_observable_predictions": {
                "met": True,
                "prediction": "El código usa = o .copy() en lugar de copy.deepcopy()",
                "evidence_needed": "Examinar el código",
            },
            "c2_explains_multiple_trajectories": {
                "met": True,
                "explanation": "Explica por qué es fácil cometer este error en Python",
                "num_trajectories_explained": 2,
            },
            "c3_elimination_changes_decisions": {
                "met": False,
                "counterfactual": "Si Python tuviera deep copy por defecto, el bug no existiría",
                "issue": "Esto es una afirmación sobre el lenguaje, no sobre la constraint específica",
            },
            "c4_falsifiable": {
                "met": True,
                "falsification": "Si ya se usa copy.deepcopy() → falsada",
            },
        },
        "criteria_met_count": 3,
        "operational_status": "PARTIALLY_OPERATIONAL",
    },
    {
        "convergence_id": "CONV-000003",
        "hypothesis_id": "C",
        "description": "Artefacto del linker: misma persona con cuentas diferentes",
        "restriction_type": "tecnica",
        "criteria": {
            "c1_observable_predictions": {
                "met": True,
                "prediction": "Los perfiles de GitHub mostrarán que son la misma persona",
                "evidence_needed": "Examinar perfiles de GitHub",
            },
            "c2_explains_multiple_trajectories": {
                "met": False,
                "explanation": "Si son la misma persona, no son trayectorias independientes",
                "issue": "Esta hypothesis niega la convergence, no la explica",
            },
            "c3_elimination_changes_decisions": {
                "met": False,
                "counterfactual": "N/A — si son la misma persona, no hay convergence",
                "issue": "No aplica",
            },
            "c4_falsifiable": {
                "met": True,
                "falsification": "Si los perfiles son claramente diferentes → falsada",
            },
        },
        "criteria_met_count": 2,
        "operational_status": "NOT_OPERATIONAL",
    },
    # === CONV-000004: retry sleep max_interval ===
    {
        "convergence_id": "CONV-000004",
        "hypothesis_id": "A",
        "description": "Restricción conceptual: semántica de retry asume jitter < max_interval pero no lo garantiza",
        "restriction_type": "conceptual",
        "criteria": {
            "c1_observable_predictions": {
                "met": True,
                "prediction": "El código calcula jitter antes de aplicar el cap de max_interval",
                "evidence_needed": "Examinar el código de retry",
            },
            "c2_explains_multiple_trajectories": {
                "met": True,
                "explanation": "Explica por qué 2 actores distintos encontraron el mismo bug",
                "num_trajectories_explained": 2,
            },
            "c3_elimination_changes_decisions": {
                "met": True,
                "counterfactual": "Si el cap se aplicara después del jitter, estos PRs no serían necesarios",
                "evidence_needed": "Verificar el orden de operaciones en el código",
            },
            "c4_falsifiable": {
                "met": True,
                "falsification": "Si el cap ya se aplica después del jitter → falsada",
            },
        },
        "criteria_met_count": 4,
        "operational_status": "OPERATIONAL",
    },
    {
        "convergence_id": "CONV-000004",
        "hypothesis_id": "B",
        "description": "Limitación matemática: la fórmula de jitter produce valores que exceden max_interval",
        "restriction_type": "matematica",
        "criteria": {
            "c1_observable_predictions": {
                "met": True,
                "prediction": "La fórmula jitter = base * (1 + factor * random) puede producir valores > max_interval",
                "evidence_needed": "Analizar la fórmula matemáticamente",
            },
            "c2_explains_multiple_trajectories": {
                "met": True,
                "explanation": "Explica por qué el bug es reproducible — es matemático",
                "num_trajectories_explained": 2,
            },
            "c3_elimination_changes_decisions": {
                "met": True,
                "counterfactual": "Si la fórmula garantizara jitter <= max_interval, los PRs no serían necesarios",
                "evidence_needed": "Verificar la fórmula",
            },
            "c4_falsifiable": {
                "met": True,
                "falsification": "Si la fórmula garantiza jitter <= max_interval → falsada",
            },
        },
        "criteria_met_count": 4,
        "operational_status": "OPERATIONAL",
    },
    {
        "convergence_id": "CONV-000004",
        "hypothesis_id": "C",
        "description": "Restricción histórica: código heredado de tenacity sin cap",
        "restriction_type": "historica",
        "criteria": {
            "c1_observable_predictions": {
                "met": True,
                "prediction": "El historial mostrará que el código viene de tenacity y no tenía cap",
                "evidence_needed": "Examinar git blame del código de retry",
            },
            "c2_explains_multiple_trajectories": {
                "met": True,
                "explanation": "Explica por qué el cap no existía — era heredado",
                "num_trajectories_explained": 2,
            },
            "c3_elimination_changes_decisions": {
                "met": False,
                "counterfactual": "Si el código no viniera de tenacity, el cap podría haber existido",
                "issue": "Especulativo — no podemos saber si tenacity influyó en la decision",
            },
            "c4_falsifiable": {
                "met": True,
                "falsification": "Si el código no viene de tenacity → falsada",
            },
        },
        "criteria_met_count": 3,
        "operational_status": "PARTIALLY_OPERATIONAL",
    },
]


def main():
    print("=" * 70)
    print("SPRINT 62 — Operationalization of Constraints")
    print("=" * 70)
    print(f"Hypotheses to evaluate: {len(HYPOTHESES_EVALUATION)}")
    print()

    # Evaluar cada hypothesis
    for h in HYPOTHESES_EVALUATION:
        conv = h["convergence_id"]
        hid = h["hypothesis_id"]
        status = h["operational_status"]
        count = h["criteria_met_count"]
        print(f"  {conv} H{hid}: {status} ({count}/4 criteria met)")

    # Calcular métricas
    total = len(HYPOTHESES_EVALUATION)
    operational = sum(1 for h in HYPOTHESES_EVALUATION if h["operational_status"] == "OPERATIONAL")
    partially = sum(1 for h in HYPOTHESES_EVALUATION if h["operational_status"] == "PARTIALLY_OPERATIONAL")
    not_operational = sum(1 for h in HYPOTHESES_EVALUATION if h["operational_status"] == "NOT_OPERATIONAL")

    # Contar predicciones observables generadas
    predictions_generated = sum(
        1 for h in HYPOTHESES_EVALUATION
        if h["criteria"]["c1_observable_predictions"]["met"]
    )

    # Contar contrafactuales definidos
    counterfactuals_defined = sum(
        1 for h in HYPOTHESES_EVALUATION
        if h["criteria"]["c3_elimination_changes_decisions"]["met"]
    )

    # Veredicto
    pct_operational = operational / total * 100
    if pct_operational >= 50:
        verdict = "GREEN — definition works, most hypotheses are operational"
    elif pct_operational >= 25:
        verdict = "YELLOW — some hypotheses operational, needs refinement"
    else:
        verdict = "RED — 'restriction' is not yet an operational variable"

    print()
    print("=" * 70)
    print("SUMMARY")
    print("=" * 70)
    print(f"Total hypotheses:           {total}")
    print(f"OPERATIONAL (4/4):          {operational} ({operational/total*100:.0f}%)")
    print(f"PARTIALLY_OPERATIONAL (3/4): {partially} ({partially/total*100:.0f}%)")
    print(f"NOT_OPERATIONAL (≤2/4):     {not_operational} ({not_operational/total*100:.0f}%)")
    print()
    print(f"Observable predictions generated: {predictions_generated}/{total}")
    print(f"Counterfactuals defined:          {counterfactuals_defined}/{total}")
    print()
    print(f"VERDICT: {verdict}")

    # Crear reporte
    report = {
        "report_id": f"OPCON-{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S')}",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "sprint": "SPRINT 62 — Operationalization of Constraints",
        "objective": (
            "Definir operacionalmente qué es una constraint. "
            "Evaluar 12 hypothesis contra 4 criterios operacionales."
        ),
        "operational_definition": {
            "criterion_1": "Genera predicciones observables",
            "criterion_2": "Explica más de una trayectoria independiente",
            "criterion_3": "Su eliminación cambia el espacio de decisiones",
            "criterion_4": "Puede ser falsada",
            "rule": "Una constraint existe si y solo si cumple los 4 criterios",
        },
        "summary": {
            "total_hypotheses": total,
            "operational_4_4": operational,
            "partially_operational_3_4": partially,
            "not_operational_le_2_4": not_operational,
            "pct_operational": round(pct_operational, 1),
            "observable_predictions_generated": predictions_generated,
            "counterfactuals_defined": counterfactuals_defined,
        },
        "verdict": verdict,
        "criteria": {
            "green": "≥50% hypotheses operational (4/4 criteria)",
            "yellow": "25-50% operational",
            "red": "<25% operational — 'restriction' not yet operational",
        },
        "hypotheses": HYPOTHESES_EVALUATION,
        "key_finding": (
            "Las hypothesis que fallan más a menudo son en el Criterio 3 "
            "(eliminación cambia el espacio de decisiones). Esto significa "
            "que es fácil generar predicciones y falsaciones, pero difícil "
            "demostrar que la constraint es causal — no solo correlacional. "
            "Esto explica por qué κ = -0.030: la variable no está "
            "suficientemente operacionalizada para que dos revisores "
            "la identifiquen independientemente."
        ),
        "epistemic_note": (
            "Este experimento NO valida ni falsa la existencia de constraints. "
            "Solo evalúa si las hypothesis propuestas son operacionalmente "
            "definidas. El resultado es: algunas sí, algunas no. "
            "La variable 'constraint' está PARTIALLY_OPERATIONAL."
        ),
        "connection_to_sprint61": {
            "kappa_is_real": -0.030,
            "kappa_hypothesis": -0.067,
            "explanation": (
                "El κ bajo puede deberse a que 'constraint compartida' "
                "no es una variable suficientemente operacionalizada. "
                "Si los criterios operacionales se refinan, κ debería mejorar."
            ),
        },
    }

    # Guardar
    output_path = Path("artifacts/constraint_operationalization.json")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, ensure_ascii=False, default=str)

    print()
    print(f"Output: {output_path}")
    print("=" * 70)

    return 0


if __name__ == "__main__":
    sys.exit(main())