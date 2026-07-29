"""
Scientific Agent Router - CoResearcher OS Sprint 4
Multi-model cognitive routing for scientific discovery.

Routes tasks to optimal agent + model combinations.
"""

import os
import json
from typing import Optional, Any
from datetime import datetime
from pathlib import Path

# Security tier: PUBLIC — DO NOT MODIFY
# See python/_tiers.py for classification
SECURITY_TIER = "PUBLIC"



# =============================================================================
# Model Registry
# =============================================================================

MODEL_REGISTRY = {
    "gpt": {
        "id": "gpt-4-turbo",
        "provider": "openai",
        "strengths": ["reasoning", "ranking", "hypothesis_generation"],
        "cost": "high",
        "speed": "fast",
    },
    "claude": {
        "id": "claude-3-opus",
        "provider": "anthropic",
        "strengths": ["critique", "writing", "analysis", "fact_checking"],
        "cost": "high",
        "speed": "medium",
    },
    "gemini": {
        "id": "gemini-1.5-pro",
        "provider": "google",
        "strengths": ["literature_review", "summarization", "browsing"],
        "cost": "medium",
        "speed": "fast",
    },
    "qwen": {
        "id": "qwen2.5:72b",
        "provider": "local",
        "strengths": ["extraction", "cheap_tasks", "claim_extraction"],
        "cost": "low",
        "speed": "slow",
    },
    "deepseek": {
        "id": "deepseek-chat",
        "provider": "deepseek",
        "strengths": ["coding", "derivation", "math"],
        "cost": "low",
        "speed": "fast",
    },
    "esm": {
        "id": "esm2",
        "provider": "local",
        "strengths": ["protein_folding", "embedding", "structure"],
        "cost": "none",
        "speed": "fast",
    },
}


# =============================================================================
# Agent Registry
# =============================================================================

AGENT_REGISTRY = {
    "literature": {
        "module": "pubmed_agent",
        "capabilities": ["search", "fetch", "extract"],
        "preferred_models": ["gemini", "claude"],
    },
    "claim_extractor": {
        "module": "claim_extractor",
        "capabilities": ["extract_claims", "find_evidence"],
        "preferred_models": ["qwen", "deepseek"],
    },
    "reviewer": {
        "module": "reviewer_engine",
        "capabilities": ["validate_doi", "validate_pmid", "fact_check"],
        "preferred_models": ["claude"],
    },
    "hypothesis_generator": {
        "module": "hypothesis_generator",
        "capabilities": ["generate", "suggest"],
        "preferred_models": ["gpt", "claude"],
    },
    "critic": {
        "module": "critic_agent",
        "capabilities": ["critique", "refute"],
        "preferred_models": ["claude", "gpt"],
    },
    "tournament": {
        "module": "hypothesis_tournament",
        "capabilities": ["rank", "compare"],
        "preferred_models": ["gpt"],
    },
    "evolution": {
        "module": "evolution_agent",
        "capabilities": ["merge", "branch", "simplify"],
        "preferred_models": ["gpt", "claude"],
    },
    "genomics": {
        "module": "genomics_pack",
        "capabilities": ["resolve_gene", "pathway_analysis"],
        "preferred_models": ["qwen", "deepseek"],
    },
    "connectors": {
        "module": "connector_service",
        "capabilities": ["knowledge_retrieval", "search_sources", "evidence_gathering"],
        "preferred_models": ["gemini", "claude"],
        "connectors": ["clinicaltrials", "opentargets", "chembl", "uniprot"],
    },
}


# =============================================================================
# Task → Model/Agent Routing
# =============================================================================

TASK_ROUTING = {
    "literature_review": {"agent": "literature", "model": "gemini"},
    "claim_extraction": {"agent": "claim_extractor", "model": "qwen"},
    "fact_checking": {"agent": "reviewer", "model": "claude"},
    "hypothesis_generation": {"agent": "hypothesis_generator", "model": "gpt"},
    "hypothesis_critique": {"agent": "critic", "model": "claude"},
    "hypothesis_ranking": {"agent": "tournament", "model": "gpt"},
    "hypothesis_evolution": {"agent": "evolution", "model": "gpt"},
    "gene_analysis": {"agent": "genomics", "model": "qwen"},
    "protein_analysis": {"agent": "esm", "model": "esm"},
    "knowledge_retrieval": {"agent": "connectors", "model": "gemini"},
    "evidence_gathering": {"agent": "connectors", "model": "claude"},
    "multi_source_search": {"agent": "connectors", "model": "gemini"},
}


# =============================================================================
# Scientific Agent Router
# =============================================================================

class AgentRouter:
    """
    Routes scientific tasks to optimal agent + model combinations.
    Maintains provenance for all routing decisions.
    """

    def __init__(self):
        self.routing_history = []

    def route(self, task: str, context: dict = None) -> dict:
        """
        Route a task to the best agent + model.
        
        Returns routing decision with provenance.
        """
        # Get default routing
        routing = TASK_ROUTING.get(task, {"agent": "literature", "model": "qwen"})
        
        # Validate agent exists
        if routing["agent"] not in AGENT_REGISTRY:
            routing = {"agent": "literature", "model": "qwen"}
        
        # Validate model exists
        if routing["model"] not in MODEL_REGISTRY:
            routing = {"agent": routing["agent"], "model": "qwen"}

        # Record routing decision
        decision = {
            "task": task,
            "agent": routing["agent"],
            "model": routing["model"],
            "timestamp": datetime.now().isoformat(),
            "context": context or {},
            "provenance": {
                "reasoning": f"Task '{task}' routed based on capability match",
                "confidence": 0.9,
            },
        }
        
        self.routing_history.append(decision)
        return decision

    def get_model_info(self, model_key: str) -> dict:
        """Get model information."""
        return MODEL_REGISTRY.get(model_key, MODEL_REGISTRY["qwen"])

    def get_agent_info(self, agent_key: str) -> dict:
        """Get agent information."""
        return AGENT_REGISTRY.get(agent_key, {})

    def list_available_models(self) -> list[str]:
        """List all available model keys."""
        return list(MODEL_REGISTRY.keys())

    def list_available_agents(self) -> list[str]:
        """List all available agent keys."""
        return list(AGENT_REGISTRY.keys())


# =============================================================================
# Provenance-aware Hypothesis
# =============================================================================

class TrackedHypothesis:
    """
    Hypothesis with full provenance chain.
    
    Every hypothesis tracks:
    - All models that touched it
    - All prompts used
    - All code executed
    - All claims/evidence
    - All criticisms
    - All ranking history
    """

    def __init__(self, statement: str, router: AgentRouter):
        self.statement = statement
        self.router = router
        self.provenance = {
            "sources": [],
            "claims": [],
            "evidence": [],
            "criticisms": [],
            "ranking_history": [],
            "models_used": [],
            "prompts_used": [],
            "code_used": [],
            "generation_chain": [],
        }

    def add_model_usage(self, model: str, purpose: str, prompt: str):
        """Record model usage."""
        self.provenance["models_used"].append({
            "model": model,
            "purpose": purpose,
            "timestamp": datetime.now().isoformat(),
        })
        self.provenance["prompts_used"].append({
            "model": model,
            "purpose": purpose,
            "prompt": prompt[:200],  # Truncate
            "timestamp": datetime.now().isoformat(),
        })

    def add_criticism(self, criticism: dict, model: str):
        """Add criticism with model attribution."""
        self.provenance["criticisms"].append({
            "criticism": criticism,
            "model": model,
            "timestamp": datetime.now().isoformat(),
        })

    def add_ranking(self, score: float, model: str, rank: int):
        """Add ranking result."""
        self.provenance["ranking_history"].append({
            "score": score,
            "model": model,
            "rank": rank,
            "timestamp": datetime.now().isoformat(),
        })

    def to_dict(self) -> dict:
        """Export full hypothesis with provenance."""
        return {
            "statement": self.statement,
            "provenance": self.provenance,
        }


# =============================================================================
# CLI Test
# =============================================================================

if __name__ == "__main__":
    router = AgentRouter()
    
    print("=" * 70)
    print("Scientific Agent Router - Sprint 4")
    print("=" * 70)
    
    # Test routing
    tasks = [
        "literature_review",
        "claim_extraction",
        "hypothesis_critique",
        "hypothesis_ranking",
    ]
    
    print("\nRouting decisions:")
    for task in tasks:
        routing = router.route(task)
        model = router.get_model_info(routing["model"])
        agent = router.get_agent_info(routing["agent"])
        print(f"\n  {task:25s}")
        print(f"    → Agent: {routing['agent']:15s} ({agent.get('module', 'unknown')})")
        print(f"    → Model: {routing['model']:15s} ({model.get('provider', 'unknown')})")
        print(f"    → Strengths: {', '.join(model.get('strengths', []))}")
    
    # Test tracked hypothesis
    print("\n" + "=" * 70)
    print("Tracked Hypothesis:")
    print("=" * 70)
    
    hyp = TrackedHypothesis(
        "APOE4 → Microglia → Tau in Alzheimer's",
        router
    )
    hyp.add_model_usage("claude", "hypothesis_generation", "Generate causal chain...")
    hyp.add_criticism({"type": "novelty", "severity": "medium"}, "claude")
    hyp.add_ranking(1500, "gpt", 1)
    
    print(f"\n  Statement: {hyp.statement}")
    print(f"  Models used: {len(hyp.provenance['models_used'])}")
    print(f"  Criticisms: {len(hyp.provenance['criticisms'])}")
    print(f"  Rankings: {len(hyp.provenance['ranking_history'])}")
    
    print("\n" + "=" * 70)
    print("Router test passed!")
    print("=" * 70)