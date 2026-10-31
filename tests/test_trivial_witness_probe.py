"""Tests for the trivial-witness / vacuity probe of Comparator statements (ADR-DISCOVERY-070)."""

import json
from pathlib import Path

import pytest

from python.discovery import trivial_witness_probe as probe

DATA = Path(__file__).resolve().parents[1] / "examples" / "openai-math-coverage" / "vacuity_probe.json"

SOURCE = """import Mathlib

namespace OAI

namespace Toy

def Good (n : ℕ) : Prop := 0 < n

def MainStatement : Prop :=
  ∀ (n : ℕ), 3 ≤ n → ∀ t : ℝ, -2 < t → t < 2 / 3 → Good n

theorem main : MainStatement := by
  sorry

/-- A target with binders. -/
theorem bounded (n k : ℕ) (hn : 3 ≤ n) (hk : 1 ≤ k) : Good n := by
  sorry

end Toy

end OAI
"""


def test_hypothesis_atoms_read_binders_antecedents_and_bounded_foralls():
    atoms = probe.hypothesis_atoms("theorem t (n : ℕ) (hn : 3 ≤ n) : ∀ ε > 0, ∀ p : ℝ, 2 ≤ p → True")
    assert ("n", ">=", "3") in atoms and ("ε", ">", "0") in atoms and ("p", ">=", "2") in atoms


def test_negative_bounds_and_subtraction_are_not_misread():
    # Regression: `-2 < t → t < 2 / 3` once lost the sign and gave a false clash t > 2, t < 2/3.
    assert probe.hypothesis_atoms("∀ t : ℝ, -2 < t → t < 2 / 3 → P t") == [("t", ">", "-2"), ("t", "<", "2/3")]
    # `n - 1 < x` bounds an expression, not the letter x.
    assert probe.hypothesis_atoms("∀ x : ℝ, n - 1 < x → P x") == []


def test_arithmetic_check_verdicts():
    assert probe.arithmetic_check("(n : ℕ) (hn : 3 ≤ n) (β : ℝ) (hb : 0 < β)")["verdict"] == "SATISFIABLE"
    clash = probe.arithmetic_check("(n : ℕ) (h1 : 3 ≤ n) (h2 : n < 2)")
    assert clash["verdict"] == "UNSAT_CANDIDATE" and set(clash["clash"]) == {"n >= 3", "n < 2"}
    # Between 2 and 3 there is a real but no natural number.
    assert probe.arithmetic_check("(n : ℕ) (h1 : 2 < n) (h2 : n < 3)")["verdict"] == "UNSAT_CANDIDATE"
    assert probe.arithmetic_check("(x : ℝ) (h1 : 2 < x) (h2 : x < 3)")["verdict"] == "SATISFIABLE"
    assert probe.arithmetic_check("(n : ℕ) (h : n < 0)")["verdict"] == "UNSAT_CANDIDATE"  # ℕ is nonnegative.
    assert probe.arithmetic_check("theorem t : True")["verdict"] == "NO_ATOMS"


def test_expanded_statement_unfolds_the_prop_definition():
    text = probe.expanded_statement(SOURCE, "main")
    assert "def MainStatement" in text
    assert probe.arithmetic_check(text)["verdict"] == "SATISFIABLE"


def test_binders_and_type():
    binders, type_ = probe.binders_and_type("theorem bounded (n k : ℕ) (hn : 3 ≤ n) : Good n := by\n  sorry")
    assert binders == "(n k : ℕ) (hn : 3 ≤ n)" and type_ == "Good n"
    assert probe.binders_and_type("theorem main : MainStatement := by sorry") == ("", "MainStatement")
    assert probe.binders_and_type("theorem u.{v} : P.{v} := by sorry") == ("", "P.{v}")


def test_cheap_tactic_probes():
    probes = probe.cheap_tactic_probes(SOURCE, "Toy.lean", ["OAI.Toy.main", "OAI.Toy.bounded"])
    assert [p.probe_id for p in probes] == ["Toy:main:trivial", "Toy:bounded:trivial", "Toy:bounded:inconsistent"]
    main = probes[0].text
    assert "theorem main : MainStatement := by\n  set_option maxHeartbeats" in main
    assert "| aesop" in main and "#print axioms main" in main
    assert main.count("sorry") == 1  # Only the other target keeps its sorry.
    inconsistent = probes[2]
    assert "theorem bounded_probe_inconsistent (n k : ℕ) (hn : 3 ≤ n) (hk : 1 ≤ k) : False := by" in inconsistent.text
    assert inconsistent.declaration == "bounded_probe_inconsistent"
    assert all(p.module_path.startswith("ComparatorChallenges/Probes/") for p in probes)


def test_parse_lean_output():
    ok = "'OAI.Toy.main' depends on axioms: [propext, Classical.choice, Quot.sound]"
    assert probe.parse_lean_output(ok, "main") == probe.LeanOutcome.PROVED
    assert probe.parse_lean_output("'OAI.Toy.main' does not depend on any axioms", "main") == probe.LeanOutcome.PROVED
    sorry = "warning: declaration uses 'sorry'\n'OAI.Toy.main' depends on axioms: [sorryAx]"
    assert probe.parse_lean_output(sorry, "main") == probe.LeanOutcome.NOT_PROVED
    error = "Probes/x.lean:12:4: error: unsolved goals\n'OAI.Toy.main' depends on axioms: [propext]"
    assert probe.parse_lean_output(error, "main") == probe.LeanOutcome.NOT_PROVED
    assert probe.parse_lean_output("", "main") == probe.LeanOutcome.NOT_PROVED


def test_classical_on_degenerate_case_files():
    source = "namespace OAI\nnamespace ClassicalON\ndef X : Prop := True\nend ClassicalON\nend OAI\n"
    files = probe.degenerate_probe_files(probe.CLASSICAL_ON, source)
    assert [f.declaration for f in files] == ["probe_degenerate_implies_target", "probe_law_is_probability"]
    for f in files:
        assert f.text.index(f"theorem {f.declaration}") < f.text.index("end ClassicalON")
        assert f"#print axioms {f.declaration}" in f.text
    assert set(probe.CLASSICAL_ON.expected.values()) == {"PROVED"}


@pytest.mark.skipif(not DATA.exists(), reason="probe output not built")
def test_committed_probe_output():
    data = json.loads(DATA.read_text(encoding="utf-8"))
    stage1 = data["stage1_arithmetic"]
    assert len(stage1["targets"]) == 546
    assert stage1["summary"].get("UNSAT_CANDIDATE", 0) == 0
    lean = data["lean_probes"]
    assert sum(lean["summary"].values()) == len(lean["probes"])
    ids = {p["probe_id"] for p in lean["probes"]}
    assert "ClassicalON:main:trivial" in ids
    assert "215-classical-on-degenerate-measure:D1_degenerate_implies_target" in ids
    assert data["degenerate_cases"][0]["theorem"] == "OAI.ClassicalON.main"
