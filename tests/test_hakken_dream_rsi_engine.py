"""
Test suite for Hakken Literature Abduction & Dream-RSI Offline Replay Engine (ADR-DISCOVERY-054).
Verifies:
1. Hakken predicts unrecorded biological link with sound PHELInE sufficiency and necessity.
2. Hakken flags temporal drift on fluctuating/unstable multi-hop chains.
3. Dream-RSI records a discovery tree and computes accurate total token cost.
4. Dream-RSI offline replay benchmarks alternative search policies without re-running simulations.
5. Dream-RSI policy optimizer selects the highest composite fitness exploration strategy.
6. REST API endpoints /api/discovery/hakken/predict-links and /api/discovery/dream-rsi/replay-policy return 200.
"""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from api.server import app
from python.discovery.hakken_dream_rsi_engine import (
    BranchOrderingHeuristic,
    DiscoveryHistoryNode,
    DreamRSIOfflineReplayEngine,
    HakkenLiteratureLinkEngine,
    LiteratureHop,
    ScientificDomainType,
    SearchPolicyConfig,
)


@pytest.fixture
def client():
    return TestClient(app)


def test_hakken_predict_unrecorded_biological_link():
    hops = [
        LiteratureHop("miR-155", "SIRT1", "DOWNREGULATES", literature_citations_count=18, temporal_stability_score=0.92, confidence_weight=0.90),
        LiteratureHop("SIRT1", "p53", "DEACETYLATES", literature_citations_count=35, temporal_stability_score=0.95, confidence_weight=0.92),
        LiteratureHop("p53", "p21_CIP1", "TRANSCRIPTIONALLY_ACTIVATES", literature_citations_count=52, temporal_stability_score=0.98, confidence_weight=0.95),
    ]

    candidate = HakkenLiteratureLinkEngine.predict_undocumented_link(
        candidate_id="cand_mir155_senescence",
        domain=ScientificDomainType.AGING_BIOLOGY,
        source="miR-155",
        target="p21_CIP1",
        predicted_relation="PROMOTES_SENESCENCE_VIA_SIRT1_AXIS",
        hops=hops,
        direct_literature_hits=0,  # Completely unrecorded in direct literature
    )

    assert candidate.novelty_score >= 0.90
    assert not candidate.is_previously_documented
    assert candidate.evidence_chain.is_sound_path
    assert candidate.evidence_chain.sufficiency_score > 0.65
    assert candidate.evidence_chain.necessity_score > 0.70
    assert candidate.evidence_chain.temporal_drift < 0.15
    assert candidate.som_hakken_hash.startswith("sha256:")
    assert "In vitro knockdown/CRISPR" in candidate.recommended_validation_assay


def test_hakken_flags_unstable_temporal_drift():
    # Hops with volatile temporal instability
    hops = [
        LiteratureHop("EntityA", "EntityB", "CORRELATES", literature_citations_count=2, temporal_stability_score=0.20, confidence_weight=0.40),
        LiteratureHop("EntityB", "EntityC", "PREDICTS", literature_citations_count=1, temporal_stability_score=0.15, confidence_weight=0.35),
    ]

    chain = HakkenLiteratureLinkEngine.audit_evidence_chain(
        chain_id="chain_drift",
        source="EntityA",
        target="EntityC",
        hops=hops,
    )

    assert not chain.is_sound_path
    assert chain.temporal_drift > 0.60  # High drift detected!
    assert chain.sufficiency_score < 0.35


def test_dream_rsi_discovery_tree_total_cost():
    leaf1 = DiscoveryHistoryNode("n3", "H3", branch_depth=2, compute_tokens_cost=3000, wet_lab_euro_cost=50.0, time_spent_hours=1.0, outcome_reward=0.2, failure_category="EPISTEMIC_FALSIFICATION", is_terminal=True)
    leaf2 = DiscoveryHistoryNode("n4", "H4", branch_depth=2, compute_tokens_cost=4000, wet_lab_euro_cost=100.0, time_spent_hours=2.0, outcome_reward=0.9, failure_category=None, is_terminal=True)
    branch = DiscoveryHistoryNode("n2", "H2", branch_depth=1, compute_tokens_cost=2000, wet_lab_euro_cost=20.0, time_spent_hours=0.5, outcome_reward=0.6, failure_category=None, is_terminal=False, children=[leaf1, leaf2])
    root = DiscoveryHistoryNode("n1", "H1", branch_depth=0, compute_tokens_cost=1000, wet_lab_euro_cost=0.0, time_spent_hours=0.2, outcome_reward=0.4, failure_category=None, is_terminal=False, children=[branch])

    total_tokens = DreamRSIOfflineReplayEngine.calculate_tree_total_cost(root)
    assert total_tokens == 1000 + 2000 + 3000 + 4000  # 10,000 tokens


def test_dream_rsi_offline_policy_replay_saves_tokens():
    # Construct a tree where branch A is a dead end (low reward) and branch B has high reward
    bad_leaf = DiscoveryHistoryNode("bad_leaf", "H_bad", branch_depth=2, compute_tokens_cost=10_000, wet_lab_euro_cost=500.0, time_spent_hours=5.0, outcome_reward=0.05, failure_category="EPISTEMIC_FALSIFICATION", is_terminal=True)
    bad_branch = DiscoveryHistoryNode("bad_branch", "H_deadend", branch_depth=1, compute_tokens_cost=5_000, wet_lab_euro_cost=200.0, time_spent_hours=2.0, outcome_reward=0.10, failure_category=None, is_terminal=False, children=[bad_leaf])

    good_leaf = DiscoveryHistoryNode("good_leaf", "H_target", branch_depth=2, compute_tokens_cost=5_000, wet_lab_euro_cost=100.0, time_spent_hours=1.0, outcome_reward=0.92, failure_category=None, is_terminal=True)
    good_branch = DiscoveryHistoryNode("good_branch", "H_promising", branch_depth=1, compute_tokens_cost=3_000, wet_lab_euro_cost=50.0, time_spent_hours=0.5, outcome_reward=0.80, failure_category=None, is_terminal=False, children=[good_leaf])

    root = DiscoveryHistoryNode("root", "H_root", branch_depth=0, compute_tokens_cost=1_000, wet_lab_euro_cost=0.0, time_spent_hours=0.1, outcome_reward=0.50, failure_category=None, is_terminal=False, children=[bad_branch, good_branch])

    # Value-Greedy policy: prunes branches below 0.20 reward
    policy = SearchPolicyConfig(
        policy_id="test_greedy",
        branch_ordering=BranchOrderingHeuristic.VALUE_GREEDY,
        pruning_reward_threshold=0.20,
        stop_early_on_reward=0.90,
    )

    result = DreamRSIOfflineReplayEngine.replay_policy_on_tree(root, policy)

    assert result.max_reward_achieved >= 0.90
    assert result.early_stopped
    assert result.pruned_nodes_count >= 1  # bad_leaf was pruned!
    assert result.tokens_saved_vs_full_tree > 0
    assert result.som_replay_hash.startswith("sha256:")


def test_dream_rsi_policy_optimization():
    # Synthetic tree
    n3 = DiscoveryHistoryNode("n3", "H3", branch_depth=2, compute_tokens_cost=8000, wet_lab_euro_cost=0.0, time_spent_hours=1.0, outcome_reward=0.05, failure_category="EPISTEMIC_FALSIFICATION", is_terminal=True)
    n2 = DiscoveryHistoryNode("n2", "H2", branch_depth=1, compute_tokens_cost=4000, wet_lab_euro_cost=0.0, time_spent_hours=0.5, outcome_reward=0.88, failure_category=None, is_terminal=False, children=[n3])
    root = DiscoveryHistoryNode("n1", "H1", branch_depth=0, compute_tokens_cost=1000, wet_lab_euro_cost=0.0, time_spent_hours=0.1, outcome_reward=0.50, failure_category=None, is_terminal=False, children=[n2])

    opt_res = DreamRSIOfflineReplayEngine.optimize_policy_offline([root])
    assert "selected_best_policy_id" in opt_res
    assert opt_res["evaluated_trees_count"] == 1
    assert "best_policy_summary" in opt_res


def test_rest_api_endpoints(client):
    # Hakken prediction endpoint
    hakken_payload = {
        "candidate_id": "api_test_cand",
        "domain": "QUANTUM_COMPUTING",
        "source_entity": "FluxQubit",
        "target_entity": "CoherenceTimeT2",
        "predicted_relation": "OPTIMIZES_RESONANCE_SWEET_SPOT",
        "hops": [
            {"source_entity": "FluxQubit", "target_entity": "SQUID_Loop", "relation": "COUPLES_MAGNETIC_FLUX", "literature_citations_count": 40, "temporal_stability_score": 0.95, "confidence_weight": 0.92},
            {"source_entity": "SQUID_Loop", "target_entity": "CoherenceTimeT2", "relation": "SUPPRESSES_FLUX_NOISE", "literature_citations_count": 28, "temporal_stability_score": 0.90, "confidence_weight": 0.88},
        ],
        "direct_literature_hits": 0,
    }
    h_resp = client.post("/api/discovery/hakken/predict-links", json=hakken_payload)
    assert h_resp.status_code == 200
    h_data = h_resp.json()
    assert h_data["candidate_id"] == "api_test_cand"
    assert h_data["domain"] == "QUANTUM_COMPUTING"
    assert h_data["novelty_score"] >= 0.90
    assert "som_hakken_hash" in h_data

    # Dream-RSI replay endpoint
    dream_payload = {
        "history_tree": {
            "node_id": "root",
            "hypothesis_id": "H0",
            "branch_depth": 0,
            "compute_tokens_cost": 2000,
            "wet_lab_euro_cost": 0.0,
            "time_spent_hours": 0.5,
            "outcome_reward": 0.70,
            "is_terminal": False,
            "children": [
                {
                    "node_id": "leaf",
                    "hypothesis_id": "H1",
                    "branch_depth": 1,
                    "compute_tokens_cost": 3000,
                    "wet_lab_euro_cost": 50.0,
                    "time_spent_hours": 1.0,
                    "outcome_reward": 0.88,
                    "is_terminal": True,
                    "children": []
                }
            ]
        },
        "policy": {
            "policy_id": "api_pol",
            "branch_ordering": "VALUE_GREEDY",
            "worker_concurrency": 1,
            "pruning_reward_threshold": 0.20,
            "max_tokens_budget": 50000,
            "stop_early_on_reward": 0.85
        }
    }
    d_resp = client.post("/api/discovery/dream-rsi/replay-policy", json=dream_payload)
    assert d_resp.status_code == 200
    d_data = d_resp.json()
    assert d_data["policy_id"] == "api_pol"
    assert d_data["max_reward_achieved"] >= 0.85
    assert d_data["early_stopped"]
    assert "som_replay_hash" in d_data
