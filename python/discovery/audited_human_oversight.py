"""
python/discovery/audited_human_oversight.py - ADR-DISCOVERY-049
Audited Human Oversight & Anti-Rubber-Stamping Gate (HITL Epistemic Integrity Protocol).

Solves the empirical failure modes identified in scholarly communication with generative AI:
1. Automation bias & passive rubber-stamping (reviewers accepting AI verdicts without inspection).
2. Epistemic consensus bias (LLMs penalizing heterodox/novel science due to low token frequency).
3. Lack of cryptographically auditable human-machine provenance in editorial workflows.
"""

from __future__ import annotations

import re
import json
import hashlib
from enum import Enum
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field


class OversightVerdictStatus(str, Enum):
    """Integrity state of human oversight in peer review or editorial judgment."""
    ACTIVE_OVERSIGHT_VERIFIED = "ACTIVE_OVERSIGHT_VERIFIED"
    RUBBER_STAMPING_DETECTED = "RUBBER_STAMPING_DETECTED"
    CONSENSUS_BIAS_INTERCEPTED = "CONSENSUS_BIAS_INTERCEPTED"
    COGNITIVE_PROOF_REQUIRED = "COGNITIVE_PROOF_REQUIRED"
    UNJUSTIFIED_REVERSAL = "UNJUSTIFIED_REVERSAL"


class EpistemicTaskCriticality(str, Enum):
    """Criticality level of the scientific task requiring oversight."""
    FORMAL_KERNEL_CHECK = "FORMAL_KERNEL_CHECK"          # Low human burden (machine verifiable)
    DIMENSIONAL_HOMOGENEITY = "DIMENSIONAL_HOMOGENEITY"  # Low human burden
    EMPIRICAL_CONTRADICTION = "EMPIRICAL_CONTRADICTION"  # Medium human burden
    AXIOMATIC_FOUNDATION = "AXIOMATIC_FOUNDATION"        # High human burden (cannot be automated)
    PARADIGMATIC_NOVELTY = "PARADIGMATIC_NOVELTY"        # Critical human burden


@dataclass(frozen=True)
class HumanInteractionTelemetry:
    """Telemetry data capturing the human reviewer's engagement with an AI report."""
    reviewer_id: str
    dwell_time_seconds: float
    counterexamples_inspected: List[str] = field(default_factory=list)
    human_notes_length_chars: int = 0
    substantive_modifications_made: bool = False
    explicit_causal_rationale: str = ""
    answered_inspection_challenge: bool = False


@dataclass(frozen=True)
class CognitiveInspectionChallenge:
    """
    Challenge presented to a human reviewer to verify active cognitive engagement
    and prevent passive clicking/rubber-stamping.
    """
    challenge_id: str
    target_claim_id: str
    prompt: str
    valid_counterexample_key: str
    candidate_options: List[str]


@dataclass(frozen=True)
class OversightAuditRecord:
    """Cryptographic record of audited human oversight."""
    record_id: str
    status: OversightVerdictStatus
    active_oversight_score: float  # 0.0 (rubber-stamp) to 1.0 (deep cognitive inspection)
    task_criticality: EpistemicTaskCriticality
    ai_recommendation: str
    final_decision: str
    consensus_bias_risk: float
    violations_detected: List[str]
    som_oversight_hash: str
    details: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "record_id": self.record_id,
            "status": self.status.value,
            "active_oversight_score": self.active_oversight_score,
            "task_criticality": self.task_criticality.value,
            "ai_recommendation": self.ai_recommendation,
            "final_decision": self.final_decision,
            "consensus_bias_risk": self.consensus_bias_risk,
            "violations_detected": self.violations_detected,
            "som_oversight_hash": self.som_oversight_hash,
            "details": self.details,
        }


class AuditedHumanOversightEngine:
    """
    Engine enforcing active human oversight, neutralizing AI consensus bias,
    and auditing peer-review interaction telemetry against complacency.
    """

    MIN_DWELL_TIME_SECONDS = {
        EpistemicTaskCriticality.FORMAL_KERNEL_CHECK: 2.0,
        EpistemicTaskCriticality.DIMENSIONAL_HOMOGENEITY: 3.0,
        EpistemicTaskCriticality.EMPIRICAL_CONTRADICTION: 15.0,
        EpistemicTaskCriticality.AXIOMATIC_FOUNDATION: 30.0,
        EpistemicTaskCriticality.PARADIGMATIC_NOVELTY: 45.0,
    }

    @classmethod
    def detect_consensus_bias(
        cls,
        ai_critique_text: str,
        is_mathematically_sound: bool,
        conserves_physical_invariants: bool,
    ) -> Tuple[bool, float, List[str]]:
        """
        Detects if an AI rejection is driven by consensus bias (statistical literature frequency)
        rather than rigorous mathematical or physical conservation flaws.
        """
        critique_lower = ai_critique_text.lower()
        consensus_indicators = [
            "unconventional", "novel", "uncommon", "not mainstream", "contrary to literature",
            "atypical", "departing from consensus", "speculative framework", "out of ordinary"
        ]
        flags = [ind for ind in consensus_indicators if ind in critique_lower]

        # If mathematically sound and physical conservation holds, but AI cites consensus departures:
        if is_mathematically_sound and conserves_physical_invariants and flags:
            bias_risk = min(1.0, 0.3 * len(flags) + 0.4)
            return True, bias_risk, [
                f"Consensus bias flag: AI objection grounded in majority literature deviation ('{ind}') "
                f"despite valid mathematical soundness and conservation laws." for ind in flags
            ]

        return False, 0.0, []

    @classmethod
    def generate_cognitive_inspection_challenge(
        cls,
        claim_id: str,
        adversarial_counterexamples: List[str],
    ) -> CognitiveInspectionChallenge:
        """
        Creates an adversarial verification challenge for the human reviewer
        to prevent mindless 'Accept All' rubber-stamping.
        """
        if not adversarial_counterexamples:
            adversarial_counterexamples = ["BoundarySingularityAtInfinity", "ZeroEnergyDissipationLimit"]

        target_counterexample = adversarial_counterexamples[0]
        distractors = [
            "TrivialEquilibriumState",
            "LinearHarmonicApproximation",
            "GaugeInvarianceDivergence",
        ]
        options = [target_counterexample] + distractors[:2]
        # Deterministic pseudo-sort
        options = sorted(options)

        challenge_id = f"CHALLENGE-{hashlib.sha256((claim_id + target_counterexample).encode('utf-8')).hexdigest()[:8]}"
        return CognitiveInspectionChallenge(
            challenge_id=challenge_id,
            target_claim_id=claim_id,
            prompt=(
                f"Adversarial Reviewer Verification: Which of the following represents the primary boundary "
                f"counterexample flagged for claim '{claim_id}'?"
            ),
            valid_counterexample_key=target_counterexample,
            candidate_options=options,
        )

    @classmethod
    def evaluate_oversight_integrity(
        cls,
        claim_id: str,
        task_criticality: EpistemicTaskCriticality,
        ai_recommendation: str,
        human_decision: str,
        telemetry: HumanInteractionTelemetry,
        ai_critique_text: str = "",
        is_mathematically_sound: bool = True,
        conserves_physical_invariants: bool = True,
        flagged_counterexamples: Optional[List[str]] = None,
    ) -> OversightAuditRecord:
        """
        Audits whether human oversight satisfies genuine cognitive inspection standards.
        Flags rubber-stamping, unexamined reversals, and consensus bias.
        """
        violations: List[str] = []
        min_dwell = cls.MIN_DWELL_TIME_SECONDS.get(task_criticality, 15.0)
        oversight_score = 1.0
        status = OversightVerdictStatus.ACTIVE_OVERSIGHT_VERIFIED

        # 1. Dwell-Time Cognitive Inspection Check (Anti-Rubber-Stamping Gate)
        if telemetry.dwell_time_seconds < min_dwell:
            oversight_score -= 0.5
            violations.append(
                f"Insufficient dwell time: Human spent {telemetry.dwell_time_seconds:.1f}s, "
                f"minimum required for {task_criticality.value} is {min_dwell:.1f}s."
            )

        # 2. Inspected Counterexamples Check
        counterexamples = flagged_counterexamples or []
        if counterexamples and not telemetry.counterexamples_inspected:
            oversight_score -= 0.3
            violations.append(
                f"Unexamined adversarial counterexamples: System flagged {len(counterexamples)} "
                f"adversarial failure points, but none were opened or inspected by reviewer."
            )

        # 3. Cognitive Challenge Adjudication
        if task_criticality in [EpistemicTaskCriticality.AXIOMATIC_FOUNDATION, EpistemicTaskCriticality.PARADIGMATIC_NOVELTY]:
            if not telemetry.answered_inspection_challenge:
                oversight_score -= 0.4
                violations.append(
                    "Cognitive inspection challenge unverified: Reviewer bypassed adversarial challenge verification."
                )

        # 4. Unjustified Reversal Check
        if human_decision != ai_recommendation and len(telemetry.explicit_causal_rationale.strip()) < 10:
            oversight_score -= 0.4
            violations.append(
                "Unjustified recommendation reversal: Human overturned AI recommendation without providing "
                "substantive causal rationale."
            )

        # 5. Consensus Bias Screening
        is_bias, bias_score, bias_notes = cls.detect_consensus_bias(
            ai_critique_text, is_mathematically_sound, conserves_physical_invariants
        )
        if is_bias:
            violations.extend(bias_notes)

        # Final Status Synthesis
        if is_bias and ai_recommendation.upper() == "REJECT" and human_decision.upper() == "ACCEPT":
            # Human correctly rescued sound novel science from AI consensus bias
            status = OversightVerdictStatus.CONSENSUS_BIAS_INTERCEPTED
            oversight_score = max(oversight_score, 0.85)
        elif oversight_score < 0.5:
            if telemetry.dwell_time_seconds < min_dwell and not telemetry.substantive_modifications_made:
                status = OversightVerdictStatus.RUBBER_STAMPING_DETECTED
            else:
                status = OversightVerdictStatus.COGNITIVE_PROOF_REQUIRED
        else:
            status = OversightVerdictStatus.ACTIVE_OVERSIGHT_VERIFIED

        record_id = f"OVERSIGHT-{hashlib.sha256((claim_id + telemetry.reviewer_id + human_decision).encode('utf-8')).hexdigest()[:10].upper()}"

        raw_payload = json.dumps(
            {
                "record_id": record_id,
                "claim_id": claim_id,
                "reviewer_id": telemetry.reviewer_id,
                "status": status.value,
                "score": round(max(0.0, min(1.0, oversight_score)), 3),
                "dwell_time": telemetry.dwell_time_seconds,
                "violations": violations,
            },
            sort_keys=True,
        )
        som_hash = f"sha256:{hashlib.sha256(raw_payload.encode('utf-8')).hexdigest()}"

        return OversightAuditRecord(
            record_id=record_id,
            status=status,
            active_oversight_score=round(max(0.0, min(1.0, oversight_score)), 3),
            task_criticality=task_criticality,
            ai_recommendation=ai_recommendation,
            final_decision=human_decision,
            consensus_bias_risk=round(bias_score, 3),
            violations_detected=violations,
            som_oversight_hash=som_hash,
            details={
                "claim_id": claim_id,
                "reviewer_id": telemetry.reviewer_id,
                "min_dwell_required_sec": min_dwell,
                "actual_dwell_sec": telemetry.dwell_time_seconds,
                "counterexamples_checked": len(telemetry.counterexamples_inspected),
            },
        )
