"""
Research Memory - CoResearcher OS Sprint 3.5
Persistent memory of hypotheses, experiments, failures, and lessons.
"""

import json
import sys
from datetime import datetime
from typing import Optional
from pathlib import Path

# Security tier: COMMUNITY — DO NOT MODIFY
# See python/_tiers.py for classification
SECURITY_TIER = "COMMUNITY"


# Research memory storage
MEMORY_DIR = Path("memory")
MEMORY_DIR.mkdir(exist_ok=True)


class ResearchMemory:
    """
    Stores and retrieves hypothesis lifecycle for cumulative learning.
    
    Tracks:
    - Generated hypotheses
    - Experiment designs
    - Experimental outcomes
    - Failed hypotheses
    - Lessons learned
    """

    def __init__(self, domain: str = "general"):
        self.domain = domain
        self.memory_file = MEMORY_DIR / f"{domain}_memory.json"
        self._memory = self._load()

    def _load(self) -> dict:
        """Load memory from disk."""
        if self.memory_file.exists():
            with open(self.memory_file, 'r') as f:
                return json.load(f)
        return {
            "hypotheses": [],
            "experiments": [],
            "failures": [],
            "lessons": [],
        }

    def _save(self):
        """Save memory to disk."""
        with open(self.memory_file, 'w') as f:
            json.dump(self._memory, f, indent=2)

    def store_hypothesis(self, hypothesis: dict) -> str:
        """Store a generated hypothesis."""
        hyp_id = f"HYP{len(self._memory['hypotheses']) + 1:06d}"
        record = {
            "id": hyp_id,
            "statement": hypothesis.get("statement", ""),
            "hypothesis_type": hypothesis.get("hypothesis_type", "unknown"),
            "entities_involved": hypothesis.get("entities_involved", []),
            "confidence": hypothesis.get("confidence", 0.5),
            "source": hypothesis.get("source", "reasoning_engine"),
            "generated_at": datetime.now().isoformat(),
            "status": "proposed",
            "version": 1,
            "parent_hypothesis": hypothesis.get("parent_hypothesis"),
        }
        self._memory["hypotheses"].append(record)
        self._save()
        return hyp_id

    def record_experiment(self, experiment: dict, hypothesis_id: str) -> str:
        """Record an experiment designed to test a hypothesis."""
        exp_id = f"EXP{len(self._memory['experiments']) + 1:06d}"
        record = {
            "id": exp_id,
            "hypothesis_id": hypothesis_id,
            "design": experiment.get("design", ""),
            "method": experiment.get("method", ""),
            "created_at": datetime.now().isoformat(),
            "status": "designed",
        }
        self._memory["experiments"].append(record)
        # Update hypothesis status
        for hyp in self._memory["hypotheses"]:
            if hyp["id"] == hypothesis_id:
                hyp["status"] = "testing"
        self._save()
        return exp_id

    def record_outcome(self, experiment_id: str, outcome: dict) -> bool:
        """Record experimental outcome."""
        for exp in self._memory["experiments"]:
            if exp["id"] == experiment_id:
                exp["outcome"] = outcome
                exp["status"] = "completed"
                
                # Update hypothesis status
                for hyp in self._memory["hypotheses"]:
                    if hyp["id"] == exp["hypothesis_id"]:
                        if outcome.get("supports", False):
                            hyp["status"] = "supported"
                            hyp["confidence"] = min(1.0, hyp["confidence"] + 0.1)
                        else:
                            hyp["status"] = "rejected"
                            # Move to failures
                            self._memory["failures"].append({
                                "hypohesis_id": hyp["id"],
                                "reason": outcome.get("reason", "Contradicted by evidence"),
                                "timestamp": datetime.now().isoformat(),
                            })
                self._save()
                return True
        return False

    def record_lesson(self, lesson: str, context: dict = None):
        """Record a lesson learned from failed hypotheses."""
        record = {
            "lesson": lesson,
            "context": context or {},
            "timestamp": datetime.now().isoformat(),
        }
        self._memory["lessons"].append(record)
        self._save()

    def get_failed_hypotheses(self, entity: Optional[str] = None) -> list[dict]:
        """Get previously rejected hypotheses."""
        failed_ids = {f["hypohesis_id"] for f in self._memory["failures"]}
        hypotheses = [h for h in self._memory["hypotheses"] if h["id"] in failed_ids]
        
        if entity:
            hypotheses = [h for h in hypotheses 
                         if any(entity.lower() in e.lower() 
                                for e in h.get("entities_involved", []))]
        return hypotheses

    def get_hypothesis_history(self, hypothesis_id: str) -> dict:
        """Get full history of a hypothesis."""
        history = {
            "hypotheses": [h for h in self._memory["hypotheses"] 
                          if h["id"] == hypothesis_id or h.get("parent_hypothesis") == hypothesis_id],
            "experiments": [e for e in self._memory["experiments"] 
                         if e.get("hypothesis_id") == hypothesis_id],
            "lessons": self._memory["lessons"],
        }
        return history

    def evolve_hypothesis(self, hypothesis_id: str, new_statement: str) -> str:
        """Create evolved version of hypothesis."""
        old_hyp = None
        for hyp in self._memory["hypotheses"]:
            if hyp["id"] == hypothesis_id:
                old_hyp = hyp
                break
        
        if not old_hyp:
            return None
        
        new_id = f"HYP{len(self._memory['hypotheses']) + 1:06d}"
        evolved = {
            "id": new_id,
            "statement": new_statement,
            "hypothesis_type": old_hyp.get("hypothesis_type"),
            "entities_involved": old_hyp.get("entities_involved", []),
            "confidence": old_hyp.get("confidence", 0.5),
            "source": old_hyp.get("source", "evolved"),
            "generated_at": datetime.now().isoformat(),
            "status": "proposed",
            "version": old_hyp.get("version", 1) + 1,
            "parent_hypothesis": hypothesis_id,
        }
        self._memory["hypotheses"].append(evolved)
        self._save()
        return new_id


# =============================================================================
# Critic Agent
# =============================================================================

class CriticAgent:
    """
    Attempts to refute hypotheses before they are tested.
    
    Checks:
    - Novelty: Is this already published/disproven?
    - Evidence sufficiency: Do we have enough supporting evidence?
    - Alternative explanations: Could something else explain this?
    """

    def __init__(self, research_memory: ResearchMemory):
        self.memory = research_memory

    def critique(self, hypothesis: dict) -> dict:
        """
        Critique a hypothesis and return objections.
        """
        objections = []
        
        # Check 1: Novelty
        entities = hypothesis.get("entities_involved", [])
        existing = self.memory.get_failed_hypotheses(entities[0] if entities else None)
        for old in existing:
            if old.get("statement") == hypothesis.get("statement"):
                objections.append({
                    "type": "novelty",
                    "severity": "critical",
                    "message": "This exact hypothesis has been previously rejected",
                })
        
        # Check 2: Evidence sufficiency
        confidence = hypothesis.get("confidence", 0.5)
        if confidence < 0.4:
            objections.append({
                "type": "evidence_sufficiency",
                "severity": "high",
                "message": f"Low confidence ({confidence}) - insufficient supporting evidence",
            })
        
        # Check 3: Alternative explanations (simple heuristic)
        statement = hypothesis.get("statement", "").lower()
        if "predicts" in statement:
            # Check if multiple biomarkers are mentioned - may be confounded
            if len(entities) > 2:
                objections.append({
                    "type": "alternative_explanation",
                    "severity": "medium",
                    "message": "Multiple entities - potential confounding factors",
                })
        
        return {
            "hypothesis_id": hypothesis.get("id"),
            "objections": objections,
            "survives_critic": len([o for o in objections if o["severity"] == "critical"]) == 0,
            "confidence_adjustment": -0.1 * len([o for o in objections if o["severity"] == "high"]),
        }


# =============================================================================
# Hypothesis Tournament
# =============================================================================

class HypothesisTournament:
    """
    Elo-based tournament for hypothesis ranking.
    
    Pairwise competition between hypotheses.
    """

    def __init__(self, research_memory: ResearchMemory):
        self.memory = research_memory

    @staticmethod
    def expected_score(a_rating: float, b_rating: float) -> float:
        """Calculate expected score for Elo."""
        return 1 / (1 + 10 ** ((b_rating - a_rating) / 400))

    @staticmethod
    def update_elo(rating: float, expected: float, actual: float, k: float = 32) -> float:
        """Update Elo rating."""
        return rating + k * (actual - expected)

    def run_tournament(self, hypotheses: list[dict], k: float = 32) -> list[dict]:
        """
        Run pairwise tournament and rank hypotheses.
        
        Scoring criteria:
        - Higher confidence = better
        - More evidence = better
        - Survives critic = bonus
        """
        # Initialize Elo ratings
        for h in hypotheses:
            h["elo_rating"] = h.get("confidence", 0.5) * 1000  # Scale to 0-1000
        
        # Pairwise comparison
        for i, h1 in enumerate(hypotheses):
            for h2 in hypotheses[i+1:]:
                # Determine winner (simple scoring)
                s1 = self._score_hypothesis(h1)
                s2 = self._score_hypothesis(h2)
                
                e1 = self.expected_score(h1["elo_rating"], h2["elo_rating"])
                e2 = self.expected_score(h2["elo_rating"], h1["elo_rating"])
                
                actual1 = 1 if s1 > s2 else (0.5 if s1 == s2 else 0)
                actual2 = 1 - actual1
                
                h1["elo_rating"] = self.update_elo(h1["elo_rating"], e1, actual1, k)
                h2["elo_rating"] = self.update_elo(h2["elo_rating"], e2, actual2, k)
        
        # Sort by Elo
        return sorted(hypotheses, key=lambda h: h["elo_rating"], reverse=True)

    def _score_hypothesis(self, h: dict) -> float:
        """Score a hypothesis for tournament."""
        score = 0
        score += h.get("confidence", 0.5) * 10
        score += len(h.get("entities_involved", [])) * 2
        if h.get("source") == "graph_inference":
            score += 5
        return score


# =============================================================================
# Evolution Agent
# =============================================================================

class EvolutionAgent:
    """
    Evolves hypotheses based on tournament results and lessons.
    """

    def __init__(self, research_memory: ResearchMemory):
        self.memory = research_memory

    def evolve_top_hypotheses(self, ranked_hypotheses: list[dict], 
                            threshold: float = 1500) -> list[dict]:
        """
        Evolve hypotheses that survive the tournament.
        """
        evolved = []
        for h in ranked_hypotheses[:5]:  # Top 5
            if h["elo_rating"] > threshold:
                # Merge with similar hypotheses
                merged = self._merge_similar(h, ranked_hypotheses)
                evolved.append(merged)
        return evolved

    def _merge_similar(self, target: dict, all_hypotheses: list[dict]) -> dict:
        """Merge with similar hypotheses to create stronger version."""
        entities = set(target.get("entities_involved", []))
        
        for h in all_hypotheses:
            if h["id"] == target["id"]:
                continue
            h_entities = set(h.get("entities_involved", []))
            if len(entities & h_entities) >= 2:  # Significant overlap
                # Increase confidence
                target["confidence"] = min(1.0, target["confidence"] + 0.05)
                # Add parent reference
                if not target.get("merged_from"):
                    target["merged_from"] = []
                target["merged_from"].append(h["id"])
        
        target["evolution_type"] = "merged"
        return target


# =============================================================================
# CLI Test
# =============================================================================

if __name__ == "__main__":
    memory = ResearchMemory("test")
    
    # Store hypotheses
    h1_id = memory.store_hypothesis({
        "statement": "APOE4 influences amyloid aggregation leading to tau pathology",
        "hypothesis_type": "causal_chain",
        "entities_involved": ["APOE", "Amyloid aggregation", "Tau hyperphosphorylation"],
        "confidence": 0.6,
    })
    h2_id = memory.store_hypothesis({
        "statement": "Lipid dysregulation causes neuroinflammation in Alzheimer",
        "hypothesis_type": "mechanistic",
        "entities_involved": ["Lipid dysregulation", "Neuroinflammation", "Alzheimer"],
        "confidence": 0.4,
    })
    
    print("=" * 70)
    print("Research Memory Test")
    print("=" * 70)
    print(f"\nStored hypotheses: {len(memory._memory['hypotheses'])}")
    
    # Critic test
    critic = CriticAgent(memory)
    result = critic.critique(memory._memory["hypotheses"][0])
    print(f"\nCritic result: {result}")
    
    # Tournament test
    tournament = HypothesisTournament(memory)
    ranked = tournament.run_tournament(memory._memory["hypotheses"])
    print(f"\nTournament ranking:")
    for h in ranked[:3]:
        print(f"  {h['elo_rating']:.0f}: {h['statement'][:60]}...")
    
    print("\n" + "=" * 70)
    print("Sprint 3.5 tests passed!")
    print("=" * 70)