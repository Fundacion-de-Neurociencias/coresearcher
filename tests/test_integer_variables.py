"""Integer variables with optional bounds, decided by z3 over the integers (ADR-DISCOVERY-090)."""

import pytest

from python.discovery import cited_registry as cr
from python.discovery.formal_hypothesis import FormalHypothesisError, HypothesisEvaluator, hypothesis_from_dict


def _context(assumptions):
    return hypothesis_from_dict(
        {"variables": [{"name": "n", "integer": True, "lower": 0}], "claims": ["true"], "assumptions": assumptions}
    )


def test_unbounded_integer_entailment_uses_parity_and_bounds():
    assert not HypothesisEvaluator.entails(_context(["n % 2 == 0", "n >= 2"]), "n > 2").entailed
    assert HypothesisEvaluator.entails(_context(["n % 2 == 0", "n >= 3"]), "n > 2").entailed
    assert HypothesisEvaluator.entails(_context(["n // 2 >= 2"]), "n >= 4").entailed


def test_counterexample_is_an_integer():
    report = HypothesisEvaluator.entails(_context(["n % 2 == 0", "n >= 2"]), "n > 2").to_dict()
    assert report["counterexamples"][0] == {"n": 2}


def test_integer_round_trip_and_validation():
    h = _context([])
    assert h.variables[0].integer and h.variables[0].continuous
    with pytest.raises(FormalHypothesisError):
        hypothesis_from_dict({"variables": [{"name": "n", "integer": True, "lower": 0.5}], "claims": ["true"]})
    with pytest.raises(FormalHypothesisError):
        HypothesisEvaluator.entails(_context(["n % k == 0"]), "n > 0")  # undeclared k


def test_cited_hypothesis_on_an_unbounded_integer_context(tmp_path):
    """The representative-range artefact: with 0..12 an unbounded n gave n = 0 as a counterexample to n > 2."""
    reg = cr.Registry(tmp_path / "r.json")
    entry = reg.register(
        {"id": "dim", "source": "s", "statement": "t", "hypotheses": [{"text": "n > 2", "formal": "n > 2"}]}
    )
    variables = [{"name": "n", "integer": True}]
    even = cr.cite_check(entry, {"variables": variables, "assumptions": ["n % 2 == 0", "n >= 4"]})
    assert even["hypotheses"][0]["outcome"] == cr.DISCHARGED
    open_n = cr.cite_check(entry, {"variables": variables, "assumptions": ["n % 2 == 0"]})
    assert open_n["hypotheses"][0]["outcome"] == cr.NOT_DISCHARGED
