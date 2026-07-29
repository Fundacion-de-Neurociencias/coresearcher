#!/usr/bin/env python3
"""
Fetch Zenodo links for a GitHub repository.

Uses the Zenodo API to find records associated with a GitHub repository.
Builds a minimal trajectory graph: paper -> dataset -> software -> release.
"""

import json
import urllib.request
import urllib.parse

def fetch_zenodo_records(github_repo):
    """Fetch Zenodo records associated with a GitHub repository."""
    # Zenodo API: search for records with the GitHub repo as metadata
    base_url = "https://zenodo.org/api/records"
    params = urllib.parse.urlencode({
        "q": f"github_repo:{github_repo}",
        "size": 20,
        "sort": "most_recent",
    })
    url = f"{base_url}?{params}"

    req = urllib.request.Request(url, headers={"Accept": "application/json", "User-Agent": "coresearcher"})
    with urllib.request.urlopen(req) as resp:
        data = json.loads(resp.read().decode())

    return data

def fetch_github_releases(repo):
    """Fetch releases from GitHub API."""
    url = f"https://api.github.com/repos/{repo}/releases?per_page=10"
    req = urllib.request.Request(url, headers={"Accept": "application/vnd.github+json", "User-Agent": "coresearcher"})
    with urllib.request.urlopen(req) as resp:
        return json.loads(resp.read().decode())

def build_trajectory_graph(github_repo):
    """Build a minimal trajectory graph: paper -> dataset -> software -> release."""
    print(f"=== Fetching Zenodo records for {github_repo} ===")

    # Fetch Zenodo records
    try:
        zenodo_data = fetch_zenodo_records(github_repo)
        records = zenodo_data.get("hits", {}).get("hits", [])
        print(f"Zenodo records found: {len(records)}")
    except Exception as e:
        print(f"Error fetching Zenodo records: {e}")
        records = []

    # Fetch GitHub releases
    try:
        releases = fetch_github_releases(github_repo)
        print(f"GitHub releases found: {len(releases)}")
    except Exception as e:
        print(f"Error fetching GitHub releases: {e}")
        releases = []

    # Build trajectory graph
    trajectory = {
        "github_repo": github_repo,
        "paper": [],
        "dataset": [],
        "software": [],
        "release": [],
    }

    # Classify Zenodo records
    for record in records:
        record_type = "other"
        metadata = record.get("metadata", {})

        # Determine type from metadata
        types = metadata.get("types", {}).get("resourceTypeGeneral", "")
        if "Publication" in types:
            record_type = "paper"
        elif "Dataset" in types:
            record_type = "dataset"
        elif "Software" in types:
            record_type = "software"

        entry = {
            "title": metadata.get("title", ""),
            "doi": record.get("doi", ""),
            "url": record.get("links", {}).get("self", ""),
            "date": metadata.get("publication_date", ""),
            "type": record_type,
        }

        if record_type in trajectory:
            trajectory[record_type].append(entry)

    # Add GitHub releases
    for release in releases:
        entry = {
            "title": f"Release {release.get('tag_name', 'unknown')}",
            "url": release.get("html_url", ""),
            "date": release.get("published_at", ""),
            "tag": release.get("tag_name", ""),
        }
        trajectory["release"].append(entry)

    return trajectory

def main():
    github_repo = "langchain-ai/langgraph"

    trajectory = build_trajectory_graph(github_repo)

    # Save result
    output_path = "artifacts/zenodo_trajectory_report_v0.md"
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write("# Zenodo Trajectory Report — LangGraph\n\n")
        f.write("> Generated from public GitHub + Zenodo data only.\n\n")
        f.write("---\n\n")

        f.write("## 1. Trajectory Graph\n\n")
        f.write("```text\n")
        f.write("Paper\n")
        f.write("  ↓\n")
        f.write("Dataset\n")
        f.write("  ↓\n")
        f.write("Software\n")
        f.write("  ↓\n")
        f.write("Release\n")
        f.write("```\n\n")

        f.write("## 2. Paper\n\n")
        if trajectory["paper"]:
            for p in trajectory["paper"]:
                f.write(f"- [{p['title']}]({p['url']}) ({p['date']})\n")
                f.write(f"  - DOI: {p['doi']}\n")
        else:
            f.write("No paper records found in Zenodo.\n")
        f.write("\n")

        f.write("## 3. Dataset\n\n")
        if trajectory["dataset"]:
            for d in trajectory["dataset"]:
                f.write(f"- [{d['title']}]({d['url']}) ({d['date']})\n")
                f.write(f"  - DOI: {d['doi']}\n")
        else:
            f.write("No dataset records found in Zenodo.\n")
        f.write("\n")

        f.write("## 4. Software\n\n")
        if trajectory["software"]:
            for s in trajectory["software"]:
                f.write(f"- [{s['title']}]({s['url']}) ({s['date']})\n")
                f.write(f"  - DOI: {s['doi']}\n")
        else:
            f.write("No software records found in Zenodo.\n")
        f.write("\n")

        f.write("## 5. Release\n\n")
        if trajectory["release"]:
            for r in trajectory["release"]:
                f.write(f"- [{r['title']}]({r['url']}) ({r['date']})\n")
        else:
            f.write("No releases found.\n")
        f.write("\n")

        f.write("## 6. Methodology\n\n")
        f.write("Este informe se generó exclusivamente a partir de:\n\n")
        f.write("- GitHub API (releases)\n")
        f.write("- Zenodo API (records)\n\n")
        f.write("No se utilizó instrumentación adicional.\n\n")

        f.write("## 7. Metrics\n\n")
        f.write("| Elemento | Conteo |\n")
        f.write("|----------|--------|\n")
        f.write(f"| Paper | {len(trajectory['paper'])} |\n")
        f.write(f"| Dataset | {len(trajectory['dataset'])} |\n")
        f.write(f"| Software | {len(trajectory['software'])} |\n")
        f.write(f"| Release | {len(trajectory['release'])} |\n")

    print(f"\nZenodo Trajectory Report saved to: {output_path}")

    # Also save raw JSON
    with open("data/zenodo_raw.json", 'w') as f:
        json.dump(trajectory, f, indent=2)
    print("Raw data saved to: data/zenodo_raw.json")


if __name__ == "__main__":
    main()
