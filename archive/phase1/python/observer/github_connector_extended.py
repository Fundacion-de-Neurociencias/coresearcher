"""
Extended GitHub Connector - Sprint 28
Maps GitHub evidence to ScientificArtifact objects.
"""

from __future__ import annotations

import re
import subprocess
import json
from typing import List, Dict, Optional
from pathlib import Path

from observer.scientific_artifact import ScientificArtifact, Contributor


def gh_json(cmd: List[str]) -> Dict:
    """Run gh CLI with UTF-8 safe handling and return parsed JSON."""
    try:
        result = subprocess.run(
            ["gh"] + cmd,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
        )
        if result.returncode != 0:
            return {}
        text = (result.stdout or "").strip()
        return json.loads(text) if text else {}
    except Exception:
        return {}


def get_repo(repo: str) -> Dict:
    """Get repository metadata."""
    return gh_json(["repo", "view", repo, "--json",
        "name,description,defaultBranchRef,stargazerCount,forkCount,"
        "primaryLanguage,pushedAt,createdAt,releases,issues,"
        "pullRequests,topContributors,readme,licenseInfo"])


def get_readme(repo: str) -> str:
    """Get README content."""
    data = gh_json(["api", f"repos/{repo}/readme", "--jq", ".content"])
    if isinstance(data, str):
        import base64
        try:
            return base64.b64decode(data).decode("utf-8", errors="replace")
        except Exception:
            return data
    return ""


def get_releases(repo: str, limit: int = 20) -> List[Dict]:
    """Get recent releases."""
    data = gh_json(["release", "list", "-R", repo, "--json",
        "tagName,name,body,publishedAt,author", "--limit", str(limit)])
    if isinstance(data, list):
        return data
    return []


def get_contributors(repo: str, limit: int = 30) -> List[Dict]:
    """Get top contributors."""
    data = gh_json(["api", f"repos/{repo}/contributors?per_page={limit}", "--jq", ".[] | {login,contributions,avatar_url,html_url}"])
    if isinstance(data, list):
        return data
    return []


def extract_doi(text: str) -> Optional[str]:
    """Extract DOI from text."""
    m = re.search(r"10\.\d{4,}/\S+", text)
    return m.group(0) if m else None


def map_repo_to_artifacts(repo: str) -> List[ScientificArtifact]:
    """Map GitHub repo evidence to ScientificArtifacts."""
    artifacts: List[ScientificArtifact] = []
    repo_meta = get_repo(repo)
    readme = get_readme(repo)
    releases = get_releases(repo)
    contributors_raw = get_contributors(repo, limit=30)

    repo_name = repo_meta.get("name") or repo.split("/")[-1]

    software = ScientificArtifact(
        artifact_id=f"github:{repo}:latest",
        type="software_release",
        title=repo_meta.get("description") or repo_name,
        github_repo=repo,
        github_release=(releases[0].get("tagName") if releases else None),
        contributors=[Contributor(name=c.get("login", ""), github=c.get("login", "")) for c in contributors_raw[:10]],
        evidence_sources=["github"],
        notes=f"Derived from GitHub repo {repo}",
    )
    if releases:
        body = releases[0].get("body") or ""
        doi = extract_doi(body)
        if doi:
            software.doi = doi
    artifacts.append(software)

    paper = None
    if readme:
        doi = extract_doi(readme)
        if doi:
            paper = ScientificArtifact(
                artifact_id=f"paper:{doi}",
                type="paper",
                doi=doi,
                title=(readme.splitlines()[0] if readme.splitlines() else repo),
                github_repo=repo,
                contributors=[],
                evidence_sources=["github:readme"],
                notes="DOI found in README",
            )
            artifacts.append(paper)

    for rel in releases[:3]:
        tag = rel.get("tagName")
        if not tag:
            continue
        body = rel.get("body") or ""
        doi = extract_doi(body)
        release_artifact = ScientificArtifact(
            artifact_id=f"github:{repo}:{tag}",
            type="software_release",
            title=rel.get("name") or tag,
            github_repo=repo,
            github_release=tag,
            doi=doi,
            contributors=[],
            evidence_sources=["github:release"],
            notes=f"Release {tag} artifact",
        )
        artifacts.append(release_artifact)

    return artifacts