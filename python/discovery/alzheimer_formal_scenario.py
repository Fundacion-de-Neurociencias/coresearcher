"""
python/discovery/alzheimer_formal_scenario.py - The Alzheimer scenario as formal hypotheses (ADR-DISCOVERY-061).

Migrates the canonical neurodegeneration Omega (`state_space.py`) and the three rival hypotheses of the demo
scenario (`api/state.py`) to the formal object of ADR-DISCOVERY-059.

STATUS: DRAFT. These formalizations were written by the CoResearcher maintainers from the prose statements and need
review by neuroscientists before any verdict below is presented as a property of the scientific hypotheses. They
are a faithful reading of the prose only where the prose speaks about single states. Parts of the prose that are
statistical or relational (a correlation, "no topological pattern", "primarily", "a byproduct") cannot be expressed
as constraints on one state and are listed under `not_formalized` instead of being approximated silently.

Omega: the six canonical axes plus white matter hyperintensity burden (`wmh`), which the vascular rival needs and the
canonical space lacked: 2 * 2 * 2 * 3 * 2 * 2 * 2 = 192 states.
"""

from __future__ import annotations

from typing import Any, Dict, List

from python.discovery.formal_hypothesis import Hypothesis, HypothesisEvaluator, Variable

STATUS = "DRAFT_PENDING_SCIENTIST_REVIEW"

VARIABLES = [
    Variable("amyloid", ("A-", "A+")),
    Variable("tau", ("T-", "T+")),
    Variable("neurodegeneration", ("N-", "N+")),
    Variable("hub", ("low", "medium", "high")),  # Functional hub nodal strength: <0.30, 0.30-0.65, >0.65.
    Variable("inflammation", ("normal", "reactive")),
    Variable("outcome", ("stable_mci", "accelerated_dementia")),  # 36-month clinical transition.
    Variable("wmh", ("low", "high")),  # Added axis: white matter hyperintensity burden.
]

RIVALS: List[Dict[str, Any]] = [
    {
        "hypothesis_id": "HYP-TAU-CONNECTOME",
        "statement": (
            "Tau spreading rates and cognitive decline are governed by connectome hub vulnerability and synaptic flux."
        ),
        "scope": "tau == 'T+'",
        "assumptions": [],
        "claims": [
            "hub != 'high' or outcome == 'accelerated_dementia'",
            "hub != 'low' or outcome == 'stable_mci'",
        ],
        "not_formalized": [
            "'spreading rates' and 'synaptic flux' are dynamics over time; Omega has one 36-month outcome.",
            "Medium hub strength: the prose does not say which outcome it implies, so it is left unconstrained.",
        ],
    },
    {
        "hypothesis_id": "HYP-VASCULAR-WMH",
        "statement": (
            "Longitudinal cognitive decline is primarily driven by microvascular ischemic damage (WMH), "
            "pTau is a co-occurring byproduct."
        ),
        "scope": None,
        "assumptions": [],
        "claims": [
            "wmh != 'high' or outcome == 'accelerated_dementia'",
            "wmh != 'low' or outcome == 'stable_mci'",
        ],
        "not_formalized": [
            "'primarily' is a share of explained variance (AUX-ISCHEMIA-DOMINANCE: >50%), a population quantity.",
            "'pTau is a byproduct' is a causal claim about direction, not a constraint on a single state.",
        ],
    },
    {
        "hypothesis_id": "HYP-NULL-NONSPECIFIC",
        "statement": (
            "pTau217 elevation is an unspecific passive leakage marker of general cortical death "
            "with no topological pattern."
        ),
        "scope": None,
        "assumptions": [],
        "claims": ["tau != 'T+' or neurodegeneration == 'N+'"],
        "not_formalized": [
            "'no topological pattern' is a claim about spatial distribution across regions; Omega has no regions.",
        ],
    },
]


def rival_hypotheses() -> List[Hypothesis]:
    return [
        Hypothesis(
            hypothesis_id=r["hypothesis_id"],
            variables=list(VARIABLES),
            claims=r["claims"],
            assumptions=r["assumptions"],
            scope=r["scope"],
            statement=r["statement"],
            alternatives=[x["hypothesis_id"] for x in RIVALS if x is not r],
        )
        for r in RIVALS
    ]


def variable_schema() -> List[Dict[str, Any]]:
    return [{"name": v.name, "domain": list(v.domain)} for v in VARIABLES]


def scenario_report(max_examples: int = 3) -> Dict[str, Any]:
    """Every rival evaluated, and every pair compared with the states that would discriminate them."""
    hypotheses = rival_hypotheses()
    evaluations = {
        h.hypothesis_id: HypothesisEvaluator.evaluate(h, max_examples=max_examples).to_dict() for h in hypotheses
    }
    comparisons = [
        HypothesisEvaluator.compare(a, b, max_examples=max_examples).to_dict()
        for i, a in enumerate(hypotheses)
        for b in hypotheses[i + 1 :]
    ]
    return {
        "status": STATUS,
        "variables": variable_schema(),
        "omega_size": hypotheses[0].omega_size,
        "rivals": [
            {k: r[k] for k in ("hypothesis_id", "statement", "scope", "assumptions", "claims", "not_formalized")}
            for r in RIVALS
        ],
        "evaluations": evaluations,
        "comparisons": comparisons,
    }
