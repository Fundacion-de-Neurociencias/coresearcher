"""
Tests for Non-Generative Energy-Based Epistemic Auditor (ADR-EPISTEMIC-040).
"""

from python.discovery.energy_predictive_auditor import (
    EnergyAuditVerdict,
    LatentPhysicalState,
    ModelPredictiveController,
    MPCEpistemicPlan,
    NonGenerativeEpistemicAuditor,
    VICRegAuditResult,
    VICRegRegularizer,
)


def test_vicreg_regularization_no_collapse():
    regularizer = VICRegRegularizer()
    emb_x = [
        [1.0, 0.0, -1.0],
        [0.0, 1.0, 0.5],
        [-1.0, -0.5, 0.0],
    ]
    emb_y = [
        [0.9, 0.1, -0.9],
        [0.1, 0.9, 0.4],
        [-0.9, -0.4, 0.1],
    ]

    res = regularizer.audit_batch_representations(emb_x, emb_y)
    assert isinstance(res, VICRegAuditResult)
    assert res.is_representation_collapsed is False
    assert res.invariance_loss < 0.1
    assert res.total_vicreg_loss > 0.0


def test_model_predictive_controller_planning():
    mpc = ModelPredictiveController(horizon=4, num_candidates=10)
    current_state = [1.0, 0.5]
    target_state = [0.0, 0.0]

    def linear_step(s, a):
        return [s[0] - 0.2 * a[0], s[1] - 0.2 * a[1]]

    plan = mpc.plan_latent_trajectory(current_state, target_state, linear_step)
    assert isinstance(plan, MPCEpistemicPlan)
    assert plan.horizon_steps == 4
    assert len(plan.optimal_action_sequence) == 4
    assert len(plan.projected_energy_trajectory) == 4


def test_energy_audit_sound_vs_fatal_violation():
    auditor = NonGenerativeEpistemicAuditor()

    # Case 1: Physically sound theory
    theory_valid = LatentPhysicalState(
        state_id="valid_lagrangian_01",
        embedding=[1.0, 2.0, 0.5],
        conserved_quantities={"energy": 100.0},
    )
    empirical_ref = LatentPhysicalState(
        state_id="empirical_meas_01",
        embedding=[1.05, 1.95, 0.48],
        conserved_quantities={"energy": 99.8},
    )

    verdict_valid = auditor.audit_physical_theory("theory_1", theory_valid, empirical_ref)
    assert isinstance(verdict_valid, EnergyAuditVerdict)
    assert verdict_valid.is_physically_sound is True
    assert verdict_valid.unnormalized_energy < 10.0
    assert verdict_valid.failure_mode is None

    # Case 2: Fatal physical violation (e.g., perpetual motion, overunity)
    theory_fatal = LatentPhysicalState(
        state_id="overunity_device",
        embedding=[50.0, -100.0, 20.0],
        hard_violations=["VIOLATION_FIRST_LAW_THERMODYNAMICS_OVERUNITY"],
    )

    verdict_fatal = auditor.audit_physical_theory("theory_2", theory_fatal, empirical_ref)
    assert verdict_fatal.is_physically_sound is False
    assert verdict_fatal.unnormalized_energy == float("inf")
    assert "Hard physical violation" in str(verdict_fatal.failure_mode)
