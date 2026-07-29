"""
GitHub Connector for Observer
Reconstructs scientific activity from public repositories.
"""

import subprocess
import json
from typing import List, Dict, Optional


def gh_json(cmd: List[str]) -> Dict:
    """Run gh CLI and return parsed JSON."""
    result = subprocess.run(
        ["gh"] + cmd,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        return {}
    try:
        return json.loads(result.stdout) if result.stdout.strip() else {}
    except Exception:
        return {}


def get_repo(repo: str) -> Dict:
    """Get repository metadata."""
    return gh_json(["repo", "view", repo, "--json", 
        "name,description,defaultBranchRef,stargazerCount,forkCount,"
        "primaryLanguage,pushedAt,createdAt,releases,issues,"
        "pullRequests,topContributors,readme,licenseInfo"])


def get_commits(repo: str, limit: int = 200) -> List[Dict]:
    """Get commits from repository."""
    data = gh_json(["commit", "list", "-R", repo, "--json",
        "oid,messageHeadline,committedDate,author,url",
        "--limit", str(limit)])
    if isinstance(data, list):
        return data
    return []


def get_issues(repo: str) -> List[Dict]:
    """Get issues."""
    data = gh_json(["issue", "list", "-R", repo, "--json",
        "number,title,body,createdAt,author,labels,state"])
    if isinstance(data, list):
        return data
    return []


def get_prs(repo: str) -> List[Dict]:
    """Get pull requests."""
    data = gh_json(["pr", "list", "-R", repo, "--json",
        "number,title,body,createdAt,author,mergedAt,labels,state"])
    if isinstance(data, list):
        return data
    return []


def get_readme(repo: str) -> str:
    """Get README content."""
    data = gh_json(["api", f"repos/{repo}/readme", "--jq", ".content"])
    if isinstance(data, str):
        import base64
        try:
            return base64.b64decode(data).decode("utf-8", errors="ignore")
        except Exception:
            return data
    return ""