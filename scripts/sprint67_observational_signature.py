#!/usr/bin/env python3
"""
SPRINT 67 — Observational Signature Discovery

Prohibido crear nuevas entidades epistemologicas.
No nuevos indices, taxonomias, scores, frameworks filosoficos, ontologias.

Busca unicamente patrones observables.

Pregunta:
  Que firmas observables aparecen repetidamente antes de una convergencia?

Entregable:
  artifacts/observable_signature.json

Regla metodologica:
  Prohibido utilizar en codigo: restriccion, paradigma, mecanismo, causa.
  Esas palabras solo en documentacion de discusion.

Ataque obligatorio:
  Clasificar convergencia real vs sintetica utilizando unicamente observables.
  Sin hipotesis. Sin restricciones. Sin interpretacion humana.

Criterio de exito:
  FPR < 30% (mejor que 70% del detector anterior)
"""
import sys
import json
from pathlib import Path
from datetime import datetime, timezone
from typing import Dict, Any, List

project_root = Path(__file__).resolve().parent.parent


def extract_observable_features(convergence: Dict[str, Any], trajectory: Dict[str, Any]) -> Dict[str, Any]:
    """Extrae unicamente features observables de una convergencia."""
    features = {}
    convergence_nodes = convergence.get("nodes", [])
    node_ids = {n.get("node_id") or n.get("id") for n in convergence_nodes}
    prior_decisions = []
    for edge in trajectory.get("edges", []):
        source = edge.get("source") or edge.get("from")
        target = edge.get("target") or edge.get("to")
        if target in node_ids:
            prior_decisions.append({
                "source": source,
                "target": target,
                "type": edge.get("type", "unknown"),
                "timestamp": edge.get("timestamp", ""),
            })
    features["convergence_id"] = convergence.get("convergence_id", convergence.get("id", "unknown"))
    features["num_actors"] = len({n.get("actor", "unknown") for n in convergence_nodes})
    features["num_nodes"] = len(convergence_nodes)
    features["num_prior_decisions"] = len(prior_decisions)
    features["num_failed_attempts"] = sum(1 for n in convergence_nodes if "fail" in str(n.get("outcome", "")).lower())
    features["num_abandonments"] = sum(1 for n in convergence_nodes if "abandon" in str(n.get("outcome", "")).lower())
    features["num_branches"] = sum(1 for e in prior_decisions if e["type"] in ("chosen_over", "abandoned_for"))
    features["duration_days"] = _compute_duration(prior_decisions)
    features["distinct_repositories"] = len({n.get("repository", "unknown") for n in convergence_nodes})
    features["has_explicit_reference"] = any(e.get("type") in ("superseded_by", "chosen_over", "abandoned_for") for e in prior_decisions)
    features["avg_prior_confidence"] = _avg_confidence(prior_decisions, trajectory)
    titles = [n.get("title", "") for n in convergence_nodes]
    features["common_keywords"] = _extract_keywords(titles)
    features["theme"] = convergence.get("theme", "unknown")
    return features


def _compute_duration(decisions: List[Dict[str, Any]]) -> int:
    """Duracion en dias entre primera y ultima decision."""
    timestamps = [d.get("timestamp", "") for d in decisions if d.get("timestamp")]
    if len(timestamps) < 2:
        return 0
    try:
        dates = [datetime.fromisoformat(ts.replace("Z", "+00:00")) for ts in timestamps]
        return (max(dates) - min(dates)).days
    except Exception:
        return 0


def _avg_confidence(decisions: List[Dict[str, Any]], trajectory: Dict[str, Any]) -> float:
    """Confianza promedio de decisiones previas."""
    confidences = []
    for d in decisions:
        confidence = d.get("confidence")
        if confidence is not None:
            confidences.append(confidence)
    return sum(confidences) / len(confidences) if confidences else 0.0


def _extract_keywords(titles: List[str]) -> List[str]:
    """Extrae keywords comunes entre titulos."""
    if not titles:
        return []
    words = []
    for title in titles:
        words.extend([w.lower() for w in title.split() if len(w) > 4])
    freq = {}
    for w in words:
        freq[w] = freq.get(w, 0) + 1
    return [w for w, c in freq.items() if c >= 2]


def classify_convergence(features: Dict[str, Any]) -> str:
    """Clasifica convergencia como real o sintetica usando solo features observables."""
    score = 0
    if features.get("num_actors", 0) >= 3:
        score += 1
    if features.get("distinct_repositories", 0) >= 2:
        score += 1
    if features.get("has_explicit_reference"):
        score += 1
    if features.get("num_failed_attempts", 0) >= 3:
        score += 1
    if features.get("num_prior_decisions", 0) >= 2:
        score += 1
    if features.get("num_actors", 0) == 1:
        score -= 2
    if features.get("duration_days", 0) < 7:
        score -= 1
    if features.get("num_prior_decisions", 0) == 0:
        score -= 1
    return "real" if score >= 2 else "synthetic"


def main():
    print("=" * 70)
    print("SPRINT 67 — Observational Signature Discovery")
    print("=" * 70)
    print("Objetivo: Buscar firmas observables antes de explicar")
    print()

    trajectory = {}
    convergences = []

    # Try to load real trajectory data
    trajectory_path = Path("data/trajectories/trajectory_graph.json")
    if trajectory_path.exists():
        try:
            with open(trajectory_path, "r", encoding="utf-8") as f:
                trajectory = json.load(f)
            from python.discovery.epistemic_gap_detector import EpistemicGapDetector
            detector = EpistemicGapDetector(repository=trajectory.get("repository", ""))
            report = detector.generate_report(trajectory)
            convergences = report.get("convergences", [])
        except Exception as e:
            print(f"WARNING: Could not load trajectory data: {e}")

    if not convergences:
        print("No trajectory data found. Generating synthetic signatures for methodology demonstration.")
        convergences = _generate_synthetic_convergences()

    signatures = []
    for conv in convergences:
        features = extract_observable_features(conv, trajectory)
        classification = classify_convergence(features)
        signatures.append({
            "convergence_id": features["convergence_id"],
            "features": features,
            "classification": classification,
        })

    real_count = sum(1 for s in signatures if s["classification"] == "real")
    synthetic_count = sum(1 for s in signatures if s["classification"] == "synthetic")

    print(f"Total convergences analyzed: {len(signatures)}")
    print(f"Classified as real: {real_count}")
    print(f"Classified as synthetic: {synthetic_count}")
    print()

    print("[Sample Signatures]")
    for s in signatures[:3]:
        print(f"  {s['convergence_id']}: actors={s['features']['num_actors']}, "
              f"failed={s['features']['num_failed_attempts']}, "
              f"branches={s['features']['num_branches']}, "
              f"duration={s['features']['duration_days']}d, "
              f"-> {s['classification']}")

    report = {
        "report_id": f"OBS67-{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S')}",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "sprint": "SPRINT 67 — Observational Signature Discovery",
        "objective": "Buscar unicamente patrones observables antes de convergencias. Sin explicacion. Sin teoria. Sin interpretacion.",
        "methodology": {
            "prohibited_words": ["restriccion", "paradigma", "mecanismo", "causa"],
            "features_extracted": [
                "num_actors", "num_nodes", "num_prior_decisions",
                "num_failed_attempts", "num_abandonments", "num_branches",
                "duration_days", "distinct_repositories", "has_explicit_reference",
                "avg_prior_confidence", "common_keywords", "theme"
            ],
            "classification_method": "Rule-based scoring using only observable features",
        },
        "signatures": signatures,
        "summary": {
            "total_convergences": len(signatures),
            "real_classified": real_count,
            "synthetic_classified": synthetic_count,
        },
        "attack_result": {
            "method": "Rule-based classification without hypotheses",
            "fpr_estimate": "Not directly measurable without ground truth labels",
            "note": "Classification uses only observable features. No constraints, no paradigms, no mechanisms.",
        },
        "epistemic_note": (
            "Este sprint NO genera explicaciones. NO infiere restricciones. "
            "Solo extrae firmas observables. Cualquier intento de explicar "
            "las firmas debe detenerse inmediatamente."
        ),
    }

    output_json = Path("artifacts/observable_signature.json")
    output_json.parent.mkdir(parents=True, exist_ok=True)
    with open(output_json, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, ensure_ascii=False, default=str)

    print()
    print("=" * 70)
    print(f"Output: {output_json}")
    print(f"Signatures extracted: {len(signatures)}")
    print("=" * 70)

    return 0


def _generate_synthetic_convergences() -> List[Dict[str, Any]]:
    """Genera convergencias sinteticas para demostracion metodologica."""
    return [
        {
            "convergence_id": "CONV-DEMO-001",
            "nodes": [
                {"actor": "dev1", "outcome": "failed", "title": "issue with api"},
                {"actor": "dev2", "outcome": "failed", "title": "api problem"},
                {"actor": "dev3", "outcome": "failed", "title": "api issue"},
            ],
            "theme": "api",
        },
        {
            "convergence_id": "CONV-DEMO-002",
            "nodes": [
                {"actor": "dev4", "outcome": "abandoned", "title": "memory leak"},
                {"actor": "dev5", "outcome": "abandoned", "title": "memory issue"},
            ],
            "theme": "memory",
        },
    ]


if __name__ == "__main__":
    sys.exit(main())