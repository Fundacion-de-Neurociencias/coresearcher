"""Kernel records and the KERNEL_CHECKED rung (ADR-DISCOVERY-092), on synthetic records.

The records here are built from hand-written logs in the shape `scripts/lean/kernel_check.py` writes: Lean output,
`#print axioms` lines and the runner's exit-code footer. No Lean runs in these tests.
"""

import json
from pathlib import Path

import pytest

from python.discovery import cited_registry as cr
from python.discovery import formal_trust
from python.discovery import kernel_records as kr
from python.discovery.trust_ladder import ClaimRecord, LadderError, Rung

H = "a" * 64
STANDARD = "'Demo.main' depends on axioms: [propext, Classical.choice, Quot.sound]\n"


def _log(body: str = STANDARD, code: int = 0) -> str:
    return f"# kernel-check lean_file demo\n{body}{kr.FOOTER}{code}\n"


def _write(tmp_path: Path, log: str, *, kind="lean_file", theorems=("Demo.main",), blocked="", name="demo") -> Path:
    record = kr.build(
        target=name,
        kind=kind,
        source={"repository": "example/repo", "commit": "c" * 40, "path": "Demo.lean"},
        file_sha256=H,
        toolchain="leanprover/lean4:v4.35.0",
        lean_version="Lean (version 4.35.0)",
        mathlib_rev="b" * 40,
        theorems=list(theorems),
        log=log,
        kernel_log=f"{name}.log",
        wall_time_s=5.7,
        checked_by="https://github.com/example/repo/actions/runs/1",
        date="2026-11-02T00:00:00Z",
        blocked_reason=blocked,
    )
    (tmp_path / f"{name}.log").write_bytes(log.encode("utf-8"))
    path = tmp_path / f"{name}.json"
    path.write_text(json.dumps(record, indent=2), encoding="utf-8")
    return path


def _audited_claim() -> ClaimRecord:
    claim = ClaimRecord("c", "a claim", "Claimant").start(
        "2026-11-01", "announced", {"announcement": "a", "announcement_sha256": H}
    )
    claim.climb(Rung.STATEMENT_PUBLIC, "2026-11-01", "public", {"statement_location": "x", "statement_sha256": H})
    claim.climb(
        Rung.STATEMENT_AUDITED,
        "2026-11-01",
        "audited",
        {"checklist": "c", "checklist_sha256": H, "audit_report": "r", "audit_outcome": "EQUIVALENT"},
    )
    return claim


# --- results are computed from the log -------------------------------------------------------------------------


def test_pass_needs_exit_zero_axioms_for_every_theorem_and_only_standard_axioms():
    result, reasons, axioms = kr.evaluate("lean_file", _log(), ["Demo.main"])
    assert (result, reasons) == (kr.PASS, [])
    assert axioms["Demo.main"] == ["Classical.choice", "Quot.sound", "propext"]


@pytest.mark.parametrize(
    "log, theorems, why",
    [
        (_log("'Demo.main' depends on axioms: [propext, sorryAx]\n"), ["Demo.main"], "sorryAx"),
        (_log(code=1), ["Demo.main"], "exited with code 1"),
        (STANDARD, ["Demo.main"], "no exit-code footer"),
        (_log("Demo.lean:3:2: error: unknown identifier 'x'\n" + STANDARD), ["Demo.main"], "Lean error line"),
        (_log(), ["Demo.main", "Demo.other"], "no #print axioms output"),
        (_log(), [], "no theorem was checked"),
        (_log("'Demo.main' depends on axioms: [propext, Demo.myAxiom]\n"), ["Demo.main"], "Demo.myAxiom"),
    ],
)
def test_anything_short_of_a_clean_run_is_fail(log, theorems, why):
    result, reasons, _ = kr.evaluate("lean_file", log, theorems)
    assert result == kr.FAIL
    assert any(why in r for r in reasons), reasons


def test_comparator_also_needs_its_success_line():
    assert kr.evaluate("comparator", _log(), ["Demo.main"])[0] == kr.FAIL
    ok = _log("Building Solution\n" + kr.COMPARATOR_OK + "\n" + kr.AXIOMS_PROBE + "Demo.lean\n" + STANDARD)
    assert kr.evaluate("comparator", ok, ["Demo.main"])[0] == kr.PASS


def test_blocked_is_a_non_verdict_whatever_the_log_says():
    result, reasons, _ = kr.evaluate("comparator", _log(), ["Demo.main"], "landrun cannot run here")
    assert (result, reasons) == (kr.BLOCKED, ["landrun cannot run here"])


def test_axiom_lines_with_primes_wrapping_and_no_axioms():
    log = (
        "X.lean:9:0: info: 'Demo.foo'' depends on axioms: [propext,\n Classical.choice]\n"
        "'Demo.bar' does not depend on any axioms\n"
    )
    assert kr.parse_axioms(log) == {"Demo.foo'": ["Classical.choice", "propext"], "Demo.bar": []}


def test_theorem_names_follow_namespaces_sections_and_skip_comments():
    text = """import Mathlib
/- theorem commented_out : True := trivial -/
namespace A.B
theorem t1 : True := trivial
section S
lemma t2 : True := trivial
end S
namespace C
@[simp] protected theorem t3 : True := trivial
end C
theorem _root_.top : True := trivial
end A.B
/-- doc -/
theorem t4 : True := trivial
"""
    assert kr.theorem_names(text) == ["A.B.t1", "A.B.t2", "A.B.C.t3", "top", "t4"]


# --- records are hash-verified ---------------------------------------------------------------------------------


def test_a_stored_pass_record_loads_and_matches_its_log(tmp_path):
    path = _write(tmp_path, _log())
    record = kr.load(path)
    assert record["result"] == kr.PASS and record["status"] == "KERNEL_CHECKED"
    assert record["axioms"] == ["Classical.choice", "Quot.sound", "propext"]
    assert record["exit_code"] == 0 and kr.record_reasons(record) == []


def test_an_edited_log_is_refused(tmp_path):
    path = _write(tmp_path, _log())
    (tmp_path / "demo.log").write_bytes(_log().replace("propext, ", "").encode())
    with pytest.raises(kr.KernelRecordError, match="does not hash"):
        kr.load(path)


def test_a_record_edited_from_fail_to_pass_is_refused(tmp_path):
    path = _write(tmp_path, _log("'Demo.main' depends on axioms: [sorryAx]\n"))
    record = json.loads(path.read_text())
    record.update(result=kr.PASS, status="KERNEL_CHECKED", reasons=[])
    path.write_text(json.dumps(record))
    with pytest.raises(kr.KernelRecordError, match="supports result FAIL"):
        kr.load(path)


def test_a_record_with_edited_axioms_is_refused(tmp_path):
    path = _write(tmp_path, _log())
    record = json.loads(path.read_text())
    record["axioms_by_theorem"]["Demo.main"] = ["propext"]
    path.write_text(json.dumps(record))
    with pytest.raises(kr.KernelRecordError, match="axioms"):
        kr.load(path)


def test_a_missing_log_is_refused(tmp_path):
    path = _write(tmp_path, _log())
    (tmp_path / "demo.log").unlink()
    with pytest.raises(kr.KernelRecordError, match="missing"):
        kr.load(path)


def test_records_dir_paths_cannot_escape():
    with pytest.raises(kr.KernelRecordError):
        kr.in_records_dir("../../pyproject.toml")
    with pytest.raises(kr.KernelRecordError):
        kr.in_records_dir("../x.json")
    assert kr.in_records_dir("2026-11-02-run1/demo.json").name == "demo.json"


# --- the trust ladder climbs only from a verified PASS record ----------------------------------------------------


def test_a_verified_pass_record_lifts_a_claim_to_kernel_checked(tmp_path):
    claim = kr.climb(_audited_claim(), _write(tmp_path, _log()), "2026-11-02", "kernel run")
    assert claim.rung is Rung.KERNEL_CHECKED
    assert claim.formal_status == "DECIDED" and claim.mandatory_relays == []
    step = claim.history[-1].evidence
    assert step["checked_by"].endswith("/actions/runs/1") and step["kernel_record_sha256"] == kr.record_sha256(
        step["kernel_record"]
    )


@pytest.mark.parametrize(
    "log, blocked",
    [
        (_log("'Demo.main' depends on axioms: [propext, sorryAx]\n"), ""),
        (_log(code=1), ""),
        (_log(), "comparator did not finish within 15300 s"),
    ],
)
def test_fail_and_blocked_records_never_climb(tmp_path, log, blocked):
    path = _write(tmp_path, log, blocked=blocked)
    assert kr.load(path)["result"] in (kr.FAIL, kr.BLOCKED)
    claim = _audited_claim()
    with pytest.raises(kr.KernelRecordError, match="never climbs"):
        kr.climb(claim, path, "2026-11-02", "kernel run")
    assert claim.rung is Rung.STATEMENT_AUDITED


def test_hand_written_kernel_evidence_is_refused(tmp_path):
    claim = _audited_claim()
    with pytest.raises(LadderError):
        claim.climb(
            Rung.KERNEL_CHECKED,
            "2026-11-02",
            "asserted",
            {"toolchain": "lean4", "axioms": ["propext"], "kernel_log_sha256": H, "checked_by": "me"},
        )
    evidence = kr.ladder_evidence(_write(tmp_path, _log()))
    for key, value in [("checked_by", "someone else"), ("kernel_record_sha256", H), ("axioms", [])]:
        forged = dict(evidence, **{key: value})
        with pytest.raises(LadderError):
            claim.climb(Rung.KERNEL_CHECKED, "2026-11-02", "forged", forged)
    forged_record = dict(evidence["kernel_record"], wall_time_s=1.0)
    forged = dict(evidence, kernel_record=forged_record, kernel_record_sha256=kr.record_sha256(forged_record))
    with pytest.raises(LadderError, match="differs from the embedded record"):
        claim.climb(Rung.KERNEL_CHECKED, "2026-11-02", "forged", forged)
    assert claim.rung is Rung.STATEMENT_AUDITED


def test_a_stored_claim_replays_without_its_log_but_not_with_an_edited_record(tmp_path):
    path = _write(tmp_path, _log())
    stored = json.loads(json.dumps(kr.climb(_audited_claim(), path, "2026-11-02", "kernel").to_dict()))
    (tmp_path / "demo.log").unlink()
    assert ClaimRecord.from_dict(stored).rung is Rung.KERNEL_CHECKED
    stored["history"][-1]["evidence"]["kernel_record"]["result"] = kr.FAIL
    with pytest.raises(LadderError):
        ClaimRecord.from_dict(stored)


def test_trust_check_view_feeds_the_adr080_grader(tmp_path):
    record = kr.load(_write(tmp_path, _log()))
    assert formal_trust.kernel_check_reasons(kr.trust_check(record, H), H) == []
    failed = kr.load(_write(tmp_path, _log(code=1), name="failed"))
    assert any("NOT_KERNEL_CHECKED" in r for r in formal_trust.kernel_check_reasons(kr.trust_check(failed, H), H))


# --- the registry (ADR-083) -------------------------------------------------------------------------------------


def test_registry_refuses_kernel_rungs_without_a_verified_record(tmp_path):
    reg = cr.Registry(tmp_path / "registry.json")
    for rung in ("KERNEL_CHECKED", "INDEPENDENTLY_REPRODUCED"):
        with pytest.raises(cr.RegistryError, match="kernel_evidence"):
            reg.register({"id": "T", "source": "s", "statement": "t", "rung": rung})
    fail = kr.ladder_evidence  # a FAIL record cannot even produce evidence
    with pytest.raises(kr.KernelRecordError):
        fail(_write(tmp_path, _log(code=1), name="failed"))


def test_registry_climbs_from_statement_audited_with_a_pass_record(tmp_path):
    reg = cr.Registry(tmp_path / "registry.json")
    reg.register({"id": "T", "source": "s", "statement": "t", "rung": "STATEMENT_PUBLIC"})
    good = _write(tmp_path, _log())
    with pytest.raises(cr.RegistryError, match="climbed from STATEMENT_AUDITED"):
        reg.record_kernel_check("T", str(good))
    reg.register({"id": "T", "source": "s", "statement": "t", "rung": "STATEMENT_AUDITED"})
    with pytest.raises(cr.RegistryError, match="never climbs"):
        reg.record_kernel_check("T", str(_write(tmp_path, _log(code=1), name="failed")))
    entry = reg.record_kernel_check("T", str(good))
    assert entry.rung == "KERNEL_CHECKED" and entry.kernel_evidence["kernel_record"]["result"] == kr.PASS
    reloaded = cr.Registry(tmp_path / "registry.json")
    assert reloaded.get("T").rung == "KERNEL_CHECKED"
    # A new version keeps its rung only while the record still matches its log.
    (tmp_path / "demo.log").write_text("edited")
    with pytest.raises(cr.RegistryError, match="does not hash"):
        reg.register({**json.loads(json.dumps(reloaded.entries["T"][-1])), "version": None})


def test_api_kernel_check_endpoint_refuses_paths_outside_records(api_client):
    api_client.post("/api/registry/entries", json={"id": "kc", "source": "s", "statement": "t"})
    r = api_client.post("/api/registry/entries/kc/kernel-check", json={"record": "../../pyproject.toml"})
    assert r.status_code == 422
    r = api_client.post(
        "/api/registry/entries", json={"id": "kc2", "source": "s", "statement": "t", "rung": "KERNEL_CHECKED"}
    )
    assert r.status_code == 422


# --- committed records ------------------------------------------------------------------------------------------


def test_every_committed_record_matches_its_log():
    """Records under records/kernel/ were written by the workflow; an edited record or log fails here."""
    for item in kr.load_dir(kr.RECORDS_DIR) if kr.RECORDS_DIR.is_dir() else []:
        record = item["record"]
        assert record["result"] in kr.RESULTS
        if record["result"] == kr.PASS:
            assert kr.record_reasons(record) == []


def test_comparator_axioms_count_only_after_the_runners_probe():
    """A solution's build can print lines that look like `#print axioms` output; only the runner's probe counts."""
    forged = "'Demo.main' depends on axioms: [propext]\n" + kr.COMPARATOR_OK + "\n"
    assert kr.evaluate("comparator", _log(forged), ["Demo.main"])[0] == kr.FAIL
    probe = f"{kr.AXIOMS_PROBE}Demo.lean\n'Demo.main' depends on axioms: [propext, sorryAx]\n"
    result, reasons, axioms = kr.evaluate("comparator", _log(forged + probe), ["Demo.main"])
    assert result == kr.FAIL and axioms["Demo.main"] == ["propext", "sorryAx"]
    clean = f"{kr.AXIOMS_PROBE}Demo.lean\n" + STANDARD
    assert kr.evaluate("comparator", _log(forged + clean), ["Demo.main"])[0] == kr.PASS
