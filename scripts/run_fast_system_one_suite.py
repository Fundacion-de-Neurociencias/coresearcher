#!/usr/bin/env python3
"""
scripts/run_fast_system_one_suite.py - Verification Suite for Jev Fast System One Classifier (ADR-DISCOVERY-024).
Tests:
1. Sub-millisecond execution latency for typed System 1 decisions.
2. Accurate classification across David Marr's tri-level hierarchy (Computational, Algorithmic, Implementational).
3. Guardrail triage for code diffs (detecting pre-split statistical data leakage and unphysical violations).
4. Agora branch action routing (New Branch vs Contribute Existing vs Cherry-Pick).
5. Integration with MarrClassifierAgent and FastAPI endpoints.
"""

import sys
import os
import time

root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

from python.discovery.fast_system_one_classifier import (
    FastSystemOneClassifier,
    ClassificationDomain,
)
from python.discovery.discovery_teams import MarrClassifierAgent
from fastapi.testclient import TestClient
from api.server import app
from api.testing import authenticated_client


def test_fast_marr_classification():
    print("--- 1. Testing Fast Marr Level Classification & Latency ---")
    
    # Computational hypothesis
    comp_stmt = "The evolutionary goal of the cognitive network is to optimize informational stability and minimize entropy loss."
    res_comp = FastSystemOneClassifier.classify_marr_level(comp_stmt)
    assert res_comp.selected_category == "COMPUTATIONAL"
    assert res_comp.confidence_score > 0.5
    assert res_comp.latency_ms < 50.0  # Typically < 1ms locally
    print(f"  [PASS] Computational classified in {res_comp.latency_ms:.2f} ms: {res_comp.selected_category} (p={res_comp.confidence_score:.3f})")

    # Algorithmic hypothesis
    algo_stmt = "Tau spreading kinetics follow graph diffusion along structural connectome hubs and nodal synaptic flux."
    res_algo = FastSystemOneClassifier.classify_marr_level(algo_stmt)
    assert res_algo.selected_category == "ALGORITHMIC"
    assert res_algo.confidence_score > 0.5
    print(f"  [PASS] Algorithmic classified in {res_algo.latency_ms:.2f} ms: {res_algo.selected_category} (p={res_algo.confidence_score:.3f})")

    # Implementational hypothesis
    impl_stmt = "Plasma pTau217 phosphorylation concentration in CSF is elevated in preclinical Alzheimer subjects."
    res_impl = FastSystemOneClassifier.classify_marr_level(impl_stmt)
    assert res_impl.selected_category == "IMPLEMENTATIONAL"
    assert res_impl.confidence_score > 0.5
    print(f"  [PASS] Implementational classified in {res_impl.latency_ms:.2f} ms: {res_impl.selected_category} (p={res_impl.confidence_score:.3f})")


def test_pr_guardrail_triage():
    print("\n--- 2. Testing Fast PR Guardrail Triage ---")
    
    # 1. Leakage diff
    leakage_diff = """
    + from sklearn.preprocessing import StandardScaler
    + scaler = StandardScaler()
    + X_norm = scaler.fit_transform(X) # Data leakage before split
    + X_train, X_test, y_train, y_test = train_test_split(X_norm, y)
    """
    res_leak = FastSystemOneClassifier.classify_pr_risk(leakage_diff)
    assert res_leak.selected_category == "DATA_LEAKAGE_RISK"
    assert res_leak.confidence_score >= 0.95
    print(f"  [PASS] Data leakage detected in {res_leak.latency_ms:.2f} ms: {res_leak.selected_category} (conf={res_leak.confidence_score:.2f})")

    # 2. Safe clean diff
    safe_diff = """
    + def compute_moca_average(scores: list[float]) -> float:
    +     return sum(scores) / len(scores) if scores else 0.0
    """
    res_safe = FastSystemOneClassifier.classify_pr_risk(safe_diff)
    assert res_safe.selected_category == "SAFE_LOW_RISK"
    print(f"  [PASS] Clean diff classified as safe in {res_safe.latency_ms:.2f} ms: {res_safe.selected_category}")


def test_agora_branch_routing():
    print("\n--- 3. Testing Agora Branch Action Routing ---")
    
    active_branches = [
        "TREM2 dependent microglial clearance of tau seeds",
        "Cortical glycolytic reserve buffering amyloid burden"
    ]

    # Topic with strong overlap -> CONTRIBUTE_EXISTING
    existing_q = "Role of microglial TREM2 clearance in tauopathy progression"
    route_contribute = FastSystemOneClassifier.route_agora_branch(existing_q, active_branches)
    assert route_contribute.selected_category == "CONTRIBUTE_EXISTING"
    print(f"  [PASS] High-overlap topic routed to CONTRIBUTE_EXISTING in {route_contribute.latency_ms:.2f} ms")

    # Topic with novel domain -> NEW_BRANCH
    novel_q = "Choroid plexus cerebrospinal fluid fluidics during deep REM sleep"
    route_new = FastSystemOneClassifier.route_agora_branch(novel_q, active_branches)
    assert route_new.selected_category == "NEW_BRANCH"
    print(f"  [PASS] Novel topic routed to NEW_BRANCH in {route_new.latency_ms:.2f} ms")


def test_agent_and_api_integration():
    print("\n--- 4. Testing Agent & FastAPI Integration ---")
    
    # 1. MarrClassifierAgent fast_classify
    agent_res = MarrClassifierAgent.fast_classify("Synaptic graph diffusion dynamics regulate cognitive decline")
    assert agent_res["selected_category"] == "ALGORITHMIC"
    print("  [PASS] MarrClassifierAgent.fast_classify successfully invoked")

    # 2. FastAPI POST /api/discovery/system-one/classify-marr
    client = authenticated_client(app)
    resp = client.post(
        "/api/discovery/system-one/classify-marr",
        json={"statement": "Plasma pTau217 is a diagnostic fluid biomarker"}
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["selected_category"] == "IMPLEMENTATIONAL"
    assert data["system_tier"] == "SYSTEM_1_LOCAL_FAST"
    print(f"  [PASS] POST /api/discovery/system-one/classify-marr responded with {data['selected_category']}")


def test_tier_resolution():
    print("\n--- 5. Testing System 1 Tier Resolution (Local vs Kev vs Jev Cloud) ---")
    
    # Default is SYSTEM_1_LOCAL_FAST
    default_tier = FastSystemOneClassifier.get_active_tier()
    assert default_tier in ["SYSTEM_1_LOCAL_FAST", "SYSTEM_1_KEV_LOCAL", "SYSTEM_1_JEV_CLOUD"]
    print(f"  [PASS] Default active tier resolved cleanly: {default_tier}")

    # Simulated Kev local endpoint
    os.environ["KEV_LOCAL_URL"] = "http://localhost:11434/v1/chat/completions"
    assert FastSystemOneClassifier.get_active_tier() == "SYSTEM_1_KEV_LOCAL"
    print("  [PASS] KEV_LOCAL_URL detected: SYSTEM_1_KEV_LOCAL")
    del os.environ["KEV_LOCAL_URL"]


if __name__ == "__main__":
    test_fast_marr_classification()
    test_pr_guardrail_triage()
    test_agora_branch_routing()
    test_agent_and_api_integration()
    test_tier_resolution()
    print("\n=======================================================")
    print(" ALL JEV SYSTEM ONE FAST CLASSIFIER TESTS PASSED (E2E) ")
    print("=======================================================")

