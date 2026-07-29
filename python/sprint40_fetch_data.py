import subprocess, json, sys

def fetch_issues(repo, count=30):
    r = subprocess.run(['gh', 'api', f'repos/{repo}/issues?state=all&sort=comments&direction=desc&per_page={count}'], capture_output=True, text=True)
    if r.returncode != 0:
        print(f"ERROR fetching {repo}: {r.stderr[:200]}")
        return []
    return json.loads(r.stdout)

def fetch_prs(repo, count=15):
    r = subprocess.run(['gh', 'api', f'repos/{repo}/pulls?state=all&sort=popularity&direction=desc&per_page={count}'], capture_output=True, text=True)
    if r.returncode != 0:
        print(f"ERROR fetching PRs for {repo}: {r.stderr[:200]}")
        return []
    return json.loads(r.stdout)

repos = ['mne-tools/mne-python', 'nilearn/nilearn', 'bids-standard/pybids']

for repo in repos:
    print(f"\n{'='*70}")
    print(f"REPO: {repo}")
    print(f"{'='*70}")
    
    issues = fetch_issues(repo, 25)
    print(f"\nFound {len(issues)} top-commented issues")
    print(f"{'='*50}")
    for i in issues:
        is_pr = "PR" if i.get('pull_request') else "ISSUE"
        labels = ", ".join(l['name'] for l in i.get('labels', [])[:3])
        signals = []
        title = i['title']
        for kw in ['WIP', 'MRG', 'ENH', 'RFC', 'FIX', 'DEP', 'DISCUSS', 'refactor', 'fail', 'try', 'propos', 'altern', 'decid', 'debate', 'contro', 'quest']:
            if kw.lower() in title.lower():
                signals.append(kw)
        sig = f"[{' '.join(signals)}]" if signals else ""
        print(f"  #{i['number']} ({i['comments']}c, {i['state']}) {is_pr} {sig}")
        print(f"  T: {title[:130]}")
        if labels:
            print(f"  L: {labels}")
        print()
