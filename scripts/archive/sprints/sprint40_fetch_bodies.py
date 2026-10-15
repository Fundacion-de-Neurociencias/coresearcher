import subprocess, json

def get_issue_body(repo, num):
    r = subprocess.run(['gh', 'api', f'repos/{repo}/issues/{num}'], capture_output=True, text=True)
    if r.returncode == 0:
        return json.loads(r.stdout)
    return None

# MNE-Python decision/failure signals
mne_targets = {
    2975: "3rd try - eeglab events",
    2676: "eeglab reader (prior attempt)",
    1388: "cross frequency coupling (never merged)",
    615: "realtime decoding (never merged)",
    3310: "sklearn-style encoding decision",
    4414: "epochs metadata (4 reviewers)",
    2154: "concatenated epoch plot (303 comments)"
}

print("=== MNE-PYTHON ===")
for num, desc in mne_targets.items():
    issue = get_issue_body('mne-tools/mne-python', num)
    if issue:
        body = issue.get('body', '') or ''
        pr = issue.get('pull_request') is not None
        merged = "YES" if pr and issue.get('pull_request',{}).get('merged_at') else "NO" if pr else "N/A"
        print(f"\n#{num} ({desc}) | PR:{pr} | Merged:{merged}")
        print(f"Title: {issue['title']} | Comments:{issue['comments']}")
        # First 300 chars of body
        print(f"Body: {body[:300].replace(chr(10),' ')}")
    else:
        print(f"#{num}: failed")
