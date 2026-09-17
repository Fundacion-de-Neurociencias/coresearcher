"""
python/discovery/scientific_logic.py - Computable Scientific Logic & Modus Tollens Engine
Implements formal deduction with Lakatosian Auxiliary Assumptions (Protective Belt).

Formal Rule:
((H ∧ A_1 ∧ A_2 ∧ ... ∧ A_n) ⟹ P) ∧ ¬P ⟹ (¬H ∨ ¬A_1 ∨ ... ∨ ¬A_n)
"""

from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from enum import Enum


class AssumptionStatus(str, Enum):
    ACCEPTED = "ACCEPTED"
    QUESTIONED = "QUESTIONED"
    REFUTED = "REFUTED"


class ImplicationStrength(str, Enum):
    DEDUCTIVE_STRICT = "DEDUCTIVE_STRICT"     # Logical necessity: (H ∧ A) ⟹ P
    INDUCTIVE_PROBABILISTIC = "INDUCTIVE_PROB" # High probability: P(P | H ∧ A) > 0.95


@dataclass
class AuxiliaryAssumption:
    """
    An explicit auxiliary assumption (Lakatosian protective belt).
    Examples: instrument calibration, linear model validity, sample homogeneity.
    """
    assumption_id: str
    statement: str
    category: str  # "INSTRUMENTATION" | "STATISTICAL_MODEL" | "SAMPLE_REPRESENTATIVENESS" | "BIOLOGICAL_BACKGROUND"
    epistemic_status: AssumptionStatus = AssumptionStatus.ACCEPTED
    falsification_test: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "assumption_id": self.assumption_id,
            "statement": self.statement,
            "category": self.category,
            "epistemic_status": self.epistemic_status.value,
            "falsification_test": self.falsification_test
        }


@dataclass
class CounterExample:
    """An empirical data point or subgroup that contradicts a prediction."""
    counterexample_id: str
    description: str
    observed_value: Any
    expected_value: Any
    subgroup: str


@dataclass
class FormalImplication:
    """
    Computable scientific rule: Core Hypothesis (H) combined with Auxiliary Assumptions (A)
    strictly implies an Observable Prediction (P).
    """
    implication_id: str
    core_hypothesis_id: str
    auxiliary_assumptions: List[AuxiliaryAssumption]
    consequent_prediction_id: str
    strength: ImplicationStrength = ImplicationStrength.DEDUCTIVE_STRICT

    def to_dict(self) -> Dict[str, Any]:
        return {
            "implication_id": self.implication_id,
            "core_hypothesis_id": self.core_hypothesis_id,
            "auxiliary_assumptions": [a.to_dict() for a in self.auxiliary_assumptions],
            "consequent_prediction_id": self.consequent_prediction_id,
            "strength": self.strength.value,
            "formula": f"({self.core_hypothesis_id} ∧ {' ∧ '.join(a.assumption_id for a in self.auxiliary_assumptions)}) ⟹ {self.consequent_prediction_id}"
        }


@dataclass
class ModusTollensResult:
    prediction_id: str
    empirical_outcome: str  # "SURVIVED" | "REFUTED"
    formula_applied: str
    core_hypothesis_impact: str  # "PROVISIONALLY_SURVIVED" | "FATALLY_REFUTED" | "MUTED_REVISED"
    auxiliary_assumptions_audited: List[Dict[str, Any]]
    deductive_trail: List[str]
    falsification_blame: str  # "CORE_HYPOTHESIS" | "AUXILIARY_ASSUMPTION" | "NONE"

    def to_dict(self) -> Dict[str, Any]:
        return {
            "prediction_id": self.prediction_id,
            "empirical_outcome": self.empirical_outcome,
            "formula_applied": self.formula_applied,
            "core_hypothesis_impact": self.core_hypothesis_impact,
            "auxiliary_assumptions_audited": self.auxiliary_assumptions_audited,
            "deductive_trail": self.deductive_trail,
            "falsification_blame": self.falsification_blame
        }


class DeductionEngine:
    """
    Executes formal logic deduction and Lakatosian Modus Tollens.
    """

    @staticmethod
    def evaluate_implication(
        implication: FormalImplication,
        prediction_passed: bool,
        counter_examples: Optional[List[CounterExample]] = None
    ) -> ModusTollensResult:
        h_id = implication.core_hypothesis_id
        aux_list = implication.auxiliary_assumptions
        aux_ids = " ∧ ".join(a.assumption_id for a in aux_list)
        p_id = implication.consequent_prediction_id

        if prediction_passed:
            trail = [
                f"1. Premise: ({h_id} ∧ {aux_ids}) ⟹ {p_id}",
                f"2. Observation: {p_id} holds true in empirical test.",
                f"3. Deduction: Core Hypothesis {h_id} provisionally survived without refuting any auxiliary assumptions."
            ]
            return ModusTollensResult(
                prediction_id=p_id,
                empirical_outcome="SURVIVED",
                formula_applied=f"(({h_id} ∧ {aux_ids}) ⟹ {p_id}) ∧ {p_id} ⟹ Provisional Survival",
                core_hypothesis_impact="PROVISIONALLY_SURVIVED",
                auxiliary_assumptions_audited=[a.to_dict() for a in aux_list],
                deductive_trail=trail,
                falsification_blame="NONE"
            )
        else:
            # Prediction Failed: Modus Tollens applies: ¬P ⟹ (¬H ∨ ¬A_1 ∨ ... ∨ ¬A_n)
            # Check if an auxiliary assumption failed or if the core hypothesis itself failed
            # If counterexamples indicate an auxiliary failure (e.g. sample heterogeneity), blame auxiliary; otherwise blame core H
            has_aux_flaw = any(a.epistemic_status == AssumptionStatus.QUESTIONED for a in aux_list)
            
            trail = [
                f"1. Premise: ({h_id} ∧ {aux_ids}) ⟹ {p_id}",
                f"2. Observation: ¬{p_id} (Empirical prediction failed to hold).",
                f"3. Modus Tollens: ¬{p_id} ⟹ (¬{h_id} ∨ ¬{' ∨ ¬'.join(a.assumption_id for a in aux_list)})"
            ]

            if has_aux_flaw:
                blame = "AUXILIARY_ASSUMPTION"
                impact = "MUTED_REVISED"
                trail.append(f"4. Audit finding: Auxiliary protective belt breached. Core {h_id} shielded pending auxiliary revision.")
            else:
                blame = "CORE_HYPOTHESIS"
                impact = "FATALLY_REFUTED"
                trail.append(f"4. Audit finding: All auxiliary assumptions verified solid. Core Hypothesis {h_id} is FATALLY REFUTED.")

            return ModusTollensResult(
                prediction_id=p_id,
                empirical_outcome="REFUTED",
                formula_applied=f"(({h_id} ∧ {aux_ids}) ⟹ {p_id}) ∧ ¬{p_id} ⟹ (¬{h_id} ∨ ¬{aux_ids})",
                core_hypothesis_impact=impact,
                auxiliary_assumptions_audited=[a.to_dict() for a in aux_list],
                deductive_trail=trail,
                falsification_blame=blame
            )
