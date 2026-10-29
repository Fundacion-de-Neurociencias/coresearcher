"""Tests for the tail proof (x >= 8) of the Mahler first-bullet scalar inequalities (python/discovery/mahler_tail.py)."""

import json
from fractions import Fraction
from pathlib import Path

import mpmath as mp

from python.discovery import mahler_obligations as mo
from python.discovery import mahler_tail as mt

PROOF = Path(__file__).resolve().parent.parent / "examples" / "mahler-obligations" / "tail_proof.json"


def test_laurent_models_have_no_negative_powers():
    # negative powers of t cancel exactly, so the models extend to t = 0 (x = infinity)
    for name, (A, B) in mt.base_models().items():
        assert A.min_exponent() >= 0, name
        assert B.min_exponent() >= 1, name  # log t always comes with a positive power of t
        assert A.m >= 0 and B.m >= 1


def test_laurent_model_arithmetic_is_exact_on_cancellation():
    x, t = mt.LTM({-1: Fraction(1)}), mt.LTM({1: Fraction(1)})
    z = x * t - 1
    assert z.min_exponent() == mt.NTRUNC and z.rem is None


def test_mills_series_brackets_the_true_ratio():
    Psi = mt.inputs()["Psi"]
    for xx in (8, 12, 40):
        enc = Psi.evaluate(Fraction(1, xx), Fraction(1, xx))
        with mp.workdps(50):
            true = xx * (mp.erfc(xx / mp.sqrt(2)) / 2) / mp.npdf(xx)  # 1 - Phi without cancellation
            assert mp.mpf(enc.a) <= true <= mp.mpf(enc.b)


def test_models_agree_with_independent_numeric_profiles():
    models = mt.base_models()
    for xx in (8, 20):
        ref = mo.evaluate(float(xx))
        for name, key in (("d", "d"), ("g", "g"), ("g2", "g2")):
            enc = mt.evaluate_pair(models[name], Fraction(1, xx), Fraction(1, xx))
            assert float(mp.mpf(enc.a)) - 1e-9 <= ref[key] <= float(mp.mpf(enc.b)) + 1e-9, (xx, name)


def test_tail_is_certified_and_a_negative_control_is_not():
    assert mt.verify_tail(16)["verified"]
    assert not mt.verify_tail(16, max_depth=2, thresholds={"C": (-1, 2)})["verified"]


def test_committed_tail_proof():
    report = json.loads(PROOF.read_text(encoding="utf-8"))
    assert report["x_from"] == 8 and report["result"]["verified"]
    assert not report["result"]["uncertified"]
    assert all(v > 0 for v in report["result"]["min_lower_bound"].values())
