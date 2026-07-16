"""
Novelty Detector - Discovery Theory Integration
Detects scientific anomalies based on the structure of known knowledge.

Based on: Diffusion models insight - creativity through structured interpolation
"""

from __future__ import annotations
from typing import List, Dict


class NoveltyDetector:
    """
    Detects novelty in scientific hypotheses by comparing against known literature.
    
    Scientific creativity emerges from structured combinations of known mechanisms.
    This detector identifies when a hypothesis is:
    - Within well-trodden connections (LOW novelty)
    - Combining known mechanisms in novel ways (MEDIUM novelty)  
    - Proposing untested connections (HIGH novelty)
    - Potentially creating new conceptual territory (HIGH novelty)
    
    Key insight: This measures unusualness, NOT impact potential.
    Impact must be inferred from evidence accumulation later.
    """
    
    def __init__(self, domain: str = "neurodegeneration"):
        self.domain = domain
        
    def assess_novelty(self, hypothesis: Dict) -> Dict:
        """
        Assess novelty of a hypothesis based on known scientific connections.
        
        Returns novelty scores (NOT impact classification - that comes later via evidence).
        - ontological_distance: How far from established categories
        - bibliographic_distance: Whether entity combinations exist in literature
        - mechanism_gap: How many linking mechanisms might be missing
        - institutional_distance: Community/citation frontier distance
        - novelty_score: Composite unusualness measure
        """
        ontological_dist = self._ontological_distance(hypothesis)
        bibliographic_dist = self._bibliographic_distance(hypothesis)
        mechanism_gap = self._mechanism_gap(hypothesis)
        institutional_dist = self._institutional_distance(hypothesis)
        
        novelty_score = self._calculate_novelty_score(
            ontological_dist, bibliographic_dist, mechanism_gap, institutional_dist
        )
        
        return {
            "ontological_distance": ontological_dist,
            "bibliographic_distance": bibliographic_dist,
            "mechanism_gap": mechanism_gap,
            "institutional_distance": institutional_dist,
            "novelty_score": novelty_score,
            "entities_known": self._known_entity_ratio(hypothesis),
        }
    
    def _ontological_distance(self, hypothesis: Dict) -> float:
        """
        Calculate distance from established ontological categories.
        
        Returns 0.0-1.0 (0 = all entities known, 1 = completely novel)
        """
        entities = hypothesis.get("entities", [])
        known_entities = self._get_known_entities(self.domain)
        
        if not entities:
            return 0.0
            
        known_count = sum(1 for e in entities if e in known_entities)
        return 1.0 - (known_count / len(entities))
    
    def _bibliographic_distance(self, hypothesis: Dict) -> float:
        """
        Estimate if this combination has been explored in literature.
        
        This would connect to PubMed/SciGraph to check co-occurrence.
        """
        return 0.5  # Conservative default
    
    def _mechanism_gap(self, hypothesis: Dict) -> int:
        """
        Count known mechanisms that might connect but haven't been linked.
        """
        return max(hypothesis.get("entities", 0).__len__() - 2, 0)
    
    def _known_entity_ratio(self, hypothesis: Dict) -> float:
        """Ratio of known vs novel entities."""
        entities = hypothesis.get("entities", [])
        known_entities = self._get_known_entities(self.domain)
        
        if not entities:
            return 0.0
            
        known_count = sum(1 for e in entities if e in known_entities)
        return known_count / len(entities)
    
    def _institutional_distance(self, hypothesis: Dict) -> float:
        """
        Calculate institutional/community distance.
        
        Measures how far this hypothesis is from established research communities.
        Would check: how many papers, labs, societies have studied these combinations.
        """
        return 0.5  # Placeholder
    
    def _calculate_novelty_score(self, ontological: float, bibliographic: float, 
                                  gap: int, institutional: float) -> float:
        """
        Calculate composite novelty score.
        
        Returns 0.0-1.0 unusualness measure.
        Note: This is NOT impact potential - just how unusual the combination is.
        """
        score = (
            ontological * 0.3 +
            bibliographic * 0.3 +
            min(gap, 5) * 0.2 +
            institutional * 0.2
        )
        return min(score, 1.0)
    
    def _get_known_entities(self, domain: str) -> set:
        """Get known entities for a domain (from CSO/bibliometric analysis)."""
        known = {
            "neurodegeneration": {
                "amyloid", "tau", "apoe4", "nfl", "gfap", "alpha-synuclein",
                "huntingtin", "tdp-43", "c9orf72", "neuroinflammation",
                "inflammation", "neurons", "stress", "proteostasis",
                "protein_folding", "phosphorylation", "neurodegeneration", "alzheimer"
            },
            "physics": {
                "gravity", "light", "mass", "energy", "spacetime", "entropy"
            },
            "biology": {
                "dna", "protein", "cell", "organism", "evolution", "selection"
            }
        }
        return known.get(domain, set())
    
    def suggest_interpolation_opportunity(self, hypothesis: Dict) -> List[str]:
        """
        Suggest what known mechanisms could be interpolated to create this hypothesis.
        """
        entities = set(hypothesis.get("entities", []))
        known = self._get_known_entities(self.domain)
        
        known_entities = entities.intersection(known)
        
        suggestions = []
        for entity in known_entities:
            suggestions.append(f"MECH-{entity.upper()}-LIKELY-SOURCE")
            
        return suggestions


# =============================================================================
# CLI Interface
# =============================================================================

if __name__ == "__main__":
    detector = NoveltyDetector(domain="neurodegeneration")
    
    test_hyp = {
        "statement": "Tau aggregation is protective response to proteostatic stress",
        "entities": ["tau", "proteostasis", "stress_response", "neuroprotection"],
        "predictions": [
            "Reducing tau should worsen outcomes in proteostasis models",
            "Tau-positive neurons show stress response activation"
        ]
    }
    
    result = detector.assess_novelty(test_hyp)
    
    print("=" * 70)
    print("NOVELTY ASSESSMENT")
    print("=" * 70)
    for key, value in result.items():
        print(f"  {key}: {value}")
    
    print("\n" + "=" * 70)
    print("INTERPOLATION OPPORTUNITIES")
    print("=" * 70)
    suggestions = detector.suggest_interpolation_opportunity(test_hyp)
    for s in suggestions:
        print(f"  - {s}")