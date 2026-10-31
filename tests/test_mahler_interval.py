"""Tests for the interval-arithmetic proof of the Mahler scalar inequalities (python/discovery/mahler_interval.py)."""

import json
from pathlib import Path

import mpmath as mp

from python.discovery import mahler_interval as mi
from python.discovery.obligation_ledger import PROOF_STATUSES, Status

PROOF = Path(__file__).resolve().parent.parent / "examples" / "mahler-obligations" / "interval_proof.json"


def test_symbolic_foundations_hold():
    checks = dict(mi.symbolic_checks())
    assert all(checks.values()), checks
    assert {"even: d", "even: g", "even: v", "stable form: d", "stable form: g", "stable form: v"} <= set(checks)


def test_point_enclosures_contain_the_true_values():
    for xx in (0.0, 0.5, 3.0, 8.0):
        P, Q, PH = mi.point(xx)
        with mp.workdps(80):
            true_p, true_phi = mp.ncdf(xx), mp.npdf(xx)
            lo = {n: (mp.mpf(e.a), mp.mpf(e.b)) for n, e in (("p", P), ("q", Q), ("phi", PH))}
            assert lo["p"][0] <= true_p <= lo["p"][1]
            assert lo["q"][0] <= 1 - true_p <= lo["q"][1]
            assert lo["phi"][0] <= true_phi <= lo["phi"][1]
        assert float(mp.mpf(Q.b - Q.a)) < 1e-20


def test_h_series_encloses_its_closed_form():
    for y in ("0.01", "0.3", "0.5"):
        y53 = mp.mpf(y)  # the exact binary number passed to the series
        enc = mi.hseries(0, y53)
        with mp.workdps(60):
            yy = mp.mpf(y53)
            closed = (-mp.log(1 - yy) - yy) / yy**2
            assert mp.mpf(enc.a) <= closed <= mp.mpf(enc.b)


def test_first_bullet_is_certified_at_the_tightest_point():
    st = mi.verify_1d(0.0, 1 / 128, 1)
    assert st["verified"] and st["certified_boxes"] >= 1
    assert 0 < st["min_lower_bound"]["C <= -.341"] < 4e-4


def test_negative_control_a_tightened_constant_is_not_certified():
    st = mi.verify_1d(0.0, 1 / 128, 1, max_depth=2, thresholds={"C": (-342, 1000)})
    assert not st["verified"]


def test_two_variable_inequalities_certified_near_the_origin():
    st = mi.verify_2d(0.125, 1)
    assert st["verified"] and st["certified_pairs"] >= 2


def test_interval_status_is_a_proof_status():
    assert Status.DISCHARGED_INTERVAL in PROOF_STATUSES
    assert Status.CHECKED_NUMERIC not in PROOF_STATUSES


def test_committed_interval_proof():
    report = json.loads(PROOF.read_text(encoding="utf-8"))
    assert all(c["holds"] for c in report["symbolic"])
    first, second = report["first_bullet"], report["two_variable"]
    assert first["verified"] and not first["uncertified"] and first["window"] == [-8.0, 8.0]
    assert second["verified"] and not second["uncertified"] and second["window"] == [-3.0, 3.0]
    assert all(v > 0 for v in first["min_lower_bound"].values())
    assert all(v > 0 for v in second["min_lower_bound"])
