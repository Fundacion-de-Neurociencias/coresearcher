"""
tests/test_phenix_molprobity_oracle.py - Unit Test Suite for Phenix MolProbity Structural Geometry Oracle (ADR-DISCOVERY-079)
"""

from __future__ import annotations
import math
import numpy as np
import pytest

from python.discovery.phenix_molprobity_oracle import (
    RamachandranConformation,
    StructuralQualityTier,
    AtomCoordinate,
    ResidueBackboneAngles,
    StericClashDetail,
    MolProbityReport,
    PhenixMolProbityOracle,
    compute_dihedral_angle,
    classify_ramachandran_region,
    classify_rotamer_outlier,
)
from python.discovery.physical_theorem_court import (
    PhysicalCoherenceCourt,
    PhysicalConservationType,
    CourtVerdict,
)
from python.discovery.preclinical_gates_engine import (
    PreClinicalGatesValidator,
    PreClinicalGateType,
    PassportVerdict,
    GateThresholdsConfig,
)


def test_dihedral_angle_calculation():
    """Verify analytical dihedral angle torsion calculation across canonical geometric angles."""
    # Trans planar configuration: points along zigzag in XY plane -> dihedral = 180 deg
    p1 = np.array([0.0, 1.0, 0.0])
    p2 = np.array([0.0, 0.0, 0.0])
    p3 = np.array([1.0, 0.0, 0.0])
    p4 = np.array([1.0, -1.0, 0.0])
    angle_trans = compute_dihedral_angle(p1, p2, p3, p4)
    assert abs(abs(angle_trans) - 180.0) < 1e-4

    # Cis planar configuration: U-shape in XY plane -> dihedral = 0 deg
    p4_cis = np.array([1.0, 1.0, 0.0])
    angle_cis = compute_dihedral_angle(p1, p2, p3, p4_cis)
    assert abs(angle_cis - 0.0) < 1e-4

    # Orthogonal 90 deg configuration: p4 rotated into +Z axis
    p4_ortho = np.array([1.0, 0.0, 1.0])
    angle_ortho = compute_dihedral_angle(p1, p2, p3, p4_ortho)
    assert abs(abs(angle_ortho) - 90.0) < 1e-4


def test_ramachandran_region_classification():
    """Verify Lovell / MolProbity contour classification for alpha, beta, and outlier conformations."""
    # Alpha-helical core: phi=-60, psi=-45
    assert classify_ramachandran_region(-60.0, -45.0, "ALA") == RamachandranConformation.FAVORED

    # Beta-sheet core: phi=-120, psi=130
    assert classify_ramachandran_region(-120.0, 130.0, "VAL") == RamachandranConformation.FAVORED

    # Left-handed alpha: phi=60, psi=40
    assert classify_ramachandran_region(60.0, 40.0, "ASN") == RamachandranConformation.FAVORED

    # Proline restricted configuration
    assert classify_ramachandran_region(-60.0, -30.0, "PRO") == RamachandranConformation.FAVORED
    assert classify_ramachandran_region(60.0, 60.0, "PRO") == RamachandranConformation.OUTLIER

    # Disallowed steric collision region: phi=+60, psi=-120 for non-glycine
    assert classify_ramachandran_region(60.0, -120.0, "ALA") == RamachandranConformation.OUTLIER


def test_rotamer_outlier_classification():
    """Verify sidechain chi1 rotamer outlier detection against canonical g+, t, g- states."""
    # Canonical rotamers: 60 (g+), 180 (t), -60 (g-)
    assert classify_rotamer_outlier(62.0, "LEU") is False
    assert classify_rotamer_outlier(178.0, "PHE") is False
    assert classify_rotamer_outlier(-58.0, "MET") is False

    # Outlier state: 120.0 (eclipsed / high energy barrier)
    assert classify_rotamer_outlier(120.0, "LEU") is True
    assert classify_rotamer_outlier(0.0, "PHE") is True


def test_phenix_oracle_ideal_structure_passes():
    """Verify that an unconstrained, well-spaced macromolecular structure passes with EXCELLENT tier."""
    oracle = PhenixMolProbityOracle(
        max_clashscore_tolerance=30.0,
        max_rama_outliers_tolerance_pct=5.0,
        max_molprobity_score_tolerance=3.5
    )

    # Build well-spaced atoms (interatomic distance >= 3.8 Angstroms, well above van der Waals sum ~ 3.4 A)
    atoms = [
        AtomCoordinate("N", "N", 0.0, 0.0, 0.0, 1, "ALA"),
        AtomCoordinate("CA", "C", 1.45, 0.0, 0.0, 1, "ALA"),
        AtomCoordinate("C", "C", 2.0, 1.4, 0.0, 1, "ALA"),
        AtomCoordinate("O", "O", 1.4, 2.4, 0.0, 1, "ALA"),
        # Residue 2 placed far away
        AtomCoordinate("N", "N", 5.0, 0.0, 0.0, 2, "VAL"),
        AtomCoordinate("CA", "C", 6.45, 0.0, 0.0, 2, "VAL"),
        AtomCoordinate("C", "C", 7.0, 1.4, 0.0, 2, "VAL"),
        AtomCoordinate("O", "O", 6.4, 2.4, 0.0, 2, "VAL"),
    ]

    angles = [
        ResidueBackboneAngles(1, "ALA", phi_deg=-60.0, psi_deg=-45.0, chi1_deg=60.0),
        ResidueBackboneAngles(2, "VAL", phi_deg=-120.0, psi_deg=130.0, chi1_deg=180.0),
    ]

    report = oracle.audit_structure_geometry(
        structure_id="IDEAL_PDB_MOCK_01",
        atoms=atoms,
        backbone_angles=angles
    )

    assert report.is_crystallographically_sound is True
    assert report.num_clashes == 0
    assert report.clashscore == 0.0
    assert report.rama_outliers_pct == 0.0
    assert report.quality_tier == StructuralQualityTier.EXCELLENT
    assert report.molprobity_score <= 1.8


def test_phenix_oracle_severe_steric_clash_rejection():
    """Verify that severe non-bonded atomic overlap (overlap >= 0.40 A) is caught and causes rejection."""
    oracle = PhenixMolProbityOracle(
        max_clashscore_tolerance=15.0,  # Strict threshold to trigger clash rejection
        max_rama_outliers_tolerance_pct=5.0,
        max_molprobity_score_tolerance=2.5
    )

    # Intentionally place two carbon atoms from different residues at distance d = 1.8 A
    # vdW sum = 1.7 + 1.7 = 3.4 A -> Overlap = 3.4 - 1.8 = 1.6 A >> 0.40 A
    atoms = [
        AtomCoordinate("CA", "C", 0.0, 0.0, 0.0, 1, "ALA"),
        AtomCoordinate("CB", "C", 0.0, 0.0, 1.8, 10, "LEU"),  # Distant residue seq 10, colliding
    ]

    report = oracle.audit_structure_geometry(
        structure_id="CLASHING_TARGET_01",
        atoms=atoms,
        backbone_angles=[]
    )

    assert report.num_clashes == 1
    assert report.clashscore == 500.0  # 1 clash / 2 atoms * 1000 = 500
    assert report.is_crystallographically_sound is False
    assert report.quality_tier == StructuralQualityTier.REJECTED_SEVERE_CLASHES
    assert "Clashscore" in str(report.rejection_reason)
    assert len(report.clash_details) == 1
    assert report.clash_details[0].overlap_angstrom >= 1.5


def test_phenix_oracle_ramachandran_outlier_rejection():
    """Verify that high percentage of Ramachandran outliers triggers stereochemical rejection."""
    oracle = PhenixMolProbityOracle(
        max_clashscore_tolerance=50.0,
        max_rama_outliers_tolerance_pct=5.0,  # 5% max tolerance
        max_molprobity_score_tolerance=3.5
    )

    atoms = [AtomCoordinate("CA", "C", 0.0, 0.0, float(i * 4.0), i, "ALA") for i in range(10)]
    
    # 3 out of 10 residues with impossible Ramachandran angles -> 30% outliers > 5%
    angles = [
        ResidueBackboneAngles(1, "ALA", phi_deg=60.0, psi_deg=-120.0),  # Outlier
        ResidueBackboneAngles(2, "ALA", phi_deg=65.0, psi_deg=-115.0),  # Outlier
        ResidueBackboneAngles(3, "ALA", phi_deg=70.0, psi_deg=-110.0),  # Outlier
    ] + [
        ResidueBackboneAngles(i, "ALA", phi_deg=-60.0, psi_deg=-45.0) for i in range(4, 11)  # Favored
    ]

    report = oracle.audit_structure_geometry(
        structure_id="RAMA_OUTLIERS_01",
        atoms=atoms,
        backbone_angles=angles
    )

    assert report.num_rama_outliers == 3
    assert report.rama_outliers_pct == 30.0
    assert report.is_crystallographically_sound is False
    assert "Ramachandran outliers" in str(report.rejection_reason)


def test_court_arbitration_phenix_molprobity():
    """Verify PhysicalCoherenceCourt arbitrates MACROMOLECULAR_GEOMETRIC_VALIDITY invariant."""
    court = PhysicalCoherenceCourt()
    oracle = PhenixMolProbityOracle()

    # 1. Arbitrate Sound Structure Report
    sound_report = MolProbityReport(
        structure_id="TROPONIN_C_CRYSTAL",
        total_atoms=1200,
        num_clashes=4,
        clashscore=3.33,
        clash_details=[],
        total_residues_evaluated=160,
        num_rama_favored=156,
        num_rama_allowed=4,
        num_rama_outliers=0,
        rama_favored_pct=97.5,
        rama_allowed_pct=2.5,
        rama_outliers_pct=0.0,
        num_rotamer_outliers=2,
        rotamer_outliers_pct=1.25,
        molprobity_score=1.42,
        quality_tier=StructuralQualityTier.EXCELLENT,
        is_crystallographically_sound=True
    )

    res_sound = court.audit_phenix_molprobity_report("CLAIM_STRUCT_SOUND", sound_report.to_dict())
    assert res_sound.verdict == CourtVerdict.VERIFIED_COHERENT
    assert res_sound.conservation_audit[0]["law"] == "MACROMOLECULAR_GEOMETRIC_VALIDITY"
    assert res_sound.conservation_audit[0]["satisfied"] is True

    # 2. Arbitrate Unsound Structure Report
    unsound_report = MolProbityReport(
        structure_id="DEFORMED_MODEL_01",
        total_atoms=500,
        num_clashes=45,
        clashscore=90.0,
        clash_details=[],
        total_residues_evaluated=80,
        num_rama_favored=40,
        num_rama_allowed=20,
        num_rama_outliers=20,
        rama_favored_pct=50.0,
        rama_allowed_pct=25.0,
        rama_outliers_pct=25.0,
        num_rotamer_outliers=15,
        rotamer_outliers_pct=18.75,
        molprobity_score=4.12,
        quality_tier=StructuralQualityTier.REJECTED_SEVERE_CLASHES,
        is_crystallographically_sound=False,
        rejection_reason="Clashscore 90.0 exceeds threshold 30.0."
    )

    res_unsound = court.audit_phenix_molprobity_report("CLAIM_STRUCT_UNSOUND", unsound_report.to_dict())
    assert res_unsound.verdict == CourtVerdict.REJECTED_CONSERVATION_VIOLATION
    assert res_unsound.conservation_audit[0]["satisfied"] is False
    assert "Clashscore 90.0" in str(res_unsound.duhem_quine_autopsy)


def test_preclinical_gate_2_integration_with_molprobity():
    """Verify that PreClinicalGatesValidator enforces MolProbity geometric criteria in Gate 2."""
    validator = PreClinicalGatesValidator()

    # Evidence payload with sound MolProbity geometry
    sound_payload = {
        "genetic_evidence": {
            "causality_score": 0.88,
            "sidecar_id": "SIDECAR_GEN_001"
        },
        "structural_evidence": {
            "mean_plddt": 85.0,
            "pocket_druggability_score": 0.82,
            "clashscore": 8.5,
            "rama_outliers_pct": 0.5,
            "molprobity_score": 1.65,
            "sidecar_id": "SIDECAR_STRUCT_001"
        },
        "biophysical_mechanism": {
            "theta_target_stimulated": 0.75,
            "theta_target_basal": 0.05,
            "sidecar_id": "SIDECAR_BIO_001",
        },
        "safety_evidence": {
            "homolog_selectivity_ratio": 250.0,
            "acute_toxic_alerts_count": 0,
            "sidecar_id": "SIDECAR_SAFE_001",
        }
    }

    passport = validator.evaluate_candidate(
        candidate_id="CAND_TROPONIN_C_MOLPROBITY_SOUND",
        target_name="Cardiac Troponin C",
        indication="Cardiomyopathy",
        evidence_payload=sound_payload
    )

    assert passport.all_gates_passed is True
    assert passport.passport_verdict == PassportVerdict.CERTIFIED_PRECLINICAL_READY
    assert passport.gate_evaluations[PreClinicalGateType.STRUCTURAL_DRUGGABILITY_GATE.value].passed is True
    assert "MolProbity: 1.65" in passport.gate_evaluations[PreClinicalGateType.STRUCTURAL_DRUGGABILITY_GATE.value].evidence_summary

    # Evidence payload with severe steric clash violation (clashscore 42.0 > 30.0)
    clashing_payload = dict(sound_payload)
    clashing_payload["structural_evidence"] = {
        "mean_plddt": 85.0,
        "pocket_druggability_score": 0.82,
        "clashscore": 42.0,  # Exceeds max_clashscore=30.0
        "rama_outliers_pct": 0.5,
        "molprobity_score": 3.85,
    }

    passport_fail = validator.evaluate_candidate(
        candidate_id="CAND_TROPONIN_C_CLASHING",
        target_name="Cardiac Troponin C",
        indication="Cardiomyopathy",
        evidence_payload=clashing_payload
    )

    assert passport_fail.all_gates_passed is False
    assert passport_fail.passport_verdict == PassportVerdict.REJECTED_GATE_FAILURE
    gate2 = passport_fail.gate_evaluations[PreClinicalGateType.STRUCTURAL_DRUGGABILITY_GATE.value]
    assert gate2.passed is False
    assert "GEOMETRY VIOLATIONS" in gate2.evidence_summary
    assert "clashscore 42.0" in gate2.evidence_summary
