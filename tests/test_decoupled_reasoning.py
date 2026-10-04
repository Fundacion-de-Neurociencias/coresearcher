"""
tests/test_decoupled_reasoning.py - Tests for ADR-REASONING-031 Epistemic Search & Decoupled Machine Reasoning.
Verifies that:
1. EpistemicTreeSearch executes search over competing trajectories.
2. PhysicalCoherenceCourt acts as an unyielding reality judge on search branches.
3. Unverified next-token generation is decoupled from formal truth state-space pruning.
"""

import pytest

from python.discovery.inference_time_scaling import EpistemicTreeSearch
from python.discovery.state_space import StateSpaceOmega, StateSpaceAxis
from python.discovery.physical_theorem_court import PhysicalCoherenceCourt


@pytest.mark.epistemic
@pytest.mark.fast
def test_decoupled_machine_reasoning_search():
    """Verifies that search_with_decoupled_reasoning coordinates search + physical court validation."""
    omega = StateSpaceOmega.create_canonical_neurodegen_space()

    result = EpistemicTreeSearch.search_with_decoupled_reasoning(
        question="How does pathological tau propagate across the brain connectome?",
        state_space=omega,
        use_local_ai_proposer=True,
    )

    assert result is not None
    assert "search_id" in result
    assert result["branches_evaluated_count"] >= 4
    assert "winning_branch" in result
    assert "physical_court_audit" in result

    # Check that PhysicalCoherenceCourt validated the winning branch
    court_audit = result["physical_court_audit"]
    assert court_audit["is_physically_coherent"] is True
    assert court_audit["verdict"] == "VERIFIED_COHERENT"
    assert court_audit["som_audit_hash"].startswith("sha256:")
    assert result["move_37_deliberation_status"] == "VALIDATED"


@pytest.mark.epistemic
@pytest.mark.fast
def test_search_node_structure_with_court_fields():
    """Verifies that EpistemicSearchNode contains explicit court inspection fields."""
    omega = StateSpaceOmega("OMEGA-TEST-NODE")
    result = EpistemicTreeSearch.search_optimal_trajectory(
        question="Test trajectory optimization",
        state_space=omega,
    )

    winning = result["winning_branch"]
    assert "is_physically_coherent" in winning
    assert "court_verdict" in winning
    assert winning["is_physically_coherent"] is True
