"""Tests for the Local smoothing statement-fidelity case (python/discovery/local_smoothing_case.py)."""

import hashlib
import json

from python.discovery import local_smoothing_case as case
from python.discovery.statement_fidelity import compare_ranges

REPORT = case.CASE_DIR / "fidelity_report.json"


def test_vendored_sources_match_the_pinned_hashes():
    for name, key in (
        ("LocalSmoothing.lean", "lean_statements_sha256"),
        ("LocalSmoothing.json", "comparator_config_sha256"),
    ):
        digest = hashlib.sha256((case.CASE_DIR / name).read_bytes()).hexdigest()
        assert digest == case.SOURCE[key], name


def test_every_comparator_target_has_a_range_spec_and_a_coverage_row():
    config = json.loads((case.CASE_DIR / "LocalSmoothing.json").read_text(encoding="utf-8"))
    assert config["permitted_axioms"] == case.SOURCE["permitted_axioms"]
    targets = {name.rsplit(".", 1)[-1] for name in config["theorem_names"]}
    assert targets == {s.theorem for s in case.RANGE_SPECS if "(" not in s.theorem}
    comparator_rows = {row["lean"] for row in case.COVERAGE if row["status"] == case.COMPARATOR}
    assert comparator_rows == targets


def test_comparator_ranges_are_equivalent_to_the_paper():
    for spec in case.RANGE_SPECS:
        result = compare_ranges(spec)
        assert result.relation.value == "EQUIVALENT", spec.theorem
        assert result.division_hazards == []
        assert all(q["agreement"] == "EQUAL" for q in result.quantities.values())


def test_development_log_powers_are_weaker_than_the_paper():
    for spec in case.DEVELOPMENT_SPECS:
        result = compare_ranges(spec)
        assert result.relation.value == "WEAKER", spec.theorem
        assert result.paper_only_witness is not None


def test_mutants_are_caught():
    for mutant in case.MUTANTS:
        assert compare_ranges(case.mutant_spec(mutant)).relation.value == mutant["expected"], mutant["label"]
    assert sum(m["expected"] != "EQUIVALENT" for m in case.MUTANTS) >= 8


def test_lint_leaves_only_reviewed_stein_findings_open():
    report = case.lint_report()
    open_ = [(f["theorem"], f["kind"], f["line"]) for f in report["findings"] if f["status"] == "OPEN"]
    assert sorted(open_) == sorted(case.REVIEWS)
    assert all(f["review"] for f in report["findings"] if f["status"] == "OPEN")
    kinds = {f["kind"] for f in report["findings"]}
    assert {"BOCHNER_INTEGRAL", "DERIV", "DIVISION", "TO_REAL", "SUPREMUM", "INFINITE_RHS"} <= kinds


def test_committed_report_matches_a_fresh_run():
    committed = json.loads(REPORT.read_text(encoding="utf-8"))
    fresh = case.case_report()
    assert [(r["theorem"], r["relation"]) for r in committed["ranges"]] == [
        (r["theorem"], r["relation"]) for r in fresh["ranges"]
    ]
    assert [m["relation"] for m in committed["mutants"]] == [m["relation"] for m in fresh["mutants"]]
    assert committed["lint"]["findings"] == fresh["lint"]["findings"]
    assert committed["coverage"] == fresh["coverage"]
    assert committed["kernel_check"]["status"] == "NOT RUN"
