"""
Knowledge Contracts - Sprint 16
Formal architectural contracts for the Scientific Knowledge Utility.
"""

from __future__ import annotations

from typing import List, Dict, Optional
from enum import Enum
from pathlib import Path
import json

# Security tier: PUBLIC — DO NOT MODIFY
# See python/_tiers.py for classification
SECURITY_TIER = "PUBLIC"


CONTRACTS_DIR = Path("knowledge/contracts")
CONTRACTS_DIR.mkdir(parents=True, exist_ok=True)


# =============================================================================
# Knowledge Producer Contract
# =============================================================================

class KnowledgeProducerContract:
    """
    Contract for components that PRODUCE scientific knowledge.
    
    Producers have authority to generate:
    - CLAIM-XXXXXX
    - EVIDENCE-XXXXXX
    - FINDING-XXXXXX
    - CONCEPT-XXXXXX
    """
    
    AUTHORIZED_TYPES = ["CLAIM", "EVIDENCE", "FINDING", "CONCEPT"]
    
    def __init__(self, producer_id: str, name: str):
        self.producer_id = producer_id
        self.name = name
        self.authorized_types = self.AUTHORIZED_TYPES.copy()
    
    def can_produce(self, knowledge_type: str) -> bool:
        return knowledge_type.upper() in self.authorized_types
    
    def produce(self, knowledge_type: str, data: dict) -> Optional[str]:
        """Produce a knowledge artifact."""
        if not self.can_produce(knowledge_type):
            raise ValueError(f"{self.name} cannot produce {knowledge_type}")
        return f"{knowledge_type.upper()}-{self.producer_id}"


# =============================================================================
# Knowledge Consumer Contract
# =============================================================================

class KnowledgeConsumerContract:
    """
    Contract for components that CONSUME scientific knowledge.
    
    defines requirements for knowledge consumption:
    - domain
    - entity types
    - predicates
    - trust thresholds
    """
    
    def __init__(self, 
                 consumer_id: str,
                 domain: str,
                 entities: List[str] = None,
                 predicates: List[str] = None,
                 trust_threshold: int = 50,
                 accepted_formats: List[str] = None):
        self.consumer_id = consumer_id
        self.domain = domain
        self.entities = entities or []
        self.predicates = predicates or []
        self.trust_threshold = trust_threshold
        self.accepted_formats = accepted_formats or ["json", "rdf"]
        
        # Save contract
        self._save_contract()
    
    def _save_contract(self):
        """Save consumer contract to disk."""
        contract_file = CONTRACTS_DIR / f"{self.consumer_id}_consumer.json"
        contract_data = {
            "consumer_id": self.consumer_id,
            "domain": self.domain,
            "entities": self.entities,
            "predicates": self.predicates,
            "trust_threshold": self.trust_threshold,
            "accepted_formats": self.accepted_formats,
        }
        with open(contract_file, 'w') as f:
            json.dump(contract_data, f, indent=2)
    
    def can_consume(self, finding: dict) -> bool:
        """Check if consumer can accept this finding."""
        # Check trust
        trust = finding.get("trust", 0)
        if trust < self.trust_threshold:
            return False
        
        # Check entity alignment (optional filter)
        if self.entities:
            subject = finding.get("subject", "").lower()
            if subject not in [e.lower() for e in self.entities]:
                return False
        
        # Check predicate (optional filter)
        if self.predicates:
            predicate = finding.get("predicate", "").lower()
            if predicate not in [p.lower() for p in self.predicates]:
                return False
        
        return True


# =============================================================================
# Knowledge Exchange Format
# =============================================================================

class KnowledgeExchangeFormat:
    """
    Universal exchange format for scientific knowledge.
    
    Standard format that all consumers understand:
    {
      "finding_id": "FIND-001234",
      "subject": "pTau217",
      "predicate": "predicts",
      "object": "amyloid positivity",
      "trust": 94,
      "consensus": "Moderate",
      "population": "preclinical AD",
      "effect_size": 0.78,
      "p_value": 0.001,
      "provenance": [...]
    }
    """
    
    @staticmethod
    def from_finding(finding: dict, trust_report: dict = None, consensus: str = None) -> dict:
        """Convert a finding to exchange format."""
        return {
            "finding_id": finding.get("id"),
            "subject": finding.get("subject"),
            "predicate": finding.get("predicate"),
            "object": finding.get("object"),
            "trust": trust_report.get("trust_index", 0) if trust_report else finding.get("quality_score", 0) * 100,
            "consensus": consensus or "Unvalidated",
            "population": finding.get("population"),
            "effect_size": finding.get("effect_size"),
            "p_value": finding.get("p_value"),
            "provenance": finding.get("derivedFrom", []),
        }
    
    @staticmethod
    def from_claim(claim: dict, trust_report: dict = None, consensus: str = None) -> dict:
        """Convert a claim to exchange format."""
        return {
            "claim_id": claim.get("id"),
            "subject": claim.get("entities", ["unknown"])[0] if claim.get("entities") else "unknown",
            "statement": claim.get("text"),
            "trust": trust_report.get("trust_index", 0) if trust_report else claim.get("evidenceScore", 0) * 100,
            "consensus": consensus or "Unvalidated",
            "domain": claim.get("domain"),
            "provenance": claim.get("supportingPapers", []),
        }


# =============================================================================
# Pre-defined Consumer Contracts
# =============================================================================

NEURODIAGNOSES_CONSUMER = KnowledgeConsumerContract(
    consumer_id="neurodiagnoses",
    domain="neurodegeneration",
    entities=["ptau217", "ptau181", "nfl", "csf", "amyloid", "tau", "apoe"],
    trust_threshold=75,
)

MEDICALIA_CONSUMER = KnowledgeConsumerContract(
    consumer_id="medicalia",
    domain="clinical-practice",
    entities=["disease", "intervention", "outcome"],
    trust_threshold=90,
)

GENEFORGE_CONSUMER = KnowledgeConsumerContract(
    consumer_id="geneforge",
    domain="genomics",
    entities=["gene", "variant", "pathway"],
    trust_threshold=70,
)

VADEMECUM_CONSUMER = KnowledgeConsumerContract(
    consumer_id="vademecum",
    domain="drug-reference",
    entities=["drug", "target", "indication"],
    trust_threshold=80,
)


# =============================================================================
# DSL Registry for Consumers
# =============================================================================

class DSLRegistry:
    """
    Registry of all domain-specific consumers.
    
    Maps domains to their consumers.
    """
    
    _consumers: Dict[str, KnowledgeConsumerContract] = {
        "neurodiagnoses": NEURODIAGNOSES_CONSUMER,
        "medicalia": MEDICALIA_CONSUMER,
        "geneforge": GENEFORGE_CONSUMER,
        "vademecum": VADEMECUM_CONSUMER,
    }
    
    @classmethod
    def get_consumer(cls, domain: str) -> Optional[KnowledgeConsumerContract]:
        """Get consumer by domain."""
        return cls._consumers.get(domain)
    
    @classmethod
    def register_consumer(cls, consumer: KnowledgeConsumerContract):
        """Register a new consumer."""
        cls._consumers[consumer.consumer_id] = consumer
    
    @classmethod
    def list_consumers(cls) -> List[str]:
        """List all registered consumers."""
        return list(cls._consumers.keys())


# =============================================================================
# CLI
# =============================================================================

if __name__ == "__main__":
    print("=" * 70)
    print("Knowledge Contracts - Sprint 16")
    print("=" * 70)
    
    print("\nDeclared Consumers:")
    for domain, consumer in DSLRegistry._consumers.items():
        print(f"\n  {domain}:")
        print(f"    Domain: {consumer.domain}")
        print(f"    Trust Threshold: {consumer.trust_threshold}")
        print(f"    Entities: {consumer.entities[:3] if consumer.entities else 'any'}...")
    
    print("\n" + "=" * 70)
    print("Knowledge Exchange Format")
    print("=" * 70)
    
    sample_finding = {
        "id": "FIND-000001",
        "subject": "ptau217",
        "predicate": "predicts",
        "object": "amyloid_positivity",
        "population": "preclinical_ad",
        "effect_size": 0.78,
        "p_value": 0.001,
    }
    
    exchange = KnowledgeExchangeFormat.from_finding(sample_finding)
    print(f"\nSample Exchange Format:")
    print(json.dumps(exchange, indent=2))