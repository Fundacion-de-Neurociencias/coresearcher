"""
python/discovery/mahler_segment_tails.py - Rigorous proof of the Mahler segment inequality (4) outside the bounded
region of mahler_segment_box: the short widths (0 < h <= .16, every m) and the tails (l <= -1.4, l >= 1.4, or
y >= 3.6), up to infinity, ADR-DISCOVERY-076.

The certifier works on boxes [m0, m1] x [h0, h1] of midpoints and half-widths in t = asinh(x/s). Bounds may be
infinite. It bounds the exact form of (4) from below:

    margin = (1 + t_+) V_pi + V_q - e_K - Gamma - (X^2 + Y^2)/(4 lambda) - t_+ (p_a + ch_q^2 + Dq^2/4),
    X = ch_C - p_a - V_q - ch_q^2 - Dq^2/4,   Y = DC/2 - p_d + ch_q Dq,

with ch_F = avg F - (F_+ + F_-)/2 (so e_K = ch_K), DF = F_+ - F_- and V_pi = f0* + r^2 B_h^2 (1 - tanh^2 m)
(`lemma_checks` proves that this is right side minus left side of (4)). The margin increases with V_q whenever
X - V_q > -2 lambda, which is checked, so V_q = 0 is the worst case.

The terms are bounded from four kinds of rigorous input:
- zone ranges of K, C, q, their t-derivatives and n_F = (s cosh t)^2 F'' on t-cells, with the far zone
  t >= 6 (x >= 726) closed at x = infinity by the Laurent-Taylor models;
- zone weights: the share of the x-length of the segment in each zone, known up to an interval, turns an average
  into a fractional knapsack (interval_engine.knapsack_average);
- the chord kernel: ch_F = -(h^2/3) int W n_F, with 0 <= W and int W <= S (1 + cosh h)/2 (lemma_checks), and the
  mean-value bound DF in 2h [min F-dot, max F-dot];
- the circle part: exact rational Taylor models in h (h <= 1), so that p_a/h^2, f0*/h^2, p_d/h^3 keep their
  precision as h -> 0; direct intervals for larger h; for unbounded h, the phase wh is left free.

For h <= 1 the margin is divided by h^2, so one uniform bound covers h -> 0.
"""

from __future__ import annotations

import math
from fractions import Fraction
from functools import lru_cache
from typing import Any, Dict, List, Optional, Tuple

import mpmath as mp
import numpy as np
import sympy as sp

from python.discovery import interval_engine as ie
from python.discovery import mahler_interval as mi
from python.discovery import mahler_ranges as mr
from python.discovery import mahler_segment_box as sb
from python.discovery import mahler_tail as mt

iv = mp.iv
T_FAR = 6.0
TM_H, TM_ORDER = Fraction(1), 32
TAIL_CFG = (6, 16, 32, 40)  # Laurent-Taylor models from x = 6 (as in mahler_twovar)
X_SWITCH = 6.0
# Bounds proved for every real x by mahler_ranges (obligation "segment: profile bounds"): they clamp the local zone
# ranges, whose mean-value enclosures are loose for derivatives on the window.
GLOBAL = {"Cd": Fraction(247, 1000), "qd": Fraction(193, 1000), "nC": Fraction(79, 100), "nq": Fraction(53, 100)}
H_SHORT = 0.16
QUANTITIES = ("K", "C", "q", "Kd", "Cd", "qd", "KCd", "nK", "nC", "nq")
PHASE_SLICES = 64


# --------------------------------------------------------------------------- zone ranges


def _jets(d, d1, d2, g1, g2, g3, g4, a_t, a_t2):
    """t-derivatives and n_F from the x-jets (a_t = dx/dt factor, a_t2 its square), as in mahler_ranges."""
    b_, r_, aR, tc = mi._c("b"), mi._c("r"), mi._c("aR"), mi._c("tc")
    ell2 = b_ - r_ * r_ - d
    ell = iv.sqrt(ell2)
    q1 = d1 / (2 * ell)
    q2 = d2 / (2 * ell) + d1 * d1 / (4 * ell2 * ell)
    C1, C2 = -d1 + (aR - 1) * g3, -d2 + (aR - 1) * g4
    K1, K2 = d1 - 2 * g1, d2 - 2 * g2
    return {
        "Kd": a_t * K1,
        "Cd": a_t * C1,
        "qd": a_t * q1,
        "KCd": a_t * (K1 + tc * C1),
        "nK": a_t2 * K2,
        "nC": a_t2 * C2,
        "nq": a_t2 * q2,
    }


def _window_box(xa: float, xb: float) -> Dict[str, Any]:
    F, FD = mr._lambdas()
    m = (xa + xb) / 2
    ip, ib = mi.inputs_point(m), mi.inputs_box(xa, xb)
    with mi.ivdps(30):
        half = iv.mpf([-(xb - xa) / 2, (xb - xa) / 2])
        v = {n: F[n](*ip) + FD[n](*ib) * half for n in F}
        X = iv.mpf([xa, xb])
        s = mi._c("s")
        a_t2 = s * s + X * X
        out = _jets(v["d"], v["d1"], v["d2"], v["g1"], v["g2"], v["g3"], v["g4"], iv.sqrt(a_t2), a_t2)
    out.update(sb._x_box_profiles(xa, xb))
    return out


_TAIL_READY = False


def _tail_models6():
    """mahler_ranges' x-scaled models, built under TAIL_CFG (valid for x >= 6). The configuration is global in
    mahler_tail, so it is set once per process and only zone jobs run there."""
    global _TAIL_READY
    if not _TAIL_READY:
        mt.configure(*TAIL_CFG)
        _TAIL_READY = True
    return _tail_models_cached()


@lru_cache(maxsize=None)
def _tail_models_cached():
    bm = mt.base_models()
    x = mt.inputs()["x"]

    def times(pair, k):
        A, B = pair
        for _ in range(k):
            A, B = x * A, x * B
        return A, B

    names = {"d": ("d", 0), "xd1": ("d1", 1), "x2d2": ("d2", 2), "xg1": ("g1", 1), "x2g2": ("g2", 2)}
    names.update({"xg3": ("g3", 1), "x2g4": ("g4", 2), "g": ("g", 0), "g2": ("g2", 0)})
    return {k: times(bm[b], e) for k, (b, e) in names.items()}


def _tail_box(t1: Fraction, t2: Fraction) -> Dict[str, Any]:
    """x in [1/t2, 1/t1] (t1 = 0 means x up to infinity); requires 1/t2 >= 6."""
    tm = _tail_models6()
    v = {n: mt.evaluate_pair(model, t1, t2) for n, model in tm.items()}
    w = v
    with mi.ivdps(40):
        s = mi._c("s")
        tI = iv.mpf([mt._iv(t1).a, mt._iv(t2).b])
        f2 = 1 + s * s * tI * tI
        out = _jets(v["d"], v["xd1"], v["x2d2"], v["xg1"], v["x2g2"], v["xg3"], v["x2g4"], iv.sqrt(f2), f2)
        out.update(sb._prof_from_jets(w["d"], w["g"], w["g2"]))
    return out


def _hull(a, b):
    return iv.mpf([min(a.a, b.a), max(a.b, b.b)])


def zone_enclosure(ta: float, tb: Optional[float]) -> Dict[str, Tuple[float, float]]:
    """Ranges of every quantity on the t-cell [ta, tb] (0 <= ta; tb None means infinity)."""
    with mi.ivdps(30):
        s = mi._c("s")
        A = iv.mpf(ta)
        xa = float(mi._lohi(s * (iv.exp(A) - iv.exp(-A)) / 2)[0])
        if tb is None:
            xb = math.inf
        else:
            B = iv.mpf(tb)
            xb = float(mi._lohi(s * (iv.exp(B) - iv.exp(-B)) / 2)[1])
    xa = max(xa, 0.0)
    acc = None
    pieces: List[Tuple[str, Any, Any]] = []
    if xa < X_SWITCH:
        top = min(xb, X_SWITCH)
        step = 0.01 if top <= 2 else (0.004 if top <= 4 else 0.002)
        n = max(1, int(math.ceil((top - xa) / step)))
        bounds = [xa + (top - xa) * i / n for i in range(n)] + [top]
        pieces += [("w", p0, p1) for p0, p1 in zip(bounds[:-1], bounds[1:])]
    if xb > X_SWITCH:
        lo = max(xa, X_SWITCH)
        t1 = Fraction(0) if xb == math.inf else Fraction(1) / Fraction(xb)
        pieces.append(("t", t1, Fraction(1) / Fraction(lo)))
    for kind, p0, p1 in pieces:
        v = _window_box(p0, p1) if kind == "w" else _tail_box(p0, p1)
        acc = v if acc is None else {n: _hull(acc[n], v[n]) for n in acc}
    with mi.ivdps(30):
        return {n: mi._lohi(acc[n]) for n in QUANTITIES}


def zone_breakpoints() -> List[float]:
    """|t| cells: width 1/128 on [0, 2], 1/32 on [2, 6]; then the far zone [6, infinity)."""
    return [k / 128 for k in range(256)] + [2 + k / 32 for k in range(129)]


def zone_job(k: int):
    """Cell k of zone_breakpoints, or the far zone [6, infinity) for the last index."""
    bp = zone_breakpoints()
    if k == len(bp) - 1:
        return zone_enclosure(T_FAR, None)
    return zone_enclosure(bp[k], bp[k + 1])


def global_clamps() -> Dict[str, Tuple[float, float]]:
    """Float brackets of the proved global bounds, plus the two implied by U_* <= .54 r^2 w^2:
    1.507 max(0, -n_K) <= U_* gives n_K >= -.54 r^2 w^2 / 1.507, and 12 (.80/m_*^2) 1.25 KCd^2 <= U_* gives
    |KCd| <= sqrt(.54 r^2 w^2 m_*^2 / 12)."""
    out = {n: (-float(v) * (1 + 1e-15), float(v) * (1 + 1e-15)) for n, v in GLOBAL.items()}
    with mi.ivdps(30):
        r, w, ms = mi._c("r"), mi._c("w"), mi._c("ms")
        G = iv.mpf(54) / 100 * r * r * w * w
        nk = (-G / (iv.mpf(1507) / 1000)).a
        kc = iv.sqrt(G * ms * ms / (12 * iv.mpf(80) / 100 * iv.mpf(125) / 100)).b
    out["nK"] = (float(mp.mpf(nk)) * (1 + 1e-15), math.inf)
    out["KCd"] = (-float(mp.mpf(kc)) * (1 + 1e-15), float(mp.mpf(kc)) * (1 + 1e-15))
    return out


class Zones:
    """Zone ranges by |t| cell, the far zone last; plus signed zones for weights."""

    def __init__(self, cells: List[Dict[str, Tuple[float, float]]]):
        self.bp = np.array(zone_breakpoints())  # cell k = [bp[k], bp[k+1]]; far zone = [bp[-1], inf)
        self.lo = {n: np.array([c[n][0] for c in cells]) for n in QUANTITIES}
        self.hi = {n: np.array([c[n][1] for c in cells]) for n in QUANTITIES}
        for n, (lo, hi) in global_clamps().items():
            self.lo[n], self.hi[n] = np.maximum(self.lo[n], lo), np.minimum(self.hi[n], hi)
            if np.any(self.lo[n] > self.hi[n]):
                raise ValueError(f"zone enclosure of {n} contradicts a proved global bound")
        edges = np.concatenate([-self.bp[::-1], self.bp[1:]])  # -6 ... 0 ... 6
        self.za = np.concatenate([[-np.inf], edges[:-1], [self.bp[-1]]])
        self.zb = np.concatenate([[edges[0]], edges[1:], [np.inf]])
        nc = len(self.bp) - 1  # finite cells per side
        idx_neg = np.arange(nc - 1, -1, -1)
        self.zsrc = np.concatenate([[nc], idx_neg, np.arange(nc), [nc]])

    def range_abs(self, a: float, b: float, name: str) -> Tuple[float, float]:
        """Range of a quantity over the t-interval [a, b] (even profiles)."""
        if a >= 0:
            u, v = a, b
        elif b <= 0:
            u, v = -b, -a
        else:
            u, v = 0.0, max(-a, b)
        k0 = int(np.searchsorted(self.bp, u, side="right")) - 1
        k1 = int(np.searchsorted(self.bp, v, side="left"))  # cells k0 .. k1-1, far zone if v > bp[-1]
        nc = len(self.bp) - 1
        k0 = min(max(k0, 0), nc)
        ks = list(range(k0, min(max(k1, k0 + 1), nc)))
        if v > self.bp[-1] or u >= self.bp[-1]:
            ks.append(nc)
        lo, hi = self.lo[name][ks], self.hi[name][ks]
        return float(lo.min()), float(hi.max())

    def weights(self, l0, l1, y0, y1, D0, D1):
        """Bounds on each signed zone's share of the x-length of [l, y]."""
        s = 3.6

        def overlap(p, q):
            a, b = np.maximum(self.za, p), np.minimum(self.zb, q)
            with np.errstate(invalid="ignore"):
                out = np.where(b > a, s * (np.sinh(b) - np.sinh(a)), 0.0)
            return np.nan_to_num(out, nan=np.inf)

        up = overlap(l0, y1)
        dn = overlap(l1, y0) if l1 < y0 else np.zeros_like(up)
        with np.errstate(divide="ignore", invalid="ignore"):
            w_hi = np.where(up == 0, 0.0, up / D0) if D0 > 0 else np.where(up == 0, 0.0, 1.0)
            w_lo = np.zeros_like(dn) if D1 == np.inf else dn / D1
        w_hi = np.nan_to_num(np.minimum(w_hi * (1 + 1e-12) + 1e-300, 1.0), nan=1.0)
        w_lo = np.nan_to_num(np.maximum(w_lo * (1 - 1e-12), 0.0), nan=0.0)
        return w_lo, w_hi

    def average(self, name, w_lo, w_hi):
        src = self.zsrc
        return ie.knapsack_average(w_lo, w_hi, self.lo[name][src], self.hi[name][src])


# --------------------------------------------------------------------------- circle part


@lru_cache(maxsize=None)
def circle_models():
    """Exact rational Taylor models in h on [0, 1]: f0*/h^2, p_a/h^2, P with p_d = tanh(m) h^3 P, and B^2/h^4."""
    w, r = Fraction(23, 5), Fraction(11, 50)
    H, N = TM_H, TM_ORDER
    C, Sc = ie.tm_cos(w, H, N), ie.tm_sinc(w, H, N)
    Ch, Sh = ie.tm_cosh(H, N), ie.tm_shc(H, N)
    iSh = ie.tm_reciprocal_one_plus(Sh - 1, N // 2 + 1)
    A = (C + w * w * Ch * iSh * Sc) * (1 / (1 + w * w))
    B = (Ch * iSh * Sc - C) * (w / (1 + w * w))
    f0 = ((1 - Sc * Sc * iSh * iSh) * (r * r * w * w / (1 + w * w))).shift(2)
    pa = ((1 - A * C) * (2 * r * r)).shift(2)
    pd = (B * Sc * (-2 * r * r * w)).shift(2)
    B2 = (B * B).shift(4)
    return {"f0": f0, "pa": pa, "pd": pd, "B2": B2}


def _consts():
    names = ("r", "w", "lam", "tp", "ms", "tc", "tr")
    return {n: mi._c(n) for n in names}


def _circle_direct(h0, h1, th):
    """f0*, p_a, p_d, V_pi on h in [h0, h1] (finite, h0 > 0) and tanh m in th."""
    c = _consts()
    r, w = c["r"], c["w"]
    H = iv.mpf([h0, h1])
    eH = iv.exp(H)
    sh, ch = (eH - 1 / eH) / 2, (eH + 1 / eH) / 2
    cw, sw = iv.cos(w * H), iv.sin(w * H)
    return [_circle_from(cw, sw, ch / sh, 1 / (sh * sh), th, r, w)]


def _circle_from(cw, sw, coth, ish2, th, r, w):
    A = (cw + w * coth * sw) / (1 + w * w)
    B = (coth * sw - w * cw) / (1 + w * w)
    f0 = r * r * (w * w - sw * sw * ish2) / (1 + w * w)
    pa = 2 * r * r * (1 - A * cw)
    pd = -2 * r * r * B * th * sw
    Vpi = f0 + r * r * B * B * (1 - th * th)
    return f0, pa, pd, Vpi


def _circle_free_phase(h0, h1, th):
    """For h in [h0, h1] (h1 may be infinite) with the phase wh left free in [0, 2 pi]."""
    c = _consts()
    r, w = c["r"], c["w"]
    H0 = iv.mpf(h0)
    e0 = iv.exp(H0)
    sh0, ch0 = (e0 - 1 / e0) / 2, (e0 + 1 / e0) / 2
    if h1 == math.inf:
        coth = iv.mpf([1, (ch0 / sh0).b])
        ish2 = iv.mpf([0, (1 / (sh0 * sh0)).b])
    else:
        H1 = iv.mpf(h1)
        e1 = iv.exp(H1)
        sh1, ch1 = (e1 - 1 / e1) / 2, (e1 + 1 / e1) / 2
        coth = iv.mpf([(ch1 / sh1).a, (ch0 / sh0).b])
        ish2 = iv.mpf([(1 / (sh1 * sh1)).a, (1 / (sh0 * sh0)).b])
    out = []
    two_pi = 2 * iv.pi
    for k in range(PHASE_SLICES):
        P = two_pi * iv.mpf([k, k + 1]) / PHASE_SLICES
        out.append(_circle_from(iv.cos(P), iv.sin(P), coth, ish2, th, r, w))
    return out


# --------------------------------------------------------------------------- box evaluation


def _I(lohi):
    return iv.mpf([lohi[0], lohi[1]])


def _meet(a, b):
    lo, hi = max(a.a, b.a), min(a.b, b.b)
    if lo > hi:
        raise ValueError("empty intersection: an enclosure is wrong")
    return iv.mpf([lo, hi])


def _chord(nrange, Wint):
    """int W n with 0 <= W, int W <= Wint and n in nrange."""
    return iv.mpf([(Wint * min(nrange.a, 0)).a, (Wint * max(nrange.b, 0)).b])


def _tanh(m0: float, m1: float):
    """tanh is increasing: [tanh m0, tanh m1] (m1 may be infinite)."""

    def th(v):
        e2 = iv.exp(2 * iv.mpf(v))
        return (e2 - 1) / (e2 + 1)

    hi = 1 if m1 == math.inf else th(m1).b
    return iv.mpf([th(m0).a, hi])


def _wint(h1: float):
    H = iv.mpf(h1)
    e = iv.exp(H)
    S = (e - 1 / e) / 2 / H
    return (S * (1 + (e + 1 / e) / 2) / 2).b


def evaluate_box(Z: Zones, m0: float, m1: float, h0: float, h1: float) -> Optional[float]:
    """Certified lower bound of the margin (divided by h^2 when h1 <= 1), or None."""
    with mi.ivdps(20):
        try:
            res = []
            if h1 <= float(TM_H):
                res.append(_normalized(Z, m0, m1, h0, h1))
            if h0 > 0:
                res.append(_regular(Z, m0, m1, h0, h1))
        except (ValueError, ZeroDivisionError):
            return None
        res = [v for v in res if v is not None]
        return max(res) if res else None


def _span(Z, m0, m1, h0, h1, names):
    a, b = m0 - h1, m1 + h1
    return {n: _I(Z.range_abs(a, b, n)) for n in names}


def _vq_ok(X_lo, Z, m0, m1, h0, h1, lam):
    q = Z.range_abs(m0 - h1, m1 + h1, "q")
    vqmax = (q[1] - q[0]) ** 2 / 4  # a variance is at most a quarter of the squared range
    return 1 + (X_lo - vqmax * 1.000001) / (2 * float(mp.mpf(lam.b))) > 0


def _normalized(Z, m0, m1, h0, h1):
    c = _consts()
    lam, tp, ms, tc, tr, r = c["lam"], c["tp"], c["ms"], c["tc"], c["tr"], c["r"]
    sp_ = _span(Z, m0, m1, h0, h1, ("Kd", "Cd", "qd", "KCd", "nK", "nC", "nq", "q"))
    Wint = _wint(h1)
    ch = {F: -_chord(sp_["n" + F], Wint) / 3 for F in ("K", "C", "q")}  # ch_F / h^2
    d = {F: 2 * sp_[F + "d"] for F in ("K", "C", "q")}  # DF / h
    dKC = _meet(2 * sp_["KCd"], d["K"] + tc * d["C"])
    Gam = iv.mpf(80) / 100 / (ms * ms) * (iv.mpf(125) / 100 * dKC * dKC + 5 * tr * tr * d["C"] * d["C"])
    H = iv.mpf([h0, h1])
    th = _tanh(m0, m1)
    cm = circle_models()
    f0, pa, PD, B2 = (cm[k].evaluate(h0, h1) for k in ("f0", "pa", "pd", "B2"))
    Vpi = f0 + r * r * (1 - th * th) * H * H * B2
    H2 = H * H
    X = ch["C"] - pa - H2 * ch["q"] * ch["q"] - d["q"] * d["q"] / 4  # X / h^2 at V_q = 0
    Y = d["C"] / 2 - th * H2 * PD + H2 * ch["q"] * d["q"]  # Y / h
    if not _vq_ok((H2 * X).a, Z, m0, m1, h0, h1, lam):
        return None
    # e_K + Gamma <= (h^2/3) int U_S with U_S = (3S/2) max(0, -n_K) + 12(.80/m_*^2)(...) <= max(1, 3S/(2 1.507)) U_*
    # (W <= 3S/2 pointwise, Cauchy-Schwarz on the endpoint differences) and U_* <= .54 r^2 w^2 (mahler_ranges)
    eH1 = iv.exp(iv.mpf(h1))
    S1 = ((eH1 - 1 / eH1) / 2 / iv.mpf(h1)) if h1 > 0 else iv.mpf(1)
    scale = iv.mpf([1, max(1, (3 * S1 / 2 / (iv.mpf(1507) / 1000)).b)])
    ustar = scale.b * iv.mpf(54) / 100 * r * r * c["w"] * c["w"] / 3
    cost = iv.mpf([(ch["K"] + Gam).a, min((ch["K"] + Gam).b, ustar.b)])
    marg = (
        (1 + tp) * Vpi
        - cost
        - (H2 * X * X + Y * Y) / (4 * lam)
        - tp * (pa + H2 * ch["q"] * ch["q"] + d["q"] * d["q"] / 4)
    )
    return float(mp.mpf(marg.a))


def _regular(Z, m0, m1, h0, h1):
    c = _consts()
    lam, tp, ms, tc, tr = c["lam"], c["tp"], c["ms"], c["tc"], c["tr"]
    l0, l1, y0, y1 = m0 - h1, m1 - h0, m0 + h0, m1 + h1
    names = ("K", "C", "q")
    Fl = {n: _I(Z.range_abs(l0, l1, n)) for n in names}
    Fy = {n: _I(Z.range_abs(y0, y1, n)) for n in names}
    sp_ = _span(Z, m0, m1, h0, h1, ("Kd", "Cd", "qd", "KCd", "nK", "nC", "nq"))
    s = mi._c("s")
    M = iv.mpf([m0, m1]) if m1 < math.inf else None
    Hh = iv.mpf([h0, h1]) if h1 < math.inf else None
    e_m0, e_h0 = iv.exp(iv.mpf(m0)), iv.exp(iv.mpf(h0))
    D0 = float(mp.mpf((2 * s * (e_m0 + 1 / e_m0) / 2 * (e_h0 - 1 / e_h0) / 2).a))
    if M is not None and Hh is not None:
        eM, eH = iv.exp(M), iv.exp(Hh)
        D1 = float(mp.mpf((2 * s * (eM + 1 / eM) / 2 * (eH - 1 / eH) / 2).b))
    else:
        D1 = math.inf
    w_lo, w_hi = Z.weights(l0, l1, y0, y1, D0, D1)
    avg = {n: _I(Z.average(n, w_lo, w_hi)) for n in names}
    ch = {n: avg[n] - (Fl[n] + Fy[n]) / 2 for n in names}
    dF = {n: Fy[n] - Fl[n] for n in names}
    if Hh is not None:
        Wint = _wint(h1)
        for n in names:
            ch[n] = _meet(ch[n], -(Hh * Hh) * _chord(sp_["n" + n], Wint) / 3)
            dF[n] = _meet(dF[n], 2 * Hh * sp_[n + "d"])
        dKC = _meet(2 * Hh * sp_["KCd"], dF["K"] + tc * dF["C"])
    else:
        dKC = dF["K"] + tc * dF["C"]
    Gam = iv.mpf(80) / 100 / (ms * ms) * (iv.mpf(125) / 100 * dKC * dKC + 5 * tr * tr * dF["C"] * dF["C"])
    th = _tanh(m0, m1)
    wv = c["w"]
    if Hh is not None and float(mp.mpf((wv * (h1 - h0)).b)) <= 0.3:
        circles = _circle_direct(h0, h1, th)
    else:
        circles = _circle_free_phase(h0, h1, th)
    worst = math.inf
    for f0, pa, pd, Vpi in circles:
        X = ch["C"] - pa - ch["q"] * ch["q"] - dF["q"] * dF["q"] / 4
        Y = dF["C"] / 2 - pd + ch["q"] * dF["q"]
        if not _vq_ok(X.a, Z, m0, m1, h0, h1, lam):
            return None
        marg = (
            (1 + tp) * Vpi
            - ch["K"]
            - Gam
            - (X * X + Y * Y) / (4 * lam)
            - tp * (pa + ch["q"] * ch["q"] + dF["q"] * dF["q"] / 4)
        )
        worst = min(worst, float(mp.mpf(marg.a)))
    return worst


# --------------------------------------------------------------------------- region and driver


def in_bounded_region(box) -> bool:
    """Box inside {|l| <= 1.4, y <= 3.6, h >= .16}, proved by mahler_segment_box."""
    m0, m1, h0, h1 = box
    return m0 - h1 >= -1.4 and m1 - h0 <= 1.4 and m1 + h1 <= 3.6 and h0 >= H_SHORT


def split_box(box):
    m0, m1, h0, h1 = box
    if h1 == math.inf:
        c = 2 * h0 + 1
        return [(m0, m1, h0, c), (m0, m1, c, h1)]
    if m1 == math.inf:
        c = 2 * m0 + 1
        return [(m0, c, h0, h1), (c, m1, h0, h1)]
    if (h1 - h0) * 3 > (m1 - m0):
        c = (h0 + h1) / 2
        return [(m0, m1, h0, c), (m0, m1, c, h1)]
    c = (m0 + m1) / 2
    return [(m0, c, h0, h1), (c, m1, h0, h1)]


def initial_boxes() -> List[Tuple[float, float, float, float]]:
    ms = [k / 4 for k in range(33)] + [16.0, math.inf]
    hs = [0.0, 0.04, 0.08, 0.12, 0.16] + [0.16 + 0.06 * k for k in range(1, 15)] + [1.0 + k / 4 for k in range(1, 29)]
    hs = sorted(set(round(v, 10) for v in hs)) + [math.inf]
    return [(a, b, c, d) for a, b in zip(ms[:-1], ms[1:]) for c, d in zip(hs[:-1], hs[1:])]


def lemma_checks() -> Dict[str, bool]:
    """The algebra and the elementary inequalities the certifier relies on."""
    out: Dict[str, bool] = {}
    Vq, Vpi, pa, pd, ch_K, ch_C, ch_q, DC, Dq, Gam, lam, tp = sp.symbols(
        "V_q V_pi p_a p_d ch_K ch_C ch_q DC Dq Gamma lambda t_p", real=True
    )
    qm, qp, qbar, Cm, Cp, Cbar = sp.symbols("q_m q_p qbar C_m C_p Cbar", real=True)
    # (4) with b_s = V_q + (qbar - q_s)^2 and the endpoint distances p_a -/+ p_d (mahler_segment)
    bp, bm = Vq + (qbar - qp) ** 2, Vq + (qbar - qm) ** 2
    devp, devm = pa + pd + bp, pa - pd + bm
    s1 = (Cbar - Cm - devp) ** 2 + (Cbar - Cp - devm) ** 2
    Vu = Vpi + Vq
    s2 = 2 * (pa - Vpi) + (qbar - qp) ** 2 + (qbar - qm) ** 2  # sum_s |ubar - u_s|^2 = 2 (p_a + b_a - V_u)
    left = ch_K + Gam + s1 / (8 * lam) + tp / 2 * s2
    subs = [(Cbar, ch_C + (Cp + Cm) / 2), (qbar, ch_q + (qp + qm) / 2), (Cp, Cm + DC), (qp, qm + Dq)]
    X = ch_C - pa - Vq - ch_q**2 - Dq**2 / 4
    Y = DC / 2 - pd + ch_q * Dq
    marg = (1 + tp) * Vpi + Vq - ch_K - Gam - (X**2 + Y**2) / (4 * lam) - tp * (pa + ch_q**2 + Dq**2 / 4)
    out["margin = right - left of (4)"] = sp.expand((Vu - left).subs(subs) - marg) == 0
    out["d margin / d V_q = 1 + X/(2 lambda)"] = sp.simplify(sp.diff(marg, Vq) - (1 + X / (2 * lam))) == 0
    # V_pi = r^2 (1 - A^2 - B^2 tanh^2 m) = f0* + r^2 B^2 (1 - tanh^2 m), with f0* = r^2 (1 - A^2 - B^2)
    A, B, th, r = sp.symbols("A B th r", real=True)
    out["V_pi split"] = (
        sp.expand(r**2 * (1 - A**2 - B**2 * th**2) - (r**2 * (1 - A**2 - B**2) + r**2 * B**2 * (1 - th**2))) == 0
    )
    # chord weight: int W dbeta/2 <= S (1 + cosh h)/2. Steps: W = 6 theta (1 - theta)(cosh m / cosh t) S >= 0 and
    # the factorization (mahler_segment); sinh(u h) <= u sinh h (sinh z / z increasing: positive coefficients);
    # (c + ch)/(c + cb) <= (1 + ch)/2 for c >= 1, cb >= 1, ch >= cb; int (1 - beta^2) dbeta/2 = 2/3.
    z = sp.Symbol("z", positive=True)
    shz = sp.Poly(sp.series(sp.sinh(z) / z, z, 0, 14).removeO(), z)
    out["sinh z / z increasing"] = all(cf > 0 for cf in shz.coeffs())
    import z3

    c_, cb, chh = z3.Reals("c cb ch")
    solver = z3.Solver()
    solver.add(c_ >= 1, cb >= 1, chh >= cb, 2 * (c_ + chh) > (1 + chh) * (c_ + cb))
    out["quotient bound (z3)"] = solver.check() == z3.unsat
    beta = sp.Symbol("beta", real=True)
    out["int (1 - beta^2) dbeta/2 = 2/3"] = sp.integrate((1 - beta**2) / 2, (beta, -1, 1)) == sp.Rational(2, 3)
    # chord identity: the trapezoid kernel in x equals -(h^2/3) int W n_F dbeta/2 after x = s sinh t
    s_, m_, h_, t_, thet, F2 = sp.symbols("s m h t theta F2", positive=True)
    lhs = (
        (2 * s_ * sp.cosh(m_) * sp.sinh(h_)) ** 2
        * thet
        * (1 - thet)
        * F2
        / 2
        * h_
        * sp.cosh(t_)
        / (2 * sp.cosh(m_) * sp.sinh(h_))
    )
    W = 6 * thet * (1 - thet) * sp.cosh(m_) / sp.cosh(t_) * sp.sinh(h_) / h_
    rhs = h_**2 / 3 * W * (s_ * sp.cosh(t_)) ** 2 * F2 / 2
    out["chord identity change of variables"] = sp.simplify(lhs - rhs) == 0
    # segment x-length: s (sinh(m + h) - sinh(m - h)) = 2 s cosh m sinh h
    out["x-length"] = (
        sp.simplify((s_ * (sp.sinh(m_ + h_) - sp.sinh(m_ - h_)) - 2 * s_ * sp.cosh(m_) * sp.sinh(h_)).rewrite(sp.exp))
        == 0
    )
    return {k: bool(v) for k, v in out.items()}


_Z: Optional[Zones] = None


def _init_worker(cells):
    global _Z
    _Z = Zones(cells)


def _certify_chunk(boxes):
    st = ie.branch_and_bound(
        boxes,
        lambda b: evaluate_box(_Z, *b),
        split_box,
        skip=in_bounded_region,
        max_depth=40,
        max_boxes=2_000_000,
    )
    st["failed"] = [[lb, [float(v) for v in b]] for lb, b in st["failed"][:50]]
    return st


def verify_with_cells(cells, pool_factory, workers: int = 8) -> Dict[str, Any]:
    """Branch and bound over the initial boxes with the given zone ranges; covers {m >= 0, h > 0} minus the bounded
    region of mahler_segment_box. `min_lower_bound` is a lower bound of the margin, divided by h^2 for h <= 1."""
    boxes = initial_boxes()
    chunks = [boxes[i :: workers * 4] for i in range(workers * 4)]
    with pool_factory(workers, initializer=_init_worker, initargs=(cells,)) as pool:
        parts = pool.map(_certify_chunk, chunks, chunksize=1)
    report = {
        "zones": len(cells),
        "initial_boxes": len(boxes),
        "certified_boxes": sum(p["certified"] for p in parts),
        "skipped_boxes_in_bounded_region": sum(p["skipped"] for p in parts),
        "evaluations": sum(p["evaluations"] for p in parts),
        "min_lower_bound": min(p["min_lower_bound"] for p in parts),
        "failed": [f for p in parts for f in p["failed"]][:50],
    }
    report["lemmas"] = lemma_checks()
    report["verified"] = all(p["verified"] for p in parts) and all(report["lemmas"].values())
    return report


def reference_margin(m: float, h: float, nodes: int = 40) -> float:
    """Independent numeric value of right minus left of (4) on the segment with midpoint m and half-width h (in t):
    Gauss-Legendre in t with density cosh t, profiles from mahler_obligations.evaluate (x < 8) or the Laurent-Taylor
    models at a point (x >= 8), closed-form circle part. Not a proof: a soundness audit of the certified bounds,
    which must never exceed it."""
    from python.discovery import mahler_obligations as mo

    with mp.workdps(30):
        r, w, lam, tp, ms, tc, tr, s = (
            mp.mpf(v) for v in ("0.22", "4.6", "0.65", "0.064", "0.352", "0.021", "0.043", "3.6")
        )

        def prof(t):
            x = abs(float(s * mp.sinh(t)))
            if x < 8:
                e = mo.evaluate(x)
                d = mp.mpf(e["d"])
                return d - 2 * mp.mpf(e["g"]), -d + mp.mpf("6.5") * mp.mpf(e["g2"]), mp.mpf(e["q"])
            tt = Fraction(1) / Fraction(x)
            bm = mt.base_models()
            v = {k: mt.evaluate_pair(bm[k], tt, tt) for k in ("d", "g", "g2")}
            pr = sb._prof_from_jets(v["d"], v["g"], v["g2"])
            return tuple(mp.mpf(pr[k].mid) for k in ("K", "C", "q"))

        na, nw = np.polynomial.legendre.leggauss(nodes)
        m, h = mp.mpf(m), mp.mpf(h)
        D = 2 * mp.cosh(m) * mp.sinh(h)
        acc = [mp.mpf(0)] * 4
        for a, b in zip(na, nw):
            t = m + h * mp.mpf(a)
            K, C, q = prof(t)
            wgt = mp.mpf(b) * h * mp.cosh(t) / D
            acc = [acc[0] + wgt * K, acc[1] + wgt * C, acc[2] + wgt * q, acc[3] + wgt * q * q]
        Kb, Cb, qb, q2b = acc
        (Kl, Cl, ql), (Ky, Cy, qy) = prof(m - h), prof(m + h)
        eK = Kb - (Kl + Ky) / 2
        Gam = mp.mpf("0.8") / ms**2 * (mp.mpf("1.25") * (Ky - Kl + tc * (Cy - Cl)) ** 2 + 5 * tr**2 * (Cy - Cl) ** 2)
        A = (mp.cos(w * h) + w * mp.coth(h) * mp.sin(w * h)) / (1 + w**2)
        B = (mp.coth(h) * mp.sin(w * h) - w * mp.cos(w * h)) / (1 + w**2)
        th = mp.tanh(m)
        Vpi = r**2 * (1 - A**2 - B**2 * th**2)
        pa, pd = 2 * r**2 * (1 - A * mp.cos(w * h)), -2 * r**2 * B * th * mp.sin(w * h)
        Vq = q2b - qb**2
        bp, bm_ = Vq + (qb - qy) ** 2, Vq + (qb - ql) ** 2
        X = Cb - (Cy + Cl) / 2 - pa - (bp + bm_) / 2
        Y = (Cy - Cl) / 2 - pd - (bp - bm_) / 2
        return float((1 + tp) * (Vpi + Vq) - (eK + Gam + (X**2 + Y**2) / (4 * lam) + tp * (pa + (bp + bm_) / 2)))
