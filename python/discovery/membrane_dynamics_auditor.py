"""
python/discovery/membrane_dynamics_auditor.py - Biophysical Membrane Dynamics Contract & Duhem-Quine Simulation Auditor (ADR-DISCOVERY-026)
Formalizes molecular dynamics workflows and membrane biophysics (e.g. BAX pro-apoptotic pore,
Amyloid-Beta 42 synaptic pore, Tau membrane permeabilization, TREM2 lipid rafts):
1. MembraneSimulationContract: Declares target protein, lipid bilayer composition, auxiliary parameter assumptions, and reference experimental invariants.
2. BiophysicalDuhemQuineAuditor: Performs rigorous Duhem-Quine failure decomposition when simulation observables (area per lipid A_L, thickness, order parameter) deviate from experiment. Differentiates between auxiliary parameter artifacts (force field Van der Waals, barostat dampening, dehydration, premature equilibration cutoff) and hard-core conformational refutations.
3. MembraneInvariantVerifier: Verifies symplectic Hamiltonian energy conservation, bilayer incompressibility, and thermodynamic entropy production.
4. Generates cryptographic SOM-SHA256 hashes and integrates with DataAILab via ARCH-002 demarcation.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, Any, List, Optional
import time
import math
import hashlib
import json
import uuid

from python.discovery.failure_engine import DuhemQuineBlameType


class MembraneLipidSpecies(str, Enum):
    POPE = "POPE"                    # 1-palmitoyl-2-oleoyl-sn-glycero-3-phosphoethanolamine
    POPC = "POPC"                    # 1-palmitoyl-2-oleoyl-sn-glycero-3-phosphocholine
    CHOLESTEROL = "CHOLESTEROL"      # Essential for lipid rafts & fluidity modulation
    CARDIOLIPIN = "CARDIOLIPIN"      # Crucial for mitochondrial inner/outer membrane & BAX pore
    SPHINGOMYELIN = "SPHINGOMYELIN"  # Microdomain organization
    DOPE = "DOPE"                    # 1,2-dioleoyl-sn-glycero-3-phosphoethanolamine


class ForceFieldArchetype(str, Enum):
    CHARMM36M = "CHARMM36M"          # Gold standard for membrane proteins & lipids
    AMBER19SB_LIPID21 = "AMBER19SB_LIPID21"  # Amber lipid21 force field with OPC/TIP3P water
    GROMOS_54A7 = "GROMOS_54A7"      # United-atom force field (historical/coarse)
    MARTINI_3_COARSE = "MARTINI_3_COARSE"  # Coarse-grained representation


class PressureCouplingScheme(str, Enum):
    SEMI_ISOTROPIC_PARRINELLO_RAHMAN = "SEMI_ISOTROPIC_PARRINELLO_RAHMAN"  # Correct XY/Z decoupling for bilayers
    BERENDSEN_WEAK = "BERENDSEN_WEAK"  # Exponential relaxation, known area suppression artifact
    MONTE_CARLO_MEMBRANE = "MONTE_CARLO_MEMBRANE"  # OpenMM / NAMD MC barostat
    ISOTROPIC = "ISOTROPIC"          # Defective for planar bilayers (distorts surface tension)


class ThermostatScheme(str, Enum):
    NOSE_HOOVER = "NOSE_HOOVER"      # Canonical ensemble (NVT/NPT)
    V_RESCALE = "V_RESCALE"          # Bussi-Donadio-Parrinello stochastic velocity rescaling
    BERENDSEN = "BERENDSEN"          # Flying ice-cube artifact risk


class TargetMembraneSystem(str, Enum):
    BAX_PORE = "BAX_PORE"                            # Pro-apoptotic pore in mitochondrial membrane
    AMYLOID_BETA_PORE = "AMYLOID_BETA_PORE"          # Abeta42 oligomer cationic nanopore
    TAU_PERMEABILIZATION = "TAU_PERMEABILIZATION"    # Tau-induced outer mitochondrial membrane rupture
    TREM2_LIPID_RAFT = "TREM2_LIPID_RAFT"            # Microglial receptor in cholesterol-rich raft
    SYNAPTIC_VESICLE_FUSION = "SYNAPTIC_VESICLE_FUSION"  # SNARE / Synaptotagmin lipid fusion


class BiophysicalBlameTarget(str, Enum):
    FORCE_FIELD_VDW_OVERATTRACTION = "FORCE_FIELD_VDW_OVERATTRACTION"
    BAROSTAT_SURFACE_TENSION_MISCOUPLING = "BAROSTAT_SURFACE_TENSION_MISCOUPLING"
    OSMOTIC_DEHYDRATION = "OSMOTIC_DEHYDRATION"
    EQUILIBRATION_TRUNCATION = "EQUILIBRATION_TRUNCATION"
    PROTEIN_LIPID_PACKING_CONSTRAINED = "PROTEIN_LIPID_PACKING_CONSTRAINED"
    HARD_CORE_CONFORMATION_REFUTED = "HARD_CORE_CONFORMATION_REFUTED"


@dataclass
class LipidCompositionItem:
    species: MembraneLipidSpecies
    ratio: float  # Fraction summing to 1.0


@dataclass
class AuxiliarySimulationParams:
    force_field: ForceFieldArchetype
    pressure_coupling: PressureCouplingScheme
    thermostat: ThermostatScheme
    target_temperature_kelvin: float = 310.15
    target_pressure_bar: float = 1.01325
    waters_per_lipid: float = 40.0
    equilibration_length_ns: float = 100.0
    production_length_ns: float = 500.0
    timestep_fs: float = 2.0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "force_field": self.force_field.value,
            "pressure_coupling": self.pressure_coupling.value,
            "thermostat": self.thermostat.value,
            "target_temperature_kelvin": self.target_temperature_kelvin,
            "target_pressure_bar": self.target_pressure_bar,
            "waters_per_lipid": self.waters_per_lipid,
            "equilibration_length_ns": self.equilibration_length_ns,
            "production_length_ns": self.production_length_ns,
            "timestep_fs": self.timestep_fs,
        }


@dataclass
class ExperimentalReferenceConstraints:
    expected_area_per_lipid_nm2: float
    area_per_lipid_tolerance: float = 0.03
    expected_bilayer_thickness_nm: float = 3.90
    bilayer_thickness_tolerance: float = 0.25
    min_order_parameter_scd: float = 0.16
    max_pore_conductance_ns: Optional[float] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "expected_area_per_lipid_nm2": self.expected_area_per_lipid_nm2,
            "area_per_lipid_tolerance": self.area_per_lipid_tolerance,
            "expected_bilayer_thickness_nm": self.expected_bilayer_thickness_nm,
            "bilayer_thickness_tolerance": self.bilayer_thickness_tolerance,
            "min_order_parameter_scd": self.min_order_parameter_scd,
            "max_pore_conductance_ns": self.max_pore_conductance_ns,
        }


@dataclass
class MembraneSimulationContract:
    contract_id: str
    target_system: TargetMembraneSystem
    lipid_composition: List[LipidCompositionItem]
    auxiliary_params: AuxiliarySimulationParams
    experimental_constraints: ExperimentalReferenceConstraints
    som_contract_hash: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return {
            "contract_id": self.contract_id,
            "target_system": self.target_system.value,
            "lipid_composition": [{"species": l.species.value, "ratio": l.ratio} for l in self.lipid_composition],
            "auxiliary_params": self.auxiliary_params.to_dict(),
            "experimental_constraints": self.experimental_constraints.to_dict(),
            "som_contract_hash": self.som_contract_hash
        }

    def compute_som_hash(self) -> str:
        raw_payload = json.dumps({
            "cid": self.contract_id,
            "system": self.target_system.value,
            "lipids": [{"s": l.species.value, "r": l.ratio} for l in self.lipid_composition],
            "aux": self.auxiliary_params.to_dict(),
            "exp": self.experimental_constraints.to_dict()
        }, sort_keys=True)
        return f"sha256:{hashlib.sha256(raw_payload.encode('utf-8')).hexdigest()[:24]}"


@dataclass
class MembraneSimulationObservables:
    observed_area_per_lipid_nm2: float
    observed_bilayer_thickness_nm: float
    observed_order_parameter_scd: float
    observed_pore_radius_nm: float = 0.0
    energy_drift_ratio: float = 1e-5  # |(E_t - E_0) / E_0| per ns
    entropy_production_rate: float = 0.002
    equilibration_converged: bool = True
    runtime_ns_completed: float = 200.0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "observed_area_per_lipid_nm2": round(self.observed_area_per_lipid_nm2, 4),
            "observed_bilayer_thickness_nm": round(self.observed_bilayer_thickness_nm, 4),
            "observed_order_parameter_scd": round(self.observed_order_parameter_scd, 4),
            "observed_pore_radius_nm": round(self.observed_pore_radius_nm, 4),
            "energy_drift_ratio": round(self.energy_drift_ratio, 6),
            "entropy_production_rate": round(self.entropy_production_rate, 6),
            "equilibration_converged": self.equilibration_converged,
            "runtime_ns_completed": self.runtime_ns_completed
        }


@dataclass
class BiophysicalDuhemQuineDiagnosis:
    diagnosis_id: str
    contract_id: str
    blame_classification: DuhemQuineBlameType
    primary_blame_target: BiophysicalBlameTarget
    ranked_blame_probabilities: Dict[str, float]
    discrepancy_narrative: str
    remediation_protocol: str
    next_action_directive: str
    som_diagnosis_hash: str

    def to_dict(self) -> Dict[str, Any]:
        return {
            "diagnosis_id": self.diagnosis_id,
            "contract_id": self.contract_id,
            "blame_classification": self.blame_classification.value,
            "primary_blame_target": self.primary_blame_target.value,
            "ranked_blame_probabilities": {k: round(v, 4) for k, v in self.ranked_blame_probabilities.items()},
            "discrepancy_narrative": self.discrepancy_narrative,
            "remediation_protocol": self.remediation_protocol,
            "next_action_directive": self.next_action_directive,
            "som_diagnosis_hash": self.som_diagnosis_hash
        }


@dataclass
class MembraneInvariantVerificationReport:
    report_id: str
    contract_id: str
    is_physically_sound: bool
    energy_drift_passed: bool
    incompressibility_passed: bool
    thermodynamic_entropy_passed: bool
    diagnostics: List[str]
    som_verification_hash: str

    def to_dict(self) -> Dict[str, Any]:
        return {
            "report_id": self.report_id,
            "contract_id": self.contract_id,
            "is_physically_sound": self.is_physically_sound,
            "energy_drift_passed": self.energy_drift_passed,
            "incompressibility_passed": self.incompressibility_passed,
            "thermodynamic_entropy_passed": self.thermodynamic_entropy_passed,
            "diagnostics": self.diagnostics,
            "som_verification_hash": self.som_verification_hash
        }


class BiophysicalContractBuilder:
    """
    Factory creating standardized biophysical membrane simulation contracts.
    """

    @classmethod
    def create_bax_membrane_contract(
        cls,
        contract_id: Optional[str] = None,
        force_field: ForceFieldArchetype = ForceFieldArchetype.CHARMM36M,
        pressure_coupling: PressureCouplingScheme = PressureCouplingScheme.SEMI_ISOTROPIC_PARRINELLO_RAHMAN,
        waters_per_lipid: float = 40.0,
        equilibration_length_ns: float = 100.0
    ) -> MembraneSimulationContract:
        cid = contract_id or f"MC-BAX-{uuid.uuid4().hex[:6].upper()}"
        lipids = [
            LipidCompositionItem(species=MembraneLipidSpecies.POPE, ratio=0.60),
            LipidCompositionItem(species=MembraneLipidSpecies.POPC, ratio=0.20),
            LipidCompositionItem(species=MembraneLipidSpecies.CARDIOLIPIN, ratio=0.20),
        ]
        aux = AuxiliarySimulationParams(
            force_field=force_field,
            pressure_coupling=pressure_coupling,
            thermostat=ThermostatScheme.NOSE_HOOVER,
            target_temperature_kelvin=310.15,
            waters_per_lipid=waters_per_lipid,
            equilibration_length_ns=equilibration_length_ns,
            production_length_ns=500.0
        )
        # Experimental reference: POPE/POPC/Cardiolipin bilayer equilibrates to ~0.59 nm^2 per lipid
        exp = ExperimentalReferenceConstraints(
            expected_area_per_lipid_nm2=0.590,
            area_per_lipid_tolerance=0.025,
            expected_bilayer_thickness_nm=3.85,
            bilayer_thickness_tolerance=0.20,
            min_order_parameter_scd=0.18,
            max_pore_conductance_ns=1.2
        )
        contract = MembraneSimulationContract(
            contract_id=cid,
            target_system=TargetMembraneSystem.BAX_PORE,
            lipid_composition=lipids,
            auxiliary_params=aux,
            experimental_constraints=exp
        )
        contract.som_contract_hash = contract.compute_som_hash()
        return contract

    @classmethod
    def create_amyloid_pore_contract(
        cls,
        contract_id: Optional[str] = None,
        force_field: ForceFieldArchetype = ForceFieldArchetype.CHARMM36M
    ) -> MembraneSimulationContract:
        cid = contract_id or f"MC-ABETA-{uuid.uuid4().hex[:6].upper()}"
        lipids = [
            LipidCompositionItem(species=MembraneLipidSpecies.POPC, ratio=0.70),
            LipidCompositionItem(species=MembraneLipidSpecies.CHOLESTEROL, ratio=0.30),
        ]
        aux = AuxiliarySimulationParams(
            force_field=force_field,
            pressure_coupling=PressureCouplingScheme.SEMI_ISOTROPIC_PARRINELLO_RAHMAN,
            thermostat=ThermostatScheme.NOSE_HOOVER,
            waters_per_lipid=45.0,
            equilibration_length_ns=150.0,
            production_length_ns=600.0
        )
        exp = ExperimentalReferenceConstraints(
            expected_area_per_lipid_nm2=0.540,
            area_per_lipid_tolerance=0.030,
            expected_bilayer_thickness_nm=4.10,
            bilayer_thickness_tolerance=0.25,
            min_order_parameter_scd=0.22,
            max_pore_conductance_ns=0.8
        )
        contract = MembraneSimulationContract(
            contract_id=cid,
            target_system=TargetMembraneSystem.AMYLOID_BETA_PORE,
            lipid_composition=lipids,
            auxiliary_params=aux,
            experimental_constraints=exp
        )
        contract.som_contract_hash = contract.compute_som_hash()
        return contract


class BiophysicalDuhemQuineAuditor:
    """
    Formal Duhem-Quine failure attribution engine for molecular dynamics & membrane simulations.
    When observables diverge from experimental bounds, isolates whether the cause is an auxiliary
    parameter artifact (force field, barostat, hydration, time) or a core conformational refutation.
    """

    @classmethod
    def diagnose_simulation_anomaly(
        cls,
        contract: MembraneSimulationContract,
        observables: MembraneSimulationObservables
    ) -> BiophysicalDuhemQuineDiagnosis:
        diag_id = f"DQ-MD-{uuid.uuid4().hex[:8].upper()}"
        exp = contract.experimental_constraints
        aux = contract.auxiliary_params

        delta_al = observables.observed_area_per_lipid_nm2 - exp.expected_area_per_lipid_nm2
        delta_thick = observables.observed_bilayer_thickness_nm - exp.expected_bilayer_thickness_nm
        tol_al = exp.area_per_lipid_tolerance

        # Initialize candidate blame probabilities
        blame_weights: Dict[BiophysicalBlameTarget, float] = {
            BiophysicalBlameTarget.FORCE_FIELD_VDW_OVERATTRACTION: 0.05,
            BiophysicalBlameTarget.BAROSTAT_SURFACE_TENSION_MISCOUPLING: 0.05,
            BiophysicalBlameTarget.OSMOTIC_DEHYDRATION: 0.05,
            BiophysicalBlameTarget.EQUILIBRATION_TRUNCATION: 0.05,
            BiophysicalBlameTarget.PROTEIN_LIPID_PACKING_CONSTRAINED: 0.05,
            BiophysicalBlameTarget.HARD_CORE_CONFORMATION_REFUTED: 0.05
        }

        # 1. Evaluate Area Per Lipid (A_L) Under-equilibration (e.g. POPE A_L below experimental)
        if delta_al < -tol_al:
            # Under-condensation of area per lipid (lipids packed too tightly)
            deficit = abs(delta_al)

            # Check 1a: Osmotic Dehydration (< 30 waters/lipid causes lateral contraction)
            if aux.waters_per_lipid < 30.0:
                blame_weights[BiophysicalBlameTarget.OSMOTIC_DEHYDRATION] += 5.0 * (30.0 - aux.waters_per_lipid)

            # Check 1b: Barostat Coupling (Isotropic coupling or Berendsen artificial dampening)
            if aux.pressure_coupling == PressureCouplingScheme.ISOTROPIC:
                blame_weights[BiophysicalBlameTarget.BAROSTAT_SURFACE_TENSION_MISCOUPLING] += 8.0
            elif aux.pressure_coupling == PressureCouplingScheme.BERENDSEN_WEAK:
                blame_weights[BiophysicalBlameTarget.BAROSTAT_SURFACE_TENSION_MISCOUPLING] += 4.5

            # Check 1c: Equilibration time truncation (< 50 ns or unconverged)
            if observables.runtime_ns_completed < 50.0 or not observables.equilibration_converged:
                blame_weights[BiophysicalBlameTarget.EQUILIBRATION_TRUNCATION] += 6.0

            # Check 1d: Force Field Van der Waals over-attraction (e.g. GROMOS or coarse models)
            if aux.force_field in [ForceFieldArchetype.GROMOS_54A7, ForceFieldArchetype.MARTINI_3_COARSE]:
                blame_weights[BiophysicalBlameTarget.FORCE_FIELD_VDW_OVERATTRACTION] += 6.5
            elif aux.force_field == ForceFieldArchetype.AMBER19SB_LIPID21 and any(l.species == MembraneLipidSpecies.CARDIOLIPIN for l in contract.lipid_composition):
                # Specific known amber lipid21 cardiolipin cross-term nuance
                blame_weights[BiophysicalBlameTarget.FORCE_FIELD_VDW_OVERATTRACTION] += 2.5

            # Check 1e: Protein-to-lipid overcrowding
            if observables.observed_pore_radius_nm > 0.0 and len(contract.lipid_composition) <= 1:
                blame_weights[BiophysicalBlameTarget.PROTEIN_LIPID_PACKING_CONSTRAINED] += 3.0

        elif delta_al > tol_al:
            # Over-expansion of membrane (bilayer disintegration)
            if aux.pressure_coupling == PressureCouplingScheme.ISOTROPIC:
                blame_weights[BiophysicalBlameTarget.BAROSTAT_SURFACE_TENSION_MISCOUPLING] += 6.0
            if observables.energy_drift_ratio > 1e-4:
                blame_weights[BiophysicalBlameTarget.HARD_CORE_CONFORMATION_REFUTED] += 5.0

        # 2. Check for Hard-Core Refutation:
        # If all auxiliary parameters are already optimal (CHARMM36m, Semi-isotropic Parrinello-Rahman, >35 waters, >150ns)
        # and yet observables diverge by > 3x tolerance, the blame falls on the core conformational model!
        is_aux_ideal = (
            aux.force_field == ForceFieldArchetype.CHARMM36M and
            aux.pressure_coupling == PressureCouplingScheme.SEMI_ISOTROPIC_PARRINELLO_RAHMAN and
            aux.waters_per_lipid >= 35.0 and
            observables.runtime_ns_completed >= 100.0 and
            observables.equilibration_converged
        )
        if is_aux_ideal and (abs(delta_al) > (2.5 * tol_al) or observables.energy_drift_ratio > 1e-3):
            blame_weights[BiophysicalBlameTarget.HARD_CORE_CONFORMATION_REFUTED] += 12.0

        # Normalize probability distribution
        total_w = sum(blame_weights.values())
        prob_dist = {k.value: v / total_w for k, v in blame_weights.items()}
        primary_target = max(blame_weights, key=blame_weights.get)

        # Allocate formal Duhem-Quine classification
        if primary_target == BiophysicalBlameTarget.HARD_CORE_CONFORMATION_REFUTED:
            blame_class = DuhemQuineBlameType.CORE_HYPOTHESIS_FATAL
            narrative = (
                f"Core structural hypothesis refuted: Simulated observables (A_L = {observables.observed_area_per_lipid_nm2:.3f} nm^2) "
                f"breached experimental bounds ({exp.expected_area_per_lipid_nm2:.3f} +/- {tol_al:.3f} nm^2) despite optimal auxiliary parameters."
            )
            remedy = "Demolish current oligomer / pore model conformation. Transfer model to Defeated Hypotheses Graveyard."
            action = "FORK_CONFORMATION_IN_GRAVEYARD"
        else:
            blame_class = DuhemQuineBlameType.AUXILIARY_ASSUMPTION_DEFECTIVE
            narrative = (
                f"Auxiliary simulation parameter defect identified ({primary_target.value}): Discrepancy in area per lipid "
                f"(observed {observables.observed_area_per_lipid_nm2:.3f} vs expected {exp.expected_area_per_lipid_nm2:.3f} nm^2) "
                f"is driven by auxiliary parameter miscalibration, not core biological hypothesis invalidity."
            )
            remedy = cls._generate_remedy(primary_target, aux)
            action = "CALIBRATE_SIMULATION_PARAMETERS_AND_RE-EXECUTE"

        # SOM diagnosis hash
        som_payload = json.dumps({
            "diag_id": diag_id,
            "cid": contract.contract_id,
            "blame": primary_target.value,
            "class": blame_class.value,
            "probs": prob_dist
        }, sort_keys=True)
        som_hash = f"sha256:{hashlib.sha256(som_payload.encode('utf-8')).hexdigest()[:24]}"

        return BiophysicalDuhemQuineDiagnosis(
            diagnosis_id=diag_id,
            contract_id=contract.contract_id,
            blame_classification=blame_class,
            primary_blame_target=primary_target,
            ranked_blame_probabilities=prob_dist,
            discrepancy_narrative=narrative,
            remediation_protocol=remedy,
            next_action_directive=action,
            som_diagnosis_hash=som_hash
        )

    @classmethod
    def _generate_remedy(cls, target: BiophysicalBlameTarget, aux: AuxiliarySimulationParams) -> str:
        if target == BiophysicalBlameTarget.BAROSTAT_SURFACE_TENSION_MISCOUPLING:
            return (
                "Switch pressure coupling to SEMI_ISOTROPIC_PARRINELLO_RAHMAN with decoupled XY and Z compressibilities "
                "(compressibility = 4.5e-5 bar^-1, tau_p = 5.0 ps). Avoid isotropic coupling or Berendsen barostats."
            )
        elif target == BiophysicalBlameTarget.OSMOTIC_DEHYDRATION:
            return (
                f"Increase solvent box dimensions to provide at least 40-45 water molecules per lipid (current: {aux.waters_per_lipid:.1f}). "
                "Ensure physiological 150 mM NaCl ionic strength."
            )
        elif target == BiophysicalBlameTarget.EQUILIBRATION_TRUNCATION:
            return (
                f"Extend NPT equilibration phase beyond 150 ns (current completed: {aux.equilibration_length_ns:.1f} ns) "
                "until running average of area per lipid (A_L) slope d<A_L>/dt < 1e-5 nm^2/ns."
            )
        elif target == BiophysicalBlameTarget.FORCE_FIELD_VDW_OVERATTRACTION:
            return (
                "Upgrade force field parameters to CHARMM36m (with modified water Lennard-Jones parameters) or AMBER19SB/lipid21. "
                "Avoid uncalibrated united-atom force fields for lipid-protein interfaces."
            )
        elif target == BiophysicalBlameTarget.PROTEIN_LIPID_PACKING_CONSTRAINED:
            return (
                "Expand bilayer XY patch dimensions: increase lipid-to-protein ratio from current setup to >= 150:1 lipids per subunit "
                "to eliminate periodic box boundary artifacts."
            )
        return "Review auxiliary parameter ensemble."


class MembraneInvariantVerifier:
    """
    ScienceIDE-compatible physical invariant verifier for membrane simulations.
    Audits symplectic energy conservation, incompressibility, and thermodynamic entropy.
    """

    @classmethod
    def verify_invariants(
        cls,
        contract: MembraneSimulationContract,
        observables: MembraneSimulationObservables,
        max_energy_drift_per_ns: float = 1e-4
    ) -> MembraneInvariantVerificationReport:
        rep_id = f"MIV-{uuid.uuid4().hex[:8].upper()}"
        diagnostics = []

        # Invariant 1: Symplectic Hamiltonian Energy Drift
        energy_ok = observables.energy_drift_ratio <= max_energy_drift_per_ns
        if not energy_ok:
            diagnostics.append(
                f"Hamiltonian energy drift breached: {observables.energy_drift_ratio:.2e} > tol={max_energy_drift_per_ns:.2e} per ns. "
                "Integrator instability or timestep tau too large."
            )

        # Invariant 2: Bilayer Incompressibility & Area Bounds
        exp = contract.experimental_constraints
        al_min = exp.expected_area_per_lipid_nm2 - (2.0 * exp.area_per_lipid_tolerance)
        al_max = exp.expected_area_per_lipid_nm2 + (2.0 * exp.area_per_lipid_tolerance)
        incompressibility_ok = (al_min <= observables.observed_area_per_lipid_nm2 <= al_max)
        if not incompressibility_ok:
            diagnostics.append(
                f"Bilayer incompressibility violated: A_L={observables.observed_area_per_lipid_nm2:.3f} nm^2 outside bounds [{al_min:.3f}, {al_max:.3f}]."
            )

        # Invariant 3: Thermodynamic Entropy Production (2nd Law: entropy rate >= -1e-6)
        entropy_ok = observables.entropy_production_rate >= -1e-6
        if not entropy_ok:
            diagnostics.append(
                f"Second law violation: entropy production rate S_dot={observables.entropy_production_rate:.2e} < 0."
            )

        all_passed = energy_ok and incompressibility_ok and entropy_ok

        # SOM verification hash
        som_payload = json.dumps({
            "rid": rep_id,
            "cid": contract.contract_id,
            "energy_ok": energy_ok,
            "incomp_ok": incompressibility_ok,
            "entropy_ok": entropy_ok
        }, sort_keys=True)
        som_hash = f"sha256:{hashlib.sha256(som_payload.encode('utf-8')).hexdigest()[:24]}"

        return MembraneInvariantVerificationReport(
            report_id=rep_id,
            contract_id=contract.contract_id,
            is_physically_sound=all_passed,
            energy_drift_passed=energy_ok,
            incompressibility_passed=incompressibility_ok,
            thermodynamic_entropy_passed=entropy_ok,
            diagnostics=diagnostics,
            som_verification_hash=som_hash
        )
