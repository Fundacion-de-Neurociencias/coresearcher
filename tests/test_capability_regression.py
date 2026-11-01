"""Every benchmark is a regression test (ADR-DISCOVERY-084, block C, method M9).

The parametrized test below runs each case offline and compares it with benchmarks/regression/expectations.json.
It fails when detection gets worse, and also when it gets better without the expectation being updated in the same
change. To update deliberately: `coresearcher regression update --reason "..."` (docs/reference/REGRESSION_BENCHMARKS.md).
"""

import argparse
import copy
import json

import pytest

from python.cli import regression as regression_cli
from python.discovery import asymptotic_forms as af
from python.discovery import capability_regression as cr
from python.discovery import openai_math_time_travel as tt

EXPECTATIONS = cr.load_expectations()


def _explain(result) -> str:
    lines = [f"{result['case']}: {result['status']} {result['error'] or ''}"]
    for d in result["differences"]:
        lines.append(f"  {d['class']}: {d['key']}: expected {d['expected']!r}, observed {d['observed']!r}")
    lines.append(
        "A REGRESSION means a capability got worse. An IMPROVEMENT or CHANGED that is deliberate must be frozen in "
        "the same change: `coresearcher regression update --reason ...` (docs/reference/REGRESSION_BENCHMARKS.md)."
    )
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# The regression cases
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("case_id", sorted(cr.CASES))
def test_case_matches_its_frozen_expectation(case_id):
    result = cr.compare_case(case_id, EXPECTATIONS["cases"].get(case_id), cr.run_case(cr.CASES[case_id]))
    assert result["status"] == cr.PASS, _explain(result)


def test_every_case_has_an_expectation_and_no_stale_ones():
    assert set(EXPECTATIONS["cases"]) == set(cr.CASES)
    assert EXPECTATIONS["history"] and EXPECTATIONS["history"][-1]["version"] == EXPECTATIONS["version"]


def test_time_travel_expectation_keeps_the_known_defect_verdicts():
    """The frozen verdicts of the openai/math corrections (OPENAI_MATH_REVISION_RESULTS.md): two HITs, no MISS."""
    observations = EXPECTATIONS["cases"]["openai_math_time_travel"]["observations"]
    verdicts = {
        k.split("/")[1]: v["value"] for k, v in observations.items() if k.count("/") == 1 and k.startswith("defect/")
    }
    assert len(verdicts) == 17
    assert sorted(k for k, v in verdicts.items() if v == "HIT") == [
        "Exact-Birch-Swinnerton-Dyer-Formula-from-Low-Selmer-Corank",
        "Uniform-real-Lipschitz-surfaces-on-the-triangular-lattice",
    ]
    assert "MISS" not in verdicts.values()


# ---------------------------------------------------------------------------
# Comparison rules
# ---------------------------------------------------------------------------


def test_classification_in_both_directions():
    v = cr.VERDICT
    assert cr.classify(cr.obs("HIT", v), cr.obs("NOT_ENCODABLE", v)) == cr.REGRESSION
    assert cr.classify(cr.obs("NOT_ENCODABLE", v), cr.obs("HIT", v)) == cr.IMPROVEMENT
    assert cr.classify(cr.obs("MISS", v), cr.obs("NOT_ENCODABLE", v)) == cr.CHANGED
    assert cr.classify(cr.obs(3, cr.LOWER), cr.obs(4, cr.LOWER)) == cr.REGRESSION
    assert cr.classify(cr.obs(3, cr.LOWER), cr.obs(2, cr.LOWER)) == cr.IMPROVEMENT
    assert cr.classify(cr.obs(1, cr.HIGHER), cr.obs(2, cr.HIGHER)) == cr.IMPROVEMENT
    assert cr.classify(cr.obs("EQUIVALENT"), cr.obs("WEAKER")) == cr.REGRESSION
    assert cr.classify(cr.obs(1, cr.HIGHER), cr.obs(1, cr.LOWER)) == cr.CHANGED
    assert cr.classify(cr.obs("x"), cr.obs("x")) is None


def _fresh(observations, fixtures=None, error=None):
    return {"observations": observations, "fixtures": fixtures or {}, "error": error, "seconds": 0.0}


def test_an_unfrozen_improvement_fails_like_a_regression():
    expected = {"fixtures": {}, "observations": {"hits": cr.obs(1, cr.HIGHER), "alarms": cr.obs(5, cr.LOWER)}}
    better = cr.compare_case("c", expected, _fresh({"hits": cr.obs(2, cr.HIGHER), "alarms": cr.obs(5, cr.LOWER)}))
    assert better["status"] == cr.IMPROVEMENT
    mixed = cr.compare_case("c", expected, _fresh({"hits": cr.obs(2, cr.HIGHER), "alarms": cr.obs(6, cr.LOWER)}))
    assert mixed["status"] == cr.REGRESSION  # the worst difference decides
    missing = cr.compare_case("c", expected, _fresh({"hits": cr.obs(1, cr.HIGHER)}))
    assert missing["status"] == cr.CHANGED


def test_fixture_bytes_are_pinned():
    expected = {"fixtures": {"f.json": "a" * 64}, "observations": {}}
    result = cr.compare_case("c", expected, _fresh({}, {"f.json": "b" * 64}))
    assert result["status"] == cr.FIXTURE_CHANGED


def test_a_case_that_cannot_run_is_an_error_never_a_pass():
    def boom():
        raise RuntimeError("no fixture")

    fresh = cr.run_case(cr.Case("boom", "t", "ADR", [], boom))
    assert fresh["error"].startswith("RuntimeError")
    assert cr.compare_case("boom", {"fixtures": {}, "observations": {}}, fresh)["status"] == cr.ERROR
    report = cr.check(["cited_registry_calibration"], expectations={"version": 0, "cases": {}})
    assert report["status"] == cr.CHANGED  # a case without an expectation is not a pass either


def test_expectations_are_pinned_by_sha256(tmp_path):
    path, sha = tmp_path / "e.json", tmp_path / "e.sha256"
    data = copy.deepcopy(EXPECTATIONS)
    path.write_text(json.dumps(data), encoding="utf-8")
    sha.write_text(cr.expectations_sha256(data) + "  e.json\n", encoding="utf-8")
    assert cr.load_expectations(path, sha)["version"] == EXPECTATIONS["version"]
    data["cases"]["openai_math_time_travel"]["observations"]["hits/CITATION"]["value"] = 0  # a quiet hand edit
    path.write_text(json.dumps(data), encoding="utf-8")
    with pytest.raises(cr.ExpectationsError):
        cr.load_expectations(path, sha)


def test_update_records_a_version_a_reason_and_the_hash(tmp_path):
    path, sha = tmp_path / "e.json", tmp_path / "e.sha256"
    with pytest.raises(cr.ExpectationsError):
        cr.update("  ", ["cited_registry_calibration"], path, sha)
    first = cr.update("first freeze", ["cited_registry_calibration"], path, sha, today="2026-11-01")
    assert first["version"] == 1 and first["changed"]["cited_registry_calibration"][0]["key"] == "*"
    again = cr.update("nothing changed", ["cited_registry_calibration"], path, sha)
    assert again == {"version": 1, "changed": {}}
    data = cr.load_expectations(path, sha)
    assert data["history"] == [
        {
            "version": 1,
            "date": "2026-11-01",
            "reason": "first freeze",
            "changes": {"cited_registry_calibration": [{"key": "*", "class": "CHANGED"}]},
        }
    ]


# ---------------------------------------------------------------------------
# Building blocks
# ---------------------------------------------------------------------------


def test_little_o_readings():
    lean = af.little_o_exponent("A*n*log(log(n))**2/sqrt(log(n))", symbols=["A"])
    assert (lean["signed_reading"], lean["nonnegative_reading"]) == (af.FITS, af.DOES_NOT_FIT)
    assert lean["implied_o1_limit"] == "0"
    assert af.little_o_exponent("n/log(n)")["nonnegative_reading"] == af.FITS
    assert af.little_o_exponent("n")["signed_reading"] == af.DOES_NOT_FIT
    # An O(1) factor against the bare main term: its size decides, and it is unknown, so no verdict.
    assert af.little_o_exponent("A*n/sqrt(log(n))", symbols=["A"])["nonnegative_reading"] == af.UNDECIDED


def test_uniformity_reads_the_quantifier_prefix():
    uniform = "theorem t : ∃ (machine : M) (C : ℝ), ∀ (n : ℕ) (F : CNF n), Runs machine F"
    per_input = "theorem t : ∀ (n : ℕ), ∃ (machine : M), ∀ (F : CNF n), Runs machine F"
    assert af.uniformity(uniform, "machine", ["n", "F"])["verdict"] == af.UNIFORM
    assert af.uniformity(per_input, "machine", ["n", "F"])["verdict"] == af.NON_UNIFORM
    assert af.uniformity("theorem t : True", "machine", ["n"])["verdict"] == af.UNDECIDED


def test_excerpts_keep_original_line_numbers():
    text = "a\nb\n$x = y$\nc\n\\begin{align}\nu &= v \\\\\nw &= z\n\\end{align}\nd"
    kept = tt.window(text, [6])
    assert kept == [5, 6, 7, 8]  # closed under the whole display environment
    rebuilt = tt.unblock(tt.blocks(text, kept)).split("\n")
    assert rebuilt[4:8] == text.split("\n")[4:8] and rebuilt[:4] == ["", "", "", ""]


# ---------------------------------------------------------------------------
# CLI and API
# ---------------------------------------------------------------------------


def test_cli_list_and_check(capsys):
    assert regression_cli.main(argparse.Namespace(regression_command="list")) == 0
    assert {c["id"] for c in json.loads(capsys.readouterr().out)} == set(cr.CASES)
    ns = argparse.Namespace(regression_command="check", cases=["manuscript_audit_calibration"], json=False)
    assert regression_cli.main(ns) == 0
    assert "PASS" in capsys.readouterr().out
    ns = argparse.Namespace(regression_command="check", cases=["no-such-case"], json=False)
    assert regression_cli.main(ns) == regression_cli.EXIT_REFUSED
    capsys.readouterr()


def test_api_cases_and_check(api_client):
    body = api_client.get("/api/regression/cases").json()
    assert body["expectations_version"] == EXPECTATIONS["version"]
    assert {c["id"] for c in body["cases"]} == set(cr.CASES)
    r = api_client.post("/api/regression/check", json={"case_ids": ["cited_registry_calibration"]})
    assert r.status_code == 200 and r.json()["status"] == cr.PASS
    assert api_client.post("/api/regression/check", json={"case_ids": ["nope"]}).status_code == 422
    catalogue = {(c["method"], c["path"]): c for c in api_client.get("/api/capabilities").json()["capabilities"]}
    assert catalogue[("POST", "/api/regression/check")]["operationClass"] == "READ_ONLY"
