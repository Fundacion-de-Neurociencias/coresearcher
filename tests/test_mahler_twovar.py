"""Tests for the proof of the two-variable Mahler inequalities (3) outside [-3, 3]^2 (mahler_twovar.py)."""

import json
from fractions import Fraction
from pathlib import Path

import numpy as np

from python.discovery import mahler_obligations as mo
from python.discovery import mahler_twovar as tv

PROOF = Path(__file__).resolve().parent.parent / "examples" / "mahler-obligations" / "twovar_proof.json"


def test_phase_reduction_identities_hold():
    assert all(tv.check_reduction().values())


def test_rho_encloses_the_norm_of_S_pi():
    for xx in (0.5, 3.0, 7.0):
        ref = mo.evaluate(xx)
        norm = float(np.hypot(ref["Sp1"], ref["Sp2"]))
        lo, hi = tv._rho_box(xx, xx)
        assert lo <= norm <= hi
    lo, hi = tv._rho_box(6.0, np.inf)  # unbounded box through t = 1/x
    assert 0 < lo <= hi < 1.2


def test_tail_box_encloses_the_profiles():
    t = Fraction(1, 9)
    enc = tv._tail_box(t, t)
    ref = mo.evaluate(9.0)
    for key in ("q", "Sq", "v2"):
        assert enc[key][0] - 1e-9 <= ref[key] <= enc[key][1] + 1e-9, key


def test_pairs_with_an_unbounded_box_are_certified():
    boxes = [tv.bounded_box((0.0, 1 / 64)), {"lo": 96.0, "hi": np.inf, **tv._tail_box(Fraction(0), Fraction(1, 96))}]
    boxes[1]["rho"] = tv._rho_box(96.0, np.inf)
    res = tv.verify_outside(boxes, csplit=16)
    assert res["pairs_checked"] == 3 and res["verified"]


def test_committed_twovar_proof():
    report = json.loads(PROOF.read_text(encoding="utf-8"))
    assert all(r["holds"] for r in report["reduction"])
    res = report["result"]
    assert res["verified"] and not res["uncertified"] and res["window"] == 3.0
    assert all(v > 0 for v in res["min_lower_bound"])
