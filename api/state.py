"""Shared in-memory engine state for the CoResearcher API."""

import os
from typing import Dict

from python.discovery import (
    AuxiliaryAssumption,
    DecomposedDiscoveryValue,
    DiscoveryCampaign,
    DiscoveryWorkbench,
    DiscriminativePrediction,
    EpistemicGitRepo,
    ExplanationLevel,
    FormalImplication,
    HypothesisGraveyard,
    Representation,
    RepresentationLedger,
    RivalHypothesis,
    StateSpaceOmega,
    get_canonical_biological_programs,
)
from python.knowledge.ontology_plan_engine import (
    OntologyPlanEngine,
)

root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

python_dir = os.path.join(root_dir, "python")


# 1. State Space Ω
state_space_omega = StateSpaceOmega.create_canonical_neurodegen_space()


# 2. Epistemic Git Repo
epistemic_git_repo = EpistemicGitRepo.create_canonical_tau_lineage()


# 3. Defeated Hypotheses Graveyard
hypothesis_graveyard = HypothesisGraveyard()


# 4. Representation Ledger
representation_ledger = RepresentationLedger(
    domain="Neurodegeneration / Preclinical Alzheimer",
    candidate_representations=[
        Representation(
            representation_id="REP-A-NETWORK-DIFFUSION",
            name="Functional Connectome Graph Diffusion",
            marr_explanation_level=ExplanationLevel.ALGORITHMIC,
            observables_space=["Nodal degree", "Transinaptic flux", "Eigenvector centrality", "Hub vulnerability"],
            invisible_space=["Local microglial receptor density", "Kinase phosphorylation kinetics"],
            invariant_principles=["Conservation of network topological flux"],
            compression_power=0.82,
        ),
        Representation(
            representation_id="REP-B-SELECTIVE-VULNERABILITY",
            name="Cellular Transcriptomic Vulnerability",
            marr_explanation_level=ExplanationLevel.IMPLEMENTATIONAL,
            observables_space=["RORB+ layer V neuron density", "Tau aggregation kinetics", "Transcriptional stress"],
            invisible_space=["Long-range axonal propagation topology"],
            invariant_principles=["Cell-type specific proteostatic failure thresholds"],
            compression_power=0.74,
        ),
        Representation(
            representation_id="REP-C-VASCULAR-DYSDESIA",
            name="Neurovascular Unit & White Matter Hypoperfusion",
            marr_explanation_level=ExplanationLevel.IMPLEMENTATIONAL,
            observables_space=["White matter hyperintensity volume", "Cerebral blood flow", "Endothelial breakdown"],
            invisible_space=["Specific tau phospho-epitope conformational changes"],
            invariant_principles=["Ischemic metabolic supply deficit"],
            compression_power=0.68,
        ),
    ],
)


# 5. Operational Biological Programs
biological_programs_list = get_canonical_biological_programs()


# 6. Competing Hypotheses & Implication Models
rival_hypotheses = [
    RivalHypothesis(
        hypothesis_id="HYP-TAU-CONNECTOME",
        statement="Tau spreading rates and cognitive decline are governed by connectome hub vulnerability and synaptic flux.",
        representation_id="REP-A-NETWORK-DIFFUSION",
        marr_level=ExplanationLevel.ALGORITHMIC,
        biological_program_id="BP-TRANS-SYNAPTIC-SPREADING",
    ),
    RivalHypothesis(
        hypothesis_id="HYP-VASCULAR-WMH",
        statement="Longitudinal cognitive decline is primarily driven by microvascular ischemic damage (WMH), pTau is a co-occurring byproduct.",
        representation_id="REP-C-VASCULAR-DYSDESIA",
        marr_level=ExplanationLevel.IMPLEMENTATIONAL,
        biological_program_id="BP-LIPID-APOE4-TRAFFICKING",
    ),
    RivalHypothesis(
        hypothesis_id="HYP-NULL-NONSPECIFIC",
        statement="pTau217 elevation is an unspecific passive leakage marker of general cortical death with no topological pattern.",
        representation_id="REP-B-SELECTIVE-VULNERABILITY",
        marr_level=ExplanationLevel.COMPUTATIONAL,
        biological_program_id="BP-PROTEOSTASIS-AUTOPHAGY",
    ),
]


implications_registry = [
    FormalImplication(
        implication_id="IMP-TAU-01",
        core_hypothesis_id="HYP-TAU-CONNECTOME",
        auxiliary_assumptions=[
            AuxiliaryAssumption(
                "AUX-GRAPH-DIFFUSION",
                "Tau transmission follows structural/functional connectivity matrices",
                "BIOLOGICAL_BACKGROUND",
            ),
            AuxiliaryAssumption(
                "AUX-LONGITUDINAL-MIXED",
                "Longitudinal Mixed Effects with random slopes accurately models trajectory",
                "STATISTICAL_MODEL",
            ),
        ],
        consequent_prediction_id="PRED-DISCRIM-01",
    ),
    FormalImplication(
        implication_id="IMP-VASC-02",
        core_hypothesis_id="HYP-VASCULAR-WMH",
        auxiliary_assumptions=[
            AuxiliaryAssumption(
                "AUX-ISCHEMIA-DOMINANCE",
                "White matter hyperintensities account for >50% of progression variance",
                "BIOLOGICAL_BACKGROUND",
            ),
            AuxiliaryAssumption(
                "AUX-TAU-BYPRODUCT",
                "pTau217 is a passive non-causal leak of ischemic necrosis",
                "BIOLOGICAL_BACKGROUND",
            ),
        ],
        consequent_prediction_id="PRED-VASC-DOMINANCE",
    ),
]


discriminative_predictions = [
    DiscriminativePrediction(
        prediction_id="PRED-DISCRIM-01",
        statement="Cognitive decline rate correlates with connectome-weighted hub atrophy rather than uniform cortical thinning or WMH volume.",
        favors_hypothesis_id="HYP-TAU-CONNECTOME",
        contradicts_hypothesis_ids=["HYP-VASCULAR-WMH", "HYP-NULL-NONSPECIFIC"],
        falsification_metric="slope_pvalue",
        falsification_threshold="p < 0.05 in connectome-weighted MixedLM",
    )
]


decomposed_dv = DecomposedDiscoveryValue(
    representation_novelty_dv=0.82,
    constraint_discovery_dv=0.88,
    mechanistic_depth_dv=0.85,
    alternative_elimination_dv=0.90,
    falsification_resistance_dv=0.89,
)


# Active In-Memory Registries
campaigns_registry: Dict[str, DiscoveryCampaign] = {}

workbenches_registry: Dict[str, DiscoveryWorkbench] = {}

_global_ontology_engine = OntologyPlanEngine()
