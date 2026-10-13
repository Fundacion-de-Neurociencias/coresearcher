"""
tests/test_hypothesis_tournament_arena.py - Test suite for Hypothesis Tournament Arena (ADR-DISCOVERY-058).
"""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from api.server import app
from python.discovery.hypothesis_tournament_arena import (
    DebateAxis,
    DebateMatchResult,
    HypothesisEloTournamentOrchestrator,
    PairwiseDebateEngine,
    TournamentHypothesis,
    TournamentReport,
)


@pytest.fixture
def client():
    return TestClient(app)


def test_pairwise_debate_decisive_victory():
    """Verifies that a hypothesis with superior evidence and physical compliance decisively defeats a weaker rival."""
    hyp_superior = TournamentHypothesis(
        hypothesis_id="hyp-001",
        title="Microglial Trem2 Cleavage",
        statement="Shedding of sTREM2 into CSF inhibits tau seeding.",
        domain="NEURODEGENERATION",
        evidence_score=0.92,
        physical_consistency_score=0.95,
        delta_omega_potential=0.85,
        falsifiability_score=0.90,
        elo_rating=1200.0,
    )

    hyp_inferior = TournamentHypothesis(
        hypothesis_id="hyp-002",
        title="Passive Amyloid Deposition",
        statement="Amyloid aggregates passively without microglial interaction.",
        domain="NEURODEGENERATION",
        evidence_score=0.35,
        physical_consistency_score=0.40,
        delta_omega_potential=0.30,
        falsifiability_score=0.45,
        elo_rating=1200.0,
    )

    result = PairwiseDebateEngine.debate(hyp_a=hyp_superior, hyp_b=hyp_inferior, k_factor=32.0)

    assert isinstance(result, DebateMatchResult)
    assert result.score_a == 1.0
    assert result.score_b == 0.0
    assert result.elo_delta_a > 0.0
    assert result.elo_delta_b < 0.0
    assert hyp_superior.elo_rating > 1200.0
    assert hyp_inferior.elo_rating < 1200.0
    assert hyp_superior.wins == 1
    assert hyp_inferior.losses == 1
    assert result.axis_differentials[DebateAxis.EVIDENCE_GROUNDING.value] > 0.0


def test_pairwise_debate_draw():
    """Verifies that nearly identical competing hypotheses end in an empirical draw."""
    hyp_a = TournamentHypothesis(
        hypothesis_id="hyp-a",
        title="Receptor A Modulator",
        statement="Mechanism operates via GPCR receptor A.",
        domain="PHARMACOLOGY",
        evidence_score=0.80,
        physical_consistency_score=0.80,
        delta_omega_potential=0.80,
        falsifiability_score=0.80,
        elo_rating=1200.0,
    )

    hyp_b = TournamentHypothesis(
        hypothesis_id="hyp-b",
        title="Receptor B Modulator",
        statement="Mechanism operates via homologous receptor B.",
        domain="PHARMACOLOGY",
        evidence_score=0.81,
        physical_consistency_score=0.79,
        delta_omega_potential=0.80,
        falsifiability_score=0.80,
        elo_rating=1200.0,
    )

    result = PairwiseDebateEngine.debate(hyp_a=hyp_a, hyp_b=hyp_b)

    assert result.score_a == 0.5
    assert result.score_b == 0.5
    assert hyp_a.draws == 1
    assert hyp_b.draws == 1
    assert abs(result.elo_delta_a) < 1.0


def test_round_robin_tournament_orchestration():
    """Verifies that a round-robin tournament produces a valid sorted Elo leaderboard."""
    candidates = [
        TournamentHypothesis(
            hypothesis_id="h-strong",
            title="Targeted Degradation",
            statement="PROTAC degrades tau with 95% specificity.",
            domain="DRUG_DISCOVERY",
            evidence_score=0.95,
            physical_consistency_score=0.98,
            delta_omega_potential=0.90,
            falsifiability_score=0.92,
        ),
        TournamentHypothesis(
            hypothesis_id="h-mid",
            title="Allosteric Inhibitor",
            statement="Small molecule stabilizes monomeric form.",
            domain="DRUG_DISCOVERY",
            evidence_score=0.65,
            physical_consistency_score=0.70,
            delta_omega_potential=0.60,
            falsifiability_score=0.65,
        ),
        TournamentHypothesis(
            hypothesis_id="h-weak",
            title="Non-specific Antioxidant",
            statement="Flavonoid scavenges ROS in tauopathy.",
            domain="DRUG_DISCOVERY",
            evidence_score=0.30,
            physical_consistency_score=0.40,
            delta_omega_potential=0.25,
            falsifiability_score=0.35,
        ),
    ]

    orchestrator = HypothesisEloTournamentOrchestrator()
    report = orchestrator.run_round_robin_tournament(
        tournament_id="protac-tournament-2026",
        domain="DRUG_DISCOVERY",
        candidates=candidates,
        rounds=1,
    )

    assert isinstance(report, TournamentReport)
    assert report.total_matches == 3
    assert len(report.leaderboard) == 3
    # h-strong must be #1, followed by h-mid, then h-weak
    assert report.top_hypothesis.hypothesis_id == "h-strong"
    assert report.leaderboard[0].hypothesis_id == "h-strong"
    assert report.leaderboard[1].hypothesis_id == "h-mid"
    assert report.leaderboard[2].hypothesis_id == "h-weak"
    assert report.leaderboard[0].elo_rating > report.leaderboard[1].elo_rating > report.leaderboard[2].elo_rating
    assert report.tournament_hash.startswith("sha256:")


def test_tournament_api_endpoints(client):
    """Verifies the REST API endpoints for debate matches and full tournaments."""
    # 1. Debate match endpoint
    debate_resp = client.post(
        "/api/discovery/tournament/debate-match",
        json={
            "hypothesis_a": {
                "hypothesis_id": "api-h1",
                "title": "Hypothesis 1",
                "statement": "Statement 1",
                "evidence_score": 0.85,
                "physical_consistency_score": 0.90,
                "delta_omega_potential": 0.80,
                "falsifiability_score": 0.80,
            },
            "hypothesis_b": {
                "hypothesis_id": "api-h2",
                "title": "Hypothesis 2",
                "statement": "Statement 2",
                "evidence_score": 0.40,
                "physical_consistency_score": 0.45,
                "delta_omega_potential": 0.35,
                "falsifiability_score": 0.40,
            },
            "k_factor": 32.0,
        },
    )
    assert debate_resp.status_code == 200
    debate_data = debate_resp.json()
    assert "match" in debate_data
    assert debate_data["match"]["score_a"] == 1.0

    # 2. Run tournament endpoint
    tournament_resp = client.post(
        "/api/discovery/tournament/run-tournament",
        json={
            "tournament_id": "api-tourney-1",
            "domain": "NEUROLOGY",
            "candidates": [
                {
                    "hypothesis_id": "cand-1",
                    "title": "Cand 1",
                    "statement": "Statement 1",
                    "evidence_score": 0.90,
                    "physical_consistency_score": 0.90,
                    "delta_omega_potential": 0.90,
                    "falsifiability_score": 0.90,
                },
                {
                    "hypothesis_id": "cand-2",
                    "title": "Cand 2",
                    "statement": "Statement 2",
                    "evidence_score": 0.30,
                    "physical_consistency_score": 0.30,
                    "delta_omega_potential": 0.30,
                    "falsifiability_score": 0.30,
                },
            ],
            "rounds": 1,
        },
    )
    assert tournament_resp.status_code == 200
    t_data = tournament_resp.json()
    assert t_data["tournament_id"] == "api-tourney-1"
    assert t_data["top_hypothesis"]["hypothesis_id"] == "cand-1"
    assert t_data["tournament_hash"].startswith("sha256:")
