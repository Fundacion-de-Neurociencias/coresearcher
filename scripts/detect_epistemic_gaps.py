#!/usr/bin/env python3
"""
SPRINT 60C+: Epistemic Gap Detection — Cartografía Epistemológica

Runs the Epistemic Gap Detector on existing SPRINT 60C trajectory data.
Produces real artifacts (JSON + Markdown) with classified gaps.

OBJETIVO: Cartografiar el espacio de conocimiento (no generar hypothesis).

EHG ESTÁ CONGELADO. No se generan hypothesis hasta que:
1. Los gaps sean auditados
2. La precisión sea ≥ 80%
3. El Triunvirato se distribuya de forma estable

This script does NOT create new schemas, graphs, or layers.
It is a read-only analysis over existing TrajectoryGraph data.

Pipeline:
  EvidenceGraph (existing)
      ↓
  TrajectoryGraph (SPRINT 60C output)
      ↓
  Epistemic Gap Detection (this script)
      ↓
  Gap Characterization (A/B/C/D)
      ↓
  Paradigm Residue Detection
      ↓
  Convergence Detection
      ↓
  Gap Report (JSON + Markdown artifacts)
      ↓
  [CONGELADO] Hypothesis Generation (EHG v2 — post-audit ≥80%)

Usage:
  python scripts/detect_epistemic_gaps.py
  python scripts/detect_epistemic_gaps.py --input data/trajectories/langchain_ai_langgraph/trajectory_graph.json
"""
import sys
import json
import random
from pathlib import Path

# Add python/ to path for imports
project_root = Path(__file__).resolve().parent.parent
python_dir = project_root / "python"
if str(python_dir) not in sys.path:
    sys.path.insert(0, str(python_dir))

from discovery.epistemic_gap_detector import (
    EpistemicGapDetector,
    EpistemicGap,
    ParadigmResidue,
    GapType,
    GapCharacterization,
    Severity,
)


def generate_audit_sample(gaps: list, sample_size: int = 50) -> dict:
    """
    Genera muestra aleatoria de gaps para auditoría humana.

    Protocolo:
    - Muestra: 50 gaps aleatorios
    - Clasificación manual: real | artifact | indeterminate
    - Métrica: precisión = (real + indeterminate * 0.5) / total
    - Criterio: ≥80% para descongelar EHG
    """
    if len(gaps) <= sample_size:
        sample = gaps
    else:
        sample = random.sample(gaps, sample_size)

    # Structure sample for manual audit
    audit_items = []
    for gap in sample:
        audit_items.append({
            "gap_id": gap["gap_id"],
            "gap_type": gap["gap_type"],
            "characterization": gap.get("characterization", "unknown"),
            "severity": gap["severity"],
            "detection_signal": gap["detection_signal"],
            "description": gap["description"],
            "evidence_anchor": gap["evidence_anchor"],
            "location": gap["location"],
            "audit_classification": None,  # To be filled: real | artifact | indeterminate
            "audit_notes": "",  # To be filled by auditor
        })

    return {
        "audit_protocol": {
            "sample_size": len(audit_items),
            "total_gaps": len(gaps),
            "classification_options": ["real", "artifact", "indeterminate"],
            "precision_formula": "(real + indeterminate * 0.5) / total",
            "threshold": 0.80,
            "instructions": (
                "For each gap, classify as:\n"
                "  real: The gap represents genuine ignorance\n"
                "  artifact: The gap is a false positive from the extractor\n"
                "  indeterminate: Cannot determine\n"
                "If precision >= 80%, EHG can be unfrozen.\n"
                "If precision < 80%, the detector needs improvement."
            ),
        },
        "items": audit_items,
    }


def main():
    import argparse

    parser = argparse.ArgumentParser(
        description="Detect Epistemic Gaps from SPRINT 60C trajectory data — Cartografía Epistemológica"
    )
    parser.add_argument(
        "--input",
        default="data/trajectories/langchain_ai_langgraph/trajectory_graph.json",
        help="Path to trajectory_graph.json (default: SPRINT 60C langgraph data)",
    )
    parser.add_argument(
        "--output-json",
        default="artifacts/epistemic_gap_report.json",
        help="Output JSON report path",
    )
    parser.add_argument(
        "--output-md",
        default="artifacts/epistemic_gap_report.md",
        help="Output Markdown report path",
    )
    parser.add_argument(
        "--output-audit",
        default="artifacts/epistemic_gap_audit_sample.json",
        help="Output audit sample JSON path",
    )
    parser.add_argument(
        "--audit-size",
        type=int,
        default=50,
        help="Audit sample size (default: 50)",
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=42,
        help="Random seed for audit sample reproducibility",
    )
    args = parser.parse_args()

    # Set seed for reproducibility
    random.seed(args.seed)

    # Cargar trajectory
    input_path = Path(args.input)
    if not input_path.exists():
        print(f"ERROR: Input file not found: {input_path}")
        return 1

    with open(input_path, "r", encoding="utf-8") as f:
        trajectory = json.load(f)

    repository = trajectory.get("repository", "")

    # Detectar gaps
    detector = EpistemicGapDetector(repository=repository)
    report = detector.generate_report(trajectory)

    # Guardar JSON
    output_json = Path(args.output_json)
    output_json.parent.mkdir(parents=True, exist_ok=True)
    with open(output_json, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, ensure_ascii=False, default=str)

    # Guardar Markdown
    output_md = Path(args.output_md)
    output_md.parent.mkdir(parents=True, exist_ok=True)
    md_content = format_report_markdown(report)
    with open(output_md, "w", encoding="utf-8") as f:
        f.write(md_content)

    # Generate audit sample
    audit_sample = generate_audit_sample(report.get("gaps", []), args.audit_size)
    output_audit = Path(args.output_audit)
    output_audit.parent.mkdir(parents=True, exist_ok=True)
    with open(output_audit, "w", encoding="utf-8") as f:
        json.dump(audit_sample, f, indent=2, ensure_ascii=False, default=str)

    # Resumen a consola
    print("=" * 70)
    print("EPISTEMIC GAP DETECTOR — Cartografía Epistemológica")
    print("=" * 70)
    print(f"Objective: {report.get('objective', 'N/A')}")
    print()
    print(f"Repository: {repository}")
    print(f"Nodes analyzed: {report['metrics']['total_nodes_analyzed']}")
    print(f"Total gaps: {report['metrics']['total_gaps']}")
    print(f"Paradigm residues: {report['metrics']['total_paradigm_residues']}")
    print(f"Convergences: {report['metrics']['total_convergences']}")
    print()
    print("Triunvirato Epistemológico:")
    print()
    print("  Emperador     | Pregunta              | Gaps")
    print("  --------------|-----------------------|-----")
    tri = report.get("triumvirato", {})
    print(f"  Evidencia     | {tri.get('evidence', {}).get('question', ''):22}| {tri.get('evidence', {}).get('gaps_detected', 0)}")
    print(f"  Matemática    | {tri.get('mathematics', {}).get('question', ''):22}| {tri.get('mathematics', {}).get('gaps_detected', 0)}")
    print(f"  Causalidad    | {tri.get('causality', {}).get('question', ''):22}| {tri.get('causality', {}).get('gaps_detected', 0)}")
    print()
    print("Gap Characterization (A/B/C/D):")
    by_char = report["metrics"].get("by_characterization", {})
    char_labels = {
        "never_explored": "A: Never explored",
        "explored_abandoned": "B: Explored & abandoned",
        "explored_partial": "C: Explored partially",
        "unknown_exploration": "D: Unknown exploration",
    }
    for char_val, label in char_labels.items():
        count = by_char.get(char_val, 0)
        print(f"  {label}: {count}")
    print()
    print("Convergence detection:")
    print(f"  Successful convergences: {report['metrics']['convergences_successful']}")
    print(f"  Barrier convergences: {report['metrics']['convergences_barrier']}")
    print()
    print("Audit status:")
    audit = report.get("audit_status", {})
    print(f"  Status: {audit.get('status', 'N/A')}")
    print(f"  Threshold: {audit.get('threshold', 0.80)}")
    print(f"  EHG: {report['provenance'].get('ehg_status', 'N/A')}")
    print()
    print("Pipeline:")
    print("  EvidenceGraph → TrajectoryGraph → Epistemic Gaps → Characterization")
    print("  → Paradigm Residue → Convergence → Report")
    print("  [CONGELADO] → Hypothesis Generation (post-audit ≥80%)")
    print()
    print(f"JSON report:    {output_json}")
    print(f"Markdown report:{output_md}")
    print(f"Audit sample:   {output_audit}")
    print("=" * 70)

    return 0


def format_report_markdown(report: dict) -> str:
    lines = []
    lines.append("# EPISTEMIC GAP REPORT — Cartografía Epistemológica")
    lines.append(f"**Repository**: {report.get('repository', 'N/A')}")
    lines.append(f"**Generated**: {report.get('generated_at', 'N/A')}")
    lines.append(f"**Report ID**: {report.get('report_id', 'N/A')}")
    lines.append(f"**Objective**: {report.get('objective', 'N/A')}")
    lines.append("")

    # Cartography questions
    lines.append("## Preguntas de Cartografía")
    lines.append("")
    cq = report.get("cartography_questions", {})
    lines.append(f"1. **What do we know?** — {cq.get('q1_what_we_know', '')}")
    lines.append(f"2. **Why do we believe we know it?** — {cq.get('q2_why_we_believe', '')}")
    lines.append(f"3. **What paths did we follow to arrive here?** — {cq.get('q3_what_paths', '')}")
    lines.append(f"4. **Qué regiones permanecen inexploradas?** — {cq.get('q4_what_unexplored', '')}")
    lines.append(f"5. **Qué hypothesis merece la pena formular?** — {cq.get('q5_hypothesis', '')}")
    lines.append("")

    lines.append("## Triunvirato Epistemológico")
    lines.append("")
    lines.append("La ciencia avanza cuando los tres emperadores convergen. Ninguno es suficiente por sí solo.")
    lines.append("")
    lines.append("| Emperador | Pregunta | Modo de validación | Gaps detectados |")
    lines.append("|-----------|----------|-------------------|-----------------|")
    tri = report.get("triumvirato", {})
    lines.append(
        f"| **Evidencia** | {tri.get('evidence', {}).get('question', '')} | "
        f"{tri.get('evidence', {}).get('validation', '')} | "
        f"**{tri.get('evidence', {}).get('gaps_detected', 0)}** |"
    )
    lines.append(
        f"| **Matemática** | {tri.get('mathematics', {}).get('question', '')} | "
        f"{tri.get('mathematics', {}).get('validation', '')} | "
        f"**{tri.get('mathematics', {}).get('gaps_detected', 0)}** |"
    )
    lines.append(
        f"| **Causalidad** | {tri.get('causality', {}).get('question', '')} | "
        f"{tri.get('causality', {}).get('validation', '')} | "
        f"**{tri.get('causality', {}).get('gaps_detected', 0)}** |"
    )
    lines.append("")

    metrics = report.get("metrics", {})
    lines.append("## Métricas")
    lines.append("")
    lines.append(f"- **Total gaps**: {metrics.get('total_gaps', 0)}")
    lines.append(f"- Nodes analizados: {metrics.get('total_nodes_analyzed', 0)}")
    lines.append(f"- Gap density: {metrics.get('gap_density', 0)}")
    lines.append(f"- Paradigm residues: {metrics.get('total_paradigm_residues', 0)}")
    lines.append(f"- Convergences: {metrics.get('total_convergences', 0)}")
    lines.append("")

    lines.append("### By Severity")
    lines.append("")
    by_sev = metrics.get("by_severity", {})
    lines.append(f"- HIGH: {by_sev.get('high', 0)}")
    lines.append(f"- MEDIUM: {by_sev.get('medium', 0)}")
    lines.append(f"- LOW: {by_sev.get('low', 0)}")
    lines.append("")

    lines.append("### By Characterization (A/B/C/D)")
    lines.append("")
    by_char = metrics.get("by_characterization", {})
    lines.append("| Tipo | Descripción | Count |")
    lines.append("|------|-------------|-------|")
    char_descs = {
        "never_explored": "A: Nunca se exploró",
        "explored_abandoned": "B: Se exploró y se abandonó",
        "explored_partial": "C: Se exploró parcialmente",
        "unknown_exploration": "D: No sabemos si fue explorado",
    }
    for char_val, desc in char_descs.items():
        count = by_char.get(char_val, 0)
        lines.append(f"| {char_val} | {desc} | {count} |")
    lines.append("")

    # Paradigm Residues
    residues = report.get("paradigm_residues", [])
    if residues:
        lines.append("## Paradigm Residues")
        lines.append("")
        lines.append("Lo que cambió y lo que permaneció entre decisiones sucesivas:")
        lines.append("")
        lines.append("| Residue | From → To | What changed | What remained |")
        lines.append("|---------|-----------|--------------|---------------|")
        for res in residues[:10]:
            changed = ", ".join(res.get("what_changed", [])[:3])
            remained = ", ".join(res.get("what_remained", [])[:3])
            lines.append(
                f"| {res['residue_id']} | {res['from_decision']} → {res['to_decision']} | "
                f"{changed} | {remained} |"
            )
        lines.append("")
        if len(residues) > 10:
            lines.append(f"... and {len(residues) - 10} more paradigm residues.")
            lines.append("")

    # Convergences
    convergences = report.get("convergences", [])
    if convergences:
        lines.append("## Convergences")
        lines.append("")
        lines.append("Trayectorias independientes que convergen:")
        lines.append("")
        for conv in convergences[:10]:
            lines.append(f"**{conv['convergence_id']}** — {conv['type']}")
            lines.append(f"- Theme: {conv.get('theme', '')}")
            lines.append(f"- Actors: {', '.join(conv.get('independent_actors', []))}")
            lines.append(f"- Description: {conv.get('description', '')}")
            lines.append("")
        if len(convergences) > 10:
            lines.append(f"... and {len(convergences) - 10} more convergences.")
            lines.append("")

    # Top gaps by type
    lines.append("## Gaps by Type")
    lines.append("")

    for gap_type, label in [
        ("empirical", "### Gap Empírico — What do we observe?"),
        ("mathematical", "### Gap Matemático — Is it coherent?"),
        ("causal", "### Gap Causal — Why does it occur?"),
    ]:
        type_gaps = [g for g in report.get("gaps", []) if g.get("gap_type") == gap_type]
        lines.append(label)
        lines.append("")
        if not type_gaps:
            lines.append("No gaps detected of this type.")
            lines.append("")
            continue

        # Mostrar top 5 por severidad
        sev_order = {"high": 0, "medium": 1, "low": 2}
        type_gaps_sorted = sorted(
            type_gaps, key=lambda g: sev_order.get(g.get("severity", "low"), 3)
        )
        for gap in type_gaps_sorted[:5]:
            char_label = gap.get("characterization", "unknown")
            lines.append(f"**{gap['gap_id']}** [{gap['severity'].upper()}] [{char_label}]")
            lines.append(f"- Location: `{gap['location']}`")
            lines.append(f"- Signal: `{gap['detection_signal']}`")
            lines.append(f"- Description: {gap['description']}")
            lines.append(f"- Evidence: {gap['evidence_anchor']}")
            lines.append(f"- Resolution: {gap['resolution_path']}")
            lines.append("")

        if len(type_gaps) > 5:
            lines.append(f"... and {len(type_gaps) - 5} more gaps of this type.")
            lines.append("")

    # Audit status
    lines.append("## Audit Status")
    lines.append("")
    audit = report.get("audit_status", {})
    lines.append(f"- **Status**: {audit.get('status', 'N/A')}")
    lines.append(f"- Total gaps: {audit.get('total_gaps', 0)}")
    lines.append(f"- Audited: {audit.get('audited', 0)}")
    lines.append(f"- Unaudited: {audit.get('unaudited', 0)}")
    lines.append(f"- Precision threshold: {audit.get('threshold', 0.80)}")
    lines.append(f"- Current precision: {audit.get('precision', 'N/A (pending audit)')}")
    lines.append("")
    lines.append("> **Próximo paso**: Auditar 50 gaps aleatorios. Ver `artifacts/epistemic_gap_audit_sample.json`")
    lines.append("")

    lines.append("---")
    lines.append("")
    lines.append("## Pipeline")
    lines.append("")
    lines.append("```")
    lines.append("EvidenceGraph (v1.1.0 — STABLE)")
    lines.append("    ↓")
    lines.append("TrajectoryGraph (SPRINT 60C)")
    lines.append("    ↓")
    lines.append("Epistemic Gap Detection (this report)")
    lines.append("    ↓")
    lines.append("Gap Characterization (A/B/C/D)")
    lines.append("    ↓")
    lines.append("Paradigm Residue Detection")
    lines.append("    ↓")
    lines.append("Convergence Detection")
    lines.append("    ↓")
    lines.append("[CONGELADO] EHG v2: Research Cartographer (post-audit ≥80%)")
    lines.append("```")
    lines.append("")
    lines.append("## Freeze Compliance")
    lines.append("")
    lines.append("- ✅ No new schemas created")
    lines.append("- ✅ No new graphs created")
    lines.append("- ✅ No new layers created")
    lines.append("- ✅ No existing schemas modified")
    lines.append("- ✅ Read-only analysis over existing data")
    lines.append("- ✅ Produces real artifacts (JSON + Markdown)")
    lines.append("- ✅ EHG congelado (no hypothesis generation)")
    lines.append("")
    lines.append("*Un hueco no es una hypothesis. Primero cartografiamos. Sólo después exploramos.*")
    lines.append("*Ver: docs/EPISTEMIC_GAP_CONCEPT.md*")

    return "\n".join(lines)


if __name__ == "__main__":
    sys.exit(main())