"""
Thought Experiment Generator - Einstein Generator Module 5 (Sprint 21)
Generates hypotheses from anomalies via mental experimentation.

This is the heart of Einstein's method:
1. Take an assumption
2. Push it to extreme case
3. Find the contradiction
4. Generate new hypothesis
"""

from __future__ import annotations
from typing import List, Dict, Optional
import json
import sys
sys.path.insert(0, str(__file__.rsplit('/', 2)[0]))

from knowledge.anomaly_registry import AnomalyRegistry
from knowledge.contradiction_registry import ContradictionRegistry
from knowledge.question_registry import QuestionRegistry
from knowledge.claim_registry import ClaimRegistry
from knowledge.finding_registry import FindingRegistry


class ThoughtExperiment:
    """
    A single thought experiment record.
    
    {
        "assumption": "...",
        "extreme_case": "...",
        "contradiction": "...",
        "new_hypothesis": "...",
        "generated_from_anomaly": "ANOMALY-001",
        "validation_path": "..."
    }
    """
    pass


class ThoughtExperimentGenerator:
    """
    Generates scientific hypotheses through mental experimentation.
    
    Einstein patterns:
    1. Ray of light thought: "What if I chase a light beam?"
    2. Elevator experiment: "Can I distinguish gravity from acceleration?"
    3. EPR paradox: "What if this theory is incomplete?"
    
    Our pattern:
    1. Take anomaly: "What if this unusual pattern is real?"
    2. Push assumption: "What if the standard model is incomplete?"
    3. Find contradiction: "This assumption leads to impossible prediction"
    4. Generate hypothesis: "Therefore, X must be true"
    """
    
    THOUGHT_EXPERIMENT_FILE = "knowledge/registry/thought_experiments.json"

    def __init__(self):
        self.anomalies = AnomalyRegistry()
        self.contradictions = ContradictionRegistry()
        self.questions = QuestionRegistry()
        self.claims = ClaimRegistry()
        self.findings = FindingRegistry()
        self._experiments = self._load_experiments()

    def _load_experiments(self) -> List[dict]:
        """Load thought experiments from disk."""
        import pathlib
        expath = pathlib.Path(self.THOUGHT_EXPERIMENT_FILE)
        if expath.exists():
            with open(expath, 'r') as f:
                return json.load(f)
        return []

    def _save_experiments(self):
        """Save thought experiments to disk."""
        import pathlib

# Security tier: PRIVATE — DO NOT MODIFY
# See python/_tiers.py for classification
SECURITY_TIER = "PRIVATE"

        expath = pathlib.Path(self.THOUGHT_EXPERIMENT_FILE)
        expath.parent.mkdir(parents=True, exist_ok=True)
        with open(expath, 'w') as f:
            json.dump(self._experiments, f, indent=2)

    def generate_from_trust_gap(self, anomaly: Dict) -> Optional[Dict]:
        """
        Generate thought experiment from trust gap anomaly.
        
        Pattern:
        - Assumption: The literature is correct
        - Extreme case: What if both claims are right in different contexts?
        - Contradiction: That would mean context-dependency exists
        - Hypothesis: There's a hidden moderator variable
        """
        entity = anomaly.get("entity", "unknown")
        high = anomaly.get("highTrustClaim", {})
        low = anomaly.get("lowTrustClaim", {})
        
        experiment = {
            "id": f"TEX-{len(self._experiments) + 1:06d}",
            "type": "trust_gap_resolution",
            "assumption": f"Claims about {entity} should have consistent evidence scores",
            "extreme_case": f"What if {entity} behaves differently in different contexts?",
            "contradiction": "If context matters, the standard model is incomplete",
            "new_hypothesis": f"{entity} has context-dependent effects not captured in current models",
            "generated_from_anomaly": anomaly.get("id"),
            "validation_path": "Test in different populations/contexts",
        }
        
        self._experiments.append(experiment)
        self._save_experiments()
        
        # Also register a question
        question_id = self.questions.register(
            text=f"What determines the context-dependency of {entity}?",
            domain=anomaly.get("domain", "general"),
            context=f"Derived from trust gap in {entity}",
        )
        
        return {"experiment": experiment, "question_id": question_id}

    def generate_from_contradiction(self, contradiction: Dict) -> Optional[Dict]:
        """
        Generate thought experiment from contradiction.
        
        Pattern:
        - Assumption: Both claims are correct
        - Extreme case: Take each to its logical conclusion
        - Contradiction: They cannot both be true
        - Hypothesis: There's a hidden factor resolving both
        """
        entity = contradiction.get("entity", "unknown")
        claim_a = contradiction.get("claimA", {})
        claim_b = contradiction.get("claimB", {})
        
        experiment = {
            "id": f"TEX-{len(self._experiments) + 1:06d}",
            "type": "contradiction_resolution",
            "assumption": f"Both {claim_a.get('text', '')[:40]}... and {claim_b.get('text', '')[:40]}... are correct",
            "extreme_case": f"What hidden factor could reconcile these seemingly opposite claims?",
            "contradiction": "The claims cannot both be universally true without mediation",
            "new_hypothesis": f"There exists a mediator/constraint that reconciles {entity} claims",
            "generated_from_anomaly": contradiction.get("id"),
            "validation_path": "Search for mediating variables",
        }
        
        self._experiments.append(experiment)
        self._save_experiments()
        
        return {"experiment": experiment}

    def generate_from_missing_link(self, anomaly: Dict) -> Optional[Dict]:
        """
        Generate thought experiment from missing link.
        
        Pattern:
        - Assumption: The chain A->B->C is complete
        - Extreme case: What if there's an implicit step?
        - Contradiction: The missing link must exist for coherence
        - Hypothesis: The missing link is X
        """
        chain = anomaly.get("metadata", {}).get("chain", "")
        
        experiment = {
            "id": f"TEX-{len(self._experiments) + 1:06d}",
            "type": "missing_link_hypothesis",
            "assumption": f"The relationship chain {chain} has no hidden steps",
            "extreme_case": f"What if there's a mediator M such that A->M->B->C?",
            "contradiction": "Without M, the relationship would be direct and simpler",
            "new_hypothesis": f"There exists a mediator M in the {chain} pathway",
            "generated_from_anomaly": anomaly.get("id"),
            "validation_path": "Search for intermediate variables",
        }
        
        self._experiments.append(experiment)
        self._save_experiments()
        
        return {"experiment": experiment}

    def generate_einstein_style(self, anomaly: Dict) -> Dict:
        """
        Generate Einstein-style thought experiment.
        
        Classic Einstein pattern:
        1. Imagine riding alongside a light wave
        2. Ask: What would I see?
        3. Derive: A stationary wave - impossible!
        4. Conclude: Light requires no medium (special relativity insight)
        """
        entity = anomaly.get("entity", "unknown")
        
        # Generate the classic "what if" pattern
        experiment = {
            "id": f"TEX-{len(self._experiments) + 1:06d}",
            "type": "einstein_paradox",
            "assumption": f"The standard understanding of {entity} is complete",
            "extreme_case": f"What if I could observe {entity} from a completely different perspective?",
            "contradiction": f"If I observe {entity} at its extreme, I find it behaves unexpectedly",
            "new_hypothesis": f"The mechanism of {entity} must be reimagined",
            "generated_from_anomaly": anomaly.get("id"),
            "validation_path": "Extreme case testing, boundary conditions",
        }
        
        self._experiments.append(experiment)
        self._save_experiments()
        
        return {"experiment": experiment}

    def run_from_all_anomalies(self) -> List[Dict]:
        """Generate thought experiments from all current anomalies."""
        results = []
        for anomaly in self.anomalies.list():
            anomaly_type = anomaly.get("type", "")
            
            if anomaly_type == "trust_gap":
                result = self.generate_from_trust_gap(anomaly)
            elif anomaly_type == "missing_link":
                result = self.generate_from_missing_link(anomaly)
            else:
                result = self.generate_einstein_style(anomaly)
            
            if result:
                results.append(result)
        
        return results

    def run_from_contradictions(self) -> List[Dict]:
        """Generate thought experiments from all contradictions."""
        results = []
        for contradiction in self.contradictions.list():
            result = self.generate_from_contradiction(contradiction)
            if result:
                results.append(result)
        
        return results


if __name__ == "__main__":
    gen = ThoughtExperimentGenerator()
    results = gen.run_from_all_anomalies()
    print(f"Generated {len(results)} thought experiments")