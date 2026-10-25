"""
tests/test_structure_property_purpose_engine.py - Test Suite for Structure-Property-Purpose (SPP) Engine (ADR-DISCOVERY-076)
"""

import pytest
from python.discovery.structure_property_purpose_engine import (
    TeleonomicPurposeClass,
    IonicSelectivityProfile,
    StructurePropertyPurposeSpec,
    CompetitiveOccupancyReport,
    MultiscaleSppTriadReport,
    StructurePropertyPurposeEngine,
)
from python.discovery.physical_theorem_court import (
    PhysicalCoherenceCourt,
    CourtVerdict,
    PhysicalConservationType,
)


def test_troponin_c_site_ii_calcium_sensing_sound():
    """
    Validates that Cardiac Troponin C Site II successfully discriminates Ca2+
    over a 10,000-fold excess of background cytosolic Mg2+ (1 mM).
    """
    spec = StructurePropertyPurposeSpec(
        mechanism_id="MECH-CTNC-SITE2-REGULATORY",
        biological_system="Human Cardiac Thin Filament",
        target_site="Site II (Regulatory EF-Hand)",
        purpose_class=TeleonomicPurposeClass.SENSING,
        coordination_geometry="OCTAHEDRAL",
        coordinating_residues=["Asp65", "Asp67", "Gly69", "Glu76"],
        tolerated_basal_leak=0.15,
        required_stimulated_occupancy=0.60
    )

    # Site II: Kd(Ca2+) = 1 uM, Kd(Mg2+) = 10 mM (Selectivity S = 10,000)
    # Basal Ca2+ = 100 nM, Stimulated Ca2+ = 10 uM, Free Mg2+ = 1 mM
    selectivity = IonicSelectivityProfile(
        target_ion="CA2",
        competing_ion="MG2",
        kd_target_molar=1e-6,
        kd_competing_molar=1e-2,
        target_conc_basal_molar=1e-7,
        target_conc_stimulated_molar=1e-5,
        competing_conc_molar=1e-3
    )

    report = StructurePropertyPurposeEngine.audit_competitive_ionic_selectivity(spec, selectivity)

    assert report.is_purpose_fulfilled is True
    assert report.theta_target_basal < 0.15
    assert report.theta_target_stimulated > 0.85
    assert report.selectivity_ratio_s >= 1e4
    assert report.som_audit_hash.startswith("sha256:")


def test_unselective_sensor_competitive_collapse():
    """
    Validates that an unselective or mutated sensor is competitively poisoned
    by background Mg2+, failing the teleonomic sensing purpose.
    """
    spec = StructurePropertyPurposeSpec(
        mechanism_id="MECH-CTNC-MUTANT-COLLAPSED",
        biological_system="Mutant Cardiac Thin Filament",
        target_site="Site II (Affinity-Defective)",
        purpose_class=TeleonomicPurposeClass.SENSING,
        tolerated_basal_leak=0.15,
        required_stimulated_occupancy=0.60
    )

    # Mutant binds Mg2+ with high affinity (Kd = 0.1 mM instead of 10 mM)
    # Background 1 mM Mg2+ heavily competes out Ca2+ activation
    selectivity = IonicSelectivityProfile(
        target_ion="CA2",
        competing_ion="MG2",
        kd_target_molar=1e-6,
        kd_competing_molar=1e-4,  # Defect: 100x tighter Mg2+ binding
        target_conc_basal_molar=1e-7,
        target_conc_stimulated_molar=1e-5,
        competing_conc_molar=1e-3
    )

    report = StructurePropertyPurposeEngine.audit_competitive_ionic_selectivity(spec, selectivity)

    assert report.is_purpose_fulfilled is False
    assert report.theta_target_stimulated < 0.60
    assert report.theta_competing_stimulated > 0.45


def test_structural_sites_iii_iv_scaffolding_behavior():
    """
    Validates that structural Sites III and IV maintain high combined divalent occupancy
    at all physiological times, acting as structural scaffolding rather than dynamic switches.
    """
    spec = StructurePropertyPurposeSpec(
        mechanism_id="MECH-CTNC-SITES3-4-STRUCTURAL",
        biological_system="Human Cardiac Thin Filament",
        target_site="Sites III/IV (Structural)",
        purpose_class=TeleonomicPurposeClass.HOMEOSTATIC_REGULATION
    )

    # Structural sites: Kd(Ca2+) = 10 nM, Kd(Mg2+) = 20 uM
    selectivity = IonicSelectivityProfile(
        target_ion="CA2",
        competing_ion="MG2",
        kd_target_molar=1e-8,
        kd_competing_molar=2e-5,
        target_conc_basal_molar=1e-7,
        target_conc_stimulated_molar=1e-5,
        competing_conc_molar=1e-3
    )

    report = StructurePropertyPurposeEngine.audit_competitive_ionic_selectivity(spec, selectivity)

    total_divalent_occupancy_basal = report.theta_target_basal + report.theta_competing_basal
    total_divalent_occupancy_stim = report.theta_target_stimulated + report.theta_competing_stimulated

    # Structural sites remain saturated (> 95%) under both basal and systolic conditions
    assert total_divalent_occupancy_basal > 0.95
    assert total_divalent_occupancy_stim > 0.95
    assert report.is_purpose_fulfilled is True


def test_multiscale_spp_triad_coherence():
    """
    Validates the causal chain:
    Molecular sensing -> Continuum Ca2+ transport (CFD) -> Sarcomere force generation (Multibody).
    """
    spec = StructurePropertyPurposeSpec(
        mechanism_id="MECH-CARDIAC-EXCITATION-CONTRACTION",
        biological_system="Cardiac Myocyte",
        target_site="Sarcomeric Thin Filament",
        purpose_class=TeleonomicPurposeClass.FORCE_TRANSDUCTION
    )

    selectivity = IonicSelectivityProfile(
        target_ion="CA2",
        competing_ion="MG2",
        kd_target_molar=1e-6,
        kd_competing_molar=1e-2,
        target_conc_basal_molar=1e-7,
        target_conc_stimulated_molar=1e-5,
        competing_conc_molar=1e-3
    )

    ionic_report = StructurePropertyPurposeEngine.audit_competitive_ionic_selectivity(spec, selectivity)

    triad_report = StructurePropertyPurposeEngine.audit_multiscale_spp_triad(
        spec=spec,
        ionic_report=ionic_report,
        continuum_cfd_sound=True,
        mechanical_kinematics_sound=True,
        continuum_flow_rate=0.45,   # Non-zero intracellular flux
        mechanical_tension_n=75.0   # Active isometric twitch tension
    )

    assert triad_report.is_triad_coherent is True
    assert triad_report.molecular_level_sound is True
    assert triad_report.continuum_level_sound is True
    assert triad_report.mechanical_level_sound is True
    assert triad_report.coupling_efficiency > 0.50
    assert triad_report.som_triad_hash.startswith("sha256:")


def test_physical_coherence_court_arbitration_spp():
    """Validates end-to-end court arbitration for the SPP teleonomic invariant."""
    court = PhysicalCoherenceCourt()

    sound_report_data = {
        "is_purpose_fulfilled": True,
        "purpose_class": "SENSING",
        "theta_target_stimulated": 0.91,
        "theta_competing_stimulated": 0.08,
        "selectivity_ratio_s": 10000.0,
        "diagnostics": "Troponin C Site II sensory discrimination sound"
    }

    verdict_sound = court.audit_spp_teleonomic_report("CLAIM-SPP-001", sound_report_data)
    assert verdict_sound.verdict == CourtVerdict.VERIFIED_COHERENT
    assert verdict_sound.conservation_audit[0]["satisfied"] is True
    assert verdict_sound.conservation_audit[0]["law"] == "STRUCTURE_PROPERTY_PURPOSE_COHERENCE"

    breach_report_data = {
        "is_purpose_fulfilled": False,
        "purpose_class": "SENSING",
        "theta_target_stimulated": 0.35,
        "theta_competing_stimulated": 0.65,
        "selectivity_ratio_s": 50.0,
        "diagnostics": "Competitive collapse: Mg2+ poisons regulatory pocket"
    }

    verdict_breach = court.audit_spp_teleonomic_report("CLAIM-SPP-002", breach_report_data)
    assert verdict_breach.verdict == CourtVerdict.REJECTED_CONSERVATION_VIOLATION
    assert "Structure-Property-Purpose breach" in verdict_breach.duhem_quine_autopsy
