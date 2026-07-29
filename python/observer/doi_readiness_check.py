"""
DOI Readiness Check - Sprint 40
Validate ledger before public publication.
"""

import json
import os

def check_provenance(ledger):
    """Every observation must have source."""
    observations = ledger.get('observations', [])
    issues = []
    for obs in observations:
        if not obs.get('source'):
            issues.append(f"Missing source: {obs.get('observation_id')}")
    return {
        'passed': len(issues) == 0,
        'issues': issues
    }

def check_reproducibility(ledger):
    """No broken references, deterministic transforms."""
    obs_ids = {o['observation_id'] for o in ledger.get('observations', [])}
    evidence_obs = {e['observation_id'] for e in ledger.get('evidence_links', [])}
    missing = evidence_obs - obs_ids
    return {
        'passed': len(missing) == 0,
        'issues': [f"Broken reference: {m}" for m in missing]
    }

def check_privacy(ledger):
    """No private data or sensitive metadata."""
    obs_text = json.dumps(ledger.get('observations', []))
    if 'private' in obs_text.lower() or 'secret' in obs_text.lower():
        return {'passed': False, 'issues': ['Private data detected']}
    return {'passed': True, 'issues': []}

def check_scope(ledger):
    """Only observations, no interpretations."""
    # Check no learnings/patterns/contradictions in ledger_base
    interpretive_keys = ['learnings', 'patterns', 'contradictions', 'hypotheses']
    found = [k for k in interpretive_keys if k in ledger]
    if found:
        return {'passed': False, 'issues': [f'Interpretive content found: {found}']}
    return {'passed': True, 'issues': []}

def doi_readiness_check(ledger_path):
    with open(ledger_path) as f:
        ledger = json.load(f)
    
    provenance = check_provenance(ledger)
    reproducibility = check_reproducibility(ledger)
    privacy = check_privacy(ledger)
    scope = check_scope(ledger)
    
    all_passed = all([provenance['passed'], reproducibility['passed'], 
                      privacy['passed'], scope['passed']])
    
    return {
        'doi_ready': all_passed,
        'checks': {
            'provenance': provenance,
            'reproducibility': reproducibility,
            'privacy': privacy,
            'scope': scope
        }
    }

if __name__ == '__main__':
    result = doi_readiness_check('data/observatory/ledger_base.json')
    print(json.dumps(result, indent=2))
    with open('data/observatory/doi_readiness_report.json', 'w') as f:
        json.dump(result, f, indent=2)