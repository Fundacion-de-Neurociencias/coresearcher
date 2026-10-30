"""Tests for the reproducible proof pipeline (proof_pipeline.py, ADR-076)."""

import importlib.util
import json
from pathlib import Path

from python.discovery import proof_pipeline as pp

ROOT = Path(__file__).resolve().parent.parent


def _mahler_steps():
    spec = importlib.util.spec_from_file_location("mahler_reproduce", ROOT / "scripts/cases/mahler_reproduce.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def test_committed_mahler_manifest_audits_clean():
    mod = _mahler_steps()
    manifest = json.loads(mod.MANIFEST.read_text(encoding="utf-8"))
    result = pp.check(mod.STEPS, manifest, mod.EX + "ledger.json")
    assert result["ok"], result
    assert result["ledger"]["consistent"]


def _toy(tmp_path):
    (tmp_path / "src.py").write_text("x = 1\n", encoding="utf-8")
    (tmp_path / "run.py").write_text("# writes out.json\n", encoding="utf-8")
    (tmp_path / "out.json").write_text(json.dumps({"r": {"verified": True}, "seconds": 3.0}), encoding="utf-8")
    step = pp.ProofStep("toy", "run.py", "out.json", ["r.verified"], ["src.py"])
    return step, pp.build_manifest([step], tmp_path)


def test_stale_source_and_unverified_report_fail_the_audit(tmp_path):
    step, manifest = _toy(tmp_path)
    assert pp.check([step], manifest, root=tmp_path)["ok"]
    # line endings and wall-clock time do not change the hashes
    (tmp_path / "src.py").write_bytes(b"x = 1\r\n")
    (tmp_path / "out.json").write_text(json.dumps({"r": {"verified": True}, "seconds": 9.0}), encoding="utf-8")
    assert pp.check([step], manifest, root=tmp_path)["ok"]
    (tmp_path / "src.py").write_text("x = 2\n", encoding="utf-8")
    res = pp.check([step], manifest, root=tmp_path)
    assert not res["ok"] and "STALE" in res["steps"]["toy"]["problems"][0]
    step, manifest = _toy(tmp_path)
    (tmp_path / "out.json").write_text(json.dumps({"r": {"verified": False}}), encoding="utf-8")
    probs = pp.check([step], manifest, root=tmp_path)["steps"]["toy"]["problems"]
    assert any("not verified" in p for p in probs) and any("differs" in p for p in probs)


def test_weakest_link_recomputation():
    led = {"claim": {"obligations": [{"status": "DISCHARGED_INTERVAL"}, {"status": "CHECKED_NUMERIC"}]}}
    assert pp.recompute_claim_status(led) == "CHECKED_NUMERIC"
    led["claim"]["obligations"].append({"status": "REFUTED"})
    assert pp.recompute_claim_status(led) == "REFUTED"
