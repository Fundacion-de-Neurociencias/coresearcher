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
