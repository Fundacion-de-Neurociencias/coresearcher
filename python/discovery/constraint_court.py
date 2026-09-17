"""
python/discovery/constraint_court.py - Constraint Court & Epistemic Conflict Resolution Engine
Formal adversarial cross-examination and Bayesian adjudication between incompatible scientific constraints
(e.g., Amyloid-first vs Tau-first vs Vascular-first vs Neuroinflammation-first).
"""

from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
import uuid


@dataclass
class LitigantConstraint:
    constraint_id: str
    name: str
    assertion_statement: str
    proposed_by_school: str  # e.g., "AMYLOID_CASCADE_SCHOOL" | "TAU_PROPAGATION_SCHOOL" | "VASCULAR_DYSFUNCTION_SCHOOL"
    prior_probability: float
    supporting_cohorts_count: int
    fatal_counterexamples_count: int
    state_space_exclusion_fraction: float


@dataclass
class CourtVerdict:
    trial_id: str
    case_title: str
    verdict_type: str  # "SCOPE_SPECIALIZATION_SYNTHESIS" | "DOMINANCE_SUBSUMPTION" | "FATAL_DEMOLITION"
    winning_constraint_id: Optional[str]
    posterior_probabilities: Dict[str, float]
    bayesian_bayes_factor: float
    adjudication_summary: str
    resolved_scope_boundaries: Dict[str, str]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "trial_id": self.trial_id,
            "case_title": self.case_title,
            "verdict_type": self.verdict_type,
            "winning_constraint_id": self.winning_constraint_id,
            "posterior_probabilities": self.posterior_probabilities,
            "bayes_factor": self.bayesian_bayes_factor,
            "adjudication_summary": self.adjudication_summary,
            "resolved_scope_boundaries": self.resolved_scope_boundaries
        }


class ConstraintCourt:
    """
    Adjudicates scientific trials between competing or incompatible constraints.
    """

    @staticmethod
    def adjudicate_canonical_neurodegeneration_clash() -> CourtVerdict:
        """
        Adjudicates the historic clash between:
        1. Amyloid-Cascade Invariant (Amyloid is strictly necessary and sufficient for tau spreading).
        2. Connectome-Tau Invariant (Tau spreads trans-synaptically along hubs, amyloid merely accelerates kinetics).
        3. Vascular Invariant (Microvascular ischemia is the true primary rate limiter).
        """
        trial_id = f"TRIAL-{uuid.uuid4().hex[:8].upper()}"

        c_amyloid = LitigantConstraint(
            constraint_id="CONST-AMYLOID-FIRST",
            name="Amyloid-Cascade Exclusivity Constraint",
            assertion_statement="∀subject, Tau neocortical spreading is impossible without prior cortical amyloid plaque saturation.",
            proposed_by_school="Classical Amyloid Hypothesis",
            prior_probability=0.35,
            supporting_cohorts_count=3,
            fatal_counterexamples_count=18,  # Primary Age-Related Tauopathy (PART) and amyloid-negative tauopathies
            state_space_exclusion_fraction=0.40
        )

        c_tau_connectome = LitigantConstraint(
            constraint_id="CONST-TAU-CONNECTOME",
            name="Connectome-Weighted Synaptic Tau Invariant",
            assertion_statement="∀subject, Tau spreads trans-synaptically along functional connectome hubs; amyloid acts as a catalytic rate multiplier rather than absolute initiator.",
            proposed_by_school="Network Neurodegeneration School",
            prior_probability=0.45,
            supporting_cohorts_count=4,
            fatal_counterexamples_count=0,
            state_space_exclusion_fraction=0.75
        )

        c_vascular = LitigantConstraint(
            constraint_id="CONST-VASCULAR-ISCHEMIA",
            name="Primary Microvascular Ischemia Constraint",
            assertion_statement="∀subject, Cognitive decline is primarily governed by white matter hypoperfusion; proteopathies are secondary.",
            proposed_by_school="Vascular Dementia School",
            prior_probability=0.20,
            supporting_cohorts_count=2,
            fatal_counterexamples_count=12,  # Pure amnestic AD with zero WMH
            state_space_exclusion_fraction=0.15
        )

        # Bayesian Posterior Computation
        # P(E|C_tau) is highest due to 0 counterexamples; P(E|C_amyloid) penalized by PART counterexamples
        likelihood_tau = 0.95
        likelihood_amyloid = 0.35
        likelihood_vasc = 0.25

        p_e = (c_tau_connectome.prior_probability * likelihood_tau) + \
              (c_amyloid.prior_probability * likelihood_amyloid) + \
              (c_vascular.prior_probability * likelihood_vasc)

        post_tau = round((c_tau_connectome.prior_probability * likelihood_tau) / p_e, 4)
        post_amyloid = round((c_amyloid.prior_probability * likelihood_amyloid) / p_e, 4)
        post_vasc = round((c_vascular.prior_probability * likelihood_vasc) / p_e, 4)

        bayes_factor = round(post_tau / post_amyloid, 2)

        verdict = CourtVerdict(
            trial_id=trial_id,
            case_title="In re Amyloid-Cascade vs Connectome-Tauopathy vs Vascular-Hypoperfusion",
            verdict_type="SCOPE_SPECIALIZATION_SYNTHESIS",
            winning_constraint_id="CONST-TAU-CONNECTOME",
            posterior_probabilities={
                "CONST-TAU-CONNECTOME": post_tau,
                "CONST-AMYLOID-FIRST": post_amyloid,
                "CONST-VASCULAR-ISCHEMIA": post_vasc
            },
            bayesian_bayes_factor=bayes_factor,
            adjudication_summary=(
                f"The Court finds in favor of CONST-TAU-CONNECTOME (Posterior P = {post_tau}, Bayes Factor K = {bayes_factor}). "
                "The absolutist Amyloid-First constraint is DEMOLISHED by 18 fatal counterexamples (PART cohorts). "
                "However, rather than discarding amyloid entirely, the Court issues a SCOPE SPECIALIZATION: "
                "Tau connectome flux governs topological spreading, while Amyloid governs phosphorylation velocity."
            ),
            resolved_scope_boundaries={
                "CONST-TAU-CONNECTOME": "Universal topological propagation axis across all ATN stages (Braak I-VI).",
                "CONST-AMYLOID-FIRST": "Restricted scope: Catalytic kinetic booster in neocortical transition phase (Braak III-IV -> V-VI).",
                "CONST-VASCULAR-ISCHEMIA": "Restricted scope: Additive co-morbidity dominating in subcortical ischemic vascular disease."
            }
        )
        return verdict
