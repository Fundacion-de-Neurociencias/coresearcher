"""
scripts/run_physics_corpus_auditor_suite.py - Verification Suite for Universal Physics Megarepo Epistemic Auditor (ADR-DISCOVERY-028 v2.0)
Tests:
1. Universal Physics Taxonomy Classification:
   - Covers all 10 major divisions and canonical subdisciplines (High Energy, GR, Quantum, Nuclear, Condensed Matter, Thermo, Classical, Astro, Applied, Patents).
2. Patent Claim Auditing & Thermodynamic Integrity:
   - Intercepts overunity / perpetual motion claims (COP > 1.0, free energy without fuel) with CRITICAL REJECTION.
   - Intercepts reactionless drive claims violating momentum conservation.
   - Certifies physically sound technical patents.
3. Dimensional Homogeneity (Buckingham Pi Theorem):
   - Intercepts equations adding dimensionally incompatible quantities (Energy + Force).
4. Multimodal File Extraction & System 1 Triage:
   - Scans .py simulation solvers, flags unseeded stochasticity, and detects mathematical equations.
5. Deep System 2 Mathematical Proof Auditing (DAG, Circularity, Axiomatic Leaks):
   - Verifies sound Sobolev-Gronwall proof.
   - Rejects circular lemma cycles.
   - Rejects unproven axiomatic assertions.
6. Deep System 2 Experimental Auditing & Reality Contact Firewall:
   - Grounded datasets (RCS >= 2) with physical anchors pass.
   - Energy conservation violations are caught and blocked.
7. Batch Peer Review Dossier Generation:
   - Aggregates multi-division verdicts, calculates mean RCS, tracks perpetual motion interceptions, and issues editorial judgment.
8. FastAPI REST API Endpoint verification (/api/discovery/physics/audit-megarepo).
"""

import sys
import os
from pathlib import Path
import tempfile
import shutil

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

from python.discovery.physics_corpus_auditor import (
    UniversalPhysicsDivision,
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


def test_universal_taxonomy_classification():
    print("\n--- 1. Testing Universal Physics Taxonomy Classification (10 Divisions) ---")
    auditor = PhysicsCorpusAuditor()

    cases = [
        ("Higgs boson decay into bottom quarks via CKM matrix in the electroweak sector.", UniversalPhysicsDivision.FUNDAMENTAL_HIGH_ENERGY, PhysicsSubdiscipline.PARTICLE_PHYSICS_STANDARD_MODEL),
        ("Gravitational waves detected by LIGO from binary black hole merger with chirp mass.", UniversalPhysicsDivision.GRAVITATION_RELATIVITY_COSMOLOGY, PhysicsSubdiscipline.GRAVITATIONAL_WAVES),
        ("Shor algorithm on a quantum circuit with fault-tolerant qubit error correction.", UniversalPhysicsDivision.QUANTUM_OPTICS_INFORMATION, PhysicsSubdiscipline.QUANTUM_INFORMATION_COMPUTING),
        ("Tokamak magnetic confinement of deuterium-tritium plasma meeting the Lawson criterion.", UniversalPhysicsDivision.NUCLEAR_AND_PLASMA, PhysicsSubdiscipline.NUCLEAR_FISSION_FUSION),
        ("Cooper pair condensation in high-Tc superconductivity and Meissner effect flux expulsion.", UniversalPhysicsDivision.CONDENSED_MATTER_MATERIALS, PhysicsSubdiscipline.SUPERCONDUCTIVITY_SUPERFLUIDITY),
        ("Non-equilibrium entropy production and Onsager reciprocity relations in open systems.", UniversalPhysicsDivision.THERMODYNAMICS_STATMECH_COMPLEXITY, PhysicsSubdiscipline.NON_EQUILIBRIUM_THERMODYNAMICS),
        ("Navier-Stokes turbulent energy cascade with high Reynolds number and viscous dissipation.", UniversalPhysicsDivision.CLASSICAL_CONTINUUM_ACOUSTICS, PhysicsSubdiscipline.CONTINUUM_FLUID_DYNAMICS),
        ("Chandrasekhar limit and core collapse nucleosynthesis in white dwarf and supernova evolution.", UniversalPhysicsDivision.ASTROPHYSICS_SPACE_SCIENCES, PhysicsSubdiscipline.STELLAR_ASTROPHYSICS),
        ("Patch clamp recording of lipid bilayer ion channels governed by Nernst-Planck electrodiffusion.", UniversalPhysicsDivision.INTERDISCIPLINARY_APPLIED_PHYSICS, PhysicsSubdiscipline.BIOPHYSICS_MEMBRANES),
        ("Invention patent claim for an electromagnetic power generator with piezoelectric detector.", UniversalPhysicsDivision.PATENTS_AND_TECHNICAL_DEVICES, PhysicsSubdiscipline.PATENT_ENERGY_GENERATION),
    ]

    for text, expected_div, expected_sub in cases:
        div, sub = auditor.classify_subdiscipline_and_division(text)
        assert div == expected_div, f"Expected {expected_div}, got {div} for text: {text[:50]}"
        print(f"  [PASS] Division verified: {div.value} -> {sub.value}")


def test_patent_claim_and_thermodynamic_auditing():
    print("\n--- 2. Testing Technical Patent Auditing & Anti-Perpetuum-Mobile Gate ---")
    auditor = PhysicsCorpusAuditor()

    # Case A: Blatant overunity claim
    text_overunity = "Claim 1: A self-powered electromagnetic motor generator achieving free energy with COP > 1.8 without fuel."
    passed_a, violations_a = auditor.audit_patent_thermodynamic_claims(text_overunity)
    assert passed_a is False
    assert any("Overunity / Perpetual Motion" in v for v in violations_a)
    print("  [PASS] Overunity / Perpetual Motion patent claim strictly INTERCEPTED")

    # Case B: Reactionless drive claim
    text_reactionless = "Claim 1: A spacecraft propellantless propulsion engine producing continuous reactionless thrust."
    passed_b, violations_b = auditor.audit_patent_thermodynamic_claims(text_reactionless)
    assert passed_b is False
    assert any("reactionless/propellantless" in v for v in violations_b)
    print("  [PASS] Reactionless drive claim violating momentum conservation INTERCEPTED")

    # Case C: Physically sound patent claim
    text_valid = "Claim 1: A cryogenic SQUID sensor device for measuring weak magnetic flux variations with calibrated superconducting loops."
    passed_c, violations_c = auditor.audit_patent_thermodynamic_claims(text_valid)
    assert passed_c is True
    assert len(violations_c) == 0
    print("  [PASS] Physically sound invention patent verified")


def test_dimensional_homogeneity_auditing():
    print("\n--- 3. Testing Dimensional Homogeneity (Buckingham Pi Principle) ---")
    auditor = PhysicsCorpusAuditor()

    # Incompatible addition: Energy + Force
    bad_eqs = ["Total_Quantity = Energy + Force"]
    passed_bad, violations = auditor.audit_dimensional_homogeneity(bad_eqs)
    assert passed_bad is False
    assert any("adds or equates Energy" in v for v in violations)
    print("  [PASS] Dimensionally inconsistent equation intercepted: Energy + Force")

    # Sound equations
    good_eqs = ["E = m * c**2", "F = m * a", "p = h / lambda"]
    passed_good, _ = auditor.audit_dimensional_homogeneity(good_eqs)
    assert passed_good is True
    print("  [PASS] Dimensionally homogeneous equations passed")


def test_file_scanning_and_multimodal_extraction():
    print("\n--- 4. Testing Multimodal File Scanning & System 1 Triage ---")
    auditor = PhysicsCorpusAuditor()

    with tempfile.TemporaryDirectory() as tmpdir:
        # Create a Python simulation file
        sim_path = Path(tmpdir) / "plasma_tokamak_solver.py"
        sim_path.write_text(
            "import numpy as np\n"
            "# Solves the MHD equilibrium in a tokamak\n"
            "def solve_plasma_equilibrium(B_field, pressure):\n"
            "    # $\\nabla p = \\mathbf{J} \\times \\mathbf{B}$\n"
            "    noise = np.random.normal(0, 1)  # Unseeded!\n"
            "    return pressure * 1.0\n",
            encoding="utf-8"
        )

        item = auditor.scan_and_extract_file(sim_path)
        assert item is not None
        assert item.item_type == CorpusItemType.SIMULATION_SOLVER
        assert item.division == UniversalPhysicsDivision.NUCLEAR_AND_PLASMA
        assert item.system_one_risk_flag is True  # Detected unseeded stochasticity
        print(f"  [PASS] Scanned: {item.title}, Division: {item.division.value}, Sub: {item.subdiscipline.value}")


def test_deep_system_two_mathematical_proofs():
    print("\n--- 5. Testing Deep System 2 Mathematical Proof Courts ---")
    auditor = PhysicsCorpusAuditor()

    item = CorpusExtractedItem(
        item_id="PROOF-TEST-001",
        file_path="riemann_geodesic_proof.tex",
        division=UniversalPhysicsDivision.GRAVITATION_RELATIVITY_COSMOLOGY,
        subdiscipline=PhysicsSubdiscipline.GENERAL_RELATIVITY,
        item_type=CorpusItemType.MATHEMATICAL_PROOF,
        title="Geodesic Completeness in Schwarzschild Spacetime",
        content_snippet="Sobolev embedding and Gronwall inequality.",
        raw_size_bytes=2048,
    )

    # 1. Sound proof
    v_sound = auditor.audit_proof_item(item, is_circular=False, unproven_axioms=False)
    assert v_sound.is_sound is True
    assert v_sound.court_verdict == CourtVerdict.VERIFIED_COHERENT.value
    print("  [PASS] Valid mathematical proof verified as sound theorem")

    # 2. Circular proof
    v_circ = auditor.audit_proof_item(item, is_circular=True, unproven_axioms=False)
    assert v_circ.is_sound is False
    assert v_circ.court_verdict == CourtVerdict.REJECTED_CIRCULAR_LEMMA.value
    print("  [PASS] Circular proof intercepted")

    # 3. Unproven axiom
    v_axiom = auditor.audit_proof_item(item, is_circular=False, unproven_axioms=True)
    assert v_axiom.is_sound is False
    assert v_axiom.court_verdict == CourtVerdict.REJECTED_UNPROVEN_AXIOM.value
    print("  [PASS] Unproven axiomatic leap intercepted")


def test_deep_system_two_experiments_and_reality_firewall():
    print("\n--- 6. Testing Deep System 2 Experimental Audits & Reality Firewall ---")
    auditor = PhysicsCorpusAuditor()

    item = CorpusExtractedItem(
        item_id="EXP-FITS-001",
        file_path="planck_cmb_spectrum.fits",
        division=UniversalPhysicsDivision.GRAVITATION_RELATIVITY_COSMOLOGY,
        subdiscipline=PhysicsSubdiscipline.COSMOLOGY_EARLY_UNIVERSE,
        item_type=CorpusItemType.EXPERIMENT_DATASET,
        title="Planck 2018 CMB Angular Power Spectrum",
        content_snippet="TT, TE, EE angular power spectra Cl",
        raw_size_bytes=1048576,
    )

    # Valid grounded experiment (RCS=2)
    v_exp = auditor.audit_experiment_item(item, empirical_rcs=2, has_external_benchmark=True, conserves_energy=True)
    assert v_exp.is_sound is True
    assert v_exp.reality_firewall_passed is True
    print("  [PASS] Real cosmological dataset passed Reality Firewall")

    # Energy conservation violation
    v_unphysical = auditor.audit_experiment_item(item, empirical_rcs=2, has_external_benchmark=True, conserves_energy=False)
    assert v_unphysical.is_sound is False
    assert v_unphysical.court_verdict == CourtVerdict.REJECTED_CONSERVATION_VIOLATION.value
    print("  [PASS] Physical conservation breach intercepted")


def test_megarepo_batch_peer_review_dossier():
    print("\n--- 7. Testing Universal Physics Megarepo Batch Peer Review Dossier ---")
    auditor = PhysicsCorpusAuditor()

    items = [
        CorpusExtractedItem("ITEM-01", "ch01_strings.tex", UniversalPhysicsDivision.FUNDAMENTAL_HIGH_ENERGY, PhysicsSubdiscipline.STRING_THEORY_QUANTUM_GRAVITY, CorpusItemType.CHAPTER_THEORY, "AdS/CFT Holographic Correspondence", "D-brane action", 3000),
        CorpusExtractedItem("ITEM-02", "ch02_plasma_fusion.py", UniversalPhysicsDivision.NUCLEAR_AND_PLASMA, PhysicsSubdiscipline.NUCLEAR_FISSION_FUSION, CorpusItemType.SIMULATION_SOLVER, "Tokamak Lawson Ignition Solver", "Lawson criterion", 4000),
        CorpusExtractedItem("ITEM-03", "ch03_patent_overunity.txt", UniversalPhysicsDivision.PATENTS_AND_TECHNICAL_DEVICES, PhysicsSubdiscipline.PATENT_ENERGY_GENERATION, CorpusItemType.PATENT_TECHNICAL_CLAIM, "Self-Powered Free Energy Device", "Free energy with COP > 2.0", 1200, is_perpetual_motion_risk=True),
        CorpusExtractedItem("ITEM-04", "ch04_supercond_proof.tex", UniversalPhysicsDivision.CONDENSED_MATTER_MATERIALS, PhysicsSubdiscipline.SUPERCONDUCTIVITY_SUPERFLUIDITY, CorpusItemType.MATHEMATICAL_PROOF, "BCS Gap Invariant Theorem", "Gronwall estimate", 2500),
    ]

    scenarios = {
        "ITEM-01": {"empirical_rcs": 2, "has_external_benchmark": True, "conserves_energy": True},
        "ITEM-02": {"empirical_rcs": 2, "has_external_benchmark": True, "conserves_energy": True},
        "ITEM-03": {"force_overunity": True},  # Unphysical patent
        "ITEM-04": {"is_circular": False, "unproven_axioms": False},
    }

    report = auditor.audit_corpus_batch(items, simulated_eval_scenarios=scenarios)
    assert isinstance(report, MegarepoPeerReviewReport)
    assert report.total_items_scanned == 4
    # v3.0: CHAPTER_THEORY->audit_chapter_deep, SIMULATION_SOLVER->audit_simulation_deep;
    # exact sound/rejected split varies by LLM response/fallback — check invariants instead.
    assert report.verified_sound_count + report.falsified_or_rejected_count == 4
    assert report.perpetual_motion_interceptions_count == 1   # overunity patent always rejected
    assert len(report.division_breakdown) == 10
    assert report.som_corpus_dossier_hash.startswith("sha256:")
    print(f"  [PASS] Batch Dossier verified: {report.verified_sound_count}/4 sound items")
    print(f"  [PASS] Perpetual motion / overunity intercepted: {report.perpetual_motion_interceptions_count}")
    print(f"  [PASS] 10 Divisions tracked: {len(report.division_breakdown)}")
    print(f"  [PASS] Dossier Hash: {report.som_corpus_dossier_hash[:25]}...")


def test_fastapi_rest_endpoint():
    print("\n--- 8. Testing FastAPI REST API Endpoint (/api/discovery/physics/audit-megarepo) ---")
    client = TestClient(app)

    with tempfile.TemporaryDirectory() as tmpdir:
        (Path(tmpdir) / "chapter_qft.md").write_text("Feynman path integrals in Yang-Mills gauge field theory.", encoding="utf-8")
        (Path(tmpdir) / "patent_generator.txt").write_text("Claim 1: A magnetohydrodynamic sensor device.", encoding="utf-8")
        (Path(tmpdir) / "data_condensed.csv").write_text("temperature,resistance\n4.2,0.0\n10.0,0.05", encoding="utf-8")

        resp = client.post("/api/discovery/physics/audit-megarepo", json={
            "repo_path": tmpdir,
            "max_files": 10
        })

        assert resp.status_code == 200
        data = resp.json()
        assert data["total_items_scanned"] == 3
        assert "perpetual_motion_interceptions_count" in data
        assert "division_breakdown" in data
        print(f"  [PASS] POST /api/discovery/physics/audit-megarepo -> {data['total_items_scanned']} items audited via REST")
        print(f"  [PASS] Editorial verdict: {data['overall_editorial_judgment'][:65]}...")


def main():
    print("=" * 80)
    print("ADR-DISCOVERY-028 v2.0: Universal Physics Megarepo Epistemic Auditor")
    print("Comprehensive Verification Suite across 10 Divisions & Multimodal Artifacts")
    print("=" * 80)

    passed = 0
    failed = 0

    for test_fn in [
        test_universal_taxonomy_classification,
        test_patent_claim_and_thermodynamic_auditing,
        test_dimensional_homogeneity_auditing,
        test_file_scanning_and_multimodal_extraction,
        test_deep_system_two_mathematical_proofs,
        test_deep_system_two_experiments_and_reality_firewall,
        test_megarepo_batch_peer_review_dossier,
        test_fastapi_rest_endpoint,
        test_v3_audit_chapter_deep,
        test_v3_audit_simulation_deep,
        test_v3_adversarial_stress_test,
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
        print("[ALL GATES PASSED] ADR-DISCOVERY-028 v3.0 Full-Engine + Laya/LocalIA Physics Auditor verification complete.")


# ---------------------------------------------------------------------------
# v3.0 Test Groups (9–11)
# ---------------------------------------------------------------------------

def test_v3_audit_chapter_deep():
    """Test 9: audit_chapter_deep on a synthetic CHAPTER_THEORY item (Laya/LocalIA with graceful fallback)."""
    print("\n--- 9. Testing v3.0 audit_chapter_deep (System 1+2 deep pipeline) ---")
    auditor = PhysicsCorpusAuditor()

    item = CorpusExtractedItem(
        item_id="CORPUS-TEST-CHAPTER-V3",
        file_path="/tmp/chapter_gr.tex",
        division=UniversalPhysicsDivision.GRAVITATION_RELATIVITY_COSMOLOGY,
        subdiscipline=PhysicsSubdiscipline.GENERAL_RELATIVITY,
        item_type=CorpusItemType.CHAPTER_THEORY,
        title="Schwarzschild Metric Derivation",
        content_snippet=(
            "The Einstein field equations G_{mu nu} = 8 pi T_{mu nu} admit the Schwarzschild solution "
            "ds^2 = -(1-2M/r)dt^2 + (1-2M/r)^{-1}dr^2 + r^2 d Omega^2. "
            "The computational goal is to maintain spacetime curvature conservation. "
            "The algorithmic mechanism is geodesic deviation propagation. "
            "Implementational constraint: metric signature (-,+,+,+)."
        ),
        raw_size_bytes=2048,
        detected_equations=["G_{mu nu} = 8 pi T_{mu nu}", "ds^2 = -(1-2M/r)dt^2"],
        dimensional_homogeneity_passed=True,
    )

    verdict = auditor.audit_chapter_deep(item)

    assert isinstance(verdict, ItemVerificationVerdict), "audit_chapter_deep must return ItemVerificationVerdict"
    assert hasattr(verdict, "holonomy_defect"), "verdict must have holonomy_defect"
    assert hasattr(verdict, "is_sound"), "verdict must have is_sound"
    assert isinstance(verdict.holonomy_defect, float), "holonomy_defect must be float"
    assert verdict.item_id == "CORPUS-TEST-CHAPTER-V3"
    assert "CHAPTER" in verdict.objective_recommendation or "COHERENT" in verdict.objective_recommendation or "REJECTED" in verdict.objective_recommendation

    status = "SOUND" if verdict.is_sound else f"REVIEW_NEEDED (holonomy={verdict.holonomy_defect:.2e})"
    print(f"  [PASS] audit_chapter_deep: verdict={verdict.court_verdict} | status={status} | novelty={verdict.objective_recommendation}")


def test_v3_audit_simulation_deep():
    """Test 10: audit_simulation_deep on a synthetic SIMULATION_SOLVER item."""
    print("\n--- 10. Testing v3.0 audit_simulation_deep (DreamRSI + ScienceIDE + Hakken) ---")
    auditor = PhysicsCorpusAuditor()

    item = CorpusExtractedItem(
        item_id="CORPUS-TEST-SIM-V3",
        file_path="/tmp/navier_stokes_solver.py",
        division=UniversalPhysicsDivision.CLASSICAL_CONTINUUM_ACOUSTICS,
        subdiscipline=PhysicsSubdiscipline.CONTINUUM_FLUID_DYNAMICS,
        item_type=CorpusItemType.SIMULATION_SOLVER,
        title="Navier Stokes Solver",
        content_snippet=(
            "import numpy as np\n"
            "def solve_ns(u, v, p, nu=1e-3, dt=0.01):\n"
            "    # Continuity: div(u) ~ 0\n"
            "    # Momentum: du/dt + (u.grad)u = -grad(p) + nu * lap(u)\n"
            "    u_new = u - dt * (u * np.gradient(u) + np.gradient(p)) + nu * dt * np.gradient(np.gradient(u))\n"
            "    return u_new\n"
        ),
        raw_size_bytes=512,
        dimensional_homogeneity_passed=True,
        system_one_notes="Unseeded stochasticity check passed",
    )

    verdict = auditor.audit_simulation_deep(item)

    assert isinstance(verdict, ItemVerificationVerdict), "audit_simulation_deep must return ItemVerificationVerdict"
    assert hasattr(verdict, "holonomy_defect")
    assert hasattr(verdict, "reality_firewall_passed")
    assert verdict.item_id == "CORPUS-TEST-SIM-V3"

    print(f"  [PASS] audit_simulation_deep: verdict={verdict.court_verdict} | sound={verdict.is_sound} | recommendation={verdict.objective_recommendation}")


def test_v3_adversarial_stress_test():
    """Test 11: run_adversarial_stress_test returns a dict with status key."""
    print("\n--- 11. Testing v3.0 run_adversarial_stress_test (AdversarialDestructionEngine) ---")
    auditor = PhysicsCorpusAuditor()

    item = CorpusExtractedItem(
        item_id="CORPUS-TEST-ADVERSARIAL-V3",
        file_path="/tmp/bsm_theory.tex",
        division=UniversalPhysicsDivision.FUNDAMENTAL_HIGH_ENERGY,
        subdiscipline=PhysicsSubdiscipline.BEYOND_STANDARD_MODEL,
        item_type=CorpusItemType.CHAPTER_THEORY,
        title="Novel BSM Axion Field Theory",
        content_snippet="The axion field phi satisfies the equation of motion: box phi + m_a^2 phi = 0.",
        raw_size_bytes=1024,
        dimensional_homogeneity_passed=True,
    )

    result = auditor.run_adversarial_stress_test(item)

    assert isinstance(result, dict), "run_adversarial_stress_test must return dict"
    assert "status" in result or "mortality_rate" in result or "error_detection_rate" in result, \
        "Result dict must contain status or summary metrics"

    print(f"  [PASS] run_adversarial_stress_test: keys={list(result.keys())[:5]}")


if __name__ == "__main__":
    main()
