"""
tests/test_ablation_rebuttal_engine.py - Test suite for ADR-DISCOVERY-037
Verifies:
1. Automated theoretical term ablation (isolating non-linear coupling potentials).
2. Asymptotic limit verification (recovering linear baseline when perturbation vanishes).
3. Closed-loop simulated peer-review critiques & rigorous mathematical rebuttals.
"""

from python.discovery.ablation_rebuttal_engine import (
    AblationRebuttalEngine,
    AblationStatus,
    RebuttalVerdict,
    SimulatedObjection,
)


def test_theoretical_ablation_quartic_oscillator():
    """
    Tests ablation on a Duffing/quartic oscillator:
    T = 1/2 * m * q_dot**2
    V_base = 1/2 * k * q**2
    V_int = 1/4 * lambda * q**4
    Ablating V_int must recover the harmonic oscillator: m*q_ddot + k*q = 0
    """
    ablations = AblationRebuttalEngine.run_theoretical_ablation(
        model_id="MODEL-DUFFING-OSCILLATOR",
        q_name="q",
        kinetic_str="1/2 * m * q_dot**2",
        base_potential_str="1/2 * k * q**2",
        interaction_terms={"lambda_quartic": "1/4 * k * q**4"},
    )

    assert len(ablations) == 1
    ab = ablations[0]
    assert ab.term_name == "lambda_quartic"
    assert ab.status == AblationStatus.NECESSARY_AND_SUFFICIENT
    assert ab.recovers_known_baseline is True


def test_simulated_peer_review_rebuttal_loop():
    """
    Simulates adversarial reviewer objections (gauge ambiguity, non-linear terms)
    and verifies that evidence-grounded rebuttals are accepted.
    """
    objections = [
        SimulatedObjection(
            reviewer_id="Reviewer-1 (Differential Geometry)",
            critique_point="Potential coordinate singularity in proposed Lagrangian.",
            severity="MAJOR",
        ),
        SimulatedObjection(
            reviewer_id="Reviewer-2 (Phenomenology)",
            critique_point="Model may inadvertently rely on linear approximations.",
            severity="MINOR",
        ),
    ]

    rebuttals = AblationRebuttalEngine.conduct_simulated_peer_review_rebuttal(
        model_id="MODEL-RELATIVISTIC-FIELD",
        objections=objections,
        derived_dynamics_summary="Covariant Euler-Lagrange equations",
    )

    assert len(rebuttals) == 2
    assert all(r.rebuttal_verdict == RebuttalVerdict.REBUTTAL_ACCEPTED for r in rebuttals)
    assert "gauge" in rebuttals[0].author_defense_proof.lower()
    assert "sin(q)" in rebuttals[1].mathematical_grounding.lower()


def test_full_dossier_generation():
    """
    Runs the full ScientistTwo-style ablation & rebuttal cycle.
    """
    dossier = AblationRebuttalEngine.generate_dossier(
        model_id="MODEL-PENDULUM-FULL",
        q_name="theta",
        kinetic_str="1/2 * m * l**2 * theta_dot**2",
        base_potential_str="1/2 * m * g * l * theta**2",  # small angle base
        interaction_terms={"anharmonic_correction": "1/24 * m * g * l * theta**4"},
        objections=[
            SimulatedObjection(reviewer_id="Reviewer-1", critique_point="Check coordinate validity.", severity="MINOR")
        ],
    )

    assert dossier.overall_peer_review_status == "ACCEPTED_AFTER_REBUTTAL"
    assert dossier.all_terms_necessary is True
    assert dossier.som_dossier_hash.startswith("sha256:")
