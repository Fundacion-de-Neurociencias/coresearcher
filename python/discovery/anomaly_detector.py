"""
Anomaly Detector - Einstein Generator Module 1 (Sprint 21)
Detects scientific anomalies from claim patterns.
"""

from __future__ import annotations
from typing import List, Dict, Optional
import sys
sys.path.insert(0, str(__file__.rsplit('/', 2)[0]))

from knowledge.anomaly_registry import AnomalyRegistry
from knowledge.claim_registry import ClaimRegistry

# Security tier: PRIVATE — DO NOT MODIFY
# See python/_tiers.py for classification
SECURITY_TIER = "PRIVATE"



class AnomalyDetector:
    """
    Detects anomalies by finding trust gaps and unexpected patterns.
    
    Patterns detected:
    1. Trust Gap: High trust claim + Low trust claim on same entity
    2. Statistical Outlier: Extreme values in meta-analysis
    3. Unexpected Correlation: Correlation found where none expected
    4. Temporal Anomaly: Trends changing over time
    """
    
    TRUST_GAP_THRESHOLD = 0.3  # Minimum gap to consider anomaly

    def __init__(self):
        self.anomalies = AnomalyRegistry()
        self.claims = ClaimRegistry()

    def detect_trust_gaps(self, entity: str = None) -> List[Dict]:
        """
        Find high-trust + low-trust claims about same entity.
        
        This is the core anomaly pattern:
        When same entity has conflicting trust levels, something interesting is happening.
        """
        claims = self.claims.list()
        high_trust = [c for c in claims if c.get("evidenceScore", 0) >= 0.7]
        low_trust = [c for c in claims if c.get("evidenceScore", 1) < 0.4]
        
        anomalies_found = []
        
        # Group by entities
        for high in high_trust:
            high_entities = set(high.get("entities", []))
            for low in low_trust:
                low_entities = set(low.get("entities", []))
                
                # Check overlap
                overlap = high_entities & low_entities
                if overlap or (entity and any(e.lower() == entity.lower() for e in high_entities | low_entities)):
                    trust_gap = high.get("evidenceScore", 0) - low.get("evidenceScore", 0)
                    
                    if trust_gap >= self.TRUST_GAP_THRESHOLD:
                        # Register anomaly
                        anomaly_id = self.anomalies.register(
                            anomaly_type="trust_gap",
                            entity=overlap.pop() if overlap else high_entities.pop(),
                            description=f"Trust gap detected: {high.get('text')[:80]}... vs {low.get('text')[:80]}...",
                            high_trust_claim=high.get("id"),
                            low_trust_claim=low.get("id"),
                            trust_gap=trust_gap,
                            domain=high.get("domain"),
                            severity=min(1.0, trust_gap),
                            evidence=[high, low],
                        )
                        anomalies_found.append(self.anomalies.get(anomaly_id))
        
        return anomalies_found

    def detect_statistical_outliers(self) -> List[Dict]:
        """Find claims with extreme effect sizes."""
        claims = self.claims.list()
        anomalies_found = []
        
        for claim in claims:
            metadata = claim.get("metadata", {})
            evidence = metadata.get("extracted_evidence", [])
            
            for ev in evidence:
                if isinstance(ev, dict):
                    val = ev.get("value", "")
                    # Look for extreme effect sizes
                    if "r=" in val or "auc=" in val:
                        try:
                            score = float(val.split("=")[-1].split()[0])
                            if score > 0.9 or score < 0.1:
                                anomaly_id = self.anomalies.register(
                                    anomaly_type="statistical_outlier",
                                    entity=claim.get("entities", ["unknown"])[0],
                                    description=f"Extreme effect size: {val}",
                                    domain=claim.get("domain"),
                                    severity=0.8,
                                )
                                anomalies_found.append(self.anomalies.get(anomaly_id))
                        except ValueError:
                            pass
        
        return anomalies_found

    def run_all(self) -> List[Dict]:
        """Run all anomaly detection methods."""
        all_anomalies = []
        all_anomalies.extend(self.detect_trust_gaps())
        all_anomalies.extend(self.detect_statistical_outliers())
        return all_anomalies


if __name__ == "__main__":
    detector = AnomalyDetector()
    found = detector.run_all()
    print(f"Found {len(found)} anomalies")