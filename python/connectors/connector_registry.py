"""
Connector Registry - CoResearcher OS Sprint 21

Central registry for all scientific data source connectors.
Provides unified access to registered connectors and multi-source queries.

Domain-agnostic infrastructure. No medical/neurodiagnoses logic.
"""

from __future__ import annotations

import json
from typing import Any, Optional
from datetime import datetime
from pathlib import Path

from .base_connector import ScientificConnector, ConnectorResult


# Registry storage
REGISTRY_DIR = Path("ecosystem/registry")
REGISTRY_DIR.mkdir(parents=True, exist_ok=True)
CONNECTORS_FILE = REGISTRY_DIR / "connectors.json"


class ConnectorRegistry:
    """
    Central registry for scientific connectors.

    Manages:
    - Registration of connector instances
    - Multi-source search across all connectors
    - Connector lifecycle (register, unregister, list)
    - Provenance tracking for all queries
    """

    def __init__(self):
        self._connectors: dict[str, ScientificConnector] = {}
        self._metadata: dict = self._load()
        self._query_log: list[dict] = []

    # ------------------------------------------------------------------
    # Persistence
    # ------------------------------------------------------------------

    def _load(self) -> dict:
        """Load registry metadata from disk."""
        if CONNECTORS_FILE.exists():
            with open(CONNECTORS_FILE, 'r') as f:
                return json.load(f)
        return {"registrations": {}, "next_id": 1}

    def _save(self):
        """Save registry metadata to disk."""
        with open(CONNECTORS_FILE, 'w') as f:
            json.dump(self._metadata, f, indent=2)

    # ------------------------------------------------------------------
    # Registration
    # ------------------------------------------------------------------

    def register(self, connector: ScientificConnector, config: dict = None) -> str:
        """
        Register a connector instance.

        Args:
            connector: A ScientificConnector instance.
            config: Optional configuration (e.g. rate limits, API keys).

        Returns:
            Registration ID.
        """
        source_name = connector.SOURCE_NAME
        reg_id = f"conn_{self._metadata['next_id']}"

        registration = {
            "id": reg_id,
            "source": source_name,
            "class": connector.__class__.__name__,
            "config": config or {},
            "registered_at": datetime.now().isoformat(),
        }

        self._connectors[source_name] = connector
        self._metadata["registrations"][reg_id] = registration
        self._metadata["next_id"] += 1
        self._save()

        return reg_id

    def unregister(self, source_name: str) -> bool:
        """Unregister a connector by source name."""
        if source_name in self._connectors:
            del self._connectors[source_name]
            # Remove from metadata
            for reg_id, reg in list(self._metadata["registrations"].items()):
                if reg["source"] == source_name:
                    del self._metadata["registrations"][reg_id]
            self._save()
            return True
        return False

    # ------------------------------------------------------------------
    # Access
    # ------------------------------------------------------------------

    def get(self, source_name: str) -> Optional[ScientificConnector]:
        """Get a connector by source name."""
        return self._connectors.get(source_name)

    def list_sources(self) -> list[str]:
        """List all registered connector source names."""
        return list(self._connectors.keys())

    def list_registrations(self) -> list[dict]:
        """List all registration metadata."""
        return list(self._metadata["registrations"].values())

    # ------------------------------------------------------------------
    # Multi-source queries
    # ------------------------------------------------------------------

    def search_all(self, query: str, max_results_per_source: int = 10,
                   sources: list[str] = None) -> dict[str, ConnectorResult]:
        """
        Search across all (or specified) connectors.

        Args:
            query: Search query string.
            max_results_per_source: Max results per connector.
            sources: Optional list of source names to restrict search to.

        Returns:
            Dict mapping source name → ConnectorResult.
        """
        targets = sources or self.list_sources()
        results = {}

        for source_name in targets:
            connector = self._connectors.get(source_name)
            if connector:
                try:
                    results[source_name] = connector.search(query, max_results_per_source)
                except Exception as e:
                    results[source_name] = connector._error_result("search", query, str(e))

        self._query_log.append({
            "type": "search_all",
            "query": query,
            "sources": targets,
            "timestamp": datetime.now().isoformat(),
        })

        return results

    def evidence_all(self, claim_or_concept: str, max_results_per_source: int = 10,
                     sources: list[str] = None) -> dict[str, ConnectorResult]:
        """
        Gather evidence across all (or specified) connectors.

        Args:
            claim_or_concept: Claim or concept to find evidence for.
            max_results_per_source: Max evidence items per connector.
            sources: Optional list of source names to restrict to.

        Returns:
            Dict mapping source name → ConnectorResult with evidence items.
        """
        targets = sources or self.list_sources()
        results = {}

        for source_name in targets:
            connector = self._connectors.get(source_name)
            if connector:
                try:
                    results[source_name] = connector.evidence(claim_or_concept, max_results_per_source)
                except Exception as e:
                    results[source_name] = connector._error_result("evidence", claim_or_concept, str(e))

        self._query_log.append({
            "type": "evidence_all",
            "query": claim_or_concept,
            "sources": targets,
            "timestamp": datetime.now().isoformat(),
        })

        return results

    def get_provenance_log(self) -> list[dict]:
        """Return the aggregated query log."""
        return list(self._query_log)

    def get_connector_provenance(self, source_name: str) -> list[dict]:
        """Return provenance log for a specific connector."""
        connector = self._connectors.get(source_name)
        if connector:
            return connector.get_provenance_log()
        return []

    def clear_all_caches(self):
        """Clear caches on all registered connectors."""
        for connector in self._connectors.values():
            connector.clear_cache()

    def __repr__(self) -> str:
        return f"<ConnectorRegistry sources={list(self._connectors.keys())}>"


# =============================================================================
# CLI Test
# =============================================================================

if __name__ == "__main__":
    print("=" * 70)
    print("Connector Registry - Sprint 21")
    print("=" * 70)

    from .clinicaltrials_connector import ClinicalTrialsConnector
    from .opentargets_connector import OpenTargetsConnector
    from .chembl_connector import ChEMBLConnector
    from .uniprot_connector import UniProtConnector

# Security tier: PUBLIC — DO NOT MODIFY
# See python/_tiers.py for classification
SECURITY_TIER = "PUBLIC"


    registry = ConnectorRegistry()

    # Register all connectors
    registry.register(ClinicalTrialsConnector())
    registry.register(OpenTargetsConnector())
    registry.register(ChEMBLConnector())
    registry.register(UniProtConnector())

    print(f"\nRegistered sources: {registry.list_sources()}")

    # Test multi-source search
    print("\n" + "=" * 70)
    print("Multi-source search: 'Alzheimer'")
    print("=" * 70)

    results = registry.search_all("Alzheimer", max_results_per_source=3)
    for source, result in results.items():
        print(f"\n  {source}: {result.total} results")
        for item in result.items[:2]:
            print(f"    - {item.get('title', '')[:60]}")

    # Test multi-source evidence
    print("\n" + "=" * 70)
    print("Multi-source evidence: 'Amyloid beta'")
    print("=" * 70)

    evidence = registry.evidence_all("Amyloid beta", max_results_per_source=3)
    for source, result in evidence.items():
        print(f"\n  {source}: {result.total} evidence items")
        for item in result.items[:2]:
            print(f"    - {item.get('title', '')[:60]}")

    # Test provenance
    print("\n" + "=" * 70)
    print("Registry Query Log:")
    print("=" * 70)
    for entry in registry.get_provenance_log():
        print(f"  {entry['type']}: '{entry['query']}' → {entry['sources']}")

    print("\nDone.")