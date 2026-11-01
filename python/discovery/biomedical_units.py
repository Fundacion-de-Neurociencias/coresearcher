"""
python/discovery/biomedical_units.py - Units and dimensional homogeneity of formal hypotheses (ADR-DISCOVERY-086).

Method M6 of docs/architecture/VERIFICATION_METHODOLOGY.md names "a unit system" among the conventions that a
biomedical hypothesis imports. This module makes units checkable:

- `parse_unit("mL/min/1.73m^2")` reads a unit string into a scale factor and a vector of base dimensions (mass,
  volume, amount, time, length, enzyme units). Symbols it does not know ("SUVR", "centiloid", "points") become their
  own base dimension, so two different scales are never silently comparable.
- `same_unit(a, b)` says whether two unit strings are the same unit (pg/mL and ng/L are), the same dimension at a
  different scale (pg/mL and ng/mL, a factor of 1000), or different dimensions.
- `check(hypothesis, units, consequences)` walks every predicate of an ADR-059 hypothesis (scope, assumptions, claims,
  consequences) and infers the unit of each sub-expression. Comparisons, sums and differences need operands of the
  same unit; products and quotients combine them; a numeric literal takes the unit of what it is compared with.

Outcomes per predicate: HOMOGENEOUS, DIMENSION_MISMATCH (pg/mL compared with mL/min), SCALE_MISMATCH (pg/mL compared
with ng/mL: same dimension, the numbers differ by a factor), UNDECLARED_UNIT (a variable without a declared unit is
combined with one that has a unit) and NOT_APPLICABLE (no unit-bearing operand). The check is exact: it is a decision
procedure over the expression tree, with no sampling. An undeclared or unreadable unit is never treated as a match
(ADR-068): it stays UNDECLARED_UNIT, a non-verdict for that predicate.

Scope: the formal object's internal consistency. Whether a unit is the right one for a measurement is not judged.
"""

from __future__ import annotations

import ast
import math
import re
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple

from python.discovery.formal_hypothesis import FormalHypothesisError, Predicate

SCHEMA = "coresearcher.biomedical_units/v1"

HOMOGENEOUS = "HOMOGENEOUS"
DIMENSION_MISMATCH = "DIMENSION_MISMATCH"
SCALE_MISMATCH = "SCALE_MISMATCH"
UNDECLARED_UNIT = "UNDECLARED_UNIT"
NOT_APPLICABLE = "NOT_APPLICABLE"

SAME = "SAME"
SAME_DIMENSION = "SAME_DIMENSION"
DIFFERENT_DIMENSION = "DIFFERENT_DIMENSION"
UNREADABLE = "UNREADABLE"

# Base symbols: name -> (scale relative to the base dimension's unit, dimension).
_BASES: Dict[str, Tuple[float, str]] = {
    "g": (1.0, "mass"),
    "L": (1.0, "volume"),
    "l": (1.0, "volume"),
    "mol": (1.0, "amount"),
    "s": (1.0, "time"),
    "sec": (1.0, "time"),
    "min": (60.0, "time"),
    "h": (3600.0, "time"),
    "hr": (3600.0, "time"),
    "d": (86400.0, "time"),
    "day": (86400.0, "time"),
    "days": (86400.0, "time"),
    "wk": (604800.0, "time"),
    "week": (604800.0, "time"),
    "weeks": (604800.0, "time"),
    "mo": (2629800.0, "time"),
    "month": (2629800.0, "time"),
    "months": (2629800.0, "time"),
    "y": (31557600.0, "time"),
    "yr": (31557600.0, "time"),
    "year": (31557600.0, "time"),
    "years": (31557600.0, "time"),
    "m": (1.0, "length"),
    "U": (1.0, "enzyme_unit"),
    "IU": (1.0, "international_unit"),
}
# Prefixes apply to g, L, l, mol, s and m only.
_PREFIXED = ("g", "L", "l", "mol", "s", "m")
_PREFIXES = {"f": 1e-15, "p": 1e-12, "n": 1e-9, "u": 1e-6, "µ": 1e-6, "μ": 1e-6, "m": 1e-3, "c": 1e-2,
             "d": 1e-1, "k": 1e3}
_DIMENSIONLESS = {"1", "", "ratio", "fraction", "dimensionless", "unitless"}


class UnitError(ValueError):
    """A unit string that cannot be read."""


@dataclass(frozen=True)
class Unit:
    """A scale factor and base-dimension exponents. Dimensionless when `dims` is empty."""

    scale: float = 1.0
    dims: Tuple[Tuple[str, int], ...] = ()

    def __mul__(self, other: "Unit") -> "Unit":
        return Unit(self.scale * other.scale, _merge(self.dims, other.dims, 1))

    def __truediv__(self, other: "Unit") -> "Unit":
        return Unit(self.scale / other.scale, _merge(self.dims, other.dims, -1))

    def power(self, n: int) -> "Unit":
        return Unit(self.scale**n, tuple((d, e * n) for d, e in self.dims if e * n))

    def describe(self) -> str:
        if not self.dims:
            return "dimensionless" if math.isclose(self.scale, 1.0) else f"dimensionless x{self.scale:g}"
        dims = " ".join(f"{d}^{e}" if e != 1 else d for d, e in self.dims)
        return dims if math.isclose(self.scale, 1.0) else f"{self.scale:g} {dims}"


def _merge(a, b, sign: int) -> Tuple[Tuple[str, int], ...]:
    out: Dict[str, int] = dict(a)
    for d, e in b:
        out[d] = out.get(d, 0) + sign * e
    return tuple(sorted((d, e) for d, e in out.items() if e))


def _symbol(sym: str) -> Unit:
    if sym in _BASES:
        scale, dim = _BASES[sym]
        return Unit(scale, ((dim, 1),))
    if len(sym) > 1 and sym[0] in _PREFIXES and sym[1:] in _PREFIXED:
        scale, dim = _BASES[sym[1:]]
        return Unit(scale * _PREFIXES[sym[0]], ((dim, 1),))
    # An unknown symbol is its own dimension: scores, SUVR, centiloids, arbitrary units.
    return Unit(1.0, ((f"[{sym}]", 1),))


_FACTOR = re.compile(
    r"^(?P<num>\d+(?:\.\d+)?)?\s*(?P<sym>%|[A-Za-zµμ][A-Za-zµμ_]*)?(?:\^?(?P<exp>-?\d+))?$")


def _factor(text: str) -> Unit:
    text = text.strip()
    if not text:
        raise UnitError("empty factor")
    m = _FACTOR.match(text)
    if not m or not (m.group("num") or m.group("sym")):
        raise UnitError(f"cannot read unit factor {text!r}")
    unit = Unit(float(m.group("num")) if m.group("num") else 1.0)
    sym = m.group("sym")
    if sym == "%":
        unit = unit * Unit(0.01)
    elif sym:
        part = _symbol(sym)
        if m.group("exp"):
            part = part.power(int(m.group("exp")))
        unit = unit * part
    elif m.group("exp"):
        raise UnitError(f"an exponent needs a symbol in {text!r}")
    return unit


def parse_unit(text: str) -> Unit:
    """Reads 'pg/mL', 'mL/min/1.73m^2', 'mmol/L', 'years', '%', '1', 'pg mL^-1', 'SUVR'.

    `a/b/c` reads as a/(b*c); spaces, '*' and '.' between symbols multiply.
    """
    if not isinstance(text, str):
        raise UnitError("a unit must be a string")
    text = text.strip()
    if text.lower() in _DIMENSIONLESS:
        return Unit()
    parts = text.split("/")
    unit = Unit()
    for i, part in enumerate(parts):
        factors = [f for f in re.split(r"[\s*·]+|(?<=[A-Za-z])\.(?=[A-Za-z])", part.strip()) if f]
        if not factors:
            raise UnitError(f"cannot read unit {text!r}")
        piece = Unit()
        for f in factors:
            piece = piece * _factor(f)
        unit = unit * piece if i == 0 else unit / piece
    return unit


def same_unit(a: str, b: str) -> Dict[str, Any]:
    """SAME (pg/mL vs ng/L), SAME_DIMENSION with the factor (pg/mL vs ng/mL), DIFFERENT_DIMENSION or UNREADABLE."""
    try:
        ua, ub = parse_unit(a), parse_unit(b)
    except UnitError as exc:
        return {"outcome": UNREADABLE, "detail": str(exc)}
    if ua.dims != ub.dims:
        return {"outcome": DIFFERENT_DIMENSION, "detail": f"{ua.describe()} vs {ub.describe()}"}
    if math.isclose(ua.scale, ub.scale, rel_tol=1e-9):
        return {"outcome": SAME, "detail": ua.describe()}
    return {"outcome": SAME_DIMENSION, "factor": ua.scale / ub.scale,
            "detail": f"1 {a} = {ua.scale / ub.scale:g} {b}"}


# ---------------------------------------------------------------------------
# Inference over a predicate
# ---------------------------------------------------------------------------

_LITERAL = "literal"  # a number: it takes the unit of what it meets
_CATEGORICAL = "categorical"  # a string or boolean
_UNKNOWN = "unknown"  # a variable without a declared unit


@dataclass
class _Typed:
    kind: str  # "unit", _LITERAL, _CATEGORICAL, _UNKNOWN, "bool"
    unit: Optional[Unit] = None
    label: str = ""
    names: List[str] = field(default_factory=list)


@dataclass
class _Finding:
    outcome: str
    expression: str
    detail: str


class _Inferrer:
    def __init__(self, units: Dict[str, Tuple[Unit, str]], categorical: set, unreadable: Dict[str, str]):
        self.units = units
        self.categorical = categorical
        self.unreadable = unreadable
        self.findings: List[_Finding] = []
        self.unit_bearing = False

    def _unify(self, node: ast.AST, a: _Typed, b: _Typed, what: str) -> _Typed:
        if a.kind in (_LITERAL, _CATEGORICAL, "bool") or b.kind in (_LITERAL, _CATEGORICAL, "bool"):
            if a.kind == "unit":
                return a
            if b.kind == "unit":
                return b
            return a if a.kind != _LITERAL else b
        if a.kind == _UNKNOWN or b.kind == _UNKNOWN:
            known = a if a.kind == "unit" else b if b.kind == "unit" else None
            if known is not None:
                unknown = [n for t in (a, b) if t.kind == _UNKNOWN for n in t.names]
                why = "; ".join(f"{n}: {self.unreadable[n]}" for n in unknown if n in self.unreadable)
                self.findings.append(_Finding(
                    UNDECLARED_UNIT, ast.unparse(node),
                    f"{', '.join(unknown)} has no readable unit and is {what} {known.label}" + (f" ({why})" if why else "")))
                self.unit_bearing = True
            return _Typed(_UNKNOWN, names=a.names + b.names)
        self.unit_bearing = True
        if a.unit.dims != b.unit.dims:
            self.findings.append(_Finding(DIMENSION_MISMATCH, ast.unparse(node),
                                          f"{what}: {a.label} ({a.unit.describe()}) vs {b.label} ({b.unit.describe()})"))
        elif not math.isclose(a.unit.scale, b.unit.scale, rel_tol=1e-9):
            self.findings.append(_Finding(SCALE_MISMATCH, ast.unparse(node),
                                          f"{what}: {a.label} and {b.label} differ by a factor of "
                                          f"{a.unit.scale / b.unit.scale:g}"))
        return a

    def infer(self, node: ast.AST) -> _Typed:
        if isinstance(node, ast.Constant):
            if isinstance(node.value, bool) or isinstance(node.value, str):
                return _Typed(_CATEGORICAL)
            return _Typed(_LITERAL, Unit(), label=repr(node.value))
        if isinstance(node, ast.Name):
            if node.id in ("True", "False", "true", "false"):
                return _Typed(_CATEGORICAL)
            if node.id in self.units:
                unit, text = self.units[node.id]
                return _Typed("unit", unit, label=f"{node.id} [{text}]", names=[node.id])
            if node.id in self.categorical:
                return _Typed(_CATEGORICAL, names=[node.id])
            return _Typed(_UNKNOWN, names=[node.id])
        if isinstance(node, (ast.Tuple, ast.List, ast.Set)):
            items = [self.infer(e) for e in node.elts]
            out = _Typed(_LITERAL)
            for item in items:
                out = self._unify(node, out, item, "listed with")
            return out
        if isinstance(node, ast.BoolOp):
            for v in node.values:
                self.infer(v)
            return _Typed("bool")
        if isinstance(node, ast.UnaryOp):
            inner = self.infer(node.operand)
            return _Typed("bool") if isinstance(node.op, ast.Not) else inner
        if isinstance(node, ast.BinOp):
            left, right = self.infer(node.left), self.infer(node.right)
            if isinstance(node.op, (ast.Add, ast.Sub, ast.Mod, ast.FloorDiv)):
                return self._unify(node, left, right, "added to or subtracted from")
            if isinstance(node.op, ast.Pow):
                if isinstance(node.right, ast.Constant) and isinstance(node.right.value, int) and left.kind == "unit":
                    return _Typed("unit", left.unit.power(node.right.value), label=f"({left.label})^{node.right.value}")
                if left.kind == "unit" and left.unit.dims:
                    self.findings.append(_Finding(DIMENSION_MISMATCH, ast.unparse(node),
                                                  f"{left.label} is raised to a non-integer or variable power"))
                return left
            if left.kind == _UNKNOWN or right.kind == _UNKNOWN:
                return _Typed(_UNKNOWN, names=left.names + right.names)
            lu = left.unit if left.kind == "unit" else Unit()
            ru = right.unit if right.kind == "unit" else Unit()
            if left.kind != "unit" and right.kind != "unit":
                return _Typed(_LITERAL)
            unit = lu * ru if isinstance(node.op, ast.Mult) else lu / ru
            label = f"({left.label or ast.unparse(node.left)} {'*' if isinstance(node.op, ast.Mult) else '/'} " \
                    f"{right.label or ast.unparse(node.right)})"
            return _Typed("unit", unit, label=label, names=left.names + right.names)
        if isinstance(node, ast.Compare):
            operands = [self.infer(node.left)] + [self.infer(c) for c in node.comparators]
            for a, b in zip(operands, operands[1:]):
                self._unify(node, a, b, "compared with")
            return _Typed("bool")
        return _Typed(_UNKNOWN)


def _predicates(hypothesis: Dict[str, Any], consequences: List[str]) -> List[Tuple[str, str]]:
    out = []
    if hypothesis.get("scope"):
        out.append(("scope", hypothesis["scope"]))
    out += [(f"assumptions[{i}]", a) for i, a in enumerate(hypothesis.get("assumptions") or [])]
    out += [(f"claims[{i}]", c) for i, c in enumerate(hypothesis.get("claims") or [])]
    out += [(f"consequences[{i}]", c) for i, c in enumerate(consequences or [])]
    return out


def check(hypothesis: Dict[str, Any], units: Dict[str, str], consequences: Optional[List[str]] = None
          ) -> Dict[str, Any]:
    """Dimensional and unit homogeneity of every predicate of a hypothesis (dict form) under declared units.

    `units` maps variable names to unit strings. Variables with string or boolean domains are categorical and need
    none. The outcome is HOMOGENEOUS, FINDINGS (a dimension or scale mismatch) or INCOMPLETE (an undeclared or
    unreadable unit where it matters); only FINDINGS and HOMOGENEOUS are decided.
    """
    variables = hypothesis.get("variables") or []
    names = [v["name"] for v in variables]
    unknown = sorted(set(units or {}) - set(names))
    if unknown:
        raise FormalHypothesisError(f"units are declared for undeclared variables {unknown}")
    parsed: Dict[str, Tuple[Unit, str]] = {}
    unreadable: Dict[str, str] = {}
    for name, text in (units or {}).items():
        try:
            parsed[name] = (parse_unit(text), text)
        except UnitError as exc:
            unreadable[name] = str(exc)
    categorical = {v["name"] for v in variables
                   if v.get("domain") and all(isinstance(x, (str, bool)) for x in v["domain"]) and v["name"] not in parsed}
    reports = []
    for where, expression in _predicates(hypothesis, consequences or []):
        Predicate(expression, names)  # The same parser and checks as the evaluator.
        inferrer = _Inferrer(parsed, categorical, unreadable)
        inferrer.infer(ast.parse(expression.strip(), mode="eval").body)
        kinds = {f.outcome for f in inferrer.findings}
        outcome = next((k for k in (DIMENSION_MISMATCH, SCALE_MISMATCH, UNDECLARED_UNIT) if k in kinds),
                       HOMOGENEOUS if inferrer.unit_bearing else NOT_APPLICABLE)
        reports.append({"where": where, "expression": expression, "outcome": outcome,
                        "findings": [f.__dict__ for f in inferrer.findings]})
    outcomes = {r["outcome"] for r in reports}
    if outcomes & {DIMENSION_MISMATCH, SCALE_MISMATCH}:
        overall = "FINDINGS"
    elif UNDECLARED_UNIT in outcomes:
        overall = "INCOMPLETE"
    else:
        overall = HOMOGENEOUS
    return {
        "schema": SCHEMA,
        "outcome": overall,
        "units": {n: {"unit": t, "dimension": parsed[n][0].describe()} for n, (_, t) in parsed.items()},
        "unreadable": unreadable,
        "predicates": reports,
        "method": "unit algebra over the predicate expression trees (exact, no sampling)",
    }


__all__ = ["parse_unit", "same_unit", "check", "Unit", "UnitError", "HOMOGENEOUS", "DIMENSION_MISMATCH",
           "SCALE_MISMATCH", "UNDECLARED_UNIT", "NOT_APPLICABLE", "SAME", "SAME_DIMENSION", "DIFFERENT_DIMENSION"]
