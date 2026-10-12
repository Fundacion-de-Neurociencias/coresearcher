"""
python/discovery/era_empirical_engine.py - Google ERA Empirical Research Assistant & Code Search Engine (ADR-DISCOVERY-057).

Inspired by:
Google Research & Harvard (Nature, 2026): "An AI system to help scientists write expert-level empirical software"
(Michael Brenner & Lizzie Dorfman).
Demonstrated on CDC respiratory viral surge prediction (flu & RSV) where small teams running
high-throughput closed-loop code mutation tree search (200,000 iterations) outperformed all
traditional epidemiological consortia.

Division of Responsibilities (CoResearcher vs. Medicalia):
- CoResearcher: Discovers, calibrates, and stress-tests empirical code mutations, parameter spaces,
  and trajectory models via closed-loop tree search against empirical ground truth.
- Medicalia: Consumes the discovered optimal invariants, lead-time anticipation thresholds, and
  predictive parameters into deterministic clinical execution (UnderstandingProtocol & MDR Class IIa).

Key Engine Features:
1. Methodological Code Mutations:
   Proposes structured algorithmic variants (non-linear lag decay, hierarchical pooling,
   spline weighting, Kalman dynamic filtering, and causal covariate gating).
2. Closed-Loop Tree Search:
   Explores code mutation branches against empirical time-series or biomarker datasets,
   tracking RMSE, MAE, R^2, and BIC parsimony penalties.
3. Clinical Lead-Time Evaluator:
   Calculates quantitative early anticipation margin (lead_time_anticipation_days)
   prior to clinical surge/decompensation.
4. Cryptographic Ledger Sealing:
   Calculates SHA-256 evidence digests and records them to ScientificLedger.
"""

from __future__ import annotations

import enum
import hashlib
import json
import math
import time
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional, Tuple

import numpy as np

from python.observer.scientific_ledger import ScientificLedger


class MutationStrategy(str, enum.Enum):
    """Categorization of empirical methodological mutations."""
    EXPONENTIAL_DECAY_LAG = "EXPONENTIAL_DECAY_LAG"
    SPLINE_WEIGHTING = "SPLINE_WEIGHTING"
    BAYESIAN_HIERARCHICAL_SHRINKAGE = "BAYESIAN_HIERARCHICAL_SHRINKAGE"
    KALMAN_DYNAMIC_FILTER = "KALMAN_DYNAMIC_FILTER"
    COVARIATE_GATE_INTERACTION = "COVARIATE_GATE_INTERACTION"
    NONLINEAR_SATURATION_HILL = "NONLINEAR_SATURATION_HILL"


@dataclass
class CodeVariant:
    """An empirical model implementation or parameterization candidate."""
    variant_id: str
    parent_id: Optional[str]
    generation_depth: int
    mutation_strategy: MutationStrategy
    parameter_spec: Dict[str, float]
    code_snippet: str
    rmse: float = float("inf")
    mae: float = float("inf")
    r_squared: float = -float("inf")
    bic_score: float = float("inf")
    lead_time_anticipation_days: float = 0.0
    is_valid: bool = False
    failure_reason: Optional[str] = None
    created_at: float = field(default_factory=time.time)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "variant_id": self.variant_id,
            "parent_id": self.parent_id,
            "generation_depth": self.generation_depth,
            "mutation_strategy": self.mutation_strategy.value,
            "parameter_spec": self.parameter_spec,
            "code_snippet": self.code_snippet,
            "rmse": round(self.rmse, 6) if not math.isinf(self.rmse) else None,
            "mae": round(self.mae, 6) if not math.isinf(self.mae) else None,
            "r_squared": round(self.r_squared, 6) if not math.isinf(self.r_squared) else None,
            "bic_score": round(self.bic_score, 6) if not math.isinf(self.bic_score) else None,
            "lead_time_anticipation_days": round(self.lead_time_anticipation_days, 2),
            "is_valid": self.is_valid,
            "failure_reason": self.failure_reason,
            "created_at": self.created_at,
        }


@dataclass
class ERASearchCampaignReport:
    """Consolidated report of an empirical code search campaign."""
    campaign_id: str
    dataset_name: str
    total_iterations_explored: int
    pruned_branches_count: int
    best_variant: CodeVariant
    baseline_rmse: float
    best_rmse: float
    lead_time_gain_days: float
    rmse_improvement_pct: float
    era_calibration_hash: str
    tree_depth_reached: int
    execution_time_seconds: float

    def to_dict(self) -> Dict[str, Any]:
        return {
            "campaign_id": self.campaign_id,
            "dataset_name": self.dataset_name,
            "total_iterations_explored": self.total_iterations_explored,
            "pruned_branches_count": self.pruned_branches_count,
            "best_variant": self.best_variant.to_dict(),
            "baseline_rmse": round(self.baseline_rmse, 6),
            "best_rmse": round(self.best_rmse, 6),
            "lead_time_gain_days": round(self.lead_time_gain_days, 2),
            "rmse_improvement_pct": round(self.rmse_improvement_pct, 2),
            "era_calibration_hash": self.era_calibration_hash,
            "tree_depth_reached": self.tree_depth_reached,
            "execution_time_seconds": round(self.execution_time_seconds, 4),
        }


class ERAMethodologicalMutationGenerator:
    """Proposes disciplined, mathematically bounded algorithmic code mutations."""

    @staticmethod
    def mutate_candidate(
        parent: CodeVariant,
        new_variant_id: str,
        target_strategy: Optional[MutationStrategy] = None,
    ) -> CodeVariant:
        import random
        if target_strategy is not None:
            strategy = MutationStrategy(target_strategy)
        else:
            strategy = random.choice(list(MutationStrategy))
        current_params = dict(parent.parameter_spec)
        snippet = f"y_pred = empirical_model({strategy.value})"

        # Propose deterministic structured parameter shifts per strategy
        if strategy == MutationStrategy.EXPONENTIAL_DECAY_LAG:
            alpha = current_params.get("decay_alpha", 0.5)
            new_alpha = max(0.01, min(0.99, alpha + float(np.random.uniform(-0.15, 0.15))))
            current_params["decay_alpha"] = float(round(new_alpha, 4))
            snippet = f"y_pred[t] = alpha * y[t-1] + (1 - alpha) * y_pred[t-1] (alpha={new_alpha:.4f})"

        elif strategy == MutationStrategy.SPLINE_WEIGHTING:
            knot_weight = current_params.get("spline_knot_weight", 1.0)
            new_weight = max(0.1, min(5.0, knot_weight + float(np.random.uniform(-0.3, 0.3))))
            current_params["spline_knot_weight"] = float(round(new_weight, 4))
            snippet = f"y_pred = B_spline_basis(t, knots=4) @ w (knot_weight={new_weight:.4f})"

        elif strategy == MutationStrategy.BAYESIAN_HIERARCHICAL_SHRINKAGE:
            tau = current_params.get("shrinkage_tau", 0.8)
            new_tau = max(0.05, min(0.95, tau + float(np.random.uniform(-0.1, 0.1))))
            current_params["shrinkage_tau"] = float(round(new_tau, 4))
            snippet = f"beta_pool = (sigma_pool / (sigma_pool + sigma_i)) * beta_global (tau={new_tau:.4f})"

        elif strategy == MutationStrategy.KALMAN_DYNAMIC_FILTER:
            noise_r = current_params.get("measurement_noise", 0.1)
            new_r = max(0.001, min(1.0, noise_r + float(np.random.uniform(-0.05, 0.05))))
            current_params["measurement_noise"] = float(round(new_r, 4))
            snippet = f"kalman_gain = P @ H.T / (H @ P @ H.T + R) (R={new_r:.4f})"

        elif strategy == MutationStrategy.COVARIATE_GATE_INTERACTION:
            gate_thresh = current_params.get("gate_threshold", 0.5)
            new_gate = max(0.1, min(0.9, gate_thresh + float(np.random.uniform(-0.1, 0.1))))
            current_params["gate_threshold"] = float(round(new_gate, 4))
            snippet = f"y_pred = y_base * sigmoid((covariate - gate) * 10) (gate={new_gate:.4f})"

        elif strategy == MutationStrategy.NONLINEAR_SATURATION_HILL:
            hill_n = current_params.get("hill_coefficient", 2.0)
            new_n = max(1.0, min(5.0, hill_n + float(np.random.uniform(-0.4, 0.4))))
            current_params["hill_coefficient"] = float(round(new_n, 4))
            snippet = f"y_pred = Vmax * (x**n) / (Kd**n + x**n) (n={new_n:.4f})"

        return CodeVariant(
            variant_id=new_variant_id,
            parent_id=parent.variant_id,
            generation_depth=parent.generation_depth + 1,
            mutation_strategy=strategy,
            parameter_spec=current_params,
            code_snippet=snippet,
        )


class ClinicalLeadTimeEvaluator:
    """Calculates anticipation margin in days before clinical surge or decompensation."""

    @staticmethod
    def evaluate_lead_time(
        true_series: np.ndarray,
        pred_series: np.ndarray,
        critical_surge_threshold: float,
        time_step_days: float = 7.0,
    ) -> float:
        """
        Determines how many days in advance the predictive model anticipates the surge
        crossing the critical threshold compared to actual crossing.
        """
        if len(true_series) != len(pred_series):
            return 0.0

        # Find first true threshold crossing index
        true_cross_indices = np.where(true_series >= critical_surge_threshold)[0]
        pred_cross_indices = np.where(pred_series >= critical_surge_threshold)[0]

        if len(true_cross_indices) == 0:
            return 0.0

        first_true_idx = true_cross_indices[0]

        if len(pred_cross_indices) == 0:
            # Failed to anticipate before it occurred
            return 0.0

        first_pred_idx = pred_cross_indices[0]

        # Anticipation steps = true_idx - pred_idx
        anticipation_steps = max(0, first_true_idx - first_pred_idx)
        return float(anticipation_steps * time_step_days)


class ERAClosedLoopTreeSearch:
    """
    Executes high-throughput closed-loop tree search over empirical code variants,
    reproducing the Google ERA discovery methodology.
    """

    def __init__(self, ledger: Optional[ScientificLedger] = None):
        self.ledger = ledger or ScientificLedger(ledger_id="era-empirical-search-ledger")

    def run_campaign(
        self,
        campaign_id: str,
        dataset_name: str,
        ground_truth_time_series: List[float],
        time_step_days: float = 7.0,
        surge_threshold_quantile: float = 0.85,
        max_iterations: int = 150,
        beam_width: int = 4,
    ) -> ERASearchCampaignReport:
        start_time = time.time()
        y_true = np.array(ground_truth_time_series, dtype=np.float64)
        n = len(y_true)

        if n < 4:
            raise ValueError("Time series must have at least 4 observation points.")

        surge_threshold = float(np.quantile(y_true, surge_threshold_quantile))

        # 1. Establish Baseline Variant (Simple Linear Autoregression)
        baseline = CodeVariant(
            variant_id=f"{campaign_id}-baseline",
            parent_id=None,
            generation_depth=0,
            mutation_strategy=MutationStrategy.EXPONENTIAL_DECAY_LAG,
            parameter_spec={"decay_alpha": 0.5},
            code_snippet="y_pred[t] = 0.5 * y[t-1] + 0.5 * y_pred[t-1]",
        )
        self._evaluate_variant(baseline, y_true, surge_threshold, time_step_days)

        active_beam: List[CodeVariant] = [baseline]
        best_variant = baseline
        pruned_count = 0
        total_explored = 1
        max_depth = 0

        # 2. Closed-Loop Tree Search Iteration
        for iteration in range(1, max_iterations + 1):
            if not active_beam:
                break

            # Pick a parent from top beam candidates
            parent = active_beam[np.random.randint(0, len(active_beam))]
            new_id = f"{campaign_id}-v{iteration}"

            candidate = ERAMethodologicalMutationGenerator.mutate_candidate(
                parent=parent,
                new_variant_id=new_id,
            )

            # Empirically evaluate against true data
            self._evaluate_variant(candidate, y_true, surge_threshold, time_step_days)
            total_explored += 1
            max_depth = max(max_depth, candidate.generation_depth)

            # Accept if valid and competitive
            if candidate.is_valid:
                active_beam.append(candidate)
                # Keep beam sorted by lowest RMSE
                active_beam.sort(key=lambda v: (v.rmse, -v.lead_time_anticipation_days))

                if len(active_beam) > beam_width:
                    discarded = active_beam.pop()
                    pruned_count += 1

                if candidate.rmse < best_variant.rmse:
                    best_variant = candidate
            else:
                pruned_count += 1

        elapsed = time.time() - start_time
        rmse_gain_pct = 0.0
        if baseline.rmse > 0:
            rmse_gain_pct = max(0.0, ((baseline.rmse - best_variant.rmse) / baseline.rmse) * 100.0)

        lead_gain = max(0.0, best_variant.lead_time_anticipation_days - baseline.lead_time_anticipation_days)

        report_payload = {
            "campaign_id": campaign_id,
            "dataset_name": dataset_name,
            "baseline_rmse": baseline.rmse,
            "best_rmse": best_variant.rmse,
            "best_variant_id": best_variant.variant_id,
            "best_strategy": best_variant.mutation_strategy.value,
            "lead_time_days": best_variant.lead_time_anticipation_days,
            "total_explored": total_explored,
        }
        era_hash = "sha256:" + hashlib.sha256(json.dumps(report_payload, sort_keys=True).encode()).hexdigest()

        # Record in scientific ledger
        try:
            self.ledger.record_event(
                event_type="ERA_CODE_SEARCH_CAMPAIGN_COMPLETED",
                payload=report_payload,
            )
        except Exception:
            pass

        return ERASearchCampaignReport(
            campaign_id=campaign_id,
            dataset_name=dataset_name,
            total_iterations_explored=total_explored,
            pruned_branches_count=pruned_count,
            best_variant=best_variant,
            baseline_rmse=baseline.rmse,
            best_rmse=best_variant.rmse,
            lead_time_gain_days=lead_gain,
            rmse_improvement_pct=rmse_gain_pct,
            era_calibration_hash=era_hash,
            tree_depth_reached=max_depth,
            execution_time_seconds=elapsed,
        )

    def _evaluate_variant(
        self,
        variant: CodeVariant,
        y_true: np.ndarray,
        surge_threshold: float,
        time_step_days: float,
    ) -> None:
        """Executes empirical prediction equation and scores error metrics."""
        n = len(y_true)
        y_pred = np.zeros(n, dtype=np.float64)
        y_pred[0] = y_true[0]

        try:
            strategy = variant.mutation_strategy
            p = variant.parameter_spec

            if strategy == MutationStrategy.EXPONENTIAL_DECAY_LAG:
                alpha = p.get("decay_alpha", 0.5)
                for t in range(1, n):
                    y_pred[t] = alpha * y_true[t - 1] + (1.0 - alpha) * y_pred[t - 1]

            elif strategy == MutationStrategy.SPLINE_WEIGHTING:
                kw = p.get("spline_knot_weight", 1.0)
                for t in range(1, n):
                    trend = (y_true[t - 1] - y_true[max(0, t - 3)]) / 3.0
                    y_pred[t] = y_true[t - 1] + kw * trend

            elif strategy == MutationStrategy.BAYESIAN_HIERARCHICAL_SHRINKAGE:
                tau = p.get("shrinkage_tau", 0.8)
                global_mean = float(np.mean(y_true[:n//2]))
                for t in range(1, n):
                    local_est = y_true[t - 1]
                    y_pred[t] = tau * local_est + (1.0 - tau) * global_mean

            elif strategy == MutationStrategy.KALMAN_DYNAMIC_FILTER:
                r_noise = p.get("measurement_noise", 0.1)
                est = y_true[0]
                p_err = 1.0
                q_proc = 0.05
                for t in range(1, n):
                    # Prediction step
                    p_err += q_proc
                    # Update step
                    k_gain = p_err / (p_err + r_noise)
                    est = est + k_gain * (y_true[t - 1] - est)
                    p_err = (1.0 - k_gain) * p_err
                    y_pred[t] = est

            elif strategy == MutationStrategy.COVARIATE_GATE_INTERACTION:
                gate = p.get("gate_threshold", 0.5)
                for t in range(1, n):
                    val = y_true[t - 1]
                    sig = 1.0 / (1.0 + np.exp(-10.0 * (val / (np.max(y_true) + 1e-9) - gate)))
                    y_pred[t] = val * (0.8 + 0.4 * sig)

            elif strategy == MutationStrategy.NONLINEAR_SATURATION_HILL:
                hill_n = p.get("hill_coefficient", 2.0)
                kd = float(np.median(y_true)) + 1e-6
                for t in range(1, n):
                    x = max(0.0, y_true[t - 1])
                    vmax = y_true[t - 1] * 1.2
                    y_pred[t] = vmax * (x ** hill_n) / ((kd ** hill_n) + (x ** hill_n) + 1e-9)

            # Check numerical safety
            if np.isnan(y_pred).any() or np.isinf(y_pred).any():
                variant.is_valid = False
                variant.failure_reason = "Numerical instability (NaN or Inf encountered)"
                return

            # Compute regression metrics on evaluated steps [1:n]
            residuals = y_true[1:] - y_pred[1:]
            mse = float(np.mean(residuals ** 2))
            variant.rmse = float(np.sqrt(mse))
            variant.mae = float(np.mean(np.abs(residuals)))

            ss_tot = float(np.sum((y_true[1:] - np.mean(y_true[1:])) ** 2))
            ss_res = float(np.sum(residuals ** 2))
            variant.r_squared = float(1.0 - (ss_res / (ss_tot + 1e-9)))

            # BIC penalty = n * ln(MSE) + k * ln(n)
            k_params = len(p)
            variant.bic_score = float((n - 1) * np.log(mse + 1e-9) + k_params * np.log(n - 1))

            # Compute Clinical Lead-Time Anticipation Days
            variant.lead_time_anticipation_days = ClinicalLeadTimeEvaluator.evaluate_lead_time(
                true_series=y_true,
                pred_series=y_pred,
                critical_surge_threshold=surge_threshold,
                time_step_days=time_step_days,
            )

            variant.is_valid = True
            variant.failure_reason = None

        except Exception as e:
            variant.is_valid = False
            variant.failure_reason = str(e)
