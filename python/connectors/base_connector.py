"""
Scientific Connector Base - CoResearcher OS Sprint 21

Abstract base class for all scientific data source connectors.
Defines the universal interface: search, get, related, evidence.

This is domain-agnostic infrastructure. No medical/neurodiagnoses logic.
"""


from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Optional
from dataclasses import dataclass, field, asdict
from datetime import datetime


# ===================================================
# Security tier: PUBLIC — DO NOT MODIFY
# See python/_tiers.py for classification
# ===================================================
SECURITY_TIER = "PUBLIC"


# ===================================================
# Data Contracts
# ===================================================

@dataclass
class ConnectorResult:
    """Standard result envelope for all connector operations."""
    source: str
    operation: str
    query: Any
    total: int
    items: list[dict] = field(default_factory=list)
    error: Optional[str] = None
    retrieved_at: str = field(default_factory=lambda: datetime.now().isoformat())

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class EvidenceItem:
    """
    Standard evidence item returned by any connector.
    Normalises disparate API response shapes into a uniform structure.
    """
    id: str
    source: str
    title: str
    description: str
    url: str
    relevance_score: float = 0.0
    metadata: dict = field(default_factory=dict)

    def to_dict(self) -> dict:
        return asdict(self)


# ===================================================
# Abstract Base Connector
# ===================================================

class ScientificConnector(ABC):
    """
    Abstract base for all scientific data source connectors.

    Every connector implements:
        search(query, **filters) → list of results
        get(identifier)            → single detailed record
        related(identifier)        → related items
        evidence(claim_or_concept) → evidence items

    Subclasses inherit rate-limiting, caching, error handling,
    and provenance logging from this base class.
    """

    # Human-readable source name (overridden by subclasses)
    SOURCE_NAME: str = "unknown"

    def __init__(self, cache_ttl: int = 300, max_retries: int = 3):
        self.cache_ttl = cache_ttl
        self.max_retries = max_retries
        self._cache: dict[str, tuple[float, Any]] = {}
        self._provenance_log: list[dict] = []

    # -----------------------------------------------
    # Abstract methods – every connector must implement
    # -----------------------------------------------

    @abstractmethod
    def search(self, query: str, max_results: int = 20, **filters) -> ConnectorResult:
        """
        Search the data source for records matching *query*.

        Args:
            query: Free-text or structured search string.
            max_results: Maximum number of results to return.
            **filters: Source-specific filter parameters (e.g. status, year).

        Returns:
            ConnectorResult with matched items.
        """
        ...

    @abstractmethod
    def get(self, identifier: str) -> ConnectorResult:
        """
        Retrieve a single record by its native identifier.

        Args:
            identifier: Native ID from the source (e.g. NCT number, UniProt ID).

        Returns:
            ConnectorResult containing the single item.
        """
        ...

    @abstractmethod
    def related(self, identifier: str, max_results: int = 10) -> ConnectorResult:
        """
        Find records related to the given identifier.

        Args:
            identifier: Native ID to find related records for.
            max_results: Maximum number of related results.

        Returns:
            ConnectorResult with related items.
        """
        ...

    @abstractmethod
    def evidence(self, claim_or_concept: str, max_results: int = 20) -> ConnectorResult:
        """
        Retrieve evidence items supporting or refuting a claim/concept.

        Args:
            claim_or_concept: A scientific claim or concept string.
            max_results: Maximum number of evidence items.

        Returns:
            ConnectorResult with evidence items, each scored by relevance.
        """
        ...

    # -----------------------------------------------
    # Built-in helpers
    # -----------------------------------------------

    def _check_cache(self, key: str) -> Optional[Any]:
        """Return cached value if still fresh, else None."""
        import time
        now = time.time()
        entry = self._cache.get(key)
        if entry and (now - entry[0]) < self.cache_ttl:
            return entry[1]
        return None

    def _set_cache(self, key: str, value: Any):
        """Store value in cache with current timestamp."""
        import time
        self._cache[key] = (time.time(), value)

    def _log_provenance(self, operation: str, query: Any, result: ConnectorResult):
        """Record a provenance entry for this query."""
        self._provenance_log.append({
            "source": self.SOURCE_NAME,
            "operation": operation,
            "query": query,
            "total_results": result.total,
            "error": result.error,
            "timestamp": datetime.now().isoformat(),
        })

    def get_provenance_log(self) -> list[dict]:
        """Return all provenance entries for this connector instance."""
        return list(self._provenance_log)

    def clear_cache(self):
        """Clear the in-memory cache."""
        self._cache.clear()

    # -----------------------------------------------
    # Utility: standard error result
    # -----------------------------------------------

    def _error_result(self, operation: str, query: Any, error_msg: str) -> ConnectorResult:
        return ConnectorResult(
            source=self.SOURCE_NAME,
            operation=operation,
            query=query,
            total=0,
            error=error_msg,
        )

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__}[{self.SOURCE_NAME}]>"