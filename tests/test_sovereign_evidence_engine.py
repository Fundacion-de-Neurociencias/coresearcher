"""
tests/test_sovereign_evidence_engine.py - Tests for ADR-DISCOVERY-044
Verifies:
1. Sub-second latency execution of Jev-style evidence engine.
2. Objective epistemic weighting decoupling from pure semantic/topical relevance.
3. Publication bias and observational confounding detection (the coffee vs diabetes scenario).
4. System 2 escalation with Hakken evidence path perturbation for ambiguous claims.
5. Deterministic SOM SHA-256 Merkle anchoring.
"""

import time

from python.discovery.sovereign_evidence_engine import (
    CandidateEvidenceItem,
    EvidencePolarity,
    SovereignEvidenceEngine,
    StudyDesignTier,
)


def test_sub_second_evidence_audit_and_epistemic_weighting():
    engine = SovereignEvidenceEngine()

    claim_text = "Drinking 3 cups of coffee daily reduces type 2 diabetes risk"

    # Synthetic candidate items representing typical literature mix
    items = [
        # Item 1: High semantic relevance, but low-weight observational epidemiology with high confounding risk
        CandidateEvidenceItem(
            item_id="EVID-OBS-01",
            title="Coffee consumption and self-reported diabetes incidence in cross-sectional cohort",
            snippet="Drinking coffee shows strong inverse correlation with self-reported diabetes risk in survey.",
            study_design=StudyDesignTier.RETROSPECTIVE_OBSERVATIONAL,
            polarity=EvidencePolarity.SUPPORTS,
            sample_size=1200,
            confounding_risk=0.65,  # Unmeasured socioeconomic/dietary confounders
            rcs_level=1,
            is_pre_registered=False,
        ),
        # Item 2: Another observational study supporting claim
        CandidateEvidenceItem(
            item_id="EVID-OBS-02",
            title="Caffeine intake and blood glucose markers in retrospective registry",
            snippet="Coffee drinkers showed mildly lower fasting insulin in unadjusted cohort.",
            study_design=StudyDesignTier.RETROSPECTIVE_OBSERVATIONAL,
            polarity=EvidencePolarity.SUPPORTS,
            sample_size=800,
            confounding_risk=0.55,
            rcs_level=1,
            is_pre_registered=False,
        ),
        # Item 3: Randomized Double-Blind Controlled Trial refuting acute causal effect
        CandidateEvidenceItem(
            item_id="EVID-RCT-01",
            title="Randomized controlled trial of caffeine administration on insulin sensitivity in pre-diabetic patients",
            snippet="Controlled caffeine infusion showed no significant improvement in clamp-measured insulin sensitivity.",
            study_design=StudyDesignTier.RANDOMIZED_CONTROLLED_TRIAL,
            polarity=EvidencePolarity.REFUTES,
            sample_size=350,
            confounding_risk=0.10,
            rcs_level=3,
            is_pre_registered=True,
            effect_size=-0.02,
            p_value=0.48,
        ),
    ]

    t0 = time.perf_counter()
    verdict = engine.audit_claim_evidence(
        claim_id="CLAIM-COFFEE-DIABETES",
        claim_text=claim_text,
        evidence_items=items,
    )
    t1 = time.perf_counter()

    # 1. Assert sub-second execution
    elapsed_ms = (t1 - t0) * 1000.0
    assert elapsed_ms < 1000.0, f"Execution took {elapsed_ms:.2f}ms, expected sub-second"

    # 2. Assert RCT epistemic weight exceeds single observational study despite observational being positive
    obs_item = next(i for i in items if i.item_id == "EVID-OBS-01")
    rct_item = next(i for i in items if i.item_id == "EVID-RCT-01")
    assert rct_item.epistemic_weight > obs_item.epistemic_weight

    # 3. Assert detection of high publication bias risk due to predominantly observational unpreregistered literature
    assert verdict.publication_bias_risk > 0.40

    # 4. Assert SOM hash is present and starts with sha256:
    assert verdict.som_claim_hash.startswith("sha256:")
    assert verdict.total_evidence_examined == 3


def test_empty_evidence_claim_handling():
    engine = SovereignEvidenceEngine()
    verdict = engine.audit_claim_evidence(
        claim_id="CLAIM-EMPTY",
        claim_text="Unprecedented cosmic particle interaction",
        evidence_items=[],
    )
    assert verdict.epistemic_verdict == "UNGROUNDED_HYPOTHESIS"
    assert verdict.total_evidence_examined == 0
    assert verdict.system_one_latency_ms < 50.0


def test_system_two_escalation_for_ambiguous_evidence():
    engine = SovereignEvidenceEngine()
    claim_text = "Moderate alcohol consumption improves cardiovascular longevity"

    items = [
        CandidateEvidenceItem(
            item_id="EVID-1",
            title="Cardiovascular health and alcohol consumption",
            snippet="Moderate intake associates with longevity in health survey.",
            study_design=StudyDesignTier.PROSPECTIVE_LONGITUDINAL_COHORT,
            polarity=EvidencePolarity.SUPPORTS,
            sample_size=2000,
            rcs_level=2,
            confounding_risk=0.4,
        ),
        CandidateEvidenceItem(
            item_id="EVID-2",
            title="Mendelian randomization of alcohol intake and coronary artery disease",
            snippet="Genetic causal instruments show no protective effect of alcohol.",
            study_design=StudyDesignTier.MECHANISTIC_CAUSAL_MODEL,
            polarity=EvidencePolarity.REFUTES,
            sample_size=50000,
            rcs_level=2,
            confounding_risk=0.15,
        ),
    ]

    verdict = engine.audit_claim_evidence(
        claim_id="CLAIM-ALCOHOL",
        claim_text=claim_text,
        evidence_items=items,
        force_system_two=True,
    )

    assert verdict.system_two_escalated is True
    assert verdict.hakken_robustness is not None
    assert "baseline_confidence" in verdict.hakken_robustness
