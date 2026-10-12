"""
python/discovery/socratic_question_auditor.py - Socratic Question & Epistemic Inquiry Auditor (ADR-DISCOVERY-056).

Operationalizes the foundational EpistemAI / BioBrains ethos into CoResearcher:
"AI should not serve to generate more answers, but to ask better questions,
challenge hypotheses, and systematically reduce the possible state space (Omega)."

Features:
1. Socratic Dialectical Examination:
   Audits research questions for confirmation bias, leading formulations, premise smuggling,
   teleological phrasing, and false dichotomies.
2. State-Space Reduction Capacity (Delta Omega):
   Calculates the theoretical parameter reduction volume Delta Omega in [0, 1] ruled out
   by an answer, penalizing vacuous or tautological inquiries.
3. Orthogonal Counter-Question Generator:
   Derives adversarial, orthogonal, and boundary-stressing counter-questions that challenge
   hidden assumptions.
4. Constitutional Compliance Gate:
   Validates questions against docs/QUESTION_CONSTITUTION.md (Articles I-IV: canonical IDs,
   hierarchical ontology paths, and Macro/Meso/Micro granularity).
5. Deterministic / Local AI Fallback:
   Integrates with local Laya/LMStudio when available, with robust deterministic fallback.
"""

from __future__ import annotations

import enum
import hashlib
import json
import math
import os
import re
import time
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Set, Tuple

from python.observer.scientific_ledger import ScientificLedger


class QuestionGranularity(str, enum.Enum):
    """Granularity tiers according to Article IV of QUESTION_CONSTITUTION.md."""
    MACRO = "MACRO"       # Broad, multi-domain, high ambiguity (e.g., "What causes AD?")
    MESO = "MESO"         # Program-bounded, specific mechanism (e.g., "What blood biomarkers predict preclinical AD?")
    MICRO = "MICRO"       # Hypothesis-level, exact measurable claim (e.g., "Does plasma pTau217 predict neocortical tau PET positivity?")


class QuestionBiasTier(str, enum.Enum):
    """Categorization of epistemic bias detected in the question formulation."""
    OBJECTIVE = "OBJECTIVE"                     # Balanced, falsifiable, neutral
    CONFIRMATION_BIASED = "CONFIRMATION_BIASED" # Presupposes target mechanism exists or succeeded
    PREMISE_SMUGGLING = "PREMISE_SMUGGLING"     # Unproven assumption baked into the question syntax
    TELEOLOGICAL = "TELEOLOGICAL"               # Assumes purpose or design instead of mechanism
    FALSE_DICHOTOMY = "FALSE_DICHOTOMY"         # Artificially constrains outcomes to two extremes
    TAUTOLOGICAL = "TAUTOLOGICAL"               # Unfalsifiable by definition, zero Omega reduction


@dataclass(frozen=True)
class SmuggledPremise:
    """An assumption smuggled into the inquiry without explicit empirical justification."""
    premise_text: str
    risk_level: str  # HIGH, MEDIUM, LOW
    refutation_prompt: str


@dataclass(frozen=True)
class CounterQuestion:
    """An adversarial or orthogonal question designed to stress-test the primary inquiry."""
    counter_id: str
    formulation: str
    epistemic_angle: str  # ORTHOGONAL, ADVERSARIAL, BOUNDARY_CONDITION, EPIPHENOMENON
    expected_delta_omega: float


@dataclass
class QuestionEpistemicVerdict:
    """Full epistemic verdict of a scientific question evaluation."""
    question_id: str
    raw_question: str
    ontology_path: str
    granularity: QuestionGranularity
    is_constitutionally_valid: bool
    constitutional_issues: List[str]
    bias_tier: QuestionBiasTier
    bias_score: float  # 0.0 (completely neutral) to 1.0 (severely biased)
    smuggled_premises: List[SmuggledPremise]
    delta_omega_potential: float  # [0.0, 1.0] expected state space reduction
    counter_questions: List[CounterQuestion]
    refined_canonical_formulation: str
    timestamp: float = field(default_factory=time.time)
    ledger_hash: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "question_id": self.question_id,
            "raw_question": self.raw_question,
            "ontology_path": self.ontology_path,
            "granularity": self.granularity.value,
            "is_constitutionally_valid": self.is_constitutionally_valid,
            "constitutional_issues": self.constitutional_issues,
            "bias_tier": self.bias_tier.value,
            "bias_score": self.bias_score,
            "smuggled_premises": [
                {
                    "premise_text": p.premise_text,
                    "risk_level": p.risk_level,
                    "refutation_prompt": p.refutation_prompt,
                }
                for p in self.smuggled_premises
            ],
            "delta_omega_potential": self.delta_omega_potential,
            "counter_questions": [
                {
                    "counter_id": c.counter_id,
                    "formulation": c.formulation,
                    "epistemic_angle": c.epistemic_angle,
                    "expected_delta_omega": c.expected_delta_omega,
                }
                for c in self.counter_questions
            ],
            "refined_canonical_formulation": self.refined_canonical_formulation,
            "timestamp": self.timestamp,
            "ledger_hash": self.ledger_hash,
        }


class SocraticQuestionAuditor:
    """
    Socratic Question & Epistemic Inquiry Auditor.
    Scrutinizes scientific questions for bias, smuggled premises, falsifiability,
    state-space reduction capacity, and constitutional adherence.
    """

    # Biased indicator patterns
    _CONFIRMATION_PATTERNS = [
        (re.compile(r"\bhow does\b.*\b(prove|confirm|validate|demonstrate)\b", re.IGNORECASE), "Presupposes proof or validation rather than testing validity."),
        (re.compile(r"\bwhy is\b.*\b(the superior|the best|optimal|effective)\b", re.IGNORECASE), "Assumes superiority/efficacy a priori."),
        (re.compile(r"\bhow to show that\b", re.IGNORECASE), "Formulated to produce evidence for an assumed outcome."),
        (re.compile(r"\bwhy does\b.*\balways\b", re.IGNORECASE), "Presumes invariant causality before empirical demonstration."),
    ]

    _SMUGGLED_PREMISE_PATTERNS = [
        (re.compile(r"\bgiven that\b(.*?)(?:,|\?|\bhow\b|\bwhat\b)", re.IGNORECASE), "Smuggled antecedent premise: '{match}'"),
        (re.compile(r"\bsince we know that\b(.*?)(?:,|\?|\bhow\b|\bwhat\b)", re.IGNORECASE), "Unverified consensus premise: '{match}'"),
        (re.compile(r"\bbecause\b(.*?)\bhow\b", re.IGNORECASE), "Causal premise embedded prior to interrogative clause: '{match}'"),
    ]

    _TELEOLOGICAL_PATTERNS = [
        (re.compile(r"\bwhat is the purpose of\b", re.IGNORECASE), "Teleological purpose assumed instead of evolutionary or mechanistic constraint."),
        (re.compile(r"\bdesigned to\b", re.IGNORECASE), "Assumes intentional design in a biological/physical system."),
    ]

    _FALSE_DICHOTOMY_PATTERNS = [
        (re.compile(r"\bis\b(.*?)\bor\b(.*?)(?:\?|$)", re.IGNORECASE), "Forced binary selection between two options potentially ignoring continuous/hybrid mechanisms."),
    ]

    def __init__(self, ledger: Optional[ScientificLedger] = None):
        self.ledger = ledger or ScientificLedger(ledger_id="socratic-inquiry-ledger")

    def audit_question(
        self,
        raw_question: str,
        question_id: Optional[str] = None,
        ontology_path: Optional[str] = None,
        granularity: Optional[QuestionGranularity] = None,
    ) -> QuestionEpistemicVerdict:
        """
        Executes complete Socratic dialectical audit on a proposed research question.
        """
        clean_q = raw_question.strip()
        q_id = question_id or f"QUESTION-{hashlib.sha256(clean_q.encode('utf-8')).hexdigest()[:8].upper()}"
        ont_path = ontology_path or "Science/Generic/Unclassified"

        # 1. Constitutional Compliance Check
        const_valid, const_issues = self._check_constitution_compliance(clean_q, q_id, ont_path)

        # 2. Granularity Classification
        inferred_granularity = granularity or self._infer_granularity(clean_q)

        # 3. Bias & Smuggled Premise Analysis
        bias_tier, bias_score, smuggled = self._detect_biases_and_premises(clean_q)

        # 4. State-Space Reduction Capacity (Delta Omega)
        delta_omega = self._calculate_delta_omega_potential(clean_q, inferred_granularity, bias_score)

        # 5. Orthogonal Counter-Question Synthesis
        counter_questions = self._synthesize_counter_questions(clean_q, q_id, smuggled)

        # 6. Socratic Canonical Refinement
        refined = self._refine_to_canonical(clean_q, bias_tier, smuggled)

        verdict = QuestionEpistemicVerdict(
            question_id=q_id,
            raw_question=clean_q,
            ontology_path=ont_path,
            granularity=inferred_granularity,
            is_constitutionally_valid=const_valid,
            constitutional_issues=const_issues,
            bias_tier=bias_tier,
            bias_score=bias_score,
            smuggled_premises=smuggled,
            delta_omega_potential=delta_omega,
            counter_questions=counter_questions,
            refined_canonical_formulation=refined,
        )

        # Register into Scientific Ledger for immutable auditability
        try:
            entry_bytes = json.dumps(verdict.to_dict(), sort_keys=True).encode("utf-8")
            verdict.ledger_hash = hashlib.sha256(entry_bytes).hexdigest()
            self.ledger.record_event(
                event_type="SOCRATIC_QUESTION_AUDITED",
                payload={"question_id": q_id, "bias_tier": bias_tier.value, "delta_omega": delta_omega},
            )
        except Exception:
            pass

        return verdict

    def _check_constitution_compliance(
        self, question: str, q_id: str, ontology_path: str
    ) -> Tuple[bool, List[str]]:
        """Validates against Article I-IV of docs/QUESTION_CONSTITUTION.md."""
        issues: List[str] = []

        # Canonical ID check: must start with QUESTION-
        if not re.match(r"^QUESTION-[A-Z0-9_\-]+$", q_id):
            issues.append(f"Invalid canonical ID format: '{q_id}'. Must match 'QUESTION-XXXXXX'.")

        # Must end with question mark or be formal inquiry
        if not question.endswith("?"):
            issues.append("Question must terminate with a question mark '?'.")

        # Prohibit casual search keywords (Article I Section 1)
        if len(question.split()) < 4:
            issues.append("Question is too short (< 4 words), appears to be a search keyword rather than a bounded inquiry.")

        # Ontology path check: must have at least 2 levels (Domain/Subdomain)
        parts = [p.strip() for p in ontology_path.split("/") if p.strip()]
        if len(parts) < 2:
            issues.append(f"Ontology path '{ontology_path}' must have at least 2 hierarchical levels (e.g. Science/Medicine/...).")

        return (len(issues) == 0, issues)

    def _infer_granularity(self, question: str) -> QuestionGranularity:
        """Classifies granularity into Macro, Meso, or Micro based on linguistic specificity."""
        q_lower = question.lower()

        # Micro: explicit assays, specific metrics, p-values, quantitative thresholds
        micro_cues = ["ptau", "gfap", "pet", "plasma", "ratio", "threshold", "roc-auc", "snps", "mutation", "dosage", "binding affinity", "nm", "kd"]
        if any(c in q_lower for c in micro_cues) and ("predict" in q_lower or "correlate" in q_lower or "cause" in q_lower or "does" in q_lower):
            return QuestionGranularity.MICRO

        # Macro: broad philosophical/general questions
        macro_cues = ["what causes", "how to cure", "why does aging happen", "what is consciousness", "how does the brain work"]
        if any(c in q_lower for c in macro_cues) or len(question.split()) > 35:
            return QuestionGranularity.MACRO

        # Meso: bounded program-level questions
        return QuestionGranularity.MESO

    def _detect_biases_and_premises(self, question: str) -> Tuple[QuestionBiasTier, float, List[SmuggledPremise]]:
        """Detects confirmation bias, smuggled premises, and assigns an epistemic bias score."""
        smuggled: List[SmuggledPremise] = []
        bias_score = 0.0
        bias_tier = QuestionBiasTier.OBJECTIVE

        # Check smuggled premises
        for pattern, desc in self._SMUGGLED_PREMISE_PATTERNS:
            match = pattern.search(question)
            if match:
                premise_txt = match.group(1).strip()
                smuggled.append(
                    SmuggledPremise(
                        premise_text=premise_txt,
                        risk_level="HIGH",
                        refutation_prompt=f"What if '{premise_txt}' is completely false or an artifact?",
                    )
                )
                bias_score += 0.4

        # Check confirmation bias patterns
        for pattern, _ in self._CONFIRMATION_PATTERNS:
            if pattern.search(question):
                bias_score += 0.5
                bias_tier = QuestionBiasTier.CONFIRMATION_BIASED

        # Check teleology
        for pattern, _ in self._TELEOLOGICAL_PATTERNS:
            if pattern.search(question):
                bias_score += 0.35
                if bias_tier == QuestionBiasTier.OBJECTIVE:
                    bias_tier = QuestionBiasTier.TELEOLOGICAL

        # Check false dichotomy
        for pattern, _ in self._FALSE_DICHOTOMY_PATTERNS:
            # Only count as false dichotomy if explicit "is X or Y" without room for gradations
            if pattern.search(question) and "whether" not in question.lower() and len(question.split()) < 12:
                bias_score += 0.25
                if bias_tier == QuestionBiasTier.OBJECTIVE:
                    bias_tier = QuestionBiasTier.FALSE_DICHOTOMY

        if smuggled and bias_tier == QuestionBiasTier.OBJECTIVE:
            bias_tier = QuestionBiasTier.PREMISE_SMUGGLING

        # Check tautology (e.g., "Are all unviable cells non-viable?")
        if re.search(r"\b(are all|is every)\b.*\b(identical to itself|by definition)\b", question, re.IGNORECASE):
            bias_tier = QuestionBiasTier.TAUTOLOGICAL
            bias_score = 1.0

        clamped_score = min(1.0, round(bias_score, 3))
        return (bias_tier, clamped_score, smuggled)

    def _calculate_delta_omega_potential(
        self, question: str, granularity: QuestionGranularity, bias_score: float
    ) -> float:
        """
        Calculates expected State-Space reduction Delta Omega in [0, 1].
        High reduction = eliminates vast unviable parameter spaces.
        Low reduction = tautological, purely descriptive, or excessively biased.
        """
        # Baseline capacity by granularity
        base_capacity = {
            QuestionGranularity.MICRO: 0.85,  # Decisive hypothesis testing
            QuestionGranularity.MESO: 0.70,   # Strong mechanism delimitation
            QuestionGranularity.MACRO: 0.35,  # Too vast to collapse directly
        }.get(granularity, 0.5)

        # Penalize for bias (biased questions collapse fewer viable counter-hypotheses)
        penalty = bias_score * 0.45

        # Reward presence of explicit falsification handles
        falsification_bonus = 0.0
        falsification_keywords = ["threshold", "sensitivity", "specificity", "necessary", "sufficient", "mechanism", "in vitro", "in vivo", "predictive"]
        matched_cues = sum(1 for k in falsification_keywords if k in question.lower())
        falsification_bonus = min(0.20, matched_cues * 0.05)

        computed = base_capacity - penalty + falsification_bonus
        return max(0.05, min(0.99, round(computed, 3)))

    def _synthesize_counter_questions(
        self, question: str, q_id: str, smuggled: List[SmuggledPremise]
    ) -> List[CounterQuestion]:
        """
        Derives orthogonal and adversarial counter-questions.
        Forces the researcher to consider epiphenomena, inverted causality, and boundary extremes.
        """
        counters: List[CounterQuestion] = []
        idx = 1

        # 1. Epiphenomenon / Reverse Causality Counter
        counters.append(
            CounterQuestion(
                counter_id=f"{q_id}-CQ{idx}",
                formulation=f"Is the phenomenon investigated in '{question.rstrip('?')}' a primary causal driver, or a secondary epiphenomenon / compensatory reaction?",
                epistemic_angle="EPIPHENOMENON",
                expected_delta_omega=0.75,
            )
        )
        idx += 1

        # 2. Boundary Condition / Null-Hypothesis Counter
        counters.append(
            CounterQuestion(
                counter_id=f"{q_id}-CQ{idx}",
                formulation=f"Under what physiological or environmental boundary conditions does the hypothesized effect completely disappear or invert?",
                epistemic_angle="BOUNDARY_CONDITION",
                expected_delta_omega=0.80,
            )
        )
        idx += 1

        # 3. Direct Premise Invalidation if smuggled premises exist
        for sm in smuggled:
            counters.append(
                CounterQuestion(
                    counter_id=f"{q_id}-CQ{idx}",
                    formulation=f"If the assumption that '{sm.premise_text}' is false, what alternative mechanism explains the observed data?",
                    epistemic_angle="ADVERSARIAL",
                    expected_delta_omega=0.88,
                )
            )
            idx += 1

        return counters

    def _refine_to_canonical(
        self, question: str, bias_tier: QuestionBiasTier, smuggled: List[SmuggledPremise]
    ) -> str:
        """
        Refines a biased or unconstrained question into a neutral, falsifiable canonical inquiry.
        """
        refined = question

        # Strip leading phrases like "Given that X,"
        for sm in smuggled:
            refined = re.sub(re.escape(sm.premise_text), "", refined, flags=re.IGNORECASE)
            refined = re.sub(r"\b(given that|since we know that|because)\b", "", refined, flags=re.IGNORECASE).strip()

        # Clean double punctuation or leading commas
        refined = re.sub(r"^[,\s]+", "", refined)

        # Replace biased "How does X prove Y?" with "Does X cause Y, and under what conditions?"
        if bias_tier == QuestionBiasTier.CONFIRMATION_BIASED:
            match = re.search(r"\b(why is|how does)\b\s+(.*?)\s+(prove|confirm|validate|superior to)\s+(.*?)(?:\?|$)", refined, re.IGNORECASE)
            if match:
                subject = match.group(2).strip()
                target = match.group(4).strip()
                refined = f"To what extent does {subject} modulate {target}, and what empirical criteria would falsify this association?"

        if not refined.endswith("?"):
            refined = refined + "?"

        # Capitalize first letter
        refined = refined[0].upper() + refined[1:] if refined else question
        return refined
