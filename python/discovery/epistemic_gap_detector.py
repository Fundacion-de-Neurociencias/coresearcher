"""
Epistemic Gap Detector — Triunvirato Epistemológico

Detecta y clasifica Epistemic Gaps desde datos existentes
(TrajectoryGraph / EvidenceGraph) sin añadir nuevos schemas,
grafos, ni capas arquitectónicas.

Triunvirato:
  Evidencia   → What do we observe?      → Datos
  Matemática  → Is it coherent?        → Demostración
  Causalidad  → Why does it occur?      → Intervención / mecanismo

Cada gap detectado se ancla a evidencia observable (nunca especulado).
Esto es un análisis derivado read-only, no un schema ni un grafo.

See: docs/EPISTEMIC_GAP_CONCEPT.md
"""

from __future__ import annotations

from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional

import json

# Security tier: PRIVATE — DO NOT MODIFY
# See python/_tiers.py for classification
SECURITY_TIER = "PRIVATE"


class GapType(str, Enum):
    """Los tres emperadores del razonamiento científico."""

    EMPIRICAL = "empirical"       # What do we observe? → faltan datos
    MATHEMATICAL = "mathematical"  # Is it coherent? → falta demostración
    CAUSAL = "causal"             # Why does it occur? → lacks mechanism


class GapCharacterization(str, Enum):
    """
    Historia de exploración del gap (A/B/C/D).

    A gap is not a hypothesis. A gap is merely
    an unmapped or poorly charted region of the knowledge space.
    Antes de generar hypothesis hay que caracterizar el gap.
    """

    NEVER_EXPLORED = "never_explored"            # A: Nunca se exploró
    EXPLORED_ABANDONED = "explored_abandoned"    # B: Se exploró y se abandonó
    EXPLORED_PARTIAL = "explored_partial"        # C: Se exploró parcialmente
    UNKNOWN_EXPLORATION = "unknown_exploration"  # D: No sabemos si fue explorado


class Severity(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class RestrictionType(str, Enum):
    """
    Experimental taxonomy of restrictions (not a schema, not an ontology).

    No restriction is directly observable; only its manifestations are observable.
    This taxonomy is an experimental classification to label shared restriction
    hypotheses during convergence auditing.

    Scientific value: a convergence caused by a technical limitation
    has much less value than one caused by a conceptual assumption.
    """

    TECHNICAL = "tecnica"          # API, computational, external dependency limitation
    MATHEMATICAL = "matematica"    # Complexity, convergence, identifiability
    CONCEPTUAL = "conceptual"      # Dominant paradigm, accepted definition, inherited abstraction
    HISTORICAL = "historica"       # Backward compatibility, past decisions, lock-in
    ONTOLOGICAL = "ontologica"     # Assumptions about the nature of the system
    UNKNOWN = "desconocida"        # Cannot be determined (epistemic honesty)


class EpistemicStatus(str, Enum):
    """
    Epistemic status of any statement in the system.

    Forbids confusing observation with hypothesis.
    Forbids promoting hypothesis to fact without falsification.
    Allows stating "we do not know" without degrading evaluation.

    Fundamental rule:
    > A false theory is worse than admitting that we do not yet have a theory.

    Inspired by research on LRM reasoning:
    - Do not confuse outcome with observable process
    - Do not confuse observable process with real mechanism
    - Do not confuse plausible explanation with demonstrated explanation

    See: docs/EPISTEMIC_GAP_CONCEPT.md §4 (Inference Audit)
    """

    OBSERVED = "observed"           # Directly observable in evidence
    DERIVED = "derived"             # Logically derived from observations
    HYPOTHESIZED = "hypothesized"   # Proposed explanation, not falsified
    FALSIFIED = "falsified"         # Hypothesis falsified by evidence
    UNDETERMINED = "undetermined"   # Multiple hypotheses explain equally well


@dataclass
class ConstraintHypothesis:
    """
    Shared restriction hypothesis explaining an observed convergence.

    Principles (SPRINT 60C/H7 — IDE Directive):
    1. Every hypothesis must have at least one rival competitor.
    2. Every hypothesis must specify falsification criteria.
    3. No hypothesis can be promoted to fact without falsifying competitors.
    4. If two hypotheses explain equally well -> UNDETERMINED.

    Prohibition of "wishful mnemonic" (McDermott):
    - ❌ "detected restriction"
    - ✔ "restriction hypothesis explaining observed convergence"
    - Forbidden to introduce ontologically loaded terms without
      operational definition and falsification criterion.
    """

    hypothesis_id: str
    description: str
    restriction_type: RestrictionType
    epistemic_status: EpistemicStatus = EpistemicStatus.HYPOTHESIZED
    falsification_criteria: List[str] = field(default_factory=list)
    operational_definition: str = ""
    is_principal: bool = False

    def to_dict(self) -> Dict[str, Any]:
        d = asdict(self)
        d["restriction_type"] = self.restriction_type.value
        d["epistemic_status"] = self.epistemic_status.value
        return d


@dataclass
class EpistemicGap:
    """
    An Epistemic Gap is a region of the knowledge space
    where ignorance is classifiable and operational.

    Scientific concept — NOT an EvidenceGraph node nor a schema.

    A gap is not a hypothesis. A gap is merely
    an unmapped or poorly charted region of the knowledge space.
    """

    gap_id: str
    gap_type: GapType
    characterization: GapCharacterization  # A/B/C/D — exploration history
    location: str               # Node/decision ID where detected
    description: str            # Specifically what is unknown
    evidence_anchor: str        # Observable URL or ID revealing the gap
    resolution_path: str        # What type of activity would resolve the gap
    severity: Severity
    detection_signal: str       # Heuristic signal that detected it
    repository: str = ""
    audit_status: str = "unaudited"  # unaudited | real | artifact | indeterminate
    epistemic_status: EpistemicStatus = EpistemicStatus.OBSERVED
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        d = asdict(self)
        d["gap_type"] = self.gap_type.value
        d["characterization"] = self.characterization.value
        d["severity"] = self.severity.value
        d["epistemic_status"] = self.epistemic_status.value
        return d


@dataclass
class ParadigmResidue:
    """
    What changed and what remained between two successive decisions.

    Science progresses by changing few things and conserving many.
    Paradigm residue defines unexplored pathways.
    """

    residue_id: str
    from_decision: str
    to_decision: str
    what_changed: List[str] = field(default_factory=list)
    what_remained: List[str] = field(default_factory=list)
    repository: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class EpistemicGapDetector:
    """
    Epistemic Gap Detector on existing TrajectoryGraph.

    Input: trajectory_graph.json (SPRINT 60C format)
    Output: GapReport with classified gaps by type

    Traceability constraint:
        Every gap must have an observable evidence_anchor.
        Gaps are not invented. They are detected from real evidence.
    """

    # ------------------------------------------------------------------
    # Heuristic patterns for mathematical gap detection
    # ------------------------------------------------------------------
    MATH_SIGNALS = [
        "converge", "convergence", "proof", "theorem", "lemma",
        "axiom", "corollary", "derivation", "formal", "proven",
        "demonstrably", "rigorously", "mathematically",
    ]

    CAUSAL_SIGNALS = [
        "because", "causes", "leads to", "results in", "due to",
        "root cause", "mechanism", "explains", "underlying",
        "driven by", "responsible for",
    ]

    def __init__(self, repository: str = ""):
        self.repository = repository
        self.gaps: List[EpistemicGap] = []
        self.residues: List[ParadigmResidue] = []
        self.convergences: List[Dict[str, Any]] = []
        self._gap_counter = 0
        self._residue_counter = 0

    # ------------------------------------------------------------------
    # API principal
    # ------------------------------------------------------------------

    def detect_from_trajectory(self, trajectory: Dict[str, Any]) -> List[EpistemicGap]:
        """
        Detecta Epistemic Gaps desde un TrajectoryGraph.

        Args:
            trajectory: Dict con keys 'nodes' y 'edges' (formato SPRINT 60C)

        Returns:
            Lista de EpistemicGap detectados
        """
        self.gaps = []
        self.residues = []
        self.convergences = []
        self._gap_counter = 0
        self._residue_counter = 0

        nodes = trajectory.get("nodes", [])
        edges = trajectory.get("edges", [])

        # Construir índices para análisis
        node_map = {n.get("decision_id", n.get("id", "")): n for n in nodes}
        edges_by_source: Dict[str, List[Dict]] = {}
        edges_by_target: Dict[str, List[Dict]] = {}
        for e in edges:
            src = e.get("from", "")
            tgt = e.get("to", "")
            edges_by_source.setdefault(src, []).append(e)
            edges_by_target.setdefault(tgt, []).append(e)

        # Detect each gap type (with characterization A/B/C/D)
        self._detect_empirical_gaps(nodes, edges_by_source, node_map)
        self._detect_mathematical_gaps(nodes, edges_by_source, node_map)
        self._detect_causal_gaps(nodes, edges, edges_by_source, edges_by_target, node_map)

        # Paradigm Residue: qué cambió y qué permaneció
        self._detect_paradigm_residues(nodes, edges, node_map)

        # Convergence: trayectorias independientes que convergen
        self._detect_convergences(nodes, edges, node_map)

        return self.gaps

    def generate_report(self, trajectory: Dict[str, Any]) -> Dict[str, Any]:
        """
        Genera un reporte completo de Epistemic Gaps.

        Returns:
            Dict con gaps, métricas, y metadatos
        """
        gaps = self.detect_from_trajectory(trajectory)

        # Metrics by type
        by_type: Dict[str, int] = {gt.value: 0 for gt in GapType}
        by_severity: Dict[str, int] = {sv.value: 0 for sv in Severity}
        for g in gaps:
            by_type[g.gap_type.value] += 1
            by_severity[g.severity.value] += 1

        total_nodes = len(trajectory.get("nodes", []))
        gap_density = len(gaps) / total_nodes if total_nodes > 0 else 0.0

        # Characterization metrics (A/B/C/D)
        by_characterization: Dict[str, int] = {gc.value: 0 for gc in GapCharacterization}
        for g in gaps:
            by_characterization[g.characterization.value] += 1

        # Epistemic status metrics (v1.6 — Directiva IDE)
        by_epistemic_status: Dict[str, int] = {es.value: 0 for es in EpistemicStatus}
        for g in gaps:
            by_epistemic_status[g.epistemic_status.value] += 1

        report = {
            "report_id": f"EGAP-{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S')}",
            "repository": self.repository,
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "objective": "Cartografiar el espacio de conocimiento (no generar hypothesis)",
            "cartography_questions": {
                "q1_what_we_know": "What do we know?",
                "q2_why_we_believe": "Why do we believe we know it?",
                "q3_what_paths": "What paths did we follow to arrive here?",
                "q4_what_unexplored": "Qué regiones permanecen inexploradas?",
                "q5_hypothesis": "CONGELADO — requiere validación ≥80%",
            },
            "triumvirato": {
                "evidence": {
                    "question": "What do we observe?",
                    "validation": "Datos",
                    "gaps_detected": by_type[GapType.EMPIRICAL.value],
                },
                "mathematics": {
                    "question": "Is it coherent?",
                    "validation": "Demostración",
                    "gaps_detected": by_type[GapType.MATHEMATICAL.value],
                },
                "causality": {
                    "question": "Why does it occur?",
                    "validation": "Intervención / mecanismo",
                    "gaps_detected": by_type[GapType.CAUSAL.value],
                },
            },
            "epistemic_discipline": {
                "principle": (
                    "Una teoría falsa es peor que admitir que "
                    "todavía no tenemos teoría."
                ),
                "rules": [
                    "Toda constraint es variable latente (no observable)",
                    "Toda convergence es observación (no explicación)",
                    "Prohibido promover constraint a hecho",
                    "Toda hypothesis de constraint debe tener competidora",
                    "Si dos hypothesis explican igualmente bien → UNDETERMINED",
                    "'No sabemos' es estado epistemológico legítimo",
                ],
                "wishful_mnemonic_prohibition": (
                    "Prohibido introducir términos ontológicamente cargados "
                    "sin operational definition and falsification criterion. "
                    "❌ 'constraint detectada' → "
                    "✔ 'hypothesis de constraint que explica la "
                    "convergence observada'"
                ),
                "status_values": [es.value for es in EpistemicStatus],
            },
            "metrics": {
                "total_gaps": len(gaps),
                "by_type": by_type,
                "by_severity": by_severity,
                "by_characterization": by_characterization,
                "total_nodes_analyzed": total_nodes,
                "gap_density": round(gap_density, 4),
                "total_paradigm_residues": len(self.residues),
                "total_convergences": len(self.convergences),
                "convergences_successful": sum(
                    1 for c in self.convergences if c.get("type") == "successful_convergence"
                ),
                "convergences_barrier": sum(
                    1 for c in self.convergences if c.get("type") == "barrier_convergence"
                ),
                "by_epistemic_status": by_epistemic_status,
                "convergences_with_competing_hypotheses": sum(
                    1 for c in self.convergences
                    if len(c.get("constraint_hypotheses", [])) >= 2
                ),
                "convergences_undetermined": sum(
                    1 for c in self.convergences
                    if c.get("restriction_epistemic_status")
                    == EpistemicStatus.UNDETERMINED.value
                ),
            },
            "gaps": [g.to_dict() for g in gaps],
            "paradigm_residues": [r.to_dict() for r in self.residues],
            "convergences": self.convergences,
            "audit_status": {
                "total_gaps": len(gaps),
                "audited": 0,
                "unaudited": len(gaps),
                "precision": None,
                "threshold": 0.80,
                "status": "PENDING_AUDIT",
            },
            "provenance": {
                "generated_by": "epistemic_gap_detector",
                "detector_version": "1.2.0",
                "input_artifact": "trajectory_graph.json",
                "analysis_type": "derived_read_only",
                "freeze_compliance": "No new schemas, graphs, or layers",
                "ehg_status": "FROZEN — requires audit precision ≥80%",
            },
        }
        return report

    # ------------------------------------------------------------------
    # Detectors by type
    # ------------------------------------------------------------------

    def _detect_empirical_gaps(
        self,
        nodes: List[Dict],
        edges_by_source: Dict[str, List[Dict]],
        node_map: Dict[str, Dict],
    ) -> None:
        """
        Gap Empírico: No tenemos datos.

        Señales:
        - Decision con outcome 'pending' y sin edges salientes (sin resultado)
        - Decision abandonada sin rationale que explique por qué
        - Decision con confidence muy baja (< 0.5) — evidencia insuficiente
        """
        for node in nodes:
            node_id = node.get("decision_id", node.get("id", ""))
            outcome = node.get("outcome", "")
            confidence = node.get("confidence", 0.5)
            rationale = node.get("rationale", "")
            artifact_url = node.get("artifact_url", "")
            title = node.get("title", node.get("decision", ""))

            # Signal 1: Pending without outgoing edges -> no observable result
            outgoing = edges_by_source.get(node_id, [])
            if outcome == "pending" and len(outgoing) == 0:
                self._add_gap(
                    GapType.EMPIRICAL,
                    location=node_id,
                    description=(
                        f"Decision '{title[:80]}' has outcome 'pending' "
                        f"with no observable result artifact. "
                        f"We do not know if this was resolved."
                    ),
                    evidence_anchor=artifact_url or node_id,
                    resolution_path="Observe outcome: check if issue/PR was resolved",
                    severity=Severity.MEDIUM,
                    detection_signal="pending_no_outgoing_edges",
                    metadata={"outcome": outcome, "confidence": confidence},
                )

            # Signal 2: Abandoned without rationale -> failure cause unknown
            if outcome == "abandoned" and not rationale.strip():
                self._add_gap(
                    GapType.EMPIRICAL,
                    location=node_id,
                    description=(
                        f"Decision '{title[:80]}' was abandoned but no rationale "
                        f"was recorded. We do not know what evidence caused abandonment."
                    ),
                    evidence_anchor=artifact_url or node_id,
                    resolution_path="Recover rationale from discussion threads or commit messages",
                    severity=Severity.HIGH,
                    detection_signal="abandoned_no_rationale",
                    metadata={"outcome": outcome, "confidence": confidence},
                )

            # Señal 3: Confidence muy baja → evidencia insuficiente
            if confidence < 0.5 and outcome in ("pending", "abandoned", "failure"):
                self._add_gap(
                    GapType.EMPIRICAL,
                    location=node_id,
                    description=(
                        f"Decision '{title[:80]}' has low confidence ({confidence}) "
                        f"and outcome '{outcome}'. Insufficient evidence to determine "
                        f"what actually happened."
                    ),
                    evidence_anchor=artifact_url or node_id,
                    resolution_path="Gather additional evidence: related issues, commits, discussions",
                    severity=Severity.MEDIUM,
                    detection_signal="low_confidence_unresolved",
                    metadata={"outcome": outcome, "confidence": confidence},
                )

    def _detect_mathematical_gaps(
        self,
        nodes: List[Dict],
        edges_by_source: Dict[str, List[Dict]],
        node_map: Dict[str, Dict],
    ) -> None:
        """
        Gap Matemático: No sabemos si es consistente.

        Señales:
        - Rationale o body que invoca términos matemáticos (converge, proof, theorem)
          sin referencia verificable a una demostración
        - Claim clasificada como 'derivable' sin verificación formal
        - Decision que asume una propiedad sin demostración
        """
        for node in nodes:
            node_id = node.get("decision_id", node.get("id", ""))
            rationale = node.get("rationale", "")
            body = node.get("body_snippet", "")
            title = node.get("title", node.get("decision", ""))
            artifact_url = node.get("artifact_url", "")
            combined_text = f"{title} {rationale} {body}".lower()

            # Señal 1: Invoca señales matemáticas sin demostración verificable
            found_math_signals = [s for s in self.MATH_SIGNALS if s in combined_text]
            if found_math_signals and "http" not in rationale.lower():
                # No hay referencia verificable a una demostración
                self._add_gap(
                    GapType.MATHEMATICAL,
                    location=node_id,
                    description=(
                        f"Decision '{title[:80]}' invokes mathematical concepts "
                        f"({', '.join(found_math_signals[:3])}) but provides no "
                        f"verifiable reference to a formal proof or demonstration."
                    ),
                    evidence_anchor=artifact_url or node_id,
                    resolution_path="Formalize the claim and verify or falsify via proof",
                    severity=Severity.MEDIUM,
                    detection_signal="math_invocation_no_proof_reference",
                    metadata={"math_signals": found_math_signals},
                )

            # Señal 2: Classification 'derivable' sin verificación formal
            classification = node.get("classification", "")
            if classification == "derivable" and outcome_is_failure_or_abandoned(node):
                self._add_gap(
                    GapType.MATHEMATICAL,
                    location=node_id,
                    description=(
                        f"Decision '{title[:80]}' was classified as 'derivable' "
                        f"but resulted in '{node.get('outcome', '')}'. The derivation "
                        f"may be inconsistent with observed outcomes."
                    ),
                    evidence_anchor=artifact_url or node_id,
                    resolution_path="Re-derive the claim and check for inconsistency",
                    severity=Severity.HIGH,
                    detection_signal="derivable_but_failed",
                    metadata={"classification": classification, "outcome": node.get("outcome")},
                )

    def _detect_causal_gaps(
        self,
        nodes: List[Dict],
        edges: List[Dict],
        edges_by_source: Dict[str, List[Dict]],
        edges_by_target: Dict[str, List[Dict]],
        node_map: Dict[str, Dict],
    ) -> None:
        """
        Gap Causal: No sabemos por qué ocurre.

        Señales:
        - Decision con outcome 'failure' donde el rationale no identifica causa raíz
        - Múltiples decisions abandonadas sobre el mismo tema (patrón recurrente)
          sin mecanismo explicativo
        - Edge 'abandoned_for' sin rationale que explique por qué la alternativa fue mejor
        """
        # Señal 1: Failure sin causa raíz en rationale
        for node in nodes:
            node_id = node.get("decision_id", node.get("id", ""))
            outcome = node.get("outcome", "")
            rationale = node.get("rationale", "")
            title = node.get("title", node.get("decision", ""))
            artifact_url = node.get("artifact_url", "")

            if outcome == "failure" and not self._has_causal_signal(rationale):
                self._add_gap(
                    GapType.CAUSAL,
                    location=node_id,
                    description=(
                        f"Decision '{title[:80]}' failed but rationale does not "
                        f"identify a root cause. We do not know why it failed."
                    ),
                    evidence_anchor=artifact_url or node_id,
                    resolution_path="Investigate mechanism: what caused the failure?",
                    severity=Severity.HIGH,
                    detection_signal="failure_no_causal_rationale",
                    metadata={"outcome": outcome},
                )

        # Signal 2: Multiple abandoned decisions on same topic -> pattern without mechanism
        title_clusters = self._cluster_by_title_similarity(nodes)
        for cluster_key, cluster_nodes in title_clusters.items():
            abandoned_count = sum(
                1 for n in cluster_nodes if n.get("outcome") == "abandoned"
            )
            if abandoned_count >= 3:
                # Recurrent abandonment pattern without explanatory mechanism
                sample = cluster_nodes[0]
                sample_id = sample.get("decision_id", sample.get("id", ""))
                self._add_gap(
                    GapType.CAUSAL,
                    location=sample_id,
                    description=(
                        f"{abandoned_count} decisions on '{cluster_key[:60]}' were "
                        f"abandoned. No underlying mechanism explains why this "
                        f"approach repeatedly fails."
                    ),
                    evidence_anchor=sample.get("artifact_url", sample_id),
                    resolution_path="Identify causal mechanism: why does this approach fail repeatedly?",
                    severity=Severity.HIGH,
                    detection_signal="repeated_abandonment_no_mechanism",
                    metadata={
                        "abandoned_count": abandoned_count,
                        "cluster_size": len(cluster_nodes),
                        "related_decisions": [
                            n.get("decision_id", n.get("id", "")) for n in cluster_nodes[:5]
                        ],
                    },
                )

        # Signal 3: Edge 'abandoned_for' without rationale in winning decision
        for edge in edges:
            if edge.get("type") == "abandoned_for":
                winner_id = edge.get("to", "")
                winner = node_map.get(winner_id, {})
                winner_rationale = winner.get("rationale", "")
                if not winner_rationale.strip():
                    loser_id = edge.get("from", "")
                    self._add_gap(
                        GapType.CAUSAL,
                        location=winner_id,
                        description=(
                            f"Decision {winner_id} was chosen over {loser_id} "
                            f"but no rationale explains why. The causal basis "
                            f"for the choice is unknown."
                        ),
                        evidence_anchor=winner.get("artifact_url", winner_id),
                        resolution_path="Recover rationale: why was this alternative chosen?",
                        severity=Severity.MEDIUM,
                        detection_signal="chosen_over_no_rationale",
                        metadata={"winner": winner_id, "loser": loser_id},
                    )

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def _add_gap(
        self,
        gap_type: GapType,
        location: str,
        description: str,
        evidence_anchor: str,
        resolution_path: str,
        severity: Severity,
        detection_signal: str,
        metadata: Optional[Dict[str, Any]] = None,
        characterization: Optional[GapCharacterization] = None,
    ) -> None:
        self._gap_counter += 1
        gap_id = f"GAP-{self._gap_counter:06d}"

        # Characterize gap by exploration history (A/B/C/D)
        if characterization is None:
            characterization = self._characterize_gap(
                detection_signal, metadata or {}, location
            )

        self.gaps.append(
            EpistemicGap(
                gap_id=gap_id,
                gap_type=gap_type,
                characterization=characterization,
                location=location,
                description=description,
                evidence_anchor=evidence_anchor,
                resolution_path=resolution_path,
                severity=severity,
                detection_signal=detection_signal,
                repository=self.repository,
                metadata=metadata or {},
            )
        )

    def _characterize_gap(
        self,
        detection_signal: str,
        metadata: Dict[str, Any],
        location: str,
    ) -> GapCharacterization:
        """
        Characterize gap by exploration history (A/B/C/D).

        A: Never explored — no decisions on this topic
        B: Explored and abandoned — outcome: abandoned
        C: Explored partially — outcome: pending or superseded
        D: Unknown exploration — can't determine (documentary gap)
        """
        outcome = metadata.get("outcome", "")

        if outcome == "abandoned":
            return GapCharacterization.EXPLORED_ABANDONED
        elif outcome == "pending":
            return GapCharacterization.EXPLORED_PARTIAL
        elif outcome == "superseded":
            return GapCharacterization.EXPLORED_PARTIAL
        elif outcome == "failure":
            return GapCharacterization.EXPLORED_ABANDONED
        else:
            # No outcome info → can't determine exploration history
            return GapCharacterization.UNKNOWN_EXPLORATION

    # ------------------------------------------------------------------
    # Paradigm Residue Detection
    # ------------------------------------------------------------------

    def _detect_paradigm_residues(
        self,
        nodes: List[Dict],
        edges: List[Dict],
        node_map: Dict[str, Dict],
    ) -> None:
        """
        Detecta paradigm residue: qué cambió y qué permaneció
        entre decisiones sucesivas (superseded_by edges).

        Science progresses by changing few things and conserving many.
        Paradigm residue defines unexplored pathways.
        """
        for edge in edges:
            if edge.get("type") not in ("superseded_by", "abandoned_for"):
                continue

            from_id = edge.get("from", "")
            to_id = edge.get("to", "")
            from_node = node_map.get(from_id, {})
            to_node = node_map.get(to_id, {})

            if not from_node or not to_node:
                continue

            # Extraer "conceptos" de cada decision (tokens significativos del título)
            from_concepts = self._extract_concepts(from_node)
            to_concepts = self._extract_concepts(to_node)

            # What changed: concepts in from but not in to
            what_changed = list(from_concepts - to_concepts)
            # Qué permaneció: conceptos en ambos
            what_remained = list(from_concepts & to_concepts)

            if what_changed or what_remained:
                self._residue_counter += 1
                self.residues.append(
                    ParadigmResidue(
                        residue_id=f"RES-{self._residue_counter:06d}",
                        from_decision=from_id,
                        to_decision=to_id,
                        what_changed=what_changed[:10],
                        what_remained=what_remained[:10],
                        repository=self.repository,
                    )
                )

    def _extract_concepts(self, node: Dict) -> set:
        """Extrae conceptos significativos del título de una decision."""
        title = node.get("title", node.get("decision", ""))
        if not title:
            return set()
        # Stopwords básicas
        stopwords = {
            "the", "a", "an", "is", "are", "was", "were", "be", "been",
            "have", "has", "had", "do", "does", "did", "will", "would",
            "could", "should", "may", "might", "must", "can", "to", "of",
            "in", "for", "on", "with", "as", "by", "at", "from", "up",
            "about", "into", "through", "during", "before", "after",
            "above", "below", "between", "this", "that", "these", "those",
            "fix", "feat", "chore", "docs", "test", "ci", "add", "remove",
            "update", "use", "allow", "support", "prevent", "ensure",
        }
        tokens = set()
        for word in title.lower().split():
            # Limpiar puntuación
            clean = word.strip(".,;:!?()[]{}\"'")
            if len(clean) > 2 and clean not in stopwords:
                tokens.add(clean)
        return tokens

    # ------------------------------------------------------------------
    # Convergence Detection
    # ------------------------------------------------------------------

    def _detect_convergences(
        self,
        nodes: List[Dict],
        edges: List[Dict],
        node_map: Dict[str, Dict],
    ) -> None:
        """
        Detecta convergences: trayectorias independientes que terminan
        en la misma conclusión o chocan contra la misma barrera.

        Caso 1: Trayectorias independientes → misma conclusión (convergence exitosa)
        Caso 2: Trayectorias independientes → misma barrera (convergence de barrera)

        Requiere H7 (Branch Detection) para implementación completa.
        Esta es una detección preliminar basada en clusters de título.
        """
        # Group by topic similarity
        title_clusters = self._cluster_by_title_similarity(nodes, threshold=0.5)

        for cluster_key, cluster_nodes in title_clusters.items():
            if len(cluster_nodes) < 2:
                continue

            # Verificar si los autores son distintos (trayectorias independientes)
            actors = set(n.get("actor", "") for n in cluster_nodes)
            if len(actors) < 2:
                continue  # Mismo autor → no es convergence independiente

            # Verificar si los outcomes convergen
            outcomes = [n.get("outcome", "") for n in cluster_nodes]
            success_count = sum(1 for o in outcomes if o == "success")
            abandoned_count = sum(1 for o in outcomes if o == "abandoned")
            failure_count = sum(1 for o in outcomes if o == "failure")

            # Case 1: Successful convergence — multiple authors, same topic, success
            if success_count >= 2:
                self.convergences.append({
                    "convergence_id": f"CONV-{len(self.convergences) + 1:06d}",
                    "type": "successful_convergence",
                    "theme": cluster_key[:80],
                    "independent_actors": list(actors)[:5],
                    "decisions": [n.get("decision_id", n.get("id", "")) for n in cluster_nodes[:5]],
                    "outcome": "success",
                    "description": (
                        f"{success_count} independent trajectories converged "
                        f"on successful resolution of '{cluster_key[:60]}'"
                    ),
                    "repository": self.repository,
                    "epistemic_status": EpistemicStatus.OBSERVED.value,
                    "restriction_epistemic_status": EpistemicStatus.UNDETERMINED.value,
                    "constraint_hypotheses": [],
                })

            # Case 2: Barrier convergence — multiple authors, same topic, abandoned/failure
            elif abandoned_count >= 2 or failure_count >= 2:
                self.convergences.append({
                    "convergence_id": f"CONV-{len(self.convergences) + 1:06d}",
                    "type": "barrier_convergence",
                    "theme": cluster_key[:80],
                    "independent_actors": list(actors)[:5],
                    "decisions": [n.get("decision_id", n.get("id", "")) for n in cluster_nodes[:5]],
                    "outcome": "abandoned_or_failure",
                    "description": (
                        f"{abandoned_count + failure_count} independent trajectories "
                        f"hit the same barrier on '{cluster_key[:60]}'"
                    ),
                    "repository": self.repository,
                    "epistemic_status": EpistemicStatus.OBSERVED.value,
                    "restriction_epistemic_status": EpistemicStatus.UNDETERMINED.value,
                    "constraint_hypotheses": [],
                })

    def _has_causal_signal(self, text: str) -> bool:
        text_lower = text.lower()
        return any(signal in text_lower for signal in self.CAUSAL_SIGNALS)

    def _cluster_by_title_similarity(
        self, nodes: List[Dict], threshold: float = 0.6
    ) -> Dict[str, List[Dict]]:
        """
        Agrupa nodos por similitud de título (para detectar patrones recurrentes).
        Usa token overlap simple (Jaccard).
        """
        clusters: Dict[str, List[Dict]] = {}
        for node in nodes:
            title = node.get("title", node.get("decision", ""))
            if not title:
                continue
            tokens = set(title.lower().split())
            if not tokens:
                continue

            # Buscar cluster existente con suficiente overlap
            best_key = None
            best_score = 0.0
            for key in clusters:
                key_tokens = set(key.lower().split())
                if not key_tokens:
                    continue
                score = len(tokens & key_tokens) / len(tokens | key_tokens)
                if score > best_score:
                    best_score = score
                    best_key = key

            if best_key and best_score >= threshold:
                clusters[best_key].append(node)
            else:
                clusters[title[:80]] = [node]

        return clusters


# ------------------------------------------------------------------
# Helpers de módulo
# ------------------------------------------------------------------


def outcome_is_failure_or_abandoned(node: Dict) -> bool:
    return node.get("outcome", "") in ("failure", "abandoned")


# ------------------------------------------------------------------
# Epistemic Status Evaluation
# ------------------------------------------------------------------


def determine_restriction_epistemic_status(
    hypotheses: List[ConstraintHypothesis],
) -> EpistemicStatus:
    """
    Determina el estado epistemológico de una constraint
    basándose en sus hypothesis competidoras.

    Reglas (Directiva IDE SPRINT 60C/H7):
    - Si no hay hypothesis → UNDETERMINED
    - Si hay una hypothesis no falsada → HYPOTHESIZED
    - Si todas están falsadas → FALSIFIED
    - Si múltiples explican igualmente bien → UNDETERMINED
    - Si una falsó a las demás → HYPOTHESIZED (la ganadora)

    El sistema debe poder responder "no sabemos" (UNDETERMINED)
    sin degradar la evaluación.
    """
    if not hypotheses:
        return EpistemicStatus.UNDETERMINED

    active = [h for h in hypotheses if h.epistemic_status != EpistemicStatus.FALSIFIED]

    if not active:
        return EpistemicStatus.FALSIFIED

    if len(active) == 1:
        return EpistemicStatus.HYPOTHESIZED

    # Multiple active hypotheses → undetermined
    return EpistemicStatus.UNDETERMINED


# ------------------------------------------------------------------
# CLI
# ------------------------------------------------------------------


def main():
    import argparse

    parser = argparse.ArgumentParser(
        description="Detect Epistemic Gaps from TrajectoryGraph data"
    )
    parser.add_argument(
        "--input",
        required=True,
        help="Path to trajectory_graph.json",
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
    args = parser.parse_args()

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
    md_content = _format_report_markdown(report)
    with open(output_md, "w", encoding="utf-8") as f:
        f.write(md_content)

    # Resumen a consola
    print("=" * 70)
    print("EPISTEMIC GAP DETECTOR — Triunvirato Epistemológico")
    print("=" * 70)
    print(f"Repository: {repository}")
    print(f"Nodes analyzed: {report['metrics']['total_nodes_analyzed']}")
    print(f"Total gaps: {report['metrics']['total_gaps']}")
    print()
    print("By type (Triunvirato):")
    for gt, label in [
        (GapType.EMPIRICAL.value, "Evidencia (What do we observe?)"),
        (GapType.MATHEMATICAL.value, "Matemática (Is it coherent?)"),
        (GapType.CAUSAL.value, "Causalidad (Why does it occur?)"),
    ]:
        count = report["metrics"]["by_type"].get(gt, 0)
        print(f"  {label}: {count}")
    print()
    print("By severity:")
    for sev in Severity:
        count = report["metrics"]["by_severity"].get(sev.value, 0)
        print(f"  {sev.value}: {count}")
    print()
    print(f"JSON report: {output_json}")
    print(f"Markdown report: {output_md}")
    print("=" * 70)

    return 0


def _format_report_markdown(report: Dict[str, Any]) -> str:
    lines = []
    lines.append("# EPISTEMIC GAP REPORT")
    lines.append(f"**Repository**: {report.get('repository', 'N/A')}")
    lines.append(f"**Generated**: {report.get('generated_at', 'N/A')}")
    lines.append(f"**Report ID**: {report.get('report_id', 'N/A')}")
    lines.append("")

    lines.append("## Triunvirato Epistemológico")
    lines.append("")
    lines.append("| Emperador | Pregunta | Gaps detectados |")
    lines.append("|-----------|----------|-----------------|")
    tri = report.get("triumvirato", {})
    lines.append(
        f"| Evidencia | {tri.get('evidence', {}).get('question', '')} | "
        f"{tri.get('evidence', {}).get('gaps_detected', 0)} |"
    )
    lines.append(
        f"| Matemática | {tri.get('mathematics', {}).get('question', '')} | "
        f"{tri.get('mathematics', {}).get('gaps_detected', 0)} |"
    )
    lines.append(
        f"| Causalidad | {tri.get('causality', {}).get('question', '')} | "
        f"{tri.get('causality', {}).get('gaps_detected', 0)} |"
    )
    lines.append("")

    metrics = report.get("metrics", {})
    lines.append("## Métricas")
    lines.append("")
    lines.append(f"- Total gaps: **{metrics.get('total_gaps', 0)}**")
    lines.append(f"- Nodes analizados: {metrics.get('total_nodes_analyzed', 0)}")
    lines.append(f"- Gap density: {metrics.get('gap_density', 0)}")
    lines.append("")

    lines.append("## Gaps Detectados")
    lines.append("")

    for gap in report.get("gaps", []):
        lines.append(f"### {gap['gap_id']} — {gap['gap_type'].upper()}")
        lines.append(f"**Severity**: {gap['severity']}")
        lines.append(f"**Location**: `{gap['location']}`")
        lines.append(f"**Signal**: `{gap['detection_signal']}`")
        lines.append(f"**Description**: {gap['description']}")
        lines.append(f"**Evidence anchor**: {gap['evidence_anchor']}")
        lines.append(f"**Resolution path**: {gap['resolution_path']}")
        if gap.get("metadata"):
            lines.append(f"**Metadata**: `{json.dumps(gap['metadata'], ensure_ascii=False)}`")
        lines.append("")

    # Epistemic Discipline (v1.6)
    discipline = report.get("epistemic_discipline", {})
    if discipline:
        lines.append("")
        lines.append("## Epistemic Discipline (v1.6)")
        lines.append("")
        lines.append(f"> {discipline.get('principle', '')}")
        lines.append("")
        lines.append("**Rules**:")
        for rule in discipline.get("rules", []):
            lines.append(f"- {rule}")
        lines.append("")
        lines.append(f"**Wishful Mnemonic Prohibition**: {discipline.get('wishful_mnemonic_prohibition', '')}")
        lines.append("")
        epistemic_metrics = metrics.get("by_epistemic_status", {})
        if epistemic_metrics:
            lines.append("**By Epistemic Status**:")
            lines.append("")
            lines.append("| Status | Count |")
            lines.append("|--------|-------|")
            for status, count in epistemic_metrics.items():
                lines.append(f"| {status} | {count} |")
            lines.append("")

    # Convergences with epistemic status
    convergences = report.get("convergences", [])
    if convergences:
        lines.append("## Convergences")
        lines.append("")
        for conv in convergences:
            conv_id = conv.get("convergence_id", "")
            conv_type = conv.get("type", "")
            theme = conv.get("theme", "")
            epistemic = conv.get("epistemic_status", "")
            restriction_status = conv.get("restriction_epistemic_status", "")
            num_hypotheses = len(conv.get("constraint_hypotheses", []))
            lines.append(f"### {conv_id} — {conv_type}")
            lines.append(f"**Theme**: {theme}")
            lines.append(f"**Epistemic Status**: {epistemic}")
            lines.append(f"**Restriction Status**: {restriction_status}")
            lines.append(f"**Competing Hypotheses**: {num_hypotheses}")
            lines.append("")

    lines.append("---")
    lines.append("*Este reporte es un análisis derivado read-only. No añade schemas, grafos, ni capas arquitectónicas.*")
    lines.append("*Ver: docs/EPISTEMIC_GAP_CONCEPT.md*")

    return "\n".join(lines)


if __name__ == "__main__":
    import sys
    sys.exit(main())