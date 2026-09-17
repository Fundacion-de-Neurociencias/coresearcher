#!/usr/bin/env python3
"""
Auditoría 2: Validar las convergences detectadas.

Responde: Are they real convergences? o Did the linker create them artificially?

Para cada convergence, presenta:
- El tema
- Los actores independientes
- Las decisiones involucradas
- Las URLs de evidencia
- Campo para clasificación manual: real | linker_artifact | indeterminate

Directiva IDE (SPRINT 60C/H7 — v1.6):
1. Tratar toda constraint como variable latente.
2. Tratar toda convergence como observación.
3. Prohibido promover una constraint a hecho.
4. Cada hypothesis de constraint debe tener al menos una hypothesis competidora.
5. Incorporar Epistemic Status: OBSERVED | DERIVED | HYPOTHESIZED | FALSIFIED | UNDETERMINED
6. Si dos hypothesis explican igualmente bien una convergence → UNDETERMINED.
7. El sistema debe poder responder "no sabemos" sin degradar la evaluación.

Prohibición de "wishful mnemonic" (McDermott):
- ❌ "constraint detectada"
- ✔ "hypothesis de constraint que explica la convergence observada"
- Prohibido introducir términos ontológicamente cargados sin
  definición operacional y criterio de falsación.

Usage:
  python scripts/audit_convergences.py
  python scripts/audit_convergences.py --input artifacts/epistemic_gap_report.json
"""
import sys
import json
from pathlib import Path

# Add python/ to path for imports
project_root = Path(__file__).resolve().parent.parent
python_dir = project_root / "python"
if str(python_dir) not in sys.path:
    sys.path.insert(0, str(python_dir))

from discovery.epistemic_gap_detector import (
    RestrictionType,
    EpistemicStatus,
    determine_restriction_epistemic_status,
)


def main():
    import argparse

    parser = argparse.ArgumentParser(
        description="Audit convergences: are they real or linker artifacts?"
    )
    parser.add_argument(
        "--input",
        default="artifacts/epistemic_gap_report.json",
        help="Path to epistemic_gap_report.json",
    )
    parser.add_argument(
        "--output",
        default="artifacts/epistemic_gap_convergence_audit.json",
        help="Output audit file",
    )
    args = parser.parse_args()

    input_path = Path(args.input)
    if not input_path.exists():
        print(f"ERROR: Input file not found: {input_path}")
        return 1

    with open(input_path, "r", encoding="utf-8") as f:
        report = json.load(f)

    convergences = report.get("convergences", [])
    gaps = {g["gap_id"]: g for g in report.get("gaps", [])}

    print("=" * 70)
    print("AUDITORÍA 2: Convergences")
    print("=" * 70)
    print(f"Total convergences to audit: {len(convergences)}")
    print()

    audit_items = []
    for conv in convergences:
        conv_id = conv.get("convergence_id", "")
        conv_type = conv.get("type", "")
        theme = conv.get("theme", "")
        actors = conv.get("independent_actors", [])
        decisions = conv.get("decisions", [])
        description = conv.get("description", "")

        print(f"--- {conv_id} ({conv_type}) ---")
        print(f"  Theme: {theme}")
        print(f"  Actors: {', '.join(actors)}")
        print(f"  Description: {description}")
        print(f"  Decisions: {', '.join(decisions)}")
        print()

        # Search for gaps associated with these decisions
        related_gaps = []
        for gap in report.get("gaps", []):
            if gap.get("location") in decisions:
                related_gaps.append({
                    "gap_id": gap["gap_id"],
                    "gap_type": gap["gap_type"],
                    "description": gap["description"][:100],
                    "evidence_anchor": gap["evidence_anchor"],
                })

        # Epistemic status from detector (v1.6)
        conv_epistemic_status = conv.get("epistemic_status", EpistemicStatus.OBSERVED.value)
        conv_restriction_status = conv.get(
            "restriction_epistemic_status", EpistemicStatus.UNDETERMINED.value
        )

        audit_items.append({
            "convergence_id": conv_id,
            "type": conv_type,
            "theme": theme,
            "independent_actors": actors,
            "decisions": decisions,
            "description": description,
            "related_gaps": related_gaps,
            # v1.6 — Epistemic Status (Directiva IDE)
            "epistemic_status": conv_epistemic_status,  # convergence = OBSERVED
            "restriction_epistemic_status": conv_restriction_status,  # restriction = UNDETERMINED until audited
            "audit_questions": [
                "Are the actors truly independent (no es el mismo equipo/persona)?",
                "Is the topic truly the same (no es coincidencia léxica)?",
                "El outcome es realmente convergente (no es extracción errónea)?",
                "Esta convergence representa una barrera real o un patrón del linker?",
                # Regla conceptual v1.3:
                "Qué constraint compartida explica esta convergence?",
                "La constraint es técnica, conceptual, histórica, matemática u ontológica?",
                "Los actores asumían implícitamente algo que limitaba sus opciones?",
                # v1.6 — Directiva IDE:
                "Cuál es la definición operacional de la constraint propuesta?",
                "Qué observación falsaría esta hypothesis de constraint?",
                "Existe al menos una hypothesis competidora que explique la misma convergence?",
            ],
            "hypothetical_restriction": None,  # To be filled: shared restriction
            "restriction_type": None,  # technica | conceptual | historica | matematica | ontologica
            # v1.6 — Competing hypotheses with operational definition + falsification
            "competing_hypotheses": [
                {
                    "hypothesis_id": "A",
                    "description": None,  # To be filled: hypothesis principal
                    "restriction_type": None,
                    "operational_definition": None,  # v1.6: definición operacional obligatoria
                    "falsification_criteria": None,  # v1.6: mandatory falsification criterion
                    "epistemic_status": EpistemicStatus.HYPOTHESIZED.value,
                    "is_principal": True,
                },
                {
                    "hypothesis_id": "B",
                    "description": None,  # To be filled: hypothesis alternativa 1
                    "restriction_type": None,
                    "operational_definition": None,
                    "falsification_criteria": None,
                    "epistemic_status": EpistemicStatus.HYPOTHESIZED.value,
                    "is_principal": False,
                },
                {
                    "hypothesis_id": "C",
                    "description": None,  # To be filled: hypothesis alternativa 2
                    "restriction_type": None,
                    "operational_definition": None,
                    "falsification_criteria": None,
                    "epistemic_status": EpistemicStatus.HYPOTHESIZED.value,
                    "is_principal": False,
                },
            ],
            "falsification_criteria": [],  # To be filled: cómo falsar B y C
            "audit_classification": None,  # real | linker_artifact | indeterminate
            "audit_notes": "",
            # v1.6 — Wishful mnemonic warning
            "wishful_mnemonic_warning": (
                "Prohibido escribir 'constraint detectada'. "
                "Escribir 'hypothesis de constraint que explica "
                "la convergence observada'. Toda constraint es "
                "variable latente hasta falsar las competidoras."
            ),
        })

    audit_report = {
        "audit_protocol": {
            "total_convergences": len(convergences),
            "classification_options": ["real", "linker_artifact", "indeterminate"],
            "instructions": (
                "For each convergence, answer:\n"
                "  1. Are the actors truly independent?\n"
                "  2. Is the theme truly the same (not lexical coincidence)?\n"
                "  3. Is the outcome truly convergent?\n"
                "  4. Does this represent a real barrier or a linker pattern?\n"
                "Classify as:\n"
                "  real: Genuine convergence of independent trajectories\n"
                "  linker_artifact: Created by the linker, not real convergence\n"
                "  indeterminate: Cannot determine"
            ),
            # v1.6 — Directiva IDE
            "ide_directive": {
                "version": "1.6",
                "principle": (
                    "Una teoría falsa es peor que admitir que "
                    "todavía no tenemos teoría."
                ),
                "rules": [
                    "Toda constraint es variable latente (no observable)",
                    "Toda convergence es observación (no explicación)",
                    "Prohibido promover constraint a hecho",
                    "Toda hypothesis de constraint debe tener competidora",
                    "Toda hypothesis debe tener definición operacional",
                    "Toda hypothesis debe tener criterio de falsación",
                    "Si dos hypothesis explican igualmente bien → UNDETERMINED",
                    "'No sabemos' es estado epistemológico legítimo",
                ],
                "epistemic_status_values": [es.value for es in EpistemicStatus],
                "wishful_mnemonic_prohibition": (
                    "Prohibido introducir términos ontológicamente cargados "
                    "sin definición operacional y criterio de falsación. "
                    "❌ 'constraint detectada' → "
                    "✔ 'hypothesis de constraint que explica la "
                    "convergence observada'"
                ),
            },
        },
        "items": audit_items,
    }

    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(audit_report, f, indent=2, ensure_ascii=False, default=str)

    print(f"Audit file: {output_path}")
    print()
    print("Classify each convergence as: real | linker_artifact | indeterminate")
    print()
    print("v1.6 — Directiva IDE:")
    print("  - Toda constraint es variable latente (no observable)")
    print("  - Toda hypothesis debe tener competidora + definición operacional + falsación")
    print("  - Si dos hypothesis explican igualmente bien → UNDETERMINED")
    print("  - 'No sabemos' es estado epistemológico legítimo")
    print("=" * 70)

    return 0


if __name__ == "__main__":
    sys.exit(main())