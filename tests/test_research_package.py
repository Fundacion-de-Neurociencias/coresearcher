"""Research packages: export, verification, read-only import and fork (ADR-DISCOVERY-065)."""

import gzip
import hashlib
import io
import itertools
import json
import tarfile
from datetime import datetime, timedelta, timezone

import pytest

from python.discovery.research_lifecycle import ActorRole, CheckKind, LifecycleError, LifecycleService, Stage
from python.discovery.research_package import (
    PackageError,
    SensitiveContentError,
    export_package,
    fork_package,
    import_package,
)

T0 = datetime(2026, 10, 1, tzinfo=timezone.utc)


def clock():
    ticks = itertools.count()
    return lambda: (T0 + timedelta(minutes=next(ticks))).isoformat()


def build(tmp_path, through=Stage.REPORT, release=True):
    """A benchmark project whose artifact checks point at real files under tmp_path."""
    svc = LifecycleService(clock=clock())
    svc.create_project("oracle", "Label oracle", template="benchmark")
    while True:
        project = svc.get("oracle")
        for check in project.checks(project.stage):
            if check.kind == CheckKind.ARTIFACT:
                rel = f"runs/{check.check_id}.txt"
                (tmp_path / "runs").mkdir(exist_ok=True)
                (tmp_path / rel).write_text(f"content of {check.check_id}\n", encoding="utf-8")
                sha = hashlib.sha256((tmp_path / rel).read_bytes()).hexdigest()
                svc.submit_result(
                    "oracle", check.check_id, True, "agent", ActorRole.AGENT, artifact_path=rel, sha256=sha
                )
            elif check.kind == CheckKind.VERIFIER:
                criteria = {"c1": "MET", "c2": "NOT_MET"} if check.check_id == "analysis.criteria_evaluated" else {}
                svc.submit_result(
                    "oracle", check.check_id, True, "comparator", ActorRole.VERIFIER_TOOL, criteria=criteria
                )
            elif check.kind == CheckKind.HUMAN:
                svc.submit_result("oracle", check.check_id, True, "scientist", ActorRole.HUMAN)
            else:
                svc.submit_result("oracle", check.check_id, True, "agent", ActorRole.AGENT, value=check.threshold)
        svc.pass_gate("oracle", "maintainer")
        if project.passed(through):
            break
    if release and svc.get("oracle").passed(Stage.REPORT):
        svc.release("oracle", "maintainer", "Labels hold.")
    return svc


def repack(data, edit):
    """Rewrite a package's members through `edit(members) -> members`, keeping the container format."""
    members = {}
    with tarfile.open(fileobj=io.BytesIO(data), mode="r:gz") as tar:
        for info in tar:
            members[info.name] = tar.extractfile(info).read()
    members = edit(members)
    buffer = io.BytesIO()
    with gzip.GzipFile(fileobj=buffer, mode="wb", mtime=0) as gz, tarfile.open(fileobj=gz, mode="w") as tar:
        for name, content in members.items():
            info = tarfile.TarInfo(name)
            info.size = len(content)
            tar.addfile(info, io.BytesIO(content))
    return buffer.getvalue()


def test_round_trip_is_verified_read_only_and_deterministic(tmp_path):
    svc = build(tmp_path)
    data, manifest = export_package(svc, "oracle", tmp_path, created_at="2026-10-17T00:00:00+00:00")
    again, _ = export_package(svc, "oracle", tmp_path, created_at="2026-10-17T00:00:00+00:00")
    assert data == again  # byte-for-byte reproducible
    package = import_package(data)
    summary = package.summary()
    assert summary["read_only"] and summary["stage"] == "REPORT" and summary["version"] == 7
    assert summary["digest"] == svc.get("oracle").digest and len(summary["artifacts"]) == 7
    assert summary["releases"][0]["criteria"] == {"c1": "MET", "c2": "NOT_MET"}
    assert "c2" in package.readme and "does not reproduce the results" in package.readme
    with pytest.raises(LifecycleError):
        package.service.rework("oracle", "ANALYSIS", "someone", "try to change history")
    crate = json.loads(_member(data, "ro-crate-metadata.json"))
    assert crate["@graph"][0]["conformsTo"]["@id"] == "https://w3id.org/ro/crate/1.1"
    assert manifest["omissions"] == []


def _member(data, name):
    with tarfile.open(fileobj=io.BytesIO(data), mode="r:gz") as tar:
        return tar.extractfile(name).read()


def test_changed_or_missing_artifacts_are_declared_not_hidden(tmp_path):
    svc = build(tmp_path)
    (tmp_path / "runs/protocol.document.txt").write_text("edited after the gate\n", encoding="utf-8")
    (tmp_path / "runs/execution.raw_outputs.txt").unlink()
    data, manifest = export_package(svc, "oracle", tmp_path)
    kinds = {o["artifact_path"]: o["kind"] for o in manifest["omissions"]}
    assert kinds == {"runs/protocol.document.txt": "changed", "runs/execution.raw_outputs.txt": "missing"}
    assert len(import_package(data).summary()["artifacts"]) == 5


@pytest.mark.parametrize(
    "edit, message",
    [
        (lambda m: {**m, "objects/" + "0" * 64: b"x"}, "Unlisted"),
        (lambda m: {**m, "../evil": b"x"}, "Unexpected entry"),
        (lambda m: {k: v for k, v in m.items() if not k.startswith("objects/")}, "missing"),
        (lambda m: {**m, "README.md": b"rewritten"}, "does not match"),
        (lambda m: {k: v for k, v in m.items() if k != "manifest.json"}, "no manifest"),
    ],
)
def test_tampered_packages_are_refused(tmp_path, edit, message):
    data, _ = export_package(build(tmp_path), "oracle", tmp_path)
    with pytest.raises(PackageError, match=message):
        import_package(repack(data, edit))


def test_rewritten_history_with_fixed_checksums_is_still_refused(tmp_path):
    """An attacker who also fixes the inventory hashes cannot make a history say something else."""
    data, _ = export_package(build(tmp_path), "oracle", tmp_path)

    def rewrite(members):
        events = [json.loads(line) for line in members["events.jsonl"].decode().splitlines()]
        for event in events:  # flip an outcome after the fact
            if event["payload"].get("criteria"):
                event["payload"]["criteria"] = {"c1": "MET", "c2": "MET"}
        new = "".join(json.dumps(e, sort_keys=True) + "\n" for e in events).encode()
        manifest = json.loads(members["manifest.json"])
        for entry in manifest["inventory"]:
            if entry["path"] == "events.jsonl":
                entry["size"], entry["sha256"] = len(new), hashlib.sha256(new).hexdigest()
        return {**members, "events.jsonl": new, "manifest.json": json.dumps(manifest).encode()}

    with pytest.raises(PackageError, match="does not follow from the recorded results"):
        import_package(repack(data, rewrite))


def test_silently_dropped_artifact_is_refused(tmp_path):
    data, _ = export_package(build(tmp_path), "oracle", tmp_path)

    def drop(members):
        manifest = json.loads(members["manifest.json"])
        gone = next(e for e in manifest["inventory"] if e["kind"] == "artifact")
        manifest["inventory"].remove(gone)
        rest = {k: v for k, v in members.items() if k != gone["path"]}
        return {**rest, "manifest.json": json.dumps(manifest).encode()}

    with pytest.raises(PackageError, match="neither included nor explained"):
        import_package(repack(data, drop))


def test_newer_packages_are_refused(tmp_path):
    data, _ = export_package(build(tmp_path), "oracle", tmp_path)
    for change in ({"schema_version": 2}, {"required_features": ["future"]}):
        newer = repack(
            data, lambda m: {**m, "manifest.json": json.dumps({**json.loads(m["manifest.json"]), **change}).encode()}
        )
        with pytest.raises(PackageError, match="newer version"):
            import_package(newer)


def test_sensitive_content_blocks_export_unless_accepted(tmp_path):
    svc = build(tmp_path, through=Stage.QUESTION, release=False)
    path = tmp_path / "runs/question.statement.txt"
    path.write_text("api_key = abcdefghijklmnop\n", encoding="utf-8")
    sha = hashlib.sha256(path.read_bytes()).hexdigest()
    svc.rework("oracle", "QUESTION", "maintainer", "restate")
    svc.submit_result(
        "oracle",
        "question.statement",
        True,
        "agent",
        ActorRole.AGENT,
        artifact_path="runs/question.statement.txt",
        sha256=sha,
    )
    with pytest.raises(SensitiveContentError) as info:
        export_package(svc, "oracle", tmp_path)
    assert info.value.findings[0]["location"] == "runs/question.statement.txt"
    assert "abcdefghijklmnop" not in str(info.value)
    _, manifest = export_package(svc, "oracle", tmp_path, allow_sensitive=True)
    assert manifest["sensitive_content_accepted"]


def test_fork_is_writable_keeps_origin_and_materializes_artifacts(tmp_path):
    data, _ = export_package(build(tmp_path), "oracle", tmp_path)
    package = import_package(data)
    mine = LifecycleService(tmp_path / "mine.jsonl")
    fork = fork_package(package, mine, "oracle-rerun", materialize_root=tmp_path / "copy")
    assert fork.forked_from["manifest_sha256"] == package.manifest_sha256
    assert fork.digest == package.service.get("oracle").digest  # same history, same digests
    assert (tmp_path / "copy/runs/protocol.document.txt").read_text() == "content of protocol.document\n"
    mine.rework("oracle-rerun", "EXECUTION", "me", "re-run with a newer toolchain")
    assert mine.get("oracle-rerun").stage == Stage.EXECUTION
    replayed = LifecycleService(tmp_path / "mine.jsonl")
    assert replayed.get("oracle-rerun").forked_from == fork.forked_from
    with pytest.raises(LifecycleError):
        fork_package(package, mine, "oracle-rerun")


def test_cli_inspect_reports_validity(tmp_path, capsys):
    import scripts.research_package as cli

    svc_log = tmp_path / "log.jsonl"
    svc = build(tmp_path)
    svc_log.write_text("".join(json.dumps(e) + "\n" for e in svc.events), encoding="utf-8")
    out = tmp_path / "p.crpkg"
    assert (
        cli.main(["export", "--log", str(svc_log), "--project", "oracle", "--out", str(out), "--root", str(tmp_path)])
        == 0
    )
    capsys.readouterr()
    assert cli.main(["inspect", str(out)]) == 0
    assert json.loads(capsys.readouterr().out)["stage"] == "REPORT"
    out.write_bytes(out.read_bytes()[: len(out.read_bytes()) // 2])
    assert cli.main(["inspect", str(out)]) == 1


def test_a_wholly_rebuilt_history_verifies_but_changes_the_digest(tmp_path):
    """Verification proves internal consistency. Telling two consistent histories apart needs the digest published
    somewhere independent (claims register, OnTrack, a commit), which is why releases carry it."""
    honest = build(tmp_path)
    data, _ = export_package(honest, "oracle", tmp_path)
    other = LifecycleService.from_events(honest.project_events("oracle")[:1], read_only=False)
    for event in honest.project_events("oracle")[1:]:
        payload = json.loads(json.dumps(event["payload"]))
        if event["type"] == "result_submitted" and payload.get("criteria"):
            payload["criteria"] = {"c1": "MET", "c2": "MET"}
        if event["type"] == "gate_passed":
            other.pass_gate("oracle", payload["actor"])
            continue
        if event["type"] == "released":
            other.release("oracle", payload["actor"], payload["summary"])
            continue
        other.submit_result(
            "oracle", **{k: v for k, v in payload.items() if k != "role"}, role=ActorRole(payload["role"])
        )
    forged, _ = export_package(other, "oracle", tmp_path)
    assert import_package(forged).summary()["releases"][0]["criteria"] == {"c1": "MET", "c2": "MET"}
    assert import_package(forged).manifest["source"]["digest"] != import_package(data).manifest["source"]["digest"]


def test_replay_refuses_a_gate_the_results_do_not_pass(tmp_path):
    events = build(tmp_path, through=Stage.QUESTION, release=False).events
    tampered = [
        e for e in events if not (e["type"] == "result_submitted" and e["payload"]["check_id"] == "question.owner")
    ]
    with pytest.raises(LifecycleError, match="does not follow"):
        LifecycleService.from_events(tampered)


def test_api_export_then_inspect(api_client):
    pid = "api-package-test"
    api_client.post("/api/lifecycle/projects", json={"project_id": pid, "title": "API package"})
    response = api_client.get(f"/api/lifecycle/projects/{pid}/package")
    assert response.status_code == 200 and response.headers["content-type"] == "application/gzip"
    summary = api_client.post("/api/lifecycle/packages/inspect", content=response.content).json()
    assert summary["valid"] and summary["project_id"] == pid and summary["read_only"]
    assert api_client.post("/api/lifecycle/packages/inspect", content=b"not a package").json()["valid"] is False
