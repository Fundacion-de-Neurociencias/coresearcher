"""Tests for the obligation ledger (ADR-DISCOVERY-076) and its Mahler scalar-input pilot."""

import json
from pathlib import Path

import pytest

from python.discovery import mahler_obligations as mo
from python.discovery.obligation_ledger import Claim, Discharge, Obligation, Status

LEDGER = Path(__file__).resolve().parent.parent / "examples" / "mahler-obligations" / "ledger.json"


def _ob(*statuses, by="CoResearcher"):
    ob = Obligation("o", "s", "src", "identity")
    for s in statuses:
        ob.discharges.append(Discharge(s, "m", "scope", by))
    return ob


def test_weakest_link_and_refutation_dominate():
    claim = Claim("c", "s", "src", [_ob(Status.DISCHARGED_SYMBOLIC), _ob(Status.CHECKED_NUMERIC)])
    assert claim.status == Status.CHECKED_NUMERIC and not claim.is_proved
    claim.obligations.append(_ob(Status.DISCHARGED_FORMAL, Status.REFUTED))
    assert claim.status == Status.REFUTED
    assert Claim("c", "s", "src", [_ob()]).status == Status.OPEN


def test_numeric_and_author_certificates_never_count_as_proofs():
    claim = Claim("c", "s", "src", [_ob(Status.CERTIFIED_BY_AUTHOR, by="author"), _ob(Status.CHECKED_NUMERIC)])
    assert not claim.is_proved
    assert not claim.obligations[0].independent and claim.obligations[1].independent
    with pytest.raises(ValueError):
        Discharge(Status.CHECKED_NUMERIC, "m", " ", "CoResearcher")


def test_profile_identities_are_symbolically_true():
    assert all(ok for _, ok in mo.check_profile_identities())


@pytest.fixture(scope="module")
def table():
    return mo.profile_table(0.25, 6.0)


def test_pointwise_inequalities_hold_on_a_coarse_grid(table):
    margins = mo.pointwise_margins(table)
    assert len(margins) == 7 and all(m["min"] > 0 for m in margins.values()), margins
    # The tightest bound in the proposition: C <= -.341 is attained within 4e-4 at x = 0.
    assert margins["C <= -.341"]["min"] < 4e-4 and margins["C <= -.341"]["at"] == 0.0


def test_negative_controls_tighter_constants_are_refuted(table):
    tight = mo.pointwise_margins(table, {"C": -0.342, "v": 0.317})
    assert tight["C <= -.341"]["min"] < 0 and tight["|v' - x| <= .319"]["min"] < 0


def test_two_variable_and_segment_inequalities_on_a_coarse_grid(table):
    assert all(m["min"] > 0 for m in mo.two_variable_margins(table).values())
    seg = mo.segment_ratio(table, step=2)
    assert seg["segments"] > 100 and seg["max_left_over_right"] < 1


def test_committed_ledger():
    report = json.loads(LEDGER.read_text(encoding="utf-8"))
    claim = report["claim"]
    assert report["source"]["commit"] == mo.SOURCE["commit"]
    assert claim["status"] == Status.CHECKED_NUMERIC.value and claim["is_proved"] is False
    by_id = {o["id"]: o for o in claim["obligations"]}
    assert by_id["identities"]["status"] == Status.DISCHARGED_SYMBOLIC.value
    # 1 identity obligation; 7 + 2 inequalities each split into a proved window and the rest; 1 segment inequality
    assert len(claim["obligations"]) == 20
    assert all(o["status"] != Status.REFUTED.value for o in claim["obligations"])
    windows = [o for o in claim["obligations"] if " on " in o["id"]]
    assert len(windows) == 9 and all(o["status"] == Status.DISCHARGED_INTERVAL.value for o in windows)
    rest = [o for o in claim["obligations"] if o["kind"] != "identity" and " on " not in o["id"]]
    assert all(o["status"] == Status.CHECKED_NUMERIC.value for o in rest)
