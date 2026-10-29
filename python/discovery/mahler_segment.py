"""
python/discovery/mahler_segment.py - Independent check of the algebraic reduction behind the segment inequality (4)
of the general Mahler paper (prop:segment-estimate, Appendix 8 of build/sections/08-segments.tex), ADR-DISCOVERY-076.

The authors reduce (4) to scalar "budget" inequalities in four width regimes. This module checks, by SymPy and exact
rational arithmetic, every algebraic step of that reduction that does not need bounds on the profiles:

- the closed-form mean of the circle part over a segment in t = asinh(x/s) (coefficients A_h, B_h);
- A_h^2 + B_h^2 = (1 + sin^2(wh)/sinh^2 h)/(1 + w^2), hence f0* = r^2 (1 - A_h^2 - B_h^2) > 0 and the circle variance
  is at least f0*;
- the endpoint distances avg|pi - pi_(+/-)|^2 = p_a +/- p_d;
- the rewriting of (4) as the budget (s0), including the variance decomposition;
- the chord-kernel identity (trapezoid error) and the two algebraic identities used for its weight bounds;
- the exact value of the short-width budget, given the profile bounds the authors state.

It does not check the profile bounds themselves (|q'| <= .193, |C'| <= .247, ... in t), the tail, middle and large
regimes, or the Bernstein certificates. Those remain separate obligations in the ledger.
"""

from __future__ import annotations

from fractions import Fraction
from typing import Dict

import sympy as sp

m, h, t, w, r, beta = sp.symbols("m h t w r beta", real=True)
I = sp.I  # noqa: E741  (imaginary unit)


def _A(hh, ww):
    return (sp.cos(ww * hh) + ww * sp.coth(hh) * sp.sin(ww * hh)) / (1 + ww**2)


def _B(hh, ww):
    return (sp.coth(hh) * sp.sin(ww * hh) - ww * sp.cos(ww * hh)) / (1 + ww**2)


def check_circle_mean() -> bool:
    """(1/(2 cosh m sinh h)) int_{m-h}^{m+h} e^{iwt} cosh t dt = e^{iwm} (A_h + i B_h tanh m)."""
    # antiderivative of e^{iwt} cosh t, written with exponentials
    Fa = (sp.exp((I * w + 1) * t) / (I * w + 1) + sp.exp((I * w - 1) * t) / (I * w - 1)) / 2
    assert sp.simplify(sp.diff(Fa, t) - sp.exp(I * w * t) * sp.cosh(t).rewrite(sp.exp)) == 0
    lhs = (Fa.subs(t, m + h) - Fa.subs(t, m - h)) / (2 * sp.cosh(m) * sp.sinh(h))
    rhs = sp.exp(I * w * m) * (_A(h, w) + I * _B(h, w) * sp.tanh(m))
    diff = sp.simplify((lhs - rhs).rewrite(sp.exp))
    return diff == 0


def check_AB_identity() -> bool:
    lhs = _A(h, w) ** 2 + _B(h, w) ** 2
    rhs = (1 + sp.sin(w * h) ** 2 / sp.sinh(h) ** 2) / (1 + w**2)
    return sp.simplify((lhs - rhs).rewrite(sp.exp)) == 0


def check_f0_positive() -> bool:
    """f0* = r^2 (w^2 - sin^2(wh)/sinh^2 h)/(1 + w^2) > 0 for h > 0: |sin(wh)| <= wh < w sinh h."""
    f0 = r**2 * (1 - _A(h, w) ** 2 - _B(h, w) ** 2)
    form = r**2 / (1 + w**2) * (w**2 - sp.sin(w * h) ** 2 / sp.sinh(h) ** 2)
    same = sp.simplify((f0 - form).rewrite(sp.exp)) == 0
    # the two elementary facts, as series signs: sinh h - h has positive Taylor coefficients; |sin y| <= |y|
    shift = sp.series(sp.sinh(h) - h, h, 0, 8).removeO()
    positive_coeffs = all(c > 0 for c in sp.Poly(shift, h).coeffs())
    return same and positive_coeffs


def check_endpoint_distances() -> bool:
    """avg|pi - pi_(+/-)|^2 = p_a +/- p_d with p_a = 2r^2(1 - A cos wh), p_d = -2r^2 B tanh m sin wh."""
    A, B = _A(h, w), _B(h, w)
    mean = r * sp.exp(I * w * m) * (A + I * B * sp.tanh(m))  # mean of pi as a complex number
    ok = True
    for sgn in (1, -1):
        end = r * sp.exp(I * w * (m + sgn * h))
        # avg|pi - e|^2 = avg|pi|^2 - 2 Re(conj(e) mean) + |e|^2 = 2 r^2 - 2 Re(conj(e) mean), since |pi| = r
        re_part = sp.re(sp.expand(sp.conjugate(end) * mean, complex=True))
        val = 2 * r**2 - 2 * re_part
        pa = 2 * r**2 * (1 - A * sp.cos(w * h))
        pd = -2 * r**2 * B * sp.tanh(m) * sp.sin(w * h)
        ok &= sp.simplify(val - (pa + sgn * pd)) == 0
    return ok


def check_s0_reduction() -> bool:
    """(4) <=> squares + e_K + Gamma + t_+(p_a + b_a) < (1 + t_+) V_u, and the squares sum to 2(X^2 + Y^2)."""
    ca, cd, pa, pd, ba, bd, Vu, eK, G, tp, lam = sp.symbols("c_a c_d p_a p_d b_a b_d V_u e_K Gamma t_p lambda")
    X, Yv = ca - pa - ba, cd - pd - bd
    lhs4 = eK + G + ((X + Yv) ** 2 + (X - Yv) ** 2) / (8 * lam) + tp * (pa + ba - Vu)
    s0 = eK + G + (X**2 + Yv**2) / (4 * lam) + tp * (pa + ba) - (1 + tp) * Vu
    return sp.simplify((lhs4 - Vu) - s0) == 0


def check_variance_decomposition() -> bool:
    """avg|u - e|^2 = V_u + |avg u - e|^2, componentwise (a finite mean as the model of the average)."""
    xs = sp.symbols("x0:4", real=True)
    e = sp.Symbol("e", real=True)
    n = len(xs)
    mean = sum(xs) / n
    lhs = sum((xi - e) ** 2 for xi in xs) / n
    var = sum(xi**2 for xi in xs) / n - mean**2
    return sp.simplify(lhs - (var + (mean - e) ** 2)) == 0


def check_chord_identities() -> Dict[str, bool]:
    """The trapezoid (Peano) identity on polynomials, and the two algebraic identities behind the bounds on W."""
    L, th = sp.symbols("L theta", positive=True)
    a = sp.Symbol("a", real=True)
    ok_trap = True
    for F in (a**2, a**3 - 2 * a, a**4 + a, a**5):
        x0 = sp.Symbol("x0", real=True)
        avg = sp.integrate(F, (a, x0, x0 + L)) / L
        trap = (F.subs(a, x0) + F.subs(a, x0 + L)) / 2
        kernel = -(L**2) * sp.integrate(th * (1 - th) * sp.diff(F, a, 2).subs(a, x0 + th * L), (th, 0, 1)) / 2
        ok_trap &= sp.simplify(avg - trap - kernel) == 0
    zeta = sp.cosh(h) - 1
    lhs = (sp.sinh(t) - sp.sinh(m) * sp.cosh(h)) ** 2 - sp.cosh(m) * (sp.cosh(m) - sp.cosh(t)) * sp.sinh(h) ** 2
    rhs = (sp.sinh(t) - sp.sinh(m)) ** 2 + 2 * (sp.cosh(m - t) - 1) * zeta + (sp.cosh(t) * sp.cosh(m) - 1) * zeta**2
    ok_w = sp.simplify((lhs - rhs).rewrite(sp.exp)) == 0
    tt = m + beta * h
    theta = (sp.sinh(tt) - sp.sinh(m - h)) / (2 * sp.cosh(m) * sp.sinh(h))
    up, um = (1 + beta) / 2, (1 - beta) / 2
    left = theta * (1 - theta) * sp.cosh(m) / sp.cosh(tt)
    right = (
        sp.sinh(up * h)
        * sp.sinh(um * h)
        / sp.sinh(h) ** 2
        * (sp.cosh(2 * m + beta * h) + sp.cosh(h))
        / (sp.cosh(2 * m + beta * h) + sp.cosh(beta * h))
    )
    ok_fact = sp.simplify((left - right).rewrite(sp.exp)) == 0
    return {"trapezoid kernel": ok_trap, "W <= 3S/2 identity": ok_w, "theta(1-theta) factorization": ok_fact}


def short_width_budget() -> Dict[str, object]:
    """Exact value of the authors' short-width lower bound (h <= .16), given their stated profile bounds."""
    Fr = Fraction
    rr, ww, lam, tp, Hh = Fr(22, 100), Fr(46, 10), Fr(65, 100), Fr(64, 1000), Fr(16, 100)
    G = rr**2 * ww**2
    P = 4 + Fr(15, 100) * Hh**2
    Q = Fr(193, 1000) ** 2 * P / G
    first = (1 + tp) * (1 - 2 * ww**4 * Hh**2 / (15 * (1 + ww**2))) / (1 + Hh**2 / 3) - tp * (P + Q)
    sq1 = G * Hh**2 / 3 * (P + Q + Fr(79, 100) * Fr(1012, 1000) / G) ** 2
    sq2 = 3 / G * (Fr(247, 1000) + Fr(2, 3) * (G + Fr(193, 1000) * Fr(53, 100) * Fr(1012, 1000)) * Hh**2) ** 2
    value = first - (sq1 + sq2) / (4 * lam)
    return {
        "value": value,
        "value_float": float(value),
        "exceeds_.55510": value > Fr(5551, 10000),
        "exceeds_cost_.54": value > Fr(54, 100),
    }


def segment_checks() -> Dict[str, bool]:
    out = {
        "circle mean (A_h, B_h)": check_circle_mean(),
        "A_h^2 + B_h^2 identity": check_AB_identity(),
        "f0* formula and positivity": check_f0_positive(),
        "endpoint distances p_a +/- p_d": check_endpoint_distances(),
        "(4) <=> budget (s0)": check_s0_reduction(),
        "variance decomposition": check_variance_decomposition(),
    }
    out.update({f"chord: {k}": v for k, v in check_chord_identities().items()})
    sw = short_width_budget()
    out["short-width budget > .54 (exact)"] = bool(sw["exceeds_cost_.54"])
    return out
