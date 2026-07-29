"""
Evidence Combiner - Sprint 17
Combine multiple findings into diagnostic/evidentiative models.
Transforms knowledge into scientific reasoning.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import List, Dict, Optional
from datetime import datetime
from statistics import mean, stdev

# Security tier: PRIVATE — DO NOT MODIFY
# See python/_tiers.py for classification
SECURITY_TIER = "PRIVATE"


REGISTRY_DIR = Path("knowledge/registry")
COMBINED_FILE = REGISTRY_DIR / "combined_models.json"


class EvidenceCombiner:
    """
    Universal knowledge synthesis engine.
    
    Combines multiple findings into composite models:
    - combines findings across entities
    - calculates composite metrics
    - generates evidence weights
    - produces structured knowledge
    """
    ALIAS = "KnowledgeSynthesisEngine"
    
    # Evidence level weights
    EVIDENCE_WEIGHTS = {
        "meta_analysis": 1.0,
        "randomized_trial": 0.9,
        "cohort_study": 0.7,
        "case_control": 0.6,
        "observational": 0.5,
        "case_report": 0.3,
    }
    
    def __init__(self):
        self._models: dict = self._load()
    
    def _load(self) -> dict:
        """Load combined models from disk."""
        if COMBINED_FILE.exists():
            with open(COMBINED_FILE, 'r') as f:
                return json.load(f)
        return {"models": {}, "next_id": 1}
    
    def _save(self):
        """Save combined models to disk."""
        with open(COMBINED_FILE, 'w') as f:
            json.dump(self._models, f, indent=2)
    
    def combine_findings(self, 
                         findings: List[dict],
                         model_type: str = "diagnostic",
                         name: str = None) -> dict:
        """
        Combine multiple findings into a scientific model.
        
        Args:
            findings: List of finding dicts
            model_type: Type of model (diagnostic, mechanistic, therapeutic)
            name: Optional model name
        
        Returns:
            Combined model with IDs
        
        Example output for diagnostic model:
        {
          "id": "MODEL-000001",
          "type": "diagnostic",
          "name": "Alzheimer Biomarker Panel",
          "components": ["FIND-001", "FIND-002", ...],
          "composite_effect": 0.78,
          "evidence_score": 0.82,
          "confidence_interval": [0.72, 0.82],
          "population": "preclinical AD",
          "recommendation": "Combined pTau217 and APOE4 improve prediction"
        }
        """
        if not findings:
            return None
        
        model_id = f"MODEL-{self._models['next_id']:06d}"
        
        # Calculate composite metrics
        effect_sizes = [f.get('effect_size') for f in findings if f.get('effect_size') is not None]
        quality_scores = [f.get('quality_score', 0.5) for f in findings]
        p_values = [f.get('p_value') for f in findings if f.get('p_value') is not None]
        
        # Composite effect size (weighted average)
        composite_effect = mean(effect_sizes) if effect_sizes else 0.5
        
        # Composite evidence score
        evidence_score = min(1.0, mean(quality_scores) * len(findings) / 3)  # Normalize by finding count
        
        # Extract population and entities
        populations = [f.get('population', 'general') for f in findings]
        population = self._most_common(populations)
        
        entities = []
        for f in findings:
            if f.get('subject'):
                entities.append(f['subject'])
        
        # Generate recommendation
        recommendation = self._generate_recommendation(findings, model_type)
        
        model = {
            "id": model_id,
            "type": model_type,
            "name": name or f"{model_type.title()} Model {model_id.split('-')[1]}",
            "components": [f.get('id') for f in findings],
            "composite_effect": round(composite_effect, 3),
            "evidence_score": round(evidence_score, 3),
            "confidence_interval": self._calculate_ci(effect_sizes),
            "population": population,
            "entities": list(set(entities)),
            "recommendation": recommendation,
            "createdAt": datetime.now().isoformat(),
            "updatedAt": datetime.now().isoformat(),
        }
        
        self._models["models"][model_id] = model
        self._models["next_id"] += 1
        self._save()
        
        return model
    
    def _most_common(self, items: List[str]) -> str:
        """Find most common item in list."""
        if not items:
            return "general"
        counts = {}
        for item in items:
            counts[item] = counts.get(item, 0) + 1
        return max(counts, key=counts.get)
    
    def _calculate_ci(self, values: List[float]) -> List[float]:
        """Calculate approximate confidence interval."""
        if len(values) < 2:
            return [0.5, 0.5]
        avg = mean(values)
        std = stdev(values)
        return [round(max(0, avg - std), 3), round(min(1, avg + std), 3)]
    
    def _generate_recommendation(self, findings: List[dict], model_type: str) -> str:
        """Generate human-readable recommendation from findings."""
        if model_type == "diagnostic":
            biomarkers = [f.get('subject', '') for f in findings 
                         if f.get('predicate') in ['predicts', 'diagnoses', 'associated_with']]
            if len(biomarkers) >= 2:
                return f"Combined {', '.join(biomarkers[:3])} improve prediction accuracy"
            elif biomarkers:
                return f"{biomarkers[0]} shows diagnostic potential"
            return "Insufficient evidence for diagnostic recommendation"
        
        elif model_type == "mechanistic":
            entities = [f.get('subject', '') for f in findings]
            return f"Mechanism involves {', '.join(entities[:3])}"
        
        elif model_type == "therapeutic":
            targets = [f.get('object', '') for f in findings]
            return f"Therapeutic target: {targets[0] if targets else 'unknown'}"
        
        return "Combined findings suggest research direction"
    
    def get_model(self, model_id: str) -> Optional[dict]:
        """Get a model by ID."""
        return self._models["models"].get(model_id)
    
    def list_by_entity(self, entity: str) -> List[dict]:
        """List models containing an entity."""
        return [
            m for m in self._models["models"].values()
            if entity.lower() in [e.lower() for e in m.get("entities", [])]
        ]


# =============================================================================
# Diagnostic Model Builder (Neurodiagnoses-specific)
# =============================================================================

class DiagnosticModelBuilder:
    """
    Build diagnostic models from biomarker findings.
    
    Specializes EvidenceCombiner for neurodegeneration.
    """
    
    # Known biomarker panels
    BIOMARKER_PANELS = {
        "atn": {
            "name": "ATN Framework",
            "entities": ["amyloid", "tau", "neurodegeneration"],
            "description": "Amyloid-Tau-Neurodegeneration biomarker framework",
        },
        "plasma_biomarkers": {
            "name": "Plasma Biomarker Panel",
            "entities": ["ptau217", "nfl", "gfap", "neurogranin"],
            "description": "Blood-based biomarkers for Alzheimer's",
        },
    }
    
    def __init__(self):
        self.combiner = EvidenceCombiner()
    
    def build_panel(self, 
                    findings: List[dict],
                    panel_type: str = "custom",
                    name: str = None) -> dict:
        """Build a diagnostic biomarker panel."""
        return self.combiner.combine_findings(
            findings=findings,
            model_type="diagnostic",
            name=name or self.BIOMARKER_PANELS.get(panel_type, {}).get("name", f"Custom Panel"),
        )
    
    def calculate_auc(self, model: dict) -> float:
        """Calculate approximate AUC for diagnostic model."""
        effect = model.get("composite_effect", 0.5)
        # Rough approximation: AUC ≈ 0.5 + effect * 0.4
        return min(1.0, 0.5 + effect * 0.4)


# =============================================================================
# CLI Test
# =============================================================================

if __name__ == "__main__":
    print("=" * 70)
    print("Sprint 17: Evidence Combiner - Scientific Reasoning")
    print("=" * 70)
    
    # Sample findings (would come from registry)
    sample_findings = [
        {
            "id": "FIND-001",
            "subject": "ptau217",
            "predicate": "predicts",
            "object": "amyloid_positivity",
            "population": "preclinical_ad",
            "effect_size": 0.78,
            "p_value": 0.001,
            "quality_score": 0.82,
        },
        {
            "id": "FIND-002",
            "subject": "nfl",
            "predicate": "predicts",
            "object": "neurodegeneration",
            "population": "alzheimer",
            "effect_size": 0.65,
            "p_value": 0.005,
            "quality_score": 0.75,
        },
        {
            "id": "FIND-003",
            "subject": "apoe4",
            "predicate": "increases",
            "object": "risk",
            "population": "preclinical",
            "effect_size": 0.45,
            "p_value": 0.01,
            "quality_score": 0.70,
        },
    ]
    
    combiner = EvidenceCombiner()
    model = combiner.combine_findings(sample_findings, model_type="diagnostic")
    
    print(f"\nCombined Model: {model['id']}")
    print(f"  Name: {model['name']}")
    print(f"  Composite Effect: {model['composite_effect']}")
    print(f"  Evidence Score: {model['evidence_score']}")
    print(f"  Confidence Interval: {model['confidence_interval']}")
    print(f"  Recommendation: {model['recommendation']}")
    
    print("\n" + "=" * 70)
    print("Diagnostic Model Builder")
    print("=" * 70)
    
    builder = DiagnosticModelBuilder()
    panel = builder.build_panel(sample_findings, panel_type="custom", name="Alzheimer Multi-Modal Panel")
    
    print(f"\nPanel: {panel['name']}")
    print(f"  AUC: {builder.calculate_auc(panel):.2f}")
    print(f"  Entities: {panel['entities']}")
    
    print("\n" + "=" * 70)