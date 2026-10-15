"""
Validate if observations generate reproducible learnings.
Two independent reviewers should reach same conclusions.
"""

import json

def validate_ledger_reproducibility():
    # Load the ledger components
    with open('data/observatory/adni_structured_observations.json') as f:
        observations = json.load(f)
    
    with open('data/observatory/adni_structural_learnings.json') as f:
        learnings = json.load(f)
    
    with open('data/observatory/adni_evidence_catalog.json') as f:
        evidence = json.load(f)
    
    # Check traceability: each learning must derive from observations
    traceability_check = {}
    for learning in learnings:
        derived_from = learning.get('derived_from', [])
        all_valid = all(
            any(o['observation_id'] == obs_id for o in observations)
            for obs_id in derived_from
        )
        traceability_check[learning['learning_id']] = {
            'derives_from': derived_from,
            'all_sources_exist': all_valid,
            'reproducible': all_valid  # True if sources exist
        }
    
    # Check evidence strength diversity
    evidence_strengths = [e['evidence_strength'] for e in evidence]
    strength_distribution = {}
    for s in evidence_strengths:
        strength_distribution[s] = strength_distribution.get(s, 0) + 1
    
    return {
        'total_observations': len(observations),
        'total_learnings': len(learnings),
        'total_evidence': len(evidence),
        'traceability': traceability_check,
        'evidence_strength_distribution': strength_distribution,
        'reproducibility_status': 'partial'  # Not fully validated yet
    }

if __name__ == '__main__':
    result = validate_ledger_reproducibility()
    print(json.dumps(result, indent=2))
    with open('data/observatory/reproducibility_validation.json', 'w') as f:
        json.dump(result, f, indent=2)