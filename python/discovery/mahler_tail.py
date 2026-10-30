"""
python/discovery/mahler_tail.py - Rigorous proof of the first-bullet scalar inequalities of the general Mahler paper
(prop:scalar-input) on the unbounded tail x >= X0 = 8, ADR-DISCOVERY-076.

Together with mahler_interval.py (|x| <= 8) and evenness this covers every real x.

Method. Put t = 1/x in (0, T], T = 1/X0.

1. Mills ratio. Y(x) = int_0^inf exp(-x s) exp(-s^2/2) ds. For y >= 0 the Taylor remainder of exp(-y) after n terms
   has the sign (-1)^n and modulus <= y^n/n!. Integrating term by term (int_0^inf s^{2k} e^{-xs} ds = (2k)!/x^{2k+1}):
       Psi := xY = sum_{k<n} (-1)^k (2k-1)!! t^{2k} + theta (-1)^n (2n-1)!! t^{2n},   theta in [0, 1].
2. Exponentially small parts. phi x^K is decreasing for x^2 > K, so phi = w t^K with w in [0, phi(X0) X0^K];
   u = 1 - p = phi Y; h_k(u) lies between h_k(0) and h_k(u(X0)).
3. Laurent-Taylor models. Each quantity is sum_e c_e t^e + R t^m with exact rational c_e for the parts that must
   cancel (negative powers of t cancel exactly), interval c_e for uncertain parts, and an interval R valid for all
   t in [0, T]. log Y = log t + log Psi; log t enters linearly and t^e log t is monotone on (0, T] for e >= 1.
4. Each margin is enclosed on boxes [t1, t2] covering [0, T] and certified when its lower bound is positive.

Trust base: mpmath interval arithmetic and Python's exact rationals.
"""

from __future__ import annotations

from contextlib import contextmanager
from fractions import Fraction
from functools import lru_cache
from typing import Any, Dict, List, Tuple

import mpmath as mp
import sympy as sp

from python.discovery import mahler_interval as mi

iv = mp.iv

X0 = 8
T = Fraction(1, X0)
NMILLS = 10  # terms of the Mills series; remainder ~ (2n-1)!! t^{2n}
KPHI = 40  # phi = w t^K, valid since X0^2 = 64 > K
NTRUNC = 24  # Laurent terms of order >= NTRUNC go into the remainder
DEFAULT = (8, 10, 40, 24)


def configure(x0: int, nmills: int, kphi: int, ntrunc: int) -> None:
    """Choose the tail start X0 and the model orders; requires X0^2 > K (phi x^K decreasing) and 2n < NTRUNC."""
    global X0, T, NMILLS, KPHI, NTRUNC
    if x0 * x0 <= kphi or 2 * nmills >= ntrunc:
        raise ValueError("need X0^2 > K and 2 n < NTRUNC")
    X0, T, NMILLS, KPHI, NTRUNC = x0, Fraction(1, x0), nmills, kphi, ntrunc
    inputs.cache_clear()
    base_models.cache_clear()


@contextmanager
def tail_config(x0: int, nmills: int, kphi: int, ntrunc: int):
    old = (X0, NMILLS, KPHI, NTRUNC)
    configure(x0, nmills, kphi, ntrunc)
    try:
        yield
    finally:
        configure(*old)


def _iv(v) -> Any:
    if isinstance(v, Fraction):
        return iv.mpf(v.numerator) / v.denominator
    return v


def _hull_with_zero(v):
    v = _iv(v)
    return iv.mpf([min(v.a, 0), max(v.b, 0)])


class LTM:
    """Laurent-Taylor model on t in [0, T]: sum c_e t^e + rem * t^m."""

    __slots__ = ("terms", "rem", "m")

    def __init__(self, terms=None, rem=None, m: int = NTRUNC):
        self.terms: Dict[int, Any] = {}
        pieces: List[Tuple[int, Any]] = []
        for e, c in (terms or {}).items():
            if isinstance(c, Fraction) and c == 0:
                continue
            if e >= NTRUNC:
                pieces.append((e, c))
            else:
                self.terms[e] = c
        self.rem, self.m = _combine(pieces + ([(m, rem)] if rem is not None else []))

    @staticmethod
    def const(c) -> "LTM":
        return LTM({0: c if isinstance(c, Fraction) else c})

    def __add__(self, other):
        other = _lift(other)
        terms = dict(self.terms)
        for e, c in other.terms.items():
            terms[e] = _addc(terms[e], c) if e in terms else c
        out = LTM(terms)
        out.rem, out.m = _combine(_rem_pieces(self) + _rem_pieces(other) + _rem_pieces(out))
        return out

    __radd__ = __add__

    def __neg__(self):
        out = LTM({e: -c for e, c in self.terms.items()})
        out.rem, out.m = (None, NTRUNC) if self.rem is None else (-self.rem, self.m)
        return out

    def __sub__(self, other):
        return self + (-_lift(other))

    def __rsub__(self, other):
        return _lift(other) - self

    def __mul__(self, other):
        other = _lift(other)
        terms: Dict[int, Any] = {}
        for e1, c1 in self.terms.items():
            for e2, c2 in other.terms.items():
                e, c = e1 + e2, _mulc(c1, c2)
                terms[e] = _addc(terms[e], c) if e in terms else c
        out = LTM(terms)
        pieces = _rem_pieces(out)
        if self.rem is not None:
            pieces += [(self.m + e, _mulc(self.rem, c)) for e, c in other.terms.items()]
        if other.rem is not None:
            pieces += [(other.m + e, _mulc(other.rem, c)) for e, c in self.terms.items()]
        if self.rem is not None and other.rem is not None:
            pieces.append((self.m + other.m, self.rem * other.rem))
        out.rem, out.m = _combine(pieces)
        return out

    __rmul__ = __mul__

    def __pow__(self, n: int):
        if n < 0:
            raise ValueError("use an explicit inverse")
        out = LTM.const(Fraction(1))
        for _ in range(n):
            out = out * self
        return out

    def min_exponent(self) -> int:
        es = [e for e, c in self.terms.items() if not (isinstance(c, Fraction) and c == 0)]
        return min(es) if es else NTRUNC

    def evaluate(self, t1: Fraction, t2: Fraction):
        """Enclosure on [t1, t2] subset [0, T]."""
        with mi.ivdps(40):
            tI = iv.mpf([_iv(t1).a, _iv(t2).b])
            total = iv.mpf(0)
            for e, c in self.terms.items():
                if e < 0:
                    if t1 == 0:
                        raise ValueError(f"negative power t^{e} survives near t = 0")
                    total += _iv(c) * (1 / tI) ** (-e)
                else:
                    total += _iv(c) * tI**e
            if self.rem is not None:
                if self.m < 0:
                    raise ValueError("negative remainder order")
                total += self.rem * tI**self.m
            return total


def _addc(a, b):
    if isinstance(a, Fraction) and isinstance(b, Fraction):
        return a + b
    return _iv(a) + _iv(b)


def _mulc(a, b):
    if isinstance(a, Fraction) and isinstance(b, Fraction):
        return a * b
    return _iv(a) * _iv(b)


def _lift(v) -> LTM:
    if isinstance(v, LTM):
        return v
    if isinstance(v, int):
        v = Fraction(v)
    return LTM.const(v)


def _rem_pieces(z: LTM) -> List[Tuple[int, Any]]:
    return [] if z.rem is None else [(z.m, z.rem)]


def _combine(pieces: List[Tuple[int, Any]]):
    """Sum c_i t^{e_i} over t in [0, T] as R t^m with m = min e_i: t^{e_i - m} lies in [0, T^{e_i - m}]."""
    pieces = [(e, c) for e, c in pieces if not (isinstance(c, Fraction) and c == 0)]
    if not pieces:
        return None, NTRUNC
    m = min(e for e, _ in pieces)
    R = iv.mpf(0)
    with mi.ivdps(40):
        for e, c in pieces:
            if e == m:
                R += _iv(c)
            else:
                R += _hull_with_zero(_iv(c) * _iv(T) ** (e - m))
    return R, m


# ---------------------------------------------------------------------------
# Inputs as Laurent-Taylor models
# ---------------------------------------------------------------------------


def _double_factorial_odd(k: int) -> int:
    out = 1
    for i in range(1, 2 * k, 2):
        out *= i
    return out


@lru_cache(maxsize=None)
def inputs() -> Dict[str, Any]:
    t = LTM({1: Fraction(1)})
    x = LTM({-1: Fraction(1)})
    c_n = (-1) ** NMILLS * _double_factorial_odd(NMILLS)
    Psi = LTM(
        {2 * k: Fraction((-1) ** k * _double_factorial_odd(k)) for k in range(NMILLS)},
        rem=_hull_with_zero(Fraction(c_n)),
        m=2 * NMILLS,
    )
    e = 1 - Psi  # 1 - xY, starts at t^2
    # bound of e on [0, T] for the geometric and log remainders
    eI = e.evaluate(Fraction(0), T)
    emax = max(abs(eI.a), abs(eI.b))
    M = 12
    inv = LTM.const(Fraction(1))
    ek = LTM.const(Fraction(1))
    for _ in range(1, M):
        ek = ek * e
        inv = inv + ek
    with mi.ivdps(40):
        tail = iv.mpf([1 / (1 + iv.mpf(emax)), 1 / (1 - iv.mpf(emax))]).b
    # 1/Psi = sum_{k<M} e^k + e^M/(1 - e), and 1/(1 - e) lies in [0, 1/(1 - |e|max)]
    inv = inv + (ek * e) * LTM.const(iv.mpf([0, tail]))
    logPsi = LTM.const(Fraction(0))
    ek = LTM.const(Fraction(1))
    for k in range(1, M):
        ek = ek * e
        logPsi = logPsi - ek * LTM.const(Fraction(1, k))
    # log(1 - e) = -sum_{k<M} e^k/k - e^M rho with |rho| <= 1/(M (1 - |e|))
    with mi.ivdps(40):
        rho = (1 / (M * (1 - iv.mpf(emax)))).b
    logPsi = logPsi + (ek * e) * LTM.const(iv.mpf([-rho, rho]))
    P8, Q8, PH8 = mi.point(float(X0))
    with mi.ivdps(40):
        wmax = PH8 * iv.mpf(X0) ** KPHI
        w = iv.mpf([0, wmax.b])
        umax = Q8.b
    ph = LTM({KPHI: w})
    Y = t * Psi
    u = ph * Y
    p = 1 - u
    # h_k(u) = h_k(0) + u * Delta_k with h_k(0) = k!/(k+2) exact and Delta_k between h_{k+1}(0) and h_{k+1}(umax)
    # (mean value theorem; h_{k+1} is increasing). The exact part cancels; the rest is O(t^{K+1}).
    H = []
    for k in range(8):
        h0k = Fraction(int(sp.factorial(k)), k + 2)
        dk = iv.mpf([mi.hseries(k + 1, mp.mpf(0)).a, mi.hseries(k + 1, mp.mpf(umax)).b])
        H.append(LTM.const(h0k) + u * LTM.const(dk))
    return {
        "t": t,
        "x": x,
        "Psi": Psi,
        "e": e,
        "invPsi": inv,
        "logPsi": logPsi,
        "ph": ph,
        "Y": Y,
        "p": p,
        "u": u,
        "H": H,
        "umax": umax,
    }


def to_ltm(expr: sp.Expr, env: Dict[sp.Symbol, LTM]) -> LTM:
    """Evaluate a SymPy expression (polynomial in the stable variables, Y^-1 allowed) as an LTM."""
    if expr.is_Add:
        out = LTM.const(Fraction(0))
        for a in expr.args:
            out = out + to_ltm(a, env)
        return out
    if expr.is_Mul:
        out = LTM.const(Fraction(1))
        for a in expr.args:
            out = out * to_ltm(a, env)
        return out
    if expr.is_Pow:
        base, n = expr.args
        if not n.is_Integer:
            raise ValueError(f"non-integer power {expr}")
        n = int(n)
        if n >= 0:
            return to_ltm(base, env) ** n
        if base == mi.Y:
            return env["invY"] ** (-n)
        if base == mi.p:
            return env["invp"] ** (-n)
        raise ValueError(f"unsupported inverse {expr}")
    if expr.is_Symbol:
        return env[expr]
    if expr.is_Rational:
        return LTM.const(Fraction(int(expr.p), int(expr.q)))
    if expr.free_symbols:
        raise ValueError(f"unsupported node {expr}")
    with mi.ivdps(40):
        val = sp.lambdify([], expr, modules=mi.IVMODS)()
    return LTM.const(val)


_L2, _LPI = sp.symbols("Llog2 Llogpi")


def _split_log(expr: sp.Expr):
    """Coefficients of expr as a polynomial in (LY, log 2, log pi). Every coefficient is a rational-coefficient
    expression in the stable variables, so its Laurent model is exact and negative powers cancel exactly."""
    expr = sp.expand(sp.expand_log(sp.expand(expr), force=True))
    expr = expr.subs({sp.log(2): _L2, sp.log(sp.pi): _LPI})
    poly = sp.Poly(expr, mi.LY, _L2, _LPI)
    if poly.total_degree() > 1:
        raise ValueError("logarithms appear nonlinearly")
    return {mono: coef for mono, coef in zip(poly.monoms(), poly.coeffs())}


@lru_cache(maxsize=None)
def base_models() -> Dict[str, Tuple[LTM, LTM]]:
    """(E0 + log Psi E1, E1) for d, d1, d2, g, g2, so that f = A + log(t) B."""
    inp = inputs()
    with mi.ivdps(40):
        invp_rho = iv.mpf([1, (1 / (1 - iv.mpf(inp["umax"]))).b])
    # 1/p = 1/(1 - u) = 1 + u * (1/(1 - u)), and 1/(1 - u) lies in [1, 1/(1 - umax)]
    invp_model = 1 + inp["u"] * LTM.const(invp_rho)
    env = {
        mi.x: inp["x"],
        mi.p: inp["p"],
        mi.ph: inp["ph"],
        mi.Y: inp["Y"],
        "invY": inp["x"] * inp["invPsi"],
        "invp": invp_model,
    }
    for k in range(8):
        env[mi.H[k]] = inp["H"][k]
    d, g = mi.d_stable, mi.g_stable
    exprs = {
        "d": d,
        "d1": mi.D(d),
        "d2": mi.D(d, 2),
        "g": g,
        "g1": mi.D(g),
        "g2": mi.D(g, 2),
        "g3": mi.D(g, 3),
        "g4": mi.D(g, 4),
        "v2": mi.D(mi.v_stable, 2),
    }
    out = {}
    with mi.ivdps(40):
        log2, logpi = iv.log(iv.mpf(2)), iv.log(iv.pi)
    for n, e in exprs.items():
        A, B = LTM.const(Fraction(0)), LTM.const(Fraction(0))
        for (aY, a2, api), coef in _split_log(e).items():
            model = to_ltm(coef, env)  # exact cancellation happens here
            if a2:
                model = model * LTM.const(log2)
            if api:
                model = model * LTM.const(logpi)
            if aY:
                B = B + model
            else:
                A = A + model
        out[n] = (A + inp["logPsi"] * B, B)
    # x*d1 (needed in S_q = 2q + x q' - q'') as a model, so the 1/t factor cancels inside the model
    A, B = out["d1"]
    out["xd1"] = (inp["x"] * A, inp["x"] * B)
    # v' - x = phi/p + (Psi - 1)/(t Psi)
    with mi.ivdps(40):
        invp = iv.mpf([1, (1 / (1 - iv.mpf(inp["umax"]))).b])
    vmx = inp["ph"] * LTM.const(invp) - inp["x"] * inp["e"] * inp["invPsi"]
    out["v1mx"] = (vmx, LTM.const(Fraction(0)))
    return out


def _tlog_term(c, e: int, t1: Fraction, t2: Fraction):
    """c t^e log t on [t1, t2], e >= 1: t^e log t is decreasing on (0, e^{-1/e}), which contains (0, T]."""
    if e < 1:
        raise ValueError("log t needs a positive power")
    with mi.ivdps(40):

        def f(tt):
            return iv.mpf(0) if tt == 0 else _iv(tt) ** e * iv.log(_iv(tt))

        lo, hi = f(t2), f(t1)  # decreasing
        rng = iv.mpf([lo.a, hi.b])
        return _iv(c) * rng


def evaluate_pair(model: Tuple[LTM, LTM], t1: Fraction, t2: Fraction):
    A, B = model
    total = A.evaluate(t1, t2)
    for e, c in B.terms.items():
        total += _tlog_term(c, e, t1, t2)
    if B.rem is not None:
        # remainder rem * t^m log t
        total += _tlog_term(iv.mpf(1), B.m, t1, t2) * B.rem
    return total


def tail_margins(t1: Fraction, t2: Fraction, thresholds: Dict[str, Tuple[int, int]] = None) -> Dict[str, Any]:
    th = {"v": (319, 1000), "C": (-341, 1000), **(thresholds or {})}
    bm = base_models()
    v = {n: evaluate_pair(m, t1, t2) for n, m in bm.items()}
    with mi.ivdps(40):
        b_, c_, r_, aR = mi._c("b"), mi._c("c"), mi._c("r"), mi._c("aR")
        lam, tm, tp, ms = mi._c("lam"), mi._c("tm"), mi._c("tp"), mi._c("ms")
        k = iv.sqrt(b_ - c_)
        s = b_ - r_ * r_ - v["d"]
        rs = iv.sqrt(s)
        q = k - rs
        xq1 = v["xd1"] / (2 * rs)
        q2 = v["d2"] / (2 * rs) + v["d1"] * v["d1"] / (4 * s * rs)
        Sq = 2 * q + xq1 - q2
        K = v["d"] - 2 * v["g"]
        C = -v["d"] + (aR - 1) * v["g2"]
        tv, tC = iv.mpf(th["v"][0]) / th["v"][1], iv.mpf(th["C"][0]) / th["C"][1]
        a37 = iv.mpf(37) / 100
        vals = [
            s,
            tv - v["v1mx"],
            tv + v["v1mx"],
            tC - C,
            Sq,
            lam * tm * tm + tm * C + K,
            -(lam * tp * tp + tp * C + K),
            -2 * a37 * C - a37 * a37 - 4 * lam * K - ms * ms,
        ]
    return dict(zip(mi.FIRST_BULLET, vals))


def verify_tail(n0: int = 16, max_depth: int = 20, thresholds=None) -> Dict[str, Any]:
    """Certify every first-bullet margin for x >= X0, i.e. t in [0, 1/X0]."""
    st: Dict[str, Any] = {
        "x_from": X0,
        "certified_boxes": 0,
        "evaluations": 0,
        "min_lower_bound": {},
        "uncertified": [],
    }
    stack = [(T * i / n0, T * (i + 1) / n0, 0) for i in range(n0)][::-1]
    while stack:
        t1, t2, depth = stack.pop()
        st["evaluations"] += 1
        try:
            vals = tail_margins(t1, t2, thresholds)
            ok = all(val.a > 0 for val in vals.values())
        except (ValueError, ZeroDivisionError, mp.libmp.libmpf.ComplexResult):
            vals, ok = None, False
        if ok:
            st["certified_boxes"] += 1
            for n, val in vals.items():
                st["min_lower_bound"][n] = min(st["min_lower_bound"].get(n, 1e9), float(mp.mpf(val.a)))
            continue
        if depth >= max_depth:
            st["uncertified"].append([str(t1), str(t2)])
            continue
        mid = (t1 + t2) / 2
        stack += [(mid, t2, depth + 1), (t1, mid, depth + 1)]
    st["verified"] = not st["uncertified"]
    return st
