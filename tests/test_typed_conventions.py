"""Typed conventions compared by meaning (ADR-DISCOVERY-087)."""

import pytest

from python.discovery import typed_conventions as tc


def test_untyped_texts_match_only_when_equal_after_normalization():
    assert tc.compare("Outward  normal", "outward normal")["outcome"] == tc.MATCH
    out = tc.compare("outward normal", "the normal points out of the domain")
    assert out["outcome"] == tc.UNCOMPARED and not out["items"]


def test_fields_decide_and_name_the_differing_field():
    cited = {"text": "a", "fields": {"normal": "outward", "branches": "matching"}}
    same = tc.compare(cited, {"fields": {"normal": "Outward"}})
    assert same["outcome"] == tc.MATCH
    assert same["unspecified"] == ["field branches (citing side silent)"]
    other = tc.compare(cited, {"fields": {"branches": "opposite"}})
    assert other["outcome"] == tc.MISMATCH
    assert other["items"][0]["item"] == "field branches"


def test_sign_formulas_compare_over_the_declared_ranges():
    cited = {"signs": {"s": "(-1)**(k-1)"}, "params": {"k": [1, 8]}}
    assert tc.compare(cited, {"signs": {"s": "-(-1)**k"}})["outcome"] == tc.MATCH
    out = tc.compare(cited, {"signs": {"s": "(-1)**k"}})
    assert out["outcome"] == tc.MISMATCH
    assert out["items"][0]["counterexample"] == {"at": {"k": 1}, "cited": 1, "citing": -1}
    assert tc.compare({"signs": {"s": "(-1)**(k*k)"}}, {"signs": {"s": "(-1)**k"}})["outcome"] == tc.MATCH


def test_formula_limits_are_non_verdicts_not_answers():
    big = {"signs": {"s": "a+b+c+d"}, "params": {n: [0, 40] for n in "abcd"}}
    assert tc.compare(big, {"signs": {"s": "d+c+b+a"}})["items"][0]["outcome"] == tc.UNCOMPARED
    assert tc.compare({"signs": {"s": "2**k"}}, {"signs": {"s": "1//(k-k)"}})["outcome"] == tc.UNCOMPARED
    huge = {"signs": {"s": "2**(10**9)"}}
    assert tc.compare(huge, huge)["outcome"] == tc.UNCOMPARED


@pytest.mark.parametrize(
    "value",
    [
        {"signs": {"s": "__import__('os')"}},
        {"signs": {"s": "1.5"}},
        {"fields": {"a": [1]}},
        {"params": {"k": [3, 1]}},
        {"colour": "red"},
    ],
)
def test_malformed_or_unsafe_values_are_refused(value):
    with pytest.raises(tc.ConventionError):
        out = tc.validate(value)
        tc.compare(out, out)


def test_describe_is_one_line():
    line = tc.describe({"text": "t", "fields": {"a": "x"}, "signs": {"s": "-1"}})
    assert line == "t; a=x; s: -1"
