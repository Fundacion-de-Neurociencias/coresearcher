"""
python/discovery/statement_fidelity.py - Statement fidelity: does a formal statement assert what the paper claims?
(ADR-DISCOVERY-070)

When a kernel check exists, trust moves from the proof to the statement. This module decides one part of that
question exactly: the parameter range over which a theorem is asserted. The paper's hypothesis range and the
range in the formal (Lean) statement are both written in the predicate language of `formal_hypothesis`, extended
with `max`, `min` and `abs`, and z3 (`formal_smt`) decides whether they are the same set.

A theorem "for every parameter in R, the conclusion holds" is stronger the larger R is. So the relation reported
is the strength of the formal statement relative to the paper, over the range alone:

- EQUIVALENT: both ranges are the same set;
- STRONGER: the formal range strictly contains the paper range (it asserts the conclusion for more parameters);
- WEAKER: the formal range is strictly contained in the paper range;
- INCOMPARABLE: each range has points the other lacks;
- UNDECIDED: the solver timed out, or the encoding could divide by zero (z3 treats x/0 as an arbitrary value,
  the same junk-value hazard the Lean lint looks for, so no answer is given).

Integer parameters (a dimension n) are z3 Ints. Mixed integer and nonlinear real arithmetic is undecidable in
general; when z3 gives up, each direction is retried over the real relaxation (integers widened to reals). An
empty difference over the reals is empty over the integers too; a real witness counts only if its integer
coordinates are integral. Anything else stays UNDECIDED.

Conclusions are not compared here: a log power against a delta^-epsilon loss is outside the decidable fragment,
and the case documents say so instead of answering.
"""

from __future__ import annotations

import ast
import copy
from dataclasses import asdict, dataclass, field
from enum import Enum
from fractions import Fraction
from typing import Any, Dict, List, Optional, Sequence

import z3

from python.discovery import formal_smt, formal_thresholds
from python.discovery.formal_hypothesis import (
    FormalHypothesisError,
    Hypothesis,
    HypothesisEvaluator,
    Predicate,
    Relation,
    SolverUndecided,
    Variable,
)

_PIECEWISE = ("max", "min", "abs")


class Fidelity(str, Enum):
    EQUIVALENT = "EQUIVALENT"
    STRONGER = "STRONGER"  # The formal range strictly contains the paper range.
    WEAKER = "WEAKER"  # The formal range is strictly contained in the paper range.
    INCOMPARABLE = "INCOMPARABLE"
    UNDECIDED = "UNDECIDED"


class Agreement(str, Enum):
    EQUAL = "EQUAL"
    DIFFERS = "DIFFERS"
    UNDECIDED = "UNDECIDED"


@dataclass(frozen=True)
class Parameter:
    """A theorem parameter: real by default, integer with `integer=True`; bounds are closed and optional."""

    name: str
    integer: bool = False
    lower: Optional[float] = None
    upper: Optional[float] = None


@dataclass(frozen=True)
class Quantity:
    """A derived quantity both statements use (a Sobolev order, an exponent), checked for equality on the range."""

    name: str
    paper: str
    lean: str


@dataclass
class RangeSpec:
    theorem: str
    parameters: List[Parameter]
    paper: str  # Hypothesis range as stated in the paper.
    lean: str  # Hypothesis range as written in the formal statement, after the encoding below.
    domain: str = "True"  # Shared facts: parameter encodings and constraints both statements take for granted.
    paper_source: str = ""
    lean_source: str = ""
    encoding: List[str] = field(default_factory=list)  # How the formal types were mapped to real arithmetic.
    quantities: List[Quantity] = field(default_factory=list)


@dataclass
class RangeResult:
    theorem: str
    relation: Fidelity
    paper_nonempty: Optional[bool]
    lean_nonempty: Optional[bool]
    lean_only_witness: Optional[Dict[str, Any]]  # In the formal range, not in the paper's.
    paper_only_witness: Optional[Dict[str, Any]]  # In the paper range, not in the formal one.
    method: Dict[str, str]  # Per direction: "exact", "real relaxation" or "undecided".
    division_hazards: List[str]
    quantities: Dict[str, Dict[str, Any]]
    undecided_reasons: List[str]
    paper: str
    lean: str
    paper_source: str
    lean_source: str
    encoding: List[str]
    solver_timeout_ms: int

    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        data["relation"] = self.relation.value
        return data


# ---------------------------------------------------------------------------
# max / min / abs as case splits
# ---------------------------------------------------------------------------


def _first_piecewise_call(node: ast.AST) -> Optional[ast.Call]:
    for child in ast.walk(node):
        if isinstance(child, ast.Call) and isinstance(child.func, ast.Name) and child.func.id in _PIECEWISE:
            return child
    return None


def _cases(call: ast.Call) -> List[tuple]:
    """(guard, replacement) pairs that cover every state exactly once."""
    name = call.func.id
    if name == "abs":
        if len(call.args) != 1:
            raise FormalHypothesisError("abs takes one argument.")
        (x,) = call.args
        return [
            (ast.Compare(x, [ast.GtE()], [ast.Constant(0)]), x),
            (ast.Compare(x, [ast.Lt()], [ast.Constant(0)]), ast.UnaryOp(ast.USub(), x)),
        ]
    if len(call.args) < 2:
        raise FormalHypothesisError(f"{name} takes at least two arguments.")
    x, rest = call.args[0], call.args[1:]
    y = rest[0] if len(rest) == 1 else ast.Call(ast.Name(name, ast.Load()), list(rest), [])
    first_wins = ast.GtE() if name == "max" else ast.LtE()
    second_wins = ast.Lt() if name == "max" else ast.Gt()
    return [(ast.Compare(x, [first_wins], [y]), x), (ast.Compare(x, [second_wins], [y]), y)]


class _Replace(ast.NodeTransformer):
    def __init__(self, target: ast.AST, replacement: ast.AST):
        self.target, self.replacement = target, replacement

    def visit(self, node):
        if node is self.target:
            return self.replacement
        return super().visit(node)


def _split_atom(atom: ast.AST) -> ast.AST:
    call = _first_piecewise_call(atom)
    if call is None:
        return atom
    branches = []
    for guard, replacement in _cases(call):
        rewritten = _replace_by_position(atom, call, replacement)
        branches.append(ast.BoolOp(ast.And(), [_split_atom(guard), _split_atom(rewritten)]))
    return ast.BoolOp(ast.Or(), branches)


def _replace_by_position(atom: ast.AST, call: ast.Call, replacement: ast.AST) -> ast.AST:
    """A copy of `atom` with `call` replaced; the call is located by its walk position, since copies lose identity."""
    clone = copy.deepcopy(atom)
    originals = list(ast.walk(atom))
    copies = list(ast.walk(clone))
    target = copies[originals.index(call)]
    return _Replace(target, copy.deepcopy(replacement)).visit(clone)


class _Desugar(ast.NodeTransformer):
    def visit_Compare(self, node: ast.Compare) -> ast.AST:
        return _split_atom(node)


def desugar(expression: str) -> str:
    """Rewrites max/min/abs into an equivalent formula of the plain predicate language.

    Each comparison that contains a call is split on the call's cases: phi[max(a, b)] becomes
    (a >= b and phi[a]) or (a < b and phi[b]). The rewrite is exact, so z3 decides the original formula.
    """
    tree = ast.parse(expression.strip(), mode="eval")
    for node in ast.walk(tree):
        if isinstance(node, ast.Call) and not (isinstance(node.func, ast.Name) and node.func.id in _PIECEWISE):
            raise FormalHypothesisError(f"Only {_PIECEWISE} calls are allowed in {expression!r}.")
    body = _Desugar().visit(tree).body
    return ast.unparse(ast.fix_missing_locations(body))


# ---------------------------------------------------------------------------
# Encoding
# ---------------------------------------------------------------------------


class _Encoder:
    """z3 symbols for the parameters; integers are Ints unless `relaxed`, where they widen to Reals."""

    def __init__(self, parameters: Sequence[Parameter], relaxed: bool = False):
        self.parameters = list(parameters)
        self.names = [p.name for p in parameters]
        self.table = formal_smt.SymbolTable(
            [Variable(p.name, continuous=True, lower=p.lower, upper=p.upper) for p in parameters]
        )
        self.table.constraints = []
        for p in parameters:
            sym = z3.Int(p.name) if p.integer and not relaxed else z3.Real(p.name)
            self.table.symbols[p.name] = sym
            if p.lower is not None:
                self.table.constraints.append(sym >= formal_smt._num(p.lower))
            if p.upper is not None:
                self.table.constraints.append(sym <= formal_smt._num(p.upper))

    def formula(self, expression: str):
        return formal_smt.to_z3(Predicate(desugar(expression), self.names), self.table)

    def bounds(self):
        return z3.And(self.table.constraints) if self.table.constraints else z3.BoolVal(True)

    def decode(self, model) -> Dict[str, Any]:
        state: Dict[str, Any] = {}
        for name, sym in self.table.symbols.items():
            value = model.eval(sym, model_completion=True)
            if z3.is_int_value(value):
                state[name] = value.as_long()
                continue
            if z3.is_algebraic_value(value):
                value = value.approx(20)
            frac = Fraction(value.as_fraction())
            state[name] = int(frac) if frac.denominator == 1 else str(frac)
        return state


def division_hazards(spec: RangeSpec, expression: str) -> List[str]:
    """Divisors in `expression` that can be zero where they are evaluated.

    A divisor inside a conjunction is evaluated only where the conjuncts to its left hold (as in Lean's
    short-circuit `if`), so those conjuncts and the shared domain are its path condition.
    """
    encoder = _Encoder(spec.parameters, relaxed=True)
    base = [encoder.bounds(), encoder.formula(spec.domain)]
    tree = ast.parse(desugar(expression), mode="eval").body
    hazards: List[str] = []

    def walk(node: ast.AST, path: List[ast.AST]) -> None:
        if isinstance(node, ast.BoolOp) and isinstance(node.op, ast.And):
            seen: List[ast.AST] = []
            for value in node.values:
                walk(value, path + seen)
                seen.append(value)
            return
        if isinstance(node, ast.BinOp) and isinstance(node.op, ast.Div):
            divisor = ast.unparse(node.right)
            conditions = [encoder.formula(ast.unparse(p)) for p in path]
            zero = encoder.formula(f"({divisor}) == 0")
            try:
                if formal_smt.satisfiable(*base, *conditions, zero) is not None and divisor not in hazards:
                    hazards.append(divisor)
            except SolverUndecided:
                hazards.append(f"{divisor} (undecided)")
        for child in ast.iter_child_nodes(node):
            walk(child, path)

    walk(tree, [])
    return hazards


def _rational_model(encoder: "_Encoder", model, formulas: Sequence[Any]):
    """A model with rational values where one exists near the given one.

    Nonlinear real arithmetic can return algebraic numbers. Their decimal approximation may fall outside a
    lower-dimensional difference set (a boundary such as alpha = max(...)), so the witness would not be checkable.
    Each irrational coordinate is pinned in turn to a rational approximation and the formulas are re-solved; the
    first all-rational model is returned, otherwise the original one."""

    def irrational(m):
        return [sym for sym in encoder.table.symbols.values()
                if z3.is_algebraic_value(m.eval(sym, model_completion=True))]

    pins = []
    for _ in range(len(encoder.table.symbols)):
        open_syms = irrational(model)
        if not open_syms:
            return model
        sym = open_syms[0]
        value = model.eval(sym, model_completion=True)
        for digits in (2, 4, 8, 16):
            pin = sym == z3.RealVal(str(Fraction(value.approx(digits).as_fraction())))
            try:
                candidate = formal_smt.satisfiable(*formulas, *pins, pin)
            except SolverUndecided:
                candidate = None
            if candidate is not None:
                pins.append(pin)
                model = candidate
                break
        else:
            return model
    return model


def _difference(spec: RangeSpec, inside: str, outside: str) -> tuple:
    """A point in `inside` and not in `outside`: (status, witness, method). Status is True, False or None."""
    reasons = []
    for relaxed in (False, True):
        if relaxed and not any(p.integer for p in spec.parameters):
            break
        encoder = _Encoder(spec.parameters, relaxed=relaxed)
        try:
            model = formal_smt.satisfiable(
                encoder.bounds(),
                encoder.formula(spec.domain),
                encoder.formula(inside),
                z3.Not(encoder.formula(outside)),
            )
        except SolverUndecided as exc:
            reasons.append(str(exc))
            continue
        method = "real relaxation" if relaxed else "exact"
        if model is None:
            return False, None, method, reasons
        model = _rational_model(encoder, model, [encoder.bounds(), encoder.formula(spec.domain),
                                                 encoder.formula(inside), z3.Not(encoder.formula(outside))])
        witness = encoder.decode(model)
        if relaxed and any(p.integer and not isinstance(witness[p.name], int) for p in spec.parameters):
            reasons.append(f"real relaxation found only a non-integral witness {witness}")
            return None, None, "undecided", reasons
        return True, witness, method, reasons
    return None, None, "undecided", reasons


def _nonempty(spec: RangeSpec, expression: str) -> Optional[bool]:
    status, _, _, _ = _difference(spec, expression, "False")
    return status


def _quantity(spec: RangeSpec, quantity: Quantity) -> Dict[str, Any]:
    differs = f"({spec.paper}) and ({spec.lean}) and ({quantity.paper}) != ({quantity.lean})"
    status, witness, method, reasons = _difference(spec, differs, "False")
    agreement = {True: Agreement.DIFFERS, False: Agreement.EQUAL, None: Agreement.UNDECIDED}[status]
    return {
        "paper": quantity.paper,
        "lean": quantity.lean,
        "agreement": agreement.value,
        "witness": witness,
        "method": method,
        "undecided_reasons": reasons,
    }


def compare_ranges(spec: RangeSpec) -> RangeResult:
    """Decides the relation between the paper range and the formal range of one theorem."""
    hazards = [f"paper: {d}" for d in division_hazards(spec, spec.paper)]
    hazards += [f"lean: {d}" for d in division_hazards(spec, spec.lean)]
    hazards += [f"domain: {d}" for d in division_hazards(spec, spec.domain)]
    lean_only, lean_witness, lean_method, r1 = _difference(spec, spec.lean, spec.paper)
    paper_only, paper_witness, paper_method, r2 = _difference(spec, spec.paper, spec.lean)
    reasons = r1 + r2
    if hazards:
        relation = Fidelity.UNDECIDED
        reasons.append("division by zero is reachable in the encoding; z3 would give it an arbitrary value")
    elif lean_only is None or paper_only is None:
        relation = Fidelity.UNDECIDED
    elif not lean_only and not paper_only:
        relation = Fidelity.EQUIVALENT
    elif lean_only and not paper_only:
        relation = Fidelity.STRONGER
    elif paper_only and not lean_only:
        relation = Fidelity.WEAKER
    else:
        relation = Fidelity.INCOMPARABLE
    return RangeResult(
        theorem=spec.theorem,
        relation=relation,
        paper_nonempty=_nonempty(spec, spec.paper),
        lean_nonempty=_nonempty(spec, spec.lean),
        lean_only_witness=lean_witness,
        paper_only_witness=paper_witness,
        method={"lean_minus_paper": lean_method, "paper_minus_lean": paper_method},
        division_hazards=hazards,
        quantities={q.name: _quantity(spec, q) for q in spec.quantities},
        undecided_reasons=reasons,
        paper=spec.paper,
        lean=spec.lean,
        paper_source=spec.paper_source,
        lean_source=spec.lean_source,
        encoding=list(spec.encoding),
        solver_timeout_ms=int(formal_thresholds.get("solver_timeout_ms")),
    )


# ---------------------------------------------------------------------------
# Cross-check through HypothesisEvaluator.compare on a finite slice of the integer parameters
# ---------------------------------------------------------------------------

_FROM_FORBIDDEN = {
    # compare(lean, paper) speaks about forbidden states (outside each range); a range that forbids more is smaller.
    Relation.EQUIVALENT: Fidelity.EQUIVALENT,
    Relation.STRONGER: Fidelity.WEAKER,
    Relation.WEAKER: Fidelity.STRONGER,
    Relation.INCOMPARABLE: Fidelity.INCOMPARABLE,
    Relation.CONTRADICTORY: Fidelity.INCOMPARABLE,
}


def _as_hypothesis(spec: RangeSpec, expression: str, label: str, integer_values: Dict[str, Sequence[int]]):
    variables = []
    for p in spec.parameters:
        if p.integer:
            variables.append(Variable(p.name, domain=tuple(integer_values[p.name])))
        else:
            variables.append(Variable(p.name, continuous=True, lower=p.lower, upper=p.upper))
    return Hypothesis(
        hypothesis_id=f"{spec.theorem}:{label}",
        variables=variables,
        scope=desugar(spec.domain) if spec.domain.strip() != "True" else None,
        claims=[desugar(expression)],
        statement=f"{label} range of {spec.theorem}",
    )


def cross_check(spec: RangeSpec, integer_values: Dict[str, Sequence[int]]) -> Dict[str, Any]:
    """The same question through HypothesisEvaluator.compare, with integer parameters fixed to finite values.

    Agreement with `compare_ranges` on every slice is evidence that the case-split encoding is right; it proves
    nothing beyond the listed values.
    """
    lean = _as_hypothesis(spec, spec.lean, "lean", integer_values)
    paper = _as_hypothesis(spec, spec.paper, "paper", integer_values)
    try:
        report = HypothesisEvaluator.compare(lean, paper, max_examples=2)
    except SolverUndecided as exc:
        return {
            "relation": Fidelity.UNDECIDED.value,
            "values": {k: list(v) for k, v in integer_values.items()},
            "reason": str(exc),
        }
    return {
        "relation": _FROM_FORBIDDEN[report.relation].value,
        "values": {k: list(v) for k, v in integer_values.items()},
        "examples": report.discriminating_examples,
    }
