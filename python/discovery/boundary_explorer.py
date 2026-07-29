"""
Boundary Explorer - Einstein Generator Module 2 (Sprint 21)
Explores the boundaries of scientific knowledge.

Detects:
- "Works in A, but what about B?"
- Population-specific effects
- Context-dependent findings
- Extremes and edge cases
"""

from __future__ import annotations
from typing import List, Dict
import sys
sys.path.insert(0, str(__file__.rsplit('/', 2)[0]))

from knowledge.anomaly_registry import AnomalyRegistry
from knowledge.finding_registry import FindingRegistry

# Security tier: PRIVATE — DO NOT MODIFY
# See python/_tiers.py for classification
SECURITY_TIER = "PRIVATE"



class BoundaryExplorer:
    """
    Explores knowledge boundaries and edge cases.
    
    Patterns:
    1. Population effects: Works in Europeans, what about Africans?
    2. Context boundaries: Works in vitro, what about in vivo?
    3. Temporal boundaries: Short-term effect, what about long-term?
    4. Dose boundaries: Effect at high dose, what about low?
    """
    
    def __init__(self):
        self.anomalies = AnomalyRegistry()
        self.findings = FindingRegistry()

    def find_population_boundaries(self) -> List[Dict]:
        """
        Find findings that may have unexplored population contexts.
        """
        findings = self.findings.list()
        anomalies_found = []
        
        # Known populations in neurodegeneration
        populations = [
            "European ancestry", "African ancestry",
            "Asian populations", "Hispanic populations",
            "preclinical", "MCI", "AD", "ALS", "FTD",
        ]
        
        for finding in findings:
            pop = finding.get("population", "")
            
            # Check if this might not apply to other populations
            if pop and any(p.lower() in pop.lower() for p in ["European", "Caucasian", "general"]):
                anomaly_id = self.anomalies.register(
                    anomaly_type="population_boundary",
                    entity=finding.get("subject", "unknown"),
                    description=f"Finding in {pop} may not generalize to other populations",
                    domain=finding.get("domain"),
                    severity=0.6,
                    evidence=[finding],
                    metadata={"tested_population": pop, "question": f"What about other populations?"}
                )
                anomalies_found.append(self.anomalies.get(anomaly_id))
        
        return anomalies_found

    def find_dose_response_gaps(self) -> List[Dict]:
        """
        Find where dose-response relationships are incomplete.
        """
        findings = self.findings.list()
        anomalies_found = []
        
        for finding in findings:
            effect = finding.get("effect_size")
            if effect and effect > 0.7:  # Strong effect observed
                anomaly_id = self.anomalies.register(
                    anomaly_type="dose_boundary",
                    entity=finding.get("subject", "unknown"),
                    description=f"Strong effect (r={effect}) - what happens at lower doses?",
                    domain=finding.get("domain"),
                    severity=0.5,
                    evidence=[finding],
                    metadata={"question": "What is the minimal effective dose?"}
                )
                anomalies_found.append(self.anomalies.get(anomaly_id))
        
        return anomalies_found

    def find_temporal_gaps(self) -> List[Dict]:
        """
        Find time-boundary anomalies.
        """
        # Look for findings without temporal context
        findings = self.findings.list()
        anomalies_found = []
        
        for finding in findings:
            if not finding.get("metadata", {}).get("long_term_followup"):
                anomaly_id = self.anomalies.register(
                    anomaly_type="temporal_boundary",
                    entity=finding.get("subject", "unknown"),
                    description=f"No long-term data - effect may change over time",
                    domain=finding.get("domain"),
                    severity=0.4,
                    evidence=[finding],
                    metadata={"question": "What happens in 5-10 years?"}
                )
                anomalies_found.append(self.anomalies.get(anomaly_id))
        
        return anomalies_found

    def run_all(self) -> List[Dict]:
        """Run all boundary exploration methods."""
        all_anomalies = []
        all_anomalies.extend(self.find_population_boundaries())
        all_anomalies.extend(self.find_dose_response_gaps())
        all_anomalies.extend(self.find_temporal_gaps())
        return all_anomalies


if __name__ == "__main__":
    explorer = BoundaryExplorer()
    found = explorer.run_all()
    print(f"Found {len(found)} boundary anomalies")