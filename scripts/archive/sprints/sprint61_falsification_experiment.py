#!/usr/bin/env python3
"""
SPRINT 61 — FASE 5: Experimento crítico de falsación.

Pregunta: Does the detector keep finding constraints convincentes
cuando se inyectan convergences sintéticas aleatorias?

Si sí → problema grave: hallucinated constraints.
Si no → el detector es robusto frente a ruido.

Método:
1. Cargar trajectory_graph real (langgraph)
2. Generar N versiones sintéticas con convergences inyectadas aleatoriamente
3. Ejecutar detector en cada versión
4. Comparar: Do synthetic convergences producen "constraints" igual de convincentes?

Entregable: artifacts/falsification_experiment.json

Ver: docs/SPRINT_61_CONSTRAINT_VALIDATION.md
"""
import sys
import json
import random
import copy
from pathlib import Path
from datetime import datetime, timezone

# Add python/ to path
project_root = Path(__file__).resolve().parent.parent
python_dir = project_root / "python"
if str(python_dir) not in sys.path:
    sys.path.insert(0, str(python_dir))

from discovery.epistemic_gap_detector import (
    EpistemicGapDetector,
    EpistemicStatus,
)


def inject_synthetic_convergences(
    trajectory: dict,
    num_synthetic: int = 5,
    seed: int = 42,
) -> dict:
    """
    Inyecta convergences sintéticas creando grupos de decisiones
    con títulos similares pero actores aleatorios y outcomes abandonados.

    Esto simula "convergences" que NO corresponden a constraints reales.
    """
    rng = random.Random(seed)
    synthetic = copy.deepcopy(trajectory)
    nodes = synthetic.get("nodes", [])

    # Generar temas sintéticos aleatorios
    synthetic_themes = [
        "fix(synthetic): refactor random module for test coverage",
        "fix(synthetic): update imaginary dependency version constraint",
        "fix(synthetic): rename placeholder variable in generated code",
        "fix(synthetic): adjust artificial parameter in mock function",
        "fix(synthetic): reorder synthetic imports for style compliance",
    ]

    synthetic_nodes = []
    for i in range(num_synthetic):
        theme = rng.choice(synthetic_themes)
        # Create 2-5 nodes with same topic but random actors
        num_actors = rng.randint(2, 5)
        for j in range(num_actors):
            node = {
                "decision_id": f"SYNTHETIC-{i:03d}-{j:03d}",
                "title": theme,
                "outcome": "abandoned",
                "actor": f"synthetic_actor_{rng.randint(1000, 9999)}",
                "artifact_url": f"https://github.com/synthetic/repo/pull/{rng.randint(1, 9999)}",
                "rationale": "",
                "confidence": 0.5,
                "body_snippet": "",
                "classification": "observable",
            }
            synthetic_nodes.append(node)

    synthetic["nodes"] = nodes + synthetic_nodes
    return synthetic


def inject_random_noise_convergences(
    trajectory: dict,
    num_noise: int = 10,
    seed: int = 42,
) -> dict:
    """
    Inyecta convergences de ruido puro: títulos aleatorios sin sentido
    que no corresponden a ningún tema real.
    """
    rng = random.Random(seed)
    noisy = copy.deepcopy(trajectory)
    nodes = noisy.get("nodes", [])

    # Random words to generate nonsense titles
    words = ["alpha", "beta", "gamma", "delta", "epsilon", "zeta", "eta",
             "theta", "iota", "kappa", "lambda", "mu", "nu", "xi"]

    noise_nodes = []
    for i in range(num_noise):
        # Crear título aleatorio
        num_words = rng.randint(2, 4)
        title_words = [rng.choice(words) for _ in range(num_words)]
        title = f"fix(noise): {' '.join(title_words)} module update"

        # Create 2-3 nodes with this random title
        num_actors = rng.randint(2, 3)
        for j in range(num_actors):
            node = {
                "decision_id": f"NOISE-{i:03d}-{j:03d}",
                "title": title,
                "outcome": "abandoned",
                "actor": f"noise_actor_{rng.randint(1000, 9999)}",
                "artifact_url": f"https://github.com/noise/repo/pull/{rng.randint(1, 9999)}",
                "rationale": "",
                "confidence": 0.5,
                "body_snippet": "",
                "classification": "observable",
            }
            noise_nodes.append(node)

    noisy["nodes"] = nodes + noise_nodes
    return noisy


def run_falsification_experiment(trajectory_path: Path) -> dict:
    """
    Ejecuta el experimento completo de falsación.

    Compara:
    1. Detector en datos reales (control)
    2. Detector con convergences sintéticas inyectadas
    3. Detector con ruido aleatorio inyectado

    Pregunta crítica: Does the detector distinguish between convergences reales
    y convergences sintéticas/ruido?
    """
    with open(trajectory_path, "r", encoding="utf-8") as f:
        original_trajectory = json.load(f)

    results = {
        "experiment_id": f"FALSEXP-{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S')}",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "objective": (
            "Intentar falsar H7: el detector distingue convergences reales "
            "de convergences sintéticas inyectadas?"
        ),
        "hypothesis": (
            "Si el detector encuentra 'constraints' igual de convincentes "
            "en convergences sintéticas, entonces H7 es falsa: el detector "
            "produce hallucinated constraints."
        ),
        "null_hypothesis": (
            "El detector NO distingue entre convergences reales y sintéticas."
        ),
        "conditions": [],
        "analysis": {},
        "verdict": "",
    }

    # Condición 1: Control (datos reales)
    print("[1/3] Running detector on original data (control)...")
    detector_real = EpistemicGapDetector(repository="langchain-ai/langgraph")
    report_real = detector_real.generate_report(original_trajectory)
    real_convergences = report_real.get("convergences", [])
    real_barrier = [c for c in real_convergences if c.get("type") == "barrier_convergence"]

    results["conditions"].append({
        "condition": "control_real_data",
        "description": "Detector en datos reales sin modificación",
        "total_nodes": len(original_trajectory.get("nodes", [])),
        "total_convergences": len(real_convergences),
        "barrier_convergences": len(real_barrier),
        "convergence_ids": [c.get("convergence_id") for c in real_convergences],
    })

    # Condición 2: Convergencias sintéticas inyectadas
    print("[2/3] Running detector with synthetic convergences injected...")
    synthetic_convergence_counts = []
    for seed in range(10):  # 10 repeticiones con seeds diferentes
        synthetic_traj = inject_synthetic_convergences(
            original_trajectory, num_synthetic=5, seed=seed
        )
        detector_synth = EpistemicGapDetector(repository="synthetic-test")
        report_synth = detector_synth.generate_report(synthetic_traj)
        synth_convergences = report_synth.get("convergences", [])
        synth_barrier = [c for c in synth_convergences if c.get("type") == "barrier_convergence"]

        # Identificar cuáles convergences son sintéticas (tema contiene "synthetic")
        synthetic_detected = [
            c for c in synth_convergences
            if "synthetic" in c.get("theme", "").lower()
        ]

        synthetic_convergence_counts.append({
            "seed": seed,
            "total_convergences": len(synth_convergences),
            "barrier_convergences": len(synth_barrier),
            "synthetic_detected": len(synthetic_detected),
            "real_convergences_preserved": len(synth_convergences) - len(synthetic_detected),
        })

    results["conditions"].append({
        "condition": "synthetic_injected",
        "description": "Convergencias sintéticas inyectadas (5 temas, 2-5 actores cada uno)",
        "num_replications": 10,
        "replications": synthetic_convergence_counts,
        "avg_synthetic_detected": sum(r["synthetic_detected"] for r in synthetic_convergence_counts) / len(synthetic_convergence_counts),
        "avg_real_preserved": sum(r["real_convergences_preserved"] for r in synthetic_convergence_counts) / len(synthetic_convergence_counts),
    })

    # Condición 3: Ruido aleatorio inyectado
    print("[3/3] Running detector with random noise injected...")
    noise_convergence_counts = []
    for seed in range(10):
        noisy_traj = inject_random_noise_convergences(
            original_trajectory, num_noise=10, seed=seed
        )
        detector_noise = EpistemicGapDetector(repository="noise-test")
        report_noise = detector_noise.generate_report(noisy_traj)
        noise_convergences = report_noise.get("convergences", [])
        noise_barrier = [c for c in noise_convergences if c.get("type") == "barrier_convergence"]

        # Identificar convergences de ruido (tema contiene "noise")
        noise_detected = [
            c for c in noise_convergences
            if "noise" in c.get("theme", "").lower()
        ]

        noise_convergence_counts.append({
            "seed": seed,
            "total_convergences": len(noise_convergences),
            "barrier_convergences": len(noise_barrier),
            "noise_detected": len(noise_detected),
            "real_convergences_preserved": len(noise_convergences) - len(noise_detected),
        })

    results["conditions"].append({
        "condition": "random_noise_injected",
        "description": "Ruido aleatorio inyectado (10 temas sin sentido, 2-3 actores)",
        "num_replications": 10,
        "replications": noise_convergence_counts,
        "avg_noise_detected": sum(r["noise_detected"] for r in noise_convergence_counts) / len(noise_convergence_counts),
        "avg_real_preserved": sum(r["real_convergences_preserved"] for r in noise_convergence_counts) / len(noise_convergence_counts),
    })

    # Analysis: does detector distinguish real from synthetic?
    control_barrier = len(real_barrier)
    avg_synth_detected = results["conditions"][1]["avg_synthetic_detected"]
    avg_noise_detected = results["conditions"][2]["avg_noise_detected"]

    # Key question: does detector detect synthetic convergences as if real?
    # Si detecta muchas → problema (hallucinated constraints)
    # Si detecta pocas → robusto

    results["analysis"] = {
        "control_barrier_convergences": control_barrier,
        "avg_synthetic_convergences_detected": avg_synth_detected,
        "avg_noise_convergences_detected": avg_noise_detected,
        "false_positive_rate_synthetic": avg_synth_detected / 5.0 if 5.0 > 0 else 0,  # 5 temas sintéticos inyectados
        "false_positive_rate_noise": avg_noise_detected / 10.0 if 10.0 > 0 else 0,  # 10 temas de ruido
        "real_convergences_preserved_synth": results["conditions"][1]["avg_real_preserved"],
        "real_convergences_preserved_noise": results["conditions"][2]["avg_real_preserved"],
    }

    # Veredicto
    fpr_synth = results["analysis"]["false_positive_rate_synthetic"]
    fpr_noise = results["analysis"]["false_positive_rate_noise"]

    if fpr_synth > 0.5 or fpr_noise > 0.5:
        results["verdict"] = "FALSIFIED — detector produces hallucinated constraints"
        results["verdict_detail"] = (
            f"False positive rate > 50%: synthetic={fpr_synth:.2f}, noise={fpr_noise:.2f}. "
            f"El detector encuentra 'convergences' en datos sintéticos/ruido. "
            f"H7 se debilita significativamente."
        )
    elif fpr_synth > 0.2 or fpr_noise > 0.2:
        results["verdict"] = "WEAKENED — detector has moderate false positive rate"
        results["verdict_detail"] = (
            f"False positive rate 20-50%: synthetic={fpr_synth:.2f}, noise={fpr_noise:.2f}. "
            f"El detector detecta algunas convergences sintéticas. "
            f"H7 necesita refinamiento."
        )
    else:
        results["verdict"] = "ROBUST — detector distinguishes real from synthetic"
        results["verdict_detail"] = (
            f"False positive rate < 20%: synthetic={fpr_synth:.2f}, noise={fpr_noise:.2f}. "
            f"El detector es robusto frente a convergences sintéticas. "
            f"H7 sobrevive este intento de falsación."
        )

    # Epistemic status del veredicto
    if "FALSIFIED" in results["verdict"]:
        results["verdict_epistemic_status"] = EpistemicStatus.FALSIFIED.value
    elif "WEAKENED" in results["verdict"]:
        results["verdict_epistemic_status"] = EpistemicStatus.HYPOTHESIZED.value
    else:
        results["verdict_epistemic_status"] = EpistemicStatus.HYPOTHESIZED.value  # Sobrevivió, pero no está probada

    results["epistemic_note"] = (
        "NOTA: Sobrevivir un intento de falsación no prueba H7. "
        "Solo le da credibilidad provisional. "
        "Se necesitan más intentos de falsación independientes."
    )

    return results


def main():
    import argparse

    parser = argparse.ArgumentParser(
        description="SPRINT 61 FASE 5: Falsification experiment for H7"
    )
    parser.add_argument(
        "--input",
        default="data/trajectories/langchain_ai_langgraph/trajectory_graph.json",
        help="Path to trajectory_graph.json",
    )
    parser.add_argument(
        "--output",
        default="artifacts/falsification_experiment.json",
        help="Output file",
    )
    args = parser.parse_args()

    trajectory_path = Path(args.input)
    if not trajectory_path.exists():
        print(f"ERROR: Input file not found: {trajectory_path}")
        return 1

    print("=" * 70)
    print("SPRINT 61 — FASE 5: Falsification Experiment")
    print("=" * 70)
    print(f"Input: {trajectory_path}")
    print()
    print("Objective: Intentar FALSAR H7")
    print("Question: El detector distingue convergences reales de sintéticas?")
    print()

    results = run_falsification_experiment(trajectory_path)

    # Guardar resultados
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False, default=str)

    # Resumen
    print()
    print("=" * 70)
    print("RESULTS")
    print("=" * 70)
    analysis = results["analysis"]
    print(f"Control (real) barrier convergences: {analysis['control_barrier_convergences']}")
    print(f"Avg synthetic convergences detected:  {analysis['avg_synthetic_convergences_detected']:.1f}")
    print(f"Avg noise convergences detected:      {analysis['avg_noise_convergences_detected']:.1f}")
    print(f"False positive rate (synthetic):      {analysis['false_positive_rate_synthetic']:.2%}")
    print(f"False positive rate (noise):          {analysis['false_positive_rate_noise']:.2%}")
    print()
    print(f"VERDICT: {results['verdict']}")
    print(f"Detail:  {results['verdict_detail']}")
    print()
    print(f"Epistemic Status: {results['verdict_epistemic_status']}")
    print(f"Note: {results['epistemic_note']}")
    print()
    print(f"Output: {output_path}")
    print("=" * 70)

    return 0


if __name__ == "__main__":
    sys.exit(main())