"""
Researcher Registry - Sprint 11A
Scientific identity layer for claim validation.
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
RESEARCHERS_FILE = REGISTRY_DIR / "researchers.json"


class ResearcherRegistry:
    """
    Registry for scientific researchers and institutions.
    
    Similar to ORCID but integrated with CoResearcher validation.
    """
    
    def __init__(self):
        self._researchers: dict = self._load()
    
    def _load(self) -> dict:
        """Load researchers from disk."""
        if RESEARCHERS_FILE.exists():
            with open(RESEARCHERS_FILE, 'r') as f:
                return json.load(f)
        return {"researchers": {}, "next_id": 1}
    
    def _save(self):
        """Save researchers to disk."""
        with open(RESEARCHERS_FILE, 'w') as f:
            json.dump(self._researchers, f, indent=2)
    
    def register(self, name: str, orcid: str = None,
                 institution: str = None,
                 domain_expertise: List[str] = None,
                 publication_count: int = 0,
                 h_index: int = 0,
                 metadata: dict = None) -> str:
        """
        Register a researcher.
        
        Returns:
            Researcher ID (RES-XXXXXX)
        """
        researcher_id = f"RES-{self._researchers['next_id']:06d}"
        
        researcher = {
            "id": researcher_id,
            "name": name,
            "orcid": orcid,
            "institution": institution,
            "domain_expertise": domain_expertise or [],
            "publication_count": publication_count,
            "h_index": h_index,
            "reputation_score": self._calculate_reputation(publication_count, h_index),
            "contributions": {
                "supported_claims": [],
                "challenged_claims": [],
                "replicated_claims": [],
                "extended_claims": [],
            },
            "createdAt": datetime.now().isoformat(),
            "metadata": metadata or {},
        }
        
        self._researchers["researchers"][researcher_id] = researcher
        self._researchers["next_id"] += 1
        self._save()
        
        return researcher_id
    
    def _calculate_reputation(self, pub_count: int, h_index: int) -> int:
        """Calculate initial reputation score."""
        base = min(100, pub_count * 2)
        h_bonus = min(50, h_index * 5)
        return min(100, base + h_bonus)
    
    def get(self, researcher_id: str) -> Optional[dict]:
        """Get a researcher by ID."""
        return self._researchers["researchers"].get(researcher_id)
    
    def list(self) -> List[dict]:
        """List all researchers."""
        return list(self._researchers["researchers"].values())
    
    def support_claim(self, researcher_id: str, claim_id: str, note: str = None):
        """Record that a researcher supports a claim."""
        researcher = self.get(researcher_id)
        if researcher:
            contribution = {"claim_id": claim_id, "note": note, "date": datetime.now().isoformat()}
            researcher["contributions"]["supported_claims"].append(contribution)
            researcher["reputation_score"] = min(100, researcher["reputation_score"] + 1)
            self._save()
    
    def challenge_claim(self, researcher_id: str, claim_id: str, note: str = None):
        """Record that a researcher challenges a claim."""
        researcher = self.get(researcher_id)
        if researcher:
            contribution = {"claim_id": claim_id, "note": note, "date": datetime.now().isoformat()}
            researcher["contributions"]["challenged_claims"].append(contribution)
            researcher["reputation_score"] = min(100, researcher["reputation_score"] + 2)
            self._save()
    
    def replicate_claim(self, researcher_id: str, claim_id: str, evidence: str = None):
        """Record that a researcher has replicated a claim."""
        researcher = self.get(researcher_id)
        if researcher:
            contribution = {"claim_id": claim_id, "evidence": evidence, "date": datetime.now().isoformat()}
            researcher["contributions"]["replicated_claims"].append(contribution)
            researcher["reputation_score"] = min(100, researcher["reputation_score"] + 5)
            self._save()


class InstitutionRegistry:
    """
    Registry for scientific institutions.
    """
    
    def __init__(self):
        self._institutions: dict = {}
    
    def register(self, name: str, country: str = None,
                 ror: str = None,
                 expertise_areas: List[str] = None) -> str:
        """Register an institution."""
        inst_id = f"INST-{uuid4().hex[:8].upper()}"
        
        self._institutions[inst_id] = {
            "id": inst_id,
            "name": name,
            "country": country,
            "ror": ror,
            "expertise_areas": expertise_areas or [],
            "researchers": [],
            "endorsed_claims": [],
        }
        
        return inst_id
    
    def get(self, inst_id: str) -> Optional[dict]:
        """Get an institution by ID."""
        return self._institutions.get(inst_id)
    
    def list(self) -> List[dict]:
        """List all institutions."""
        return list(self._institutions.values())


# =============================================================================
# Consensus Engine
# =============================================================================

class ConsensusEngine:
    """
    Generates scientific consensus from validated claims.
    """
    
    def __init__(self, claim_registry, researcher_registry, trust_framework):
        self.claims = claim_registry
        self.researchers = researcher_registry
        self.trust = trust_framework
    
    def generate_consensus(self, claim_id: str) -> dict:
        """
        Generate consensus level for a claim.
        """
        claim = self.claims.get(claim_id)
        if not claim:
            return {"error": "Claim not found"}
        
        trust_report = self.trust.get_trust_report(claim_id)
        
        # Count supporting researchers
        supporting_res = 0
        supporting_insts = set()
        
        for researcher in self.researchers.list():
            for contrib in researcher.get("contributions", {}).get("supported_claims", []):
                if contrib.get("claim_id") == claim_id:
                    supporting_res += 1
                    if researcher.get("institution"):
                        supporting_insts.add(researcher["institution"])
        
        # Determine consensus level
        consensus_level = self._determine_level(
            trust_report["trust_index"],
            supporting_res,
            len(supporting_insts)
        )
        
        return {
            "claim_id": claim_id,
            "consensus_level": consensus_level,
            "trust_index": trust_report["trust_index"],
            "supporting_researchers": supporting_res,
            "supporting_institutions": list(supporting_insts),
            "supporting_institution_count": len(supporting_insts),
            "evidence_count": len(claim.get("supportingPapers", [])),
            "contradiction_count": len(claim.get("contradictingPapers", [])),
        }
    
    def _determine_level(self, trust_index: int, researchers: int, institutions: int) -> str:
        """Determine consensus level."""
        if trust_index >= 90 and researchers >= 50 and institutions >= 20:
            return "Strong Consensus"
        elif trust_index >= 80 and researchers >= 20 and institutions >= 10:
            return "Moderate Consensus"
        elif trust_index >= 70 and researchers >= 5:
            return "Emerging Consensus"
        elif trust_index >= 50:
            return "Preliminary Support"
        else:
            return "Unvalidated"


# =============================================================================
# CLI Test
# =============================================================================

if __name__ == "__main__":
    print("=" * 70)
    print("Sprint 11A - Scientific Identity & Consensus Layer")
    print("=" * 70)
    
    # Register researchers
    reg = ResearcherRegistry()
    
    res1 = reg.register(
        name="Dr. Elena Rodriguez",
        orcid="0000-0002-1234-5678",
        institution="UCSF",
        domain_expertise=["neuroscience", "biomarkers"],
        publication_count=87,
        h_index=23
    )
    
    res2 = reg.register(
        name="Prof. James Chen",
        orcid="0000-0002-8765-4321",
        institution="MIT",
        domain_expertise=["genomics", "neurodegeneration"],
        publication_count=156,
        h_index=34
    )
    
    print(f"\nRegistered researchers:")
    for r in reg.list():
        print(f"  {r['id']}: {r['name']} (rep: {r['reputation_score']})")
    
    # Record support
    reg.support_claim(res1, "CLAIM-000001", "Excellent evidence base")
    reg.replicate_claim(res2, "CLAIM-000001", "Confirmed in our cohort")
    
    print(f"\nAfter validations:")
    for r in reg.list():
        if r["id"] == res1:
            print(f"  {r['name']} now has reputation {r['reputation_score']}")
    
    # Consensus example (would need claim data)
    print("\n" + "=" * 70)
    print("Consensus Engine")
    print("=" * 70)
    print("  Strong Consensus (>90 trust, 50+ researchers, 20+ institutions)")
    print("  Moderate Consensus (>80 trust, 20+ researchers, 10+ institutions)")
    print("  Emerging Consensus (>70 trust, 5+ researchers)")
    print("  Preliminary Support (>50 trust)")
    print("  Unvalidated (<50 trust)")