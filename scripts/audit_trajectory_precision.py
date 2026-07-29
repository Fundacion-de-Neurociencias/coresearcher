#!/usr/bin/env python3
"""
Audit the epistemic precision of a Trajectory Report.

For each extracted element (Decision, Alternative, Criterion, Evidence, Gap),
classify as:
- observable: appears literally in GitHub/Zenodo
- derivable: calculated via explicit algorithm
- inferred: reasonable interpretation, not literal
- unknown: explicit absence of evidence

Output: JSON with counts and precision_observable metric.
"""

import json
import re

def classify_element(element_type, text, context):
    """Classify an element based on its content and context."""
    text_lower = text.lower()

    # Observable indicators
    observable_patterns = [
        r'https://github\.com/',
        r'#\d+',
        r'commit\s+[a-f0-9]{7,}',
        r'release\s+\S+',
        r'tag:\s*\S+',
        r'issue\s+#?\d+',
        r'pr\s+#?\d+',
        r'pull request\s+#?\d+',
    ]
    for pattern in observable_patterns:
        if re.search(pattern, text_lower):
            return "observable"

    # Unknown indicators
    unknown_patterns = [
        r'not observable', r'not recuperable', r'no evidence',
        r'unknown', r'no public record', r'not documented',
        r'cannot be recovered',
    ]
    for pattern in unknown_patterns:
        if re.search(pattern, text_lower):
            return "unknown"

    # Derivable indicators
    derivable_patterns = [
        r'count', r'number of', r'total', r'sum',
        r'date\s*diff', r'time\s*between', r'frequency',
    ]
    for pattern in derivable_patterns:
        if re.search(pattern, text_lower):
            return "derivable"

    return "inferred"


def audit_report(report_path):
    """Audit a Trajectory Report and return epistemic classification."""
    with open(report_path, 'r', encoding='utf-8', errors='replace') as f:
        content = f.read()

    elements = []

    # Decision sections
    for match in re.finditer(r'### Decisión \d+: (.+)', content):
        elements.append({"type": "decision", "text": match.group(1), "context": "decision"})

    # Alternative sections
    for match in re.finditer(r'### Alternativa \d+', content):
        start = match.end()
        end = content.find('\n\n', start)
        if end == -1:
            end = start + 500
        elements.append({"type": "alternative", "text": content[start:end], "context": "alt"})

    # Criteria sections
    for match in re.finditer(r'### Criterio \d+', content):
        start = match.end()
        end = content.find('\n\n', start)
        if end == -1:
            end = start + 500
        elements.append({"type": "criterion", "text": content[start:end], "context": "crit"})

    # Evidence sections
    for match in re.finditer(r'### Evidencia \d+', content):
        start = match.end()
        end = content.find('\n\n', start)
        if end == -1:
            end = start + 500
        elements.append({"type": "evidence", "text": content[start:end], "context": "evid"})

    # Gap sections
    for match in re.finditer(r'### (Observable|Inferible|Desconocido)', content):
        start = match.end()
        end = content.find('\n\n', start)
        if end == -1:
            end = start + 500
        elements.append({"type": "gap", "text": content[start:end], "context": match.group(1).lower()})

    counts = {"observable": 0, "derivable": 0, "inferred": 0, "unknown": 0}
    classified = []

    for elem in elements:
        status = classify_element(elem["type"], elem["text"], elem.get("context", ""))
        counts[status] += 1
        classified.append({"type": elem["type"], "text_preview": elem["text"][:100], "epistemic_status": status})

    total = counts["observable"] + counts["derivable"] + counts["inferred"]
    precision = counts["observable"] / total if total > 0 else 0.0

    return {
        "report": report_path,
        "total_elements": len(elements),
        "counts": counts,
        "precision_observable": round(precision, 4),
        "classified_elements": classified,
    }


def main():
    report_path = "artifacts/langgraph_trajectory_report_v0.md"
    print("=== Sprint 58: Precision Audit ===")
    print(f"Auditing: {report_path}\n")

    result = audit_report(report_path)

    print(f"Total elements: {result['total_elements']}")
    print(f"Observable: {result['counts']['observable']}")
    print(f"Derivable: {result['counts']['derivable']}")
    print(f"Inferred: {result['counts']['inferred']}")
    print(f"Unknown: {result['counts']['unknown']}")
    print(f"Precision observable: {result['precision_observable']}\n")

    with open("artifacts/sprint58_precision_audit.json", 'w') as f:
        json.dump(result, f, indent=2)
    print("Audit saved to: artifacts/sprint58_precision_audit.json")

    with open("artifacts/sprint58_precision_audit.md", 'w') as f:
        f.write("# Sprint 58 — Precision Audit\n\n")
        f.write(f"## Report auditado\n\n`{report_path}`\n\n")
        f.write("## Resultados\n\n| Clase | Conteo |\n|-------|--------|\n")
        f.write(f"| Observable | {result['counts']['observable']} |\n")
        f.write(f"| Derivable | {result['counts']['derivable']} |\n")
        f.write(f"| Inferido | {result['counts']['inferred']} |\n")
        f.write(f"| Desconocido | {result['counts']['unknown']} |\n\n")
        f.write(f"## Métrica principal\n\n```\nprecision_observable = {result['precision_observable']}\n```\n\n")
        f.write("## Detalle de elementos\n\n")
        for elem in result["classified_elements"]:
            f.write(f"- **{elem['type']}** ({elem['epistemic_status']}): {elem['text_preview']}\n")
    print("Markdown summary saved to: artifacts/sprint58_precision_audit.md")


if __name__ == "__main__":
    main()
