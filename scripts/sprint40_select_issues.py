#!/usr/bin/env python3
"""
Sprint 40 - Decision Observation Issue Selector (fast)

Selects closed items (issues+PRs) per repo meeting:
- Closed
- >= 10 comments  
- Duration > 7 days (checked later)
- >= 2 participants (checked later)

Outputs: data/sprint40_candidates.json
"""

import json
import subprocess
from datetime import datetime
from pathlib import Path


def parse_iso_date(date_str):
    if not date_str:
        return None
    date_str = date_str.replace('Z', '+00:00')
    try:
        return datetime.fromisoformat(date_str)
    except ValueError:
        return None


def fetch_candidates(repo, include_prs=True, max_items=100):
    """Fetch closed issues/PRs with >= 10 comments sorted by comments desc."""
    r = subprocess.run(
        ['gh', 'api',
         f'repos/{repo}/issues?state=closed&sort=comments&direction=desc&per_page={max_items}'],
        capture_output=True, text=True, encoding='utf-8'
    )
    if r.returncode != 0:
        print(f"  ERROR: {r.stderr[:200]}")
        return []
    
    all_items = json.loads(r.stdout)
    items = []
    for raw in all_items:
        if not include_prs and 'pull_request' in raw:
            continue
        if raw.get('comments', 0) >= 10:
            created = parse_iso_date(raw.get('created_at'))
            closed = parse_iso_date(raw.get('closed_at'))
            duration_days = 0
            if created and closed:
                duration_days = (closed - created).total_seconds() / 86400
            
            items.append({
                'number': raw['number'],
                'title': raw['title'],
                'state': raw.get('state'),
                'comments': raw.get('comments', 0),
                'created_at': raw.get('created_at'),
                'closed_at': raw.get('closed_at'),
                'duration_days': duration_days,
                'is_pr': 'pull_request' in raw
            })
    
    return items


def main():
    repos = [
        'mne-tools/mne-python',
        'nilearn/nilearn',
        'bids-standard/pybids'
    ]
    
    all_candidates = {}
    
    for repo in repos:
        raw_items = fetch_candidates(repo, include_prs=True, max_items=100)
        raw_items.sort(key=lambda x: x.get('comments', 0), reverse=True)
        
        selected = raw_items[:30]
        all_candidates[repo] = selected
        print(f"{repo}: {len(selected)} items selected")
    
    Path('data').mkdir(exist_ok=True)
    output_path = Path('data/sprint40_candidates.json')
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(all_candidates, f, indent=2, ensure_ascii=False)
    
    print(f"\nSaved candidates to {output_path}")


if __name__ == '__main__':
    main()
