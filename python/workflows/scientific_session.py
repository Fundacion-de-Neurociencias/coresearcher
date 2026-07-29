"""
Scientific Session - Sprint 7
Orchestrates complete end-to-end scientific discovery workflow.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Optional, List, Dict
from datetime import datetime
import sys

# Add path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from workflows import ResearchScout, GrantWriter
from agents import ReasoningEngine, ResearchMemory, CriticAgent, HypothesisTournament
from ecosystem import (

# Security tier: COMMUNITY — DO NOT MODIFY
# See python/_tiers.py for classification
SECURITY_TIER = "COMMUNITY"

    ProvenanceDashboard,
    ProvenanceStep,
    ResearchProject,
    ProjectManager,
)


class ScientificSession:
    """
    Complete scientific discovery session.
    
    Orchestrates the full pipeline:
    Question → Literature → Claims → Evidence → Gaps → Hypotheses → Critique → Ranking → Report
    """
    
    def __init__(self, question: str, project_name: str = None):
        self.question = question
        self.project_name = project_name or f"Session: {datetime.now().isoformat()}"
        self.session_id = f"sess_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        self.dashboard = ProvenanceDashboard()
        self.flow_id = self.dashboard.create_flow()
        self.results: Dict = {}
        
        # Initialize components
        self.scout = ResearchScout(domain="neurodegeneration")
        self.reasoning = ReasoningEngine()
        self.memory = ResearchMemory("session")
        self.critic = CriticAgent(self.memory)
        self.tournament = HypothesisTournament(self.memory)
    
    def run(self, max_papers: int = 50) -> Dict:
        """
        Run complete discovery session.
        
        Returns:
            Complete results with all artifacts and provenance
        """
        # Step 1: Literature intake
        self.results["question"] = self.question
        self.dashboard.add_step(
            self.flow_id,
            ProvenanceStep.PAPER,
            f"question_{self.session_id}",
            metadata={"question": self.question}
        )
        
        # Step 2: Run scout workflow
        scout_result = self.scout.scout(self.question, max_papers)
        self.results["literature"] = scout_result["literature"]
        self.results["analysis"] = scout_result["analysis"]
        self.results["hypotheses_raw"] = scout_result["hypotheses"]
        
        self.dashboard.add_step(
            self.flow_id,
            ProvenanceStep.CLAIM,
            f"claims_{self.session_id}",
            model="qwen",
            evidence_score=scout_result["literature"].get("claims_summary", {}).get("avg_confidence", 0.5),
            metadata={"total_claims": scout_result["literature"].get("total_claims", 0)}
        )
        
        # Step 3: Critic review
        criticized = []
        for h in scout_result["hypotheses"]["top_5_tracked"]:
            critique = self.critic.critique(h)
            criticized.append({**h, "critique": critique})
        
        self.dashboard.add_step(
            self.flow_id,
            ProvenanceStep.CRITIC_REVIEW,
            f"critique_{self.session_id}",
            model="claude",
            metadata={"reviewed_hypotheses": len(criticized)}
        )
        
        # Step 4: Final ranking
        ranked = self.tournament.run_tournament(criticized)
        self.results["hypotheses_ranked"] = ranked
        
        self.dashboard.add_step(
            self.flow_id,
            ProvenanceStep.TOURNAMENT_RANK,
            f"ranking_{self.session_id}",
            model="gpt",
            metadata={"top_hypothesis": ranked[0]["statement"] if ranked else None}
        )
        
        # Step 5: Generate report
        self.results["report"] = self._generate_report()
        
        self.dashboard.add_step(
            self.flow_id,
            ProvenanceStep.GRANT_SECTION,
            f"report_{self.session_id}",
            model="gpt",
            metadata={"report_type": "research"}
        )
        
        return self.results
    
    def _generate_report(self) -> str:
        """Generate markdown research report."""
        report = [
            f"# Research Session: {self.session_id}",
            "",
            f"## Question",
            f"{self.question}",
            "",
            "## Literature Summary",
            f"- Papers analyzed: {self.results.get('literature', {}).get('total_papers', 0)}",
            f"- Claims extracted: {self.results.get('literature', {}).get('total_claims', 0)}",
            "",
            "## Key Claims",
        ]
        
        # Add claims summary
        claims_summary = self.results.get('literature', {}).get('claims_summary', {})
        report.extend([
            f"- Average confidence: {claims_summary.get('avg_confidence', 0):.2f}",
            f"- Biomarker claims: {claims_summary.get('biomarker_claims', 0)}",
            f"- Genetic claims: {claims_summary.get('genetic_claims', 0)}",
            "",
            "## Evidence Assessment",
        ])
        
        # Add evidence stats
        report.extend([
            f"- Weak evidence claims: {self.results.get('analysis', {}).get('weak_evidence_claims', 0)}",
            f"- Contradictions: {self.results.get('analysis', {}).get('contradictions', 0)}",
            "",
            "## Generated Hypotheses",
        ])
        
        # Add top hypotheses
        for i, h in enumerate(self.results.get('hypotheses_ranked', [])[:5]):
            report.extend([
                f"",
                f"### {i+1}. {h['statement'][:80]}...",
                f"- Confidence: {h.get('confidence', 0):.2f}",
                f"- ELO Rating: {h.get('elo_rating', 0):.0f}",
                f"- Entities: {', '.join(h.get('entities_involved', []))}",
            ])
        
        return "\n".join(report)
    
    def export(self, output_dir: str = "sessions") -> Path:
        """Export all artifacts to a session directory."""
        session_dir = Path(output_dir) / self.session_id
        session_dir.mkdir(parents=True, exist_ok=True)
        
        # Export report
        report_path = session_dir / "report.md"
        report_path.write_text(self.results.get("report", "# No report"))
        
        # Export provenance
        flow = self.dashboard.get_flow(self.flow_id)
        provenance_path = session_dir / "provenance.json"
        provenance_path.write_text(json.dumps(flow, indent=2))
        
        # Export hypotheses
        hypotheses_path = session_dir / "hypotheses.json"
        hypotheses_path.write_text(json.dumps(self.results.get("hypotheses_ranked", []), indent=2))
        
        # Export mermaid diagram
        mermaid = self._generate_mermaid()
        mermaid_path = session_dir / "provenance.html"
        mermaid_path.write_text(self._html_template(mermaid))
        
        return session_dir
    
    def _generate_mermaid(self) -> str:
        """Generate Mermaid diagram for the session."""
        flow = self.dashboard.get_flow(self.flow_id)
        return self._mermaid_from_flow(flow)
    
    @staticmethod
    def _mermaid_from_flow(flow: dict) -> str:
        """Convert flow to Mermaid diagram."""
        diagram = ["graph TD"]
        
        for i, step in enumerate(flow.get("steps", [])):
            step_id = f"S{i}"
            step_label = step.get("step", "").replace("_", " ").title()
            confidence = f"\\nconf: {step.get('confidence', 0):.2f}" if step.get("confidence") else ""
            
            diagram.append(f"    {step_id}[\"{step_label}{confidence}\"]")
            
            if i > 0:
                diagram.append(f"    S{i-1} --> {step_id}")
        
        return "\n".join(diagram)
    
    @staticmethod
    def _html_template(mermaid: str) -> str:
        """Generate HTML with embedded Mermaid diagram."""
        return f"""<!DOCTYPE html>
<html>
<head>
    <script src="https://cdn.jsdelivr.net/npm/mermaid@10/dist/mermaid.esm.min.mjs"></script>
</head>
<body>
    <pre class="mermaid">{mermaid}</pre>
    <script>mermaid.initialize({{ startOnLoad: true }})</script>
</body>
</html>"""


# =============================================================================
# Alzheimer Biomarker Discovery Demo
# =============================================================================

def demo_alzheimer_biomarkers():
    """
    One-click demo for Alzheimer biomarker discovery.
    
    Question: "What emerging biomarkers predict preclinical Alzheimer's disease?"
    """
    print("=" * 70)
    print("Sprint 7 Demo - End-to-End Scientific Discovery")
    print("=" * 70)
    
    question = "What emerging biomarkers predict preclinical Alzheimer's disease?"
    print(f"\nQuestion: {question}")
    
    # Create and run session
    session = ScientificSession(question, "Alzheimer Biomarkers")
    print("\nRunning discovery pipeline...")
    results = session.run(max_papers=30)
    
    # Show results
    print("\n" + "=" * 70)
    print("Results Summary:")
    print("=" * 70)
    
    print(f"\nPapers analyzed: {results['literature'].get('total_papers', 0)}")
    print(f"Claims extracted: {results['literature'].get('total_claims', 0)}")
    print(f"Weak evidence claims: {results['analysis'].get('weak_evidence_claims', 0)}")
    
    print("\n" + "=" * 70)
    print("Top 3 Hypotheses:")
    print("=" * 70)
    
    for i, h in enumerate(results['hypotheses_ranked'][:3]):
        print(f"\n{i+1}. {h['statement'][:100]}...")
        print(f"   Confidence: {h.get('confidence', 0):.2f}")
        print(f"   ELO: {h.get('elo_rating', 0):.0f}")
    
    # Export
    session_dir = session.export()
    print(f"\n" + "=" * 70)
    print(f"Artifacts exported to: {session_dir}")
    print("=" * 70)
    
    print(f"\nFiles:")
    for f in session_dir.iterdir():
        print(f"  - {f.name}")
    
    return session, results


if __name__ == "__main__":
    demo_alzheimer_biomarkers()