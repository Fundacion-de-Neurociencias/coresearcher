"""
python/discovery/backward_execution_synthesizer.py - ToolGrad-Inspired Backward Execution-First Synthesizer
Implements the Execution-First paradigm for scientific discovery:
1. Validates and executes ground-truth analytical tool trajectories directly against physical datasets (e.g., DataAILab primitives).
2. Inverts executable trajectories into canonical, guaranteed-executable ResearchQuestionContracts (100% pass rate).
3. Reverse-chains causal and statistical pathologies to generate adversarial falsification suites (Simpson paradox, collider bias, leakage).
"""

import hashlib
import json
import os
import uuid
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional

import numpy as np
import pandas as pd


@dataclass
class AnalyticalToolPrimitive:
    tool_id: str
    tool_name: str
    required_inputs: List[str]
    produced_outputs: List[str]
    executable_fn: Callable[[Dict[str, Any]], Dict[str, Any]]
    computational_cost_tokens: int = 100


@dataclass
class ToolExecutionStep:
    step_id: str
    tool_id: str
    input_bindings: Dict[str, Any]
    output_state: Dict[str, Any] = field(default_factory=dict)
    execution_success: bool = False
    execution_error: Optional[str] = None


@dataclass
class ExecutableAnalyticalTrajectory:
    trajectory_id: str
    target_dataset_path: str
    steps: List[ToolExecutionStep] = field(default_factory=list)
    final_execution_state: Dict[str, Any] = field(default_factory=dict)
    is_fully_executable: bool = False
    som_execution_hash: str = ""

    def compute_som_hash(self) -> str:
        serialized = json.dumps(
            {
                "tid": self.trajectory_id,
                "dataset": self.target_dataset_path,
                "steps": [{"id": s.step_id, "tool": s.tool_id, "success": s.execution_success} for s in self.steps],
                "state_keys": sorted(list(self.final_execution_state.keys())),
            },
            sort_keys=True,
        )
        return f"sha256:{hashlib.sha256(serialized.encode('utf-8')).hexdigest()[:24]}"


class BackwardContractSynthesizer:
    """
    ToolGrad-inspired synthesizer:
    Executes physical data extraction first, verifies complete empirical tractability,
    and then inverts the successful execution into a canonical ResearchQuestionContract.
    """

    def __init__(self, physical_dataset_path: Optional[Path] = None):
        self.default_dataset = physical_dataset_path or Path(
            os.environ.get("CORESEARCHER_COHORT_CSV", "data/cohorts/metaboad_atn_processed.csv")
        )
        self.primitives: Dict[str, AnalyticalToolPrimitive] = {}
        self._register_default_primitives()

    def _register_default_primitives(self) -> None:
        # Primitive 1: Ingest and validate column availability
        def _ingest_data(inputs: Dict[str, Any]) -> Dict[str, Any]:
            path = inputs["dataset_path"]
            df = pd.read_csv(path)
            cols = list(df.columns)
            return {"dataframe": df, "available_columns": cols, "row_count": len(df)}

        self.primitives["TOOL-DATA-INGEST"] = AnalyticalToolPrimitive(
            tool_id="TOOL-DATA-INGEST",
            tool_name="Physical Cohort Ingestion & Schema Inspection",
            required_inputs=["dataset_path"],
            produced_outputs=["dataframe", "available_columns", "row_count"],
            executable_fn=_ingest_data,
        )

        # Primitive 2: Filter cohort and extract pair
        def _extract_pair(inputs: Dict[str, Any]) -> Dict[str, Any]:
            df: pd.DataFrame = inputs["dataframe"]
            exp_col = inputs["exposure_col"]
            out_col = inputs["outcome_col"]
            filter_query = inputs.get("filter_query")

            sub_df = df.copy()
            if filter_query:
                sub_df = sub_df.query(filter_query)

            valid_df = sub_df[[exp_col, out_col]].dropna()
            if len(valid_df) < 5:
                raise ValueError(f"Insufficient valid pairs for {exp_col} -> {out_col} (n={len(valid_df)})")

            x = valid_df[exp_col].values
            y = valid_df[out_col].values
            return {"n_valid_pairs": len(valid_df), "x_values": x, "y_values": y, "filtered_df": valid_df}

        self.primitives["TOOL-EXTRACT-BIOMARKER-PAIR"] = AnalyticalToolPrimitive(
            tool_id="TOOL-EXTRACT-BIOMARKER-PAIR",
            tool_name="Cohort Filtering and Biomarker Pair Extraction",
            required_inputs=["dataframe", "exposure_col", "outcome_col"],
            produced_outputs=["n_valid_pairs", "x_values", "y_values", "filtered_df"],
            executable_fn=_extract_pair,
        )

        # Primitive 3: OLS & Falsification Threshold Computation
        def _fit_ols(inputs: Dict[str, Any]) -> Dict[str, Any]:
            x = inputs["x_values"]
            y = inputs["y_values"]
            slope, intercept = np.polyfit(x, y, 1)
            y_pred = slope * x + intercept
            residuals = y - y_pred
            ss_tot = np.sum((y - np.mean(y)) ** 2)
            ss_res = np.sum(residuals**2)
            r2 = 1.0 - (ss_res / max(1e-9, ss_tot))

            # Falsification boundary: critical beta threshold
            falsification_slope_threshold = 0.0 if slope < 0 else 0.05
            return {
                "empirical_slope": float(slope),
                "empirical_intercept": float(intercept),
                "empirical_r2": float(r2),
                "suggested_falsification_threshold": (
                    f"beta < {falsification_slope_threshold:.3f}"
                    if slope < 0
                    else f"beta > {falsification_slope_threshold:.3f}"
                ),
            }

        self.primitives["TOOL-FIT-OLS-REGRESSION"] = AnalyticalToolPrimitive(
            tool_id="TOOL-FIT-OLS-REGRESSION",
            tool_name="Empirical OLS & Falsification Threshold Computation",
            required_inputs=["x_values", "y_values"],
            produced_outputs=[
                "empirical_slope",
                "empirical_intercept",
                "empirical_r2",
                "suggested_falsification_threshold",
            ],
            executable_fn=_fit_ols,
        )

    def execute_ground_truth_trajectory(
        self,
        exposure_col: str,
        outcome_col: str,
        dataset_path: Optional[Path] = None,
        filter_query: Optional[str] = None,
    ) -> ExecutableAnalyticalTrajectory:
        """
        Step 1: Execute tool chain forward against real physical dataset.
        Validates schema, extracts data, and calculates empirical feasibility.
        """
        target_path = dataset_path or self.default_dataset
        traj = ExecutableAnalyticalTrajectory(
            trajectory_id=f"TRAJ-{uuid.uuid4().hex[:8].upper()}", target_dataset_path=str(target_path)
        )

        current_state: Dict[str, Any] = {}

        # Step A: Ingest
        step_a = ToolExecutionStep(
            step_id="STEP-01", tool_id="TOOL-DATA-INGEST", input_bindings={"dataset_path": str(target_path)}
        )
        try:
            res_a = self.primitives["TOOL-DATA-INGEST"].executable_fn(step_a.input_bindings)
            step_a.output_state = res_a
            step_a.execution_success = True
            current_state.update(res_a)
        except Exception as e:
            step_a.execution_success = False
            step_a.execution_error = str(e)
            traj.steps.append(step_a)
            return traj

        traj.steps.append(step_a)

        # Step B: Extract Pair
        step_b = ToolExecutionStep(
            step_id="STEP-02",
            tool_id="TOOL-EXTRACT-BIOMARKER-PAIR",
            input_bindings={
                "dataframe": current_state["dataframe"],
                "exposure_col": exposure_col,
                "outcome_col": outcome_col,
                "filter_query": filter_query,
            },
        )
        try:
            res_b = self.primitives["TOOL-EXTRACT-BIOMARKER-PAIR"].executable_fn(step_b.input_bindings)
            step_b.output_state = res_b
            step_b.execution_success = True
            current_state.update(res_b)
        except Exception as e:
            step_b.execution_success = False
            step_b.execution_error = str(e)
            traj.steps.append(step_b)
            return traj

        traj.steps.append(step_b)

        # Step C: Fit OLS
        step_c = ToolExecutionStep(
            step_id="STEP-03",
            tool_id="TOOL-FIT-OLS-REGRESSION",
            input_bindings={"x_values": current_state["x_values"], "y_values": current_state["y_values"]},
        )
        try:
            res_c = self.primitives["TOOL-FIT-OLS-REGRESSION"].executable_fn(step_c.input_bindings)
            step_c.output_state = res_c
            step_c.execution_success = True
            current_state.update(res_c)
        except Exception as e:
            step_c.execution_success = False
            step_c.execution_error = str(e)
            traj.steps.append(step_c)
            return traj

        traj.steps.append(step_c)
        traj.is_fully_executable = True
        traj.final_execution_state = current_state
        traj.som_execution_hash = traj.compute_som_hash()
        return traj

    def invert_trajectory_to_contract(
        self,
        trajectory: ExecutableAnalyticalTrajectory,
        question_id: Optional[str] = None,
        hypothesis_id: Optional[str] = None,
        marr_level: str = "ALGORITHMIC",
        target_population_desc: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Step 2: Invert the ground-truth executable trajectory into a canonical ResearchQuestionContract.
        This guarantees 100% executability by design (no missing variables, no invalid power).
        """
        if not trajectory.is_fully_executable:
            raise RuntimeError(f"Cannot invert failed trajectory {trajectory.trajectory_id}")

        state = trajectory.final_execution_state
        exp_col = trajectory.steps[1].input_bindings["exposure_col"]
        out_col = trajectory.steps[1].input_bindings["outcome_col"]
        n_pairs = state["n_valid_pairs"]
        threshold = state["suggested_falsification_threshold"]
        slope = state["empirical_slope"]
        r2 = state["empirical_r2"]

        qid = question_id or f"RQ-2026-{uuid.uuid4().hex[:4].upper()}"
        hid = hypothesis_id or f"HYP-DISCOVERY-{uuid.uuid4().hex[:6].upper()}"
        pop_desc = (
            target_population_desc
            or f"Cohort from {Path(trajectory.target_dataset_path).name} with complete ({exp_col}, {out_col}) observations (N={n_pairs})"
        )

        contract = {
            "question_id": qid,
            "hypothesis_id": hid,
            "marr_explanation_level": marr_level,
            "target_population": pop_desc,
            "exposure_variable": exp_col,
            "outcome_variable": out_col,
            "timeframe_months": 24,
            "discriminative_predictions": [
                {
                    "prediction_id": f"PRED-{qid}-01",
                    "statement": f"Linear effect of {exp_col} on {out_col} satisfies {threshold} (empirical slope={slope:.4f}, R2={r2*100:.1f}%)",
                    "falsification_threshold": threshold,
                }
            ],
            "scope_conditions": {
                "valid_domain": [f"Dataset URI: {trajectory.target_dataset_path}", f"Sample size N >= {n_pairs}"],
                "boundary_conditions": [
                    f"Valid observation range: {exp_col} in [{np.min(state['x_values']):.1f}, {np.max(state['x_values']):.1f}]",
                    f"Bounded outcome range: {out_col} in [{np.min(state['y_values']):.1f}, {np.max(state['y_values']):.1f}]",
                ],
            },
            "backward_synthesis_metadata": {
                "trajectory_id": trajectory.trajectory_id,
                "som_execution_hash": trajectory.som_execution_hash,
                "guaranteed_executable": True,
                "generation_mode": "TOOLGRAD_EXECUTION_FIRST_INVERSION",
            },
        }
        return contract


class ReverseAdversarialFalsifier:
    """
    Synthesizes adversarial datasets and deception contracts by running
    a reverse execution pipeline that injects known statistical/causal traps.
    """

    @staticmethod
    def generate_simpsons_paradox_trap() -> Dict[str, Any]:
        """
        Synthesizes a clean Simpson's Paradox:
        Subgroup 1: Beta = -1.5
        Subgroup 2: Beta = -1.5
        Aggregated: Beta = +1.2
        Inverts into a seemingly solid ResearchQuestionContract that naive models will falsely confirm.
        """
        rng = np.random.default_rng(42)
        n1 = 40
        x1 = rng.uniform(10, 30, n1)
        y1 = 60.0 - 1.5 * x1 + rng.normal(0, 1.5, n1)

        n2 = 40
        x2 = rng.uniform(40, 60, n2)
        y2 = 120.0 - 1.5 * x2 + rng.normal(0, 1.5, n2)

        x_agg = np.concatenate([x1, x2])
        y_agg = np.concatenate([y1, y2])
        subgroup = np.array([1] * n1 + [2] * n2)

        slope_agg, _ = np.polyfit(x_agg, y_agg, 1)

        # The deceptive contract claims a positive linear relationship
        contract = {
            "question_id": "RQ-2026-SIMPSON-TRAP",
            "hypothesis_id": "HYP-DECEPTIVE-POSITIVE-CORRELATION",
            "marr_explanation_level": "ALGORITHMIC",
            "target_population": "Aggregated clinical population ignoring unobserved metabolic subgroup split",
            "exposure_variable": "Biomarker_X_Aggregated",
            "outcome_variable": "Clinical_Endpoint_Y",
            "timeframe_months": 12,
            "discriminative_predictions": [
                {
                    "prediction_id": "PRED-SIMPSON-01",
                    "statement": f"Aggregate exposure linearly promotes endpoint with beta >= +0.8 (observed beta={slope_agg:.2f})",
                    "falsification_threshold": "beta < 0.5",
                }
            ],
            "scope_conditions": {
                "valid_domain": ["Aggregated multi-center cohort"],
                "boundary_conditions": ["Subgroup partition unobserved in primary model"],
            },
            "trap_metadata": {
                "archetype": "SIMPSONS_PARADOX_INVERSION",
                "ground_truth_subgroup_slope": -1.5,
                "apparent_aggregate_slope": float(slope_agg),
                "deception_mechanism": "Confounding by latent clinical stratum (Z) inverting true causal direction",
            },
        }
        return {
            "contract": contract,
            "synthetic_data": {"x": x_agg.tolist(), "y": y_agg.tolist(), "subgroup": subgroup.tolist()},
        }

    @staticmethod
    def generate_collider_bias_trap() -> Dict[str, Any]:
        """
        Synthesizes a Collider Stratification Trap:
        Exposure (X) and Outcome (Y) are completely independent in nature (Beta = 0.0),
        but conditioning on a Collider (C = X + Y + eps) creates a strong spurious correlation.
        """
        rng = np.random.default_rng(99)
        n = 100
        x = rng.normal(0, 1, n)
        y = rng.normal(0, 1, n)
        collider = x + y + rng.normal(0, 0.2, n)

        # Condition on hospitalized / high collider subset
        conditioned_idx = np.where(collider > 0.5)[0]
        x_cond = x[conditioned_idx]
        y_cond = y[conditioned_idx]
        slope_cond, _ = np.polyfit(x_cond, y_cond, 1)

        contract = {
            "question_id": "RQ-2026-COLLIDER-TRAP",
            "hypothesis_id": "HYP-SPURIOUS-COLLIDER-INDUCED-ASSOCIATION",
            "marr_explanation_level": "ALGORITHMIC",
            "target_population": "Hospitalized / Clinical cohort conditioned on hospitalization collider C > 0.5",
            "exposure_variable": "Biomarker_A",
            "outcome_variable": "Pathology_B",
            "timeframe_months": 12,
            "discriminative_predictions": [
                {
                    "prediction_id": "PRED-COLLIDER-01",
                    "statement": f"In conditioned cohort, Biomarker A negatively predicts Pathology B with beta <= -0.5 (observed beta={slope_cond:.2f})",
                    "falsification_threshold": "beta > -0.2",
                }
            ],
            "scope_conditions": {
                "valid_domain": ["Inpatient clinical registry"],
                "boundary_conditions": ["Collider conditioning active"],
            },
            "trap_metadata": {
                "archetype": "COLLIDER_STRATIFICATION_TRAP",
                "ground_truth_unconditioned_slope": 0.0,
                "apparent_conditioned_slope": float(slope_cond),
                "deception_mechanism": "Conditioning on collider C = A + B induces Berkson's bias and spurious association",
            },
        }
        return {
            "contract": contract,
            "synthetic_data": {
                "x_unconditioned": x.tolist(),
                "y_unconditioned": y.tolist(),
                "x_conditioned": x_cond.tolist(),
                "y_conditioned": y_cond.tolist(),
            },
        }
