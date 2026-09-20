"""
scripts/run_twin_gate_harness_suite.py - End-to-End Verification Suite for Twin-Gate Epistemic Harness (ADR-DISCOVERY-025)
Tests:
1. Hakken Evidence Gate (PHELInE path perturbation: sufficiency, necessity, temporal drift).
2. Dream-RSI Failure Triage (Repairable code bug vs genuine epistemic refutation).
3. ScienceIDE Invariant Sandbox (Compilation + execution of physical conservation laws: mass, energy, entropy).
4. Jev Continuous In-Turn Verifier (Sub-millisecond loop goal checking, stall detection).
5. FastAPI REST API endpoints.
"""

import sys
import os
from pathlib import Path

# Ensure repo root is on sys.path
REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

from python.discovery.twin_gate_harness import (
    ExecutionFailureCategory,
    InvariantCheckStatus,
    HakkenEvidenceGate,
    DreamRSIStrategyGate,
    ScienceIDEInvariantRunner,
    JevContinuousVerifier,
)
from python.discovery.fast_system_one_classifier import (
    FastSystemOneClassifier,
    ClassificationDomain,
)
from fastapi.testclient import TestClient
from api.server import app


def test_hakken_evidence_gate():
    print("\n--- 1. Testing Hakken Evidence Gate (PHELInE Path Perturbation) ---")
    
    # Construct a 3-hop scientific evidence chain:
    # APOE-e4 -> Microglial Glycolytic Impairment -> Tau Hyperphosphorylation
    path_hops = [
        {"source": "APOE-e4", "target": "Microglial Glycolysis", "relation": "downregulates", "weight": 0.88},
        {"source": "Microglial Glycolysis", "target": "Phagocytic Clearance", "relation": "impairs", "weight": 0.82},
        {"source": "Phagocytic Clearance", "target": "Tau Propagation", "relation": "permits", "weight": 0.90}
    ]
    temporal_snapshots = [
        {"epoch": "2018", "co_occurrence_count": 45},
        {"epoch": "2022", "co_occurrence_count": 92},
        {"epoch": "2026", "co_occurrence_count": 140}
    ]

    res = HakkenEvidenceGate.audit_evidence_path(
        hypothesis_id="HYP-APOE4-MICROGLIA-TAU",
        path_hops=path_hops,
        temporal_snapshots=temporal_snapshots
    )

    print(f"Hypothesis: {res.hypothesis_id}")
    print(f"Baseline Confidence: {res.baseline_confidence:.4f}")
    print(f"Sufficiency Score: {res.sufficiency_score:.4f}")
    print(f"Necessity Score: {res.necessity_score:.4f}")
    print(f"Temporal Drift: {res.temporal_stability_drift:.4f}")
    print(f"Is Epistemically Robust: {res.is_epistemically_robust}")
    print(f"SOM Hash: {res.som_evidence_hash}")

    assert res.baseline_confidence > 0.35, "Baseline confidence must reflect multi-hop product."
    assert res.sufficiency_score > 0.40, "Sufficiency score must be robust."
    assert res.necessity_score > 0.50, "Necessity score must reflect critical link dependency."
    assert res.is_epistemically_robust is True, "Evidence chain must pass epistemic robustness gate."
    assert res.som_evidence_hash.startswith("sha256:"), "Must generate SOM cryptographic hash."
    print("[OK] Hakken Evidence Gate tests PASSED.")


def test_dream_rsi_failure_triage():
    print("\n--- 2. Testing Dream-RSI Failure Triage (Code Error vs Epistemic Refutation) ---")

    # Case A: Repairable code bug (tensor shape mismatch)
    shape_error_trace = """
    File "simulation/solver.py", line 142, in step
        stress_tensor = torch.matmul(vorticity, velocity_gradient)
    RuntimeError: shape '[64, 128]' cannot be multiplied by '[256, 128]'
    """
    triage_a = DreamRSIStrategyGate.classify_failure_nature(shape_error_trace)
    print(f"Case A Category: {triage_a.category.value} | Repairable: {triage_a.is_repairable}")
    assert triage_a.category == ExecutionFailureCategory.REPAIRABLE_CODE_ERROR
    assert triage_a.is_repairable is True
    assert "Do NOT prune MCTS branch" in triage_a.remediation_strategy

    # Case B: Numerical instability
    linalg_trace = """
    File "simulation/fem.py", line 88, in solve_poisson
        return scipy.linalg.inv(stiffness_matrix)
    numpy.linalg.LinAlgError: Singular matrix in decomposition
    """
    triage_b = DreamRSIStrategyGate.classify_failure_nature(linalg_trace)
    print(f"Case B Category: {triage_b.category.value} | Repairable: {triage_b.is_repairable}")
    assert triage_b.category == ExecutionFailureCategory.NUMERICAL_INSTABILITY
    assert triage_b.is_repairable is True

    # Case C: Genuine physical conservation violation (scientific falsification)
    conservation_trace = """
    Traceback (most recent call last):
    AssertionError: Conservation law violated: Leray-Hopf bound breach: dE/dt = +1.42e-2 > bound = -3.10e-3
    """
    triage_c = DreamRSIStrategyGate.classify_failure_nature(conservation_trace)
    print(f"Case C Category: {triage_c.category.value} | Repairable: {triage_c.is_repairable}")
    assert triage_c.category == ExecutionFailureCategory.GENUINE_EPISTEMIC_FALSIFICATION
    assert triage_c.is_repairable is False
    assert "Defeated Hypotheses Graveyard" in triage_c.remediation_strategy

    # Case D: Search policy adaptation
    policy = DreamRSIStrategyGate.evaluate_search_policy(active_branch_count=1, stalled_step_count=4, average_branch_depth=5.2)
    assert policy["is_search_stalled"] is True
    assert policy["recommend_widening"] is True
    assert policy["recommended_breadth_multiplier"] >= 2.0
    print("[OK] Dream-RSI Failure Triage tests PASSED.")


def test_science_ide_invariant_runner():
    print("\n--- 3. Testing ScienceIDE Invariant Runner (Simulation & Conservation Laws) ---")

    # Case 1: Sound patch obeying Navier-Stokes Leray-Hopf & Mass Continuity
    sound_patch = """
    def compute_flux(u, v, nu, enstrophy):
        div_u = 1e-6
        dE_dt = -nu * enstrophy - 1e-5
        return div_u, dE_dt
    """
    state_vars = {"velocity_divergence": 1e-6, "kinematic_viscosity": 1e-3, "enstrophy": 25.0}
    rate_vars = {"dE_dt": -0.030, "entropy_production_rate": 0.005}  # bound is -1e-3*25 = -0.025; -0.030 <= -0.025 -> satisfied!

    res_sound = ScienceIDEInvariantRunner.evaluate_patch(
        case_id="CASE-ATHENA-001",
        target_codebase="Athena++",
        code_patch=sound_patch,
        state_variables=state_vars,
        differential_rates=rate_vars
    )
    print(f"Sound Patch Status: {res_sound.status.value} | Reward: {res_sound.reward_earned}")
    assert res_sound.status == InvariantCheckStatus.PASSED_CONSERVED
    assert res_sound.reward_earned == 1.0
    assert res_sound.physical_invariants_satisfied is True

    # Case 2: Patch compiles but violates conservation (Positive divergence & Energy generation)
    unphysical_state = {"velocity_divergence": 0.05, "kinematic_viscosity": 1e-3, "enstrophy": 20.0}
    unphysical_rates = {"dE_dt": 0.010, "entropy_production_rate": -0.020}  # dE_dt > 0 in closed system!
    res_unphysical = ScienceIDEInvariantRunner.evaluate_patch(
        case_id="CASE-PLUTO-002",
        target_codebase="PLUTO",
        code_patch="def step(): pass",
        state_variables=unphysical_state,
        differential_rates=unphysical_rates
    )
    print(f"Unphysical Patch Status: {res_unphysical.status.value} | Reward: {res_unphysical.reward_earned}")
    assert res_unphysical.status == InvariantCheckStatus.FAILED_PHYSICAL_INVARIANT
    assert res_unphysical.reward_earned == 0.0
    assert res_unphysical.physical_invariants_satisfied is False

    # Case 3: Patch with syntax error
    syntax_error_patch = "def broken_code(: SyntaxError"
    res_syntax = ScienceIDEInvariantRunner.evaluate_patch(
        case_id="CASE-MITGCM-003",
        target_codebase="MITgcm",
        code_patch=syntax_error_patch,
        state_variables=state_vars,
        differential_rates=rate_vars
    )
    assert res_syntax.status == InvariantCheckStatus.FAILED_COMPILATION
    assert res_syntax.compiled_successfully is False
    print("[OK] ScienceIDE Invariant Runner tests PASSED.")


def test_jev_continuous_verifier():
    print("\n--- 4. Testing Jev Continuous In-Turn Verifier (Sub-millisecond /goal Check) ---")

    # Turn 1: Normal progress
    turn1 = JevContinuousVerifier.verify_turn_goal(
        goal_description="Calculate connectome diffusion matrix and prune state space",
        action_history=["load_dataset", "compute_adjacency"],
        current_state_payload={"status": "IN_PROGRESS", "progress": 0.45}
    )
    print(f"Turn 1 Action: {turn1.recommended_action} | Latency: {turn1.latency_ms:.3f} ms")
    assert turn1.recommended_action == "PROCEED_NEXT_STEP"
    assert turn1.latency_ms < 5.0, "Jev System 1 check must execute in under 5ms."

    # Turn 2: Goal satisfied
    turn2 = JevContinuousVerifier.verify_turn_goal(
        goal_description="Calculate connectome diffusion matrix and prune state space",
        action_history=["load_dataset", "compute_adjacency", "prune_omega"],
        current_state_payload={"status": "VERIFIED", "progress": 1.0, "done": True}
    )
    print(f"Turn 2 Action: {turn2.recommended_action} | Satisfied: {turn2.goal_satisfied}")
    assert turn2.goal_satisfied is True
    assert turn2.recommended_action == "TERMINATE_GOAL_MET"

    # Turn 3: Loop stalling detection
    turn3 = JevContinuousVerifier.verify_turn_goal(
        goal_description="Resolve patient cohort metadata",
        action_history=["check_missing_cols", "check_missing_cols", "check_missing_cols"],
        current_state_payload={"status": "IN_PROGRESS", "progress": 0.2}
    )
    print(f"Turn 3 Action: {turn3.recommended_action} | Stalled: {turn3.is_loop_stalled}")
    assert turn3.is_loop_stalled is True
    assert turn3.recommended_action == "ESCALATE_SYSTEM_TWO"

    # FastSystemOneClassifier integration check
    sys1_res = FastSystemOneClassifier.classify_failure_nature("RuntimeError: shape mismatch in tensor contraction")
    assert sys1_res.domain == ClassificationDomain.FAILURE_TRIAGE
    assert sys1_res.selected_category == ExecutionFailureCategory.REPAIRABLE_CODE_ERROR.value
    assert sys1_res.latency_ms < 5.0

    print("[OK] Jev Continuous Verifier tests PASSED.")


def test_rest_api_endpoints():
    print("\n--- 5. Testing REST API Endpoints via FastAPI TestClient ---")
    client = TestClient(app)

    # 1. In-turn goal verification
    r1 = client.post("/api/discovery/harness/verify-in-turn-goal", json={
        "goal_description": "Validate thermodynamic consistency",
        "action_history": ["extract_enthalpy", "compute_entropy"],
        "current_state_payload": {"status": "SUCCESS", "progress": 0.98, "done": True}
    })
    assert r1.status_code == 200
    d1 = r1.json()
    assert d1["goal_satisfied"] is True
    assert d1["recommended_action"] == "TERMINATE_GOAL_MET"

    # 2. Hakken evidence audit
    r2 = client.post("/api/discovery/harness/hakken-evidence-audit", json={
        "hypothesis_id": "HYP-REST-TEST-001",
        "path_hops": [
            {"source": "Biomarker_A", "target": "Mechanism_B", "relation": "activates", "weight": 0.85},
            {"source": "Mechanism_B", "target": "Endpoint_C", "relation": "suppresses", "weight": 0.90}
        ]
    })
    assert r2.status_code == 200
    d2 = r2.json()
    assert d2["is_epistemically_robust"] is True
    assert d2["sufficiency_score"] > 0.3

    # 3. Dream-RSI failure triage
    r3 = client.post("/api/discovery/harness/dream-classify-failure", json={
        "error_traceback": "CUDA out of memory. Tried to allocate 4.00 GiB"
    })
    assert r3.status_code == 200
    d3 = r3.json()
    assert d3["category"] == "REPAIRABLE_CODE_ERROR"
    assert d3["is_repairable"] is True

    # 4. ScienceIDE invariant check
    r4 = client.post("/api/discovery/science-ide/execute-invariant-check", json={
        "case_id": "CASE-REST-PLUTO-01",
        "target_codebase": "PLUTO",
        "code_patch": "def step(): pass",
        "state_variables": {"velocity_divergence": 1e-5, "kinematic_viscosity": 1e-3, "enstrophy": 10.0},
        "differential_rates": {"dE_dt": -0.015, "entropy_production_rate": 0.01}
    })
    assert r4.status_code == 200
    d4 = r4.json()
    assert d4["status"] == "PASSED_CONSERVED"
    assert d4["reward_earned"] == 1.0

    print("[OK] All REST API Endpoints PASSED.")


def main():
    print("================================================================================")
    print("Running Twin-Gate Epistemic Harness & Verification Suite (ADR-DISCOVERY-025)")
    print("================================================================================")
    test_hakken_evidence_gate()
    test_dream_rsi_failure_triage()
    test_science_ide_invariant_runner()
    test_jev_continuous_verifier()
    test_rest_api_endpoints()
    print("\n================================================================================")
    print("ALL 5 TWIN-GATE VERIFICATION GATES PASSED EMPIRICALLY (100% OPERATIONAL)")
    print("================================================================================")


if __name__ == "__main__":
    main()
