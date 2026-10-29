"""
python/discovery/mahler_obligations.py - Obligation ledger pilot: the scalar input of "The Mahler Conjecture for General
Convex Bodies" (openai/math, September 22, 2026), ADR-DISCOVERY-076.

The released reasoning summary for this result (family 087, Part III) ends conditional on "uniform scalar
inequalities". In the manuscript these are Proposition "Scalar inequalities" (prop:scalar-input, Section 1) together
with Lemma "Profile identities" (lem:profile-identities). They involve only fixed one-variable profiles built from the
Gaussian distribution function and fixed parameters, independent of the body and the dimension. The authors certify
them with appendices and with their own programs (verification/), which this module deliberately does not run: the
checks below are re-implemented from the statements, so that they are independent of the authors' code.

What is checked here:
- the three profile identities, symbolically, for any p with p' = phi (DISCHARGED_SYMBOLIC);
- every pointwise and segment inequality of the proposition, numerically at high precision on bounded ranges
  (CHECKED_NUMERIC, with the range, resolution and smallest margin recorded). That is evidence, not a proof: the
  unbounded tails and the continuum between grid points rest on the authors' appendices.
"""

from __future__ import annotations

from functools import lru_cache
from typing import Any, Callable, Dict, List, Tuple

import mpmath as mp
import numpy as np
import sympy as sp

from python.discovery.obligation_ledger import Claim, Discharge, Obligation, Status

SOURCE = {
    "repository": "https://github.com/openai/math",
    "commit": "7ef5c0cc5ca4b0e072b7a050fca09ab24bc6fa3a",
    "paper": "preprints/The-Mahler-Conjecture-for-General-Convex-Bodies-September-22-2026/paper.pdf",
    "statements": "build/sections/01-cones.tex (lem:profile-identities, prop:scalar-input)",
    "author_programs": "verification/programs/*.py (not run here, by design)",
    "lean": "not formalized; the Comparator targets in family 087 cover the symmetric case and its equality "
    "classification only (symmetric_mahler, symmetric_mahler_equality)",
}

R = sp.Rational
PARAMS = {
    "b": R(602, 1000),
    "c": R(365, 1000),
    "r": R(22, 100),
    "w": R(46, 10),
    "s": R(36, 10),
    "eta": R(22, 1000),
    "kappa": R(116, 100),
    "lambda": R(65, 100),
    "a_R": R(75, 10),
    "t_minus": R(-22, 1000),
    "t_plus": R(64, 1000),
    "t_c": R(21, 1000),
    "t_r": R(43, 1000),
    "m_star": R(352, 1000),
}

x = sp.Symbol("x", real=True)
_P = sp.Function("p")(x)  # Gaussian distribution function
_Q = sp.Function("q1")(x)  # its complement 1 - p, kept separate to avoid cancellation
_PHI = sp.exp(-(x**2) / 2) / sp.sqrt(2 * sp.pi)


def _D(e: sp.Expr, k: int = 1) -> sp.Expr:
    for _ in range(k):
        e = sp.diff(e, x).subs({sp.Derivative(_P, x): _PHI, sp.Derivative(_Q, x): -_PHI})
    return e


def _N(e: sp.Expr) -> sp.Expr:
    return x * _D(e) - _D(e, 2)


@lru_cache(maxsize=None)
def profiles() -> Dict[str, sp.Expr]:
    """The paper's profiles d, g, v and the derived quantities, in terms of p and 1 - p."""
    X, Y = _P / _PHI, _Q / _PHI
    f, j = -_Q - sp.log(_P), -_P - sp.log(_Q)
    d = (1 + x * X) ** 2 * f + (1 - x * Y) ** 2 * j
    g = R(1, 2) * (1 - X**2 * f - Y**2 * j)
    v = sp.log(X * Y)
    P = PARAMS
    k = sp.sqrt(P["b"] - P["c"])
    q = k - sp.sqrt(P["b"] - P["r"] ** 2 - d)
    theta = P["w"] * sp.asinh(x / P["s"])
    p1, p2 = P["r"] * sp.cos(theta), P["r"] * sp.sin(theta)
    S = lambda e: 2 * e + _N(e)  # noqa: E731  S = (2 + N)
    return {
        "d": d,
        "g": g,
        "v": v,
        "g2": _D(g, 2),
        "v1": _D(v),
        "v2": _D(v, 2),
        "q": q,
        "Sq": S(q),
        "p1": p1,
        "p2": p2,
        "Sp1": S(p1),
        "Sp2": S(p2),
    }


def check_profile_identities() -> List[Tuple[str, bool]]:
    pr = profiles()
    d, g, v = pr["d"], pr["g"], pr["v"]
    checks = [
        ("(N+2)g = d", _N(g) + 2 * g - d),
        ("d' = 2xd - v' - 2g'", _D(d) - (2 * x * d - _D(v) - 2 * _D(g))),
        ("Nd - v'' = -(N+2)(d + g'')", _N(d) - _D(v, 2) + _N(d + _D(g, 2)) + 2 * (d + _D(g, 2))),
    ]
    # The identities use 1 - p = q1; the numeric profiles keep q1 separate only to avoid cancellation.
    return [(name, sp.simplify(sp.expand(e.subs(_Q, 1 - _P))) == 0) for name, e in checks]


@lru_cache(maxsize=None)
def _numeric() -> Dict[str, Callable]:
    sub = {_P: sp.erfc(-x / sp.sqrt(2)) / 2, _Q: sp.erfc(x / sp.sqrt(2)) / 2}
    return {name: sp.lambdify(x, e.subs(sub), "mpmath") for name, e in profiles().items() if name not in ("v",)}


def evaluate(xx: float) -> Dict[str, float]:
    """All profile values at x, with precision raised as x^2 grows (X ~ e^{x^2/2} multiplies quantities ~ e^{-x^2})."""
    with mp.workdps(60 + int(0.9 * xx * xx)):
        xv = mp.mpf(xx)
        return {name: float(mp.re(fn(xv))) for name, fn in _numeric().items()}


def profile_table(h: float, half_width: float) -> Dict[str, np.ndarray]:
    n = int(round(half_width / h))
    xs = np.array([i * h for i in range(-n, n + 1)])
    rows = [evaluate(float(v)) for v in xs]
    table = {name: np.array([r[name] for r in rows]) for name in rows[0]}
    table["x"] = xs
    return table


def _derived(t: Dict[str, np.ndarray]) -> Dict[str, np.ndarray]:
    P = {k: float(v) for k, v in PARAMS.items()}
    K = t["d"] - 2 * t["g"]
    C = -t["d"] + (P["a_R"] - 1) * t["g2"]
    return {"K": K, "C": C}


def pointwise_margins(t: Dict[str, np.ndarray], thresholds: Dict[str, float] = None) -> Dict[str, Dict[str, float]]:
    """First bullet of prop:scalar-input. Each margin must be > 0 (>= 0 for the two non-strict bounds)."""
    P = {k: float(v) for k, v in PARAMS.items()}
    th = {"v": 0.319, "C": -0.341, "disc": 0.37, **(thresholds or {})}
    K, C = _derived(t).values()
    lam, tm, tp, ms = P["lambda"], P["t_minus"], P["t_plus"], P["m_star"]
    margins = {
        "b - r^2 - d > 0": P["b"] - P["r"] ** 2 - t["d"],
        "|v' - x| <= .319": th["v"] - np.abs(t["v1"] - t["x"]),
        "C <= -.341": th["C"] - C,
        "S_q > 0": t["Sq"],
        "lambda t_-^2 + t_- C + K > 0": lam * tm**2 + tm * C + K,
        "lambda t_+^2 + t_+ C + K < 0": -(lam * tp**2 + tp * C + K),
        "2(-.37)C - .37^2 - 4 lambda K > m_*^2": 2 * (-th["disc"]) * C - th["disc"] ** 2 - 4 * lam * K - ms**2,
    }
    return {name: {"min": float(m.min()), "at": float(t["x"][int(np.argmin(m))])} for name, m in margins.items()}


def two_variable_margins(t: Dict[str, np.ndarray]) -> Dict[str, Dict[str, float]]:
    """Inequalities (3) of prop:scalar-input on all grid pairs (z, x); margins must be > 0."""
    P = {k: float(v) for k, v in PARAMS.items()}
    b, c, eta, kap = P["b"], P["c"], P["eta"], P["kappa"]
    k = (b - c) ** 0.5
    tm, tp, tc, tr = P["t_minus"], P["t_plus"], P["t_c"], P["t_r"]
    bm = (1 + tp) * (b - 3 * eta) / (3 * (3 * (b + eta) - 4 * c))
    e0, alpha, hs = 0.256, 2.26, 0.5
    q, Sq, v2 = t["q"], t["Sq"], t["v2"]
    H = 4 * c + 4 * k * q[None, :] + 2 * (k - q[None, :]) * Sq[:, None]
    H = H - 2 * (t["Sp1"][:, None] * t["p1"][None, :] + t["Sp2"][:, None] * t["p2"][None, :])
    H0 = H + v2[None, :] - 2 * kap
    lhs = H + tc * H0 - 0.5 * tr * (hs + H0**2 / hs)
    rhs = 2 * (b + eta + (b + eta - kap) * tm) + 2 * bm * Sq[:, None] * Sq[None, :] + 2 * e0 * (2 * tr) ** 2
    m1 = lhs - (rhs + H0**2 / alpha)
    m2 = 4 * c + 2 * k * (Sq[:, None] + Sq[None, :]) - Sq[:, None] * Sq[None, :]
    m2 = m2 - (t["Sp1"][:, None] * t["Sp1"][None, :] + t["Sp2"][:, None] * t["Sp2"][None, :])
    out = {}
    for name, m in (("(3) first", m1), ("(3) second", m2)):
        i = np.unravel_index(np.argmin(m), m.shape)
        out[name] = {"min": float(m.min()), "at_z": float(t["x"][i[0]]), "at_x": float(t["x"][i[1]])}
    return out


def segment_ratio(t: Dict[str, np.ndarray], step: int) -> Dict[str, Any]:
    """Inequality (4): left/right over all segments with endpoints on every `step`-th grid point; must be < 1.

    Segment averages use the cumulative trapezoid rule on the full grid."""
    P = {k: float(v) for k, v in PARAMS.items()}
    lam, tp, tc, tr, ms = P["lambda"], P["t_plus"], P["t_c"], P["t_r"], P["m_star"]
    xs = t["x"]
    h = xs[1] - xs[0]
    K, C = _derived(t).values()
    U = np.stack([t["p1"], t["p2"], t["q"]], 1)
    U2 = (U**2).sum(1)

    def cum(y):
        return np.concatenate([[0.0], np.cumsum((y[1:] + y[:-1]) * h / 2)])

    cK, cC, cU2 = cum(K), cum(C), cum(U2)
    cU = np.stack([cum(U[:, i]) for i in range(3)], 1)
    worst, count = (-np.inf, None), 0
    idx = range(0, len(xs), step)
    for a in idx:
        for e in idx:
            if e <= a:
                continue
            length = xs[e] - xs[a]
            Kb, Cb, U2b = (cK[e] - cK[a]) / length, (cC[e] - cC[a]) / length, (cU2[e] - cU2[a]) / length
            Ub = (cU[e] - cU[a]) / length
            eK = Kb - (K[a] + K[e]) / 2
            gam = 0.80 / ms**2 * (1.25 * (K[e] - K[a] + tc * (C[e] - C[a])) ** 2 + 5 * tr**2 * (C[e] - C[a]) ** 2)
            s1 = s2 = 0.0
            for i, j in ((a, e), (e, a)):
                dev = U2b - 2 * Ub @ U[i] + U[i] @ U[i]  # average of |u - u_sigma|^2
                s1 += (Cb - C[j] - dev) ** 2
                s2 += ((Ub - U[i]) ** 2).sum()
            left = eK + gam + s1 / (8 * lam) + tp / 2 * s2
            right = U2b - Ub @ Ub
            count += 1
            if left / right > worst[0]:
                worst = (left / right, (float(xs[a]), float(xs[e])))
    return {"segments": count, "max_left_over_right": float(worst[0]), "at": worst[1]}


def build_ledger(grid: Dict[str, Any], interval: Dict[str, Any] = None) -> Claim:
    """Assemble the ledger from computed results. `grid` holds the outputs of the numeric checks and their scopes;
    `interval` is the report of mahler_interval (optional). With an interval proof each inequality is split into an
    obligation on the proved window and one outside it, so a window proof never stands in for the whole statement."""
    claim = Claim(
        "mahler.general.scalar_input",
        "Lemma 'Profile identities' and Proposition 'Scalar inequalities' hold for the stated profiles and exact "
        "parameters (input to the Mahler conjecture for general convex bodies)",
        "01-cones.tex: lem:profile-identities, prop:scalar-input",
    )
    ident = Obligation(
        "identities",
        "(N+2)g = d; d' = 2xd - v' - 2g'; Nd - v'' = -(N+2)(d + g'')",
        "lem:profile-identities, (2)",
        "identity",
    )
    ok = all(v for _, v in grid["identities"])
    ident.discharges.append(
        Discharge(
            Status.DISCHARGED_SYMBOLIC if ok else Status.REFUTED,
            "sympy simplify",
            "for any p with p' = phi; exact",
            "CoResearcher",
            detail={n: v for n, v in grid["identities"]},
        )
    )
    claim.obligations.append(ident)
    author = Discharge(
        Status.CERTIFIED_BY_AUTHOR,
        "Appendices 7-8 and verification/programs (not re-run)",
        "all x, including tails",
        "author",
    )
    first = (interval or {}).get("first_bullet")
    for name, m in grid["pointwise"]["margins"].items():
        rest = "" if not first else f" for |x| > {first['window'][1]:g}"
        ob = Obligation(
            f"pointwise: {name}{rest}", name + rest, "prop:scalar-input, first bullet", "pointwise inequality"
        )
        ob.discharges.append(_numeric_discharge(m["min"], grid["pointwise"]["scope"], {"at": m["at"]}))
        ob.discharges.append(author)
        if first:
            w = first["window"][1]
            proved = Obligation(
                f"pointwise: {name} on |x| <= {w:g}",
                f"{name} on |x| <= {w:g}",
                "prop:scalar-input, first bullet",
                "pointwise inequality",
            )
            keys = INTERVAL_KEYS[name]
            margin = min(first["min_lower_bound"][k] for k in keys)
            proved.discharges.append(
                _interval_discharge(
                    first["verified"],
                    f"|x| <= {w:g} (evenness for x < 0)",
                    margin,
                    {"certified_boxes": first["certified_boxes"]},
                )
            )
            claim.obligations.append(proved)
        claim.obligations.append(ob)
    second = (interval or {}).get("two_variable")
    for idx, (name, m) in enumerate(grid["two_variable"]["margins"].items()):
        rest = "" if not second else f" outside [-{second['window'][1]:g}, {second['window'][1]:g}]^2"
        ob = Obligation(f"two-variable: {name}{rest}", name + rest, "prop:scalar-input, (3)", "pointwise inequality")
        ob.discharges.append(_numeric_discharge(m["min"], grid["two_variable"]["scope"], m))
        ob.discharges.append(author)
        if second:
            w = second["window"][1]
            proved = Obligation(
                f"two-variable: {name} on [-{w:g}, {w:g}]^2",
                f"{name} on [-{w:g}, {w:g}]^2",
                "prop:scalar-input, (3)",
                "pointwise inequality",
            )
            proved.discharges.append(
                _interval_discharge(
                    second["verified"],
                    f"(z, x) in [-{w:g}, {w:g}]^2",
                    second["min_lower_bound"][idx],
                    {"certified_pairs": second["certified_pairs"]},
                )
            )
            claim.obligations.append(proved)
        claim.obligations.append(ob)
    seg = grid["segments"]
    ob = Obligation(
        "segment: (4)",
        "e_K + Gamma + ... < avg|u|^2 - |avg u|^2 on every segment",
        "prop:scalar-input, (4); prop:segment-estimate",
        "segment inequality",
    )
    ob.discharges.append(_numeric_discharge(1 - seg["result"]["max_left_over_right"], seg["scope"], seg["result"]))
    ob.discharges.append(author)
    claim.obligations.append(ob)
    return claim


# Ledger names of the first-bullet inequalities -> the margins of mahler_interval.FIRST_BULLET that prove them.
INTERVAL_KEYS = {
    "b - r^2 - d > 0": ["b - r^2 - d > 0"],
    "|v' - x| <= .319": ["v' - x <= .319", "-(v' - x) <= .319"],
    "C <= -.341": ["C <= -.341"],
    "S_q > 0": ["S_q > 0"],
    "lambda t_-^2 + t_- C + K > 0": ["lambda t_-^2 + t_- C + K > 0"],
    "lambda t_+^2 + t_+ C + K < 0": ["lambda t_+^2 + t_+ C + K < 0"],
    "2(-.37)C - .37^2 - 4 lambda K > m_*^2": ["2(-.37)C - .37^2 - 4 lambda K > m_*^2"],
}


def _interval_discharge(verified: bool, scope: str, margin: float, detail: Dict[str, Any]) -> Discharge:
    status = Status.DISCHARGED_INTERVAL if verified else Status.OPEN
    method = "mpmath interval arithmetic, branch and bound (mahler_interval.py)"
    return Discharge(status, method, scope, "CoResearcher", margin=margin, detail=detail)


def _numeric_discharge(margin: float, scope: str, detail: Dict[str, Any]) -> Discharge:
    status = Status.CHECKED_NUMERIC if margin > 0 else Status.REFUTED
    return Discharge(
        status,
        "mpmath, 60 + 0.9 x^2 digits; exact symbolic derivatives",
        scope,
        "CoResearcher",
        margin=margin,
        detail=detail,
    )


def run(
    pointwise_h: float = 0.02,
    pointwise_L: float = 20.0,
    h: float = 0.02,
    L: float = 12.0,
    step: int = 2,
    interval: Dict[str, Any] = None,
):
    t_point = profile_table(pointwise_h, pointwise_L)
    t = t_point if (pointwise_h, pointwise_L) == (h, L) else profile_table(h, L)
    grid = {
        "identities": check_profile_identities(),
        "pointwise": {
            "margins": pointwise_margins(t_point),
            "scope": f"x in [-{pointwise_L}, {pointwise_L}], step {pointwise_h}",
        },
        "two_variable": {"margins": two_variable_margins(t), "scope": f"(z, x) in [-{L}, {L}]^2, step {h}"},
        "segments": {
            "result": segment_ratio(t, step),
            "scope": f"segments with endpoints in [-{L}, {L}] every {step * h:g}; trapezoid step {h}",
        },
    }
    return build_ledger(grid, interval), grid
