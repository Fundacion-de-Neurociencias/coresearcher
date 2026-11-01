"""
python/discovery/asymptotic_forms.py - Asymptotic notation as explicit quantified forms (ADR-DISCOVERY-084).

Method M1 of docs/architecture/VERIFICATION_METHODOLOGY.md: check the question before the answer. Asymptotic
notation hides a direction. A headline exponent n/(log n)^{c+o(1)} admits two readings:

- SIGNED: there is a function eps(n) -> 0, of any sign, with E(n) <= n/(log n)^{c+eps(n)} for all large n;
- NONNEGATIVE: the same with eps(n) >= 0, which says E(n) <= n/(log n)^c for all large n.

Given an explicit bound E(n) (for example the one in a Lean statement), this module decides which readings it
satisfies, with sympy limits after the substitution n = exp(exp(t)), so that log n = e^t and log log n = t. The
implied exponent is eps_E(n) = log(n/E(n))/log log n - c:

- SIGNED fits iff liminf eps_E >= 0; it is decided here when eps_E has a limit L (FITS for L >= 0, DOES_NOT_FIT
  for L < 0);
- NONNEGATIVE fits iff E(n) <= n/(log n)^c eventually; it is decided from the limit R of their ratio (FITS for
  R < 1, DOES_NOT_FIT for R > 1, including infinity).

Anything else, including a limit sympy cannot compute, is UNDECIDED (a non-verdict, never a fit).

`binder_order` and `uniformity` read the quantifier prefix of a Lean statement: a complexity claim is uniform only
if the machine is bound before every input, since a machine allowed to depend on n could hard-code its answers.
"""

from __future__ import annotations

import re
from typing import Any, Dict, List, Optional, Sequence, Tuple

import sympy

FITS = "FITS"
DOES_NOT_FIT = "DOES_NOT_FIT"
UNDECIDED = "UNDECIDED"

UNIFORM = "UNIFORM"
NON_UNIFORM = "NON_UNIFORM"

_n = sympy.Symbol("n", positive=True)
_t = sympy.Symbol("t", positive=True)


def _limit(expr: sympy.Expr) -> Optional[sympy.Expr]:
    try:
        value = sympy.limit(expr, _t, sympy.oo)
    except Exception:
        return None
    if value.has(sympy.AccumBounds) or value.has(sympy.nan) or _t in value.free_symbols:
        return None
    return value


def _sign(value: sympy.Expr) -> Optional[int]:
    if value is sympy.oo:
        return 1
    if value is sympy.zoo or value is -sympy.oo:
        return -1 if value is -sympy.oo else None
    if value.is_zero:
        return 0
    if value.is_positive:
        return 1
    if value.is_negative:
        return -1
    return None


def little_o_exponent(bound: str, c: str = "1/2", symbols: Sequence[str] = ()) -> Dict[str, Any]:
    """Which readings of n/(log n)^{c+o(1)} the explicit exponent `bound` (a sympy expression in n) satisfies.

    `symbols` are positive constants in the bound (an O(1) factor written as a symbol)."""
    local = {name: sympy.Symbol(name, positive=True) for name in symbols}
    local["n"] = _n
    exponent = sympy.sympify(bound, locals=local)
    power = sympy.Rational(c) if re.fullmatch(r"-?\d+(/\d+)?", c) else sympy.sympify(c)
    substituted = exponent.subs(_n, sympy.exp(sympy.exp(_t)))
    main = sympy.exp(sympy.exp(_t)) / sympy.exp(power * _t)  # n / (log n)^c
    implied = sympy.simplify(sympy.expand_log(sympy.log(sympy.exp(sympy.exp(_t)) / substituted), force=True) / _t
                             - power)
    eps_limit = _limit(implied)
    ratio_limit = _limit(sympy.simplify(substituted / main))
    eps_sign = _sign(eps_limit) if eps_limit is not None else None
    ratio_sign = None if ratio_limit is None else _sign(ratio_limit - 1) if ratio_limit is not sympy.oo else 1
    signed = UNDECIDED if eps_sign is None else FITS if eps_sign >= 0 else DOES_NOT_FIT
    nonnegative = UNDECIDED if ratio_sign in (None, 0) else FITS if ratio_sign < 0 else DOES_NOT_FIT
    return {
        "headline": f"n/(log n)^({c}+o(1))",
        "bound": bound,
        "substitution": "n = exp(exp(t)): log n = exp(t), log log n = t",
        "implied_o1": str(implied),
        "implied_o1_limit": None if eps_limit is None else str(eps_limit),
        "ratio_to_main_term_limit": None if ratio_limit is None else str(ratio_limit),
        "signed_reading": signed,
        "nonnegative_reading": nonnegative,
    }


# ---------------------------------------------------------------------------
# Quantifier prefix of a Lean statement
# ---------------------------------------------------------------------------

_BINDER = re.compile(r"(∃|∀)\s*((?:\([^():]*:[^()]*(?:\([^()]*\))?[^()]*\)\s*|[^\s,(]+\s*)+?)\s*,")
_NAMES = re.compile(r"\(([^():]*):")


def binder_order(statement: str) -> List[Tuple[str, List[str]]]:
    """(quantifier, bound names) in the order they occur. Parenthesized binders `(x y : T)` and bare `x` are read."""
    out = []
    for m in _BINDER.finditer(statement):
        group = m.group(2)
        names = [name for part in _NAMES.findall(group) for name in part.split()]
        if not names:
            names = [w for w in re.split(r"\s+", group.strip()) if w and not w.startswith(":")]
        out.append((m.group(1), names))
    return out


def uniformity(statement: str, witness: str, inputs: Sequence[str]) -> Dict[str, Any]:
    """UNIFORM when `witness` is bound by ∃ before every ∀ that binds one of `inputs`; NON_UNIFORM when an input is
    bound first; UNDECIDED when either is not found."""
    order = binder_order(statement)
    witness_at = next((i for i, (q, names) in enumerate(order) if q == "∃" and witness in names), None)
    input_at = [i for i, (q, names) in enumerate(order) if q == "∀" and set(names) & set(inputs)]
    if witness_at is None or not input_at:
        verdict = UNDECIDED
    else:
        verdict = UNIFORM if witness_at < min(input_at) else NON_UNIFORM
    return {"witness": witness, "inputs": list(inputs), "binders": [[q, names] for q, names in order],
            "verdict": verdict}
