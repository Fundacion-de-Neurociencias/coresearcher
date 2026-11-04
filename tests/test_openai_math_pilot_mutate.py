"""Tests for the M3 and M5 mutation operators of the openai/math pilot.

The shapes are the three mutants that the Lean/Comparator oracle rejected only because they do not parse
(F231_M3, F243_M3, F277_M5; see docs/reference/benchmarks/LEAN_ORACLE_PROTOCOL.md).
"""

import importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
_spec = importlib.util.spec_from_file_location("openai_math_pilot", ROOT / "scripts/benchmarks/openai_math_pilot.py")
pilot = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(pilot)

# Family 231: the first ∀ carries instance binders; a later ∀ does not.
F231 = (
    "theorem finite_strongly_rayleigh_response :\n"
    "    ∀ (F : Type u_1) [Fintype F] [Nonempty F] (μ : ProbabilityMeasure (F → Bool)),\n"
    "      StronglyRayleighFinite μ →\n"
    "        (∀ (i j : F) (h : F → ℝ),\n"
    "          HasDerivAt (fun r : ℝ => tiltMean μ (coordinatePerturb h j r) i)\n"
    "            (tiltCovariance μ h i j) 0) "
)

# Family 243: the only ∀ carries instance binders.
F243 = (
    "theorem main :\n"
    "    (∀ (A B : Type) [Fintype A] [Fintype B] (S : Input A) (T : Input B),\n"
    "      S.Iso T → (S.query ↔ T.query)) ∧\n"
    "    OrdinaryPolynomialTime ∧\n"
    "    ¬ FullCPT.EvaluationDefinable (fun {_} [_] I => I.query) "
)

# Family 277: extraction stops at the ':=' of the named argument (k := ...), leaving '(k' open.
F277 = (
    "theorem threshold_parallel_repetition :\n"
    "    ∃ κ₀ : ℝ, 0 < κ₀ ∧\n"
    "      ∀ (k : ℕ), 1 ≤ k →\n"
    "        (∀ S : RepeatedStrategy x y a b k,\n"
    "          thresholdProbability G δ S ≤ Real.exp (-κ₀ * k)) ∧\n"
    "        thresholdValue (k "
)


def test_m3_skips_quantifier_with_instance_binders():
    m3 = pilot.mutate(F231)["M3"]
    assert "∀ (F : Type u_1) [Fintype F]" in m3
    assert "(∃ (i j : F) (h : F → ℝ)," in m3


def test_m3_absent_when_every_quantifier_has_instance_binders():
    assert "M3" not in pilot.mutate(F243)


def test_m3_skips_implicit_binders_and_unique_existence():
    stmt = "theorem t :\n    ∀ {n : ℕ}, ∃! m : ℕ, m = n "
    assert "M3" not in pilot.mutate(stmt)


def test_m3_still_flips_plain_binders():
    assert pilot.mutate(F277)["M3"].startswith("theorem threshold_parallel_repetition :\n    ∀ κ₀ : ℝ,")


def test_m5_absent_when_conclusion_is_unbalanced():
    assert "M5" not in pilot.mutate(F277)


def test_m5_wraps_balanced_multiline_conclusion():
    m5 = pilot.mutate(F243)["M5"]
    assert m5.startswith("theorem main : ¬ ((∀ (A B : Type)")
    assert pilot._balanced(m5)


def test_theorem_statement_ignores_named_argument_assign():
    lean = (
        "import Mathlib\n\n"
        "theorem threshold_parallel_repetition :\n"
        "    ∃ κ₀ : ℝ, 0 < κ₀ ∧\n"
        "        thresholdValue (k := k) G ≤ Real.exp (-κ₀) := by\n"
        "  sorry\n"
    )
    name, stmt, start, end = pilot.theorem_statement(lean)
    assert name == "threshold_parallel_repetition"
    assert stmt.endswith("thresholdValue (k := k) G ≤ Real.exp (-κ₀) ")
    assert lean[start:end] == stmt and lean[end:].startswith(":= by")
    assert "M5" in pilot.mutate(stmt) and pilot._balanced(pilot.mutate(stmt)["M5"])


def test_theorem_statement_ignores_binder_default_value():
    lean = "theorem t (n : ℕ := 3) : n = n := rfl\n"
    assert pilot.theorem_statement(lean)[1] == "theorem t (n : ℕ := 3) : n = n "


def test_theorem_statement_by_name_skips_helper_lemmas():
    lean = "theorem helper : 1 = 1 := by\n  rfl\n\ntheorem target (n : ℕ) : n = n := by\n  sorry\n"
    assert pilot.theorem_statement(lean)[0] == "helper"
    assert pilot.theorem_statement(lean, "target")[1] == "theorem target (n : ℕ) : n = n "
    assert pilot.challenge_target('{"theorem_names": ["OAI.X.target"]}') == "target"
    assert pilot.challenge_target(None) is None
