"""
tests/test_api_endpoints.py - Pytest suite for CoResearcher FastAPI REST API (api/server.py).
"""

import pytest
from fastapi.testclient import TestClient


@pytest.mark.api
@pytest.mark.fast
def test_epistemic_stigmergy_endpoints(api_client: TestClient):
    """Tests POST /api/discovery/stigmergy/query-pheromone-field and /audit-reality-firewall."""
    # Query pheromone field
    res_field = api_client.post(
        "/api/discovery/stigmergy/query-pheromone-field",
        json={"research_topic": "Condensed Matter Invariants"},
    )
    assert res_field.status_code == 200
    field_data = res_field.json()
    assert "som_landscape_hash" in field_data
    assert "recommended_swarm_role" in field_data

    # Audit reality firewall
    res_firewall = api_client.post(
        "/api/discovery/stigmergy/audit-reality-firewall",
        json={
            "hypothesis_id": "CAND-001",
            "claimed_regularity": "Planck constant invariance h = 6.62607015e-34 J*s",
            "rcs_level": 2,
            "empirical_anchors": ["NIST Reference on Constants, Units, and Uncertainty"],
        },
    )
    assert res_firewall.status_code == 200
    fw_data = res_firewall.json()
    assert fw_data["is_firewall_passed"] is True
