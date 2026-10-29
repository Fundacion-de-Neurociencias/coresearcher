"""Tests for the algebraic reduction of the Mahler segment inequality (python/discovery/mahler_segment.py)."""

from fractions import Fraction

from python.discovery import mahler_segment as ms


def test_every_reduction_step_holds():
    checks = ms.segment_checks()
    assert all(checks.values()), checks
    assert len(checks) == 10


def test_short_width_budget_matches_the_paper_exactly():
    sw = ms.short_width_budget()
    assert isinstance(sw["value"], Fraction)
    assert Fraction(5551, 10000) < sw["value"] < Fraction(5552, 10000)


def test_negative_control_a_wrong_budget_constant_is_caught():
    # with the derivative bound on C' raised from .247 to .5 the short-width budget no longer covers the cost .54
    rr, ww, lam, Hh = Fraction(22, 100), Fraction(46, 10), Fraction(65, 100), Fraction(16, 100)
    G = rr**2 * ww**2
    sq2 = (
        3
        / G
        * (
            Fraction(1, 2)
            + Fraction(2, 3) * (G + Fraction(193, 1000) * Fraction(53, 100) * Fraction(1012, 1000)) * Hh**2
        )
        ** 2
    )
    sq2_paper = (
        3
        / G
        * (
            Fraction(247, 1000)
            + Fraction(2, 3) * (G + Fraction(193, 1000) * Fraction(53, 100) * Fraction(1012, 1000)) * Hh**2
        )
        ** 2
    )
    assert ms.short_width_budget()["value"] - (sq2 - sq2_paper) / (4 * lam) < Fraction(54, 100)
