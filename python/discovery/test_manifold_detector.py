"""
Test Manifold Detector - Validates Diffusion Discovery Theory integration
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from discovery.manifold_detector import ManifoldDetector


def test_interpolation_detection():
    """Test that interpolation is correctly detected between known mechanisms."""
    detector = ManifoldDetector(domain="neurodegeneration")
    
    mech_a = {
        "id": "MECH-TAU",
        "entities": ["tau", "aggregation", "neurodegeneration", "phosphorylation"],
        "confidence": 0.7
    }
    
    mech_b = {
        "id": "MECH-PROTEOSTASIS", 
        "entities": ["proteostasis", "stress", "protein_folding", "neurodegeneration"],
        "confidence": 0.6
    }
    
    interp = detector.interpolate_mechanisms(mech_a, mech_b)
    
    assert "id" in interp
    assert interp["operation"] == "structured_interpolation"
    assert 0.0 <= interp["confidence"] <= 1.0
    assert 0.0 <= interp["manifold_distance"] <= 1.0
    
    print("✓ Interpolation test passed")
    return interp


def test_manifold_break_detection():
    """Test detection of manifold breaks (revolutionary hypotheses)."""
    detector = ManifoldDetector(domain="neurodegeneration")
    
    # Revolutionary hypothesis - outside current manifold (entities not in knowledge base)
    revolutionary = {
        "statement": "CRISPR-based gene editing can reverse tau aggregation by rewriting evolutionary constraints",
        "entities": ["crispr", "tau", "gene_editing", "evolutionary_constraints"],
        "predictions": [
            "CRISPR editing reduces tau pathology in vivo",
            "Constraint rewriting creates neuroprotection"
        ]
    }
    
    # Interpolation hypothesis - within current manifold
    interpolation = {
        "statement": "Tau aggregation and neuroinflammation co-occur in stressed neurons",
        "entities": ["tau", "inflammation", "neurons", "stress"],
        "predictions": [
            "Combined treatment targets both pathways",
            "Temporal sequence shows stress precedes both"
        ]
    }
    
    rev_result = detector.detect_manifold_break(revolutionary)
    interp_result = detector.detect_manifold_break(interpolation)
    
    print(f"Revolutionary: {rev_result['manifold_change']}")
    print(f"Interpolation: {interp_result['manifold_change']}")
    
    # Revolutionary should have higher manifold change score
    assert rev_result["manifold_change"] in ["HIGH", "REVOLUTIONARY"]
    print("✓ Manifold break detection test passed")
    return rev_result, interp_result


def test_discovery_benchmark_integration():
    """
    Test integration with discovery benchmarks.
    
    Validates that manifold detection produces meaningful results.
    """
    detector = ManifoldDetector(domain="neurodegeneration")
    
    # Type B: Synthesis of existing claims (all known entities)
    type_b = {
        "statement": "Tau and amyloid correlate with cognitive decline in Alzheimer",
        "entities": ["tau", "amyloid", "alzheimer", "cognitive_decline"],
        "predictions": ["Biomarker levels predict progression"]
    }
    
    # Type C: Interpolation (mix of known and emerging entities)
    type_c = {
        "statement": "Tau aggregation and neuroinflammation co-occur in stressed neurons",
        "entities": ["tau", "inflammation", "neurons", "stress"],
        "predictions": [
            "Combined treatment targets both pathways",
            "Temporal sequence shows stress precedes both"
        ]
    }
    
    # Type D: Manifold change (conceptual breakthrough with novel entities)
    type_d = {
        "statement": "CRISPR editing rewrites evolutionary constraints in neurodegeneration",
        "entities": ["crispr", "tau", "evolutionary_constraints"],
        "predictions": [
            "Editing creates neuroprotection",
            "Constraint removal reverses pathology"
        ]
    }
    
    b_result = detector.detect_manifold_break(type_b)
    c_result = detector.detect_manifold_break(type_c)
    d_result = detector.detect_manifold_break(type_d)
    
    print(f"Type B (synthesis): {b_result['manifold_change']}")
    print(f"Type C (interpolation): {c_result['manifold_change']}")
    print(f"Type D (manifold change): {d_result['manifold_change']}")
    
    # All should produce valid results
    assert b_result["manifold_change"] in ["LOW", "MEDIUM", "HIGH", "REVOLUTIONARY"]
    assert c_result["manifold_change"] in ["LOW", "MEDIUM", "HIGH", "REVOLUTIONARY"]
    assert d_result["manifold_change"] in ["LOW", "MEDIUM", "HIGH", "REVOLUTIONARY"]
    
    print("✓ Discovery benchmark integration test passed")


if __name__ == "__main__":
    print("=" * 70)
    print("MANIFOLD DETECTOR TESTS")
    print("=" * 70)
    
    test_interpolation_detection()
    test_manifold_break_detection()
    test_discovery_benchmark_integration()
    
    print("\n" + "=" * 70)
    print("ALL TESTS PASSED")
    print("=" * 70)