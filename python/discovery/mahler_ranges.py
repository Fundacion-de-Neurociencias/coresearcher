"""
python/discovery/mahler_ranges.py - Rigorous proof of the profile derivative bounds of lem:scalar-ranges that the
short-width regime of the Mahler segment inequality uses, ADR-DISCOVERY-076.

In the coordinate t = asinh(x/s), F-dot = sqrt(s^2 + x^2) F'(x) and n_F = (s^2 + x^2) F''(x). The bounds are
    |q-dot| <= .193,  |C-dot| <= .247,  |n_C| <= .79,  |n_q| <= .53,
    U_* = 1.507 max(0, -n_K) + (12 * .80 / m_*^2) [1.25 (K-dot + t_c C-dot)^2 + 5 t_r^2 C-dot^2] <= .54 r^2 w^2,
with K = d - 2g, C = -d + (a_R - 1) g'' and q = k - sqrt(b - r^2 - d). All are even in x, so x >= 0 suffices.

On 0 <= x <= 8 they are certified by the mean-value form with branch and bound (as in mahler_interval). On x >= 8
they are certified with the Laurent-Taylor models of mahler_tail in t = 1/x, where the factors x and x^2 are
multiplied inside the models so that the cancellations are exact.
"""

from __future__ import annotations

from fractions import Fraction
from functools import lru_cache
from typing import Any, Dict

import mpmath as mp
import sympy as sp

from python.discovery import mahler_interval as mi
from python.discovery import mahler_tail as mt

iv = mp.iv

BOUNDS = ["|q-dot| <= .193", "|C-dot| <= .247", "|n_C| <= .79", "|n_q| <= .53", "U_* <= .54 r^2 w^2"]
WINDOW = 8.0


@lru_cache(maxsize=None)
def _lambdas():
    d, g = mi.d_stable, mi.g_stable
    base = {
        "d": d,
        "d1": mi.D(d),
        "d2": mi.D(d, 2),
        "g1": mi.D(g),
        "g2": mi.D(g, 2),
        "g3": mi.D(g, 3),
        "g4": mi.D(g, 4),
    }
    F = {n: sp.lambdify(mi.SYMS, e, modules=mi.IVMODS) for n, e in base.items()}
    FD = {n: sp.lambdify(mi.SYMS, mi.D(e), modules=mi.IVMODS) for n, e in base.items()}
    return F, FD


def _abs_hi(v):
    return max(abs(v.a), abs(v.b))


def _margins(d, d1, d2, g1, g2, g3, g4, a_t, a_t2, thresholds=None):
    """Lower bounds of the five margins from the jets. a_t multiplies first derivatives, a_t2 second derivatives
    (sqrt(s^2 + x^2) and s^2 + x^2 in the window; in the tail the x factors are already inside the jets)."""
    th = {"qdot": (193, 1000), "Cdot": (247, 1000), "nC": (79, 100), "nq": (53, 100), "U": (54, 100)}
    th.update(thresholds or {})
    lim = {k: iv.mpf(n) / m for k, (n, m) in th.items()}
    b_, r_, aR = mi._c("b"), mi._c("r"), mi._c("aR")
    tc, tr, ms, w = mi._c("tc"), mi._c("tr"), mi._c("ms"), mi._c("w")
    ell2 = b_ - r_ * r_ - d
    ell = iv.sqrt(ell2)
    q1 = d1 / (2 * ell)
    q2 = d2 / (2 * ell) + d1 * d1 / (4 * ell2 * ell)
    C1 = -d1 + (aR - 1) * g3
    C2 = -d2 + (aR - 1) * g4
    K1 = d1 - 2 * g1
    K2 = d2 - 2 * g2
    qdot, Cdot, Kdot = a_t * q1, a_t * C1, a_t * K1
    nC, nq, nK = a_t2 * C2, a_t2 * q2, a_t2 * K2
    negnK = iv.mpf([max(0, -nK.b), max(0, -nK.a)])  # range of max(0, -n_K)
    U = iv.mpf(1507) / 1000 * negnK + (12 * iv.mpf(80) / 100 / (ms * ms)) * (
        iv.mpf(125) / 100 * (Kdot + tc * Cdot) ** 2 + 5 * tr * tr * Cdot * Cdot
    )
    vals = [
        lim["qdot"] - _abs_hi(qdot),
        lim["Cdot"] - _abs_hi(Cdot),
        lim["nC"] - _abs_hi(nC),
        lim["nq"] - _abs_hi(nq),
        lim["U"] * r_ * r_ * w * w - U.b,
    ]
    return dict(zip(BOUNDS, [iv.mpf(v) for v in vals]))


def window_margins(a: float, b: float, thresholds=None) -> Dict[str, Any]:
    F, FD = _lambdas()
    m = (a + b) / 2
    ip, ib = mi.inputs_point(m), mi.inputs_box(a, b)
    with mi.ivdps(30):
        half = iv.mpf([-(b - a) / 2, (b - a) / 2])
        v = {n: F[n](*ip) + FD[n](*ib) * half for n in F}
        X = iv.mpf([a, b])
        s = mi._c("s")
        a_t2 = s * s + X * X
        return _margins(v["d"], v["d1"], v["d2"], v["g1"], v["g2"], v["g3"], v["g4"], iv.sqrt(a_t2), a_t2, thresholds)


@lru_cache(maxsize=None)
def _tail_models():
    """Models of d, x d1, x^2 d2, x g1, x^2 g2, x g3, x^2 g4 (pairs (A, B): value A + log(t) B)."""
    bm = mt.base_models()
    x = mt.inputs()["x"]

    def times(pair, k):
        A, B = pair
        for _ in range(k):
            A, B = x * A, x * B
        return A, B

    return {
        "d": bm["d"],
        "xd1": times(bm["d1"], 1),
        "x2d2": times(bm["d2"], 2),
        "xg1": times(bm["g1"], 1),
        "x2g2": times(bm["g2"], 2),
        "xg3": times(bm["g3"], 1),
        "x2g4": times(bm["g4"], 2),
    }


def tail_margins(t1: Fraction, t2: Fraction, thresholds=None) -> Dict[str, Any]:
    """x in [1/t2, 1/t1]: a_t = x sqrt(1 + s^2 t^2) and a_t^2 = x^2 (1 + s^2 t^2), with the x factors in the models.
    Then x q' = (x d1)/(2 ell) and x^2 q'' = (x^2 d2)/(2 ell) + (x d1)^2/(4 ell^3), as _margins computes."""
    tm = _tail_models()
    v = {n: mt.evaluate_pair(model, t1, t2) for n, model in tm.items()}
    with mi.ivdps(40):
        s = mi._c("s")
        tI = iv.mpf([mt._iv(t1).a, mt._iv(t2).b])
        f2 = 1 + s * s * tI * tI
        return _margins(
            v["d"], v["xd1"], v["x2d2"], v["xg1"], v["x2g2"], v["xg3"], v["x2g4"], iv.sqrt(f2), f2, thresholds
        )


def _branch_and_bound(stack, evaluate, label_fn, max_depth, thresholds):
    st: Dict[str, Any] = {"certified_boxes": 0, "evaluations": 0, "min_lower_bound": {}, "uncertified": []}
    while stack:
        a, b, depth = stack.pop()
        st["evaluations"] += 1
        try:
            vals = evaluate(a, b, thresholds)
            ok = all(v.a > 0 for v in vals.values())
        except (ValueError, ZeroDivisionError, mp.libmp.libmpf.ComplexResult):
            vals, ok = None, False
        if ok:
            st["certified_boxes"] += 1
            for n, v in vals.items():
                st["min_lower_bound"][n] = min(st["min_lower_bound"].get(n, 1e9), float(mp.mpf(v.a)))
            continue
        if depth >= max_depth:
            st["uncertified"].append(label_fn(a, b))
            continue
        mid = (a + b) / 2
        stack += [(mid, b, depth + 1), (a, mid, depth + 1)]
    st["verified"] = not st["uncertified"]
    return st


def verify_window(n0: int = 64, max_depth: int = 30, thresholds=None) -> Dict[str, Any]:
    stack = [(WINDOW * i / n0, WINDOW * (i + 1) / n0, 0) for i in range(n0)][::-1]
    st = _branch_and_bound(stack, window_margins, lambda a, b: [a, b], max_depth, thresholds)
    st["range"] = [0.0, WINDOW]
    return st


def verify_tail(n0: int = 16, max_depth: int = 20, thresholds=None) -> Dict[str, Any]:
    T = Fraction(1, 8)
    stack = [(T * i / n0, T * (i + 1) / n0, 0) for i in range(n0)][::-1]
    st = _branch_and_bound(stack, tail_margins, lambda a, b: [str(a), str(b)], max_depth, thresholds)
    st["x_from"] = 8
    return st
