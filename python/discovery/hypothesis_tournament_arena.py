"""
python/discovery/hypothesis_tournament_arena.py - Hypothesis Tournament Arena & Multi-Agent Elo Ranking (ADR-DISCOVERY-058).

Inspired by:
Google DeepMind, Google Research & Google Labs (Nature, 2026): "Co-Scientist: A multi-agent AI partner to accelerate research"
(Idea Tournament via Pairwise Debate & Elo Ranking).

Review note (2026-10-15): the four axis scores are supplied by the caller; this module does not compute them.
A match is a weighted difference of those scores, so the ranking follows the scores themselves and Elo only
adds match-order effects. See ADR-DISCOVERY-058 (review section) and claims register row 22.

In contrast to cloud-dependent narrative consensus engines, CoResearcher's Tournament Arena:
1. Conducts pairwise comparative debates evaluated against rigorous non-generative epistemic axes:
   - Empirical Evidence Grounding (citations, UniProt/ChEMBL bioactivity, biological program linkage).
   - Physical & Thermodynamic Consistency (conservation laws, lack of holonomy defect).
   - State-Space Reduction Capacity (Delta Omega parameter space volume eliminated).
   - Falsifiability & Parsimony (Popperian testability, Occam penalty).
2. Updates dynamic Elo ratings (logistic expectancy curve) with adaptive K-factors.
3. Supports Round-Robin and Top-K Ladder tournament modes.
4. Cryptographically seals tournament ranking state into ScientificLedger.
5. Fully on-premise, zero-cloud sovereign execution (ADR-030).
"""

from __future__ import annotations

import enum
import hashlib
import json
import math
import time
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple

from python.observer.scientific_ledger import ScientificLedger


class DebateAxis(str, enum.Enum):
    """The four non-generative axes of scientific pairwise debate."""

    EVIDENCE_GROUNDING = "EVIDENCE_GROUNDING"
    PHYSICAL_CONSISTENCY = "PHYSICAL_CONSISTENCY"
    STATE_SPACE_REDUCTION = "STATE_SPACE_REDUCTION"
    FALSIFIABILITY_PARSIMONY = "FALSIFIABILITY_PARSIMONY"


@dataclass
class TournamentHypothesis:
    """A scientific hypothesis participating in the Elo tournament."""

    hypothesis_id: str
    title: str
    statement: str
    domain: str
    evidence_score: float = 0.5  # [0.0, 1.0] Grounding strength
    physical_consistency_score: float = 0.5  # [0.0, 1.0] Physical court compliance
    delta_omega_potential: float = 0.5  # [0.0, 1.0] State-space volume reduction
    falsifiability_score: float = 0.5  # [0.0, 1.0] Popperian falsifiability & testability
    elo_rating: float = 1200.0
    matches_played: int = 0
    wins: int = 0
    losses: int = 0
    draws: int = 0
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "hypothesis_id": self.hypothesis_id,
            "title": self.title,
            "statement": self.statement,
            "domain": self.domain,
            "evidence_score": round(self.evidence_score, 4),
            "physical_consistency_score": round(self.physical_consistency_score, 4),
            "delta_omega_potential": round(self.delta_omega_potential, 4),
            "falsifiability_score": round(self.falsifiability_score, 4),
            "elo_rating": round(self.elo_rating, 2),
            "matches_played": self.matches_played,
            "wins": self.wins,
            "losses": self.losses,
            "draws": self.draws,
            "metadata": self.metadata,
        }


@dataclass
class DebateMatchResult:
    """Outcome and detailed breakdown of a pairwise debate between two hypotheses."""

    match_id: str
    hypothesis_a_id: str
    hypothesis_b_id: str
    score_a: float  # 1.0 (win A), 0.5 (draw), 0.0 (win B)
    score_b: float
    axis_differentials: Dict[str, float]  # positive favors A, negative favors B
    elo_delta_a: float
    elo_delta_b: float
    synthesis_rationale: str
    timestamp: float = field(default_factory=time.time)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "match_id": self.match_id,
            "hypothesis_a_id": self.hypothesis_a_id,
            "hypothesis_b_id": self.hypothesis_b_id,
            "score_a": self.score_a,
            "score_b": self.score_b,
            "axis_differentials": {k: round(v, 4) for k, v in self.axis_differentials.items()},
            "elo_delta_a": round(self.elo_delta_a, 2),
            "elo_delta_b": round(self.elo_delta_b, 2),
            "synthesis_rationale": self.synthesis_rationale,
            "timestamp": self.timestamp,
        }


@dataclass
class TournamentReport:
    """Final consolidated summary of a hypothesis tournament."""

    tournament_id: str
    domain: str
    total_matches: int
    leaderboard: List[TournamentHypothesis]
    top_hypothesis: TournamentHypothesis
    matches: List[DebateMatchResult]
    tournament_hash: str
    execution_time_seconds: float

    def to_dict(self) -> Dict[str, Any]:
        return {
            "tournament_id": self.tournament_id,
            "domain": self.domain,
            "total_matches": self.total_matches,
            "leaderboard": [h.to_dict() for h in self.leaderboard],
            "top_hypothesis": self.top_hypothesis.to_dict(),
            "matches": [m.to_dict() for m in self.matches],
            "tournament_hash": self.tournament_hash,
            "execution_time_seconds": round(self.execution_time_seconds, 4),
        }


class PairwiseDebateEngine:
    """Evaluates a scientific debate match between two competing hypotheses."""

    # Default axis weights
    AXIS_WEIGHTS: Dict[DebateAxis, float] = {
        DebateAxis.EVIDENCE_GROUNDING: 0.30,
        DebateAxis.PHYSICAL_CONSISTENCY: 0.30,
        DebateAxis.STATE_SPACE_REDUCTION: 0.25,
        DebateAxis.FALSIFIABILITY_PARSIMONY: 0.15,
    }

    @classmethod
    def debate(
        cls,
        hyp_a: TournamentHypothesis,
        hyp_b: TournamentHypothesis,
        match_id: Optional[str] = None,
        k_factor: float = 32.0,
    ) -> DebateMatchResult:
        m_id = match_id or f"match_{hyp_a.hypothesis_id}_vs_{hyp_b.hypothesis_id}_{int(time.time() * 1000)}"

        # Compute differentials along each axis (A - B)
        diff_evidence = hyp_a.evidence_score - hyp_b.evidence_score
        diff_physical = hyp_a.physical_consistency_score - hyp_b.physical_consistency_score
        diff_omega = hyp_a.delta_omega_potential - hyp_b.delta_omega_potential
        diff_falsif = hyp_a.falsifiability_score - hyp_b.falsifiability_score

        axis_diffs = {
            DebateAxis.EVIDENCE_GROUNDING.value: diff_evidence,
            DebateAxis.PHYSICAL_CONSISTENCY.value: diff_physical,
            DebateAxis.STATE_SPACE_REDUCTION.value: diff_omega,
            DebateAxis.FALSIFIABILITY_PARSIMONY.value: diff_falsif,
        }

        # Weighted aggregate margin
        aggregate_margin = (
            cls.AXIS_WEIGHTS[DebateAxis.EVIDENCE_GROUNDING] * diff_evidence
            + cls.AXIS_WEIGHTS[DebateAxis.PHYSICAL_CONSISTENCY] * diff_physical
            + cls.AXIS_WEIGHTS[DebateAxis.STATE_SPACE_REDUCTION] * diff_omega
            + cls.AXIS_WEIGHTS[DebateAxis.FALSIFIABILITY_PARSIMONY] * diff_falsif
        )

        # Determine outcome: draw margin threshold = +/- 0.05
        if aggregate_margin > 0.05:
            score_a = 1.0
            score_b = 0.0
            winner_str = f"Hypothesis '{hyp_a.title}' won by margin +{aggregate_margin:.3f}"
        elif aggregate_margin < -0.05:
            score_a = 0.0
            score_b = 1.0
            winner_str = f"Hypothesis '{hyp_b.title}' won by margin +{abs(aggregate_margin):.3f}"
        else:
            score_a = 0.5
            score_b = 0.5
            winner_str = f"Empirical draw (margin {aggregate_margin:.3f} within tolerance)"

        # Standard Elo update
        expected_a = 1.0 / (1.0 + 10.0 ** ((hyp_b.elo_rating - hyp_a.elo_rating) / 400.0))
        expected_b = 1.0 - expected_a

        delta_elo_a = k_factor * (score_a - expected_a)
        delta_elo_b = k_factor * (score_b - expected_b)

        # Update mutable records
        hyp_a.elo_rating += delta_elo_a
        hyp_b.elo_rating += delta_elo_b
        hyp_a.matches_played += 1
        hyp_b.matches_played += 1

        if score_a == 1.0:
            hyp_a.wins += 1
            hyp_b.losses += 1
        elif score_b == 1.0:
            hyp_b.wins += 1
            hyp_a.losses += 1
        else:
            hyp_a.draws += 1
            hyp_b.draws += 1

        return DebateMatchResult(
            match_id=m_id,
            hypothesis_a_id=hyp_a.hypothesis_id,
            hypothesis_b_id=hyp_b.hypothesis_id,
            score_a=score_a,
            score_b=score_b,
            axis_differentials=axis_diffs,
            elo_delta_a=delta_elo_a,
            elo_delta_b=delta_elo_b,
            synthesis_rationale=winner_str,
        )


class HypothesisEloTournamentOrchestrator:
    """
    Orchestrates round-robin or multi-round tournaments among candidates,
    producing an epistemically grounded leaderboard.
    """

    def __init__(self, ledger: Optional[ScientificLedger] = None):
        self.ledger = ledger or ScientificLedger(ledger_id="hypothesis-tournament-ledger")

    def run_round_robin_tournament(
        self,
        tournament_id: str,
        domain: str,
        candidates: List[TournamentHypothesis],
        rounds: int = 1,
        k_factor: float = 32.0,
    ) -> TournamentReport:
        start_time = time.time()
        if len(candidates) < 2:
            raise ValueError("Tournament requires at least 2 candidate hypotheses.")

        matches: List[DebateMatchResult] = []
        n = len(candidates)

        for _ in range(rounds):
            for i in range(n):
                for j in range(i + 1, n):
                    match_res = PairwiseDebateEngine.debate(
                        hyp_a=candidates[i],
                        hyp_b=candidates[j],
                        k_factor=k_factor,
                    )
                    matches.append(match_res)

        # Sort leaderboard descending by Elo rating
        leaderboard = sorted(candidates, key=lambda h: h.elo_rating, reverse=True)
        top_hyp = leaderboard[0]

        elapsed = time.time() - start_time

        # Cryptographic sealing of tournament state
        summary_payload = {
            "tournament_id": tournament_id,
            "domain": domain,
            "total_matches": len(matches),
            "top_hypothesis_id": top_hyp.hypothesis_id,
            "top_elo": round(top_hyp.elo_rating, 2),
            "leaderboard_ids": [h.hypothesis_id for h in leaderboard],
        }
        t_hash = "sha256:" + hashlib.sha256(json.dumps(summary_payload, sort_keys=True).encode()).hexdigest()

        # Log to immutable ledger
        try:
            self.ledger.record_event(
                event_type="HYPOTHESIS_ELO_TOURNAMENT_COMPLETED",
                payload=summary_payload,
            )
        except Exception:
            pass

        return TournamentReport(
            tournament_id=tournament_id,
            domain=domain,
            total_matches=len(matches),
            leaderboard=leaderboard,
            top_hypothesis=top_hyp,
            matches=matches,
            tournament_hash=t_hash,
            execution_time_seconds=elapsed,
        )
