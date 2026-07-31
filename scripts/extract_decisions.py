#!/usr/bin/env python3
"""
SPRINT 60C: Extract decision signals from GitHub repositories.
Extracts explicit and implicit decisions from issues, PRs, commits, and releases.
"""
import json
import urllib.request
import urllib.parse
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional

class DecisionExtractor:
    """Extract decision signals from GitHub repository data."""
    
    def __init__(self, repo: str, token: Optional[str] = None):
        self.repo = repo
        self.token = token
        self.base_url = f"https://api.github.com/repos/{repo}"
        self.decisions = []
        self.artifacts = []
        
    def _fetch_json(self, url: str) -> Dict:
        """Fetch JSON from GitHub API."""
        headers = {
            "Accept": "application/vnd.github+json",
            "User-Agent": "coresearcher-sprint60c"
        }
        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"
        
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req) as resp:
            return json.loads(resp.read().decode())
    
    def _fetch_paginated(self, url: str, max_pages: int = 10) -> List[Dict]:
        """Fetch paginated results from GitHub API."""
        results = []
        for page in range(1, max_pages + 1):
            sep = "&" if "?" in url else "?"
            url_with_page = f"{url}{sep}page={page}&per_page=100"
            try:
                data = self._fetch_json(url_with_page)
                if isinstance(data, list) and len(data) > 0:
                    results.extend(data)
                else:
                    break
                time.sleep(0.5)  # Rate limiting
            except Exception as e:
                print(f"Error fetching page {page}: {e}")
                break
        return results
    
    def extract_issues(self, state: str = "all", since: Optional[str] = None) -> List[Dict]:
        """Extract issues with decision signals."""
        print(f"Fetching {state} issues...")
        url = f"{self.base_url}/issues?state={state}&sort=updated&direction=desc"
        issues = self._fetch_paginated(url, max_pages=5)
        
        decision_signals = []
        for issue in issues:
            # Skip pull requests (they appear in issues endpoint)
            if "pull_request" in issue:
                continue
                
            signals = self._detect_decision_signals(issue, "issue")
            if signals:
                decision_signals.append({
                    "artifact_type": "issue",
                    "artifact_id": issue["number"],
                    "state": issue["state"],
                    "title": issue["title"],
                    "body": issue.get("body", "")[:500],
                    "created_at": issue["created_at"],
                    "updated_at": issue["updated_at"],
                    "closed_at": issue.get("closed_at"),
                    "labels": [l["name"] for l in issue.get("labels", [])],
                    "signals": signals,
                    "url": issue["html_url"],
                    "author": issue["user"]["login"]
                })
        
        print(f"  Found {len(decision_signals)} issues with decision signals")
        return decision_signals
    
    def extract_prs(self, state: str = "all") -> List[Dict]:
        """Extract pull requests with decision signals."""
        print(f"Fetching {state} PRs...")
        url = f"{self.base_url}/pulls?state={state}&sort=updated&direction=desc"
        prs = self._fetch_paginated(url, max_pages=10)
        
        decision_signals = []
        for pr in prs:
            signals = self._detect_decision_signals(pr, "pr")
            if signals:
                decision_signals.append({
                    "artifact_type": "pr",
                    "artifact_id": pr["number"],
                    "state": pr["state"],
                    "title": pr["title"],
                    "body": pr.get("body", "")[:500],
                    "created_at": pr["created_at"],
                    "merged_at": pr.get("merged_at"),
                    "closed_at": pr.get("closed_at"),
                    "merged": pr.get("merged", False),
                    "signals": signals,
                    "url": pr["html_url"],
                    "author": pr["user"]["login"]
                })
        
        print(f"  Found {len(decision_signals)} PRs with decision signals")
        return decision_signals
    
    def extract_commits(self, since: Optional[str] = None) -> List[Dict]:
        """Extract commits with decision signals."""
        print("Fetching commits...")
        url = f"{self.base_url}/commits?per_page=100"
        commits = self._fetch_paginated(url, max_pages=5)
        
        decision_signals = []
        for commit in commits:
            commit_data = commit.get("commit", {})
            message = commit_data.get("message", "")
            
            signals = self._detect_decision_signals_in_text(message, "commit")
            if signals:
                decision_signals.append({
                    "artifact_type": "commit",
                    "artifact_id": commit["sha"][:7],
                    "message": message[:500],
                    "created_at": commit_data.get("author", {}).get("date", ""),
                    "author": commit_data.get("author", {}).get("name", ""),
                    "signals": signals,
                    "url": commit.get("html_url", "")
                })
        
        print(f"  Found {len(decision_signals)} commits with decision signals")
        return decision_signals
    
    def _detect_decision_signals(self, item: Dict, item_type: str) -> List[str]:
        """Detect decision signals in an issue or PR."""
        text = f"{item.get('title', '')} {item.get('body', '')}"
        return self._detect_decision_signals_in_text(text, item_type)
    
    def _detect_decision_signals_in_text(self, text: str, source_type: str) -> List[str]:
        """Detect decision signals using keyword matching."""
        text_lower = text.lower()
        signals = []
        
        # Explicit decision patterns
        explicit_patterns = [
            (r'we decided to', 'explicit_decision'),
            (r'decision:', 'explicit_decision'),
            (r'chose to', 'explicit_decision'),
            (r'chosen to', 'explicit_decision'),
            (r'opted for', 'explicit_decision'),
            (r'went with', 'explicit_decision'),
            (r'picked', 'explicit_decision'),
            (r'selected', 'explicit_decision'),
            (r'switched to', 'switch'),
            (r'replaced', 'switch'),
            (r'replaced by', 'superseded'),
            (r'superseded', 'superseded'),
            (r'supersedes', 'superseded'),
            (r'instead of', 'alternative_considered'),
            (r'rather than', 'alternative_considered'),
        ]
        
        # Implicit decision patterns
        implicit_patterns = [
            (r'will be removed', 'removal'),
            (r'will be deprecated', 'deprecation'),
            (r'plan to remove', 'removal_plan'),
            (r'no longer', 'removal'),
            (r'abandoned', 'abandonment'),
            (r'archived', 'archival'),
            (r'not pursued', 'not_pursued'),
            (r'won\'t implement', 'rejection'),
            (r'will not', 'rejection'),
        ]
        
        # Outcome patterns
        outcome_patterns = [
            (r'successfully', 'success_indicator'),
            (r'completed', 'completion'),
            (r'finished', 'completion'),
            (r'failed', 'failure_indicator'),
            (r'didn\'t work', 'failure'),
            (r'did not work', 'failure'),
            (r'issues with', 'problems'),
        ]
        
        all_patterns = explicit_patterns + implicit_patterns + outcome_patterns
        
        for pattern, signal_type in all_patterns:
            if pattern in text_lower:
                signals.append(signal_type)
        
        return list(set(signals))  # Deduplicate
    
    def classify_decision(self, artifact: Dict) -> Optional[Dict]:
        """Classify an artifact as a decision node."""
        signals = artifact.get("signals", [])
        
        if not signals:
            return None
        
        # Determine outcome based on artifact state and signals
        outcome = self._determine_outcome(artifact)
        
        # Calculate confidence based on signal strength
        confidence = self._calculate_confidence(artifact)
        
        decision = {
            "decision_id": None,  # Assigned later
            "repository": self.repo,
            "artifact_type": artifact["artifact_type"],
            "artifact_id": artifact["artifact_id"],
            "artifact_url": artifact["url"],
            "title": artifact.get("title", artifact.get("message", ""))[:200],
            "body_snippet": artifact.get("body", artifact.get("message", ""))[:300],
            "actor": artifact.get("author", ""),
            "timestamp": self._get_timestamp(artifact),
            "signals": signals,
            "outcome": outcome,
            "confidence": confidence,
            "rationale": self._extract_rationale(artifact),
            "labels": artifact.get("labels", [])
        }
        
        return decision
    
    def _determine_outcome(self, artifact: Dict) -> str:
        """Determine decision outcome from artifact metadata."""
        if artifact["artifact_type"] == "pr":
            if artifact.get("merged"):
                return "success"
            elif artifact.get("closed_at") and not artifact.get("merged"):
                return "abandoned"
        
        if artifact["artifact_type"] == "issue":
            state = artifact.get("state", "")
            if state == "closed":
                labels = [l.lower() for l in artifact.get("labels", [])]
                if "wontfix" in labels or "obsolete" in labels:
                    return "abandoned"
                elif "duplicate" in labels:
                    return "superseded"
                else:
                    return "success"  # Closed but not clearly abandoned
            elif state == "open":
                # Check for abandonment signals
                signals = artifact.get("signals", [])
                if any(s in signals for s in ["abandonment", "archival", "not_pursued"]):
                    return "abandoned"
                return "pending"
        
        if artifact["artifact_type"] == "commit":
            signals = artifact.get("signals", [])
            if any(s in signals for s in ["failure", "rejection", "removal"]):
                return "failure"
            return "success"
        
        return "unknown"
    
    def _calculate_confidence(self, artifact: Dict) -> float:
        """Calculate extraction confidence score."""
        confidence = 0.5  # Base
        
        # Boost for explicit signals
        signals = artifact.get("signals", [])
        if any("explicit" in s for s in signals):
            confidence += 0.3
        if any(s in signals for s in ["switch", "superseded", "alternative_considered"]):
            confidence += 0.1
        
        # Boost for rich metadata
        if artifact.get("body") and len(artifact["body"]) > 100:
            confidence += 0.1
        
        # Cap at 1.0
        return min(confidence, 1.0)
    
    def _get_timestamp(self, artifact: Dict) -> str:
        """Extract timestamp from artifact."""
        for field in ["closed_at", "merged_at", "updated_at", "created_at"]:
            if artifact.get(field):
                return artifact[field]
        return ""
    
    def _extract_rationale(self, artifact: Dict) -> str:
        """Extract rationale from artifact body."""
        body = artifact.get("body", artifact.get("message", ""))
        # Look for rationale indicators
        rationale_indicators = [
            "because", "since", "due to", "reason:", "rationale:",
            "motivation:", "motivation", "because we", "since we"
        ]
        
        body_lower = body.lower()
        for indicator in rationale_indicators:
            if indicator in body_lower:
                idx = body_lower.index(indicator)
                snippet = body[idx:idx+200]
                return snippet.strip()
        
        return ""
    
    def extract_all(self, since: Optional[str] = None) -> List[Dict]:
        """Extract all decision signals from repository."""
        print(f"\n=== Extracting decisions from {self.repo} ===\n")
        
        # Extract from different sources
        issues = self.extract_issues(state="all", since=since)
        prs = self.extract_prs(state="all")
        commits = self.extract_commits(since=since)
        
        all_artifacts = issues + prs + commits
        
        # Classify each artifact as a decision
        decisions = []
        for artifact in all_artifacts:
            decision = self.classify_decision(artifact)
            if decision:
                decisions.append(decision)
        
        print(f"\n=== Extraction Summary ===")
        print(f"Total artifacts analyzed: {len(all_artifacts)}")
        print(f"Decisions extracted: {len(decisions)}")
        print(f"Success decisions: {sum(1 for d in decisions if d['outcome'] == 'success')}")
        print(f"Abandoned decisions: {sum(1 for d in decisions if d['outcome'] == 'abandoned')}")
        print(f"Superseded decisions: {sum(1 for d in decisions if d['outcome'] == 'superseded')}")
        print(f"Failed decisions: {sum(1 for d in decisions if d['outcome'] == 'failure')}")
        
        return decisions
    
    def save_decisions(self, decisions: List[Dict], output_path: str):
        """Save extracted decisions to JSONL."""
        with open(output_path, "w") as f:
            for i, decision in enumerate(decisions, 1):
                decision["decision_id"] = f"DECISION-{i:06d}"
                f.write(json.dumps(decision, default=str) + "\n")
        
        print(f"\nDecisions saved to {output_path}")


def main():
    """Main execution for SPRINT 60C."""
    import argparse
    
    parser = argparse.ArgumentParser(description="SPRINT 60C: Extract decisions from GitHub")
    parser.add_argument("--repo", required=True, help="Repository in format owner/repo")
    parser.add_argument("--output", default="data/trajectories/decisions.jsonl", help="Output path")
    parser.add_argument("--token", help="GitHub token (optional, increases rate limits)")
    parser.add_argument("--since", help="Only analyze commits/issues since this date (YYYY-MM-DD)")
    
    args = parser.parse_args()
    
    # Create extractor
    extractor = DecisionExtractor(args.repo, token=args.token)
    
    # Extract decisions
    decisions = extractor.extract_all(since=args.since)
    
    # Save results
    extractor.save_decisions(decisions, args.output)
    
    print(f"\nSPRINT 60C extraction complete for {args.repo}")
    print(f"   Decisions extracted: {len(decisions)}")


if __name__ == "__main__":
    main()