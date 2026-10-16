"""
python/discovery/formal_hypothesis.py - Formal hypotheses over a state space (ADR-DISCOVERY-059, ADR-DISCOVERY-060).

A hypothesis is a conjecture about which constraints govern a phenomenon (ADR-DISCOVERY-006). Here it is
a formal object, not prose:

- variables, each with a finite domain or a continuous (real) range; their product is the state space Omega;
- a scope and a list of assumptions: predicates that select the states the hypothesis speaks about;
- a list of claims: predicates that must hold in every state where the scope and the assumptions hold.

A state is *forbidden* by the hypothesis when it is in scope, satisfies every assumption and violates a
claim. Every evaluation below is exact. When all variables are finite, Omega is enumerated. When any variable
is continuous, the questions are posed to the z3 SMT solver (`formal_smt`), which decides them over the reals;
state counts and excluded fractions are then undefined and reported as None. Either way the results are proofs
over Omega, not samples.

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


class _LowercaseBooleans(ast.NodeTransformer):
    """Reads `true` and `false` as the constants True and False, unless a variable has that name.

    Language models trained on JSON write the lowercase forms; in round 0 they made 3 of qwen2.5:14b's 4 invalid
    outputs. Accepting them changes no meaning, so it is done here rather than by asking the model in the prompt.
    """

    def __init__(self, variables: set):
        self.variables = variables

    def visit_Name(self, node: ast.Name) -> ast.AST:
        if node.id in ("true", "false") and node.id not in self.variables:
            return ast.copy_location(ast.Constant(node.id == "true"), node)
        return node


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
        self._node = _LowercaseBooleans(set(variables)).visit(tree).body
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
    """A finite variable (`domain`) or a continuous real one (`continuous=True`, optional closed bounds)."""

    name: str
    domain: Tuple[Any, ...] = ()
    continuous: bool = False
    lower: Optional[float] = None
    upper: Optional[float] = None

    def __post_init__(self) -> None:
        if not self.name.isidentifier():
            raise FormalHypothesisError(f"Variable name {self.name!r} is not a valid identifier.")
        if self.continuous:
            if self.domain:
                raise FormalHypothesisError(f"Continuous variable {self.name!r} cannot also have a finite domain.")
            for bound in (self.lower, self.upper):
                if bound is not None and (isinstance(bound, bool) or not isinstance(bound, (int, float))):
                    raise FormalHypothesisError(f"Bounds of {self.name!r} must be numbers.")
                if bound is not None and not math.isfinite(bound):
                    raise FormalHypothesisError(f"Bounds of {self.name!r} must be finite; omit a bound instead.")
            if self.lower is not None and self.upper is not None and self.lower > self.upper:
                raise FormalHypothesisError(f"Variable {self.name!r} has lower bound above its upper bound.")
            return
        if self.lower is not None or self.upper is not None:
            raise FormalHypothesisError(f"Bounds on {self.name!r} need continuous=True.")
        if not self.domain:
            raise FormalHypothesisError(f"Variable {self.name!r} has an empty domain.")
        if len(set(self.domain)) != len(self.domain):
            raise FormalHypothesisError(f"Variable {self.name!r} has repeated domain values.")

    @property
    def is_continuous(self) -> bool:
        return self.continuous


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
        if self.is_continuous:
            from python.discovery import formal_smt

            formal_smt.encode(self)  # Fails early on constructs the SMT back end cannot decide.
        elif self.omega_size > MAX_STATES:
            raise FormalHypothesisError(
                f"State space has {self.omega_size:,} states; exhaustive evaluation is capped at {MAX_STATES:,}."
            )

    @property
    def variable_names(self) -> List[str]:
        return [v.name for v in self.variables]

    @property
    def is_continuous(self) -> bool:
        return any(v.is_continuous for v in self.variables)

    @property
    def omega_size(self) -> Optional[int]:
        """Number of states, or None when a variable is continuous."""
        if self.is_continuous:
            return None
        return math.prod(len(v.domain) for v in self.variables)

    def states(self) -> Iterator[State]:
        if self.is_continuous:
            raise FormalHypothesisError("A hypothesis with continuous variables cannot be enumerated.")
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
    backend: str  # "enumeration" or "smt"
    omega_size: Optional[int]  # None when a variable is continuous.
    applicable_states: Optional[int]
    forbidden_states: Optional[int]
    content_verdict: ContentVerdict
    excluded_fraction_of_omega: Optional[float]
    excluded_fraction_of_applicable: Optional[float]
    conflicting_assumption_sets: List[List[str]]
    claim_exclusions: Dict[str, Optional[int]]  # States each claim forbids; None under the SMT back end.
    claims_with_content: List[str]  # Claims that forbid at least one applicable state.
    falsifier_examples: List[State]
    certain_counterexamples: List[Dict[str, Any]]
    possible_counterexamples: List[Dict[str, Any]]
    observations_checked: int
    is_refuted: bool

    def to_dict(self) -> Dict[str, Any]:
        return {
            "hypothesis_id": self.hypothesis_id,
            "backend": self.backend,
            "omega_size": self.omega_size,
            "applicable_states": self.applicable_states,
            "forbidden_states": self.forbidden_states,
            "content_verdict": self.content_verdict.value,
            "excluded_fraction_of_omega": self.excluded_fraction_of_omega,
            "excluded_fraction_of_applicable": self.excluded_fraction_of_applicable,
            "conflicting_assumption_sets": self.conflicting_assumption_sets,
            "claim_exclusions": self.claim_exclusions,
            "claims_with_content": self.claims_with_content,
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
    backend: str
    relation: Relation
    forbidden_only_by_a: Optional[int]  # Counts are None under the SMT back end.
    forbidden_only_by_b: Optional[int]
    forbidden_by_both: Optional[int]
    discriminating_examples: List[Dict[str, Any]]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "hypothesis_a": self.hypothesis_a,
            "hypothesis_b": self.hypothesis_b,
            "backend": self.backend,
            "relation": self.relation.value,
            "forbidden_only_by_a": self.forbidden_only_by_a,
            "forbidden_only_by_b": self.forbidden_only_by_b,
            "forbidden_by_both": self.forbidden_by_both,
            "discriminating_examples": self.discriminating_examples,
        }


@dataclass
class ConsequenceReport:
    """Whether a predicate follows from a hypothesis: it holds in every applicable state the hypothesis allows."""

    hypothesis_id: str
    consequence: str
    backend: str
    entailed: bool
    follows_from_claims: bool  # Entailed, and not already implied by domains, scope and assumptions alone.
    vacuous: bool  # No applicable state is allowed, so everything is entailed trivially.
    counterexamples: List[State]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "hypothesis_id": self.hypothesis_id,
            "consequence": self.consequence,
            "backend": self.backend,
            "entailed": self.entailed,
            "follows_from_claims": self.follows_from_claims,
            "vacuous": self.vacuous,
            "counterexamples": self.counterexamples,
        }


_BACKENDS = ("auto", "enumeration", "smt")


def _use_smt(backend: str, *hypotheses: Hypothesis) -> bool:
    if backend not in _BACKENDS:
        raise FormalHypothesisError(f"Unknown backend {backend!r}; use one of {_BACKENDS}.")
    continuous = any(h.is_continuous for h in hypotheses)
    if backend == "enumeration" and continuous:
        raise FormalHypothesisError("Hypotheses with continuous variables need the SMT back end.")
    return backend == "smt" or continuous


def _verdict(applicable: bool, all_forbidden: bool, none_forbidden: bool) -> ContentVerdict:
    if not applicable:
        return ContentVerdict.VACUOUS
    if all_forbidden:
        return ContentVerdict.SELF_CONTRADICTORY
    if none_forbidden:
        return ContentVerdict.UNFALSIFIABLE
    return ContentVerdict.FALSIFIABLE


def _relation(allowed_by_both: bool, only_a: bool, only_b: bool) -> Relation:
    # Equivalence first: two identical self-contradictory hypotheses forbid the same states and are EQUIVALENT,
    # even though no state is allowed by both.
    if not only_a and not only_b:
        return Relation.EQUIVALENT
    if not allowed_by_both:
        return Relation.CONTRADICTORY
    if not only_b:
        return Relation.STRONGER
    if not only_a:
        return Relation.WEAKER
    return Relation.INCOMPARABLE


def _minimal_unsatisfiable(labels: List[str], satisfiable: Callable[[Sequence[int]], bool]) -> List[List[str]]:
    """Minimal subsets of the indexed premises that are jointly unsatisfiable, smallest first."""
    if len(labels) > MAX_ASSUMPTIONS_FOR_CONFLICT_SEARCH:
        raise FormalHypothesisError(f"Conflict search is limited to {MAX_ASSUMPTIONS_FOR_CONFLICT_SEARCH} assumptions.")
    if satisfiable(range(len(labels))):
        return []
    minimal: List[Tuple[int, ...]] = []
    for size in range(1, len(labels) + 1):
        for combo in itertools.combinations(range(len(labels)), size):
            if any(set(m) <= set(combo) for m in minimal):
                continue
            if not satisfiable(combo):
                minimal.append(combo)
    return [[labels[i] for i in combo] for combo in minimal]


class HypothesisEvaluator:
    """Exact evaluation of formal hypotheses, by enumeration of Omega or by SMT over the reals.

    `backend="auto"` enumerates when every variable is finite and uses SMT otherwise. `"smt"` can be forced on
    finite hypotheses, which is how the two back ends are cross-checked.
    """

    @staticmethod
    def conflicting_assumption_sets(hypothesis: Hypothesis, backend: str = "auto") -> List[List[str]]:
        """Minimal sets of assumptions (with the scope) that no state can satisfy together.

        Empty when the assumptions are jointly satisfiable. Each returned set is minimal: removing any one
        of its members makes it satisfiable. These are the premises a researcher must revise.
        """
        labels = [p.expression for p in hypothesis._assumptions]
        if _use_smt(backend, hypothesis):
            from python.discovery import formal_smt

            enc = formal_smt.encode(hypothesis)
            if formal_smt.satisfiable(enc.domain, enc.scope) is None:
                return [[f"scope: {hypothesis.scope}"]]
            return _minimal_unsatisfiable(
                labels,
                lambda idx: formal_smt.satisfiable(enc.domain, enc.scope, *[enc.assumptions[i] for i in idx])
                is not None,
            )
        states = [s for s in hypothesis.states() if hypothesis._scope is None or hypothesis._scope.evaluate(s)]
        if not states:
            return [[f"scope: {hypothesis.scope}"]]
        preds = hypothesis._assumptions
        return _minimal_unsatisfiable(labels, lambda idx: any(all(preds[i].evaluate(s) for i in idx) for s in states))

    @classmethod
    def evaluate(
        cls,
        hypothesis: Hypothesis,
        observations: Optional[List[State]] = None,
        max_examples: int = 5,
        backend: str = "auto",
    ) -> EvaluationReport:
        observations = observations or []
        if _use_smt(backend, hypothesis):
            return cls._evaluate_smt(hypothesis, observations, max_examples)
        applicable = forbidden = 0
        claim_exclusions: Dict[str, Optional[int]] = {c.expression: 0 for c in hypothesis._claims}
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

        verdict = _verdict(applicable > 0, forbidden == applicable, forbidden == 0)
        conflicts = cls.conflicting_assumption_sets(hypothesis, "enumeration") if applicable == 0 else []
        certain, possible = cls.confront(hypothesis, observations, backend="enumeration")

        return EvaluationReport(
            hypothesis_id=hypothesis.hypothesis_id,
            backend="enumeration",
            omega_size=hypothesis.omega_size,
            applicable_states=applicable,
            forbidden_states=forbidden,
            content_verdict=verdict,
            excluded_fraction_of_omega=forbidden / hypothesis.omega_size,
            excluded_fraction_of_applicable=(forbidden / applicable) if applicable else 0.0,
            conflicting_assumption_sets=conflicts,
            claim_exclusions=claim_exclusions,
            claims_with_content=[c for c, n in claim_exclusions.items() if n],
            falsifier_examples=falsifiers,
            certain_counterexamples=certain,
            possible_counterexamples=possible,
            observations_checked=len(observations),
            is_refuted=bool(certain),
        )

    @classmethod
    def _evaluate_smt(cls, hypothesis: Hypothesis, observations: List[State], max_examples: int) -> EvaluationReport:
        from python.discovery import formal_smt

        z3 = formal_smt.z3
        enc = formal_smt.encode(hypothesis)
        applicable = formal_smt.satisfiable(enc.applies) is not None
        allowed = applicable and formal_smt.satisfiable(enc.applies, enc.claims_hold) is not None
        falsifiers = formal_smt.models(enc.forbidden, enc.table, max_examples) if applicable else []
        content = [
            p.expression
            for p, f in zip(hypothesis._claims, enc.claims)
            if applicable and formal_smt.satisfiable(enc.applies, z3.Not(f)) is not None
        ]
        certain, possible = cls.confront(hypothesis, observations, backend="smt")
        return EvaluationReport(
            hypothesis_id=hypothesis.hypothesis_id,
            backend="smt",
            omega_size=hypothesis.omega_size,
            applicable_states=None,
            forbidden_states=None,
            content_verdict=_verdict(applicable, not allowed, not falsifiers),
            excluded_fraction_of_omega=None,
            excluded_fraction_of_applicable=None,
            conflicting_assumption_sets=[] if applicable else cls.conflicting_assumption_sets(hypothesis, "smt"),
            claim_exclusions={p.expression: None for p in hypothesis._claims},
            claims_with_content=content,
            falsifier_examples=falsifiers,
            certain_counterexamples=certain,
            possible_counterexamples=possible,
            observations_checked=len(observations),
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
        cls, hypothesis: Hypothesis, observations: List[State], backend: str = "auto"
    ) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
        """Modus tollens against observations.

        An observation is a *certain* counterexample when every completion of its unobserved variables is
        forbidden, and a *possible* one when only some completions are. For each counterexample the report
        lists the violated claims and the assumptions that made the hypothesis applicable: under
        Duhem-Quine, either a claim is wrong or one of those auxiliaries does not hold in that case.
        Completion counts are None under the SMT back end.
        """
        certain: List[Dict[str, Any]] = []
        possible: List[Dict[str, Any]] = []
        smt = _use_smt(backend, hypothesis)
        if smt:
            from python.discovery import formal_smt

            z3 = formal_smt.z3
            enc = formal_smt.encode(hypothesis)
        for index, observation in enumerate(observations):
            if smt:
                fixed = enc.table.fix(observation)
                if formal_smt.satisfiable(enc.domain, fixed, enc.forbidden) is None:
                    continue
                is_certain = formal_smt.satisfiable(enc.domain, fixed, z3.Not(enc.forbidden)) is None
                violated = sorted(
                    p.expression
                    for p, f in zip(hypothesis._claims, enc.claims)
                    if formal_smt.satisfiable(fixed, enc.applies, z3.Not(f)) is not None
                )
                n_forbidden = n_total = None
            else:
                completions = list(cls._completions(hypothesis, observation))
                forbidden = [s for s in completions if hypothesis.forbids(s)]
                if not forbidden:
                    continue
                is_certain = len(forbidden) == len(completions)
                violated = sorted({c for s in forbidden for c in hypothesis.violated_claims(s)})
                n_forbidden, n_total = len(forbidden), len(completions)
            record = {
                "observation_index": index,
                "observation": observation,
                "violated_claims": violated,
                "auxiliaries_in_question": list(hypothesis.assumptions),
                "forbidden_completions": n_forbidden,
                "total_completions": n_total,
            }
            (certain if is_certain else possible).append(record)
        return certain, possible

    @staticmethod
    def _same_space(a: Hypothesis, b: Hypothesis) -> None:
        def spec(h: Hypothesis):
            return [(v.name, tuple(v.domain), v.continuous, v.lower, v.upper) for v in h.variables]

        if spec(a) != spec(b):
            raise FormalHypothesisError("Hypotheses can only be compared over the same variables and domains.")

    @classmethod
    def compare(cls, a: Hypothesis, b: Hypothesis, max_examples: int = 5, backend: str = "auto") -> ComparisonReport:
        """Logical relation between two hypotheses over the same state space."""
        cls._same_space(a, b)
        if _use_smt(backend, a, b):
            return cls._compare_smt(a, b, max_examples)
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
        return ComparisonReport(
            hypothesis_a=a.hypothesis_id,
            hypothesis_b=b.hypothesis_id,
            backend="enumeration",
            relation=_relation(allowed_by_both > 0, only_a > 0, only_b > 0),
            forbidden_only_by_a=only_a,
            forbidden_only_by_b=only_b,
            forbidden_by_both=both,
            discriminating_examples=examples,
        )

    @staticmethod
    def _compare_smt(a: Hypothesis, b: Hypothesis, max_examples: int) -> ComparisonReport:
        from python.discovery import formal_smt

        z3 = formal_smt.z3
        ea, eb = formal_smt.encode(a), formal_smt.encode(b)
        only_a = formal_smt.models(z3.And(ea.forbidden, z3.Not(eb.forbidden)), ea.table, max_examples)
        only_b = formal_smt.models(z3.And(eb.forbidden, z3.Not(ea.forbidden)), ea.table, max_examples)
        allowed_by_both = formal_smt.satisfiable(ea.domain, z3.Not(ea.forbidden), z3.Not(eb.forbidden)) is not None
        examples = [
            {"state": s, "forbidden_by": hid}
            for pair in itertools.zip_longest(only_a, only_b)
            for s, hid in zip(pair, (a.hypothesis_id, b.hypothesis_id))
            if s is not None
        ]
        return ComparisonReport(
            hypothesis_a=a.hypothesis_id,
            hypothesis_b=b.hypothesis_id,
            backend="smt",
            relation=_relation(allowed_by_both, bool(only_a), bool(only_b)),
            forbidden_only_by_a=None,
            forbidden_only_by_b=None,
            forbidden_by_both=None,
            discriminating_examples=examples[:max_examples],
        )

    @staticmethod
    def entails(
        hypothesis: Hypothesis, consequence: str, max_examples: int = 5, backend: str = "auto"
    ) -> ConsequenceReport:
        """Checks whether `consequence` holds in every applicable state the hypothesis allows.

        This is how a derived prediction is checked: if the claims are true where the hypothesis applies, must
        the consequence hold there too? `follows_from_claims` separates real consequences of the claims from
        statements already implied by the domains, scope and assumptions alone.
        """
        predicate = Predicate(consequence, hypothesis.variable_names)
        if _use_smt(backend, hypothesis):
            from python.discovery import formal_smt

            z3 = formal_smt.z3
            enc = formal_smt.encode(hypothesis)
            target = formal_smt.to_z3(predicate, enc.table)
            vacuous = formal_smt.satisfiable(enc.applies, enc.claims_hold) is None
            counter = formal_smt.models(z3.And(enc.applies, enc.claims_hold, z3.Not(target)), enc.table, max_examples)
            implied_without_claims = formal_smt.satisfiable(enc.applies, z3.Not(target)) is None
            name = "smt"
        else:
            applicable = [s for s in hypothesis.states() if hypothesis.applies(s)]
            allowed = [s for s in applicable if not hypothesis.violated_claims(s)]
            vacuous = not allowed
            counter = [s for s in allowed if not predicate.evaluate(s)][:max_examples]
            implied_without_claims = all(predicate.evaluate(s) for s in applicable)
            name = "enumeration"
        entailed = not counter
        return ConsequenceReport(
            hypothesis_id=hypothesis.hypothesis_id,
            consequence=predicate.expression,
            backend=name,
            entailed=entailed,
            follows_from_claims=entailed and not vacuous and not implied_without_claims,
            vacuous=vacuous,
            counterexamples=counter,
        )


_SCALARS = (str, int, float, bool)


def hypothesis_from_dict(data: Dict[str, Any]) -> Hypothesis:
    """Builds a Hypothesis from its JSON form (the API schema and the formalizer output share it)."""
    if not isinstance(data, dict):
        raise FormalHypothesisError("A hypothesis must be a JSON object.")
    raw_vars = data.get("variables")
    if not isinstance(raw_vars, list):
        raise FormalHypothesisError("'variables' must be a list.")
    variables = []
    for v in raw_vars:
        if not isinstance(v, dict) or not isinstance(v.get("name"), str):
            raise FormalHypothesisError("Each variable needs a string 'name'.")
        domain = v.get("domain") or []
        if not isinstance(domain, list) or not all(isinstance(value, _SCALARS) for value in domain):
            raise FormalHypothesisError(f"Domain of {v['name']!r} must contain only strings, numbers or booleans.")
        variables.append(
            Variable(v["name"], tuple(domain), bool(v.get("continuous", False)), v.get("lower"), v.get("upper"))
        )
    for key in ("claims", "assumptions", "alternatives"):
        value = data.get(key, [])
        if not isinstance(value, list) or not all(isinstance(x, str) for x in value):
            raise FormalHypothesisError(f"'{key}' must be a list of strings.")
    scope = data.get("scope")
    if scope is not None and not isinstance(scope, str):
        raise FormalHypothesisError("'scope' must be a string or null.")
    return Hypothesis(
        hypothesis_id=str(data.get("hypothesis_id") or "H"),
        variables=variables,
        claims=list(data.get("claims", [])),
        assumptions=list(data.get("assumptions", [])),
        scope=scope or None,
        statement=str(data.get("statement", "")),
        alternatives=list(data.get("alternatives", [])),
    )
