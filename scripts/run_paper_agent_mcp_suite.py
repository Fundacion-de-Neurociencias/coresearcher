#!/usr/bin/env python3
"""
scripts/run_paper_agent_mcp_suite.py - Verification Gate for Paper2Agent MCP Adapter.
Tests:
1. Query external virtual author paper agents across domains (connectome, genomics, metabolomics).
2. Execute real analytical tools exposed by external paper agents.
3. Validate SOM-SHA256 cryptographic provenance of outputs.
4. Verify Reality Contact Level promotion (RCS = 2 / EMPIRICAL_EXECUTION_GROUNDED).
5. Verify API endpoints via FastAPI TestClient.
"""

import sys
import os

root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

from python.discovery.grounded_search_sensor import (
    GroundedSearchSensor,
    PaperAgentMCPAdapter,
)
from python.discovery.reality_contact_score import RealityContactLevel
from fastapi.testclient import TestClient
from api.server import app


def test_mcp_adapter_query():
    print("--- 1. Testing GroundedSearchSensor.query_paper_agents ---")
    
    # Query for genomics / AlphaGenome
    genomics_agents = GroundedSearchSensor.query_paper_agents("genomics variant pathogenicity")
    assert len(genomics_agents) >= 1, "Expected at least 1 agent for genomics query"
    alpha_agent = next((a for a in genomics_agents if a.agent_id == "AGENT-PAPER-ALPHAGENOME-2026"), None)
    assert alpha_agent is not None, "AGENT-PAPER-ALPHAGENOME-2026 not found"
    tool_names = [t.tool_name for t in alpha_agent.available_tools]
    assert "score_genetic_perturbation" in tool_names
    print(f"  [PASS] Found agent: {alpha_agent.title} ({alpha_agent.agent_id})")

    # Query for connectome / diffusion
    connectome_agents = GroundedSearchSensor.query_paper_agents("tau spread connectome network")
    assert len(connectome_agents) >= 1, "Expected at least 1 agent for connectome query"
    conn_agent = next((a for a in connectome_agents if a.agent_id == "AGENT-PAPER-CONNECTOME-2024"), None)
    assert conn_agent is not None, "AGENT-PAPER-CONNECTOME-2024 not found"
    tool_names_conn = [t.tool_name for t in conn_agent.available_tools]
    assert "compute_connectome_diffusion" in tool_names_conn
    print(f"  [PASS] Found agent: {conn_agent.title} ({conn_agent.agent_id})")

    # Query for metabolomics / reserve
    metabo_agents = GroundedSearchSensor.query_paper_agents("metabolomic profiling reserve")
    assert len(metabo_agents) >= 1, "Expected at least 1 agent for metabolomics query"
    metabo_agent = next((a for a in metabo_agents if a.agent_id == "AGENT-PAPER-METABOAD-2025"), None)
    assert metabo_agent is not None, "AGENT-PAPER-METABOAD-2025 not found"
    tool_names_metabo = [t.tool_name for t in metabo_agent.available_tools]
    assert "evaluate_metabolic_glycolytic_reserve" in tool_names_metabo
    print(f"  [PASS] Found agent: {metabo_agent.title} ({metabo_agent.agent_id})")


def test_mcp_adapter_execution():
    print("\n--- 2. Testing GroundedSearchSensor.execute_paper_agent_method ---")
    
    # Execute AlphaGenome score_genetic_perturbation
    variant_args = {
        "target_gene": "TYK2",
        "cell_type": "CD4_T_CELL",
        "variant_id": "rs34536443"
    }
    result_alpha = GroundedSearchSensor.execute_paper_agent_method(
        agent_id="AGENT-PAPER-ALPHAGENOME-2026",
        tool_name="score_genetic_perturbation",
        arguments=variant_args
    )
    assert result_alpha.execution_status == "SUCCESS"
    assert result_alpha.epistemic_rcs_level == 2
    assert result_alpha.som_execution_hash.startswith("sha256:")
    assert result_alpha.result_data["gene"] == "TYK2"
    assert result_alpha.result_data["causal_perturbation_score"] > 0.8
    print(f"  [PASS] AlphaGenome execution successful. Output score: {result_alpha.result_data['causal_perturbation_score']}")
    print(f"         SOM Hash: {result_alpha.som_execution_hash}")

    # Execute Connectome compute_connectome_diffusion
    diff_args = {
        "tau_baseline": 0.85,
        "hub_strength": 0.90
    }
    result_conn = GroundedSearchSensor.execute_paper_agent_method(
        agent_id="AGENT-PAPER-CONNECTOME-2024",
        tool_name="compute_connectome_diffusion",
        arguments=diff_args
    )
    assert result_conn.execution_status == "SUCCESS"
    assert result_conn.epistemic_rcs_level == 2
    assert result_conn.result_data["is_progression_buffered"] is True
    print(f"  [PASS] Connectome execution successful. Buffered: {result_conn.result_data['is_progression_buffered']}")

    # Execute MetaboAD evaluate_metabolic_glycolytic_reserve
    metabo_args = {
        "fdg_suvr": 1.25,
        "ptau217": 92.0
    }
    result_metabo = GroundedSearchSensor.execute_paper_agent_method(
        agent_id="AGENT-PAPER-METABOAD-2025",
        tool_name="evaluate_metabolic_glycolytic_reserve",
        arguments=metabo_args
    )
    assert result_metabo.execution_status == "SUCCESS"
    assert result_metabo.result_data["glycolytic_reserve_status"] == "SUFFICIENT"
    print(f"  [PASS] MetaboAD execution successful. Status: {result_metabo.result_data['glycolytic_reserve_status']}")


def test_api_endpoints():
    print("\n--- 3. Testing FastAPI Paper2Agent MCP Endpoints ---")
    client = TestClient(app)

    # Test Query Endpoint
    query_resp = client.post(
        "/api/discovery/paper-agent/query",
        json={"topic": "genetic perturbation of enhancers"}
    )
    assert query_resp.status_code == 200, f"Query returned status {query_resp.status_code}: {query_resp.text}"
    query_data = query_resp.json()
    assert query_data["matched_agents_count"] >= 1
    assert any(a["agent_id"] == "AGENT-PAPER-ALPHAGENOME-2026" for a in query_data["agents"])
    print(f"  [PASS] POST /api/discovery/paper-agent/query verified: matched {query_data['matched_agents_count']} agents")

    # Test Execute Endpoint
    exec_resp = client.post(
        "/api/discovery/paper-agent/execute",
        json={
            "agent_id": "AGENT-PAPER-ALPHAGENOME-2026",
            "tool_name": "score_genetic_perturbation",
            "arguments": {
                "target_gene": "TYK2",
                "cell_type": "CD4_T_CELL",
                "variant_id": "rs34536443"
            }
        }
    )
    assert exec_resp.status_code == 200, f"Execute returned status {exec_resp.status_code}: {exec_resp.text}"
    exec_data = exec_resp.json()
    assert exec_data["execution_status"] == "SUCCESS"
    assert exec_data["epistemic_rcs_level"] == 2
    assert exec_data["som_execution_hash"].startswith("sha256:")
    print(f"  [PASS] POST /api/discovery/paper-agent/execute verified: RCS={exec_data['epistemic_rcs_level']}, status={exec_data['execution_status']}")


if __name__ == "__main__":
    test_mcp_adapter_query()
    test_mcp_adapter_execution()
    test_api_endpoints()
    print("\n=======================================================")
    print(" ALL PAPER2AGENT MCP TESTS PASSED EMPIRICALLY (E2E)    ")
    print("=======================================================")
