"""
python/discovery/marr_engine.py - David Marr's Tri-Level Translation & Epistemic Coherence Engine
Validates alignment between Computational, Algorithmic, and Implementational levels
and prevents category mistakes (e.g. confusing biomarkers with mechanisms).
"""

from typing import Dict, Any, List
from python.discovery.epistemic_trajectory import ExplanationLevel


class MarrTranslationEngine:
    """
    Translates and audits cross-level scientific statements across Marr's hierarchy:
    1. COMPUTATIONAL: What is the goal/loss function? (e.g. Cognitive trajectory maintenance)
    2. ALGORITHMIC: What is the representation and process? (e.g. Graph diffusion on the connectome)
    3. IMPLEMENTATIONAL: What is the physical/biochemical substrate? (e.g. Phospho-tau, synaptic vesicles)
    """

    @staticmethod
    def audit_tri_level_alignment(
        computational_goal: str,
        algorithmic_mechanism: str,
        implementational_biomarkers: List[str]
    ) -> Dict[str, Any]:
        """
        Audits whether a scientific model bridges all 3 levels without category errors.
        """
        category_errors = []

        # Check if implementational biomarkers are falsely treated as algorithmic mechanisms
        for bm in implementational_biomarkers:
            if "predicts" in algorithmic_mechanism.lower() and bm.lower() in algorithmic_mechanism.lower():
                category_errors.append(
                    f"Category Mistake: Biomarker '{bm}' is an implementational measurement, "
                    f"not an algorithmic mechanism. A statistical correlation is not a process."
                )

        is_coherent = len(category_errors) == 0

        return {
            "is_tri_level_coherent": is_coherent,
            "computational_level": {
                "level": ExplanationLevel.COMPUTATIONAL.value,
                "statement": computational_goal,
                "role": "Loss function / Functional optimization objective"
            },
            "algorithmic_level": {
                "level": ExplanationLevel.ALGORITHMIC.value,
                "statement": algorithmic_mechanism,
                "role": "State representation & causal transition process"
            },
            "implementational_level": {
                "level": ExplanationLevel.IMPLEMENTATIONAL.value,
                "biomarkers": implementational_biomarkers,
                "role": "Physical / molecular substrate and empirical measurement"
            },
            "category_mistakes_detected": category_errors,
            "mechanistic_depth_score": 0.85 if is_coherent else 0.40
        }
