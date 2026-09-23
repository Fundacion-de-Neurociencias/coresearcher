"""
scripts/run_membrane_dynamics_suite.py - Verification Suite for Biophysical Membrane Dynamics & Duhem-Quine Auditor (ADR-DISCOVERY-026)
Tests:
1. Biophysical contract creation and SOM cryptographic hashing for BAX and Abeta42 pore systems.
2. Formal Duhem-Quine failure diagnosis on the user's scenario (POPE bilayer area per lipid below experimental value).
3. Hard-core conformational refutation vs auxiliary parameter defect isolation.
4. Physical invariant auditing (symplectic energy drift, bilayer incompressibility, thermodynamic entropy).
5. FastAPI REST API endpoints via TestClient.
"""

import sys
import os
from pathlib import Path

# Ensure repo root is on sys.path
REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

from python.discovery.membrane_dynamics_auditor import (
    MembraneLipidSpecies,
    ForceFieldArchetype,
    PressureCouplingScheme,
    TargetMembraneSystem,
    BiophysicalBlameTarget,
    BiophysicalContractBuilder,
    BiophysicalDuhemQuineAuditor,
    MembraneInvariantVerifier,
    MembraneSimulationObservables,
)
from python.discovery.failure_engine import DuhemQuineBlameType
from fastapi.testclient import TestClient
from api.server import app


def test_contract_construction():
    print("\n--- 1. Testing Biophysical Membrane Contract Construction ---")

    # Contract 1: BAX pro-apoptotic pore
    bax_contract = BiophysicalContractBuilder.create_bax_membrane_contract()
    assert bax_contract.target_system == TargetMembraneSystem.BAX_PORE
    assert len(bax_contract.lipid_composition) == 3
    assert bax_contract.experimental_constraints.expected_area_per_lipid_nm2 == 0.590
    assert bax_contract.som_contract_hash.startswith("sha256:")
    print(f"  [PASS] BAX Contract created: {bax_contract.contract_id} (SOM: {bax_contract.som_contract_hash[:18]}...)")

    # Contract 2: Amyloid-Beta oligomer cationic nanopore
    abeta_contract = BiophysicalContractBuilder.create_amyloid_pore_contract()
    assert abeta_contract.target_system == TargetMembraneSystem.AMYLOID_BETA_PORE
    assert any(l.species == MembraneLipidSpecies.CHOLESTEROL for l in abeta_contract.lipid_composition)
    assert abeta_contract.experimental_constraints.expected_area_per_lipid_nm2 == 0.540
    print(f"  [PASS] Amyloid-Beta Contract created: {abeta_contract.contract_id}")


def test_duhem_quine_simulation_diagnosis():
    print("\n--- 2. Testing Duhem-Quine Diagnosis (Author's POPE Bilayer Scenario) ---")

    # Scenario A: User's POPE Bilayer scenario:
    # Bilayer equilibrates to area per lipid below experimental value (observed 0.525 vs expected 0.590 nm^2).
    # Auxiliary params: Low hydration (24 waters/lipid) and isotropic/Berendsen pressure coupling.
    contract_a = BiophysicalContractBuilder.create_bax_membrane_contract(
        pressure_coupling=PressureCouplingScheme.BERENDSEN_WEAK,
        waters_per_lipid=24.0,
        equilibration_length_ns=100.0
    )
    obs_a = MembraneSimulationObservables(
        observed_area_per_lipid_nm2=0.525,  # 0.065 nm^2 below expected 0.590 nm^2 (breaches 0.025 tolerance)
        observed_bilayer_thickness_nm=4.15, # compressed laterally, thickened vertically
        observed_order_parameter_scd=0.24,
        observed_pore_radius_nm=0.0,
        energy_drift_ratio=1.2e-5,
        entropy_production_rate=0.003,
        equilibration_converged=True,
        runtime_ns_completed=200.0
    )

    diag_a = BiophysicalDuhemQuineAuditor.diagnose_simulation_anomaly(contract_a, obs_a)
    print(f"  [PASS] Scenario A Blame: {diag_a.blame_classification.value}")
    print(f"         Primary Target: {diag_a.primary_blame_target.value}")
    print(f"         Directive: {diag_a.next_action_directive}")
    print(f"         Remedy: {diag_a.remediation_protocol[:80]}...")

    assert diag_a.blame_classification == DuhemQuineBlameType.AUXILIARY_ASSUMPTION_DEFECTIVE
    assert diag_a.primary_blame_target in [
        BiophysicalBlameTarget.BAROSTAT_SURFACE_TENSION_MISCOUPLING,
        BiophysicalBlameTarget.OSMOTIC_DEHYDRATION
    ]
    assert "CALIBRATE_SIMULATION_PARAMETERS" in diag_a.next_action_directive
    assert diag_a.som_diagnosis_hash.startswith("sha256:")

    # Scenario B: Premature Equilibration Truncation
    contract_b = BiophysicalContractBuilder.create_bax_membrane_contract(
        equilibration_length_ns=20.0
    )
    obs_b = MembraneSimulationObservables(
        observed_area_per_lipid_nm2=0.530,
        observed_bilayer_thickness_nm=4.10,
        observed_order_parameter_scd=0.22,
        runtime_ns_completed=25.0,
        equilibration_converged=False
    )
    diag_b = BiophysicalDuhemQuineAuditor.diagnose_simulation_anomaly(contract_b, obs_b)
    print(f"  [PASS] Scenario B Blame: {diag_b.primary_blame_target.value}")
    assert diag_b.primary_blame_target == BiophysicalBlameTarget.EQUILIBRATION_TRUNCATION
    assert diag_b.blame_classification == DuhemQuineBlameType.AUXILIARY_ASSUMPTION_DEFECTIVE

    # Scenario C: Hard Core Conformational Refutation
    # All auxiliary parameters are optimal (CHARMM36m, Semi-isotropic Parrinello-Rahman, 45 waters, 300ns),
    # but area per lipid collapses radically (0.46 nm^2, > 3x tolerance) with catastrophic energy drift.
    contract_c = BiophysicalContractBuilder.create_bax_membrane_contract(
        force_field=ForceFieldArchetype.CHARMM36M,
        pressure_coupling=PressureCouplingScheme.SEMI_ISOTROPIC_PARRINELLO_RAHMAN,
        waters_per_lipid=45.0
    )
    obs_c = MembraneSimulationObservables(
        observed_area_per_lipid_nm2=0.460,
        observed_bilayer_thickness_nm=4.80,
        observed_order_parameter_scd=0.32,
        energy_drift_ratio=2.5e-3, # severe Hamiltonian drift
        runtime_ns_completed=300.0,
        equilibration_converged=True
    )
    diag_c = BiophysicalDuhemQuineAuditor.diagnose_simulation_anomaly(contract_c, obs_c)
    print(f"  [PASS] Scenario C Blame: {diag_c.blame_classification.value} | Target: {diag_c.primary_blame_target.value}")
    assert diag_c.blame_classification == DuhemQuineBlameType.CORE_HYPOTHESIS_FATAL
    assert diag_c.primary_blame_target == BiophysicalBlameTarget.HARD_CORE_CONFORMATION_REFUTED
    assert "FORK_CONFORMATION_IN_GRAVEYARD" in diag_c.next_action_directive


def test_membrane_invariants_verification():
    print("\n--- 3. Testing Membrane Invariants Verification (ScienceIDE Standards) ---")

    contract = BiophysicalContractBuilder.create_bax_membrane_contract()

    # Case 1: Healthy converged simulation
    healthy_obs = MembraneSimulationObservables(
        observed_area_per_lipid_nm2=0.592, # within [0.565, 0.615]
        observed_bilayer_thickness_nm=3.86,
        observed_order_parameter_scd=0.19,
        energy_drift_ratio=2.0e-5,
        entropy_production_rate=0.001
    )
    rep_healthy = MembraneInvariantVerifier.verify_invariants(contract, healthy_obs)
    print(f"  [PASS] Healthy Invariant Soundness: {rep_healthy.is_physically_sound}")
    assert rep_healthy.is_physically_sound is True
    assert rep_healthy.energy_drift_passed is True
    assert rep_healthy.incompressibility_passed is True
    assert rep_healthy.thermodynamic_entropy_passed is True

    # Case 2: Integrator instability (energy drift breach)
    unstable_obs = MembraneSimulationObservables(
        observed_area_per_lipid_nm2=0.590,
        observed_bilayer_thickness_nm=3.85,
        observed_order_parameter_scd=0.18,
        energy_drift_ratio=5.0e-4, # breaches 1e-4 tol
        entropy_production_rate=0.001
    )
    rep_unstable = MembraneInvariantVerifier.verify_invariants(contract, unstable_obs)
    print(f"  [PASS] Unstable Invariant Soundness: {rep_unstable.is_physically_sound}")
    assert rep_unstable.is_physically_sound is False
    assert rep_unstable.energy_drift_passed is False
    assert any("Hamiltonian energy drift breached" in d for d in rep_unstable.diagnostics)


def test_rest_api_endpoints():
    print("\n--- 4. Testing Biophysical Membrane REST API Endpoints ---")
    client = TestClient(app)

    # 1. Create Simulation Contract
    r1 = client.post("/api/discovery/membrane/create-simulation-contract", json={
        "system_type": "BAX_PORE",
        "force_field": "CHARMM36M",
        "pressure_coupling": "SEMI_ISOTROPIC_PARRINELLO_RAHMAN",
        "waters_per_lipid": 40.0
    })
    assert r1.status_code == 200
    d1 = r1.json()
    assert d1["target_system"] == "BAX_PORE"
    assert "som_contract_hash" in d1
    print(f"  [PASS] POST /api/discovery/membrane/create-simulation-contract: {d1['contract_id']}")

    # 2. Audit Duhem-Quine
    r2 = client.post("/api/discovery/membrane/audit-duhem-quine", json={
        "system_type": "BAX_PORE",
        "pressure_coupling": "BERENDSEN_WEAK",
        "waters_per_lipid": 22.0,
        "observed_area_per_lipid_nm2": 0.520,
        "observed_bilayer_thickness_nm": 4.15,
        "observed_order_parameter_scd": 0.23
    })
    assert r2.status_code == 200
    d2 = r2.json()
    assert d2["blame_classification"] == "AUXILIARY_ASSUMPTION_DEFECTIVE"
    assert "remediation_protocol" in d2
    print(f"  [PASS] POST /api/discovery/membrane/audit-duhem-quine: {d2['primary_blame_target']}")

    # 3. Verify Physical Invariants
    r3 = client.post("/api/discovery/membrane/verify-physical-invariants", json={
        "system_type": "BAX_PORE",
        "observed_area_per_lipid_nm2": 0.588,
        "observed_bilayer_thickness_nm": 3.87,
        "observed_order_parameter_scd": 0.19,
        "energy_drift_ratio": 1.5e-5
    })
    assert r3.status_code == 200
    d3 = r3.json()
    assert d3["is_physically_sound"] is True
    print("  [PASS] POST /api/discovery/membrane/verify-physical-invariants: Invariants verified")


def main():
    print("================================================================================")
    print("Running Biophysical Membrane Dynamics & Duhem-Quine Suite (ADR-DISCOVERY-026)")
    print("================================================================================")
    test_contract_construction()
    test_duhem_quine_simulation_diagnosis()
    test_membrane_invariants_verification()
    test_rest_api_endpoints()
    print("\n================================================================================")
    print("ALL BIOPHYSICAL MEMBRANE GATES PASSED EMPIRICALLY (100% OPERATIONAL)")
    print("================================================================================")


if __name__ == "__main__":
    main()
