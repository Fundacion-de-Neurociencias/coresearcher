#!/usr/bin/env python3
"""
Sprint 40 - Decision Observation Pilot
Fetches issue data for manual classification.
"""

import json
import subprocess
from pathlib import Path

def fetch_issue_details(repo, number):
    """Fetch full issue/PR details including body."""
    r = subprocess.run(
        ['gh', 'api', f'repos/{repo}/issues/{number}'],
        capture_output=True, text=True, encoding='utf-8'
    )
    if r.returncode != 0:
        return None
    return json.loads(r.stdout)


def fetch_comments(repo, number, max_comments=20):
    """Fetch up to max_comments for an issue."""
    r = subprocess.run(
        ['gh', 'api', f'repos/{repo}/issues/{number}/comments?per_page={max_comments}'],
        capture_output=True, text=True, encoding='utf-8'
    )
    if r.returncode != 0:
        return []
    return json.loads(r.stdout)


def summarize_for_observation(issue, comments, max_comments=20):
    """Create a brief human-readable summary for manual classification."""
    lines = []
    lines.append(f"# {issue['title']} (#{issue['number']})")
    lines.append(f"URL: {issue['html_url']}")
    lines.append(f"State: {issue['state']} | PR: {'YES' if 'pull_request' in issue else 'NO'}")
    lines.append(f"Comments: {issue['comments']} | Created: {issue['created_at']} | Closed: {issue['closed_at']}")
    lines.append("")
    lines.append("## Body (first 1000 chars)")
    body = issue.get('body', '') or ''
    lines.append(body[:1000])
    lines.append("")
    lines.append("## Comments (first 1000 chars each)")
    for i, c in enumerate(comments[:max_comments]):
        user = c.get('user', {}).get('login', 'unknown')
        cbody = c.get('body', '') or ''
        lines.append(f"\n--- Comment {i+1} by {user} ---")
        lines.append(cbody[:1000])
    lines.append("")
    lines.append("--- END ---")
    return "\n".join(lines)


if __name__ == '__main__':
    candidates = json.load(open('data/sprint40_candidates.json'))
    Path('data/sprint40_samples').mkdir(exist_ok=True)
    
    for repo, items in candidates.items():
        repo_name = repo.replace('/', '_')
        for i, item in enumerate(items[:5] if repo == 'mne-tools/mne-python' else items[:3]):
            print(f"Fetching {repo} #{item['number']}...")
            issue = fetch_issue_details(repo, item['number'])
            if not issue:
                continue
            comments = fetch_comments(repo, item['number'])
            summary = summarize_for_observation(issue, comments)
            out_path = Path('data/sprint40_samples') / f"{repo_name}_{item['number']}.md"
            with open(out_path, 'w', encoding='utf-8') as f:
                f.write(summary)
            print(f"  Saved to {out_path} ({len(summary)} chars)")
