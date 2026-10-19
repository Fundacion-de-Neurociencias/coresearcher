"""Counterexample search benchmark: corpus, point check, arms (with stubs) and scoring.

Items used here are at indices 1000 and above, outside the benchmark (corpus indices are 0..199).
"""

import json
import random
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts" / "benchmarks"))

import run_counterexample_search as ce  # noqa: E402

from python.discovery.formal_hypothesis import ThresholdExceeded, hypothesis_from_dict  # noqa: E402


def item(index: int) -> dict:
    return ce.make_item(index)


def test_corpus_is_deterministic_and_has_the_declared_shape():
    a, b = ce.make_item(7), ce.make_item(7)
    assert a == b
    assert [x["planted"] for x in ce.corpus()].count(True) == ce.N_ITEMS - ce.N_CORRECT
    for i in (0, 150):
        x = item(i)
        assert len(x["variables"]) == ce.N_VARIABLES
        assert all(v["domain"] == list(ce.DOMAIN) for v in x["variables"])


def test_the_corpus_is_beyond_the_exhaustive_threshold():
    x = item(0)
    spec = {"hypothesis_id": "T", "variables": x["variables"], "assumptions": x["assumptions"], "claims": x["claims"]}
    with pytest.raises(ThresholdExceeded):
        hypothesis_from_dict(spec)
    assert ce.exact_arm(x)["status"] == "BLOCKED"


@pytest.mark.parametrize("index", [0, 25, 99])
def test_correct_items_have_no_counterexample_among_samples(index):
    x = item(index)
    preds = ce._predicates(x)
    rng = random.Random(index)
    for _ in range(2000):
        state = {n: rng.choice(ce.DOMAIN) for n in ce.variable_names()}
        assert ce.check_state(x, state, preds)[0] != "CONFIRMED"


@pytest.mark.parametrize("index", [100, 150, 199])
def test_planted_pattern_is_confirmed_and_its_neighbour_is_not(index):
    x = item(index)
    pattern = x["pattern"]
    state = {n: 0 for n in ce.variable_names()}
    state.update(pattern)
    status, violated = ce.check_state(x, state)
    assert status == "CONFIRMED" and violated == [x["claims"][-1]]
    other = dict(state)
    other["v3" if "v3" not in pattern else "v4"] = 9
    other[next(n for n in pattern if n != "v0")] = (pattern[next(n for n in pattern if n != "v0")] + 1) % 10
    assert ce.check_state(x, other)[0] != "CONFIRMED"


def test_point_check_rejects_malformed_and_irrelevant_states():
    x = item(120)
    good = {n: 5 for n in ce.variable_names()}
    assert ce.check_state(x, {"v0": 5})[0] == "NOT_A_STATE"
    assert ce.check_state(x, dict(good, v0=10))[0] == "NOT_A_STATE"
    assert ce.check_state(x, dict(good, v0=True))[0] == "NOT_A_STATE"
    assert ce.check_state(x, dict(good, v0="5"))[0] == "NOT_A_STATE"
    assert ce.check_state(x, None)[0] == "NOT_A_STATE"
    irrelevant = dict(good, v0=x["pattern"]["v0"] - 1 if x["pattern"]["v0"] > 0 else 9)
    assert ce.check_state(x, irrelevant)[0] == "NOT_RELEVANT"


def test_parser_reads_only_json_object_lines():
    text = 'Here are states:\n{"v0": 1, "v1": 2}\n,\n{"v0": 3\n{"v0": 4}'
    states, dropped = ce.parse_states(text)
    assert states == [{"v0": 1, "v1": 2}, {"v0": 4}] and dropped == 1


def test_random_arm_is_seeded_and_budgeted():
    x = item(130)
    first, second = ce.random_arm(x, 9), ce.random_arm(x, 9)
    assert first == second and first["candidates"] == ce.BUDGET and first["budget_used"] == ce.BUDGET


def test_proposer_arm_with_a_stub_model_counts_only_confirmed_states():
    x = item(160)
    pattern = x["pattern"]
    hit = {n: 0 for n in ce.variable_names()}
    hit.update(pattern)
    miss = {n: 0 for n in ce.variable_names()}
    miss["v0"] = (pattern["v0"] + 5) % 10
    prompts = []

    def propose(prompt, seed):
        prompts.append((prompt, seed))
        return "\n".join(json.dumps(s) for s in ([hit] + [miss] * 9)) + "\nYou can also try this."

    result = ce.proposer_arm(x, propose)
    assert len(prompts) == ce.CALLS
    assert result["detected"] and result["confirmed"] == ce.CALLS
    assert result["candidates"] == ce.BUDGET
    assert [s for _, s in prompts] == [ce.PROPOSER_SEED + 10 * 160 + k for k in range(ce.CALLS)]


def test_proposer_prompt_names_no_violated_claim():
    x = item(170)
    prompt = ce.item_prompt(x, 0)
    assert x["pattern"]["v0"] is not None
    assert str(x["pattern"]) not in prompt
    assert "not (v0 ==" in prompt  # the claim is shown, as the protocol requires
    assert "wrong" not in prompt.lower() and "violate" not in prompt.lower()


def test_run_and_score_end_to_end_with_a_stub_proposer(tmp_path, monkeypatch):
    monkeypatch.setattr(ce, "RAW", tmp_path / "raw.jsonl")
    monkeypatch.setattr(ce, "N_ITEMS", 6)
    monkeypatch.setattr(ce, "N_CORRECT", 3)
    zeros = {n: 0 for n in ce.variable_names()}

    def propose(prompt, seed):
        return json.dumps(zeros)

    for arm in "ER":
        ce.run(arm, range(6))
    ce.run("P", range(6), propose=propose)
    rows = ce.load_raw()
    assert {r["arm"] for r in rows} == {"E", "R", "P"} and len(rows) == 18
    result = ce.score(rows)
    assert result["arms"]["E"]["detection_planted"] == 0.0
    assert "A" in result["criteria"] and "S" in result["criteria"]
    assert result["validity"]["met"] is True


def test_score_refuses_results_from_another_protocol():
    rows = [
        {
            "protocol_sha256": "0" * 64,
            "arm": "R",
            "item_index": 0,
            "planted": True,
            "detected": False,
            "candidates": 1,
            "confirmed": 0,
        }
    ]
    with pytest.raises(SystemExit):
        ce.score(rows)


def test_score_reports_not_run_arms_and_does_not_invent_criteria():
    result = ce.score([])
    assert result["arms"]["P"]["status"] == "not run"
    assert result["criteria"] == {}
