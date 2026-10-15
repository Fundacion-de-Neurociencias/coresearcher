"""
Scientific Reasoning Engine - CoResearcher OS Sprint 3
Transforms knowledge graph into scientific discovery engine.

Capabilities:
  1. Gap Detection: Find missing causal chains
  2. Contradiction Analysis: Generate research questions from conflicts
  3. Weak Evidence Detection: Identify underpowered studies
  4. Hypothesis Generation: Derive hypotheses from graph structure
"""

import sys
from typing import Optional
from collections import defaultdict

# Import from Scientific Core
sys.path.insert(0, "C:\\Users\\usuario\\coresearcher\\python\\agents")
from claim_graph_builder import EntityResolver, EvidenceRanker, ScientificTraversals


# =============================================================================
# 1. Gap Detection
# =============================================================================

class GapDetector:
    """
    Detects missing links in the scientific knowledge graph.
    
    Patterns:
    - Gene → ? → Biomarker (missing mechanism)
    - Gene → Mechanism → ? → Disease (missing biomarker)
    - Biomarker → ? → Drug (missing target relationship)
    - Claim A → Claim B → ? (missing intermediate claims)
    """

    def __init__(self, neo4j_client=None):
        self.client = neo4j_client
        self.traversals = ScientificTraversals()

    def find_gene_disease_gaps(self, disease: str) -> list[dict]:
        """
        Find genes associated with a disease but missing mechanistic chain.
        
        Returns potential hypotheses: Gene might influence Disease via unknown mechanism.
        """
        # Query: Genes associated with disease but no mechanism connection
        query = f"""
        MATCH (g:Gene)-[:ASSOCIATED_WITH]->(d:Disease {{name: '{disease}'}})
        OPTIONAL MATCH (g)-[:INFLUENCES]->(m:Mechanism)-[:CAUSES]->(b:Biomarker)-[:PREDICTS]->(d)
        WHERE m IS NULL
        RETURN g.name AS gene, d.name AS disease, 'mechanism_missing' AS gap_type
        """
        return self._execute_or_simulate(query)

    def find_gene_mechanism_biomarker_gaps(self) -> list[dict]:
        """
        Find (Gene → Mechanism) but missing biomarker connection.
        """
        query = """
        MATCH (g:Gene)-[:INFLUENCES]->(m:Mechanism)
        OPTIONAL MATCH (m)-[:CAUSES]->(b:Biomarker)
        WHERE b IS NULL
        RETURN g.name AS gene, m.name AS mechanism, 'biomarker_missing' AS gap_type
        """
        return self._execute_or_simulate(query)

    def find_clinical_evidence_gaps(self, entity: str) -> list[dict]:
        """
        Find claims about an entity but missing clinical trial evidence.
        """
        query = f"""
        MATCH (c:Claim)-[:MENTIONS_BIOMARKER|ABOUT_DISEASE]->(n)
        WHERE n.name = '{entity}'
        OPTIONAL MATCH (t:Trial)-[:MEASURES]->(n)
        WHERE t IS NULL
        RETURN c.text AS claim, n.name AS entity, 'clinical_trial_missing' AS gap_type
        """
        return self._execute_or_simulate(query)

    def suggest_hypotheses_from_gaps(self, gaps: list[dict]) -> list[dict]:
        """
        Convert detected gaps into testable hypotheses.
        """
        hypotheses = []
        for gap in gaps:
            if gap.get("gap_type") == "mechanism_missing":
                h = {
                    "statement": f"{gap['gene']} may influence {gap['disease']} via an unknown mechanism",
                    "hypothesis_type": "mechanistic_bridge",
                    "entities_involved": [gap["gene"], gap["disease"]],
                    "confidence": 0.3,  # Low base confidence for novel hypothesis
                    "supporting_evidence": [],
                    "trials_needed": True,
                }
                hypotheses.append(h)
            elif gap.get("gap_type") == "biomarker_missing":
                h = {
                    "statement": f"{gap['mechanism']} may cause measurable changes in biomarkers",
                    "hypothesis_type": "biomarker_discovery",
                    "entities_involved": [gap["gene"], gap["mechanism"]],
                    "confidence": 0.25,
                    "supporting_evidence": [],
                    "trials_needed": False,
                }
                hypotheses.append(h)
        return hypotheses

    def _execute_or_simulate(self, query: str) -> list[dict]:
        """Execute query or return simulated results for dry-run."""
        # For now, return empty list (dry-run mode)
        # When Neo4j is available, execute real query
        return []


# =============================================================================
# 2. Contradiction Analysis
# =============================================================================

class ContradictionAnalyzer:
    """
    Analyzes contradictions to generate research questions.
    """

    def __init__(self, neo4j_client=None):
        self.client = neo4j_client

    def analyze_contradictions(self, entity: str) -> list[dict]:
        """
        Find contradicting claims about an entity and generate research questions.
        
        Output: Research questions that would resolve the contradiction.
        """
        # Query for contradicting claims
        query = f"""
        MATCH (c1:Claim)-[:CONTRADICTS]->(c2:Claim)
        WHERE c1.text CONTAINS '{entity}' OR c2.text CONTAINS '{entity}'
        RETURN c1.text AS claim_a, c1.evidenceScore AS score_a,
               c2.text AS claim_b, c2.evidenceScore AS score_b
        """
        rows = self._execute_or_simulate(query)
        
        research_questions = []
        for row in rows:
            # Generate research question based on contradiction
            q = {
                "question": f"What is the true relationship between {entity} and the reported outcomes?",
                "contradiction": {
                    "claim_a": row.get("claim_a"),
                    "claim_b": row.get("claim_b"),
                },
                "evidence_a": row.get("score_a", 0),
                "evidence_b": row.get("score_b", 0),
                "confidence": min(row.get("score_a", 0), row.get("score_b", 0)),
            }
            research_questions.append(q)
        
        return research_questions

    def _execute_or_simulate(self, query: str) -> list[dict]:
        """Execute query or return simulated results for dry-run."""
        return []


# =============================================================================
# 3. Weak Evidence Detection
# =============================================================================

class EvidenceGapDetector:
    """
    Identifies claims supported by weak or underpowered evidence.
    """

    @staticmethod
    def analyze_claim_strength(claim: dict) -> dict:
        """
        Analyze if a claim has insufficient evidence.
        
        Red flags:
        - Sample size < 100
        - No statistical evidence
        - Single study
        - No replication
        """
        evidence = claim.get("evidence", [])
        rank = claim.get("evidence_ranking", {})
        
        red_flags = []
        score = rank.get("evidence_score", 0.5) if rank else 0.5
        
        # Check sample size
        n_matches = []
        for e in evidence:
            value = e.get("value", "")
            if "n=" in value.lower() or "n =" in value.lower():
                import re

# Security tier: PRIVATE — DO NOT MODIFY
# See python/_tiers.py for classification
SECURITY_TIER = "PRIVATE"

                n_matches.extend(re.findall(r'n\s*[=≈]\s*(\d+)', value.lower()))
        
        if n_matches:
            max_n = max(int(n) for n in n_matches) if n_matches else 0
            if max_n < 100:
                red_flags.append("small_sample_size")
            elif max_n < 500:
                red_flags.append("moderate_sample_size")

        # Check statistical evidence
        has_stat = rank.get("has_statistical_evidence", False) if rank else False
        if not has_stat:
            red_flags.append("no_statistical_evidence")

        # Check evidence count
        if len(evidence) < 3:
            red_flags.append("limited_evidence_items")

        return {
            "claim_id": claim.get("id", ""),
            "claim_text": claim.get("statement", "")[:100],
            "evidence_score": score,
            "red_flags": red_flags,
            "weak_evidence": len(red_flags) > 0 or score < 0.6,
        }


# =============================================================================
# 4. Hypothesis Generator
# =============================================================================

class HypothesisGenerator:
    """
    Generates hypotheses from graph structure, not LLM prompts.
    
    Pattern: If Gene A connects to Mechanism B connects to Biomarker C,
    but nobody has explicitly claimed Gene A → Biomarker C,
    generate that hypothesis.
    """

    @staticmethod
    def generate_from_entity_chain(entities: list[tuple]) -> list[dict]:
        """
        Generate hypotheses from observed entity co-mentions.
        
        entities: [(entity, type), ...] from claim extractions
        """
        # Group by type
        by_type = defaultdict(list)
        for entity, etype in entities:
            by_type[etype].append(entity)

        hypotheses = []
        
        # Pattern: Gene + Mechanism + Biomarker → causal chain hypothesis
        genes = by_type.get("Gene", [])
        mechanisms = by_type.get("Mechanism", [])
        biomarkers = by_type.get("Biomarker", [])
        diseases = by_type.get("Disease", [])

        for gene in genes:
            for mech in mechanisms:
                h = {
                    "statement": f"{gene} influences {mech}, leading to measurable effects on {', '.join(biomarkers[:3])}",
                    "hypothesis_type": "causal_chain",
                    "entities_involved": [gene, mech] + biomarkers[:3],
                    "confidence": 0.3,
                    "source": "graph_inference",
                }
                hypotheses.append(h)

        for biomarker in biomarkers:
            for disease in diseases:
                # Check if prediction is claimed
                h = {
                    "statement": f"{biomarker} predicts progression to {disease}",
                    "hypothesis_type": "diagnostic_prediction",
                    "entities_involved": [biomarker, disease],
                    "confidence": 0.25,
                    "source": "entity_cooccurrence",
                }
                hypotheses.append(h)

        return hypotheses


# =============================================================================
# Main Reasoning Engine
# =============================================================================

class ReasoningEngine:
    """
    Main orchestrator for scientific reasoning queries.
    """

    def __init__(self, neo4j_client=None):
        self.gap_detector = GapDetector(neo4j_client)
        self.contradiction_analyzer = ContradictionAnalyzer(neo4j_client)
        self.evidence_gap_detector = EvidenceGapDetector()
        self.hypothesis_generator = HypothesisGenerator()

    def run_analysis(self, pipeline_result: dict) -> dict:
        """
        Run full reasoning analysis on pipeline results.
        
        Returns:
        - detected_gaps
        - research_questions
        - weak_evidence_claims
        - candidate_hypotheses
        """
        # 1. Gap Detection (if we had a real Neo4j connection)
        gaps = []

        # 2. Contradiction Analysis
        all_claims = []
        for paper in pipeline_result.get("papers", []):
            for claim in paper.get("claims", []):
                all_claims.append(claim)

        # 3. Weak Evidence Detection
        weak_evidence = []
        for claim in all_claims:
            result = self.evidence_gap_detector.analyze_claim_strength(claim)
            if result.get("weak_evidence"):
                weak_evidence.append(result)

        # 4. Hypothesis Generation
        entities = []
        for paper in pipeline_result.get("papers", []):
            for claim in paper.get("claims", []):
                for ent in claim.get("resolved_entities", []):
                    entities.append((ent.get("canonical", ""), ent.get("type", "")))

        hypotheses = self.hypothesis_generator.generate_from_entity_chain(entities)

        return {
            "detected_gaps": len(gaps),
            "research_questions": self.contradiction_analyzer.analyze_contradictions(""),
            "weak_evidence_claims": weak_evidence,
            "candidate_hypotheses": hypotheses[:10],  # Limit output
        }


# =============================================================================
# CLI
# =============================================================================

if __name__ == "__main__":
    engine = ReasoningEngine()
    
    # Test with sample data
    sample = {
        "query": "Alzheimer biomarkers",
        "papers": [
            {
                "source": {"pmid": "38273008"},
                "claims": [
                    {
                        "statement": "pTau217 predicts progression",
                        "entities": ["pTau217", "Alzheimer"],
                        "evidence": [{"value": "p<0.001, n=3487"}],
                        "confidence": 0.85,
                        "evidence_ranking": {"evidence_score": 0.9, "has_statistical_evidence": True},
                    }
                ],
            }
        ],
        "claim_graph": {},
    }
    
    result = engine.run_analysis(sample)
    
    print("=" * 70)
    print("Reasoning Engine Analysis")
    print("=" * 70)
    print(f"\nWeak evidence claims: {len(result['weak_evidence_claims'])}")
    print(f"Candidate hypotheses generated: {len(result['candidate_hypotheses'])}")
    
    for i, h in enumerate(result["candidate_hypotheses"][:3]):
        print(f"\n  Hypothesis {i+1}: {h['statement']}")
        print(f"    Confidence: {h['confidence']}")
        print(f"    Type: {h['hypothesis_type']}")