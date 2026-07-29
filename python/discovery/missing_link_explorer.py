"""
Missing Link Explorer - Einstein Generator Module 3 (Sprint 21)
Finds gaps in causal and correlational chains.

Detects:
- A -> B, B -> C, but no A -> C
- Known mechanism parts with missing connections
- Pathway gaps in biological processes
"""

from __future__ import annotations
from typing import List, Dict, Set
import sys
sys.path.insert(0, str(__file__.rsplit('/', 2)[0]))

from knowledge.anomaly_registry import AnomalyRegistry
from knowledge.finding_registry import FindingRegistry

# Security tier: PRIVATE — DO NOT MODIFY
# See python/_tiers.py for classification
SECURITY_TIER = "PRIVATE"



class MissingLinkExplorer:
    """
    Explores for missing connections in knowledge graphs.
    
    Patterns:
    1. Transitivity gap: A->B, B->C implies A->C missing
    2. Mechanism gap: Pathway steps missing
    3. Mediator gap: Unknown intermediate variables
    """
    
    def __init__(self):
        self.anomalies = AnomalyRegistry()
        self.findings = FindingRegistry()

    def build_entity_graph(self) -> Dict[str, Set[str]]:
        """Build a directed graph of entity relationships."""
        findings = self.findings.list()
        graph = {}
        
        for finding in findings:
            subject = finding.get("subject", "")
            predicate = finding.get("predicate", "")
            obj = finding.get("object", "")
            
            if subject:
                if subject not in graph:
                    graph[subject] = set()
                if obj:
                    graph[subject].add(obj)
        
        return graph

    def find_transitivity_gaps(self) -> List[Dict]:
        """
        Find A->B, B->C where A->C is missing.
        This is where missing mediators might be.
        """
        graph = self.build_entity_graph()
        anomalies_found = []
        
        for a, connected_b in graph.items():
            for b in connected_b:
                if b in graph:  # B has outgoing connections
                    connected_c = graph[b]
                    for c in connected_c:
                        # Check if A->C exists
                        if c not in connected_b:
                            # Missing link detected!
                            anomaly_id = self.anomalies.register(
                                anomaly_type="missing_link",
                                entity=f"{a}->{c}",
                                description=f"Path A({a})->B({b})->C({c}) exists but A->C missing - potential mediator?",
                                domain="discovered",
                                severity=0.7,
                                evidence=[{"subject": a, "via": b, "object": c}],
                                metadata={"chain": f"{a}->{b}->{c}", "gap_at": f"{a}->{c}"}
                            )
                            anomalies_found.append(self.anomalies.get(anomaly_id))
        
        return anomalies_found

    def find_mediator_gaps(self) -> List[Dict]:
        """
        Find where a relationship exists but no known mediator.
        
        Example: Gene A affects Trait B, but mechanism unknown.
        This could inspire: What is the mediator?
        """
        findings = self.findings.list()
        anomalies_found = []
        
        for finding in findings:
            if finding.get("predicate") in ["predicts", "associated_with", "causes"]:
                # Check if mediator is unknown
                metadata = finding.get("metadata", {})
                if not metadata.get("mechanism_known"):
                    anomaly_id = self.anomalies.register(
                        anomaly_type="mediator_gap",
                        entity=finding.get("subject", "unknown"),
                        description=f"Relationship {finding.get('subject')}->{finding.get('object')} established but mechanism unknown",
                        domain=finding.get("domain"),
                        severity=0.8,
                        evidence=[finding],
                        metadata={"question": "What mediates this relationship?"}
                    )
                    anomalies_found.append(self.anomalies.get(anomaly_id))
        
        return anomalies_found

    def run_all(self) -> List[Dict]:
        """Run all missing link exploration methods."""
        all_anomalies = []
        all_anomalies.extend(self.find_transitivity_gaps())
        all_anomalies.extend(self.find_mediator_gaps())
        return all_anomalies


if __name__ == "__main__":
    explorer = MissingLinkExplorer()
    found = explorer.run_all()
    print(f"Found {len(found)} missing link anomalies")