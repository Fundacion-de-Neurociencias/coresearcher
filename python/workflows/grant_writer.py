"""
Grant Writer Workflow - CoResearcher OS Sprint 5
Generate grant proposal sections from validated hypotheses.

Transforms ranked hypotheses into grant-ready research proposals.
"""

import sys
from datetime import datetime
from typing import Optional

sys.path.insert(0, "C:\\Users\\usuario\\coresearcher\\python\\agents")
sys.path.insert(0, "C:\\Users\\usuario\\coresearcher\\python\\agents\\router")
sys.path.insert(0, "C:\\Users\\usuario\\coresearcher\\python")

from agent_router import AgentRouter, TrackedHypothesis
from research_memory import ResearchMemory

# Security tier: PRIVATE — DO NOT MODIFY
# See python/_tiers.py for classification
SECURITY_TIER = "PRIVATE"



class GrantWriter:
    """
    Converts validated hypotheses into grant proposal components.
    
    Sections generated:
    - Specific Aims (from top hypotheses)
    - Background & Significance
    - Innovation (from critic analysis)
    - Approach (experimental design hints)
    """
    
    def __init__(self, domain: str = "neurodegeneration"):
        self.domain = domain
        self.router = AgentRouter()
        self.memory = ResearchMemory(domain)
    
    def write_specific_aims(self, hypotheses: list[dict], n_aims: int = 3) -> dict:
        """
        Generate Specific Aims section from ranked hypotheses.
        
        Takes TrackedHypothesis.to_dict() output.
        """
        aims = []
        for i, h in enumerate(hypotheses[:n_aims]):
            aim = {
                "aim_number": i + 1,
                "title": self._generate_aim_title(h),
                "hypothesis_statement": h.get("statement", ""),
                "significance": self._generate_significance(h),
                "expected_outcomes": self._generate_expected_outcomes(h),
                "feasibility_score": self._assess_feasibility(h),
            }
            aims.append(aim)
        
        return {
            "section": "Specific Aims",
            "generated_at": datetime.now().isoformat(),
            "aims": aims,
            "model_used": self.router.route("hypothesis_critique")["model"],
        }
    
    def write_innovation(self, hypotheses: list[dict], criticisms: list[dict]) -> dict:
        """
        Generate Innovation section highlighting novel aspects.
        
        Uses critic analysis to identify what makes hypotheses innovative.
        """
        innovations = []
        
        for h in hypotheses[:5]:
            prov = h.get("provenance", {})
            criticisms_list = prov.get("criticisms", [])
            
            # Innovation = survives critic but addresses weaknesses
            innovation = {
                "hypothesis": h.get("statement", "")[:100],
                "innovative_aspects": self._extract_innovative_aspects(h, criticisms_list),
                "validation_status": "survives critic" if prov.get("confidence_adjustment", 0) >= -0.1 else "critiqued",
            }
            innovations.append(innovation)
        
        return {
            "section": "Innovation",
            "generated_at": datetime.now().isoformat(),
            "innovations": innovations,
            "model_used": self.router.route("hypothesis_critique")["model"],
        }
    
    def write_approach(self, hypotheses: list[dict], memory: ResearchMemory = None) -> dict:
        """
        Generate experimental approach sections.
        
        Provides methodological suggestions based on hypothesis type.
        """
        approaches = []
        
        for h in hypotheses[:5]:
            approach = {
                "hypothesis": h.get("statement", "")[:100],
                "experimental_strategy": self._suggest_experimental_strategy(h),
                "study_design": self._suggest_study_design(h),
                "endpoints": self._suggest_endpoints(h),
                "sample_size_estimate": self._estimate_sample_size(h),
                "timeline": self._estimate_timeline(h),
            }
            approaches.append(approach)
        
        return {
            "section": "Approach",
            "generated_at": datetime.now().isoformat(),
            "approaches": approaches,
            "model_used": self.router.route("hypothesis_ranking")["model"],
        }
    
    def write_background_significance(self, hypotheses: list[dict], claim_graph: dict = None) -> dict:
        """
        Generate Background & Significance section.
        
        Synthesizes literature context from claim graph.
        """
        # Aggregate entity context
        entities_mentioned = set()
        evidence_count = 0
        
        if claim_graph:
            for paper in claim_graph.get("papers", []):
                for claim in paper.get("claims", []):
                    for ent in claim.get("resolved_entities", []):
                        entities_mentioned.add(ent.get("canonical", ""))
                    evidence_count += len(claim.get("evidence", []))
        
        significance = {
            "field_context": self._generate_field_context(hypotheses, entities_mentioned),
            "knowledge_gap": self._identify_knowledge_gap(hypotheses),
            "clinical_impact": self._estimate_clinical_impact(hypotheses),
            "literature_precedent": {
                "entities_discovered": len(entities_mentioned),
                "evidence_items": evidence_count,
            },
        }
        
        return {
            "section": "Background & Significance",
            "generated_at": datetime.now().isoformat(),
            "significance": significance,
            "model_used": self.router.route("literature_review")["model"],
        }
    
    def write_full_proposal(self, hypotheses: list[dict], claim_graph: dict = None) -> dict:
        """
        Generate complete grant proposal draft.
        
        Combines all sections into a structured proposal.
        """
        proposal = {
            "proposal_id": f"GRANT{datetime.now().strftime('%Y%m%d')}",
            "title": self._generate_proposal_title(hypotheses),
            "abstract": self._generate_abstract(hypotheses),
            "specific_aims": self.write_specific_aims(hypotheses),
            "background_significance": self.write_background_significance(hypotheses, claim_graph),
            "innovation": self.write_innovation(hypotheses, []),
            "approach": self.write_approach(hypotheses),
            "generated_at": datetime.now().isoformat(),
        }
        
        # Record all model usage in TrackedHypothesis format
        tracked = TrackedHypothesis(proposal["title"], self.router)
        tracked.add_model_usage("claude", "grant_writing", "Generate proposal sections")
        
        proposal["provenance"] = tracked.to_dict()["provenance"]
        
        return proposal
    
    # -----------------------------------------------------------------------
    # Helper methods for content generation
    # -----------------------------------------------------------------------
    
    def _generate_aim_title(self, hypothesis: dict) -> str:
        """Generate concise aim title from hypothesis."""
        statement = hypothesis.get("statement", "")
        # Extract key entities
        words = statement.split()
        key_terms = [w for w in words if len(w) > 3 and w not in ["shows", "linked", "the", "that", "with"]]
        return "Aim " + str(hypothesis.get("aim_number", 1)) + ": " + " ".join(key_terms[:4])
    
    def _generate_significance(self, hypothesis: dict) -> str:
        """Generate significance text for an aim."""
        entities = hypothesis.get("entities_involved", [])
        ent_str = ", ".join(entities[:3]) if entities else "target pathways"
        
        return (f"This aim addresses a critical gap in understanding {ent_str}. "
                f"The proposed research will provide essential mechanistic insights "
                f"that could inform therapeutic development.")
    
    def _generate_expected_outcomes(self, hypothesis: dict) -> str:
        """Generate expected outcomes for an aim."""
        return (f"We expect to demonstrate that the proposed mechanism is operative "
                f"in the context of interest. Positive results will validate "
                f"this pathway as a therapeutic target.")
    
    def _assess_feasibility(self, hypothesis: dict) -> float:
        """Assess technical feasibility based on evidence and critic analysis."""
        prov = hypothesis.get("provenance", {})
        confidence = hypothesis.get("confidence", 0.5)
        
        # Adjust based on criticisms
        criticisms = prov.get("criticisms", [])
        for c in criticisms:
            c_obj = c.get("criticism", {})
            if isinstance(c_obj, dict):
                severity = c_obj.get("severity", "medium")
                if severity == "critical":
                    return 0.3
                elif severity == "high":
                    confidence *= 0.7
            elif isinstance(c_obj, str):
                confidence *= 0.8
        
        return round(confidence, 2)
    
    def _extract_innovative_aspects(self, hypothesis: dict, criticisms: list) -> list[str]:
        """Extract innovative aspects from critic feedback."""
        aspects = []
        
        # First, identify what the critic didn't flag as problematic
        statement = hypothesis.get("statement", "").lower()
        
        if "unknown mechanism" in statement or "novel" in statement:
            aspects.append("Novel mechanism identification")
        
        if len(hypothesis.get("entities_involved", [])) >= 3:
            aspects.append("Multimodal pathway analysis")
        
        if hypothesis.get("source") == "graph_inference":
            aspects.append("Data-driven hypothesis generation")
        
        if not criticisms:
            aspects.append("Uncontested novel hypothesis")
        
        return aspects if aspects else ["Standard hypothesis approach"]
    
    def _suggest_experimental_strategy(self, hypothesis: dict) -> str:
        """Suggest experimental strategy based on hypothesis type."""
        htype = hypothesis.get("hypothesis_type", "")
        entities = hypothesis.get("entities_involved", [])
        
        if htype == "causal_chain":
            return "Longitudinal cohort study with mechanistic intermediates"
        elif htype == "mechanistic_bridge":
            return "Cross-sectional validation with pathway perturbation"
        elif htype == "diagnostic_prediction":
            return "Diagnostic accuracy study with ROC analysis"
        elif htype == "biomarker_discovery":
            return "Proteomics study with machine learning validation"
        else:
            return "Standard experimental validation approach"
    
    def _suggest_study_design(self, hypothesis: dict) -> str:
        """Suggest study design."""
        htype = hypothesis.get("hypothesis_type", "")
        
        designs = {
            "causal_chain": "Prospective observational study",
            "mechanistic_bridge": "Controlled intervention study",
            "diagnostic_prediction": "Case-control diagnostic study",
            "biomarker_discovery": "Cross-sectional discovery study",
        }
        return designs.get(htype, "Observational study")
    
    def _suggest_endpoints(self, hypothesis: dict) -> list[str]:
        """Suggest study endpoints."""
        entities = hypothesis.get("entities_involved", [])
        
        endpoints = []
        if "Biomarker" in str(entities):
            endpoints.append("Biomarker concentration change")
        if "Disease" in str(entities):
            endpoints.append("Disease progression metrics")
        
        endpoints.append("Primary mechanistic endpoint")
        endpoints.append("Secondary safety/tolerability")
        
        return endpoints[:3]
    
    def _estimate_sample_size(self, hypothesis: dict) -> int:
        """Estimate required sample size based on confidence."""
        confidence = hypothesis.get("confidence", 0.5)
        # Low confidence → need larger sample
        if confidence < 0.4:
            return 500
        elif confidence < 0.6:
            return 200
        else:
            return 100
    
    def _estimate_timeline(self, hypothesis: dict) -> dict:
        """Estimate project timeline in months."""
        htype = hypothesis.get("hypothesis_type", "")
        
        timelines = {
            "causal_chain": {"total_months": 24, "recruitment_months": 12},
            "mechanistic_bridge": {"total_months": 18, "recruitment_months": 6},
            "diagnostic_prediction": {"total_months": 12, "recruitment_months": 3},
            "biomarker_discovery": {"total_months": 15, "recruitment_months": 8},
        }
        return timelines.get(htype, {"total_months": 18, "recruitment_months": 6})
    
    def _generate_proposal_title(self, hypotheses: list[dict]) -> str:
        """Generate proposal title from hypotheses."""
        if hypotheses:
            main_entities = hypotheses[0].get("entities_involved", [])
            if len(main_entities) >= 2:
                return f"Mechanistic Investigation of {' and '.join(main_entities[:2])} in Neurodegeneration"
        return "Investigating Novel Mechanisms in Neurodegenerative Disease"
    
    def _generate_abstract(self, hypotheses: list[dict]) -> str:
        """Generate proposal abstract."""
        n_hypotheses = len(hypotheses)
        n_entities = len(set(
            e for h in hypotheses[:3] for e in h.get("entities_involved", [])
        ))
        
        return (f"This proposal investigates {n_hypotheses} novel hypotheses involving "
                f"{n_entities} key entities in neurodegenerative disease. "
                f"Our approach combines multi-source literature analysis with "
                f"mechanistic validation to address critical knowledge gaps.")
    
    def _generate_field_context(self, hypotheses: list[dict], entities: set) -> str:
        """Generate field context for background."""
        ent_list = list(entities)[:5]
        return f"The field has established connections involving {', '.join(ent_list)}. "
    
    def _identify_knowledge_gap(self, hypotheses: list[dict]) -> str:
        """Identify the key knowledge gap."""
        if hypotheses:
            entities = hypotheses[0].get("entities_involved", [])
            if entities:
                return f"However, the relationship between {' and '.join(entities[:2])} remains poorly understood."
        return "Critical mechanistic relationships remain to be elucidated."
    
    def _estimate_clinical_impact(self, hypotheses: list[dict]) -> str:
        """Estimate potential clinical impact."""
        entities = set()
        for h in hypotheses:
            for e in h.get("entities_involved", []):
                if "Disease" in e or "disease" in e.lower():
                    entities.add(e)
        
        if entities:
            return f"Successful completion could lead to new therapeutic targets for {', '.join(entities)}."
        return "Potential impact on neurodegenerative disease therapeutics."


if __name__ == "__main__":
    writer = GrantWriter()
    
    print("=" * 70)
    print("Grant Writer Workflow - Sprint 5")
    print("=" * 70)
    
    # Test with sample hypotheses
    sample_hypotheses = [
        {
            "statement": "APOE4 influences amyloid aggregation leading to tau pathology",
            "hypothesis_type": "causal_chain",
            "entities_involved": ["APOE", "Amyloid aggregation", "Tau hyperphosphorylation"],
            "confidence": 0.65,
            "source": "graph_inference",
        },
        {
            "statement": "pTau217 predicts progression to Alzheimer's disease",
            "hypothesis_type": "diagnostic_prediction",
            "entities_involved": ["pTau217", "Alzheimer's disease"],
            "confidence": 0.85,
            "source": "evidence",
        },
    ]
    
    print("\n--- Specific Aims ---")
    aims = writer.write_specific_aims(sample_hypotheses)
    for aim in aims["aims"]:
        print(f"\n  Aim {aim['aim_number']}: {aim['title']}")
        print(f"    Significance: {aim['significance'][:80]}...")
    
    print("\n--- Innovation ---")
    innovation = writer.write_innovation(sample_hypotheses, [])
    for inv in innovation["innovations"][:2]:
        print(f"  {inv['innovative_aspects']}")
    
    print("\n--- Approach ---")
    approach = writer.write_approach(sample_hypotheses)
    for app in approach["approaches"][:2]:
        print(f"  Strategy: {app['experimental_strategy']}")
        print(f"  Design: {app['study_design']}")
    
    print("\n--- Full Proposal ---")
    proposal = writer.write_full_proposal(sample_hypotheses)
    print(f"  Title: {proposal['title']}")
    print(f"  Generated: {proposal['generated_at']}")
    
    print("\n" + "=" * 70)
    print("Grant Writer workflow complete!")
    print("=" * 70)