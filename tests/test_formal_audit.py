"""Auditable formal verdicts (ADR-DISCOVERY-068): provenance, non-verdict statuses, thresholds, relays, two-phase CLI.

No model is called: formalizer outputs come from a seeded fake client.
"""

import argparse
import json
import socket
from pathlib import Path

import pytest
import z3

from python.cli import formal as formal_cli
from python.discovery import (
    evidence_service,
    formal_pipeline,
    formal_provenance,
    formal_smt,
    formal_status,
    formal_thresholds,
)
from python.discovery.formal_hypothesis import (
    ContentVerdict,
    FormalHypothesisError,
    Hypothesis,
    HypothesisEvaluator,
    Relation,
    SolverUndecided,
    ThresholdExceeded,
    Variable,
    hypothesis_from_dict,
    hypothesis_to_dict,
)
from python.discovery.formal_status import FormalStatus
from python.discovery.formalization_gate import GateStatus, gate, sampling_schedule
from python.discovery.formalizer import FormalizationStatus, parse_formalization, prompt_sha256

FINITE = {
    "hypothesis_id": "H1",
    "variables": [{"name": "a", "domain": [0, 1, 2]}, {"name": "b", "domain": [0, 1, 2]}],
    "assumptions": ["a >= 0"],
    "claims": ["not (a > 1) or (b > 0)"],
}
RIVAL = {
    "hypothesis_id": "H2",
    "variables": [{"name": "a", "domain": [0, 1, 2]}, {"name": "b", "domain": [0, 1, 2]}],
    "claims": ["b > 0"],
}
CONTINUOUS = {
    "hypothesis_id": "C1",
    "variables": [{"name": "x", "continuous": True, "lower": 0, "upper": 10}],
    "claims": ["x <= 5"],
}
SCHEMA = [{"name": "x", "domain": [0, 1, 2, 3]}]


def _h(data=FINITE) -> Hypothesis:
    return hypothesis_from_dict(data)


def _out(*claims):
    return json.dumps({"variables": SCHEMA, "scope": None, "assumptions": [], "claims": list(claims)})


class SeededClient:
    def __init__(self, outputs, model="fake"):
        self.outputs, self.model, self.calls = outputs, model, 0

    def complete(self, messages, temperature=0.0, seed=0):
        self.calls += 1
        return self.outputs[seed % len(self.outputs)]


class FailingClient:
    model = "down"

    def complete(self, messages, temperature=0.0, seed=0):
        raise ConnectionError("refused")


@pytest.fixture(autouse=True)
def _no_project_thresholds(monkeypatch, tmp_path):
    """Isolate every test from a stray project override file."""
    monkeypatch.delenv(formal_thresholds.OVERRIDE_ENV, raising=False)
    monkeypatch.chdir(tmp_path)


def _codes(report) -> list:
    items = report["mandatory_relays"] if isinstance(report, dict) else report.mandatory_relays
    return [r["code"] for r in items]


def _undecided_solver(monkeypatch):
    class Unknown(z3.Solver):
        def check(self, *args):
            return z3.unknown

        def reason_unknown(self):
            return "timeout"

    monkeypatch.setattr(formal_smt.z3, "Solver", Unknown)


# ---------------------------------------------------------------------------
# 1. Provenance
# ---------------------------------------------------------------------------


def test_evaluation_report_carries_full_provenance():
    report = HypothesisEvaluator.evaluate(_h(), max_examples=3)
    p = report.to_dict()["provenance"]
    assert p["engine"] == "coresearcher" and p["engine_version"] not in ("", None)
    assert p["z3_version"] == z3.get_version_string()
    assert p["backend"] == "enumeration" and p["solver_timeout_ms"] is None
    assert p["operation"] == "evaluate"
    inputs = {"hypothesis": hypothesis_to_dict(_h()), "observations": [], "max_examples": 3, "backend": "auto"}
    assert p["input_sha256"] == formal_provenance.sha256_canonical({"operation": "evaluate", **inputs})
    assert p["output_sha256"] == formal_provenance.sha256_canonical(report.body())
    assert p["threshold_set"] == formal_thresholds.FORMAL_DEFAULTS.tag
    assert p["thresholds_applied"]["max_states"] == 2_000_000
    assert p["timestamp"].endswith("Z")


def test_smt_reports_record_the_solver_timeout():
    report = HypothesisEvaluator.evaluate(_h(CONTINUOUS))
    assert report.provenance["backend"] == "smt"
    assert report.provenance["solver_timeout_ms"] == 10_000


def test_comparison_and_consequence_reports_carry_provenance():
    comparison = HypothesisEvaluator.compare(_h(), _h(RIVAL)).to_dict()
    consequence = HypothesisEvaluator.entails(_h(), "not (a == 2) or b >= 1").to_dict()
    assert comparison["provenance"]["operation"] == "compare"
    assert consequence["provenance"]["operation"] == "entails"
    for report in (comparison, consequence):
        assert len(report["provenance"]["input_sha256"]) == 64
        assert len(report["provenance"]["output_sha256"]) == 64


def test_digests_are_stable_and_follow_the_input():
    one = HypothesisEvaluator.evaluate(_h()).provenance
    two = HypothesisEvaluator.evaluate(_h()).provenance
    assert (one["input_sha256"], one["output_sha256"]) == (two["input_sha256"], two["output_sha256"])
    changed = HypothesisEvaluator.evaluate(_h({**FINITE, "claims": ["b > 0"]})).provenance
    assert changed["input_sha256"] != one["input_sha256"]
    assert changed["output_sha256"] != one["output_sha256"]


def test_gate_provenance_names_the_formalizer_and_covers_raw_outputs():
    outputs = [_out("x > 1"), _out("x >= 2"), _out("x > 1")]
    samples = [parse_formalization(o, "H", SCHEMA) for o in outputs]
    result = gate(samples, sampling_schedule(["m"], 3), {"prose": "x exceeds one"})
    p = result.to_dict()["provenance"]
    assert p["operation"] == "formalize_gate"
    assert p["formalizer"]["models"] == ["m"]
    assert p["formalizer"]["prompt_sha256"] == prompt_sha256()
    assert p["formalizer"]["seeds"] == [0, 1, 2]
    assert p["formalizer"]["temperatures"] == [0.0, 0.7, 0.7]
    other = gate([parse_formalization(o, "H", SCHEMA) for o in reversed(outputs)], sampling_schedule(["m"], 3))
    assert other.provenance["input_sha256"] != p["input_sha256"]


def test_digests_use_the_evidence_graph_convention():
    data = {"b": [1, 2], "a": "é", "n": None}
    assert evidence_service._canonical(data) == formal_provenance.canonical(data)
    assert formal_provenance.canonical(data) == b'{"a":"\xc3\xa9","b":[1,2],"n":null}'


def test_hypothesis_to_dict_round_trips():
    for data in (FINITE, CONTINUOUS):
        assert hypothesis_to_dict(hypothesis_from_dict(hypothesis_to_dict(_h(data)))) == hypothesis_to_dict(_h(data))


def test_existing_report_fields_are_unchanged():
    report = HypothesisEvaluator.evaluate(_h()).to_dict()
    assert report["content_verdict"] == "FALSIFIABLE" and report["backend"] == "enumeration"
    assert report["formal_status"] == "DECIDED"
    assert set(report) - {"formal_status", "mandatory_relays", "provenance"} == set(
        HypothesisEvaluator.evaluate(_h()).body()
    )


# ---------------------------------------------------------------------------
# 2. Non-verdict statuses
# ---------------------------------------------------------------------------


def test_only_decided_is_a_verdict():
    assert formal_status.is_verdict(FormalStatus.DECIDED)
    assert all(not formal_status.is_verdict(s) for s in formal_status.NON_VERDICT)
    assert {s.value for s in formal_status.NON_VERDICT} >= {
        "BLOCKED",
        "UNDECIDED",
        "NOT_KERNEL_CHECKED",
        "FORMALIZATION_AMBIGUOUS",
    }


def test_existing_enums_keep_working_and_map_onto_the_vocabulary():
    assert GateStatus.FORMALIZATION_AMBIGUOUS.value == "FORMALIZATION_AMBIGUOUS"
    assert ContentVerdict.FALSIFIABLE.value == "FALSIFIABLE" and Relation.EQUIVALENT.value == "EQUIVALENT"
    assert FormalizationStatus.PARSED.value == "PARSED"
    assert formal_status.from_gate_status("CONSISTENT") is FormalStatus.DECIDED
    assert formal_status.from_gate_status("SINGLE_SAMPLE") is FormalStatus.DECIDED
    assert formal_status.from_gate_status("FORMALIZATION_AMBIGUOUS") is FormalStatus.FORMALIZATION_AMBIGUOUS
    assert formal_status.from_gate_status("FORMALIZATION_FAILED") is FormalStatus.FORMALIZATION_FAILED


def test_a_solver_timeout_is_undecided_never_a_verdict(monkeypatch):
    _undecided_solver(monkeypatch)
    with pytest.raises(SolverUndecided):
        HypothesisEvaluator.evaluate(_h(CONTINUOUS))
    response = formal_pipeline.compute(formal_pipeline.make_request(hypothesis=CONTINUOUS))
    assert response["formal_status"] == "UNDECIDED"
    assert response["reports"]["evaluation"] is None
    assert formal_pipeline.verdict(response) == {}
    assert formal_status.exit_code(FormalStatus.UNDECIDED) == 10


def test_an_undecided_pair_never_counts_as_agreement(monkeypatch):
    samples = [parse_formalization(_out("x > 1"), "H", SCHEMA) for _ in range(3)]
    real_compare = HypothesisEvaluator.compare

    def undecided_compare(a, b, max_examples=5, backend="auto"):
        raise SolverUndecided("timeout")

    monkeypatch.setattr(HypothesisEvaluator, "compare", staticmethod(undecided_compare))
    result = gate(samples)
    monkeypatch.setattr(HypothesisEvaluator, "compare", real_compare)
    assert result.status == GateStatus.FORMALIZATION_AMBIGUOUS
    assert not formal_status.is_verdict(result.formal_status)
    assert result.undecided == [0, 1, 2]
    assert all(s.get("formal_status") == "UNDECIDED" for s in result.to_dict()["samples"])


def test_a_missing_formalizer_model_is_blocked():
    response = formal_pipeline.compute(formal_pipeline.make_request(prose="x exceeds one"), clients={})
    assert response["formal_status"] == "BLOCKED"
    assert formal_status.exit_code(FormalStatus.BLOCKED, response["_exception"]) == formal_status.EXIT_DEPENDENCY


def test_an_unreachable_formalizer_is_blocked_with_the_endpoint_code():
    response = formal_pipeline.compute(
        formal_pipeline.make_request(prose="x exceeds one"), clients={"down": FailingClient()}
    )
    assert response["formal_status"] == "BLOCKED"
    assert formal_status.exit_code(FormalStatus.BLOCKED, response["_exception"]) == formal_status.EXIT_ENDPOINT


def test_a_state_space_over_the_cap_is_blocked_not_invalid():
    small = formal_thresholds.FORMAL_DEFAULTS.with_overrides({"max_states": 4}, "flag")
    with formal_thresholds.using(small):
        with pytest.raises(ThresholdExceeded):
            _h()
        response = formal_pipeline.compute(formal_pipeline.make_request(hypothesis=FINITE))
    assert response["formal_status"] == "BLOCKED"
    assert formal_status.exit_code(FormalStatus.BLOCKED, response["_exception"]) == formal_status.EXIT_THRESHOLD


def test_malformed_input_is_invalid_and_bugs_are_not_swallowed():
    response = formal_pipeline.compute(formal_pipeline.make_request(hypothesis={"variables": "nope"}))
    assert response["formal_status"] == "INVALID_INPUT"
    with pytest.raises(KeyError):
        formal_status.classify(KeyError("a bug"))


def test_lean_theorems_are_not_kernel_checked():
    request = formal_pipeline.make_request(
        hypothesis=CONTINUOUS, consequences=["x <= 6"], include_lean=True, max_examples=1
    )
    response = formal_pipeline.compute(request)
    assert response["lean"][0]["status"] == "NOT_KERNEL_CHECKED"
    assert "LEAN_NOT_KERNEL_CHECKED" in _codes(response)


def test_api_entails_with_lean_carries_the_relay(api_client):
    response = api_client.post(
        "/api/hypotheses/entails",
        json={"hypothesis": CONTINUOUS, "consequence": "x <= 6", "include_lean": True},
    )
    assert response.status_code == 200
    body = response.json()
    assert body["lean_status"] == "NOT_KERNEL_CHECKED"
    assert "LEAN_NOT_KERNEL_CHECKED" in _codes(body)
    assert body["provenance"]["operation"] == "entails"


# ---------------------------------------------------------------------------
# 3. Thresholds
# ---------------------------------------------------------------------------


def test_defaults_are_versioned_and_recorded():
    record = formal_thresholds.FORMAL_DEFAULTS.record()
    assert record["threshold_set"].startswith("formal@")
    assert set(record["thresholds_applied"]) == {
        "max_states",
        "max_assumptions_for_conflict_search",
        "solver_timeout_ms",
        "gate_samples",
        "gate_max_samples",
        "gate_temperature",
        "gate_majority_fraction",
        "formalizer_temperature",
        "formalizer_seed",
    }
    assert set(record["threshold_sources"].values()) == {"default"}
    assert record["threshold_provenance"]


def test_an_unset_threshold_raises_and_never_defaults():
    unset = formal_thresholds.FORMAL_DEFAULTS.with_overrides({"solver_timeout_ms": None}, "project", "unset")
    with pytest.raises(formal_thresholds.ThresholdError):
        unset.get("solver_timeout_ms")
    assert "solver_timeout_ms" in unset.record()["thresholds_unresolved"]
    with formal_thresholds.using(unset):
        with pytest.raises(formal_thresholds.ThresholdError):
            HypothesisEvaluator.evaluate(_h(CONTINUOUS))
        response = formal_pipeline.compute(formal_pipeline.make_request(hypothesis=CONTINUOUS))
    assert response["formal_status"] == "BLOCKED"
    declared = formal_thresholds.ThresholdSet("t", "1", {"k": formal_thresholds.UNRESOLVED}, "none")
    with pytest.raises(formal_thresholds.ThresholdError):
        declared.get("k")
    with pytest.raises(formal_thresholds.ThresholdError):
        declared.get("unknown")


def test_project_override_file_is_applied_and_recorded(monkeypatch, tmp_path):
    path = tmp_path / ".coresearcher" / "formal_thresholds.json"
    path.parent.mkdir()
    path.write_text(
        json.dumps({"set": "formal", "provenance": "slow cluster", "overrides": {"solver_timeout_ms": 30000}}),
        encoding="utf-8",
    )
    nested = tmp_path / "a" / "b"
    nested.mkdir(parents=True)
    monkeypatch.chdir(nested)
    assert formal_thresholds.find_override_file().resolve() == path.resolve()
    report = HypothesisEvaluator.evaluate(_h(CONTINUOUS))
    p = report.provenance
    assert p["solver_timeout_ms"] == 30000
    assert p["threshold_sources"]["solver_timeout_ms"] == "project"
    assert "slow cluster" in p["threshold_provenance"]
    assert "THRESHOLDS_OVERRIDDEN" in _codes(report)


@pytest.mark.parametrize(
    "content",
    [
        "not json",
        json.dumps({"set": "formal", "overrides": {"solver_timeout_ms": 1}}),  # No provenance.
        json.dumps({"set": "formal", "provenance": "x", "overrides": {"no_such_threshold": 1}}),
        json.dumps({"set": "other", "provenance": "x", "overrides": {}}),
    ],
)
def test_a_bad_override_file_raises_instead_of_being_skipped(tmp_path, content):
    path = tmp_path / "t.json"
    path.write_text(content, encoding="utf-8")
    with pytest.raises(formal_thresholds.ThresholdError):
        formal_thresholds.load_thresholds(path)


def test_override_env_var_naming_a_missing_file_raises(monkeypatch, tmp_path):
    monkeypatch.setenv(formal_thresholds.OVERRIDE_ENV, str(tmp_path / "missing.json"))
    with pytest.raises(formal_thresholds.ThresholdError):
        formal_thresholds.active()


def test_the_solver_uses_the_threshold_in_force(monkeypatch):
    seen = []
    real = z3.Solver.set

    def spy(self, *args, **kwargs):
        seen.append(args)
        return real(self, *args, **kwargs)

    monkeypatch.setattr(z3.Solver, "set", spy)
    with formal_thresholds.using(formal_thresholds.FORMAL_DEFAULTS.with_overrides({"solver_timeout_ms": 1234})):
        HypothesisEvaluator.evaluate(_h(CONTINUOUS))
    assert ("timeout", 1234) in seen


def test_the_gate_majority_is_a_threshold():
    samples = [parse_formalization(o, "H", SCHEMA) for o in (_out("x > 1"), _out("x >= 2"), _out("x < 1"))]
    assert gate(samples).status == GateStatus.CONSISTENT  # 2 of 3 > 0.5.
    strict = formal_thresholds.FORMAL_DEFAULTS.with_overrides({"gate_majority_fraction": 0.7})
    with formal_thresholds.using(strict):
        result = gate(samples)
    assert result.status == GateStatus.FORMALIZATION_AMBIGUOUS
    assert result.provenance["thresholds_applied"]["gate_majority_fraction"] == 0.7


def test_the_sampling_schedule_follows_the_thresholds():
    custom = formal_thresholds.FORMAL_DEFAULTS.with_overrides({"gate_temperature": 0.3, "formalizer_seed": 10})
    with formal_thresholds.using(custom):
        specs = sampling_schedule(["m"], 3)
    assert [(s.temperature, s.seed) for s in specs] == [(0.0, 10), (0.3, 11), (0.3, 12)]


def test_existing_constants_remain_the_versioned_defaults():
    from python.discovery import formal_hypothesis, formalization_gate

    values = formal_thresholds.FORMAL_DEFAULTS.values
    assert formal_hypothesis.MAX_STATES == values["max_states"]
    assert formal_smt.SOLVER_TIMEOUT_MS == values["solver_timeout_ms"]
    assert formalization_gate.DEFAULT_SAMPLES == values["gate_samples"] == 5
    assert formalization_gate.MAX_SAMPLES == values["gate_max_samples"] == 7


# ---------------------------------------------------------------------------
# 4. Relays
# ---------------------------------------------------------------------------


def test_every_verdict_carries_formal_not_empirical_and_its_backend_caveat():
    enum_report = HypothesisEvaluator.evaluate(_h())
    smt_report = HypothesisEvaluator.evaluate(_h(CONTINUOUS))
    comparison = HypothesisEvaluator.compare(_h(), _h(RIVAL))
    assert _codes(enum_report) == ["FORMAL_NOT_EMPIRICAL", "ENUMERATION_DECLARED_DOMAINS_ONLY"]
    assert _codes(smt_report) == ["FORMAL_NOT_EMPIRICAL", "SMT_FIXED_SIZE_ONLY"]
    assert "FORMAL_NOT_EMPIRICAL" in _codes(comparison)
    assert all(set(r) == {"code", "message"} for r in enum_report.to_dict()["mandatory_relays"])


def test_entailment_relays_name_the_trivial_readings():
    vacuous = Hypothesis("V", [Variable("a", (0, 1))], claims=["a > 5"])
    assert "VACUOUS_ENTAILMENT" in _codes(HypothesisEvaluator.entails(vacuous, "a == 0"))
    by_assumptions = Hypothesis("A", [Variable("a", (0, 1, 2))], claims=["a < 2"], assumptions=["a >= 1"])
    report = HypothesisEvaluator.entails(by_assumptions, "a >= 1")
    assert report.entailed and "ENTAILED_BY_ASSUMPTIONS_ALONE" in _codes(report)
    real = HypothesisEvaluator.entails(by_assumptions, "a == 1")
    assert real.follows_from_claims and not {"VACUOUS_ENTAILMENT", "ENTAILED_BY_ASSUMPTIONS_ALONE"} & set(_codes(real))


def test_gate_relays():
    consistent = gate([parse_formalization(_out("x > 1"), "H", SCHEMA) for _ in range(3)])
    single = gate([parse_formalization(_out("x > 1"), "H", SCHEMA)])
    assert _codes(consistent) == ["FORMALIZATION_IS_DRAFT"]
    assert _codes(single) == ["FORMALIZATION_IS_DRAFT", "GATE_SINGLE_SAMPLE"]


def test_unregistered_relay_codes_are_rejected():
    with pytest.raises(KeyError):
        formal_status.relay("MADE_UP")
    assert formal_status.relay("FORMAL_NOT_EMPIRICAL")["code"] == "FORMAL_NOT_EMPIRICAL"


# ---------------------------------------------------------------------------
# 5. Two-phase CLI
# ---------------------------------------------------------------------------


def _parse_cli(argv):
    parser = argparse.ArgumentParser()
    formal_cli.add_parser(parser.add_subparsers(dest="command"))
    return parser.parse_args(argv)


def _cli(argv, clients=None):
    args = _parse_cli(argv)
    if args.formal_command == "run" and clients is not None:
        return formal_cli.run(args, clients=clients)
    return formal_cli.main(args)


def _write(path: Path, data) -> str:
    path.write_text(json.dumps(data), encoding="utf-8")
    return str(path)


@pytest.fixture
def stored_run(tmp_path):
    h = _write(tmp_path / "h.json", FINITE)
    r = _write(tmp_path / "r.json", RIVAL)
    out = tmp_path / "raw"
    code = _cli(
        ["formal", "run", "--hypothesis", h, "--rival", r, "--consequence", "not (a == 2) or b >= 1"]
        + ["--out", str(out), "--name", "t1"]
    )
    assert code == 0
    return out


def test_run_writes_request_response_and_a_checksummed_sidecar(stored_run, capsys):
    meta = json.loads((stored_run / "t1.meta.json").read_text(encoding="utf-8"))
    assert meta["tool"] == "coresearcher" and meta["subcommand"] == "formal run"
    assert [o["path"] for o in meta["outputs"]] == ["t1.request.json", "t1.response.json"]
    for entry in meta["outputs"]:
        data = (stored_run / entry["path"]).read_bytes()
        assert entry["sha256"] == formal_provenance.sha256_bytes(data) and entry["bytes"] == len(data)
    for key in ("cli_version", "env_version", "timestamp", "completed", "threshold_set", "mandatory_relays"):
        assert key in meta
    assert meta["formal_status"] == "DECIDED"
    assert "FORMAL_NOT_EMPIRICAL" in _codes(meta)
    response = json.loads((stored_run / "t1.response.json").read_text(encoding="utf-8"))
    assert response["reports"]["evaluation"]["content_verdict"] == "FALSIFIABLE"
    assert len(response["reports"]["comparisons"]) == 1 and len(response["reports"]["consequences"]) == 1


def test_run_prints_only_the_three_paths(tmp_path, capsys):
    h = _write(tmp_path / "h.json", FINITE)
    _cli(["formal", "run", "--hypothesis", h, "--out", str(tmp_path / "o"), "--name", "p"])
    lines = capsys.readouterr().out.strip().splitlines()
    assert [Path(line).name for line in lines] == ["p.request.json", "p.response.json", "p.meta.json"]


def test_analyze_reproduces_the_run_byte_for_byte_on_comparable_fields(stored_run):
    assert _cli(["formal", "analyze", str(stored_run / "t1.meta.json")]) == 0
    analysis = json.loads((stored_run / "t1.analysis.json").read_text(encoding="utf-8"))
    response_bytes = (stored_run / "t1.response.json").read_bytes()
    assert analysis["record_type"] == "analysis"
    assert analysis["source"] == "t1.response.json"
    assert analysis["source_sha256"] == formal_provenance.sha256_bytes(response_bytes)
    assert analysis["threshold_set"] == formal_thresholds.FORMAL_DEFAULTS.tag
    assert analysis["assessment"]["reproduces_run"] is True and analysis["assessment"]["mismatches"] == []
    assert analysis["verdict"]["content_verdict"] == "FALSIFIABLE"
    assert analysis["verdict"]["relations"] == {"H2": "WEAKER"}
    assert analysis["metrics"]["evaluation"]["omega_size"] == 9
    assert "FORMAL_NOT_EMPIRICAL" in _codes(analysis)
    run_reports = json.loads(response_bytes)["reports"]
    assert formal_provenance.canonical(formal_cli.comparable(run_reports)) == formal_provenance.canonical(
        formal_cli.comparable(analysis["reports"])
    )


def test_analyze_reproduces_a_prose_run_offline(tmp_path, monkeypatch):
    client = SeededClient([_out("x > 1"), _out("x >= 2"), _out("x > 1")], model="m")
    out = tmp_path / "raw"
    code = _cli(
        ["formal", "run", "--prose", "x exceeds one", "--samples", "3", "--out", str(out), "--name", "p"], {"m": client}
    )
    assert code == 0 and client.calls == 3
    response = json.loads((out / "p.response.json").read_text(encoding="utf-8"))
    assert response["formalization_gate"]["status"] == "CONSISTENT"
    assert response["formalizer"]["raw_outputs"][1] == _out("x >= 2")
    request = json.loads((out / "p.request.json").read_text(encoding="utf-8"))
    assert request["formalizer_messages"][0]["role"] == "system"

    from python.discovery import formalizer

    def no_model(*args, **kwargs):
        raise AssertionError("analyze called the formalizer")

    monkeypatch.setattr(formalizer.ChatClient, "complete", no_model)
    monkeypatch.setenv("FORMALIZER_MODEL", "would-be-called")
    assert _cli(["formal", "analyze", str(out / "p.meta.json")]) == 0
    analysis = json.loads((out / "p.analysis.json").read_text(encoding="utf-8"))
    assert analysis["assessment"]["reproduces_run"] is True
    assert analysis["verdict"]["gate_status"] == "CONSISTENT"
    assert "FORMALIZATION_IS_DRAFT" in _codes(analysis)


def test_analyze_detects_a_fabricated_verdict(stored_run):
    """The reviewer's mechanical check: a response edited after the run (checksums re-forged) is not reproduced."""
    response_path = stored_run / "t1.response.json"
    response = json.loads(response_path.read_text(encoding="utf-8"))
    response["reports"]["evaluation"]["content_verdict"] = "UNFALSIFIABLE"
    response_path.write_text(json.dumps(response, indent=2) + "\n", encoding="utf-8")
    meta_path = stored_run / "t1.meta.json"
    meta = json.loads(meta_path.read_text(encoding="utf-8"))
    meta["outputs"][1] = formal_cli._output_entry(response_path)
    meta_path.write_text(json.dumps(meta), encoding="utf-8")
    assert _cli(["formal", "analyze", str(meta_path)]) == formal_status.EXIT_NOT_REPRODUCED
    analysis = json.loads((stored_run / "t1.analysis.json").read_text(encoding="utf-8"))
    assert analysis["assessment"]["reproduces_run"] is False
    assert analysis["verdict"]["content_verdict"] == "FALSIFIABLE"


def test_analyze_rejects_an_output_that_changed_after_the_run(stored_run):
    path = stored_run / "t1.response.json"
    path.write_text(path.read_text(encoding="utf-8").replace("FALSIFIABLE", "UNFALSIFIABLE"), encoding="utf-8")
    assert _cli(["formal", "analyze", str(stored_run / "t1.meta.json")]) == formal_status.EXIT_ARTIFACT
    assert not (stored_run / "t1.analysis.json").exists()


def test_analyze_keeps_an_identical_record_and_refuses_a_differing_one(stored_run):
    meta = str(stored_run / "t1.meta.json")
    analysis = stored_run / "t1.analysis.json"
    assert _cli(["formal", "analyze", meta]) == 0
    first = analysis.read_bytes()
    assert _cli(["formal", "analyze", meta]) == 0
    assert analysis.read_bytes() == first  # Identical analysis: not rewritten.
    changed = ["formal", "analyze", meta, "--threshold", "max_states=4"]
    assert _cli(changed) == formal_status.EXIT_REFUSAL
    assert analysis.read_bytes() == first
    elsewhere = stored_run / "second.analysis.json"
    assert _cli(changed + ["--out", str(elsewhere)]) == formal_status.EXIT_THRESHOLD  # BLOCKED, not a verdict.
    second = json.loads(elsewhere.read_text(encoding="utf-8"))
    assert second["formal_status"] == "BLOCKED" and second["verdict"] == {}
    assert second["assessment"]["thresholds_match_run"] is False
    assert second["threshold_sources"]["max_states"] == "flag"
    assert _cli(changed + ["--overwrite"]) == formal_status.EXIT_THRESHOLD
    assert json.loads(analysis.read_text(encoding="utf-8"))["formal_status"] == "BLOCKED"


def test_analyze_refuses_network_access(stored_run, monkeypatch):
    def reach_out(*args, **kwargs):
        socket.create_connection(("example.org", 80), timeout=1)

    monkeypatch.setattr(formal_pipeline, "compute", reach_out)
    assert _cli(["formal", "analyze", str(stored_run / "t1.meta.json")]) == formal_status.EXIT_REFUSAL
    assert socket.create_connection is not None and socket.socket.connect.__name__ != "refuse"


def test_run_records_non_verdicts_with_their_exit_codes(tmp_path, monkeypatch):
    monkeypatch.delenv("FORMALIZER_MODEL", raising=False)
    monkeypatch.delenv("FORMALIZER_GATE_MODELS", raising=False)
    code = _cli(["formal", "run", "--prose", "x exceeds one", "--out", str(tmp_path), "--name", "b"])
    assert code == formal_status.EXIT_DEPENDENCY
    meta = json.loads((tmp_path / "b.meta.json").read_text(encoding="utf-8"))
    assert meta["formal_status"] == "BLOCKED" and meta["warnings"]
    assert _cli(["formal", "analyze", str(tmp_path / "b.meta.json")]) == formal_status.EXIT_ARTIFACT

    _undecided_solver(monkeypatch)
    c = _write(tmp_path / "c.json", CONTINUOUS)
    assert _cli(["formal", "run", "--hypothesis", c, "--out", str(tmp_path), "--name", "u"]) == 10
    assert json.loads((tmp_path / "u.response.json").read_text(encoding="utf-8"))["formal_status"] == "UNDECIDED"

    ambiguous = SeededClient([_out("x > 1"), _out("x < 1"), _out("x == 3")], model="m")
    code = _cli(
        ["formal", "run", "--prose", "p", "--samples", "3", "--out", str(tmp_path), "--name", "a"], {"m": ambiguous}
    )
    assert code == 11


def test_run_refuses_to_overwrite_an_existing_run(stored_run):
    h = _write(stored_run / "h.json", FINITE)
    assert _cli(["formal", "run", "--hypothesis", h, "--out", str(stored_run), "--name", "t1"]) == 9


def test_doctor_reports_capabilities(capsys, monkeypatch):
    monkeypatch.delenv("FORMALIZER_MODEL", raising=False)
    monkeypatch.delenv("FORMALIZER_GATE_MODELS", raising=False)
    assert _cli(["formal", "doctor"]) == 0
    report = json.loads(capsys.readouterr().out)
    assert report["z3"] == {"status": "available", "version": z3.get_version_string()}
    assert report["lean"]["status"] in ("available", "unavailable")
    assert report["formalizer"]["status"] == "unconfigured"
    assert report["formalizer"]["prompt_sha256"] == prompt_sha256()
    assert report["thresholds"]["threshold_set"] == formal_thresholds.FORMAL_DEFAULTS.tag
    assert "FORMAL_NOT_EMPIRICAL" in report["relay_codes"]


def test_the_main_cli_exposes_formal(monkeypatch, tmp_path, capsys):
    from python.cli import main as main_cli

    monkeypatch.setattr("sys.argv", ["coresearcher", "formal", "doctor"])
    with pytest.raises(SystemExit) as exc:
        main_cli.main()
    assert exc.value.code == 0
    assert json.loads(capsys.readouterr().out)["z3"]["status"] == "available"


def test_formal_hypothesis_error_stays_the_base_class():
    assert issubclass(SolverUndecided, FormalHypothesisError)
    assert issubclass(ThresholdExceeded, FormalHypothesisError)
