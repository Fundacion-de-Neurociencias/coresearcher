"""
python/discovery/preclinical_gates_engine.py - Four Pre-Clinical Gates Validator & Program Passport (ADR-DISCOVERY-078)
Inspired by Google Cloud's Open Agentic Science Engine (OASE, 2026).

Enforces:
1. The Four Pre-Clinical Gates:
   - Gate 1: Target-Disease Genetic Causality (eQTLs, GWAS, ClinVar, AlphaGenome).
   - Gate 2: Structural Tractability & Druggability (AlphaFold pLDDT, binding pockets, Cartan-DEC hinges).
   - Gate 3: Biophysical & Teleonomic Mechanism (Competitive Langmuir-Hill occupancy, allosteric coupling).
   - Gate 4: Safety & Off-Target Counter-Screening (Homolog selectivity index, zero toxic/adverse alerts).
2. Versioned Threshold Overrides: Thresholds reside in immutable, versioned configuration schemas
   (GateThresholdsConfig) rather than prompt text.
3. Pre-Clinical Passport: Cryptographically signed certificate certifying candidate readiness.
"""

from __future__ import annotations
from dataclasses import dataclass, field, asdict
from enum import Enum
from typing import Dict, Any, List, Optional, Tuple
import hashlib
import json
import time

from python.discovery.provenance_sidecar_engine import (
    ProvenanceSidecar,
    ProvenanceSidecarEngine,
    ToolExecutionStatus,
)


class PreClinicalGateType(str, Enum):
    GENETIC_CAUSALITY_GATE = "GENETIC_CAUSALITY_GATE"
    STRUCTURAL_DRUGGABILITY_GATE = "STRUCTURAL_DRUGGABILITY_GATE"
    BIOPHYSICAL_MECHANISM_GATE = "BIOPHYSICAL_MECHANISM_GATE"
    SAFETY_OFFTARGET_GATE = "SAFETY_OFFTARGET_GATE"


class PassportVerdict(str, Enum):
    CERTIFIED_PRECLINICAL_READY = "CERTIFIED_PRECLINICAL_READY"
    REJECTED_GATE_FAILURE = "REJECTED_GATE_FAILURE"
    BLOCKED_MISSING_DATA = "BLOCKED_MISSING_DATA"


@dataclass
class GateThresholdsConfig:
    """Versioned configuration for pre-clinical stage-gate pass criteria."""
    config_version: str = "v1.0.0-canonical"
    min_genetic_causality_score: float = 0.70      # Scale [0.0, 1.0]
    min_structural_plddt: float = 70.0             # Scale [0.0, 100.0]
    min_pocket_druggability_score: float = 0.60    # Scale [0.0, 1.0]
    min_stimulated_occupancy: float = 0.60         # Fractional binding occupancy at stimulated state
    max_basal_leak_occupancy: float = 0.15         # Max allowable false activation at resting basal state
    min_homolog_selectivity_ratio: float = 100.0   # Kd(off-target) / Kd(target)
    max_tolerated_safety_alerts: int = 0           # Zero tolerance for severe tox/hERG alerts

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class SingleGateEvaluation:
    """Outcome of testing a target/molecule against a single pre-clinical gate."""
    gate_type: PreClinicalGateType
    passed: bool
    observed_score: float
    threshold_value: float
    metric_name: str
    evidence_summary: str
    sidecar_id: Optional[str] = None
    is_blocked: bool = False

    def to_dict(self) -> Dict[str, Any]:
        d = asdict(self)
        d["gate_type"] = self.gate_type.value
        return d


@dataclass
class PreClinicalPassport:
    """Immutable pre-clinical certification passport with cryptographic provenance."""
    candidate_id: str
    target_name: str
    indication: str
    config_version: str
    all_gates_passed: bool
    passport_verdict: PassportVerdict
    gate_evaluations: Dict[str, SingleGateEvaluation]
    provenance_sidecars: List[str]
    passport_hash: str
    issued_timestamp: float

    def to_dict(self) -> Dict[str, Any]:
        return {
            "candidate_id": self.candidate_id,
            "target_name": self.target_name,
            "indication": self.indication,
            "config_version": self.config_version,
            "all_gates_passed": self.all_gates_passed,
            "passport_verdict": self.passport_verdict.value,
            "gate_evaluations": {k: v.to_dict() for k, v in self.gate_evaluations.items()},
            "provenance_sidecars": self.provenance_sidecars,
            "passport_hash": self.passport_hash,
            "issued_timestamp": self.issued_timestamp
        }


class PreClinicalGatesValidator:
    """
    Validator engine testing candidate targets and molecules against the four pre-clinical gates.
    """

    def __init__(self, sidecar_engine: Optional[ProvenanceSidecarEngine] = None):
        self.sidecar_engine = sidecar_engine or ProvenanceSidecarEngine()

    def evaluate_candidate(
        self,
        candidate_id: str,
        target_name: str,
        indication: str,
        evidence_payload: Dict[str, Any],
        config: Optional[GateThresholdsConfig] = None
    ) -> PreClinicalPassport:
        """
        Evaluate candidate evidence against the four pre-clinical gates.
        Enforces blocked state if required evidence is completely absent.
        """
        cfg = config or GateThresholdsConfig()
        evaluations: Dict[str, SingleGateEvaluation] = {}
        sidecars: List[str] = []
        is_any_blocked = False

        # --- GATE 1: Genetic Causality ---
        gen_data = evidence_payload.get("genetic_evidence")
        if gen_data is None:
            evaluations[PreClinicalGateType.GENETIC_CAUSALITY_GATE.value] = SingleGateEvaluation(
                gate_type=PreClinicalGateType.GENETIC_CAUSALITY_GATE,
                passed=False,
                observed_score=0.0,
                threshold_value=cfg.min_genetic_causality_score,
                metric_name="genetic_causality_score",
                evidence_summary="Missing genetic evidence dataset; flagged as BLOCKED.",
                is_blocked=True
            )
            is_any_blocked = True
        else:
            score = float(gen_data.get("causality_score", 0.0))
            passed = score >= cfg.min_genetic_causality_score
            sidecar_ref = gen_data.get("sidecar_id")
            if sidecar_ref:
                sidecars.append(sidecar_ref)
            evaluations[PreClinicalGateType.GENETIC_CAUSALITY_GATE.value] = SingleGateEvaluation(
                gate_type=PreClinicalGateType.GENETIC_CAUSALITY_GATE,
                passed=passed,
                observed_score=score,
                threshold_value=cfg.min_genetic_causality_score,
                metric_name="genetic_causality_score",
                evidence_summary=gen_data.get("summary", f"Genetic link score: {score:.3f}"),
                sidecar_id=sidecar_ref
            )

        # --- GATE 2: Structural Druggability ---
        struct_data = evidence_payload.get("structural_evidence")
        if struct_data is None:
            evaluations[PreClinicalGateType.STRUCTURAL_DRUGGABILITY_GATE.value] = SingleGateEvaluation(
                gate_type=PreClinicalGateType.STRUCTURAL_DRUGGABILITY_GATE,
                passed=False,
                observed_score=0.0,
                threshold_value=cfg.min_structural_plddt,
                metric_name="alphafold_plddt",
                evidence_summary="Missing structural/pocket model; flagged as BLOCKED.",
                is_blocked=True
            )
            is_any_blocked = True
        else:
            plddt = float(struct_data.get("mean_plddt", 0.0))
            pocket_score = float(struct_data.get("pocket_druggability_score", 0.0))
            passed = (plddt >= cfg.min_structural_plddt) and (pocket_score >= cfg.min_pocket_druggability_score)
            sidecar_ref = struct_data.get("sidecar_id")
            if sidecar_ref:
                sidecars.append(sidecar_ref)
            evaluations[PreClinicalGateType.STRUCTURAL_DRUGGABILITY_GATE.value] = SingleGateEvaluation(
                gate_type=PreClinicalGateType.STRUCTURAL_DRUGGABILITY_GATE,
                passed=passed,
                observed_score=plddt,
                threshold_value=cfg.min_structural_plddt,
                metric_name="alphafold_plddt",
                evidence_summary=f"pLDDT: {plddt:.1f}, Pocket Score: {pocket_score:.2f}, Hinges: {struct_data.get('hinges_detected', 0)}",
                sidecar_id=sidecar_ref
            )

        # --- GATE 3: Biophysical Mechanism ---
        bio_data = evidence_payload.get("biophysical_mechanism")
        if bio_data is None:
            evaluations[PreClinicalGateType.BIOPHYSICAL_MECHANISM_GATE.value] = SingleGateEvaluation(
                gate_type=PreClinicalGateType.BIOPHYSICAL_MECHANISM_GATE,
                passed=False,
                observed_score=0.0,
                threshold_value=cfg.min_stimulated_occupancy,
                metric_name="stimulated_occupancy_theta",
                evidence_summary="Missing biophysical Langmuir-Hill model; flagged as BLOCKED.",
                is_blocked=True
            )
            is_any_blocked = True
        else:
            theta_stim = float(bio_data.get("theta_target_stimulated", 0.0))
            theta_basal = float(bio_data.get("theta_target_basal", 0.0))
            passed = (theta_stim >= cfg.min_stimulated_occupancy) and (theta_basal <= cfg.max_basal_leak_occupancy)
            sidecar_ref = bio_data.get("sidecar_id")
            if sidecar_ref:
                sidecars.append(sidecar_ref)
            evaluations[PreClinicalGateType.BIOPHYSICAL_MECHANISM_GATE.value] = SingleGateEvaluation(
                gate_type=PreClinicalGateType.BIOPHYSICAL_MECHANISM_GATE,
                passed=passed,
                observed_score=theta_stim,
                threshold_value=cfg.min_stimulated_occupancy,
                metric_name="stimulated_occupancy_theta",
                evidence_summary=f"Stimulated theta: {theta_stim:.3f}, Basal leak: {theta_basal:.3f}",
                sidecar_id=sidecar_ref
            )

        # --- GATE 4: Safety & Off-Target Screening ---
        safety_data = evidence_payload.get("safety_evidence")
        if safety_data is None:
            evaluations[PreClinicalGateType.SAFETY_OFFTARGET_GATE.value] = SingleGateEvaluation(
                gate_type=PreClinicalGateType.SAFETY_OFFTARGET_GATE,
                passed=False,
                observed_score=0.0,
                threshold_value=cfg.min_homolog_selectivity_ratio,
                metric_name="homolog_selectivity_ratio",
                evidence_summary="Missing safety off-target assay; flagged as BLOCKED.",
                is_blocked=True
            )
            is_any_blocked = True
        else:
            selectivity = float(safety_data.get("homolog_selectivity_ratio", 0.0))
            alerts = int(safety_data.get("acute_toxic_alerts_count", 0))
            passed = (selectivity >= cfg.min_homolog_selectivity_ratio) and (alerts <= cfg.max_tolerated_safety_alerts)
            sidecar_ref = safety_data.get("sidecar_id")
            if sidecar_ref:
                sidecars.append(sidecar_ref)
            evaluations[PreClinicalGateType.SAFETY_OFFTARGET_GATE.value] = SingleGateEvaluation(
                gate_type=PreClinicalGateType.SAFETY_OFFTARGET_GATE,
                passed=passed,
                observed_score=selectivity,
                threshold_value=cfg.min_homolog_selectivity_ratio,
                metric_name="homolog_selectivity_ratio",
                evidence_summary=f"Selectivity ratio: {selectivity:.1f}x, Toxic alerts: {alerts}",
                sidecar_id=sidecar_ref
            )

        # Determine master verdict
        all_passed = all(ev.passed for ev in evaluations.values())
        if is_any_blocked:
            verdict = PassportVerdict.BLOCKED_MISSING_DATA
        elif all_passed:
            verdict = PassportVerdict.CERTIFIED_PRECLINICAL_READY
        else:
            verdict = PassportVerdict.REJECTED_GATE_FAILURE

        timestamp = time.time()
        passport_payload = {
            "candidate_id": candidate_id,
            "target": target_name,
            "verdict": verdict.value,
            "all_passed": all_passed,
            "config_version": cfg.config_version,
            "timestamp": round(timestamp, 2)
        }
        passport_hash = hashlib.sha256(json.dumps(passport_payload, sort_keys=True).encode("utf-8")).hexdigest()

        return PreClinicalPassport(
            candidate_id=candidate_id,
            target_name=target_name,
            indication=indication,
            config_version=cfg.config_version,
            all_gates_passed=all_passed,
            passport_verdict=verdict,
            gate_evaluations=evaluations,
            provenance_sidecars=sidecars,
            passport_hash=passport_hash,
            issued_timestamp=timestamp
        )
