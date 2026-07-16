"""
Einstein Generator - Sprint 21 Discovery Layer Orchestrator
Main entry point for anomaly-driven hypothesis generation.

New architecture:
Question
  ↓
Evidence
  ↓
Finding
  ↓
Anomaly ← (this module)
  ↓
Contradiction
  ↓
Thought Experiment
  ↓
Hypothesis
"""

from __future__ import annotations
from typing import List, Dict, Optional
import json
from pathlib import Path
from datetime import datetime

from .anomaly_detector import AnomalyDetector
from .boundary_explorer import BoundaryExplorer
from .missing_link_explorer import MissingLinkExplorer
from .cross_domain_transfer import CrossDomainTransfer
from .thought_experiment_generator import ThoughtExperimentGenerator
from .manifold_detector import ManifoldDetector

from knowledge.anomaly_registry import AnomalyRegistry
from knowledge.contradiction_registry import ContradictionRegistry
from knowledge.question_registry import QuestionRegistry
from knowledge.claim_registry import ClaimRegistry, HypothesisRegistry, ClaimStatus

# Security tier: PRIVATE — DO NOT MODIFY
# See python/_tiers.py for classification
SECURITY_TIER = "PRIVATE"



class EinsteinGenerator:
    """
    Main orchestrator for the Einstein Generator discovery layer.
    
    This generates hypotheses FROM SURPRISE, not FROM LITERATURE.
    
    Key insight: The real discovery asset might be QUESTION-XXXXXX,
    not CLAIM-XXXXXX or HYP-XXXXXX.
    
    Flow:
    1. Detect anomalies (trust gaps, boundaries, missing links)
    2. Generate thought experiments from anomalies
    3. Convert thought experiments to hypotheses
    4. Register new questions in the Question Registry
    """
    
    def __init__(self, domain: str = "neurodegeneration"):
        self.domain = domain
        
        # Detection modules
        self.anomaly_detector = AnomalyDetector()
        self.boundary_explorer = BoundaryExplorer()
        self.missing_link_explorer = MissingLinkExplorer()
        self.cross_domain_transfer = CrossDomainTransfer()
        self.thought_experiment_gen = ThoughtExperimentGenerator()
        self.manifold_detector = ManifoldDetector(domain=domain)
        
        # Registries
        self.anomalies = AnomalyRegistry()
        self.contradictions = ContradictionRegistry()
        self.questions = QuestionRegistry()
        self.claims = ClaimRegistry()
        self.hypotheses = HypothesisRegistry()
        
    def detect_manifold_breaks(self, hypotheses: List[Dict]) -> List[Dict]:
        """
        Detect manifold rupture in generated hypotheses.
        
        Based on Diffusion Discovery Theory:
        creativity = structured interpolation on manifolds
        """
        results = []
        
        for hyp_data in hypotheses:
            hyp_id = hyp_data.get("hypothesis_id")
            if not hyp_id:
                continue
                
            # Get hypothesis details
            hypothesis = self.hypotheses.get(hyp_id)
            if not hypothesis:
                continue
                
            # Detect manifold break
            break_result = self.manifold_detector.detect_manifold_break({
                "statement": hypothesis.get("statement", ""),
                "entities": hypothesis.get("entities", []),
                "predictions": hypothesis.get("predictions", []),
            })
            
            hyp_data["manifold_break"] = break_result
            
            # If revolutionary potential, alert
            if break_result.get("manifold_change") in ["HIGH", "REVOLUTIONARY"]:
                hyp_data["potential_manifold_rupture"] = True
                
            results.append(hyp_data)
            
        return results

    def discover_anomalies(self) -> List[Dict]:
        """Run all anomaly detection modules."""
        all_anomalies = []
        
        # Trust gap detection
        trust_gaps = self.anomaly_detector.detect_trust_gaps()
        all_anomalies.extend(trust_gaps)
        
        # Statistical outliers
        outliers = self.anomaly_detector.detect_statistical_outliers()
        all_anomalies.extend(outliers)
        
        # Boundary exploration
        boundaries = self.boundary_explorer.run_all()
        all_anomalies.extend(boundaries)
        
        # Missing link detection
        missing = self.missing_link_explorer.run_all()
        all_anomalies.extend(missing)
        
        # Cross-domain opportunities
        cross_domain = self.cross_domain_transfer.run_all()
        all_anomalies.extend(cross_domain)
        
        return all_anomalies

    def generate_hypotheses_from_anomalies(self) -> List[Dict]:
        """
        Generate hypotheses from detected anomalies.
        
        This is the core of Einstein's method:
        Anomaly → Thought Experiment → Hypothesis
        """
        results = []
        
        for anomaly in self.anomalies.list():
            # Generate thought experiment
            tex_result = self.thought_experiment_gen.generate_einstein_style(anomaly)
            
            if tex_result:
                experiment = tex_result.get("experiment", {})
                
                # Convert to hypothesis
                hypothesis_id = self.hypotheses.register(
                    statement=experiment.get("new_hypothesis", ""),
                    evidence_score=0.3,  # Low initial evidence - it's novel!
                    derived_from=[],  # Not derived from existing claims
                    domain=self.domain,
                    metadata={
                        "generated_from_anomaly": anomaly.get("id"),
                        "assumption": experiment.get("assumption"),
                        "extreme_case": experiment.get("extreme_case"),
                        "contradiction": experiment.get("contradiction"),
                        "validation_path": experiment.get("validation_path"),
                        "source": "einstein_generator",
                    }
                )
                
                # Link anomaly to hypothesis
                self.anomalies.link_hypothesis(anomaly.get("id"), hypothesis_id)
                
                # Generate a primary question from this
                question_id = self.questions.register(
                    text=f"What if {anomaly.get('entity', 'this')} has a fundamentally different mechanism?",
                    domain=self.domain,
                    context=f"Derived from Einstein Generator anomaly {anomaly.get('id')}",
                )
                
                results.append({
                    "anomaly": anomaly,
                    "experiment": experiment,
                    "hypothesis_id": hypothesis_id,
                    "question_id": question_id,
                })
        
        return results

    def run_discovery_cycle(self) -> Dict:
        """
        Run a complete discovery cycle.
        
        Returns summary of:
        - Anomalies detected
        - Thought experiments generated
        - Hypotheses created
        - Questions registered
        - Manifold break analysis (Diffusion Discovery Theory)
        """
        print("=" * 70)
        print("EINSTEIN GENERATOR - Sprint 21 Discovery Cycle")
        print("=" * 70)
        
        # Step 1: Discover anomalies
        print("\n[1] Detecting anomalies...")
        anomalies = self.discover_anomalies()
        print(f"    Found {len(anomalies)} anomalies")
        
        # Step 2: Generate hypotheses
        print("\n[2] Generating hypotheses from anomalies...")
        hyp_results = self.generate_hypotheses_from_anomalies()
        print(f"    Generated {len(hyp_results)} hypotheses")
        
        # Step 3: Generate thought experiments
        print("\n[3] Running thought experiments...")
        tex_results = self.thought_experiment_gen.run_from_all_anomalies()
        print(f"    Generated {len(tex_results)} thought experiments")
        
        # Step 4: Manifold break detection (NEW - Diffusion Discovery Theory)
        print("\n[4] Analyzing manifold breaks...")
        hyp_results = self.detect_manifold_breaks(hyp_results)
        ruptures = sum(1 for h in hyp_results if h.get("potential_manifold_rupture"))
        print(f"    Found {ruptures} potential manifold ruptures")
        
        # Summary
        summary = {
            "anomalies_detected": len(anomalies),
            "hypotheses_generated": len(hyp_results),
            "questions_generated": len([q for q in self.questions.list() if "Einstein" in q.get("context", "")]),
            "manifold_ruptures_detected": ruptures,
            "timestamps": {
                "started": datetime.now().isoformat(),
            },
            "breakthrough": "Hypothesis FROM SURPRISE, not FROM LITERATURE",
            "diffusion_insight": "Creativity as structured manifold interpolation",
        }
        
        return {
            "summary": summary,
            "hypotheses": hyp_results,
            "anomalies": anomalies,
        }

    def generate_einstein_paradox_questions(self) -> List[Dict]:
        """
        Generate classic Einstein-style 'What if?' questions.
        
        These are the questions that lead to real breakthroughs.
        """
        paradoxes = [
            {
                "question": "What if I could ride alongside a tau protein aggregate?",
                "domain": "neurodegeneration",
                "analogy": "Einstein's light beam thought experiment",
            },
            {
                "question": "What if amyloid pathology is not the cause but the body's protective response?",
                "domain": "neurodegeneration",
                "analogy": "Reverse the causal direction",
            },
            {
                "question": "What if APOE4 is not a risk factor but an adaptation marker?",
                "domain": "genomics",
                "analogy": "Reframe a risk as adaptation",
            },
            {
                "question": "What if neurofilament light is not a biomarker but the actual neurotoxic agent?",
                "domain": "neurodegeneration",
                "analogy": "Object becomes agent",
            },
        ]
        
        registered = []
        for p in paradoxes:
            qid = self.questions.register(
                text=p["question"],
                domain=p["domain"],
                context=f"Einstein paradox: {p['analogy']}",
            )
            registered.append({"id": qid, "question": p["question"]})
        
        return registered


# =============================================================================
# CLI Interface
# =============================================================================

if __name__ == "__main__":
    generator = EinsteinGenerator(domain="neurodegeneration")
    
    # Run discovery cycle
    results = generator.run_discovery_cycle()
    
    print("\n" + "=" * 70)
    print("DISCOVERY SUMMARY")
    print("=" * 70)
    print(f"Anomalies detected: {results['summary']['anomalies_detected']}")
    print(f"Hypotheses generated: {results['summary']['hypotheses_generated']}")
    
    # Generate Einstein paradox questions
    print("\n[Einstein Paradox Questions]")
    paradoxes = generator.generate_einstein_paradox_questions()
    for p in paradoxes:
        print(f"  {p['id']}: {p['question'][:60]}...")
    
    print("\n" + "=" * 70)
    print("HYPOTHESES FROM SURPRISE (not synthesis)")
    print("=" * 70)