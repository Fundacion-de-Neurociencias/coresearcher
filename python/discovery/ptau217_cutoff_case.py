"""
python/discovery/ptau217_cutoff_case.py - Biomedical showcase: Plasma p-tau217 two-cutoff decision rule as a formal hypothesis.

Inspired by:
Palmqvist et al. (2020, 2024), Ashton et al. (2024), Bateman et al. (Nature Medicine, 2024)
on plasma phospho-tau217 (p-tau217) for identifying Alzheimer's Disease pathology (amyloid PET positivity and tau accumulation).

Clinical claim:
In preclinical and early symptomatic cognitive impairment, a two-cutoff rule (low cutoff c_low, high cutoff c_high)
for plasma p-tau217 triages patients into three tiers:
1. Rule-out tier (p_tau <= c_low): amyloid-beta PET negative with >= 90% sensitivity (NPV high).
2. Rule-in tier (p_tau >= c_high): amyloid-beta PET positive with >= 90% specificity (PPV high).
3. Intermediate/Indeterminate tier (c_low < p_tau < c_high): requires confirmatory CSF or amyloid PET.

Formal analysis:
This module formalizes the mathematical and pathophysiological conditions under which the two-cutoff clinical
decision rule is sound:
- Positive separation between non-AD distribution (Aβ-) and AD distribution (Aβ+).
- Monotonicity: higher plasma p-tau217 corresponds to non-decreasing probability of amyloid PET positivity.
- Normal renal clearance (eGFR >= 60 mL/min/1.73m^2). Chronic kidney disease (CKD) impairs peripheral clearance
  and inflates plasma p-tau217, generating false positives if cutoffs are unadjusted.
- Absence of non-amyloid confounding tauopathies.

We formulate the claim in Z3 via `python.discovery.formal_hypothesis`, examine the necessity of each physiological
assumption, synthesize checkable counterexamples when assumptions are dropped, and provide an empirical cohort simulator.
"""

from __future__ import annotations

import math
import random
from dataclasses import dataclass
from typing import Any, Callable, Dict, List, Optional, Tuple

from python.discovery.formal_hypothesis import FormalHypothesisError, Hypothesis, HypothesisEvaluator, Variable

STATUS = "SHOWCASE: plasma p-tau217 two-cutoff clinical triage rule under formal assumption decomposition"
SOURCE = "Palmqvist et al. (2024), Ashton et al. (2024), Bateman et al. (2024)"

ASSUMPTIONS = (
    "biomarker_separation",
    "preserved_renal_function",
    "ordered_cutoffs",
)



def ptau_variables() -> List[Variable]:
    """Variables representing patient biomarker values, cutoffs, and diagnostic indicators."""
    names = [
        "c_low",
        "c_high",
        "ptau_val",
        "amyloid_pet",  # 1 = amyloid positive, 0 = amyloid negative
        "egfr",         # renal filtration rate (mL/min/1.73m^2)
        "true_pathology",
        "clearance_factor",
    ]
    return [Variable(n, continuous=True) for n in names]


def ptau_scope() -> str:
    """The physiological and operational domain scope."""
    return (
        "(c_low > 0) and (c_high > 0) and (ptau_val >= 0) and "
        "(amyloid_pet == 0 or amyloid_pet == 1) and "
        "(egfr > 0) and (clearance_factor > 0) and "
        "((egfr >= 60) or (clearance_factor > 1.0))"
    )


def assumption_predicates() -> Dict[str, str]:
    """The explicit physiological and diagnostic assumptions."""
    return {
        "ordered_cutoffs": "c_low < c_high",
        "biomarker_separation": (
            "((amyloid_pet != 0) or ((ptau_val / clearance_factor) <= c_low)) and "
            "((amyloid_pet != 1) or ((ptau_val / clearance_factor) >= c_high))"
        ),
        "preserved_renal_function": "clearance_factor == 1",
    }



def ptau_claims() -> List[str]:
    """Claims asserted by the two-cutoff clinical decision protocol:
    1. Rule-out safety: If ptau_val <= c_low, then amyloid_pet == 0 (no false negatives in rule-out zone).
    2. Rule-in precision: If ptau_val >= c_high, then amyloid_pet == 1 (no false positives in rule-in zone).
    """
    return [
        "(ptau_val > c_low) or (amyloid_pet == 0)",
        "(ptau_val < c_high) or (amyloid_pet == 1)",
    ]



def ptau217_hypothesis(
    drop: Tuple[str, ...] = (),
    hypothesis_id: Optional[str] = None,
) -> Hypothesis:
    """Constructs the formal hypothesis for the p-tau217 cutoff decision rule."""
    unknown = set(drop) - set(ASSUMPTIONS)
    if unknown:
        raise ValueError(f"Unknown assumptions {sorted(unknown)}; choose from {ASSUMPTIONS}.")
    preds = assumption_predicates()
    active_assumptions = [preds[a] for a in ASSUMPTIONS if a not in drop]
    suffix = "" if not drop else "-without-" + "-".join(drop)
    return Hypothesis(
        hypothesis_id=hypothesis_id or f"PTAU217-CUTOFF-RULE{suffix}",
        variables=ptau_variables(),
        scope=ptau_scope(),
        assumptions=active_assumptions,
        claims=ptau_claims(),
        statement=(
            "Under preserved renal clearance (eGFR >= 60) and positive biomarker distribution separation, "
            "the two-cutoff decision boundary for plasma p-tau217 guarantees rule-in precision (p >= c_high implies "
            "amyloid PET positive) and rule-out safety (p <= c_low implies amyloid PET negative)."
        ),
    )


def verdict(hypothesis: Hypothesis, max_examples: int = 1) -> Dict[str, Any]:
    """Evaluates formal hypothesis with Z3 solver and returns court verdict."""
    try:
        report = HypothesisEvaluator.evaluate(hypothesis, max_examples=max_examples)
    except FormalHypothesisError as exc:
        if "could not decide" not in str(exc):
            raise
        return {
            "hypothesis_id": hypothesis.hypothesis_id,
            "status": "UNDECIDED",
            "content_verdict": None,
            "reason": str(exc),
            "witness": None,
        }

    content = report.content_verdict.value
    if content == "UNFALSIFIABLE" and not report.conflicting_assumption_sets:
        status = "PROVED"
    elif content in ("FALSIFIABLE", "SELF_CONTRADICTORY"):
        status = "REFUTED"
    else:
        status = f"FLAGGED_{content}"

    witness = report.falsifier_examples[0] if report.falsifier_examples else None
    violated = hypothesis.violated_claims(witness) if witness is not None else []
    return {
        "hypothesis_id": hypothesis.hypothesis_id,
        "status": status,
        "content_verdict": content,
        "conflicting_assumption_sets": report.conflicting_assumption_sets,
        "witness": witness,
        "violated_claims": violated,
    }



def necessity_table() -> Dict[str, str]:
    """Tests necessity of each clinical assumption by dropping it one at a time."""
    table = {}
    for a in ASSUMPTIONS:
        h = ptau217_hypothesis(drop=(a,))
        res = verdict(h)
        table[a] = "NECESSARY" if res["status"] == "REFUTED" else "REDUNDANT"
    return table


# --------------------------------------------------------------------------- Empirical Cohort Simulator


@dataclass
class PatientRecord:
    patient_id: str
    amyloid_pet: int         # 0 or 1
    ptau217_pg_ml: float
    egfr: float
    hippocampal_vol_z: float


def simulate_patient_cohort(
    n_patients: int = 500,
    amyloid_prevalence: float = 0.35,
    ckd_prevalence: float = 0.15,
    rng_seed: int = 42,
) -> List[PatientRecord]:
    """Generates synthetic cohort matching clinical cohorts (e.g. BioFinder-2 / ADNI).

    Amyloid negative: log-normal p-tau217 centered at ~0.45 pg/mL, sd=0.3.
    Amyloid positive: log-normal p-tau217 centered at ~1.85 pg/mL, sd=0.4.
    CKD (eGFR < 60) introduces an elevation factor of 1.4x - 2.0x due to decreased clearance.
    """
    rng = random.Random(rng_seed)
    cohort: List[PatientRecord] = []
    for i in range(n_patients):
        is_amyloid_pos = 1 if rng.random() < amyloid_prevalence else 0
        is_ckd = rng.random() < ckd_prevalence

        egfr = rng.uniform(25.0, 55.0) if is_ckd else rng.uniform(65.0, 115.0)
        # Renal elevation factor
        renal_factor = (90.0 / egfr) ** 0.5 if egfr < 60.0 else 1.0

        if is_amyloid_pos:
            base_ptau = math.exp(rng.gauss(0.60, 0.35))
            hip_z = rng.gauss(-1.8, 0.7)
        else:
            base_ptau = math.exp(rng.gauss(-0.80, 0.30))
            hip_z = rng.gauss(-0.2, 0.6)

        final_ptau = base_ptau * renal_factor
        cohort.append(
            PatientRecord(
                patient_id=f"PATIENT-{i+1:04d}",
                amyloid_pet=is_amyloid_pos,
                ptau217_pg_ml=final_ptau,
                egfr=egfr,
                hippocampal_vol_z=hip_z,
            )
        )
    return cohort


def evaluate_two_cutoff_rule(
    cohort: List[PatientRecord],
    c_low: float = 0.70,
    c_high: float = 1.30,
    filter_ckd: bool = False,
) -> Dict[str, Any]:
    """Evaluates clinical performance of two-cutoff rule on a cohort."""
    pts = [p for p in cohort if (p.egfr >= 60.0 or not filter_ckd)]
    rule_out = [p for p in pts if p.ptau217_pg_ml <= c_low]
    rule_in = [p for p in pts if p.ptau217_pg_ml >= c_high]
    indeterminate = [p for p in pts if c_low < p.ptau217_pg_ml < c_high]

    # Rule-out performance (NPV / sensitivity)
    true_negs_rule_out = sum(1 for p in rule_out if p.amyloid_pet == 0)
    false_negs_rule_out = sum(1 for p in rule_out if p.amyloid_pet == 1)
    npv = true_negs_rule_out / len(rule_out) if rule_out else 1.0

    # Rule-in performance (PPV / specificity)
    true_pos_rule_in = sum(1 for p in rule_in if p.amyloid_pet == 1)
    false_pos_rule_in = sum(1 for p in rule_in if p.amyloid_pet == 0)
    ppv = true_pos_rule_in / len(rule_in) if rule_in else 1.0

    return {
        "total_patients": len(pts),
        "rule_out_count": len(rule_out),
        "rule_out_npv": round(npv, 4),
        "false_negatives": false_negs_rule_out,
        "rule_in_count": len(rule_in),
        "rule_in_ppv": round(ppv, 4),
        "false_positives": false_pos_rule_in,
        "indeterminate_count": len(indeterminate),
        "indeterminate_pct": round(len(indeterminate) / len(pts), 4) if pts else 0.0,
    }
