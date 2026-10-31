"""Tests for ADR-DISCOVERY-080: the intent probe, the trust ladder and statement fidelity as a service."""

import argparse
import json
from pathlib import Path

import pytest

from python.cli import formal as formal_cli
from python.discovery import fidelity_service, formal_pipeline, formal_provenance, formal_trust
from python.discovery.evidence_service import resolve
from python.discovery.formal_hypothesis import (
    ContentVerdict,
    FormalHypothesisError,
    HypothesisEvaluator,
    default_non_witnesses,
    hypothesis_from_dict,
    hypothesis_to_dict,
)

# A toy existence claim: "a theory with coupling g in dimension d has a non-zero correlation c".
# As written, the claims never mention g, so the free theory (g = 0) satisfies them.
EXISTENCE = {
    "hypothesis_id": "EX",
    "variables": [
        {"name": "g", "domain": [0, 1, 2]},
        {"name": "d", "domain": [2, 3, 4]},
        {"name": "c", "domain": [0, 1]},
    ],
    "scope": "d == 4",
    "claims": ["c == 1"],
    "non_witnesses": [
        {"label": "free theory", "state": {"g": 0}},
        {"label": "lower dimension", "state": {"d": 3}},
    ],
}
# The same claim with the intent written into it: interacting and non-trivial.
REPAIRED = dict(EXISTENCE, hypothesis_id="EX2", claims=["c == 1", "g > 0"])


def _h(data=EXISTENCE, **changes):
    return hypothesis_from_dict(dict(data, **changes))


def _codes(report):
    return {r["code"] for r in report["mandatory_relays"]}


# ---------------------------------------------------------------------------
# 1. Intent probe
# ---------------------------------------------------------------------------


def test_a_declared_non_witness_that_satisfies_the_claims_is_vacuous_relative_to_intent():
    report = HypothesisEvaluator.evaluate(_h()).to_dict()
    assert report["content_verdict"] == "VACUOUS_RELATIVE_TO_INTENT"
    probe = report["intent_probe"]
    assert probe["base_verdict"] == "FALSIFIABLE"
    assert probe["declared_non_witnesses_satisfied"] == ["free theory"]
    free = next(p for p in probe["probes"] if p["label"] == "free theory")
    assert free["outcome"] == "SATISFIES_CLAIMS" and free["origin"] == "declared"
    assert free["witness"] == {"g": 0, "d": 4, "c": 1}
    hypothesis = _h()
    assert hypothesis.applies(free["witness"]) and not hypothesis.violated_claims(free["witness"])
    lower = next(p for p in probe["probes"] if p["label"] == "lower dimension")
    assert lower["outcome"] == "OUT_OF_SCOPE" and lower["witness"] is None
    assert "VACUOUS_RELATIVE_TO_INTENT" in _codes(report)
    assert report["formal_status"] == "DECIDED"


def test_the_verdict_is_distinct_from_vacuous():
    assert ContentVerdict.VACUOUS_RELATIVE_TO_INTENT is not ContentVerdict.VACUOUS
    empty = HypothesisEvaluator.evaluate(_h(scope="d == 5 - 1 and d == 2")).to_dict()
    assert empty["content_verdict"] == "VACUOUS"
    assert empty["intent_probe"]["base_verdict"] == "VACUOUS"
    assert {p["outcome"] for p in empty["intent_probe"]["probes"]} == {"OUT_OF_SCOPE"}
    assert "VACUOUS_RELATIVE_TO_INTENT" not in _codes(empty)


def test_a_claim_that_excludes_its_non_witnesses_keeps_its_verdict():
    report = HypothesisEvaluator.evaluate(_h(REPAIRED)).to_dict()
    assert report["content_verdict"] == "FALSIFIABLE"
    outcomes = {p["label"]: p["outcome"] for p in report["intent_probe"]["probes"]}
    assert outcomes == {"free theory": "FORBIDDEN", "lower dimension": "OUT_OF_SCOPE"}
    assert report["intent_probe"]["declared_non_witnesses_satisfied"] == []
    assert "VACUOUS_RELATIVE_TO_INTENT" not in _codes(report)


def test_smt_and_enumeration_agree_on_the_probe():
    enum = HypothesisEvaluator.evaluate(_h(), backend="enumeration").to_dict()
    smt = HypothesisEvaluator.evaluate(_h(), backend="smt").to_dict()
    assert enum["content_verdict"] == smt["content_verdict"] == "VACUOUS_RELATIVE_TO_INTENT"
    assert [p["outcome"] for p in enum["intent_probe"]["probes"]] == [
        p["outcome"] for p in smt["intent_probe"]["probes"]
    ]
    witness = smt["intent_probe"]["probes"][0]["witness"]
    assert witness["g"] == 0 and _h().applies(witness) and not _h().violated_claims(witness)


def test_continuous_hypotheses_are_probed_by_z3():
    data = {
        "hypothesis_id": "R",
        "variables": [{"name": "m", "continuous": True, "lower": 0, "upper": 10}],
        "claims": ["m >= 0"],
        "non_witnesses": [{"label": "massless", "state": {"m": 0}}],
    }
    report = HypothesisEvaluator.evaluate(hypothesis_from_dict(data)).to_dict()
    assert report["backend"] == "smt" and report["content_verdict"] == "VACUOUS_RELATIVE_TO_INTENT"
    assert report["intent_probe"]["base_verdict"] == "UNFALSIFIABLE"
    assert report["intent_probe"]["probes"][0]["witness"] == {"m": 0}
    gapped = dict(data, claims=["m >= 1"])
    assert HypothesisEvaluator.evaluate(hypothesis_from_dict(gapped)).content_verdict.value == "FALSIFIABLE"


def test_default_probes_are_derived_and_advisory():
    data = {
        "hypothesis_id": "D",
        "variables": [
            {"name": "x", "domain": [-1, 0, 3]},
            {"name": "y", "continuous": True, "lower": 1, "upper": 2},
            {"name": "kind", "domain": ["a", "b"]},
            {"name": "flag", "domain": [True, False]},
        ],
        "claims": ["x >= 0"],
    }
    hypothesis = hypothesis_from_dict(data)
    probes = {p["label"]: p["state"] for p in default_non_witnesses(hypothesis)}
    assert probes == {
        "default: numeric variables at zero": {"x": 0},
        "default: numeric variables at their lower bounds": {"x": -1, "y": 1},
        "default: numeric variables at their upper bounds": {"x": 3, "y": 2},
    }
    report = HypothesisEvaluator.evaluate(hypothesis, default_probes=True).to_dict()
    assert report["content_verdict"] == "FALSIFIABLE"  # Default probes never change the verdict.
    assert report["intent_probe"]["default_probes_satisfied"] == [
        "default: numeric variables at zero",
        "default: numeric variables at their upper bounds",
    ]
    assert "TRIVIAL_WITNESS_SATISFIES_CLAIMS" in _codes(report)


def test_reports_without_probes_keep_their_bytes_and_digests():
    plain = {k: v for k, v in EXISTENCE.items() if k != "non_witnesses"}
    hypothesis = hypothesis_from_dict(plain)
    assert "non_witnesses" not in hypothesis_to_dict(hypothesis)
    report = HypothesisEvaluator.evaluate(hypothesis)
    assert report.intent_probe is None and "intent_probe" not in report.to_dict()
    again = HypothesisEvaluator.evaluate(hypothesis, default_probes=False)
    assert report.provenance["input_sha256"] == again.provenance["input_sha256"]
    probed = HypothesisEvaluator.evaluate(hypothesis, default_probes=True)
    assert probed.provenance["input_sha256"] != report.provenance["input_sha256"]


def test_non_witnesses_round_trip_and_are_validated():
    hypothesis = _h()
    assert hypothesis_to_dict(hypothesis_from_dict(hypothesis_to_dict(hypothesis))) == hypothesis_to_dict(hypothesis)
    unlabeled = _h(non_witnesses=[{"state": {"g": 0, "d": 4}}])
    assert unlabeled.non_witnesses[0]["label"] == "g=0, d=4"
    for bad in (
        [{"label": "x", "state": {"nope": 0}}],
        [{"label": "x", "state": {"g": 7}}],
        [{"label": "x", "state": {}}],
        [{"g": 0}],
        "free",
    ):
        with pytest.raises(FormalHypothesisError):
            _h(non_witnesses=bad)
    with pytest.raises(FormalHypothesisError):
        hypothesis_from_dict(
            {
                "hypothesis_id": "R",
                "variables": [{"name": "m", "continuous": True, "lower": 0, "upper": 1}],
                "claims": ["m >= 0"],
                "non_witnesses": [{"label": "far", "state": {"m": 5}}],
            }
        )


# ---------------------------------------------------------------------------
# 2. Trust ladder
# ---------------------------------------------------------------------------

STATEMENT = "theorem t (p : ℝ) (hp : 2 < p) : 0 < p - 2 := by linarith"
PINNED = formal_trust.statement_sha256(STATEMENT)
FILE_SHA = "a" * 64


def _check(**changes):
    return dict(
        {
            "status": "KERNEL_CHECKED",
            "toolchain": "leanprover/lean4:v4.34.1",
            "file_sha256": FILE_SHA,
            "statement_sha256": PINNED,
            "axioms": ["propext", "Classical.choice"],
            "checker": "lab A",
        },
        **changes,
    )


def _evidence(**changes):
    return dict(
        {
            "claim": "p - 2 is positive for p > 2",
            "statement": {"text": STATEMENT, "location": "lean/T.lean", "sha256": PINNED},
            "statement_audit": {"statement_sha256": PINNED, "fidelity": "EQUIVALENT", "lint_open_unreviewed": 0},
            "kernel_check": _check(),
            "reproductions": [_check(checker="lab B")],
        },
        **changes,
    )


def test_full_evidence_reaches_the_top_rung():
    result = formal_trust.assess(_evidence())
    assert result["rung"] == "INDEPENDENTLY_REPRODUCED" and result["lean_status"] == "DECIDED"
    assert all(r["met"] for r in result["rungs"]) and result["next_rung"] is None


@pytest.mark.parametrize(
    "changes, rung, reason",
    [
        ({"statement": None}, "CLAIMED", "no formal statement"),
        ({"statement": {"text": STATEMENT, "location": "x", "sha256": "b" * 64}}, "CLAIMED", "does not match"),
        (
            {"statement_audit": {"statement_sha256": PINNED, "fidelity": "WEAKER", "lint_open_unreviewed": 0}},
            "STATEMENT_PUBLIC",
            "WEAKER",
        ),
        (
            {"statement_audit": {"statement_sha256": PINNED, "fidelity": "EQUIVALENT", "lint_open_unreviewed": 2}},
            "STATEMENT_PUBLIC",
            "OPEN without a review",
        ),
        ({"kernel_check": _check(status="NOT_KERNEL_CHECKED")}, "STATEMENT_AUDITED", "NOT_KERNEL_CHECKED"),
        ({"kernel_check": _check(axioms=["propext", "sorryAx"])}, "STATEMENT_AUDITED", "sorryAx"),
        ({"kernel_check": _check(axioms=None)}, "STATEMENT_AUDITED", "axioms is missing"),
        ({"kernel_check": _check(toolchain="")}, "STATEMENT_AUDITED", "toolchain"),
        ({"kernel_check": _check(file_sha256="abc")}, "STATEMENT_AUDITED", "file_sha256"),
        ({"kernel_check": _check(statement_sha256="c" * 64)}, "STATEMENT_AUDITED", "pinned statement"),
        ({"reproductions": [_check(checker="lab A")]}, "KERNEL_CHECKED", "not independent"),
        ({"reproductions": []}, "KERNEL_CHECKED", "no reproduction"),
    ],
)
def test_each_rung_has_a_mechanical_rule(changes, rung, reason):
    result = formal_trust.assess(_evidence(**changes))
    assert result["rung"] == rung
    failing = next(r for r in result["rungs"] if not r["met"])
    assert any(reason in why for why in failing["reasons"]), failing


def test_rungs_are_not_skipped():
    result = formal_trust.assess(_evidence(statement_audit=None))
    assert result["rung"] == "STATEMENT_PUBLIC" and result["lean_status"] == "NOT_KERNEL_CHECKED"
    kernel = next(r for r in result["rungs"] if r["rung"] == "KERNEL_CHECKED")
    assert not kernel["met"] and kernel["reasons"][0] == "needs STATEMENT_AUDITED first"
    assert result["next_rung"] == "STATEMENT_AUDITED"
    assert formal_trust.relays([result])[0]["code"] == "CLAIM_BELOW_KERNEL_CHECKED"
    assert formal_trust.relays([formal_trust.assess(_evidence())]) == []
    with pytest.raises(ValueError):
        formal_trust.assess({"claim": ""})


def test_an_audit_record_is_built_from_the_fidelity_service():
    spec = {"theorem": "t", "parameters": [{"name": "p"}], "paper": "p > 2", "lean": "p > 2"}
    fidelity = fidelity_service.compare(spec)
    lint = fidelity_service.lean_lint(STATEMENT, "T.lean")
    audit = formal_trust.audit_record(STATEMENT, fidelity, lint)
    assert audit["statement_sha256"] == PINNED and audit["fidelity"] == "EQUIVALENT"
    assert audit["lint_open_unreviewed"] == 0
    assert formal_trust.assess(_evidence(statement_audit=audit))["rung"] == "INDEPENDENTLY_REPRODUCED"
    weaker = fidelity_service.compare(dict(spec, lean="p > 3"))
    assert (
        formal_trust.assess(_evidence(statement_audit=formal_trust.audit_record(STATEMENT, weaker, lint)))["rung"]
        == "STATEMENT_PUBLIC"
    )
    unlinted = formal_trust.audit_record(STATEMENT, fidelity, None)
    assert formal_trust.assess(_evidence(statement_audit=unlinted))["rung"] == "STATEMENT_PUBLIC"


def test_formalizer_drafts_stay_claimed_and_supplied_objects_are_public():
    request = formal_pipeline.make_request(hypothesis=EXISTENCE)
    response = formal_pipeline.compute(request)
    trust = formal_trust.for_response(request, response)
    assert [t["rung"] for t in trust] == ["STATEMENT_PUBLIC"]
    prose = dict(request, input_kind="prose")
    assert [t["rung"] for t in formal_trust.for_response(prose, response)] == ["CLAIMED"]


# ---------------------------------------------------------------------------
# 3. Statement fidelity as a service
# ---------------------------------------------------------------------------

SPEC = {
    "theorem": "stein",
    "parameters": [{"name": "n", "integer": True, "lower": 2}, {"name": "p", "lower": 2}, {"name": "alpha"}],
    "paper": "alpha > max(1/2, n*(1/2 - 1/p))",
    "lean": "alpha >= max(1/2, n*(1/2 - 1/p))",
    "paper_source": "Theorem 1.1",
    "lean_source": "Comparator.lean:12",
}


def test_compare_is_sealed_with_status_relays_and_provenance():
    report = fidelity_service.compare(SPEC)
    assert report["relation"] == "STRONGER" and report["formal_status"] == "DECIDED"
    assert report["lean_only_witness"] is not None and report["paper_only_witness"] is None
    assert {"FORMAL_NOT_EMPIRICAL", "FIDELITY_RANGE_ONLY"} <= _codes(report)
    body = {k: v for k, v in report.items() if k not in ("formal_status", "mandatory_relays", "provenance")}
    assert report["provenance"]["output_sha256"] == formal_provenance.sha256_canonical(body)
    assert report["provenance"]["operation"] == "fidelity_compare"
    assert fidelity_service.compare(SPEC)["provenance"]["output_sha256"] == report["provenance"]["output_sha256"]


def test_compare_reports_undecided_as_a_non_verdict():
    risky = {"theorem": "t", "parameters": [{"name": "p"}], "paper": "p > 2", "lean": "1/(p - 2) > 0"}
    report = fidelity_service.compare(risky)
    assert report["formal_status"] == "UNDECIDED" and report["relation"] == "UNDECIDED"
    assert report["division_hazards"] == ["lean: p - 2"]


def test_compare_cross_check_and_invalid_specs():
    report = fidelity_service.compare(SPEC, {"n": [2, 3]})
    assert report["cross_check"]["relation"] == "STRONGER"
    with pytest.raises(FormalHypothesisError):
        fidelity_service.compare(SPEC, {"m": [1]})
    for bad in ({}, dict(SPEC, parameters=[]), dict(SPEC, lean="alpha >"), dict(SPEC, paper="foo(alpha)")):
        with pytest.raises(FormalHypothesisError):
            fidelity_service.compare(bad)


LEAN = """import Mathlib
noncomputable section
theorem bound : ∀ f : ℝ → ℝ, ∀ x : ℝ, 0 < x → f x / x ≤ deriv f x := by
  sorry
"""


def test_lean_lint_marks_findings_discharged_or_open():
    report = fidelity_service.lean_lint(LEAN, "Bound.lean")
    kinds = {f["kind"]: f["status"] for f in report["findings"]}
    assert kinds == {"DIVISION": "DISCHARGED", "DERIV": "OPEN"}
    assert report["open"] == 1 and report["discharged"] == 1 and report["theorems"] == ["bound"]
    assert report["statement_sha256"] == formal_trust.statement_sha256(LEAN)
    assert {"LINT_IS_SYNTACTIC", "LEAN_NOT_KERNEL_CHECKED"} <= _codes(report)
    line = next(f["line"] for f in report["findings"] if f["kind"] == "DERIV")
    reviewed = fidelity_service.lean_lint(
        LEAN, "Bound.lean", [{"theorem": "bound", "kind": "DERIV", "line": line, "note": "f is smooth here"}]
    )
    assert next(f for f in reviewed["findings"] if f["kind"] == "DERIV")["review"] == "f is smooth here"
    with pytest.raises(FormalHypothesisError):
        fidelity_service.lean_lint("   ")


# ---------------------------------------------------------------------------
# 4. Two-phase CLI
# ---------------------------------------------------------------------------


def _cli(argv):
    parser = argparse.ArgumentParser()
    formal_cli.add_parser(parser.add_subparsers(dest="command"))
    return formal_cli.main(parser.parse_args(argv))


def _write(path: Path, data) -> str:
    path.write_text(data if isinstance(data, str) else json.dumps(data), encoding="utf-8")
    return str(path)


def _load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def test_formal_analyze_reports_vacuity_relative_to_intent_and_claim_trust(tmp_path, capsys):
    h = _write(tmp_path / "h.json", EXISTENCE)
    out = tmp_path / "raw"
    assert _cli(["formal", "run", "--hypothesis", h, "--default-probes", "--out", str(out), "--name", "ex"]) == 0
    meta = _load(out / "ex.meta.json")
    assert meta["claim_trust"][0]["rung"] == "STATEMENT_PUBLIC"
    assert "CLAIM_BELOW_KERNEL_CHECKED" in _codes(meta)
    capsys.readouterr()
    assert _cli(["formal", "analyze", str(out / "ex.meta.json")]) == 0
    assert "content_verdict=VACUOUS_RELATIVE_TO_INTENT" in capsys.readouterr().out
    analysis = _load(out / "ex.analysis.json")
    assert analysis["assessment"]["reproduces_run"] is True
    assert analysis["verdict"]["intent"]["declared_non_witnesses_satisfied"] == ["free theory"]
    assert analysis["verdict"]["intent"]["base_verdict"] == "FALSIFIABLE"
    assert analysis["claim_trust"] == meta["claim_trust"]
    assert {"VACUOUS_RELATIVE_TO_INTENT", "CLAIM_BELOW_KERNEL_CHECKED"} <= _codes(analysis)


def test_claim_evidence_lifts_a_claim_in_the_cli(tmp_path):
    claim = "c == 1"
    pinned = formal_trust.statement_sha256(claim)
    evidence = {
        claim: {
            "statement_audit": {"statement_sha256": pinned, "fidelity": "EQUIVALENT", "lint_open_unreviewed": 0},
            "kernel_check": _check(statement_sha256=pinned),
        }
    }
    h = _write(tmp_path / "h.json", REPAIRED)
    e = _write(tmp_path / "e.json", evidence)
    out = tmp_path / "raw"
    assert _cli(["formal", "run", "--hypothesis", h, "--claim-evidence", e, "--out", str(out), "--name", "ev"]) == 0
    assert _cli(["formal", "analyze", str(out / "ev.meta.json")]) == 0
    rungs = {t["claim"]: t["rung"] for t in _load(out / "ev.analysis.json")["claim_trust"]}
    assert rungs == {"c == 1": "KERNEL_CHECKED", "g > 0": "STATEMENT_PUBLIC"}


def test_formal_fidelity_is_two_phase(tmp_path, capsys):
    spec = _write(tmp_path / "spec.json", SPEC)
    out = tmp_path / "raw"
    assert _cli(["formal", "fidelity", "--spec", spec, "--out", str(out), "--name", "fid"]) == 0
    meta = _load(out / "fid.meta.json")
    assert meta["subcommand"] == "formal fidelity" and meta["formal_status"] == "DECIDED"
    assert "spec" not in meta["parameters"] and meta["parameters"]["input_kind"] == "fidelity"
    capsys.readouterr()
    assert _cli(["formal", "analyze", str(out / "fid.meta.json")]) == 0
    assert "fidelity=STRONGER" in capsys.readouterr().out
    analysis = _load(out / "fid.analysis.json")
    assert analysis["assessment"]["reproduces_run"] is True and analysis["verdict"] == {"fidelity": "STRONGER"}
    assert [d["report"] for d in formal_pipeline.report_digests(analysis)] == ["fidelity"]


def test_a_fabricated_fidelity_verdict_is_not_reproduced(tmp_path):
    spec = _write(tmp_path / "spec.json", SPEC)
    out = tmp_path / "raw"
    _cli(["formal", "fidelity", "--spec", spec, "--out", str(out), "--name", "fid"])
    response_path = out / "fid.response.json"
    response = _load(response_path)
    response["reports"]["fidelity"]["relation"] = "EQUIVALENT"
    _write(response_path, json.dumps(response, indent=2))
    meta = _load(out / "fid.meta.json")
    meta["outputs"][1]["sha256"] = formal_provenance.sha256_bytes(response_path.read_bytes())
    _write(out / "fid.meta.json", meta)
    assert _cli(["formal", "analyze", str(out / "fid.meta.json")]) == 12


def test_an_undecided_fidelity_run_exits_10(tmp_path):
    spec = _write(
        tmp_path / "s.json", {"theorem": "t", "parameters": [{"name": "p"}], "paper": "p > 2", "lean": "1/(p-2) > 0"}
    )
    assert _cli(["formal", "fidelity", "--spec", spec, "--out", str(tmp_path / "raw"), "--name", "u"]) == 10
    assert _load(tmp_path / "raw" / "u.response.json")["formal_status"] == "UNDECIDED"


def test_formal_lean_lint_is_two_phase(tmp_path, capsys):
    lean = _write(tmp_path / "Bound.lean", LEAN)
    out = tmp_path / "raw"
    assert _cli(["formal", "lean-lint", "--file", lean, "--out", str(out), "--name", "lint"]) == 0
    assert _cli(["formal", "analyze", str(out / "lint.meta.json")]) == 0
    assert "lean_lint.open=1" in capsys.readouterr().out
    analysis = _load(out / "lint.analysis.json")
    assert analysis["assessment"]["reproduces_run"] is True
    assert analysis["verdict"]["lean_lint"] == {"open": 1, "discharged": 1}
    assert _cli(["formal", "lean-lint", "--file", str(tmp_path / "missing.lean"), "--out", str(out)]) == 3


def test_formal_trust_prints_the_ladder(tmp_path, capsys):
    e = _write(tmp_path / "e.json", [_evidence(), _evidence(kernel_check=_check(status="NOT_KERNEL_CHECKED"))])
    assert _cli(["formal", "trust", "--evidence", e]) == 0
    printed = json.loads(capsys.readouterr().out)
    assert [t["rung"] for t in printed["claim_trust"]] == ["INDEPENDENTLY_REPRODUCED", "STATEMENT_AUDITED"]
    assert _codes(printed) == {"CLAIM_BELOW_KERNEL_CHECKED"}
    assert _cli(["formal", "trust", "--evidence", _write(tmp_path / "bad.json", {"claim": ""})]) == 9


# ---------------------------------------------------------------------------
# 5. API and evidence graph
# ---------------------------------------------------------------------------


def test_api_evaluate_reports_intent_and_claim_trust(api_client):
    response = api_client.post("/api/hypotheses/evaluate", json={"hypothesis": EXISTENCE, "default_probes": True})
    assert response.status_code == 200, response.text
    body = response.json()
    assert body["content_verdict"] == "VACUOUS_RELATIVE_TO_INTENT"
    assert body["intent_probe"]["probes"][0]["witness"] == {"g": 0, "d": 4, "c": 1}
    assert [t["rung"] for t in body["claim_trust"]] == ["STATEMENT_PUBLIC"]
    assert {"VACUOUS_RELATIVE_TO_INTENT", "CLAIM_BELOW_KERNEL_CHECKED"} <= _codes(body)
    plain = {k: v for k, v in EXISTENCE.items() if k != "non_witnesses"}
    assert "intent_probe" not in api_client.post("/api/hypotheses/evaluate", json={"hypothesis": plain}).json()
    bad = dict(EXISTENCE, non_witnesses=[{"label": "x", "state": {"g": 9}}])
    assert api_client.post("/api/hypotheses/evaluate", json={"hypothesis": bad}).status_code == 422


def test_api_evaluate_grades_claim_evidence(api_client):
    pinned = formal_trust.statement_sha256("c == 1")
    evidence = {
        "c == 1": {
            "statement_audit": {"statement_sha256": pinned, "fidelity": "EQUIVALENT", "lint_open_unreviewed": 0},
            "kernel_check": _check(statement_sha256=pinned, status="NOT_KERNEL_CHECKED"),
        }
    }
    body = api_client.post("/api/hypotheses/evaluate", json={"hypothesis": REPAIRED, "claim_evidence": evidence}).json()
    assert {t["claim"]: t["rung"] for t in body["claim_trust"]} == {
        "c == 1": "STATEMENT_AUDITED",
        "g > 0": "STATEMENT_PUBLIC",
    }


def test_api_fidelity_compare(api_client):
    body = api_client.post("/api/fidelity/compare", json=dict(SPEC, integer_values={"n": [2, 3]})).json()
    assert body["relation"] == "STRONGER" and body["formal_status"] == "DECIDED"
    assert body["cross_check"]["relation"] == "STRONGER" and body["provenance"]["input_sha256"]
    weaker = api_client.post("/api/fidelity/compare", json=dict(SPEC, lean="alpha > max(1, n*(1/2 - 1/p))")).json()
    assert weaker["relation"] == "WEAKER" and weaker["paper_only_witness"] is not None
    assert api_client.post("/api/fidelity/compare", json=dict(SPEC, lean="alpha >")).status_code == 422
    assert api_client.post("/api/fidelity/compare", json={"theorem": "t"}).status_code == 422


def test_api_lean_lint(api_client):
    body = api_client.post("/api/fidelity/lean-lint", json={"source": LEAN, "file": "Bound.lean"}).json()
    assert {f["kind"]: f["status"] for f in body["findings"]} == {"DIVISION": "DISCHARGED", "DERIV": "OPEN"}
    assert body["formal_status"] == "DECIDED" and body["provenance"]["operation"] == "lean_lint"
    assert api_client.post("/api/fidelity/lean-lint", json={"source": ""}).status_code == 422


def test_api_trust_assess(api_client):
    claims = [_evidence(), _evidence(claim="other", statement=None)]
    body = api_client.post("/api/trust/assess", json={"claims": claims}).json()
    assert [t["rung"] for t in body["claim_trust"]] == ["INDEPENDENTLY_REPRODUCED", "CLAIMED"]
    assert _codes(body) == {"CLAIM_BELOW_KERNEL_CHECKED"}
    assert api_client.post("/api/trust/assess", json={"claims": []}).status_code == 422


def test_new_endpoints_are_catalogued_as_read_only_and_deterministic(api_client):
    catalogue = {(c["method"], c["path"]): c for c in api_client.get("/api/capabilities").json()["capabilities"]}
    for path in ("/api/fidelity/compare", "/api/fidelity/lean-lint", "/api/trust/assess"):
        entry = catalogue[("POST", path)]
        assert entry["operationClass"] == "READ_ONLY" and entry["determinism"] == "DETERMINISTIC"


def test_evidence_graph_carries_claim_trust_and_the_intent_gap():
    graph = resolve({"target": {"type": "FORMAL_HYPOTHESIS", "hypothesis": EXISTENCE}})
    focus = next(n for n in graph["nodes"] if n["id"] == graph["focus"])
    assert focus["attributes"]["claim_trust"] == {"c == 1": "STATEMENT_PUBLIC"}
    verdict = next(n for n in graph["nodes"] if n["kind"] == "verification")
    assert verdict["attributes"]["content_verdict"] == "VACUOUS_RELATIVE_TO_INTENT"
    assert verdict["attributes"]["intent_probe"]["declared_non_witnesses_satisfied"] == ["free theory"]
    assert "vacuous_relative_to_intent" in {g["kind"] for g in graph["gaps"]}


def test_the_intent_probe_is_domain_neutral_on_a_biomedical_hypothesis():
    # "High pTau217 predicts decline", formalized carelessly as "decline" alone: the prediction still holds when the
    # biomarker is held at a constant with no signal, so the biomarker does no work in the claim.
    careless = {
        "hypothesis_id": "PTAU-DECLINE",
        "variables": [{"name": "ptau", "domain": [0, 1, 2, 3]}, {"name": "decline", "domain": [0, 1]}],
        "claims": ["decline == 1"],
        "non_witnesses": [{"label": "biomarker constant at baseline", "state": {"ptau": 0, "decline": 1}}],
    }
    report = HypothesisEvaluator.evaluate(hypothesis_from_dict(careless)).to_dict()
    assert report["content_verdict"] == "VACUOUS_RELATIVE_TO_INTENT"
    assert report["intent_probe"]["probes"][0]["witness"] == {"ptau": 0, "decline": 1}
    linked = dict(careless, claims=["ptau < 2 or decline == 1", "ptau >= 2 or decline == 0"])
    report = HypothesisEvaluator.evaluate(hypothesis_from_dict(linked)).to_dict()
    assert report["content_verdict"] == "FALSIFIABLE"
    assert report["intent_probe"]["probes"][0]["outcome"] == "FORBIDDEN"
