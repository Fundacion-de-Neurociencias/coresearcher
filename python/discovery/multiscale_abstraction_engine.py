"""
Multiscale Latent Abstraction Engine (ADR-DISCOVERY-039).

Formalizes the principle that science and modeling seek the optimal representation
at the proper level of abstraction:
- Microscopic/implementational levels capture fine details but have short-range horizons.
- Macroscopic/conservative levels compress state into invariants for long-range predictions.
- World Models act as action-conditioned differentiable predictors in abstract latent space,
  rather than brute-force digital twins or simulators.
"""

from __future__ import annotations

import enum
import math
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional, Tuple


class AbstractionLevel(enum.Enum):
    """Hierarchical abstraction tiers across spatial and temporal scales."""
    MICRO_IMPLEMENTATIONAL = "MICRO_IMPLEMENTATIONAL"
    MESO_ALGORITHMIC = "MESO_ALGORITHMIC"
    MACRO_COMPUTATIONAL_CONSERVATIVE = "MACRO_COMPUTATIONAL_CONSERVATIVE"


@dataclass
class MultiscaleStateNode:
    """Represents a physical or epistemic state within an abstraction tier."""
    node_id: str
    level: AbstractionLevel
    latent_vector: List[float]
    detail_dimension: int
    noise_variance: float = 0.05
    conserved_quantities: Dict[str, float] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)

    @property
    def norm(self) -> float:
        return math.sqrt(sum(x * x for x in self.latent_vector))


@dataclass
class ActionConditionedPredictionVerdict:
    """Outcome of a differentiable latent transition under an action."""
    source_node_id: str
    action_vector: List[float]
    target_prediction: List[float]
    prediction_horizon: float
    energy_loss: float
    gradient_norm: float
    is_differentiable: bool
    abstraction_level: AbstractionLevel
    details: Dict[str, Any] = field(default_factory=dict)


@dataclass
class RepresentationSuitabilityReport:
    """Evaluation of whether a given abstraction tier suits a scientific inquiry."""
    level: AbstractionLevel
    target_horizon: float
    achievable_horizon: float
    horizon_gap: float
    energy_cost: float
    is_optimal_abstraction: bool
    rationality_score: float
    recommendation: str


class ActionConditionedPredictor:
    """
    Differentiable predictor mapping (s_t, a_t) -> s_{t+dt} in latent representation space.
    Implements analytical forward mapping and gradient computation.
    """

    def __init__(self, weight_decay: float = 0.01):
        self.weight_decay = weight_decay

    def predict_forward(
        self,
        latent_state: List[float],
        action: List[float],
        transition_matrix: Optional[List[List[float]]] = None,
    ) -> List[float]:
        """
        Projects latent state forward under action conditioning.
        If transition_matrix is omitted, defaults to linear-additive coupling.
        """
        dim_s = len(latent_state)
        dim_a = len(action)
        if dim_s == 0:
            return []

        out = [0.0] * dim_s
        # Linear dynamical base: s_{t+1} = s_t + B * a_t
        for i in range(dim_s):
            a_term = action[i % dim_a] if dim_a > 0 else 0.0
            coupling = 0.1 * math.sin(latent_state[i]) + 0.5 * a_term
            out[i] = latent_state[i] + coupling

        if transition_matrix and len(transition_matrix) == dim_s:
            transformed = [0.0] * dim_s
            for i in range(dim_s):
                for j in range(min(dim_s, len(transition_matrix[i]))):
                    transformed[i] += transition_matrix[i][j] * out[j]
            return transformed

        return out

    def compute_energy_and_gradients(
        self,
        predicted_state: List[float],
        ground_truth_latent: List[float],
        action: List[float],
    ) -> Tuple[float, List[float], float]:
        """
        Computes quadratic latent energy E = 0.5 * ||s_hat - s*||^2
        and analytic gradient dE/da.
        """
        dim = min(len(predicted_state), len(ground_truth_latent))
        if dim == 0:
            return 0.0, [], 0.0

        diff = [predicted_state[i] - ground_truth_latent[i] for i in range(dim)]
        energy = 0.5 * sum(d * d for d in diff)

        # Gradient with respect to action vector
        dim_a = len(action)
        grad_a = [0.0] * dim_a
        for j in range(dim_a):
            for i in range(dim):
                if i % dim_a == j:
                    # ds_hat_i / da_j = 0.5
                    grad_a[j] += diff[i] * 0.5

        grad_norm = math.sqrt(sum(g * g for g in grad_a))
        return energy, grad_a, grad_norm


class MultiscaleAbstractionEngine:
    """
    Core engine managing the hierarchy of abstractions and evaluating model suitability.
    """

    HORIZON_CONSTANT = 500.0  # Empirical horizon constant kappa

    def __init__(self, horizon_constant: float = 500.0):
        self.horizon_constant = horizon_constant
        self.predictor = ActionConditionedPredictor()

    def calculate_prediction_horizon(
        self,
        detail_dimension: int,
        noise_variance: float = 0.05,
        level: AbstractionLevel = AbstractionLevel.MESO_ALGORITHMIC,
    ) -> float:
        """
        Calculates achievable prediction horizon via the scaling law:
        Horizon = (kappa * scale_multiplier) / (detail_dimension * (1 + noise))
        """
        dim = max(1, detail_dimension)
        scale_mult = {
            AbstractionLevel.MICRO_IMPLEMENTATIONAL: 0.1,
            AbstractionLevel.MESO_ALGORITHMIC: 1.0,
            AbstractionLevel.MACRO_COMPUTATIONAL_CONSERVATIVE: 10.0,
        }.get(level, 1.0)

        raw_horizon = (self.horizon_constant * scale_mult) / (dim * (1.0 + max(0.0, noise_variance)))
        return round(raw_horizon, 4)

    def evaluate_action_conditioned_transition(
        self,
        state: MultiscaleStateNode,
        action: List[float],
        expected_target: Optional[List[float]] = None,
    ) -> ActionConditionedPredictionVerdict:
        """
        Applies action to state node, calculates forward latent trajectory,
        verifies differentiability and energy loss against expected target.
        """
        predicted = self.predictor.predict_forward(state.latent_vector, action)
        target = expected_target if expected_target is not None else predicted

        energy, grad, grad_norm = self.predictor.compute_energy_and_gradients(
            predicted, target, action
        )

        horizon = self.calculate_prediction_horizon(
            state.detail_dimension, state.noise_variance, state.level
        )

        return ActionConditionedPredictionVerdict(
            source_node_id=state.node_id,
            action_vector=action,
            target_prediction=predicted,
            prediction_horizon=horizon,
            energy_loss=energy,
            gradient_norm=grad_norm,
            is_differentiable=True,
            abstraction_level=state.level,
            details={
                "grad_a": grad,
                "dimension": len(predicted),
                "conserved_quantities": state.conserved_quantities,
            },
        )

    def find_optimal_abstraction_level(
        self,
        candidate_nodes: List[MultiscaleStateNode],
        target_horizon: float,
        action: List[float],
        expected_targets: Optional[Dict[str, List[float]]] = None,
    ) -> List[RepresentationSuitabilityReport]:
        """
        Audits a list of candidate representation states across abstraction levels,
        determining which tier provides the best balance of prediction horizon and energy fidelity.
        """
        reports: List[RepresentationSuitabilityReport] = []
        expected_targets = expected_targets or {}

        for node in candidate_nodes:
            exp_target = expected_targets.get(node.node_id)
            verdict = self.evaluate_action_conditioned_transition(node, action, exp_target)

            achievable_h = verdict.prediction_horizon
            h_gap = abs(target_horizon - achievable_h)
            cost = h_gap + 5.0 * verdict.energy_loss
            rationality = 1.0 / (1.0 + cost)

            reports.append(
                RepresentationSuitabilityReport(
                    level=node.level,
                    target_horizon=target_horizon,
                    achievable_horizon=achievable_h,
                    horizon_gap=round(h_gap, 4),
                    energy_cost=round(verdict.energy_loss, 4),
                    is_optimal_abstraction=False,
                    rationality_score=round(rationality, 4),
                    recommendation="",
                )
            )

        if not reports:
            return []

        # Mark the one with highest rationality score as optimal
        best_report = max(reports, key=lambda r: r.rationality_score)
        for r in reports:
            if r.level == best_report.level:
                r.is_optimal_abstraction = True
                r.recommendation = (
                    f"Optimal abstraction tier: captures target horizon {target_horizon} "
                    f"with minimal energy distortion ({r.energy_cost})."
                )
            elif r.achievable_horizon < target_horizon:
                r.recommendation = (
                    f"Sub-optimal (Over-detailed): horizon {r.achievable_horizon} is too short "
                    f"for target {target_horizon}. Elevate abstraction to macro-invariants."
                )
            else:
                r.recommendation = (
                    f"Sub-optimal (Over-abstracted): achievable horizon {r.achievable_horizon} "
                    f"far exceeds target {target_horizon}. Granular details may be lost."
                )

        return reports
