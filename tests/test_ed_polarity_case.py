"""Tests for the Sakana Error Diffusion showcase case (python/discovery/ed_polarity_case.py)."""

import hashlib
import json
import random
import re
from pathlib import Path

from python.discovery import ed_polarity_case as ed
from python.discovery.formal_hypothesis import HypothesisEvaluator, hypothesis_from_dict

ROOT = Path(__file__).resolve().parent.parent
CASE_DIR = ROOT / "examples" / "sakana-ed-polarity"


def _full_state(hypothesis, witness):
    return {name: witness.get(name, 0) for name in hypothesis.variable_names}


def test_main_claim_is_proved_for_small_networks():
    for depth, width in ((1, 1), (2, 1), (3, 1), (2, 2)):
        result = ed.decide(depth, width)
        assert result["status"] == "PROVED", (depth, width, result)
        for part in result["parts"].values():
            assert part["content_verdict"] == "UNFALSIFIABLE"
            assert part["conflicting_assumption_sets"] == []


def test_hypothesis_object_has_explicit_assumptions_and_scope():
    h = ed.ed_hypothesis(2, 1)
    assert len(h.assumptions) == len(ed.ASSUMPTIONS)
    assert h.scope and "sg == 1" in h.scope
    assert h.is_continuous
    assert any(c.startswith("sp_1_0 >= 0") for c in h.claims)
    assert len(ed.sign_sufficiency_claims(2, 1)) == 8  # 4 families x 2 layers x 1 x 1


def test_dropping_assumptions_is_refuted_with_a_checkable_witness():
    for drop in (ed.ALL_WEIGHTS, ed.ALL_FPRIME):
        h = ed.ed_hypothesis(2, 1, drop=drop, claims="polarity")
        result = ed.verdict(h)
        assert result["status"] == "REFUTED"
        # The witness is re-checked by the enumeration-side interpreter, not by z3.
        state = _full_state(h, result["witness"])
        assert h.applies(state)
        assert h.violated_claims(state)


def test_necessity_depends_on_depth():
    assert set(ed.necessity_table(1, 1).values()) == {"REDUNDANT"}
    depth2 = ed.necessity_table(2, 1)
    assert {a for a, v in depth2.items() if v == "NECESSARY"} == {"Wpp>=0", "Wnp>=0", "fprime_p>=0"}
    assert set(ed.necessity_table(3, 1).values()) == {"NECESSARY"}


def test_transport_rival_is_sign_equivalent_but_not_value_equivalent():
    assert ed.decide(2, 1)["status"] == "PROVED"
    h = ed.transport_hypothesis(2, 1)
    result = ed.verdict(h)
    assert result["status"] == "REFUTED"
    state = _full_state(h, result["witness"])
    assert h.applies(state) and h.violated_claims(state)


def test_replay_agrees_on_nonnegative_sigmoid_networks():
    rng = random.Random(1)
    for _ in range(20):
        net = ed.random_network(3, 2, rng)
        result = ed.replay(net, [rng.uniform(0, 1)] * 2, [rng.uniform(0, 1)] * 2)
        assert result["weights_checked"] == 48
        assert result["disagreements"] == []


def test_replay_witnesses_break_the_sign_rule_on_concrete_networks():
    negative = ed.replay(ed.witness_negative_weight(), *ed.WITNESS_INPUT)
    decreasing = ed.replay(ed.witness_decreasing_activation(), *ed.WITNESS_INPUT)
    assert {d["weight"] for d in negative["disagreements"]} == {"Wpp_1_0_0", "Wnp_1_0_0"}
    assert len(decreasing["disagreements"]) == 4
    witness = ed.witness_decreasing_activation()
    assert all(w >= 0 for family in witness.W.values() for layer in family for row in layer for w in row)


def test_lean_file_is_complete_and_matches_the_recorded_check():
    lean = CASE_DIR / "EdPolarity.lean"
    text = lean.read_bytes().replace(b"\r\n", b"\n")
    assert b"sorry" not in text and b"admit" not in text
    for name in (b"theorem sens_polarized", b"theorem ed_sign_sufficiency"):
        assert name in text
    log = (CASE_DIR / "lean_check.txt").read_text(encoding="utf-8")
    recorded = re.search(r"File SHA-256: ([0-9a-f]{64})", log).group(1)
    assert hashlib.sha256(text).hexdigest() == recorded, "EdPolarity.lean changed: re-run Lean and update the log."
    assert "[propext, Classical.choice, Quot.sound]" in log


def test_formalizer_item_f21_gold_and_a_dropped_assumption():
    items = json.loads((ROOT / "docs/reference/benchmarks/formalizer_dataset.json").read_text(encoding="utf-8"))
    item = next(i for i in items["items"] if i["id"] == "F21")
    gold = hypothesis_from_dict({**item["gold"], "hypothesis_id": "F21-gold"})
    assert HypothesisEvaluator.evaluate(gold).content_verdict.value == item["intended_verdict"] == "UNFALSIFIABLE"
    weaker = hypothesis_from_dict(
        {**item["gold"], "assumptions": ["w_pp >= 0", "d_out >= 0"], "hypothesis_id": "F21-x"}
    )
    assert HypothesisEvaluator.evaluate(weaker).content_verdict.value == "FALSIFIABLE"
    assert HypothesisEvaluator.compare(weaker, gold).relation.value == "STRONGER"
