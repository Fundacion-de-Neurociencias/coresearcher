"""
tests/test_api_endpoints.py - Pytest suite for CoResearcher FastAPI REST API (api/server.py).
"""

import tempfile
from pathlib import Path

import pytest
from fastapi.testclient import TestClient


@pytest.mark.api
@pytest.mark.fast
def test_physics_megarepo_audit_endpoint(api_client: TestClient):
    """Tests POST /api/discovery/physics/audit-megarepo with synthetic physical corpus files."""
    with tempfile.TemporaryDirectory() as tmpdir:
        root = Path(tmpdir)
        (root / "ch01_qft.md").write_text("Gauge invariance in non-abelian SU(N) Yang-Mills theory.", encoding="utf-8")
        (root / "proof_sobolev.tex").write_text("Theorem: Sobolev embedding W^{1,p} inside L^{p^*}.", encoding="utf-8")
        (root / "dataset_planck.csv").write_text("multipole_l,cl_temperature,error\n100,5600.2,4.5\n", encoding="utf-8")

        response = api_client.post(
            "/api/discovery/physics/audit-megarepo",
            json={"repo_path": str(root)},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["total_items_scanned"] == 3
        assert "overall_editorial_judgment" in data
        assert data["som_corpus_dossier_hash"].startswith("sha256:")
        assert len(data["item_verdicts"]) == 3


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
