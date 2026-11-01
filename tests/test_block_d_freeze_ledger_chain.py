"""Tests for ADR-DISCOVERY-085: the freeze service, the obligation ledger as the standard path, and the chain."""

import argparse
import json
from pathlib import Path

import pytest

from python.cli import chain as chain_cli
from python.cli import formal as formal_cli
from python.cli import freeze as freeze_cli
from python.discovery import (
    cited_registry,
    formal_pipeline,
    formal_status,
    freeze_service,
    hash_chain,
    hypothesis_ledger,
    research_lifecycle,
    verification_chain,
)
from python.discovery.formal_hypothesis import HypothesisEvaluator, SolverUndecided, hypothesis_from_dict

VARS = [{"name": "x", "domain": [0, 1, 2]}, {"name": "y", "domain": [0, 1]}]
H = {"hypothesis_id": "H", "variables": VARS, "claims": ["x < 2 or y == 1"]}
R = {"hypothesis_id": "R", "variables": VARS, "claims": ["y == 0"]}
EDITED = dict(H, claims=["x < 1 or y == 1"])
PTAU = {
    "hypothesis_id": "PT",
    "variables": [
        {"name": "ptau", "domain": [0, 1, 2, 3]},
        {"name": "decline", "domain": [0, 1]},
        {"name": "age", "domain": [40, 60, 80]},
    ],
    "scope": "age >= 60",
    "claims": ["ptau < 2 or decline == 1", "ptau >= 2 or decline == 0"],
    "non_witnesses": [{"label": "constant low biomarker with decline", "state": {"ptau": 0, "decline": 1}}],
}
CUTOFF = {
    "id": "ptau-cutoff",
    "source": "illustrative",
    "statement": "level 2 cutoff",
    "hypotheses": [{"text": "aged 50 or more", "formal": "age >= 50"}],
    "conventions": {"validated_assay": "assay A"},
}


def _codes(items):
    return {r["code"] for r in items}


# --------------------------------------------------------------------------- freeze service


def test_freeze_records_discriminating_states_without_observations():
    store = freeze_service.FreezeStore()
    record = store.freeze_hypothesis(H, [R], "author-1", "pre-registration")
    content = record["content"]
    assert record["id"] == "FZ-" + record["sha256"][:16] and record["author"] == "author-1" and record["frozen_at"]
    assert record["sha256"] == research_lifecycle.content_sha256(content)
    assert content["refutation"]["falsifier_examples"] == [{"x": 2, "y": 0}] and content["refutation"]["possible"]
    assert content["discrimination"][0]["rival"] == "R" and content["discrimination"][0]["discriminating_examples"]
    again = store.freeze_hypothesis(dict(H, alternatives=[]), [R], "someone else")  # same subject in normal form
    assert again["already_frozen"] and again["author"] == "author-1" and len(store.events) == 1


def test_verification_blocks_any_change_of_subject_digest_or_record():
    store = freeze_service.FreezeStore()
    record = store.freeze_hypothesis(H, [R], "a")
    assert store.verify_reference(record["id"], None, H, [R])["status"] == freeze_service.VERIFIED
    for check in (
        store.verify_reference(record["id"], None, EDITED, [R]),
        store.verify_reference(record["id"], None, H, []),
        store.verify_reference(record["id"], "0" * 64, H, [R]),
    ):
        assert check["status"] == freeze_service.CHANGED and check["formal_status"] == "BLOCKED" and check["problems"]
    unknown = store.verify_reference("FZ-0000000000000000", None, H, [R])
    assert unknown["status"] == freeze_service.UNKNOWN and unknown["formal_status"] == "BLOCKED"
    tampered = json.loads(json.dumps(record))
    tampered["content"]["refutation"]["falsifier_examples"] = []
    assert freeze_service.verify_embedded(tampered, None, H, [R])["status"] == freeze_service.CHANGED
    with pytest.raises(formal_status.FrozenCriteriaChanged):
        freeze_service.require_verified(freeze_service.verify_embedded(tampered, None, H, [R]))


def test_document_freeze_uses_the_lifecycle_artifact_digest(tmp_path):
    protocol = tmp_path / "protocol.md"
    protocol.write_bytes(b"Criteria: refute if x == 2 and y == 0.\r\n")
    store = freeze_service.FreezeStore()
    record = store.freeze_document(protocol.read_bytes(), "a", name="protocol.md")
    assert record["sha256"] == research_lifecycle.sha256_file(protocol)
    assert store.verify_reference(record["id"], document=protocol.read_bytes())["status"] == freeze_service.VERIFIED
    assert store.verify_reference(record["id"], document=b"other")["status"] == freeze_service.CHANGED

    service = research_lifecycle.LifecycleService()
    service.create_project("P1", "t")
    service.submit_result(
        "P1",
        "question.statement",
        True,
        "me",
        research_lifecycle.ActorRole.AGENT,
        artifact_path="protocol.md",
        sha256=record["sha256"],
    )
    lookup = freeze_service.lifecycle_lookup(service)
    anchored = freeze_service.FreezeStore().freeze_document(
        protocol.read_bytes(), "a", lifecycle={"project_id": "P1", "check_id": "question.statement"}, lookup=lookup
    )
    assert anchored["lifecycle"] == {"project_id": "P1", "check_id": "question.statement", "sha256": record["sha256"]}
    with pytest.raises(freeze_service.FreezeError, match="not the same artifact"):
        freeze_service.FreezeStore().freeze_document(
            b"different", "a", lifecycle={"project_id": "P1", "check_id": "question.statement"}, lookup=lookup
        )


def test_store_persists_and_refuses_edits(tmp_path):
    path = tmp_path / "freezes.json"
    record = freeze_service.FreezeStore(path).freeze_hypothesis(H, [R], "a")
    assert freeze_service.FreezeStore(path).get(record["id"])["sha256"] == record["sha256"]
    data = json.loads(path.read_text(encoding="utf-8"))
    data["freezes"][record["id"]]["author"] = "someone else"
    path.write_text(json.dumps(data), encoding="utf-8")
    with pytest.raises(freeze_service.FreezeError, match="edited outside"):
        freeze_service.FreezeStore(path)
    data["freezes"][record["id"]]["author"] = "a"
    data["events"][0]["payload"]["frozen_at"] = "2020-01-01T00:00:00Z"
    path.write_text(json.dumps(data), encoding="utf-8")
    with pytest.raises(freeze_service.FreezeError, match="Event log broken"):
        freeze_service.FreezeStore(path)


def test_freeze_needs_an_author_and_never_freezes_a_non_verdict(monkeypatch):
    with pytest.raises(freeze_service.FreezeError, match="author"):
        freeze_service.FreezeStore().freeze_hypothesis(H, [], " ")

    def undecided(*args, **kwargs):
        raise SolverUndecided("z3 returned unknown")

    store = freeze_service.FreezeStore()
    monkeypatch.setattr(HypothesisEvaluator, "evaluate", undecided)
    with pytest.raises(SolverUndecided):
        store.freeze_hypothesis(H, [], "a")
    assert not store.freezes and not store.events


# --------------------------------------------------------------------------- the ledger


def test_ledger_obligations_and_weakest_link():
    hypothesis = hypothesis_from_dict(PTAU)
    evaluation = HypothesisEvaluator.evaluate(hypothesis).to_dict()
    consequences = [
        HypothesisEvaluator.entails(hypothesis, c).to_dict() for c in ("ptau < 2 or decline == 1", "decline == 1")
    ]
    citations = hypothesis_ledger.check_citations(
        PTAU, [{"entry": CUTOFF, "conventions": {"validated_assay": "assay A"}}]
    )
    ledger = hypothesis_ledger.build(PTAU, evaluation, consequences, citations, ["cutoff"])
    statuses = {o["id"]: o["status"] for o in ledger["claim"]["obligations"]}
    assert statuses == {
        "fidelity": "OPEN",
        "vacuity": "DISCHARGED_SYMBOLIC",
        "claim[0]": "DISCHARGED_SYMBOLIC",
        "claim[1]": "DISCHARGED_SYMBOLIC",
        "cite[0]": "DISCHARGED_SYMBOLIC",
        "consequence[0]": "DISCHARGED_SYMBOLIC",
        "consequence[1]": "REFUTED",
    }
    assert ledger["rollup"]["status"] == "REFUTED" and ledger["rollup"]["refuted"] == ["consequence[1]"]
    assert ledger["dag"]["acyclic"] and not ledger["dag"]["missing"]
    assert _codes(ledger["mandatory_relays"]) == {"LEDGER_NOT_PROVED"}


def test_ledger_marks_vacuity_unfalsifiable_claims_and_fallen_premises():
    careless = dict(PTAU, claims=["ptau < 2 or decline == 1"])
    evaluation = HypothesisEvaluator.evaluate(hypothesis_from_dict(careless)).to_dict()
    ledger = hypothesis_ledger.build(careless, evaluation)
    assert {o["id"]: o["status"] for o in ledger["claim"]["obligations"]}["vacuity"] == "REFUTED"

    redundant = dict(H, assumptions=["y == 1"])
    evaluation = HypothesisEvaluator.evaluate(hypothesis_from_dict(redundant)).to_dict()
    ledger = hypothesis_ledger.build(redundant, evaluation)
    claim = ledger["claim"]["obligations"][2]
    assert claim["id"] == "claim[0]" and claim["status"] == "REFUTED"

    retracted = dict(CUTOFF, status="RETRACTED", status_reason="assay withdrawn")
    citations = hypothesis_ledger.check_citations(PTAU, [{"entry": retracted}])
    trust = [{"claim": "c", "rung": "STATEMENT_PUBLIC", "rungs": []}]
    ledger = hypothesis_ledger.build(
        PTAU, HypothesisEvaluator.evaluate(hypothesis_from_dict(PTAU)).to_dict(), citations=citations, claim_trust=trust
    )
    assert ledger["rollup"]["trust_rung"] == "CLAIMED" and ledger["rollup"]["trust_caps"]


def test_ledger_of_a_non_verdict_is_all_open():
    ledger = hypothesis_ledger.build(
        H, None, status="UNDECIDED", reason="z3 unknown", requested_consequences=["y == 1"]
    )
    assert ledger["formal_status"] == "UNDECIDED" and ledger["rollup"]["status"] == "OPEN"
    assert {o["status"] for o in ledger["claim"]["obligations"]} == {"OPEN"}
    assert "consequence[0]" in ledger["rollup"]["open"] and not ledger["rollup"]["proved"]


# --------------------------------------------------------------------------- the API


def test_api_evaluate_keeps_its_fields_and_adds_the_ledger(api_client):
    before = api_client.post("/api/hypotheses/evaluate", json={"hypothesis": H}).json()
    for key in ("content_verdict", "claims_with_content", "claim_trust", "mandatory_relays", "provenance"):
        assert key in before
    assert before["obligation_ledger"]["schema"] == hypothesis_ledger.SCHEMA
    assert "freeze_check" not in before and "consequences" not in before
    assert "CRITERIA_FROZEN" not in _codes(before["mandatory_relays"])


def test_api_freeze_then_evaluate_and_refuse_an_edit(api_client):
    record = api_client.post("/api/freezes/hypothesis", json={"hypothesis": H, "rivals": [R], "author": "a"}).json()
    assert api_client.get(f"/api/freezes/{record['id']}").json()["sha256"] == record["sha256"]
    body = api_client.post(
        "/api/hypotheses/evaluate",
        json={"hypothesis": H, "rivals": [R], "freeze": {"freeze_id": record["id"]}, "consequences": ["y == 1"]},
    ).json()
    assert body["freeze_check"]["status"] == "VERIFIED" and "CRITERIA_FROZEN" in _codes(body["mandatory_relays"])
    assert body["comparisons"][0]["relation"] and body["consequences"][0]["entailed"] is False
    assert body["obligation_ledger"]["rollup"]["status"] == "REFUTED"
    refused = api_client.post(
        "/api/hypotheses/evaluate", json={"hypothesis": EDITED, "rivals": [R], "freeze": {"freeze_id": record["id"]}}
    )
    assert refused.status_code == 409 and refused.json()["detail"]["formal_status"] == "BLOCKED"
    verify = api_client.post(f"/api/freezes/{record['id']}/verify", json={"hypothesis": EDITED, "rivals": [R]})
    assert verify.json()["status"] == "CHANGED"
    assert api_client.get("/api/freezes/FZ-unknown").status_code == 404
    assert api_client.post("/api/freezes/hypothesis", json={"hypothesis": H, "author": ""}).status_code == 422
    doc = api_client.post("/api/freezes/document", json={"text": "checklist v1", "author": "a"}).json()
    assert doc["sha256"] == research_lifecycle.bytes_sha256(b"checklist v1")


def test_api_evaluate_checks_citations_against_the_registry(api_client):
    api_client.post("/api/registry/entries", json=CUTOFF)
    body = api_client.post(
        "/api/hypotheses/evaluate",
        json={
            "hypothesis": PTAU,
            "citations": [
                {"entry_id": "ptau-cutoff", "conventions": {"validated_assay": "assay B"}, "source": "cutoff"}
            ],
        },
    ).json()
    assert body["citations"][0]["outcome"] == "FINDINGS"
    cite = [o for o in body["obligation_ledger"]["claim"]["obligations"] if o["id"] == "cite[0]"][0]
    assert cite["status"] == "OPEN" and cite["source"] == "cutoff"
    missing = api_client.post(
        "/api/hypotheses/evaluate", json={"hypothesis": PTAU, "citations": [{"entry_id": "nope"}]}
    )
    assert missing.status_code == 422


def test_api_chain_runs_every_step_and_stops_on_non_verdicts(api_client, monkeypatch):
    body = api_client.post(
        "/api/chain/run", json={"hypothesis": PTAU, "author": "a", "consequences": ["decline == 1"]}
    ).json()
    assert [s["name"] for s in body["steps"]] == [n for n, _ in verification_chain.STEPS]
    assert body["formal_status"] == "DECIDED" and body["outcome"] == "REFUTED"
    assert {"CRITERIA_FROZEN", "CRITERIA_FROZEN_IN_SAME_RUN", "LEDGER_NOT_PROVED"} <= _codes(body["mandatory_relays"])
    monkeypatch.delenv("FORMALIZER_MODEL", raising=False)
    monkeypatch.delenv("FORMALIZER_GATE_MODELS", raising=False)
    prose = api_client.post("/api/chain/run", json={"prose": "high pTau217 predicts decline", "author": "a"}).json()
    assert prose["formal_status"] == "BLOCKED" and prose["outcome"] is None
    assert [s["state"] for s in prose["steps"]][1:] == ["BLOCKED"] + ["NOT_RUN"] * 6
    assert api_client.post("/api/chain/run", json={"hypothesis": H}).status_code == 422  # no author, no freeze
    catalogue = {(c["method"], c["path"]): c for c in api_client.get("/api/capabilities").json()["capabilities"]}
    assert catalogue[("POST", "/api/freezes/{freeze_id}/verify")]["operationClass"] == "READ_ONLY"


# --------------------------------------------------------------------------- the chain


def test_chain_with_a_preregistered_freeze_and_an_undecided_evaluation(monkeypatch):
    store = freeze_service.FreezeStore()
    record = store.freeze_hypothesis(H, [R], "a")
    ok = verification_chain.run({"hypothesis": H, "rivals": [R], "freeze": {"freeze_id": record["id"]}}, store)
    assert ok["steps"][0]["detail"]["mode"] == "preregistered" and ok["formal_status"] == "DECIDED"
    assert "CRITERIA_FROZEN_IN_SAME_RUN" not in _codes(ok["mandatory_relays"])
    blocked = verification_chain.run(
        {"hypothesis": EDITED, "rivals": [R], "freeze": {"freeze_id": record["id"]}}, store
    )
    assert blocked["formal_status"] == "BLOCKED" and chain_cli.exit_code(blocked) == formal_status.EXIT_FREEZE_CHANGED

    real = HypothesisEvaluator.evaluate

    def flaky(*args, **kwargs):
        if kwargs.get("observations") is None and len(args) > 1:
            raise SolverUndecided("z3 returned unknown")
        return real(*args, **kwargs)

    monkeypatch.setattr(HypothesisEvaluator, "evaluate", flaky)
    undecided = verification_chain.run({"hypothesis": H, "rivals": [R], "freeze": {"freeze_id": record["id"]}}, store)
    assert undecided["formal_status"] == "UNDECIDED" and undecided["outcome"] == "OPEN"
    assert [s["state"] for s in undecided["steps"]][2:] == ["UNDECIDED"] + ["NOT_RUN"] * 5
    assert not undecided["obligation_ledger"]["rollup"]["proved"]


def test_chain_formalizes_prose_from_stored_readings(monkeypatch):
    agreed = json.dumps({"hypothesis_id": "H", "variables": VARS, "claims": ["x < 2 or y == 1"]})

    class Client:
        model = "stub"

        def complete(self, messages, temperature=0.0, seed=None):
            return agreed

    store = freeze_service.FreezeStore()
    result = verification_chain.run(
        {"prose": "x is small unless y", "author": "a", "samples": 3}, store, clients={"stub": Client()}
    )
    assert result["formal_status"] == "DECIDED", result["reason"]
    assert result["steps"][0]["detail"]["mode"] == "same_run_document"
    assert result["steps"][1]["detail"]["criteria_freeze"]["freeze_id"] in store.freezes
    assert {t["rung"] for t in result["claim_trust"]} == {"CLAIMED"}  # a formalizer draft is never a statement


# --------------------------------------------------------------------------- the CLI


def _ns(**kw):
    return argparse.Namespace(**kw)


def test_cli_freeze_formal_run_analyze_and_chain(tmp_path, capsys):
    hfile, rfile, efile = tmp_path / "h.json", tmp_path / "r.json", tmp_path / "e.json"
    hfile.write_text(json.dumps(H), encoding="utf-8")
    rfile.write_text(json.dumps(R), encoding="utf-8")
    efile.write_text(json.dumps(EDITED), encoding="utf-8")
    store = str(tmp_path / "freezes.json")
    args = _ns(
        store=store,
        freeze_command="hypothesis",
        hypothesis=str(hfile),
        rival=[str(rfile)],
        author="a",
        label="",
        criteria=None,
        max_examples=5,
        backend="auto",
        out=str(tmp_path / "frozen"),
        lifecycle_project=None,
        lifecycle_check="protocol.document",
    )
    assert freeze_cli.main(args) == 0
    record = json.loads(capsys.readouterr().out)
    assert research_lifecycle.sha256_file(Path(record["written"])) == record["sha256"]
    verify = _ns(
        store=store,
        freeze_command="verify",
        id=record["id"],
        hypothesis=str(efile),
        rival=[str(rfile)],
        file=None,
        sha256=None,
    )
    assert freeze_cli.main(verify) == formal_status.EXIT_FREEZE_CHANGED

    base = dict(
        prose=None,
        prose_file=None,
        hypothesis_id="H",
        variable_schema=None,
        rival=[str(rfile)],
        consequence=["y == 1"],
        observations=None,
        max_examples=5,
        backend="auto",
        samples=None,
        lean=False,
        default_probes=False,
        claim_evidence=None,
        citations=None,
        registry=None,
        fidelity_spec=None,
        freeze=record["id"],
        freeze_sha256=None,
        freeze_store=store,
        threshold=None,
        out=str(tmp_path / "runs"),
        overwrite=False,
    )
    assert formal_cli.run(_ns(**base, hypothesis=str(hfile), name="ok")) == 0
    sidecar = json.loads((tmp_path / "runs" / "ok.meta.json").read_text(encoding="utf-8"))
    assert sidecar["obligation_ledger"]["rollup"]["status"] == "REFUTED"
    capsys.readouterr()
    analyze = _ns(target=str(tmp_path / "runs" / "ok.meta.json"), threshold=None, out=None, overwrite=False)
    assert formal_cli.analyze(analyze) == 0
    analysis = json.loads((tmp_path / "runs" / "ok.analysis.json").read_text(encoding="utf-8"))
    assert analysis["verdict"]["freeze"] == "VERIFIED" and analysis["assessment"]["reproduces_run"]
    assert analysis["obligation_ledger"] == sidecar["obligation_ledger"]
    assert formal_cli.run(_ns(**base, hypothesis=str(efile), name="edited")) == formal_status.EXIT_FREEZE_CHANGED
    response = json.loads((tmp_path / "runs" / "edited.response.json").read_text(encoding="utf-8"))
    assert response["formal_status"] == "BLOCKED" and response["reports"]["evaluation"] is None

    request = tmp_path / "chain.json"
    request.write_text(json.dumps({"hypothesis": H, "author": "a", "consequences": ["y == 1"]}), encoding="utf-8")
    chain_args = _ns(
        chain_command="run",
        request=str(request),
        freeze_store=store,
        registry=str(tmp_path / "registry.json"),
        out=str(tmp_path / "chain.out.json"),
    )
    assert chain_cli.main(chain_args) == 0
    assert "8. trust_ladder (M7): DONE - REFUTED" in capsys.readouterr().out


def test_formal_requests_without_block_d_fields_are_unchanged():
    request = formal_pipeline.make_request(hypothesis=H)
    assert not {"citations", "fidelity_spec", "freeze"} & set(request)
    response = formal_pipeline.compute(request)
    assert "freeze_check" not in response and set(response["reports"]) == {"evaluation", "comparisons", "consequences"}


def test_registry_log_still_verifies_after_the_shared_chain_refactor(tmp_path):
    path = tmp_path / "registry.json"
    cited_registry.Registry(path).register(dict(CUTOFF))
    reg = cited_registry.Registry(path)
    assert reg.events[0]["kind"] == "register"


def test_hash_chain_detects_edits_reordering_and_removal():
    events = []
    for i in range(3):
        hash_chain.append(events, "freeze", {"i": i})
    hash_chain.verify(events, ValueError)
    for broken in (
        events[:1] + events[2:],
        [events[1], events[0], events[2]],
        [dict(events[0], payload={"i": 9})] + events[1:],
    ):
        with pytest.raises(ValueError, match="Event log broken"):
            hash_chain.verify(broken, ValueError)
