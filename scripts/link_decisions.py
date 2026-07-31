#!/usr/bin/env python3
"""
SPRINT 60C: Link decisions to reconstruct trajectory edges.
Detects chosen_over, superseded_by, abandoned_for relationships.
"""
import json
from typing import Dict, List, Optional

class DecisionLinker:
    """Link decisions based on evidence patterns."""
    
    def __init__(self):
        self.abandonment_labels = {"wontfix", "obsolete", "invalid", "duplicate"}
    
    def link_decisions(self, decisions: List[Dict]) -> List[Dict]:
        """Create edges between related decisions."""
        edges = []
        decisions_by_id = {d["decision_id"]: d for d in decisions}
        
        # Sort by timestamp
        sorted_decisions = sorted(
            [d for d in decisions if d.get("timestamp")],
            key=lambda d: d["timestamp"]
        )
        
        for i, d1 in enumerate(sorted_decisions):
            for d2 in sorted_decisions[i+1:]:
                edge = self._detect_relationship(d1, d2)
                if edge:
                    edges.append(edge)
        
        return edges
    
    def _detect_relationship(self, d1: Dict, d2: Dict) -> Optional[Dict]:
        """Detect relationship between two decisions."""
        # Check for superseded_by (d2 explicitly replaces d1)
        if self._is_superseded(d1, d2):
            return {
                "from": d1["decision_id"],
                "to": d2["decision_id"],
                "type": "superseded_by",
                "confidence": 0.9,
                "evidence": []
            }
        
        # Check for chosen_over (d1 abandoned, d2 success, same context)
        if self._is_chosen_over(d1, d2):
            return {
                "from": d2["decision_id"],
                "to": d1["decision_id"],
                "type": "chosen_over",
                "confidence": 0.7,
                "evidence": []
            }
        
        # Check for abandoned_for (d1 abandoned, d2 is alternative)
        if self._is_abandoned_for(d1, d2):
            return {
                "from": d1["decision_id"],
                "to": d2["decision_id"],
                "type": "abandoned_for",
                "confidence": 0.6,
                "evidence": []
            }
        
        return None
    
    def _is_superseded(self, d1: Dict, d2: Dict) -> bool:
        """Check if d2 supersedes d1."""
        # Look for explicit references
        d1_id_num = d1["decision_id"].split("-")[1]
        d2_id_num = d2["decision_id"].split("-")[1]
        
        d1_text = json.dumps(d1).lower()
        d2_text = json.dumps(d2).lower()
        
        # Check for "supersedes", "replaces", "instead of" patterns
        if "supersede" in d2_text or "replace" in d2_text:
            if d1_id_num in d2_text or self._similar_context(d1, d2):
                return True
        
        return False
    
    def _is_chosen_over(self, d1: Dict, d2: Dict) -> bool:
        """Check if d2 was chosen over d1."""
        if not (d1.get("outcome") == "abandoned" and d2.get("outcome") == "success"):
            return False
        
        # Must be close in time (within 30 days)
        try:
            from datetime import datetime
            t1 = datetime.fromisoformat(d1["timestamp"].replace("Z", "+00:00"))
            t2 = datetime.fromisoformat(d2["timestamp"].replace("Z", "+00:00"))
            if abs((t2 - t1).days) > 30:
                return False
        except:
            pass
        
        # Must share context (similar titles or same artifact type)
        return self._similar_context(d1, d2)
    
    def _is_abandoned_for(self, d1: Dict, d2: Dict) -> bool:
        """Check if d1 was abandoned for d2."""
        if not (d1.get("outcome") == "abandoned"):
            return False
        
        # d2 should be success or pending
        if d2.get("outcome") not in ["success", "pending"]:
            return False
        
        return self._similar_context(d1, d2)
    
    def _similar_context(self, d1: Dict, d2: Dict) -> bool:
        """Check if two decisions share similar context."""
        title1 = d1.get("decision", d1.get("title", "")).lower()
        title2 = d2.get("decision", d2.get("title", "")).lower()
        
        # Simple word overlap
        words1 = set(title1.split())
        words2 = set(title2.split())
        
        # Remove common words
        stop_words = {"the", "a", "an", "to", "for", "in", "on", "of", "and", "or", "is", "was"}
        words1 -= stop_words
        words2 -= stop_words
        
        if not words1 or not words2:
            return False
        
        overlap = len(words1 & words2)
        smaller = min(len(words1), len(words2))
        
        return overlap / smaller >= 0.3 if smaller > 0 else False
    
    def link_batch(self, decisions: List[Dict]) -> List[Dict]:
        """Link a batch of decisions."""
        edges = self.link_decisions(decisions)
        
        # Deduplicate edges
        seen = set()
        unique_edges = []
        for edge in edges:
            key = (edge["from"], edge["to"], edge["type"])
            if key not in seen:
                seen.add(key)
                unique_edges.append(edge)
        
        return unique_edges


def main():
    import argparse
    parser = argparse.ArgumentParser(description="SPRINT 60C: Link decisions")
    parser.add_argument("--input", required=True, help="Input decisions JSONL")
    parser.add_argument("--output", required=True, help="Output edges JSONL")
    args = parser.parse_args()
    
    # Load decisions
    decisions = []
    with open(args.input, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                decisions.append(json.loads(line))
    
    linker = DecisionLinker()
    edges = linker.link_batch(decisions)
    
    with open(args.output, "w", encoding="utf-8") as f:
        for edge in edges:
            f.write(json.dumps(edge) + "\n")
    
    print(f"Linked {len(decisions)} decisions into {len(edges)} edges")
    print(f"Output: {args.output}")


if __name__ == "__main__":
    main()