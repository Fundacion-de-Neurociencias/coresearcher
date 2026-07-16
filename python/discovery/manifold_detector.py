"""
Manifold Detector - Discovery Theory Integration
Detects when hypotheses are attempting to create new scientific manifolds.

Based on: Diffusion models creativity = structured interpolation on manifolds
"""

from __future__ import annotations
from typing import List, Dict
import math


class ManifoldDetector:
    """
    Detects manifold rupture and calculates interpolation distances.
    
    Scientific creativity as structured interpolation on the manifold of knowledge.
    """
    
    def __init__(self, domain: str = "neurodegeneration"):
        self.domain = domain
        
    def detect_manifold_break(self, hypothesis: Dict) -> Dict:
        """
        Detect when a hypothesis is outside current conceptual space.
        
        Returns manifold rupture indicators:
        - novel_concepts: Entities not found in existing literature
        - paradigm_shift: Predictions that contradict established paradigms
        - ontological_need: Claims requiring new ontological categories
        - semantic_distance: Measure from known mechanisms
        """
        # Calculate components (no recursion)
        novel_concepts = self._count_unprecedented_entities(hypothesis)
        paradigm_shift = self._assess_paradoxical_predictions(hypothesis)
        ontological_need = self._detect_missing_categories(hypothesis)
        semantic_distance = self._measure_from_known_mechanisms(hypothesis)
        
        manifold_change = self._estimate_manifold_change_from_scores(
            novel_concepts, paradigm_shift, ontological_need, semantic_distance
        )
        
        return {
            "novel_concepts": novel_concepts,
            "paradigm_shift": paradigm_shift,
            "ontological_need": ontological_need,
            "semantic_distance": semantic_distance,
            "manifold_change": manifold_change,
        }
    
    def _count_unprecedented_entities(self, hypothesis: Dict) -> int:
        """Count concepts that have no precedent in current knowledge."""
        entities = hypothesis.get("entities", [])
        known_entities = self._get_known_entities(self.domain)
        
        unprecedented = [e for e in entities if e not in known_entities]
        return len(unprecedented)
    
    def _assess_paradoxical_predictions(self, hypothesis: Dict) -> float:
        """
        Assess if predictions contradict established paradigms.
        
        Returns score 0.0-1.0 indicating paradigm shift probability.
        """
        predictions = hypothesis.get("predictions", [])
        contradictions = 0
        
        for pred in predictions:
            if self._contradicts_paradigm(pred):
                contradictions += 1
                
        return contradictions / max(len(predictions), 1)
    
    def _detect_missing_categories(self, hypothesis: Dict) -> int:
        """Detect if hypothesis requires new ontological categories."""
        # This would check against CSO ontology
        # For now, use simple heuristics
        text = hypothesis.get("statement", "") + " " + str(hypothesis.get("entities", []))
        
        missing_indicators = [
            "unknown mechanism",
            "novel pathway",
            "previously unreported",
            "first described",
            "unique to",
        ]
        
        count = sum(1 for ind in missing_indicators if ind in text.lower())
        return count
    
    def _measure_from_known_mechanisms(self, hypothesis: Dict) -> float:
        """
        Calculate semantic distance from known mechanisms.
        
        Returns distance score 0.0-1.0 (0 = within known space, 1 = outside)
        """
        # Simple embedding-based distance calculation placeholder
        # In production, would use vector embeddings from literature
        entities = set(hypothesis.get("entities", []))
        known_mech_entities = self._get_known_mechanism_entities(self.domain)
        
        if not known_mech_entities:
            return 1.0
            
        intersection = entities.intersection(known_mech_entities)
        union = entities.union(known_mech_entities)
        
        # Jaccard similarity inverted to distance
        similarity = len(intersection) / max(len(union), 1)
        return 1.0 - similarity
    
    def _estimate_manifold_change_from_scores(
        self, 
        novel_concepts: int, 
        paradigm_shift: float, 
        ontological_need: int, 
        semantic_distance: float
    ) -> str:
        """
        Classify the type of manifold change from pre-calculated scores.
        
        Returns: LOW, MEDIUM, HIGH, or REVOLUTIONARY
        """
        score = (
            novel_concepts * 0.3 +
            paradigm_shift * 100 +
            ontological_need * 0.4 +
            semantic_distance * 100
        )
        
        if score > 80:
            return "REVOLUTIONARY"
        elif score > 50:
            return "HIGH"
        elif score > 20:
            return "MEDIUM"
        else:
            return "LOW"
    
    def _contradicts_paradigm(self, prediction: str) -> bool:
        """Check if prediction contradicts established scientific paradigms."""
        contradiction_patterns = [
            "contradicts",
            "opposite of",
            "inverse relationship",
            "protective effect",
            "causes",
        ]
        return any(p in prediction.lower() for p in contradiction_patterns)
    
    def _get_known_entities(self, domain: str) -> set:
        """Get known entities for a domain (placeholder implementation)."""
        # Would query knowledge base in production
        known = {
            "neurodegeneration": {
                "amyloid", "tau", "apoe4", "nfl", "gfap", "alpha-synuclein",
                "huntingtin", "tdp-43", "c9orf72", "neuroinflammation",
                "inflammation", "neurons", "stress", "stress_response", "proteostasis",
                "protein_folding", "phosphorylation", "neurodegeneration", "alzheimer",
                "biomarkers", "clock_genes", "cellular_aging"
            },
            "physics": {
                "gravity", "light", "mass", "energy", "spacetime", "entropy"
            },
            "biology": {
                "dna", "protein", "cell", "organism", "evolution", "selection"
            }
        }
        return known.get(domain, set())
    
    def _get_known_mechanism_entities(self, domain: str) -> set:
        """Get entities from known mechanisms (more restrictive than general entities)."""
        return self._get_known_entities(domain)
    
    def interpolate_mechanisms(self, mech_a: Dict, mech_b: Dict) -> Dict:
        """
        Perform structured interpolation between two mechanisms.
        
        This is the core operation: creativity through geometric synthesis.
        """
        return {
            "id": f"INTERP-{self._hash_mechanisms(mech_a, mech_b)}",
            "inputs": [mech_a.get("id"), mech_b.get("id")],
            "operation": "structured_interpolation",
            "method": "geometric_synthesis",
            "outputs": self._synthesize_outputs(mech_a, mech_b),
            "confidence": self._calculate_interpolation_confidence(mech_a, mech_b),
            "manifold_distance": self._calculate_manifold_distance(mech_a, mech_b),
        }
    
    def _hash_mechanisms(self, mech_a: Dict, mech_b: Dict) -> str:
        """Create unique ID for interpolation."""
        combined = f"{mech_a.get('id')}-{mech_b.get('id')}"
        return str(hash(combined) % 1000000)
    
    def _synthesize_outputs(self, mech_a: Dict, mech_b: Dict) -> List[str]:
        """Synthesize new entities from mechanism combination."""
        outputs = []
        
        # Combine entities from both mechanisms
        entities_a = mech_a.get("entities", [])
        entities_b = mech_b.get("entities", [])
        
        # Create combined concepts
        if set(entities_a).intersection(entities_b):
            outputs.append("integrated_causal_pathway")
        else:
            outputs.append("cross_domain_connection")
            
        outputs.extend([
            "combined_temporal_trajectory",
            "synthetic_biomarker_profile"
        ])
        
        return outputs
    
    def _calculate_interpolation_confidence(self, mech_a: Dict, mech_b: Dict) -> float:
        """
        Calculate confidence for interpolated mechanism.
        
        Based on support levels of input mechanisms and domain overlap.
        """
        conf_a = mech_a.get("confidence", 0.5)
        conf_b = mech_b.get("confidence", 0.5)
        
        # Average confidence weighted by domain overlap
        overlap = self._calculate_domain_overlap(mech_a, mech_b)
        
        return (conf_a + conf_b) / 2 * (0.5 + 0.5 * overlap)
    
    def _calculate_domain_overlap(self, mech_a: Dict, mech_b: Dict) -> float:
        """Calculate semantic overlap between two mechanisms."""
        domain_a = set(mech_a.get("entities", []))
        domain_b = set(mech_b.get("entities", []))
        
        if not domain_a or not domain_b:
            return 0.5
            
        intersection = domain_a.intersection(domain_b)
        return len(intersection) / max(len(domain_a), len(domain_b))
    
    def _calculate_manifold_distance(self, mech_a: Dict, mech_b: Dict) -> float:
        """
        Calculate manifold distance between mechanisms.
        
        Low distance = interpolation within known manifold
        High distance = potential manifold rupture
        """
        # This is the key insight: distance determines creativity type
        overlap = self._calculate_domain_overlap(mech_a, mech_b)
        
        # If overlap is high, we're interpolating within manifold
        # If overlap is low, we might be creating new manifold
        return 1.0 - overlap


# =============================================================================
# CLI Interface
# =============================================================================

if __name__ == "__main__":
    detector = ManifoldDetector(domain="neurodegeneration")
    
    # Test hypothesis
    test_hyp = {
        "statement": "Tau aggregation is protective response to proteostatic stress",
        "entities": ["tau", "proteostasis", "stress_response", "neuroprotection"],
        "predictions": [
            "Reducing tau should worsen outcomes in proteostasis models",
            "Tau-positive neurons show stress response activation"
        ]
    }
    
    result = detector.detect_manifold_break(test_hyp)
    
    print("=" * 70)
    print("MANIFOLD BREAK DETECTION")
    print("=" * 70)
    for key, value in result.items():
        print(f"  {key}: {value}")
    
    print("\n" + "=" * 70)
    print("INTERPOLATION TEST")
    print("=" * 70)
    
    mech_a = {
        "id": "MECH-001",
        "entities": ["tau", "aggregation", "neurodegeneration"],
        "confidence": 0.7
    }
    
    mech_b = {
        "id": "MECH-002", 
        "entities": ["proteostasis", "stress", "neuroprotection"],
        "confidence": 0.6
    }
    
    interp = detector.interpolate_mechanisms(mech_a, mech_b)
    for key, value in interp.items():
        print(f"  {key}: {value}")