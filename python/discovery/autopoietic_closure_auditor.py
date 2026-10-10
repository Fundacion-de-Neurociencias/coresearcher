"""
Rosen Autopoietic Closure & Causal Organization Auditor (ADR-DISCOVERY-052).
Inspired by Robert Rosen (Life Itself, (M,R)-systems, 1991), Adam Frank (The Atlantic, 2025),
and A.H. Louie's categorical formalization of biological closure to efficient causation:

Core Axioms:
1. "Closed to Efficient Causation": In living systems, every efficient cause (catalyst / enzyme /
   repair operator f: A -> B) is itself the target of an internal production or repair mapping
   Phi: B -> H(A, B).
2. Demarcation Between Linear Mechanical DAGs and Autopoietic Functional Loops:
   - Tautological Circularity (Fallacy in logic / deadlocks): X -> X without metabolic throughput.
   - Autopoietic Causal Closure (Life): Open to material & energy flux (thermodynamic dissipation),
     yet closed to relational efficient causation.
3. Categorical (M,R)-System Verification:
   Audits whether candidate biological theories have causal open leaks (unaccounted external
   super-catalysts) or constitute genuine autonomous autopoietic organization.
4. Non-Equilibrium Dissipation Check:
   Enforces Prigogine entropy dissipation (sigma_ent > 0) supporting metabolic turnover.
5. Sovereign Merkle Sealing (som_autopoietic_hash) registered into ScientificLedger.
"""

from __future__ import annotations

import enum
import hashlib
import json
import math
import time
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Set, Tuple

import numpy as np

from python.discovery.categorical_epistemic_engine import (
    CategoryMorphism,
    CategoryObject,
    EpistemicCategory,
    MorphismType,
)
from python.observer.scientific_ledger import ScientificLedger


class CausalityType(str, enum.Enum):
    MATERIAL_INPUT = "MATERIAL_INPUT"        # Substrate entering reaction (Aristotelian material cause)
    EFFICIENT_CATALYST = "EFFICIENT_CATALYST"  # Enzyme / operator directing transformation (efficient cause)
    METABOLIC_OUTPUT = "METABOLIC_OUTPUT"      # Product molecule or repair component
    DISSIPATIVE_WASTE = "DISSIPATIVE_WASTE"    # Entropy export / waste heat


class ClosureVerdictStatus(str, enum.Enum):
    AUTOPOIETIC_CLOSURE_VERIFIED = "AUTOPOIETIC_CLOSURE_VERIFIED"
    CAUSAL_LEAK_UNPRODUCED_CATALYST = "CAUSAL_LEAK_UNPRODUCED_CATALYST"
    TAUTOLOGICAL_CIRCULAR_COLLAPSE = "TAUTOLOGICAL_CIRCULAR_COLLAPSE"
    EQUILIBRIUM_DEATH_NO_DISSIPATION = "EQUILIBRIUM_DEATH_NO_DISSIPATION"
    PURE_MECHANICAL_LINEAR_DAG = "PURE_MECHANICAL_LINEAR_DAG"


@dataclass
class MetabolicComponent:
    """A biochemical species or catalytic macromolecule in the (M,R) system."""
    component_id: str
    name: str
    is_external_nutrient: bool = False
    is_dissipated_waste: bool = False
    molecular_mass_da: float = 100.0


@dataclass
class CatalyticProcess:
    """
    A biological process with explicit material inputs, products, and efficient catalysts:
    material_inputs --[ efficient_catalyst ]--> material_products + waste
    """
    process_id: str
    name: str
    material_inputs: List[str]
    efficient_catalysts: List[str]  # Efficient causes
    material_products: List[str]
    entropy_production_rate: float = 0.05  # sigma_ent > 0 (Prigogine non-equilibrium)


@dataclass
class AutopoieticSystemSpec:
    """
    Specification of a candidate relational biological system (M,R).
    """
    system_id: str
    system_name: str
    components: Dict[str, MetabolicComponent]
    processes: List[CatalyticProcess]


@dataclass
class AutopoieticClosureAuditReport:
    """Audit report for Rosen (M,R) causal closure and non-equilibrium dissipation."""
    system_id: str
    verdict: ClosureVerdictStatus
    is_closed_to_efficient_causation: bool
    is_thermodynamically_dissipative: bool
    total_catalysts_audited: int
    internally_produced_catalysts: List[str]
    unaccounted_external_catalysts: List[str]
    mean_entropy_production_rate: float
    holonomy_defect: float
    rationale: str
    som_autopoietic_hash: str

    def to_dict(self) -> Dict[str, Any]:
        return {
            "system_id": self.system_id,
            "verdict": self.verdict.value,
            "is_closed_to_efficient_causation": self.is_closed_to_efficient_causation,
            "is_thermodynamically_dissipative": self.is_thermodynamically_dissipative,
            "total_catalysts_audited": self.total_catalysts_audited,
            "internally_produced_catalysts": self.internally_produced_catalysts,
            "unaccounted_external_catalysts": self.unaccounted_external_catalysts,
            "mean_entropy_production_rate": round(self.mean_entropy_production_rate, 4),
            "holonomy_defect": round(self.holonomy_defect, 6),
            "rationale": self.rationale,
            "som_autopoietic_hash": self.som_autopoietic_hash,
        }


class RosenAutopoieticClosureAuditor:
    """
    Categorical Epistemic Court evaluating Biological Organization and Causal Closure.
    Audits candidate biological systems for:
    1. Closure to Efficient Causation (Rosen's (M,R)-theorem).
    2. Prevention of Tautological Triviality (requires thermodynamic throughput).
    3. Non-Equilibrium Dissipative Viability.
    """

    @classmethod
    def audit_system(cls, spec: AutopoieticSystemSpec) -> AutopoieticClosureAuditReport:
        # 1. Collect all declared catalysts (efficient causes)
        all_catalysts: Set[str] = set()
        for p in spec.processes:
            for cat in p.efficient_catalysts:
                all_catalysts.add(cat)

        # 2. Collect all produced species across all processes
        all_products: Set[str] = set()
        entropy_rates: List[float] = []
        for p in spec.processes:
            for prod in p.material_products:
                all_products.add(prod)
            entropy_rates.append(p.entropy_production_rate)

        mean_entropy = float(np.mean(entropy_rates)) if entropy_rates else 0.0

        # Check for non-equilibrium dissipation (sigma_ent > 0)
        is_dissipative = mean_entropy > 0.0

        # 3. Assess Closure to Efficient Causation:
        # Every catalyst must be internally produced by at least one process
        internally_produced = sorted(list(all_catalysts.intersection(all_products)))
        unaccounted_catalysts = sorted(list(all_catalysts.difference(all_products)))

        # 4. Check for Trivial Tautological Collapse (e.g. no nutrient inputs or no products)
        has_nutrients = any(c.is_external_nutrient for c in spec.components.values())
        has_waste = any(c.is_dissipated_waste for c in spec.components.values())

        # Categorical holonomy check: build a transition matrix of efficient causation
        n_cats = max(1, len(all_catalysts))
        closure_ratio = len(internally_produced) / n_cats
        # Holonomy defect measures distance from perfect algebraic closure
        holonomy_defect = abs(1.0 - closure_ratio)

        if not is_dissipative:
            verdict = ClosureVerdictStatus.EQUILIBRIUM_DEATH_NO_DISSIPATION
            rationale = "Thermodynamic failure: Zero or negative entropy production rate. System is at dead equilibrium."
            is_closed = False
        elif len(all_catalysts) == 0:
            verdict = ClosureVerdictStatus.PURE_MECHANICAL_LINEAR_DAG
            rationale = "System lacks efficient causation catalysis. Operates as a purely linear non-living mechanical transformation."
            is_closed = False
        elif not has_nutrients and closure_ratio == 1.0:
            verdict = ClosureVerdictStatus.TAUTOLOGICAL_CIRCULAR_COLLAPSE
            rationale = "Tautological loop detected: Closed cycle without open material/energy throughput (violates thermodynamic open-boundary law)."
            is_closed = False
        elif unaccounted_catalysts:
            verdict = ClosureVerdictStatus.CAUSAL_LEAK_UNPRODUCED_CATALYST
            rationale = f"Causal open leak: {len(unaccounted_catalysts)} catalysts ({', '.join(unaccounted_catalysts)}) lack internal synthesis mappings."
            is_closed = False
        else:
            verdict = ClosureVerdictStatus.AUTOPOIETIC_CLOSURE_VERIFIED
            rationale = "System is strictly closed to efficient causation and open to thermodynamic flux. Valid autopoietic (M,R)-organization."
            is_closed = True

        # Compute Merkle seal
        payload = f"{spec.system_id}:{verdict.value}:{is_closed}:{closure_ratio}:{mean_entropy}"
        som_hash = f"sha256:{hashlib.sha256(payload.encode('utf-8')).hexdigest()}"

        # Register audit event into canonical ScientificLedger
        ledger = ScientificLedger(ledger_id="autopoietic-closure-ledger")
        ledger.record_epistemic_verdict(
            artifact_id=spec.system_id,
            verdict_type="ROSEN_AUTOPOIETIC_CLOSURE_AUDIT",
            status="SOUND" if is_closed else "REFUTED",
            som_merkle_hash=som_hash,
            details={
                "system_id": spec.system_id,
                "closure_ratio": closure_ratio,
                "unaccounted_catalysts": unaccounted_catalysts,
                "rationale": rationale,
            },
            author="RosenAutopoieticClosureAuditor",
        )

        return AutopoieticClosureAuditReport(
            system_id=spec.system_id,
            verdict=verdict,
            is_closed_to_efficient_causation=is_closed,
            is_thermodynamically_dissipative=is_dissipative,
            total_catalysts_audited=len(all_catalysts),
            internally_produced_catalysts=internally_produced,
            unaccounted_external_catalysts=unaccounted_catalysts,
            mean_entropy_production_rate=mean_entropy,
            holonomy_defect=holonomy_defect,
            rationale=rationale,
            som_autopoietic_hash=som_hash,
        )
