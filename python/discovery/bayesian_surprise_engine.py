"""
python/discovery/bayesian_surprise_engine.py - Bayesian Surprise & Information Gain Engine
Quantifies scientific surprise via Kullback-Leibler (KL) divergence between prior belief P(H)
and posterior belief P(H | D), computing Expected Information Gain (EIG).
"""

from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
import numpy as np
import math


@dataclass
class BayesianSurpriseEvaluation:
    hypothesis_id: str
    hypothesis_statement: str
    prior_probability: float           # P(H)
    likelihood: float                  # P(D | H)
    evidence_probability: float        # P(D)
    posterior_probability: float       # P(H | D)
    kl_divergence_bits: float          # KL( Posterior || Prior ) in bits
    bayesian_surprise_score: float     # log2( P(D | H) / P(D) )
    expected_information_gain_eig: float
    epistemic_tier: str                # "TRIVIAL_CONFIRMATION" | "MODERATE_GAIN" | "HIGH_VALUE_DISCOVERY" | "PARADIGM_SHIFT"
    rationale: str

    def to_dict(self) -> Dict[str, Any]:
        return {
            "hypothesis_id": self.hypothesis_id,
            "hypothesis_statement": self.hypothesis_statement,
            "prior_probability": self.prior_probability,
            "likelihood": self.likelihood,
            "evidence_probability": self.evidence_probability,
            "posterior_probability": self.posterior_probability,
            "kl_divergence_bits": self.kl_divergence_bits,
            "bayesian_surprise_score": self.bayesian_surprise_score,
            "expected_information_gain_eig": self.expected_information_gain_eig,
            "epistemic_tier": self.epistemic_tier,
            "rationale": self.rationale
        }


class BayesianSurpriseEngine:
    """
    Computes rigorous Bayesian belief updating and epistemic information gain for scientific experiments.
    """

    @classmethod
    def evaluate_experiment_surprise(
        cls,
        hypothesis_id: str,
        hypothesis_statement: str,
        prior_p: float,
        empirical_p_value: float,
        effect_size: float,
        sample_size: int,
        is_falsified: bool = False
    ) -> BayesianSurpriseEvaluation:
        """
        Computes Bayesian belief transition:
        - If prior is low (e.g., P(H) = 0.05) and severe test survives (p < 0.001), Surprise is MAXIMAL.
        - If prior is high (e.g., P(H) = 0.95) and test survives, Surprise is MINIMAL.
        """
        prior_p = float(np.clip(prior_p, 1e-4, 1.0 - 1e-4))

        if is_falsified:
            # Falsification scenario
            likelihood = 0.05
            p_not_h_given_d = 0.95
            p_d = (likelihood * prior_p) + (0.90 * (1.0 - prior_p))
            posterior_p = (likelihood * prior_p) / max(p_d, 1e-6)
        else:
            # Severe test corroboration
            # Likelihood under H is high given strong effect size
            power = min(0.99, max(0.50, 1.0 - empirical_p_value))
            likelihood = power
            # Likelihood under Null / Rivals
            p_d_given_not_h = max(0.01, empirical_p_value)
            p_d = (likelihood * prior_p) + (p_d_given_not_h * (1.0 - prior_p))
            posterior_p = (likelihood * prior_p) / max(p_d, 1e-6)

        posterior_p = float(np.clip(posterior_p, 1e-4, 1.0 - 1e-4))

        # KL divergence: D_KL( Posterior || Prior ) = P(H|D)*log2(P(H|D)/P(H)) + (1-P(H|D))*log2((1-P(H|D))/(1-P(H)))
        kl_bits = (
            posterior_p * math.log2(posterior_p / prior_p) +
            (1.0 - posterior_p) * math.log2((1.0 - posterior_p) / (1.0 - prior_p))
        )
        kl_bits = max(0.0, kl_bits)

        # Surprise score
        surprise = math.log2(likelihood / max(p_d, 1e-6))

        # Expected Information Gain (EIG)
        eig = round(kl_bits * (1.0 - prior_p), 4)

        if kl_bits > 2.5:
            tier = "PARADIGM_SHIFT"
            rationale = f"Exceptional information gain ({kl_bits:.2f} bits): Low-prior hypothesis ({prior_p:.1%}) strongly corroborated."
        elif kl_bits > 1.0:
            tier = "HIGH_VALUE_DISCOVERY"
            rationale = f"Significant information gain ({kl_bits:.2f} bits): Substantial belief revision from {prior_p:.1%} to {posterior_p:.1%}."
        elif kl_bits > 0.3:
            tier = "MODERATE_GAIN"
            rationale = f"Moderate information gain ({kl_bits:.2f} bits): Useful incremental evidence."
        else:
            tier = "TRIVIAL_CONFIRMATION"
            rationale = f"Low information gain ({kl_bits:.2f} bits): High prior expectation ({prior_p:.1%}) trivially confirmed."

        return BayesianSurpriseEvaluation(
            hypothesis_id=hypothesis_id,
            hypothesis_statement=hypothesis_statement,
            prior_probability=round(prior_p, 4),
            likelihood=round(likelihood, 4),
            evidence_probability=round(p_d, 4),
            posterior_probability=round(posterior_p, 4),
            kl_divergence_bits=round(kl_bits, 4),
            bayesian_surprise_score=round(surprise, 4),
            expected_information_gain_eig=eig,
            epistemic_tier=tier,
            rationale=rationale
        )
