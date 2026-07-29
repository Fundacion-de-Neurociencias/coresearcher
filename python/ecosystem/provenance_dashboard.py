"""
Provenance Dashboard - CoResearcher OS Sprint 6
Visualizes the full provenance chain: Paper → Claim → Evidence → Hypothesis → Critic → Tournament → Grant.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Optional, List
from datetime import datetime
from uuid import uuid4

# Security tier: COMMUNITY — DO NOT MODIFY
# See python/_tiers.py for classification
SECURITY_TIER = "COMMUNITY"


# Dashboard storage
DASHBOARD_DIR = Path("ecosystem/provenance")
DASHBOARD_DIR.mkdir(parents=True, exist_ok=True)
FLOWS_FILE = DASHBOARD_DIR / "flows.json"


# Provenance chain step types
class ProvenanceStep:
    PAPER = "paper"
    CLAIM = "claim"
    EVIDENCE = "evidence"
    HYPOTHESIS = "hypothesis"
    CRITIC_REVIEW = "critic_review"
    TOURNAMENT_RANK = "tournament_rank"
    GRANT_SECTION = "grant_section"


class ProvenanceDashboard:
    """
    Tracks and visualizes the full provenance chain of scientific artifacts.
    
    The flow shows how knowledge evolves:
    Paper → Claim → Evidence → Hypothesis → Critic Review → Tournament Rank → Grant Section
    """
    
    def __init__(self):
        self._flows: dict = self._load()
    
    def _load(self) -> dict:
        """Load provenance flows from disk."""
        if FLOWS_FILE.exists():
            with open(FLOWS_FILE, 'r') as f:
                return json.load(f)
        return {"flows": {}, "next_id": 1}
    
    def _save(self):
        """Save provenance flows to disk."""
        with open(FLOWS_FILE, 'w') as f:
            json.dump(self._flows, f, indent=2)
    
    def create_flow(self, project_id: Optional[str] = None) -> str:
        """
        Create a new provenance flow.
        
        Returns:
            Flow ID
        """
        flow_id = f"flow_{self._flows['next_id']}"
        flow = {
            "id": flow_id,
            "project_id": project_id,
            "steps": [],
            "current_step": None,
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
        }
        self._flows["flows"][flow_id] = flow
        self._flows["next_id"] += 1
        self._save()
        return flow_id
    
    def add_step(self, flow_id: str, step: str, artifact_id: str,
                 model: str = None, confidence: float = None,
                 evidence_score: float = None, metadata: dict = None):
        """
        Add a step to the provenance flow.
        
        Args:
            flow_id: The flow to update
            step: Type of step (paper, claim, evidence, etc.)
            artifact_id: ID of the artifact at this step
            model: Model used (optional)
            confidence: Confidence score (optional)
            evidence_score: Evidence score (optional)
            metadata: Additional metadata (optional)
        """
        if flow_id not in self._flows["flows"]:
            raise ValueError(f"Flow {flow_id} not found")
        
        flow_step = {
            "step": step,
            "artifact_id": artifact_id,
            "timestamp": datetime.now().isoformat(),
            "model": model,
            "confidence": confidence,
            "evidence_score": evidence_score,
            "metadata": metadata or {},
        }
        
        self._flows["flows"][flow_id]["steps"].append(flow_step)
        self._flows["flows"][flow_id]["current_step"] = step
        self._flows["flows"][flow_id]["updated_at"] = datetime.now().isoformat()
        self._save()
    
    def get_flow(self, flow_id: str) -> Optional[dict]:
        """Get a provenance flow by ID."""
        return self._flows["flows"].get(flow_id)
    
    def get_flow_visualization(self, flow_id: str) -> str:
        """
        Generate a text visualization of the provenance flow.
        
        Shows the complete chain from Paper to Grant Section.
        """
        flow = self.get_flow(flow_id)
        if not flow:
            return f"Flow {flow_id} not found"
        
        # Build step map
        step_map = {s["step"]: s for s in flow["steps"]}
        
        # Visual chain
        chain = "Paper"
        chain += "\n ↓" if step_map.get("claim") else ""
        chain += "\nClaim" if step_map.get("claim") else ""
        chain += "\n ↓" if step_map.get("evidence") else ""
        chain += "\nEvidence" if step_map.get("evidence") else ""
        chain += "\n ↓" if step_map.get("hypothesis") else ""
        chain += "\nHypothesis" if step_map.get("hypothesis") else ""
        chain += "\n ↓" if step_map.get("critic_review") else ""
        chain += "\nCritic Review" if step_map.get("critic_review") else ""
        chain += "\n ↓" if step_map.get("tournament_rank") else ""
        chain += "\nTournament Rank" if step_map.get("tournament_rank") else ""
        chain += "\n ↓" if step_map.get("grant_section") else ""
        chain += "\nGrant Section" if step_map.get("grant_section") else ""
        
        result = f"Provenance Flow: {flow_id}\n"
        result += "=" * 50 + "\n"
        result += chain + "\n\n"
        
        # Show detailed steps
        result += "Steps:\n"
        for s in flow["steps"]:
            result += f"\n  {s['step'].upper()}:\n"
            if s.get("model"):
                result += f"    Model: {s['model']}\n"
            if s.get("confidence") is not None:
                result += f"    Confidence: {s['confidence']:.2f}\n"
            if s.get("evidence_score") is not None:
                result += f"    Evidence Score: {s['evidence_score']:.2f}\n"
        
        return result
    
    def trace_artifact(self, artifact_id: str) -> Optional[dict]:
        """
        Trace the full provenance chain for an artifact.
        """
        for flow_id, flow in self._flows["flows"].items():
            for step in flow["steps"]:
                if step["artifact_id"] == artifact_id:
                    return {
                        "flow_id": flow_id,
                        "step": step,
                        "full_chain": flow["steps"],
                    }
        return None
    
    def complete_chain(self, flow_id: str) -> bool:
        """
        Check if a flow has completed the full chain (Paper → Grant).
        """
        flow = self.get_flow(flow_id)
        if not flow:
            return False
        
        steps = [s["step"] for s in flow["steps"]]
        required = [
            ProvenanceStep.PAPER,
            ProvenanceStep.CLAIM,
            ProvenanceStep.HYPOTHESIS,
            ProvenanceStep.GRANT_SECTION,
        ]
        
        return all(s in steps for s in required)


# =============================================================================
# Visual Provenance Tree
# =============================================================================

class ProvenanceTree:
    """
    Generates visual tree representations of provenance flows.
    """
    
    @staticmethod
    def format_tree(steps: list[dict]) -> str:
        """Format provenance steps as a tree."""
        if not steps:
            return "Empty flow"
        
        tree = ["Paper"]
        
        for i, step in enumerate(steps[1:], 1):
            indent = "  " * i
            connector = "└── " if i == len(steps) - 1 else "├── "
            tree.append(f"\n{indent}{connector}{step['step'].upper()}")
            
            # Add metadata
            if step.get("confidence"):
                tree.append(f"\n{'  ' * (i + 1)}confidence: {step['confidence']:.2f}")
            if step.get("model"):
                tree.append(f"\n{'  ' * (i + 1)}model: {step['model']}")
        
        return "".join(tree)
    
    @staticmethod
    def to_mermaid(flow: dict) -> str:
        """Generate Mermaid diagram for provenance flow."""
        if not flow:
            return ""
        
        diagram = ["graph TD"]
        
        for i, step in enumerate(flow["steps"]):
            step_id = f"S{i}"
            step_label = step["step"].replace("_", " ").title()
            confidence = f"\\nconf: {step['confidence']:.2f}" if step.get("confidence") else ""
            
            diagram.append(f"    {step_id}[\"{step_label}{confidence}\"]")
            
            if i > 0:
                diagram.append(f"    S{i-1} --> {step_id}")
        
        return "\n".join(diagram)


# =============================================================================
# CLI Test
# =============================================================================

if __name__ == "__main__":
    print("=" * 70)
    print("Provenance Dashboard - Sprint 6")
    print("=" * 70)
    
    dashboard = ProvenanceDashboard()
    
    # Create a flow
    flow_id = dashboard.create_flow(project_id="plasma_ptau217")
    print(f"\nCreated flow: {flow_id}")
    
    # Add steps to the chain
    steps = [
        ("paper", "paper_001", None, None, None, {"doi": "10.1234/test"}),
        ("claim", "claim_001", "qwen", 0.85, 0.90, {"text": "pTau217 predicts AD"}),
        ("hypothesis", "hyp_001", "gpt", 0.75, None, {"statement": "Plasma pTau217 predicts Alzheimer onset"}),
        ("critic_review", "critique_001", "claude", None, None, {"objections": ["low_sample_size"]}),
        ("tournament_rank", "rank_001", "gpt", None, None, {"elo_score": 1450}),
        ("grant_section", "grant_001", "gpt", None, None, {"section": "Specific Aims"}),
    ]
    
    print(f"\nAdding steps to flow {flow_id}...")
    for step, artifact, model, confidence, evidence_score, metadata in steps:
        dashboard.add_step(flow_id, step, artifact, model, confidence, evidence_score, metadata)
        print(f"  Added {step}")
    
    # Show visualization
    print("\n" + "=" * 70)
    print("Provenance Visualization:")
    print("=" * 70)
    print(dashboard.get_flow_visualization(flow_id))
    
    # Show Mermaid diagram
    print("\n" + "=" * 70)
    print("Mermaid Diagram:")
    print("=" * 70)
    flow = dashboard.get_flow(flow_id)
    print(ProvenanceTree.to_mermaid(flow))
    
    print("\n" + "=" * 70)
    print("Provenance Dashboard complete!")
    print("=" * 70)