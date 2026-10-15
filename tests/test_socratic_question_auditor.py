"""
tests/test_socratic_question_auditor.py - Test suite for Socratic Question & Epistemic Inquiry Auditor (ADR-DISCOVERY-056).
"""

from python.discovery.socratic_question_auditor import (
    QuestionBiasTier,
    QuestionEpistemicVerdict,
    QuestionGranularity,
    SocraticQuestionAuditor,
)


def test_objective_micro_question_audit():
    """Verifies that a well-formulated, neutral micro question receives high Delta Omega and objective tier."""
    auditor = SocraticQuestionAuditor()
    question = "Does plasma pTau217 concentration above 0.3 pg/mL predict neocortical tau PET positivity with sensitivity > 85%?"
    verdict = auditor.audit_question(
        raw_question=question,
        question_id="QUESTION-000001",
        ontology_path="Science/Medicine/Neurology/Alzheimer/Biomarkers",
    )

    assert isinstance(verdict, QuestionEpistemicVerdict)
    assert verdict.is_constitutionally_valid is True
    assert len(verdict.constitutional_issues) == 0
    assert verdict.granularity == QuestionGranularity.MICRO
    assert verdict.bias_tier == QuestionBiasTier.OBJECTIVE
    assert verdict.bias_score <= 0.1
    assert len(verdict.smuggled_premises) == 0
    assert verdict.delta_omega_potential >= 0.75
    assert len(verdict.counter_questions) >= 2


def test_confirmation_biased_question_audit():
    """Detects confirmation bias in loaded question and refines formulation."""
    auditor = SocraticQuestionAuditor()
    question = "How does novel drug X prove that amyloid clearance halts cognitive decline?"
    verdict = auditor.audit_question(
        raw_question=question,
        question_id="QUESTION-000002",
        ontology_path="Science/Medicine/Pharmacology/Alzheimer",
    )

    assert verdict.bias_tier == QuestionBiasTier.CONFIRMATION_BIASED
    assert verdict.bias_score >= 0.4
    # State space reduction is penalized due to confirmation bias
    assert verdict.delta_omega_potential < 0.8
    # Verifies canonical refinement replaces loaded claim
    assert (
        "falsify" in verdict.refined_canonical_formulation.lower()
        or "modulate" in verdict.refined_canonical_formulation.lower()
    )


def test_smuggled_premise_detection():
    """Detects embedded unproven assumptions and generates targeted refutation counter-questions."""
    auditor = SocraticQuestionAuditor()
    question = (
        "Given that microglia activation is purely neurotoxic in tauopathies, how can we inhibit TREM2 signalling?"
    )
    verdict = auditor.audit_question(
        raw_question=question,
        question_id="QUESTION-000003",
        ontology_path="Science/Medicine/Immunology/Neurodegeneration",
    )

    assert len(verdict.smuggled_premises) >= 1
    premise = verdict.smuggled_premises[0]
    assert "microglia activation is purely neurotoxic" in premise.premise_text
    assert premise.risk_level == "HIGH"

    # Counter-questions must include an adversarial counter addressing the smuggled premise
    adversarial_counters = [cq for cq in verdict.counter_questions if cq.epistemic_angle == "ADVERSARIAL"]
    assert len(adversarial_counters) >= 1
    assert "microglia activation is purely neurotoxic" in adversarial_counters[0].formulation


def test_constitutional_violations():
    """Flags malformed IDs, missing question marks, and shallow ontology paths."""
    auditor = SocraticQuestionAuditor()
    question = "alzheimer biomarkers"  # Too short, no question mark
    verdict = auditor.audit_question(
        raw_question=question,
        question_id="bad_id_123",  # Malformed ID
        ontology_path="Medicine",  # Only 1 level
    )

    assert verdict.is_constitutionally_valid is False
    assert len(verdict.constitutional_issues) >= 3


def test_counter_questions_angles():
    """Ensures epiphenomenon and boundary condition angles are synthesized."""
    auditor = SocraticQuestionAuditor()
    question = "What blood biomarkers predict preclinical Alzheimer's disease?"
    verdict = auditor.audit_question(
        raw_question=question,
        ontology_path="Science/Medicine/Neurology/Alzheimer/Biomarkers",
    )

    angles = {cq.epistemic_angle for cq in verdict.counter_questions}
    assert "EPIPHENOMENON" in angles
    assert "BOUNDARY_CONDITION" in angles
    assert verdict.delta_omega_potential > 0.5
