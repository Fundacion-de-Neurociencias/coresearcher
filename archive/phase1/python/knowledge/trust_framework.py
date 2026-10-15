"""
Claim Trust Framework - Sprint 10
Scientific reputation system for claims.
"""

from __future__ import annotations

from typing import Optional
from datetime import datetime

# Security tier: PRIVATE — DO NOT MODIFY
# See python/_tiers.py for classification
SECURITY_TIER = "PRIVATE"



class TrustScore:
    """
    Trust scores for scientific claims.
    
    Similar to PageRank/GitHub Stars but for knowledge.
    """
    
    def __init__(self, claim_id: str):
        self.claim_id = claim_id
        self.support_score: float = 0.0  # Based on supporting papers
        self.contradiction_score: float = 0.0  # Based on contradicting papers
        self.recency_score: float = 0.0  # Based on publication dates
        self.reproducibility_score: float = 0.0  # Based on replications
        self.evidence_score: float = 0.0  # Quality of supporting evidence
        self.community_score: float = 0.0  # Community validation
        self.last_updated: str = datetime.now().isoformat()
    
    def calculate_trust_index(self) -> int:
        """
        Calculate overall trust index (0-100).
        
        Formula: weighted combination of all scores
        """
        # Weights (should be refined over time)
        w_support = 0.30
        w_contradiction = 0.20  # Inverse weighted
        w_recency = 0.15
        w_reproducibility = 0.20
        w_evidence = 0.10
        w_community = 0.05
        
        # Normalize contradiction (inverse)
        contradiction_penalty = (1.0 - self.contradiction_score)
        
        trust = (
            w_support * self.support_score +
            w_contradiction * contradiction_penalty +
            w_recency * self.recency_score +
            w_reproducibility * self.reproducibility_score +
            w_evidence * self.evidence_score +
            w_community * self.community_score
        )
        
        return int(trust * 100)
    
    def to_dict(self) -> dict:
        """Export as dictionary."""
        return {
            "claim_id": self.claim_id,
            "trust_index": self.calculate_trust_index(),
            "breakdown": {
                "support": self.support_score,
                "contradictions": self.contradiction_score,
                "recency": self.recency_score,
                "reproducibility": self.reproducibility_score,
                "evidence": self.evidence_score,
                "community": self.community_score,
            },
            "last_updated": self.last_updated,
        }


class ClaimTrustFramework:
    """
    Framework for calculating and managing trust scores.
    """
    
    def __init__(self):
        self._scores: dict = {}
    
    def get_or_create(self, claim_id: str) -> TrustScore:
        """Get existing or create new trust score."""
        if claim_id not in self._scores:
            self._scores[claim_id] = TrustScore(claim_id)
        return self._scores[claim_id]
    
    def update_support(self, claim_id: str, paper_count: int, avg_quality: float = 0.5):
        """Update support score based on papers."""
        score = self.get_or_create(claim_id)
        # More papers = higher score, capped at 1.0
        score.support_score = min(1.0, paper_count / 50.0)
        score.evidence_score = avg_quality
        score.last_updated = datetime.now().isoformat()
    
    def update_contradictions(self, claim_id: str, contradiction_count: int, total_papers: int = 100):
        """Update contradiction score (penalty)."""
        score = self.get_or_create(claim_id)
        # Proportion of contradicting papers
        score.contradiction_score = min(1.0, contradiction_count / total_papers)
        score.last_updated = datetime.now().isoformat()
    
    def update_recency(self, claim_id: str, age_days: int):
        """Update recency score (newer = better)."""
        score = self.get_or_create(claim_id)
        # Decay: newer = higher score
        # 0 days = 1.0, 365 days = 0.5, 1825 days = 0.1
        if age_days < 30:
            score.recency_score = 1.0
        elif age_days < 365:
            score.recency_score = 0.8
        elif age_days < 730:
            score.recency_score = 0.6
        elif age_days < 1825:
            score.recency_score = 0.3
        else:
            score.recency_score = 0.1
        score.last_updated = datetime.now().isoformat()
    
    def update_reproducibility(self, claim_id: str, replication_count: int, total_attempts: int = 100):
        """Update reproducibility score."""
        score = self.get_or_create(claim_id)
        if total_attempts > 0:
            score.reproducibility_score = min(1.0, replication_count / total_attempts)
        score.last_updated = datetime.now().isoformat()
    
    def get_trust_report(self, claim_id: str) -> dict:
        """Get complete trust report for a claim."""
        score = self.get_or_create(claim_id)
        return score.to_dict()


# =============================================================================
# Knowledge Hierarchy
# =============================================================================

class KnowledgeHierarchy:
    """
    The epistemic hierarchy of scientific knowledge.
    """
    
    LEVELS = [
        "Observation",      # Raw data point
        "Evidence",         # Structured support
        "Claim",            # Assertion with evidence
        "SupportedClaim",   # Claim with strong evidence
        "ConsensusClaim",   # Community-agreed claim
        "Theory",           # Explanatory framework
    ]
    
    @staticmethod
    def next_level(current: str) -> Optional[str]:
        """Get next level in hierarchy."""
        try:
            idx = KnowledgeHierarchy.LEVELS.index(current)
            return KnowledgeHierarchy.LEVELS[idx + 1] if idx + 1 < len(KnowledgeHierarchy.LEVELS) else None
        except ValueError:
            return None
    
    @staticmethod
    def level_requirements(level: str) -> dict:
        """Get requirements to reach a knowledge level."""
        requirements = {
            "SupportedClaim": {
                "min_evidence_score": 0.7,
                "min_support_papers": 10,
                "max_contradiction_rate": 0.1,
            },
            "ConsensusClaim": {
                "min_evidence_score": 0.8,
                "min_support_papers": 25,
                "max_contradiction_rate": 0.05,
                "min_community_reviews": 5,
                "min_trust_index": 80,
            },
            "Theory": {
                "min_evidence_score": 0.85,
                "min_support_papers": 50,
                "max_contradiction_rate": 0.02,
                "min_trust_index": 90,
                "explains_multiple_claims": True,
            },
        }
        return requirements.get(level, {})


if __name__ == "__main__":
    print("=" * 70)
    print("Claim Trust Framework")
    print("=" * 70)
    
    framework = ClaimTrustFramework()
    
    # Simulate trust calculation for pTau217 claim
    framework.update_support("CLAIM-000001", paper_count=38, avg_quality=0.89)
    framework.update_contradictions("CLAIM-000001", contradiction_count=2, total_papers=100)
    framework.update_recency("CLAIM-000001", age_days=180)
    framework.update_reproducibility("CLAIM-000001", replication_count=15)
    
    report = framework.get_trust_report("CLAIM-000001")
    
    print(f"\nClaim: CLAIM-000001")
    print(f"Trust Index: {report['trust_index']}/100")
    print("\nBreakdown:")
    for key, value in report['breakdown'].items():
        print(f"  {key}: {value:.2f}")
    
    print("\n" + "=" * 70)
    print("Knowledge Hierarchy")
    print("=" * 70)
    
    for level in KnowledgeHierarchy.LEVELS:
        reqs = KnowledgeHierarchy.level_requirements(level)
        if reqs:
            print(f"\n{level}:")
            for req, val in reqs.items():
                print(f"  {req}: {val}")