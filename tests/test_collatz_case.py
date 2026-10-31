"""Tests for the Collatz checkability case (python/discovery/collatz_case.py)."""

import json
from pathlib import Path

import pytest

from python.discovery import collatz_case as case

REPORT = Path(__file__).resolve().parent.parent / "examples" / "collatz-checkable" / "collatz_report.json"


@pytest.fixture(scope="module")
def checks():
    return {c["id"]: c for c in case.run_checks()}


def test_dag_is_acyclic_complete_and_keeps_the_conjecture_open():
    audit = case.build_dag().verify_dag_acyclicity_and_completeness()
    assert audit["is_acyclic"] and audit["missing_premises"] == []
    assert case.NODES["Collatz"][1] == "OPEN"
    assert {"NoNontrivialCycle", "NoDivergentOrbit"} <= {k for k, v in case.NODES.items() if v[1] == "OPEN"}


def test_every_encodable_check_is_verified(checks):
    for template, _ in case.CHECKS:
        assert checks[template.id]["status"] == case.VERIFIED, checks[template.id]


def test_open_problems_stay_not_encodable(checks):
    for template in case.NOT_ENCODED:
        assert checks[template.id]["status"] == case.NOT_ENCODABLE


def test_no_assertion_is_hard_coded(checks):
    source = Path(case.__file__).read_text(encoding="utf-8")
    assert '"holds": True' not in source


def test_cycle_bound_reproduces_eliahou_and_extends_it():
    assert case.min_cycle_size(40)["k"] == 17087915
    at68 = case.min_cycle_size(68)
    assert at68 == {"m": 72057431991, "k": 114208327604, "inside": True}


def test_affine_form_by_hand():
    a, b, parities = case._symbolic_iterate(5, 6)
    for t in range(50):
        assert case._iterate(5 + 64 * t, 6) == a + b * t
    assert b == 3 ** sum(parities)


def test_negative_controls_detect_failure():
    assert all(c["detected"] for c in case.negative_controls())


def test_committed_report_matches(checks):
    report = json.loads(REPORT.read_text(encoding="utf-8"))
    assert report["claim_status"].startswith("OPEN")
    assert {c["id"]: c["status"] for c in report["checks"]} == {k: c["status"] for k, c in checks.items()}
