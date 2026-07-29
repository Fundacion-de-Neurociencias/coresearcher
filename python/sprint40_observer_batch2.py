#!/usr/bin/env python3
"""
Sprint 40 - Fetch additional samples for observation batch 2
"""
import json, subprocess
from pathlib import Path

def fetch_issue_details(repo, number):
    r = subprocess.run(
        ['gh', 'api', f'repos/{repo}/issues/{number}'],
        capture_output=True, text=True, encoding='utf-8'
    )
    if r.returncode == 0:
        return json.loads(r.stdout)
    return None

def fetch_comments(repo, number):
    r = subprocess.run(
        ['gh', 'api', f'repos/{repo}/issues/{number}/comments?per_page=100'],
        capture_output=True, text=True, encoding='utf-8'
    )
    if r.returncode == 0:
        return json.loads(r.stdout)
    return []

def summarize(issue, comments, max_comments=20):
    lines = []
    lines.append(f"# {issue['title']} (#{issue['number']})")
    lines.append(f"URL: {issue['html_url']}")
    lines.append(f"State: {issue['state']} | PR: {'YES' if 'pull_request' in issue else 'NO'}")
    lines.append(f"Comments: {issue['comments']} | Created: {issue['created_at']} | Closed: {issue['closed_at']}")
    lines.append("")
    body = issue.get('body', '') or ''
    lines.append("## Body (first 1000 chars)")
    lines.append(body[:1000])
    lines.append("")
    lines.append("## Comments")
    for i, c in enumerate(comments[:max_comments]):
        user = c.get('user', {}).get('login', 'unknown')
        cbody = c.get('body', '') or ''
        lines.append(f"\n--- Comment {i+1} by {user} ---")
        lines.append(cbody[:1000])
    lines.append("\n--- END ---")
    return "\n".join(lines)

if __name__ == '__main__':
    # Batch 2: next items from each repo
    candidates = {
        'mne-tools/mne-python': [3205, 580, 2710, 776, 1261, 379, 1462, 1629, 3842, 7070, 2304],
        'nilearn/nilearn': [219, 651, 693, 2738, 2000, 3525, 589, 698, 3173, 2946],
        'bids-standard/pybids': [308, 552, 746, 840, 395, 36, 547, 100, 649, 487, 555]
    }
    
    for repo, issues in candidates.items():
        repo_name = repo.replace('/', '_')
        for num in issues:
            print(f"Fetching {repo} #{num}...")
            issue = fetch_issue_details(repo, num)
            if not issue:
                print(f"  Failed to fetch {repo} #{num}")
                continue
            comments = fetch_comments(repo, num)
            summary = summarize(issue, comments)
            out_path = Path(f'data/sprint40_samples/{repo_name}_{num}.md')
            with open(out_path, 'w', encoding='utf-8') as f:
                f.write(summary)
            print(f"  Saved {len(summary)} chars")
