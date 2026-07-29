"""
CoResearcher Security Tier Classification
===========================================

Central definition for the Open Core + Scientific Network Moat strategy.

Each module in the codebase must have a SECURITY_TIER constant.
The audit script (scripts/audit_tiers.py) enforces this and prevents
PRIVATE code from appearing in public repositories.

Tiers:
------
PUBLIC    (Tier 1) — Public Infrastructure (Open Source)
COMMUNITY (Tier 2) — Community Layer (Open / Free SaaS)
PRIVATE   (Tier 3) — Strategic Moat (Never public)

See docs/private/MOAT_STRATEGY.md for the full strategy.
"""

from enum import Enum


class SecurityTier(str, Enum):
    """Security tiers for CoResearcher modules."""
    PUBLIC = "PUBLIC"
    COMMUNITY = "COMMUNITY"
    PRIVATE = "PRIVATE"


# List of all modules with their tier classification.
# This is the single source of truth for the audit system.
MODULE_TIERS: dict[str, str] = {
    # =========================================================================
    # PUBLIC (Tier 1) — Public Infrastructure
    # Connectors, Scientific Core, Ontology, SDK, MCP, Schemas, API contracts
    # =========================================================================
    "python.connectors": "PUBLIC",
    "python.connectors.base_connector": "PUBLIC",
    "python.connectors.pubmed_agent": "PUBLIC",
    "python.connectors.openalex_agent": "PUBLIC",
    "python.connectors.crossref_agent": "PUBLIC",
    "python.connectors.clinicaltrials_connector": "PUBLIC",
    "python.connectors.chembl_connector": "PUBLIC",
    "python.connectors.uniprot_connector": "PUBLIC",
    "python.connectors.opentargets_connector": "PUBLIC",
    "python.connectors.connector_registry": "PUBLIC",
    "python.connectors.test_all": "PUBLIC",
    "python.knowledge.ontology": "PUBLIC",
    "python.knowledge.contracts": "PUBLIC",
    "python.knowledge.question_registry": "PUBLIC",
    "python.ecosystem.capability_registry": "PUBLIC",
    "python.ecosystem.domain_pack_registry": "PUBLIC",
    "python.ecosystem.dependency_engine": "PUBLIC",
    "python.ecosystem.project_container": "PUBLIC",
    "python.agents.neo4j_client": "PUBLIC",
    "python.agents.router.agent_router": "PUBLIC",

    # =========================================================================
    # COMMUNITY (Tier 2) — Community Layer
    # Visible, usable, drives adoption
    # =========================================================================
    "python.knowledge.claim_registry": "COMMUNITY",
    "python.knowledge.researcher_registry": "COMMUNITY",
    "python.knowledge.finding_registry": "COMMUNITY",
    "python.knowledge.interop_layer": "COMMUNITY",
    "python.knowledge.translation_layer": "COMMUNITY",
    "python.knowledge.api": "COMMUNITY",
    "python.knowledge.anomaly_registry": "COMMUNITY",
    "python.knowledge.failed_prediction_registry": "COMMUNITY",
    "python.knowledge.__init__": "COMMUNITY",
    "python.ecosystem.provenance_dashboard": "COMMUNITY",
    "python.ecosystem.__init__": "COMMUNITY",
    "python.agents.research_memory": "COMMUNITY",
    "python.agents.ingestion_pipeline": "COMMUNITY",
    "python.agents.__init__": "COMMUNITY",
    "python.agents.genomics_pack": "COMMUNITY",
    "python.agents.pubmed_agent": "COMMUNITY",
    "python.agents.openalex_agent": "COMMUNITY",
    "python.agents.crossref_agent": "COMMUNITY",
    "python.workflows.demo": "COMMUNITY",
    "python.workflows.sprint6_demo": "COMMUNITY",
    "python.workflows.research_scout": "COMMUNITY",
    "python.workflows.scientific_session": "COMMUNITY",
    "python.workflows.__init__": "COMMUNITY",

    # =========================================================================
    # PRIVATE (Tier 3) — Strategic Moat
    # Never public. Core engines that transform data into discovery.
    # =========================================================================
    "python.discovery": "PRIVATE",
    "python.discovery.einstein_generator": "PRIVATE",
    "python.discovery.anomaly_detector": "PRIVATE",
    "python.discovery.boundary_explorer": "PRIVATE",
    "python.discovery.missing_link_explorer": "PRIVATE",
    "python.discovery.cross_domain_transfer": "PRIVATE",
    "python.discovery.thought_experiment_generator": "PRIVATE",
    "python.discovery.__init__": "PRIVATE",
    "python.knowledge.trust_framework": "PRIVATE",
    "python.knowledge.evidence_combiner": "PRIVATE",
    "python.knowledge.contradiction_registry": "PRIVATE",
    "python.evaluation.novelty_audit": "PRIVATE",
    "python.agents.reasoning_engine": "PRIVATE",
    "python.agents.claim_extractor": "PRIVATE",
    "python.agents.claim_graph_builder": "PRIVATE",
    "python.workflows.hypothesis_discovery": "PRIVATE",
    "python.workflows.grant_writer": "PRIVATE",
    "python.workflows.vertical_slice_001": "PRIVATE",
    "scripts.atlas_extractor": "PRIVATE",
}


def get_tier(module_path: str) -> str:
    """Get the security tier for a module path."""
    # Exact match first
    if module_path in MODULE_TIERS:
        return MODULE_TIERS[module_path]
    # Package prefix match
    for key, tier in MODULE_TIERS.items():
        if module_path.startswith(key + "."):
            return tier
    return "UNCLASSIFIED"


def is_private(module_path: str) -> bool:
    """Check if a module is PRIVATE."""
    return get_tier(module_path) == "PRIVATE"


def is_public(module_path: str) -> bool:
    """Check if a module is PUBLIC."""
    return get_tier(module_path) == "PUBLIC"


def is_community(module_path: str) -> bool:
    """Check if a module is COMMUNITY."""
    return get_tier(module_path) == "COMMUNITY"