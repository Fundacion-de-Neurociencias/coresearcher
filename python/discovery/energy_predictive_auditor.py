"""
Non-Generative Energy-Based Epistemic Auditor & Model-Predictive Controller (ADR-EPISTEMIC-040).

Operationalizes Yann LeCun's 4 AMI Axioms for Scientific Discovery:
1. Abandon generative models -> Joint-Embedding Architecture (JEPA).
2. Abandon probabilistic models -> Energy-Based Models (EBM).
3. Abandon contrastive methods -> Non-contrastive VICReg (Variance/Invariance/Covariance).
4. Abandon blind RL -> Model-Predictive Control (MPC) with residual calibration.
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional, Tuple


@dataclass
class LatentPhysicalState:
    """Abstract latent representation of a physical system or theoretical state."""
    state_id: str
    embedding: List[float]
    conserved_quantities: Dict[str, float] = field(default_factory=dict)
    hard_violations: List[str] = field(default_factory=list)


@dataclass
class VICRegAuditResult:
    """Audit of latent representation using non-contrastive variance/covariance regularization."""
    invariance_loss: float
    variance_loss: float
    covariance_loss: float
    total_vicreg_loss: float
    is_representation_collapsed: bool


@dataclass
class MPCEpistemicPlan:
    """Action plan derived through Model-Predictive Control in the latent World Model."""
    horizon_steps: int
    optimal_action_sequence: List[List[float]]
    projected_energy_trajectory: List[float]
    best_candidate_energy: float
    residual_rl_calibration_needed: bool
    explanation: str


@dataclass
class EnergyAuditVerdict:
    """Final unnormalized Energy-Based Model judgment of physical validity."""
    theory_id: str
    unnormalized_energy: float
    is_physically_sound: bool
    vicreg_health: VICRegAuditResult
    mpc_plan: MPCEpistemicPlan
    failure_mode: Optional[str] = None


class VICRegRegularizer:
    """
    Non-contrastive regularizer preventing representation collapse without negative samples.
    Computes Variance, Invariance, and Covariance penalties.
    """

    def __init__(self, sim_coeff: float = 1.0, var_coeff: float = 1.0, cov_coeff: float = 0.04):
        self.sim_coeff = sim_coeff
        self.var_coeff = var_coeff
        self.cov_coeff = cov_coeff

    def audit_batch_representations(
        self,
        embeddings_x: List[List[float]],
        embeddings_y: List[List[float]],
        gamma_margin: float = 1.0,
        eps: float = 1e-4,
    ) -> VICRegAuditResult:
        n = len(embeddings_x)
        if n == 0 or len(embeddings_x[0]) == 0:
            return VICRegAuditResult(0.0, 0.0, 0.0, 0.0, is_representation_collapsed=True)

        d = len(embeddings_x[0])

        # 1. Invariance (Mean Squared Discrepancy)
        inv_loss = 0.0
        for i in range(n):
            inv_loss += sum((embeddings_x[i][j] - embeddings_y[i][j]) ** 2 for j in range(d))
        inv_loss /= max(1, n * d)

        # 2. Variance Regularization on X
        var_loss = 0.0
        for j in range(d):
            mean_j = sum(embeddings_x[i][j] for i in range(n)) / n
            var_j = sum((embeddings_x[i][j] - mean_j) ** 2 for i in range(n)) / n
            std_j = math.sqrt(var_j + eps)
            var_loss += max(0.0, gamma_margin - std_j)
        var_loss /= max(1, d)

        # 3. Covariance Regularization on X (decorrelate orthogonal dimensions)
        cov_loss = 0.0
        if n > 1 and d > 1:
            means = [sum(embeddings_x[i][j] for i in range(n)) / n for j in range(d)]
            centered = [[embeddings_x[i][j] - means[j] for j in range(d)] for i in range(n)]
            cov_matrix = [[0.0] * d for _ in range(d)]
            for j1 in range(d):
                for j2 in range(d):
                    cov_matrix[j1][j2] = (
                        sum(centered[i][j1] * centered[i][j2] for i in range(n)) / (n - 1)
                    )
            for j1 in range(d):
                for j2 in range(d):
                    if j1 != j2:
                        cov_loss += cov_matrix[j1][j2] ** 2
            cov_loss /= max(1, d)

        total_loss = (
            self.sim_coeff * inv_loss + self.var_coeff * var_loss + self.cov_coeff * cov_loss
        )
        # Collapse condition: all dimensions have variance strictly below epsilon or zero diversity
        dim_variances = [sum((embeddings_x[i][j] - (sum(embeddings_x[k][j] for k in range(n)) / n)) ** 2 for i in range(n)) / max(1, n) for j in range(d)]
        is_collapsed = n > 2 and all(v < 1e-6 for v in dim_variances)

        return VICRegAuditResult(
            invariance_loss=round(inv_loss, 4),
            variance_loss=round(var_loss, 4),
            covariance_loss=round(cov_loss, 4),
            total_vicreg_loss=round(total_loss, 4),
            is_representation_collapsed=is_collapsed,
        )


class ModelPredictiveController:
    """
    Model-Predictive Control (MPC) optimizer in latent representation space.
    Minimizes energy trajectory over a receding horizon.
    """

    def __init__(self, horizon: int = 5, num_candidates: int = 20):
        self.horizon = horizon
        self.num_candidates = num_candidates

    def plan_latent_trajectory(
        self,
        current_state: List[float],
        target_state: List[float],
        transition_fn: Callable[[List[float], List[float]], List[float]],
        hard_constraint_fn: Optional[Callable[[List[float]], bool]] = None,
    ) -> MPCEpistemicPlan:
        dim_s = len(current_state)
        dim_a = 2  # Action perturbation dimensionality

        best_actions: List[List[float]] = []
        best_energy = float("inf")
        best_trajectory: List[float] = []

        # Optimization via shooting / cross-entropy over latent actions
        import random

        rng = random.Random(42)  # Deterministic seed

        for _ in range(self.num_candidates):
            actions = [[rng.uniform(-0.5, 0.5) for _ in range(dim_a)] for _ in range(self.horizon)]
            state = list(current_state)
            trajectory_energies = []
            violated = False

            for t in range(self.horizon):
                state = transition_fn(state, actions[t])
                if hard_constraint_fn and not hard_constraint_fn(state):
                    violated = True
                    break

                # Energy = quadratic distance to target invariant
                e_t = sum((state[i] - target_state[i % len(target_state)]) ** 2 for i in range(dim_s))
                trajectory_energies.append(e_t)

            if violated:
                continue

            total_e = sum(trajectory_energies) / max(1, len(trajectory_energies))
            if total_e < best_energy:
                best_energy = total_e
                best_actions = actions
                best_trajectory = trajectory_energies

        needs_residual_rl = best_energy > 5.0 or len(best_trajectory) == 0

        return MPCEpistemicPlan(
            horizon_steps=self.horizon,
            optimal_action_sequence=best_actions,
            projected_energy_trajectory=[round(e, 4) for e in best_trajectory],
            best_candidate_energy=round(best_energy, 4) if best_energy != float("inf") else 1e9,
            residual_rl_calibration_needed=needs_residual_rl,
            explanation=(
                "Optimal MPC latent plan identified with energy convergence."
                if not needs_residual_rl
                else "Planning discrepancy exceeds tolerance: trigger residual RL calibration for world model."
            ),
        )


class NonGenerativeEpistemicAuditor:
    """
    Unified epistemic auditor implementing LeCun's non-generative, energy-based,
    regularized, and model-predictive paradigm.
    """

    ENERGY_FATAL_THRESHOLD = 1e6

    def __init__(self):
        self.vicreg = VICRegRegularizer()
        self.mpc = ModelPredictiveController()

    def audit_physical_theory(
        self,
        theory_id: str,
        theory_latent: LatentPhysicalState,
        empirical_reference_latent: LatentPhysicalState,
    ) -> EnergyAuditVerdict:
        """
        Audits a proposed physical theory using unnormalized energy and VICReg representations.
        """
        # Hard constraint violations trigger E = +inf
        if theory_latent.hard_violations:
            vicreg_dummy = VICRegAuditResult(1.0, 1.0, 1.0, 3.0, is_representation_collapsed=False)
            plan_dummy = MPCEpistemicPlan(
                horizon_steps=0,
                optimal_action_sequence=[],
                projected_energy_trajectory=[float("inf")],
                best_candidate_energy=float("inf"),
                residual_rl_calibration_needed=False,
                explanation="Fatal physical violation detected.",
            )
            return EnergyAuditVerdict(
                theory_id=theory_id,
                unnormalized_energy=float("inf"),
                is_physically_sound=False,
                vicreg_health=vicreg_dummy,
                mpc_plan=plan_dummy,
                failure_mode=f"Hard physical violation: {', '.join(theory_latent.hard_violations)}",
            )

        # 1. Audit representation health via VICReg
        vicreg_health = self.vicreg.audit_batch_representations(
            [theory_latent.embedding, [x * 0.99 for x in theory_latent.embedding]],
            [empirical_reference_latent.embedding, empirical_reference_latent.embedding],
        )

        # 2. Plan trajectory via MPC
        def simple_transition(s: List[float], a: List[float]) -> List[float]:
            dim = len(s)
            return [s[i] + 0.1 * a[i % len(a)] for i in range(dim)]

        def conservation_check(s: List[float]) -> bool:
            # Conserved norm bounds
            norm = math.sqrt(sum(x * x for x in s))
            return norm < 1000.0

        mpc_plan = self.mpc.plan_latent_trajectory(
            current_state=theory_latent.embedding,
            target_state=empirical_reference_latent.embedding,
            transition_fn=simple_transition,
            hard_constraint_fn=conservation_check,
        )

        # 3. Compute final unnormalized Energy
        dim = min(len(theory_latent.embedding), len(empirical_reference_latent.embedding))
        latent_discrepancy = (
            sum(
                (theory_latent.embedding[i] - empirical_reference_latent.embedding[i]) ** 2
                for i in range(dim)
            )
            / max(1, dim)
        )

        total_energy = latent_discrepancy + vicreg_health.total_vicreg_loss
        is_sound = total_energy < 10.0 and not vicreg_health.is_representation_collapsed

        return EnergyAuditVerdict(
            theory_id=theory_id,
            unnormalized_energy=round(total_energy, 4),
            is_physically_sound=is_sound,
            vicreg_health=vicreg_health,
            mpc_plan=mpc_plan,
            failure_mode=None if is_sound else "Excessive latent energy or representation collapse",
        )
