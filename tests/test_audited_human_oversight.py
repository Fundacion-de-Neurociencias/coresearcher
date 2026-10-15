"""
tests/test_audited_human_oversight.py - Tests for ADR-DISCOVERY-049
Verifies:
1. Detection and interception of passive rubber-stamping (dwell time violation + no counterexamples opened).
2. Cognitive inspection challenge generation and verification.
3. Consensus bias interception when AI rejects sound, physically conserved theories for being 'unconventional' or 'not mainstream'.
4. Verified active human oversight workflow with complete cryptographic Merkle anchoring.
"""

from python.discovery.audited_human_oversight import (
    AuditedHumanOversightEngine,
    CognitiveInspectionChallenge,
    EpistemicTaskCriticality,
    HumanInteractionTelemetry,
    OversightVerdictStatus,
)


def test_rubber_stamping_interception():
    """
    Tests that a human reviewer approving an AI rejection/acceptance in 1.2 seconds
    without inspecting flagged counterexamples is strictly flagged as RUBBER_STAMPING_DETECTED.
    """
    telemetry = HumanInteractionTelemetry(
        reviewer_id="fast_clicker_editor",
        dwell_time_seconds=1.2,  # Far below the 45s required for PARADIGMATIC_NOVELTY
        counterexamples_inspected=[],
        human_notes_length_chars=0,
        substantive_modifications_made=False,
        explicit_causal_rationale="",
        answered_inspection_challenge=False,
    )
    record = AuditedHumanOversightEngine.evaluate_oversight_integrity(
        claim_id="CLAIM-QUANTUM-GRAVITY-01",
        task_criticality=EpistemicTaskCriticality.PARADIGMATIC_NOVELTY,
        ai_recommendation="REJECT",
        human_decision="REJECT",
        telemetry=telemetry,
        ai_critique_text="Complex topological defect analysis.",
        flagged_counterexamples=["InstantonSingularity", "NonUnitaryBranch"],
    )
    assert record.status == OversightVerdictStatus.RUBBER_STAMPING_DETECTED
    assert record.active_oversight_score < 0.5
    assert any("dwell time" in v.lower() for v in record.violations_detected)
    assert any("counterexample" in v.lower() for v in record.violations_detected)


def test_cognitive_inspection_challenge_generation():
    """
    Verifies that the engine generates targeted adversarial challenges
    requiring genuine verification before sign-off.
    """
    challenge = AuditedHumanOversightEngine.generate_cognitive_inspection_challenge(
        claim_id="NS-Blowup-01",
        adversarial_counterexamples=["BoundarySingularityAtInfinity", "EnergyDissipationCutoff"],
    )
    assert isinstance(challenge, CognitiveInspectionChallenge)
    assert challenge.target_claim_id == "NS-Blowup-01"
    assert challenge.valid_counterexample_key == "BoundarySingularityAtInfinity"
    assert "BoundarySingularityAtInfinity" in challenge.candidate_options
    assert len(challenge.candidate_options) >= 3


def test_ai_consensus_bias_interception():
    """
    Verifies that when an AI recommendation rejects a theory for being 'unconventional'
    and 'contrary to literature' despite the math being sound and invariants conserved,
    the human overturning the rejection is validated as CONSENSUS_BIAS_INTERCEPTED.
    """
    ai_critique = (
        "The proposed non-equilibrium thermomechanics model is mathematically rigorous and conserves "
        "total energy and entropy production. However, it presents an unconventional and not mainstream "
        "interpretation departing from consensus textbooks."
    )
    telemetry = HumanInteractionTelemetry(
        reviewer_id="sovereign_physicist",
        dwell_time_seconds=60.0,
        counterexamples_inspected=["ThermodynamicBranchingPoint"],
        human_notes_length_chars=120,
        substantive_modifications_made=True,
        explicit_causal_rationale="Accepted because conservation laws and mathematical proofs are intact; departure from orthodoxy is not a flaw.",
        answered_inspection_challenge=True,
    )
    record = AuditedHumanOversightEngine.evaluate_oversight_integrity(
        claim_id="CLAIM-NON-ORTHODOX-THERMO",
        task_criticality=EpistemicTaskCriticality.PARADIGMATIC_NOVELTY,
        ai_recommendation="REJECT",
        human_decision="ACCEPT",
        telemetry=telemetry,
        ai_critique_text=ai_critique,
        is_mathematically_sound=True,
        conserves_physical_invariants=True,
    )
    assert record.status == OversightVerdictStatus.CONSENSUS_BIAS_INTERCEPTED
    assert record.active_oversight_score >= 0.8
    assert record.consensus_bias_risk > 0.5


def test_active_oversight_verified_full_flow():
    """
    Tests complete valid oversight satisfying dwell time, counterexample checks, and rationale.
    """
    telemetry = HumanInteractionTelemetry(
        reviewer_id="diligent_reviewer_42",
        dwell_time_seconds=75.0,
        counterexamples_inspected=["SingularityHorizon"],
        human_notes_length_chars=95,
        substantive_modifications_made=True,
        explicit_causal_rationale="Verified invariant bounds in Section 4; counterexample properly mitigated.",
        answered_inspection_challenge=True,
    )
    record = AuditedHumanOversightEngine.evaluate_oversight_integrity(
        claim_id="CLAIM-RELATIVITY-55",
        task_criticality=EpistemicTaskCriticality.PARADIGMATIC_NOVELTY,
        ai_recommendation="ACCEPT",
        human_decision="ACCEPT",
        telemetry=telemetry,
        ai_critique_text="Consistent curvature bounds.",
        is_mathematically_sound=True,
        conserves_physical_invariants=True,
        flagged_counterexamples=["SingularityHorizon"],
    )
    assert record.status == OversightVerdictStatus.ACTIVE_OVERSIGHT_VERIFIED
    assert record.active_oversight_score == 1.0
    assert record.som_oversight_hash.startswith("sha256:")
