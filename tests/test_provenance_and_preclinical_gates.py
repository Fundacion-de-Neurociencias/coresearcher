"""
tests/test_provenance_and_preclinical_gates.py - Unit Test Suite for Provenance Sidecars & Four Pre-Clinical Gates (ADR-DISCOVERY-078)
"""

from __future__ import annotations
import json
import math
import pytest
from typing import Dict, Any

from python.discovery.provenance_sidecar_engine import (
    ToolExecutionStatus,
    ProvenanceSidecar,
    ProvenanceSidecarEngine,
)
from python.discovery.preclinical_gates_engine import (
    PreClinicalGateType,
    PassportVerdict,
    GateThresholdsConfig,
    SingleGateEvaluation,
    PreClinicalPassport,
    PreClinicalGatesValidator,
)
from python.discovery.physical_theorem_court import (
    PhysicalCoherenceCourt,
    PhysicalConservationType,
    CourtVerdict,
)


def _sample_calculation_tool(base: float, exponent: float) -> Dict[str, float]:
    """Sample deterministic scientific tool for sidecar testing."""
    return {"power": float(base ** exponent), "root": float(math.sqrt(abs(base)))}


def test_provenance_sidecar_generation_and_serialization(tmp_path):
    """Verify tool execution wrapping, metadata capture, and disk serialization."""
    engine = ProvenanceSidecarEngine(current_git_sha="commit_abc123")
    inputs = {"base": 16.0, "exponent": 0.5}
    sidecar_file = str(tmp_path / "calc_test.sidecar.json")

    result, sidecar = engine.wrap_tool_execution(
        tool_name="sample_calculation_tool",
        tool_fn=_sample_calculation_tool,
        inputs=inputs,
        output_sidecar_path=sidecar_file,
        reproducibility_cmd="python -m sample_calc --base 16.0 --exponent 0.5"
    )

    assert result == {"power": 4.0, "root": 4.0}
    assert sidecar.tool_name == "sample_calculation_tool"
    assert sidecar.status == ToolExecutionStatus.SUCCESS
    assert sidecar.git_commit_sha == "commit_abc123"
    assert sidecar.execution_time_seconds > 0.0
    assert len(sidecar.verification_hash) == 64

    # Load from disk and verify identity
    loaded_sidecar = ProvenanceSidecar.load(sidecar_file)
    assert loaded_sidecar.sidecar_id == sidecar.sidecar_id
    assert loaded_sidecar.verification_hash == sidecar.verification_hash
    assert loaded_sidecar.raw_output_digest == sidecar.raw_output_digest

    # Arbitrate in court
    court = PhysicalCoherenceCourt()
    court_res = court.audit_provenance_sidecar_report("CLAIM_SIDECAR_01", sidecar.to_dict())
    assert court_res.verdict == CourtVerdict.VERIFIED_COHERENT
    assert court_res.conservation_audit[0]["law"] == "PROVENANCE_SIDECAR_VALIDITY"


def test_provenance_sidecar_blocked_missing_data(tmp_path):
    """Verify radical epistemic honesty: blocked status when upstream dataset is missing."""
    engine = ProvenanceSidecarEngine()
    sidecar_file = str(tmp_path / "blocked_tool.sidecar.json")

    sidecar = engine.record_blocked_missing_data(
        tool_name="AlphaGenome_Variant_Scanner",
        missing_resource="Private_Assay_Cohort_2026.parquet",
        inputs={"variant_id": "chr1:12345:A>G"},
        output_sidecar_path=sidecar_file
    )

    assert sidecar.status == ToolExecutionStatus.BLOCKED_MISSING_DATA
    assert "Private_Assay_Cohort_2026.parquet" in sidecar.blocking_reason
    assert sidecar.raw_output_digest == "NONE_BLOCKED_UNAVAILABLE"

    # Attempting to re-run a blocked sidecar must fail honestly
    reproduced, reason = engine.verify_sidecar(sidecar, _sample_calculation_tool)
    assert reproduced is False
    assert "Cannot re-run: Sidecar was marked BLOCKED" in reason

    # Arbitrate in court: blocked tool must not pass as verified
    court = PhysicalCoherenceCourt()
    court_res = court.audit_provenance_sidecar_report("CLAIM_SIDECAR_BLOCKED", sidecar.to_dict())
    assert court_res.verdict == CourtVerdict.REJECTED_CONSERVATION_VIOLATION


def test_provenance_sidecar_reproducibility_verification():
    """Verify that re-executing tool calls from sidecar matches output hash."""
    engine = ProvenanceSidecarEngine()
    inputs = {"base": 9.0, "exponent": 2.0}

    result, sidecar = engine.wrap_tool_execution(
        tool_name="sample_calculation_tool",
        tool_fn=_sample_calculation_tool,
        inputs=inputs
    )

    reproduced, reason = engine.verify_sidecar(sidecar, _sample_calculation_tool)
    assert reproduced is True
    assert "output hash matches" in reason

    # Tampered inputs should fail reproducibility
    tampered_sidecar = ProvenanceSidecar(
        sidecar_id="TAMPERED_01",
        tool_name="sample_calculation_tool",
        execution_timestamp=sidecar.execution_timestamp,
        git_commit_sha="commit_tampered",
        input_parameters={"base": 9.0, "exponent": 3.0},  # Tampered!
        input_hash="fake_hash",
        raw_output_digest=sidecar.raw_output_digest,
        execution_time_seconds=0.01,
        reproducibility_command="python tampered",
        status=ToolExecutionStatus.SUCCESS
    )
    tampered_repro, tampered_reason = engine.verify_sidecar(tampered_sidecar, _sample_calculation_tool)
    assert tampered_repro is False
    assert "Reproducibility divergence" in tampered_reason


def test_four_preclinical_gates_candidate_all_pass():
    """Verify candidate target evaluation passing all 4 pre-clinical gates."""
    validator = PreClinicalGatesValidator()

    evidence_payload = {
        "genetic_evidence": {
            "causality_score": 0.85,
            "summary": "Mendelian causal linkage with ClinVar pathogenic confirmation.",
            "sidecar_id": "SIDECAR_GENETICS_001"
        },
        "structural_evidence": {
            "mean_plddt": 88.5,
            "pocket_druggability_score": 0.78,
            "hinges_detected": 2,
            "sidecar_id": "SIDECAR_ALPHA_FOLD_002"
        },
        "biophysical_mechanism": {
            "theta_target_stimulated": 0.76,
            "theta_target_basal": 0.04,
            "sidecar_id": "SIDECAR_SPP_TITRATION_003"
        },
        "safety_evidence": {
            "homolog_selectivity_ratio": 450.0,
            "acute_toxic_alerts_count": 0,
            "sidecar_id": "SIDECAR_CHEMBL_SAFETY_004"
        }
    }

    passport = validator.evaluate_candidate(
        candidate_id="CANDIDATE_TROPONIN_MIMETIC_01",
        target_name="Troponin C Site II",
        indication="Hypertrophic Cardiomyopathy",
        evidence_payload=evidence_payload
    )

    assert passport.all_gates_passed is True
    assert passport.passport_verdict == PassportVerdict.CERTIFIED_PRECLINICAL_READY
    assert len(passport.provenance_sidecars) == 4
    assert len(passport.passport_hash) == 64

    # Verify each gate
    for gate_type in PreClinicalGateType:
        ev = passport.gate_evaluations[gate_type.value]
        assert ev.passed is True
        assert ev.is_blocked is False

    # Arbitrate in court
    court = PhysicalCoherenceCourt()
    court_res = court.audit_preclinical_gates_report("CLAIM_PASSPORT_01", passport.to_dict())
    assert court_res.verdict == CourtVerdict.VERIFIED_COHERENT
    assert court_res.conservation_audit[0]["law"] == "PRECLINICAL_FOUR_GATES_COHERENCE"


def test_four_preclinical_gates_candidate_fails_safety_offtarget():
    """Verify rejection when Gate 4 (safety/off-target) fails."""
    validator = PreClinicalGatesValidator()

    evidence_payload = {
        "genetic_evidence": {"causality_score": 0.90},
        "structural_evidence": {"mean_plddt": 85.0, "pocket_druggability_score": 0.80},
        "biophysical_mechanism": {"theta_target_stimulated": 0.75, "theta_target_basal": 0.05},
        "safety_evidence": {
            "homolog_selectivity_ratio": 25.0,  # Below threshold 100.0!
            "acute_toxic_alerts_count": 1       # Severe hERG alert!
        }
    }

    passport = validator.evaluate_candidate(
        candidate_id="CANDIDATE_TOXIC_HOMOLOG_02",
        target_name="Kinase Target X",
        indication="Neuroinflammation",
        evidence_payload=evidence_payload
    )

    assert passport.all_gates_passed is False
    assert passport.passport_verdict == PassportVerdict.REJECTED_GATE_FAILURE
    assert passport.gate_evaluations[PreClinicalGateType.SAFETY_OFFTARGET_GATE.value].passed is False

    # Arbitrate in court: failure must lead to rejection
    court = PhysicalCoherenceCourt()
    court_res = court.audit_preclinical_gates_report("CLAIM_PASSPORT_FAILS_SAFETY", passport.to_dict())
    assert court_res.verdict == CourtVerdict.REJECTED_CONSERVATION_VIOLATION


def test_four_preclinical_gates_missing_evidence_triggers_blocked():
    """Verify that omitting a gate's evidence payload marks the passport as BLOCKED."""
    validator = PreClinicalGatesValidator()

    # Omit structural evidence completely
    evidence_payload = {
        "genetic_evidence": {"causality_score": 0.95},
        # "structural_evidence" is missing!
        "biophysical_mechanism": {"theta_target_stimulated": 0.80, "theta_target_basal": 0.02},
        "safety_evidence": {"homolog_selectivity_ratio": 200.0, "acute_toxic_alerts_count": 0}
    }

    passport = validator.evaluate_candidate(
        candidate_id="CANDIDATE_UNSTRUCTURED_03",
        target_name="Novel Uncharacterized ORF",
        indication="Amyotrophic Lateral Sclerosis",
        evidence_payload=evidence_payload
    )

    assert passport.all_gates_passed is False
    assert passport.passport_verdict == PassportVerdict.BLOCKED_MISSING_DATA
    struct_eval = passport.gate_evaluations[PreClinicalGateType.STRUCTURAL_DRUGGABILITY_GATE.value]
    assert struct_eval.is_blocked is True
    assert "Missing structural/pocket model" in struct_eval.evidence_summary


def test_preclinical_gates_versioned_threshold_override():
    """Verify program-specific threshold overrides via versioned config."""
    validator = PreClinicalGatesValidator()

    evidence_payload = {
        "genetic_evidence": {"causality_score": 0.75},  # Passes canonical (>=0.70), fails strict (>=0.90)
        "structural_evidence": {"mean_plddt": 80.0, "pocket_druggability_score": 0.70},
        "biophysical_mechanism": {"theta_target_stimulated": 0.70, "theta_target_basal": 0.05},
        "safety_evidence": {"homolog_selectivity_ratio": 150.0, "acute_toxic_alerts_count": 0}
    }

    # Canonical config: score 0.75 passes
    canonical_passport = validator.evaluate_candidate(
        candidate_id="CANDIDATE_OVERRIDE_04",
        target_name="Tau Aggregation Inhibitor",
        indication="Alzheimer's Disease",
        evidence_payload=evidence_payload,
        config=GateThresholdsConfig(config_version="v1.0.0-canonical", min_genetic_causality_score=0.70)
    )
    assert canonical_passport.all_gates_passed is True

    # Strict config: score 0.75 fails
    strict_passport = validator.evaluate_candidate(
        candidate_id="CANDIDATE_OVERRIDE_04",
        target_name="Tau Aggregation Inhibitor",
        indication="Alzheimer's Disease",
        evidence_payload=evidence_payload,
        config=GateThresholdsConfig(config_version="v2.0.0-strict-fda", min_genetic_causality_score=0.90)
    )
    assert strict_passport.all_gates_passed is False
    assert strict_passport.gate_evaluations[PreClinicalGateType.GENETIC_CAUSALITY_GATE.value].passed is False
    assert strict_passport.config_version == "v2.0.0-strict-fda"
