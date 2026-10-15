"""
Research Scout Workflow - CoResearcher OS Sprint 5
End-to-end scientific discovery: question → literature → gaps → hypotheses.

This is the core workflow that demonstrates the full system capability.
"""

import sys
from datetime import datetime
from typing import Optional

# Add agents directory to path for imports
sys.path.insert(0, "C:\\Users\\usuario\\coresearcher\\python\\agents")
sys.path.insert(0, "C:\\Users\\usuario\\coresearcher\\python\\agents\\router")
sys.path.insert(0, "C:\\Users\\usuario\\coresearcher\\python")

from ingestion_pipeline import IngestionPipeline
from claim_graph_builder import ClaimGraphBuilder
from reasoning_engine import ReasoningEngine, HypothesisGenerator
from research_memory import ResearchMemory, CriticAgent, HypothesisTournament
from agent_router import AgentRouter, TrackedHypothesis

# Security tier: COMMUNITY — DO NOT MODIFY
# See python/_tiers.py for classification
SECURITY_TIER = "COMMUNITY"



class ResearchScout:
    """
    Full scientific discovery workflow.
    
    Takes a research question and produces:
    1. Literature review (multi-source)
    2. Entity-resolved claim graph
    3. Detected knowledge gaps
    4. Generated hypotheses with confidence scores
    5. Critic analysis of top hypotheses
    """
    
    def __init__(self, domain: str = "neurodegeneration"):
        self.domain = domain
        self.pipeline = IngestionPipeline(dry_run=True)
        self.graph_builder = ClaimGraphBuilder()
        self.reasoning = ReasoningEngine()
        self.memory = ResearchMemory(domain)
        self.router = AgentRouter()
        self.critic = CriticAgent(self.memory)
        self.tournament = HypothesisTournament(self.memory)
    
    def scout(self, question: str, max_papers: int = 50) -> dict:
        """
        Run complete scout workflow for a research question.
        
        Example:
            scout("What are the gaps in Alzheimer's biomarker research?")
        """
        print(f"\n[Scout] Starting discovery workflow for: {question}", file=sys.stderr)
        
        # Step 1: Literature search
        print("[Scout] Step 1: Running literature pipeline...", file=sys.stderr)
        pipeline_result = self.pipeline.neuro_pipeline(question, max_papers)
        
        # Step 2: Build claim graph
        print("[Scout] Step 2: Building claim graph...", file=sys.stderr)
        enriched_result = self.graph_builder.process_pipeline_result(pipeline_result)
        
        # Step 3: Run reasoning analysis
        print("[Scout] Step 3: Running reasoning analysis...", file=sys.stderr)
        analysis = self.reasoning.run_analysis(enriched_result)
        
        # Step 4: Store hypotheses in memory
        print("[Scout] Step 4: Storing hypotheses in memory...", file=sys.stderr)
        stored_hypotheses = []
        for h in analysis.get("candidate_hypotheses", []):
            hyp_id = self.memory.store_hypothesis(h)
            stored_hypotheses.append({"id": hyp_id, **h})
        
        # Step 5: Critic analysis
        print("[Scout] Step 5: Running critic analysis...", file=sys.stderr)
        criticized = []
        for h in stored_hypotheses[:10]:
            critique = self.critic.critique(h)
            criticized.append({**h, "critique": critique})
        
        # Step 6: Tournament ranking
        print("[Scout] Step 6: Ranking hypotheses...", file=sys.stderr)
        ranked = self.tournament.run_tournament(criticized)
        
        # Step 7: Wrap top hypotheses with TrackedHypothesis
        tracked = []
        for h in ranked[:5]:
            tracked_hyp = TrackedHypothesis(h["statement"], self.router)
            tracked_hyp.add_model_usage("gpt", "hypothesis_generation", "Generated from literature gaps")
            tracked_hyp.add_criticism(h.get("critique", {}).get("objections", []), "claude")
            tracked_hyp.add_ranking(h.get("elo_rating", 1000), "gpt", ranked.index(h) + 1)
            tracked.append(tracked_hyp.to_dict())
        
        return {
            "question": question,
            "timestamp": datetime.now().isoformat(),
            "literature": {
                "total_papers": pipeline_result.get("total_papers", 0),
                "total_claims": pipeline_result.get("total_claims", 0),
                "claims_summary": pipeline_result.get("claims_summary", {}),
            },
            "analysis": {
                "weak_evidence_claims": len(analysis.get("weak_evidence_claims", [])),
                "contradictions": len(analysis.get("research_questions", [])),
            },
            "hypotheses": {
                "generated": len(stored_hypotheses),
                "ranked": len(ranked),
                "top_5_tracked": tracked,
            },
            "routing_used": {
                "literature_review": self.router.route("literature_review"),
                "claim_extraction": self.router.route("claim_extraction"),
            },
        }
    
    def scout_drug_target(self, disease: str, biomarker: Optional[str] = None) -> dict:
        """
        Specialized workflow for drug target discovery.
        
        Example:
            scout_drug_target("Alzheimer disease", "pTau217")
        """
        query = f"{disease} {biomarker} drug target" if biomarker else f"{disease} drug target"
        
        result = self.scout(query)
        
        # Add drug-specific analysis
        drug_hypotheses = [h for h in result["hypotheses"]["top_5_tracked"] 
                          if "target" in h["statement"].lower() or 
                             "inhibitor" in h["statement"].lower() or
                             "modulator" in h["statement"].lower()]
        
        result["drug_target_focus"] = {
            "disease": disease,
            "biomarker": biomarker,
            "drug_relevant_hypotheses": drug_hypotheses,
        }
        
        return result
    
    def scout_biomarker_panel(self, disease: str, existing: list[str] = None) -> dict:
        """
        Specialized workflow for biomarker panel expansion.
        
        Example:
            scout_biomarker_panel("Parkinson disease", ["alpha-synuclein", "NfL"])
        """
        query = f"{disease} biomarker diagnostic"
        
        result = self.scout(query)
        
        # Analyze biomarker coverage
        all_entities = set()
        for paper in result.get("papers", []):
            for claim in paper.get("claims", []):
                for ent in claim.get("resolved_entities", []):
                    if ent.get("type") == "Biomarker":
                        all_entities.add(ent["canonical"])
        
        existing_set = set(existing or [])
        new_biomarkers = all_entities - existing_set
        
        result["biomarker_panel"] = {
            "existing": existing or [],
            "discovered": list(all_entities),
            "new_candidates": list(new_biomarkers),
        }
        
        return result


if __name__ == "__main__":
    scout = ResearchScout()
    
    print("=" * 70)
    print("Research Scout Workflow - Sprint 5")
    print("=" * 70)
    
    # Test with a research question
    question = "Alzheimer disease tau biomarker prediction"
    print(f"\nResearch Question: {question}")
    
    result = scout.scout(question, max_papers=10)
    
    print("\n" + "=" * 70)
    print("Workflow Results")
    print("=" * 70)
    
    print(f"\nLiterature:")
    print(f"  Papers found: {result['literature']['total_papers']}")
    print(f"  Claims extracted: {result['literature']['total_claims']}")
    print(f"  Avg confidence: {result['literature']['claims_summary'].get('avg_confidence', 0)}")
    
    print(f"\nAnalysis:")
    print(f"  Weak evidence claims: {result['analysis']['weak_evidence_claims']}")
    print(f"  Contradictions found: {result['analysis']['contradictions']}")
    
    print(f"\nTop Hypotheses:")
    for i, h in enumerate(result["hypotheses"]["top_5_tracked"][:3]):
        print(f"  {i+1}. {h['statement'][:80]}...")
        prov = h.get("provenance", {})
        if prov.get("ranking_history"):
            print(f"     Score: {prov['ranking_history'][0]['score']:.0f}")
    
    print("\n" + "=" * 70)
    print("Scout workflow complete!")
    print("=" * 70)