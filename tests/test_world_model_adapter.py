"""
tests/test_world_model_adapter.py - Test suite for ADR-DISCOVERY-038
Verifies:
1. Latent intervention simulation over continuous state channels (H-JEPA).
2. Infinite Energy Guardrail (E = +inf): Immediate pruning of destructive or conservation breaches.
3. Hierarchical macro-subgoal achievement tracking.
"""

import pytest
import math
from python.discovery.world_model_adapter import (
    WorldModelEpistemicAdapter,
    LatentInterventionSpec,
    SafetyConstraintSpec,
    GuardrailType,
    LatentSimulationVerdict,
)


def test_feasible_latent_intervention_minimum_energy():
    """
    Simulates a safe intervention: adjusting synaptic density without breaching energy bounds.
    """
    initial_state = {
        "synaptic_density": 0.50,
        "total_energy": 10.0,
        "temperature": 37.0,
    }

    intervention = LatentInterventionSpec(
        intervention_id="INT-SYNAPSE-STABILIZE",
        target_manifold_node="synaptic_density",
        intervention_magnitude=0.15,
        safety_constraints=[
            SafetyConstraintSpec(
                constraint_id="GUARD-MAX-ENERGY",
                guardrail_type=GuardrailType.CONSERVATION_OF_ENERGY,
                target_channel="total_energy",
                max_safe_value=20.0,
            )
        ]
    )

    result = WorldModelEpistemicAdapter.simulate_latent_intervention(
        intervention=intervention,
        current_latent_state=initial_state
    )

    assert result.guardrail_violated is False
    assert result.verdict == LatentSimulationVerdict.FEASIBLE_MINIMUM_ENERGY
    assert not math.isinf(result.projected_energy_cost)
    assert result.projected_latent_state["synaptic_density"] == pytest.approx(0.65)
    assert result.som_simulation_hash.startswith("sha256:")


def test_infinite_energy_guardrail_breach_interception():
    """
    Simulates a violent or destructive intervention that breaches the conservation bound,
    verifying that cost becomes +inf and the trajectory is pruned.
    """
    initial_state = {
        "synaptic_density": 0.50,
        "total_energy": 18.0,
        "temperature": 37.0,
    }

    # Intervening by +10.0 magnitude will push energy to 18.0 + 5.0 = 23.0 (> max 20.0)
    destructive_intervention = LatentInterventionSpec(
        intervention_id="INT-EXPLOSIVE-EXCITATION",
        target_manifold_node="synaptic_density",
        intervention_magnitude=10.0,
        safety_constraints=[
            SafetyConstraintSpec(
                constraint_id="GUARD-MAX-ENERGY",
                guardrail_type=GuardrailType.CONSERVATION_OF_ENERGY,
                target_channel="total_energy",
                max_safe_value=20.0,
            )
        ]
    )

    result = WorldModelEpistemicAdapter.simulate_latent_intervention(
        intervention=destructive_intervention,
        current_latent_state=initial_state
    )

    assert result.guardrail_violated is True
    assert math.isinf(result.projected_energy_cost)
    assert result.verdict == LatentSimulationVerdict.PRUNED_INFINITE_ENERGY_GUARDRAIL
    assert "GUARD-MAX-ENERGY" in (result.violated_constraint or "")


def test_hierarchical_subgoal_achievement():
    """
    Verifies that macro subgoals are tracked when the latent state approaches target values.
    """
    initial_state = {
        "glycolytic_reserve": 0.30,
        "total_energy": 5.0,
    }

    intervention = LatentInterventionSpec(
        intervention_id="INT-METABOLIC-RESCUE",
        target_manifold_node="glycolytic_reserve",
        intervention_magnitude=0.50,
        safety_constraints=[]
    )

    macro_subgoals = [
        {"glycolytic_reserve": 0.80} # Target is 0.30 + 0.50 = 0.80
    ]

    result = WorldModelEpistemicAdapter.simulate_latent_intervention(
        intervention=intervention,
        current_latent_state=initial_state,
        macro_subgoals=macro_subgoals
    )

    assert result.guardrail_violated is False
    assert result.hierarchical_subgoals_completed == 1
