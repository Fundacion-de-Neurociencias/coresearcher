#!/usr/bin/env python3
"""
Sprint 59: Cross-Repository Benchmark

Runs the evidence-anchored pipeline on 4 repositories:
- LangGraph
- LangChain
- LlamaIndex
- Haystack

Generates individual metrics + cross-repo comparison.
"""

import json
import re
import urllib.request

REPOS_BY_CATEGORY = {
    "A_frameworks_ia": [
        "langchain-ai/langgraph",
        "langchain-ai/langchain",
        "run-llama/LlamaIndex",
        "deepset-ai/haystack",
    ],
    "B_proyectos_cientificos": [
        "scikit-learn/scikit-learn",
        "pytorch/pytorch",
        "jax-ml/jax",
        "nilearn/nilearn",
    ],
    "C_bibliotecas_pequenas": [
        "pallets/flask",
        "psf/requests",
        "pallets/click",
        "marshmallow-code/marshmallow",
    ],
    "D_archivados": [
        "google/guetzli",
        "esimov/caire",
        "request/request",
        "bitly/segment",
    ],
    "E_baja_actividad": [
        "tj/commander.js",
        "substack/gray-matter",
        "pallets/itsdangerous",
        "jashkenas/underscore",
    ],
}

REPOS = [
    "langchain-ai/langgraph",
    "langchain-ai/langchain",
    "run-llama/LlamaIndex",
    "deepset-ai/haystack",
]

def fetch_json(url):
    req = urllib.request.Request(url, headers={"Accept": "application/vnd.github+json", "User-Agent": "coresearcher"})
    with urllib.request.urlopen(req) as resp:
        return json.loads(resp.read().decode())

def fetch_paginated(url, max_pages=5):
    results = []
    for page in range(1, max_pages + 1):
        url_with_page = url + (f"&page={page}" if "?" in url else f"?page={page}")
        try:
            data = fetch_json(url_with_page)
            if isinstance(data, list) and len(data) > 0:
                results.extend(data)
            else:
                break
        except Exception as e:
            print(f"  Error page {page}: {e}")
            break
    return results

def classify_claim(claim_text, source_url, quote):
    if quote and source_url:
        if claim_text.lower() in quote.lower():
            return "observable"
        else:
            return "derivable"
    elif source_url:
        return "derivable"
    else:
        return "inferred"

def extract_claims(repo):
    """Extract claims with evidence anchors from a GitHub repo."""
    base_url = f"https://api.github.com/repos/{repo}"
    claims = []

    # Fetch data
    issues = fetch_paginated(f"{base_url}/issues?state=closed&per_page=100")
    prs = fetch_paginated(f"{base_url}/pulls?state=closed&per_page=100")
    open_issues = fetch_paginated(f"{base_url}/issues?state=open&per_page=50")

    decision_keywords = ["we decided to", "chose", "opted for", "replaced", "switched to", "decided to", "went with"]
    alt_keywords = ["we could", "we considered", "instead of", "rather than", "alternative"]
    criteria_keywords = ["for performance", "for simplicity", "for compatibility", "because", "since", "due to"]
    evidence_keywords = ["benchmark", "test", "performance", "latency", "memory", "paper", "data", "metric"]

    # Decisions from issues
    for issue in issues:
        body = (issue.get("body") or "") + " " + (issue.get("title") or "")
        body_lower = body.lower()
        for kw in decision_keywords:
            if kw in body_lower:
                sentences = re.split(r'[.!?]+', body)
                for sentence in sentences:
                    if kw in sentence.lower():
                        quote = issue.get("title", "") + ": " + (issue.get("body") or "")[:500]
                        claims.append({
                            "claim": sentence.strip()[:200],
                            "type": "decision",
                            "source_url": issue.get("html_url", ""),
                            "quote": quote[:500],
                            "classification": classify_claim(sentence.strip()[:200], issue.get("html_url", ""), quote),
                        })
                        break
                break

    # Decisions from PRs
    for pr in prs:
        body = (pr.get("body") or "") + " " + (pr.get("title") or "")
        body_lower = body.lower()
        for kw in decision_keywords:
            if kw in body_lower:
                sentences = re.split(r'[.!?]+', body)
                for sentence in sentences:
                    if kw in sentence.lower():
                        quote = pr.get("title", "") + ": " + (pr.get("body") or "")[:500]
                        claims.append({
                            "claim": sentence.strip()[:200],
                            "type": "decision",
                            "source_url": pr.get("html_url", ""),
                            "quote": quote[:500],
                            "classification": classify_claim(sentence.strip()[:200], pr.get("html_url", ""), quote),
                        })
                        break
                break

    # Alternatives
    for issue in issues:
        body = (issue.get("body") or "") + " " + (issue.get("title") or "")
        body_lower = body.lower()
        for kw in alt_keywords:
            if kw in body_lower:
                sentences = re.split(r'[.!?]+', body)
                for sentence in sentences:
                    if kw in sentence.lower():
                        quote = issue.get("title", "") + ": " + (issue.get("body") or "")[:500]
                        claims.append({
                            "claim": sentence.strip()[:200],
                            "type": "alternative",
                            "source_url": issue.get("html_url", ""),
                            "quote": quote[:500],
                            "classification": classify_claim(sentence.strip()[:200], issue.get("html_url", ""), quote),
                        })
                        break
                break

    # Criteria
    for issue in issues:
        body = (issue.get("body") or "") + " " + (issue.get("title") or "")
        body_lower = body.lower()
        for kw in criteria_keywords:
            if kw in body_lower:
                sentences = re.split(r'[.!?]+', body)
                for sentence in sentences:
                    if kw in sentence.lower():
                        quote = issue.get("title", "") + ": " + (issue.get("body") or "")[:500]
                        claims.append({
                            "claim": sentence.strip()[:200],
                            "type": "criterion",
                            "source_url": issue.get("html_url", ""),
                            "quote": quote[:500],
                            "classification": classify_claim(sentence.strip()[:200], issue.get("html_url", ""), quote),
                        })
                        break
                break

    # Evidence
    for issue in issues:
        body = (issue.get("body") or "") + " " + (issue.get("title") or "")
        body_lower = body.lower()
        for kw in evidence_keywords:
            if kw in body_lower:
                sentences = re.split(r'[.!?]+', body)
                for sentence in sentences:
                    if kw in sentence.lower():
                        quote = issue.get("title", "") + ": " + (issue.get("body") or "")[:500]
                        claims.append({
                            "claim": sentence.strip()[:200],
                            "type": "evidence",
                            "source_url": issue.get("html_url", ""),
                            "quote": quote[:500],
                            "classification": classify_claim(sentence.strip()[:200], issue.get("html_url", ""), quote),
                        })
                        break
                break

    # Gaps (open issues)
    for issue in open_issues:
        quote = issue.get("title", "") + ": " + (issue.get("body") or "")[:500]
        claims.append({
            "claim": issue.get("title", "")[:200],
            "type": "gap",
            "source_url": issue.get("html_url", ""),
            "quote": quote[:500],
            "classification": "unknown",
        })

    return claims

def calculate_metrics(repo, claims):
    total = len(claims)
    observable = sum(1 for c in claims if c["classification"] == "observable")
    derivable = sum(1 for c in claims if c["classification"] == "derivable")
    inferred = sum(1 for c in claims if c["classification"] == "inferred")
    unknown = sum(1 for c in claims if c["classification"] == "unknown")
    has_url = sum(1 for c in claims if c["source_url"])
    has_quote = sum(1 for c in claims if c["quote"])

    return {
        "repo": repo,
        "total_claims": total,
        "observable_claims": observable,
        "derivable_claims": derivable,
        "inferred_claims": inferred,
        "unknown_claims": unknown,
        "auditability_score": round((has_url + has_quote) / (2 * total), 4) if total > 0 else 0.0,
        "evidence_coverage": round((total - inferred - unknown) / total, 4) if total > 0 else 0.0,
        "observable_ratio": round(observable / total, 4) if total > 0 else 0.0,
        "total_gaps": unknown,
    }

def main():
    print("=== Sprint 59: Cross-Repository Benchmark ===")
    print()

    all_metrics = []

    for repo in REPOS:
        print(f"Processing: {repo}")
        try:
            claims = extract_claims(repo)
            metrics = calculate_metrics(repo, claims)
            all_metrics.append(metrics)

            # Save individual metrics
            repo_name = repo.replace("/", "_").replace("-", "_")
            output_path = f"artifacts/{repo_name}_metrics.json"
            with open(output_path, 'w') as f:
                json.dump(metrics, f, indent=2)
            print(f"  Claims: {metrics['total_claims']}")
            print(f"  Auditability: {metrics['auditability_score']}")
            print(f"  Observable ratio: {metrics['observable_ratio']}")
            print(f"  Evidence coverage: {metrics['evidence_coverage']}")
            print(f"  Saved: {output_path}")
        except Exception as e:
            print(f"  ERROR: {e}")
            all_metrics.append({
                "repo": repo,
                "total_claims": 0,
                "observable_claims": 0,
                "derivable_claims": 0,
                "inferred_claims": 0,
                "unknown_claims": 0,
                "auditability_score": 0.0,
                "evidence_coverage": 0.0,
                "observable_ratio": 0.0,
                "total_gaps": 0,
                "error": str(e),
            })
        print()

    # Save cross-repo metrics
    with open("artifacts/cross_repo_metrics.json", 'w') as f:
        json.dump(all_metrics, f, indent=2)
    print("Cross-repo metrics saved to: artifacts/cross_repo_metrics.json")

    # Generate comparison markdown
    with open("artifacts/cross_repo_comparison.md", 'w') as f:
        f.write("# Sprint 59 — Cross-Repository Comparison\n\n")
        f.write("## Métricas comparativas\n\n")
        f.write("| Repo | Claims | Observable | Derivable | Inferred | Unknown | Auditability | Coverage | Obs Ratio |\n")
        f.write("|------|--------|------------|-----------|----------|---------|--------------|----------|-----------|\n")
        for m in all_metrics:
            f.write(f"| {m['repo']} | {m['total_claims']} | {m['observable_claims']} | {m['derivable_claims']} | {m['inferred_claims']} | {m['unknown_claims']} | {m['auditability_score']} | {m['evidence_coverage']} | {m['observable_ratio']} |\n")
        f.write("\n")
        f.write("## Análisis\n\n")
        f.write("No se interpretan diferencias en este sprint.\n")
        f.write("Solo se registran métricas.\n")

    print("Comparison saved to: artifacts/cross_repo_comparison.md")

    # Print summary
    print("\n=== Summary ===")
    for m in all_metrics:
        print(f"  {m['repo']}: {m['total_claims']} claims, auditability={m['auditability_score']}")

if __name__ == "__main__":
    main()
