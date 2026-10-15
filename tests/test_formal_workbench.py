"""End-to-end formal flow: formal Alzheimer rivals, formalize endpoint and workbench formal block (ADR-061)."""

import json

from api.routers import hypotheses as hypotheses_router
from python.discovery import alzheimer_formal_scenario
from python.discovery.formal_hypothesis import HypothesisEvaluator, Relation

CARRIER_LIKE = {
    "hypothesis_id": "H-USER",
    "variables": alzheimer_formal_scenario.variable_schema(),
    "scope": "amyloid == 'A+'",
    "claims": ["tau != 'T+' or outcome == 'accelerated_dementia'"],
}


def test_formal_rivals_are_falsifiable_and_pairwise_incomparable():
    report = alzheimer_formal_scenario.scenario_report()
    assert report["omega_size"] == 192
    assert {e["content_verdict"] for e in report["evaluations"].values()} == {"FALSIFIABLE"}
    assert {c["relation"] for c in report["comparisons"]} == {"INCOMPARABLE"}
    tau, vascular, _ = alzheimer_formal_scenario.rival_hypotheses()
    # A state both rivals judge differently is a discriminating experiment: high hubs, low WMH, positive tau.
    state = {
        "amyloid": "A+",
        "tau": "T+",
        "neurodegeneration": "N+",
        "hub": "high",
        "inflammation": "normal",
        "outcome": "stable_mci",
        "wmh": "low",
    }
    assert tau.forbids(state) and not vascular.forbids(state)
    assert HypothesisEvaluator.compare(tau, tau).relation == Relation.EQUIVALENT


def test_every_rival_lists_what_it_could_not_formalize():
    assert all(r["not_formalized"] for r in alzheimer_formal_scenario.RIVALS)


def test_scenario_endpoint(api_client):
    body = api_client.get("/api/hypotheses/scenarios/alzheimer").json()
    assert body["status"] == "DRAFT_PENDING_SCIENTIST_REVIEW"
    assert len(body["comparisons"]) == 3


def test_workbench_with_a_formal_hypothesis(api_client):
    resp = api_client.post(
        "/api/discovery/workbench/launch",
        json={
            "question": "Does tau drive decline in amyloid-positive people?",
            "iterations": 1,
            "formal_hypothesis": CARRIER_LIKE,
        },
    )
    assert resp.status_code == 200
    formal = resp.json()["formal"]
    assert formal["source"] == "request"
    assert formal["evaluation"]["content_verdict"] == "FALSIFIABLE"
    assert [c["hypothesis_b"] for c in formal["comparisons"]] == [
        "HYP-TAU-CONNECTOME",
        "HYP-VASCULAR-WMH",
        "HYP-NULL-NONSPECIFIC",
    ]


def test_workbench_without_formal_input_has_no_formal_block(api_client):
    resp = api_client.post("/api/discovery/workbench/launch", json={"question": "q", "iterations": 1})
    assert resp.status_code == 200 and resp.json()["formal"] is None


def test_formalize_endpoint_unconfigured_returns_503(api_client, monkeypatch):
    monkeypatch.delenv("FORMALIZER_MODEL", raising=False)
    resp = api_client.post("/api/hypotheses/formalize", json={"prose": "x"})
    assert resp.status_code == 503


def test_formalize_endpoint_with_a_fake_model(api_client, monkeypatch):
    class FakeClient:
        def __init__(self, *args, **kwargs):
            pass

        def complete(self, messages):
            return "```json\n" + json.dumps({k: v for k, v in CARRIER_LIKE.items() if k != "hypothesis_id"}) + "\n```"

    monkeypatch.setattr(hypotheses_router, "ChatClient", FakeClient)
    resp = api_client.post(
        "/api/hypotheses/formalize",
        json={
            "prose": "In amyloid-positive people, tau positivity leads to accelerated dementia.",
            "variable_schema": alzheimer_formal_scenario.variable_schema(),
            "rivals": [dict(CARRIER_LIKE, hypothesis_id="H-SAME")],
        },
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["status"] == "PARSED" and body["draft"] is True
    assert body["comparisons"][0]["relation"] == "EQUIVALENT"
