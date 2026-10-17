"""Tests for the parts of the Lean fidelity auditor that need no Lean (LEAN_FIDELITY_AUDITOR_PLAN.md)."""

import importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
_spec = importlib.util.spec_from_file_location(
    "openai_math_lean_fidelity", ROOT / "scripts/benchmarks/openai_math_lean_fidelity.py"
)
fid = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(fid)

LEAN = "import Mathlib\n\ntheorem t (n : ℕ) :\n    thresholdValue (k := n) ≤ 1 := by\n  sorry\n"
PAIR = {"theorem": "t", "statement": "theorem t (n : ℕ) :\n    thresholdValue (k "}


def test_extraction_check_passes_on_named_argument():
    row = fid.extraction_check(PAIR, LEAN)
    assert row["ok"] and row["same_theorem"] and row["balanced"] and row["found_once"]
    assert row["matches_frozen_statement"] is False


def test_extraction_check_fails_on_wrong_theorem_name():
    assert not fid.extraction_check({**PAIR, "theorem": "other"}, LEAN)["ok"]


def test_extraction_check_fails_without_theorem():
    assert fid.extraction_check(PAIR, "import Mathlib\n") == {"ok": False, "reason": "no theorem found"}


def test_elaboration_errors_ignore_sorry_warnings():
    output = (
        "ComparatorChallenges/X.lean:3:8: warning: declaration uses 'sorry'\n"
        "ComparatorChallenges/X.lean:9:2: error: unknown identifier 'foo'\n"
    )
    assert fid.elaboration_errors(output) == ["ComparatorChallenges/X.lean:9:2: error: unknown identifier 'foo'"]


def test_lean_version_line_skips_lake_warnings():
    output = "warning: iut: repository has local changes\nLean (version 4.34.1, x86_64-w64-windows-gnu, Release)\n"
    assert fid.lean_version_line(output) == "Lean (version 4.34.1, x86_64-w64-windows-gnu, Release)"


# ---------------------------------------------------------------- phase 1


def test_statement_prop_closes_binders_over_conclusion():
    assert fid.statement_prop("theorem t (n : ℕ) (hn : 0 < n) :\n    n ≠ 0 ") == "∀ (n : ℕ) (hn : 0 < n), n ≠ 0"
    assert fid.statement_prop("theorem t :\n    ∀ n : ℕ, n = n ") == "∀ n : ℕ, n = n"


def test_rename_is_alpha_equivalent_and_keeps_fields_and_named_arguments():
    out = fid._rename("∀ (k : ℕ) (S : Input k), f (k := k) S.k ∧ k = k")
    assert out == "∀ (k_r : ℕ) (S_r : Input k_r), f (k := k_r) S_r.k ∧ k_r = k_r"


def test_flip_lt_only_on_atomic_operands():
    assert fid._flip_lt("∀ a b : ℕ, 1 ≤ a → a < b") == "∀ a b : ℕ, a ≥ 1 → a < b"
    assert fid._flip_lt("f x < y") is None


def test_swap_respects_precedence():
    assert fid._swap("∀ x : ℕ, (A x ∧ B ∧ C)") == "∀ x : ℕ, ((B ∧ C) ∧ (A x))"
    assert fid._swap("A ∧ B ∨ C") == "((C) ∨ (A ∧ B))"
    assert fid._swap("A ∧ B → C") is None
    # A quantifier inside the body extends to its end, so the split is refused rather than risked.
    assert fid._swap("∃ n, P n ∧ ∀ m, Q m ∧ R") is None


def test_curry_needs_two_premises():
    assert fid._curry("∀ a : ℕ, 1 ≤ a → a < 2 → P a") == "∀ a : ℕ, (((1 ≤ a) ∧ (a < 2)) → P a)"
    assert fid._curry("A → B") is None
    assert fid._curry("A ↔ B → C → D") is None


def test_insertion_point_keeps_docstring_attributes_and_modifiers_with_theorem():
    lean = "def x := 1\n\n/-- doc -/\n@[simp]\nprivate theorem t : x = 1 := by\n  sorry\n"
    at = fid._insertion_point(lean, lean.index("theorem"))
    assert lean[at:].startswith("/-- doc -/")


def test_check_file_line_ranges_point_at_the_blocks():
    lean = "import Mathlib\n\ntheorem t : 1 = 1 := by\n  sorry\n"
    text, ranges = fid.build_check_file(lean, lean.index("theorem"), [("c1", "1 = 1", "1 = 1")])
    lines = text.splitlines()
    assert lines[ranges[0]["first_line"] - 1] == "-- fidelity check c1"
    assert lines[ranges[0]["proof_line"] - 1].strip() == ":= by"
    assert text.endswith(lean[lean.index("theorem") :])


def test_classify_and_trust():
    ranges = [
        {"id": "a", "first_line": 3, "proof_line": 7, "last_line": 11},
        {"id": "b", "first_line": 11, "proof_line": 15, "last_line": 19},
        {"id": "s", "first_line": 19, "proof_line": 23, "last_line": 27},
    ]
    output = (
        "C:/x/F1.lean:5:4: error: unknown identifier 'foo'\n"
        "C:/x/F1.lean:23:2: error: simp made no progress\n"
        "C:/x/F1.lean:30:0: warning: declaration uses 'sorry'\n"
    )
    outcomes, outside = fid.classify(output, ranges)
    assert [outcomes[k]["outcome"] for k in "abs"] == ["invalid", "proved", "not_shown"]
    assert outside == [] and fid.trusted(outcomes, outside, "s") is None
    outcomes, outside = fid.classify(output + "C:/x/F1.lean:1:0: error: unknown module\n", ranges)
    assert fid.trusted(outcomes, outside, "s").startswith("errors outside")
    outcomes, outside = fid.classify("", ranges)
    assert fid.trusted(outcomes, outside, "s") == "the sentinel check did not fail as expected"
