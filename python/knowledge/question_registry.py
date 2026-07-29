"""
Question Registry - Sprint 18
Scientific questions as primary knowledge assets.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Optional, List, Dict
from datetime import datetime

# Security tier: PUBLIC — DO NOT MODIFY
# See python/_tiers.py for classification
SECURITY_TIER = "PUBLIC"


REGISTRY_DIR = Path("knowledge/registry")
REGISTRY_DIR.mkdir(parents=True, exist_ok=True)
QUESTIONS_FILE = REGISTRY_DIR / "questions.json"


class QuestionRegistry:
    """
    Registry for scientific questions.
    
    Questions drive the scientific cycle:
    Question → Hypothesis → Prediction → Test → Evidence → Claim
    
    Example:
    {
        "id": "QUESTION-000001",
        "text": "What predicts Alzheimer's disease before PET positivity?",
        "domain": "neurodegeneration",
        "generated_hypotheses": ["HYP-001", "HYP-002"],
        "status": "active",
        "createdAt": "..."
    }
    """
    
    def __init__(self):
        self._questions: dict = self._load()
    
    def _load(self) -> dict:
        """Load questions from disk."""
        if QUESTIONS_FILE.exists():
            with open(QUESTIONS_FILE, 'r') as f:
                return json.load(f)
        return {"questions": {}, "next_id": 1}
    
    def _save(self):
        """Save questions to disk."""
        with open(QUESTIONS_FILE, 'w') as f:
            json.dump(self._questions, f, indent=2)
    
    def register(self,
                 text: str,
                 domain: str = "general",
                 context: str = None,
                 status: str = "active",
                 generated_hypotheses: List[str] = None,
                 related_findings: List[str] = None) -> str:
        """
        Register a scientific question.
        
        Returns:
            Question ID (QUESTION-XXXXXX)
        """
        question_id = f"QUESTION-{self._questions['next_id']:06d}"
        
        question = {
            "id": question_id,
            "text": text,
            "domain": domain,
            "context": context,
            "status": status,
            "generated_hypotheses": generated_hypotheses or [],
            "related_findings": related_findings or [],
            "createdAt": datetime.now().isoformat(),
            "updatedAt": datetime.now().isoformat(),
        }
        
        self._questions["questions"][question_id] = question
        self._questions["next_id"] += 1
        self._save()
        
        return question_id
    
    def get(self, question_id: str) -> Optional[dict]:
        """Get a question by ID."""
        return self._questions["questions"].get(question_id)
    
    def list(self) -> List[dict]:
        """List all questions."""
        return list(self._questions["questions"].values())
    
    def list_by_domain(self, domain: str) -> List[dict]:
        """List questions by domain."""
        return [
            q for q in self._questions["questions"].values()
            if q.get("domain", "").lower() == domain.lower()
        ]
    
    def link_hypothesis(self, question_id: str, hypothesis_id: str):
        """Link a hypothesis to a question."""
        question = self._questions["questions"].get(question_id)
        if question:
            if hypothesis_id not in question.get("generated_hypotheses", []):
                question["generated_hypotheses"].append(hypothesis_id)
                question["updatedAt"] = datetime.now().isoformat()
                self._save()


# =============================================================================
# CLI Test
# =============================================================================

if __name__ == "__main__":
    print("=" * 70)
    print("Sprint 18: Question Registry - Scientific Questions as Assets")
    print("=" * 70)
    
    registry = QuestionRegistry()
    
    sample_questions = [
        {
            "text": "What predicts Alzheimer's before PET positivity?",
            "domain": "neurodegeneration",
        },
        {
            "text": "Can plasma biomarkers replace CSF analysis?",
            "domain": "neurodegeneration",
        },
        {
            "text": "What mechanisms link APOE4 to tau pathology?",
            "domain": "neurodegeneration",
        },
    ]
    
    for q in sample_questions:
        qid = registry.register(**q)
        print(f"\nRegistered: {qid}")
        print(f"  {q['text'][:50]}...")
    
    questions = registry.list()
    print(f"\n" + "=" * 70)
    print(f"Total questions: {len(questions)}")
    print("=" * 70)