"""
Tests for Multiscale Latent Abstraction Engine (ADR-DISCOVERY-039).
"""

from python.discovery.multiscale_abstraction_engine import (
    AbstractionLevel,
    ActionConditionedPredictionVerdict,
    ActionConditionedPredictor,
    MultiscaleAbstractionEngine,
    MultiscaleStateNode,
)


def test_horizon_scaling_law():
    engine = MultiscaleAbstractionEngine(horizon_constant=500.0)

    # Micro level with high detail
    micro_h = engine.calculate_prediction_horizon(
        detail_dimension=100,
        noise_variance=0.2,
        level=AbstractionLevel.MICRO_IMPLEMENTATIONAL,
    )
    # Meso level with intermediate detail
    meso_h = engine.calculate_prediction_horizon(
        detail_dimension=10,
        noise_variance=0.05,
        level=AbstractionLevel.MESO_ALGORITHMIC,
    )
    # Macro level with low detail
    macro_h = engine.calculate_prediction_horizon(
        detail_dimension=2,
        noise_variance=0.01,
        level=AbstractionLevel.MACRO_COMPUTATIONAL_CONSERVATIVE,
    )

    # Verify hierarchy: Macro horizon >> Meso horizon >> Micro horizon
    assert macro_h > meso_h > micro_h
    assert micro_h < 1.0
    assert macro_h > 2000.0


def test_differentiable_action_conditioned_transition():
    engine = MultiscaleAbstractionEngine()
    state = MultiscaleStateNode(
        node_id="state_meso_01",
        level=AbstractionLevel.MESO_ALGORITHMIC,
        latent_vector=[1.0, 0.5, -0.5, 2.0],
        detail_dimension=4,
        conserved_quantities={"energy": 10.5},
    )
    action = [0.2, -0.1]

    verdict = engine.evaluate_action_conditioned_transition(state, action)

    assert isinstance(verdict, ActionConditionedPredictionVerdict)
    assert verdict.is_differentiable is True
    assert len(verdict.target_prediction) == 4
    # Self-prediction energy with expected=predicted should be 0.0
    assert verdict.energy_loss == 0.0
    assert verdict.gradient_norm == 0.0


def test_action_gradient_computation():
    predictor = ActionConditionedPredictor()
    s_t = [1.0, 2.0]
    a_t = [0.5, -0.5]
    predicted = predictor.predict_forward(s_t, a_t)

    # Simulate discrepancy with empirical target
    ground_truth = [predicted[0] + 0.4, predicted[1] - 0.2]
    energy, grad_a, grad_norm = predictor.compute_energy_and_gradients(predicted, ground_truth, a_t)

    assert energy > 0.0
    assert len(grad_a) == 2
    assert grad_norm > 0.0


def test_find_optimal_abstraction_level():
    engine = MultiscaleAbstractionEngine(horizon_constant=500.0)

    micro_node = MultiscaleStateNode(
        node_id="node_micro",
        level=AbstractionLevel.MICRO_IMPLEMENTATIONAL,
        latent_vector=[0.1] * 50,
        detail_dimension=50,
    )
    meso_node = MultiscaleStateNode(
        node_id="node_meso",
        level=AbstractionLevel.MESO_ALGORITHMIC,
        latent_vector=[0.5, 1.2, -0.3, 0.8],
        detail_dimension=5,
    )
    macro_node = MultiscaleStateNode(
        node_id="node_macro",
        level=AbstractionLevel.MACRO_COMPUTATIONAL_CONSERVATIVE,
        latent_vector=[10.5, 300.0],
        detail_dimension=2,
    )

    # For an inquiry targeting a horizon of ~100 steps
    reports = engine.find_optimal_abstraction_level(
        candidate_nodes=[micro_node, meso_node, macro_node],
        target_horizon=100.0,
        action=[0.1, 0.2],
    )

    assert len(reports) == 3
    optimal_reports = [r for r in reports if r.is_optimal_abstraction]
    assert len(optimal_reports) == 1
    # Meso should be closest to 100 steps (achievable ~95 steps)
    assert optimal_reports[0].level == AbstractionLevel.MESO_ALGORITHMIC
    assert "Optimal abstraction tier" in optimal_reports[0].recommendation
