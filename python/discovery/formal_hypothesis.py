"""
python/discovery/formal_hypothesis.py - Formal hypotheses over a finite state space (ADR-DISCOVERY-059).

A hypothesis is a conjecture about which constraints govern a phenomenon (ADR-DISCOVERY-006). Here it is
a formal object, not prose:

- variables, each with a finite domain; their product is the state space Omega;
- a scope and a list of assumptions: predicates that select the states the hypothesis speaks about;
- a list of claims: predicates that must hold in every state where the scope and the assumptions hold.

A state is *forbidden* by the hypothesis when it is in scope, satisfies every assumption and violates a
claim. Every evaluation below is exact: Omega is enumerated, so results are proofs over Omega, not samples.
Continuous quantities must be discretised into a finite domain first.

Predicates use a small expression language (comparisons, `and`/`or`/`not`, arithmetic, `in`/`not in`
over literal collections). They are interpreted over the Python AST and never passed to `eval`.
"""

from __future__ import annotations

import ast
import itertools
import math
import operator
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable, Dict, Iterator, List, Optional, Sequence, Tuple

MAX_STATES = 2_000_000
MAX_ASSUMPTIONS_FOR_CONFLICT_SEARCH = 12

State = Dict[str, Any]


class FormalHypothesisError(ValueError):
    """Raised when a hypothesis or an observation is malformed."""


# ---------------------------------------------------------------------------
# Safe predicate language
# ---------------------------------------------------------------------------

_COMPARE: Dict[type, Callable[[Any, Any], bool]] = {
    ast.Eq: operator.eq,
    ast.NotEq: operator.ne,
    ast.Lt: operator.lt,
    ast.LtE: operator.le,
    ast.Gt: operator.gt,
    ast.GtE: operator.ge,
    ast.In: lambda a, b: a in b,
    ast.NotIn: lambda a, b: a not in b,
}
_BINARY: Dict[type, Callable[[Any, Any], Any]] = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.FloorDiv: operator.floordiv,
    ast.Mod: operator.mod,
    ast.Pow: operator.pow,
}


class Predicate:
    """A boolean expression over the hypothesis variables, parsed once and interpreted safely."""

    def __init__(self, expression: str, variables: Sequence[str]):
        self.expression = expression.strip()
        if not self.expression:
            raise FormalHypothesisError("Empty predicate.")
        try:
            tree = ast.parse(self.expression, mode="eval")
        except SyntaxError as exc:
            raise FormalHypothesisError(f"Invalid predicate {expression!r}: {exc.msg}") from exc
        self._node = tree.body
        self.variables_used = self._validate(self._node, set(variables))

    def _validate(self, node: ast.AST, known: set) -> set:
        used = set()
        for child in ast.walk(node):
            if isinstance(child, ast.Name):
                if child.id in ("True", "False", "None"):
                    continue
                if child.id not in known:
                    raise FormalHypothesisError(
                        f"Unknown variable {child.id!r} in {self.expression!r}. Declared: {sorted(known)}."
                    )
                used.add(child.id)
            elif not isinstance(
                child,
                (
                    ast.Expression,
                    ast.BoolOp,
                    ast.And,
                    ast.Or,
                    ast.UnaryOp,
                    ast.Not,
                    ast.USub,
                    ast.UAdd,
                    ast.Compare,
                    ast.BinOp,
                    ast.Constant,
                    ast.Load,
                    ast.Tuple,
                    ast.List,
                    ast.Set,
                    *_COMPARE.keys(),
                    *_BINARY.keys(),
                ),
            ):
                raise FormalHypothesisError(
                    f"Unsupported construct {type(child).__name__} in {self.expression!r}. "
                    "Only comparisons, and/or/not, arithmetic and membership in literal collections are allowed."
                )
        return used

    def evaluate(self, state: State) -> bool:
        try:
            return bool(self._eval(self._node, state))
        except (ZeroDivisionError, TypeError, OverflowError) as exc:
            raise FormalHypothesisError(f"Cannot evaluate {self.expression!r} at {state}: {exc}") from exc

    def _eval(self, node: ast.AST, state: State) -> Any:
        if isinstance(node, ast.Constant):
            return node.value
        if isinstance(node, ast.Name):
            if node.id == "True":
                return True
            if node.id == "False":
                return False
            return state[node.id]
        if isinstance(node, ast.BoolOp):
            if isinstance(node.op, ast.And):
                return all(self._eval(v, state) for v in node.values)
            return any(self._eval(v, state) for v in node.values)
        if isinstance(node, ast.UnaryOp):
            value = self._eval(node.operand, state)
            if isinstance(node.op, ast.Not):
                return not value
            return -value if isinstance(node.op, ast.USub) else +value
        if isinstance(node, ast.BinOp):
            return _BINARY[type(node.op)](self._eval(node.left, state), self._eval(node.right, state))
        if isinstance(node, ast.Compare):
            left = self._eval(node.left, state)
            for op, comparator in zip(node.ops, node.comparators):
                right = self._eval(comparator, state)
                if not _COMPARE[type(op)](left, right):
                    return False
                left = right
            return True
        if isinstance(node, (ast.Tuple, ast.List, ast.Set)):
            return tuple(self._eval(e, state) for e in node.elts)
        raise FormalHypothesisError(f"Cannot evaluate {type(node).__name__}.")  # unreachable after validation

    def __repr__(self) -> str:
        return f"Predicate({self.expression!r})"


# ---------------------------------------------------------------------------
# Hypothesis
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class Variable:
    name: str
    domain: Tuple[Any, ...]

    def __post_init__(self) -> None:
        if not self.name.isidentifier():
            raise FormalHypothesisError(f"Variable name {self.name!r} is not a valid identifier.")
        if not self.domain:
            raise FormalHypothesisError(f"Variable {self.name!r} has an empty domain.")
        if len(set(self.domain)) != len(self.domain):
            raise FormalHypothesisError(f"Variable {self.name!r} has repeated domain values.")


@dataclass
class Hypothesis:
    hypothesis_id: str
    variables: List[Variable]
    claims: List[str]
    assumptions: List[str] = field(default_factory=list)
    scope: Optional[str] = None
    statement: str = ""  # Human-readable description; never evaluated.
    alternatives: List[str] = field(default_factory=list)

    def __post_init__(self) -> None:
        names = [v.name for v in self.variables]
        if not names:
            raise FormalHypothesisError("A hypothesis needs at least one variable.")
        if len(set(names)) != len(names):
            raise FormalHypothesisError("Variable names must be unique.")
        if not self.claims:
            raise FormalHypothesisError("A hypothesis needs at least one claim (a constraint it asserts).")
        self._claims = [Predicate(c, names) for c in self.claims]
        self._assumptions = [Predicate(a, names) for a in self.assumptions]
        self._scope = Predicate(self.scope, names) if self.scope else None
        if self.omega_size > MAX_STATES:
            raise FormalHypothesisError(
                f"State space has {self.omega_size:,} states; exhaustive evaluation is capped at {MAX_STATES:,}."
            )

    @property
    def variable_names(self) -> List[str]:
        return [v.name for v in self.variables]

    @property
    def omega_size(self) -> int:
        return math.prod(len(v.domain) for v in self.variables)

    def states(self) -> Iterator[State]:
        names = self.variable_names
        for values in itertools.product(*(v.domain for v in self.variables)):
            yield dict(zip(names, values))

    def applies(self, state: State) -> bool:
        """True when the state is in scope and satisfies every assumption."""
        if self._scope is not None and not self._scope.evaluate(state):
            return False
        return all(a.evaluate(state) for a in self._assumptions)

    def violated_claims(self, state: State) -> List[str]:
        return [c.expression for c in self._claims if not c.evaluate(state)]

    def forbids(self, state: State) -> bool:
        return self.applies(state) and bool(self.violated_claims(state))


# ---------------------------------------------------------------------------
# Evaluation
# ---------------------------------------------------------------------------


class ContentVerdict(str, Enum):
    VACUOUS = "VACUOUS"  # No state satisfies scope and assumptions: the hypothesis speaks about nothing.
    SELF_CONTRADICTORY = "SELF_CONTRADICTORY"  # Every applicable state is forbidden: claims contradict assumptions.
    UNFALSIFIABLE = "UNFALSIFIABLE"  # No state is forbidden: no observation could refute it.
    FALSIFIABLE = "FALSIFIABLE"


class Relation(str, Enum):
    EQUIVALENT = "EQUIVALENT"
    STRONGER = "STRONGER"  # A forbids everything B forbids, and more.
    WEAKER = "WEAKER"
    INCOMPARABLE = "INCOMPARABLE"
    CONTRADICTORY = "CONTRADICTORY"  # No state is allowed by both.


@dataclass
class EvaluationReport:
    hypothesis_id: str
    omega_size: int
    applicable_states: int
    forbidden_states: int
    content_verdict: ContentVerdict
    excluded_fraction_of_omega: float
    excluded_fraction_of_applicable: float
    conflicting_assumption_sets: List[List[str]]
    claim_exclusions: Dict[str, int]
    falsifier_examples: List[State]
    certain_counterexamples: List[Dict[str, Any]]
    possible_counterexamples: List[Dict[str, Any]]
    observations_checked: int
    is_refuted: bool

    def to_dict(self) -> Dict[str, Any]:
        return {
            "hypothesis_id": self.hypothesis_id,
            "omega_size": self.omega_size,
            "applicable_states": self.applicable_states,
            "forbidden_states": self.forbidden_states,
            "content_verdict": self.content_verdict.value,
            "excluded_fraction_of_omega": self.excluded_fraction_of_omega,
            "excluded_fraction_of_applicable": self.excluded_fraction_of_applicable,
            "conflicting_assumption_sets": self.conflicting_assumption_sets,
            "claim_exclusions": self.claim_exclusions,
            "falsifier_examples": self.falsifier_examples,
            "certain_counterexamples": self.certain_counterexamples,
            "possible_counterexamples": self.possible_counterexamples,
            "observations_checked": self.observations_checked,
            "is_refuted": self.is_refuted,
        }


@dataclass
class ComparisonReport:
    hypothesis_a: str
    hypothesis_b: str
    relation: Relation
    forbidden_only_by_a: int
    forbidden_only_by_b: int
    forbidden_by_both: int
    discriminating_examples: List[Dict[str, Any]]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "hypothesis_a": self.hypothesis_a,
            "hypothesis_b": self.hypothesis_b,
            "relation": self.relation.value,
            "forbidden_only_by_a": self.forbidden_only_by_a,
            "forbidden_only_by_b": self.forbidden_only_by_b,
            "forbidden_by_both": self.forbidden_by_both,
            "discriminating_examples": self.discriminating_examples,
        }


class HypothesisEvaluator:
    """Exact evaluation of formal hypotheses by enumeration of the state space."""

    @staticmethod
    def conflicting_assumption_sets(hypothesis: Hypothesis) -> List[List[str]]:
        """Minimal sets of assumptions (with the scope) that no state can satisfy together.

        Empty when the assumptions are jointly satisfiable. Each returned set is minimal: removing any one
        of its members makes it satisfiable. These are the premises a researcher must revise.
        """
        preds = hypothesis._assumptions
        if len(preds) > MAX_ASSUMPTIONS_FOR_CONFLICT_SEARCH:
            raise FormalHypothesisError(
                f"Conflict search is limited to {MAX_ASSUMPTIONS_FOR_CONFLICT_SEARCH} assumptions."
            )
        states = [s for s in hypothesis.states() if hypothesis._scope is None or hypothesis._scope.evaluate(s)]

        def satisfiable(subset: Sequence[Predicate]) -> bool:
            return any(all(p.evaluate(s) for p in subset) for s in states)

        if not states:
            return [[f"scope: {hypothesis.scope}"]]
        if satisfiable(preds):
            return []
        minimal: List[Tuple[int, ...]] = []
        for size in range(1, len(preds) + 1):
            for combo in itertools.combinations(range(len(preds)), size):
                if any(set(m) <= set(combo) for m in minimal):
                    continue
                if not satisfiable([preds[i] for i in combo]):
                    minimal.append(combo)
        return [[preds[i].expression for i in combo] for combo in minimal]

    @classmethod
    def evaluate(
        cls,
        hypothesis: Hypothesis,
        observations: Optional[List[State]] = None,
        max_examples: int = 5,
    ) -> EvaluationReport:
        applicable = forbidden = 0
        claim_exclusions = {c.expression: 0 for c in hypothesis._claims}
        falsifiers: List[State] = []
        for state in hypothesis.states():
            if not hypothesis.applies(state):
                continue
            applicable += 1
            violated = hypothesis.violated_claims(state)
            if violated:
                forbidden += 1
                for c in violated:
                    claim_exclusions[c] += 1
                if len(falsifiers) < max_examples:
                    falsifiers.append(state)

        if applicable == 0:
            verdict = ContentVerdict.VACUOUS
        elif forbidden == applicable:
            verdict = ContentVerdict.SELF_CONTRADICTORY
        elif forbidden == 0:
            verdict = ContentVerdict.UNFALSIFIABLE
        else:
            verdict = ContentVerdict.FALSIFIABLE

        conflicts = cls.conflicting_assumption_sets(hypothesis) if applicable == 0 else []
        certain, possible = cls.confront(hypothesis, observations or [])

        return EvaluationReport(
            hypothesis_id=hypothesis.hypothesis_id,
            omega_size=hypothesis.omega_size,
            applicable_states=applicable,
            forbidden_states=forbidden,
            content_verdict=verdict,
            excluded_fraction_of_omega=forbidden / hypothesis.omega_size,
            excluded_fraction_of_applicable=(forbidden / applicable) if applicable else 0.0,
            conflicting_assumption_sets=conflicts,
            claim_exclusions=claim_exclusions,
            falsifier_examples=falsifiers,
            certain_counterexamples=certain,
            possible_counterexamples=possible,
            observations_checked=len(observations or []),
            is_refuted=bool(certain),
        )

    @staticmethod
    def _completions(hypothesis: Hypothesis, observation: State) -> Iterator[State]:
        names = hypothesis.variable_names
        unknown = [n for n in observation if n not in names]
        if unknown:
            raise FormalHypothesisError(f"Observation uses undeclared variables: {unknown}.")
        for var in hypothesis.variables:
            if var.name in observation and observation[var.name] not in var.domain:
                raise FormalHypothesisError(
                    f"Observed value {observation[var.name]!r} for {var.name!r} is outside its domain {var.domain}."
                )
        missing = [v for v in hypothesis.variables if v.name not in observation]
        for values in itertools.product(*(v.domain for v in missing)):
            yield {**observation, **dict(zip((v.name for v in missing), values))}

    @classmethod
    def confront(
        cls, hypothesis: Hypothesis, observations: List[State]
    ) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
        """Modus tollens against observations.

        An observation is a *certain* counterexample when every completion of its unobserved variables is
        forbidden, and a *possible* one when only some completions are. For each counterexample the report
        lists the violated claims and the assumptions that made the hypothesis applicable: under
        Duhem-Quine, either a claim is wrong or one of those auxiliaries does not hold in that case.
        """
        certain: List[Dict[str, Any]] = []
        possible: List[Dict[str, Any]] = []
        for index, observation in enumerate(observations):
            completions = list(cls._completions(hypothesis, observation))
            forbidden = [s for s in completions if hypothesis.forbids(s)]
            if not forbidden:
                continue
            record = {
                "observation_index": index,
                "observation": observation,
                "violated_claims": sorted({c for s in forbidden for c in hypothesis.violated_claims(s)}),
                "auxiliaries_in_question": list(hypothesis.assumptions),
                "forbidden_completions": len(forbidden),
                "total_completions": len(completions),
            }
            (certain if len(forbidden) == len(completions) else possible).append(record)
        return certain, possible

    @staticmethod
    def compare(a: Hypothesis, b: Hypothesis, max_examples: int = 5) -> ComparisonReport:
        """Logical relation between two hypotheses over the same state space."""
        spec_a = [(v.name, tuple(v.domain)) for v in a.variables]
        spec_b = [(v.name, tuple(v.domain)) for v in b.variables]
        if spec_a != spec_b:
            raise FormalHypothesisError("Hypotheses can only be compared over the same variables and domains.")
        only_a = only_b = both = allowed_by_both = 0
        examples: List[Dict[str, Any]] = []
        for state in a.states():
            fa, fb = a.forbids(state), b.forbids(state)
            if fa and fb:
                both += 1
            elif fa or fb:
                if fa:
                    only_a += 1
                else:
                    only_b += 1
                if len(examples) < max_examples:
                    examples.append({"state": state, "forbidden_by": a.hypothesis_id if fa else b.hypothesis_id})
            if not fa and not fb:
                allowed_by_both += 1

        if allowed_by_both == 0:
            relation = Relation.CONTRADICTORY
        elif only_a == 0 and only_b == 0:
            relation = Relation.EQUIVALENT
        elif only_b == 0:
            relation = Relation.STRONGER
        elif only_a == 0:
            relation = Relation.WEAKER
        else:
            relation = Relation.INCOMPARABLE
        return ComparisonReport(
            hypothesis_a=a.hypothesis_id,
            hypothesis_b=b.hypothesis_id,
            relation=relation,
            forbidden_only_by_a=only_a,
            forbidden_only_by_b=only_b,
            forbidden_by_both=both,
            discriminating_examples=examples,
        )
