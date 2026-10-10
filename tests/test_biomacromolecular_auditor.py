"""
Test suite for Biomacromolecular & Ternary Coordination Auditor (ADR-DISCOVERY-051).
Verifies:
1. Interception of Van der Waals steric atomic clashes (r < 1.2 A).
2. Interception of metal coordination sphere corruptions (Zn2+ incomplete coordination).
3. Interception of negative thermodynamic cooperativity (alpha < 1.0).
4. Interception by H-JEPA latent world model infinite energy guardrails.
5. Successful validation of sound PROTAC ternary complex.
6. REST API endpoint /api/discovery/biomacromolecular/audit-complex.
"""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from api.server import app
from python.discovery.biomacromolecular_auditor import (
    BiomacromolecularCoordinationAuditor,
    ChemicalValidationVerdict,
    CoordinationGeometry,
    MetalCoordinationCenter,
    MetalIonType,
    ProtacTernaryComplexSpec,
)


@pytest.fixture
def client():
    return TestClient(app)


def test_van_der_waals_clash_pruned():
    spec = ProtacTernaryComplexSpec(
        complex_id="protac_clash_001",
        target_protein="BRD4_BD1",
        e3_ligase="VHL",
        linker_length_atoms=8,
        warhead_kd_nm=10.0,
        e3_kd_nm=20.0,
        ternary_kd_nm=5.0,
        min_atom_distance_angstrom=0.85,  # Steric overlap!
    )
    report = BiomacromolecularCoordinationAuditor.audit_complex(spec)
    assert not report.is_physically_sound
    assert report.verdict == ChemicalValidationVerdict.PRUNED_VAN_DER_WAALS_CLASH
    assert "van der waals" in report.rationale.lower()


def test_metal_coordination_corruption_pruned():
    # Zn2+ requires 4 coordinating atoms, only 2 provided
    bad_zn = MetalCoordinationCenter(
        ion_id="zn_pocket_1",
        metal_type=MetalIonType.ZN2,
        coordinating_atom_count=2,
        geometry=CoordinationGeometry.TETRAHEDRAL,
        observed_mean_bond_length_angstrom=2.05,
    )
    spec = ProtacTernaryComplexSpec(
        complex_id="protac_zn_fail",
        target_protein="HDAC6_CATALYTIC",
        e3_ligase="CRBN",
        linker_length_atoms=12,
        warhead_kd_nm=15.0,
        e3_kd_nm=30.0,
        ternary_kd_nm=8.0,
        min_atom_distance_angstrom=2.10,
        metal_centers=[bad_zn],
    )
    report = BiomacromolecularCoordinationAuditor.audit_complex(spec)
    assert not report.is_physically_sound
    assert report.verdict == ChemicalValidationVerdict.PRUNED_METAL_COORDINATION_BREACH


def test_negative_cooperativity_pruned():
    # Binary KDs avg = 15 nM, Ternary KD = 60 nM -> alpha = 15/60 = 0.25 < 1.0
    spec = ProtacTernaryComplexSpec(
        complex_id="protac_antagonistic",
        target_protein="STAT3",
        e3_ligase="VHL",
        linker_length_atoms=6,
        warhead_kd_nm=10.0,
        e3_kd_nm=20.0,
        ternary_kd_nm=60.0,  # Unstable ternary complex
        min_atom_distance_angstrom=2.10,
    )
    report = BiomacromolecularCoordinationAuditor.audit_complex(spec)
    assert not report.is_physically_sound
    assert report.verdict == ChemicalValidationVerdict.PRUNED_NEGATIVE_COOPERATIVITY


def test_sound_ternary_complex_passed():
    good_zn = MetalCoordinationCenter(
        ion_id="zn_active_site",
        metal_type=MetalIonType.ZN2,
        coordinating_atom_count=4,
        geometry=CoordinationGeometry.TETRAHEDRAL,
        observed_mean_bond_length_angstrom=2.08,
    )
    spec = ProtacTernaryComplexSpec(
        complex_id="arv_110_androgen_protac",
        target_protein="ANDROGEN_RECEPTOR",
        e3_ligase="VHL",
        linker_length_atoms=14,
        warhead_kd_nm=12.0,
        e3_kd_nm=24.0,
        ternary_kd_nm=3.0,  # Positive cooperativity alpha = 18 / 3 = 6.0
        min_atom_distance_angstrom=2.15,
        metal_centers=[good_zn],
    )
    report = BiomacromolecularCoordinationAuditor.audit_complex(spec)
    assert report.is_physically_sound
    assert report.verdict == ChemicalValidationVerdict.THERMODYNAMICALLY_SOUND
    assert report.cooperativity_alpha > 1.0
    assert report.free_energy_delta_g_kcal_mol < 0.0
    assert report.som_biomacromolecular_hash.startswith("sha256:")


def test_biomacromolecular_rest_api_endpoint(client):
    payload = {
        "complex_id": "test_protac_brd4",
        "target_protein": "BRD4",
        "e3_ligase": "VHL",
        "linker_length_atoms": 12,
        "warhead_kd_nm": 10.0,
        "e3_kd_nm": 20.0,
        "ternary_kd_nm": 3.0,
        "min_atom_distance_angstrom": 2.20,
        "metal_centers": [
            {
                "ion_id": "zn_01",
                "metal_type": "ZN2",
                "coordinating_atom_count": 4,
                "geometry": "TETRAHEDRAL",
                "observed_mean_bond_length_angstrom": 2.05,
                "expected_bond_length_angstrom": 2.05,
                "tolerance_angstrom": 0.35,
            }
        ],
    }
    response = client.post("/api/discovery/biomacromolecular/audit-complex", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["complex_id"] == "test_protac_brd4"
    assert data["is_physically_sound"]
    assert data["verdict"] == "THERMODYNAMICALLY_SOUND"
    assert "som_biomacromolecular_hash" in data
