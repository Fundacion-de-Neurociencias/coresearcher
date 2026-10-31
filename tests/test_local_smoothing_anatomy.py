"""Tests for the Local smoothing proof-anatomy case (python/discovery/local_smoothing_anatomy.py)."""

import json
from pathlib import Path

import pytest

from python.discovery import local_smoothing_anatomy as anatomy
from python.discovery import local_smoothing_case as fidelity

REPORT = Path(__file__).resolve().parent.parent / "examples" / "local-smoothing-anatomy" / "anatomy_report.json"


@pytest.fixture(scope="module")
def checks():
    return {c["id"]: c for c in anatomy.run_checks()}


def test_target_paper_is_the_one_audited_in_adr_070():
    target = next(s for s in anatomy.SOURCES if s["role"] == "target")
    assert target["sha256"] == fidelity.SOURCE["paper_sha256"]
    assert target["path"] == fidelity.SOURCE["paper"]
    assert anatomy.COMMIT == fidelity.SOURCE["commit"]


def test_dag_is_acyclic_and_complete():
    audit = anatomy.build_dag().verify_dag_acyclicity_and_completeness()
    assert audit["is_acyclic"]
    assert audit["missing_premises"] == []
    # Only the imported external results are leaves without proof, by design.
    assert sorted(audit["unproven_axioms"]) == sorted(f"EXT:{k}" for k in anatomy.EXTERNAL)
    assert len(anatomy.topological_order()) == len(anatomy.NODES)


def test_dag_contains_the_main_chain_of_the_paper():
    edges = {(prem, k) for k, (_, _, premises, _) in anatomy.NODES.items() for prem in premises}
    for premise, consequence in [
        ("Thm1.2", "Eq7.3"),
        ("Eq7.3", "Thm1.1"),
        ("Prop6.3", "Thm1.2"),
        ("Lem6.1", "Prop6.3"),
        ("Prop5.1", "Prop6.3"),
        ("Prop4.2", "Prop5.1"),
        ("Lem4.3", "Prop5.1"),
        ("ThmA.1", "Prop5.1"),
        ("Lem3.3", "Prop4.2"),
        ("Lem2.1", "Prop2.2"),
    ]:
        assert (premise, consequence) in edges
    for node in ("Lem2.1", "Prop2.2", "Lem3.1", "Lem3.2", "Lem3.3", "ThmA.1", "Lem4.3", "Lem6.1"):
        assert node in anatomy.ancestors("Thm1.1")
    # The obstruction results and the precursor-independent sharpness remark are not premises of Theorem 1.1.
    for node in ("Prop8.1", "Prop8.2", "Rem6.2"):
        assert node not in anatomy.ancestors("Thm1.1")


def test_main_theorem_imports_the_named_external_results():
    imports = set(anatomy.imports_of("Thm1.1"))
    assert {"Friedrichs1954", "Kaiser1990", "Serre2018", "Alesker2013", "Aubin1984", "Mabuchi1986"} <= imports
    assert "Tao1999" not in imports and "Keich1999" not in imports
    assert "Tao1999" in anatomy.imports_of("Cor9.3")
    assert "Keich1999" in anatomy.imports_of("Cor9.1")
    assert "BeltranHickmanSogge" in anatomy.imports_of("Thm10.1")


def test_every_coverage_join_finds_its_adr_070_rows():
    for node in anatomy.COVERAGE_JOIN:
        assert node in anatomy.NODES
        assert anatomy.coverage_rows(node), node
    joined = {row["item"] for node in anatomy.COVERAGE_JOIN for row in anatomy.coverage_rows(node)}
    assert joined == {row["item"] for row in fidelity.COVERAGE}


def test_encodable_checks_are_verified(checks):
    for template, _ in anatomy.CHECKS:
        result = checks[template.id]
        assert result["status"] == anatomy.VERIFIED, (template.id, result)
        assert result["assertions"] and all(x["holds"] for x in result["assertions"])


def test_unencoded_claims_stay_not_encodable(checks):
    for template in anatomy.NOT_ENCODED:
        assert checks[template.id]["status"] == anatomy.NOT_ENCODABLE
        assert checks[template.id]["assertions"] == []


def test_negative_controls_are_refuted():
    results = anatomy.run_mutants()
    assert len(results) == len(anatomy.MUTANTS)
    assert all(r["status"] == anatomy.REFUTED for r in results), results


def test_committed_report_matches_the_code(checks):
    report = json.loads(REPORT.read_text(encoding="utf-8"))
    assert report["commit"] == anatomy.COMMIT
    assert {c["id"]: c["status"] for c in report["checks"]} == {k: c["status"] for k, c in checks.items()}
    assert [n["id"] for n in report["dag"]["nodes"]] == anatomy.topological_order()
    assert report["dag"]["is_acyclic"] and report["dag"]["missing_premises"] == []
    assert all(m["status"] == m["expected"] for m in report["mutants"])
