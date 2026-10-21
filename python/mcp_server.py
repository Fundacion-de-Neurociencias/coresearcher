"""CoResearcher FastMCP Server for Claude Science and Desktop Integration.

Exposes CoResearcher's:
1. Knowledge graph & State space inspection
2. Tournament debates & Hypothesis validation
3. Reality Contact Score (RCS) & Empirical verification
4. Defeated Hypotheses Graveyard & Autopsy queries
5. Paper2Agent reproducible methods
"""

from __future__ import annotations

import json
from typing import Any, Dict, List, Optional
from mcp.server.fastmcp import FastMCP

# Initialize FastMCP Server
mcp = FastMCP(
    "CoResearcher-Science-Engine",
    instructions="CoResearcher Epistemic Engine providing audit-grade scientific discovery, hypothesis tournaments, state space pruning, and empirical verification."
)


@mcp.tool()
def inspect_state_space() -> str:
    """Inspect the CoResearcher Omega State Space, active axes, and combinatorial volume."""
    from api.state import state_space_omega
    data = {
        "domain": state_space_omega.domain_name,
        "total_combinatorial_states": state_space_omega.total_volume,
        "axes": [
            {
                "name": ax.name,
                "description": ax.description,
                "cardinality": ax.cardinality,
                "domain_values": ax.domain_values,
            }
            for ax in state_space_omega.axes
        ],
    }
    return json.dumps(data, indent=2)


@mcp.tool()
def list_biological_programs() -> str:
    """List all biological programs mapped in CoResearcher with their mechanisms and entities."""
    from api.state import biological_programs_list
    programs = [bp.to_dict() for bp in biological_programs_list]
    return json.dumps(programs, indent=2)


@mcp.tool()
def query_defeated_hypotheses_graveyard(domain: Optional[str] = None) -> str:
    """Query the graveyard of falsified and defeated scientific hypotheses, including autopsy reasons."""
    from api.state import hypothesis_graveyard
    records = hypothesis_graveyard.get_all_records()
    if domain:
        records = [r for r in records if getattr(r, "domain", None) == domain]
    return json.dumps([r.to_dict() for r in records], indent=2)


@mcp.tool()
def calculate_reality_contact_score(
    claim_id: str,
    empirical_evidence_ids: List[str],
    predicted_effect_size: float,
    observed_effect_size: float,
    sample_size: int = 100
) -> str:
    """Evaluate the Reality Contact Score (RCS) and substrate distance for a scientific claim."""
    from python.discovery import RealityContactEvaluator, RealityContactEvidence, SubstrateTier

    evidence_items = [
        RealityContactEvidence(
            evidence_id=eid,
            substrate_tier=SubstrateTier.WET_EMPIRICAL,
            effect_size_observed=observed_effect_size,
            sample_size=sample_size,
            p_value=0.001,
            replicated=True,
        )
        for eid in empirical_evidence_ids
    ]

    evaluation = RealityContactEvaluator.evaluate_claim(
        claim_id=claim_id,
        predicted_effect_size=predicted_effect_size,
        evidence_chain=evidence_items,
    )
    return json.dumps(evaluation.to_dict(), indent=2)


@mcp.tool()
def debate_pairwise_hypotheses(
    statement_a: str,
    statement_b: str,
    domain: str = "neuroscience",
    evidence_score_a: float = 0.8,
    evidence_score_b: float = 0.7
) -> str:
    """Execute a pairwise tournament debate between two rival hypotheses and update Elo ratings."""
    from python.discovery.hypothesis_elo_tournament import PairwiseDebateEngine, TournamentHypothesis

    h_a = TournamentHypothesis(
        hypothesis_id="HYP-A-USER",
        title="Candidate A",
        statement=statement_a,
        domain=domain,
        evidence_score=evidence_score_a,
        physical_consistency_score=0.9,
        delta_omega_potential=0.85,
        falsifiability_score=0.9,
    )
    h_b = TournamentHypothesis(
        hypothesis_id="HYP-B-USER",
        title="Candidate B",
        statement=statement_b,
        domain=domain,
        evidence_score=evidence_score_b,
        physical_consistency_score=0.85,
        delta_omega_potential=0.80,
        falsifiability_score=0.85,
    )

    match_res = PairwiseDebateEngine.debate(h_a, h_b)
    return json.dumps({
        "match": match_res.to_dict(),
        "winner": match_res.winner_id,
        "loser": match_res.loser_id,
        "rationale": match_res.decision_rationale,
        "hypothesis_a_updated_elo": h_a.elo_rating,
        "hypothesis_b_updated_elo": h_b.elo_rating,
    }, indent=2)


@mcp.tool()
def execute_scientific_failure_autopsy(
    hypothesis_id: str,
    predicted_outcome: str,
    observed_outcome: str,
    auxiliary_assumptions: Optional[List[str]] = None
) -> str:
    """Diagnose root cause of an empirical failure using the Duhem-Quine scientific failure engine."""
    from python.discovery import ScientificFailureEngine
    autopsy = ScientificFailureEngine.diagnose_failure(
        hypothesis_id=hypothesis_id,
        prediction_id=f"PRED-{hypothesis_id}",
        observed_outcome=observed_outcome,
        predicted_outcome=predicted_outcome,
        auxiliary_assumptions=auxiliary_assumptions or [],
    )
    return json.dumps(autopsy.to_dict(), indent=2)


@mcp.tool()
def query_paper2agent_reproducible_tools(topic: str) -> str:
    """Query Nature 2026 Paper2Agent virtual authors and their executable analytical methods."""
    from python.discovery import GroundedSearchSensor
    agents = GroundedSearchSensor.query_paper_agents(topic)
    return json.dumps([a.to_dict() for a in agents], indent=2)


if __name__ == "__main__":
    mcp.run()
