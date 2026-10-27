"""`oase formal` inside an OASE checkout with apply.sh applied (ADR-DISCOVERY-069).

POSIX only: OASE imports fcntl. Run from the CI job `oase-conformance`:

    PYTHONPATH=<OASE>/tools CORESEARCHER_HOME=<repo> pytest integrations/oase/tests

Every test drives the real CLI (`oase.cli:cli`) in a fresh OASE program directory.
"""

from __future__ import annotations

import json
import os
import shutil
import sys
from pathlib import Path

import pytest

if sys.platform == "win32":  # pragma: no cover - collected only to explain the skip
    pytest.skip("OASE imports fcntl and runs on POSIX only", allow_module_level=True)

os.environ["OASE_NO_DIRTY_WARNING"] = "1"
ADAPTER = Path(__file__).resolve().parents[1]
REPO = ADAPTER.parents[1]
os.environ.setdefault("CORESEARCHER_HOME", str(REPO))
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

oase_cli = pytest.importorskip("oase.cli", reason="PYTHONPATH must include <OASE>/tools")
from click.testing import CliRunner  # noqa: E402
from oase.core import http, policy, provenance, thresholds  # noqa: E402
from oase.core.context import init_project  # noqa: E402
from oase.core.evidence import validate_assessment  # noqa: E402

INPUTS = ADAPTER / "demo" / "inputs"
ARTIFACTS = ADAPTER / "demo" / "artifacts"
OASE_ROOT = Path(oase_cli.__file__).resolve().parents[2]
CONSEQUENCE = (
    "not (stage == 'early' and trem2_function == 'normal' and treatment == 'agonist') "
    "or dystrophy_change != 'increase'"
)


@pytest.fixture(autouse=True)
def _clean_latches(monkeypatch):
    """The phase-2 network latch and the overwrite latch are per-process; reset them per test."""
    for var in ("FORMALIZER_MODEL", "FORMALIZER_GATE_MODELS", "CORESEARCHER_URL", "OASE_WORK_ORDER_ID"):
        monkeypatch.delenv(var, raising=False)
    http._network_forbidden = None
    provenance.allow_overwrite(False)
    yield
    http._network_forbidden = None
    provenance.allow_overwrite(False)


@pytest.fixture
def project(tmp_path, monkeypatch):
    root = init_project(tmp_path / "program")
    shutil.copytree(INPUTS, root / "inputs")
    monkeypatch.setenv("OASE_PROJECT", str(root))
    monkeypatch.chdir(root)
    return root


def oase(*args):
    return CliRunner().invoke(oase_cli.cli, list(args), catch_exceptions=False)


def analysis(project: Path, stem: str) -> dict:
    return json.loads((project / "raw" / "formal" / f"{stem}.analysis.json").read_text())


def codes(record: dict) -> list[str]:
    return [r["code"] for r in record.get("mandatory_relays", [])]


# ---------------------------------------------------------------------------
# Registration and conformance
# ---------------------------------------------------------------------------


def test_registered_with_conformant_options():
    group = oase_cli.cli.commands["formal"]
    run, analyze = group.commands["run"], group.commands["analyze"]
    run_params = {p.name for p in run.params}
    analyze_params = {p.name for p in analyze.params}
    assert {"out", "overwrite", "as_json", "quiet"} <= run_params
    # --overwrite and --overwrite-cross-wo are injected into phase 2 by enforce_phase_two.
    assert {"out", "overwrite", "overwrite_cross_wo", "as_json", "quiet"} <= analyze_params
    assert getattr(analyze.callback, "_phase_two_guarded", False)


def test_threshold_set_and_relays_registered():
    ts = thresholds.load("formal")
    assert ts.tag == "formal@1.0"
    assert ts.get("max_formal_defects") == 0
    assert ts.unresolved() == ["min_excluded_fraction_of_applicable"]
    from python.discovery.formal_thresholds import FORMAL_DEFAULTS

    for key, value in FORMAL_DEFAULTS.values.items():
        assert ts.get(key) == value, f"formal@1.0 {key} drifted from CoResearcher's default"
    from oase.commands.formal import _oase_code

    from python.discovery.formal_status import RELAY_CODES as CR_RELAYS

    for code in [*CR_RELAYS, "UNDECIDED", "BLOCKED", "FORMALIZATION_AMBIGUOUS", "FORMALIZATION_FAILED"]:
        assert _oase_code(code) in provenance.RELAY_CODES


def test_relays_command_attributes_every_formal_code():
    result = oase("relays", "--json")
    records = json.loads(result.output)
    formal_codes = {c: r for c, r in records.items() if c.startswith("formal.")}
    assert len(formal_codes) == 14
    for code, record in formal_codes.items():
        assert record["emitted_by"], f"{code} has no emission site"


def test_doctor_reports_formal_capabilities():
    result = oase("doctor")
    assert "formal: coresearcher engine" in result.output
    assert "formal: z3 solver" in result.output
    result = oase("formal", "doctor", "--json")
    assert result.exit_code == 0
    names = {c["name"]: c for c in json.loads(result.output)["checks"]}
    assert names["formal: z3 solver"]["ok"] is True


# ---------------------------------------------------------------------------
# Decided verdicts
# ---------------------------------------------------------------------------


def test_rivals_end_to_end(project):
    result = oase(
        "formal",
        "run",
        "inputs/H-0001.json",
        "--formal",
        "inputs/H-0001.formal.json",
        "--rival",
        "inputs/H-0002.formal.json",
        "--consequence",
        CONSEQUENCE,
    )
    assert result.exit_code == 0, result.output
    lines = result.output.strip().splitlines()
    assert lines == [
        "raw/formal/fm-H-0001_vs_H-0002.request.json",
        "raw/formal/fm-H-0001_vs_H-0002.response.json",
        "raw/formal/fm-H-0001_vs_H-0002.meta.json",
    ]
    meta = json.loads((project / lines[2]).read_text())
    assert meta["tool"] == "formal" and len(meta["outputs"]) == 2
    assert all(len(o["sha256"]) == 64 for o in meta["outputs"])
    assert "formal.not_empirical" in codes(meta)

    result = oase("formal", "analyze", lines[2])
    assert result.exit_code == 0, result.output
    record = analysis(project, "fm-H-0001_vs_H-0002")
    a = record["assessment"]
    assert record["threshold_set"] == "formal@1.0"
    assert record["source"] == "raw/formal/fm-H-0001_vs_H-0002.response.json"
    assert a["verdict"]["content_verdict"] == "FALSIFIABLE"
    assert a["verdict"]["relations"] == {"H-0002": "INCOMPARABLE"}
    assert a["reproduction"]["reproduces_run"] is True
    assert a["criteria"]["max_formal_defects"]["met"] is True
    assert a["criteria"]["min_excluded_fraction_of_applicable"]["met"] is None
    assert a["evidence_assessment"]["evidence_status"] == "supported"
    states = a["reports"]["comparisons"][0]["discriminating_examples"]
    assert {"stage": "early", "trem2_function": "normal", "treatment": "agonist", "dystrophy_change": "decrease"} in [
        s["state"] for s in states
    ]
    assert "formal.not_empirical" in codes(record)


@pytest.mark.parametrize("hid,verdict", [("H-0003", "SELF_CONTRADICTORY"), ("H-0004", "UNFALSIFIABLE")])
def test_decided_defect_is_contradicted_and_exits_zero(project, hid, verdict):
    assert oase("formal", "run", f"inputs/{hid}.json", "--formal", f"inputs/{hid}.formal.json").exit_code == 0
    result = oase("formal", "analyze", f"raw/formal/fm-{hid}.meta.json")
    assert result.exit_code == 0, "a negative answer is an answer: exit 0"
    a = analysis(project, f"fm-{hid}")["assessment"]
    assert a["criteria"]["defects"] == [verdict]
    assert a["criteria"]["max_formal_defects"]["met"] is False
    assert a["evidence_assessment"]["execution_outcome"] == "completed"
    assert a["evidence_assessment"]["evidence_status"] == "contradicted"


def test_rerun_identical_is_a_cache_hit_and_different_is_refused(project):
    args = ["formal", "run", "inputs/H-0002.json", "--formal", "inputs/H-0002.formal.json"]
    assert oase(*args).exit_code == 0
    assert oase(*args, "--json").exit_code == 0
    assert json.loads(oase(*args, "--json").output)["cached"] is True
    result = oase(*args, "--consequence", "dystrophy_change != 'increase'")
    assert result.exit_code == 9
    assert oase(*args, "--consequence", "dystrophy_change != 'increase'", "--overwrite").exit_code == 0


def test_adopted_set_candidate(project):
    hset = {
        "schema": "oase.hypothesis-set.v1",
        "origin": "charter",
        "candidates": [
            {"candidate_id": "1", "statement": "first"},
            {"candidate_id": "2", "statement": "Early TREM2 agonism reduces dystrophy when TREM2 works."},
        ],
    }
    (project / "raw/hypotheses/demo.charter.json").write_text(json.dumps(hset))
    formal = json.loads((INPUTS / "H-0001.formal.json").read_text())
    formal["hypothesis_id"] = "demo-c2"
    (project / "inputs/c2.formal.json").write_text(json.dumps(formal))
    assert oase("formal", "run", "raw/hypotheses/demo.charter.json", "--formal", "inputs/c2.formal.json").exit_code == 2
    result = oase(
        "formal", "run", "raw/hypotheses/demo.charter.json", "--candidate", "2", "--formal", "inputs/c2.formal.json"
    )
    assert result.exit_code == 0, result.output
    assert oase("formal", "analyze", "raw/formal/fm-demo-c2.meta.json").exit_code == 0
    assert (
        oase(
            "formal", "run", "raw/hypotheses/demo.charter.json", "--candidate", "9", "--formal", "inputs/c2.formal.json"
        ).exit_code
        == 9
    )


def test_identity_mismatch_is_refused(project):
    result = oase("formal", "run", "inputs/H-0001.json", "--formal", "inputs/H-0002.formal.json")
    assert result.exit_code == 9
    assert not (project / "raw/formal/fm-H-0001.meta.json").exists()


def test_rival_over_other_variables_is_invalid_input(project):
    rival = json.loads((INPUTS / "H-0002.formal.json").read_text())
    rival["variables"] = rival["variables"][:2]
    rival["claims"] = ["stage == 'early'"]
    rival["assumptions"] = []
    (project / "inputs/odd.formal.json").write_text(json.dumps(rival))
    result = oase(
        "formal",
        "run",
        "inputs/H-0001.json",
        "--formal",
        "inputs/H-0001.formal.json",
        "--rival",
        "inputs/odd.formal.json",
    )
    assert result.exit_code == 9
    result = oase("formal", "analyze", "raw/formal/fm-H-0001_vs_H-0002.meta.json")
    assert result.exit_code == 9
    a = analysis(project, "fm-H-0001_vs_H-0002")["assessment"]
    assert a["formal_status"] == "INVALID_INPUT"
    assert a["evidence_assessment"]["evidence_status"] == "not_assessed"


# ---------------------------------------------------------------------------
# Non-verdicts are never negatives
# ---------------------------------------------------------------------------


def _continuous(project: Path) -> None:
    h = json.loads((INPUTS / "H-0001.json").read_text())
    h["id"] = "H-0042"
    (project / "inputs/H-0042.json").write_text(json.dumps(h))
    obj = {
        "hypothesis_id": "H-0042",
        "variables": [{"name": f"x{i}", "continuous": True, "lower": 0, "upper": 100} for i in range(3)],
        "scope": None,
        "assumptions": [],
        "claims": ["x0 * x1 * x2 - x0 * x0 * x1 > 7"],
    }
    (project / "inputs/H-0042.formal.json").write_text(json.dumps(obj))


def test_undecided_exits_10_and_maps_to_not_assessed(project, monkeypatch):
    _continuous(project)
    import z3

    from python.discovery import formal_smt

    class Unknown(z3.Solver):
        def check(self, *args):
            return z3.unknown

        def reason_unknown(self):
            return "timeout"

    monkeypatch.setattr(formal_smt.z3, "Solver", Unknown)
    result = oase(
        "formal", "run", "inputs/H-0042.json", "--formal", "inputs/H-0042.formal.json", "--solver-timeout-ms", "1"
    )
    assert result.exit_code == 10, result.output
    meta = json.loads((project / "raw/formal/fm-H-0042.meta.json").read_text())
    assert meta["formal_status"] == "UNDECIDED"
    assert "formal.undecided" in codes(meta)
    assert meta["threshold_sources"]["solver_timeout_ms"] == "flag"
    assert oase("formal", "analyze", "raw/formal/fm-H-0042.meta.json", "--solver-timeout-ms", "1").exit_code == 10
    a = analysis(project, "fm-H-0042")["assessment"]
    assert a["evidence_assessment"]["execution_outcome"] == "blocked"
    assert a["evidence_assessment"]["evidence_status"] == "not_assessed"
    assert a["criteria"]["max_formal_defects"]["met"] is None
    assert a["verdict"] == {}


def test_prose_without_a_model_is_blocked_not_negative(project):
    result = oase("formal", "run", "inputs/H-0001.json")
    assert result.exit_code == 8
    assert (project / "raw/formal/fm-H-0001.meta.json").is_file()
    result = oase("formal", "analyze", "raw/formal/fm-H-0001.meta.json")
    assert result.exit_code == 8
    record = analysis(project, "fm-H-0001")
    assert record["assessment"]["formal_status"] == "BLOCKED"
    assert record["assessment"]["evidence_assessment"]["evidence_status"] == "not_assessed"
    assert codes(record) == ["formal.blocked"]


class _Fake:
    def __init__(self, outputs, model="fake"):
        self.outputs, self.model, self.calls = list(outputs), model, 0

    def complete(self, messages, temperature=0.0, seed=0):
        self.calls += 1
        return self.outputs[(self.calls - 1) % len(self.outputs)]


def _formal_text(claims):
    obj = json.loads((INPUTS / "H-0001.formal.json").read_text())
    return json.dumps(
        {"variables": obj["variables"], "scope": obj["scope"], "assumptions": obj["assumptions"], "claims": claims}
    )


def test_prose_gate_consistent_is_draft_and_reproduced_offline(project, monkeypatch):
    claims = json.loads((INPUTS / "H-0001.formal.json").read_text())["claims"]
    fake = _Fake([_formal_text(claims)])
    from oase.commands import formal as adapter

    monkeypatch.setattr(adapter, "_formalizer_clients", lambda cr: {"fake": fake})
    result = oase("formal", "run", "inputs/H-0001.json", "--samples", "3")
    assert result.exit_code == 0, result.output
    assert fake.calls == 3
    monkeypatch.setattr(adapter, "_formalizer_clients", lambda cr: pytest.fail("analyze called a model"))
    assert oase("formal", "analyze", "raw/formal/fm-H-0001.meta.json").exit_code == 0
    record = analysis(project, "fm-H-0001")
    assert record["assessment"]["reproduction"]["reproduces_run"] is True
    assert "formal.formalization_is_draft" in codes(record)
    assert record["assessment"]["formalization_gate"]["status"] == "CONSISTENT"


def test_prose_gate_ambiguous_is_refused_never_picked(project, monkeypatch):
    fake = _Fake(
        [
            _formal_text(["dystrophy_change == 'decrease'"]),
            _formal_text(["dystrophy_change == 'none'"]),
            _formal_text(["dystrophy_change == 'increase'"]),
        ]
    )
    from oase.commands import formal as adapter

    monkeypatch.setattr(adapter, "_formalizer_clients", lambda cr: {"fake": fake})
    result = oase("formal", "run", "inputs/H-0001.json", "--samples", "3")
    assert result.exit_code == 9
    assert oase("formal", "analyze", "raw/formal/fm-H-0001.meta.json").exit_code == 9
    record = analysis(project, "fm-H-0001")
    a = record["assessment"]
    assert a["formal_status"] == "FORMALIZATION_AMBIGUOUS"
    assert a["reports"]["evaluation"] is None
    assert a["evidence_assessment"]["evidence_status"] == "not_assessed"
    assert "formal.formalization_ambiguous" in codes(record)


# ---------------------------------------------------------------------------
# Phase 2 is offline, checks its inputs and detects fabrication
# ---------------------------------------------------------------------------


def _run_h2(project):
    assert oase("formal", "run", "inputs/H-0002.json", "--formal", "inputs/H-0002.formal.json").exit_code == 0
    return project / "raw/formal/fm-H-0002.response.json"


def test_tampered_response_is_an_artifact_error(project):
    path = _run_h2(project)
    path.write_text(path.read_text().replace("FALSIFIABLE", "UNFALSIFIABLE"))
    assert oase("formal", "analyze", "raw/formal/fm-H-0002.meta.json").exit_code == 3


def test_fabricated_verdict_with_reforged_checksum_is_not_reproduced(project):
    path = _run_h2(project)
    record = json.loads(path.read_text())
    record["coresearcher_response"]["reports"]["evaluation"]["content_verdict"] = "UNFALSIFIABLE"
    path.write_text(json.dumps(record, indent=2) + "\n")
    meta_path = project / "raw/formal/fm-H-0002.meta.json"
    meta = json.loads(meta_path.read_text())
    for entry in meta["outputs"]:
        if entry["path"] == path.name:
            entry["sha256"] = provenance.sha256_file(path)
            entry["bytes"] = path.stat().st_size
    meta_path.write_text(json.dumps(meta, indent=2))
    result = oase("formal", "analyze", "raw/formal/fm-H-0002.meta.json")
    assert result.exit_code == 12
    record = analysis(project, "fm-H-0002")
    assert record["assessment"]["reproduction"]["reproduces_run"] is False
    assert "formal.not_reproduced" in codes(record)
    # The recomputed verdict is what the analysis carries, not the edited one.
    assert record["assessment"]["verdict"]["content_verdict"] == "FALSIFIABLE"


def _reforge(project, path):
    meta_path = project / "raw/formal/fm-H-0002.meta.json"
    meta = json.loads(meta_path.read_text())
    for entry in meta["outputs"]:
        if entry["path"] == path.name:
            entry["sha256"] = provenance.sha256_file(path)
            entry["bytes"] = path.stat().st_size
    meta_path.write_text(json.dumps(meta, indent=2))


def test_engine_upgrade_is_an_environment_change_not_a_disagreement(project):
    """A run stamped by another z3 build reproduces if its verdict digests match (OASE: env stamps are volatile)."""
    path = _run_h2(project)
    record = json.loads(path.read_text())
    record["coresearcher_response"]["reports"]["evaluation"]["provenance"]["z3_version"] = "0.0.1"
    path.write_text(json.dumps(record, indent=2) + "\n")
    _reforge(project, path)
    result = oase("formal", "analyze", "raw/formal/fm-H-0002.meta.json")
    assert result.exit_code == 0, result.output
    reproduction = analysis(project, "fm-H-0002")["assessment"]["reproduction"]
    assert reproduction["reproduces_run"] is True
    assert [c["field"] for c in reproduction["engine_changes"]] == ["z3_version"]
    assert "0.0.1" in reproduction["engine_changes"][0]["run"]


def test_analyze_refuses_the_network(project, monkeypatch):
    _run_h2(project)
    from python.discovery import formal_pipeline

    real = formal_pipeline.compute

    def phoning_home(*a, **k):
        import socket

        socket.create_connection(("example.org", 80), timeout=1)
        return real(*a, **k)

    monkeypatch.setattr(formal_pipeline, "compute", phoning_home)
    result = oase("formal", "analyze", "raw/formal/fm-H-0002.meta.json")
    assert result.exit_code == 1  # PhaseContractError: a bug in phase 2, not a caller error


def test_differing_analysis_is_not_replaced_without_overwrite(project):
    _run_h2(project)
    assert oase("formal", "analyze", "raw/formal/fm-H-0002.meta.json").exit_code == 0
    assert oase("formal", "analyze", "raw/formal/fm-H-0002.meta.json").exit_code == 0  # identical: kept
    changed = ["formal", "analyze", "raw/formal/fm-H-0002.meta.json", "--max-formal-defects", "1"]
    assert oase(*changed).exit_code == 9
    assert oase(*changed, "--out", "raw/formal/second-opinion").exit_code == 0
    assert oase(*changed, "--overwrite").exit_code == 0


# ---------------------------------------------------------------------------
# Thresholds
# ---------------------------------------------------------------------------


def test_program_override_resolves_unresolved_threshold(project):
    (project / ".oase/thresholds.yaml").write_text("formal:\n  min_excluded_fraction_of_applicable: 0.25\n")
    _run_h2(project)
    assert oase("formal", "analyze", "raw/formal/fm-H-0002.meta.json").exit_code == 0
    record = analysis(project, "fm-H-0002")
    crit = record["assessment"]["criteria"]["min_excluded_fraction_of_applicable"]
    assert crit["threshold"] == 0.25 and crit["met"] in (True, False)
    assert record["threshold_sources"]["min_excluded_fraction_of_applicable"] == "program"
    assert record["threshold_set"] == "formal@1.0+program"


def test_engine_threshold_override_fires_relay(project):
    result = oase(
        "formal", "run", "inputs/H-0002.json", "--formal", "inputs/H-0002.formal.json", "--max-states", "1000"
    )
    assert result.exit_code == 0
    meta = json.loads((project / "raw/formal/fm-H-0002.meta.json").read_text())
    assert "formal.thresholds_overridden" in codes(meta)
    assert meta["coresearcher"]["threshold_sources"]["max_states"] == "oase"


def test_engine_threshold_cap_exceeded_is_blocked(project):
    result = oase("formal", "run", "inputs/H-0002.json", "--formal", "inputs/H-0002.formal.json", "--max-states", "4")
    assert result.exit_code == 4
    meta = json.loads((project / "raw/formal/fm-H-0002.meta.json").read_text())
    assert meta["formal_status"] == "BLOCKED"


# ---------------------------------------------------------------------------
# HTTP transport, against the real CoResearcher API in-process
# ---------------------------------------------------------------------------


def test_http_transport_matches_package(project, monkeypatch):
    pytest.importorskip("fastapi")
    monkeypatch.setenv("CORESEARCHER_API_KEY", "test-key")
    monkeypatch.setenv("CORESEARCHER_URL", "http://coresearcher.test")
    monkeypatch.setenv("CORESEARCHER_RATE_LIMIT_PER_MINUTE", "100000")
    from fastapi.testclient import TestClient

    from api.server import app

    client = TestClient(app)

    def via_testclient(method, url, *, json=None, headers=None, tolerate_status=(), **_k):
        assert http.network_forbidden() is None, "phase 2 must not call the API"
        response = client.request(method, url.replace("http://coresearcher.test", ""), json=json, headers=headers)
        assert response.status_code == 200 or response.status_code in tolerate_status
        return response

    monkeypatch.setattr(http, "request", via_testclient)
    args = [
        "formal",
        "run",
        "inputs/H-0001.json",
        "--formal",
        "inputs/H-0001.formal.json",
        "--rival",
        "inputs/H-0002.formal.json",
        "--consequence",
        CONSEQUENCE,
    ]
    result = oase(*args, "--transport", "http", "--out", "raw/formal/http")
    assert result.exit_code == 0, result.output
    response = json.loads((project / "raw/formal/http/fm-H-0001_vs_H-0002.response.json").read_text())
    assert [e["route"] for e in response["http_exchanges"]] == [
        "/api/hypotheses/evaluate",
        "/api/hypotheses/compare",
        "/api/hypotheses/entails",
    ]
    assert oase("formal", "analyze", "raw/formal/http/fm-H-0001_vs_H-0002.meta.json").exit_code == 0
    record = json.loads((project / "raw/formal/http/fm-H-0001_vs_H-0002.analysis.json").read_text())
    assert record["assessment"]["reproduction"]["reproduces_run"] is True
    assert oase(*args).exit_code == 0
    assert oase("formal", "analyze", "raw/formal/fm-H-0001_vs_H-0002.meta.json").exit_code == 0
    package = analysis(project, "fm-H-0001_vs_H-0002")
    assert package["assessment"]["verdict"] == record["assessment"]["verdict"]


def test_http_transport_refuses_prose(project, monkeypatch):
    monkeypatch.setenv("CORESEARCHER_URL", "http://coresearcher.test")
    assert oase("formal", "run", "inputs/H-0001.json", "--transport", "http").exit_code == 9


# ---------------------------------------------------------------------------
# The documented uses: hypex inputs, Stage 1 gate, committed demo
# ---------------------------------------------------------------------------


def test_demo_inputs_are_valid_hypex_hypotheses():
    jsonschema = pytest.importorskip("jsonschema")
    schema_path = OASE_ROOT / "tools/vendor/hypex/hypothesis-explorer/schemas/hypothesis.schema.json"
    schema = json.loads(schema_path.read_text())
    for path in sorted(INPUTS.glob("H-[0-9][0-9][0-9][0-9].json")):
        jsonschema.validate(json.loads(path.read_text()), schema)


def test_gate_policy_and_assessments_validate_and_match():
    gp = json.loads((ADAPTER / "gate/GP-001.formal-soundness.json").read_text())
    assert policy.validate_policy(gp) == []
    req = gp["requirements"][0]
    ts = thresholds.load("formal")
    assert req["threshold_set"] == ts.tag
    ts.get(req["threshold_key"])  # resolvable, not UNRESOLVED
    for name in ("gate-AR-001.json", "gate-AR-002.json", "gate-AR-003.json"):
        ar = json.loads((ARTIFACTS / "gate" / name).read_text())
        assert validate_assessment(ar) == [], name
        match = policy.match_assessment_to_requirement(req, ar)
        assert match["matches"] is True and not match["method_excluded"] or ar["execution_outcome"] != "completed"
    statuses = {
        json.loads((ARTIFACTS / "gate" / n).read_text())["evidence_status"]
        for n in ("gate-AR-001.json", "gate-AR-002.json", "gate-AR-003.json")
    }
    assert statuses == {"supported", "contradicted", "not_assessed"}
    snap = policy.freeze_policy(
        gp,
        {"formal@1.0": ts},
        snapshot_id="SNAP-001",
        concept_refs=["IC-001"],
        assessments=["AR-001", "AR-002", "AR-003"],
    )
    assert snap["threshold_sets"]["formal@1.0"]["unresolved"] == ["min_excluded_fraction_of_applicable"]


def test_committed_demo_artifacts_reproduce_here(tmp_path, monkeypatch):
    root = init_project(tmp_path / "replay")
    shutil.copytree(ARTIFACTS / "raw" / "formal", root / "raw" / "formal", dirs_exist_ok=True)
    monkeypatch.setenv("OASE_PROJECT", str(root))
    monkeypatch.chdir(root)
    for meta in sorted((root / "raw/formal").glob("fm-*.meta.json")):
        result = oase("formal", "analyze", str(meta.relative_to(root)), "--out", "raw/formal/replay")
        assert result.exit_code == 0, (meta.name, result.output)
        replay = json.loads(
            (root / "raw/formal/replay" / meta.name.replace(".meta.json", ".analysis.json")).read_text()
        )
        committed = json.loads(meta.with_name(meta.name.replace(".meta.json", ".analysis.json")).read_text())
        assert replay["assessment"]["reproduction"]["reproduces_run"] is True
        assert replay["assessment"]["verdict"] == committed["assessment"]["verdict"]
        assert replay["assessment"]["criteria"] == committed["assessment"]["criteria"]
