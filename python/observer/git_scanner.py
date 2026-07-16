"""
Git Scanner for Scientific Activity
Reconstructs project history from git commits and messages.
"""

import subprocess
import json
import re
from pathlib import Path
from datetime import datetime
from typing import List, Dict


def extract_commit_messages(repo_path: str = ".") -> List[Dict]:
    """Extract commit messages from git log."""
    result = subprocess.run(
        ["git", "log", "--pretty=format:%H|%ad|%s", "--date=iso"],
        cwd=repo_path,
        capture_output=True,
        text=True
    )
    
    commits = []
    for line in result.stdout.strip().split("\n"):
        if "|" in line:
            parts = line.split("|", 2)
            commits.append({
                "hash": parts[0],
                "date": parts[1],
                "message": parts[2] if len(parts) > 2 else ""
            })
    
    return commits


def infer_questions(commits: List[Dict]) -> List[Dict]:
    """Infer questions from commit messages."""
    questions = []
    
    # Patterns that suggest questions/research directions
    question_patterns = [
        r"question:\s*(.+)",
        r"research\s+(.+)",
        r"investigate\s+(.+)",
        r"what\s+if\s+(.+)",
        r"how\s+to\s+(.+)",
        r"why\s+(.+)"
    ]
    
    for i, commit in enumerate(commits):
        msg = commit["message"].lower()
        for pattern in question_patterns:
            match = re.search(pattern, msg)
            if match:
                questions.append({
                    "id": f"QUESTION-{len(questions)+1:06d}",
                    "text": match.group(1).capitalize(),
                    "inferred_from": commit["hash"][:7],
                    "date": commit["date"]
                })
                break
    
    return questions


def infer_actions(commits: List[Dict]) -> List[Dict]:
    """Infer actions from commits."""
    actions = []
    
    action_keywords = [
        "add", "create", "implement", "fix", "update", 
        "remove", "refactor", "optimize", "test"
    ]
    
    for i, commit in enumerate(commits):
        msg = commit["message"]
        # Check for action indicators
        for keyword in action_keywords:
            if keyword in msg.lower():
                actions.append({
                    "id": f"ACTION-{len(actions)+1:06d}",
                    "description": msg,
                    "from_commit": commit["hash"][:7],
                    "date": commit["date"],
                    "executed_by": "git-author"  # Will improve with agent detection
                })
                break
    
    return actions


def infer_artifacts(commits: List[Dict], repo_path: str = ".") -> List[Dict]:
    """Infer artifacts from releases/tags."""
    result = subprocess.run(
        ["git", "tag"],
        cwd=repo_path,
        capture_output=True,
        text=True
    )
    
    artifacts = []
    for tag in result.stdout.strip().split("\n"):
        if tag:
            artifacts.append({
                "id": f"ARTIFACT-{len(artifacts)+1:06d}",
                "type": "release",
                "tag": tag,
                "date": datetime.now().isoformat()
            })
    
    return artifacts


def reconstruct_ledger(repo_path: str = ".") -> Dict:
    """Reconstruct complete scientific activity ledger."""
    commits = extract_commit_messages(repo_path)
    
    return {
        "questions": infer_questions(commits),
        "actions": infer_actions(commits),
        "artifacts": infer_artifacts(commits, repo_path),
        "total_commits": len(commits),
        "timeline": [
            {"date": c["date"], "event": c["message"][:50]}
            for c in commits[:50]  # Last 50 events
        ]
    }


if __name__ == "__main__":
    ledger = reconstruct_ledger()
    
    print("=" * 70)
    print("CORESEARCHER ACTIVITY LEDGER")
    print("=" * 70)
    
    print(f"\nTotal commits analyzed: {ledger['total_commits']}")
    print(f"Questions inferred: {len(ledger['questions'])}")
    print(f"Actions inferred: {len(ledger['actions'])}")
    print(f"Artifacts inferred: {len(ledger['artifacts'])}")
    
    print("\n" + "=" * 70)
    print("SAMPLE QUESTIONS")
    print("=" * 70)
    for q in ledger['questions'][:5]:
        print(f"  {q['id']}: {q['text'][:60]}...")
    
    print("\n" + "=" * 70)
    print("SAMPLE ACTIONS")
    print("=" * 70)
    for a in ledger['actions'][:5]:
        print(f"  {a['id']}: {a['description'][:60]}...")