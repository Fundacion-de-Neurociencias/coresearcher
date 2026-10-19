"""
python/discovery/formal_smt.py - SMT back end for formal hypotheses (ADR-DISCOVERY-060).

Translates the restricted predicate language of `formal_hypothesis` into z3 formulas, so hypotheses over continuous
variables can be evaluated exactly. Finite variables are encoded too, which lets the SMT back end be cross-checked
against exhaustive enumeration on finite hypotheses.

Encoding:
- continuous variable: z3 Real, with optional lower and upper bounds;
- finite numeric variable: z3 Real constrained to its domain values;
- finite boolean variable: z3 Bool;
- finite string variable: z3 Int index into its domain; only ==, !=, in and not in are allowed on it.

Unsupported in this back end: ordering comparisons on strings, % and //, and powers with a non-constant exponent.
"""

from __future__ import annotations

import ast
from dataclasses import dataclass
from fractions import Fraction
from typing import Any, Dict, List, Optional

import z3

from python.discovery import formal_thresholds
from python.discovery.formal_hypothesis import FormalHypothesisError, Predicate, SolverUndecided

# Versioned default; the value in force is the threshold solver_timeout_ms (ADR-DISCOVERY-068). Per solver call; on
# timeout the question is reported as UNDECIDED, never answered.
SOLVER_TIMEOUT_MS = formal_thresholds.FORMAL_DEFAULTS.values["solver_timeout_ms"]

_ARITH = {
    ast.Add: lambda a, b: a + b,
    ast.Sub: lambda a, b: a - b,
    ast.Mult: lambda a, b: a * b,
    ast.Div: lambda a, b: a / b,
}
_ORDER = {
    ast.Lt: lambda a, b: a < b,
    ast.LtE: lambda a, b: a <= b,
    ast.Gt: lambda a, b: a > b,
    ast.GtE: lambda a, b: a >= b,
}


class SymbolTable:
    """z3 symbols and domain constraints for a hypothesis's variables."""

    def __init__(self, variables: List[Any]):
        self.symbols: Dict[str, Any] = {}
        self.kinds: Dict[str, str] = {}
        self.domains: Dict[str, tuple] = {}
        self.constraints: List[Any] = []
        self.variables = {var.name: var for var in variables}
        for var in variables:
            name = var.name
            if getattr(var, "is_continuous", False):
                sym = z3.Real(name)
                self.kinds[name] = "real"
                if var.lower is not None:
                    self.constraints.append(sym >= _num(var.lower))
                if var.upper is not None:
                    self.constraints.append(sym <= _num(var.upper))
            elif all(isinstance(v, bool) for v in var.domain):
                sym = z3.Bool(name)
                self.kinds[name] = "bool"
                if len(set(var.domain)) == 1:
                    self.constraints.append(sym == z3.BoolVal(var.domain[0]))
            elif all(isinstance(v, (int, float)) and not isinstance(v, bool) for v in var.domain):
                sym = z3.Real(name)
                self.kinds[name] = "number"
                self.constraints.append(z3.Or([sym == _num(v) for v in var.domain]))
            elif all(isinstance(v, str) for v in var.domain):
                sym = z3.Int(name)
                self.kinds[name] = "string"
                self.constraints.append(z3.And(sym >= 0, sym < len(var.domain)))
            else:
                raise FormalHypothesisError(f"Variable {name!r} mixes value types; the SMT back end cannot encode it.")
            self.symbols[name] = sym
            self.domains[name] = tuple(getattr(var, "domain", ()))

    def domain_formula(self):
        return z3.And(self.constraints) if self.constraints else z3.BoolVal(True)

    def fix(self, observation: Dict[str, Any]):
        """Formula fixing the observed variables to their observed values."""
        parts = []
        for name, value in observation.items():
            if name not in self.symbols:
                raise FormalHypothesisError(f"Observation uses undeclared variable {name!r}.")
            kind = self.kinds[name]
            if kind == "string":
                if value not in self.domains[name]:
                    raise FormalHypothesisError(f"Observed value {value!r} is outside the domain of {name!r}.")
                parts.append(self.symbols[name] == self.domains[name].index(value))
            elif kind == "bool":
                parts.append(self.symbols[name] == z3.BoolVal(bool(value)))
            else:
                if isinstance(value, bool) or not isinstance(value, (int, float)):
                    raise FormalHypothesisError(f"Observed value {value!r} for {name!r} must be a number.")
                if kind == "number" and value not in self.domains[name]:
                    raise FormalHypothesisError(f"Observed value {value!r} is outside the domain of {name!r}.")
                if kind == "real":
                    var = self.variables[name]
                    if (var.lower is not None and value < var.lower) or (var.upper is not None and value > var.upper):
                        raise FormalHypothesisError(f"Observed value {value!r} is outside the bounds of {name!r}.")
                parts.append(self.symbols[name] == _num(value))
        return z3.And(parts) if parts else z3.BoolVal(True)

    def decode(self, model) -> Dict[str, Any]:
        """Turns a z3 model into a state with domain values (or exact numbers for continuous variables)."""
        state = {}
        for name, sym in self.symbols.items():
            value = model.eval(sym, model_completion=True)
            kind = self.kinds[name]
            if kind == "string":
                state[name] = self.domains[name][value.as_long()]
            elif kind == "bool":
                state[name] = z3.is_true(value)
            else:
                if z3.is_algebraic_value(value):  # Irrational root from nonlinear arithmetic.
                    value = value.approx(20)
                frac = value.as_fraction()
                if kind == "number":
                    state[name] = next(v for v in self.domains[name] if _frac(v) == frac)
                else:
                    state[name] = int(frac) if frac.denominator == 1 else float(frac)
        return state


def _frac(value) -> Fraction:
    return Fraction(value).limit_denominator(10**12)


def _num(value) -> Any:
    return z3.RealVal(str(_frac(value)))


def to_z3(predicate: Predicate, table: SymbolTable):
    """Translates a parsed predicate into a z3 boolean formula."""
    return _Translator(table).boolean(predicate._node, predicate.expression)


class _Translator:
    def __init__(self, table: SymbolTable):
        self.table = table

    def boolean(self, node, expression):
        value = self.expr(node, expression)
        if not z3.is_bool(value):
            raise FormalHypothesisError(f"{expression!r} is not a boolean expression.")
        return value

    def expr(self, node, expression):
        if isinstance(node, ast.Constant):
            if isinstance(node.value, bool):
                return z3.BoolVal(node.value)
            if isinstance(node.value, (int, float)):
                return _num(node.value)
            raise FormalHypothesisError(f"String constant outside a comparison in {expression!r}.")
        if isinstance(node, ast.Name):
            if self.table.kinds.get(node.id) == "string":
                raise FormalHypothesisError(f"String variable {node.id!r} used outside ==, !=, in in {expression!r}.")
            return self.table.symbols[node.id]
        if isinstance(node, ast.BoolOp):
            parts = [self.boolean(v, expression) for v in node.values]
            return z3.And(parts) if isinstance(node.op, ast.And) else z3.Or(parts)
        if isinstance(node, ast.UnaryOp):
            if isinstance(node.op, ast.Not):
                return z3.Not(self.boolean(node.operand, expression))
            value = self.expr(node.operand, expression)
            return -value if isinstance(node.op, ast.USub) else value
        if isinstance(node, ast.BinOp):
            if isinstance(node.op, ast.Pow):
                if not (
                    isinstance(node.right, ast.Constant) and isinstance(node.right.value, int) and node.right.value >= 0
                ):
                    raise FormalHypothesisError(
                        f"Only constant non-negative integer powers are supported in {expression!r}."
                    )
                base = self.expr(node.left, expression)
                result = _num(1)
                for _ in range(node.right.value):
                    result = result * base
                return result
            if type(node.op) not in _ARITH:
                raise FormalHypothesisError(f"Operator {type(node.op).__name__} is not supported by the SMT back end.")
            return _ARITH[type(node.op)](self.expr(node.left, expression), self.expr(node.right, expression))
        if isinstance(node, ast.Compare):
            parts = []
            left = node.left
            for op, right in zip(node.ops, node.comparators):
                parts.append(self.compare(left, op, right, expression))
                left = right
            return z3.And(parts) if len(parts) > 1 else parts[0]
        raise FormalHypothesisError(f"{type(node).__name__} is not supported by the SMT back end in {expression!r}.")

    def _string_side(self, node) -> Optional[str]:
        if isinstance(node, ast.Name) and self.table.kinds.get(node.id) == "string":
            return node.id
        return None

    def compare(self, left, op, right, expression):
        string_var = self._string_side(left) or self._string_side(right)
        if string_var:
            other = right if self._string_side(left) else left
            sym, domain = self.table.symbols[string_var], self.table.domains[string_var]
            if isinstance(op, (ast.In, ast.NotIn)):
                if not isinstance(other, (ast.Tuple, ast.List, ast.Set)):
                    raise FormalHypothesisError(f"'in' needs a literal collection in {expression!r}.")
                values = [e.value for e in other.elts if isinstance(e, ast.Constant)]
                options = [sym == domain.index(v) for v in values if v in domain]
                member = z3.Or(options) if options else z3.BoolVal(False)
                return member if isinstance(op, ast.In) else z3.Not(member)
            if not isinstance(other, ast.Constant) or not isinstance(other.value, str):
                raise FormalHypothesisError(
                    f"String variable {string_var!r} must be compared with a string in {expression!r}."
                )
            equal = sym == domain.index(other.value) if other.value in domain else z3.BoolVal(False)
            if isinstance(op, ast.Eq):
                return equal
            if isinstance(op, ast.NotEq):
                return z3.Not(equal)
            raise FormalHypothesisError(f"Ordering comparison on string variable {string_var!r} in {expression!r}.")
        if isinstance(op, (ast.In, ast.NotIn)):
            if not isinstance(right, (ast.Tuple, ast.List, ast.Set)):
                raise FormalHypothesisError(f"'in' needs a literal collection in {expression!r}.")
            a = self.expr(left, expression)
            options = [a == self.expr(e, expression) for e in right.elts]
            member = z3.Or(options) if options else z3.BoolVal(False)
            return member if isinstance(op, ast.In) else z3.Not(member)
        a, b = self.expr(left, expression), self.expr(right, expression)
        if isinstance(op, ast.Eq):
            return a == b
        if isinstance(op, ast.NotEq):
            return a != b
        if type(op) in _ORDER:
            return _ORDER[type(op)](a, b)
        raise FormalHypothesisError(f"Comparison {type(op).__name__} is not supported in {expression!r}.")


def _solver():
    solver = z3.Solver()
    solver.set("timeout", int(formal_thresholds.get("solver_timeout_ms")))
    return solver


def satisfiable(*formulas) -> Optional[Any]:
    """Returns a model when the conjunction is satisfiable, None when it is not."""
    solver = _solver()
    solver.add(*formulas)
    result = solver.check()
    if result == z3.unknown:
        raise SolverUndecided(f"The SMT solver could not decide the formula ({solver.reason_unknown()}).")
    return solver.model() if result == z3.sat else None


def models(formula, table: SymbolTable, limit: int) -> List[Dict[str, Any]]:
    """Up to `limit` distinct states satisfying the formula (and the variable domains)."""
    solver = _solver()
    solver.add(table.domain_formula(), formula)
    found: List[Dict[str, Any]] = []
    while len(found) < limit:
        result = solver.check()
        if result == z3.unknown:
            raise SolverUndecided(f"The SMT solver could not decide the formula ({solver.reason_unknown()}).")
        if result == z3.unsat:
            break
        model = solver.model()
        found.append(table.decode(model))
        solver.add(z3.Or([sym != model.eval(sym, model_completion=True) for sym in table.symbols.values()]))
    return found


@dataclass
class Encoding:
    """A hypothesis as z3 formulas. `forbidden` holds exactly in the states the hypothesis forbids."""

    table: SymbolTable
    domain: Any
    scope: Any
    assumptions: List[Any]
    claims: List[Any]

    @property
    def applies(self):
        return z3.And(self.domain, self.scope, *self.assumptions)

    @property
    def claims_hold(self):
        return z3.And(*self.claims)

    @property
    def forbidden(self):
        return z3.And(self.applies, z3.Not(self.claims_hold))


def encode(hypothesis) -> Encoding:
    table = SymbolTable(hypothesis.variables)
    return Encoding(
        table=table,
        domain=table.domain_formula(),
        scope=to_z3(hypothesis._scope, table) if hypothesis._scope is not None else z3.BoolVal(True),
        assumptions=[to_z3(p, table) for p in hypothesis._assumptions],
        claims=[to_z3(p, table) for p in hypothesis._claims],
    )
