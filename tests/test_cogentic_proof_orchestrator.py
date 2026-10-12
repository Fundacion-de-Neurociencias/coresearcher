"""
Test suite for Cogentic Multi-Agent Prove-Verify Harness (ADR-DISCOVERY-050).
Verifies:
1. Strict adversarial verification gate trapping counterexamples.
2. Trapping of unstated implicit mathematical assumptions.
3. Premise grounding enforcement (no unverified premise dependencies).
4. Full prove-verify loop, persistent lemma ledger, and Merkle root anchoring.
5. REST API endpoint /api/discovery/cogentic/run-proof-discovery.
"""

from __future__ import annotations

import pytest

from api.server import app
from api.testing import authenticated_client
from python.discovery.cogentic_proof_orchestrator import (
    AdversarialLemmaVerifier,
    AdversarialVerdictStatus,
    CandidateLemmaStep,
    CogenticProofOrchestrator,
)


@pytest.fixture
def client():
    return authenticated_client(app)


def test_adversarial_counterexample_trapped():
    verifier = AdversarialLemmaVerifier()
    # Step claims equality to zero for all x, but expression evaluates to non-zero
    step = CandidateLemmaStep(
        step_id="bad_lemma_1",
        target_conjecture_id="conj_001",
        statement="x + 5 == 0 for all x",
        symbolic_expression="x + 5",
        premises=[],
    )
    result = verifier.audit_lemma_step(step, {})
    assert not result.is_sound
    assert result.verdict == AdversarialVerdictStatus.COUNTEREXAMPLE_FOUND
    assert "counterexample" in result.rationale.lower()


def test_unstated_implicit_assumption_trapped():
    verifier = AdversarialLemmaVerifier()
    # Step relies on unstated regularity/compactness
    step = CandidateLemmaStep(
        step_id="flawed_assumption_step",
        target_conjecture_id="conj_002",
        statement="Every bounded continuous function attains its supremum",
        symbolic_expression="y",
        premises=[],
        unstated_assumptions=["compactness_of_domain"],
    )
    result = verifier.audit_lemma_step(step, {})
    assert not result.is_sound
    assert result.verdict == AdversarialVerdictStatus.IMPLICIT_ASSUMPTION_VIOLATION


def test_ungrounded_premise_trapped():
    verifier = AdversarialLemmaVerifier()
    step = CandidateLemmaStep(
        step_id="premise_leap_step",
        target_conjecture_id="conj_003",
        statement="Continuation step relying on unverified lemma",
        symbolic_expression="z - z",
        premises=["ghost_lemma_99"],
    )
    result = verifier.audit_lemma_step(step, {})
    assert not result.is_sound
    assert result.verdict == AdversarialVerdictStatus.DEDUCTIVE_GAP
    assert "ghost_lemma_99" in result.rationale


def test_cogentic_full_prove_verify_loop_success():
    orchestrator = CogenticProofOrchestrator(max_model_budget=50)
    report = orchestrator.run_proof_discovery(
        conjecture_id="auction_complexity_bound",
        target_statement="Mechanism revenue monotonicity holds under linear prior distribution",
    )
    assert report.is_fully_proven
    assert report.total_model_calls <= 50
    assert report.verified_lemmas_count >= 2
    assert report.merkle_root_sha256 is not None
    assert len(report.merkle_root_sha256) == 64


def test_cogentic_rest_api_endpoint(client):
    payload = {
        "conjecture_id": "online_learning_regret_bound",
        "target_statement": "Sub-linear regret O(sqrt(T)) for online convex optimization",
        "max_model_budget": 100,
    }
    response = client.post("/api/discovery/cogentic/run-proof-discovery", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["conjecture_id"] == "online_learning_regret_bound"
    assert "is_fully_proven" in data
    assert "merkle_root_sha256" in data
    assert data["verified_lemmas_count"] >= 1
