"""
python/discovery/reality_contact_score.py - Reality Contact Score (RCS) Engine
"Every hypothesis must earn reality."
Evaluates how much structured reality a scientific hypothesis or constraint has touched (Levels 0 to 4).
"""

from enum import IntEnum
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional


class RealityContactLevel(IntEnum):
    LEVEL_0_LITERATURE_ONLY = 0
    LEVEL_1_EXTERNAL_RETROSPECTIVE = 1
    LEVEL_2_PROSPECTIVE_HOLDOUT = 2
    LEVEL_3_PHYSICAL_EXPERIMENT_STEERED = 3
    LEVEL_4_LEDGERED_INVARIANT_CONSTRAINT = 4


@dataclass
class RealityContactEvidence:
    literature_citations_count: int = 0
    retrospective_cohorts_validated: List[str] = field(default_factory=list)  # e.g., ["ADNI", "NACC", "AIBL", "OASIS"]
    prospective_holdout_datasets: List[str] = field(default_factory=list)  # e.g., ["UK_BIOBANK_2026_PROSPECTIVE"]
    physical_experiment_runs: List[Dict[str, Any]] = field(default_factory=list)  # e.g., [{"run_id": "CHIP-884", "device": "SPARSE_IMAGING"}]
    promoted_invariant_constraint_id: Optional[str] = None  # e.g., "CONST-INVARIANT-151FD6"
    state_space_omega_pruned_fraction: float = 0.0  # e.g., 0.1667

    def to_dict(self) -> Dict[str, Any]:
        return {
            "literature_citations_count": self.literature_citations_count,
            "retrospective_cohorts_validated": self.retrospective_cohorts_validated,
            "prospective_holdout_datasets": self.prospective_holdout_datasets,
            "physical_experiment_runs": self.physical_experiment_runs,
            "promoted_invariant_constraint_id": self.promoted_invariant_constraint_id,
            "state_space_omega_pruned_fraction": self.state_space_omega_pruned_fraction
        }


@dataclass
class RealityContactScoreReport:
    hypothesis_id: str
    rcs_score: int  # 0 to 4
    level_name: str
    level_description: str
    is_promotable_as_invariant: bool  # True if rcs_score >= 3
    reality_trail: List[str]
    epistemic_justification: str

    def to_dict(self) -> Dict[str, Any]:
        return {
            "hypothesis_id": self.hypothesis_id,
            "reality_contact_score": self.rcs_score,
            "level_name": self.level_name,
            "level_description": self.level_description,
            "is_promotable_as_invariant": self.is_promotable_as_invariant,
            "reality_trail": self.reality_trail,
            "epistemic_justification": self.epistemic_justification
        }


class RealityContactEvaluator:
    """
    Evaluates the Reality Contact Score (RCS) for any scientific hypothesis or constraint.
    """

    LEVEL_DEFINITIONS = {
        RealityContactLevel.LEVEL_0_LITERATURE_ONLY: {
            "name": "Level 0: Pure Literature / In-Silico Reasoning",
            "description": "Bibliographic speculation or LLM text generation without external empirical validation."
        },
        RealityContactLevel.LEVEL_1_EXTERNAL_RETROSPECTIVE: {
            "name": "Level 1: External Retrospective Cohort Replication",
            "description": "Prediction confirmed across independent external retrospective cohorts (e.g. ADNI, NACC, OASIS, AIBL)."
        },
        RealityContactLevel.LEVEL_2_PROSPECTIVE_HOLDOUT: {
            "name": "Level 2: Prospective / Blinded Holdout Confirmation",
            "description": "Prediction confirmed on unseen prospective or blinded holdout biobank datasets prior to outcome unblinding."
        },
        RealityContactLevel.LEVEL_3_PHYSICAL_EXPERIMENT_STEERED: {
            "name": "Level 3: Physical Laboratory Experiment Steering",
            "description": "Prediction translated into physical laboratory protocols that steered/modified a real-world wet-lab assay, microfluidic chip, or reactor."
        },
        RealityContactLevel.LEVEL_4_LEDGERED_INVARIANT_CONSTRAINT: {
            "name": "Level 4: Ledgered Invariant Constraint Discovery",
            "description": "Prediction produced a brand-new, stress-tested invariant constraint formally promoted and incorporated into the immutable ledger, pruning state space Ω."
        }
    }

    @classmethod
    def evaluate_rcs(
        cls,
        hypothesis_id: str,
        evidence: RealityContactEvidence
    ) -> RealityContactScoreReport:
        trail = []
        score = RealityContactLevel.LEVEL_0_LITERATURE_ONLY

        # Level 0 Check
        if evidence.literature_citations_count > 0:
            trail.append(f"Literature grounding: {evidence.literature_citations_count} citations analyzed.")
        else:
            trail.append("Literature grounding: Baseline conceptual formulation.")

        # Level 1 Check: Retrospective Cohorts
        if len(evidence.retrospective_cohorts_validated) > 0:
            score = RealityContactLevel.LEVEL_1_EXTERNAL_RETROSPECTIVE
            trail.append(f"Retrospective replication: Validated across {len(evidence.retrospective_cohorts_validated)} external cohorts ({', '.join(evidence.retrospective_cohorts_validated)}).")

        # Level 2 Check: Prospective Holdout
        if len(evidence.prospective_holdout_datasets) > 0:
            score = RealityContactLevel.LEVEL_2_PROSPECTIVE_HOLDOUT
            trail.append(f"Prospective validation: Confirmed on {len(evidence.prospective_holdout_datasets)} blinded holdouts ({', '.join(evidence.prospective_holdout_datasets)}).")

        # Level 3 Check: Physical Laboratory Steering
        if len(evidence.physical_experiment_runs) > 0:
            score = RealityContactLevel.LEVEL_3_PHYSICAL_EXPERIMENT_STEERED
            devices = [r.get("device", "WET_LAB") for r in evidence.physical_experiment_runs]
            trail.append(f"Physical lab steering: Modified {len(evidence.physical_experiment_runs)} real-world experimental runs ({', '.join(devices)}).")

        # Level 4 Check: Promoted Invariant Constraint in Ledger
        if evidence.promoted_invariant_constraint_id is not None and evidence.state_space_omega_pruned_fraction > 0:
            score = RealityContactLevel.LEVEL_4_LEDGERED_INVARIANT_CONSTRAINT
            trail.append(f"Invariant constraint ledger promotion: Mined invariant {evidence.promoted_invariant_constraint_id}, pruning {evidence.state_space_omega_pruned_fraction*100:.1f}% of state space Ω.")

        info = cls.LEVEL_DEFINITIONS[score]
        promotable = score >= RealityContactLevel.LEVEL_3_PHYSICAL_EXPERIMENT_STEERED

        justification = (
            f"Hypothesis '{hypothesis_id}' has achieved Reality Contact Score RCS = {score.value} ({info['name']}). "
            f"{'It has earned sufficient physical/ledgered reality to be certified as an active invariant constraint.' if promotable else 'It remains a provisional/unsteered candidate and requires further physical or ledgered reality contact before permanent promotion.'}"
        )

        return RealityContactScoreReport(
            hypothesis_id=hypothesis_id,
            rcs_score=int(score.value),
            level_name=info["name"],
            level_description=info["description"],
            is_promotable_as_invariant=promotable,
            reality_trail=trail,
            epistemic_justification=justification
        )
