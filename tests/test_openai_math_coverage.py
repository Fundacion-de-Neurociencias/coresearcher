"""Tests for the corpus-wide claim-vs-formal coverage map of openai/math (ADR-DISCOVERY-070)."""

import json
import re
from collections import Counter
from pathlib import Path

import pytest

from python.discovery import lean_junk_lint
from python.discovery import openai_math_coverage as cov

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "examples" / "openai-math-coverage"

CONTENTS = """# Mathematics manuscript collection

**002 result families.**

**001. A first result.** Proves the thing for every $`n\\ge2`$, e.g. in dimension two. It also gives a corollary. ([Lean](lean/docs/001.md))

&emsp;[First paper](preprints/First-paper/paper.pdf)

**002. A prose result.** Constructs an object. In particular, J. Smith's question has a negative answer.

&emsp;[Second paper](preprints/Second/main.pdf)
"""

OVERVIEW = r"""\newcommand{\resultentry}[4]{#1}
\begin{document}
\cataloguesection{Number theory}{1}
\resultentry{001}{A first result}{Proves the thing for every $n\ge2$, e.g.\ in dimension two. It also gives a {\em corollary}.}{\href{x}{y}}
\cataloguesection{Topology}{4}
\resultentry{002}{A prose result}{Constructs an object.}{\href{x}{y}}
"""

SCOPE = """# A first result

The following describes the scope of the Lean formalization related to the following accompanying paper(s):

- [First paper](../../preprints/First-paper/paper.pdf)

## Scope

The formalization proves the thing for every $n\\ge 2$.

The corollary is not included.

## Comparator links

| Result | Comparator statement |
| --- | --- |
| The thing | [First.lean](../ComparatorChallenges/First.lean#L7) |
| Helper | [First.lean](../ComparatorChallenges/First.lean) |
"""

LEAN = """import Mathlib

namespace OAI.First

def Good (n : ℕ) : Prop := 0 < n

/-- The thing, for every `n ≥ 2`. -/
theorem thing (n : ℕ) (hn : 2 ≤ n) : Good n := by
  sorry

theorem helper.{u} : True := by
  sorry

end OAI.First
"""

CONFIG = {"theorem_names": ["OAI.First.thing", "OAI.First.helper"]}


# ---------------------------------------------------------------------------
# Parsing
# ---------------------------------------------------------------------------


def test_parse_contents_reads_families_links_and_preprints():
    families = cov.parse_contents(CONTENTS)
    assert sorted(families) == ["001", "002"]
    first, second = families["001"], families["002"]
    assert first.title == "A first result" and first.lean_doc == "lean/docs/001.md"
    assert not first.summary.endswith(")") and "[Lean]" not in first.summary
    assert first.preprints == [{"title": "First paper", "path": "preprints/First-paper/paper.pdf"}]
    assert second.lean_doc is None


def test_parse_overview_handles_nested_braces_and_sections():
    overview = cov.parse_overview(OVERVIEW)
    assert overview["001"]["discipline"] == "Number theory"
    assert overview["002"]["discipline"] == "Topology"
    assert "{\\em corollary}" in overview["001"]["summary"]


def test_split_claims_masks_math_abbreviations_and_initials():
    families = cov.parse_contents(CONTENTS)
    assert cov.split_claims(families["001"].summary) == [
        "Proves the thing for every $`n\\ge2`$, e.g. in dimension two.",
        "It also gives a corollary.",
    ]
    assert len(cov.split_claims(families["002"].summary)) == 2  # "J. Smith" does not end a sentence.
    assert cov.split_claims("Holds for $`x=1. Y`$ always. Then more.") == ["Holds for $`x=1. Y`$ always.", "Then more."]


def test_parse_scope_doc_rows_keep_anchor_lines():
    doc = cov.parse_scope_doc(SCOPE)
    assert doc.title == "A first result" and doc.papers == ["First paper"]
    assert len(doc.scope_paragraphs) == 2
    assert doc.rows == [
        {"label": "The thing", "file": "First.lean", "line": 7},
        {"label": "Helper", "file": "First.lean", "line": None},
    ]


def test_comparator_targets_locate_theorems_universes_and_docstrings():
    targets = cov.comparator_targets(LEAN, CONFIG, "First.lean")
    by_name = {t.theorem: t for t in targets}
    thing, helper = by_name["OAI.First.thing"], by_name["OAI.First.helper"]
    assert thing.line == 8 and thing.docstring == "The thing, for every `n ≥ 2`."
    assert thing.statement.startswith("theorem thing (n : ℕ) (hn : 2 ≤ n) : Good n")
    assert "def Good" in thing.support
    assert helper.line == 11  # `theorem helper.{u}` is found although the name parses as "helper.".
    doc = cov.parse_scope_doc(SCOPE)
    assert [t.theorem for t in cov.targets_for_row(doc.rows[0], targets)] == ["OAI.First.thing"]  # Docstring.
    in_body = {"label": "x", "file": "First.lean", "line": 9}
    assert [t.theorem for t in cov.targets_for_row(in_body, targets)] == ["OAI.First.thing"]
    assert len(cov.targets_for_row(doc.rows[1], targets)) == 2  # No anchor: every target of the file.


def test_config_for_falls_back_to_main_json_in_a_subdirectory():
    configs = {"A.json": {}, "Sub/main.json": {}}
    assert cov.config_for("A.lean", configs) == "A.json"
    assert cov.config_for("Sub/Challenge.lean", configs) == "Sub/main.json"


def test_load_corpus_and_family_record_on_a_miniature(tmp_path):
    (tmp_path / "lean" / "docs").mkdir(parents=True)
    (tmp_path / "lean" / "ComparatorChallenges").mkdir()
    (tmp_path / "CONTENTS.md").write_text(CONTENTS, encoding="utf-8")
    (tmp_path / "overview.tex").write_text(OVERVIEW, encoding="utf-8")
    (tmp_path / "lean" / "docs" / "001.md").write_text(SCOPE, encoding="utf-8")
    (tmp_path / "lean" / "ComparatorChallenges" / "First.lean").write_text(LEAN, encoding="utf-8")
    (tmp_path / "lean" / "ComparatorChallenges" / "First.json").write_text(json.dumps(CONFIG), encoding="utf-8")
    (tmp_path / "lean" / "formalization.yaml").write_text(
        "status:\n  main_results:\n    - comparator_config: ComparatorChallenges/First.json\n"
        "      declaration: OAI.First.thing\n",
        encoding="utf-8",
    )
    corpus = cov.load_corpus(tmp_path)
    record = cov.family_record(corpus, "001")
    assert record["discipline"] == "Number theory"
    assert [c["claim_id"] for c in record["claims"]] == ["001.1", "001.2"]
    assert record["yaml_main_results"] == ["OAI.First.thing"]
    assert record["summary_overview_similarity"] > 0.9
    assert {t["theorem"] for t in record["targets"]} == {"OAI.First.thing", "OAI.First.helper"}
    assert cov.family_record(corpus, "002")["lean_doc"] is None
    assert len(corpus.hashes) == 6


# ---------------------------------------------------------------------------
# Ranges
# ---------------------------------------------------------------------------


def test_prose_and_lean_atoms():
    prose = "for $`2\\le p\\lt\\infty`$ and <i>n</i> ≥ 3 with $`0\\lt q\\le4`$ and $`\\beta&gt;0`$"
    assert cov.prose_atoms(prose) == [
        ("p", ">=", "2"),
        ("n", ">=", "3"),
        ("q", ">", "0"),
        ("q", "<=", "4"),
        ("β", ">", "0"),
    ]
    atoms, integers = cov.lean_atoms("∀ (n : ℕ), 3 ≤ n → ∀ (β : ℝ), 0 < β → (n : ℝ) ≤ 7")
    assert ("n", ">=", "3") in atoms and ("β", ">", "0") in atoms and ("n", "<=", "7") in atoms
    assert integers == {"n"}


def test_auto_range_check_detects_a_narrower_lean_range():
    weaker = cov.auto_range_check("every $`n\\ge2`$", ["∀ (n : ℕ), 3 ≤ n → True"])
    assert weaker["relation"] == "WEAKER" and weaker["paper_only_witness"] == {"v0": 2}
    same = cov.auto_range_check("<i>n</i> ≥ 3 and $`\\beta&gt;0`$", ["∀ (n : ℕ), 3 ≤ n → ∀ (β : ℝ), 0 < β → True"])
    assert same["relation"] == "EQUIVALENT" and same["variables"] == ["n", "β"]
    assert cov.auto_range_check("no bounds here", ["∀ (n : ℕ), 3 ≤ n → True"]) is None


def test_auto_range_check_refuses_an_inconsistent_extraction():
    # Two regimes of one letter in one sentence give an empty paper range: no answer rather than a wrong one.
    result = cov.auto_range_check("for $`0\\lt q\\le4`$ and for <i>q</i> &gt; 4", ["∀ q : ℝ, 0 < q → True"])
    assert result["relation"] == "UNDECIDED"


def test_hand_specs_reproduce_the_calibration_ranges():
    from python.discovery import statement_fidelity as sf

    specs = cov.hand_specs()
    assert sf.compare_ranges(specs["079.1"]["spec"]).relation == sf.Fidelity.EQUIVALENT
    assert sf.compare_ranges(specs["215.3"]["spec"]).relation == sf.Fidelity.EQUIVALENT
    assert specs["215.3"]["decides"] is False  # The finite-volume gap is not a range question.
    items = {r["item"]: r for r in cov.paper_item_calibration()}
    assert items["logarithmic_refinement (Theorem 1.2)"]["strength"] == "WEAKER"
    assert items["logarithmic_sobolev (Corollary 7.1, C = 0 slice)"]["strength"] == "WEAKER"
    assert all(r["status"] == "STATEMENT_ONLY" and r["basis"] == "z3" for r in items.values())


# ---------------------------------------------------------------------------
# Classification
# ---------------------------------------------------------------------------


def _record(**kw):
    record = {
        "family_id": "001",
        "discipline": "Number theory",
        "lean_doc": "lean/docs/001.md",
        "scope_paragraphs": [
            "The formalization proves the zeta bound for every modulus.",
            "The Hecke consequences are not included.",
        ],
        "comparator_rows": [{"label": "Zeta bound", "file": "F.lean", "line": None, "theorems": ["OAI.F.main"]}],
        "targets": [
            {
                "theorem": "OAI.F.main",
                "docstring": "Zeta bound",
                "statement": "theorem main (n : ℕ) " "(h : 2 ≤ n) : True",
                "file": "F.lean",
                "line": 3,
                "support": "",
            }
        ],
    }
    record.update(kw)
    return record


def test_heuristic_baseline():
    record = _record()
    assert cov.heuristic_status("Proves the zeta bound for every modulus.", record)[0] == "KERNEL_TARGET_EQUIVALENT"
    assert cov.heuristic_status("The Hecke consequences follow.", record)[0] == "PROSE_ONLY"
    assert cov.heuristic_status("Anything at all.", _record(lean_doc=None))[0] == "PROSE_ONLY"


def test_classify_claim_bases():
    no_doc = cov.classify_claim(_record(lean_doc=None), {"claim_id": "001.1", "text": "Proves X."}, None, {})
    assert no_doc["status"] == "PROSE_ONLY" and no_doc["basis"] == "mechanical" and no_doc["tag"] is None
    judged = cov.classify_claim(
        _record(),
        {"claim_id": "001.1", "text": "Proves it for every $`n\\ge1`$."},
        {"status": "KERNEL_TARGET_WEAKER", "targets": ["OAI.F.main"], "weaker_kind": "range", "rationale": "r"},
        {},
    )
    assert judged["basis"] == "judgement" and judged["tag"] == cov.INFERRED
    assert judged["auto_range_check"]["relation"] == "WEAKER"  # n >= 1 in prose, 2 <= n in Lean.
    unjudged = cov.classify_claim(_record(), {"claim_id": "001.1", "text": "Zeta bound."}, None, {})
    assert unjudged["basis"] == "heuristic" and unjudged["tag"] == cov.INFERRED


def test_a_deciding_hand_spec_overrides_the_kernel_relation():
    from python.discovery import statement_fidelity as sf

    spec = sf.RangeSpec(theorem="t", parameters=[sf.Parameter("n", integer=True)], paper="n >= 2", lean="n >= 3")
    row = cov.classify_claim(
        _record(),
        {"claim_id": "001.1", "text": "x"},
        {"status": "KERNEL_TARGET_EQUIVALENT", "targets": [], "rationale": "r"},
        {"001.1": {"spec": spec, "decides": True}},
    )
    assert row["status"] == "KERNEL_TARGET_WEAKER" and row["basis"] == "z3" and row["tag"] is None
    assert row["range_check"]["relation"] == "WEAKER"


def test_summarise_shares_add_up():
    rows = [
        {
            "claim_id": "1.1",
            "family_id": "1",
            "discipline": "A",
            "status": "PROSE_ONLY",
            "basis": "mechanical",
            "heuristic_status": "PROSE_ONLY",
        },
        {
            "claim_id": "2.1",
            "family_id": "2",
            "discipline": "B",
            "status": "KERNEL_TARGET_EQUIVALENT",
            "basis": "judgement",
            "heuristic_status": "PROSE_ONLY",
        },
        {
            "claim_id": "2.2",
            "family_id": "2",
            "discipline": "B",
            "status": "KERNEL_TARGET_EQUIVALENT",
            "basis": "judgement",
            "heuristic_status": "KERNEL_TARGET_EQUIVALENT",
        },
    ]
    summary = cov.summarise(rows)
    assert summary["overall"]["counts"]["KERNEL_TARGET_EQUIVALENT"] == 2
    assert summary["by_discipline"]["B"]["shares"]["KERNEL_TARGET_EQUIVALENT"] == 1.0
    assert summary["families"]["every_claim_kernel_equivalent"] == 1
    assert summary["heuristic_agreement"] == {"claims": 2, "agree": 1, "rate": 0.5}


# ---------------------------------------------------------------------------
# Lint
# ---------------------------------------------------------------------------


def test_lint_comparator_file_keeps_only_target_findings():
    source = (
        "def r (x y : ℝ) : ℝ := x / y\n\ntheorem main (x y : ℝ) : r x y = r x y := by\n  sorry\n\n"
        "theorem other (x y : ℝ) : r x y = 0 := by\n  sorry\n"
    )
    entry = cov.lint_comparator_file(source, "X.lean", ["OAI.X.main"])
    assert entry["targets"] == 1
    assert {f["theorem"] for f in entry["open"]} == {"main"}
    assert entry["open"][0]["kind"] == "DIVISION"


def test_uses_token_shortcut_matches_the_regex_definition():
    source = (
        "def a' : ℕ := 1\ndef b : ℕ := a' + 1\ndef ab : ℕ := 2\ndef c : ℕ := b + ab\ntheorem t : c = c := by\n  sorry\n"
    )
    decls = lean_junk_lint.parse_declarations(source)
    for d in decls:
        expected = [o for o in decls if o is not d and re.search(rf"(?<![\w']){re.escape(o.short)}(?![\w'])", d.text)]
        assert lean_junk_lint._uses(d, decls) == expected


# ---------------------------------------------------------------------------
# The committed dataset
# ---------------------------------------------------------------------------

needs_dataset = pytest.mark.skipif(not (DATA / "coverage_map.json").exists(), reason="dataset not built")


@pytest.fixture(scope="module")
def dataset():
    return json.loads((DATA / "coverage_map.json").read_text(encoding="utf-8"))


@needs_dataset
def test_dataset_is_pinned_and_complete(dataset):
    assert dataset["source"]["commit"] == cov.SOURCE_COMMIT
    assert len(dataset["families"]) == 373
    statuses = set(cov.STATUS_ORDER)
    claims = dataset["claims"]
    assert all(c["status"] in statuses for c in claims)
    assert len({c["claim_id"] for c in claims}) == len(claims)
    for c in claims:
        if c["basis"] in ("judgement", "heuristic"):
            assert c["tag"] == cov.INFERRED
        if c["basis"] == "mechanical":
            assert c["status"] == "PROSE_ONLY"
    assert not [c for c in claims if c["basis"] == "heuristic"], "every claim with a scope note is judged"
    summary = dataset["summary"]
    assert summary["overall"]["claims"] == len(claims)
    assert sum(summary["overall"]["counts"].values()) == len(claims)
    assert sum(d["claims"] for d in summary["by_discipline"].values()) == len(claims)


@needs_dataset
def test_judgements_cover_exactly_the_claims_with_a_scope_note(dataset):
    judgements = json.loads((DATA / "judgements.json").read_text(encoding="utf-8"))
    judged = {j["claim_id"] for j in judgements}
    with_doc = {c["claim_id"] for c in dataset["claims"] if c["basis"] != "mechanical"}
    assert judged == with_doc
    assert Counter(j["status"] for j in judgements).keys() <= set(cov.STATUS_ORDER)


@needs_dataset
def test_calibration_family_079(dataset):
    rows = {c["claim_id"]: c for c in dataset["claims"] if c["family_id"] == "079"}
    assert rows["079.1"]["status"] == "KERNEL_TARGET_EQUIVALENT" and rows["079.1"]["basis"] == "z3"
    assert rows["079.1"]["range_check"]["relation"] == "EQUIVALENT"
    # Maximal Bochner–Riesz, the paraboloid, the cone, Schrödinger and Nikodym are outside the Comparator file.
    for cid in ("079.2", "079.3", "079.4"):
        assert rows[cid]["status"] == "KERNEL_TARGET_WEAKER"
    items = {r["item"]: r for r in dataset["calibration_paper_items"]}
    assert items["logarithmic_refinement (Theorem 1.2)"]["strength"] == "WEAKER"
    assert items["logarithmic_sobolev (Corollary 7.1, C = 0 slice)"]["strength"] == "WEAKER"


@needs_dataset
def test_calibration_family_215(dataset):
    rows = {c["claim_id"]: c for c in dataset["claims"] if c["family_id"] == "215"}
    assert "continuum limit" in rows["215.1"]["text"] and "mass gap" in rows["215.1"]["text"]
    assert rows["215.1"]["status"] == "PROSE_ONLY"  # O(3) continuum limit, relativistic theory, mass gap.
    assert rows["215.2"]["status"] == "PROSE_ONLY"  # O(4) transfer-gap asymptotic.
    assert rows["215.3"]["status"] == "KERNEL_TARGET_WEAKER"  # Only finite-lattice decay is a kernel target.
    assert rows["215.3"]["weaker_kind"] == "finite_volume"
    assert rows["215.3"]["range_check"]["relation"] == "EQUIVALENT"


@needs_dataset
def test_lint_output_is_consistent(dataset):
    lint = json.loads((DATA / "lint_open.json").read_text(encoding="utf-8"))
    assert lint["open"] == len(lint["open_findings"]) == dataset["summary"]["lint"]["open"]
    assert lint["targets"] >= 400
    assert all(f["kind"] in lean_junk_lint.JunkKind.__members__ for f in lint["open_findings"])


@needs_dataset
def test_lint_reproduces_the_adr070_open_findings_and_flags_classical_on():
    lint = json.loads((DATA / "lint_open.json").read_text(encoding="utf-8"))
    smoothing = {
        (f["theorem"].split(".")[-1], f["kind"], f["line"])
        for f in lint["open_findings"]
        if f["file"] == "LocalSmoothing.lean"
    }
    assert smoothing == {("stein_square", "DIVISION", 49), ("stein_square", "RPOW", 49), ("stein_square", "DERIV", 76)}
    classical = [f for f in lint["open_findings"] if f["file"] == "ClassicalON.lean"]
    assert {f["declaration"] for f in classical} == {"sphereProbability", "partition", "correlation"}
    assert all(f["families"] == ["215"] for f in classical)
