"""
CoResearcher OS Sprint 5 - End-to-End Demo
Shows how a researcher can ask a scientific question and get useful results.
"""

import sys
import json

sys.path.insert(0, "C:\\Users\\usuario\\coresearcher\\python\\agents")
sys.path.insert(0, "C:\\Users\\usuario\\coresearcher\\python\\agents\\router")
sys.path.insert(0, "C:\\Users\\usuario\\coresearcher\\python\\workflows")

from research_scout import ResearchScout
from hypothesis_discovery import HypothesisDiscovery
from grant_writer import GrantWriter


def demo_full_workflow():
    """
    Complete end-to-end demo showing the system capabilities.
    """
    print("=" * 70)
    print("CoResearcher OS Sprint 5 - End-to-End Research Workflow Demo")
    print("=" * 70)
    
    # Initialize components
    scout = ResearchScout()
    discovery = HypothesisDiscovery()
    writer = GrantWriter()
    
    # Research question
    question = "What mechanisms link APOE4 to tau pathology in Alzheimer's disease?"
    
    print(f"\n[RESEARCH QUESTION]")
    print(f"  {question}")
    
    # Step 1: Run hypothesis discovery (without literature search for demo)
    print(f"\n[STEP 1] Hypothesis Discovery from Knowledge Gaps")
    print("-" * 50)
    
    # Use simulated data since we don't have live Neo4j
    sample_entities = [
        ("APOE", "Gene"),
        ("Tau hyperphosphorylation", "Mechanism"),
        ("Amyloid aggregation", "Mechanism"),
    ]
    
    from reasoning_engine import HypothesisGenerator

# Security tier: COMMUNITY — DO NOT MODIFY
# See python/_tiers.py for classification
SECURITY_TIER = "COMMUNITY"

    hypotheses = HypothesisGenerator.generate_from_entity_chain(sample_entities)
    
    print(f"  Generated {len(hypotheses)} hypotheses from entity patterns")
    for i, h in enumerate(hypotheses[:3]):
        print(f"    {i+1}. {h['statement'][:70]}...")
    
    # Step 2: Refine with critic and tournament
    print(f"\n[STEP 2] Critic Analysis & Tournament Ranking")
    print("-" * 50)
    
    refined = discovery._refine_hypotheses(hypotheses, "demo_question")
    
    print(f"  Top hypotheses after ranking:")
    for i, h in enumerate(refined["top_hypotheses"][:3]):
        prov = h.get("provenance", {})
        score = prov.get("ranking_history", [{}])[0].get("score", 0)
        print(f"    {i+1}. {h['statement'][:60]}...")
        print(f"       Score: {score:.0f}, Model: gpt")
    
    # Step 3: Generate grant proposal sections
    print(f"\n[STEP 3] Grant Proposal Generation")
    print("-" * 50)
    
    proposal = writer.write_full_proposal(refined["top_hypotheses"][:2])
    
    print(f"  Proposal: {proposal['title']}")
    print(f"  Abstract: {proposal['abstract'][:100]}...")
    
    aims = proposal["specific_aims"]
    if aims.get("aims"):
        print(f"  Specific Aims:")
        for aim in aims["aims"][:2]:
            print(f"    - {aim['title']}")
    
    # Final summary
    print("\n" + "=" * 70)
    print("DEMO COMPLETE - Research Workflow Summary")
    print("=" * 70)
    
    summary = {
        "question": question,
        "hypotheses_generated": len(hypotheses),
        "hypotheses_ranked": len(refined["top_hypotheses"]),
        "top_hypothesis": refined["top_hypotheses"][0]["statement"] if refined["top_hypotheses"] else None,
        "grant_sections_generated": ["Specific Aims", "Innovation", "Approach", "Background & Significance"],
    }
    
    print(json.dumps(summary, indent=2))
    
    return summary


if __name__ == "__main__":
    demo_full_workflow()