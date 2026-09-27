"""
tests/conftest.py - Pytest shared fixtures and configuration for CoResearcher.
"""

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from fastapi.testclient import TestClient

from api.server import app
from python.discovery.epistemic_stigmergy import EpistemicPheromoneField, RealityContactFirewall
from python.discovery.physical_theorem_court import PhysicalCoherenceCourt
from python.discovery.physics_corpus_auditor import PhysicsCorpusAuditor


@pytest.fixture(scope="session")
def api_client() -> TestClient:
    """Provides a shared FastAPI TestClient instance."""
    return TestClient(app)


@pytest.fixture(scope="function")
def physics_auditor() -> PhysicsCorpusAuditor:
    """Provides a freshly instantiated PhysicsCorpusAuditor."""
    return PhysicsCorpusAuditor()


@pytest.fixture(scope="function")
def physical_court() -> PhysicalCoherenceCourt:
    """Provides a PhysicalCoherenceCourt instance for proof auditing."""
    return PhysicalCoherenceCourt()


@pytest.fixture(scope="function")
def pheromone_field() -> EpistemicPheromoneField:
    """Provides an EpistemicPheromoneField instance."""
    return EpistemicPheromoneField()


@pytest.fixture(scope="function")
def reality_firewall() -> RealityContactFirewall:
    """Provides a RealityContactFirewall instance."""
    return RealityContactFirewall()
