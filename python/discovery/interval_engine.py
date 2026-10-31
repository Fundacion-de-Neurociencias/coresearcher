"""
python/discovery/interval_engine.py - Case-independent building blocks for rigorous interval proofs, ADR-DISCOVERY-076.

- `TaylorModel`: a univariate polynomial with exact rational coefficients plus an interval remainder R h^m, valid for
  h in [0, H]. Cancellations between exact coefficients are exact, so quotients such as (1 - cos(wh))/h^2 keep their
  precision as h -> 0. Constructors for cos(a h), sin(a h)/(a h), cosh h, sinh h / h and the reciprocal of 1 + E
  carry explicit remainder bounds.
- `knapsack_average`: the exact range of sum w_k v_k over weights with w_k in [lo_k, hi_k] and sum w_k = 1, with
  each value v_k in [vlo_k, vhi_k]. This bounds an average over a set split into zones whose share of the measure
  is known only up to an interval.
- `branch_and_bound`: a generic driver over boxes with a user-supplied evaluator and splitter.

Trust base: Python's exact rationals and mpmath interval arithmetic. The float knapsack widens its result by an
explicit bound on the float rounding of the sums.
"""

from __future__ import annotations

import math
from fractions import Fraction
from typing import Any, Callable, Dict, List, Optional, Sequence, Tuple

import mpmath as mp
import numpy as np

iv = mp.iv


def _ivq(q) -> Any:
    if isinstance(q, Fraction):
        return iv.mpf(q.numerator) / q.denominator
    return iv.mpf(q)


class TaylorModel:
    """sum_k c_k h^k + R h^m on h in [0, H]; c_k exact Fractions (k < order), R an mpmath interval, m <= order."""

    __slots__ = ("c", "R", "m", "H", "order", "_cache")

    def __init__(self, coeffs: Dict[int, Fraction], H: Fraction, order: int, R=None, m: Optional[int] = None):
        self.H, self.order = Fraction(H), order
        self._cache: Dict[Tuple[float, float], Any] = {}
        self.c: Dict[int, Fraction] = {}
        self.R, self.m = (iv.mpf(0), order) if R is None else (iv.mpf(R), order if m is None else m)
        for k, v in coeffs.items():
            if v != 0:
                self._put(k, Fraction(v))

    def _put(self, k: int, v: Fraction) -> None:
        if k < self.order:
            self.c[k] = self.c.get(k, Fraction(0)) + v
            if self.c[k] == 0:
                del self.c[k]
        else:
            self._fold(k, _ivq(v))

    def _fold(self, k: int, R) -> None:
        """Add R h^k (k >= m or k >= order) to the remainder R h^m, using h^k <= H^(k - m) h^m on [0, H]."""
        if k >= self.m:
            span = iv.mpf([0, 1]) * _ivq(self.H ** (k - self.m))
            self.R = self.R + R * span if k > self.m else self.R + R
        else:  # lower the remainder exponent to k
            span = iv.mpf([0, 1]) * _ivq(self.H ** (self.m - k))
            self.R, self.m = R + self.R * span, k

    def copy(self) -> "TaylorModel":
        out = TaylorModel({}, self.H, self.order)
        out.c, out.R, out.m = dict(self.c), self.R, self.m
        return out

    def __add__(self, other):
        other = self._lift(other)
        out = self.copy()
        for k, v in other.c.items():
            out._put(k, v)
        out._fold(other.m, other.R)
        return out

    __radd__ = __add__

    def __neg__(self):
        out = TaylorModel({k: -v for k, v in self.c.items()}, self.H, self.order)
        out.R, out.m = -self.R, self.m
        return out

    def __sub__(self, other):
        return self + (-self._lift(other))

    def __rsub__(self, other):
        return self._lift(other) - self

    def __mul__(self, other):
        other = self._lift(other)
        out = TaylorModel({}, self.H, self.order)
        for k1, v1 in self.c.items():
            for k2, v2 in other.c.items():
                out._put(k1 + k2, v1 * v2)
        for k, v in other.c.items():
            out._fold(self.m + k, self.R * _ivq(v))
        for k, v in self.c.items():
            out._fold(other.m + k, other.R * _ivq(v))
        out._fold(self.m + other.m, self.R * other.R)
        return out

    __rmul__ = __mul__

    def _lift(self, other) -> "TaylorModel":
        if isinstance(other, TaylorModel):
            if other.H != self.H or other.order != self.order:
                raise ValueError("Taylor models on different domains")
            return other
        return TaylorModel({0: Fraction(other)}, self.H, self.order)

    def min_exponent(self) -> int:
        ks = list(self.c) + ([self.m] if (self.R.a != 0 or self.R.b != 0) else [])
        return min(ks) if ks else self.order

    def shift(self, k: int) -> "TaylorModel":
        """Divide by h^k; every exponent must be >= k."""
        if any(e < k for e in self.c) or self.m < k:
            raise ValueError(f"cannot divide by h^{k}: min exponent {self.min_exponent()}")
        out = TaylorModel({e - k: v for e, v in self.c.items()}, self.H, self.order)
        out.R, out.m = self.R, self.m - k
        return out

    def evaluate(self, h0, h1):
        """Enclosure on [h0, h1] subset [0, H] (floats or Fractions). The exact part is re-expanded around the
        midpoint (exact rationals) and evaluated by Horner in h - c, which avoids most of the interval dependency."""
        key = (float(h0), float(h1))
        if key in self._cache:
            return self._cache[key]
        a, b = Fraction(h0), Fraction(h1)
        Hb = iv.mpf([_ivq(a).a, _ivq(b).b])
        if a < 0 or b > self.H:
            raise ValueError("outside the model's domain")
        c = Fraction((a + b) / 2).limit_denominator(2**40)
        top = max(self.c) if self.c else 0
        d = [Fraction(0)] * (top + 1)
        for k, v in self.c.items():  # sum_k v (c + delta)^k = sum_j delta^j sum_k v binom(k, j) c^(k - j)
            for j in range(k + 1):
                d[j] += v * math.comb(k, j) * c ** (k - j)
        delta = iv.mpf([_ivq(a - c).a, _ivq(b - c).b])
        val = iv.mpf(0)
        for j in range(top, -1, -1):
            val = val * delta + _ivq(d[j])
        out = val + self.R * Hb**self.m
        self._cache[key] = out
        return out


def _series(coeffs: Dict[int, Fraction], H, order: int, R, m: int) -> TaylorModel:
    return TaylorModel(coeffs, H, order, R, m)


def tm_cos(a: Fraction, H: Fraction, order: int) -> TaylorModel:
    """cos(a h): alternating series; the remainder after degree < N (N even) is at most (a h)^N / N!."""
    N = order if order % 2 == 0 else order + 1
    if (a * H) ** 2 >= (N + 1) * (N + 2):
        raise ValueError("terms not decreasing; raise the order")
    co = {2 * j: Fraction((-1) ** j) * a ** (2 * j) / math.factorial(2 * j) for j in range(N // 2)}
    b = _ivq(a**N / math.factorial(N))
    return _series(co, H, order, iv.mpf([-b.b, b.b]), N)


def tm_sinc(a: Fraction, H: Fraction, order: int) -> TaylorModel:
    """sin(a h)/(a h): alternating; remainder at most (a h)^N / (N + 1)!."""
    N = order if order % 2 == 0 else order + 1
    if (a * H) ** 2 >= (N + 2) * (N + 3):
        raise ValueError("terms not decreasing; raise the order")
    co = {2 * j: Fraction((-1) ** j) * a ** (2 * j) / math.factorial(2 * j + 1) for j in range(N // 2)}
    b = _ivq(a**N / math.factorial(N + 1))
    return _series(co, H, order, iv.mpf([-b.b, b.b]), N)


def tm_cosh(H: Fraction, order: int) -> TaylorModel:
    """cosh h: Lagrange remainder cosh(xi) h^N / N! in [0, cosh(H) h^N / N!] (N even)."""
    N = order if order % 2 == 0 else order + 1
    co = {2 * j: Fraction(1, math.factorial(2 * j)) for j in range(N // 2)}
    ch = iv.cosh(_ivq(H)) if hasattr(iv, "cosh") else (iv.exp(_ivq(H)) + iv.exp(-_ivq(H))) / 2
    return _series(co, H, order, iv.mpf([0, (ch / math.factorial(N)).b]), N)


def tm_shc(H: Fraction, order: int) -> TaylorModel:
    """sinh h / h = sum h^(2j)/(2j+1)!; tail <= h^N/(N+1)! * 1/(1 - H^2/((N+2)(N+3)))."""
    N = order if order % 2 == 0 else order + 1
    co = {2 * j: Fraction(1, math.factorial(2 * j + 1)) for j in range(N // 2)}
    q = Fraction(H * H, (N + 2) * (N + 3))
    return _series(co, H, order, iv.mpf([0, _ivq(Fraction(1, math.factorial(N + 1)) / (1 - q)).b]), N)


def tm_reciprocal_one_plus(E: TaylorModel, n: int) -> TaylorModel:
    """1/(1 + E) for a model E >= 0 with E = O(h^2): sum_{k<n} (-E)^k + (-E)^n/(1 + E). The last term lies between
    0 and E^n with the sign of (-1)^n, and E^n <= (e h^2)^n where e bounds E/h^2 on the domain. E must have
    nonnegative coefficients and remainder (then E >= 0 and E/h^2 <= its value at H)."""
    if any(v < 0 for v in E.c.values()) or E.R.a < 0 or E.min_exponent() < 2:
        raise ValueError("E needs nonnegative coefficients and remainder and E = O(h^2)")
    e = E.shift(2).evaluate(E.H, E.H)
    out = TaylorModel({0: Fraction(1)}, E.H, E.order)
    p = TaylorModel({0: Fraction(1)}, E.H, E.order)
    for _ in range(1, n):
        p = p * (-E)
        out = out + p
    b = iv.mpf(e.b) ** n
    R = iv.mpf([0, b.b]) if n % 2 == 0 else iv.mpf([-b.b, 0])
    out._fold(2 * n, R)
    return out


def knapsack_average(w_lo, w_hi, v_lo, v_hi) -> Tuple[float, float]:
    """Range of sum w_k v_k over w_lo <= w <= w_hi, sum w = 1 (exact LP solution, greedy), widened for rounding."""
    w_lo, w_hi = np.maximum(w_lo, 0.0), np.minimum(w_hi, 1.0)
    if w_lo.sum() > 1 + 1e-12 or w_hi.sum() < 1 - 1e-12:
        raise ValueError("infeasible weights")
    rest = max(0.0, 1.0 - float(w_lo.sum()))
    cap = w_hi - w_lo

    def best(vals, sign):
        order = np.argsort(-sign * vals)
        take = np.minimum(cap[order], np.maximum(0.0, rest - np.concatenate([[0.0], np.cumsum(cap[order])[:-1]])))
        return float(np.dot(w_lo, vals) + np.dot(take, vals[order]))

    hi, lo = best(v_hi, 1), best(v_lo, -1)
    pad = 1e-12 * (float(np.dot(w_hi, np.abs(v_hi))) + float(np.dot(w_hi, np.abs(v_lo)))) + 1e-300
    return lo - pad, hi + pad


def branch_and_bound(
    boxes: Sequence[Any],
    evaluate: Callable[[Any], Optional[float]],
    split: Callable[[Any], List[Any]],
    skip: Callable[[Any], bool] = lambda b: False,
    max_depth: int = 30,
    max_boxes: int = 10**7,
) -> Dict[str, Any]:
    """Certify every box: `evaluate` returns a certified lower bound (> 0 certifies) or None; failing boxes are
    split until `max_depth`. `skip` marks boxes covered elsewhere."""
    stack = [(b, 0) for b in reversed(list(boxes))]
    st: Dict[str, Any] = {"certified": 0, "skipped": 0, "evaluations": 0, "min_lower_bound": math.inf, "failed": []}
    while stack:
        box, depth = stack.pop()
        if skip(box):
            st["skipped"] += 1
            continue
        st["evaluations"] += 1
        if st["evaluations"] > max_boxes:
            st["failed"].append(("budget", box))
            break
        lb = evaluate(box)
        if lb is not None and lb > 0:
            st["certified"] += 1
            st["min_lower_bound"] = min(st["min_lower_bound"], lb)
            continue
        if depth >= max_depth:
            st["failed"].append((lb, box))
            continue
        stack += [(b, depth + 1) for b in reversed(split(box))]
    st["verified"] = not st["failed"]
    return st
