"""
python/discovery/state_space.py - Explicit Scientific State Space (Ω) & Volume Exclusion Engine
Models discrete/discretized continuous states and computes exact combinatorial state space
reductions to mathematically derive Constraint Discovery Value (CDV).
"""

from dataclasses import dataclass, field
from typing import List, Dict, Any, Tuple, Set
import itertools


@dataclass
class StateSpaceAxis:
    name: str
    description: str
    domain_values: List[str]

    @property
    def cardinality(self) -> int:
        return len(self.domain_values)


@dataclass
class StateSpaceOmega:
    """
    The complete state space Ω of the system.
    A state ω ∈ Ω is a full tuple of coordinates across all physical/biological axes.
    """
    domain_name: str
    axes: List[StateSpaceAxis] = field(default_factory=list)

    @classmethod
    def create_canonical_neurodegen_space(cls) -> "StateSpaceOmega":
        """
        Builds the canonical preclinical neurodegeneration state space Ω.
        Axes:
        1. Amyloid: [A-, A+] (2)
        2. Tau: [T-, T+] (2)
        3. Neurodegeneration: [N-, N+] (2)
        4. Connectome Hub Strength: [Low (<0.30), Medium (0.30-0.65), High (>0.65)] (3)
        5. Neuroinflammation: [Normal, Reactive_GFAP_NfL] (2)
        6. 36-Month Clinical Transition: [Stable_MCI, Accelerated_Dementia] (2)
        
        Total Combinatorial States |Ω| = 2 * 2 * 2 * 3 * 2 * 2 = 96 states.
        """
        return cls(
            domain_name="Preclinical-to-Dementia Continuum",
            axes=[
                StateSpaceAxis("Amyloid_Status", "Cortical amyloid deposition (A)", ["A-", "A+"]),
                StateSpaceAxis("Tau_Status", "Plasma/PET tau phosphorylation (T)", ["T-", "T+"]),
                StateSpaceAxis("Neurodegeneration_Status", "Structural cortical atrophy (N)", ["N-", "N+"]),
                StateSpaceAxis("Connectome_Hub_Strength", "Functional hub nodal strength (H)", ["Low (<0.30)", "Medium (0.30-0.65)", "High (>0.65)"]),
                StateSpaceAxis("Neuroinflammation", "Reactive astrogliosis/neuroaxonal damage (I)", ["Normal", "Reactive"]),
                StateSpaceAxis("Clinical_36m_Outcome", "Longitudinal cognitive transition (C)", ["Stable_MCI", "Accelerated_Dementia"])
            ]
        )

    @property
    def total_volume(self) -> int:
        """Calculates total combinatorial volume |Ω| = ∏ |Axis_i|."""
        vol = 1
        for ax in self.axes:
            vol *= ax.cardinality
        return vol

    def enumerate_all_states(self) -> List[Dict[str, str]]:
        axis_names = [ax.name for ax in self.axes]
        domains = [ax.domain_values for ax in self.axes]
        states = []
        for combo in itertools.product(*domains):
            states.append(dict(zip(axis_names, combo)))
        return states

    def evaluate_constraint_exclusion(self, constraint_rule_fn) -> Dict[str, Any]:
        """
        Applies an invariant biological rule predicate to every state ω ∈ Ω.
        States that violate the rule are EXCLUDED (forbidden in nature).
        """
        all_states = self.enumerate_all_states()
        total_count = len(all_states)
        permitted_states = []
        excluded_states = []

        for state in all_states:
            if constraint_rule_fn(state):
                permitted_states.append(state)
            else:
                excluded_states.append(state)

        excluded_count = len(excluded_states)
        permitted_count = len(permitted_states)
        exclusion_fraction = round(excluded_count / total_count, 4)

        return {
            "total_state_space_volume": total_count,
            "permitted_volume": permitted_count,
            "excluded_volume": excluded_count,
            "exclusion_fraction": exclusion_fraction,
            "mathematical_cdv": exclusion_fraction,
            "formula": f"CDV = |Ω_excluded| / |Ω_total| = {excluded_count} / {total_count} = {exclusion_fraction}"
        }
