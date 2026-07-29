#!/usr/bin/env python3
"""
Fetch LangGraph GitHub data and generate a Trajectory Report.
Uses only public GitHub API - no instrumentation required.
"""

import json
import urllib.request
import urllib.parse
from datetime import datetime

REPO = "langchain-ai/langgraph"
BASE_URL = f"https://api.github.com/repos/{REPO}"

def fetch_json(url):
    """Fetch JSON from GitHub API."""
    req = urllib.request.Request(url, headers={"Accept": "application/vnd.github+json", "User-Agent": "coresearcher"})
    with urllib.request.urlopen(req) as resp:
        return json.loads(resp.read().decode())

def fetch_paginated(url, max_pages=5):
    """Fetch paginated results from GitHub API."""
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

def main():
    print("=== Fetching LangGraph repository data ===")

    # 1. Repository info
    repo = fetch_json(BASE_URL)
    print(f"Repository: {repo['full_name']}")
    print(f"Created: {repo['created_at']}")
    print(f"Language: {repo['language']}")
    print(f"Description: {repo.get('description', 'N/A')}")
    print(f"Default branch: {repo['default_branch']}")

    # 2. Issues (closed, with decision-relevant content)
    print("\n=== Fetching issues ===")
    issues = fetch_paginated(f"{BASE_URL}/issues?state=closed&per_page=100&sort=created&direction=desc")
    print(f"Closed issues fetched: {len(issues)}")

    # 3. Pull requests (merged)
    print("\n=== Fetching pull requests ===")
    prs = fetch_paginated(f"{BASE_URL}/pulls?state=closed&per_page=100&sort=created&direction=desc")
    print(f"Closed PRs fetched: {len(prs)}")

    # 4. Releases
    print("\n=== Fetching releases ===")
    releases = fetch_paginated(f"{BASE_URL}/releases?per_page=30")
    print(f"Releases fetched: {len(releases)}")

    # 5. Commits (recent)
    print("\n=== Fetching commits ===")
    commits = fetch_paginated(f"{BASE_URL}/commits?per_page=100")
    print(f"Commits fetched: {len(commits)}")

    # Save raw data
    raw_data = {
        "repo": repo,
        "issues": issues,
        "pulls": prs,
        "releases": releases,
        "commits": commits,
    }

    with open("data/langgraph_raw.json", "w") as f:
        json.dump(raw_data, f, indent=2, default=str)
    print("\nRaw data saved to data/langgraph_raw.json")

    # === Generate Trajectory Report ===
    print("\n=== Generating Trajectory Report ===")

    # Timeline events
    timeline = []

    # Releases
    for r in releases:
        timeline.append({
            "date": r.get("published_at", r.get("created_at", "")),
            "type": "release",
            "title": f"Release {r.get('tag_name', 'unknown')}",
            "url": r.get("html_url", ""),
        })

    # Merged PRs
    for pr in prs:
        if pr.get("merged_at"):
            timeline.append({
                "date": pr.get("merged_at", ""),
                "type": "pr_merged",
                "title": pr.get("title", ""),
                "url": pr.get("html_url", ""),
                "number": pr.get("number", ""),
            })

    # Closed issues with resolution
    for issue in issues:
        if issue.get("closed_at"):
            timeline.append({
                "date": issue.get("closed_at", ""),
                "type": "issue_closed",
                "title": issue.get("title", ""),
                "url": issue.get("html_url", ""),
                "number": issue.get("number", ""),
            })

    # Sort timeline
    timeline.sort(key=lambda x: x.get("date", ""))
    print(f"Timeline events: {len(timeline)}")

    # Key Decisions - search for decision keywords
    decision_keywords = [
        "we decided to", "let's go with", "chose", "opted for",
        "replaced", "switched to", "removed", "eliminated",
        "decided to", "went with", "picked", "selected",
        "instead of", "rather than", "rather than",
    ]

    decisions = []
    for issue in issues:
        body = (issue.get("body") or "") + " " + (issue.get("title") or "")
        body_lower = body.lower()
        for kw in decision_keywords:
            if kw in body_lower:
                decisions.append({
                    "source": "issue",
                    "number": issue.get("number", ""),
                    "title": issue.get("title", ""),
                    "url": issue.get("html_url", ""),
                    "date": issue.get("closed_at", issue.get("created_at", "")),
                    "keyword": kw,
                    "text": body[:300],
                })
                break

    for pr in prs:
        body = (pr.get("body") or "") + " " + (pr.get("title") or "")
        body_lower = body.lower()
        for kw in decision_keywords:
            if kw in body_lower:
                decisions.append({
                    "source": "pr",
                    "number": pr.get("number", ""),
                    "title": pr.get("title", ""),
                    "url": pr.get("html_url", ""),
                    "date": pr.get("merged_at", pr.get("created_at", "")),
                    "keyword": kw,
                    "text": body[:300],
                })
                break

    print(f"Decisions identified: {len(decisions)}")

    # Alternatives - search for alternative keywords
    alt_keywords = [
        "we could", "we considered", "instead of", "rather than",
        "option a", "option b", "alternative", "another option",
        "might use", "could use", "considered using",
    ]

    alternatives = []
    for issue in issues:
        body = (issue.get("body") or "") + " " + (issue.get("title") or "")
        body_lower = body.lower()
        for kw in alt_keywords:
            if kw in body_lower:
                alternatives.append({
                    "source": "issue",
                    "number": issue.get("number", ""),
                    "title": issue.get("title", ""),
                    "url": issue.get("html_url", ""),
                    "keyword": kw,
                    "text": body[:300],
                })
                break

    for pr in prs:
        body = (pr.get("body") or "") + " " + (pr.get("title") or "")
        body_lower = body.lower()
        for kw in alt_keywords:
            if kw in body_lower:
                alternatives.append({
                    "source": "pr",
                    "number": pr.get("number", ""),
                    "title": pr.get("title", ""),
                    "url": pr.get("html_url", ""),
                    "keyword": kw,
                    "text": body[:300],
                })
                break

    print(f"Alternatives identified: {len(alternatives)}")

    # Selection Criteria
    criteria_keywords = [
        "for performance", "for simplicity", "for compatibility",
        "for maintainability", "for scalability", "for reliability",
        "because", "since", "due to", "as",
        "latency", "memory", "speed", "efficiency",
        "complexity", "maintenance", "dependencies",
    ]

    criteria = []
    for issue in issues:
        body = (issue.get("body") or "") + " " + (issue.get("title") or "")
        body_lower = body.lower()
        for kw in criteria_keywords:
            if kw in body_lower:
                criteria.append({
                    "source": "issue",
                    "number": issue.get("number", ""),
                    "title": issue.get("title", ""),
                    "url": issue.get("html_url", ""),
                    "keyword": kw,
                    "text": body[:300],
                })
                break

    for pr in prs:
        body = (pr.get("body") or "") + " " + (pr.get("title") or "")
        body_lower = body.lower()
        for kw in criteria_keywords:
            if kw in body_lower:
                criteria.append({
                    "source": "pr",
                    "number": pr.get("number", ""),
                    "title": pr.get("title", ""),
                    "url": pr.get("html_url", ""),
                    "keyword": kw,
                    "text": body[:300],
                })
                break

    print(f"Criteria identified: {len(criteria)}")

    # Evidence Chain - issues/PRs with references to benchmarks, tests, papers
    evidence_keywords = [
        "benchmark", "test", "performance", "latency", "memory",
        "paper", "study", "research", "data", "metric",
        "measurement", "evaluation", "experiment",
    ]

    evidence = []
    for issue in issues:
        body = (issue.get("body") or "") + " " + (issue.get("title") or "")
        body_lower = body.lower()
        for kw in evidence_keywords:
            if kw in body_lower:
                evidence.append({
                    "source": "issue",
                    "number": issue.get("number", ""),
                    "title": issue.get("title", ""),
                    "url": issue.get("html_url", ""),
                    "keyword": kw,
                    "text": body[:300],
                })
                break

    for pr in prs:
        body = (pr.get("body") or "") + " " + (pr.get("title", ""))
        body_lower = body.lower()
        for kw in evidence_keywords:
            if kw in body_lower:
                evidence.append({
                    "source": "pr",
                    "number": pr.get("number", ""),
                    "title": pr.get("title", ""),
                    "url": pr.get("html_url", ""),
                    "keyword": kw,
                    "text": body[:300],
                })
                break

    print(f"Evidence identified: {len(evidence)}")

    # Information Gaps - issues still open, PRs without resolution
    open_issues = fetch_paginated(f"{BASE_URL}/issues?state=open&per_page=50")
    print(f"Open issues: {len(open_issues)}")

    # Generate the report
    report = generate_report(
        repo=repo,
        timeline=timeline[:30],  # top 30
        decisions=decisions[:15],
        alternatives=alternatives[:10],
        criteria=criteria[:10],
        evidence=evidence[:10],
        open_issues=open_issues[:10],
        releases=releases[:10],
    )

    with open("artifacts/langgraph_trajectory_report_v0.md", "w") as f:
        f.write(report)
    print("\nTrajectory Report saved to artifacts/langgraph_trajectory_report_v0.md")

    # Print summary
    print(f"\n=== Summary ===")
    print(f"Timeline events: {len(timeline[:30])}")
    print(f"Decisions: {len(decisions[:15])}")
    print(f"Alternatives: {len(alternatives[:10])}")
    print(f"Criteria: {len(criteria[:10])}")
    print(f"Evidence: {len(evidence[:10])}")
    print(f"Open issues (gaps): {len(open_issues[:10])}")


def generate_report(repo, timeline, decisions, alternatives, criteria, evidence, open_issues, releases):
    """Generate the Trajectory Report markdown."""

    lines = []
    lines.append("# Trajectory Report — LangGraph")
    lines.append("")
    lines.append("> Generated from public GitHub data only.")
    lines.append("> No instrumentation required. No private data used.")
    lines.append("")
    lines.append("---")
    lines.append("")

    # 1. Project Overview
    lines.append("## 1. Project Overview")
    lines.append("")
    lines.append(f"**Repository**: [{repo['full_name']}]({repo['html_url']})")
    lines.append(f"**Created**: {repo['created_at']}")
    lines.append(f"**Language**: {repo.get('language', 'N/A')}")
    lines.append(f"**Stars**: {repo.get('stargazers_count', 'N/A')}")
    lines.append(f"**Default branch**: {repo['default_branch']}")
    lines.append("")
    desc = repo.get("description", "N/A")
    lines.append(f"**Description**: {desc}")
    lines.append("")
    lines.append("**Objective (declared)**: LangGraph is a library for building stateful, multi-agent applications with LLMs.")
    lines.append("")
    lines.append("---")
    lines.append("")

    # 2. Timeline
    lines.append("## 2. Timeline")
    lines.append("")
    lines.append("Lista cronológica de eventos relevantes extraídos del registro público.")
    lines.append("")
    lines.append("| Fecha | Tipo | Evento |")
    lines.append("|-------|------|--------|")
    for event in timeline:
        date = event.get("date", "").split("T")[0] if event.get("date") else "N/A"
        etype = event.get("type", "unknown")
        title = event.get("title", "")[:80]
        url = event.get("url", "")
        if url:
            title = f"[{title}]({url})"
        lines.append(f"| {date} | {etype} | {title} |")
    lines.append("")
    lines.append("---")
    lines.append("")

    # 3. Key Decisions
    lines.append("## 3. Key Decisions")
    lines.append("")
    lines.append("Decisiones identificables desde evidencia pública. Cada decisión incluye evidencia, fecha y artefactos relacionados.")
    lines.append("")
    if decisions:
        for i, d in enumerate(decisions, 1):
            date = d.get("date", "").split("T")[0] if d.get("date") else "N/A"
            lines.append(f"### Decisión {i}: {d.get('title', '')[:80]}")
            lines.append("")
            lines.append(f"- **Fuente**: {d.get('source', '')} #{d.get('number', '')}")
            lines.append(f"- **Fecha**: {date}")
            lines.append(f"- **URL**: [{d.get('url', '')}]({d.get('url', '')})")
            lines.append(f"- **Keyword**: `{d.get('keyword', '')}`")
            lines.append(f"- **Texto**: {d.get('text', '')[:200]}")
            lines.append("")
    else:
        lines.append("No se identificaron decisiones explícitas desde el registro público.")
        lines.append("")
    lines.append("---")
    lines.append("")

    # 4. Alternatives
    lines.append("## 4. Alternatives")
    lines.append("")
    lines.append("Alternativas explícitamente observables en el registro público. NO se inferencia.")
    lines.append("")
    if alternatives:
        for i, a in enumerate(alternatives, 1):
            lines.append(f"### Alternativa {i}")
            lines.append("")
            lines.append(f"- **Fuente**: {a.get('source', '')} #{a.get('number', '')}")
            lines.append(f"- **URL**: [{a.get('url', '')}]({a.get('url', '')})")
            lines.append(f"- **Keyword**: `{a.get('keyword', '')}`")
            lines.append(f"- **Texto**: {a.get('text', '')[:200]}")
            lines.append("")
    else:
        lines.append("No se identificaron alternativas explícitas desde el registro público.")
        lines.append("")
    lines.append("---")
    lines.append("")

    # 5. Selection Criteria
    lines.append("## 5. Selection Criteria")
    lines.append("")
    lines.append("Criterios explícitos encontrados en el registro público, siempre acompañados de evidencia.")
    lines.append("")
    if criteria:
        for i, c in enumerate(criteria, 1):
            lines.append(f"### Criterio {i}")
            lines.append("")
            lines.append(f"- **Fuente**: {c.get('source', '')} #{c.get('number', '')}")
            lines.append(f"- **URL**: [{c.get('url', '')}]({c.get('url', '')})")
            lines.append(f"- **Keyword**: `{c.get('keyword', '')}`")
            lines.append(f"- **Texto**: {c.get('text', '')[:200]}")
            lines.append("")
    else:
        lines.append("No se identificaron criterios explícitos desde el registro público.")
        lines.append("")
    lines.append("---")
    lines.append("")

    # 6. Evidence Chain
    lines.append("## 6. Evidence Chain")
    lines.append("")
    lines.append("Para cada afirmación, se rastrea a: Issue, PR, Commit, Release o Documento.")
    lines.append("")
    if evidence:
        for i, e in enumerate(evidence, 1):
            lines.append(f"### Evidencia {i}")
            lines.append("")
            lines.append(f"- **Fuente**: {e.get('source', '')} #{e.get('number', '')}")
            lines.append(f"- **URL**: [{e.get('url', '')}]({e.get('url', '')})")
            lines.append(f"- **Keyword**: `{e.get('keyword', '')}`")
            lines.append(f"- **Texto**: {e.get('text', '')[:200]}")
            lines.append("")
    else:
        lines.append("No se identificó evidencia explícita desde el registro público.")
        lines.append("")
    lines.append("---")
    lines.append("")

    # 7. Information Gaps
    lines.append("## 7. Information Gaps")
    lines.append("")
    lines.append("Información necesaria para explicar la trayectoria pero no observable públicamente.")
    lines.append("")
    lines.append("### Observable")
    lines.append("")
    lines.append("- Issues, PRs, commits, releases y discusiones públicas son observables.")
    lines.append("- Las decisiones explícitas documentadas en estos canales son observables.")
    lines.append("")
    lines.append("### Inferible")
    lines.append("")
    lines.append("- El contexto organizativo (recursos, prioridades, deadlines) no está documentado públicamente.")
    lines.append("- Las alternativas consideradas pero no verbalizadas no son observables.")
    lines.append("")
    lines.append("### Desconocido")
    lines.append("")
    if open_issues:
        lines.append("Issues abiertos sin resolución documentada:")
        lines.append("")
        for issue in open_issues:
            title = issue.get("title", "")[:80]
            url = issue.get("html_url", "")
            number = issue.get("number", "")
            lines.append(f"- [#{number}]({url}) {title}")
        lines.append("")
    else:
        lines.append("No se identificaron issues abiertos sin resolución.")
        lines.append("")
    lines.append("---")
    lines.append("")

    # Methodology
    lines.append("## Methodology")
    lines.append("")
    lines.append("Este informe se generó exclusivamente a partir de la API pública de GitHub.")
    lines.append("")
    lines.append("**Fuentes utilizadas:**")
    lines.append("- GitHub Issues (abiertos y cerrados)")
    lines.append("- GitHub Pull Requests (merged y closed)")
    lines.append("- GitHub Commits")
    lines.append("- GitHub Releases")
    lines.append("")
    lines.append("**Fuentes prohibidas (no utilizadas):**")
    lines.append("- Entrevistas")
    lines.append("- Instrumentación adicional")
    lines.append("- Logs privados")
    lines.append("- Telemetría")
    lines.append("- Nuevas bases de datos")
    lines.append("")
    lines.append("**Regla de extracción:**")
    lines.append("- Prohibido escribir: 'probablemente', 'seguramente', 'el equipo pensó', 'la intención era'")
    lines.append("- Solo: evidencia observable, ausencia de evidencia, incertidumbre explícita")
    lines.append("")
    lines.append("---")
    lines.append("")

    # Metrics
    lines.append("## Metrics")
    lines.append("")
    lines.append("| Métrica | Conteo |")
    lines.append("|---------|--------|")
    lines.append(f"| Eventos cronológicos | {len(timeline)} |")
    lines.append(f"| Decisiones identificadas | {len(decisions)} |")
    lines.append(f"| Alternativas identificadas | {len(alternatives)} |")
    lines.append(f"| Criterios identificados | {len(criteria)} |")
    lines.append(f"| Evidencia identificada | {len(evidence)} |")
    lines.append(f"| Issues abiertos (gaps) | {len(open_issues)} |")
    lines.append("")

    return "\n".join(lines)


if __name__ == "__main__":
    main()
