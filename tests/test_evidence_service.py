"""EvidenceRequest -> EvidenceGraph, the capability catalogue, and the contracts EdiTXT and DataAILab consume
(ADR-DISCOVERY-067)."""

import hashlib
import json
import shutil

import pytest
from fastapi.testclient import TestClient

jsonschema = pytest.importorskip("jsonschema")

from api.server import app  # noqa: E402
from python.discovery import evidence_service as ev  # noqa: E402
from python.discovery.research_lifecycle import STAGES, ActorRole, CheckKind, LifecycleService  # noqa: E402
from tests.test_research_lifecycle import clock, satisfy  # noqa: E402

SCHEMAS = ev.ROOT / "schemas" / "evidence" / "v1"
REQUEST_SCHEMA = json.loads((SCHEMAS / "evidence_request.schema.json").read_text(encoding="utf-8"))
GRAPH_SCHEMA = json.loads((SCHEMAS / "evidence_graph.schema.json").read_text(encoding="utf-8"))
FIXED = lambda: "2026-10-18T00:00:00+00:00"  # noqa: E731

HYPOTHESIS = {
    "hypothesis_id": "HYP-EV",
    "variables": [
        {"name": "group", "domain": ["carrier", "non_carrier"]},
        {"name": "decline", "domain": ["fast", "slow"]},
    ],
    "assumptions": ["group == 'non_carrier'"],
    "claims": ["decline == 'slow'"],
}


def check(request, graph):
    jsonschema.validate(request, REQUEST_SCHEMA)
    jsonschema.validate(graph, GRAPH_SCHEMA)
    ids = {n["id"] for n in graph["nodes"]}
    assert graph["focus"] in ids
    assert all(e["source"] in ids and e["target"] in ids for e in graph["edges"])
    assert all(g["node"] is None or g["node"] in ids for g in graph["gaps"])
    body = {k: graph[k] for k in ("target", "nodes", "edges", "gaps")}
    digest = hashlib.sha256(ev._canonical(body)).hexdigest()
    assert graph["provenance"]["digest"] == digest and graph["graph_id"] == f"EG-{digest[:16]}"
    return graph


def resolve(request, **kwargs):
    return check(request, ev.resolve(request, clock=FIXED, **kwargs))


def kinds(graph):
    return sorted(g["kind"] for g in graph["gaps"])


def lifecycle_project(tmp_path, criteria):
    """A released project whose artifacts are real files under tmp_path."""
    svc = LifecycleService(clock=clock())
    svc.create_project("p", "Project P")
    for stage in STAGES:
        artifacts = {c.check_id for c in svc.get("p").checks(stage) if c.kind == CheckKind.ARTIFACT}
        for check_id in sorted(artifacts):
            path = tmp_path / f"{check_id}.txt"
            path.write_text(check_id)
            sha = hashlib.sha256(path.read_bytes()).hexdigest()
            svc.submit_result("p", check_id, True, "agent", ActorRole.AGENT, artifact_path=path.name, sha256=sha)
        satisfy(svc, "p", stage, criteria, skip=artifacts)
        svc.pass_gate("p", "maintainer")
    svc.release("p", "maintainer")
    return svc


def test_lifecycle_graph_reports_gates_artifacts_and_criteria(tmp_path):
    svc = lifecycle_project(tmp_path, {"c_met": "MET", "c_failed": "NOT_MET"})
    request = {"target": {"type": "LIFECYCLE_PROJECT", "id": "p"}, "claim_ids": ["CLM-001"]}
    graph = resolve(request, lifecycle_service=svc, root=tmp_path)
    assert kinds(graph) == ["criterion_not_met"]
    by_kind = {n["kind"] for n in graph["nodes"]}
    assert {"lifecycle_project", "gate", "verification", "artifact", "release", "criterion", "claim"} <= by_kind
    relations = {(e["source"].rsplit(":", 1)[-1], e["relation"]) for e in graph["edges"] if e["target"] == "project:p"}
    assert {("c_met", "supports"), ("c_failed", "contradicts")} <= relations
    assert any(e["source"] == "manuscript_claim:CLM-001" and e["target"] == "project:p" for e in graph["edges"])
    assert all(n["attributes"]["status"] == "intact" for n in graph["nodes"] if n["attributes"].get("artifact_path"))

    # Same evidence, same id; an artifact edited after its gate gives a new id and a gap.
    assert resolve(request, lifecycle_service=svc, root=tmp_path)["graph_id"] == graph["graph_id"]
    next(tmp_path.glob("*.txt")).write_text("edited")
    changed = resolve(request, lifecycle_service=svc, root=tmp_path)
    assert changed["graph_id"] != graph["graph_id"] and "artifact_changed" in kinds(changed)


def test_lifecycle_graph_reports_open_checks_before_release():
    svc = LifecycleService(clock=clock())
    svc.create_project("q", "Q")
    graph = resolve({"target": {"type": "LIFECYCLE_PROJECT", "id": "q"}}, lifecycle_service=svc, root=None)
    assert "open_check" in kinds(graph) and "not_released" in kinds(graph)
    with pytest.raises(ev.EvidenceRequestError):
        ev.resolve({"target": {"type": "LIFECYCLE_PROJECT", "id": "nope"}}, lifecycle_service=svc)


def test_published_package_verifies_and_matches_the_index():
    graph = resolve({"target": {"type": "RESEARCH_PACKAGE", "id": "openai-math-lean-oracle.crpkg"}})
    package = next(n for n in graph["nodes"] if n["kind"] == "research_package")
    assert package["attributes"]["valid"] and package["attributes"]["published_digest_matches"]
    assert any(n["kind"] == "lifecycle_project" for n in graph["nodes"])
    assert "artifact_omitted" not in kinds(graph)


def test_tampered_or_unlisted_package_is_reported(tmp_path, monkeypatch):
    source = ev.PACKAGES_DIR / "openai-math-lean-oracle.crpkg"
    monkeypatch.setattr(ev, "PACKAGES_DIR", tmp_path)
    shutil.copy(source, tmp_path / "copy.crpkg")
    assert "unpublished_digest" in kinds(resolve({"target": {"type": "RESEARCH_PACKAGE", "id": "copy.crpkg"}}))
    data = bytearray(source.read_bytes())
    data[len(data) // 2] ^= 0xFF
    (tmp_path / "bad.crpkg").write_bytes(bytes(data))
    assert kinds(resolve({"target": {"type": "RESEARCH_PACKAGE", "id": "bad.crpkg"}})) == ["package_invalid"]
    for name in ("../x.crpkg", "missing.crpkg"):
        with pytest.raises(ev.EvidenceRequestError):
            ev.resolve({"target": {"type": "RESEARCH_PACKAGE", "id": name}})


def test_registered_claims_carry_status_and_scripts():
    passed = resolve({"target": {"type": "REGISTERED_CLAIM", "id": "1"}})
    assert kinds(passed) == [] and any(n["kind"] == "script" for n in passed["nodes"])
    draft = resolve({"target": {"type": "REGISTERED_CLAIM", "id": "25"}})
    assert kinds(draft) == ["not_validated"]
    rows = [r["id"] for r in ev.list_targets()["REGISTERED_CLAIM"]]
    assert len(rows) == len(set(rows)), "claims register row numbers must be unique"
    with pytest.raises(ev.EvidenceRequestError):
        ev.resolve({"target": {"type": "REGISTERED_CLAIM", "id": "9999"}})


def test_formal_hypothesis_with_consequences_and_rivals():
    rival = dict(
        HYPOTHESIS, hypothesis_id="HYP-RIVAL", assumptions=[], claims=["group == 'carrier' or decline == 'fast'"]
    )
    request = {
        "target": {"type": "FORMAL_HYPOTHESIS", "hypothesis": HYPOTHESIS},
        "scope": {
            "consequences": ["decline == 'slow'", "group == 'carrier'"],
            "rivals": [rival],
        },
    }
    graph = resolve(request)
    assert graph["target"] == {"type": "FORMAL_HYPOTHESIS", "hypothesis_id": "HYP-EV"}
    consequences = {n["label"]: n["attributes"]["entailed"] for n in graph["nodes"] if n["kind"] == "consequence"}
    assert consequences == {"decline == 'slow'": True, "group == 'carrier'": False}
    assert "not_entailed" in kinds(graph) and "not_kernel_checked" in kinds(graph)
    assert any(e["relation"] == "discriminates" for e in graph["edges"])


def test_formal_cases():
    ptau = resolve({"target": {"type": "FORMAL_CASE", "id": "ptau217_two_cutoff"}})
    assert {n["label"] for n in ptau["nodes"] if n["kind"] == "assumption"} == {
        "biomarker_separation",
        "preserved_renal_function",
        "ordered_cutoffs",
    }
    assert "content_in_assumptions" in kinds(ptau) and "model_scope" in kinds(ptau)
    rivals = resolve({"target": {"type": "FORMAL_CASE", "id": "alzheimer_rivals"}})
    assert len([n for n in rivals["nodes"] if n["kind"] == "rival"]) >= 2 and "draft" in kinds(rivals)
    with pytest.raises(ev.EvidenceRequestError):
        ev.resolve({"target": {"type": "FORMAL_CASE", "id": "unknown"}})


def test_ed_polarity_case_graph():
    graph = resolve({"target": {"type": "FORMAL_CASE", "id": "ed_polarity"}})
    assert [n for n in graph["nodes"] if n["kind"] == "verification"]


def test_question_target_invents_nothing():
    graph = resolve({"target": {"type": "QUESTION", "text": "Does pTau217 predict MMSE decline?"}})
    assert [n["kind"] for n in graph["nodes"]] == ["question"] and kinds(graph) == ["no_linked_evidence"]


@pytest.mark.parametrize(
    "request_",
    [
        [],
        {"target": {"type": "NOPE"}},
        {"target": {"type": "FORMAL_CASE"}},
        {"target": {"type": "QUESTION", "text": " "}},
        {"target": {"type": "FORMAL_HYPOTHESIS"}},
        {"target": {"type": "FORMAL_CASE", "id": "ptau217_two_cutoff"}, "extra": 1},
        {"target": {"type": "FORMAL_CASE", "id": "ptau217_two_cutoff"}, "request_id": "bad id"},
        {"target": {"type": "FORMAL_CASE", "id": "ptau217_two_cutoff"}, "scope": {"rivals": [{}]}},
        {"target": {"type": "FORMAL_HYPOTHESIS", "hypothesis": HYPOTHESIS}, "scope": {"rivals": [{}] * 6}},
        {"target": {"type": "FORMAL_CASE", "id": "ptau217_two_cutoff"}, "claim_ids": [1]},
    ],
)
def test_malformed_requests_are_refused(request_):
    with pytest.raises(ev.EvidenceRequestError):
        ev.resolve(request_)


# --------------------------------------------------------------------------- API


def test_api_evidence_round_trip(api_client):
    request = {"target": {"type": "FORMAL_CASE", "id": "ptau217_two_cutoff"}, "claim_ids": ["CLM-001"]}
    resp = api_client.post("/api/evidence/requests", json=request)
    assert resp.status_code == 200
    graph = check(request, resp.json())
    assert api_client.get(graph["links"]["self"]).json() == graph
    assert api_client.get("/api/evidence/graphs/EG-0000000000000000").status_code == 404
    assert api_client.post("/api/evidence/requests", json={"target": {"type": "NOPE"}}).status_code == 422
    schema = api_client.get("/api/evidence/schema").json()
    assert schema["evidence_graph"] == GRAPH_SCHEMA and schema["evidence_request"] == REQUEST_SCHEMA
    targets = api_client.get("/api/evidence/targets").json()
    assert {t["id"] for t in targets["FORMAL_CASE"]} == set(ev.FORMAL_CASES)
    assert "openai-math-lean-oracle.crpkg" in {t["id"] for t in targets["RESEARCH_PACKAGE"]}


def test_api_evidence_requests_need_a_key():
    client = TestClient(app)
    assert client.post("/api/evidence/requests", json={"target": {"type": "QUESTION", "text": "x"}}).status_code in (
        401,
        503,
    )


def test_api_published_packages(api_client):
    packages = api_client.get("/api/lifecycle/packages").json()["packages"]
    oracle = next(p for p in packages if p["name"] == "openai-math-lean-oracle.crpkg")
    assert oracle["listed_in_index"]
    resp = TestClient(app).get("/api/lifecycle/packages/openai-math-lean-oracle.crpkg")
    assert resp.status_code == 200 and hashlib.sha256(resp.content).hexdigest() == oracle["sha256"]
    assert resp.headers["x-package-sha256"] == oracle["sha256"]
    assert TestClient(app).get("/api/lifecycle/packages/unknown.crpkg").status_code == 404


def test_capability_catalogue_covers_every_endpoint(api_client):
    catalogue = api_client.get("/api/capabilities").json()
    assert catalogue["schema"] == "coresearcher.capabilities/v1"
    listed = {(c["method"], c["path"]) for c in catalogue["capabilities"]}
    spec = app.openapi()
    assert listed == {(m.upper(), p) for p, ops in spec["paths"].items() for m in ops}
    by_route = {(c["method"], c["path"]): c for c in catalogue["capabilities"]}
    evaluate = by_route[("POST", "/api/hypotheses/evaluate")]
    assert evaluate["determinism"] == "DETERMINISTIC" and evaluate["operationClass"] == "READ_ONLY"
    assert evaluate["requiresApiKey"] and evaluate["inputSchema"]["body"]
    assert {"module": "formal_hypothesis", "maturity": "Integrated"} in evaluate["modules"]
    assert by_route[("POST", "/api/lifecycle/projects")]["operationClass"] == "STATE_MODIFYING"
    assert by_route[("GET", "/api/lifecycle/projects/{project_id}/package")]["requiresApiKey"]
    for c in catalogue["capabilities"]:
        assert c["determinism"] in ("DETERMINISTIC", "NON_DETERMINISTIC")
        assert c["operationClass"] in ("READ_ONLY", "STATE_MODIFYING")
        assert c["operationClass"] == "READ_ONLY" or c["method"] != "GET"


# --------------------------------------------------------------------------- consumer contracts

# DataAILab (repo scidatalab, docs/integrations/CORESEARCHER_HTTP_CONTRACT.md) calls these three endpoints.
# Changing a path, a request field or a response field below breaks it.


def test_dataailab_contract_health(api_client):
    assert api_client.get("/api/health").json()["status"] == "healthy"


def test_dataailab_contract_inference_scaling(api_client):
    resp = api_client.post(
        "/api/discovery/inference-scaling/search", json={"question": "Does tau spread along hubs?", "beam_width": 2}
    )
    assert resp.status_code == 200 and "winning_branch" in resp.json()


def test_dataailab_contract_ground_recipe(api_client):
    resp = api_client.post(
        "/api/discovery/lab-in-the-loop/ground-recipe",
        json={
            "prediction_id": "PRED-1",
            "hypothesis_statement": "Hub tau load predicts decline.",
            "target_instrument": "SPARSE_IMAGING",
            "raw_measurements": None,
        },
    )
    body = resp.json()
    assert resp.status_code == 200 and body["recipe"]["recipe_id"] and "ingestion" in body


def test_dataailab_contract_requires_the_key():
    client = TestClient(app)
    for path in ("/api/discovery/inference-scaling/search", "/api/discovery/lab-in-the-loop/ground-recipe"):
        assert client.post(path, json={}).status_code in (401, 503)
