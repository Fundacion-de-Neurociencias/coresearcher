"""
Evidence Extractor
Classifies activity as ENGINEERING vs SCIENTIFIC
"""

import re
from typing import List, Dict, Tuple


def classify_activity(text: str) -> Tuple[str, str]:
    """
    Classify text into category and confidence.
    Returns: (category, confidence)
    """
    
    engineering_patterns = [
        (r"\brefactor\b", "engineering"),
        (r"\btest\b", "engineering"),
        (r"\bbugfix\b", "engineering"),
        (r"\bCI/CD\b", "engineering"),
        (r"\binfrastructure\b", "engineering"),
        (r"\bdocker\b", "engineering"),
        (r"\blog\b", "engineering"),
    ]
    
    scientific_patterns = [
        (r"\bhipótesis\b", "scientific"),
        (r"\bhypothesis\b", "scientific"),
        (r"\bmecanismo\b", "scientific"),
        (r"\bmechanism\b", "scientific"),
        (r"\bmodo?el\b", "scientific"),
        (r"\bmodel\b", "scientific"),
        (r"\banálisis\b", "scientific"),
        (r"\bvalidation\b", "scientific"),
        (r"\bfigure\b", "scientific"),
        (r"\bmanuscrito\b", "scientific"),
        (r"\bpaper\b", "scientific"),
        (r"\bresultado\b", "scientific"),
        (r"\bresult\b", "scientific"),
        (r"\botology\b", "scientific"),
        (r"\bdataset\b", "scientific"),
    ]
    
    text_lower = text.lower()
    
    # Check scientific first (higher priority)
    for pattern, category in scientific_patterns:
        if re.search(pattern, text_lower):
            return ("scientific", "high")
    
    for pattern, category in engineering_patterns:
        if re.search(pattern, text_lower):
            return ("engineering", "high")
    
    return ("unknown", "low")


def extract_evidence(commits: List[Dict]) -> Dict[str, List[Dict]]:
    """Extract and classify evidence from commits."""
    
    evidence = {
        "scienctific": [],
        "engineering": [],
        "unknown": []
    }
    
    for commit in commits:
        msg = commit.get("message", "")
        cat, conf = classify_activity(msg)
        
        evidence[cat].append({
            "commit": commit.get("hash", "")[:7],
            "date": commit.get("date", ""),
            "text": msg[:100],
            "confidence": conf
        })
    
    return evidence


def group_scientific_evidence(evidence_list: List[Dict]) -> List[Dict]:
    """Group scientific evidence into potential objectives."""
    
    # Simple temporal clustering
    clusters = []
    current_cluster = []
    
    for ev in evidence_list:
        if not current_cluster:
            current_cluster.append(ev)
        else:
            # Check if within 2 weeks of last evidence
            if is_close(ev, current_cluster[-1]):
                current_cluster.append(ev)
            else:
                if len(current_cluster) > 2:  # Minimum threshold
                    clusters.append({
                        "evidence": [e["commit"] for e in current_cluster],
                        "period": f"{current_cluster[0]['date']} → {current_cluster[-1]['date']}",
                        "hypothesis": "Related scientific effort"
                    })
                current_cluster = [ev]
    
    if len(current_cluster) > 2:
        clusters.append({
            "evidence": [e["commit"] for e in current_cluster],
            "period": f"{current_cluster[0]['date']} → {current_cluster[-1]['date']}",
            "hypothesis": "Related scientific effort"
        })
    
    return clusters


def is_close(ev1: Dict, ev2: Dict) -> bool:
    """Check if two evidence units are temporally close."""
    # Simplified - just check if same month/year
    date1 = ev1.get("date", "")[:7]
    date2 = ev2.get("date", "")[:7]
    return date1 == date2


if __name__ == "__main__":
    # Test with sample commits
    test_commits = [
        {"hash": "abc123", "date": "2024-01-15", "message": "feat: add biomarker ontology"},
        {"hash": "def456", "date": "2024-01-16", "message": "fix: parser bug"},
        {"hash": "ghi789", "date": "2024-01-17", "message": "add: hypothesis on APOE4 mechanism"},
        {"hash": "jkl012", "date": "2024-01-18", "message": "test: add unit tests"},
        {"hash": "mno345", "date": "2024-01-20", "message": "docs: write results section"},
    ]
    
    evidence = extract_evidence(test_commits)
    clusters = group_scientific_evidence(evidence["scientific"])
    
    print(f"Scientific evidence: {len(evidence['scientific'])}")
    print(f"Engineering evidence: {len(evidence['engineering'])}")
    print(f"Scientific clusters: {len(clusters)}")