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


def test_kernel_results_map_to_probe_outcomes():
    assert probe.outcome_from_kernel("PASS") == probe.LeanOutcome.PROVED
    assert probe.outcome_from_kernel("FAIL") == probe.LeanOutcome.NOT_PROVED
    assert probe.outcome_from_kernel("BLOCKED") == probe.LeanOutcome.BLOCKED
    assert "vacuity finding" in probe.meaning("trivial") and "D2" in probe.meaning("D1_degenerate_implies_target")


def _script():
    import importlib.util

    path = Path(__file__).resolve().parents[1] / "scripts" / "cases" / "trivial_witness_probe_report.py"
    spec = importlib.util.spec_from_file_location("trivial_witness_probe_report", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_report_folds_verified_kernel_records(tmp_path, monkeypatch):
    from python.discovery import kernel_records

    script = _script()
    assert script._probe_target("ClassicalON:main:trivial") == "openai-math-probe-classicalon-main-trivial"
    assert script._qualified({"theorem": "OAI.ClassicalON.main", "declaration": "probe_x"}) == "OAI.ClassicalON.probe_x"
    out = tmp_path / "vacuity_probe.json"
    out.write_text(
        json.dumps(
            {
                "lean_probes": {
                    "probes": [
                        {"probe_id": "T:main:trivial", "mode": "trivial", "outcome": "NOT_RUN"},
                        {"probe_id": "T:main:inconsistent", "mode": "inconsistent", "outcome": "NOT_RUN"},
                    ]
                }
            }
        ),
        encoding="utf-8",
    )
    monkeypatch.setattr(script, "OUT", out)
    records = tmp_path / "records"
    records.mkdir()
    log = "error-free\n'OAI.T.main' depends on axioms: [sorryAx]\n# kernel-check: exit_code=0\n"
    target = script._probe_target("T:main:trivial")
    record = kernel_records.build(
        target=target,
        kind="lean_file",
        source={"repository": "openai/math", "commit": "x", "path": "p"},
        file_sha256="0" * 64,
        toolchain="t",
        lean_version="v",
        mathlib_rev="m",
        theorems=["OAI.T.main"],
        log=log,
        kernel_log=f"{target}.log",
        wall_time_s=1.0,
        checked_by="local:test",
        date="2026-11-02T00:00:00Z",
        extra={"probe": {"probe_id": "T:main:trivial", "mode": "trivial"}},
    )
    (records / f"{target}.log").write_bytes(log.encode("utf-8"))
    (records / f"{target}.json").write_text(json.dumps(record), encoding="utf-8")
    script.report(records)
    data = json.loads(out.read_text(encoding="utf-8"))
    rows = {r["probe_id"]: r for r in data["lean_probes"]["probes"]}
    assert rows["T:main:trivial"]["kernel_result"] == "FAIL"  # sorryAx: the menu did not close the target.
    assert rows["T:main:trivial"]["outcome"] == "NOT_PROVED"
    assert rows["T:main:inconsistent"]["outcome"] == "NOT_RUN"
    assert data["lean_probes"]["summary"] == {"NOT_PROVED": 1, "NOT_RUN": 1}


def test_probe_generation_handles_term_mode_named_arguments_and_partial_imports():
    source = (
        "import Mathlib.Data.Finset.Basic\n\nnamespace OAI\nnamespace T\n\n"
        "theorem term_mode (n : ℕ) (h : Foo (n := n)) : Bar (n := n) :=\n  sorry\n\nend T\nend OAI\n"
    )
    trivial, inconsistent = probe.cheap_tactic_probes(source, "T.lean", ["OAI.T.term_mode"])
    assert ":=\n  by\n    set_option maxHeartbeats" in trivial.text  # Term-mode `:= sorry` gets a `by`.
    assert "aesop" not in trivial.text and "| simp_all" in trivial.text  # No Mathlib tactic library imported.
    assert "(n : ℕ) (h : Foo (n := n)) : False := by" in inconsistent.text  # `(n := n)` is not the body's `:=`.
    assert probe.binders_and_type("theorem t (h : Foo (n := n)) : Bar := by sorry") == ("(h : Foo (n := n))", "Bar")
    assert probe.menu_for("import Mathlib\n") == probe.TACTIC_MENU


PROBE_RECORDS = Path(__file__).resolve().parents[1] / "records" / "kernel" / "2026-11-03-probe-lenovo"


@pytest.mark.skipif(not PROBE_RECORDS.is_dir(), reason="probe records not committed")
def test_committed_probe_run():
    from python.discovery import kernel_records

    data = json.loads(DATA.read_text(encoding="utf-8"))
    rows = data["lean_probes"]["probes"]
    assert all(r["outcome"] != "NOT_RUN" for r in rows)
    # No target closed by a cheap tactic and no contradictory binders: no vacuity finding.
    assert not [r for r in rows if r["outcome"] == "PROVED" and not r["mode"].startswith("D")]
    # ClassicalON: the junk branch would make the target trivial (D1), and it cannot fire for n >= 3 (D2).
    for row in [r for r in rows if r["mode"].startswith("D")]:
        record = kernel_records.load(kernel_records.resolve(row["kernel_record"]))
        assert record["result"] == "PASS" and record["axioms"] == ["Classical.choice", "Quot.sound", "propext"]
    # A BLOCKED probe is a non-verdict: each says why, and each combined menu that was aborted was split.
    blocked = [r for r in rows if r["outcome"] == "BLOCKED"]
    assert blocked and all(r["reasons"] for r in blocked)
    split_parents = {r["split_of"] for r in rows if "split_of" in r}
    assert {r["probe_id"] for r in blocked if r["mode"] == "trivial"} <= split_parents
