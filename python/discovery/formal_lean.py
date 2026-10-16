"""
python/discovery/formal_lean.py - Lean 4 export of formal-hypothesis consequences (ADR-DISCOVERY-060).

`HypothesisEvaluator.entails` decides a consequence with z3. This module states the same consequence as a Lean 4
theorem over the reals, so an independent kernel can check it. Nothing here runs Lean: the theorem is checked by
`lake env lean` on a machine with Mathlib (see docs/reference/benchmarks/LEGION_RUNBOOK.md), and until then its
status is NOT_KERNEL_CHECKED. A failed tactic means "not proved by this tactic", never "false".

The default proof script (`default_tactic`) is built from the shape of the consequence: premises are split into
cases, conjunctions are proved part by part, negations are introduced and refuted, and disjunctions are tried side
by side, by contradiction, and (for equalities) through a vanishing product. Checked against Lean v4.35 + Mathlib.

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
# Closes one arithmetic goal (or False) from the context. Round 0 used this alone as the whole proof script; it is
# now the leaf closer of `default_tactic`. `norm_num` must close the goal: it can succeed while leaving one open.
_LEAF = "first | linarith | nlinarith [sq_nonneg ({vars_sum}), sq_nonneg ({vars_diff})] | positivity | (norm_num; done)"
# Splits conjunctive and disjunctive premises (finite domains, `in`, `or`) into one goal per case.
_SPLIT_PREMISES = "casesm* _ ∧ _, _ ∨ _"
# Turns a negated disjunction into a conjunction of strict comparisons. `push_neg` is avoided on purpose: it was
# deprecated in Mathlib for Lean v4.35, and these simp lemmas behave the same on every version.
_PUSH_NOT = "simp only [not_or, not_and_or, not_le, not_lt] at hne"


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


def _conjuncts(node) -> List:
    """The parts of a goal that `_lean` renders as a conjunction (and-expressions and comparison chains)."""
    if isinstance(node, ast.BoolOp) and isinstance(node.op, ast.And):
        return list(node.values)
    if isinstance(node, ast.Compare) and len(node.ops) > 1:
        parts, left = [], node.left
        for op, right in zip(node.ops, node.comparators):
            parts.append(ast.Compare(left=left, ops=[op], comparators=[right]))
            left = right
        return parts
    return [node]


def _disjuncts(node) -> List:
    """The parts of a goal that `_lean` renders as a disjunction (or-expressions and `x in (...)`)."""
    if isinstance(node, ast.BoolOp) and isinstance(node.op, ast.Or):
        return list(node.values)
    if isinstance(node, ast.Compare) and len(node.ops) == 1 and isinstance(node.ops[0], ast.In):
        return [ast.Compare(left=node.left, ops=[ast.Eq()], comparators=[e]) for e in node.comparators[0].elts]
    return [node]


def _is_negation(node) -> bool:
    if isinstance(node, ast.UnaryOp) and isinstance(node.op, ast.Not):
        return True
    return isinstance(node, ast.Compare) and len(node.ops) == 1 and isinstance(node.ops[0], (ast.NotEq, ast.NotIn))


def _is_equality(node) -> bool:
    return isinstance(node, ast.Compare) and len(node.ops) == 1 and isinstance(node.ops[0], ast.Eq)


def _goal_tactic(node, leaf: str) -> str:
    """A one-line tactic for a goal, following its shape.

    Conjunctions are proved part by part. A negation (`¬`, `≠`, `not in`) is introduced and refuted. A disjunction
    is tried side by side, then by contradiction: its negation is turned into a conjunction of strict comparisons
    that linarith can use. Negated equalities are useless to linarith, so a disjunction of equalities
    `a₁ = b₁ ∨ … ∨ aₙ = bₙ` is also tried through `(a₁ - b₁) * … * (aₙ - bₙ) = 0`, which closes polynomial-root
    goals such as `s*s - 3*s + 2 = 0 → s = 1 ∨ s = 2`.
    """
    parts = _conjuncts(node)
    if len(parts) > 1:
        # `refine` + `focus … done` rather than `exact ⟨by …, by …⟩`: a failure inside a nested `by` term is logged
        # rather than raised, so an enclosing `first` would not backtrack to its next alternative. Each `focus` is
        # parenthesised because `focus` takes the rest of the sequence as its argument.
        holes = ", ".join("?_" for _ in parts)
        return f"(refine ⟨{holes}⟩; " + "; ".join(f"(focus ({_goal_tactic(p, leaf)}; done))" for p in parts) + ")"
    if _is_negation(node):
        return f"(intro hc; (try {_SPLIT_PREMISES}); all_goals ({leaf}))"
    options = _disjuncts(node)
    if len(options) == 1:
        return leaf
    return "first | " + " | ".join(_disjunction_attempts(options, leaf))


def _disjunction_attempts(options: List, leaf: str) -> List[str]:
    head, rest = options[0], options[1:]
    rest_tactic = (
        _goal_tactic(rest[0], leaf) if len(rest) == 1 else "first | " + " | ".join(_disjunction_attempts(rest, leaf))
    )
    attempts = [f"(left; ({_goal_tactic(head, leaf)}); done)", f"(right; ({rest_tactic}); done)"]
    attempts.append(f"(by_contra hne; {_PUSH_NOT}; (try {_SPLIT_PREMISES}); all_goals ({leaf}))")
    if all(_is_equality(o) for o in options):
        names = [f"hne{i}" for i in range(len(options))]
        product = f"(sub_ne_zero.mpr {names[0]})"
        for n in names[1:]:
            product = f"(mul_ne_zero {product} (sub_ne_zero.mpr {n}))"
        attempts.append(
            f"(by_contra hne; simp only [not_or] at hne; obtain ⟨{', '.join(names)}⟩ := hne; refine {product} ?_; {leaf})"
        )
    return attempts


def default_tactic(goal: Predicate, variable_names: List[str]) -> str:
    """The default proof script: split the premises into cases, then prove the goal following its shape."""
    leaf = _LEAF.format(vars_sum=" + ".join(variable_names), vars_diff=" - ".join(variable_names))
    return "\n".join(
        [
            f"try {_SPLIT_PREMISES}",
            "all_goals (try subst_vars)",
            f"all_goals ({_goal_tactic(goal._node, leaf)})",
        ]
    )


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
    goal_predicate = Predicate(consequence, names)
    goal = predicate_to_lean(goal_predicate)

    name = theorem_name or "".join(c if c.isalnum() else "_" for c in f"{hypothesis.hypothesis_id}_entails")
    binders = " ".join(f"({n} : ℝ)" for n in names)
    hyps = "\n".join(f"    (h{i} : {p})" for i, p in enumerate(premises))
    tactic = tactic or default_tactic(goal_predicate, names)
    body = "\n".join(f"  {line}" for line in tactic.splitlines())
    return (
        "import Mathlib\n\n"
        f"-- Generated from formal hypothesis {hypothesis.hypothesis_id!r} by python/discovery/formal_lean.py.\n"
        "-- Status: NOT_KERNEL_CHECKED until compiled with `lake env lean` against Mathlib.\n"
        f"theorem {name} {binders}\n{hyps} :\n    {goal} := by\n{body}\n"
    )
