#!/usr/bin/env python3
"""
SPRINT 60C: Classify extracted artifacts as DecisionNodes.
Heuristic + pattern-based classification.
"""
import json
import re
from typing import Dict, List, Optional

class DecisionClassifier:
    """Classify GitHub artifacts into Decision nodes."""
    
    def __init__(self):
        self.abandonment_labels = {"wontfix", "obsolete", "invalid", "duplicate"}
        self.explicit_indicators = [
            "we decided", "decision:", "chose to", "opted for",
            "switched to", "replaced", "superseded", "instead of"
        ]
    
    def classify(self, artifact: Dict) -> Optional[Dict]:
        """Classify a single artifact as a DecisionNode."""
        signals = artifact.get("signals", [])
        if not signals:
            return None
        
        outcome = self._determine_outcome(artifact)
        confidence = self._calculate_confidence(artifact)
        
        # Extract evidence references
        evidence = self._build_evidence(artifact)
        
        decision = {
            "decision_id": None,
            "repository": artifact.get("repository", ""),
            "artifact_type": artifact["artifact_type"],
            "artifact_id": artifact["artifact_id"],
            "artifact_url": artifact.get("url", ""),
            "decision": self._extract_decision_text(artifact),
            "actor": artifact.get("author", ""),
            "timestamp": artifact.get("created_at", artifact.get("updated_at", "")),
            "rationale": self._extract_rationale(artifact),
            "outcome": outcome,
            "confidence": confidence,
            "signals": signals,
            "evidence": evidence,
            "classification": "observable" if confidence >= 0.9 else "derivable"
        }
        
        return decision
    
    def _determine_outcome(self, artifact: Dict) -> str:
        """Determine outcome from artifact state and signals."""
        atype = artifact.get("artifact_type")
        
        if atype == "pr":
            if artifact.get("merged"):
                return "success"
            elif artifact.get("closed_at"):
                return "abandoned" if not artifact.get("merged") else "success"
        
        if atype == "issue":
            labels = {l.lower() for l in artifact.get("labels", [])}
            if artifact.get("state") == "closed":
                if labels & self.abandonment_labels:
                    return "abandoned"
                return "success"
            else:
                # Open issue with abandonment signals
                signals = artifact.get("signals", [])
                if any(s in ["abandonment", "archival", "not_pursued", "rejection"] for s in signals):
                    return "abandoned"
                return "pending"
        
        if atype == "commit":
            signals = artifact.get("signals", [])
            if any(s in ["failure", "rejection", "removal"] for s in signals):
                return "failure"
            return "success"
        
        return "unknown"
    
    def _calculate_confidence(self, artifact: Dict) -> float:
        """Calculate confidence score for classification."""
        confidence = 0.6  # Base
        
        signals = artifact.get("signals", [])
        
        # Boost for explicit decision language
        if any("explicit" in s for s in signals):
            confidence += 0.25
        elif any(s in ["switch", "superseded", "alternative_considered"] for s in signals):
            confidence += 0.15
        
        # Boost for outcome evidence
        if artifact.get("artifact_type") == "pr":
            if artifact.get("merged"):
                confidence += 0.1
            elif artifact.get("closed_at") and not artifact.get("merged"):
                confidence -= 0.1
        
        # Cap and floor
        return max(0.0, min(1.0, confidence))
    
    def _extract_decision_text(self, artifact: Dict) -> str:
        """Extract concise decision statement."""
        title = artifact.get("title", artifact.get("message", ""))
        body = artifact.get("body", "")[:200]
        
        # Look for explicit decision pattern
        for indicator in self.explicit_indicators:
            pattern = rf'({indicator}[^.!?]{{0,100}})'
            match = re.search(pattern, f"{title} {body}", re.IGNORECASE)
            if match:
                return match.group(1).strip()
        
        # Fallback to title
        return title[:200]
    
    def _extract_rationale(self, artifact: Dict) -> str:
        """Extract rationale snippet."""
        text = artifact.get("body", artifact.get("message", ""))
        if not text:
            return ""
        
        text_lower = text.lower()
        indicators = ["because", "since", "due to", "reason:", "motivation:"]
        
        for indicator in indicators:
            idx = text_lower.find(indicator)
            if idx >= 0:
                snippet = text[idx:idx + 200].strip()
                return snippet
        
        return ""
    
    def _build_evidence(self, artifact: Dict) -> List[Dict]:
        """Build evidence references."""
        evidence = []
        atype = artifact.get("artifact_type")
        aid = artifact.get("artifact_id")
        
        if atype == "issue":
            evidence.append({"type": "issue", "id": aid, "url": artifact.get("url", "")})
        elif atype == "pr":
            evidence.append({"type": "pr", "id": aid, "url": artifact.get("url", "")})
        elif atype == "commit":
            evidence.append({"type": "commit", "id": aid, "url": artifact.get("url", "")})
        
        return evidence
    
    def classify_batch(self, artifacts: List[Dict]) -> List[Dict]:
        """Classify a batch of artifacts."""
        decisions = []
        for artifact in artifacts:
            decision = self.classify(artifact)
            if decision:
                decisions.append(decision)
        return decisions


def load_artifacts(path: str) -> List[Dict]:
    """Load artifacts from JSONL."""
    artifacts = []
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                artifacts.append(json.loads(line))
    return artifacts


def main():
    import argparse
    parser = argparse.ArgumentParser(description="SPRINT 60C: Classify decisions")
    parser.add_argument("--input", required=True, help="Input artifacts JSONL")
    parser.add_argument("--output", required=True, help="Output decisions JSONL")
    args = parser.parse_args()
    
    classifier = DecisionClassifier()
    artifacts = load_artifacts(args.input)
    decisions = classifier.classify_batch(artifacts)
    
    with open(args.output, "w", encoding="utf-8") as f:
        for i, decision in enumerate(decisions, 1):
            decision["decision_id"] = f"DECISION-{i:06d}"
            f.write(json.dumps(decision, default=str) + "\n")
    
    print(f"Classified {len(decisions)} decisions")
    print(f"Output: {args.output}")


if __name__ == "__main__":
    main()