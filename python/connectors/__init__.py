"""
Scientific Connector Layer - CoResearcher OS Sprint 21

Unified access layer for scientific data sources.
Domain-agnostic infrastructure for querying external scientific APIs.

Connectors:
- ClinicalTrials.gov: Clinical trial registry and results database
- Open Targets: Target-disease association platform
- ChEMBL: Bioactive molecule database with drug-like properties
- UniProt: Universal protein knowledgebase
"""

from .base_connector import ScientificConnector
from .connector_registry import ConnectorRegistry
from .clinicaltrials_connector import ClinicalTrialsConnector
from .opentargets_connector import OpenTargetsConnector
from .chembl_connector import ChEMBLConnector
from .uniprot_connector import UniProtConnector

# Security tier: PUBLIC — DO NOT MODIFY
# See python/_tiers.py for classification
SECURITY_TIER = "PUBLIC"


__all__ = [
    "ScientificConnector",
    "ConnectorRegistry",
    "ClinicalTrialsConnector",
    "OpenTargetsConnector",
    "ChEMBLConnector",
    "UniProtConnector",
]