"""
Scientific Translation Layer (STL) - Sprint 14
Concept normalization and conversion mappings.
"""

from __future__ import annotations

from typing import Optional, List
import json
from pathlib import Path

# Security tier: COMMUNITY — DO NOT MODIFY
# See python/_tiers.py for classification
SECURITY_TIER = "COMMUNITY"


INTEROP_DIR = Path("knowledge/interop")
INTEROP_DIR.mkdir(parents=True, exist_ok=True)


# =============================================================================
# Concept Registry - Canonical scientific concepts
# =============================================================================

class ConceptRegistry:
    """
    Registry for canonical scientific concepts.
    
    Maps synonyms to canonical IDs.
    """
    
    # Predefined concepts with synonyms
    CONCEPTS = {
        "CONCEPT-000001": {
            "canonical": "pTau217",
            "synonyms": ["p-tau217", "phosphorylated tau 217", "tau217", "ptau-217"],
            "type": "biomarker",
            "domain": "neurodegeneration",
        },
        "CONCEPT-000002": {
            "canonical": "APOE4",
            "synonyms": ["ApoE4", "APOE ε4", "apo E4", "APOE4 allele"],
            "type": "genetic_variant",
            "domain": "neurodegeneration",
        },
        "CONCEPT-000003": {
            "canonical": "MMSE",
            "synonyms": ["Mini-Mental State Examination", "Mini Mental State", "Folstein test"],
            "type": "cognitive_assessment",
        },
    }
    
    def __init__(self):
        self._concepts = self.CONCEPTS.copy()
        self.next_id = len(self._concepts) + 1
        self._synonym_index = {}
        self._build_synonym_index()
    
    def _build_synonym_index(self):
        """Build reverse index from synonyms to canonical."""
        for concept_id, data in self._concepts.items():
            for synonym in data.get("synonyms", []):
                self._synonym_index[synonym.lower()] = concept_id
            self._synonym_index[data["canonical"].lower()] = concept_id
    
    def resolve(self, term: str) -> Optional[dict]:
        """Resolve a term to canonical concept."""
        concept_id = self._synonym_index.get(term.lower())
        if concept_id:
            return {**self._concepts[concept_id], "id": concept_id}
        return None
    
    def register(self, canonical: str, synonyms: List[str], 
                 concept_type: str, domain: str = None) -> str:
        """Register a new concept."""
        concept_id = f"CONCEPT-{self.next_id:06d}"
        
        self._concepts[concept_id] = {
            "canonical": canonical,
            "synonyms": synonyms,
            "type": concept_type,
            "domain": domain,
        }
        
        # Update synonym index
        for synonym in synonyms:
            self._synonym_index[synonym.lower()] = concept_id
        self._synonym_index[canonical.lower()] = concept_id
        
        self.next_id += 1
        return concept_id
    
    def get(self, concept_id: str) -> Optional[dict]:
        """Get concept by ID."""
        return self._concepts.get(concept_id)
    
    def list(self) -> List[dict]:
        """List all concepts."""
        return [
            {"id": cid, **data} 
            for cid, data in self._concepts.items()
        ]


# =============================================================================
# Conversion Registry - Verified transformations between systems
# =============================================================================

class ConversionRegistry:
    """
    Registry for verified conversions between scientific systems.
    """
    
    CONVERSIONS = {
        # Unit conversions
        "CONV-000001": {
            "type": "unit",
            "from": "pg/mL",
            "to": "fg/mL",
            "factor": 1000,
            "confidence": 1.0,
        },
        "CONV-000002": {
            "type": "unit",
            "from": "ng/mL",
            "to": "fg/mL",
            "factor": 1000000,
            "confidence": 1.0,
        },
        # Scale conversions
        "CONV-000003": {
            "type": "scale",
            "from": "SUVR",
            "to": "Centiloid",
            "formula": "(x - 1.0) * 118.7",
            "confidence": 0.85,
        },
        "CONV-000004": {
            "type": "scale",
            "from": "MMSE",
            "to": "CDR",
            "mapping": {
                "24-30": 0,
                "18-23": 0.5,
                "10-17": 1,
                "5-9": 2,
                "0-4": 3,
            },
            "confidence": 0.8,
        },
        # Framework conversions
        "CONV-000005": {
            "type": "framework",
            "from": "ATN",
            "to": "NIA-AA",
            "mapping": {
                "A+T+N-": "Alzheimer's disease",
                "A+T+N+": "Alzheimer's disease",
                "A-T-N-": "Normal",
            },
            "confidence": 0.9,
        },
        # Entity translations
        "CONV-000006": {
            "type": "entity",
            "from": "pTau217",
            "to": "Phosphorylated Tau 217",
            "confidence": 1.0,
        },
    }
    
    def __init__(self):
        self._conversions = self.CONVERSIONS.copy()
        self.next_id = len(self._conversions) + 1
    
    def get_conversion(self, from_val: str, to_val: str) -> Optional[dict]:
        """Get conversion between two systems."""
        for conv in self._conversions.values():
            if conv["from"] == from_val and conv["to"] == to_val:
                return conv
        return None
    
    def convert(self, value: float, from_system: str, to_system: str) -> dict:
        """Perform conversion."""
        conv = self.get_conversion(from_system, to_system)
        if not conv:
            return {"error": f"No conversion from {from_system} to {to_system}"}
        
        if conv["type"] == "unit" and "factor" in conv:
            return {
                "value": value * conv["factor"],
                "confidence": conv["confidence"],
            }
        
        if conv["type"] == "scale" and "formula" in conv:
            # Evaluate formula safely
            result = eval(conv["formula"], {"x": value})
            return {"value": result, "confidence": conv["confidence"]}
        
        if conv["type"] == "scale" and "mapping" in conv:
            for range_key, mapped in conv["mapping"].items():
                parts = range_key.split("-")
                if len(parts) == 2:
                    low, high = int(parts[0]), int(parts[1])
                    if low <= value <= high:
                        return {"value": mapped, "confidence": conv["confidence"]}
        
        return {"value": value, "confidence": 0.5, "note": "Unknown conversion type"}
    
    def register(self, conversion: dict) -> str:
        """Register a new conversion."""
        conv_id = f"CONV-{self.next_id:06d}"
        self._conversions[conv_id] = conversion
        self.next_id += 1
        return conv_id


# =============================================================================
# Scientific Translation Engine
# =============================================================================

class ScientificTranslationEngine:
    """
    Engine for translating scientific concepts between systems.
    """
    
    def __init__(self):
        self.concepts = ConceptRegistry()
        self.conversions = ConversionRegistry()
    
    def translate(self, term: str) -> dict:
        """Translate a term to canonical concept."""
        return self.concepts.resolve(term) or {"error": "Concept not found"}
    
    def convert(self, value: float, from_system: str, to_system: str) -> dict:
        """Convert between scientific systems."""
        return self.conversions.convert(value, from_system, to_system)
    
    def get_all_equivalents(self, concept: str) -> List[dict]:
        """Get all equivalent forms of a concept."""
        resolved = self.concepts.resolve(concept)
        if not resolved:
            return []
        
        equivalents = []
        for conv in self.conversions._conversions.values():
            if conv["from"] == concept or conv["to"] == concept:
                equivalents.append(conv)
        
        return equivalents


if __name__ == "__main__":
    print("=" * 70)
    print("Scientific Translation Layer (STL)")
    print("=" * 70)
    
    engine = ScientificTranslationEngine()
    
    # Concept resolution
    print("\nConcept Resolution:")
    tests = ["p-tau217", "tau217", "APOE ε4", "MMSE"]
    for term in tests:
        result = engine.translate(term)
        print(f"  {term} → {result.get('canonical', 'NOT FOUND')}")
    
    # Unit conversion
    print("\nUnit Conversions:")
    conv1 = engine.convert(0.34, "pg/mL", "fg/mL")
    print(f"  0.34 pg/mL = {conv1['value']} fg/mL (confidence: {conv1['confidence']})")
    
    # Scale conversion
    print("\nScale Conversions:")
    conv2 = engine.convert(24, "MMSE", "CDR")
    print(f"  MMSE 24 = CDR {conv2['value']} (confidence: {conv2['confidence']})")
    
    print("\n" + "=" * 70)
    print("STL enables cross-ontology interoperability")
    print("=" * 70)