#!/usr/bin/env python3
"""
SPRINT 66B — Calibration Attack

Objetivo: Intentar destruir el Instrumentability Index.
No validarlo. Destruirlo.

Experimentos:
  1. Entidades artificiales con propiedades conocidas
  2. Pasar por la métrica
  3. Introducir entidades absurdas (éter, flogisto, miasma, vitalismo)
  4. Introducir entidades validadas (gen, electrón, placa tectónica, campo gravitatorio)

Criterio de éxito:
  La métrica separa entidades reales, hypothesis útiles y entidades históricamente falsas.

Si la métrica colapsa sistemáticamente al mismo valor:
  Instrumentability Index = FALSIFIED

Si la métrica no distingue entidades realmente distintas:
  Instrumentability Index = FALSIFIED
"""
import sys
import json
from pathlib import Path
from datetime import datetime, timezone

project_root = Path(__file__).resolve().parent.parent


# ------------------------------------------------------------------
# Utilidad: calcular índice igual que en SPRINT 66
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
# Experimento 1: Entidades artificiales con propiedades conocidas
# ------------------------------------------------------------------

ARTIFICIAL_ENTITIES = [
    {
        "name": "ENTITY_A",
        "description": "Directamente observable, replicable, sin capacidad inferencial",
        "observable": True,
        "inferible": False,
        "instrumentable": True,
        "falsable": True,
        "replicable": True,
        "expected_index": 0.8,  # 4/5: observable, instrumentable, falsable, replicable
    },
    {
        "name": "ENTITY_B",
        "description": "Inferible pero no observable, falsable, no replicable",
        "observable": False,
        "inferible": True,
        "instrumentable": False,
        "falsable": True,
        "replicable": False,
        "expected_index": 0.4,  # 2/5: inferible, falsable
    },
    {
        "name": "ENTITY_C",
        "description": "No observable, no inferible, no falsable, no replicable",
        "observable": False,
        "inferible": False,
        "instrumentable": False,
        "falsable": False,
        "replicable": False,
        "expected_index": 0.0,  # 0/5
    },
    {
        "name": "ENTITY_D",
        "description": "Solo observable",
        "observable": True,
        "inferible": False,
        "instrumentable": False,
        "falsable": False,
        "replicable": False,
        "expected_index": 0.2,  # 1/5
    },
    {
        "name": "ENTITY_E",
        "description": "Falsable pero no observable ni inferible",
        "observable": False,
        "inferible": False,
        "instrumentable": True,
        "falsable": True,
        "replicable": False,
        "expected_index": 0.4,  # 2/5
    },
]


# ------------------------------------------------------------------
# Experimento 3: Entidades absurdas
# ------------------------------------------------------------------

ABSURD_ENTITIES = [
    {
        "name": "Éter luminífero",
        "description": " Medio hipotético del siglo XIX para propagación de luz. Falsado por Michelson-Morley.",
        "observable": False,
        "inferible": False,
        "instrumentable": True,  # Podría argumentarse que era falsable
        "falsable": True,
        "replicable": False,
        "expected_status": "NON_INVESTIGABLE o HISTORICALLY_FALSIFIED",
    },
    {
        "name": "Flogisto",
        "description": "Elemento hipotético del fuego. Falsado por Lavoisier.",
        "observable": False,
        "inferible": False,
        "instrumentable": True,  # Podría argumentarse
        "falsable": True,
        "replicable": False,
        "expected_status": "NON_INVESTIGABLE o HISTORICALLY_FALSIFIED",
    },
    {
        "name": "Miasma",
        "description": "Teoría de enfermedades por aire viciado. Falsado por germ theory.",
        "observable": False,
        "inferible": False,
        "instrumentable": True,
        "falsable": True,
        "replicable": False,
        "expected_status": "NON_INVESTIGABLE o HISTORICALLY_FALSIFIED",
    },
    {
        "name": "Vitalismo",
        "description": "Fuerza vital especial para vida. Falsado por bioquímica.",
        "observable": False,
        "inferible": False,
        "instrumentable": True,
        "falsable": True,
        "replicable": False,
        "expected_status": "NON_INVESTIGABLE o HISTORICALLY_FALSIFIED",
    },
]


# ------------------------------------------------------------------
# Experimento 4: Entidades validadas
# ------------------------------------------------------------------

VALIDATED_ENTITIES = [
    {
        "name": "Gen",
        "description": "Unidad de herencia. No observable en 1850. Ahora observable via DNA sequencing.",
        "observable": True,  # Actualmente observable
        "inferible": True,
        "instrumentable": True,
        "falsable": True,
        "replicable": True,
        "expected_index": 1.0,
        "note": "Debe obtener índice alto porque es entidad real y establecida",
    },
    {
        "name": "Electrón",
        "description": "Partícula subatómica. No observable directamente (campo), pero sus efectos son medibles.",
        "observable": True,  # Efectos observables
        "inferible": True,
        "instrumentable": True,
        "falsable": True,
        "replicable": True,
        "expected_index": 1.0,
        "note": "Debe obtener índice alto porque es entidad real",
    },
    {
        "name": "Placa tectónica",
        "description": "Estructura geológica. Observable via GPS y sismología.",
        "observable": True,
        "inferible": True,
        "instrumentable": True,
        "falsable": True,
        "replicable": True,
        "expected_index": 1.0,
        "note": "Debe obtener índice alto. Wegener 1912 → rechazada. Ahora establecida.",
    },
    {
        "name": "Campo gravitatorio",
        "description": "Entidad física. No observable directamente pero sus efectos son medibles.",
        "observable": True,  # Efectos observables
        "inferible": True,
        "instrumentable": True,
        "falsable": True,
        "replicable": True,
        "expected_index": 1.0,
        "note": "Debe obtener índice alto. Newton → Einstein. Entidad real.",
    },
]


def main():
    print("=" * 70)
    print("SPRINT 66B — Calibration Attack")
    print("=" * 70)
    print("Objetivo: Intentar destruir el Instrumentability Index")
    print()

    results = {
        "experiment_1_artificial": [],
        "experiment_3_absurd": [],
        "experiment_4_validated": [],
        "attacks_detected": [],
        "verdict": "PASS",
    }

    # ------------------------------------------------------------------
    # Experimento 1: Entidades artificiales
    # ------------------------------------------------------------------
    print("[Experimento 1] Entidades artificiales con propiedades conocidas")
    print(f"{'Name':<15} {'Expected':>9} {'Actual':>9} {'Match':>6}")
    print(f"{'-'*15} {'-'*9} {'-'*9} {'-'*6}")

    for entity in ARTIFICIAL_ENTITIES:
        index = calculate_instrumentability_index(
            entity["observable"],
            entity["inferible"],
            entity["instrumentable"],
            entity["falsable"],
            entity["replicable"],
        )
        match = abs(index - entity["expected_index"]) < 0.01
        results["experiment_1_artificial"].append({
            "name": entity["name"],
            "expected": entity["expected_index"],
            "actual": index,
            "match": match,
        })
        print(f"{entity['name']:<15} {entity['expected_index']:>9.2f} {index:>9.2f} {'Yes' if match else 'NO':>6}")

        if not match:
            results["attacks_detected"].append({
                "experiment": "1",
                "entity": entity["name"],
                "issue": f"Expected {entity['expected_index']}, got {index:.2f}",
            })

    # ------------------------------------------------------------------
    # Experiment 2: Pass through metric (implicit in Experiment 1)
    # ------------------------------------------------------------------
    print()
    print("[Experimento 2] La métrica distingue entidades realmente distintas?")
    indices = [calculate_instrumentability_index(
        e["observable"], e["inferible"], e["instrumentable"], e["falsable"], e["replicable"]
    ) for e in ARTIFICIAL_ENTITIES]
    distinct_values = len(set(indices))
    print(f"  Distinct index values: {distinct_values} / {len(indices)}")
    if distinct_values < len(indices):
        print("  ⚠️  WARNING: Metric collapses some entities to same value")
        results["attacks_detected"].append({
            "experiment": "2",
            "entity": "N/A",
            "issue": f"Metric collapses entities: only {distinct_values} distinct values for {len(indices)} entities",
        })

    # ------------------------------------------------------------------
    # Experimento 3: Entidades absurdas
    # ------------------------------------------------------------------
    print()
    print("[Experimento 3] Entidades absurdas (falsadas históricamente)")
    print(f"{'Name':<20} {'Index':>6} {'Expected':<30}")
    print(f"{'-'*20} {'-'*6} {'-'*30}")

    for entity in ABSURD_ENTITIES:
        index = calculate_instrumentability_index(
            entity["observable"],
            entity["inferible"],
            entity["instrumentable"],
            entity["falsable"],
            entity["replicable"],
        )
        results["experiment_3_absurd"].append({
            "name": entity["name"],
            "index": index,
            "expected_status": entity["expected_status"],
        })
        print(f"{entity['name']:<20} {index:>6.2f} {entity['expected_status']:<30}")

        if index >= 0.6:
            print(f"  ⚠️  ATTACK: {entity['name']} got index {index:.2f} but should be NON_INVESTIGABLE")
            results["attacks_detected"].append({
                "experiment": "3",
                "entity": entity["name"],
                "issue": f"Historically falsified entity got index {index:.2f} >= 0.6",
            })

    # ------------------------------------------------------------------
    # Experimento 4: Entidades validadas
    # ------------------------------------------------------------------
    print()
    print("[Experimento 4] Entidades validadas científicamente")
    print(f"{'Name':<20} {'Index':>6} {'Expected':>9} {'Match':>6}")
    print(f"{'-'*20} {'-'*6} {'-'*9} {'-'*6}")

    for entity in VALIDATED_ENTITIES:
        index = calculate_instrumentability_index(
            entity["observable"],
            entity["inferible"],
            entity["instrumentable"],
            entity["falsable"],
            entity["replicable"],
        )
        match = abs(index - entity["expected_index"]) < 0.01
        results["experiment_4_validated"].append({
            "name": entity["name"],
            "index": index,
            "expected": entity["expected_index"],
            "match": match,
            "note": entity["note"],
        })
        print(f"{entity['name']:<20} {index:>6.2f} {entity['expected_index']:>9.2f} {'Yes' if match else 'NO':>6}")

        if not match:
            results["attacks_detected"].append({
                "experiment": "4",
                "entity": entity["name"],
                "issue": f"Validated entity got unexpected index {index:.2f}",
            })

    # ------------------------------------------------------------------
    # Veredicto
    # ------------------------------------------------------------------
    print()
    print("[Verdict]")
    if results["attacks_detected"]:
        print(f"  ⚠️  ATTACKS DETECTED: {len(results['attacks_detected'])}")
        for attack in results["attacks_detected"]:
            print(f"    - Exp {attack['experiment']}: {attack['entity']}: {attack['issue']}")
        results["verdict"] = "FALSIFIED"
    else:
        print("  ✓ No attacks detected. Metric passes calibration.")
        results["verdict"] = "PASS"

    # ------------------------------------------------------------------
    # Guardar resultados
    # ------------------------------------------------------------------
    report = {
        "report_id": f"CALIB66B-{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S')}",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "sprint": "SPRINT 66B — Calibration Attack",
        "objective": (
            "Intentar destruir el Instrumentability Index. "
            "No validarlo. Destruirlo."
        ),
        "experiments": results,
        "summary": {
            "total_attacks": len(results["attacks_detected"]),
            "verdict": results["verdict"],
            "artificial_distinct_values": distinct_values,
            "absurd_high_index_count": sum(1 for e in results["experiment_3_absurd"] if e["index"] >= 0.6),
            "validated_correct_count": sum(1 for e in results["experiment_4_validated"] if e["match"]),
        },
        "conclusion": (
            "Si attacks > 0: Instrumentability Index = FALSIFIED"
            if results["attacks_detected"]
            else "Instrumentability Index passes calibration attack."
        ),
    }

    output_json = Path("artifacts/instrumentability_calibration_attack.json")
    output_json.parent.mkdir(parents=True, exist_ok=True)
    with open(output_json, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, ensure_ascii=False, default=str)

    print()
    print("=" * 70)
    print(f"Output: {output_json}")
    print(f"Verdict: {results['verdict']}")
    print("=" * 70)

    return 0


if __name__ == "__main__":
    sys.exit(main())