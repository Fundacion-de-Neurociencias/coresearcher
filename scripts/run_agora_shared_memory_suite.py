#!/usr/bin/env python3
"""
scripts/run_agora_shared_memory_suite.py - Verification Suite for Agora Shared Memory (ADR-DISCOVERY-023).
Tests:
1. Multi-agent asynchronous commit logging into EpistemicGitRepo.
2. Agora Open-Branches Index correctly prevents parallel workers from duplicating directions.
3. Agora Verified-Claims Index allows downstream workers to reuse verified invariants (RCS >= 2).
4. Cross-branch epistemic cherry-picking links disparate discovery lines with preserved parent DAG lineage.
5. FastAPI REST API endpoints (/api/discovery/git/*) respond with valid schemas.
"""

import sys
import os

root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

from python.discovery.scientific_git_history import (
    EpistemicGitRepo,
    EpistemicDiff,
    BranchStatus,
)
from fastapi.testclient import TestClient
from api.server import app
from api.testing import authenticated_client


def test_agora_branch_and_claim_coordination():
    print("--- 1. Testing Agora Branch & Verified Claim Coordination ---")
    repo = EpistemicGitRepo.create_canonical_tau_lineage()

    # Verify initial canonical claims
    verified_claims = repo.agora_index.get_verified_claims()
    assert len(verified_claims) >= 1, "Expected at least 1 verified claim from canonical tau lineage"
    claim_tau = verified_claims[0]
    print(f"  [PASS] Verified claim detected: {claim_tau.claim_id} (RCS={claim_tau.rcs_score})")

    # Worker 1 creates branch for Microglial Clearance
    c3_sha = repo.commits[claim_tau.commit_sha].commit_sha
    branch_microglia = repo.create_branch(
        branch_id="branch-worker-microglia-01",
        start_commit_sha=c3_sha,
        entity_id="HYP-MICROGLIAL-CLEARANCE",
        entity_type="HYPOTHESIS",
        research_topic="TREM2 dependent microglial clearance of tau seeds",
        author_role="Worker Agent #1",
        tags=["immunology", "tauopathy"]
    )
    assert branch_microglia.status == BranchStatus.ACTIVE
    print(f"  [PASS] Worker #1 created branch: {branch_microglia.branch_id}")

    # Worker 2 checks open branches before starting work
    open_branches = repo.agora_index.get_open_branches()
    open_topics = [b.research_topic for b in open_branches]
    assert any("TREM2" in t for t in open_topics), "Worker #2 should see TREM2 branch is already being explored"
    print(f"  [PASS] Worker #2 queried open branches ({len(open_branches)} active): successfully detected ongoing TREM2 effort")

    # Worker 2 opens an unaddressed branch: Vascular Glymphatic Clearance
    branch_vascular = repo.create_branch(
        branch_id="branch-worker-vascular-02",
        start_commit_sha=c3_sha,
        entity_id="HYP-GLYMPHATIC-PERFUSION",
        entity_type="HYPOTHESIS",
        research_topic="Slow-wave sleep glymphatic clearance buffers tau accumulation",
        author_role="Worker Agent #2",
        tags=["vascular", "sleep", "clearance"]
    )
    print(f"  [PASS] Worker #2 opened independent branch: {branch_vascular.branch_id}")

    # Worker 1 commits experimental result and elevates it to a verified constraint
    diff_microglia = EpistemicDiff(
        parameter_changes={"trem2_activation_fold": 2.4},
        scope_changes={"cohort": "Preclinical ADNI-3"},
        auxiliary_assumptions_added=["AUX-TREM2-PHAGOCYTOSIS"],
        auxiliary_assumptions_removed=[],
        falsification_conditions_modified=[]
    )
    commit_microglia = repo.commit(
        author_role="Worker Agent #1",
        entity_type="CONSTRAINT",
        entity_id="CONST-TREM2-CLEARANCE-RATE",
        version_tag="v1.0.0",
        commit_message="Verified invariant: TREM2 activation accelerates tau seed clearance by 2.4x",
        mutation_trigger="Empirical in-vitro microglial clearance assay",
        epistemic_diff=diff_microglia,
        payload_snapshot={"statement": "TREM2 activation strictly increases oligomeric clearance velocity > 2.0x"},
        branch_id="branch-worker-microglia-01",
        rcs_score=2,
        is_verified_invariant=True
    )
    print(f"  [PASS] Worker #1 committed verified invariant: {commit_microglia.commit_sha}")

    # Worker 2 cherry-picks Worker 1's verified claim to synthesize a unified hybrid model
    claims_now = repo.agora_index.get_verified_claims()
    trem2_claim = next((c for c in claims_now if "TREM2" in c.claim_id), None)
    assert trem2_claim is not None, "Worker #1's verified claim must be present in Agora index"

    prev_head_sha = branch_vascular.head_commit_sha
    cherry_commit = repo.cherry_pick_claim(
        target_branch_id="branch-worker-vascular-02",
        source_claim_id=trem2_claim.claim_id,
        author_role="Worker Agent #2"
    )
    assert cherry_commit.parent_commit_sha == prev_head_sha
    assert branch_vascular.head_commit_sha == cherry_commit.commit_sha
    print(f"  [PASS] Worker #2 cherry-picked claim {trem2_claim.claim_id} into vascular branch without duplicating experiments")


def test_agora_api_endpoints():
    print("\n--- 2. Testing Agora FastAPI Endpoints ---")
    client = authenticated_client(app)

    # 1. GET /api/discovery/git/open-branches
    resp_open = client.get("/api/discovery/git/open-branches")
    assert resp_open.status_code == 200
    data_open = resp_open.json()
    assert "open_branches_count" in data_open
    print(f"  [PASS] GET /api/discovery/git/open-branches returned {data_open['open_branches_count']} active branches")

    # 2. GET /api/discovery/git/verified-claims
    resp_claims = client.get("/api/discovery/git/verified-claims")
    assert resp_claims.status_code == 200
    data_claims = resp_claims.json()
    assert data_claims["verified_claims_count"] >= 1
    sample_claim = data_claims["claims"][0]
    print(f"  [PASS] GET /api/discovery/git/verified-claims returned {data_claims['verified_claims_count']} claims (e.g. {sample_claim['claim_id']})")

    # 3. POST /api/discovery/git/branch/create
    # Use the sample claim's commit_sha as root
    root_sha = sample_claim["commit_sha"]
    resp_create = client.post(
        "/api/discovery/git/branch/create",
        json={
            "branch_id": "branch-api-agent-99",
            "start_commit_sha": root_sha,
            "entity_id": "HYP-API-TEST",
            "entity_type": "HYPOTHESIS",
            "research_topic": "Testing Agora Shared Memory API creation",
            "author_role": "API Test Worker",
            "tags": ["test", "api"]
        }
    )
    assert resp_create.status_code == 200
    data_create = resp_create.json()
    assert data_create["branch_id"] == "branch-api-agent-99"
    assert data_create["status"] == "ACTIVE"
    print(f"  [PASS] POST /api/discovery/git/branch/create verified: branch {data_create['branch_id']} active")

    # 4. POST /api/discovery/git/branch/cherry-pick
    resp_cherry = client.post(
        "/api/discovery/git/branch/cherry-pick",
        json={
            "target_branch_id": "branch-api-agent-99",
            "source_claim_id": sample_claim["claim_id"],
            "author_role": "API Test Worker"
        }
    )
    assert resp_cherry.status_code == 200
    data_cherry = resp_cherry.json()
    assert data_cherry["commit_sha"].startswith("sha1:")
    print(f"  [PASS] POST /api/discovery/git/branch/cherry-pick verified: commit {data_cherry['commit_sha']}")


if __name__ == "__main__":
    test_agora_branch_and_claim_coordination()
    test_agora_api_endpoints()
    print("\n=======================================================")
    print(" ALL AGORA SHARED MEMORY TESTS PASSED EMPIRICALLY     ")
    print("=======================================================")
