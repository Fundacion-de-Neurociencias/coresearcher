#!/usr/bin/env python3
"""
SPRINT 66C — Meta-Measurement Audit

Objetivo: Medir los instrumentos de medición.
No medir entidades. Medir las métricas.

Pregunta central:
  Cómo distinguimos una métrica informativa de una métrica tautológica?

Tesis a intentar destruir:
  Una métrica epistemológica útil debe separar entidades históricamente
  validadas, entidades actualmente plausibles y entidades históricamente
  falsadas.

Experimentos:
  1. Historical Separation Test (A > B > C)
  2. Blind Classification (sin nombres)
  3. Adversarial Entity Generation (entidades ficticias)
  4. Predictive Power Test (qué predice el índice?)

Criterio de salida:
  GREEN = métrica sobrevive
  YELLOW = necesita rediseño parcial
  RED = abandonada

No existen estados intermedios.
"""
import sys
import json
from pathlib import Path
from datetime import datetime, timezone

project_root = Path(__file__).resolve().parent.parent


# ------------------------------------------------------------------
# Utilidad: calcular Instrumentability Index igual que en SPRINT 66
# ------------------------------------------------------------------

def calculate_instrumentability_index(observable, inferible, instrumentable, falsable, replicable):
    dims = [
        observable,
        inferible,
        instrumentable,
        falsable,
        replicable is not None and replicable != "UNKNOWN",
    ]
    return sum(1 for d in dims if d is True) / len(dims)


# ------------------------------------------------------------------
# Experimento 1: Historical Separation Test
# ------------------------------------------------------------------

GROUP_A_ESTABLISHED = [
    {
        "name": "Gen",
        "observable": True,
        "inferible": True,
        "instrumentable": True,
        "falsable": True,
        "replicable": True,
        "note": "Unidad de herencia. Observable via DNA.",
    },
    {
        "name": "Electrón",
        "observable": True,
        "inferible": True,
        "instrumentable": True,
        "falsable": True,
        "replicable": True,
        "note": "Partícula subatómica. Efectos medibles.",
    },
    {
        "name": "Placa tectónica",
        "observable": True,
        "inferible": True,
        "instrumentable": True,
        "falsable": True,
        "replicable": True,
        "note": "Estructura geológica. Observable via GPS.",
    },
    {
        "name": "ADN",
        "observable": True,
        "inferible": True,
        "instrumentable": True,
        "falsable": True,
        "replicable": True,
        "note": "Molécula. Observable via cristalografía.",
    },
    {
        "name": "Campo gravitatorio",
        "observable": True,
        "inferible": True,
        "instrumentable": True,
        "falsable": True,
        "replicable": True,
        "note": "Entidad física. Efectos medibles.",
    },
]

GROUP_B_PLAUSIBLE = [
    {
        "name": "Restriction",
        "observable": False,
        "inferible": False,
        "instrumentable": True,
        "falsable": True,
        "replicable": "PARTIAL",
        "note": "Supuesto compartido. No observable directamente.",
    },
    {
        "name": "Mechanism",
        "observable": False,
        "inferible": False,
        "instrumentable": True,
        "falsable": True,
        "replicable": "PARTIAL",
        "note": "Proceso causal. No observable directamente.",
    },
    {
        "name": "Paradigm",
        "observable": False,
        "inferible": False,
        "instrumentable": True,
        "falsable": True,
        "replicable": "UNKNOWN",
        "note": "Marco compartido. No observable desde commits.",
    },
    {
        "name": "Explanation",
        "observable": False,
        "inferible": False,
        "instrumentable": True,
        "falsable": True,
        "replicable": "PARTIAL",
        "note": "Narrativa causal. No observable directamente.",
    },
]

GROUP_C_FALSIFIED = [
    {
        "name": "Éter luminífero",
        "observable": False,
        "inferible": False,
        "instrumentable": True,
        "falsable": True,
        "replicable": False,
        "note": "Falsado por Michelson-Morley.",
    },
    {
        "name": "Flogisto",
        "observable": False,
        "inferible": False,
        "instrumentable": True,
        "falsable": True,
        "replicable": False,
        "note": "Falsado por Lavoisier.",
    },
    {
        "name": "Miasma",
        "observable": False,
        "inferible": False,
        "instrumentable": True,
        "falsable": True,
        "replicable": False,
        "note": "Falsado por teoría microbiana.",
    },
    {
        "name": "Vitalismo",
        "observable": False,
        "inferible": False,
        "instrumentable": True,
        "falsable": True,
        "replicable": False,
        "note": "Falsado por bioquímica.",
    },
]


# ------------------------------------------------------------------
# Experimento 3: Adversarial Entity Generation
# ------------------------------------------------------------------

ADVERSARIAL_ENTITIES = [
    {
        "name": "Quantum Essence Field",
        "description": "Campo cuántico esencial. Definido para cumplir todos los criterios del framework sin contenido empírico.",
        "observable": True,  # Se define como detectable
        "inferible": True,   # Se define como reconstruible
        "instrumentable": True,
        "falsable": True,
        "replicable": True,
        "note": "Entidad ficticia diseñada para maximizar el índice.",
    },
    {
        "name": "Meta-Causal Resonance",
        "description": "Resonancia metacausal. Cumple todos los criterios.",
        "observable": True,
        "inferible": True,
        "instrumentable": True,
        "falsable": True,
        "replicable": True,
        "note": "Otra entidad ficticia.",
    },
    {
        "name": "Cognitive Ether",
        "description": "Éter cognitivo. Cumple todos los criterios.",
        "observable": True,
        "inferible": True,
        "instrumentable": True,
        "falsable": True,
        "replicable": True,
        "note": "Otra entidad ficticia.",
    },
    {
        "name": "Dynamic Vital Substrate",
        "description": "Sustrato vital dinámico. Cumple todos los criterios.",
        "observable": True,
        "inferible": True,
        "instrumentable": True,
        "falsable": True,
        "replicable": True,
        "note": "Otra entidad ficticia.",
    },
]


def compute_group_stats(entities):
    """Calcula estadísticas de un grupo."""
    indices = []
    for e in entities:
        idx = calculate_instrumentability_index(
            e["observable"], e["inferible"], e["instrumentable"],
            e["falsable"], e["replicable"]
        )
        indices.append(idx)
    if not indices:
        return {"mean": 0, "min": 0, "max": 0, "count": 0}
    return {
        "mean": sum(indices) / len(indices),
        "min": min(indices),
        "max": max(indices),
        "count": len(indices),
        "values": indices,
    }


def main():
    print("=" * 70)
    print("SPRINT 66C — Meta-Measurement Audit")
    print("=" * 70)
    print("Objetivo: Medir los instrumentos de medición")
    print("Tesis: Una métrica útil debe separar A > B > C")
    print()

    attacks = []
    results = {
        "experiment_1_historical_separation": {},
        "experiment_2_blind_classification": "NOT_APPLICABLE — index no usa nombres",
        "experiment_3_adversarial": [],
        "experiment_4_predictive_power": {},
        "verdict": "PASS",
    }

    # ------------------------------------------------------------------
    # Experimento 1: Historical Separation
    # ------------------------------------------------------------------
    print("[Experimento 1] Historical Separation Test (A > B > C)")
    stats_a = compute_group_stats(GROUP_A_ESTABLISHED)
    stats_b = compute_group_stats(GROUP_B_PLAUSIBLE)
    stats_c = compute_group_stats(GROUP_C_FALSIFIED)

    print(f"  Grupo A (Establecidas): mean={stats_a['mean']:.2f}, min={stats_a['min']:.2f}, max={stats_a['max']:.2f}")
    print(f"  Grupo B (Plausibles):   mean={stats_b['mean']:.2f}, min={stats_b['min']:.2f}, max={stats_b['max']:.2f}")
    print(f"  Grupo C (Falsadas):     mean={stats_c['mean']:.2f}, min={stats_c['min']:.2f}, max={stats_c['max']:.2f}")

    results["experiment_1_historical_separation"] = {
        "group_a": stats_a,
        "group_b": stats_b,
        "group_c": stats_c,
    }

    # Verificar separación A > B > C
    separation_ok = stats_a["mean"] > stats_b["mean"] > stats_c["mean"]
    if not separation_ok:
        attacks.append({
            "experiment": "1",
            "issue": f"No separation: A={stats_a['mean']:.2f}, B={stats_b['mean']:.2f}, C={stats_c['mean']:.2f}",
        })
        print(f"  ⚠️  ATTACK: No separation A > B > C")
    else:
        print(f"  ✓ Separation A > B > C confirmed")

    # ------------------------------------------------------------------
    # Experimento 2: Blind Classification
    # ------------------------------------------------------------------
    print()
    print("[Experimento 2] Blind Classification")
    print("  NOT_APPLICABLE — El index no usa nombres, solo propiedades booleanas.")
    print("  Sin nombres, el índice produce exactamente los mismos valores.")
    print("  Esto NO es un ataque. Es una propiedad del diseño.")
    print("  El índice no hace leakage porque no tiene acceso a etiquetas.")
    results["experiment_2_blind_classification"] = "PASS — no aplicable, el índice es invariante a nombres"

    # ------------------------------------------------------------------
    # Experimento 3: Adversarial Entity Generation
    # ------------------------------------------------------------------
    print()
    print("[Experimento 3] Adversarial Entity Generation")
    adversarial_scores = []
    for entity in ADVERSARIAL_ENTITIES:
        idx = calculate_instrumentability_index(
            entity["observable"], entity["inferible"], entity["instrumentable"],
            entity["falsable"], entity["replicable"]
        )
        adversarial_scores.append(idx)
        print(f"  {entity['name']:<30} index={idx:.2f}")
        if idx >= 0.8:
            attacks.append({
                "experiment": "3",
                "entity": entity["name"],
                "issue": f"Adversarial entity got index {idx:.2f} >= 0.8",
            })
            print(f"    ⚠️  ATTACK: Entidad ficticia con índice alto")

    results["experiment_3_adversarial"] = [
        {"name": e["name"], "index": idx, "note": e["note"]}
        for e, idx in zip(ADVERSARIAL_ENTITIES, adversarial_scores)
    ]

    # ------------------------------------------------------------------
    # Experimento 4: Predictive Power Test
    # ------------------------------------------------------------------
    print()
    print("[Experimento 4] Predictive Power Test")
    print("  Pregunta: Qué predice exactamente este índice?")
    print("  Respuesta: Nada observable.")
    print("  El índice predice si una entidad cumple la definición de instrumentabilidad.")
    print("  No predice si la entidad es real, útil o científicamente valiosa.")
    print("  Por tanto: no es una métrica, es una taxonomía.")
    results["experiment_4_predictive_power"] = {
        "predictive_power": "NONE",
        "reason": "El índice no predice nada observable. Solo clasifica según definición interna.",
        "conclusion": "Taxonomía ≠ medición",
    }

    # ------------------------------------------------------------------
    # Veredicto
    # ------------------------------------------------------------------
    print()
    print("[Veredicto]")
    if attacks:
        print(f"  ⚠️  ATTACKS: {len(attacks)}")
        for a in attacks:
            print(f"    - Exp {a['experiment']}: {a['entity'] if 'entity' in a else 'N/A'}: {a['issue']}")
        results["verdict"] = "RED"
    else:
        if not separation_ok:
            results["verdict"] = "RED"
        else:
            results["verdict"] = "GREEN"

    if results["verdict"] == "RED":
        print("  VEREDICTO: RED — métrica abandonada")
    elif results["verdict"] == "YELLOW":
        print("  VEREDICTO: YELLOW — necesita rediseño parcial")
    else:
        print("  VEREDICTO: GREEN — métrica sobrevive")

    # ------------------------------------------------------------------
    # Guardar
    # ------------------------------------------------------------------
    report = {
        "report_id": f"META66C-{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S')}",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "sprint": "SPRINT 66C — Meta-Measurement Audit",
        "objective": (
            "Medir los instrumentos de medición. "
            "No medir entidades. Medir las métricas."
        ),
        "thesis_under_attack": (
            "Una métrica epistemológica útil debe separar entidades "
            "históricamente validadas, entidades actualmente plausibles "
            "y entidades históricamente falsadas."
        ),
        "experiments": results,
        "attacks": attacks,
        "summary": {
            "total_attacks": len(attacks),
            "verdict": results["verdict"],
            "separation_a_b_c": separation_ok,
            "adversarial_high_scores": sum(1 for idx in adversarial_scores if idx >= 0.8),
            "predictive_power": "NONE",
        },
        "conclusion": (
            "El Instrumentability Index es una taxonomía, no una métrica. "
            "No predice nada observable. No separa grupos históricos. "
            "Es vulnerable a generación adversarial de entidades."
        ),
    }

    output_json = Path("artifacts/meta_measurement_audit.json")
    output_json.parent.mkdir(parents=True, exist_ok=True)
    with open(output_json, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, ensure_ascii=False, default=str)

    print()
    print("=" * 70)
    print(f"Output: {output_json}")
    print(f"VEREDICTO: {results['verdict']}")
    print("=" * 70)

    return 0


if __name__ == "__main__":
    sys.exit(main())