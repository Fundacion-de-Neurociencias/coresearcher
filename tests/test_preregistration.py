"""Tests for frozen checklists (python/discovery/preregistration.py) and the trust ladder (trust_ladder.py)."""

import copy
import json
from pathlib import Path

import pytest

from python.discovery import preregistration as pr
from python.discovery.formal_hypothesis import FormalHypothesisError
from python.discovery.trust_ladder import ClaimRecord, LadderError, Rung

ROOT = Path(__file__).resolve().parent.parent
YM = ROOT / "examples" / "yang-mills-preregistration" / "ym4_existence_checklist.v1.json"
O3 = ROOT / "examples" / "o3-continuum-rehearsal" / "o3_continuum_claim.v1.json"

YM_SHA256 = "2f899469928cf85a9c34ab19dd1dc73be45624a60b54253e727f61903bf3b353"


@pytest.fixture(scope="module")
def ym():
    return pr.load(YM)


# ---------------------------------------------------------------------------
# Freezing
# ---------------------------------------------------------------------------


def test_ym_checklist_matches_its_lock_and_the_published_hash(ym):
    assert ym.sha256 == YM_SHA256  # Also quoted in ADR-081 and the case doc; changing it means a new version.
    assert ym.lock["sha256"] == YM_SHA256
    assert ym.lock["frozen_on"] == ym.data["frozen_on"] == "2026-10-30"
    assert ym.version == "1.0.0"


def test_o3_checklist_matches_its_lock():
    c = pr.load(O3)
    assert c.lock["sha256"] == c.sha256


def test_any_edit_is_refused(tmp_path):
    data = json.loads(YM.read_text(encoding="utf-8"))
    data["obligations"][0]["formal_clause"] = "gauge_group != 'none'"  # A quiet weakening.
    spec = tmp_path / "ym.json"
    spec.write_text(json.dumps(data), encoding="utf-8")
    with pytest.raises(pr.FrozenSpecMismatch):
        pr.load(spec, lock_path=YM.with_suffix(".lock.json"))


def test_hash_ignores_formatting_but_not_content():
    data = json.loads(YM.read_text(encoding="utf-8"))
    reformatted = json.loads(json.dumps(data, indent=7))
    assert pr.spec_sha256(reformatted) == YM_SHA256
    changed = copy.deepcopy(data)
    changed["witnesses"].pop()
    assert pr.spec_sha256(changed) != YM_SHA256


def test_every_obligation_cites_a_known_source_and_the_jw_text_is_pinned(ym):
    refs = ym.data["references"]
    assert refs["JW"]["sha256"] and refs["JW"]["read"]
    assert refs["Committee26"]["sha256"] and refs["Committee26"]["read"]
    assert refs["Douglas26"]["read"] is False  # Cited as the committee's pointer only.
    for o in ym.obligations:
        assert o.sources and all(s["ref"] in refs for s in o.sources)


def test_mass_gap_and_confinement_are_outside_the_claim(ym):
    out = {o.id for o in ym.obligations if o.category == "out_of_claim"}
    assert out == {"OUT-MASS-GAP", "OUT-CONFINEMENT"}
    assert not out & ({o.id for o in ym.in_claim("YM")} | {o.id for o in ym.in_claim("QCD")})


def test_os_axioms_are_separate_obligations(ym):
    ids = {o.id for o in ym.in_claim("YM")}
    assert {"YM-OS-REGULARITY", "YM-OS-EUCLIDEAN", "YM-OS-RP", "YM-OS-SYMMETRY", "YM-OS-CLUSTER"} <= ids
    assert {"QCD-FERMIONS", "QCD-GROUP-SU3"} <= {o.id for o in ym.in_claim("QCD")} - ids


def test_validate_rejects_unknown_reference_and_category():
    data = json.loads(YM.read_text(encoding="utf-8"))
    bad = copy.deepcopy(data)
    bad["obligations"][0]["sources"] = [{"ref": "OpenAI2026", "locator": "their definition"}]
    with pytest.raises(FormalHypothesisError):
        pr.validate(bad)
    bad = copy.deepcopy(data)
    bad["obligations"][0]["category"] = "nice_to_have"
    with pytest.raises(FormalHypothesisError):
        pr.validate(bad)
    bad = copy.deepcopy(data)
    bad["obligations"][0]["formal_clause"] = "gauge_group == 'SU3' and undefined_feature"
    with pytest.raises(FormalHypothesisError):
        pr.validate(bad)


# ---------------------------------------------------------------------------
# Deciding
# ---------------------------------------------------------------------------


def test_decide_over_finite_and_continuous_features(ym):
    assert pr.decide(ym, ["dim == 4"], "dim == 4") == "ENTAILED"
    assert pr.decide(ym, ["dim == 2"], "dim == 4") == "REFUTED"
    assert pr.decide(ym, ["dim == 4"], "gauge_group == 'SU3'") == "OPEN"
    # Continuous features go to z3.
    assert pr.decide(ym, ["spacing > 0"], "spacing == 0 and continuum_limit == 'lattice_independent'") == "REFUTED"
    assert pr.decide(ym, ["mass_gap == 0"], "mass_gap > 0") == "REFUTED"
    assert pr.decide(ym, ["spacing == 0"], "spacing == 0 and continuum_limit == 'lattice_independent'") == "OPEN"


def test_contradictory_facts_are_rejected_not_read_as_entailing_everything(ym):
    with pytest.raises(FormalHypothesisError):
        pr.decide(ym, ["dim == 4", "dim == 2"], "os_cluster")
    with pytest.raises(FormalHypothesisError):
        pr.decide(ym, ["spacing > 0", "spacing < 0"], "dim == 4")


def test_coverage_of_a_hypothetical_torus_statement(ym):
    transcription = {
        "facts": ["dim == 4", "volume == 'torus'", "gauge_group == 'SU3'", "connected_4pt == 'nonzero'"],
        "quotes": {"YM-SPACETIME-INFINITE": "def T4 := UnitAddTorus (Fin 4)"},
    }
    rows = {r.obligation: r for r in pr.coverage(ym, transcription, claim="YM")}
    assert rows["YM-SPACETIME-DIM4"].coverage == "COVERED"
    assert rows["YM-SPACETIME-INFINITE"].coverage == "OBJECT_DIFFERS"
    assert rows["YM-SPACETIME-INFINITE"].formal_text.startswith("def T4")
    assert rows["YM-GROUP-NONABELIAN"].coverage == "COVERED"
    assert rows["YM-GROUP-COVERAGE"].coverage == "OBJECT_DIFFERS"  # SU(3) only: partial, not every G.
    assert rows["YM-OS-RP"].coverage == "NOT_ADDRESSED"
    assert rows["OUT-MASS-GAP"].coverage == "NOT_ADDRESSED"
    assert "QCD-FERMIONS" not in rows


# ---------------------------------------------------------------------------
# Trust ladder
# ---------------------------------------------------------------------------

CLAIMED = {"announcement": "https://example.org/a.pdf", "announcement_sha256": "a" * 64}


def _record() -> ClaimRecord:
    return ClaimRecord("c", "a claim", "Claimant").start("2026-10-30", "announced", CLAIMED)


def test_ladder_climbs_one_rung_at_a_time_with_evidence():
    record = _record()
    assert record.rung is Rung.CLAIMED
    assert record.formal_status == "NOT_KERNEL_CHECKED"
    assert record.mandatory_relays[0]["code"] == "LEAN_NOT_KERNEL_CHECKED"
    with pytest.raises(LadderError):
        record.climb(Rung.KERNEL_CHECKED, "2026-11-01", "skip", {})
    with pytest.raises(LadderError):
        record.climb(Rung.STATEMENT_PUBLIC, "2026-11-01", "no hash", {"statement_location": "x"})
    record.climb(
        Rung.STATEMENT_PUBLIC, "2026-11-01", "released", {"statement_location": "x", "statement_sha256": "b" * 64}
    )
    record.climb(
        Rung.STATEMENT_AUDITED,
        "2026-11-02",
        "audited",
        {
            "checklist": "ym4-existence v1.0.0",
            "checklist_sha256": YM_SHA256,
            "audit_report": "r.json",
            "audit_outcome": "VACUOUS_RELATIVE_TO_INTENT",
        },
    )
    record.climb(
        Rung.KERNEL_CHECKED,
        "2026-11-03",
        "kernel",
        {"toolchain": "lean4 v4.x", "axioms": ["propext"], "kernel_log_sha256": "c" * 64, "checked_by": "CoResearcher"},
    )
    assert record.formal_status == "DECIDED" and record.mandatory_relays == []
    with pytest.raises(LadderError):
        record.climb(
            Rung.INDEPENDENTLY_REPRODUCED,
            "2026-11-04",
            "self",
            {"reproduced_by": "Claimant", "method": "m", "record_sha256": "d" * 64},
        )
    record.climb(
        Rung.INDEPENDENTLY_REPRODUCED,
        "2026-11-04",
        "other",
        {"reproduced_by": "Lab B", "method": "m", "record_sha256": "d" * 64},
    )
    assert record.to_dict()["next_rung"] is None


def test_ladder_descends_with_a_reason_and_replays_from_json():
    record = _record()
    record.climb(
        Rung.STATEMENT_PUBLIC, "2026-11-01", "released", {"statement_location": "x", "statement_sha256": "b" * 64}
    )
    with pytest.raises(LadderError):
        record.descend(Rung.CLAIMED, "2026-11-02", " ")
    record.descend(Rung.CLAIMED, "2026-11-02", "statement withdrawn")
    replay = ClaimRecord.from_dict(json.loads(json.dumps(record.to_dict())))
    assert replay.to_dict() == record.to_dict()
    assert [s.rung for s in replay.history] == ["CLAIMED", "STATEMENT_PUBLIC", "CLAIMED"]


def test_a_record_cannot_start_without_the_announcement_hash():
    with pytest.raises(LadderError):
        ClaimRecord("c", "a claim", "Claimant").start("2026-10-30", "announced", {"announcement": "x"})
