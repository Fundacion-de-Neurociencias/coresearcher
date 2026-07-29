"""
Cross Domain Transfer - Einstein Generator Module 4 (Sprint 21)
Transfers concepts between scientific domains.

Einstein was a master at taking ideas from one domain to another:
- Thermodynamics to Brownian motion
- Electromagnetism to optics
- Statistical mechanics to quantum theory
"""

from __future__ import annotations
from typing import List, Dict, Optional
import sys
sys.path.insert(0, str(__file__.rsplit('/', 2)[0]))

from knowledge.anomaly_registry import AnomalyRegistry
from knowledge.finding_registry import FindingRegistry
from knowledge.claim_registry import ClaimRegistry

# Security tier: PRIVATE — DO NOT MODIFY
# See python/_tiers.py for classification
SECURITY_TIER = "PRIVATE"



class CrossDomainTransfer:
    """
    Explores conceptual transfers between domains.
    
    The ecosistema has multiple domain packs:
    - GeneForge (genomics)
    - Medicalia (medicine)
    - Neurodiagnoses (neuroscience)
    - Vademecum (drug interactions)
    - EditXT (CRISPR editing)
    
    Einstein patterns:
    1. Take mechanism A from domain X, apply to B in domain Y
    2. Take principle P from theory X, test in domain Y
    3. Take boundary condition from X, explore in Y
    """
    
    # Domain packs in the ecosystem
    DOMAIN_PACKS = [
        "geneforge", "medicalia", "neurodiagnoses",
        "vademecum", "editxt", "oncolia", "metabolica"
    ]
    
    def __init__(self):
        self.anomalies = AnomalyRegistry()
        self.findings = FindingRegistry()
        self.claims = ClaimRegistry()

    def get_domain_concepts(self, domain: str) -> List[Dict]:
        """Get all concepts (findings/claims) from a domain."""
        concepts = []
        claims = [c for c in self.claims.list() if c.get("domain", "").lower() == domain.lower()]
        findings = [f for f in self.findings.list() if f.get("domain", "").lower() == domain.lower()]
        concepts.extend(claims)
        concepts.extend(findings)
        return concepts

    def find_transfer_opportunities(self) -> List[Dict]:
        """
        Find opportunities to transfer concepts between domains.
        
        Example:
        - GeneForge has: CRISPR efficiency principles
        - Neurodiagnoses has: Protein aggregation in neurons
        - Transfer: Could CRISPR editing principles apply to understanding aggregation?
        """
        anomalies_found = []
        
        # Sample transfers based on known domain patterns
        transfer_patterns = [
            {
                "source_domain": "geneforge",
                "target_domain": "neurodiagnoses",
                "source_concept": "CRISPR efficiency correlates with guide RNA structure",
                "target_question": "Does protein aggregation correlate with sequence/structure patterns?",
                "entity": "tau_aggregation",
            },
            {
                "source_domain": "vademecum",
                "target_domain": "neurodiagnoses",
                "source_concept": "Drug-drug interactions create emergent effects",
                "target_question": "Do biomarker interactions create emergent diagnostic signals?",
                "entity": "biomarker_panel",
            },
            {
                "source_domain": "editxt",
                "target_domain": "neurodiagnoses",
                "source_concept": "Off-target effects reveal system constraints",
                "target_question": "What are the off-target effects of pathological processes?",
                "entity": "neuroinflammation",
            },
        ]
        
        for pattern in transfer_patterns:
            anomaly_id = self.anomalies.register(
                anomaly_type="cross_domain",
                entity=pattern["entity"],
                description=f"Transfer: {pattern['source_domain']} concept '{pattern['source_concept'][:40]}...' -> {pattern['target_domain']}",
                domain=pattern["target_domain"],
                severity=0.75,
                metadata={
                    "source_domain": pattern["source_domain"],
                    "target_domain": pattern["target_domain"],
                    "source_concept": pattern["source_concept"],
                    "target_question": pattern["target_question"],
                }
            )
            anomalies_found.append(self.anomalies.get(anomaly_id))
        
        return anomalies_found

    def find_analogy_gaps(self) -> List[Dict]:
        """
        Find where analogous mechanisms in different domains might exist.
        """
        anomalies_found = []
        
        # Look for similar patterns across domains
        analogies = [
            ("protein_folding", "protein_misfolding diseases"),
            ("network_resilience", "biological_network robustness"),
            ("phase_transitions", "cellular_state transitions"),
        ]
        
        for src, tgt in analogies:
            anomaly_id = self.anomalies.register(
                anomaly_type="analogy_gap",
                entity=src,
                description=f"Analogy opportunity: {src} -> {tgt}",
                domain="cross_domain",
                severity=0.65,
                metadata={"source_analogy": src, "target_context": tgt}
            )
            anomalies_found.append(self.anomalies.get(anomaly_id))
        
        return anomalies_found

    def run_all(self) -> List[Dict]:
        """Run all cross-domain transfer detection methods."""
        all_anomalies = []
        all_anomalies.extend(self.find_transfer_opportunities())
        all_anomalies.extend(self.find_analogy_gaps())
        return all_anomalies


if __name__ == "__main__":
    transfer = CrossDomainTransfer()
    found = transfer.run_all()
    print(f"Found {len(found)} cross-domain anomalies")