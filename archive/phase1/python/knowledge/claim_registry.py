"""
Claim Registry - Sprint 9: Evidence Network
Central registry for scientific claims - like CrossRef but for claims.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Optional, List
from datetime import datetime
from uuid import uuid4

# Security tier: COMMUNITY — DO NOT MODIFY
# See python/_tiers.py for classification
SECURITY_TIER = "COMMUNITY"


REGISTRY_DIR = Path("knowledge/registry")
REGISTRY_DIR.mkdir(parents=True, exist_ok=True)
CLAIMS_FILE = REGISTRY_DIR / "claims.json"


class ClaimStatus:
    SUPPORTED = "supported"
    CONTRADICTED = "contradicted"
    UNVALIDATED = "unvalidated"
    PENDING = "pending"


class ClaimRegistry:
    """
    Global registry for scientific claims.
    
    Creates an accumulative asset that grows with each analysis.
    Each claim gets a persistent ID (CLAIM-000001, etc.)
    """
    
    def __init__(self):
        self._claims: dict = self._load()
    
    def _load(self) -> dict:
        """Load claims from disk."""
        if CLAIMS_FILE.exists():
            with open(CLAIMS_FILE, 'r') as f:
                return json.load(f)
        return {"claims": {}, "next_id": 1}
    
    def _save(self):
        """Save claims to disk."""
        with open(CLAIMS_FILE, 'w') as f:
            json.dump(self._claims, f, indent=2)
    
    def register(self, text: str, evidence_score: float = 0.5,
                 supporting_papers: List[str] = None,
                 contradicting_papers: List[str] = None,
                 domain: str = None,
                 entities: List[str] = None,
                 metadata: dict = None) -> str:
        """
        Register a claim in the global registry.
        
        Returns:
            Claim ID (CLAIM-XXXXXX)
        """
        claim_id = f"CLAIM-{self._claims['next_id']:06d}"
        
        claim = {
            "id": claim_id,
            "text": text,
            "evidenceScore": evidence_score,
            "supportingPapers": supporting_papers or [],
            "contradictingPapers": contradicting_papers or [],
            "domain": domain,
            "entities": entities or [],
            "status": ClaimStatus.UNVALIDATED,
            "createdAt": datetime.now().isoformat(),
            "updatedAt": datetime.now().isoformat(),
            "derivedFrom": [],  # Other claims this was derived from
            "usedIn": [],  # Hypotheses that used this claim
            "metadata": metadata or {},
        }
        
        self._claims["claims"][claim_id] = claim
        self._claims["next_id"] += 1
        self._save()
        
        return claim_id
    
    def get(self, claim_id: str) -> Optional[dict]:
        """Get a claim by ID."""
        return self._claims["claims"].get(claim_id)
    
    def list(self) -> List[dict]:
        """List all claims."""
        return list(self._claims["claims"].values())
    
    def list_by_domain(self, domain: str) -> List[dict]:
        """List claims by domain."""
        return [
            c for c in self._claims["claims"].values()
            if c.get("domain") == domain
        ]
    
    def update_status(self, claim_id: str, status: str):
        """Update claim status (supported, contradicted, etc.)."""
        claim = self.get(claim_id)
        if claim:
            claim["status"] = status
            claim["updatedAt"] = datetime.now().isoformat()
            self._save()
    
    def add_supporting_paper(self, claim_id: str, paper_doi: str):
        """Add a supporting paper to a claim."""
        claim = self.get(claim_id)
        if claim and paper_doi not in claim.get("supportingPapers", []):
            claim["supportingPapers"].append(paper_doi)
            claim["evidenceScore"] = min(1.0, claim["evidenceScore"] + 0.05)
            self._save()
    
    def add_contradicting_paper(self, claim_id: str, paper_doi: str):
        """Add a contradicting paper to a claim."""
        claim = self.get(claim_id)
        if claim and paper_doi not in claim.get("contradictingPapers", []):
            claim["contradictingPapers"].append(paper_doi)
            claim["evidenceScore"] = max(0.0, claim["evidenceScore"] - 0.1)
            self._save()


# =============================================================================
# Hypothesis Registry
# =============================================================================

HYPOTHESES_FILE = REGISTRY_DIR / "hypotheses.json"


class HypothesisRegistry:
    """
    Global registry for scientific hypotheses.
    
    Each hypothesis gets a persistent ID (HYP-000001, etc.)
    """
    
    def __init__(self):
        self._hypotheses: dict = self._load()
    
    def _load(self) -> dict:
        """Load hypotheses from disk."""
        if HYPOTHESES_FILE.exists():
            with open(HYPOTHESES_FILE, 'r') as f:
                return json.load(f)
        return {"hypotheses": {}, "next_id": 1}
    
    def _save(self):
        """Save hypotheses to disk."""
        with open(HYPOTHESES_FILE, 'w') as f:
            json.dump(self._hypotheses, f, indent=2)
    
    def register(self, statement: str, evidence_score: float = 0.5,
                 derived_from: List[str] = None,
                 entities: List[str] = None,
                 critique_score: float = None,
                 domain: str = None,
                 metadata: dict = None) -> str:
        """
        Register a hypothesis in the global registry.
        
        Returns:
            Hypothesis ID (HYP-XXXXXX)
        """
        hyp_id = f"HYP-{self._hypotheses['next_id']:06d}"
        
        hypothesis = {
            "id": hyp_id,
            "statement": statement,
            "evidenceScore": evidence_score,
            "derivedFrom": derived_from or [],  # Claim IDs
            "entities": entities or [],
            "criticScore": critique_score,
            "eloRating": int(evidence_score * 1000),
            "status": "generated",
            "domain": domain,
            "createdAt": datetime.now().isoformat(),
            "updatedAt": datetime.now().isoformat(),
            "usedIn": [],  # Experiments, grants that used this
            "metadata": metadata or {},
        }
        
        self._hypotheses["hypotheses"][hyp_id] = hypothesis
        self._hypotheses["next_id"] += 1
        self._save()
        
        # Update claims to reference this hypothesis
        if derived_from:
            claim_registry = ClaimRegistry()
            for claim_id in derived_from:
                claim = claim_registry.get(claim_id)
                if claim:
                    if "usedIn" not in claim:
                        claim["usedIn"] = []
                    claim["usedIn"].append(hyp_id)
                    claim_registry._save()
        
        return hyp_id
    
    def get(self, hyp_id: str) -> Optional[dict]:
        """Get a hypothesis by ID."""
        return self._hypotheses["hypotheses"].get(hyp_id)
    
    def list(self) -> List[dict]:
        """List all hypotheses."""
        return list(self._hypotheses["hypotheses"].values())
    
    def update_elo(self, hyp_id: str, new_elo: int):
        """Update ELO rating after tournament ranking."""
        hypothesis = self.get(hyp_id)
        if hypothesis:
            hypothesis["eloRating"] = new_elo
            hypothesis["updatedAt"] = datetime.now().isoformat()
            self._save()


# =============================================================================
# Evidence Registry
# =============================================================================

EVIDENCE_FILE = REGISTRY_DIR / "evidence.json"


class EvidenceRegistry:
    """
    Global registry for scientific evidence.
    """
    
    def __init__(self):
        self._evidence: dict = self._load()
    
    def _load(self) -> dict:
        """Load evidence from disk."""
        if EVIDENCE_FILE.exists():
            with open(EVIDENCE_FILE, 'r') as f:
                return json.load(f)
        return {"evidence": {}, "next_id": 1}
    
    def _save(self):
        """Save evidence to disk."""
        with open(EVIDENCE_FILE, 'w') as f:
            json.dump(self._evidence, f, indent=2)
    
    def register(self, value: str, evidence_type: str = "observational",
                 quality_score: float = 0.5,
                 sample_size: int = None,
                 p_value: float = None,
                 effect_size: float = None,
                 paper_doi: str = None,
                 claim_id: str = None,
                 metadata: dict = None) -> str:
        """
        Register evidence in the global registry.
        
        Returns:
            Evidence ID (EVID-XXXXXX)
        """
        evid_id = f"EVID-{self._evidence['next_id']:06d}"
        
        evidence = {
            "id": evid_id,
            "value": value,
            "type": evidence_type,
            "qualityScore": quality_score,
            "sampleSize": sample_size,
            "pValue": p_value,
            "effectSize": effect_size,
            "paperDoi": paper_doi,
            "claimId": claim_id,
            "createdAt": datetime.now().isoformat(),
            "metadata": metadata or {},
        }
        
        self._evidence["evidence"][evid_id] = evidence
        self._evidence["next_id"] += 1
        self._save()
        
        return evid_id
    
    def get(self, evid_id: str) -> Optional[dict]:
        """Get evidence by ID."""
        return self._evidence["evidence"].get(evid_id)
    
    def list(self) -> List[dict]:
        """List all evidence."""
        return list(self._evidence["evidence"].values())


# =============================================================================
# CLI Test
# =============================================================================

if __name__ == "__main__":
    print("=" * 70)
    print("Sprint 9: Evidence Network - Claim Registry")
    print("=" * 70)
    
    # Register some claims
    claims = [
        ("Plasma pTau217 predicts amyloid positivity in cognitively unimpaired individuals", 0.82, "neurodiagnoses"),
        ("APOE4 increases Alzheimer risk by 3-15x depending on population", 0.75, "genomics"),
        ("CSF NfL correlates with neurodegeneration rate in ALS", 0.68, "neurodiagnosis"),
    ]
    
    claim_registry = ClaimRegistry()
    for text, score, domain in claims:
        claim_id = claim_registry.register(text, score, domain=domain)
        print(f"\nRegistered {claim_id}:")
        print(f"  {text[:60]}...")
        print(f"  Evidence Score: {score}")
    
    # Register hypotheses
    hyp_registry = HypothesisRegistry()
    hyp_id = hyp_registry.register(
        statement="Plasma pTau217 predicts preclinical Alzheimer with 5-year horizon",
        evidence_score=0.78,
        derived_from=["CLAIM-000001"],
        domain="neurodiagnosis"
    )
    print(f"\n\nRegistered {hyp_id}")
    
    # Register evidence
    evid_registry = EvidenceRegistry()
    evid_id = evid_registry.register(
        value="pTau217 levels in plasma correlate with brain amyloid burden (r=0.78)",
        evidence_type="clinical_trial",
        quality_score=0.89,
        sample_size=1254,
        p_value=0.001,
        effect_size=0.78,
        paper_doi="10.1038/s41591-025-12345"
    )
    print(f"\nRegistered {evid_id}")
    
    print("\n" + "=" * 70)
    print(f"Total claims: {len(claim_registry.list())}")
    print(f"Total hypotheses: {len(hyp_registry.list())}")
    print(f"Total evidence: {len(evid_registry.list())}")
    print("=" * 70)