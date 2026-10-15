"""
Sprint 38 - Independent Reviewer Validation
Test if two independent reviewers reach same learnings from same observations.
"""

import json
import hashlib

# Reviewer 1 logic (current)
def reviewer_1(observations):
    # Simplified: group by category and infer learnings
    learnings = {}
    for obs in observations:
        cat = obs.get('category', '')
        if cat not in learnings:
            learnings[cat] = []
        learnings[cat].append(obs['observation_id'])
    return learnings

# Reviewer 2 logic (alternative)
def reviewer_2(observations):
    # Different logic: focus on evidence type combinations
    learnings = {}
    for obs in observations:
        ev_type = obs.get('evidence_type', '')
        if ev_type not in learnings:
            learnings[ev_type] = []
        learnings[ev_type].append(obs['observation_id'])
    return learnings

# Compare reviewers
def compare_reviewers(learned_a, learned_b):
    agreement = {}
    all_keys = set(learned_a.keys()) | set(learned_b.keys())
    for key in all_keys:
        set_a = set(learned_a.get(key, []))
        set_b = set(learned_b.get(key, []))
        agreement[key] = {
            'reviewer_1': len(set_a),
            'reviewer_2': len(set_b),
            'intersection': len(set_a & set_b),
            'union': len(set_a | set_b),
            'jaccard': len(set_a & set_b) / (len(set_a | set_b) or 1)
        }
    return agreement

if __name__ == '__main__':
    with open('data/observatory/adni_structured_observations.json') as f:
        observations = json.load(f)
    
    # Run both reviewers
    learned_1 = reviewer_1(observations)
    learned_2 = reviewer_2(observations)
    
    # Compare
    comparison = compare_reviewers(learned_1, learned_2)
    
    result = {
        'total_observations': len(observations),
        'reviewer_1_clusters': len(learned_1),
        'reviewer_2_clusters': len(learned_2),
        'agreement_matrix': comparison,
        'interpretation_risk': any(v['jaccard'] < 0.5 for v in comparison.values())
    }
    
    print(json.dumps(result, indent=2))
    with open('data/observatory/reviewer_comparison.json', 'w') as f:
        json.dump(result, f, indent=2)