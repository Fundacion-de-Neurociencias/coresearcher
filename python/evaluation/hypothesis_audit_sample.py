"""
Hypothesis Audit Sample - Sprint 22
Manual audit of hypotheses to validate Type C/D classification.
"""

import json
from pathlib import Path

# Security tier: PRIVATE
SECURITY_TIER = "PRIVATE"


def audit_hypotheses_sample():
    """
    Audit a sample of hypotheses to determine if they are truly Type C/D.
    
    This addresses the critical question: Are our hypotheses genuine discoveries
    or just clever rephrasings?
    """
    # Sample hypotheses from the benchmark (expected to be C/D)
    samples = [
        # Type B candidates (from current system patterns)
        {
            "id": "SAMPLE-B-001",
            "statement": "The effect of amyloid-beta on disease progression is mediated by an unrecognized threshold mechanism that connects to patient outcomes through a hidden feedback loop.",
            "domain": "Alzheimer's"
        },
        {
            "id": "SAMPLE-B-002", 
            "statement": "Contradiction detected: 'Why do striatal neurons die before cortical neurons'. This suggests a hidden mediator that resolves the paradox through a threshold-dependent mechanism.",
            "domain": "Huntington's"
        },
        {
            "id": "SAMPLE-B-003",
            "statement": "The relationship between amyloid and tau pathology becomes pathological when combined with a circadian disruption in microglial phagocytic rhythm.",
            "domain": "Neuroinflammation"
        },
        
        # Type C candidates (genuine inference)
        {
            "id": "SAMPLE-C-001",
            "statement": "The pleiotropic effects of neurodevelopmental risk genes are mediated by an unknown regulatory switch in critical period timing that determines whether synaptic overgrowth or undergrowth occurs.",
            "domain": "Neurodevelopment"
        },
        {
            "id": "SAMPLE-C-002",
            "statement": "Tissue specificity in autoimmunity is not determined by HLA binding affinity alone but by a threshold-dependent process where self-antigens become immunogenic when combined with specific stress-induced modifications.",
            "domain": "Autoimmune"
        },
        
        # Type D candidates (true discovery/reframing)
        {
            "id": "SAMPLE-D-001",
            "statement": "What if amyloid-beta deposition is not the primary cause but a protective response to early-stage neurodegeneration, attempting to sequester toxic oligomers?",
            "domain": "Alzheimer's"
        },
        {
            "id": "SAMPLE-D-002",
            "statement": "What if the lack of phenotype in some genetic knockouts is not due to redundancy but to an adaptive rewiring that creates an emergent property only visible under stress conditions?",
            "domain": "Rare Diseases"
        }
    ]
    
    output_path = Path("evaluation/results/hypothesis_audit_sample.json")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_path, 'w') as f:
        json.dump({
            "title": "Manual Hypothesis Audit Sample",
            "purpose": "Expert validation of Type C/D classification",
            "samples": samples,
            "question": "Would an expert say 'No había pensado en esto' about this hypothesis?",
            "instructions": [
                "Rate each hypothesis on surprise factor (1-5)",
                "Rate novelty of mechanism (1-5)",
                "Rate testability (1-5)",
                "Final classification: A/B/C/D"
            ]
        }, f, indent=2)
    
    print("Hypothesis audit sample saved to:", output_path)
    print("\nSamples for expert review:")
    for s in samples:
        print(f"\n[{s['id']}] {s['domain']}")
        print(f"  {s['statement'][:100]}...")
    
    return samples


class ParticipationLayer:
    """
    Sprint 22.5: Participation Layer
    
    Scientific primitives for collective knowledge validation.
    Not social signals - scientific validation signals.
    """
    
    PARTICIPATION_ACTIONS = [
        "SUPPORT",      # I endorse this claim/hypothesis
        "CHALLENGE",    # I dispute this claim/hypothesis
        "REPLICATE",    # I've reproduced this finding
        "CONFIRM",      # Empirical support found
        "REJECT",       # Empirical refutation found
        "COMMENT",      # Scientific discussion
        "REVIEW",       # Peer review contribution
        "FORK_HYPOTHESIS",  # Create variant hypothesis
    ]
    
    def __init__(self):
        self.registry_path = Path("knowledge/registry/participation.json")
        self.registry_path.parent.mkdir(parents=True, exist_ok=True)
    
    def record_action(self, hypothesis_id: str, action: str, researcher_id: str, evidence: str = None):
        """Record a participation action on a hypothesis."""
        if action not in self.PARTICIPATION_ACTIONS:
            raise ValueError(f"Invalid action: {action}")
        
        # Load existing registry
        if self.registry_path.exists():
            with open(self.registry_path, 'r') as f:
                registry = json.load(f)
        else:
            registry = {"actions": []}
        
        action_record = {
            "hypothesis_id": hypothesis_id,
            "action": action,
            "researcher_id": researcher_id,
            "evidence": evidence,
            "timestamp": __import__('datetime').datetime.now().isoformat()
        }
        
        registry["actions"].append(action_record)
        
        with open(self.registry_path, 'w') as f:
            json.dump(registry, f, indent=2)
        
        return action_record
    
    def get_trust_score(self, hypothesis_id: str) -> float:
        """Calculate trust score based on participation signals."""
        if not self.registry_path.exists():
            return 0.5
            
        with open(self.registry_path, 'r') as f:
            registry = json.load(f)
        
        actions = [a for a in registry["actions"] if a["hypothesis_id"] == hypothesis_id]
        
        if not actions:
            return 0.5
        
        # Weighted scoring
        weights = {"CONFIRM": 2.0, "REPLICATE": 1.5, "SUPPORT": 1.0, 
                  "REJECT": -2.0, "CHALLENGE": -1.0}
        
        score = sum(weights.get(a["action"], 0) for a in actions) / len(actions)
        return max(0.0, min(1.0, 0.5 + score))


if __name__ == "__main__":
    print("=" * 70)
    print("PARTICIPATION LAYER - Sprint 22.5")
    print("=" * 70)
    
    # Show samples
    audit_hypotheses_sample()
    
    # Demonstrate participation
    layer = ParticipationLayer()
    
    print("\nParticipation Actions Available:")
    for action in ParticipationLayer.PARTICIPATION_ACTIONS:
        print(f"  - {action}")
    
    print("\n" + "=" * 70)
    print("Trust signals should come from:")
    print("  CLAIM validado/refutado")
    print("  FINDING replicado")
    print("  HIPÓTESIS propuesta/descartada")
    print("  PREDICCIÓN confirmada")
    print("=" * 70)