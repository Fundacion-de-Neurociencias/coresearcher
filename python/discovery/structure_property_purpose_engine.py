"""
python/discovery/structure_property_purpose_engine.py - Structure-Property-Purpose (SPP) Teleonomic Mechanism Engine (ADR-DISCOVERY-076)

Provides causal biomimetic modeling bridging molecular structure to physiological purpose:
1. Formalizes teleonomic purpose classes:
   - SENSING (e.g. Ca2+ threshold detection in Troponin C Site II or synaptic sensors)
   - GATING_ALLOSTERY (e.g. conformational shifts in thin filaments unblocking actin)
   - FORCE_TRANSDUCTION (e.g. sarcomere contraction and mechanical tension generation)
   - HOMEOSTATIC_REGULATION (e.g. cytoplasmic Ca2+ clearance and diastolic relaxation)
   - CATALYTIC_REPAIR (e.g. autopoietic enzymatic maintenance)
2. Competitive Ionic Discrimination Auditing:
   - Exact two-ligand competitive Langmuir-Hill isotherm under physiological millimolar/nanomolar regimes:
     theta_target = ([target] / KD_target) / (1 + [target] / KD_target + [competing] / KD_competing)
   - Selectivity Index: S = KD_competing / KD_target
   - Guarantees regulatory sensing sites are not saturated by 10,000x excess of background Mg2+ (1 mM).
3. Multiscale Triad Coupling:
   - Connects molecular coordination (BiomacromolecularCoordinationAuditor),
     continuum cytoplasmic ion transport (OpenFoamContinuumOracle),
     and sarcomere mechanical lattice kinematics (IsaacSimGroundingAdapter) into an auditable causal chain.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, Any, List, Optional, Tuple
import hashlib
import json
import math
import numpy as np


class TeleonomicPurposeClass(str, Enum):
    SENSING = "SENSING"                              # High-affinity, selective detection of signal triggers
    GATING_ALLOSTERY = "GATING_ALLOSTERY"            # Ligand- or voltage-induced conformational switching
    FORCE_TRANSDUCTION = "FORCE_TRANSDUCTION"        # Conversion of chemical energy into mechanical tension
    HOMEOSTATIC_REGULATION = "HOMEOSTATIC_REGULATION"# Feedback loops restoring basal physiological states
    CATALYTIC_REPAIR = "CATALYTIC_REPAIR"            # Enzymatic turnover maintaining metabolic closure


@dataclass
class IonicSelectivityProfile:
    """Biophysical parameters for competitive ion binding at regulatory or structural pockets."""
    target_ion: str = "CA2"
    competing_ion: str = "MG2"
    kd_target_molar: float = 1e-6          # e.g., 1 uM for Ca2+ on Troponin C Site II
    kd_competing_molar: float = 1e-2       # e.g., 10 mM for Mg2+ on Site II (weak affinity)
    target_conc_basal_molar: float = 1e-7   # 100 nM resting cytosolic calcium
    target_conc_stimulated_molar: float = 1e-5 # 10 uM stimulated systolic calcium
    competing_conc_molar: float = 1e-3     # 1 mM physiological cytosolic free magnesium

    def to_dict(self) -> Dict[str, Any]:
        return {
            "target_ion": self.target_ion,
            "competing_ion": self.competing_ion,
            "kd_target_molar": float(self.kd_target_molar),
            "kd_competing_molar": float(self.kd_competing_molar),
            "target_conc_basal_molar": float(self.target_conc_basal_molar),
            "target_conc_stimulated_molar": float(self.target_conc_stimulated_molar),
            "competing_conc_molar": float(self.competing_conc_molar)
        }


@dataclass
class StructurePropertyPurposeSpec:
    """Specifications linking macromolecular structural geometry to physiological teleonomic purpose."""
    mechanism_id: str
    biological_system: str
    target_site: str
    purpose_class: TeleonomicPurposeClass
    coordination_geometry: str = "OCTAHEDRAL"
    coordinating_residues: List[str] = field(default_factory=list)
    allosteric_coupling_factor: float = 1.0
    tolerated_basal_leak: float = 0.15          # Max fractional target occupancy permitted at basal state
    required_stimulated_occupancy: float = 0.60 # Min fractional target occupancy demanded at stimulated state

    def to_dict(self) -> Dict[str, Any]:
        return {
            "mechanism_id": self.mechanism_id,
            "biological_system": self.biological_system,
            "target_site": self.target_site,
            "purpose_class": self.purpose_class.value,
            "coordination_geometry": self.coordination_geometry,
            "coordinating_residues": self.coordinating_residues,
            "allosteric_coupling_factor": float(self.allosteric_coupling_factor),
            "tolerated_basal_leak": float(self.tolerated_basal_leak),
            "required_stimulated_occupancy": float(self.required_stimulated_occupancy)
        }


@dataclass
class CompetitiveOccupancyReport:
    mechanism_id: str
    purpose_class: TeleonomicPurposeClass
    theta_target_basal: float
    theta_target_stimulated: float
    theta_competing_basal: float
    theta_competing_stimulated: float
    selectivity_ratio_s: float
    is_purpose_fulfilled: bool
    diagnostics: str
    som_audit_hash: str
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "mechanism_id": self.mechanism_id,
            "purpose_class": self.purpose_class.value,
            "theta_target_basal": float(self.theta_target_basal),
            "theta_target_stimulated": float(self.theta_target_stimulated),
            "theta_competing_basal": float(self.theta_competing_basal),
            "theta_competing_stimulated": float(self.theta_competing_stimulated),
            "selectivity_ratio_s": float(self.selectivity_ratio_s),
            "is_purpose_fulfilled": self.is_purpose_fulfilled,
            "diagnostics": self.diagnostics,
            "som_audit_hash": self.som_audit_hash,
            "metadata": self.metadata
        }


@dataclass
class MultiscaleSppTriadReport:
    mechanism_id: str
    molecular_level_sound: bool
    continuum_level_sound: bool
    mechanical_level_sound: bool
    is_triad_coherent: bool
    coupling_efficiency: float
    som_triad_hash: str
    diagnostics: str

    def to_dict(self) -> Dict[str, Any]:
        return {
            "mechanism_id": self.mechanism_id,
            "molecular_level_sound": self.molecular_level_sound,
            "continuum_level_sound": self.continuum_level_sound,
            "mechanical_level_sound": self.mechanical_level_sound,
            "is_triad_coherent": self.is_triad_coherent,
            "coupling_efficiency": float(self.coupling_efficiency),
            "som_triad_hash": self.som_triad_hash,
            "diagnostics": self.diagnostics
        }


class StructurePropertyPurposeEngine:
    """
    Epistemic engine evaluating whether physical and molecular structures fulfill
    their teleonomic purpose without false-positive activation or competitive collapse.
    """

    @classmethod
    def compute_competitive_occupancy(
        cls,
        target_conc: float,
        competing_conc: float,
        kd_target: float,
        kd_competing: float
    ) -> Tuple[float, float]:
        """
        Computes exact fractional occupancies for two competing ligands:
        theta_A = (A / Kd_A) / (1 + A / Kd_A + B / Kd_B)
        theta_B = (B / Kd_B) / (1 + A / Kd_A + B / Kd_B)
        """
        if kd_target <= 0.0 or kd_competing <= 0.0:
            raise ValueError(f"Dissociation constants must be strictly positive: Kd_target={kd_target}, Kd_competing={kd_competing}")

        term_target = max(0.0, target_conc) / kd_target
        term_competing = max(0.0, competing_conc) / kd_competing
        denom = 1.0 + term_target + term_competing

        theta_target = term_target / denom
        theta_competing = term_competing / denom
        return float(theta_target), float(theta_competing)

    @classmethod
    def audit_competitive_ionic_selectivity(
        cls,
        spec: StructurePropertyPurposeSpec,
        selectivity: IonicSelectivityProfile
    ) -> CompetitiveOccupancyReport:
        """
        Evaluates whether a sensory or regulatory binding site successfully discriminates
        against high background competitor ions (e.g. Ca2+ sensor operating in 1 mM free Mg2+).
        """
        # 1. Basal State Occupancy
        theta_t_basal, theta_c_basal = cls.compute_competitive_occupancy(
            target_conc=selectivity.target_conc_basal_molar,
            competing_conc=selectivity.competing_conc_molar,
            kd_target=selectivity.kd_target_molar,
            kd_competing=selectivity.kd_competing_molar
        )

        # 2. Stimulated State Occupancy
        theta_t_stim, theta_c_stim = cls.compute_competitive_occupancy(
            target_conc=selectivity.target_conc_stimulated_molar,
            competing_conc=selectivity.competing_conc_molar,
            kd_target=selectivity.kd_target_molar,
            kd_competing=selectivity.kd_competing_molar
        )

        # 3. Selectivity ratio S = Kd_competing / Kd_target
        selectivity_ratio_s = float(selectivity.kd_competing_molar / selectivity.kd_target_molar)

        # 4. Teleonomic Purpose Assessment
        if spec.purpose_class == TeleonomicPurposeClass.SENSING:
            # Must remain off at basal, and switch on at stimulated
            basal_quiet = (theta_t_basal <= spec.tolerated_basal_leak)
            stim_active = (theta_t_stim >= spec.required_stimulated_occupancy)
            is_fulfilled = basal_quiet and stim_active
            diagnostics = (
                f"Sensing Purpose Audit: theta_basal={theta_t_basal:.3f} (max={spec.tolerated_basal_leak:.2f}), "
                f"theta_stim={theta_t_stim:.3f} (min={spec.required_stimulated_occupancy:.2f}), "
                f"Selectivity S={selectivity_ratio_s:.1e}, fulfilled={is_fulfilled}"
            )
        elif spec.purpose_class == TeleonomicPurposeClass.GATING_ALLOSTERY:
            dynamic_range = theta_t_stim - theta_t_basal
            is_fulfilled = dynamic_range >= 0.50
            diagnostics = (
                f"Allosteric Gating Audit: dynamic_range={dynamic_range:.3f} (min=0.50), "
                f"competitor_block_at_stim={theta_c_stim:.3f}, fulfilled={is_fulfilled}"
            )
        else:
            # Default purpose check
            is_fulfilled = theta_t_stim > theta_t_basal
            diagnostics = (
                f"General Teleonomic Audit: purpose={spec.purpose_class.value}, "
                f"theta_stim={theta_t_stim:.3f}, theta_basal={theta_t_basal:.3f}, fulfilled={is_fulfilled}"
            )

        hasher = hashlib.sha256()
        hasher.update(
            f"{spec.mechanism_id}:{theta_t_basal}:{theta_t_stim}:{selectivity_ratio_s}:{is_fulfilled}".encode("utf-8")
        )
        som_audit_hash = f"sha256:{hasher.hexdigest()}"

        return CompetitiveOccupancyReport(
            mechanism_id=spec.mechanism_id,
            purpose_class=spec.purpose_class,
            theta_target_basal=theta_t_basal,
            theta_target_stimulated=theta_t_stim,
            theta_competing_basal=theta_c_basal,
            theta_competing_stimulated=theta_c_stim,
            selectivity_ratio_s=selectivity_ratio_s,
            is_purpose_fulfilled=is_fulfilled,
            diagnostics=diagnostics,
            som_audit_hash=som_audit_hash,
            metadata={
                "target_ion": selectivity.target_ion,
                "competing_ion": selectivity.competing_ion,
                "kd_target": selectivity.kd_target_molar,
                "kd_competing": selectivity.kd_competing_molar
            }
        )

    @classmethod
    def audit_multiscale_spp_triad(
        cls,
        spec: StructurePropertyPurposeSpec,
        ionic_report: CompetitiveOccupancyReport,
        continuum_cfd_sound: bool,
        mechanical_kinematics_sound: bool,
        continuum_flow_rate: float,
        mechanical_tension_n: float
    ) -> MultiscaleSppTriadReport:
        """
        Harmonizes the multiscale causal chain:
        Molecular Sensory Activation -> Continuum Ion Diffusion (CFD) -> Sarcomere Mechanical Tension (Multibody).
        """
        molecular_sound = ionic_report.is_purpose_fulfilled
        continuum_sound = continuum_cfd_sound and (continuum_flow_rate > 0.0)
        mechanical_sound = mechanical_kinematics_sound and (mechanical_tension_n > 0.0)

        is_triad_coherent = molecular_sound and continuum_sound and mechanical_sound

        # Coupling efficiency is product of occupancy activation and normalized tension
        if is_triad_coherent:
            act_delta = max(0.0, ionic_report.theta_target_stimulated - ionic_report.theta_target_basal)
            norm_tension = min(1.0, mechanical_tension_n / 100.0)
            coupling_eff = float(act_delta * norm_tension)
        else:
            coupling_eff = 0.0

        diagnostics = (
            f"Multiscale SPP Triad Audit: Molecular={molecular_sound}, Continuum={continuum_sound}, "
            f"Mechanical={mechanical_sound}, Coherent={is_triad_coherent}, Efficiency={coupling_eff:.3f}"
        )

        hasher = hashlib.sha256()
        hasher.update(f"{spec.mechanism_id}:{is_triad_coherent}:{coupling_eff}".encode("utf-8"))
        som_triad_hash = f"sha256:{hasher.hexdigest()}"

        return MultiscaleSppTriadReport(
            mechanism_id=spec.mechanism_id,
            molecular_level_sound=molecular_sound,
            continuum_level_sound=continuum_sound,
            mechanical_level_sound=mechanical_sound,
            is_triad_coherent=is_triad_coherent,
            coupling_efficiency=coupling_eff,
            som_triad_hash=som_triad_hash,
            diagnostics=diagnostics
        )
