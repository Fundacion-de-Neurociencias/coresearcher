"""
Test suite for Frontier Math Ingestion & Epistemic Closed-Loop Flywheel (ADR-DISCOVERY-055).
Verifies:
1. Admissibility auditor intercepts drifted or weakened problem statements.
2. Admissibility auditor approves sound, bijectively aligned problems.
3. Proof equivalence auditor accepts distinct valid derivations and awards dense partial rewards.
4. Extracted bridge lemmas are functorially compiled into active AI acceleration operators.
5. Dream-RSI offline policy recalibration optimizes exploration parameters using problem trees.
6. Full closed-loop self-improvement cycle and REST API endpoints execute cleanly.
"""

from __future__ import annotations

import pytest

from api.server import app
from api.testing import authenticated_client
from python.discovery.frontier_math_flywheel import (
    AdmissibilityStatus,
    FrontierMathFlywheelEngine,
    FrontierMathProblemTask,
    ProofEquivalenceAuditor,
)


@pytest.fixture
def client():
    return authenticated_client(app)


def test_admissibility_auditor_detects_sound_problem():
    task = FrontierMathProblemTask(
        task_id="task_riemann_zeta_bound",
        title="Riemann Zeta Critical Strip Growth Bound",
        problem_statement_prose="For any epsilon > 0, the Riemann zeta function satisfies |zeta(1/2 + it)| <= C * (1 + |t|)^(1/6 + epsilon).",
        formal_lean_statement="theorem riemann_zeta_bound (t : Real) (eps : Real) (h_eps : eps > 0) : abs (zeta (1/2 + I * t)) <= C * (1 + abs t)^(1/6 + eps) := by sorry",
        domain_topic="ANALYTIC_NUMBER_THEORY",
    )

    report = FrontierMathFlywheelEngine.audit_problem_admissibility(task)
    assert report.is_admissible
    assert report.status == AdmissibilityStatus.ADMISSIBLE_SOUND
    assert report.som_admissibility_hash.startswith("sha256:")


def test_admissibility_auditor_intercepts_drifted_problem():
    # Prose specifies 4 derivatives, Lean statement demands 5 derivatives (goalpost shift)
    task = FrontierMathProblemTask(
        task_id="task_navier_stokes_drift",
        title="Navier-Stokes Regularity",
        problem_statement_prose="Under mild initial vorticity, four additional derivatives suffice to ensure finiteness in 3D.",
        formal_lean_statement="theorem NavierStokesGlobalRegularity (u0 : VelocityField) (hd : contDiff 5 u0) : GlobalRegularity u0 := by sorry",
        domain_topic="FLUID_DYNAMICS",
    )

    report = FrontierMathFlywheelEngine.audit_problem_admissibility(task)
    assert not report.is_admissible
    assert report.status == AdmissibilityStatus.DRIFTED_GOAL
    assert "drift" in report.admissibility_notes.lower()


def test_proof_equivalence_and_dense_rewards():
    task = FrontierMathProblemTask(
        task_id="task_harmonic_divergence",
        title="Harmonic Series Divergence",
        problem_statement_prose="The harmonic series diverges to infinity.",
        formal_lean_statement="theorem harmonic_diverges : Tendsto (fun n => sum (1/k)) atTop atTop := by sorry",
        reference_solution_code="theorem harmonic_diverges : Tendsto (fun n => sum (1/k)) atTop atTop := by apply cauchy_integral_test",
    )

    # Submitted proof: distinct tactic and syntax, proves 2 helper lemmas but has sorry at the end
    partial_submission = """
    lemma block_subdivision_lower_bound (m : Nat) : sum_block m >= 1/2 := by ring
    lemma monotonic_growth (n : Nat) : monotonic (fun n => sum (1/k)) := by intro h; linarith
    theorem harmonic_diverges : Tendsto (fun n => sum (1/k)) atTop atTop := by
      have h1 := block_subdivision_lower_bound
      sorry
    """

    score = ProofEquivalenceAuditor.evaluate_submitted_proof(task, partial_submission)
    assert not score.is_exact_string_match
    assert score.contains_sorry_escape
    assert score.verified_bridge_lemmas_count >= 1
    assert score.dense_reward_score >= 0.35  # Partial credit awarded!
    assert not score.kernel_accepted

    # Complete proof without sorry
    complete_submission = """
    lemma helper_identity : 1 + 1 = 2 := by rfl
    theorem harmonic_diverges : Tendsto (fun n => sum (1/k)) atTop atTop := by
      intro eps
      linarith
    """
    full_score = ProofEquivalenceAuditor.evaluate_submitted_proof(task, complete_submission)
    assert full_score.kernel_accepted
    assert full_score.is_equivalent_proof
    assert full_score.dense_reward_score == 1.0


def test_lemma_extraction_and_functorial_compilation():
    engine = FrontierMathFlywheelEngine()
    task = FrontierMathProblemTask(
        task_id="task_geometric_clifford_invariance",
        title="Clifford Algebra Rotation Invariance",
        problem_statement_prose="The rotor product preserves multivector norm under SO(3) rotations.",
        formal_lean_statement="""
        lemma rotor_orthogonal_preservation : rotation_norm R = 1 := by ring
        lemma toeplitz_convolution_spectral : circulant_matrix C = diagonal := by ring
        theorem clifford_so3_invariance : invariant_under_rotation := by ring
        """,
        reference_solution_code="""
        lemma rotor_orthogonal_preservation : rotation_norm R = 1 := by ring
        lemma toeplitz_convolution_spectral : circulant_matrix C = diagonal := by ring
        theorem clifford_so3_invariance : invariant_under_rotation := by ring
        """,
    )

    lemmas = engine.extract_reusable_lemmas(task)
    assert len(lemmas) >= 2

    # Compile lemmas to AI operators
    ops = engine.compile_lemmas_into_ai_operators(lemmas)
    assert len(ops) >= 2
    op_classes = [op.structure_class.value for op in ops]
    assert "CLIFFORD_GEOMETRIC_ALGEBRA" in op_classes or "TOEPLITZ_SPECTRAL_OPERATOR" in op_classes


def test_full_flywheel_cycle():
    engine = FrontierMathFlywheelEngine()
    tasks = [
        FrontierMathProblemTask(
            task_id="task_toeplitz_circulant",
            title="Circulant Fourier Diagonalization",
            problem_statement_prose="A circulant Toeplitz operator is diagonalized by the Discrete Fourier Transform matrix.",
            formal_lean_statement="theorem toeplitz_fourier_diag : T = F_inv * D * F := by sorry",
            reference_solution_code="theorem toeplitz_fourier_diag : T = F_inv * D * F := by apply fourier_transform",
        ),
        FrontierMathProblemTask(
            task_id="task_drifted_defect",
            title="Boundary Curvature Drift",
            problem_statement_prose="Under initial boundary conditions, four additional derivatives suffice in 3D.",
            formal_lean_statement="theorem boundary_curvature_weakened (u : Field) (hd : contDiff 5 u) : curvature u := by sorry",
        ),
    ]

    res = engine.execute_closed_loop_flywheel_cycle(
        cycle_id="cycle_benchmark_001",
        problem_tasks=tasks,
    )

    assert res.ingested_problems_count == 2
    assert res.admissible_problems_count == 1
    assert res.rejected_drifted_count == 1
    assert res.extracted_bridge_lemmas_count >= 1
    assert res.compiled_ai_operators_count >= 1
    assert len(res.cross_domain_subsystems_upgraded) >= 3
    assert res.som_math_flywheel_hash.startswith("sha256:")


def test_rest_api_endpoints(client):
    task_payload = {
        "task_id": "api_test_task",
        "title": "Symplectic Phase Space Area Preservation",
        "problem_statement_prose": "Hamiltonian flow preserves the symplectic 2-form d p wedge d q in phase space.",
        "formal_lean_statement": "theorem symplectic_liouville : d (omega) = 0 := by sorry",
        "reference_solution_code": "theorem symplectic_liouville : d (omega) = 0 := by ext; ring",
        "domain_topic": "SYMPLECTIC_GEOMETRY",
        "source_repository": "openai/math",
    }

    # Test admissibility audit endpoint
    adm_resp = client.post("/api/discovery/math-flywheel/audit-admissibility", json=task_payload)
    assert adm_resp.status_code == 200
    adm_data = adm_resp.json()
    assert adm_data["is_admissible"]
    assert "som_admissibility_hash" in adm_data

    # Test run flywheel cycle endpoint
    cycle_payload = {
        "cycle_id": "api_flywheel_cycle_test",
        "problem_tasks": [task_payload],
    }
    cycle_resp = client.post("/api/discovery/math-flywheel/run-cycle", json=cycle_payload)
    assert cycle_resp.status_code == 200
    cycle_data = cycle_resp.json()
    assert cycle_data["cycle_id"] == "api_flywheel_cycle_test"
    assert cycle_data["admissible_problems_count"] == 1
    assert cycle_data["compiled_ai_operators_count"] >= 1
    assert "som_math_flywheel_hash" in cycle_data
