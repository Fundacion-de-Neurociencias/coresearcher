"""
python/discovery/formal_lean.py - Lean 4 export of formal-hypothesis consequences (ADR-DISCOVERY-060).

`HypothesisEvaluator.entails` decides a consequence with z3. This module states the same consequence as a Lean 4
theorem over the reals, so an independent kernel can check it. Nothing here runs Lean: the theorem is checked by
`lake env lean` on a machine with Mathlib (see docs/reference/benchmarks/LEGION_RUNBOOK.md), and until then its
status is NOT_KERNEL_CHECKED. A failed tactic means "not proved by this tactic", never "false".

Supported: continuous variables and finite numeric variables (a finite domain becomes a disjunction hypothesis).
String and boolean variables have no faithful real encoding here and are rejected.
"""

from __future__ import annotations

import ast
from fractions import Fraction
from typing import List

from python.discovery.formal_hypothesis import FormalHypothesisError, Hypothesis, Predicate

_CMP = {ast.Eq: "=", ast.NotEq: "≠", ast.Lt: "<", ast.LtE: "≤", ast.Gt: ">", ast.GtE: "≥"}
_BIN = {ast.Add: "+", ast.Sub: "-", ast.Mult: "*", ast.Div: "/"}
DEFAULT_TACTIC = "first | linarith | nlinarith [sq_nonneg ({vars_sum}), sq_nonneg ({vars_diff})] | positivity"


def _number(value) -> str:
    frac = Fraction(value).limit_denominator(10**12)
    text = str(frac.numerator) if frac.denominator == 1 else f"{frac.numerator}/{frac.denominator}"
    return f"({text} : ℝ)"


def _lean(node, expression: str) -> str:
    if isinstance(node, ast.Constant):
        if isinstance(node.value, bool):
            return "True" if node.value else "False"
        if isinstance(node.value, (int, float)):
            return _number(node.value)
        raise FormalHypothesisError(f"String constants cannot be exported to Lean ({expression!r}).")
    if isinstance(node, ast.Name):
        return node.id
    if isinstance(node, ast.BoolOp):
        joiner = " ∧ " if isinstance(node.op, ast.And) else " ∨ "
        return "(" + joiner.join(_lean(v, expression) for v in node.values) + ")"
    if isinstance(node, ast.UnaryOp):
        inner = _lean(node.operand, expression)
        if isinstance(node.op, ast.Not):
            return f"¬{inner}"
        return f"(-{inner})" if isinstance(node.op, ast.USub) else inner
    if isinstance(node, ast.BinOp):
        if isinstance(node.op, ast.Pow):
            if not (
                isinstance(node.right, ast.Constant) and isinstance(node.right.value, int) and node.right.value >= 0
            ):
                raise FormalHypothesisError(f"Only constant natural powers can be exported ({expression!r}).")
            return f"({_lean(node.left, expression)} ^ {node.right.value})"
        if type(node.op) not in _BIN:
            raise FormalHypothesisError(f"Operator {type(node.op).__name__} cannot be exported to Lean.")
        return f"({_lean(node.left, expression)} {_BIN[type(node.op)]} {_lean(node.right, expression)})"
    if isinstance(node, ast.Compare):
        parts, left = [], node.left
        for op, right in zip(node.ops, node.comparators):
            if isinstance(op, (ast.In, ast.NotIn)):
                if not isinstance(right, (ast.Tuple, ast.List, ast.Set)) or not right.elts:
                    raise FormalHypothesisError(f"'in' needs a non-empty literal collection ({expression!r}).")
                member = " ∨ ".join(f"{_lean(left, expression)} = {_lean(e, expression)}" for e in right.elts)
                parts.append(f"({member})" if isinstance(op, ast.In) else f"¬({member})")
            else:
                parts.append(f"{_lean(left, expression)} {_CMP[type(op)]} {_lean(right, expression)}")
            left = right
        return "(" + " ∧ ".join(parts) + ")"
    raise FormalHypothesisError(f"{type(node).__name__} cannot be exported to Lean ({expression!r}).")


def predicate_to_lean(predicate: Predicate) -> str:
    return _lean(predicate._node, predicate.expression)


def consequence_theorem(hypothesis: Hypothesis, consequence: str, theorem_name: str = "", tactic: str = "") -> str:
    """A self-contained Lean 4 file stating: domains, scope, assumptions and claims imply the consequence."""
    names = hypothesis.variable_names
    premises: List[str] = []
    for var in hypothesis.variables:
        if var.continuous:
            if var.lower is not None:
                premises.append(f"{_number(var.lower)} ≤ {var.name}")
            if var.upper is not None:
                premises.append(f"{var.name} ≤ {_number(var.upper)}")
            continue
        if not all(isinstance(v, (int, float)) and not isinstance(v, bool) for v in var.domain):
            raise FormalHypothesisError(f"Variable {var.name!r} is not numeric; it cannot be exported to Lean.")
        premises.append("(" + " ∨ ".join(f"{var.name} = {_number(v)}" for v in var.domain) + ")")
    if hypothesis._scope is not None:
        premises.append(predicate_to_lean(hypothesis._scope))
    premises += [predicate_to_lean(p) for p in hypothesis._assumptions]
    premises += [predicate_to_lean(p) for p in hypothesis._claims]
    goal = predicate_to_lean(Predicate(consequence, names))

    name = theorem_name or "".join(c if c.isalnum() else "_" for c in f"{hypothesis.hypothesis_id}_entails")
    binders = " ".join(f"({n} : ℝ)" for n in names)
    hyps = "\n".join(f"    (h{i} : {p})" for i, p in enumerate(premises))
    tactic = tactic or DEFAULT_TACTIC.format(vars_sum=" + ".join(names), vars_diff=" - ".join(names))
    return (
        "import Mathlib\n\n"
        f"-- Generated from formal hypothesis {hypothesis.hypothesis_id!r} by python/discovery/formal_lean.py.\n"
        "-- Status: NOT_KERNEL_CHECKED until compiled with `lake env lean` against Mathlib.\n"
        f"theorem {name} {binders}\n{hyps} :\n    {goal} := by\n  {tactic}\n"
    )
