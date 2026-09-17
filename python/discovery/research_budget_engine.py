"""
python/discovery/research_budget_engine.py - Research Budget & Resource Allocation Engine
Enforces strict economic scarcity across scientific discovery campaigns:
1. Compute Tokens (GPU/LLM reasoning quota)
2. Patient/Cohort Samples (Clinical subject access limit N)
3. Laboratory Reagent Cost (Physical assay budget in €/$)
4. Execution Time (Wall-clock and timeline constraints)
"""

from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional, Tuple
import uuid



@dataclass
class ResourceAllocationCost:
    compute_tokens_cost: int
    cohort_samples_requested: int
    wet_lab_assay_euro_cost: float
    time_units_required: int  # Hours / Days

    def to_dict(self) -> Dict[str, Any]:
        return {
            "compute_tokens_cost": self.compute_tokens_cost,
            "cohort_samples_requested": self.cohort_samples_requested,
            "wet_lab_assay_euro_cost": self.wet_lab_assay_euro_cost,
            "time_units_required": self.time_units_required
        }


@dataclass
class ResearchBudgetLedger:
    campaign_id: str
    total_compute_tokens: int = 500_000
    consumed_compute_tokens: int = 0
    total_patient_samples_quota: int = 250
    consumed_patient_samples: int = 0
    total_wet_lab_budget_euros: float = 15_000.0
    consumed_wet_lab_euros: float = 0.0
    total_time_units_hours: int = 168  # 1 Week campaign
    consumed_time_units_hours: int = 0

    @property
    def remaining_compute_tokens(self) -> int:
        return max(0, self.total_compute_tokens - self.consumed_compute_tokens)

    @property
    def remaining_patient_samples(self) -> int:
        return max(0, self.total_patient_samples_quota - self.consumed_patient_samples)

    @property
    def remaining_wet_lab_euros(self) -> float:
        return max(0.0, self.total_wet_lab_budget_euros - self.consumed_wet_lab_euros)

    @property
    def is_bankrupt(self) -> bool:
        return (
            self.remaining_compute_tokens <= 0 or
            self.remaining_patient_samples <= 0 or
            self.remaining_wet_lab_euros <= 0 or
            self.consumed_time_units_hours >= self.total_time_units_hours
        )

    def can_afford(self, cost: ResourceAllocationCost) -> Tuple[bool, str]:
        if cost.compute_tokens_cost > self.remaining_compute_tokens:
            return False, f"Insufficient compute tokens: requested {cost.compute_tokens_cost}, remaining {self.remaining_compute_tokens}"
        if cost.cohort_samples_requested > self.remaining_patient_samples:
            return False, f"Insufficient cohort samples quota: requested {cost.cohort_samples_requested}, remaining {self.remaining_patient_samples}"
        if cost.wet_lab_assay_euro_cost > self.remaining_wet_lab_euros:
            return False, f"Insufficient wet-lab budget: requested €{cost.wet_lab_assay_euro_cost:.2f}, remaining €{self.remaining_wet_lab_euros:.2f}"
        return True, "Budget verified"

    def charge(self, cost: ResourceAllocationCost) -> None:
        self.consumed_compute_tokens += cost.compute_tokens_cost
        self.consumed_patient_samples += cost.cohort_samples_requested
        self.consumed_wet_lab_euros += cost.wet_lab_assay_euro_cost
        self.consumed_time_units_hours += cost.time_units_required

    def to_dict(self) -> Dict[str, Any]:
        return {
            "campaign_id": self.campaign_id,
            "compute": {
                "total": self.total_compute_tokens,
                "consumed": self.consumed_compute_tokens,
                "remaining": self.remaining_compute_tokens,
                "utilization_pct": round((self.consumed_compute_tokens / self.total_compute_tokens) * 100, 1)
            },
            "patient_samples": {
                "total": self.total_patient_samples_quota,
                "consumed": self.consumed_patient_samples,
                "remaining": self.remaining_patient_samples,
                "utilization_pct": round((self.consumed_patient_samples / self.total_patient_samples_quota) * 100, 1)
            },
            "wet_lab_euros": {
                "total": self.total_wet_lab_budget_euros,
                "consumed": self.consumed_wet_lab_euros,
                "remaining": self.remaining_wet_lab_euros,
                "utilization_pct": round((self.consumed_wet_lab_euros / self.total_wet_lab_budget_euros) * 100, 1)
            },
            "time_hours": {
                "total": self.total_time_units_hours,
                "consumed": self.consumed_time_units_hours,
                "remaining": max(0, self.total_time_units_hours - self.consumed_time_units_hours)
            },
            "is_bankrupt": self.is_bankrupt
        }

