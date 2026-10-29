"""
tests/test_cellular_automata_barrier_auditor.py - Tests for ADR-DISCOVERY-070 and ADR-DISCOVERY-071.

Verifies:
1. Realization barrier detection: rejection of candidate invariants shared by Rule 90, 150, or 210.
2. Admissibility of invariants unique to Rule 30's non-linear OR structure.
3. Finite abstraction lasso barrier (Barrier B1) pruning.
4. Center column simulation mechanics for Rule 90 (eventually constant 0) and Rule 30.
5. Jen's adjacent-column moving edge relaxation and periodic word exclusion.
6. Integration with AsymptoticBarrierAuditor (ADR-DISCOVERY-045).
"""

from python.discovery.asymptotic_barrier_auditor import (
    AsymptoticBarrierAuditor,
    BarrierType,
    MathematicalMethodFamily,
)
from python.discovery.cellular_automata_barrier_auditor import (
    CellularAutomataBarrierAuditor,
    CellularBarrierType,
    ElementaryRule,
)
from python.discovery.rule30_word_exclusion import (
    Rule30PeriodicWordExclusionEngine,
)


def test_cellular_barrier_auditor_rejects_rule90_shared_invariant():
    """
    Asserts that an invariant holding for both Rule 30 and Rule 90 (linear additive)
    is caught and rejected by the realization barrier.
    """
    auditor = CellularAutomataBarrierAuditor()
    # Invariant that holds universally across all rules
    def universal_invariant(rule, t):
        return True

    verdict = auditor.audit_invariant_against_realization_barrier(
        candidate_id="INV-UNIVERSAL-SHARED",
        invariant_evaluator=universal_invariant,
        test_steps=16,
    )

    assert verdict.is_admissible is False
    assert verdict.detected_barrier == CellularBarrierType.RULE90_REALIZATION_OBSTRUCTION
    assert ElementaryRule.RULE_90 in verdict.falsifying_rules
    assert "Realization Barrier Obstruction" in verdict.detailed_critique
    assert "barrier_center_traces" in verdict.counterexample_trace


def test_cellular_barrier_auditor_rejects_rule150_shared_invariant():
    """
    Asserts that an invariant holding for Rule 30 and Rule 150 (but failing Rule 90)
    is rejected with RULE150_REALIZATION_OBSTRUCTION.
    """
    auditor = CellularAutomataBarrierAuditor()
    def invariant(rule, t):
        return rule in [ElementaryRule.RULE_30, ElementaryRule.RULE_150]

    verdict = auditor.audit_invariant_against_realization_barrier(
        candidate_id="INV-RULE150-SHARED",
        invariant_evaluator=invariant,
        test_steps=16,
    )

    assert verdict.is_admissible is False
    assert verdict.detected_barrier == CellularBarrierType.RULE150_REALIZATION_OBSTRUCTION
    assert ElementaryRule.RULE_150 in verdict.falsifying_rules


def test_cellular_barrier_auditor_rejects_rule210_shared_invariant():
    """
    Asserts that an invariant holding for Rule 30 and Rule 210 (but failing Rule 90/150)
    is rejected with RULE210_REALIZATION_OBSTRUCTION.
    """
    auditor = CellularAutomataBarrierAuditor()
    def invariant(rule, t):
        return rule in [ElementaryRule.RULE_30, ElementaryRule.RULE_210]

    verdict = auditor.audit_invariant_against_realization_barrier(
        candidate_id="INV-RULE210-SHARED",
        invariant_evaluator=invariant,
        test_steps=16,
    )

    assert verdict.is_admissible is False
    assert verdict.detected_barrier == CellularBarrierType.RULE210_REALIZATION_OBSTRUCTION
    assert ElementaryRule.RULE_210 in verdict.falsifying_rules


def test_cellular_barrier_auditor_admits_rule30_specific_invariant():
    """
    Asserts that an invariant holding exclusively for Rule 30 (broken on Rule 90, 150, 210)
    is recognized as admissible and passes the realization firewall.
    """
    auditor = CellularAutomataBarrierAuditor()
    # Holds only on Rule 30's non-linear structure
    def rule30_only_invariant(rule, t):
        return rule == ElementaryRule.RULE_30

    verdict = auditor.audit_invariant_against_realization_barrier(
        candidate_id="INV-RULE30-NONLINEAR",
        invariant_evaluator=rule30_only_invariant,
        test_steps=16,
    )

    assert verdict.is_admissible is True
    assert verdict.detected_barrier == CellularBarrierType.NONE_DETECTED
    assert len(verdict.falsifying_rules) == 0
    assert "Admissible" in verdict.detailed_critique


def test_cellular_barrier_auditor_rejects_false_rule30_invariant():
    """
    Asserts that an invariant false for Rule 30 itself is immediately rejected.
    """
    auditor = CellularAutomataBarrierAuditor()
    def false_invariant(rule, t):
        return False

    verdict = auditor.audit_invariant_against_realization_barrier(
        candidate_id="INV-FALSE-R30",
        invariant_evaluator=false_invariant,
        test_steps=16,
    )

    assert verdict.is_admissible is False
    assert ElementaryRule.RULE_30 in verdict.falsifying_rules
    assert "false for Rule 30 itself" in verdict.detailed_critique


def test_finite_abstraction_lasso_detection():
    """
    Asserts that Barrier B1 (Rule30ZeroBoundaryBarriers.finite_abstraction_has_lasso)
    prunes any finite state abstraction.
    """
    verdict_finite = CellularAutomataBarrierAuditor.audit_finite_abstraction_search(
        candidate_id="ABS-FINITE-32",
        state_space_size=32,
    )
    assert verdict_finite.is_admissible is False
    assert verdict_finite.detected_barrier == CellularBarrierType.FINITE_ABSTRACTION_LASSO
    assert "Barrier B1 Obstruction" in verdict_finite.detailed_critique

    verdict_infinite = CellularAutomataBarrierAuditor.audit_finite_abstraction_search(
        candidate_id="ABS-INFINITE",
        state_space_size=float("inf"),
    )
    assert verdict_infinite.is_admissible is True
    assert verdict_infinite.detected_barrier == CellularBarrierType.NONE_DETECTED


def test_rule_simulation_center_column():
    """
    Verifies the center column simulation mechanics:
    Rule 90 from single seed has center(0)=True, center(t)=False for all t >= 1.
    Rule 30 center column maintains non-trivial values.
    """
    r90_center = CellularAutomataBarrierAuditor.simulate_center_column(ElementaryRule.RULE_90, steps=10)
    assert r90_center[0] is True
    assert all(val is False for val in r90_center[1:])

    r30_center = CellularAutomataBarrierAuditor.simulate_center_column(ElementaryRule.RULE_30, steps=10)
    assert r30_center[0] is True
    assert r30_center[1] is True
    assert any(val is False for val in r30_center)  # Rule 30 exhibits mixed 0 and 1


def test_rule30_word_exclusion_engine():
    """
    Tests periodic word exclusion based on Jen's moving edge contradiction (v=1).
    """
    report_large_q = Rule30PeriodicWordExclusionEngine.test_repeating_zero_tail(q_zeros=12)
    assert report_large_q.is_contradictory is True
    assert "not_eventuallyWord_white_12" in report_large_q.candidate_lean_theorem
    assert "Rule30Jen" in report_large_q.candidate_lean_theorem

    report_small_q = Rule30PeriodicWordExclusionEngine.test_repeating_zero_tail(q_zeros=2)
    assert report_small_q.is_contradictory is False

    report_p2 = Rule30PeriodicWordExclusionEngine.analyze_period_two_alternating_tail()
    assert report_p2.target.word_pattern == "10"
    assert report_p2.metadata["known_width_bound"] == 52
    assert "period_two_reduced_to_q01" in report_p2.candidate_lean_theorem


def test_asymptotic_barrier_cellular_invariant_pruning():
    """
    Verifies that AsymptoticBarrierAuditor (ADR-DISCOVERY-045) prunes the
    CELLULAR_AUTOMATA_LOCAL_INVARIANT method family via CELLULAR_REALIZATION_BARRIER.
    """
    verdict = AsymptoticBarrierAuditor.audit_proof_strategy(
        strategy_id="STRAT-R30-LOCAL-INVARIANT",
        target_hypothesis="Rule 30 Center Column Aperiodicity",
        method_family=MathematicalMethodFamily.CELLULAR_AUTOMATA_LOCAL_INVARIANT,
        target_threshold=0.0,
    )

    assert verdict.is_obstructed_by_known_barrier is True
    assert verdict.barrier_detected == BarrierType.CELLULAR_REALIZATION_BARRIER.value
    assert "Cellular Realization Barrier" in verdict.barrier_description
    assert any("LEAN4_RULIOLOGY_REALIZATION_CERTIFICATE" in p for p in verdict.orthogonal_paradigms_recommended)
