"""
Generate priority observation ledger for CoResearcher.
Outputs a markdown ledger with top 100 scientific objects.
"""

import sys
sys.path.insert(0, '.')

from observer.priority_discovery import generate_priority_ledger
from datetime import datetime

# Generate the ledger
ledger = generate_priority_ledger(fetch_metadata=False)

# Build markdown output
md = f"""# Priority Observation Queue

Generated: {datetime.now().isoformat()}

## Summary

- **Total objects**: {ledger['total_objects']}
- **Strategy**: Observe the most influential science first
- **Scoring formula**: {ledger['scoring_formula']}

## Distribution by Source

| Source | Count |
|--------|-------|
| OpenAlex (papers) | {ledger['by_type']['papers']} |
| Zenodo (artifacts) | {ledger['by_type']['zenodo_records']} |
| Ecosystem (pre-validated) | {ledger['by_type']['ecosystems']} |

## Top 20 Priority Objects

"""

for i, obj in enumerate(ledger['top_20'], 1):
    score = obj.get('final_score', obj.get('score', 0))
    if obj['type'] == 'paper':
        md += f"### {i}. [{score:.2f}] {obj.get('title', 'Unknown')[:60]}\n"
        md += f"- **Type**: Paper\n"
        md += f"- **Source**: OpenAlex\n"
        md += f"- **Citations**: {obj.get('citations', 0)}\n"
        md += f"- **Year**: {obj.get('year', 'Unknown')}\n"
        if obj.get('github_url'):
            md += f"- **GitHub**: {obj['github_url']}\n"
    elif obj['type'] == 'zenodo_record':
        md += f"### {i}. [{score:.2f}] {obj.get('title', 'Unknown')[:60]}\n"
        md += f"- **Type**: Zenodo Record\n"
        md += f"- **Source**: Zenodo\n"
        md += f"- **DOI**: {obj.get('doi', 'Unknown')}\n"
        md += f"- **Query**: {obj.get('search_query', 'Unknown')}\n"
    else:
        md += f"### {i}. [{score:.2f}] {obj.get('name', 'Unknown')}\n"
        md += f"- **Type**: Ecosystem Repository\n"
        md += f"- **Source**: Ecosystem\n"
        md += f"- **Domain**: {obj.get('domain', 'Unknown')}\n"
        md += f"- **Repo**: {obj.get('repo', 'Unknown')}\n"
    md += "\n"

# Save to priority_ledger.md in current directory
with open("priority_ledger.md", "w", encoding="utf-8") as f:
    f.write(md)

print(f"Priority ledger saved with {ledger['total_objects']} objects")
print(f"- Papers: {ledger['by_type']['papers']}")
print(f"- Zenodo records: {ledger['by_type']['zenodo_records']}")
print(f"- Ecosystems: {ledger['by_type']['ecosystems']}")
print("\nSaved to: priority_ledger.md")