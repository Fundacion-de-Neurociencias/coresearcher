"""Tests for the formalizer self-consistency gate (ADR-DISCOVERY-064). No model is called."""

import json
import sys
from pathlib import Path

import pytest

from api.routers import hypotheses as hypotheses_router
from python.discovery import alzheimer_formal_scenario
from python.discovery.formalization_gate import (
    GateStatus,
    formalize_gated,
    gate,
    sampling_schedule,
)
from python.discovery.formalizer import parse_formalization

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts" / "benchmarks"))
import formalizer_bench  # noqa: E402

SCHEMA = [{"name": "x", "domain": [0, 1, 2, 3]}]


def _out(*claims, variables=None):
    return json.dumps({"variables": variables or SCHEMA, "scope": None, "assumptions": [], "claims": list(claims)})


def _parse(*outputs, schema=SCHEMA):
    return [parse_formalization(o, f"H-s{i}", schema) for i, o in enumerate(outputs)]


class SeededClient:
    """Returns a fixed output per seed, standing in for a model sampled at different seeds."""

    def __init__(self, outputs):
        self.outputs = outputs
        self.calls = []

    def complete(self, messages, temperature=0.0, seed=0):
        self.calls.append((temperature, seed))
        return self.outputs[seed % len(self.outputs)]


def test_schedule_keeps_sample_zero_frozen_and_cycles_models():
    specs = sampling_schedule(["a"], 3)
    assert [(s.temperature, s.seed) for s in specs] == [(0.0, 0), (0.7, 1), (0.7, 2)]
    mixed = sampling_schedule(["a", "b"], 5, temperature=0.5)
    assert [(s.model, s.temperature, s.seed) for s in mixed] == [
        ("a", 0.0, 0),
        ("b", 0.0, 0),
        ("a", 0.5, 1),
        ("b", 0.5, 1),
        ("a", 0.5, 2),
    ]
    with pytest.raises(ValueError):
        sampling_schedule([], 3)


def test_syntactically_different_but_equivalent_samples_are_consistent():
    result = gate(_parse(_out("x <= 1"), _out("not (x > 1)"), _out("x in (0, 1)")))
    assert result.status == GateStatus.CONSISTENT and result.passes
    assert result.classes == [[0, 1, 2]] and result.agreement == 1.0 and result.accepted == 0
    assert {p["relation"] for p in result.pairwise} == {"EQUIVALENT"}


def test_no_majority_is_ambiguous_and_accepts_nothing():
    result = gate(_parse(_out("x <= 1"), _out("x <= 0"), _out("x >= 2")))
    assert result.status == GateStatus.FORMALIZATION_AMBIGUOUS and not result.passes
    assert result.accepted is None and result.formalization is None
    assert len(result.classes) == 3 and result.agreement == pytest.approx(0.3333)
    body = result.to_dict()
    assert [c["content_verdict"] for c in body["classes"]] == ["FALSIFIABLE"] * 3


def test_a_tie_is_not_a_majority():
    result = gate(_parse(_out("x <= 1"), _out("x < 2"), _out("x <= 0"), _out("x == 0")))
    assert result.classes == [[0, 1], [2, 3]]
    assert result.status == GateStatus.FORMALIZATION_AMBIGUOUS


def test_failed_samples_count_against_the_majority():
    two_of_three = gate(_parse(_out("x <= 1"), "no json here", _out("x < 2")))
    assert two_of_three.status == GateStatus.CONSISTENT and two_of_three.accepted == 0
    one_of_three = gate(_parse(_out("x <= 1"), "no json", _out("x <= ")))
    assert one_of_three.status == GateStatus.FORMALIZATION_AMBIGUOUS
    none = gate(_parse("nothing", "nothing"))
    assert none.status == GateStatus.FORMALIZATION_FAILED and none.agreement == 0.0


def test_schema_mismatch_does_not_vote():
    other = _out("x <= 1", variables=[{"name": "x", "domain": [0, 1]}])
    result = gate(_parse(other, other, _out("x <= 1")))
    assert result.status == GateStatus.FORMALIZATION_AMBIGUOUS and result.classes == [[2]]


def test_the_majority_reading_wins_even_when_sample_zero_is_the_outlier():
    result = gate(_parse(_out("x <= 0"), _out("x <= 1"), _out("x < 2")))
    assert result.status == GateStatus.CONSISTENT and result.accepted == 1
    assert result.formalization.data["claims"] == ["x <= 1"]


def test_single_sample_gives_no_evidence_but_passes():
    result = gate(_parse(_out("x <= 1")))
    assert result.status == GateStatus.SINGLE_SAMPLE and result.passes and result.accepted == 0
    assert gate(_parse("no json")).status == GateStatus.FORMALIZATION_FAILED


def test_continuous_samples_are_compared_with_z3():
    cont = [{"name": "x", "continuous": True, "lower": 0, "upper": 10}, {"name": "y", "continuous": True}]
    outputs = [_out("y > 2 * x", variables=cont), _out("not (y <= x + x)", variables=cont)]
    result = gate(_parse(*outputs, _out("y > x", variables=cont), schema=cont))
    assert result.status == GateStatus.CONSISTENT and result.classes[0] == [0, 1]
    assert {p["relation"] for p in result.pairwise if p["a"] == 0 and p["b"] == 2} == {"STRONGER"}


def test_samples_over_different_variables_are_never_merged():
    a = _out("x <= 1")
    b = _out("z <= 1", variables=[{"name": "z", "domain": [0, 1, 2, 3]}])
    result = gate(_parse(a, b, b, schema=None))
    assert result.status == GateStatus.CONSISTENT and result.classes[0] == [1, 2]
    assert {p["relation"] for p in result.pairwise if p["a"] == 0} == {"UNDECIDED"}
    split = gate(_parse(a, b, schema=None))
    assert split.status == GateStatus.FORMALIZATION_AMBIGUOUS


def test_gate_never_reports_verified():
    assert "VERIFIED" not in {s.value for s in GateStatus}


def test_formalize_gated_draws_n_samples():
    client = SeededClient([_out("x <= 1"), _out("x < 2"), _out("x <= 0")])
    result = formalize_gated("x stays low", {"m": client}, n=3, variable_schema=SCHEMA)
    assert client.calls == [(0.0, 0), (0.7, 1), (0.7, 2)]
    assert result.status == GateStatus.CONSISTENT and result.n_samples == 3


# API and workbench -------------------------------------------------------------------------------------------------

CARRIER = {
    "variables": alzheimer_formal_scenario.variable_schema(),
    "scope": "amyloid == 'A+'",
    "claims": ["tau != 'T+' or outcome == 'accelerated_dementia'"],
}
DIFFERENT = dict(CARRIER, claims=["hub != 'high' or outcome == 'accelerated_dementia'"])
UNFALSIFIABLE = dict(CARRIER, claims=["tau == 'T+' or tau != 'T+'"])


def _fake_model(monkeypatch, outputs):
    class FakeClient:
        def __init__(self, *args, **kwargs):
            self.model = kwargs.get("model") or "fake"

        def complete(self, messages, temperature=0.0, seed=0):
            return json.dumps(outputs[seed % len(outputs)])

    monkeypatch.setenv("FORMALIZER_MODEL", "fake")
    monkeypatch.delenv("FORMALIZER_GATE_MODELS", raising=False)
    monkeypatch.setattr(hypotheses_router, "ChatClient", FakeClient)


def test_formalize_endpoint_blocks_an_ambiguous_formalization(api_client, monkeypatch):
    _fake_model(monkeypatch, [CARRIER, DIFFERENT, UNFALSIFIABLE])
    resp = api_client.post(
        "/api/hypotheses/formalize",
        json={"prose": "tau drives decline", "variable_schema": alzheimer_formal_scenario.variable_schema()},
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["status"] == "FORMALIZATION_AMBIGUOUS" and body["draft"] is True
    assert "evaluation" not in body and "comparisons" not in body and body["formal_hypothesis"] == {}
    gate_block = body["formalization_gate"]
    assert gate_block["passes"] is False and gate_block["n_samples"] == 5
    assert {c["content_verdict"] for c in gate_block["classes"]} == {"FALSIFIABLE", "UNFALSIFIABLE"}


def test_formalize_endpoint_accepts_a_consistent_formalization(api_client, monkeypatch):
    _fake_model(monkeypatch, [CARRIER, CARRIER, DIFFERENT])
    resp = api_client.post(
        "/api/hypotheses/formalize",
        json={
            "prose": "tau drives decline",
            "variable_schema": alzheimer_formal_scenario.variable_schema(),
            "samples": 3,
        },
    )
    body = resp.json()
    assert body["status"] == "PARSED" and body["formalization_gate"]["status"] == "CONSISTENT"
    assert body["formalization_gate"]["agreement"] == pytest.approx(0.6667)
    assert body["evaluation"]["content_verdict"] == "FALSIFIABLE"


def test_formalize_endpoint_rejects_too_many_samples(api_client, monkeypatch):
    _fake_model(monkeypatch, [CARRIER])
    resp = api_client.post("/api/hypotheses/formalize", json={"prose": "x", "samples": 50})
    assert resp.status_code == 422


def test_workbench_formal_block_carries_no_verdict_when_ambiguous(api_client, monkeypatch):
    _fake_model(monkeypatch, [CARRIER, DIFFERENT, UNFALSIFIABLE])
    resp = api_client.post(
        "/api/discovery/workbench/launch",
        json={"question": "Does tau drive decline?", "iterations": 1, "formalize_question": True},
    )
    assert resp.status_code == 200
    formal = resp.json()["formal"]
    assert formal["source"] == "formalizer" and formal["status"] == "FORMALIZATION_AMBIGUOUS"
    assert "evaluation" not in formal and formal["formalization_gate"]["passes"] is False


def test_workbench_formal_block_with_one_sample_keeps_the_old_behaviour(api_client, monkeypatch):
    _fake_model(monkeypatch, [CARRIER])
    resp = api_client.post(
        "/api/discovery/workbench/launch",
        json={"question": "q", "iterations": 1, "formalize_question": True, "formalizer_samples": 1},
    )
    formal = resp.json()["formal"]
    assert formal["status"] == "PARSED" and formal["formalization_gate"]["status"] == "SINGLE_SAMPLE"
    assert formal["evaluation"]["content_verdict"] == "FALSIFIABLE"


# Benchmark scorer --------------------------------------------------------------------------------------------------


def test_gate_scorer_on_gold_answers_accepts_everything():
    rows = []
    for item in formalizer_bench.load_items():
        gold = json.dumps(item["gold"])
        specs = sampling_schedule(["gold"], 3)
        rows.append(formalizer_bench.gate_item(item, [gold, gold, gold], specs, True))
    summary = formalizer_bench.gate_summary(rows)
    assert summary["coverage"] == 1.0 and summary["equivalent_among_accepted"] == 1.0
    assert summary["false_acceptances"] == 0 and summary["ambiguous_rate"] == 0.0


def test_gate_scorer_blocks_a_split_item():
    item = next(i for i in formalizer_bench.load_items() if i["id"] == "F06")
    tautology = json.dumps(dict(item["gold"], claims=["prey >= 0"]))
    other = json.dumps(dict(item["gold"], claims=["prey <= 0"]))
    row = formalizer_bench.gate_item(item, [tautology, json.dumps(item["gold"]), other], None, True)
    assert row["gate_status"] == "FORMALIZATION_AMBIGUOUS" and not row["passes"]
    assert row["baseline_equivalent"] is False


def test_gate_conditions_per_model_and_mixed():
    conditions = dict(formalizer_bench.gate_conditions(["a", "b"], [1, 3]))
    assert list(conditions) == ["a N=1", "b N=1", "a N=3", "b N=3", "mixed N=3"]
    assert conditions["a N=3"] == [("a", 0), ("a", 1), ("a", 2)]
    assert conditions["mixed N=3"] == [("a", 0), ("b", 0), ("a", 1)]


def test_mcnemar_exact():
    assert formalizer_bench.mcnemar_exact(0, 0) == 1.0
    assert formalizer_bench.mcnemar_exact(5, 0) == 0.0625
    assert formalizer_bench.mcnemar_exact(3, 3) == 1.0
