"""
tests/test_heuristic_physical_and_formal_invariants.py - Unit tests for unvalidated physical and formal heuristics.

Verifies:
1. PhysicalTheoremCourt audits SYMPLECTIC_PHASE_CONSERVATION (Liouville volume preservation / phase divergence = 0).
2. PhysicalTheoremCourt audits CONFORMATIONAL_RMSD_BOUND (heuristic RMSD bound of 0.50 angstrom).
3. ProofEquivalenceAuditor computes the partial-progress and axiom-hygiene heuristics on Lean arguments.
"""

from __future__ import annotations

from python.discovery.frontier_math_flywheel import (
    FrontierMathProblemTask,
    ProofEquivalenceAuditor,
)
from python.discovery.physical_theorem_court import (
    PhysicalConservationConstraint,
    PhysicalConservationType,
)


def test_symplectic_phase_conservation_satisfied():
    """Verifies that Hamiltonian phase-space divergence near zero satisfies Symplectic phase conservation."""
    constraint = PhysicalConservationConstraint(
        law_type=PhysicalConservationType.SYMPLECTIC_PHASE_CONSERVATION,
        canonical_formula="div_phase(H) = 0",
        tolerance=1e-5,
    )

    state = {}
    diff_rates = {"phase_space_divergence": 1e-6}
    result = constraint.check_compliance(state, diff_rates)

    assert result["satisfied"] is True
    assert result["violation_magnitude"] == 1e-6


def test_symplectic_phase_conservation_violated():
    """Verifies that non-zero phase-space divergence (violating Liouville's theorem) is flagged."""
    constraint = PhysicalConservationConstraint(
        law_type=PhysicalConservationType.SYMPLECTIC_PHASE_CONSERVATION,
        canonical_formula="div_phase(H) = 0",
        tolerance=1e-5,
    )

    state = {}
    diff_rates = {"phase_space_divergence": 0.05}  # Large divergence -> spurious energy/dissipation
    result = constraint.check_compliance(state, diff_rates)

    assert result["satisfied"] is False
    assert result["violation_magnitude"] == 0.05


def test_conformational_rmsd_bound_satisfied():
    """Verifies that conformational RMSD <= 0.50 A satisfies quantum tight-binding ground state constraint."""
    constraint = PhysicalConservationConstraint(
        law_type=PhysicalConservationType.CONFORMATIONAL_RMSD_BOUND,
        canonical_formula="RMSD(conformational, ground_state) <= 0.50 A",
        tolerance=1e-4,
    )

    state = {"conformational_rmsd_angstrom": 0.22}
    diff_rates = {}
    result = constraint.check_compliance(state, diff_rates)

    assert result["satisfied"] is True
    assert result["violation_magnitude"] == 0.0


def test_conformational_rmsd_bound_violated():
    """Verifies that conformational distortion > 0.50 A breaches tight-binding quantum equilibrium."""
    constraint = PhysicalConservationConstraint(
        law_type=PhysicalConservationType.CONFORMATIONAL_RMSD_BOUND,
        canonical_formula="RMSD(conformational, ground_state) <= 0.50 A",
        tolerance=1e-4,
    )

    state = {"conformational_rmsd_angstrom": 1.15}  # Excessive steric distortion
    diff_rates = {}
    result = constraint.check_compliance(state, diff_rates)

    assert result["satisfied"] is False
    assert result["violation_magnitude"] > 0.60


def test_partial_progress_and_axiom_hygiene_heuristics():
    """Checks the partial-progress and axiom-hygiene heuristics on Lean arguments."""
    task = FrontierMathProblemTask(
        task_id="task_riemann_test",
        title="Riemann Analytic Continuation",
        problem_statement_prose="Zeta function analytic continuation holds without singular branch cuts.",
        formal_lean_statement="theorem riemann_analytic : analytic_continuation zeta := by sorry",
    )

    # 1. Partial proof with sorry
    partial_code = """
    lemma functional_equation_step1 : eq1 := by ring
    lemma functional_equation_step2 : eq2 := by linarith
    theorem riemann_analytic : analytic_continuation zeta := by sorry
    """
    partial_score = ProofEquivalenceAuditor.evaluate_submitted_proof(task, partial_code)

    assert partial_score.partial_proof_progress_heuristic >= 0.35
    assert partial_score.axiom_hygiene_heuristic == 0.70  # Contains sorry penalty
    assert partial_score.contains_sorry_escape is True

    # 2. Fake axiom injection
    fake_code = """
    axiom magic_analytic_jump : False
    theorem riemann_analytic : analytic_continuation zeta := by apply magic_analytic_jump
    """
    fake_score = ProofEquivalenceAuditor.evaluate_submitted_proof(task, fake_code)

    assert fake_score.axiom_hygiene_heuristic == 0.0  # Fake axioms give zero axiom hygiene
    assert fake_score.dense_reward_score == 0.0
    assert (
        "unguided custom axioms" in fake_score.critique_notes.lower()
        or "custom axioms" in fake_score.critique_notes.lower()
    )

    # 3. Kernel accepted full proof
    complete_code = """
    lemma step_identity : 1 = 1 := by rfl
    theorem riemann_analytic : analytic_continuation zeta := by rfl
    """
    full_score = ProofEquivalenceAuditor.evaluate_submitted_proof(task, complete_code)

    assert full_score.static_checks_passed is True
    assert full_score.partial_proof_progress_heuristic == 1.0
    assert full_score.axiom_hygiene_heuristic == 1.0
    assert full_score.dense_reward_score == 1.0
