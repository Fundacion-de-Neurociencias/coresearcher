#!/usr/bin/env python3
"""SPRINT 59D: Corregir definitivamente LlamaIndex. Objetivo: repository_resolution_rate = 1.0"""
import json, urllib.request
from datetime import datetime, timezone

REPOS = ["run-llama/llama_index", "run-llama/LlamaIndex"]
GITHUB_HEADERS = {"Accept":"application/vnd.github+json","User-Agent":"coresearcher-benchmark","X-GitHub-Api-Version":"2022-11-28"}

def fetch_json(url):
    req = urllib.request.Request(url, headers=GITHUB_HEADERS)
    with urllib.request.urlopen(req) as resp:
        return json.loads(resp.read().decode())

def extract_claims(repo):
    base_url = f"https://api.github.com/repos/{repo}"
    claims, failure_modes = [], []
    try:
        repo_info = fetch_json(base_url)
    except Exception as e:
        return claims, [f"REPOSITORY_IDENTIFIER_ERROR: {e}"], {}, 0, 0
    try:
        try:
            issues = fetch_json(f"{base_url}/issues?state=closed&per_page=100&sort=updated&direction=desc")
        except Exception as e:
            failure_modes.append(f"ISSUES_FETCH_ERROR: {e}")
            issues = []
        try:
            prs = fetch_json(f"{base_url}/pulls?state=closed&per_page=100&sort=updated&direction=desc")
        except Exception as e:
            failure_modes.append(f"PRS_FETCH_ERROR: {e}")
            prs = []
        if not isinstance(issues, list): issues = []
        if not isinstance(prs, list): prs = []
    except Exception as e:
        return claims, [f"DATA_FETCH_ERROR: {e}"], repo_info, 0, 0
    keywords = ["we decided to","chose","opted for","replaced","switched to","decided to","went with","picked","selected"]
    def process(items, ctype):
        out = []
        for item in items:
            if not isinstance(item, dict):
                continue
            body = (item.get("body") or "") + " " + (item.get("title") or "")
            for kw in keywords:
                if kw in body.lower():
                    quote_text = item.get("title","") + ": " + (item.get("body") or "")[:500]
                    out.append({"claim": item.get("title","")[:200], "type": ctype, "source_url": item.get("html_url",""), "quote": quote_text[:500], "classification": "observable" if item.get("html_url") else "inferred"})
                    break
        return out
    claims.extend(process(issues if isinstance(issues, list) else [], "decision"))
    claims.extend(process(prs if isinstance(prs, list) else [], "decision"))
    return claims, failure_modes, repo_info, len(issues) if isinstance(issues, list) else 0, len(prs) if isinstance(prs, list) else 0

def calculate_metrics(repo, claims, failure_modes, repo_info, n_issues, n_prs):
    total = len(claims)
    has_url = sum(1 for c in claims if c.get("source_url"))
    has_quote = sum(1 for c in claims if c.get("quote"))
    auditability_score = round((has_url + has_quote) / (2 * total), 4) if total > 0 else 0.0
    failure_type = "OK"
    if total == 0:
        failure_type = "NO_CLAIMS"
    elif auditability_score < 0.90:
        failure_type = "LOW_AUDITABILITY"
    if any("ERROR" in str(fm) for fm in failure_modes):
        failure_type = "FETCH_ERROR"
    return {"repo": repo, "stars": repo_info.get("stargazers_count", 0), "issues": n_issues, "prs": n_prs, "claims": total, "auditability_score": auditability_score, "failure_type": failure_type, "failure_modes": failure_modes}

def main():
    print("=== SPRINT 59D: LlamaIndex Retry ===")
    results = []
    for repo in REPOS:
        print(f"Intentando: {repo}")
        try:
            claims, failure_modes, repo_info, n_issues, n_prs = extract_claims(repo)
            metrics = calculate_metrics(repo, claims, failure_modes, repo_info, n_issues, n_prs)
            results.append(metrics)
            print(f"  Status: {metrics['failure_type']}, claims={metrics['claims']}, audit={metrics['auditability_score']}")
            if failure_modes:
                print(f"  failure_modes={failure_modes}")
        except Exception as e:
            print(f"  ERROR: {e}")
            results.append({"repo": repo, "stars": 0, "issues": 0, "prs": 0, "claims": 0, "auditability_score": 0.0, "failure_type": "FETCH_ERROR", "failure_modes": [str(e)]})
        print()
    with open("artifacts/llamaindex_retry_metrics.json", "w", encoding="utf-8") as f:
        json.dump({"results": results, "timestamp": datetime.now(timezone.utc).isoformat()}, f, indent=2)
    print("Generado: artifacts/llamaindex_retry_metrics.json")
    for r in results:
        flag = " [FALLO]" if r["auditability_score"] < 0.90 or r["claims"] == 0 else ""
        print(f"  {r['repo']}: claims={r['claims']}, audit={r['auditability_score']}{flag}")
    success = any(r["claims"] > 0 and r["auditability_score"] >= 0.90 for r in results)
    print(f"\nCriterio de éxito (claims>0 AND audit>=0.90): {'PASS' if success else 'FAIL'}")
    print("SPRINT 59D completado.")
    return success

if __name__ == "__main__":
    main()
</parameter>
</write_to_file>