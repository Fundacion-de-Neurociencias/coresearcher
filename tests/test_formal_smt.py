"""Tests for the SMT back end of formal hypotheses and for consequence checking (ADR-DISCOVERY-060)."""

import random

import pytest

from python.discovery.formal_hypothesis import (
    ContentVerdict,
    FormalHypothesisError,
    Hypothesis,
    HypothesisEvaluator,
    Relation,
    Variable,
)

R = Variable("r", continuous=True, lower=0, upper=10)
S = Variable("s", continuous=True)
G = Variable("group", ("carrier", "non_carrier"))


def H(hid, claims, assumptions=(), scope=None, variables=(R,)):
    return Hypothesis(hid, list(variables), list(claims), list(assumptions), scope)


# --- continuous content -------------------------------------------------------


def test_continuous_hypothesis_uses_smt_and_reports_no_counts():
    report = HypothesisEvaluator.evaluate(H("F", ["r <= 5"]))
    assert report.backend == "smt"
    assert report.content_verdict == ContentVerdict.FALSIFIABLE
    assert report.omega_size is None and report.forbidden_states is None
    assert all(5 < s["r"] <= 10 for s in report.falsifier_examples)


def test_bounds_make_a_claim_unfalsifiable():
    assert HypothesisEvaluator.evaluate(H("U", ["r >= 0"])).content_verdict == ContentVerdict.UNFALSIFIABLE


def test_continuous_self_contradiction():
    report = HypothesisEvaluator.evaluate(H("C", ["r > 3", "r < 2"]))
    assert report.content_verdict == ContentVerdict.SELF_CONTRADICTORY


def test_continuous_vacuity_reports_minimal_conflicts():
    h = H("V", ["r == 1"], assumptions=["r >= 0", "r > 7", "r + 1 < 3"])
    report = HypothesisEvaluator.evaluate(h)
    assert report.content_verdict == ContentVerdict.VACUOUS
    assert report.conflicting_assumption_sets == [["r > 7", "r + 1 < 3"]]


def test_nonlinear_real_arithmetic_is_decided_exactly():
    # No real s satisfies s*s < 0, so the claim forbids nothing.
    assert HypothesisEvaluator.evaluate(H("N", ["s*s >= 0"], variables=(S,))).content_verdict == (
        ContentVerdict.UNFALSIFIABLE
    )
    # s**2 == 2 has irrational solutions; the falsifier search must still return numbers.
    report = HypothesisEvaluator.evaluate(H("I", ["s**2 != 2"], variables=(S,)))
    assert report.content_verdict == ContentVerdict.FALSIFIABLE
    assert all(abs(x["s"] ** 2 - 2) < 1e-9 for x in report.falsifier_examples)


def test_mixed_finite_and_continuous_scope():
    h = H("M", ["r >= 4"], scope="group == 'carrier'", variables=(R, G))
    report = HypothesisEvaluator.evaluate(h, [{"group": "carrier", "r": 2}, {"group": "non_carrier", "r": 2}, {"r": 2}])
    assert [c["observation_index"] for c in report.certain_counterexamples] == [0]
    assert [c["observation_index"] for c in report.possible_counterexamples] == [2]
    assert report.is_refuted


def test_observation_outside_bounds_is_rejected():
    with pytest.raises(FormalHypothesisError):
        HypothesisEvaluator.evaluate(H("B", ["r <= 5"]), [{"r": 11}])


def test_continuous_comparison():
    a, b = H("A", ["r <= 5"]), H("B", ["r <= 6"])
    assert HypothesisEvaluator.compare(a, b).relation == Relation.STRONGER
    assert HypothesisEvaluator.compare(a, H("A2", ["2*r <= 10"])).relation == Relation.EQUIVALENT
    assert HypothesisEvaluator.compare(a, H("C", ["r > 5"])).relation == Relation.CONTRADICTORY
    report = HypothesisEvaluator.compare(H("L", ["r <= 5"]), H("U", ["r >= 3"]))
    assert report.relation == Relation.INCOMPARABLE
    assert {e["forbidden_by"] for e in report.discriminating_examples} == {"L", "U"}


def test_unsupported_constructs_fail_at_construction():
    with pytest.raises(FormalHypothesisError):
        H("P", ["r ** s > 1"], variables=(R, S))
    with pytest.raises(FormalHypothesisError):
        H("O", ["group < 'z'"], variables=(R, G))
    with pytest.raises(FormalHypothesisError):
        H("M", ["r % 2 == 0"])


def test_variable_validation():
    with pytest.raises(FormalHypothesisError):
        Variable("x", (1, 2), continuous=True)
    with pytest.raises(FormalHypothesisError):
        Variable("x", continuous=True, lower=3, upper=1)
    with pytest.raises(FormalHypothesisError):
        Variable("x", (1, 2), lower=0)
    with pytest.raises(FormalHypothesisError):
        HypothesisEvaluator.evaluate(H("E", ["r <= 5"]), backend="enumeration")


# --- consequences ---------------------------------------------------------------


def test_entailed_consequence_follows_from_claims():
    h = H("E", ["r*r >= 2"])
    report = HypothesisEvaluator.entails(h, "r > 1.4")
    assert report.entailed and report.follows_from_claims and not report.vacuous


def test_non_entailed_consequence_has_counterexamples():
    report = HypothesisEvaluator.entails(H("E", ["r*r >= 2"]), "r > 1.5")
    assert not report.entailed
    assert all(2 <= s["r"] ** 2 + 1e-12 and s["r"] <= 1.5 for s in report.counterexamples)


def test_consequence_implied_by_bounds_alone_does_not_follow_from_claims():
    report = HypothesisEvaluator.entails(H("E", ["r <= 5"]), "r >= 0")
    assert report.entailed and not report.follows_from_claims


def test_consequence_of_contradictory_hypothesis_is_vacuous():
    report = HypothesisEvaluator.entails(H("C", ["r > 3", "r < 2"]), "r == 100")
    assert report.entailed and report.vacuous and not report.follows_from_claims


def test_finite_consequence_by_enumeration():
    x = Variable("x", (0, 1, 2, 3))
    report = HypothesisEvaluator.entails(H("F", ["x <= 1"], variables=(x,)), "x < 2")
    assert report.backend == "enumeration" and report.entailed and report.follows_from_claims


# --- cross-check: SMT and enumeration agree on finite hypotheses -------------------


def _random_hypothesis(rng, hid, variables):
    names = [v.name for v in variables]

    def atom():
        a, b = rng.sample(names, 2)
        op = rng.choice(["<", "<=", "==", "!=", ">", ">="])
        return rng.choice(
            [
                f"{a} {op} {rng.randint(-1, 3)}",
                f"{a} + {b} {op} {rng.randint(0, 5)}",
                f"2*{a} {op} {b}",
                f"{a} in ({rng.randint(-1, 2)}, {rng.randint(0, 3)})",
                f"{a} * {b} not in (0, 2)",
            ]
        )

    def predicate():
        return rng.choice([atom(), f"{atom()} or {atom()}", f"not ({atom()})", f"{atom()} and {atom()}"])

    return Hypothesis(
        hid,
        list(variables),
        [predicate() for _ in range(rng.randint(1, 2))],
        [predicate() for _ in range(rng.randint(0, 3))],
        predicate() if rng.random() < 0.5 else None,
    )


def test_backends_agree_on_random_finite_hypotheses():
    rng = random.Random(20261015)
    variables = (Variable("a", (0, 1, 2, 3)), Variable("b", (-1, 0, 2)), Variable("c", (0, 1)))
    for i in range(60):
        h = _random_hypothesis(rng, f"H{i}", variables)
        k = _random_hypothesis(rng, f"K{i}", variables)
        obs = [{"a": rng.choice((0, 1, 2, 3))}, {"a": 1, "b": 0, "c": 1}]
        e = HypothesisEvaluator.evaluate(h, obs, backend="enumeration")
        s = HypothesisEvaluator.evaluate(h, obs, backend="smt")
        assert e.content_verdict == s.content_verdict, h
        assert sorted(map(sorted, e.conflicting_assumption_sets)) == sorted(map(sorted, s.conflicting_assumption_sets))
        assert sorted(e.claims_with_content) == sorted(s.claims_with_content)
        for kind in ("certain_counterexamples", "possible_counterexamples"):
            ce, cs = getattr(e, kind), getattr(s, kind)
            assert [r["observation_index"] for r in ce] == [r["observation_index"] for r in cs], (h, kind)
            assert [r["violated_claims"] for r in ce] == [r["violated_claims"] for r in cs], (h, kind)
        assert all(h.forbids(state) for state in s.falsifier_examples)
        rel_e = HypothesisEvaluator.compare(h, k, backend="enumeration").relation
        rel_s = HypothesisEvaluator.compare(h, k, backend="smt").relation
        assert rel_e == rel_s, (h, k)
        consequence = k.claims[0]
        ent_e = HypothesisEvaluator.entails(h, consequence, backend="enumeration")
        ent_s = HypothesisEvaluator.entails(h, consequence, backend="smt")
        assert (ent_e.entailed, ent_e.follows_from_claims, ent_e.vacuous) == (
            ent_s.entailed,
            ent_s.follows_from_claims,
            ent_s.vacuous,
        )


def test_backends_agree_with_string_variables():
    group = Variable("group", ("carrier", "non_carrier", "unknown"))
    level = Variable("level", (0, 1, 2))
    h = Hypothesis(
        "S",
        [group, level],
        ["level >= 1"],
        ["group in ('carrier', 'unknown')"],
        "group != 'unknown'",
    )
    e = HypothesisEvaluator.evaluate(h, backend="enumeration")
    s = HypothesisEvaluator.evaluate(h, backend="smt")
    assert e.content_verdict == s.content_verdict == ContentVerdict.FALSIFIABLE
    assert {tuple(sorted(x.items())) for x in s.falsifier_examples} == {(("group", "carrier"), ("level", 0))}


# --- Lean export ------------------------------------------------------------------


def test_lean_theorem_states_premises_and_goal():
    from python.discovery.formal_lean import consequence_theorem

    k = Variable("k", (1, 2))
    h = Hypothesis("H-1", [R, k], ["r*r >= 2*k"], ["k in (1, 2)"], "r != 3.5")
    text = consequence_theorem(h, "r > 1.4")
    assert "theorem H_1_entails (r : ℝ) (k : ℝ)" in text
    assert "((0 : ℝ) ≤ r)" not in text and "(0 : ℝ) ≤ r" in text and "r ≤ (10 : ℝ)" in text
    assert "(k = (1 : ℝ) ∨ k = (2 : ℝ))" in text
    assert "(r ≠ (7/2 : ℝ))" in text
    assert "((r * r) ≥ ((2 : ℝ) * k))" in text
    assert "    (r > (7/5 : ℝ)) := by\n" in text
    assert "NOT_KERNEL_CHECKED" in text


def test_lean_default_tactic_follows_goal_shape():
    """The script splits premises, then proves the goal by its shape (checked against Lean v4.35 + Mathlib)."""
    from python.discovery.formal_lean import consequence_theorem

    k = Variable("k", (1, 2))
    tactic = consequence_theorem(H("T", ["r >= 3 * k"], variables=(R, k)), "r >= 3").split(":= by\n", 1)[1]
    assert tactic.splitlines()[0] == "  try casesm* _ ∧ _, _ ∨ _"
    conj = consequence_theorem(H("T", ["r > 2"]), "r > 1 and r < 11")
    assert "refine ⟨?_, ?_⟩" in conj and conj.count("(focus (") == 2 and "(by " not in conj
    roots = consequence_theorem(H("T", ["r*r - 3*r + 2 == 0"]), "r in (1, 2)")
    assert "(left; " in roots and "(right; " in roots
    assert "refine (mul_ne_zero (sub_ne_zero.mpr hne0) (sub_ne_zero.mpr hne1)) ?_" in roots
    mixed = consequence_theorem(H("T", ["r > 2"]), "r > 5 or r > 1")
    assert "mul_ne_zero" not in mixed and "simp only [not_or, not_and_or, not_le, not_lt] at hne" in mixed
    assert "(intro hc; " in consequence_theorem(H("T", ["r > 2"]), "r != 1")
    assert "push_neg" not in roots + mixed
    custom = consequence_theorem(H("T", ["r > 2"]), "r > 1", tactic="linarith")
    assert custom.endswith(":= by\n  linarith\n")


def test_lean_export_rejects_string_variables():
    from python.discovery.formal_lean import consequence_theorem

    with pytest.raises(FormalHypothesisError):
        consequence_theorem(H("S", ["r >= 1"], variables=(R, G)), "r >= 0")


def test_api_continuous_evaluate_and_entails(api_client):
    hypothesis = {
        "hypothesis_id": "HYP-CONT",
        "variables": [{"name": "r", "continuous": True, "lower": 0, "upper": 10}],
        "claims": ["r*r >= 2"],
    }
    body = api_client.post("/api/hypotheses/evaluate", json={"hypothesis": hypothesis}).json()
    assert body["backend"] == "smt" and body["content_verdict"] == "FALSIFIABLE"

    resp = api_client.post(
        "/api/hypotheses/entails", json={"hypothesis": hypothesis, "consequence": "r > 1.4", "include_lean": True}
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["entailed"] is True and body["follows_from_claims"] is True
    assert body["lean_status"] == "NOT_KERNEL_CHECKED" and "theorem HYP_CONT_entails" in body["lean_theorem"]

    bad = {"hypothesis": hypothesis, "consequence": "r ** r > 1"}
    assert api_client.post("/api/hypotheses/entails", json=bad).status_code == 422


def test_smt_models_enumerate_distinct_states():
    from python.discovery import formal_smt

    h = Hypothesis("D", [Variable("x", (0, 1, 2))], ["x >= 0"])
    enc = formal_smt.encode(h)
    states = formal_smt.models(enc.domain, enc.table, 10)
    assert sorted(s["x"] for s in states) == [0, 1, 2]
    assert formal_smt.satisfiable(enc.domain, formal_smt.z3.BoolVal(False)) is None
