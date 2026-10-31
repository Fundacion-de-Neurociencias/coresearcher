"""
python/discovery/mahler_segment_box.py - Rigorous check of the segment inequality (4) of the general Mahler paper on
the bounded region of endpoint pairs {|l| <= 1.4, y <= 3.6, h >= .16} (t = asinh(x/s) coordinates, h = (y - l)/2),
ADR-DISCOVERY-076. This covers the paper's middle and large width regimes with an independent method (no Bernstein
certificates).

Exact form. With averages taken with the density cosh t on [l, y] (the uniform average in x), (4) is equivalent to
    e_K + Gamma + (X^2 + Y^2)/(4 lambda) + t_+ (p_a + b_a) < (1 + t_+) V_u,
    X = c_a - p_a - b_a,  Y = c_d - p_d - b_d,  V_u = r^2 (1 - A_h^2 - B_h^2 tanh^2 m) + V_q
(mahler_segment proves the identities). Here b_sigma = avg (q - q_sigma)^2, V_q = avg q^2 - (avg q)^2, and A_h, B_h,
p_a, p_d are the closed forms of the circle part.

Method.
1. t-cells of width 1/1280. On each cell, enclosures of K, C, q, q^2 and cosh t: mean-value forms in x
   (mahler_interval) for |x| <= 8, Laurent-Taylor models (mahler_tail) for |x| >= 8. The profiles are even.
2. Integrals over [l, y] = sums of cell integrals (cell width times enclosure of F cosh t), plus the two partial
   cells, each enclosed by [0, width] times the cell enclosure.
3. Every pair (cell of l, cell of y) in the region with l + y >= 0 is checked in float intervals widened by one ulp
   per operation. Reflection t -> -t maps [l, y] to [-y, -l] and preserves both sides of (4) (K, C, q are even and
   the circle map is an isometry), so l + y >= 0 suffices.
"""

from __future__ import annotations

from fractions import Fraction
from functools import partial
from typing import Any, Dict, List, Tuple

import mpmath as mp
import numpy as np

from python.discovery import mahler_interval as mi
from python.discovery import mahler_ranges as mr
from python.discovery import mahler_tail as mt

iv = mp.iv
CELLS_PER_UNIT = 1280
T_LO, T_HI = -1.4, 3.6
H_MIN = 0.16
L_MAX = 1.4


def _prof_from_jets(d, g, g2):
    b_, c_, r_, aR = mi._c("b"), mi._c("c"), mi._c("r"), mi._c("aR")
    q = iv.sqrt(b_ - c_) - iv.sqrt(b_ - r_ * r_ - d)
    return {"K": d - 2 * g, "C": -d + (aR - 1) * g2, "q": q}


def _x_box_profiles(xa: float, xb: float) -> Dict[str, Any]:
    """K, C, q enclosures for x in [xa, xb], 0 <= xa < xb."""
    if xa >= 8:
        t1, t2 = Fraction(1) / Fraction(xb), Fraction(1) / Fraction(xa)
        bm = mt.base_models()
        v = {n: mt.evaluate_pair(bm[n], t1, t2) for n in ("d", "g", "g2")}
        with mi.ivdps(40):
            return _prof_from_jets(v["d"], v["g"], v["g2"])
    F, _, _ = mi._lambdas()
    R, RD = mr._lambdas()
    m = (xa + xb) / 2
    ip, ib = mi.inputs_point(m), mi.inputs_box(xa, xb)
    with mi.ivdps(30):
        half = iv.mpf([-(xb - xa) / 2, (xb - xa) / 2])
        h2 = iv.mpf([0, ((xb - xa) / 2) ** 2]) / 2
        # second-order Taylor forms: value and first derivative at the midpoint, second derivative on the box
        d = F["d"](*ip) + R["d1"](*ip) * half + RD["d1"](*ib) * h2
        g = F["g"](*ip) + R["g1"](*ip) * half + RD["g1"](*ib) * h2
        g2 = R["g2"](*ip) + R["g3"](*ip) * half + RD["g3"](*ib) * h2
        return _prof_from_jets(d, g, g2)


def _hull(a, b):
    return iv.mpf([min(a.a, b.a), max(a.b, b.b)])


def cell_enclosure(k: int, n: int = CELLS_PER_UNIT) -> Dict[str, Tuple[float, float]]:
    """Cell [k, k+1]/n in t (k may be negative): enclosures of K, C, q, q^2, cosh t and F cosh t."""
    ta, tb = Fraction(k, n), Fraction(k + 1, n)
    a, b = (ta, tb) if ta >= 0 else (-tb, -ta)  # evenness: use |t|
    with mi.ivdps(30):
        T = iv.mpf([mt._iv(a).a, mt._iv(b).b])
        s = mi._c("s")
        eT = iv.exp(T)
        sinhT, coshT = (eT - 1 / eT) / 2, (eT + 1 / eT) / 2
        X = s * sinhT
    # split the x box into pieces narrow enough for the mean-value forms
    xa, xb = mi._lohi(X)  # rounded outward
    xa = max(float(xa), 0.0)
    xb = float(xb)
    step = 0.02 if xb < 4 else 0.005
    pieces = max(1, int(np.ceil((min(xb, 8) - xa) / step))) if xa < 8 else 1
    if xa < 8 < xb:
        bounds = [xa] + [xa + (8 - xa) * i / pieces for i in range(1, pieces)] + [8.0, xb]
    else:
        bounds = [xa + (xb - xa) * i / pieces for i in range(pieces + 1)]
    prof = None
    for p0, p1 in zip(bounds[:-1], bounds[1:]):
        pv = _x_box_profiles(p0, p1)
        prof = pv if prof is None else {n: _hull(prof[n], pv[n]) for n in pv}
    with mi.ivdps(30):
        out = {n: mi._lohi(v) for n, v in prof.items()}
        out["q2"] = mi._lohi(prof["q"] * prof["q"])
        out["cosh"] = mi._lohi(coshT)
        for n in ("K", "C", "q"):
            out[n + "c"] = mi._lohi(prof[n] * coshT)
        out["q2c"] = mi._lohi(prof["q"] * prof["q"] * coshT)
    return out


# vectorized float intervals (lo, hi), one ulp outward per operation
def _out(lo, hi):
    return np.nextafter(lo, -np.inf), np.nextafter(hi, np.inf)


def _add(A, B):
    return _out(np.add(A[0], B[0]), np.add(A[1], B[1]))


def _sub(A, B):
    return _out(np.subtract(A[0], B[1]), np.subtract(A[1], B[0]))


def _mul(A, B):
    c = [np.multiply(A[0], B[0]), np.multiply(A[0], B[1]), np.multiply(A[1], B[0]), np.multiply(A[1], B[1])]
    return _out(np.minimum.reduce(c), np.maximum.reduce(c))


def _sq(A):
    lo2, hi2 = np.multiply(A[0], A[0]), np.multiply(A[1], A[1])
    lo = np.where((A[0] <= 0) & (A[1] >= 0), 0.0, np.minimum(lo2, hi2))
    return _out(lo, np.maximum(lo2, hi2))


def _div(A, B):
    if np.any(B[0] <= 0):
        raise ValueError("division by an interval containing 0")
    inv = _out(1.0 / B[1], 1.0 / B[0])
    return _mul(A, inv)


def _const(v):
    return (np.nextafter(v, -np.inf), np.nextafter(v, np.inf))


def _flo(v):
    return float(mp.mpf(v.a)), float(mp.mpf(v.b))


INTEGRANDS = ("Kc", "Cc", "qc", "q2c", "cosh")
VALUES = ("K", "C", "q")


def cell_table(cells: Dict[int, Dict[str, Tuple[float, float]]], k0: int, k1: int, n: int) -> Dict[str, Any]:
    """Arrays over cells k = k0 .. k1 - 1 of width 1/n, negative cells mirrored from |t|. For each integrand: the
    cell integral (width times enclosure) and its prefix sums, with rounding slack."""
    ks = np.arange(k0, k1)
    src = [k if k >= 0 else -k - 1 for k in ks]
    width = _const(1.0 / n)
    tab: Dict[str, Any] = {"k0": k0, "k1": k1, "n": n}
    for name in INTEGRANDS + VALUES:
        lo = np.array([cells[k][name][0] for k in src])
        hi = np.array([cells[k][name][1] for k in src])
        tab[name] = (lo, hi)
        if name in INTEGRANDS:
            clo, chi = _mul(width, (lo, hi))
            tab[name + "_cell"] = (clo, chi)
            # float prefix sums err by at most (k u) sum |terms| (u = 2^-53); the slack below is twice that
            idx = np.arange(1, len(ks) + 1)
            slo = np.concatenate([[0.0], np.cumsum(clo)])
            shi = np.concatenate([[0.0], np.cumsum(chi)])
            slack = np.concatenate([[0.0], idx * 2.3e-16 * np.cumsum(np.maximum(np.abs(clo), np.abs(chi)))])
            tab[name + "_S"] = _out(slo - slack, shi + slack)
    return tab


def _circle_tables(nd: int, ns: int, n: int = CELLS_PER_UNIT):
    """Circle factors by h index d (h in [(d-1), (d+1)] / (2N)) and m index s (m in [s, s+2] / (2N)):
    1 - A cos(wh), 1 - A^2, B sin(wh), B^2 (functions of h) and tanh m, tanh^2 m."""
    w = mi._c("w")
    hcols: Dict[str, List[Tuple[float, float]]] = {k: [] for k in ("P1", "Q1", "Bs", "B2")}
    with mi.ivdps(30):
        for d in range(nd):
            H = iv.mpf([max(d - 1, 0), d + 1]) / (2 * n)
            if H.a <= 0:
                for k in hcols:
                    hcols[k].append((np.nan, np.nan))
                continue
            eH = iv.exp(H)
            sh, ch = (eH - 1 / eH) / 2, (eH + 1 / eH) / 2
            cw, sw = iv.cos(w * H), iv.sin(w * H)
            A = (cw + w * ch / sh * sw) / (1 + w * w)
            B = (ch / sh * sw - w * cw) / (1 + w * w)
            for k, v in (("P1", 1 - A * cw), ("Q1", 1 - A * A), ("Bs", B * sw), ("B2", B * B)):
                hcols[k].append(_flo(v))
        scols: Dict[str, List[Tuple[float, float]]] = {"th": [], "th2": []}
        for s in range(-4, ns):
            M = iv.mpf([s, s + 2]) / (2 * n)
            e2 = iv.exp(2 * M)
            th = (e2 - 1) / (e2 + 1)
            scols["th"].append(_flo(th))
            scols["th2"].append(_flo(th * th))
    hc = {k: (np.array([a for a, _ in v]), np.array([b for _, b in v])) for k, v in hcols.items()}
    sc = {k: (np.array([a for a, _ in v]), np.array([b for _, b in v])) for k, v in scols.items()}
    return hc, sc


def _widen(A):
    """mpmath-to-float conversion rounds to nearest: widen by one ulp."""
    return _out(*A)


def _pick(A, idx):
    return A[0][idx], A[1][idx]


def _hull0(A):
    return _out(np.minimum(A[0], 0.0), np.maximum(A[1], 0.0))


def pair_margins(tab, hc, sc, li, yj) -> Tuple[np.ndarray, np.ndarray]:
    """Lower bound of right - left of (4) for l in cell li and y in cell yj (arrays of absolute cell indices),
    and an upper bound of left / right."""
    k0 = tab["k0"]
    i, j = li - k0, yj - k0
    C = {n: mi._c(n) for n in ("r", "lam", "tp", "ms", "tc", "tr")}
    r2, lam, tp, ms, tc, tr = (_const(float(mp.mpf(v.mid))) for v in (C["r"] ** 2, *(C[n] for n in list(C)[1:])))
    # exact constants are dyadic-unfriendly; _const brackets the float nearest the midpoint, which is within half an
    # ulp of the exact value, so the bracket contains it
    av = {}
    for name in INTEGRANDS:
        S, cell = tab[name + "_S"], tab[name + "_cell"]
        full = _sub(_pick(S, j), _pick(S, i + 1))
        av[name] = _add(_add(full, _hull0(_pick(cell, i))), _hull0(_pick(cell, j)))
    D = av["cosh"]
    mean = {n: _div(av[n + "c"], D) for n in ("K", "C", "q", "q2")}
    lv = {n: _pick(tab[n], i) for n in VALUES}
    yv = {n: _pick(tab[n], j) for n in VALUES}
    half = _const(0.5)
    eK = _sub(mean["K"], _mul(half, _add(lv["K"], yv["K"])))
    dK, dC = _sub(yv["K"], lv["K"]), _sub(yv["C"], lv["C"])
    gam = _mul(
        _div(_const(0.8), _sq(ms)),
        _add(_mul(_const(1.25), _sq(_add(dK, _mul(tc, dC)))), _mul(_mul(_const(5.0), _sq(tr)), _sq(dC))),
    )
    dd, ss = yj - li, li + yj + 4
    P1, Q1, Bs, B2 = (_widen(_pick(hc[k], dd)) for k in ("P1", "Q1", "Bs", "B2"))
    th, th2 = (_widen(_pick(sc[k], ss)) for k in ("th", "th2"))
    two_r2 = _mul(_const(2.0), r2)
    pa = _mul(two_r2, P1)
    pd = _mul(_mul(_const(-1.0), two_r2), _mul(Bs, th))
    Vpi = _mul(r2, _sub(Q1, _mul(B2, th2)))
    Vq = _sub(mean["q2"], _sq(mean["q"]))

    def b_of(qe):
        return _add(_sub(mean["q2"], _mul(_mul(_const(2.0), qe), mean["q"])), _sq(qe))

    dev_l = _add(_sub(pa, pd), b_of(lv["q"]))
    dev_y = _add(_add(pa, pd), b_of(yv["q"]))
    s1 = _add(_sq(_sub(_sub(mean["C"], yv["C"]), dev_l)), _sq(_sub(_sub(mean["C"], lv["C"]), dev_y)))
    s2 = _add(_mul(_const(2.0), _sub(pa, Vpi)), _add(_sq(_sub(mean["q"], lv["q"])), _sq(_sub(mean["q"], yv["q"]))))
    left = _add(_add(eK, gam), _add(_div(s1, _mul(_const(8.0), lam)), _mul(_mul(half, tp), s2)))
    right = _add(Vpi, Vq)
    return right[0] - left[1], left[1] / right[0]


def region_pairs(n: int = CELLS_PER_UNIT):
    """Cell index pairs (li, yj) covering {|l| <= 1.4, y <= 3.6, y - l >= .32, l + y >= 0}, by rows of li."""
    k0, k1 = int(round(-L_MAX * n)), int(round(T_HI * n))
    dmin = int(np.floor(2 * H_MIN * n)) - 1
    for li in range(k0, -k0):
        jlo = max(li + dmin, -li - 2)
        if jlo < k1:
            yield li, np.arange(jlo, k1)


def _rows(tab, hc, sc, pairs, stats):
    bad = []
    for li, js in pairs:
        m, ratio = pair_margins(tab, hc, sc, np.full(len(js), li), js)
        stats["pairs"] += len(js)
        ok = m > 0
        if ok.any():
            stats["min_margin"] = min(stats["min_margin"], float(m[ok].min()))
            stats["max_ratio"] = max(stats["max_ratio"], float(ratio[ok].max()))
        bad += [(li, int(j)) for j in js[~ok]]
    stats["uncertified"] = len(bad)
    return bad


def verify_bounded(pool, refine: int = 8, levels: int = 2) -> Dict[str, Any]:
    """Check (4) on {|l| <= 1.4, y <= 3.6, h >= .16, m >= 0}: all cell pairs at width 1/1280, then the pairs that fail
    split into refine x refine sub-pairs at width 1/(1280 refine), up to `levels` times."""
    n = CELLS_PER_UNIT
    k0, k1 = int(round(T_LO * n)), int(round(T_HI * n))
    ks = list(range(0, k1))
    cells = dict(zip(ks, pool.map(partial(cell_enclosure, n=n), ks, chunksize=16)))
    tab = cell_table(cells, k0, k1, n)
    hc, sc = _circle_tables(k1 - k0 + 2, 2 * k1 + 4, n)
    st = {"cell_width": f"1/{n}", "pairs": 0, "min_margin": np.inf, "max_ratio": 0.0}
    bad = _rows(tab, hc, sc, region_pairs(n), st)
    report = {"levels": [st]}
    f = 1
    for _ in range(levels):
        if not bad:
            break
        f *= refine
        nf = n * f
        B = np.array(bad)
        sub = np.arange(refine)
        shape = (len(B), refine, refine)
        L = np.broadcast_to(B[:, 0, None, None] * refine + sub[None, :, None], shape).reshape(-1)
        Y = np.broadcast_to(B[:, 1, None, None] * refine + sub[None, None, :], shape).reshape(-1)
        keep = (Y + 1 - L) >= int(np.ceil(2 * H_MIN * nf))
        L, Y = L[keep], Y[keep]
        c0, c1 = int(L.min()), int(Y.max()) + 1
        ks = list(range(c0, c1))
        cells = dict(zip(ks, pool.map(partial(cell_enclosure, n=nf), ks, chunksize=32)))
        tab = cell_table(cells, c0, c1, nf)
        hc, sc = _circle_tables(int((Y - L).max()) + 2, int((L + Y).max()) + 4, nf)
        st = {"cell_width": f"1/{nf}", "pairs": 0, "min_margin": np.inf, "max_ratio": 0.0}
        order = np.argsort(L, kind="stable")
        L, Y = L[order], Y[order]
        cut = np.flatnonzero(np.diff(L)) + 1
        rows = [(int(Ls[0]), Ys) for Ls, Ys in zip(np.split(L, cut), np.split(Y, cut))]
        bad = _rows(tab, hc, sc, rows, st)
        report["levels"].append(st)
    report["verified"] = not bad
    report["uncertified"] = [list(map(int, b)) for b in bad[:20]]
    report["max_ratio"] = max(s_["max_ratio"] for s_ in report["levels"])
    report["min_margin"] = min(s_["min_margin"] for s_ in report["levels"])
    return report
