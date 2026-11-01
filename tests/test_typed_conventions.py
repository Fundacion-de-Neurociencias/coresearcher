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
    assert same["outcome"] == tc.PARTIAL  # ADR-088: a silent item keeps the comparison open
    assert same["unspecified"] == ["field branches (citing side silent)"]
    full = tc.compare(cited, {"fields": {"normal": "Outward", "branches": "matching"}})
    assert full["outcome"] == tc.MATCH
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


def test_where_restricts_the_comparison_to_the_shared_domain():
    """ADR-088: a counterexample outside the citing domain (n odd where the passage has n = 2k) is not a mismatch."""
    cited = {"signs": {"reversal_sign": "(-1)**(n+1)"}, "params": {"n": [2, 40]}}
    unconstrained = tc.compare(cited, {"signs": {"reversal_sign": "-1"}})
    assert unconstrained["outcome"] == tc.MISMATCH
    assert unconstrained["items"][0]["counterexample"]["at"] == {"n": 3}
    even = tc.compare(cited, {"signs": {"reversal_sign": "-1"}, "where": ["n % 2 == 0"]})
    assert even["outcome"] == tc.MATCH and even["items"][0]["points"] == 20
    empty = tc.compare(
        {"signs": {"s": "(-1)**n"}, "params": {"n": [0, 3]}}, {"signs": {"s": "(-1)**n"}, "params": {"n": [5, 9]}}
    )
    assert empty["outcome"] == tc.UNCOMPARED


def test_case_used_is_checked_against_the_cases_covered():
    cited = {"cases": {"homotopy_direction": ["forward", "reverse"]}, "fields": {"index": "whitney"}}
    covered = tc.compare(cited, {"case": {"homotopy_direction": "Reverse"}, "fields": {"index": "whitney"}})
    assert covered["outcome"] == tc.MATCH
    narrow = {"cases": {"homotopy_direction": ["forward"]}}
    out = tc.compare(narrow, {"case": {"homotopy_direction": "reverse"}})
    assert out["outcome"] == tc.MISMATCH and out["items"][0]["detail"].startswith("the cited result does not cover")
    silent = tc.compare({"text": "t"}, {"text": "u", "case": {"homotopy_direction": "reverse"}})
    assert silent["outcome"] == tc.UNCOMPARED
    assert silent["unspecified"] == ["case homotopy_direction (cited side lists no cases)"]


@pytest.mark.parametrize(
    "value",
    [{"where": ["n == 2 or __import__('os')"]}, {"where": ["n == 1.5"]}, {"cases": {"d": []}}, {"case": {"d": [1]}}],
)
def test_malformed_conditions_and_cases_are_refused(value):
    with pytest.raises(tc.ConventionError):
        tc.validate(value)
