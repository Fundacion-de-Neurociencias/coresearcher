"""
python/discovery/mahler_twovar.py - Rigorous proof of the two-variable scalar inequalities (3) of the general Mahler
paper (prop:scalar-input) outside the square [-3, 3]^2, ADR-DISCOVERY-076. With mahler_interval.verify_2d
(on [-3, 3]^2) this covers all of R^2.

Reduction (checked symbolically in `check_reduction`). With pi = r u(theta), theta = w asinh(x/s),
u = (cos, sin), u_perp = (-sin, cos):
    S_pi = r (a u + b u_perp),   a = 2 + theta'^2,   b = x theta' - theta''.
The inequalities see pi only through S_pi(z).pi(x) = r^2 (a_z cos D + b_z sin D) and
S_pi(z).S_pi(x) = r^2 ((a_z a_x + b_z b_x) cos D + (b_z a_x - a_z b_x) sin D), with D = theta(x) - theta(z).
If D is left free, the two dot products range over |S_pi(z)| r [-1, 1] and |S_pi(z)| |S_pi(x)| [-1, 1]
(Cauchy-Schwarz, attained), so it suffices to prove both inequalities for every
    c in [-1, 1]:  S_pi(z).pi(x) -> rho(z) r c,   S_pi(z).S_pi(x) -> rho(z) rho(x) c',   rho = r sqrt(a^2 + b^2).
Every remaining quantity (q, S_q, v'', rho) is even, so (z, x) may be replaced by (|z|, |x|): the region outside
[-3, 3]^2 becomes z, x >= 0 with max(z, x) > 3. Dropping the phase only enlarges the set of cases to check.

Enclosures. On [0, X0] the even pieces come from mahler_interval.even_enclosures (second-order Taylor forms); on
[X0, inf) from the Laurent-Taylor models of mahler_tail with X0 = 6, in t = 1/x. rho is elementary. The pair check
uses float intervals widened by one ulp per operation (as in mahler_interval).
"""

from __future__ import annotations

from fractions import Fraction
from functools import lru_cache
from typing import Any, Dict, List, Tuple

import mpmath as mp
import numpy as np
import sympy as sp

from python.discovery import mahler_interval as mi
from python.discovery import mahler_tail as mt

iv = mp.iv
TAIL = (6, 16, 32, 40)  # X0, Mills terms, phi power, truncation order for the (3) tail
WINDOW = 3.0


def check_reduction() -> Dict[str, bool]:
    """S_pi = r (a u + b u_perp) and the two dot-product formulas, symbolically."""
    x, z = sp.symbols("x z", real=True)
    r, w, s = sp.Rational(22, 100), sp.Rational(46, 10), sp.Rational(36, 10)

    def pieces(v):
        th = w * sp.asinh(v / s)
        p = sp.Matrix([r * sp.cos(th), r * sp.sin(th)])
        S = 2 * p + v * sp.diff(p, v) - sp.diff(p, v, 2)
        t1 = sp.diff(th, v)
        a, b = 2 + t1**2, v * t1 - sp.diff(th, v, 2)
        u, up = sp.Matrix([sp.cos(th), sp.sin(th)]), sp.Matrix([-sp.sin(th), sp.cos(th)])
        return th, p, S, a, b, u, up

    thz, pz, Sz, az, bz, uz, upz = pieces(z)
    thx, px, Sx, ax, bx, ux, upx = pieces(x)
    D = thx - thz
    form = sp.simplify(Sz - r * (az * uz + bz * upz)) == sp.zeros(2, 1)
    dot1 = sp.simplify(sp.expand_trig((Sz.T * px)[0] - r**2 * (az * sp.cos(D) + bz * sp.sin(D)))) == 0
    dot2 = (
        sp.simplify(
            sp.expand_trig((Sz.T * Sx)[0] - r**2 * ((az * ax + bz * bx) * sp.cos(D) + (bz * ax - az * bx) * sp.sin(D)))
        )
        == 0
    )
    norm = sp.simplify((Sz.T * Sz)[0] - r**2 * (az**2 + bz**2)) == 0
    return {"S_pi = r(a u + b u_perp)": form, "S_pi(z).pi(x)": dot1, "S_pi(z).S_pi(x)": dot2, "|S_pi|^2": norm}


def _rho_box(lo, hi):
    """rho = r sqrt(a^2 + b^2) on x in [lo, hi] (hi may be inf). For x >= 1 it is evaluated in t = 1/x, where
    a = 2 + w^2 t^2/(s^2 t^2 + 1) and b = w/sqrt(s^2 t^2 + 1) + w t^2/(s^2 t^2 + 1)^(3/2) carry no dependency on a
    repeated x."""
    with mi.ivdps(30):
        r, w, s = mi._c("r"), mi._c("w"), mi._c("s")
        if lo >= 1:
            t = iv.mpf([0 if hi == np.inf else (1 / iv.mpf(hi)).a, (1 / iv.mpf(lo)).b])
            den = s * s * t * t + 1
            th1 = w * t / iv.sqrt(den)
            b = w / iv.sqrt(den) + w * t * t / (den * iv.sqrt(den))
        else:
            X = iv.mpf([lo, hi])
            den = s * s + X * X
            th1 = w / iv.sqrt(den)
            b = X * th1 + w * X / (den * iv.sqrt(den))
        a = 2 + th1 * th1
        return mi._lohi(r * iv.sqrt(a * a + b * b))


@lru_cache(maxsize=None)
def _tail_box(t1: Fraction, t2: Fraction) -> Dict[str, Tuple[float, float]]:
    with mt.tail_config(*TAIL):
        bm = mt.base_models()
        v = {n: mt.evaluate_pair(bm[n], t1, t2) for n in ("d", "d1", "d2", "xd1", "v2")}
    with mi.ivdps(40):
        b_, c_, r_ = mi._c("b"), mi._c("c"), mi._c("r")
        k = iv.sqrt(b_ - c_)
        s = b_ - r_ * r_ - v["d"]
        rs = iv.sqrt(s)
        q = k - rs
        Sq = 2 * q + v["xd1"] / (2 * rs) - (v["d2"] / (2 * rs) + v["d1"] * v["d1"] / (4 * s * rs))
        return {"q": mi._lohi(q), "Sq": mi._lohi(Sq), "v2": mi._lohi(v["v2"])}


BAND = ((3.0, 6.0, 1 / 256),)  # (from, to, starting box width) on the band [3, X0]; refined adaptively


def _band_edges(low_width: float, band) -> List[float]:
    edges = [i * low_width for i in range(int(WINDOW / low_width) + 1)]
    for lo, hi, w in band:
        edges += [lo + i * w for i in range(1, int(round((hi - lo) / w)) + 1)]
    return edges


def bounded_box(ab: Tuple[float, float]) -> Dict[str, Any]:
    a, b = ab
    return {"lo": a, "hi": b, **mi.even_enclosures(a, b), "rho": _rho_box(a, b)}


TOL = {"Sq": 0.01, "q": 0.005, "v2": 0.005, "rho": 0.005}  # largest allowed enclosure width per piece


def _wide(box) -> bool:
    return any(box[k][1] - box[k][0] > tol for k, tol in TOL.items())


def one_dim_boxes(low_width: float = 1 / 64, band=BAND, tail_boxes: int = 64, pool=None, max_rounds: int = 8):
    """Enclosures of q, S_q, v'', rho on boxes covering [0, inf). Bounded boxes are bisected in rounds until every
    enclosure is narrower than TOL. `pool` (optional) parallelizes the bounded part."""
    edges = _band_edges(low_width, band)
    todo = list(zip(edges[:-1], edges[1:]))
    done: List[Dict] = []
    for _ in range(max_rounds):
        if not todo:
            break
        res = pool.map(bounded_box, todo, chunksize=8) if pool else [bounded_box(p) for p in todo]
        todo = []
        for box in res:
            if _wide(box):
                m = (box["lo"] + box["hi"]) / 2
                todo += [(box["lo"], m), (m, box["hi"])]
            else:
                done.append(box)
    if todo:  # keep whatever is left; the pair check decides whether it is good enough
        done += pool.map(bounded_box, todo, chunksize=8) if pool else [bounded_box(p) for p in todo]
    done.sort(key=lambda bx: bx["lo"])
    x0 = TAIL[0]
    T = Fraction(1, x0)
    for i in range(tail_boxes):
        t1, t2 = T * i / tail_boxes, T * (i + 1) / tail_boxes
        lo, hi = float(1 / t2), (np.inf if t1 == 0 else float(1 / t1))
        done.append({"lo": lo, "hi": hi, **_tail_box(t1, t2), "rho": _rho_box(lo, hi)})
    return done


# vectorized float intervals (lo, hi arrays), one ulp outward per operation
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


def _arr(boxes, key, side):
    return np.array([b[key][side] for b in boxes])


def _pair_block(Z, X, inside, K, r, csplit):
    m1min = np.full(inside.shape, np.inf)
    for i in range(csplit):
        c = (np.float64(-1 + 2 * i / csplit), np.float64(-1 + 2 * (i + 1) / csplit))
        dot1 = _mul(_mul(Z["rho"], r), c)
        Hv = _add(_add(K["4c"], _mul(K["4"], _mul(K["k"], X["q"]))), _mul(K["2"], _mul(_sub(K["k"], X["q"]), Z["Sq"])))
        Hv = _sub(Hv, _mul(K["2"], dot1))
        H0 = _sub(_add(Hv, X["v2"]), K["2kap"])
        H02 = _sq(H0)
        lhs = _sub(_add(Hv, _mul(K["tc"], H0)), _mul(K["tr/2"], _add(K["hs"], _mul(K["1/hs"], H02))))
        rhs = _add(_add(K["rhs0"], _mul(K["2bm"], _mul(Z["Sq"], X["Sq"]))), _mul(K["1/alpha"], H02))
        m1min = np.minimum(m1min, _sub(lhs, rhs)[0])
    dot2 = _mul(_mul(Z["rho"], X["rho"]), (np.float64(-1.0), np.float64(1.0)))
    m2 = _sub(_add(K["4c"], _mul(_mul(K["2"], K["k"]), _add(Z["Sq"], X["Sq"]))), _add(_mul(Z["Sq"], X["Sq"]), dot2))[0]
    return np.where(inside, np.inf, m1min), np.where(inside, np.inf, m2)


def verify_outside(boxes: List[Dict] = None, csplit: int = 16, block: int = 256) -> Dict[str, Any]:
    """Both inequalities (3) for every pair of boxes with max(z, x) > 3 and every phase (z rows in blocks)."""
    boxes = boxes or one_dim_boxes()
    K = mi._consts()
    r = mi._lohi(mi._c("r"))
    lo = {k: _arr(boxes, k, 0) for k in ("q", "Sq", "v2", "rho")}
    hi = {k: _arr(boxes, k, 1) for k in ("q", "Sq", "v2", "rho")}
    his = np.array([b["hi"] for b in boxes])
    X = {k: (lo[k][None, :], hi[k][None, :]) for k in lo}
    mins, bad, checked = [np.inf, np.inf], [], 0
    for start in range(0, len(boxes), block):
        sl = slice(start, start + block)
        Z = {k: (lo[k][sl, None], hi[k][sl, None]) for k in lo}
        inside = (his[sl, None] <= WINDOW) & (his[None, :] <= WINDOW)
        m1, m2 = _pair_block(Z, X, inside, K, r, csplit)
        checked += int((~inside).sum())
        mins = [min(mins[0], float(m1.min())), min(mins[1], float(m2.min()))]
        for i, j in np.argwhere((m1 <= 0) | (m2 <= 0))[:20]:
            bad.append([boxes[start + i]["lo"], boxes[start + i]["hi"], boxes[j]["lo"], boxes[j]["hi"]])
    return {
        "window": WINDOW,
        "boxes_1d": len(boxes),
        "pairs_checked": checked,
        "phase_splits": csplit,
        "min_lower_bound": mins,
        "uncertified": bad[:20],
        "verified": not bad,
    }
