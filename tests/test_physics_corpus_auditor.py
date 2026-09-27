"""
tests/test_physics_corpus_auditor.py - Pytest suite for ADR-DISCOVERY-028 v3.0.
Verifies taxonomy classification, Buckingham Pi dimensional homogeneity, proof courts,
simulation solvers, patent gates, and deep System 1/2 pipelines.
"""

import pytest

from python.discovery.physical_theorem_court import CourtVerdict
from python.discovery.physics_corpus_auditor import (
    CorpusExtractedItem,
    CorpusItemType,
    ItemVerificationVerdict,
    PhysicsCorpusAuditor,
    PhysicsSubdiscipline,
    UniversalPhysicsDivision,
)


@pytest.mark.physics
@pytest.mark.fast
def test_taxonomy_divisions_coverage(physics_auditor: PhysicsCorpusAuditor):
    """Verifies that key subdisciplines map correctly across all 10 major physical divisions."""
    test_cases = [
        (
            "Renormalization group and ward identity in Yang-Mills path integral",
            UniversalPhysicsDivision.FUNDAMENTAL_HIGH_ENERGY,
            PhysicsSubdiscipline.QUANTUM_FIELD_THEORY,
        ),
        (
            "Gravitational waves detected by LIGO interferometer",
            UniversalPhysicsDivision.GRAVITATION_RELATIVITY_COSMOLOGY,
            PhysicsSubdiscipline.GRAVITATIONAL_WAVES,
        ),
        (
            "Quantum key distribution and Bell state entanglement",
            UniversalPhysicsDivision.QUANTUM_OPTICS_INFORMATION,
            PhysicsSubdiscipline.QUANTUM_INFORMATION_COMPUTING,
        ),
        (
            "Tokamak magnetic confinement and deuterium tritium plasma",
            UniversalPhysicsDivision.NUCLEAR_AND_PLASMA,
            PhysicsSubdiscipline.NUCLEAR_FISSION_FUSION,
        ),
        (
            "Cooper pairing in high temperature superconductors",
            UniversalPhysicsDivision.CONDENSED_MATTER_MATERIALS,
            PhysicsSubdiscipline.SUPERCONDUCTIVITY_SUPERFLUIDITY,
        ),
        (
            "Non-equilibrium entropy production in open systems",
            UniversalPhysicsDivision.THERMODYNAMICS_STATMECH_COMPLEXITY,
            PhysicsSubdiscipline.NON_EQUILIBRIUM_THERMODYNAMICS,
        ),
        (
            "Navier-Stokes turbulent boundary layer vorticity",
            UniversalPhysicsDivision.CLASSICAL_CONTINUUM_ACOUSTICS,
            PhysicsSubdiscipline.CONTINUUM_FLUID_DYNAMICS,
        ),
        (
            "Hertzsprung-Russell white dwarf supernova nucleosynthesis",
            UniversalPhysicsDivision.ASTROPHYSICS_SPACE_SCIENCES,
            PhysicsSubdiscipline.STELLAR_ASTROPHYSICS,
        ),
        (
            "Lipid bilayer phase transition and patch clamp conductance",
            UniversalPhysicsDivision.INTERDISCIPLINARY_APPLIED_PHYSICS,
            PhysicsSubdiscipline.BIOPHYSICS_MEMBRANES,
        ),
        (
            "Overunity generator patent application with continuous energy",
            UniversalPhysicsDivision.PATENTS_AND_TECHNICAL_DEVICES,
            PhysicsSubdiscipline.PATENT_ENERGY_GENERATION,
        ),
    ]

    for text, expected_div, expected_sub in test_cases:
        div, sub = physics_auditor.classify_subdiscipline_and_division(text)
        assert div == expected_div, f"Expected division {expected_div} for '{text[:30]}', got {div}"
        assert sub == expected_sub, f"Expected subdiscipline {expected_sub} for '{text[:30]}', got {sub}"


@pytest.mark.physics
@pytest.mark.fast
def test_anti_perpetual_motion_patent_interception(physics_auditor: PhysicsCorpusAuditor):
    """Verifies strict interception of overunity and reactionless drive claims."""
    # Overunity
    overunity_item = CorpusExtractedItem(
        item_id="PAT-OVERUNITY-01",
        file_path="/tmp/overunity.txt",
        division=UniversalPhysicsDivision.PATENTS_AND_TECHNICAL_DEVICES,
        subdiscipline=PhysicsSubdiscipline.PATENT_ENERGY_GENERATION,
        item_type=CorpusItemType.PATENT_TECHNICAL_CLAIM,
        title="Zero-Point Overunity Generator",
        content_snippet="Device achieves COP > 2.5 producing continuous electric power without fuel input.",
        raw_size_bytes=1000,
        is_perpetual_motion_risk=True,
    )
    v_overunity = physics_auditor.audit_patent_item(overunity_item, force_overunity=True)
    assert not v_overunity.is_sound
    assert v_overunity.court_verdict == CourtVerdict.REJECTED_CONSERVATION_VIOLATION.value
    assert any("Perpetual Motion" in v for v in v_overunity.violations)

    # Reactionless Drive
    emdrive_item = CorpusExtractedItem(
        item_id="PAT-EMDRIVE-02",
        file_path="/tmp/emdrive.txt",
        division=UniversalPhysicsDivision.PATENTS_AND_TECHNICAL_DEVICES,
        subdiscipline=PhysicsSubdiscipline.PATENT_PROPULSION_MECHANISMS,
        item_type=CorpusItemType.PATENT_TECHNICAL_CLAIM,
        title="Reactionless Propellantless RF Thruster",
        content_snippet="Asymmetric resonant cavity produces propellantless thrust with a reactionless drive violating Newton's third law.",
        raw_size_bytes=1200,
        is_perpetual_motion_risk=True,
    )
    v_emdrive = physics_auditor.audit_patent_item(emdrive_item)
    assert not v_emdrive.is_sound
    assert any("reactionless" in v.lower() for v in v_emdrive.violations)


@pytest.mark.physics
@pytest.mark.fast
def test_dimensional_homogeneity_auditing(physics_auditor: PhysicsCorpusAuditor):
    """Verifies Buckingham Pi dimensional consistency checks."""
    bad_eq = "Energy = Mass*c^2 + Force"  # Energy + Force
    is_homo_bad, diag_bad = physics_auditor.audit_dimensional_homogeneity([bad_eq])
    assert not is_homo_bad
    assert len(diag_bad) > 0

    good_eq = "E = m*c^2"
    is_homo_good, _ = physics_auditor.audit_dimensional_homogeneity([good_eq])
    assert is_homo_good


@pytest.mark.physics
@pytest.mark.epistemic
def test_deep_chapter_audit_pipeline(physics_auditor: PhysicsCorpusAuditor):
    """Verifies v3.0 audit_chapter_deep method integration."""
    item = CorpusExtractedItem(
        item_id="CORPUS-CH-TEST",
        file_path="/tmp/gr_chap.tex",
        division=UniversalPhysicsDivision.GRAVITATION_RELATIVITY_COSMOLOGY,
        subdiscipline=PhysicsSubdiscipline.GENERAL_RELATIVITY,
        item_type=CorpusItemType.CHAPTER_THEORY,
        title="Geodesic Invariance in Kerr Spacetime",
        content_snippet=(
            "The Kerr metric describes stationary axisymmetric vacuum solutions. "
            "Computational goal: preserve Killing tensor invariants. "
            "Algorithmic mechanism: Carter constant propagation along affine parameter. "
            "Implementational constraint: event horizon boundary r_+."
        ),
        raw_size_bytes=3000,
        detected_equations=["R_{mu nu} = 0", "Delta = r^2 - 2Mr + a^2"],
        dimensional_homogeneity_passed=True,
    )
    verdict = physics_auditor.audit_chapter_deep(item)
    assert isinstance(verdict, ItemVerificationVerdict)
    assert hasattr(verdict, "holonomy_defect")
    assert isinstance(verdict.holonomy_defect, float)
    assert verdict.item_id == "CORPUS-CH-TEST"


@pytest.mark.physics
@pytest.mark.epistemic
def test_deep_simulation_audit_pipeline(physics_auditor: PhysicsCorpusAuditor):
    """Verifies v3.0 audit_simulation_deep method integration."""
    item = CorpusExtractedItem(
        item_id="CORPUS-SIM-TEST",
        file_path="/tmp/fluid_sim.py",
        division=UniversalPhysicsDivision.CLASSICAL_CONTINUUM_ACOUSTICS,
        subdiscipline=PhysicsSubdiscipline.CONTINUUM_FLUID_DYNAMICS,
        item_type=CorpusItemType.SIMULATION_SOLVER,
        title="2D Incompressible Navier-Stokes Solver",
        content_snippet=(
            "import numpy as np\n"
            "def step(u, v, p, dt=0.001):\n"
            "    div = np.sum(np.abs(np.gradient(u)[0] + np.gradient(v)[1]))\n"
            "    return u, v, div\n"
        ),
        raw_size_bytes=400,
        dimensional_homogeneity_passed=True,
        system_one_notes="Stochasticity audit clean",
    )
    verdict = physics_auditor.audit_simulation_deep(item)
    assert isinstance(verdict, ItemVerificationVerdict)
    assert verdict.item_id == "CORPUS-SIM-TEST"
    assert hasattr(verdict, "reality_firewall_passed")


@pytest.mark.physics
@pytest.mark.slow
def test_adversarial_stress_test(physics_auditor: PhysicsCorpusAuditor):
    """Verifies 50-case adversarial destruction engine interaction."""
    item = CorpusExtractedItem(
        item_id="CORPUS-ADV-01",
        file_path="/tmp/hypo.tex",
        division=UniversalPhysicsDivision.FUNDAMENTAL_HIGH_ENERGY,
        subdiscipline=PhysicsSubdiscipline.BEYOND_STANDARD_MODEL,
        item_type=CorpusItemType.CHAPTER_THEORY,
        title="Novel Pseudoscalar Particle Proposal",
        content_snippet="Pseudoscalar coupling to dual electromagnetic tensor with mass m_a.",
        raw_size_bytes=500,
        dimensional_homogeneity_passed=True,
    )
    res = physics_auditor.run_adversarial_stress_test(item)
    assert isinstance(res, dict)
    assert "status" in res or "mortality_rate" in res or "error_detection_rate" in res
