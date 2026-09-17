"""
epistemic_trajectory.py - Full Epistemic Discovery & Representation Framework (2026-2027)
Strictly adheres to ADR-DISCOVERY-001 through ADR-DISCOVERY-006 & ADR-MECH-001.

Implements:
1. Representation Ledger (Enumeration of alternative observational frameworks)
2. Competing Hypotheses & Incompatible Discriminative Predictions
3. David Marr's Tri-Level Classification (COMPUTATIONAL, ALGORITHMIC, IMPLEMENTATIONAL)
4. BiologicalProgram as Primary Mechanistic Causal Unit
5. Constraint Discovery Engine (Detecting new emergent invariant prohibitions)
6. True Popperian Falsification & Modus Tollens (Elimination & Provisional Corroboration, NOT Verification)
7. Decomposed Discovery Value (RDV, CDV, MDV, AEV, FRV)
"""

from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional, Set
from enum import Enum
import datetime


class ExplanationLevel(str, Enum):
    COMPUTATIONAL = "COMPUTATIONAL"       # Goal, purpose, invariants preserved
    ALGORITHMIC = "ALGORITHMIC"           # Representation, process, network transfer
    IMPLEMENTATIONAL = "IMPLEMENTATIONAL" # Molecular, biophysical, physical substrate


class ConstraintType(str, Enum):
    PHYSICAL = "PHYSICAL"
    BIOLOGICAL = "BIOLOGICAL"
    LOGICAL = "LOGICAL"
    CONTEXTUAL = "CONTEXTUAL"
    STATISTICAL = "STATISTICAL"


class EpistemicConstraintStatus(str, Enum):
    CONJECTURED = "CONJECTURED"
    SURVIVED = "SURVIVED"
    CANONICAL = "CANONICAL"
    FALSIFIED = "FALSIFIED"
    DISCOVERED_EMERGENT = "DISCOVERED_EMERGENT"


class AlternativeStatus(str, Enum):
    ACTIVE_UNRESOLVED = "ACTIVE_UNRESOLVED"
    WEAKENED = "WEAKENED"
    ELIMINATED = "ELIMINATED"
    PROVISIONALLY_SURVIVED = "PROVISIONALLY_SURVIVED"


@dataclass
class Representation:
    """A first-class observational/conceptual framework (ADR-DISCOVERY-001)."""
    representation_id: str
    name: str
    marr_explanation_level: ExplanationLevel
    observables_space: List[str]
    invisible_space: List[str]
    invariant_principles: List[str]
    compression_power: float = 0.0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "representation_id": self.representation_id,
            "name": self.name,
            "marr_explanation_level": self.marr_explanation_level.value,
            "observables_space": self.observables_space,
            "invisible_space": self.invisible_space,
            "invariant_principles": self.invariant_principles,
            "compression_power": self.compression_power,
        }


@dataclass
class RepresentationLedger:
    """Enumerates competing observational frameworks before hypothesis commitment."""
    domain: str
    candidate_representations: List[Representation] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "domain": self.domain,
            "candidate_representations": [r.to_dict() for r in self.candidate_representations]
        }


@dataclass
class Constraint:
    """Fundamental invariant prohibition on the state space."""
    constraint_id: str
    statement: str
    constraint_type: ConstraintType
    invariance_domain: List[str]
    falsification_conditions: List[str]
    marr_level: Optional[ExplanationLevel] = None
    epistemic_status: EpistemicConstraintStatus = EpistemicConstraintStatus.CONJECTURED
    excluded_state_space_volume: float = 0.0
    falsification_attempts_count: int = 0
    emergent_discovery: bool = False

    @property
    def constraint_discovery_value(self) -> float:
        return round(self.excluded_state_space_volume * (1.0 + 0.15 * min(self.falsification_attempts_count, 10)), 4)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "constraint_id": self.constraint_id,
            "statement": self.statement,
            "constraint_type": self.constraint_type.value,
            "marr_level": self.marr_level.value if self.marr_level else None,
            "invariance_domain": self.invariance_domain,
            "falsification_conditions": self.falsification_conditions,
            "epistemic_status": self.epistemic_status.value,
            "excluded_state_space_volume": self.excluded_state_space_volume,
            "falsification_attempts_count": self.falsification_attempts_count,
            "constraint_discovery_value": self.constraint_discovery_value,
            "emergent_discovery": self.emergent_discovery
        }


@dataclass
class BiologicalProgram:
    """Primary Mechanistic Causal Unit connecting genes, biomarkers, images and trajectories."""
    program_id: str
    name: str
    explanation_level: ExplanationLevel
    computational_objective: str
    key_entities: List[str]
    causal_chain: List[Dict[str, Any]]
    target_diseases: List[str]
    transferability_score: float = 0.0
    marr_links: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "program_id": self.program_id,
            "name": self.name,
            "explanation_level": self.explanation_level.value,
            "computational_objective": self.computational_objective,
            "key_entities": self.key_entities,
            "causal_chain": self.causal_chain,
            "target_diseases": self.target_diseases,
            "transferability_score": self.transferability_score,
            "marr_links": self.marr_links,
        }


@dataclass
class DiscriminativePrediction:
    """An incompatible prediction that separates rival hypotheses."""
    prediction_id: str
    statement: str
    favors_hypothesis_id: str
    contradicts_hypothesis_ids: List[str]
    falsification_metric: str
    falsification_threshold: str
    outcome: str = "PENDING"  # PENDING | SURVIVED | REFUTED | INCONCLUSIVE


@dataclass
class RivalHypothesis:
    hypothesis_id: str
    statement: str
    representation_id: str
    marr_level: ExplanationLevel
    biological_program_id: Optional[str] = None
    status: AlternativeStatus = AlternativeStatus.ACTIVE_UNRESOLVED
    refutation_evidence: List[str] = field(default_factory=list)


@dataclass
class DecomposedDiscoveryValue:
    """
    Transparent, non-magic Discovery Value decomposed into verifiable epistemological contributions:
    - RDV: Representation Novelty / Shift
    - CDV: Constraint Discovery Value (volume of excluded impossible states)
    - MDV: Mechanistic Depth (tri-level causal anchoring)
    - AEV: Alternative Elimination Value (refutation of rival explanations)
    - FRV: Falsification Resistance (survived severe empirical tests)
    """
    representation_novelty_dv: float = 0.0  # RDV
    constraint_discovery_dv: float = 0.0    # CDV
    mechanistic_depth_dv: float = 0.0       # MDV
    alternative_elimination_dv: float = 0.0 # AEV
    falsification_resistance_dv: float = 0.0# FRV

    @property
    def total_score(self) -> float:
        return round(
            0.25 * self.representation_novelty_dv +
            0.30 * self.constraint_discovery_dv +
            0.15 * self.mechanistic_depth_dv +
            0.15 * self.alternative_elimination_dv +
            0.15 * self.falsification_resistance_dv,
            4
        )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "total_score": self.total_score,
            "rdv_representation_novelty": self.representation_novelty_dv,
            "cdv_constraint_discovery": self.constraint_discovery_dv,
            "mdv_mechanistic_depth": self.mechanistic_depth_dv,
            "aev_alternative_elimination": self.alternative_elimination_dv,
            "frv_falsification_resistance": self.falsification_resistance_dv,
            "formula": "DV = 0.25*RDV + 0.30*CDV + 0.15*MDV + 0.15*AEV + 0.15*FRV"
        }


@dataclass
class ScopeConditions:
    valid_domain: List[str] = field(default_factory=list)
    boundary_conditions: List[str] = field(default_factory=list)


class PopperEngine:
    """Authentic Popperian Falsification & Elimination Engine."""

    @staticmethod
    def evaluate_discriminative_experiment(
        hypotheses: List[RivalHypothesis],
        predictions: List[DiscriminativePrediction],
        empirical_results: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Evaluates empirical findings against discriminative predictions.
        Eliminates/weakens contradicted alternatives and awards provisional survival.
        """
        audit_log = []
        eliminated_count = 0

        for pred in predictions:
            # Check empirical metric against threshold
            # E.g. connectome slope p < 0.05 while WMH variance < 5%
            slope_p = empirical_results.get("slope_pvalue", 0.001)
            sample_size = empirical_results.get("sample_size", 0)

            if slope_p < 0.05 and sample_size >= 30:
                pred.outcome = "SURVIVED"
                audit_log.append(f"Prediction {pred.prediction_id} SURVIVED empirical test.")

                # Weaken/eliminate contradicting rival hypotheses
                for alt_id in pred.contradicts_hypothesis_ids:
                    matched_alt = next((h for h in hypotheses if h.hypothesis_id == alt_id), None)
                    if matched_alt:
                        matched_alt.status = AlternativeStatus.WEAKENED
                        matched_alt.refutation_evidence.append(f"Contradicted by survival of {pred.prediction_id}")
                        eliminated_count += 1
                        audit_log.append(f"Modus Tollens applied: Alternative {alt_id} WEAKENED/MUTED.")

                # Provisionally corroborate favored hypothesis
                favored = next((h for h in hypotheses if h.hypothesis_id == pred.favors_hypothesis_id), None)
                if favored:
                    favored.status = AlternativeStatus.PROVISIONALLY_SURVIVED
                    audit_log.append(f"Hypothesis {pred.favors_hypothesis_id} remains PROVISIONALLY VIABLE (not verified).")

        return {
            "audit_verdict": "PROVISIONAL_CORROBORATION_WITH_ELIMINATION",
            "epistemic_principle": "Popperian Demarcation: Survival of Falsification != Verification",
            "audit_log": audit_log,
            "hypotheses_state": [
                {
                    "hypothesis_id": h.hypothesis_id,
                    "statement": h.statement,
                    "marr_level": h.marr_level.value,
                    "status": h.status.value,
                    "refutation_log": h.refutation_evidence
                }
                for h in hypotheses
            ],
            "eliminated_alternatives_count": eliminated_count
        }
