"""Tests for formal hypotheses over a finite state space (ADR-DISCOVERY-059)."""

import pytest

from python.discovery.formal_hypothesis import (
    ContentVerdict,
    FormalHypothesisError,
    Hypothesis,
    HypothesisEvaluator,
    Relation,
    Variable,
)

X = Variable("x", (0, 1, 2, 3))
G = Variable("group", ("carrier", "non_carrier"))
D = Variable("decline", ("fast", "slow"))


def H(hid, claims, assumptions=(), scope=None, variables=(X,)):
    return Hypothesis(hid, list(variables), list(claims), list(assumptions), scope)


# --- content ----------------------------------------------------------------


def test_vacuous_when_assumptions_cannot_hold_together():
    report = HypothesisEvaluator.evaluate(H("V", ["x == 1"], assumptions=["x > 2", "x < 1"]))
    assert report.content_verdict == ContentVerdict.VACUOUS
    assert report.applicable_states == 0
    assert report.conflicting_assumption_sets == [["x > 2", "x < 1"]]


def test_minimal_conflicting_sets_exclude_innocent_assumptions():
    h = H("M", ["x == 1"], assumptions=["x >= 0", "x > 2", "x < 1"])
    sets = HypothesisEvaluator.evaluate(h).conflicting_assumption_sets
    assert sets == [["x > 2", "x < 1"]]  # 'x >= 0' is not part of the conflict


def test_unfalsifiable_claim_forbids_nothing():
    report = HypothesisEvaluator.evaluate(H("U", ["x >= 0"]))
    assert report.content_verdict == ContentVerdict.UNFALSIFIABLE
    assert report.forbidden_states == 0


def test_self_contradictory_claims():
    report = HypothesisEvaluator.evaluate(H("C", ["x == 1", "x == 2"]))
    assert report.content_verdict == ContentVerdict.SELF_CONTRADICTORY


def test_falsifiable_hypothesis_reports_exact_exclusion():
    report = HypothesisEvaluator.evaluate(H("F", ["x <= 1"], scope="x != 0"))
    assert report.content_verdict == ContentVerdict.FALSIFIABLE
    assert report.applicable_states == 3  # x in {1, 2, 3}
    assert report.forbidden_states == 2  # x in {2, 3}
    assert report.excluded_fraction_of_omega == pytest.approx(2 / 4)
    assert {s["x"] for s in report.falsifier_examples} == {2, 3}


# --- confrontation with observations -----------------------------------------


def test_certain_counterexample_refutes():
    h = H("R", ["decline == 'slow'"], assumptions=["group == 'non_carrier'"], variables=(G, D))
    report = HypothesisEvaluator.evaluate(h, observations=[{"group": "non_carrier", "decline": "fast"}])
    assert report.is_refuted is True
    record = report.certain_counterexamples[0]
    assert record["violated_claims"] == ["decline == 'slow'"]
    assert record["auxiliaries_in_question"] == ["group == 'non_carrier'"]


def test_observation_outside_assumptions_does_not_refute():
    h = H("R", ["decline == 'slow'"], assumptions=["group == 'non_carrier'"], variables=(G, D))
    report = HypothesisEvaluator.evaluate(h, observations=[{"group": "carrier", "decline": "fast"}])
    assert report.is_refuted is False
    assert report.certain_counterexamples == [] and report.possible_counterexamples == []


def test_partial_observation_is_only_a_possible_counterexample():
    h = H("R", ["decline == 'slow'"], assumptions=["group == 'non_carrier'"], variables=(G, D))
    report = HypothesisEvaluator.evaluate(h, observations=[{"decline": "fast"}])  # group unknown
    assert report.is_refuted is False
    assert len(report.possible_counterexamples) == 1
    assert report.possible_counterexamples[0]["forbidden_completions"] == 1
    assert report.possible_counterexamples[0]["total_completions"] == 2


def test_observation_outside_domain_is_rejected():
    with pytest.raises(FormalHypothesisError):
        HypothesisEvaluator.evaluate(H("F", ["x <= 1"]), observations=[{"x": 9}])


# --- comparison --------------------------------------------------------------


def test_equivalent_formulations():
    report = HypothesisEvaluator.compare(H("A", ["x > 1"]), H("B", ["x >= 2"]))
    assert report.relation == Relation.EQUIVALENT


def test_stronger_and_weaker():
    strong, weak = H("S", ["x <= 1"]), H("W", ["x <= 2"])
    assert HypothesisEvaluator.compare(strong, weak).relation == Relation.STRONGER
    assert HypothesisEvaluator.compare(weak, strong).relation == Relation.WEAKER


def test_incomparable_hypotheses_have_discriminating_states():
    report = HypothesisEvaluator.compare(H("A", ["x != 1"]), H("B", ["x != 2"]))
    assert report.relation == Relation.INCOMPARABLE
    assert {e["state"]["x"] for e in report.discriminating_examples} == {1, 2}


def test_contradictory_hypotheses():
    report = HypothesisEvaluator.compare(H("A", ["x <= 1"]), H("B", ["x >= 2"]))
    assert report.relation == Relation.CONTRADICTORY


def test_comparison_requires_same_state_space():
    with pytest.raises(FormalHypothesisError):
        HypothesisEvaluator.compare(H("A", ["x <= 1"]), H("B", ["group == 'carrier'"], variables=(G,)))


# --- safety and validation ---------------------------------------------------


@pytest.mark.parametrize(
    "expression",
    ["__import__('os').system('echo hi')", "x.__class__", "open('f')", "[i for i in (1, 2)]", "lambda: 1"],
)
def test_unsafe_expressions_are_rejected(expression):
    with pytest.raises(FormalHypothesisError):
        H("BAD", [expression])


def test_unknown_variable_is_rejected():
    with pytest.raises(FormalHypothesisError):
        H("BAD", ["y > 1"])


def test_arithmetic_error_is_reported_cleanly():
    with pytest.raises(FormalHypothesisError):
        HypothesisEvaluator.evaluate(H("Z", ["1 / x > 0"]))


# --- API ----------------------------------------------------------------------


def test_api_evaluate_and_compare(api_client):
    hypothesis = {
        "hypothesis_id": "HYP-API",
        "variables": [
            {"name": "group", "domain": ["carrier", "non_carrier"]},
            {"name": "decline", "domain": ["fast", "slow"]},
        ],
        "assumptions": ["group == 'non_carrier'"],
        "claims": ["decline == 'slow'"],
    }
    resp = api_client.post(
        "/api/hypotheses/evaluate",
        json={"hypothesis": hypothesis, "observations": [{"group": "non_carrier", "decline": "fast"}]},
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["content_verdict"] == "FALSIFIABLE"
    assert body["is_refuted"] is True

    bad = dict(hypothesis, claims=["__import__('os')"])
    assert api_client.post("/api/hypotheses/evaluate", json={"hypothesis": bad}).status_code == 422

    # Narrowing the assumption to the only forbidden case forbids the same state: equivalent hypotheses.
    narrow = dict(hypothesis, hypothesis_id="HYP-NARROW", assumptions=["group == 'non_carrier' and decline == 'fast'"])
    resp = api_client.post("/api/hypotheses/compare", json={"a": hypothesis, "b": narrow})
    assert resp.status_code == 200
    assert resp.json()["relation"] == "EQUIVALENT"
