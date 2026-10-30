"""Tests for the bounded-region proof of the Mahler segment inequality (4) (mahler_segment_box.py, ADR-076)."""

import json
import math
from pathlib import Path

import numpy as np

from python.discovery import mahler_obligations as mo
from python.discovery import mahler_segment_box as sb

PROOF = Path(__file__).resolve().parent.parent / "examples" / "mahler-obligations" / "segment_box_proof.json"


def test_cell_enclosures_contain_the_profiles():
    for k in (3, 700, -900, 2100):
        e = sb.cell_enclosure(k)
        t = abs(k + 0.5) / sb.CELLS_PER_UNIT
        r = mo.evaluate(3.6 * math.sinh(t))
        vals = {"K": r["d"] - 2 * r["g"], "C": -r["d"] + 6.5 * r["g2"], "q": r["q"]}
        for name, v in vals.items():
            lo, hi = e[name]
            assert lo <= v <= hi and hi - lo < 2e-3, (k, name, lo, v, hi)


def test_a_coarse_middle_width_pair_is_certified_and_a_wrong_budget_is_not():
    n = 40
    k0, k1 = 38, 84  # l in [.95, .975], y in [2.075, 2.1]
    cells = {k: sb.cell_enclosure(k, n) for k in range(k0, k1)}
    tab = sb.cell_table(cells, k0, k1, n)
    hc, sc = sb._circle_tables(k1 - k0 + 2, 2 * k1 + 4, n)
    m, ratio = sb.pair_margins(tab, hc, sc, np.array([k0]), np.array([k1 - 1]))
    assert m[0] > 0 and ratio[0] < 1
    # a wrong extra cost of .05 on the left side would not be certified
    assert m[0] < 0.05


def test_region_pairs_cover_the_region():
    n = 20
    pairs = {(li, int(j)) for li, js in sb.region_pairs(n) for j in js}
    for l_, y_ in ((-1.4, 1.5), (0.0, 0.32), (1.39, 3.59), (-0.1, 0.25), (0.5, 3.6)):
        if y_ - l_ < 0.32 or l_ + y_ < 0:
            continue
        li, yj = int(np.floor(l_ * n)), min(int(np.floor(y_ * n)), int(round(sb.T_HI * n)) - 1)
        assert (li, yj) in pairs, (l_, y_)


def test_committed_proof():
    report = json.loads(PROOF.read_text(encoding="utf-8"))
    assert report["verified"] and not report["uncertified"]
    assert report["levels"][0]["pairs"] > 10_000_000 and 0 < report["max_ratio"] < 1 and report["min_margin"] > 0
