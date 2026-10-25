"""
tests/test_cartan_dec_and_evidence_portal.py - Unit Test Suite for Cartan-DEC Proteomics & Evidence Portal (ADR-DISCOVERY-077)
"""

from __future__ import annotations
import json
import math
import numpy as np
import pytest
from typing import Dict, Any, List

from python.discovery.cartan_dec_proteomics_auditor import (
    ResidueFrame,
    ConnectionOneForm,
    CurvatureTwoForm,
    HolonomyDefectReport,
    CartanDECStructureReport,
    CartanDECProteomicsAuditor,
)
from python.discovery.coe_integrity_auditor import (
    IntegrityDimension,
    EmpiricalRebuttalVerdict,
    IntegrityAuditResult,
    EmpiricalRebuttalDossier,
    FullCoEIntegrityReport,
    CoEIntegrityAuditor,
)
from python.discovery.evidence_portal import (
    DiscoveryPaperEntry,
    EvidencePortalGenerator,
)
from python.discovery.physical_theorem_court import (
    PhysicalCoherenceCourt,
    PhysicalConservationType,
    CourtVerdict,
)
from python.discovery.structure_property_purpose_engine import (
    StructurePropertyPurposeEngine,
    StructurePropertyPurposeSpec,
    IonicSelectivityProfile,
    TeleonomicPurposeClass,
)


def _generate_synthetic_protein_backbone(num_residues: int = 8, hinge_index: int = 3) -> List[Dict[str, Any]]:
    """Generate synthetic realistic peptide coordinates with a deliberate twist hinge."""
    residues: List[Dict[str, Any]] = []
    # Alpha-helix like pitch: radius 2.3 Angstrom, pitch 1.5 Angstrom per residue
    for i in range(num_residues):
        theta = i * (2.0 * math.pi / 3.6)
        # Induce conformational twist kink at hinge_index
        twist_kink = 0.8 if i >= hinge_index else 0.0

        ca = np.array([2.3 * math.cos(theta + twist_kink), 2.3 * math.sin(theta + twist_kink), i * 1.5], dtype=np.float64)
        # N is slightly behind, C is slightly ahead
        n_atom = ca + np.array([-0.8 * math.sin(theta), 0.8 * math.cos(theta), -0.6], dtype=np.float64)
        c_atom = ca + np.array([0.8 * math.sin(theta), -0.8 * math.cos(theta), 0.6], dtype=np.float64)

        residues.append({
            "name": f"GLY_{i+1}" if i != hinge_index else f"ASP_{i+1}_HINGE",
            "CA": ca.tolist(),
            "N": n_atom.tolist(),
            "C": c_atom.tolist(),
        })
    return residues


def test_cartan_moving_frames_construction_and_so3_orthonormality():
    """Verify that Cartan moving frames E_i are strictly orthonormal and SO(3) compliant."""
    residues = _generate_synthetic_protein_backbone(num_residues=6)
    auditor = CartanDECProteomicsAuditor(contact_cutoff_angstrom=8.0)
    frames = auditor.build_frames_from_backbone(residues)

    assert len(frames) == 6
    for idx, f in enumerate(frames):
        assert f.is_valid_so3 is True
        assert math.isclose(f.det_e, 1.0, abs_tol=1e-3)
        E = np.array(f.e_matrix, dtype=np.float64)
        assert np.allclose(E.T @ E, np.eye(3), atol=1e-3)


def test_discrete_connection_one_forms_and_rodrigues_logarithm():
    """Verify discrete connection 1-forms omega_ij in so(3) on contact edges."""
    residues = _generate_synthetic_protein_backbone(num_residues=6)
    auditor = CartanDECProteomicsAuditor(contact_cutoff_angstrom=8.0)
    frames = auditor.build_frames_from_backbone(residues)
    connections = auditor.compute_connection_one_forms(frames)

    assert len(connections) > 0
    for (i, j), conn in connections.items():
        assert conn.distance_angstrom < 8.0
        assert conn.twist_angle_rad >= 0.0
        # Antisymmetry: omega_ji = -omega_ij
        conn_opposite = connections[(j, i)]
        w_ij = np.array(conn.omega_vector, dtype=np.float64)
        w_ji = np.array(conn_opposite.omega_vector, dtype=np.float64)
        assert np.allclose(w_ij, -w_ji, atol=1e-5)


def test_curvature_two_forms_and_lie_bracket():
    """Verify discrete curvature 2-forms Omega_f and Lie bracket commutators on contact triangles."""
    residues = _generate_synthetic_protein_backbone(num_residues=8)
    auditor = CartanDECProteomicsAuditor(contact_cutoff_angstrom=8.0)
    frames = auditor.build_frames_from_backbone(residues)
    connections = auditor.compute_connection_one_forms(frames)
    curvatures = auditor.compute_curvature_two_forms(frames, connections)

    assert len(curvatures) > 0
    for c in curvatures:
        assert len(c.triangle) == 3
        assert len(c.omega_vector) == 3
        # Commutator norm should be non-negative
        assert c.comm_norm >= 0.0


def test_path_ordered_holonomy_defect_identifies_hinge():
    """Verify that holonomy defect energy D_i isolates the conformational hinge."""
    residues = _generate_synthetic_protein_backbone(num_residues=8, hinge_index=3)
    auditor = CartanDECProteomicsAuditor(contact_cutoff_angstrom=8.0, hinge_threshold_percentile=75.0)
    report = auditor.audit_protein_structure(residues, structure_id="TROPONIN_C_EF_HAND")

    assert report.num_residues == 8
    assert report.num_contact_edges > 0
    assert report.num_contact_triangles > 0
    assert report.reconstruction_gauge_coherence > 0.40

    # Residue 3 was assigned the twist kink; check that it has non-zero defect energy
    defect_hinge = report.holonomy_defects[3]
    assert defect_hinge.participating_cycles_count > 0
    assert defect_hinge.holonomy_defect_energy > 1.0

    # Arbitrate report through PhysicalCoherenceCourt
    court = PhysicalCoherenceCourt()
    audit_res = court.audit_cartan_dec_report("CLAIM_CARTAN_DEC_01", report.to_dict())
    assert audit_res.verdict == CourtVerdict.VERIFIED_COHERENT
    assert audit_res.conservation_audit[0]["law"] == "CARTAN_DEC_HOLONOMY_COHERENCE"
    assert audit_res.conservation_audit[0]["satisfied"] is True


def test_coe_integrity_auditor_four_dimensions():
    """Verify the 4 dimensions of the CoE Integrity Audit."""
    auditor = CoEIntegrityAuditor(numeric_tolerance=1e-4)

    # 1. Score verification (exact match)
    claimed_scores = {"accuracy": 87.50, "f1_score": 0.824}
    reproduced_scores = {"accuracy": 87.50, "f1_score": 0.824}
    r_scores = auditor.verify_scores(claimed_scores, reproduced_scores)
    assert r_scores.passed is True
    assert r_scores.score == 1.0

    # 2. Score verification with violation
    bad_reproduced = {"accuracy": 82.00, "f1_score": 0.824}
    r_bad_scores = auditor.verify_scores(claimed_scores, bad_reproduced)
    assert r_bad_scores.passed is False
    assert r_bad_scores.violations_count == 1

    # 3. Specification compliance
    constraints = {"energy": (0.0, 1000.0), "probability": (0.0, 1.0)}
    observed = {"energy": 450.2, "probability": 0.95}
    r_spec = auditor.verify_specification_compliance(constraints, observed)
    assert r_spec.passed is True

    # 4. Reference verification (valid vs hallucinated)
    citations = [
        {"title": "Cartan Moving Frames and DEC", "doi": "10.1000/182", "year": "2025"},
        {"title": "OpenFOAM Continuum Mechanics", "pmid": "34901678", "year": "2021"}
    ]
    r_refs = auditor.verify_references(citations)
    assert r_refs.passed is True

    bad_citations = [
        {"title": "Generic Uncited Claim", "doi": "generic_placeholder", "year": "2025"}
    ]
    r_bad_refs = auditor.verify_references(bad_citations)
    assert r_bad_refs.passed is False

    # 5. Method-code alignment
    claimed_terms = ["CartanDECProteomicsAuditor", "HolonomyDefectReport"]
    code_symbols = {"CartanDECProteomicsAuditor", "HolonomyDefectReport", "ResidueFrame"}
    r_align = auditor.verify_method_code_alignment(claimed_terms, code_symbols)
    assert r_align.passed is True

    # Full Master Audit
    full_report = auditor.audit_full_integrity(
        target_id="PAPER_CARTAN_DEC_MIAE",
        claimed_scores=claimed_scores,
        reproduced_scores=reproduced_scores,
        constraints=constraints,
        observed_metrics=observed,
        citations=citations,
        claimed_method_terms=claimed_terms,
        available_code_symbols=code_symbols
    )
    assert full_report.all_dimensions_passed is True
    assert full_report.verdict == "PASSED_PUBLICATION_BAR"

    # Arbitrate in Court
    court = PhysicalCoherenceCourt()
    court_res = court.audit_coe_integrity_report("CLAIM_COE_INTEGRITY_01", full_report.to_dict())
    assert court_res.verdict == CourtVerdict.VERIFIED_COHERENT
    assert court_res.conservation_audit[0]["law"] == "COE_INTEGRITY_AUDIT"


def test_active_empirical_rebuttal_execution():
    """Verify active empirical rebuttal dispatching an actual calculation to answer an objection."""
    integrity_auditor = CoEIntegrityAuditor()
    spp_engine = StructurePropertyPurposeEngine()

    spec = StructurePropertyPurposeSpec(
        mechanism_id="TROPONIN_C_SITE_II",
        biological_system="Cardiac Troponin C",
        target_site="Site II regulatory EF-hand",
        purpose_class=TeleonomicPurposeClass.SENSING,
        coordination_geometry="OCTAHEDRAL",
        coordinating_residues=["Asp65", "Asp67", "Ser69", "Glu76"],
        allosteric_coupling_factor=1.0,
        tolerated_basal_leak=0.15,
        required_stimulated_occupancy=0.60
    )
    profile = IonicSelectivityProfile(
        target_ion="CA2",
        competing_ion="MG2",
        kd_target_molar=5.0e-6,
        kd_competing_molar=5.0e-3,
        target_conc_basal_molar=100.0e-9,
        target_conc_stimulated_molar=10.0e-6,
        competing_conc_molar=1.0e-3
    )

    # Reviewer critique
    critique = "Claimed Troponin C Site II Ca2+ sensing fails in the presence of 10,000-fold excess physiological Mg2+."

    dossier = integrity_auditor.execute_active_empirical_rebuttal(
        objection_id="REV_OBJ_TROPONIN_01",
        reviewer_critique=critique,
        experiment_name="Competitive Ionic Titration Audit",
        experiment_fn=spp_engine.audit_competitive_ionic_selectivity,
        assertion_fn=lambda rep: (rep.is_purpose_fulfilled and rep.theta_target_stimulated >= 0.60,
                                  f"theta_stim={rep.theta_target_stimulated:.3f} >= 0.60, selectivity={rep.selectivity_ratio_s:.1f}"),
        spec=spec,
        selectivity=profile
    )

    assert dossier.rebuttal_verdict == EmpiricalRebuttalVerdict.EMPIRICALLY_VERIFIED
    assert "theta_stim=" in dossier.justification
    assert dossier.telemetry_output["is_purpose_fulfilled"] is True


def test_evidence_portal_generation_and_deep_linking(tmp_path):
    """Verify Evidence Portal asset generation and content integrity."""
    generator = EvidencePortalGenerator(output_dir=str(tmp_path))
    res = generator.generate_portal_assets()

    assert res["num_discoveries"] >= 5

    # Check JSON
    with open(res["json_path"], "r", encoding="utf-8") as f:
        data = json.load(f)
    assert len(data) >= 5
    ids = [d["id"] for d in data]
    assert "cartan_dec_miae" in ids
    assert "openfoam_bkm" in ids
    assert "spp_teleonomy" in ids

    # Check HTML
    with open(res["html_path"], "r", encoding="utf-8") as f:
        html = f.read()
    assert "CoResearcher Evidence & Discovery Hub" in html
    assert "sidecar://biomolecular-structure-viewer" in html
    assert "CoE Integrity Audit & Active Empirical Rebuttal" in html
    assert "applyHash" in html
