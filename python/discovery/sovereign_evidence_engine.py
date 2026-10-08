"""
python/discovery/sovereign_evidence_engine.py - Sovereign Evidence-Weighting Engine & Sub-Second Jev-Style Adversarial Claim Auditor (ADR-DISCOVERY-044).

Decouples semantic topic relevance from objective epistemic strength,
neutralizes publication bias and observational confounding, and provides
lightning-fast (sub-second) adversarial evidence triage backed by System 2 causal verification.
"""

from __future__ import annotations

import enum
import hashlib
import json
import math
import re
import time
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple

from python.discovery.reality_contact_score import (
    RealityContactEvidence,
    RealityContactLevel,
    RealityContactEvaluator,
    RealityContactScoreReport,
)
from python.discovery.twin_gate_harness import (
    EvidencePathPerturbationResult,
    HakkenEvidenceGate,
    JevContinuousVerifier,
)


class StudyDesignTier(enum.Enum):
    """Methodological hierarchy of scientific evidence designs."""
    PREREGISTERED_SYSTEMATIC_META_ANALYSIS = "PREREGISTERED_SYSTEMATIC_META_ANALYSIS"  # Weight: 1.0
    RANDOMIZED_CONTROLLED_TRIAL = "RANDOMIZED_CONTROLLED_TRIAL"                        # Weight: 0.9
    MECHANISTIC_CAUSAL_MODEL = "MECHANISTIC_CAUSAL_MODEL"                              # Weight: 0.75
    PROSPECTIVE_LONGITUDINAL_COHORT = "PROSPECTIVE_LONGITUDINAL_COHORT"                # Weight: 0.60
    IN_VITRO_PRECLINICAL = "IN_VITRO_PRECLINICAL"                                      # Weight: 0.45
    RETROSPECTIVE_OBSERVATIONAL = "RETROSPECTIVE_OBSERVATIONAL"                        # Weight: 0.30
    IN_SILICO_UNVALIDATED = "IN_SILICO_UNVALIDATED"                                    # Weight: 0.15
    ANECDOTAL_EXPERT_OPINION = "ANECDOTAL_EXPERT_OPINION"                              # Weight: 0.05


STUDY_DESIGN_BASE_WEIGHTS: Dict[StudyDesignTier, float] = {
    StudyDesignTier.PREREGISTERED_SYSTEMATIC_META_ANALYSIS: 1.00,
    StudyDesignTier.RANDOMIZED_CONTROLLED_TRIAL: 0.90,
    StudyDesignTier.MECHANISTIC_CAUSAL_MODEL: 0.75,
    StudyDesignTier.PROSPECTIVE_LONGITUDINAL_COHORT: 0.60,
    StudyDesignTier.IN_VITRO_PRECLINICAL: 0.45,
    StudyDesignTier.RETROSPECTIVE_OBSERVATIONAL: 0.30,
    StudyDesignTier.IN_SILICO_UNVALIDATED: 0.15,
    StudyDesignTier.ANECDOTAL_EXPERT_OPINION: 0.05,
}


class EvidencePolarity(enum.Enum):
    """Directional relationship of an evidence item relative to a scientific claim."""
    SUPPORTS = "SUPPORTS"
    REFUTES = "REFUTES"
    AMBIGUOUS = "AMBIGUOUS"


@dataclass
class CandidateEvidenceItem:
    """An individual scientific study or experimental dataset evaluating a claim."""
    item_id: str
    title: str
    snippet: str
    study_design: StudyDesignTier
    polarity: EvidencePolarity
    sample_size: int = 0
    p_value: Optional[float] = None
    effect_size: Optional[float] = None
    doi_or_source: str = ""
    rcs_level: int = 0  # 0 to 4 Reality Contact Level
    confounding_risk: float = 0.0  # 0.0 (no confounding) to 1.0 (severe confounding)
    is_pre_registered: bool = False
    topical_relevance: float = 0.0  # Computed semantic relevance [0, 1]
    epistemic_weight: float = 0.0   # Computed objective epistemic weight [0, 1]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item_id": self.item_id,
            "title": self.title,
            "snippet": self.snippet,
            "study_design": self.study_design.value,
            "polarity": self.polarity.value,
            "sample_size": self.sample_size,
            "p_value": self.p_value,
            "effect_size": self.effect_size,
            "doi_or_source": self.doi_or_source,
            "rcs_level": self.rcs_level,
            "confounding_risk": round(self.confounding_risk, 3),
            "is_pre_registered": self.is_pre_registered,
            "topical_relevance": round(self.topical_relevance, 3),
            "epistemic_weight": round(self.epistemic_weight, 4),
        }


@dataclass
class AdversarialClaimAuditVerdict:
    """The complete epistemic balance and verdict for a scientific claim."""
    claim_id: str
    claim_text: str
    total_evidence_examined: int
    supporting_count: int
    refuting_count: int
    ambiguous_count: int
    net_evidence_margin: float       # Positive: favored; Negative: refuted
    publication_bias_risk: float     # Estimated likelihood of hidden negative data [0, 1]
    dominant_study_design: str
    system_one_latency_ms: float
    system_two_escalated: bool
    epistemic_verdict: str           # "ROBUSTLY_SUPPORTED", "EMPIRICALLY_REFUTED", "CONFOUNDED_EQUIVOCAL", "UNGROUNDED_HYPOTHESIS"
    strongest_supporting_item: Optional[Dict[str, Any]] = None
    strongest_refuting_item: Optional[Dict[str, Any]] = None
    hakken_robustness: Optional[Dict[str, Any]] = None
    som_claim_hash: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return {
            "claim_id": self.claim_id,
            "claim_text": self.claim_text,
            "total_evidence_examined": self.total_evidence_examined,
            "supporting_count": self.supporting_count,
            "refuting_count": self.refuting_count,
            "ambiguous_count": self.ambiguous_count,
            "net_evidence_margin": round(self.net_evidence_margin, 4),
            "publication_bias_risk": round(self.publication_bias_risk, 4),
            "dominant_study_design": self.dominant_study_design,
            "system_one_latency_ms": round(self.system_one_latency_ms, 3),
            "system_two_escalated": self.system_two_escalated,
            "epistemic_verdict": self.epistemic_verdict,
            "strongest_supporting_item": self.strongest_supporting_item,
            "strongest_refuting_item": self.strongest_refuting_item,
            "hakken_robustness": self.hakken_robustness,
            "som_claim_hash": self.som_claim_hash,
        }


class SovereignEvidenceEngine:
    """
    Sub-second Jev-style Evidence Retrieval & Causal Weighting Engine.
    Enforces ADR-DISCOVERY-044.
    """

    def __init__(self):
        self.rcs_evaluator = RealityContactEvaluator()
        self.hakken_gate = HakkenEvidenceGate()

    @classmethod
    def calculate_topical_relevance(cls, claim: str, text: str) -> float:
        """
        Fast token Jaccard + substring proximity estimator for topical relevance.
        Runs in sub-millisecond time.
        """
        if not claim or not text:
            return 0.0

        claim_tokens = set(re.findall(r"\b[a-zA-Z]{3,}\b", claim.lower()))
        text_tokens = set(re.findall(r"\b[a-zA-Z]{3,}\b", text.lower()))

        if not claim_tokens:
            return 0.0

        intersection = claim_tokens.intersection(text_tokens)
        jaccard = len(intersection) / len(claim_tokens)

        # Check exact key phrase match boost
        phrase_boost = 0.2 if claim.lower() in text.lower() else 0.0
        return min(1.0, float(jaccard * 0.8 + phrase_boost))

    @classmethod
    def calculate_epistemic_weight(cls, item: CandidateEvidenceItem) -> float:
        """
        Computes the objective epistemic weight of a piece of evidence.
        W = Base(Design) * (1 + RCS / 4) * (1 - Confounding) * PreRegBoost * SampleSizeFactor
        """
        base_w = STUDY_DESIGN_BASE_WEIGHTS.get(item.study_design, 0.2)

        # Reality contact boost (up to 2.0x for RCS 4)
        rcs_factor = 1.0 + (min(4, max(0, item.rcs_level)) / 4.0)

        # Methodological vulnerability / Confounding factor
        confound_factor = max(0.1, 1.0 - min(1.0, max(0.0, item.confounding_risk)))

        # Pre-registration protection against p-hacking
        prereg_factor = 1.25 if item.is_pre_registered else 1.0

        # Sample size log scale factor: saturates around 5000 subjects
        n = max(1, item.sample_size)
        sample_factor = min(1.3, 0.7 + 0.15 * math.log10(n)) if item.sample_size > 0 else 0.8

        raw_weight = base_w * rcs_factor * confound_factor * prereg_factor * sample_factor
        return min(1.0, max(0.01, float(raw_weight)))

    def audit_claim_evidence(
        self,
        claim_id: str,
        claim_text: str,
        evidence_items: List[CandidateEvidenceItem],
        force_system_two: bool = False,
    ) -> AdversarialClaimAuditVerdict:
        """
        Audits a scientific claim by weighting and balancing candidate evidence items.
        Executes sub-second Jev-style System 1 scoring and escalates to System 2 when ambiguous.
        """
        t0 = time.perf_counter()

        if not evidence_items:
            t1 = time.perf_counter()
            return AdversarialClaimAuditVerdict(
                claim_id=claim_id,
                claim_text=claim_text,
                total_evidence_examined=0,
                supporting_count=0,
                refuting_count=0,
                ambiguous_count=0,
                net_evidence_margin=0.0,
                publication_bias_risk=0.5,
                dominant_study_design="NONE",
                system_one_latency_ms=(t1 - t0) * 1000.0,
                system_two_escalated=False,
                epistemic_verdict="UNGROUNDED_HYPOTHESIS",
                som_claim_hash=f"sha256:{hashlib.sha256(claim_text.encode('utf-8')).hexdigest()[:24]}",
            )

        # 1. Compute Relevance and Epistemic Weights for all items (System 1 fast loop)
        supporting: List[CandidateEvidenceItem] = []
        refuting: List[CandidateEvidenceItem] = []
        ambiguous: List[CandidateEvidenceItem] = []

        total_obs_count = 0

        for item in evidence_items:
            item.topical_relevance = self.calculate_topical_relevance(claim_text, item.snippet + " " + item.title)
            item.epistemic_weight = self.calculate_epistemic_weight(item)

            if item.study_design == StudyDesignTier.RETROSPECTIVE_OBSERVATIONAL:
                total_obs_count += 1

            if item.polarity == EvidencePolarity.SUPPORTS:
                supporting.append(item)
            elif item.polarity == EvidencePolarity.REFUTES:
                refuting.append(item)
            else:
                ambiguous.append(item)

        # 2. Sort by epistemic weight (NOT just topical relevance)
        supporting.sort(key=lambda x: x.epistemic_weight, reverse=True)
        refuting.sort(key=lambda x: x.epistemic_weight, reverse=True)

        sum_support_weight = sum(item.epistemic_weight for item in supporting)
        sum_refute_weight = sum(item.epistemic_weight for item in refuting)
        total_weight = sum_support_weight + sum_refute_weight

        net_margin = (sum_support_weight - sum_refute_weight) / max(1e-4, total_weight) if total_weight > 0 else 0.0

        # 3. Publication Bias Estimator ("Behind the Mirror")
        # High risk when predominantly observational, without preregistrations and almost zero published refutations
        obs_ratio = total_obs_count / len(evidence_items) if evidence_items else 0.0
        # If observational studies lack preregistration, they carry high p-hacking / selective publication risk
        obs_unprereg_ratio = sum(1 for i in evidence_items if i.study_design == StudyDesignTier.RETROSPECTIVE_OBSERVATIONAL and not i.is_pre_registered) / len(evidence_items) if evidence_items else 0.0
        zero_negative_risk = 0.3 if len(refuting) == 0 and len(supporting) > 3 else 0.0

        pub_bias_risk = min(1.0, (obs_ratio * 0.4) + (obs_unprereg_ratio * 0.3) + zero_negative_risk)

        # Dominant study design
        design_counts: Dict[str, int] = {}
        for item in evidence_items:
            d_name = item.study_design.name
            design_counts[d_name] = design_counts.get(d_name, 0) + 1
        dominant_design = max(design_counts, key=design_counts.get) if design_counts else "UNKNOWN"

        t1 = time.perf_counter()
        latency_ms = (t1 - t0) * 1000.0

        # 4. System 2 Escalation: If ambiguous or explicitly requested
        escalate_to_s2 = force_system_two or (abs(net_margin) < 0.25 and len(evidence_items) >= 2)
        hakken_report = None

        if escalate_to_s2:
            # Build an evidence path for Hakken perturbation
            hops = []
            for item in (supporting[:2] + refuting[:2]):
                hops.append({
                    "source": item.item_id,
                    "target": claim_id,
                    "relation": item.polarity.value,
                    "weight": item.epistemic_weight,
                })
            res = self.hakken_gate.audit_evidence_path(
                hypothesis_id=claim_id,
                path_hops=hops,
            )
            hakken_report = res.to_dict()

        # 5. Final Epistemic Verdict
        if pub_bias_risk >= 0.70 and obs_ratio >= 0.80 and abs(net_margin) < 0.5:
            verdict_text = "CONFOUNDED_EQUIVOCAL"
        elif net_margin >= 0.40 and sum_support_weight >= 1.2:
            verdict_text = "ROBUSTLY_SUPPORTED"
        elif net_margin <= -0.40 and sum_refute_weight >= 1.2:
            verdict_text = "EMPIRICALLY_REFUTED"
        elif total_weight < 0.5:
            verdict_text = "UNGROUNDED_HYPOTHESIS"
        else:
            verdict_text = "CONFOUNDED_EQUIVOCAL"

        # SOM Signature
        sig_data = {
            "claim_id": claim_id,
            "verdict": verdict_text,
            "margin": net_margin,
            "bias_risk": pub_bias_risk,
            "top_sup": supporting[0].item_id if supporting else None,
            "top_ref": refuting[0].item_id if refuting else None,
        }
        som_hash = f"sha256:{hashlib.sha256(json.dumps(sig_data, sort_keys=True).encode('utf-8')).hexdigest()[:24]}"

        return AdversarialClaimAuditVerdict(
            claim_id=claim_id,
            claim_text=claim_text,
            total_evidence_examined=len(evidence_items),
            supporting_count=len(supporting),
            refuting_count=len(refuting),
            ambiguous_count=len(ambiguous),
            net_evidence_margin=net_margin,
            publication_bias_risk=pub_bias_risk,
            dominant_study_design=dominant_design,
            system_one_latency_ms=latency_ms,
            system_two_escalated=escalate_to_s2,
            epistemic_verdict=verdict_text,
            strongest_supporting_item=supporting[0].to_dict() if supporting else None,
            strongest_refuting_item=refuting[0].to_dict() if refuting else None,
            hakken_robustness=hakken_report,
            som_claim_hash=som_hash,
        )
