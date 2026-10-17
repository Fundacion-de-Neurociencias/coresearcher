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


# ---------------------------------------------------------------- phase 2

TARGET_LEAN = (
    "import Mathlib\n\nnamespace X\n\ndef f (n : ℕ) : ℕ := n + 1\n\n"
    "/-- The answer. -/\ntheorem target (n : ℕ) : f n > n := by\n  sorry\n\nend X\n"
)


def _target():
    name, stmt, start, end = fid.pilot.theorem_statement(TARGET_LEAN, "target")
    return {
        "family": "001",
        "theorem": name,
        "statement": stmt,
        "lean": TARGET_LEAN,
        "start": start,
        "end": end,
        "scope": "For every natural number n, f n exceeds n.",
        "title": "T",
        "challenge": "lean/X.lean",
    }


def test_build_context_removes_target_docstring_and_proof():
    context = fid.build_context(_target())
    assert "theorem target" not in context and "The answer" not in context and "sorry" not in context
    assert "def f (n : ℕ)" in context and context.rstrip().endswith("end X")
    assert fid.MARKER in context


def test_prompt_gives_name_prose_and_context_but_not_the_statement():
    user = fid.build_messages(_target())[1]["content"]
    assert "`target`" in user and "f n exceeds n" in user and "def f" in user
    assert "f n > n" not in user


def test_parse_candidate():
    reply = "Here it is:\n```lean\ntheorem target (n : ℕ) : n < f n := by sorry\n```\n"
    assert fid.parse_candidate(reply, "target") == ("parsed", "theorem target (n : ℕ) : n < f n")
    assert fid.parse_candidate("```lean\ntheorem other : True := by sorry\n```", "target")[0] == "wrong_name"
    assert fid.parse_candidate("I cannot do this.", "target") == ("no_theorem", None)


def test_screen_sheet_round_trip_and_score():
    targets = [_target(), {**_target(), "family": "002"}]
    sheet = fid.screen_sheet(targets, "A", "1581d4cbdd69a0faf34b2089614fe2a814316a6a")
    blank = {"verdict": None, "note": "", "wrapper": False}
    assert fid.parse_sheet(sheet) == {"001": blank, "002": blank}
    a = sheet.replace("- [ ] determined", "- [x] determined")
    b = a.replace("## F002: T", "## F002: T", 1)
    b = b[: b.index("## F002")] + b[b.index("## F002") :].replace(
        "- [x] determined\n- [ ] underdetermined", "- [ ] determined\n- [X] underdetermined"
    )
    b = b.replace("Note: \n", "Note: constant not in the prose\n", 1)
    assert fid.parse_sheet(b)["002"]["verdict"] == "underdetermined"
    result = fid.screen_score({"A": a, "B": b})
    assert result["complete"] and result["determined"] == ["001"] and result["agreement"] == 0.5
    assert fid.screen_score({"A": sheet, "B": b}) == {"complete": False, "missing": ["A:F001", "A:F002"]}


def test_cohen_kappa():
    assert fid.cohen_kappa(["determined", "underdetermined"] * 2, ["determined", "underdetermined"] * 2) == 1.0
    assert fid.cohen_kappa(["determined"] * 4, ["determined"] * 4) is None


class FakeClient:
    model = "fake:1b"
    base_url = "http://localhost:11434/v1"

    def __init__(self, reply):
        self.reply, self.calls = reply, []

    def complete(self, messages, temperature=0.0, seed=0):
        self.calls.append((temperature, seed))
        if isinstance(self.reply, Exception):
            raise self.reply
        return self.reply


def test_formalize_writes_raw_outputs_and_resumes(tmp_path, monkeypatch):
    import json

    monkeypatch.setattr(fid.oracle, "check_commit", lambda root: "c" * 40)
    monkeypatch.setattr(fid, "load_targets", lambda root: [_target()])
    out = tmp_path / "f.jsonl"
    fid.cmd_formalize(tmp_path, out, FakeClient(OSError("down")), False, None)
    rows = [json.loads(line) for line in out.read_text(encoding="utf-8").splitlines()]
    assert rows[0]["kind"] == "meta" and rows[0]["prompt_sha256"] == fid.prompt_sha256()
    assert rows[1]["status"] == "no_output" and rows[1]["transport_error"].startswith("OSError")
    client = FakeClient("```lean\ntheorem target (n : ℕ) : n < f n := by sorry\n```")
    fid.cmd_formalize(tmp_path, out, client, True, None)
    rows = [json.loads(line) for line in out.read_text(encoding="utf-8").splitlines()]
    assert client.calls == [(0.0, 0)] and rows[1]["status"] == "parsed"
    assert rows[1]["candidate"] == "theorem target (n : ℕ) : n < f n"


def test_wrapper_definition_detects_named_propositions():
    lean = "def MainStatement : Prop :=\n  ∀ n : ℕ, n = n\n\ntheorem main : MainStatement := by\n  sorry\n"
    name, stmt, start, end = fid.pilot.theorem_statement(lean, "main")
    target = {"statement": stmt, "lean": lean, "start": start, "end": end}
    assert fid.wrapper_definition(target) == "def MainStatement : Prop :=\n  ∀ n : ℕ, n = n"
    assert fid.wrapper_definition(_target()) is None
    sheet = fid.screen_sheet([{**_target(), **target, "theorem": name}], "A", "c" * 40)
    assert "Judge its definition" in sheet


def test_screen_score_keeps_wrappers_out_of_the_headline():
    lean = "def MainStatement : Prop :=\n  ∀ n : ℕ, n = n\n\ntheorem main : MainStatement := by\n  sorry\n"
    name, stmt, start, end = fid.pilot.theorem_statement(lean, "main")
    wrapper = {**_target(), "family": "002", "statement": stmt, "lean": lean, "start": start, "end": end}
    sheet = fid.screen_sheet([_target(), wrapper], "A", "c" * 40).replace("- [ ] determined", "- [x] determined")
    result = fid.screen_score({"A": sheet, "B": sheet})
    assert result["determined"] == ["001", "002"]
    assert result["headline"] == ["001"] and result["wrappers_reported_separately"] == ["002"]
    assert [r["wrapper"] for r in result["rows"]] == [False, True]


def test_auto_screen_marks_wrappers_and_numeric_anchoring():
    anchored = {**_target(), "statement": "theorem t (n : ℕ) : n ^ 2 < 7 * n + 1", "scope": "below 7 n"}
    loose = {**anchored, "family": "002", "scope": "below some multiple of n"}
    result = fid.auto_screen([anchored, loose])
    assert result["headline"] == ["001", "002"] and result["headline_anchored"] == ["001"]
    assert result["rows"][1]["missing"] == ["7"]
