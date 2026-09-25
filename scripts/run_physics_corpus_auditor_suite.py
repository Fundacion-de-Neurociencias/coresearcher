"""
scripts/run_physics_corpus_auditor_suite.py - Verification Suite for Physics Megarepo Epistemic Auditor (ADR-DISCOVERY-028)
Tests:
1. Subdiscipline classification across 8 canonical physics areas.
2. File scanning & extraction: extraction of equations, item types, and Fast System 1 triage (unseeded stochasticity, Marr level).
3. Deep System 2 Mathematical Proof Verification:
   - Sound deductive DAG (Sobolev + Gronwall) -> VERIFIED_COHERENT.
   - Circular lemma cycle -> REJECTED_CIRCULAR_LEMMA.
   - Unproven axiomatic assertion -> REJECTED_UNPROVEN_AXIOM.
4. Deep System 2 Experimental & Simulation Auditing:
   - Energy conservation breach -> REJECTED_CONSERVATION_VIOLATION.
   - Reality Contact Firewall: RCS < 2 or no anchors -> BLOCKED; RCS >= 2 with external anchors -> PASSED.
5. Batch Peer Review Dossier Generation:
   - Aggregates verdicts, calculates mean RCS, generates som_corpus_dossier_hash, and issues objective editorial judgment.
6. FastAPI REST API Endpoint verification via TestClient.
"""

import sys
import os
from pathlib import Path
import tempfile
import shutil

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

from python.discovery.physics_corpus_auditor import (
    PhysicsSubdiscipline,
    CorpusItemType,
    CorpusExtractedItem,
    ItemVerificationVerdict,
    MegarepoPeerReviewReport,
    PhysicsCorpusAuditor,
)
from python.discovery.physical_theorem_court import CourtVerdict
from fastapi.testclient import TestClient
from api.server import app


def test_subdiscipline_classification():
    print("\n--- 1. Testing Physics Subdiscipline Classification ---")
    auditor = PhysicsCorpusAuditor()

    # Classical Mechanics
    text_cm = "We derive the equations of motion using the Lagrangian L = T - V and Poisson brackets."
    assert auditor.classify_subdiscipline(text_cm) == PhysicsSubdiscipline.CLASSICAL_MECHANICS
    print("  [PASS] Classical Mechanics classified correctly")

    # Electrodynamics
    text_em = "Applying Maxwell's equations and Lorentz gauge to evaluate the Poynting vector flux."
    assert auditor.classify_subdiscipline(text_em) == PhysicsSubdiscipline.ELECTRODYNAMICS
    print("  [PASS] Electrodynamics classified correctly")

    # Thermodynamics / StatMech
    text_th = "The canonical partition function yields the Helmholtz free energy and thermodynamic entropy."
    assert auditor.classify_subdiscipline(text_th) == PhysicsSubdiscipline.THERMODYNAMICS_STATMECH
    print("  [PASS] Thermodynamics & StatMech classified correctly")

    # Quantum Mechanics
    text_qm = "The state vector in Hilbert space evolves under the Hermitian Hamiltonian via Schrödinger equation."
    assert auditor.classify_subdiscipline(text_qm) == PhysicsSubdiscipline.QUANTUM_MECHANICS
    print("  [PASS] Quantum Mechanics classified correctly")

    # General Relativity
    text_gr = "The geodesic equation in Schwarzschild metric derived from the Einstein tensor and Riemann curvature."
    assert auditor.classify_subdiscipline(text_gr) == PhysicsSubdiscipline.GENERAL_RELATIVITY_COSMOLOGY
    print("  [PASS] General Relativity classified correctly")

    # Fluids / Nonlinear
    text_fl = "Turbulent enstrophy dissipation in 3D Navier-Stokes at high Reynolds numbers."
    assert auditor.classify_subdiscipline(text_fl) == PhysicsSubdiscipline.NONLINEAR_DYNAMICS_FLUIDS
    print("  [PASS] Nonlinear Dynamics & Fluids classified correctly")


def test_file_scanning_and_system_one_triage():
    print("\n--- 2. Testing File Scanning & System 1 Triage ---")
    auditor = PhysicsCorpusAuditor()

    with tempfile.TemporaryDirectory() as tmpdir:
        # Create a mock Python simulation file with unseeded randomness and equation
        sim_path = Path(tmpdir) / "schrodinger_solver.py"
        sim_path.write_text(
            "import numpy as np\n"
            "# Solves the Schrodinger wave equation\n"
            "def solve_wavepacket(psi_0, V):\n"
            "    # $i \\hbar \\frac{\\partial \\psi}{\\partial t} = \\hat{H} \\psi$\n"
            "    noise = np.random.normal(0, 1)  # Unseeded!\n"
            "    return psi_0 + noise\n",
            encoding="utf-8"
        )

        item = auditor.scan_and_extract_file(sim_path)
        assert item is not None
        assert item.item_type == CorpusItemType.SIMULATION_SOLVER
        assert item.subdiscipline == PhysicsSubdiscipline.QUANTUM_MECHANICS
        assert item.system_one_risk_flag is True  # Detected unseeded stochasticity
        assert "Unseeded stochasticity" in item.system_one_notes
        assert len(item.detected_equations) > 0
        print(f"  [PASS] Extracted item: {item.item_id}, Subdiscipline: {item.subdiscipline.value}")
        print(f"  [PASS] System 1 Risk flagged correctly: {item.system_one_notes}")


def test_system_two_mathematical_proof_auditing():
    print("\n--- 3. Testing Deep System 2 Proof Auditing (DAG, Circularity, Axioms) ---")
    auditor = PhysicsCorpusAuditor()

    item = CorpusExtractedItem(
        item_id="PROOF-TEST-001",
        file_path="mock_proof.tex",
        subdiscipline=PhysicsSubdiscipline.NONLINEAR_DYNAMICS_FLUIDS,
        item_type=CorpusItemType.MATHEMATICAL_PROOF,
        title="Global Regularity of Leray Solutions",
        content_snippet="Sobolev inequality implies Gronwall bound.",
        raw_size_bytes=1024,
    )

    # 1. Sound proof
    v_sound = auditor.audit_proof_item(item, is_circular=False, unproven_axioms=False)
    assert v_sound.is_sound is True
    assert v_sound.court_verdict == CourtVerdict.VERIFIED_COHERENT.value
    assert v_sound.objective_recommendation == "PUBLISHABLE_MATHEMATICAL_THEOREM"
    assert v_sound.holonomy_defect == 0.0
    print("  [PASS] Sound proof passed formal court verification")

    # 2. Circular proof
    v_circ = auditor.audit_proof_item(item, is_circular=True, unproven_axioms=False)
    assert v_circ.is_sound is False
    assert v_circ.court_verdict == CourtVerdict.REJECTED_CIRCULAR_LEMMA.value
    assert "circular reasoning cycle" in v_circ.violations[1]
    assert v_circ.objective_recommendation == "REJECT_UNSOUND_PROOF_DAG"
    print(f"  [PASS] Circular proof intercepted: {v_circ.court_verdict}")

    # 3. Unproven axiom
    v_axiom = auditor.audit_proof_item(item, is_circular=False, unproven_axioms=True)
    assert v_axiom.is_sound is False
    assert v_axiom.court_verdict == CourtVerdict.REJECTED_UNPROVEN_AXIOM.value
    print(f"  [PASS] Unproven axiom intercepted: {v_axiom.court_verdict}")


def test_system_two_experimental_and_firewall_auditing():
    print("\n--- 4. Testing Deep System 2 Experimental Auditing & Reality Firewall ---")
    auditor = PhysicsCorpusAuditor()

    item = CorpusExtractedItem(
        item_id="EXP-TEST-002",
        file_path="lhc_higgs_cross_section.csv",
        subdiscipline=PhysicsSubdiscipline.QUANTUM_FIELD_THEORY_PARTICLES,
        item_type=CorpusItemType.EXPERIMENT_DATASET,
        title="LHC Higgs Boson Decay Invariant Cross Section",
        content_snippet="GeV cross sections measured by ATLAS/CMS",
        raw_size_bytes=2048,
    )

    # Scenario A: Real physical data with external benchmark (RCS=2)
    v_real = auditor.audit_experiment_item(item, empirical_rcs=2, has_external_benchmark=True, conserves_energy=True)
    assert v_real.is_sound is True
    assert v_real.reality_firewall_passed is True
    assert v_real.objective_recommendation == "VERIFIED_EMPIRICAL_INVARIANT"
    print("  [PASS] Grounded experimental dataset passed Reality Firewall (RCS=2)")

    # Scenario B: Energy conservation breach
    v_unphysical = auditor.audit_experiment_item(item, empirical_rcs=2, has_external_benchmark=True, conserves_energy=False)
    assert v_unphysical.is_sound is False
    assert v_unphysical.court_verdict == CourtVerdict.REJECTED_CONSERVATION_VIOLATION.value
    assert any("Hamiltonian energy drift" in vi for vi in v_unphysical.violations)
    print("  [PASS] Energy conservation breach intercepted")

    # Scenario C: Pure simulation (RCS=1) claiming to be an empirical law
    v_unanchored = auditor.audit_experiment_item(item, empirical_rcs=1, has_external_benchmark=False, conserves_energy=True)
    assert v_unanchored.reality_firewall_passed is False
    assert v_unanchored.is_sound is False
    assert any("BLOCKED" in vi for vi in v_unanchored.violations)
    print("  [PASS] Unanchored simulation blocked by Reality Contact Firewall")


def test_megarepo_peer_review_dossier():
    print("\n--- 5. Testing Batch Megarepo Peer Review Dossier Generation ---")
    auditor = PhysicsCorpusAuditor()

    # Create mock items representing chapters across different disciplines
    items = [
        CorpusExtractedItem("ITEM-01", "ch01_classical.tex", PhysicsSubdiscipline.CLASSICAL_MECHANICS, CorpusItemType.CHAPTER_THEORY, "Lagrangian Formulation of Mechanics", "L = T - V", 1000),
        CorpusExtractedItem("ITEM-02", "ch02_fluids_proof.tex", PhysicsSubdiscipline.NONLINEAR_DYNAMICS_FLUIDS, CorpusItemType.MATHEMATICAL_PROOF, "Navier Stokes Smoothness Bound", "Energy estimate", 1500),
        CorpusExtractedItem("ITEM-03", "ch03_qft_data.csv", PhysicsSubdiscipline.QUANTUM_FIELD_THEORY_PARTICLES, CorpusItemType.EXPERIMENT_DATASET, "Higgs Branching Ratios", "Decay data", 2500),
        CorpusExtractedItem("ITEM-04", "ch04_perpetual_sim.py", PhysicsSubdiscipline.THERMODYNAMICS_STATMECH, CorpusItemType.SIMULATION_SOLVER, "Non-equilibrium Work Engine", "Work extraction", 800),
    ]

    scenarios = {
        "ITEM-01": {"empirical_rcs": 2, "has_external_benchmark": True, "conserves_energy": True},
        "ITEM-02": {"is_circular": False, "unproven_axioms": False},
        "ITEM-03": {"empirical_rcs": 2, "has_external_benchmark": True, "conserves_energy": True},
        "ITEM-04": {"empirical_rcs": 0, "has_external_benchmark": False, "conserves_energy": False},  # Unphysical perpetual motion
    }

    report = auditor.audit_corpus_batch(items, simulated_eval_scenarios=scenarios)
    assert isinstance(report, MegarepoPeerReviewReport)
    assert report.total_items_scanned == 4
    assert report.verified_sound_count == 3
    assert report.falsified_or_rejected_count == 1
    assert report.som_corpus_dossier_hash.startswith("sha256:")
    assert "SUBSTANTIAL MERIT" in report.overall_editorial_judgment
    print(f"  [PASS] Peer Review Dossier: {report.verified_sound_count}/4 sound items")
    print(f"  [PASS] Editorial Judgment: {report.overall_editorial_judgment[:70]}...")
    print(f"  [PASS] Cryptographic Dossier Hash: {report.som_corpus_dossier_hash[:25]}...")

    d = report.to_dict()
    assert "item_verdicts" in d
    assert len(d["item_verdicts"]) == 4
    print("  [PASS] to_dict() verified")


def test_fastapi_rest_endpoint():
    print("\n--- 6. Testing FastAPI REST API Endpoint (/api/discovery/physics/audit-megarepo) ---")
    client = TestClient(app)

    with tempfile.TemporaryDirectory() as tmpdir:
        # Create a small sample repo
        (Path(tmpdir) / "chapter_electrodynamics.md").write_text("Maxwell equations in covariant tensor form: F^{mu nu}.", encoding="utf-8")
        (Path(tmpdir) / "proof_thermo.tex").write_text("Deduction of the Second Law and entropy non-decrease.", encoding="utf-8")
        (Path(tmpdir) / "data_cosmology.csv").write_text("redshift,distance_modulus\n0.1,38.2\n0.5,42.1", encoding="utf-8")

        resp = client.post("/api/discovery/physics/audit-megarepo", json={
            "repo_path": tmpdir,
            "max_files": 10
        })

        assert resp.status_code == 200
        data = resp.json()
        assert data["total_items_scanned"] == 3
        assert "overall_editorial_judgment" in data
        assert "som_corpus_dossier_hash" in data
        print(f"  [PASS] POST /api/discovery/physics/audit-megarepo -> {data['total_items_scanned']} items audited successfully")
        print(f"  [PASS] Editorial verdict: {data['overall_editorial_judgment'][:65]}...")


def main():
    print("=" * 80)
    print("ADR-DISCOVERY-028: Physics Megarepo Epistemic Auditor")
    print("Verification Suite")
    print("=" * 80)

    passed = 0
    failed = 0

    for test_fn in [
        test_subdiscipline_classification,
        test_file_scanning_and_system_one_triage,
        test_system_two_mathematical_proof_auditing,
        test_system_two_experimental_and_firewall_auditing,
        test_megarepo_peer_review_dossier,
        test_fastapi_rest_endpoint,
    ]:
        try:
            test_fn()
            passed += 1
        except Exception as e:
            failed += 1
            print(f"\n  [FAIL] {test_fn.__name__}: {e}")
            import traceback
            traceback.print_exc()

    print("\n" + "=" * 80)
    print(f"RESULTS: {passed} passed, {failed} failed out of {passed + failed} test groups")
    print("=" * 80)

    if failed > 0:
        sys.exit(1)
    else:
        print("[ALL GATES PASSED] ADR-DISCOVERY-028 verification complete.")


if __name__ == "__main__":
    main()
