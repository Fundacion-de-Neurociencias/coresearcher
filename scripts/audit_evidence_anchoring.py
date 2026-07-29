#!/usr/bin/env python3
"""
Sprint 58A: Evidence Anchoring Audit

For each claim in the Trajectory Report, check if it has traceable evidence
in the raw GitHub data. Classify as observable, derivable, inferred, or unknown.

Key metric: observable_ratio = observable / total
"""

import json
import re

def load_raw_data(path):
    """Load raw GitHub data."""
    with open(path, 'r', encoding='utf-8', errors='replace') as f:
        return json.load(f)

def extract_claims(report_path):
    """Extract all claims from the Trajectory Report."""
    with open(report_path, 'r', encoding='utf-8', errors='replace') as f:
        content = f.read()

    claims = []

    # Extract Decision claims
    for match in re.finditer(r'### Decisión \d+: (.+)', content):
        claims.append({
            "claim": match.group(1),
            "type": "decision",
            "section": "Decisions",
        })

    # Extract Alternative claims
    for match in re.finditer(r'### Alternativa \d+', content):
        start = match.end()
        end = content.find('\n\n', start)
        if end == -1:
            end = start + 500
        text = content[start:end].strip()
        claims.append({
            "claim": text[:200],
            "type": "alternative",
            "section": "Alternatives",
        })

    # Extract Criteria claims
    for match in re.finditer(r'### Criterio \d+', content):
        start = match.end()
        end = content.find('\n\n', start)
        if end == -1:
            end = start + 500
        text = content[start:end].strip()
        claims.append({
            "claim": text[:200],
            "type": "criterion",
            "section": "Criteria",
        })

    # Extract Evidence claims
    for match in re.finditer(r'### Evidencia \d+', content):
        start = match.end()
        end = content.find('\n\n', start)
        if end == -1:
            end = start + 500
        text = content[start:end].strip()
        claims.append({
            "claim": text[:200],
            "type": "evidence",
            "section": "Evidence",
        })

    # Extract Gap claims
    for match in re.finditer(r'### (Observable|Inferible|Desconocido)', content):
        start = match.end()
        end = content.find('\n\n', start)
        if end == -1:
            end = start + 500
        text = content[start:end].strip()
        claims.append({
            "claim": text[:200],
            "type": "gap",
            "section": match.group(1),
        })

    return claims

def find_evidence_sources(claim, raw_data):
    """Find traceable evidence sources for a claim in raw data."""
    sources = {
        "issue": None,
        "pr": None,
        "commit": None,
        "release": None,
        "zenodo": None,
    }

    claim_lower = claim.lower()

    # Check issues
    for issue in raw_data.get("issues", []):
        issue_title = (issue.get("title") or "").lower()
        issue_body = (issue.get("body") or "").lower()
        issue_number = str(issue.get("number", ""))

        # Check if claim text matches issue title or body
        if claim_lower in issue_title or claim_lower in issue_body:
            sources["issue"] = f"#{issue_number}: {issue.get('title', '')[:80]}"
            break

        # Check if issue number is mentioned in claim
        if f"#{issue_number}" in claim:
            sources["issue"] = f"#{issue_number}: {issue.get('title', '')[:80]}"
            break

    # Check PRs
    for pr in raw_data.get("pulls", []):
        pr_title = (pr.get("title") or "").lower()
        pr_body = (pr.get("body") or "").lower()
        pr_number = str(pr.get("number", ""))

        if claim_lower in pr_title or claim_lower in pr_body:
            sources["pr"] = f"#{pr_number}: {pr.get('title', '')[:80]}"
            break

        if f"#{pr_number}" in claim:
            sources["pr"] = f"#{pr_number}: {pr.get('title', '')[:80]}"
            break

    # Check releases
    for release in raw_data.get("releases", []):
        tag = release.get("tag_name", "").lower()
        if tag and tag in claim_lower:
            sources["release"] = f"Release {release.get('tag_name', '')}"
            break

    # Check commits
    for commit in raw_data.get("commits", []):
        msg = commit.get("commit", {}).get("message", "").lower()
        sha = commit.get("sha", "")[:7]
        if claim_lower in msg or sha in claim_lower:
            sources["commit"] = f"Commit {sha}: {msg[:80]}"
            break

    return sources

def classify_claim(claim, sources):
    """Classify a claim based on evidence sources."""
    has_source = any(v is not None for v in sources.values())

    if not has_source:
        return "inferred"

    # Check if claim appears literally in any source
    # This is a simplified check - in practice would need more sophisticated matching
    claim_lower = claim.lower()

    # If we found a matching source, it's at least derivable
    # If the exact claim text appears in the source, it's observable
    # For now, if source found, classify as derivable
    return "derivable"

def main():
    report_path = "artifacts/langgraph_trajectory_report_v0.md"
    raw_data_path = "data/langgraph_raw.json"

    print("=== Sprint 58A: Evidence Anchoring Audit ===")
    print(f"Report: {report_path}")
    print(f"Raw data: {raw_data_path}\n")

    # Load data
    raw_data = load_raw_data(raw_data_path)
    claims = extract_claims(report_path)

    print(f"Total claims extracted: {len(claims)}")

    # Audit each claim
    counts = {"observable": 0, "derivable": 0, "inferred": 0, "unknown": 0}
    anchored = []
    unanchored = []

    for claim in claims:
        sources = find_evidence_sources(claim["claim"], raw_data)
        classification = classify_claim(claim["claim"], sources)
        counts[classification] += 1

        result = {
            "claim": claim["claim"][:150],
            "type": claim["type"],
            "section": claim["section"],
            "sources": sources,
            "classification": classification,
        }

        if any(v is not None for v in sources.values()):
            anchored.append(result)
        else:
            unanchored.append(result)

    # Calculate metrics
    total = len(claims)
    observable_ratio = counts["observable"] / total if total > 0 else 0.0
    evidence_coverage = len(anchored) / total if total > 0 else 0.0
    inference_ratio = counts["inferred"] / total if total > 0 else 0.0

    result = {
        "total_claims": total,
        "counts": counts,
        "observable_ratio": round(observable_ratio, 4),
        "evidence_coverage": round(evidence_coverage, 4),
        "inference_ratio": round(inference_ratio, 4),
        "anchored_claims": anchored,
        "unanchored_claims": unanchored,
    }

    print(f"\nResults:")
    print(f"  Observable: {counts['observable']}")
    print(f"  Derivable: {counts['derivable']}")
    print(f"  Inferred: {counts['inferred']}")
    print(f"  Unknown: {counts['unknown']}")
    print(f"  Observable ratio: {observable_ratio}")
    print(f"  Evidence coverage: {evidence_coverage}")
    print(f"  Inference ratio: {inference_ratio}")
    print(f"  Anchored claims: {len(anchored)}")
    print(f"  Unanchored claims: {len(unanchored)}")

    # Save results
    output_json = "artifacts/sprint58a_evidence_audit.json"
    with open(output_json, 'w') as f:
        json.dump(result, f, indent=2)
    print(f"\nJSON saved to: {output_json}")

    # Save markdown summary
    output_md = "artifacts/sprint58a_evidence_audit.md"
    with open(output_md, 'w') as f:
        f.write("# Sprint 58A — Evidence Anchoring Audit\n\n")
        f.write(f"## Report auditado\n\n`{report_path}`\n\n")
        f.write("## Métricas\n\n")
        f.write("| Métrica | Valor |\n|---------|-------|\n")
        f.write(f"| Total claims | {total} |\n")
        f.write(f"| Observable | {counts['observable']} |\n")
        f.write(f"| Derivable | {counts['derivable']} |\n")
        f.write(f"| Inferido | {counts['inferred']} |\n")
        f.write(f"| Desconocido | {counts['unknown']} |\n")
        f.write(f"| Observable ratio | {observable_ratio} |\n")
        f.write(f"| Evidence coverage | {evidence_coverage} |\n")
        f.write(f"| Inference ratio | {inference_ratio} |\n\n")
        f.write("## Claims anclados (con evidencia)\n\n")
        for c in anchored:
            f.write(f"### {c['type']}: {c['claim'][:100]}\n\n")
            f.write(f"- **Clasificación**: {c['classification']}\n")
            for k, v in c['sources'].items():
                if v:
                    f.write(f"- **{k}**: {v}\n")
            f.write("\n")
        f.write("## Claims no anclados (sin evidencia)\n\n")
        for c in unanchored:
            f.write(f"### {c['type']}: {c['claim'][:100]}\n\n")
            f.write(f"- **Clasificación**: {c['classification']}\n")
            f.write(f"- **Problema**: No se encontró evidencia rastreable\n\n")

    print(f"Markdown saved to: {output_md}")

    # Print interpretation
    print("\n=== Interpretación ===")
    if observable_ratio < 0.3:
        print("observable_ratio < 0.3")
        print("El reporte actual genera más inferencias que evidencia.")
        print("Necesario reescribir el extractor para incluir evidence anchors.")
        print("El producto debe ser 'Evidence-Anchored Trajectory Report'.")
    else:
        print("observable_ratio >= 0.3")
        print("El reporte contiene trazabilidad parcial.")
        print("Necesario mejorar la presentación de anchors.")

if __name__ == "__main__":
    main()
