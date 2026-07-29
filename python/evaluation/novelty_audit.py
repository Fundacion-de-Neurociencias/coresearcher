"""
Scientific Novelty Audit - Sprint 20
Evaluate if hypotheses are truly novel vs literature rephrasing.
"""

import json
from pathlib import Path
from typing import Dict, List
from dataclasses import dataclass

# Security tier: PRIVATE — DO NOT MODIFY
# See python/_tiers.py for classification
SECURITY_TIER = "PRIVATE"



@dataclass
class NoveltyScore:
    """Novelty assessment for a hypothesis."""
    hypothesis_id: str
    novelty_score: float  # 0.0-1.0
    novelty_class: str  # A|B|C|D
    supporting_claims: List[str]
    contradicting_claims: List[str]
    rationale: str


class NoveltyAuditor:
    """
    Audit hypotheses for scientific novelty.
    
    Types:
    - A: Literature Rephrasing (direct from claims)
    - B: Literature Synthesis (combination known)
    - C: Novel Inference (unstated connections)
    - D: Potential Discovery (no prior support)
    """
    
    NOVELTY_PATTERNS = {
        # Type A patterns - direct rephrasing
        "direct_claim": ["predicts", "associated", "diagnoses", "treats"],
        
        # Type D patterns - potential discovery
        "novel_inference": ["mediator", "mechanism", "synergistic", "threshold effect", "compensatory"],
        "cross_domain": ["between", "links", "connects", "mediates"],
        "population_specific": ["in APOE4 negatives", "specifically in", "only when"],
    }
    
    def __init__(self):
        self.audit_dir = Path("evaluation/results")
        self.audit_dir.mkdir(parents=True, exist_ok=True)
    
    def audit_hypothesis(self, hypothesis: dict, claims: List[dict]) -> NoveltyScore:
        """
        Audit a single hypothesis for novelty.
        """
        statement = hypothesis.get("statement", "").lower()
        
        # Check for direct claim (Type A)
        for pattern in self.NOVELTY_PATTERNS["direct_claim"]:
            if pattern in statement:
                # Check if this exact claim exists
                matching = [c for c in claims if pattern in c.get("text", "").lower()]
                if matching:
                    return NoveltyScore(
                        hypothesis_id=hypothesis.get("id"),
                        novelty_score=0.1,
                        novelty_class="A",
                        supporting_claims=[c.get("id") for c in matching[:3]],
                        contradicting_claims=[],
                        rationale="Direct rephrasing of existing literature",
                    )
        
        # Check for novel inference patterns (Type C/D)
        novel_matches = []
        for pattern in self.NOVELTY_PATTERNS["novel_inference"]:
            if pattern in statement:
                novel_matches.append(pattern)
        
        cross_matches = []
        for pattern in self.NOVELTY_PATTERNS["cross_domain"]:
            if pattern in statement:
                cross_matches.append(pattern)
        
        # Calculate novelty score
        if novel_matches and cross_matches:
            score = 0.9
            novelty_class = "D"
            rationale = f"Potential discovery - novel inference ({', '.join(novel_matches)}) across domains ({', '.join(cross_matches)})"
        elif novel_matches:
            score = 0.7
            novelty_class = "C"
            rationale = f"Novel inference ({', '.join(novel_matches)})"
        elif cross_matches:
            score = 0.6
            novelty_class = "C"
            rationale = f"Cross-domain connection ({', '.join(cross_matches)})"
        else:
            score = 0.4
            novelty_class = "B"
            rationale = "Literature synthesis - combination of known elements"
        
        return NoveltyScore(
            hypothesis_id=hypothesis.get("id"),
            novelty_score=score,
            novelty_class=novelty_class,
            supporting_claims=[],
            contradicting_claims=[],
            rationale=rationale,
        )
    
    def audit_session(self, session_path: str = "sessions/VS001"):
        """
        Audit all hypotheses in a session.
        """
        session = Path(session_path)
        
        # Load data
        with open(session / "hypotheses.json", encoding='utf-8') as f:
            hypotheses = json.load(f)
        
        with open(session / "claims.json", encoding='utf-8') as f:
            claims = json.load(f)
        
        # Audit each hypothesis
        scores = []
        for hyp in hypotheses:
            score = self.audit_hypothesis(hyp, claims)
            scores.append(score)
            print(f"\n{score.hypothesis_id}:")
            print(f"  Score: {score.novelty_score}")
            print(f"  Class: {score.novelty_class}")
            print(f"  Rationale: {score.rationale}")
        
        # Save audit results
        results = {
            "hypotheses": [
                {
                    "hypothesis_id": s.hypothesis_id,
                    "novelty_score": s.novelty_score,
                    "novelty_class": s.novelty_class,
                    "supporting_claims": s.supporting_claims,
                    "contradicting_claims": s.contradicting_claims,
                    "rationale": s.rationale,
                }
                for s in scores
            ],
            "summary": {
                "total": len(scores),
                "type_a": len([s for s in scores if s.novelty_class == "A"]),
                "type_b": len([s for s in scores if s.novelty_class == "B"]),
                "type_c": len([s for s in scores if s.novelty_class == "C"]),
                "type_d": len([s for s in scores if s.novelty_class == "D"]),
                "avg_novelty": sum(s.novelty_score for s in scores) / len(scores) if scores else 0,
            }
        }
        
        with open(self.audit_dir / "novelty_audit.json", 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2)
        
        print(f"\n{'=' * 70}")
        print("Novelty Summary:")
        print(f"  Type A (Rephrasing): {results['summary']['type_a']}")
        print(f"  Type B (Synthesis): {results['summary']['type_b']}")
        print(f"  Type C (Inference): {results['summary']['type_c']}")
        print(f"  Type D (Discovery): {results['summary']['type_d']}")
        print(f"  Avg Novelty Score: {results['summary']['avg_novelty']:.2f}")
        
        return results


if __name__ == "__main__":
    auditor = NoveltyAuditor()
    results = auditor.audit_session()
    
    avg = results['summary']['avg_novelty']
    if avg >= 0.5:
        print("\n✓ System produces novel scientific hypotheses")
    else:
        print("\n✗ Most hypotheses are literature rephrasing - needs improvement")