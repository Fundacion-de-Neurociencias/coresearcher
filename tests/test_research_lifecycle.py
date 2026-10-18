"""Stage gates, versions, releases, policies and agents of the research lifecycle (ADR-DISCOVERY-063)."""

import hashlib
import itertools
import json
from datetime import datetime, timedelta, timezone

import pytest

from python.discovery.hypothesis_tournament_arena import TournamentHypothesis, TournamentReport
from python.discovery.research_lifecycle import (
    EXPORT_SCHEMA,
    STAGES,
    ActorRole,
    CheckKind,
    FindingKind,
    GateDecision,
    LifecycleError,
    LifecycleService,
    LifecycleWatcher,
    ReleaseKind,
    Stage,
    ontrack_status,
    project_to_dict,
    verify_tournament_elo,
)

T0 = datetime(2026, 10, 1, tzinfo=timezone.utc)
SHA = "a" * 64


def clock():
    ticks = itertools.count()
    return lambda: (T0 + timedelta(minutes=next(ticks))).isoformat()


def service(tmp_path=None):
    return LifecycleService(tmp_path / "lifecycle.jsonl" if tmp_path else None, clock=clock())


def satisfy(svc, pid, stage, criteria=None, skip=()):
    """Submit a passing result from the right role for every check of a stage."""
    for check in svc.get(pid).checks(stage):
        if check.check_id in skip:
            continue
        kwargs = {}
        if check.kind == CheckKind.VERIFIER:
            role, actor = ActorRole.VERIFIER_TOOL, "z3"
        elif check.kind == CheckKind.HUMAN:
            role, actor = ActorRole.HUMAN, "scientist-1"
        else:
            role, actor = ActorRole.AGENT, "agent-1"
        if check.kind == CheckKind.ARTIFACT:
            kwargs = {"artifact_path": f"runs/{check.check_id}.json", "sha256": SHA}
        if check.kind == CheckKind.RUBRIC:
            kwargs = {"value": check.threshold}
        if check.check_id == "analysis.criteria_evaluated" and criteria:
            kwargs = {"criteria": criteria}
        svc.submit_result(pid, check.check_id, True, actor, role, **kwargs)


def run_to(svc, pid, stop, criteria=None):
    while svc.get(pid).stage != stop:
        satisfy(svc, pid, svc.get(pid).stage, criteria)
        svc.pass_gate(pid, "maintainer")


def run_all(svc, pid, criteria=None):
    run_to(svc, pid, Stage.REPORT, criteria)
    satisfy(svc, pid, Stage.REPORT)
    svc.pass_gate(pid, "maintainer")


def test_full_path_passes_every_gate_and_releases_preregistered():
    svc = service()
    svc.create_project("formalizer-r1", "Formalizer benchmark, round 1")
    run_all(svc, "formalizer-r1", {"equivalence>=0.80": "NOT_MET", "parse_rate>=0.90": "MET"})
    project = svc.get("formalizer-r1")
    assert [g.stage for g in project.active_gates()] == STAGES and project.version == len(STAGES)
    release = svc.release("formalizer-r1", "maintainer", "The model stays a draft formalizer.")
    assert release.kind == ReleaseKind.PREREGISTERED and release.version == 7
    assert release.criteria == {"equivalence>=0.80": "NOT_MET", "parse_rate>=0.90": "MET"}
    assert "Criteria **not met**: equivalence>=0.80" in release.notes and "verified by z3" in release.notes
    with pytest.raises(LifecycleError):
        svc.release("formalizer-r1", "maintainer")  # same version twice


def test_self_check_never_satisfies_a_verifier_check():
    svc = service()
    svc.create_project("p", "P")
    run_to(svc, "p", Stage.HYPOTHESIS)
    satisfy(svc, "p", Stage.HYPOTHESIS, skip={"hypothesis.formal_object"})
    svc.submit_result("p", "hypothesis.formal_object", True, "agent-1", ActorRole.AGENT, note="I checked it myself")
    gate = svc.evaluate_gate("p")
    assert gate.decision == GateDecision.INCOMPLETE
    missing = [c for c in gate.checks if c.check.check_id == "hypothesis.formal_object"][0]
    assert "self-checks" in missing.reason
    with pytest.raises(LifecycleError):
        svc.pass_gate("p", "maintainer")
    svc.submit_result("p", "hypothesis.formal_object", True, "formal-evaluator", ActorRole.VERIFIER_TOOL)
    assert svc.evaluate_gate("p").decision == GateDecision.PASS


def test_pending_human_fail_and_latest_result_wins():
    svc = service()
    svc.create_project("p", "P", template="signed")
    run_to(svc, "p", Stage.HYPOTHESIS)
    satisfy(svc, "p", Stage.HYPOTHESIS, skip={"hypothesis.confirmed"})
    assert svc.evaluate_gate("p").decision == GateDecision.PENDING_HUMAN
    svc.submit_result("p", "hypothesis.confirmed", True, "agent-1", ActorRole.AGENT)  # an agent cannot sign off
    assert svc.evaluate_gate("p").decision == GateDecision.PENDING_HUMAN
    svc.submit_result("p", "hypothesis.rivals", True, "agent-1", ActorRole.AGENT, value=0)
    assert svc.evaluate_gate("p").decision == GateDecision.FAIL
    svc.submit_result("p", "hypothesis.rivals", True, "agent-1", ActorRole.AGENT, value=3)
    svc.submit_result("p", "hypothesis.confirmed", True, "scientist-1", ActorRole.HUMAN)
    assert svc.evaluate_gate("p").decision == GateDecision.PASS


def test_optional_checks_do_not_block_and_results_are_validated():
    svc = service()
    svc.create_project("p", "P")
    run_to(svc, "p", Stage.EXECUTION)
    satisfy(svc, "p", Stage.EXECUTION, skip={"execution.integrity"})
    assert svc.evaluate_gate("p").decision == GateDecision.PASS
    with pytest.raises(LifecycleError):  # artifact without a hash
        svc.submit_result("p", "execution.raw_outputs", True, "agent-1", ActorRole.AGENT, artifact_path="x")
    with pytest.raises(LifecycleError):  # check of another stage
        svc.submit_result("p", "report.signoff", True, "scientist-1", ActorRole.HUMAN)
    with pytest.raises(LifecycleError):
        svc.submit_result("p", "no.such.check", True, "agent-1", ActorRole.AGENT)


def test_rework_supersedes_later_gates_and_protocol_rework_downgrades_the_release():
    svc = service()
    svc.create_project("p", "P")
    run_to(svc, "p", Stage.CONTROLS)
    before = svc.get("p").digest
    svc.rework("p", Stage.PROTOCOL, "maintainer", "Accept lowercase true/false in predicates (formalizer-v2).")
    project = svc.get("p")
    assert project.stage == Stage.PROTOCOL and project.protocol_reworked_after_execution
    assert [g.stage for g in project.active_gates()] == [Stage.QUESTION, Stage.HYPOTHESIS]
    assert "protocol.document" not in project.results
    run_all(svc, "p", {"c1": "MET"})
    assert svc.get("p").version == 9 and svc.get("p").digest != before
    release = svc.release("p", "maintainer")
    assert release.kind == ReleaseKind.EXPLORATORY
    assert "reopened after execution" in release.notes and "formalizer-v2" in release.notes
    with pytest.raises(LifecycleError):
        svc.rework("p", "NOT_A_STAGE", "maintainer", "x")
    with pytest.raises(LifecycleError):
        svc.rework("p", Stage.QUESTION, "maintainer", " ")


def test_protocol_rework_before_execution_keeps_preregistration():
    svc = service()
    svc.create_project("p", "P")
    run_to(svc, "p", Stage.EXECUTION)
    svc.rework("p", Stage.PROTOCOL, "maintainer", "Reviewer asked for a second criterion.")
    run_all(svc, "p")
    assert svc.release("p", "maintainer").kind == ReleaseKind.PREREGISTERED


def test_digest_chains_previous_digest_and_evidence():
    a, b = service(), service()
    for svc in (a, b):
        svc.create_project("p", "P")
        satisfy(svc, "p", Stage.QUESTION)
        svc.pass_gate("p", "m")
    assert a.get("p").digest == b.get("p").digest
    for svc in (a, b):
        satisfy(svc, "p", Stage.HYPOTHESIS)
        svc.pass_gate("p", "m")
    assert a.get("p").digest == b.get("p").digest
    a.rework("p", Stage.HYPOTHESIS, "m", "redo")
    b.rework("p", Stage.HYPOTHESIS, "m", "redo")
    a.submit_result("p", "hypothesis.rivals", True, "agent-1", ActorRole.AGENT, value=2)
    for svc in (a, b):
        satisfy(svc, "p", Stage.HYPOTHESIS, skip={"hypothesis.rivals"} if svc is a else ())
        svc.pass_gate("p", "m")
    assert a.get("p").digest != b.get("p").digest


def test_log_replay_rebuilds_the_same_state(tmp_path):
    svc = service(tmp_path)
    svc.create_project("p", "P")
    run_to(svc, "p", Stage.CONTROLS)
    svc.rework("p", Stage.EXECUTION, "maintainer", "rerun with pinned model tag")
    run_all(svc, "p", {"c1": "MET"})
    svc.release("p", "maintainer")
    replayed = LifecycleService(tmp_path / "lifecycle.jsonl")
    assert json.dumps(project_to_dict(replayed.get("p"), replayed), sort_keys=True) == json.dumps(
        project_to_dict(svc.get("p"), svc), sort_keys=True
    )
    assert replayed.get("p").releases[0].notes == svc.get("p").releases[0].notes


def test_log_rejects_unknown_schema_and_invalid_events_never_reach_it(tmp_path):
    svc = service(tmp_path)
    svc.create_project("p", "P")
    with pytest.raises(LifecycleError):
        svc.create_project("p", "again")
    log = tmp_path / "lifecycle.jsonl"
    assert len(log.read_text(encoding="utf-8").splitlines()) == 1
    event = json.loads(log.read_text(encoding="utf-8"))
    log.write_text(json.dumps({**event, "schema_version": 99}) + "\n", encoding="utf-8")
    with pytest.raises(LifecycleError):
        LifecycleService(log)


def test_watcher_reports_drift_missing_pending_stalled_and_unreleased(tmp_path):
    (tmp_path / "runs").mkdir()
    question = tmp_path / "runs" / "question.md"
    question.write_text("Does X predict Y?", encoding="utf-8")
    svc = service()
    svc.create_project("p", "P", template="signed")
    sha = hashlib.sha256(question.read_bytes()).hexdigest()
    svc.submit_result(
        "p", "question.statement", True, "agent-1", ActorRole.AGENT, artifact_path="runs/question.md", sha256=sha
    )
    watcher = LifecycleWatcher(svc, root=tmp_path, stall_days=14)
    now = T0 + timedelta(days=1)
    assert [f.kind for f in watcher.scan(now)] == [FindingKind.PENDING_HUMAN]
    question.write_text("Does X predict Z?", encoding="utf-8")
    kinds = {f.kind for f in watcher.scan(T0 + timedelta(days=30))}
    assert kinds == {FindingKind.PENDING_HUMAN, FindingKind.STALLED, FindingKind.ARTIFACT_DRIFT}
    question.unlink()
    assert FindingKind.ARTIFACT_MISSING in {f.kind for f in watcher.scan(now)}

    done = service()
    done.create_project("q", "Q")
    run_all(done, "q")
    assert [f.kind for f in LifecycleWatcher(done).scan(now)] == [FindingKind.UNRELEASED]
    done.release("q", "maintainer")
    assert LifecycleWatcher(done).scan(now) == []


def test_verify_tournament_elo_gate_integration():
    hyp_a = TournamentHypothesis("hyp-a", "Hypothesis A", "A is true", "bio", elo_rating=1280.0)
    hyp_b = TournamentHypothesis("hyp-b", "Hypothesis B", "B is true", "bio", elo_rating=1120.0)
    report = TournamentReport(
        tournament_id="tourn-1",
        domain="bio",
        total_matches=1,
        leaderboard=[hyp_a, hyp_b],
        top_hypothesis=hyp_a,
        matches=[],
        tournament_hash="sha256:1234",
        execution_time_seconds=0.1,
    )
    # Check above threshold
    res_pass = verify_tournament_elo(report, "hyp-a", min_elo=1200.0)
    assert res_pass.ok is True
    assert res_pass.role == ActorRole.VERIFIER_TOOL
    assert res_pass.check_id == "protocol.tournament_elo"

    # Check below threshold
    res_fail = verify_tournament_elo(report, "hyp-b", min_elo=1200.0)
    assert res_fail.ok is False
    assert res_fail.role == ActorRole.VERIFIER_TOOL

    # Check missing hypothesis
    res_missing = verify_tournament_elo(report, "hyp-unknown", min_elo=1200.0)
    assert res_missing.ok is False


def test_watcher_scan_and_alert_callback(tmp_path):
    svc = service()
    svc.create_project("p_alert", "P Alert", template="signed")
    svc.submit_result(
        "p_alert", "question.statement", True, "agent-1", ActorRole.AGENT, artifact_path="runs/q.md", sha256=SHA
    )
    watcher = LifecycleWatcher(svc, root=None, stall_days=7)
    alerts = []

    findings = watcher.scan_and_alert(
        now=T0 + timedelta(days=1),
        alert_callback=lambda f: alerts.append(f.kind),
    )
    assert len(findings) == 1
    assert alerts == [FindingKind.PENDING_HUMAN]


def test_ontrack_export_shape():
    svc = service()
    svc.create_project("p", "P")
    run_to(svc, "p", Stage.PROTOCOL)
    status = ontrack_status(svc, findings=[])
    assert status["schema"] == EXPORT_SCHEMA and status["product"] == "coresearcher"
    (row,) = status["projects"]
    assert row["stage"] == "PROTOCOL" and row["stage_index"] == 2 and row["stage_count"] == 7
    assert row["gate_decision"] == "INCOMPLETE" and row["checklist"] == {"required_satisfied": 0, "required_total": 3}
    assert row["version"] == 2 and len(row["digest"]) == 64 and row["latest_release"] is None


# --- API ------------------------------------------------------------------------


def test_api_lifecycle_round_trip(api_client):
    pid = "api-lifecycle-test"
    assert api_client.get("/api/lifecycle/template").json()["stages"]["REPORT"][1]["check_id"] == "report.signoff"
    created = api_client.post("/api/lifecycle/projects", json={"project_id": pid, "title": "API test"})
    assert created.status_code == 200 and created.json()["stage"] == "QUESTION"
    assert api_client.post("/api/lifecycle/projects", json={"project_id": pid, "title": "dup"}).status_code == 409
    gate = api_client.post(f"/api/lifecycle/projects/{pid}/gate/pass", json={"actor": "m"})
    assert gate.status_code == 409
    for body in (
        {
            "check_id": "question.statement",
            "ok": True,
            "actor": "agent-1",
            "role": "AGENT",
            "artifact_path": "q.md",
            "sha256": SHA,
        },
        {"check_id": "question.owner", "ok": True, "actor": "scientist-1", "role": "HUMAN"},
    ):
        assert api_client.post(f"/api/lifecycle/projects/{pid}/results", json=body).status_code == 200
    bad = {"check_id": "question.statement", "ok": True, "actor": "a", "role": "AGENT", "artifact_path": "q.md"}
    assert api_client.post(f"/api/lifecycle/projects/{pid}/results", json=bad).status_code == 422
    assert api_client.get(f"/api/lifecycle/projects/{pid}/gate").json()["decision"] == "PASS"
    passed = api_client.post(f"/api/lifecycle/projects/{pid}/gate/pass", json={"actor": "m"}).json()
    assert passed["stage"] == "QUESTION" and passed["version"] == 1
    project = api_client.get(f"/api/lifecycle/projects/{pid}").json()
    assert project["stage"] == "HYPOTHESIS"
    assert api_client.post(f"/api/lifecycle/projects/{pid}/release", json={"actor": "m"}).status_code == 409
    rework = api_client.post(
        f"/api/lifecycle/projects/{pid}/rework", json={"stage": "QUESTION", "actor": "m", "reason": "rephrase"}
    )
    assert rework.json()["stage"] == "QUESTION" and rework.json()["version"] == 0
    assert api_client.get("/api/lifecycle/projects/nope").status_code == 404
    status = api_client.get("/api/lifecycle/ontrack").json()
    assert status["schema"] == EXPORT_SCHEMA and pid in {p["project_id"] for p in status["projects"]}
    assert isinstance(api_client.get("/api/lifecycle/watch").json()["findings"], list)


def test_api_lifecycle_writes_need_a_key():
    from fastapi.testclient import TestClient

    from api.server import app

    response = TestClient(app).post("/api/lifecycle/projects", json={"project_id": "x", "title": "x"})
    assert response.status_code in (401, 503)


def test_human_sign_offs_are_optional_by_default_and_reported():
    svc = service()
    svc.create_project("p", "P")
    satisfy(svc, "p", Stage.QUESTION, skip={"question.owner"})
    assert svc.evaluate_gate("p").decision == GateDecision.PASS
    svc.pass_gate("p", "maintainer")
    run_all(svc, "p")  # satisfy() signs every later stage
    notes = svc.release("p", "maintainer").notes
    assert "Human sign-offs: scientist-1 (analysis.deviations)" in notes and "question.owner" not in notes
    unsigned = service()
    unsigned.create_project("u", "U")
    while not unsigned.get("u").passed(Stage.REPORT):
        satisfy(
            unsigned,
            "u",
            unsigned.get("u").stage,
            skip={c.check_id for c in unsigned.get("u").checks(unsigned.get("u").stage) if c.kind == CheckKind.HUMAN},
        )
        unsigned.pass_gate("u", "maintainer")
    assert "Human sign-offs: none" in unsigned.release("u", "maintainer").notes


def test_formal_claim_template_separates_validity_from_provenance():
    svc = service()
    svc.create_project("ns", "Claimed proof", template="formal-claim")
    for stage in (Stage.QUESTION, Stage.HYPOTHESIS, Stage.PROTOCOL):
        satisfy(svc, "ns", stage)
        svc.pass_gate("ns", "auditor")
    # The prover's own report is a self-check: it cannot satisfy the kernel check.
    svc.submit_result("ns", "execution.proof_checked", True, "the-model", ActorRole.AGENT)
    satisfy(svc, "ns", Stage.EXECUTION, skip={"execution.proof_checked"})
    assert svc.evaluate_gate("ns").decision == GateDecision.INCOMPLETE
    svc.submit_result("ns", "execution.proof_checked", True, "comparator", ActorRole.VERIFIER_TOOL)
    svc.pass_gate("ns", "auditor")
    # Expert reviews of validity block, unlike optional sign-offs elsewhere.
    satisfy(svc, "ns", Stage.CONTROLS, skip={"controls.statement_fidelity"})
    assert svc.evaluate_gate("ns").decision == GateDecision.PENDING_HUMAN
    svc.submit_result(
        "ns", "controls.statement_fidelity", False, "expert-1", ActorRole.HUMAN, note="drops a hypothesis"
    )
    assert svc.evaluate_gate("ns").decision == GateDecision.FAIL
    svc.submit_result("ns", "controls.statement_fidelity", True, "expert-2", ActorRole.HUMAN)
    svc.pass_gate("ns", "auditor")
    satisfy(svc, "ns", Stage.ANALYSIS)
    svc.pass_gate("ns", "auditor")
    # Provenance is optional and never blocks; the release notes say whether it was declared.
    satisfy(svc, "ns", Stage.REPORT, skip={"report.provenance"})
    svc.pass_gate("ns", "auditor")
    assert "Provenance (does not affect validity): not declared" in svc.release("ns", "auditor").notes


def test_formal_claim_premise_origin_is_reported_and_never_blocks():
    svc = service()
    svc.create_project("po", "Claimed discovery", template="formal-claim")
    run_to(svc, "po", Stage.REPORT)
    satisfy(svc, "po", Stage.REPORT, skip={"report.premise_origin"})
    svc.pass_gate("po", "auditor")
    notes = svc.release("po", "auditor").notes
    assert "Premise origin (does not affect validity): not declared" in notes
    assert "Provenance (does not affect validity): `runs/report.provenance.json`" in notes

    svc.create_project("po2", "Claimed discovery, premises declared", template="formal-claim")
    run_all(svc, "po2")
    assert (
        "Premise origin (does not affect validity): `runs/report.premise_origin.json`"
        in svc.release("po2", "auditor").notes
    )
