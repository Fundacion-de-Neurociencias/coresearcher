"""
tests/conftest.py - Pytest shared fixtures and configuration for CoResearcher.
"""

import os
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent

# The API rate limiter is exercised explicitly in test_api_security.py; the rest of
# the suite issues many requests from one client, so the limit is raised here.
os.environ.setdefault("CORESEARCHER_RATE_LIMIT_PER_MINUTE", "100000")
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from fastapi.testclient import TestClient

from api.server import app
from api.testing import authenticated_client
from python.discovery.epistemic_stigmergy import EpistemicPheromoneField, RealityContactFirewall
from python.discovery.physical_theorem_court import PhysicalCoherenceCourt


@pytest.fixture(scope="session")
def api_client() -> TestClient:
    """Provides a shared FastAPI TestClient instance."""
    return authenticated_client(app)


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
