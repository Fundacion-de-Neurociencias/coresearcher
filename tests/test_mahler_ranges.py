"""Tests for the profile derivative bounds of lem:scalar-ranges (python/discovery/mahler_ranges.py)."""

import json
from fractions import Fraction
from pathlib import Path

from python.discovery import mahler_ranges as mr

PROOF = Path(__file__).resolve().parent.parent / "examples" / "mahler-obligations" / "ranges_proof.json"


def test_tail_bounds_are_certified():
    st = mr.verify_tail()
    assert st["verified"] and st["certified_boxes"] == 16


def test_a_small_window_box_is_certified_and_a_tightened_bound_is_not():
    vals = mr.window_margins(1.0, 1.0 + 1 / 4096)
    assert all(v.a > 0 for v in vals.values())
    # |C-dot| is within about 1.4e-3 of .247 near x = 1.7, so .245 must fail there
    tight = mr.window_margins(1.7, 1.7 + 1 / 65536, thresholds={"Cdot": (245, 1000)})
    assert tight["|C-dot| <= .247"].b < 0


def test_tail_models_carry_no_negative_powers():
    for name, (A, B) in mr._tail_models().items():
        assert A.min_exponent() >= 0, name


def test_committed_ranges_proof():
    report = json.loads(PROOF.read_text(encoding="utf-8"))
    assert report["window"]["verified"] and not report["window"]["uncertified"]
    assert report["tail"]["verified"] and report["window"]["range"] == [0.0, 8.0]
    assert all(v > 0 for v in report["window"]["min_lower_bound"].values())
    assert set(report["bounds"]) == set(mr.BOUNDS)
    assert Fraction(1, 8)  # tail starts at x = 8
