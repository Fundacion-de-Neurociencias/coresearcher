"""Tests for the interval engine and the short-width and tail proof of the Mahler segment inequality (4) (ADR-076)."""

import json
import math
from fractions import Fraction
from pathlib import Path

import mpmath as mp
import numpy as np
import pytest

from python.discovery import interval_engine as ie
from python.discovery import mahler_segment_tails as st

EX = Path(__file__).resolve().parent.parent / "examples" / "mahler-obligations"


def test_taylor_models_enclose_the_functions():
    H, N = Fraction(1), 32
    w = Fraction(23, 5)
    C, Sc, Sh = ie.tm_cos(w, H, N), ie.tm_sinc(w, H, N), ie.tm_shc(H, N)
    iSh = ie.tm_reciprocal_one_plus(Sh - 1, 17)
    f = (1 - Sc * Sc * iSh * iSh).shift(2)
    for h in (0.003, 0.2, 0.7, 1.0):
        hh = mp.mpf(h)
        assert mp.mpf(C.evaluate(h, h).a) <= mp.cos(w * hh) <= mp.mpf(C.evaluate(h, h).b)
        ref = (1 - (mp.sin(float(w) * hh) / (float(w) * hh) / (mp.sinh(hh) / hh)) ** 2) / hh**2
        v = f.evaluate(h, h)
        assert v.a <= ref <= v.b and v.b - v.a < 1e-6
    # the limit at h = 0 is exact: (w^2 + 1)/3
    v0 = f.evaluate(0, 0)
    assert v0.a <= (float(w) ** 2 + 1) / 3 <= v0.b
    with pytest.raises(ValueError):
        (1 - C).shift(3)  # 1 - cos(wh) = O(h^2), not O(h^3)


def test_knapsack_is_the_exact_lp_range():
    lo, hi = ie.knapsack_average(
        np.array([0.1, 0.0, 0.2]), np.array([0.5, 1.0, 0.3]), np.array([1.0, 2.0, 3.0]), np.array([1.0, 2.0, 3.0])
    )
    # max: 0.1 + w2 + w3 with w3 = .3, w1 = .1 -> .1*1 + .6*2 + .3*3 = 2.2; min: w1 = .5, w3 = .2 -> .5 + .3*2 + .6
    assert abs(hi - 2.2) < 1e-9 and abs(lo - 1.7) < 1e-9


def test_lemmas():
    assert all(st.lemma_checks().values())


@pytest.fixture(scope="module")
def zones():
    data = json.loads((EX / "segment_tails_zones.json").read_text(encoding="utf-8"))
    return st.Zones([{k: tuple(v) for k, v in c.items()} for c in data["cells"]])


def test_sample_boxes_certify_including_infinite_ones(zones):
    for box in [(0.0, 0.05, 0.0, 0.04), (16.0, math.inf, 0.0, 0.04), (16.0, math.inf, 8.0, math.inf)]:
        lb = st.evaluate_box(zones, *box)
        assert lb is not None and lb > 0, box


def test_negative_control_without_the_proved_derivative_bound(zones):
    """Doubling the range of C-dot near the worst short-width location breaks the certificate."""
    Z = st.Zones.__new__(st.Zones)
    Z.__dict__.update({k: (dict(v) if isinstance(v, dict) else v) for k, v in zones.__dict__.items()})
    Z.lo["Cd"], Z.hi["Cd"] = zones.lo["Cd"] * 2, zones.hi["Cd"] * 2
    box = (0.4, 0.41, 0.15, 0.16)
    assert st.evaluate_box(zones, *box) > 0
    lb = st.evaluate_box(Z, *box)
    assert lb is None or lb <= 0


def test_certified_bounds_never_exceed_the_true_margin(zones):
    """Soundness audit against an independent Gauss-Legendre value of (4), short widths and tails."""
    boxes = st.initial_boxes()
    for m, h in ((0.43, 0.15), (1.9, 0.05), (2.2, 3.1), (0.3, 6.5)):
        box = next(b for b in boxes if b[0] <= m <= b[1] and b[2] <= h <= b[3])
        lb = st.evaluate_box(zones, *box)
        true = st.reference_margin(m, h)
        certified = lb * h * h if box[3] <= 1 else lb
        assert 0 < certified <= true, (m, h, certified, true)


def test_committed_proof():
    report = json.loads((EX / "segment_tails_proof.json").read_text(encoding="utf-8"))
    assert report["verified"] and not report["failed"] and all(report["lemmas"].values())
    assert report["certified_boxes"] > 1000 and report["min_lower_bound"] > 0
