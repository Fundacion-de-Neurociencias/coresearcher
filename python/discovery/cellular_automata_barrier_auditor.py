"""
python/discovery/cellular_automata_barrier_auditor.py - Cellular Automata Barrier Auditor & Realization Filter (ADR-DISCOVERY-070).

Audits candidate mathematical invariants and proof strategies for elementary cellular automata
(specifically Rule 30 Prize Problem 1, 2, and 3) against fundamental No-Go barriers:
1. Realization Barrier (Jen 1986, WolframInstitute Rule30Realization):
   Elementary rules with identical left-permutivity and moving left edges
   (Rule 90, Rule 150, Rule 210) share the structural properties of Rule 30, yet their center columns
   are provably eventually constant when started from a single seed. Any proposed proof invariant
   that also holds for Rule 90, Rule 150, or Rule 210 CANNOT decide Rule 30 aperiodicity.
2. Finite Abstraction Lasso Barrier (Rule30ZeroBoundaryBarriers, Barrier B1):
   Every abstraction into a finite state space admits a reachable periodic cycle (lasso).
3. Local / Strip Ranking Ceiling (Barrier B2):
   No local window ranking function into Nat strictly decreases along surviving steps.

This engine serves as an epistemic firewall, instantly discarding flawed proof candidates before
spending compute or human time on formal Lean 4 derivations.
"""

from __future__ import annotations

import enum
import hashlib
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional, Set, Tuple


class ElementaryRule(enum.Enum):
    """Elementary cellular automata rules relevant to realization barriers."""
    RULE_30 = 30    # x XOR (y OR z)   - Target non-linear cellular automaton
    RULE_90 = 90    # x XOR z          - Linear/additive, center column eventually 0
    RULE_150 = 150  # x XOR y XOR z    - Additive, center column eventually constant
    RULE_210 = 210  # x XOR (NOT y AND z) - Non-linear, right non-permutive, center column eventually constant


class CellularBarrierType(enum.Enum):
    """Specific mathematical obstruction in cellular automata proof search."""
    NONE_DETECTED = "NONE_DETECTED"
    RULE90_REALIZATION_OBSTRUCTION = "RULE90_REALIZATION_OBSTRUCTION"
    RULE150_REALIZATION_OBSTRUCTION = "RULE150_REALIZATION_OBSTRUCTION"
    RULE210_REALIZATION_OBSTRUCTION = "RULE210_REALIZATION_OBSTRUCTION"
    FINITE_ABSTRACTION_LASSO = "FINITE_ABSTRACTION_LASSO"
    LOCAL_STRIP_RANKING_CEILING = "LOCAL_STRIP_RANKING_CEILING"


@dataclass(frozen=True)
class RuleDefinition:
    """Boolean transition function for an elementary cellular automaton."""
    rule_number: int
    name: str
    is_left_permutive: bool
    is_additive: bool
    center_column_from_single_seed_is_eventually_constant: bool
    transition: Callable[[bool, bool, bool], bool]


def _rule30_step(l: bool, c: bool, r: bool) -> bool:
    return l ^ (c | r)


def _rule90_step(l: bool, c: bool, r: bool) -> bool:
    return l ^ r


def _rule150_step(l: bool, c: bool, r: bool) -> bool:
    return l ^ c ^ r


def _rule210_step(l: bool, c: bool, r: bool) -> bool:
    return l ^ ((not c) and r)


RULE_CATALOG: Dict[ElementaryRule, RuleDefinition] = {
    ElementaryRule.RULE_30: RuleDefinition(
        rule_number=30,
        name="Rule 30",
        is_left_permutive=True,
        is_additive=False,
        center_column_from_single_seed_is_eventually_constant=False,  # Conjectured / Prize Problem 1
        transition=_rule30_step,
    ),
    ElementaryRule.RULE_90: RuleDefinition(
        rule_number=90,
        name="Rule 90",
        is_left_permutive=True,
        is_additive=True,
        center_column_from_single_seed_is_eventually_constant=True,   # Proved: center(t) = 0 for t >= 1
        transition=_rule90_step,
    ),
    ElementaryRule.RULE_150: RuleDefinition(
        rule_number=150,
        name="Rule 150",
        is_left_permutive=True,
        is_additive=True,
        center_column_from_single_seed_is_eventually_constant=True,   # Proved: center(t) = 0 for t >= 1
        transition=_rule150_step,
    ),
    ElementaryRule.RULE_210: RuleDefinition(
        rule_number=210,
        name="Rule 210",
        is_left_permutive=True,
        is_additive=False,
        center_column_from_single_seed_is_eventually_constant=True,   # Proved: center(t) = 0 for t >= 2
        transition=_rule210_step,
    ),
}


@dataclass
class CandidateInvariantAuditResult:
    """Outcome of evaluating a proposed invariant against cellular automata barriers."""
    candidate_id: str
    is_admissible: bool
    detected_barrier: CellularBarrierType
    falsifying_rules: List[ElementaryRule]
    detailed_critique: str
    counterexample_trace: Optional[Dict[str, Any]] = None
    suggested_alternative_paradigms: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "candidate_id": self.candidate_id,
            "is_admissible": self.is_admissible,
            "detected_barrier": self.detected_barrier.value,
            "falsifying_rules": [r.name for r in self.falsifying_rules],
            "detailed_critique": self.detailed_critique,
            "counterexample_trace": self.counterexample_trace,
            "suggested_alternative_paradigms": self.suggested_alternative_paradigms,
        }


class CellularAutomataBarrierAuditor:
    """
    Auditor that tests whether a candidate invariant or deduction method for Rule 30
    suffers from realization barriers or finite abstraction lassos.
    """

    def __init__(self) -> None:
        self.catalog = RULE_CATALOG

    @staticmethod
    def simulate_center_column(
        rule: ElementaryRule,
        steps: int = 64,
        initial_seed: Optional[Dict[int, bool]] = None,
    ) -> List[bool]:
        """
        Simulates the center column (position 0) for `steps` iterations.
        Default initial seed is a single black cell at position 0.
        """
        fn = RULE_CATALOG[rule].transition
        # Sparse representation of active cells
        if initial_seed is None:
            current: Dict[int, bool] = {0: True}
        else:
            current = dict(initial_seed)

        center_history: List[bool] = [current.get(0, False)]

        for _ in range(steps):
            # Range of potentially active positions
            if current:
                min_pos = min(current.keys()) - 1
                max_pos = max(current.keys()) + 1
            else:
                min_pos, max_pos = -1, 1

            next_state: Dict[int, bool] = {}
            for p in range(min_pos, max_pos + 1):
                left_val = current.get(p - 1, False)
                center_val = current.get(p, False)
                right_val = current.get(p + 1, False)
                res = fn(left_val, center_val, right_val)
                if res:
                    next_state[p] = True

            current = next_state
            center_history.append(current.get(0, False))

        return center_history

    def audit_invariant_against_realization_barrier(
        self,
        candidate_id: str,
        invariant_evaluator: Callable[[ElementaryRule, int], bool],
        test_steps: int = 32,
    ) -> CandidateInvariantAuditResult:
        """
        Tests whether a candidate invariant holds for Rule 30 AND also for Rule 90, 150, or 210.
        If an invariant holds for Rule 90/150/210, it is structurally blind to the specific
        non-linear OR structure of Rule 30 and cannot prove aperiodicity.
        """
        r30_holds = all(invariant_evaluator(ElementaryRule.RULE_30, t) for t in range(test_steps))
        if not r30_holds:
            return CandidateInvariantAuditResult(
                candidate_id=candidate_id,
                is_admissible=False,
                detected_barrier=CellularBarrierType.NONE_DETECTED,
                falsifying_rules=[ElementaryRule.RULE_30],
                detailed_critique="Candidate invariant is false for Rule 30 itself.",
                suggested_alternative_paradigms=["Revise invariant predicate definitions."],
            )

        falsifying: List[ElementaryRule] = []
        barrier = CellularBarrierType.NONE_DETECTED

        for check_rule in [ElementaryRule.RULE_90, ElementaryRule.RULE_150, ElementaryRule.RULE_210]:
            holds_for_check_rule = all(invariant_evaluator(check_rule, t) for t in range(test_steps))
            if holds_for_check_rule:
                falsifying.append(check_rule)
                if check_rule == ElementaryRule.RULE_90 and barrier == CellularBarrierType.NONE_DETECTED:
                    barrier = CellularBarrierType.RULE90_REALIZATION_OBSTRUCTION
                elif check_rule == ElementaryRule.RULE_150 and barrier == CellularBarrierType.NONE_DETECTED:
                    barrier = CellularBarrierType.RULE150_REALIZATION_OBSTRUCTION
                elif check_rule == ElementaryRule.RULE_210 and barrier == CellularBarrierType.NONE_DETECTED:
                    barrier = CellularBarrierType.RULE210_REALIZATION_OBSTRUCTION

        if falsifying:
            center_traces = {
                r.name: self.simulate_center_column(r, steps=16) for r in falsifying
            }
            return CandidateInvariantAuditResult(
                candidate_id=candidate_id,
                is_admissible=False,
                detected_barrier=barrier,
                falsifying_rules=falsifying,
                detailed_critique=(
                    f"Realization Barrier Obstruction: The proposed invariant holds simultaneously for Rule 30 "
                    f"and realization barrier rules ({', '.join(r.name for r in falsifying)}). "
                    f"Because the center column of {falsifying[0].name} collapses to an eventually constant sequence "
                    "from a single seed, any deduction relying solely on this invariant fails to distinguish Rule 30's "
                    "chaotic behavior from degenerate constant behavior."
                ),
                counterexample_trace={
                    "steps_checked": test_steps,
                    "barrier_center_traces": center_traces,
                },
                suggested_alternative_paradigms=[
                    "Exploit non-linear boolean OR interaction specific to Rule 30 (xor a (b || c)).",
                    "Analyze left-half zero-boundary propagation (Q01 frontier beyond width 52).",
                    "Examine finite relaxation with Jen's adjacent-column moving-edge contradiction.",
                ],
            )

        return CandidateInvariantAuditResult(
            candidate_id=candidate_id,
            is_admissible=True,
            detected_barrier=CellularBarrierType.NONE_DETECTED,
            falsifying_rules=[],
            detailed_critique="Admissible: Invariant breaks on degenerate rules (Rule 90, 150, 210) and is specific to Rule 30.",
            suggested_alternative_paradigms=[],
        )

    @staticmethod
    def audit_finite_abstraction_search(
        candidate_id: str,
        state_space_size: int,
    ) -> CandidateInvariantAuditResult:
        """
        Barrier B1 Audit: Verifies whether a proposed proof relies on a finite abstraction of the infinite state space.
        As established in Rule30ZeroBoundaryBarriers.lean (finite_abstraction_has_lasso), any finite abstraction
        admits a reachable periodic cycle from finite starts.
        """
        if state_space_size < float("inf"):
            return CandidateInvariantAuditResult(
                candidate_id=candidate_id,
                is_admissible=False,
                detected_barrier=CellularBarrierType.FINITE_ABSTRACTION_LASSO,
                falsifying_rules=[ElementaryRule.RULE_30],
                detailed_critique=(
                    f"Barrier B1 Obstruction: State space size is finite ({state_space_size}). "
                    "By theorem `Rule30ZeroBoundaryBarriers.finite_abstraction_has_lasso`, every finite state abstraction "
                    "of Rule 30 admits a reachable cycle (lasso) and cannot establish strict non-periodicity."
                ),
                suggested_alternative_paradigms=[
                    "Use unbounded induction on configuration width or infinite relaxation.",
                    "Adopt algebraic degree or formal language complexity invariants.",
                ],
            )

        return CandidateInvariantAuditResult(
            candidate_id=candidate_id,
            is_admissible=True,
            detected_barrier=CellularBarrierType.NONE_DETECTED,
            falsifying_rules=[],
            detailed_critique="Admissible: State space is infinite, bypassing finite abstraction lasso barrier.",
        )
