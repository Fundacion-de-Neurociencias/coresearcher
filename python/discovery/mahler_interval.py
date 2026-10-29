"""
python/discovery/mahler_interval.py - Rigorous interval-arithmetic proof, on a bounded window, of the scalar
inequalities of "The Mahler Conjecture for General Convex Bodies" (prop:scalar-input), ADR-DISCOVERY-076.

Method (independent of the authors' programs):

1. Stable closed forms on x >= 0. With Y = (1 - p)/phi (the Mills ratio), u = 1 - p = phi*Y and
   h0(y) = (-log(1 - y) - y)/y^2 = sum_m y^m/(m + 2), the profiles read
       d = (phi + x p)^2 Y^2 h0(u) + (1 - xY)^2 j,   j = -1 + u + x^2/2 + log sqrt(2 pi) - log Y,
       g = (1 - p^2 Y^2 h0(u) - Y^2 j)/2,              v = log p + log Y + x^2/2 + log sqrt(2 pi).
   They contain no exponentially large factor. Derivatives close over p' = phi, phi' = -x phi, Y' = xY - 1,
   u' = -phi, h_k' = -phi h_{k+1}. `check_stable_forms` proves symbolically that these equal the paper's profiles,
   and `check_evenness` that d, g, v are even, so x >= 0 suffices for every even quantity.
2. Rigorous inputs. p(x), 1 - p(x) at a point come from the alternating erf series with its remainder bound;
   phi from interval exp. On a box [a, b] subset [0, inf), p is increasing and phi, Y, u decreasing
   (Y(x) = int_0^inf exp(-xt - t^2/2) dt), and h_k has positive coefficients, so endpoint values enclose them.
3. Enclosures. One-variable margins use the mean-value form f(m) + f'([a, b]) [-w/2, w/2]; the even pieces of the
   two-variable inequalities use second-order Taylor forms. All arithmetic is mpmath interval arithmetic (outward
   rounding); the two-variable combination uses float intervals widened by one ulp per operation, with every
   constant enclosed exactly.
4. Branch and bound. A box is certified when every margin's lower bound is > 0; otherwise it is bisected.

What it proves: the first bullet of prop:scalar-input on |x| <= W1 and the two inequalities (3) on [-W2, W2]^2.
It relies on mpmath's interval library being correct. It does not cover the tails or the segment inequality (4).
"""

from __future__ import annotations

from contextlib import contextmanager
from functools import lru_cache
from typing import Any, Dict, List, Tuple

import mpmath as mp
import numpy as np
import sympy as sp

iv = mp.iv
R = sp.Rational


@contextmanager
def ivdps(n: int):
    old = iv.dps
    iv.dps = n
    try:
        yield
    finally:
        iv.dps = old


# ---------------------------------------------------------------------------
# Symbolic layer
# ---------------------------------------------------------------------------

x, p, ph, Y, LY = sp.symbols("x p ph Y LY", real=True)
H = sp.symbols("H0:8", real=True)
DER = {x: 1, p: ph, ph: -x * ph, Y: x * Y - 1, LY: (x * Y - 1) / Y}
for _k in range(7):
    DER[H[_k]] = -ph * H[_k + 1]


def D(e: sp.Expr, n: int = 1) -> sp.Expr:
    for _ in range(n):
        e = sum(sp.diff(e, s) * ds for s, ds in DER.items())
    return sp.expand(e)


_L2PI = sp.log(2 * sp.pi) / 2
_u = ph * Y
_j = -1 + _u + x**2 / 2 + _L2PI - LY
d_stable = (ph + x * p) ** 2 * Y**2 * H[0] + (1 - x * Y) ** 2 * _j
g_stable = R(1, 2) * (1 - p**2 * Y**2 * H[0] - Y**2 * _j)
v_stable = sp.log(p) + LY + x**2 / 2 + _L2PI
SYMS = [x, p, ph, Y, LY] + list(H)
IVMODS = [
    {"sqrt": iv.sqrt, "log": iv.log, "exp": iv.exp, "pi": iv.pi, "mpf": iv.mpf, "cos": iv.cos, "sin": iv.sin},
    "mpmath",
]

PARAMS = {
    "b": (602, 1000),
    "c": (365, 1000),
    "r": (22, 100),
    "aR": (15, 2),
    "lam": (13, 20),
    "tm": (-22, 1000),
    "tp": (64, 1000),
    "ms": (352, 1000),
    "eta": (22, 1000),
    "kappa": (116, 100),
    "tc": (21, 1000),
    "tr": (43, 1000),
    "e0": (256, 1000),
    "alpha": (226, 100),
    "hs": (1, 2),
    "w": (46, 10),
    "s": (36, 10),
}


def _c(name: str):
    n, m = PARAMS[name]
    return iv.mpf(n) / m


def check_evenness() -> Dict[str, bool]:
    """d, g, v are even: x -> -x swaps p and 1 - p and fixes phi."""
    P, Q = sp.Function("p")(x), sp.Function("q1")(x)
    phi = sp.exp(-(x**2) / 2) / sp.sqrt(2 * sp.pi)
    X, Yo = P / phi, Q / phi
    f, j = -Q - sp.log(P), -P - sp.log(Q)
    exprs = {
        "d": (1 + x * X) ** 2 * f + (1 - x * Yo) ** 2 * j,
        "g": R(1, 2) * (1 - X**2 * f - Yo**2 * j),
        "v": sp.log(X * Yo),
    }

    def flip(e):
        e = e.subs(x, -x)
        return e.subs({sp.Function("p")(-x): Q, sp.Function("q1")(-x): P}, simultaneous=True)

    return {n: sp.simplify(flip(e) - e) == 0 for n, e in exprs.items()}


def check_stable_forms() -> Dict[str, bool]:
    """The stable forms equal the paper's profiles (q1 = 1 - p is a positive symbol in (0, 1))."""
    q1 = sp.Symbol("q1", positive=True)
    phi = sp.Symbol("phi", positive=True)
    xs = sp.Symbol("x", positive=True)
    P = 1 - q1
    X, Yo = P / phi, q1 / phi
    f, j = -q1 - sp.log(P), -P - sp.log(q1)
    paper = {
        "d": (1 + xs * X) ** 2 * f + (1 - xs * Yo) ** 2 * j,
        "g": R(1, 2) * (1 - X**2 * f - Yo**2 * j),
        "v": sp.log(X) + sp.log(Yo),
    }
    sub = {x: xs, p: P, ph: phi, Y: q1 / phi, LY: sp.log(q1) - sp.log(phi), H[0]: (-sp.log(1 - q1) - q1) / q1**2}
    stable = {"d": d_stable, "g": g_stable, "v": v_stable}
    out = {}
    for name, e in stable.items():
        diff = sp.expand_log(sp.expand(e.subs(sub) - paper[name]), force=True)
        # log(phi) = -x^2/2 - log sqrt(2 pi) is what ties the two forms together
        diff = diff.subs(sp.log(phi), -(xs**2) / 2 - _L2PI)
        out[name] = sp.simplify(diff) == 0
    return out


def check_derivative_rules() -> Dict[str, bool]:
    """Y' = xY - 1 and u' = -phi for Y = (1 - p)/phi, u = 1 - p, with p' = phi, phi' = -x phi."""
    P = sp.Function("p")(x)
    phi = sp.exp(-(x**2) / 2) / sp.sqrt(2 * sp.pi)
    Yf = (1 - P) / phi
    dY = sp.diff(Yf, x).subs(sp.Derivative(P, x), phi)
    du = sp.diff(1 - P, x).subs(sp.Derivative(P, x), phi)
    return {"Y' = xY - 1": sp.simplify(dY - (x * Yf - 1)) == 0, "u' = -phi": sp.simplify(du + phi) == 0}


@lru_cache(maxsize=None)
def _lambdas():
    d1, d2 = D(d_stable), D(d_stable, 2)
    base = {"d": d_stable, "d1": d1, "d2": d2, "g": g_stable, "g2": D(g_stable, 2), "v1": D(v_stable)}
    F = {n: sp.lambdify(SYMS, e, modules=IVMODS) for n, e in base.items()}
    FD = {n: sp.lambdify(SYMS, D(e), modules=IVMODS) for n, e in base.items()}
    jets = [d_stable]
    for _ in range(4):
        jets.append(D(jets[-1]))
    vj = [D(v_stable, 2), D(v_stable, 3), D(v_stable, 4)]
    JF = [sp.lambdify(SYMS, e, modules=IVMODS) for e in jets + vj]
    return F, FD, JF


# ---------------------------------------------------------------------------
# Rigorous inputs
# ---------------------------------------------------------------------------


def _erf(T, dps: int):
    """erf on an interval argument T >= 0 by the alternating series with its remainder bound."""
    T2 = T * T
    s, term, n = iv.mpf(0), T, 0
    tmax = float(mp.mpf(T.b))
    while True:
        s += term / (2 * n + 1)
        n += 1
        term = -term * T2 / n
        # past n > t^2 the terms decrease, so the first omitted term bounds the remainder
        if n > tmax * tmax + 2 and float(mp.mpf(abs(term).b)) < 10.0 ** (-dps + 8):
            break
    nxt = abs(term) / (2 * n + 1)
    return 2 / iv.sqrt(iv.pi) * (s + iv.mpf([-nxt.b, nxt.b]))


@lru_cache(maxsize=None)
def point(xx: float):
    """Enclosures of p(x), 1 - p(x), phi(x) at a binary-exact x >= 0."""
    dps = 40 + int(0.6 * xx * xx)
    with ivdps(dps):
        e = _erf(iv.mpf(xx) / iv.sqrt(2), dps)
        return (1 + e) / 2, (1 - e) / 2, iv.exp(-iv.mpf(xx) ** 2 / 2) / iv.sqrt(2 * iv.pi)


def hseries(k: int, y_hi, M: int = 140):
    """Upper/lower enclosure of h_k(y) = k-th derivative of sum_m y^m/(m + 2) at y = y_hi (a point interval or
    an mpf), valid for 0 <= y < M/(M + 1)^... checked: requires ((M+1)/M)^k * y < 1."""
    y = iv.mpf(y_hi)
    total = iv.mpf(0)
    for m in range(k, M):
        coef = 1
        for i in range(k):
            coef *= m - i
        total += iv.mpf(coef) / (m + 2) * y ** (m - k)
    yb = mp.mpf(y.b)
    ratio = (mp.mpf(M + 1) / M) ** k * yb
    if ratio >= 1:
        raise ValueError("h-series tail bound needs a smaller argument")
    tail = mp.mpf(M) ** k * yb ** (M - k) / (1 - ratio)
    return total + iv.mpf([0, tail])


def inputs_point(m: float):
    P, Qv, PH = point(m)
    with ivdps(30):
        Yv = Qv / PH
        return [iv.mpf(m), P, PH, Yv, iv.log(Yv)] + [hseries(k, Qv) for k in range(8)]


def inputs_box(a: float, b: float):
    Pa, Qa, PHa = point(a)
    Pb, Qb, PHb = point(b)
    with ivdps(30):
        uI = iv.mpf([Qb.a, Qa.b])
        Hs = [iv.mpf([hseries(k, mp.mpf(uI.a)).a, hseries(k, mp.mpf(uI.b)).b]) for k in range(8)]
        YI = iv.mpf([(Qb / PHb).a, (Qa / PHa).b])
        return [iv.mpf([a, b]), iv.mpf([Pa.a, Pb.b]), iv.mpf([PHb.a, PHa.b]), YI, iv.log(YI)] + Hs


# ---------------------------------------------------------------------------
# One-variable margins (first bullet)
# ---------------------------------------------------------------------------

FIRST_BULLET = [
    "b - r^2 - d > 0",
    "v' - x <= .319",
    "-(v' - x) <= .319",
    "C <= -.341",
    "S_q > 0",
    "lambda t_-^2 + t_- C + K > 0",
    "lambda t_+^2 + t_+ C + K < 0",
    "2(-.37)C - .37^2 - 4 lambda K > m_*^2",
]


def one_var_margins(a: float, b: float, thresholds: Dict[str, Tuple[int, int]] = None):
    """Interval lower bounds of the first-bullet margins on [a, b] subset [0, inf)."""
    th = {"v": (319, 1000), "C": (-341, 1000), **(thresholds or {})}
    F, FD, _ = _lambdas()
    m = (a + b) / 2
    ip, ib = inputs_point(m), inputs_box(a, b)
    with ivdps(30):
        X = iv.mpf([a, b])
        half = iv.mpf([-(b - a) / 2, (b - a) / 2])
        bv = {n: F[n](*ip) + FD[n](*ib) * half for n in F}
        b_, c_, r_, aR = _c("b"), _c("c"), _c("r"), _c("aR")
        lam, tm, tp, ms = _c("lam"), _c("tm"), _c("tp"), _c("ms")
        k = iv.sqrt(b_ - c_)
        s = b_ - r_ * r_ - bv["d"]
        rs = iv.sqrt(s)
        q = k - rs
        q1 = bv["d1"] / (2 * rs)
        q2 = bv["d2"] / (2 * rs) + bv["d1"] * bv["d1"] / (4 * s * rs)
        Sq = 2 * q + X * q1 - q2
        K = bv["d"] - 2 * bv["g"]
        C = -bv["d"] + (aR - 1) * bv["g2"]
        tv, tC = iv.mpf(th["v"][0]) / th["v"][1], iv.mpf(th["C"][0]) / th["C"][1]
        a37 = iv.mpf(37) / 100
        vals = [
            s,
            tv - (bv["v1"] - X),
            tv + (bv["v1"] - X),
            tC - C,
            Sq,
            lam * tm * tm + tm * C + K,
            -(lam * tp * tp + tp * C + K),
            -2 * a37 * C - a37 * a37 - 4 * lam * K - ms * ms,
        ]
    return dict(zip(FIRST_BULLET, vals))


def verify_1d(lo: float, hi: float, n0: int, max_depth: int = 40, thresholds=None) -> Dict[str, Any]:
    st: Dict[str, Any] = {
        "range": [lo, hi],
        "certified_boxes": 0,
        "evaluations": 0,
        "min_lower_bound": {},
        "uncertified": [],
    }
    stack = [(lo + (hi - lo) * i / n0, lo + (hi - lo) * (i + 1) / n0, 0) for i in range(n0)][::-1]
    while stack:
        a, b, depth = stack.pop()
        st["evaluations"] += 1
        try:
            vals = one_var_margins(a, b, thresholds)
            ok = all(v.a > 0 for v in vals.values())
        except (ValueError, ZeroDivisionError, mp.libmp.libmpf.ComplexResult):
            vals, ok = None, False
        if ok:
            st["certified_boxes"] += 1
            for n, v in vals.items():
                st["min_lower_bound"][n] = min(st["min_lower_bound"].get(n, 1e9), float(mp.mpf(v.a)))
            continue
        if depth >= max_depth:
            st["uncertified"].append([a, b])
            continue
        mid = (a + b) / 2
        stack += [(mid, b, depth + 1), (a, mid, depth + 1)]
    st["verified"] = not st["uncertified"]
    return st


# ---------------------------------------------------------------------------
# Two-variable inequalities (3)
# ---------------------------------------------------------------------------

_A = sp.Symbol("A")  # asinh(x/s), A' = 1/sqrt(s^2 + x^2)


def _pi_lambdas():
    Af = sp.Function("Af")(x)
    s_ = R(36, 10)

    def Dx(e, n=1):
        for _ in range(n):
            e = sp.diff(e, x).subs(sp.Derivative(Af, x), 1 / sp.sqrt(s_**2 + x**2))
        return e

    w_, r_ = R(46, 10), R(22, 100)
    p1, p2 = r_ * sp.cos(w_ * Af), r_ * sp.sin(w_ * Af)
    S = lambda e: 2 * e + x * Dx(e) - Dx(e, 2)  # noqa: E731
    pis = {"p1": p1, "p2": p2, "Sp1": S(p1), "Sp2": S(p2)}
    lam = lambda e: sp.lambdify([x, _A], e.subs(Af, _A), modules=IVMODS)  # noqa: E731
    return {n: lam(e) for n, e in pis.items()}, {n: lam(Dx(e)) for n, e in pis.items()}


_PI = None


def _asinh(T):
    if T.a >= 0:
        return iv.log(T + iv.sqrt(T * T + 1))
    if T.b <= 0:
        U = -T
        return -iv.log(U + iv.sqrt(U * U + 1))
    raise ValueError("box straddles 0")


def _lohi(val) -> Tuple[float, float]:
    return np.nextafter(float(mp.mpf(val.a)), -np.inf), np.nextafter(float(mp.mpf(val.b)), np.inf)


@lru_cache(maxsize=None)
def _q_lambdas():
    D0, D1, D2, D3, D4 = sp.symbols("D0:5", real=True)
    b_, c_, r_ = R(602, 1000), R(365, 1000), R(22, 100)
    qe = sp.sqrt(b_ - c_) - sp.sqrt(b_ - r_**2 - D0)
    chain = {D0: D1, D1: D2, D2: D3, D3: D4}

    def Dj(e):
        return sp.diff(e, x) + sum(sp.diff(e, s) * ds for s, ds in chain.items())

    Sqe = 2 * qe + x * Dj(qe) - Dj(Dj(qe))
    JS = [x, D0, D1, D2, D3, D4]
    lf = lambda e: sp.lambdify(JS, e, modules=IVMODS)  # noqa: E731
    return [lf(qe), lf(Dj(qe)), lf(Dj(Dj(qe)))], [lf(Sqe), lf(Dj(Sqe)), lf(Dj(Dj(Sqe)))]


@lru_cache(maxsize=None)
def even_enclosures(a: float, b: float) -> Dict[str, Tuple[float, float]]:
    """Second-order Taylor enclosures of q, S_q, v'' on [a, b] subset [0, inf)."""
    _, _, JF = _lambdas()
    QL, SL = _q_lambdas()
    m = (a + b) / 2
    ip, ib = inputs_point(m), inputs_box(a, b)
    with ivdps(30):
        jp, jb = [f(*ip) for f in JF], [f(*ib) for f in JF]
        M, X = iv.mpf(m), iv.mpf([a, b])
        half = iv.mpf([-(b - a) / 2, (b - a) / 2])
        h2 = iv.mpf([0, ((b - a) / 2) ** 2]) / 2
        q = QL[0](M, *jp[:5]) + QL[1](M, *jp[:5]) * half + QL[2](X, *jb[:5]) * h2
        Sq = SL[0](M, *jp[:5]) + SL[1](M, *jp[:5]) * half + SL[2](X, *jb[:5]) * h2
        v2 = jp[5] + jp[6] * half + jb[7] * h2
    return {"q": _lohi(q), "Sq": _lohi(Sq), "v2": _lohi(v2)}


@lru_cache(maxsize=None)
def pi_enclosures(a: float, b: float) -> Dict[str, Tuple[float, float]]:
    global _PI
    if _PI is None:
        _PI = _pi_lambdas()
    PF, PFD = _PI
    with ivdps(30):
        m = (a + b) / 2
        M, X = iv.mpf(m), iv.mpf([a, b])
        half = iv.mpf([-(b - a) / 2, (b - a) / 2])
        s = _c("s")
        Am, AX = _asinh(M / s), _asinh(X / s)
        return {n: _lohi(PF[n](M, Am) + PFD[n](X, AX) * half) for n in PF}


@lru_cache(maxsize=None)
def enclosures(a: float, b: float):
    ev = even_enclosures(abs(b), abs(a)) if b <= 0 else even_enclosures(a, b)
    return {**ev, **pi_enclosures(a, b)}


# float interval arithmetic, one ulp outward per operation (IEEE round-to-nearest errs by at most half an ulp)
def _out(lo, hi):
    return np.nextafter(lo, -np.inf), np.nextafter(hi, np.inf)


def _add(A, B):
    return _out(A[0] + B[0], A[1] + B[1])


def _sub(A, B):
    return _out(A[0] - B[1], A[1] - B[0])


def _mul(A, B):
    c = [A[0] * B[0], A[0] * B[1], A[1] * B[0], A[1] * B[1]]
    return _out(min(c), max(c))


def _sq(A):
    lo = 0.0 if A[0] <= 0 <= A[1] else min(A[0] ** 2, A[1] ** 2)
    return _out(lo, max(A[0] ** 2, A[1] ** 2))


@lru_cache(maxsize=None)
def _consts():
    with ivdps(40):
        b, c, eta, kap = _c("b"), _c("c"), _c("eta"), _c("kappa")
        tm, tp, tc, tr = _c("tm"), _c("tp"), _c("tc"), _c("tr")
        e0, alpha, hs = _c("e0"), _c("alpha"), _c("hs")
        bm = (1 + tp) * (b - 3 * eta) / (3 * (3 * (b + eta) - 4 * c))
        out = {
            "k": iv.sqrt(b - c),
            "4c": 4 * c,
            "2kap": 2 * kap,
            "tc": tc,
            "tr/2": tr / 2,
            "hs": hs,
            "1/hs": 1 / hs,
            "rhs0": 2 * (b + eta + (b + eta - kap) * tm) + 2 * e0 * (2 * tr) ** 2,
            "2bm": 2 * bm,
            "1/alpha": 1 / alpha,
            "2": iv.mpf(2),
            "4": iv.mpf(4),
        }
        return {k: _lohi(v) for k, v in out.items()}


def two_var_margins(zbox, xbox) -> Tuple[float, float]:
    """Lower bounds of the two inequalities (3) on the box zbox x xbox."""
    Z, X = enclosures(*zbox), enclosures(*xbox)
    K = _consts()
    q, Sqx, v2, Sqz = X["q"], X["Sq"], X["v2"], Z["Sq"]
    Hv = _add(_add(K["4c"], _mul(K["4"], _mul(K["k"], q))), _mul(K["2"], _mul(_sub(K["k"], q), Sqz)))
    Hv = _sub(Hv, _mul(K["2"], _add(_mul(Z["Sp1"], X["p1"]), _mul(Z["Sp2"], X["p2"]))))
    H0 = _sub(_add(Hv, v2), K["2kap"])
    H02 = _sq(H0)
    lhs = _sub(_add(Hv, _mul(K["tc"], H0)), _mul(K["tr/2"], _add(K["hs"], _mul(K["1/hs"], H02))))
    rhs = _add(_add(K["rhs0"], _mul(K["2bm"], _mul(Sqz, Sqx))), _mul(K["1/alpha"], H02))
    m1 = _sub(lhs, rhs)
    m2 = _sub(
        _add(K["4c"], _mul(_mul(K["2"], K["k"]), _add(Sqz, Sqx))),
        _add(_mul(Sqz, Sqx), _add(_mul(Z["Sp1"], X["Sp1"]), _mul(Z["Sp2"], X["Sp2"]))),
    )
    return float(m1[0]), float(m2[0])


def verify_2d(W: float, n0: int, max_depth: int = 14, z_range: Tuple[int, int] = None) -> Dict[str, Any]:
    """(3) on z in [0, W], x in [-W, W]; (z, x) -> (-z, -x) leaves (3) unchanged, which covers z < 0.

    `z_range` = (i, j) restricts z to the initial boxes i..j-1, so the window can be split across processes."""
    edges = [W * i / n0 for i in range(n0 + 1)]
    all_boxes = list(zip(edges[:-1], edges[1:]))
    xboxes = [(-b, -a) for a, b in all_boxes[::-1]] + all_boxes
    zboxes = all_boxes[slice(*(z_range or (0, n0)))]
    stack = [(zb, xb, 0) for zb in zboxes for xb in xboxes]
    st: Dict[str, Any] = {
        "window": W,
        "certified_pairs": 0,
        "evaluations": 0,
        "min_lower_bound": [np.inf, np.inf],
        "uncertified": [],
    }
    while stack:
        zb, xb, depth = stack.pop()
        st["evaluations"] += 1
        try:
            m1, m2 = two_var_margins(zb, xb)
        except (ValueError, ZeroDivisionError, mp.libmp.libmpf.ComplexResult):
            m1 = m2 = -np.inf
        if m1 > 0 and m2 > 0:
            st["certified_pairs"] += 1
            st["min_lower_bound"] = [min(st["min_lower_bound"][0], m1), min(st["min_lower_bound"][1], m2)]
            continue
        if depth >= max_depth:
            st["uncertified"].append([list(zb), list(xb)])
            continue
        zm, xm = (zb[0] + zb[1]) / 2, (xb[0] + xb[1]) / 2
        for z2 in ((zb[0], zm), (zm, zb[1])):
            for x2 in ((xb[0], xm), (xm, xb[1])):
                stack.append((z2, x2, depth + 1))
    st["verified"] = not st["uncertified"]
    st["min_lower_bound"] = [float(v) for v in st["min_lower_bound"]]
    return st


def symbolic_checks() -> List[Tuple[str, bool]]:
    out = [(f"even: {k}", v) for k, v in check_evenness().items()]
    out += [(f"stable form: {k}", v) for k, v in check_stable_forms().items()]
    out += [(f"derivative rule: {k}", v) for k, v in check_derivative_rules().items()]
    return out
