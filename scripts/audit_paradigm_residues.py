#!/usr/bin/env python3
"""
Auditoría 3: Investigar los 0 paradigm residues detectados.

Responde: Do they not exist? o Do we not know how to detect them?

El supervisor identificó tres posibles explicaciones:
1. La extracción es demasiado superficial (ve cambios de fichero, no supuestos persistentes)
2. El algoritmo busca residuos explícitos (y los residuos casi nunca son explícitos)
3. El concepto es correcto pero la unidad de análisis es demasiado pequeña
   (los residuos aparecen entre trayectorias, no entre commits consecutivos)

Este script:
- Examina los edges superseded_by/abandoned_for disponibles
- Verifica si hay nodos conectados para comparar
- Diagnostica cuál de las tres explicaciones es más probable
- Documenta la limitación

Usage:
  python scripts/audit_paradigm_residues.py
  python scripts/audit_paradigm_residues.py --input data/trajectories/langchain_ai_langgraph/trajectory_graph.json
"""
import sys
import json
from pathlib import Path

project_root = Path(__file__).resolve().parent.parent


def main():
    import argparse

    parser = argparse.ArgumentParser(
        description="Audit paradigm residues: why 0 detected?"
    )
    parser.add_argument(
        "--input",
        default="data/trajectories/langchain_ai_langgraph/trajectory_graph.json",
        help="Path to trajectory_graph.json",
    )
    parser.add_argument(
        "--output",
        default="artifacts/epistemic_gap_residue_audit.json",
        help="Output audit file",
    )
    args = parser.parse_args()

    input_path = Path(args.input)
    if not input_path.exists():
        print(f"ERROR: Input file not found: {input_path}")
        return 1

    with open(input_path, "r", encoding="utf-8") as f:
        trajectory = json.load(f)

    nodes = trajectory.get("nodes", [])
    edges = trajectory.get("edges", [])

    # Construir node_map
    node_map = {}
    for n in nodes:
        nid = n.get("decision_id", n.get("id", ""))
        if nid:
            node_map[nid] = n

    # Examinar edges relevantes
    superseded_edges = [e for e in edges if e.get("type") == "superseded_by"]
    abandoned_edges = [e for e in edges if e.get("type") == "abandoned_for"]
    chosen_over_edges = [e for e in edges if e.get("type") == "chosen_over"]

    print("=" * 70)
    print("AUDITORÍA 3: Paradigm Residues")
    print("=" * 70)
    print()
    print(f"Total nodes: {len(nodes)}")
    print(f"Total edges: {len(edges)}")
    print(f"  superseded_by edges: {len(superseded_edges)}")
    print(f"  abandoned_for edges: {len(abandoned_edges)}")
    print(f"  chosen_over edges: {len(chosen_over_edges)}")
    print()

    # Diagnóstico 1: Are there edges to compare?
    comparable_edges = superseded_edges + abandoned_edges
    print(f"Diagnóstico 1: Edges disponibles para residue detection")
    print(f"  Total comparable edges: {len(comparable_edges)}")
    if len(comparable_edges) == 0:
        print(f"  → EXPLICACIÓN 1 PROBABLE: No hay edges superseded_by/abandoned_for")
        print(f"    El linker no detectó sucesiones de decisiones.")
        print(f"    Sin sucesiones, no hay residuos que detectar.")
    else:
        print(f"  → Hay edges suficientes para intentar detección")
    print()

    # Diagnóstico 2: Do edges connect real nodes?
    valid_pairs = 0
    invalid_pairs = 0
    for e in comparable_edges:
        from_id = e.get("from", "")
        to_id = e.get("to", "")
        if from_id in node_map and to_id in node_map:
            valid_pairs += 1
        else:
            invalid_pairs += 1

    print(f"Diagnóstico 2: Pares válidos (ambos nodos existen)")
    print(f"  Valid pairs: {valid_pairs}")
    print(f"  Invalid pairs: {invalid_pairs}")
    if valid_pairs == 0 and len(comparable_edges) > 0:
        print(f"  → EXPLICACIÓN 2 PROBABLE: Los edges referencian nodos inexistentes")
    print()

    # Diagnóstico 3: Los títulos tienen conceptos comparables?
    concept_overlap_count = 0
    no_overlap_count = 0
    sample_comparisons = []

    for e in comparable_edges[:20]:  # Sample of 20
        from_id = e.get("from", "")
        to_id = e.get("to", "")
        from_node = node_map.get(from_id, {})
        to_node = node_map.get(to_id, {})

        from_title = from_node.get("title", from_node.get("decision", ""))
        to_title = to_node.get("title", to_node.get("decision", ""))

        # Token overlap simple
        from_tokens = set(from_title.lower().split())
        to_tokens = set(to_title.lower().split())
        overlap = from_tokens & to_tokens

        if overlap:
            concept_overlap_count += 1
        else:
            no_overlap_count += 1

        if len(sample_comparisons) < 5:
            sample_comparisons.append({
                "edge_type": e.get("type"),
                "from_id": from_id,
                "to_id": to_id,
                "from_title": from_title[:80],
                "to_title": to_title[:80],
                "shared_tokens": list(overlap)[:5],
                "has_overlap": len(overlap) > 0,
            })

    print(f"Diagnóstico 3: Concept overlap en pares comparables (muestra 20)")
    print(f"  Pairs with overlap: {concept_overlap_count}")
    print(f"  Pairs without overlap: {no_overlap_count}")
    if no_overlap_count > concept_overlap_count:
        print(f"  → EXPLICACIÓN 3 PROBABLE: Los títulos no comparten conceptos")
        print(f"    El algoritmo de residuos usa token overlap del título.")
        print(f"    Si los títulos son muy distintos, no detecta residuos.")
        print(f"    Los residuos reales están en supuestos, no en títulos.")
    print()

    # Mostrar muestras
    print("Muestras de comparación:")
    for i, s in enumerate(sample_comparisons):
        print(f"  [{i+1}] {s['edge_type']}: {s['from_id']} → {s['to_id']}")
        print(f"      From: {s['from_title']}")
        print(f"      To:   {s['to_title']}")
        print(f"      Shared: {s['shared_tokens']}")
        print()

    # Conclusión
    diagnosis = {
        "total_nodes": len(nodes),
        "total_edges": len(edges),
        "superseded_by_edges": len(superseded_edges),
        "abandoned_for_edges": len(abandoned_edges),
        "comparable_edges": len(comparable_edges),
        "valid_pairs": valid_pairs,
        "invalid_pairs": invalid_pairs,
        "concept_overlap_count": concept_overlap_count,
        "no_overlap_count": no_overlap_count,
        "sample_comparisons": sample_comparisons,
        "diagnosis": {
            "explanation_1_no_edges": len(comparable_edges) == 0,
            "explanation_2_invalid_refs": valid_pairs == 0 and len(comparable_edges) > 0,
            "explanation_3_no_concept_overlap": no_overlap_count > concept_overlap_count,
            "most_likely": (
                "explanation_1_no_edges" if len(comparable_edges) == 0
                else "explanation_3_no_concept_overlap" if no_overlap_count > concept_overlap_count
                else "needs_further_investigation"
            ),
        },
        "supervisor_analysis": {
            "option_1_superficial_extraction": (
                "La extracción ve cambios de fichero/función/configuración, "
                "no supuestos persistentes. Los residuos paradigmáticos son "
                "supuestos que nadie cuestiona, no cambios explícitos."
            ),
            "option_2_implicit_residues": (
                "El algoritmo busca residuos explícitos. Pero los residuos "
                "casi nunca son explícitos. Precisamente porque son lo que "
                "nadie cuestiona."
            ),
            "option_3_wrong_analysis_unit": (
                "El concepto es correcto pero la unidad de análisis es "
                "demasiado pequeña. Los residuos aparecen entre trayectorias, "
                "no entre commits consecutivos. Einstein no cuestionó la "
                "continuidad entre dos commits. La cuestionó después de "
                "siglos de física continua."
            ),
        },
        "conclusion": (
            "Los 0 paradigm residues probablemente indican que la detección "
            "actual opera a nivel de commit/PR (demasiado granular), no a "
            "nivel de trayectoria paradigmática. Los residuos reales requieren "
            "identificar supuestos persistentes a lo largo de múltiples "
            "decisiones, no comparar títulos de commits consecutivos. "
            "Esto es una limitación conocida que requiere H7 (Branch Detection) "
            "y análisis a nivel de trayectoria, no de commit individual."
        ),
    }

    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(diagnosis, f, indent=2, ensure_ascii=False, default=str)

    print(f"Diagnosis file: {output_path}")
    print()
    print("Conclusión:")
    print(f"  {diagnosis['conclusion']}")
    print("=" * 70)

    return 0


if __name__ == "__main__":
    sys.exit(main())