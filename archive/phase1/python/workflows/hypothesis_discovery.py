"""
Hypothesis Discovery Workflow - CoResearcher OS Sprint 5
Deep hypothesis generation and validation pipeline.

Extends ResearchScout with more sophisticated hypothesis analysis.
"""

import sys
from datetime import datetime
from typing import Optional

sys.path.insert(0, "C:\\Users\\usuario\\coresearcher\\python\\agents")
sys.path.insert(0, "C:\\Users\\usuario\\coresearcher\\python\\agents\\router")
sys.path.insert(0, "C:\\Users\\usuario\\coresearcher\\python")

from reasoning_engine import ReasoningEngine, HypothesisGenerator, GapDetector
from research_memory import ResearchMemory, CriticAgent, HypothesisTournament, EvolutionAgent
from agent_router import AgentRouter, TrackedHypothesis


class HypothesisDiscovery:
    """
    Deep hypothesis discovery and validation workflow.
    
    Capabilities:
    - Gap-driven hypothesis generation
    - Contradiction-based research questions
    - Multi-model hypothesis critique
    - Tournament ranking with Elo ratings
    - Evolutionary hypothesis refinement
    """
    
    def __init__(self, domain: str = "neurodegeneration"):
        self.domain = domain
        self.reasoning = ReasoningEngine()
        self.gap_detector = GapDetector()
        self.generator = HypothesisGenerator()
        self.memory = ResearchMemory(domain)
        self.critic = CriticAgent(self.memory)
        self.tournament = HypothesisTournament(self.memory)
        self.evolution = EvolutionAgent(self.memory)
        self.router = AgentRouter()
    
    def discover_from_gaps(self, disease: str, domain_packs: list = None) -> dict:
        """
        Generate hypotheses specifically from detected knowledge gaps.
        
        Example:
            discover_from_gaps("Alzheimer disease")
        """
        # Detect gene-disease gaps
        gene_gaps = self.gap_detector.find_gene_disease_gaps(disease)
        
        # Convert gaps to hypotheses
        hypotheses = self.gap_detector.suggest_hypotheses_from_gaps(gene_gaps)
        
        # Apply domain pack knowledge if available
        if domain_packs:
            for pack in domain_packs:
                pack_hypotheses = pack.generate_hypotheses_from_gaps(gene_gaps)
                hypotheses.extend(pack_hypotheses)
        
        return self._refine_hypotheses(hypotheses, "gap-driven")
    
    def discover_from_claim_graph(self, claim_graph: dict) -> dict:
        """
        Generate hypotheses from entity co-occurrence patterns.
        
        Takes output from ClaimGraphBuilder.process_pipeline_result()
        """
        # Extract entity chains from claim graph
        entities = []
        for paper in claim_graph.get("papers", []):
            for claim in paper.get("claims", []):
                for ent in claim.get("resolved_entities", []):
                    entities.append((ent.get("canonical", ""), ent.get("type", "")))
        
        hypotheses = self.generator.generate_from_entity_chain(entities)
        return self._refine_hypotheses(hypotheses, "entity-chain")
    
    def discover_from_question(self, question: str, claim_graph: dict = None) -> dict:
        """
        Generate hypotheses from a natural language research question.
        
        Uses reasoning engine to decompose question into entity chains.
        """
        # Extract entities from question
        simple_entities = self._extract_entities_from_question(question)
        
        hypotheses = self.generator.generate_from_entity_chain(simple_entities)
        
        # If we have claim graph, also use that
        if claim_graph:
            graph_entities = []
            for paper in claim_graph.get("papers", []):
                for claim in paper.get("claims", []):
                    for ent in claim.get("resolved_entities", []):
                        graph_entities.append((ent.get("canonical", ""), ent.get("type", "")))
            hypotheses.extend(self.generator.generate_from_entity_chain(graph_entities))
        
        return self._refine_hypotheses(hypotheses, f"question: {question}")
    
    def _extract_entities_from_question(self, question: str) -> list[tuple]:
        """Extract entities and types from a research question."""
        # Simple heuristic extraction
        import re

# Security tier: PRIVATE — DO NOT MODIFY
# See python/_tiers.py for classification
SECURITY_TIER = "PRIVATE"

        
        entities = []
        
        # Look for gene patterns (capital letters)
        genes = re.findall(r'\b([A-Z]{2,5})\b', question)
        entities.extend([(g, "Gene") for g in genes])
        
        # Look for disease patterns
        if "alzheimer" in question.lower():
            entities.append(("Alzheimer's disease", "Disease"))
        if "parkinson" in question.lower():
            entities.append(("Parkinson's disease", "Disease"))
        if "dementia" in question.lower():
            entities.append(("Dementia", "Disease"))
        
        # Look for mechanism patterns
        for mech in ["inflammation", "aggregation", "phosphorylation", "dysfunction"]:
            if mech in question.lower():
                entities.append((mech.title(), "Mechanism"))
        
        return entities
    
    def _refine_hypotheses(self, hypotheses: list[dict], source: str) -> dict:
        """
        Full refinement pipeline: store → criticize → rank → evolve.
        """
        # Step 1: Store all hypotheses
        stored = []
        for h in hypotheses:
            h["source"] = source
            hyp_id = self.memory.store_hypothesis(h)
            stored.append({"id": hyp_id, **h})
        
        # Step 2: Critic analysis
        criticized = []
        for h in stored:
            critique = self.critic.critique(h)
            criticized.append({**h, "critique": critique})
        
        # Step 3: Tournament ranking
        ranked = self.tournament.run_tournament(criticized)
        
        # Step 4: Evolution (for high-scoring hypotheses)
        evolved = self.evolution.evolve_top_hypotheses(ranked)
        
        # Step 5: Create TrackedHypothesis for top results
        tracked = []
        for h in ranked[:10]:
            tracked_hyp = TrackedHypothesis(h["statement"], self.router)
            
            # Record routing used
            model = self.router.route("hypothesis_generation")["model"]
            tracked_hyp.add_model_usage(
                model, 
                "hypothesis_generation", 
                f"Generated from {source}"
            )
            
            # Record criticism
            if h.get("critique"):
                tracked_hyp.add_criticism(h["critique"].get("objections", []), "claude")
            
            # Record ranking
            tracked_hyp.add_ranking(h.get("elo_rating", 1000), "gpt", ranked.index(h) + 1)
            
            tracked.append(tracked_hyp.to_dict())
        
        return {
            "source": source,
            "timestamp": datetime.now().isoformat(),
            "total_hypotheses_generated": len(hypotheses),
            "total_hypotheses_ranked": len(ranked),
            "top_hypotheses": tracked[:10],
            "evolved_hypotheses": len(evolved),
        }
    
    def iterative_discovery(self, seed_hypothesis: dict, iterations: int = 3) -> dict:
        """
        Iteratively evolve a hypothesis over multiple rounds.
        
        Each iteration: critique → evolve → re-rank
        """
        current = seed_hypothesis
        history = []
        
        for i in range(iterations):
            # Store current version
            hyp_id = self.memory.store_hypothesis(current)
            
            # Critic analysis
            critique = self.critic.critique(current)
            
            # Create evolved version if surviving critic
            if critique.get("survives_critic", True):
                evolved = self.memory.evolve_hypothesis(
                    hyp_id, 
                    current["statement"] + " [refined]"
                )
                current = {**seed_hypothesis, "id": evolved, "statement": current["statement"] + " [refined]"}
            
            history.append({
                "iteration": i + 1,
                "hypothesis_id": hyp_id,
                "critique": critique,
            })
        
        return {
            "iterations": iterations,
            "final_hypothesis": current,
            "history": history,
        }


if __name__ == "__main__":
    discovery = HypothesisDiscovery()
    
    print("=" * 70)
    print("Hypothesis Discovery Workflow - Sprint 5")
    print("=" * 70)
    
    # Test gap-driven discovery
    print("\n--- Gap-Driven Discovery ---")
    result = discovery.discover_from_gaps("Alzheimer disease")
    print(f"Generated: {result['total_hypotheses_generated']}")
    print(f"Ranked: {result['total_hypotheses_ranked']}")
    
    for i, h in enumerate(result["top_hypotheses"][:3]):
        print(f"\n  Hypothesis {i+1}: {h['statement'][:70]}...")
        prov = h.get("provenance", {})
        if prov.get("ranking_history"):
            print(f"    Score: {prov['ranking_history'][0]['score']:.0f}")
    
    print("\n" + "=" * 70)
    print("Discovery workflow complete!")
    print("=" * 70)