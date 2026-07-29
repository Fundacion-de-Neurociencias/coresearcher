#!/usr/bin/env python3
"""
Sprint 58B: Evidence-Anchored Trajectory Report Generator

Transforms raw GitHub data into an Evidence-Anchored Trajectory Report
where every claim has explicit evidence: claim, source, quote, url, classification.

No LLMs. No agents. No new databases. Just better traceability.
"""

import json
import re
import urllib.request

REPO = "langchain-ai/langgraph"
BASE_URL = f"https://api.github.com/repos/{REPO}"

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
            print(f"Error fetching page {page}: {e}")
            break
    return results

def classify_claim(claim_text, source_type, source_url, quote):
    """Classify a claim based on evidence."""
    if quote and source_url:
        # Check if claim text appears literally in the quote
        if claim_text.lower() in quote.lower():
            return "observable"
        else:
            return "derivable"
    elif source_url:
        return "derivable"
    else:
        return "inferred"

def extract_claims_from_raw(raw_data):
    """Extract claims with evidence anchors from raw GitHub data."""
    claims = []

    # Extract from issues
    decision_keywords = [
        "we decided to", "let's go with", "chose", "opted for",
        "replaced", "switched to", "removed", "eliminated",
        "decided to", "went with", "picked", "selected",
    ]

    for issue in raw_data.get("issues", []):
        body = (issue.get("body") or "") + " " + (issue.get("title") or "")
        body_lower = body.lower()

        for kw in decision_keywords:
            if kw in body_lower:
                # Find the sentence containing the keyword
                sentences = re.split(r'[.!?]+', body)
                for sentence in sentences:
                    if kw in sentence.lower():
                        claim_text = sentence.strip()[:200]
                        source_url = issue.get("html_url", "")
                        quote = issue.get("title", "") + ": " + (issue.get("body") or "")[:500]

                        claims.append({
                            "claim": claim_text,
                            "type": "decision",
                            "source_type": "issue",
                            "source_id": f"#{issue.get('number', '')}",
                            "source_url": source_url,
                            "quote": quote[:500],
                            "classification": classify_claim(claim_text, "issue", source_url, quote),
                        })
                        break
                break

    # Extract from PRs
    for pr in raw_data.get("pulls", []):
        body = (pr.get("body") or "") + " " + (pr.get("title") or "")
        body_lower = body.lower()

        for kw in decision_keywords:
            if kw in body_lower:
                sentences = re.split(r'[.!?]+', body)
                for sentence in sentences:
                    if kw in sentence.lower():
                        claim_text = sentence.strip()[:200]
                        source_url = pr.get("html_url", "")
                        quote = pr.get("title", "") + ": " + (pr.get("body") or "")[:500]

                        claims.append({
                            "claim": claim_text,
                            "type": "decision",
                            "source_type": "pr",
                            "source_id": f"#{pr.get('number', '')}",
                            "source_url": source_url,
                            "quote": quote[:500],
                            "classification": classify_claim(claim_text, "pr", source_url, quote),
                        })
                        break
                break

    # Extract alternatives
    alt_keywords = [
        "we could", "we considered", "instead of", "rather than",
        "option a", "option b", "alternative", "another option",
    ]

    for issue in raw_data.get("issues", []):
        body = (issue.get("body") or "") + " " + (issue.get("title") or "")
        body_lower = body.lower()

        for kw in alt_keywords:
            if kw in body_lower:
                sentences = re.split(r'[.!?]+', body)
                for sentence in sentences:
                    if kw in sentence.lower():
                        claim_text = sentence.strip()[:200]
                        source_url = issue.get("html_url", "")
                        quote = issue.get("title", "") + ": " + (issue.get("body") or "")[:500]

                        claims.append({
                            "claim": claim_text,
                            "type": "alternative",
                            "source_type": "issue",
                            "source_id": f"#{issue.get('number', '')}",
                            "source_url": source_url,
                            "quote": quote[:500],
                            "classification": classify_claim(claim_text, "issue", source_url, quote),
                        })
                        break
                break

    # Extract criteria
    criteria_keywords = [
        "for performance", "for simplicity", "for compatibility",
        "for maintainability", "for scalability", "for reliability",
        "because", "since", "due to",
    ]

    for issue in raw_data.get("issues", []):
        body = (issue.get("body") or "") + " " + (issue.get("title") or "")
        body_lower = body.lower()

        for kw in criteria_keywords:
            if kw in body_lower:
                sentences = re.split(r'[.!?]+', body)
                for sentence in sentences:
                    if kw in sentence.lower():
                        claim_text = sentence.strip()[:200]
                        source_url = issue.get("html_url", "")
                        quote = issue.get("title", "") + ": " + (issue.get("body") or "")[:500]

                        claims.append({
                            "claim": claim_text,
                            "type": "criterion",
                            "source_type": "issue",
                            "source_id": f"#{issue.get('number', '')}",
                            "source_url": source_url,
                            "quote": quote[:500],
                            "classification": classify_claim(claim_text, "issue", source_url, quote),
                        })
                        break
                break

    # Extract evidence
    evidence_keywords = [
        "benchmark", "test", "performance", "latency", "memory",
        "paper", "study", "research", "data", "metric",
    ]

    for issue in raw_data.get("issues", []):
        body = (issue.get("body") or "") + " " + (issue.get("title") or "")
        body_lower = body.lower()

        for kw in evidence_keywords:
            if kw in body_lower:
                sentences = re.split(r'[.!?]+', body)
                for sentence in sentences:
                    if kw in sentence.lower():
                        claim_text = sentence.strip()[:200]
                        source_url = issue.get("html_url", "")
                        quote = issue.get("title", "") + ": " + (issue.get("body") or "")[:500]

                        claims.append({
                            "claim": claim_text,
                            "type": "evidence",
                            "source_type": "issue",
                            "source_id": f"#{issue.get('number', '')}",
                            "source_url": source_url,
                            "quote": quote[:500],
                            "classification": classify_claim(claim_text, "issue", source_url, quote),
                        })
                        break
                break

    # Extract gaps (open issues)
    for issue in raw_data.get("open_issues", []):
        claim_text = issue.get("title", "")[:200]
        source_url = issue.get("html_url", "")
        quote = issue.get("title", "") + ": " + (issue.get("body") or "")[:500]

        claims.append({
            "claim": claim_text,
            "type": "gap",
            "source_type": "issue",
            "source_id": f"#{issue.get('number', '')}",
            "source_url": source_url,
            "quote": quote[:500],
            "classification": "unknown",
        })

    return claims

def calculate_metrics(claims):
    """Calculate auditability metrics."""
    total = len(claims)
    observable = sum(1 for c in claims if c["classification"] == "observable")
    derivable = sum(1 for c in claims if c["classification"] == "derivable")
    inferred = sum(1 for c in claims if c["classification"] == "inferred")
    unknown = sum(1 for c in claims if c["classification"] == "unknown")

    has_url = sum(1 for c in claims if c["source_url"])
    has_quote = sum(1 for c in claims if c["quote"])

    return {
        "total_claims": total,
        "observable_claims": observable,
        "derivable_claims": derivable,
        "inferred_claims": inferred,
        "unknown_claims": unknown,
        "observable_ratio": round(observable / total, 4) if total > 0 else 0.0,
        "evidence_coverage": round((total - inferred - unknown) / total, 4) if total > 0 else 0.0,
        "quote_coverage": round(has_quote / total, 4) if total > 0 else 0.0,
        "url_coverage": round(has_url / total, 4) if total > 0 else 0.0,
        "auditability_score": round((has_url + has_quote) / (2 * total), 4) if total > 0 else 0.0,
    }

def generate_report(claims, metrics, repo_info):
    """Generate the Evidence-Anchored Trajectory Report."""
    lines = []

    # Header
    lines.append("# Evidence-Anchored Trajectory Report — LangGraph")
    lines.append("")
    lines.append("> Generated from public GitHub data only.")
    lines.append("> No instrumentation required. No private data used.")
    lines.append("")
    lines.append("---")
    lines.append("")

    # Auditability metrics
    lines.append("## Auditability Metrics")
    lines.append("")
    lines.append("| Métrica | Valor |")
    lines.append("|---------|-------|")
    lines.append(f"| Total claims | {metrics['total_claims']} |")
    lines.append(f"| Observable claims | {metrics['observable_claims']} |")
    lines.append(f"| Derivable claims | {metrics['derivable_claims']} |")
    lines.append(f"| Inferred claims | {metrics['inferred_claims']} |")
    lines.append(f"| Unknown claims | {metrics['unknown_claims']} |")
    lines.append(f"| Observable ratio | {metrics['observable_ratio']} |")
    lines.append(f"| Evidence coverage | {metrics['evidence_coverage']} |")
    lines.append(f"| Quote coverage | {metrics['quote_coverage']} |")
    lines.append(f"| URL coverage | {metrics['url_coverage']} |")
    lines.append(f"| Auditability score | {metrics['auditability_score']} |")
    lines.append("")
    lines.append("---")
    lines.append("")

    # Project Overview
    lines.append("## 1. Project Overview")
    lines.append("")
    lines.append(f"**Repository**: [{repo_info.get('full_name', '')}]({repo_info.get('html_url', '')})")
    lines.append(f"**Created**: {repo_info.get('created_at', '')}")
    lines.append(f"**Language**: {repo_info.get('language', '')}")
    lines.append(f"**Description**: {repo_info.get('description', '')}")
    lines.append("")
    lines.append("---")
    lines.append("")

    # Claims by type
    lines.append("## 2. Decisions")
    lines.append("")
    decisions = [c for c in claims if c["type"] == "decision"]
    for i, c in enumerate(decisions, 1):
        lines.append(f"### Decision {i}")
        lines.append("")
        lines.append(f"**CLAIM**: {c['claim']}")
        lines.append("")
        lines.append(f"**CLASSIFICATION**: {c['classification']}")
        lines.append("")
        lines.append(f"**SOURCE**: {c['source_type']} {c['source_id']}")
        lines.append("")
        lines.append(f"**QUOTE**: \"{c['quote'][:300]}\"")
        lines.append("")
        lines.append(f"**URL**: {c['source_url']}")
        lines.append("")
    lines.append("---")
    lines.append("")

    lines.append("## 3. Alternatives")
    lines.append("")
    alts = [c for c in claims if c["type"] == "alternative"]
    for i, c in enumerate(alts, 1):
        lines.append(f"### Alternative {i}")
        lines.append("")
        lines.append(f"**CLAIM**: {c['claim']}")
        lines.append("")
        lines.append(f"**CLASSIFICATION**: {c['classification']}")
        lines.append("")
        lines.append(f"**SOURCE**: {c['source_type']} {c['source_id']}")
        lines.append("")
        lines.append(f"**QUOTE**: \"{c['quote'][:300]}\"")
        lines.append("")
        lines.append(f"**URL**: {c['source_url']}")
        lines.append("")
    lines.append("---")
    lines.append("")

    lines.append("## 4. Selection Criteria")
    lines.append("")
    criteria = [c for c in claims if c["type"] == "criterion"]
    for i, c in enumerate(criteria, 1):
        lines.append(f"### Criterion {i}")
        lines.append("")
        lines.append(f"**CLAIM**: {c['claim']}")
        lines.append("")
        lines.append(f"**CLASSIFICATION**: {c['classification']}")
        lines.append("")
        lines.append(f"**SOURCE**: {c['source_type']} {c['source_id']}")
        lines.append("")
        lines.append(f"**QUOTE**: \"{c['quote'][:300]}\"")
        lines.append("")
        lines.append(f"**URL**: {c['source_url']}")
        lines.append("")
    lines.append("---")
    lines.append("")

    lines.append("## 5. Evidence")
    lines.append("")
    evidence = [c for c in claims if c["type"] == "evidence"]
    for i, c in enumerate(evidence, 1):
        lines.append(f"### Evidence {i}")
        lines.append("")
        lines.append(f"**CLAIM**: {c['claim']}")
        lines.append("")
        lines.append(f"**CLASSIFICATION**: {c['classification']}")
        lines.append("")
        lines.append(f"**SOURCE**: {c['source_type']} {c['source_id']}")
        lines.append("")
        lines.append(f"**QUOTE**: \"{c['quote'][:300]}\"")
        lines.append("")
        lines.append(f"**URL**: {c['source_url']}")
        lines.append("")
    lines.append("---")
    lines.append("")

    lines.append("## 6. Information Gaps")
    lines.append("")
    gaps = [c for c in claims if c["type"] == "gap"]
    for i, c in enumerate(gaps, 1):
        lines.append(f"### Gap {i}")
        lines.append("")
        lines.append(f"**CLAIM**: {c['claim']}")
        lines.append("")
        lines.append(f"**CLASSIFICATION**: {c['classification']}")
        lines.append("")
        lines.append(f"**SOURCE**: {c['source_type']} {c['source_id']}")
        lines.append("")
        lines.append(f"**URL**: {c['source_url']}")
        lines.append("")
    lines.append("---")
    lines.append("")

    # Methodology
    lines.append("## 7. Methodology")
    lines.append("")
    lines.append("Este informe se generó exclusivamente a partir de la API pública de GitHub.")
    lines.append("")
    lines.append("**Regla de trazabilidad**:")
    lines.append("- Todo claim debe contener: claim, classification, source, quote, url")
    lines.append("- Si no hay evidencia rastreable: classification = inferred")
    lines.append("- Si no hay evidencia disponible: classification = unknown")
    lines.append("")
    lines.append("---")
    lines.append("")

    # Auditability rule
    lines.append("## 8. Auditability Rule")
    lines.append("")
    lines.append("Todo claim producido por Coresearcher debe ser auditable.")
    lines.append("")
    lines.append("Auditable significa que un tercero puede localizar la evidencia original en menos de 60 segundos usando únicamente la información contenida en el reporte.")
    lines.append("")

    return "\n".join(lines)

def main():
    print("=== Sprint 58B: Evidence-Anchored Report Generator ===")

    # Load raw data
    with open("data/langgraph_raw.json", 'r', encoding='utf-8', errors='replace') as f:
        raw_data = json.load(f)

    # Fetch repo info
    repo_info = raw_data.get("repo", {})
    print(f"Repository: {repo_info.get('full_name', 'unknown')}")

    # Fetch open issues for gaps
    print("Fetching open issues...")
    raw_data["open_issues"] = fetch_paginated(f"{BASE_URL}/issues?state=open&per_page=50")
    print(f"Open issues: {len(raw_data['open_issues'])}")

    # Extract claims with evidence anchors
    print("Extracting claims with evidence anchors...")
    claims = extract_claims_from_raw(raw_data)
    print(f"Total claims: {len(claims)}")

    # Calculate metrics
    metrics = calculate_metrics(claims)
    print(f"Observable: {metrics['observable_claims']}")
    print(f"Derivable: {metrics['derivable_claims']}")
    print(f"Inferred: {metrics['inferred_claims']}")
    print(f"Unknown: {metrics['unknown_claims']}")
    print(f"Observable ratio: {metrics['observable_ratio']}")
    print(f"Evidence coverage: {metrics['evidence_coverage']}")
    print(f"Quote coverage: {metrics['quote_coverage']}")
    print(f"URL coverage: {metrics['url_coverage']}")
    print(f"Auditability score: {metrics['auditability_score']}")

    # Generate report
    report = generate_report(claims, metrics, repo_info)

    # Save report
    output_path = "artifacts/langgraph_trajectory_report_v1.md"
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(report)
    print(f"\nReport saved to: {output_path}")

    # Save metrics JSON
    with open("artifacts/sprint58b_auditability_metrics.json", 'w') as f:
        json.dump(metrics, f, indent=2)
    print("Metrics saved to: artifacts/sprint58b_auditability_metrics.json")


if __name__ == "__main__":
    main()
