"""
tests/test_rule30_reasoning_bridge.py - Tests for ADR-DISCOVERY-072.

Verifies:
1. Python AST exploration of bitmask strip certificates.
2. Realization barrier filtering: ensuring certificates do not hold on Rule 90 / Rule 150.
3. Lean 4 code emission matching Rule30PrizeKit specification.
"""

from python.discovery.cellular_automata_barrier_auditor import ElementaryRule
from python.discovery.rule30_reasoning_bridge import (
    BitmaskStripCertificateExplorer,
    CandidateWord,
    Rule30ReasoningBridge,
)


def test_candidate_word_parsing():
    """Verifies parsing of binary periodic word patterns."""
    word = CandidateWord.from_string("01111111")
    assert word.pattern_str == "01111111"
    assert word.length == 8
    assert word.bits == 127
    assert word.to_bool_list() == [False, True, True, True, True, True, True, True]


def test_bitmask_strip_certificate_explorer():
    """
    Verifies that BitmaskStripCertificateExplorer accurately determines
    satisfaction of the bitmask strip certificate on Rule 30 while
    falsifying on linear Rule 90.
    """
    explorer = BitmaskStripCertificateExplorer()
    w8_bools = [False, True, True, True, True, True, True, True]  # 0 1^7

    # Holds on Rule 30
    assert explorer.evaluate_strip_certificate(ElementaryRule.RULE_30, w8_bools, K=5, k_warmup=2) is True

    # Breaks on linear Rule 90
    assert explorer.evaluate_strip_certificate(ElementaryRule.RULE_90, w8_bools, K=5, k_warmup=2) is False


def test_rule30_reasoning_bridge_barrier_clearing():
    """
    Asserts that candidate word 01111111 clears the realization barrier
    and generates compliant Lean 4 proof code.
    """
    bridge = Rule30ReasoningBridge()
    verdict = bridge.explore_word_certificate("01111111", strip_width_K=5, warmup_k=2)

    assert verdict.holds_on_rule30 is True
    assert verdict.holds_on_rule90 is False
    assert verdict.holds_on_rule150 is False
    assert verdict.is_barrier_cleared is True
    assert "BARRIER CLEARED" in verdict.barrier_critique
    assert verdict.generated_lean_code is not None
    assert "not_eventually_word_01111111" in verdict.generated_lean_code
    assert "not_eventually_word_strip" in verdict.generated_lean_code


def test_rule30_reasoning_bridge_rejects_failing_word():
    """
    Asserts that an uncertifiable parameter combination fails on Rule 30
    and is prevented from generating proof code.
    """
    bridge = Rule30ReasoningBridge()
    # At K=2, strip width is too small to certify word 01111111
    verdict = bridge.explore_word_certificate("01111111", strip_width_K=2, warmup_k=1)

    assert verdict.holds_on_rule30 is False
    assert verdict.is_barrier_cleared is False
    assert verdict.generated_lean_code is None
