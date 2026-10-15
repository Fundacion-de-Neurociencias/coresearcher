"""
Scientific Interoperability Layer (SIL) - Sprint 13
Measurement normalization and framework translation.
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
# Measurement Registry
# =============================================================================

class MeasurementRegistry:
    """
    Registry for scientific measurements with unit normalization.
    """
    
    def __init__(self):
        self._measurements: dict = {}
        self.next_id = 1
    
    def register(self, entity: str, value: float, unit: str,
                 framework: str = None,
                 paper_doi: str = None,
                 metadata: dict = None) -> str:
        """
        Register a measurement with normalization.
        
        Returns:
            Measurement ID (MEAS-XXXXXX)
        """
        meas_id = f"MEAS-{self.next_id:06d}"
        
        measurement = {
            "id": meas_id,
            "entity": entity,
            "value": value,
            "unit": unit,
            "framework": framework,
            "normalized_value": self._normalize_value(entity, value, unit),
            "normalized_unit": self._get_normalized_unit(entity),
            "conversion_confidence": 1.0,
            "paper_doi": paper_doi,
            "metadata": metadata or {},
        }
        
        self._measurements[meas_id] = measurement
        self.next_id += 1
        return meas_id
    
    def _normalize_value(self, entity: str, value: float, unit: str) -> float:
        """Normalize measurement value to standard unit."""
        # Protein biomarkers: fg/mL
        if entity.lower() in ["ptau217", "ptau", "nfl", "gfap", "taup", "ab42"]:
            if unit in ["pg/mL", "pg/mL"]:
                return value * 1000  # pg to fg
            elif unit in ["ng/mL", "ng/L"]:
                return value * 1000000  # ng to fg
        
        # Centiloid conversion
        if "suVR" in entity.lower() or "suvr" in unit.lower():
            # Approximate conversion SUVR -> Centiloid
            return (value - 1.0) * 118.7  # Approximate
        
        return value
    
    def _get_normalized_unit(self, entity: str) -> str:
        """Get normalized unit for entity."""
        if entity.lower() in ["ptau217", "ptau", "nfl", "gfap", "taup", "ab42"]:
            return "fg/mL"
        return "normalized"
    
    def get(self, meas_id: str) -> Optional[dict]:
        """Get measurement by ID."""
        return self._measurements.get(meas_id)


# =============================================================================
# Framework Registry
# =============================================================================

class FrameworkRegistry:
    """
    Registry for scientific frameworks and ontologies.
    """
    
    # Predefined frameworks
    FRAMEWORKS = {
        "ATN": {
            "name": "ATN Biomarker Framework",
            "domain": "Alzheimer",
            "components": ["A (Amyloid)", "T (Tau)", "N (Neurodegeneration)"],
            "description": "NIA-AA Research Framework for Alzheimer's biomarkers",
        },
        "MMSE": {
            "name": "Mini-Mental State Examination",
            "domain": "Cognitive Assessment",
            "components": ["orientation", "registration", "attention", "recall", "language"],
            "scale": "0-30",
        },
        "CDR": {
            "name": "Clinical Dementia Rating",
            "domain": "Dementia Assessment",
            "components": ["0 (Normal)", "0.5 (MCI)", "1 (Mild)", "2 (Moderate)", "3 (Severe)"],
        },
        "LOINC": {
            "name": "Logical Observation Identifiers Names and Codes",
            "domain": "Laboratory Tests",
        },
        "HGVS": {
            "name": "Human Genome Variation Society",
            "domain": "Genetic Variants",
        },
    }
    
    def __init__(self):
        self._frameworks: dict = self.FRAMEWORKS.copy()
    
    def register(self, name: str, domain: str, components: List[str] = None,
                 parent: str = None) -> str:
        """Register a new framework."""
        framework_id = f"FRAME-{len(self._frameworks) + 1:04d}"
        
        self._frameworks[name] = {
            "id": framework_id,
            "name": name,
            "domain": domain,
            "components": components or [],
            "parent": parent,
        }
        
        return framework_id
    
    def get(self, name: str) -> Optional[dict]:
        """Get framework by name."""
        return self._frameworks.get(name)
    
    def list(self) -> List[str]:
        """List all frameworks."""
        return list(self._frameworks.keys())
    
    def translate(self, value: float, from_framework: str, to_framework: str) -> dict:
        """Translate between assessment frameworks."""
        translations = {
            ("MMSE", "CDR"): {
                "24-30": 0,
                "18-23": 0.5,
                "10-17": 1,
                "5-9": 2,
                "0-4": 3,
            },
            ("SUVR", "Centiloid"): {
                "fn": lambda x: (x - 1.0) * 118.7,
            },
        }
        
        key = (from_framework, to_framework)
        if key in translations:
            trans = translations[key]
            if "fn" in trans:
                return {"value": trans["fn"](value), "confidence": 0.85}
        
        return {"value": value, "confidence": 0.5, "note": "No direct translation available"}


# =============================================================================
# Semantic Unit Registry
# =============================================================================

class SemanticUnitRegistry:
    """
    Registry for semantic units and conversion functions.
    """
    
    UNITS = {
        "pg/mL": {"factor": 1000, "to": "fg/mL", "type": "concentration"},
        "ng/mL": {"factor": 1000000, "to": "fg/mL", "type": "concentration"},
        "pg/L": {"factor": 1, "to": "fg/mL", "type": "concentration"},
        "ng/L": {"factor": 1000, "to": "fg/mL", "type": "concentration"},
        "SUVR": {"type": "ratio", "context": "PET"},
        "Centiloid": {"type": "score", "context": "PET"},
    }
    
    def convert(self, value: float, from_unit: str, to_unit: str) -> dict:
        """Convert between units."""
        if from_unit not in self.UNITS or to_unit not in self.UNITS:
            return {"error": "Unknown unit"}
        
        from_info = self.UNITS[from_unit]
        to_info = self.UNITS[to_unit]
        
        if from_info["type"] == "concentration" and to_info["type"] == "concentration":
            if from_info["to"] == to_info["to"]:
                # Both convert to same base unit
                base_value = value * from_info["factor"]
                final_value = base_value / to_info["factor"]
                return {"value": final_value, "confidence": 1.0}
        
        return {"value": value, "confidence": 0.5, "note": "Conversion may need context"}


if __name__ == "__main__":
    print("=" * 70)
    print("Scientific Interoperability Layer (SIL)")
    print("=" * 70)
    
    # Measurement example
    meas_reg = MeasurementRegistry()
    meas_id = meas_reg.register(
        entity="pTau217",
        value=0.34,
        unit="pg/mL",
        framework="Fujirebio Lumipulse"
    )
    
    print(f"\nMeasurement {meas_id}:")
    meas = meas_reg.get(meas_id)
    print(f"  {meas['entity']} = {meas['value']} {meas['unit']}")
    print(f"  Normalized: {meas['normalized_value']} {meas['normalized_unit']}")
    
    # Framework example
    frame_reg = FrameworkRegistry()
    print(f"\nFrameworks:")
    for name in ["ATN", "MMSE", "CDR"]:
        fw = frame_reg.get(name)
        print(f"  {name}: {fw['components']}")
    
    # Translation example
    print(f"\nTranslation MMSE 24 -> CDR:")
    trans = frame_reg.translate(24, "MMSE", "CDR")
    print(f"  {trans}")
    
    print("\n" + "=" * 70)
    print("SIL enables interoperability between heterogeneous scientific measurements")
    print("=" * 70)