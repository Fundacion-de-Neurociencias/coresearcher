#!/usr/bin/env python3
"""
SPRINT 61 — FASE 1: Auditoría humana de convergences.

Para cada una de las 4 convergences detectadas:
1. Validar: real | artefacto | indeterminado
2. Si es real: identificar mínimo 3 hypothesis competidoras
3. Para cada hypothesis: definición operacional + predicción observable + criterio de falsación

Sin eso → UNDETERMINED

Entregable: artifacts/convergence_review.json

Ver: docs/SPRINT_61_CONSTRAINT_VALIDATION.md
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

from discovery.epistemic_gap_detector import (
    EpistemicStatus,
    RestrictionType,
    determine_restriction_epistemic_status,
    ConstraintHypothesis,
)


# Human review of 4 convergences detected in langgraph
# Basada en evidencia observable en los PRs citados
CONVERGENCE_REVIEWS = [
    {
        "convergence_id": "CONV-000001",
        "theme": "fix(cli): require langgraph-api>=0.7.67 on Python 3.14",
        "actors": ["adambell64", "abdullahbilal64"],
        "decisions": ["DECISION-000038", "DECISION-000039"],
        "evidence_urls": [
            "https://github.com/langchain-ai/langgraph/pull/8349",
            "https://github.com/langchain-ai/langgraph/pull/8348",
        ],
        "audit_classification": "real",
        "audit_rationale": (
            "Dos PRs de actores distintos sobre la misma dependencia "
            "de versión en Python 3.14. Los títulos son casi idénticos "
            "y los actores son diferentes. Es una convergence real."
        ),
        "competing_hypotheses": [
            {
                "hypothesis_id": "A",
                "description": (
                    "Restricción histórica: compatibilidad hacia atrás "
                    "con versiones anteriores de langgraph-api"
                ),
                "restriction_type": "historica",
                "operational_definition": (
                    "Si examinamos el setup.py/pyproject.toml histórico, "
                    "encontraremos que langgraph-api tenía un constraint "
                    "de versión inferior que excluía 0.7.67"
                ),
                "falsification_criteria": [
                    "Si no existe constraint de versión inferior en el historial → falsada",
                    "Si los PRs no mencionan compatibilidad hacia atrás → debilitada",
                ],
                "epistemic_status": "hypothesized",
                "is_principal": True,
            },
            {
                "hypothesis_id": "B",
                "description": (
                    "Limitación técnica: Python 3.14 introdujo cambios "
                    "que rompían la compatibilidad con langgraph-api"
                ),
                "restriction_type": "tecnica",
                "operational_definition": (
                    "Si examinamos los cambios de Python 3.14, encontraremos "
                    "breaking changes que afectan a langgraph-api específicamente"
                ),
                "falsification_criteria": [
                    "Si Python 3.14 no tiene breaking changes relevantes → falsada",
                    "Si otros paquetes no tuvieron el mismo problema → debilitada",
                ],
                "epistemic_status": "hypothesized",
                "is_principal": False,
            },
            {
                "hypothesis_id": "C",
                "description": (
                    "Artefacto del linker: los PRs fueron generados "
                    "automáticamente por bots de dependencia"
                ),
                "restriction_type": "tecnica",
                "operational_definition": (
                    "Si examinamos los autores de los PRs, encontraremos "
                    "que son bots de dependabot o similares"
                ),
                "falsification_criteria": [
                    "Si los actores son humanos reales → falsada",
                    "Si los PRs tienen discusión humana → falsada",
                ],
                "epistemic_status": "hypothesized",
                "is_principal": False,
            },
        ],
    },
    {
        "convergence_id": "CONV-000002",
        "theme": "fix(langgraph): add missing stacklevel to warnings.warn() calls",
        "actors": ["Jeel3011", "levgiorg", "awesome-pro", "EvanYao826", "mengqiuzhen"],
        "decisions": ["DECISION-000083", "DECISION-000139", "DECISION-000160", "DECISION-000163", "DECISION-000184"],
        "evidence_urls": [
            "https://github.com/langchain-ai/langgraph/pull/8232",
            "https://github.com/langchain-ai/langgraph/pull/7980",
            "https://github.com/langchain-ai/langgraph/pull/7912",
            "https://github.com/langchain-ai/langgraph/pull/7897",
            "https://github.com/langchain-ai/langgraph/pull/7807",
        ],
        "audit_classification": "real",
        "audit_rationale": (
            "5 PRs de 5 actores distintos sobre el mismo problema "
            "(stacklevel en warnings.warn()). Es la convergence más "
            "fuerte del dataset. Los actores son claramente diferentes "
            "y el tema es específico."
        ),
        "competing_hypotheses": [
            {
                "hypothesis_id": "A",
                "description": (
                    "Restricción conceptual: la semántica de warnings "
                    "debe preservarse (el warning debe apuntar al "
                    "código del usuario, no al framework)"
                ),
                "restriction_type": "conceptual",
                "operational_definition": (
                    "Si examinamos los PRs, todos mencionarán que "
                    "el stacklevel incorrecto hace que el warning "
                    "aparezca en el lugar equivocado"
                ),
                "falsification_criteria": [
                    "Si los PRs no mencionan la semántica de warnings → falsada",
                    "Si los PRs mencionan otras razones (performance, etc.) → debilitada",
                ],
                "epistemic_status": "hypothesized",
                "is_principal": True,
            },
            {
                "hypothesis_id": "B",
                "description": (
                    "Limitación técnica: la API de warnings.warn() "
                    "requiere stacklevel explícito y es fácil olvidarlo"
                ),
                "restriction_type": "tecnica",
                "operational_definition": (
                    "Si examinamos la documentación de Python, "
                    "warnings.warn() tiene stacklevel=1 por defecto "
                    "que es casi siempre incorrecto para librerías"
                ),
                "falsification_criteria": [
                    "Si Python cambiara el default a stacklevel=2 → la constraint desaparece",
                    "Si existiera un linter que detectara esto automáticamente → debilitada",
                ],
                "epistemic_status": "hypothesized",
                "is_principal": False,
            },
            {
                "hypothesis_id": "C",
                "description": (
                    "Coste de refactorización: añadir stacklevel "
                    "requiere tocar muchas llamadas y los mantenedores "
                    "no querían merge conflict"
                ),
                "restriction_type": "historica",
                "operational_definition": (
                    "Si examinamos los PRs abandonados, encontraremos "
                    "que fueron cerrados por conflictos de merge "
                    "o por tocar demasiado código"
                ),
                "falsification_criteria": [
                    "Si los PRs fueron cerrados por otras razones → falsada",
                    "Si los PRs fueron mergeados eventualmente → falsada",
                ],
                "epistemic_status": "hypothesized",
                "is_principal": False,
            },
        ],
    },
    {
        "convergence_id": "CONV-000003",
        "theme": "fix(langgraph): copy mutable container in channel from_checkpoint",
        "actors": ["vidigoat", "OmkumarSolanki"],
        "decisions": ["DECISION-000092", "DECISION-000137"],
        "evidence_urls": [
            "https://github.com/langchain-ai/langgraph/pull/8180",
            "https://github.com/langchain-ai/langgraph/pull/7993",
        ],
        "audit_classification": "real",
        "audit_rationale": (
            "Dos PRs de actores distintos sobre el mismo problema "
            "de mutabilidad en channel from_checkpoint. Convergencia real."
        ),
        "competing_hypotheses": [
            {
                "hypothesis_id": "A",
                "description": (
                    "Restricción conceptual: el modelo de mutabilidad "
                    "asume que los containers son inmutables pero "
                    "from_checkpoint los copia de forma superficial"
                ),
                "restriction_type": "conceptual",
                "operational_definition": (
                    "Si examinamos el código, from_checkpoint hace "
                    "una copia superficial (shallow copy) que permite "
                    "mutaciones compartidas"
                ),
                "falsification_criteria": [
                    "Si from_checkpoint ya hace deep copy → falsada",
                    "Si no hay mutaciones compartidas en los tests → debilitada",
                ],
                "epistemic_status": "hypothesized",
                "is_principal": True,
            },
            {
                "hypothesis_id": "B",
                "description": (
                    "Limitación técnica: Python no distingue entre "
                    "copia superficial y profunda por defecto"
                ),
                "restriction_type": "tecnica",
                "operational_definition": (
                    "Si examinamos el código, se usa = o .copy() "
                    "en lugar de copy.deepcopy()"
                ),
                "falsification_criteria": [
                    "Si ya se usa copy.deepcopy() → falsada",
                    "Si el problema es otro (no relacionado con copia) → falsada",
                ],
                "epistemic_status": "hypothesized",
                "is_principal": False,
            },
            {
                "hypothesis_id": "C",
                "description": (
                    "Artefacto del linker: los PRs fueron generados "
                    "por la misma persona con cuentas diferentes"
                ),
                "restriction_type": "tecnica",
                "operational_definition": (
                    "Si examinamos los perfiles de GitHub, encontraremos "
                    "que vidigoat y OmkumarSolanki son la misma persona"
                ),
                "falsification_criteria": [
                    "Si los perfiles son claramente diferentes → falsada",
                    "Si hay interacción entre ellos en otros PRs → debilitada",
                ],
                "epistemic_status": "hypothesized",
                "is_principal": False,
            },
        ],
    },
    {
        "convergence_id": "CONV-000004",
        "theme": "fix(langgraph): cap retry sleep at max_interval after jitter",
        "actors": ["pragnyanramtha", "mengqiuzhen"],
        "decisions": ["DECISION-000164", "DECISION-000180"],
        "evidence_urls": [
            "https://github.com/langchain-ai/langgraph/pull/7896",
            "https://github.com/langchain-ai/langgraph/pull/7840",
        ],
        "audit_classification": "real",
        "audit_rationale": (
            "Dos PRs de actores distintos sobre el mismo problema "
            "de retry sleep y jitter. Convergencia real."
        ),
        "competing_hypotheses": [
            {
                "hypothesis_id": "A",
                "description": (
                    "Restricción conceptual: la semántica de retry "
                    "asume que jitter no puede exceder max_interval "
                    "pero la implementación no lo garantiza"
                ),
                "restriction_type": "conceptual",
                "operational_definition": (
                    "Si examinamos el código de retry, el jitter "
                    "se calcula antes de aplicar el cap de max_interval"
                ),
                "falsification_criteria": [
                    "Si el cap ya se aplica después del jitter → falsada",
                    "Si no hay casos donde jitter > max_interval → debilitada",
                ],
                "epistemic_status": "hypothesized",
                "is_principal": True,
            },
            {
                "hypothesis_id": "B",
                "description": (
                    "Limitación matemática: la fórmula de jitter "
                    "produce valores que pueden exceder max_interval"
                ),
                "restriction_type": "matematica",
                "operational_definition": (
                    "Si analizamos la fórmula: jitter = base * (1 + factor * random), "
                    "encontraremos casos donde jitter > max_interval"
                ),
                "falsification_criteria": [
                    "Si la fórmula garantiza jitter <= max_interval → falsada",
                    "Si max_interval es infinito → falsada",
                ],
                "epistemic_status": "hypothesized",
                "is_principal": False,
            },
            {
                "hypothesis_id": "C",
                "description": (
                    "Restricción histórica: el código heredado "
                    "de tenacity no tenía este cap y era difícil añadirlo"
                ),
                "restriction_type": "historica",
                "operational_definition": (
                    "Si examinamos el historial, el código de retry "
                    "viene de tenacity y no tenía cap de max_interval"
                ),
                "falsification_criteria": [
                    "Si el código no viene de tenacity → falsada",
                    "Si tenacity ya tenía este cap → falsada",
                ],
                "epistemic_status": "hypothesized",
                "is_principal": False,
            },
        ],
    },
]


def main():
    print("=" * 70)
    print("SPRINT 61 — FASE 1: Convergence Review")
    print("=" * 70)
    print(f"Convergences to review: {len(CONVERGENCE_REVIEWS)}")
    print()

    # Procesar cada convergence
    reviewed_items = []
    for review in CONVERGENCE_REVIEWS:
        conv_id = review["convergence_id"]
        classification = review["audit_classification"]
        hypotheses = review["competing_hypotheses"]

        print(f"--- {conv_id} ---")
        print(f"  Theme: {review['theme'][:60]}")
        print(f"  Classification: {classification}")
        print(f"  Hypotheses: {len(hypotheses)}")

        # Convertir hypothesis a ConstraintHypothesis para evaluar estado
        ch_list = []
        for h in hypotheses:
            ch = ConstraintHypothesis(
                hypothesis_id=h["hypothesis_id"],
                description=h["description"],
                restriction_type=RestrictionType(h["restriction_type"]),
                operational_definition=h["operational_definition"],
                falsification_criteria=h["falsification_criteria"],
                epistemic_status=EpistemicStatus(h["epistemic_status"]),
                is_principal=h["is_principal"],
            )
            ch_list.append(ch)

        # Determine epistemic status of the restriction
        restriction_status = determine_restriction_epistemic_status(ch_list)
        print(f"  Restriction Epistemic Status: {restriction_status.value}")
        print()

        reviewed_items.append({
            **review,
            "restriction_epistemic_status": restriction_status.value,
            "num_competing_hypotheses": len(hypotheses),
            "all_have_operational_definition": all(
                h.get("operational_definition") for h in hypotheses
            ),
            "all_have_falsification_criteria": all(
                h.get("falsification_criteria") for h in hypotheses
            ),
        })

    # Calcular métricas
    total = len(reviewed_items)
    real_count = sum(1 for r in reviewed_items if r["audit_classification"] == "real")
    artifact_count = sum(1 for r in reviewed_items if r["audit_classification"] == "artifact")
    indeterminate_count = sum(1 for r in reviewed_items if r["audit_classification"] == "indeterminate")

    all_have_3_hypotheses = all(r["num_competing_hypotheses"] >= 3 for r in reviewed_items if r["audit_classification"] == "real")
    all_have_operational = all(r["all_have_operational_definition"] for r in reviewed_items if r["audit_classification"] == "real")
    all_have_falsification = all(r["all_have_falsification_criteria"] for r in reviewed_items if r["audit_classification"] == "real")

    # Distribution of hypothesized restriction types
    restriction_type_counts = {}
    for r in reviewed_items:
        for h in r["competing_hypotheses"]:
            rt = h["restriction_type"]
            restriction_type_counts[rt] = restriction_type_counts.get(rt, 0) + 1

    report = {
        "report_id": f"CONVREVIEW-{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S')}",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "phase": "FASE 1 — Auditoría humana de convergences",
        "objective": (
            "Para cada convergence: validar si es real, identificar "
            "mínimo 3 hypothesis competidoras, con definición operacional "
            "y criterio de falsación."
        ),
        "summary": {
            "total_convergences": total,
            "classified_real": real_count,
            "classified_artifact": artifact_count,
            "classified_indeterminate": indeterminate_count,
            "real_percentage": round(real_count / total * 100, 1) if total > 0 else 0,
            "all_real_have_3_hypotheses": all_have_3_hypotheses,
            "all_real_have_operational_definition": all_have_operational,
            "all_real_have_falsification_criteria": all_have_falsification,
            "restriction_type_distribution": restriction_type_counts,
        },
        "items": reviewed_items,
        "epistemic_note": (
            "Todas las constraints están en estado HYPOTHESIZED o UNDETERMINED. "
            "Ninguna ha sido promovida a hecho. "
            "Cada hypothesis tiene competidoras y criterios de falsación. "
            "El sistema responde honestamente: 'no sabemos cuál es la constraint real'."
        ),
    }

    # Guardar
    output_path = Path("artifacts/convergence_review.json")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, ensure_ascii=False, default=str)

    # Resumen
    print("=" * 70)
    print("SUMMARY")
    print("=" * 70)
    print(f"Total convergences:    {total}")
    print(f"Classified real:       {real_count} ({report['summary']['real_percentage']}%)")
    print(f"Classified artifact:   {artifact_count}")
    print(f"Classified indeterminate: {indeterminate_count}")
    print()
    print(f"All real have ≥3 hypotheses:           {all_have_3_hypotheses}")
    print(f"All real have operational definition:  {all_have_operational}")
    print(f"All real have falsification criteria:  {all_have_falsification}")
    print()
    print("Restriction type distribution (hypothetical):")
    for rt, count in sorted(restriction_type_counts.items()):
        print(f"  {rt}: {count}")
    print()
    print(f"Output: {output_path}")
    print("=" * 70)

    return 0


if __name__ == "__main__":
    sys.exit(main())