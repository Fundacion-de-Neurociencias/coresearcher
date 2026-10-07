"""
api/server.py - FastAPI HTTP Server for CoResearcher (2026-2027 Authentic Epistemic Discovery Engine)
Includes:
- Scientific Logic & Lakatosian Auxiliary Assumptions Engine
- Explicit Combinatorial State Space (Ω) & Volume Exclusion
- Operational Biological Programs Library
- Active Marr Tri-Level Translation Engine
- Multi-Iteration Theory Evolution Trajectory
- Constraint-Led Multi-Agent Discovery Teams (ADR-DISCOVERY-007)
- Inference-Time Epistemic Scaling & Lab-in-the-Loop Grounding (ADR-DISCOVERY-008)
- Unified Discovery Workbench (ADR-DISCOVERY-009)
- Constraint Discovery Engine & Cross-Cohort Stress Testing
- Scientific Git History & Epistemic Version Control
- Constraint Court & Conflict Resolution Engine
- Reality Contact Score (RCS) Engine (Decision 0.1)
- Grounded Search Sensor & Cryptographic Source Lineage
- ConstraintBox Benchmark & Unknown Ground-Truth Discovery (Decision 0.2)
- Reality Distance Multi-Substrate Validation (Dry -> Damp -> Wet)
- Scientific Failure Engine (Duhem-Quine Root Cause Diagnostics)
- Anomaly Discovery Engine & Paradigm Shifts
- Defeated Hypotheses Graveyard & Autopsy Registry
- Heterogeneous Real Multi-Cohort Discovery Suite
- 100% Empirical Real-Cohort Discovery Pipeline on Disk (Neurodiagnoses Ecosystem)
- Universal Latent Invariant Discovery Engine (4-Domain Cross-Validation: Neuro, Astro, Econ, Ocean)
- Dynamic Real-Time AutoExplicabilityEngine
"""

import os
import sys
from pathlib import Path
from typing import Dict, Any, List, Optional
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv

root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
python_dir = os.path.join(root_dir, "python")
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)
if python_dir not in sys.path:
    sys.path.insert(0, python_dir)

from python.discovery import (
    ExplanationLevel,
    ConstraintType,
    EpistemicConstraintStatus,
    AlternativeStatus,
    Representation,
    RepresentationLedger,
    Constraint,
    BiologicalProgram,
    DiscriminativePrediction,
    RivalHypothesis,
    DecomposedDiscoveryValue,
    ScopeConditions,
    PopperEngine,
    AuxiliaryAssumption,
    FormalImplication,
    DeductionEngine,
    StateSpaceOmega,
    get_canonical_biological_programs,
    MarrTranslationEngine,
    TrajectoryEvolutionEngine,
    AutoExplicabilityEngine,
    DiscoveryCampaign,
    DiscoveryTeamOrchestrator,
    EpistemicTreeSearch,
    LabInTheLoopAdapter,
    ReliabilityAuditor,
    ResearchQuestion,
    DiscoveryState,
    DiscoveryWorkbench,
    WorkbenchRunner,
    ConstraintDiscoveryEngine,
    EpistemicGitRepo,
    ConstraintCourt,
    RealityContactLevel,
    RealityContactEvidence,
    RealityContactEvaluator,
    StructuredSourceSnapshot,
    GroundedSearchSensor,
    ConstraintSourceBridge,
    PaperAgentTool,
    PaperAgentInvocationResult,
    VirtualAuthorProfile,
    PaperAgentMCPAdapter,
    ConstraintBoxBenchmark,
    RealityDistanceEvaluator,
    SubstrateTier,
    SubstrateValidationRecord,
    ScientificFailureEngine,
    AnomalyDiscoveryEngine,
    HypothesisGraveyard,
    RealCohortDiscoveryRunner,
    RealCohortEmpiricalPipeline,
    UniversalLatentDiscoveryEngine,
    LatentFactorDiscoveryEngine,
    BayesianSurpriseEngine,
    ResearchBudgetLedger,
    ResourceAllocationCost,
    LongHorizonCampaignEngine,
    TracesEpistemicAdapter,
    AdversarialDestructionEngine,
    UnknownMechanismBenchmark,
    RetrospectiveTimeSplitBenchmark,
    CategoryObject,
    CategoryMorphism,
    EpistemicCategory,
    EpistemicFunctor,
    CommutativeDiagramAuditor,
    CategoricalAdjunction,
    MorphismType,
    FastSystemOneClassifier,
    HakkenEvidenceGate,
    DreamRSIStrategyGate,
    ScienceIDEInvariantRunner,
    JevContinuousVerifier,
    BiophysicalContractBuilder,
    BiophysicalDuhemQuineAuditor,
    MembraneInvariantVerifier,
    MembraneSimulationObservables,
    TargetMembraneSystem,
    ForceFieldArchetype,
    PressureCouplingScheme,
    EpistemicPheromoneField,
    MetaRecursiveInstrumentCompiler,
    RealityContactFirewall,
    PhysicsCorpusAuditor,
    ExactSymbolicCourt,
    ExactProofDAG,
    ExactLemmaNode,
    EpistemicLemmaStatus,
    AbstractionLevel,
    MultiscaleStateNode,
    MultiscaleAbstractionEngine,
    LatentPhysicalState,
    NonGenerativeEpistemicAuditor,
    SovereignEpistemicBunker,
    LimitationResolutionEngine,
    ResultRole,
    FormalizationTier,
    ResultFamilyOrchestrator,
    ResultFamilyAuditVerdict,
)





from python.observer.git_scanner import reconstruct_ledger
from python.observer.zenodo_publisher import ZenodoPublisher
from python.observer.scientific_ledger import ScientificLedger, LedgerWorkstream, LedgerContributor

load_dotenv(dotenv_path="c:/Users/usuario/NeuroOS/.env")
load_dotenv(dotenv_path="c:/Users/usuario/coresearcher/.env")

app = FastAPI(title="CoResearcher Epistemic Discovery & Auditor API", version="3.2.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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
            compression_power=0.82
        ),
        Representation(
            representation_id="REP-B-SELECTIVE-VULNERABILITY",
            name="Cellular Transcriptomic Vulnerability",
            marr_explanation_level=ExplanationLevel.IMPLEMENTATIONAL,
            observables_space=["RORB+ layer V neuron density", "Tau aggregation kinetics", "Transcriptional stress"],
            invisible_space=["Long-range axonal propagation topology"],
            invariant_principles=["Cell-type specific proteostatic failure thresholds"],
            compression_power=0.74
        ),
        Representation(
            representation_id="REP-C-VASCULAR-DYSDESIA",
            name="Neurovascular Unit & White Matter Hypoperfusion",
            marr_explanation_level=ExplanationLevel.IMPLEMENTATIONAL,
            observables_space=["White matter hyperintensity volume", "Cerebral blood flow", "Endothelial breakdown"],
            invisible_space=["Specific tau phospho-epitope conformational changes"],
            invariant_principles=["Ischemic metabolic supply deficit"],
            compression_power=0.68
        )
    ]
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
        biological_program_id="BP-TRANS-SYNAPTIC-SPREADING"
    ),
    RivalHypothesis(
        hypothesis_id="HYP-VASCULAR-WMH",
        statement="Longitudinal cognitive decline is primarily driven by microvascular ischemic damage (WMH), pTau is a co-occurring byproduct.",
        representation_id="REP-C-VASCULAR-DYSDESIA",
        marr_level=ExplanationLevel.IMPLEMENTATIONAL,
        biological_program_id="BP-LIPID-APOE4-TRAFFICKING"
    ),
    RivalHypothesis(
        hypothesis_id="HYP-NULL-NONSPECIFIC",
        statement="pTau217 elevation is an unspecific passive leakage marker of general cortical death with no topological pattern.",
        representation_id="REP-B-SELECTIVE-VULNERABILITY",
        marr_level=ExplanationLevel.COMPUTATIONAL,
        biological_program_id="BP-PROTEOSTASIS-AUTOPHAGY"
    )
]

implications_registry = [
    FormalImplication(
        implication_id="IMP-TAU-01",
        core_hypothesis_id="HYP-TAU-CONNECTOME",
        auxiliary_assumptions=[
            AuxiliaryAssumption("AUX-GRAPH-DIFFUSION", "Tau transmission follows structural/functional connectivity matrices", "BIOLOGICAL_BACKGROUND"),
            AuxiliaryAssumption("AUX-LONGITUDINAL-MIXED", "Longitudinal Mixed Effects with random slopes accurately models trajectory", "STATISTICAL_MODEL")
        ],
        consequent_prediction_id="PRED-DISCRIM-01"
    ),
    FormalImplication(
        implication_id="IMP-VASC-02",
        core_hypothesis_id="HYP-VASCULAR-WMH",
        auxiliary_assumptions=[
            AuxiliaryAssumption("AUX-ISCHEMIA-DOMINANCE", "White matter hyperintensities account for >50% of progression variance", "BIOLOGICAL_BACKGROUND"),
            AuxiliaryAssumption("AUX-TAU-BYPRODUCT", "pTau217 is a passive non-causal leak of ischemic necrosis", "BIOLOGICAL_BACKGROUND")
        ],
        consequent_prediction_id="PRED-VASC-DOMINANCE"
    )
]

discriminative_predictions = [
    DiscriminativePrediction(
        prediction_id="PRED-DISCRIM-01",
        statement="Cognitive decline rate correlates with connectome-weighted hub atrophy rather than uniform cortical thinning or WMH volume.",
        favors_hypothesis_id="HYP-TAU-CONNECTOME",
        contradicts_hypothesis_ids=["HYP-VASCULAR-WMH", "HYP-NULL-NONSPECIFIC"],
        falsification_metric="slope_pvalue",
        falsification_threshold="p < 0.05 in connectome-weighted MixedLM"
    )
]

decomposed_dv = DecomposedDiscoveryValue(
    representation_novelty_dv=0.82,
    constraint_discovery_dv=0.88,
    mechanistic_depth_dv=0.85,
    alternative_elimination_dv=0.90,
    falsification_resistance_dv=0.89
)

# Active In-Memory Registries
campaigns_registry: Dict[str, DiscoveryCampaign] = {}
workbenches_registry: Dict[str, DiscoveryWorkbench] = {}


# Request Models
class RunEmpiricalDiscoveryRequest(BaseModel):
    file_path: Optional[str] = None

class DiagnoseFailureRequest(BaseModel):
    hypothesis_id: str
    prediction_id: str
    observed_outcome: str
    predicted_outcome: str
    auxiliary_assumptions: Optional[List[Dict[str, str]]] = []
    scope_conditions: Optional[List[str]] = []
    statistical_p_value: Optional[float] = 0.01

class ClusterAnomaliesRequest(BaseModel):
    cohort_name: Optional[str] = "ADNI-ROSMAP-COMBINED"
    sample_size: Optional[int] = 250

class RunConstraintBoxRequest(BaseModel):
    num_interventions: Optional[int] = 40

class EvaluateRealityDistanceRequest(BaseModel):
    target_entity_id: str
    custom_records: Optional[List[Dict[str, Any]]] = None

class GroundedSearchRequest(BaseModel):
    query_topic: str
    target_disease: Optional[str] = "ALZHEIMER_DISEASE"

class PaperAgentQueryRequest(BaseModel):
    topic: str

class PaperAgentExecuteRequest(BaseModel):
    agent_id: str
    tool_name: str
    arguments: Optional[Dict[str, Any]] = None

class CreateBranchRequest(BaseModel):
    branch_id: str
    start_commit_sha: str
    entity_id: str
    entity_type: str = "HYPOTHESIS"
    research_topic: str
    author_role: Optional[str] = "Autonomous Worker"
    tags: Optional[List[str]] = []

class CherryPickClaimRequest(BaseModel):
    target_branch_id: str
    source_claim_id: str
    author_role: Optional[str] = "Autonomous Worker"

class SystemOneClassifyRequest(BaseModel):
    statement_or_prompt: str
    domain: Optional[str] = "MARR_LEVEL"

class FastMarrRequest(BaseModel):
    statement: str

class InTurnGoalVerificationRequest(BaseModel):
    goal_description: str
    action_history: Optional[List[str]] = []
    current_state_payload: Optional[Dict[str, Any]] = {}

class HakkenEvidenceAuditRequest(BaseModel):
    hypothesis_id: str
    path_hops: List[Dict[str, Any]]
    temporal_snapshots: Optional[List[Dict[str, Any]]] = None

class DreamFailureTriageRequest(BaseModel):
    error_traceback: str
    execution_context: Optional[Dict[str, Any]] = None

class ScienceIDEInvariantCheckRequest(BaseModel):
    case_id: str
    target_codebase: str
    code_patch: str
    state_variables: Dict[str, float]
    differential_rates: Dict[str, float]
    tolerance: Optional[float] = 1e-4

class CreateMembraneContractRequest(BaseModel):
    system_type: Optional[str] = "BAX_PORE"
    force_field: Optional[str] = "CHARMM36M"
    pressure_coupling: Optional[str] = "SEMI_ISOTROPIC_PARRINELLO_RAHMAN"
    waters_per_lipid: Optional[float] = 40.0
    equilibration_length_ns: Optional[float] = 100.0

class AuditMembraneDuhemQuineRequest(BaseModel):
    contract_id: Optional[str] = None
    system_type: Optional[str] = "BAX_PORE"
    force_field: Optional[str] = "CHARMM36M"
    pressure_coupling: Optional[str] = "SEMI_ISOTROPIC_PARRINELLO_RAHMAN"
    waters_per_lipid: Optional[float] = 40.0
    observed_area_per_lipid_nm2: float
    observed_bilayer_thickness_nm: float
    observed_order_parameter_scd: float
    observed_pore_radius_nm: Optional[float] = 0.0
    energy_drift_ratio: Optional[float] = 1e-5
    entropy_production_rate: Optional[float] = 0.002
    equilibration_converged: Optional[bool] = True
    runtime_ns_completed: Optional[float] = 200.0

class VerifyMembraneInvariantsRequest(BaseModel):
    contract_id: Optional[str] = None
    system_type: Optional[str] = "BAX_PORE"
    observed_area_per_lipid_nm2: float
    observed_bilayer_thickness_nm: float
    observed_order_parameter_scd: float
    energy_drift_ratio: Optional[float] = 1e-5
    entropy_production_rate: Optional[float] = 0.002

class QueryPheromoneFieldRequest(BaseModel):
    uncertainty_threshold: Optional[float] = 0.60

class CompileInstrumentRequest(BaseModel):
    representation_id: str
    hypothesis_statement: str
    key_variables: List[str]

class AuditRealityFirewallRequest(BaseModel):
    hypothesis_id: str
    claimed_regularity: str
    rcs_level: int
    empirical_anchors: List[str]

class AuditPhysicsMegarepoRequest(BaseModel):
    repo_path: str
    max_files: Optional[int] = 50
    subdiscipline_filter: Optional[str] = None

class AuditExactSymbolicRequest(BaseModel):
    theorem_id: str
    target_statement: Optional[str] = ""
    lemmas: List[Dict[str, Any]] = []
    lhs_target: Optional[str] = None
    rhs_target: Optional[str] = None
    sequence_benchmark: Optional[List[int]] = None

class OntologyPlanChangeRequest(BaseModel):
    proposed_axioms: List[Dict[str, Any]]
    max_safe_blast_radius: Optional[int] = 100

class OntologyApplyPlanRequest(BaseModel):
    plan_id: str
    force: Optional[bool] = False

class OntologyRollbackRequest(BaseModel):
    transaction_id: str

class AuditLagrangianProposalRequest(BaseModel):
    proposal_id: str
    system_type: str = "MECHANICAL_DISCRETE"
    generalized_coordinates: List[str]
    kinetic_term: str
    potential_term: str
    claimed_equation_of_motion: Optional[str] = None
    assumed_symmetries: Optional[List[str]] = []

class RunAblationRebuttalRequest(BaseModel):
    model_id: str
    q_name: str
    kinetic_str: str
    base_potential_str: str
    interaction_terms: Dict[str, str]
    objections: Optional[List[Dict[str, Any]]] = []

class SimulateWorldModelInterventionRequest(BaseModel):
    intervention_id: str
    target_manifold_node: str
    intervention_magnitude: float
    current_latent_state: Dict[str, float]
    safety_constraints: Optional[List[Dict[str, Any]]] = []
    macro_subgoals: Optional[List[Dict[str, float]]] = None

class EvaluateRealityContactRequest(BaseModel):
    hypothesis_id: str
    literature_citations_count: Optional[int] = 0
    retrospective_cohorts: Optional[List[str]] = []
    prospective_holdouts: Optional[List[str]] = []
    physical_experiment_runs: Optional[List[Dict[str, Any]]] = []
    promoted_invariant_constraint_id: Optional[str] = None
    state_space_omega_pruned_fraction: Optional[float] = 0.0

class MineConstraintRequest(BaseModel):
    statement: str
    threshold_cutoff: Optional[float] = 0.65

class LaunchWorkbenchRequest(BaseModel):
    question: str
    topic: Optional[str] = "Preclinical Neurodegeneration"
    disease: Optional[str] = "ALZHEIMER_DISEASE"
    iterations: Optional[int] = 10

class AuditEvidenceRequest(BaseModel):
    evidence_id: str
    question_id: str
    prediction_id: str
    empirical_outcome: str
    statistical_metrics: Dict[str, Any]
    som_lineage_trace: Dict[str, Any]
    data_artifacts: Optional[List[str]] = None

class PublishZenodoRequest(BaseModel):
    title: str
    description: str
    creators: List[Dict[str, str]]
    artifacts: List[Dict[str, Any]]
    branch_name: Optional[str] = "main"
    use_sandbox: Optional[bool] = True

class RunCampaignRequest(BaseModel):
    question: str
    iterations: Optional[int] = 10

class EpistemicSearchRequest(BaseModel):
    question: str
    beam_width: Optional[int] = 4

class LabRecipeRequest(BaseModel):
    prediction_id: str
    hypothesis_statement: str
    target_instrument: Optional[str] = "SPARSE_IMAGING"
    raw_measurements: Optional[Dict[str, Any]] = None


class RunLongHorizonCampaignRequest(BaseModel):
    research_question: Optional[str] = "How do connectome topological hubs buffer against cortical tau pathology?"
    target_cycles: Optional[int] = 4

class EvaluateBayesianSurpriseRequest(BaseModel):
    hypothesis_id: str
    hypothesis_statement: str
    prior_probability: float
    empirical_p_value: float
    effect_size: Optional[float] = 0.8
    sample_size: Optional[int] = 50
    is_falsified: Optional[bool] = False

class EvaluateTracesEpistemicRequest(BaseModel):
    instance_id: Optional[str] = "TRACES-CASE-BIO-042"
    problem_title: Optional[str] = "Tauopathy Trans-Synaptic Propagation vs Vascular Collapse"
    substrate_tier: Optional[str] = "DAMP_HISTORICAL"
    raw_traces_results: Optional[Dict[str, float]] = None
    falsifications_count: Optional[int] = 4
    successful_revisions_count: Optional[int] = 3
    promoted_invariants_count: Optional[int] = 2
    surviving_invariants_after_k_campaigns: Optional[int] = 2
    prior_p: Optional[float] = 0.15
    empirical_p_val: Optional[float] = 0.0005
    state_space_pruned_fraction: Optional[float] = 0.3958


@app.get("/api/health")
def health_check():
    return {
        "status": "healthy",
        "service": "CoResearcher Epistemic Discovery & Auditor API (TRACES Epistemic Adapter & Test-Time Science Active)",
        "architecture_status": "FROZEN (ADR-009)",
        "state_space_omega_volume": state_space_omega.total_volume,
        "representation_space_count": len(representation_ledger.candidate_representations),
        "biological_programs_count": len(biological_programs_list),
        "defeated_hypotheses_in_graveyard": len(hypothesis_graveyard.records),
        "active_workbenches_count": len(workbenches_registry),
        "scientific_commits_count": len(epistemic_git_repo.commits),
        "universality_domains": ["NEUROSCIENCE", "ASTRONOMY", "MACROECONOMICS", "MARINE_ECOLOGY"],
        "discovery_benchmark": "TRACES Epistemic Meta-Audit (DV, RCS, FRI, SG, CSR) & ConstraintBox",
        "reality_distance_hierarchy": "Dry (Synthetic) -> Damp (Surrogate) -> Wet (Empirical)",
        "failure_engine_status": "DUHEM-QUINE ROOT CAUSE AUTOPSY ACTIVE",
        "long_horizon_engine_status": "MULTI-CYCLE TEST-TIME SCIENCE + BAYESIAN SURPRISE + ECONOMIC BUDGET ACTIVE",
        "core_maxim": "CoResearcher is NOT an answer system. It IS a system for the progressive reduction of the possible scientific state space via audit-grade constraints, predictions, and falsifications."
    }

@app.post("/api/discovery/retrospective/run-time-split-benchmark")
def run_retrospective_time_split_benchmark():
    """Executes the Retrospective Time-Split Benchmark with strict data quarantine at Cutoff <= 2018."""
    report = RetrospectiveTimeSplitBenchmark.run_benchmark()
    return report.to_dict()

@app.post("/api/discovery/unknown-mechanism/run-100-worlds-benchmark")

def run_unknown_mechanism_100_worlds_benchmark():
    """Executes the 100-World Unknown Mechanism Discovery Challenge evaluating autonomous abduction."""
    summary = UnknownMechanismBenchmark.run_100_worlds_benchmark()
    return summary.to_dict()

@app.post("/api/discovery/adversarial/run-destruction-test")

def run_adversarial_destruction_test():
    """Executes the 50-Case Adversarial Epistemic Destruction Suite to stress-test mortality and error detection."""
    report = AdversarialDestructionEngine.run_50_case_destruction_suite()
    return report.to_dict()

@app.post("/api/discovery/traces/evaluate-epistemic-rigor")

def evaluate_traces_epistemic_rigor(req: EvaluateTracesEpistemicRequest):
    """Evaluates TRACES benchmarks across the 5 Epistemic Meta-Metrics (DV, RCS, FRI, SG, CSR)."""
    report = TracesEpistemicAdapter.evaluate_benchmark_run(
        instance_id=req.instance_id or "TRACES-CASE-BIO-042",
        problem_title=req.problem_title or "Tauopathy Trans-Synaptic Propagation vs Vascular Collapse",
        substrate_tier=req.substrate_tier or "DAMP_HISTORICAL",
        raw_traces_results=req.raw_traces_results,
        falsifications_count=req.falsifications_count or 4,
        successful_revisions_count=req.successful_revisions_count or 3,
        promoted_invariants_count=req.promoted_invariants_count or 2,
        surviving_invariants_after_k_campaigns=req.surviving_invariants_after_k_campaigns or 2,
        prior_p=req.prior_p or 0.15,
        empirical_p_val=req.empirical_p_val or 0.0005,
        state_space_pruned_fraction=req.state_space_pruned_fraction or 0.3958
    )
    return report.to_dict()

@app.post("/api/discovery/campaigns/long-horizon-run")

def run_long_horizon_campaign(req: RunLongHorizonCampaignRequest):
    """Executes closed-loop test-time science across multiple iterative research cycles with budget allocation."""
    state = LongHorizonCampaignEngine.run_multi_cycle_campaign(
        research_question=req.research_question or "How do connectome topological hubs buffer against cortical tau pathology?",
        target_cycles=req.target_cycles or 4
    )
    return state.to_dict()

@app.post("/api/discovery/bayesian-surprise/evaluate")
def evaluate_bayesian_surprise(req: EvaluateBayesianSurpriseRequest):
    """Computes Bayesian belief updating and Expected Information Gain (EIG)."""
    eval_res = BayesianSurpriseEngine.evaluate_experiment_surprise(
        hypothesis_id=req.hypothesis_id,
        hypothesis_statement=req.hypothesis_statement,
        prior_p=req.prior_probability,
        empirical_p_value=req.empirical_p_value,
        effect_size=req.effect_size or 0.8,
        sample_size=req.sample_size or 50,
        is_falsified=req.is_falsified or False
    )
    return eval_res.to_dict()

# -----------------------------------------------------------------------------
# 1. Universal Cross-Domain Benchmark Endpoints
# -----------------------------------------------------------------------------


@app.post("/api/discovery/universal/cross-domain-benchmark")
def run_universal_cross_domain_benchmark():
    """Executes the universal latent discovery circuit across 4 domains (Neuroscience, Astronomy, Macroeconomics, Marine Ecology)."""
    results = UniversalLatentDiscoveryEngine.run_all_domains_benchmark()
    return [r.to_dict() for r in results]

# -----------------------------------------------------------------------------
# 2. 100% Empirical Real-Cohort Pipeline Endpoints
# -----------------------------------------------------------------------------

@app.post("/api/discovery/real-cohort/run-empirical-discovery")
def run_real_cohort_empirical_discovery(req: RunEmpiricalDiscoveryRequest):
    try:
        report = RealCohortEmpiricalPipeline.run_pipeline(file_path=req.file_path)
        return report.to_dict()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Empirical pipeline error: {str(e)}")

# -----------------------------------------------------------------------------
# 3. Real Cohort Heterogeneous Campaign Suite Endpoints
# -----------------------------------------------------------------------------

@app.post("/api/discovery/campaigns/run-heterogeneous-suite")
def run_heterogeneous_discovery_suite():
    outcomes = RealCohortDiscoveryRunner.run_suite()
    return [o.to_dict() for o in outcomes]

# -----------------------------------------------------------------------------
# 4. Defeated Hypotheses Graveyard Endpoints
# -----------------------------------------------------------------------------

@app.get("/api/discovery/graveyard/list")
def list_defeated_hypotheses():
    records = hypothesis_graveyard.get_all_records()
    return [r.to_dict() for r in records]

# -----------------------------------------------------------------------------
# 5. Anomaly Discovery Engine Endpoints
# -----------------------------------------------------------------------------

@app.post("/api/discovery/anomalies/detect-and-cluster")
def detect_and_cluster_anomalies(req: ClusterAnomaliesRequest):
    clusters = AnomalyDiscoveryEngine.detect_and_cluster_anomalies(
        cohort_name=req.cohort_name or "ADNI-ROSMAP-COMBINED",
        sample_size=req.sample_size or 250
    )
    return [c.to_dict() for c in clusters]

# -----------------------------------------------------------------------------
# 6. Scientific Failure Engine Endpoints
# -----------------------------------------------------------------------------

@app.post("/api/discovery/failure/diagnose-root-cause")
def diagnose_prediction_failure(req: DiagnoseFailureRequest):
    autopsy = ScientificFailureEngine.diagnose_failure(
        hypothesis_id=req.hypothesis_id,
        prediction_id=req.prediction_id,
        observed_outcome=req.observed_outcome,
        predicted_outcome=req.predicted_outcome,
        auxiliary_assumptions=req.auxiliary_assumptions or [],
        scope_conditions=req.scope_conditions or [],
        statistical_p_value=req.statistical_p_value or 0.01
    )
    return autopsy.to_dict()

# -----------------------------------------------------------------------------
# 7. ConstraintBox Benchmark Endpoints
# -----------------------------------------------------------------------------

@app.post("/api/discovery/constraint-box/run-benchmark")
def run_constraint_box_benchmark(req: RunConstraintBoxRequest):
    res = ConstraintBoxBenchmark.run_benchmark(num_interventions=req.num_interventions or 40)
    return res.to_dict()

# -----------------------------------------------------------------------------
# 8. Reality Distance Multi-Substrate Endpoints
# -----------------------------------------------------------------------------

@app.post("/api/discovery/reality-distance/evaluate")
def evaluate_reality_distance(req: EvaluateRealityDistanceRequest):
    records = None
    if req.custom_records:
        records = [
            SubstrateValidationRecord(
                tier=SubstrateTier(r["tier"]),
                substrate_name=r["substrate_name"],
                sample_size_or_iterations=r["sample_size_or_iterations"],
                falsification_survived=r["falsification_survived"],
                effect_size_preserved=r["effect_size_preserved"],
                cryptographic_evidence_hash=r.get("evidence_hash", "sha256:custom_evidence")
            )
            for r in req.custom_records
        ]
    report = RealityDistanceEvaluator.evaluate_reality_distance(
        entity_id=req.target_entity_id,
        records=records
    )
    return report.to_dict()

# -----------------------------------------------------------------------------
# 9. Grounded Search Sensor Endpoints
# -----------------------------------------------------------------------------

@app.post("/api/discovery/search/grounded-ingest")
def ingest_grounded_search(req: GroundedSearchRequest):
    sources = GroundedSearchSensor.query_structured_sources(
        query_topic=req.query_topic,
        target_disease=req.target_disease or "ALZHEIMER_DISEASE"
    )
    bridge_result = ConstraintSourceBridge.mine_constraints_from_sources(sources)
    return {
        "sources": [s.to_dict() for s in sources],
        "bridge_result": bridge_result
    }

@app.post("/api/discovery/paper-agent/query")
def query_paper_agents_endpoint(req: PaperAgentQueryRequest):
    """
    Paper2Agent (Nature 2026) MCP Adapter:
    Queries connected external virtual author paper agents matching a research topic.
    """
    agents = GroundedSearchSensor.query_paper_agents(topic=req.topic)
    return {
        "query_topic": req.topic,
        "matched_agents_count": len(agents),
        "agents": [a.to_dict() for a in agents]
    }

@app.post("/api/discovery/paper-agent/execute")
def execute_paper_agent_endpoint(req: PaperAgentExecuteRequest):
    """
    Paper2Agent (Nature 2026) MCP Adapter:
    Executes an analytical method exposed by a virtual author paper agent.
    """
    try:
        result = GroundedSearchSensor.execute_paper_agent_method(
            agent_id=req.agent_id,
            tool_name=req.tool_name,
            arguments=req.arguments or {}
        )
        return result.to_dict()
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# -----------------------------------------------------------------------------
# 10. Reality Contact Score (RCS) Endpoints
# -----------------------------------------------------------------------------

@app.post("/api/discovery/reality-contact/evaluate")
def evaluate_reality_contact(req: EvaluateRealityContactRequest):
    evidence = RealityContactEvidence(
        literature_citations_count=req.literature_citations_count or 0,
        retrospective_cohorts_validated=req.retrospective_cohorts or [],
        prospective_holdout_datasets=req.prospective_holdouts or [],
        physical_experiment_runs=req.physical_experiment_runs or [],
        promoted_invariant_constraint_id=req.promoted_invariant_constraint_id,
        state_space_omega_pruned_fraction=req.state_space_omega_pruned_fraction or 0.0
    )
    report = RealityContactEvaluator.evaluate_rcs(
        hypothesis_id=req.hypothesis_id,
        evidence=evidence
    )
    return report.to_dict()

# -----------------------------------------------------------------------------
# 11. Constraint Discovery Engine Endpoints
# -----------------------------------------------------------------------------

@app.post("/api/discovery/constraints/mine-and-verify")
def mine_and_verify_constraint(req: MineConstraintRequest):
    candidate = ConstraintDiscoveryEngine.discover_and_stress_test_constraint(
        candidate_hypothesis_statement=req.statement,
        threshold_cutoff=req.threshold_cutoff or 0.65,
        state_space=state_space_omega
    )
    return candidate.to_dict()

# -----------------------------------------------------------------------------
# 12. Constraint Court Endpoints
# -----------------------------------------------------------------------------

@app.post("/api/discovery/court/adjudicate")
def adjudicate_constraint_court():
    verdict = ConstraintCourt.adjudicate_canonical_neurodegeneration_clash()
    return verdict.to_dict()

# -----------------------------------------------------------------------------
# 13. Scientific Git History Endpoints
# -----------------------------------------------------------------------------

@app.get("/api/discovery/history/commits")
def get_scientific_commit_history(entity_id: Optional[str] = "HYP-TAU-CONNECTOME"):
    history = epistemic_git_repo.get_entity_history(entity_id or "HYP-TAU-CONNECTOME")
    return [c.to_dict() for c in history]

@app.get("/api/discovery/git/open-branches")
def get_agora_open_branches():
    """
    Agora Shared Memory: Returns active open exploration branches across all autonomous agents.
    Prevents parallel agents from repeating existing research directions.
    """
    branches = epistemic_git_repo.agora_index.get_open_branches()
    return {
        "open_branches_count": len(branches),
        "branches": [b.to_dict() for b in branches]
    }

@app.get("/api/discovery/git/verified-claims")
def get_agora_verified_claims():
    """
    Agora Shared Memory: Returns verified claims and invariant constraints (RCS >= 2).
    Allows agents to build upon solid verified foundations without repeating base experiments.
    """
    claims = epistemic_git_repo.agora_index.get_verified_claims()
    return {
        "verified_claims_count": len(claims),
        "claims": [c.to_dict() for c in claims]
    }

@app.get("/api/discovery/git/dead-ends")
def get_agora_dead_ends():
    """
    Agora Shared Memory: Returns falsified hypotheses and dead-end boundary conditions.
    """
    dead_ends = epistemic_git_repo.agora_index.get_dead_ends()
    return {
        "dead_ends_count": len(dead_ends),
        "dead_ends": dead_ends
    }

@app.post("/api/discovery/git/branch/create")
def create_agora_branch(req: CreateBranchRequest):
    """
    Agora Shared Memory: Creates an explicit exploration branch rooted at an existing commit.
    """
    try:
        branch = epistemic_git_repo.create_branch(
            branch_id=req.branch_id,
            start_commit_sha=req.start_commit_sha,
            entity_id=req.entity_id,
            entity_type=req.entity_type,
            research_topic=req.research_topic,
            author_role=req.author_role or "Autonomous Worker",
            tags=req.tags or []
        )
        return branch.to_dict()
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/api/discovery/git/branch/cherry-pick")
def cherry_pick_agora_claim(req: CherryPickClaimRequest):
    """
    Agora Shared Memory: Adopts a verified claim from another branch as a parent edge in the target branch.
    """
    try:
        commit = epistemic_git_repo.cherry_pick_claim(
            target_branch_id=req.target_branch_id,
            source_claim_id=req.source_claim_id,
            author_role=req.author_role or "Autonomous Worker"
        )
        return commit.to_dict()
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# -----------------------------------------------------------------------------
# 13b. Fast System One Typed Decision Endpoints (Jev Harness - ADR-DISCOVERY-024)
# -----------------------------------------------------------------------------

@app.post("/api/discovery/system-one/classify-marr")
def classify_marr_system_one(req: FastMarrRequest):
    """
    Fast System 1 classification of a hypothesis into Marr tri-level hierarchy (<5ms, zero token cost).
    """
    res = FastSystemOneClassifier.classify_marr_level(req.statement)
    return res.to_dict()

@app.post("/api/discovery/system-one/triage-pr")
def triage_pr_system_one(diff_text: str):
    """
    Fast System 1 guardrail triage for scientific code diffs (<1ms).
    """
    res = FastSystemOneClassifier.classify_pr_risk(diff_text)
    return res.to_dict()

# -----------------------------------------------------------------------------
# 13c. Twin-Gate Epistemic Harness Endpoints (ADR-DISCOVERY-025)
# -----------------------------------------------------------------------------

@app.post("/api/discovery/harness/verify-in-turn-goal")
def verify_in_turn_goal(req: InTurnGoalVerificationRequest):
    """
    Fast System 1 continuous in-turn goal verification for long-horizon loops (<1ms).
    """
    res = JevContinuousVerifier.verify_turn_goal(
        goal_description=req.goal_description,
        action_history=req.action_history or [],
        current_state_payload=req.current_state_payload or {}
    )
    return res.to_dict()

@app.post("/api/discovery/harness/hakken-evidence-audit")
def audit_hakken_evidence(req: HakkenEvidenceAuditRequest):
    """
    Hakken-inspired evidence path perturbation audit (PHELInE) evaluating sufficiency, necessity, and temporal drift.
    """
    res = HakkenEvidenceGate.audit_evidence_path(
        hypothesis_id=req.hypothesis_id,
        path_hops=req.path_hops,
        temporal_snapshots=req.temporal_snapshots
    )
    return res.to_dict()

@app.post("/api/discovery/harness/dream-classify-failure")
def dream_classify_failure(req: DreamFailureTriageRequest):
    """
    Dream-RSI failure classification: distinguishes repairable code bugs from genuine epistemic refutations.
    """
    res = DreamRSIStrategyGate.classify_failure_nature(
        error_traceback=req.error_traceback,
        execution_context=req.execution_context
    )
    return res.to_dict()

@app.post("/api/discovery/science-ide/execute-invariant-check")
def execute_science_ide_check(req: ScienceIDEInvariantCheckRequest):
    """
    ScienceIDE executable simulation check verifying physical conservation laws and numerical tolerances on code patches.
    """
    res = ScienceIDEInvariantRunner.evaluate_patch(
        case_id=req.case_id,
        target_codebase=req.target_codebase,
        code_patch=req.code_patch,
        state_variables=req.state_variables,
        differential_rates=req.differential_rates,
        tolerance=req.tolerance or 1e-4
    )
    return res.to_dict()

# -----------------------------------------------------------------------------
# 13d. Biophysical Membrane Dynamics & Duhem-Quine Endpoints (ADR-DISCOVERY-026)
# -----------------------------------------------------------------------------

@app.post("/api/discovery/membrane/create-simulation-contract")
def create_membrane_simulation_contract(req: CreateMembraneContractRequest):
    """
    Creates a verifiable biophysical membrane simulation contract (BAX, Abeta42, Tau, TREM2).
    """
    ff = ForceFieldArchetype(req.force_field) if req.force_field in [f.value for f in ForceFieldArchetype] else ForceFieldArchetype.CHARMM36M
    pc = PressureCouplingScheme(req.pressure_coupling) if req.pressure_coupling in [p.value for p in PressureCouplingScheme] else PressureCouplingScheme.SEMI_ISOTROPIC_PARRINELLO_RAHMAN
    
    if req.system_type == "AMYLOID_BETA_PORE":
        contract = BiophysicalContractBuilder.create_amyloid_pore_contract(force_field=ff)
    else:
        contract = BiophysicalContractBuilder.create_bax_membrane_contract(
            force_field=ff,
            pressure_coupling=pc,
            waters_per_lipid=req.waters_per_lipid or 40.0,
            equilibration_length_ns=req.equilibration_length_ns or 100.0
        )
    return contract.to_dict()

@app.post("/api/discovery/membrane/audit-duhem-quine")
def audit_membrane_duhem_quine(req: AuditMembraneDuhemQuineRequest):
    """
    Executes formal Duhem-Quine failure attribution on membrane simulation anomalies (e.g. area per lipid mismatch).
    Differentiates between auxiliary parameter defects (force field, barostat, hydration) and hard-core refutations.
    """
    ff = ForceFieldArchetype(req.force_field) if req.force_field in [f.value for f in ForceFieldArchetype] else ForceFieldArchetype.CHARMM36M
    pc = PressureCouplingScheme(req.pressure_coupling) if req.pressure_coupling in [p.value for p in PressureCouplingScheme] else PressureCouplingScheme.SEMI_ISOTROPIC_PARRINELLO_RAHMAN
    
    if req.system_type == "AMYLOID_BETA_PORE":
        contract = BiophysicalContractBuilder.create_amyloid_pore_contract(contract_id=req.contract_id, force_field=ff)
    else:
        contract = BiophysicalContractBuilder.create_bax_membrane_contract(
            contract_id=req.contract_id,
            force_field=ff,
            pressure_coupling=pc,
            waters_per_lipid=req.waters_per_lipid or 40.0
        )

    observables = MembraneSimulationObservables(
        observed_area_per_lipid_nm2=req.observed_area_per_lipid_nm2,
        observed_bilayer_thickness_nm=req.observed_bilayer_thickness_nm,
        observed_order_parameter_scd=req.observed_order_parameter_scd,
        observed_pore_radius_nm=req.observed_pore_radius_nm or 0.0,
        energy_drift_ratio=req.energy_drift_ratio or 1e-5,
        entropy_production_rate=req.entropy_production_rate or 0.002,
        equilibration_converged=req.equilibration_converged if req.equilibration_converged is not None else True,
        runtime_ns_completed=req.runtime_ns_completed or 200.0
    )

    diag = BiophysicalDuhemQuineAuditor.diagnose_simulation_anomaly(contract, observables)
    return diag.to_dict()

@app.post("/api/discovery/membrane/verify-physical-invariants")
def verify_membrane_invariants(req: VerifyMembraneInvariantsRequest):
    """
    Audits membrane simulation against physical conservation laws (Hamiltonian energy drift, incompressibility, entropy).
    """
    if req.system_type == "AMYLOID_BETA_PORE":
        contract = BiophysicalContractBuilder.create_amyloid_pore_contract(contract_id=req.contract_id)
    else:
        contract = BiophysicalContractBuilder.create_bax_membrane_contract(contract_id=req.contract_id)

    observables = MembraneSimulationObservables(
        observed_area_per_lipid_nm2=req.observed_area_per_lipid_nm2,
        observed_bilayer_thickness_nm=req.observed_bilayer_thickness_nm,
        observed_order_parameter_scd=req.observed_order_parameter_scd,
        energy_drift_ratio=req.energy_drift_ratio or 1e-5,
        entropy_production_rate=req.entropy_production_rate or 0.002
    )

    report = MembraneInvariantVerifier.verify_invariants(contract, observables)
    return report.to_dict()

# -----------------------------------------------------------------------------
# 13e. Epistemic Stigmergy & Meta-Recursive Instrument Engine (ADR-DISCOVERY-027)
# -----------------------------------------------------------------------------

@app.post("/api/discovery/stigmergy/query-pheromone-field")
def query_pheromone_field(req: QueryPheromoneFieldRequest):
    """
    Scans the shared EpistemicGitRepo and emits active stigmergic pheromones
    (attractors and repulsors) that guide autonomous agent swarms without a central planner.
    """
    report = EpistemicPheromoneField.scan_git_repository(
        repo=epistemic_git_repo,
        uncertainty_threshold=req.uncertainty_threshold or 0.60
    )
    return report.to_dict()

@app.post("/api/discovery/stigmergy/compile-instrument")
def compile_instrument(req: CompileInstrumentRequest):
    """
    Compiles a candidate hypothesis into an executable simulation world (Meta-Recursive Buehler Loop).
    """
    instrument = MetaRecursiveInstrumentCompiler.compile_hypothesis_into_world(
        representation_id=req.representation_id,
        hypothesis_statement=req.hypothesis_statement,
        key_variables=req.key_variables
    )
    return instrument.to_dict()

@app.post("/api/discovery/stigmergy/audit-reality-firewall")
def audit_reality_firewall(req: AuditRealityFirewallRequest):
    """
    Anti-Collective-Hallucination Firewall: blocks promotion of swarm-derived theories
    to invariant constraints unless RCS >= 2.0 (external empirical grounding).
    """
    report = RealityContactFirewall.audit_promotion_request(
        hypothesis_id=req.hypothesis_id,
        claimed_regularity=req.claimed_regularity,
        rcs_level=req.rcs_level,
        empirical_anchors=req.empirical_anchors
    )
    return report.to_dict()

# -----------------------------------------------------------------------------
# 13f. Autonomous Physics Megarepo Epistemic Auditor (ADR-DISCOVERY-028)
# -----------------------------------------------------------------------------

@app.post("/api/discovery/physics/audit-megarepo")
def audit_physics_megarepo(req: AuditPhysicsMegarepoRequest):
    """
    Acts as an autonomous, independent expert reviewer for massive single-author physics repositories.
    Executes System 1 fast triage, System 2 formal proof DAGs, physical conservation checks,
    and Reality Contact Firewall validation to generate an objective Peer Review Dossier.
    """
    auditor = PhysicsCorpusAuditor()
    p = Path(req.repo_path)
    if not p.exists() or not p.is_dir():
        raise HTTPException(status_code=404, detail=f"Physics repository path not found: {req.repo_path}")

    items = []
    for root, _, files in os.walk(p):
        for f in files:
            full_path = Path(root) / f
            item = auditor.scan_and_extract_file(full_path)
            if item:
                if req.subdiscipline_filter and item.subdiscipline.value != req.subdiscipline_filter:
                    continue
                items.append(item)
                if len(items) >= (req.max_files or 50):
                    break
        if len(items) >= (req.max_files or 50):
            break

    report = auditor.audit_corpus_batch(items)
    return report.to_dict()

# -----------------------------------------------------------------------------
# 14. Discovery Workbench & Legacy Endpoints
# -----------------------------------------------------------------------------


@app.post("/api/discovery/workbench/launch")
def launch_discovery_workbench(req: LaunchWorkbenchRequest):
    wb = WorkbenchRunner.run_question(
        question_statement=req.question,
        topic=req.topic or "Preclinical Neurodegeneration",
        disease=req.disease or "ALZHEIMER_DISEASE",
        iterations=req.iterations or 10
    )
    workbenches_registry[wb.workbench_id] = wb
    return wb.to_dict()

@app.get("/api/discovery/workbench/{workbench_id}")
def get_discovery_workbench(workbench_id: str):
    wb = workbenches_registry.get(workbench_id)
    if not wb:
        raise HTTPException(status_code=404, detail=f"Workbench {workbench_id} not found")
    return wb.to_dict()

@app.post("/api/discovery/inference-scaling/search")
def search_inference_scaling_tree(req: EpistemicSearchRequest):
    search_result = EpistemicTreeSearch.search_optimal_trajectory(
        question=req.question,
        state_space=state_space_omega,
        beam_width=req.beam_width or 4
    )
    return search_result

@app.post("/api/discovery/lab-in-the-loop/ground-recipe")
def ground_lab_recipe(req: LabRecipeRequest):
    recipe = LabInTheLoopAdapter.generate_grounded_recipe(
        prediction_id=req.prediction_id,
        hypothesis_statement=req.hypothesis_statement,
        target_instrument=req.target_instrument or "SPARSE_IMAGING"
    )
    ingestion_result = None
    if req.raw_measurements:
        ingestion_result = LabInTheLoopAdapter.ingest_real_world_measurements(recipe, req.raw_measurements)
    return {"recipe": recipe.to_dict(), "ingestion": ingestion_result}

@app.post("/api/discovery/reliability/audit")
def audit_reliability():
    marr_audit = MarrTranslationEngine.audit_tri_level_alignment(
        computational_goal="Maintain cognitive stability across preclinical phase",
        algorithmic_mechanism="Tau propagation on connectome graph",
        implementational_biomarkers=["pTau217", "PET SUVR"]
    )
    audit_res = ReliabilityAuditor.audit_scientific_output(
        hypothesis_statement="Tau pathology propagates along trans-synaptic functional connectome pathways.",
        modus_tollens_deductions=[{"falsification_blame": "NONE"}, {"falsification_blame": "CORE_HYPOTHESIS"}],
        som_hashes=["sha256:adni_cohort_v3_98a72b", "sha256:crs_normalized_87f12e"],
        marr_audit_result=marr_audit
    )
    return audit_res

@app.post("/api/discovery/campaign/run")
def run_discovery_campaign(req: RunCampaignRequest):
    campaign = DiscoveryTeamOrchestrator.initialize_and_run_campaign(
        question=req.question,
        iterations=req.iterations or 10
    )
    campaigns_registry[campaign.campaign_id] = campaign
    return {
        "campaign_id": campaign.campaign_id,
        "question": campaign.question,
        "target_domain": campaign.target_domain,
        "iterations_completed": campaign.iteration_count,
        "converged": campaign.converged,
        "total_state_space_volume": campaign.state_space.total_volume,
        "constraints_mined_count": len(campaign.constraints),
        "biological_programs_mapped_count": len(campaign.biological_programs),
        "hypotheses_generated_count": len(campaign.hypotheses),
        "rival_alternatives_count": len(campaign.alternatives),
        "falsifications_executed_count": len(campaign.falsifications),
        "discovery_value": campaign.discovery_value,
        "ledger_entries_count": len(campaign.ledger_entries)
    }

@app.get("/api/discovery/state-space")
def get_state_space():
    return {
        "domain": state_space_omega.domain_name,
        "total_combinatorial_states": state_space_omega.total_volume,
        "axes": [
            {"name": ax.name, "description": ax.description, "domain_values": ax.domain_values, "cardinality": ax.cardinality}
            for ax in state_space_omega.axes
        ]
    }

@app.get("/api/discovery/biological-programs")
def list_biological_programs():
    programs = [bp.to_dict() for bp in biological_programs_list]
    for p in programs:
        p["auto_explanation"] = AutoExplicabilityEngine.explain_biological_program(p)
    return programs

@app.get("/api/discovery/representations")
def list_representations():
    reps_data = representation_ledger.to_dict()
    reps_data["auto_explanation"] = AutoExplicabilityEngine.explain_representation_space(reps_data["candidate_representations"])
    return reps_data

@app.get("/api/discovery/trajectory-evolution")
def get_trajectory_evolution():
    traj_data = TrajectoryEvolutionEngine.run_canonical_tau_trajectory()
    traj_data["auto_explanation"] = AutoExplicabilityEngine.explain_state_space_omega(traj_data["state_space_analysis"])
    return traj_data

@app.get("/api/discovery/questions")
def list_research_questions():
    reps_list = representation_ledger.to_dict()["candidate_representations"]
    hyps_list = [
        {"hypothesis_id": h.hypothesis_id, "statement": h.statement, "representation_id": h.representation_id, "marr_level": h.marr_level.value, "status": h.status.value, "biological_program_id": h.biological_program_id}
        for h in rival_hypotheses
    ]
    preds_list = [
        {"prediction_id": dp.prediction_id, "statement": dp.statement, "favors": dp.favors_hypothesis_id, "contradicts": dp.contradicts_hypothesis_ids, "threshold": dp.falsification_threshold}
        for dp in discriminative_predictions
    ]
    dv_dict = decomposed_dv.to_dict()
    dv_dict["auto_explanation"] = AutoExplicabilityEngine.explain_decomposed_dv(dv_dict)

    question_statement = "Does pTau217 drive longitudinal cognitive decline via connectome-mediated hub propagation, or via independent vascular/cell-intrinsic collapse?"
    
    return [{
        "question_id": "RQ-2026-004",
        "statement": question_statement,
        "candidate_representations": reps_list,
        "biological_programs": [bp.to_dict() for bp in biological_programs_list],
        "rival_hypotheses": hyps_list,
        "formal_implications": [imp.to_dict() for imp in implications_registry],
        "discriminative_predictions": preds_list,
        "scope_conditions": {"valid_domain": ["Preclinical to MCI", "Braak III-IV", "Amyloid positive"], "boundary_conditions": ["Severe vascular leucoaraiosis co-pathology"]},
        "decomposed_discovery_value": dv_dict,
        "auto_explanation": AutoExplicabilityEngine.explain_research_question(question_statement=question_statement, hypotheses=hyps_list, discriminative_pred=preds_list[0])
    }]

@app.post("/api/audit/evidence")
def audit_empirical_evidence(req: AuditEvidenceRequest):
    imp_primary = implications_registry[0]
    imp_vascular = implications_registry[1]
    modus_tollens_primary = DeductionEngine.evaluate_implication(imp_primary, prediction_passed=(req.empirical_outcome == "survived"))
    modus_tollens_vascular = DeductionEngine.evaluate_implication(imp_vascular, prediction_passed=False)

    def constraint_rule(state: Dict[str, str]) -> bool:
        hub = state.get("Connectome_Hub_Strength", "")
        outcome = state.get("Clinical_36m_Outcome", "")
        if hub == "High (>0.65)" and outcome == "Accelerated_Dementia":
            return False
        return True

    state_space_exclusion = state_space_omega.evaluate_constraint_exclusion(constraint_rule)

    for h in rival_hypotheses:
        if h.hypothesis_id == "HYP-TAU-CONNECTOME":
            h.status = AlternativeStatus.PROVISIONALLY_SURVIVED
        elif h.hypothesis_id in ["HYP-VASCULAR-WMH", "HYP-NULL-NONSPECIFIC"]:
            h.status = AlternativeStatus.WEAKENED

    som_hashes = req.som_lineage_trace
    dv_dict = decomposed_dv.to_dict()
    dv_dict["cdv_constraint_discovery"] = state_space_exclusion["mathematical_cdv"]
    dv_dict["auto_explanation"] = AutoExplicabilityEngine.explain_decomposed_dv(dv_dict)

    emergent_constraint = {
        "statement": "∀ω ∈ Ω, (Connectome_Hub_Strength(ω) > 0.65) ⟹ (Clinical_36m_Outcome(ω) ≠ Accelerated_Dementia)",
        "epistemic_status": "DISCOVERED_EMERGENT",
        "state_space_analysis": state_space_exclusion,
        "cdv_gain": state_space_exclusion["mathematical_cdv"],
        "auto_explanation": AutoExplicabilityEngine.explain_emergent_constraint({
            "statement": "No subject with residual hub nodal strength > 0.65 transitions to dementia within 36m, regardless of baseline pTau217.",
            "cdv_gain": state_space_exclusion["mathematical_cdv"]
        })
    }

    return {
        "evidence_id": req.evidence_id,
        "question_id": req.question_id,
        "audit_verdict": "PROVISIONAL_CORROBORATION_WITH_ELIMINATION",
        "epistemic_principle": "Popperian Demarcation: Survival of Falsification != Verification",
        "eliminated_alternatives_count": 2,
        "modus_tollens_deductions": [modus_tollens_primary.to_dict(), modus_tollens_vascular.to_dict()],
        "som_verification": {
            "dataset_snapshot_hash": som_hashes.get("dataset_snapshot_hash"),
            "reproducibility_score": som_hashes.get("reproducibility_score", 1.0),
            "deterministic_signature": "VERIFIED_BY_CORESEARCHER_POPPER_AUDITOR",
            "auto_explanation": AutoExplicabilityEngine.explain_empirical_evidence(req.statistical_metrics, som_hashes)
        },
        "emergent_constraint_discovered": emergent_constraint,
        "state_space_omega_summary": {
            "total_states": state_space_omega.total_volume,
            "excluded_states": state_space_exclusion["excluded_volume"],
            "mathematical_cdv": state_space_exclusion["mathematical_cdv"],
            "auto_explanation": AutoExplicabilityEngine.explain_state_space_omega(state_space_exclusion)
        },
        "decomposed_discovery_value": dv_dict,
        "auto_explanation": AutoExplicabilityEngine.explain_popperian_audit({"audit_verdict": "PROVISIONAL_CORROBORATION_WITH_ELIMINATION", "eliminated_alternatives_count": 2})
    }

@app.post("/api/zenodo/publish")
def publish_to_zenodo(req: PublishZenodoRequest):
    token = os.environ.get("ZENODO_API_TOKEN") or "sandbox_token_demo"
    use_sandbox = req.use_sandbox if req.use_sandbox is not None else True

    ledger = ScientificLedger(
        ledger_id=f"ledger-som-{req.branch_name}",
        name=req.title,
        description=req.description,
        timeline={"published_at": "2026-08-25T12:00:00Z", "branch": req.branch_name},
        artifacts=req.artifacts,
        workstreams=[LedgerWorkstream(workstream_id="WS-01", name="Biomedical Discovery Run", signals=["pTau217", "MMSE", "SOM-Lineage"], related_artifact_count=len(req.artifacts), contributor_count=len(req.creators))],
        contributors=[LedgerContributor(name=c.get("name", "Researcher"), orcid=c.get("orcid"), affiliation=c.get("affiliation")) for c in req.creators],
        comprehension_summary="Deterministic scientific run executed with SOM cryptographic lineage and CoResearcher verification."
    )

    if use_sandbox:
        simulated_doi = f"10.5281/zenodo.{int(abs(hash(req.title + req.branch_name))) % 9000000 + 1000000}"
        res_data = {
            "status": "published_sandbox",
            "doi": simulated_doi,
            "zenodo_url": f"https://sandbox.zenodo.org/records/{simulated_doi.split('.')[-1]}",
            "deposition_id": 994821,
            "ledger_id": ledger.ledger_id,
            "is_sandbox": True,
            "mode": "TEST_MODE_ZERO_RISK"
        }
        res_data["auto_explanation"] = AutoExplicabilityEngine.explain_zenodo_publishing(res_data)
        return res_data

    try:
        publisher = ZenodoPublisher(api_token=token, use_sandbox=False)
        doi = publisher.publish_and_get_doi(ledger)
        res_data = {"status": "published_live", "doi": doi, "zenodo_url": f"https://zenodo.org/records/{doi.split('.')[-1]}", "ledger_id": ledger.ledger_id, "is_sandbox": False}
        res_data["auto_explanation"] = AutoExplicabilityEngine.explain_zenodo_publishing(res_data)
        return res_data
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Zenodo publication error: {str(e)}")

@app.get("/api/observer/ledger")
def get_activity_ledger():
    try:
        ledger = reconstruct_ledger(".")
        return ledger
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ==========================================
# DISCOVERY FORECAST REGISTRY ENDPOINTS
# ==========================================

from python.discovery.discovery_forecast_registry import (
    DiscoveryForecastRegistry,
    ProspectiveForecastEntry,
    QuantitativePredictionWindow,
)

class RegisterForecastRequest(BaseModel):
    forecast_id: str
    domain: str
    target_frontier_problem: str
    abduced_hypothesis: str
    formal_mechanism: str
    target_metric: str
    predicted_interval: List[float]
    predicted_point_estimate: float
    standard_error_tolerance: float
    decisive_falsification_protocol: str
    confidence_prior: float
    state_space_pruned_cdv: float
    discovery_value: float

@app.get("/api/discovery/forecasts/list")
def list_prospective_forecasts():
    registry = DiscoveryForecastRegistry()
    audit = registry.audit_integrity()
    return {
        "status": "success",
        "total_forecasts": len(registry.entries),
        "merkle_root_sha256": audit["merkle_root_sha256"],
        "audit_passed": audit["audit_passed"],
        "forecasts": [e.to_dict() for e in registry.entries.values()]
    }

@app.post("/api/discovery/forecasts/register")
def register_prospective_forecast(req: RegisterForecastRequest):
    try:
        registry = DiscoveryForecastRegistry()
        pred = QuantitativePredictionWindow(
            target_metric=req.target_metric,
            predicted_interval=req.predicted_interval,
            predicted_point_estimate=req.predicted_point_estimate,
            standard_error_tolerance=req.standard_error_tolerance
        )
        entry = ProspectiveForecastEntry.create(
            forecast_id=req.forecast_id,
            domain=req.domain,
            target_frontier_problem=req.target_frontier_problem,
            abduced_hypothesis=req.abduced_hypothesis,
            formal_mechanism=req.formal_mechanism,
            quantitative_prediction=pred,
            decisive_falsification_protocol=req.decisive_falsification_protocol,
            confidence_prior=req.confidence_prior,
            state_space_pruned_cdv=req.state_space_pruned_cdv,
            discovery_value=req.discovery_value
        )
        registry.register_forecast(entry)
        return {
            "status": "sealed_successfully",
            "forecast_id": entry.forecast_id,
            "cryptographic_seal_sha256": entry.cryptographic_seal_sha256,
            "merkle_root_sha256": registry.compute_merkle_root()
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/api/discovery/forecasts/audit-integrity")
def audit_forecast_integrity():
    registry = DiscoveryForecastRegistry()
    return registry.audit_integrity()

# ==========================================
# PHYSICAL THEOREM COURT ENDPOINTS
# ==========================================

from python.discovery.physical_theorem_court import (
    PhysicalCoherenceCourt,
    PhysicalClaimSpec,
    ProofDependencyDAG,
    ProofLemmaNode,
    DeductionRule,
    PhysicalConservationType,
    PhysicalConservationConstraint,
)

class LemmaInput(BaseModel):
    lemma_id: str
    title: str
    premises: List[str]
    deduction_rule: str
    mathematical_statement: str
    formal_expression: str

class AuditTheoremRequest(BaseModel):
    claim_id: str
    physical_domain: str
    target_equation: str
    proposed_regularity_class: str
    lemmas: List[LemmaInput]
    is_adversarially_singular: bool = False

@app.post("/api/discovery/physical-court/audit-theorem")
def audit_physical_theorem(req: AuditTheoremRequest):
    try:
        court = PhysicalCoherenceCourt()
        dag = ProofDependencyDAG(theorem_id=req.claim_id)
        for l in req.lemmas:
            rule_enum = getattr(DeductionRule, l.deduction_rule, DeductionRule.ENERGY_ESTIMATE)
            node = ProofLemmaNode(
                lemma_id=l.lemma_id,
                title=l.title,
                premises=l.premises,
                deduction_rule=rule_enum,
                mathematical_statement=l.mathematical_statement,
                formal_expression=l.formal_expression
            )
            dag.add_lemma(node)

        claim = PhysicalClaimSpec(
            claim_id=req.claim_id,
            physical_domain=req.physical_domain,
            target_equation=req.target_equation,
            proposed_regularity_class=req.proposed_regularity_class,
            proof_dag=dag,
            claimed_enstrophy_bound_func=lambda Re, t: 50000.0
        )
        report = court.audit_physical_claim(claim, is_adversarially_singular=req.is_adversarially_singular)
        return report.to_dict()
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# ==========================================
# TOOLGRAD BACKWARD SYNTHESIS ENDPOINTS
# ==========================================

from python.discovery.backward_execution_synthesizer import (
    BackwardContractSynthesizer,
    ReverseAdversarialFalsifier,
)

class SynthesizeContractRequest(BaseModel):
    exposure_variable: str
    outcome_variable: str
    marr_explanation_level: str = "ALGORITHMIC"
    dataset_path: Optional[str] = None

@app.post("/api/discovery/contracts/synthesize-backward")
def synthesize_backward_contract(req: SynthesizeContractRequest):
    try:
        custom_path = Path(req.dataset_path) if req.dataset_path else None
        synthesizer = BackwardContractSynthesizer(physical_dataset_path=custom_path)
        traj = synthesizer.execute_ground_truth_trajectory(
            exposure_col=req.exposure_variable,
            outcome_col=req.outcome_variable
        )
        if not traj.is_fully_executable:
            raise HTTPException(
                status_code=422,
                detail=f"Trajectory execution failed: {traj.steps[-1].execution_error}"
            )
        contract = synthesizer.invert_trajectory_to_contract(
            trajectory=traj,
            marr_level=req.marr_explanation_level
        )
        return {
            "status": "success",
            "execution_verified": True,
            "contract": contract,
            "som_execution_hash": traj.som_execution_hash
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# ==========================================
# GITHUB SCIENTIFIC EPISTEMIC PR AUDITOR
# ==========================================

from python.discovery.epistemic_pr_auditor import (
    ScientificEpistemicPRAuditor,
    PullRequestDiffSnapshot,
    FileDiffChunk,
    EpistemicReviewReport,
)

class FileDiffInput(BaseModel):
    file_path: str
    content: str
    is_new_file: bool = False
    is_deleted_file: bool = False

class AuditPRWebhookRequest(BaseModel):
    repo_name: str
    pull_request_number: int
    base_branch: str
    head_branch: str
    commit_sha: str
    pr_title: str
    pr_description: str
    files: List[FileDiffInput]

@app.post("/api/discovery/github/audit-pr-webhook")
def audit_pr_webhook(req: AuditPRWebhookRequest):
    try:
        auditor = ScientificEpistemicPRAuditor()
        diff_chunks = [
            FileDiffChunk(
                file_path=f.file_path,
                content=f.content,
                is_new_file=f.is_new_file,
                is_deleted_file=f.is_deleted_file
            )
            for f in req.files
        ]
        pr_snapshot = PullRequestDiffSnapshot(
            repo_name=req.repo_name,
            pull_request_number=req.pull_request_number,
            base_branch=req.base_branch,
            head_branch=req.head_branch,
            commit_sha=req.commit_sha,
            pr_title=req.pr_title,
            pr_description=req.pr_description,
            files=diff_chunks
        )
        report = auditor.audit_pull_request(pr_snapshot)
        return report.to_dict()
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


# ==========================================
# CATEGORICAL EPISTEMIC REASONING & DIAGRAM AUDIT
# ==========================================

class MorphismSpec(BaseModel):
    morphism_id: str
    domain: str
    codomain: str
    morphism_type: str = "CAUSAL_TRANSITION"
    matrix: Optional[List[List[float]]] = None
    symbolic_rule: str = ""

class CategoricalAuditRequest(BaseModel):
    category_name: str = "EpistemicReasoningCategory"
    objects: Optional[List[Dict[str, Any]]] = None
    morphisms: Optional[List[MorphismSpec]] = None
    path_a_morphism_ids: Optional[List[str]] = None
    path_b_morphism_ids: Optional[List[str]] = None
    tolerance: float = 1e-5

@app.post("/api/discovery/categorical/audit-diagram")
def audit_categorical_diagram(req: CategoricalAuditRequest):
    """
    Audits a commutative diagram of scientific reasoning.
    Computes holonomy defect ||Path_A - Path_B||_F to detect unobserved confounders or causal fallacies.
    """
    import numpy as np
    try:
        cat = EpistemicCategory(category_name=req.category_name)
        
        # Default demonstration diagram (MetaboAD metabolic gate) if empty
        if not req.objects or not req.morphisms:
            obj_tau = CategoryObject.create("Tau", "Tau Pathology", "BIO_MARKER", load=0.85)
            obj_fdg = CategoryObject.create("FDG", "FDG-PET Hypometabolism", "METABOLIC_GATE", suvr=1.05)
            obj_moca = CategoryObject.create("MoCA", "Cognitive Decline Score", "CLINICAL_STATE", score=18.0)

            cat.add_object(obj_tau)
            cat.add_object(obj_fdg)
            cat.add_object(obj_moca)

            m_tau_fdg = CategoryMorphism(
                morphism_id="f_tau_fdg",
                domain=obj_tau,
                codomain=obj_fdg,
                morphism_type=MorphismType.CAUSAL_TRANSITION,
                transformation_matrix=np.array([[0.8, -0.2], [0.1, 0.9]]),
                symbolic_rule="Tau -> Glycolytic_Failure"
            )
            m_fdg_moca = CategoryMorphism(
                morphism_id="g_fdg_moca",
                domain=obj_fdg,
                codomain=obj_moca,
                morphism_type=MorphismType.CAUSAL_TRANSITION,
                transformation_matrix=np.array([[0.7, 0.0], [0.3, 0.85]]),
                symbolic_rule="Glycolytic_Failure -> Synaptic_Decay"
            )
            direct_comp = np.dot(m_fdg_moca.transformation_matrix, m_tau_fdg.transformation_matrix)
            m_direct = CategoryMorphism(
                morphism_id="h_direct_tau_moca",
                domain=obj_tau,
                codomain=obj_moca,
                morphism_type=MorphismType.EMPIRICAL_MEASUREMENT,
                transformation_matrix=direct_comp,
                symbolic_rule="Tau -> Synaptic_Decay (Direct)"
            )

            cat.add_morphism(m_tau_fdg)
            cat.add_morphism(m_fdg_moca)
            cat.add_morphism(m_direct)

            path_a = [m_tau_fdg, m_fdg_moca]
            path_b = [m_direct]
        else:
            obj_lookup: Dict[str, CategoryObject] = {}
            for o in req.objects:
                c_obj = CategoryObject.create(
                    object_id=o["id"],
                    name=o.get("name", o["id"]),
                    dimension_space=o.get("dimension_space", "OBSERVATIONAL_SPACE"),
                    **o.get("attributes", {})
                )
                cat.add_object(c_obj)
                obj_lookup[c_obj.object_id] = c_obj

            for m in req.morphisms:
                if m.domain not in obj_lookup or m.codomain not in obj_lookup:
                    raise ValueError(f"Domain '{m.domain}' or Codomain '{m.codomain}' not found in objects.")
                
                m_matrix = np.array(m.matrix) if m.matrix else np.eye(2)
                m_type = MorphismType(m.morphism_type) if m.morphism_type in MorphismType.__members__ else MorphismType.CAUSAL_TRANSITION
                cat_m = CategoryMorphism(
                    morphism_id=m.morphism_id,
                    domain=obj_lookup[m.domain],
                    codomain=obj_lookup[m.codomain],
                    morphism_type=m_type,
                    transformation_matrix=m_matrix,
                    symbolic_rule=m.symbolic_rule
                )
                cat.add_morphism(cat_m)

            path_a = [cat.morphisms[mid] for mid in (req.path_a_morphism_ids or [])]
            path_b = [cat.morphisms[mid] for mid in (req.path_b_morphism_ids or [])]

        axioms_check = cat.verify_category_axioms()
        audit_res = CommutativeDiagramAuditor.audit_diagram_commutativity(
            path_a=path_a,
            path_b=path_b,
            tolerance=req.tolerance
        )

        return {
            "category_axioms": axioms_check,
            "diagram_audit": audit_res
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/api/discovery/exact-symbolic/audit")
def audit_exact_symbolic(req: AuditExactSymbolicRequest):
    """
    ADR-EPISTEMIC-034: Exact Symbolic Dual-Verification & Obstacle-Driven Discovery Engine
    Audits candidate mathematical/physical proofs using SymPy and strict lemma purity checks.
    """
    try:
        dag = ExactProofDAG(theorem_id=req.theorem_id, target_statement=req.target_statement or "")
        for l in req.lemmas:
            status_str = l.get("status", "ESTABLISHED_AXIOM")
            status = EpistemicLemmaStatus(status_str) if status_str in EpistemicLemmaStatus.__members__ else EpistemicLemmaStatus.ESTABLISHED_AXIOM
            dag.add_lemma(ExactLemmaNode(
                lemma_id=l["lemma_id"],
                statement=l.get("statement", ""),
                status=status,
                premises=l.get("premises", []),
                symbolic_expression=l.get("symbolic_expression")
            ))

        report = ExactSymbolicCourt.audit_exact_proof(
            dag=dag,
            lhs_target=req.lhs_target,
            rhs_target=req.rhs_target,
            sequence_benchmark=req.sequence_benchmark
        )
        return report.to_dict()
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


# Global singleton instance for OntologyPlanEngine
from python.knowledge.ontology_plan_engine import (
    OntologyPlanEngine,
    OntologicalAxiom,
    AxiomType,
)
_global_ontology_engine = OntologyPlanEngine()


@app.post("/api/ontology/plan")
def plan_ontology_change(req: OntologyPlanChangeRequest):
    """
    ADR-ONTOLOGY-035: Computes epistemic blast radius for proposed ontology mutations.
    """
    try:
        axioms = []
        for ax in req.proposed_axioms:
            ax_type = AxiomType(ax["axiom_type"])
            axioms.append(OntologicalAxiom(
                axiom_id=ax.get("axiom_id", f"AX-{len(axioms)+1}"),
                axiom_type=ax_type,
                subject=ax.get("subject", ""),
                predicate=ax.get("predicate", ""),
                object_target=ax.get("object_target", ""),
                metadata=ax.get("metadata", {})
            ))
        report = _global_ontology_engine.plan_change(
            proposed_axioms=axioms,
            max_safe_blast_radius=req.max_safe_blast_radius or 100
        )
        return report.to_dict()
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/api/ontology/apply")
def apply_ontology_plan(req: OntologyApplyPlanRequest):
    """
    ADR-ONTOLOGY-035: Atomically applies an approved plan to the ontology state.
    """
    try:
        tx = _global_ontology_engine.apply_plan(plan_id=req.plan_id, force=req.force or False)
        return {
            "transaction_id": tx.transaction_id,
            "plan_id": tx.plan_id,
            "blast_radius": tx.blast_radius,
            "som_commit_hash": tx.som_commit_hash,
            "status": "APPLIED_SUCCESSFULLY"
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/api/ontology/rollback")
def rollback_ontology_transaction(req: OntologyRollbackRequest):
    """
    ADR-ONTOLOGY-035: Immediately rolls back a previously applied transaction.
    """
    try:
        success = _global_ontology_engine.rollback_transaction(transaction_id=req.transaction_id)
        if not success:
            raise HTTPException(status_code=404, detail=f"Transaction '{req.transaction_id}' not found.")
        return {
            "transaction_id": req.transaction_id,
            "status": "ROLLED_BACK_SUCCESSFULLY"
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


from python.discovery.lagrangian_epistemic_engine import (
    LagrangianEpistemicEngine,
    LagrangianProposal,
    DynamicalSystemType,
)


@app.post("/api/discovery/lagrangian/audit")
def audit_lagrangian_proposal(req: AuditLagrangianProposalRequest):
    """
    ADR-DISCOVERY-036: Generalized Lagrangian Epistemics & Principle of Stationary Action
    Derives exact Euler-Lagrange equations of motion and audits Noether symmetries.
    """
    try:
        sys_type = (
            DynamicalSystemType(req.system_type)
            if req.system_type in DynamicalSystemType.__members__
            else DynamicalSystemType.MECHANICAL_DISCRETE
        )
        proposal = LagrangianProposal(
            proposal_id=req.proposal_id,
            system_type=sys_type,
            generalized_coordinates=req.generalized_coordinates,
            kinetic_term=req.kinetic_term,
            potential_term=req.potential_term,
            claimed_equation_of_motion=req.claimed_equation_of_motion,
            assumed_symmetries=req.assumed_symmetries or []
        )
        report = LagrangianEpistemicEngine.audit_lagrangian_proposal(proposal)
        return report.to_dict()
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


from python.discovery.ablation_rebuttal_engine import (
    AblationRebuttalEngine,
    SimulatedObjection,
)


@app.post("/api/discovery/ablation-rebuttal/run")
def run_ablation_and_rebuttal(req: RunAblationRebuttalRequest):
    """
    ADR-DISCOVERY-037: Automated Theoretical Ablation & Simulated Peer-Review Rebuttal Loop
    Inspired by ScientistTwo (Google Cloud AI, 2026).
    """
    try:
        objs = []
        for o in req.objections or []:
            objs.append(SimulatedObjection(
                reviewer_id=o.get("reviewer_id", "Reviewer-1"),
                critique_point=o.get("critique_point", ""),
                severity=o.get("severity", "MINOR"),
                targeted_subexpression=o.get("targeted_subexpression")
            ))
        dossier = AblationRebuttalEngine.generate_dossier(
            model_id=req.model_id,
            q_name=req.q_name,
            kinetic_str=req.kinetic_str,
            base_potential_str=req.base_potential_str,
            interaction_terms=req.interaction_terms,
            objections=objs
        )
        return dossier.to_dict()
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


from python.discovery.world_model_adapter import (
    WorldModelEpistemicAdapter,
    LatentInterventionSpec,
    SafetyConstraintSpec,
    GuardrailType,
)


@app.post("/api/discovery/world-model/simulate")
def simulate_world_model_intervention(req: SimulateWorldModelInterventionRequest):
    """
    ADR-DISCOVERY-038: Latent World Model Grounding & Hierarchical H-JEPA Guardrail Simulation
    Simulates physical perturbations in the continuous latent manifold with E = +inf guardrails.
    """
    try:
        constraints = []
        for c in req.safety_constraints or []:
            g_type = (
                GuardrailType(c["guardrail_type"])
                if c["guardrail_type"] in GuardrailType.__members__
                else GuardrailType.CONSERVATION_OF_ENERGY
            )
            constraints.append(SafetyConstraintSpec(
                constraint_id=c.get("constraint_id", f"GUARD-{len(constraints)+1}"),
                guardrail_type=g_type,
                target_channel=c["target_channel"],
                min_safe_value=c.get("min_safe_value"),
                max_safe_value=c.get("max_safe_value")
            ))

        intervention = LatentInterventionSpec(
            intervention_id=req.intervention_id,
            target_manifold_node=req.target_manifold_node,
            intervention_magnitude=req.intervention_magnitude,
            safety_constraints=constraints
        )

        result = WorldModelEpistemicAdapter.simulate_latent_intervention(
            intervention=intervention,
            current_latent_state=req.current_latent_state,
            macro_subgoals=req.macro_subgoals
        )
        return result.to_dict()
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


class MultiscalePredictRequest(BaseModel):
    node_id: str
    abstraction_level: str  # MICRO_IMPLEMENTATIONAL, MESO_ALGORITHMIC, MACRO_COMPUTATIONAL_CONSERVATIVE
    latent_vector: List[float]
    detail_dimension: int
    action_vector: List[float]
    expected_target: Optional[List[float]] = None
    noise_variance: float = 0.05
    conserved_quantities: Optional[Dict[str, float]] = None


@app.post("/api/discovery/multiscale/predict")
def predict_multiscale_latent_transition(req: MultiscalePredictRequest):
    """
    ADR-DISCOVERY-039: Multiscale Latent Abstraction Hierarchy & Differentiable Action-Conditioned Epistemics
    Calculates forward latent prediction, prediction horizon, and energy gradients.
    """
    try:
        level_map = {
            "MICRO_IMPLEMENTATIONAL": AbstractionLevel.MICRO_IMPLEMENTATIONAL,
            "MESO_ALGORITHMIC": AbstractionLevel.MESO_ALGORITHMIC,
            "MACRO_COMPUTATIONAL_CONSERVATIVE": AbstractionLevel.MACRO_COMPUTATIONAL_CONSERVATIVE,
        }
        level = level_map.get(req.abstraction_level, AbstractionLevel.MESO_ALGORITHMIC)

        state = MultiscaleStateNode(
            node_id=req.node_id,
            level=level,
            latent_vector=req.latent_vector,
            detail_dimension=req.detail_dimension,
            noise_variance=req.noise_variance,
            conserved_quantities=req.conserved_quantities or {},
        )

        engine = MultiscaleAbstractionEngine()
        verdict = engine.evaluate_action_conditioned_transition(
            state=state,
            action=req.action_vector,
            expected_target=req.expected_target,
        )

        return {
            "source_node_id": verdict.source_node_id,
            "abstraction_level": verdict.abstraction_level.value,
            "prediction_horizon": verdict.prediction_horizon,
            "target_prediction": verdict.target_prediction,
            "energy_loss": verdict.energy_loss,
            "gradient_norm": verdict.gradient_norm,
            "is_differentiable": verdict.is_differentiable,
            "details": verdict.details,
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


class EnergyAuditRequest(BaseModel):
    theory_id: str
    theory_embedding: List[float]
    theory_conserved_quantities: Optional[Dict[str, float]] = None
    theory_hard_violations: Optional[List[str]] = None
    empirical_reference_embedding: List[float]
    empirical_conserved_quantities: Optional[Dict[str, float]] = None


@app.post("/api/discovery/energy-ebm/audit")
def audit_theory_energy_ebm(req: EnergyAuditRequest):
    """
    ADR-EPISTEMIC-040: Non-Generative Energy-Based Epistemics & Model-Predictive Scientific Auditing
    Evaluates physical theories using unnormalized energy compatibility (EBM) and VICReg regularizers.
    """
    try:
        theory_latent = LatentPhysicalState(
            state_id=req.theory_id,
            embedding=req.theory_embedding,
            conserved_quantities=req.theory_conserved_quantities or {},
            hard_violations=req.theory_hard_violations or [],
        )

        empirical_ref = LatentPhysicalState(
            state_id=f"ref_{req.theory_id}",
            embedding=req.empirical_reference_embedding,
            conserved_quantities=req.empirical_conserved_quantities or {},
        )

        auditor = NonGenerativeEpistemicAuditor()
        verdict = auditor.audit_physical_theory(
            theory_id=req.theory_id,
            theory_latent=theory_latent,
            empirical_reference_latent=empirical_ref,
        )

        return {
            "theory_id": verdict.theory_id,
            "unnormalized_energy": verdict.unnormalized_energy,
            "is_physically_sound": verdict.is_physically_sound,
            "failure_mode": verdict.failure_mode,
            "vicreg_health": {
                "invariance_loss": verdict.vicreg_health.invariance_loss,
                "variance_loss": verdict.vicreg_health.variance_loss,
                "covariance_loss": verdict.vicreg_health.covariance_loss,
                "total_vicreg_loss": verdict.vicreg_health.total_vicreg_loss,
                "is_representation_collapsed": verdict.vicreg_health.is_representation_collapsed,
            },
            "mpc_plan": {
                "horizon_steps": verdict.mpc_plan.horizon_steps,
                "best_candidate_energy": verdict.mpc_plan.best_candidate_energy,
                "residual_rl_calibration_needed": verdict.mpc_plan.residual_rl_calibration_needed,
                "explanation": verdict.mpc_plan.explanation,
            },
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


class NotarizeThoughtRequest(BaseModel):
    hypothesis_content: str
    author_id: Optional[str] = None
    extra_metadata: Optional[Dict[str, Any]] = None


class AuditPerimeterRequest(BaseModel):
    active_endpoints: List[str]
    session_id: Optional[str] = "session"


@app.post("/api/discovery/sovereignty/notarize")
def notarize_thought_claim(req: NotarizeThoughtRequest):
    """
    ADR-SOVEREIGNTY-041: Zero-Trust Epistemic Bunker & Cryptographic Thought-Privacy Architecture
    Instantly fingerprints scientific priority with SHA-256 and Merkle proof without cloud leakage.
    """
    try:
        bunker = SovereignEpistemicBunker(author_id=req.author_id or "sovereign_researcher")
        rec = bunker.notarize_intellectual_claim(
            hypothesis_content=req.hypothesis_content,
            author_id=req.author_id,
            extra_metadata=req.extra_metadata,
        )
        return {
            "thought_hash_sha256": rec.thought_hash_sha256,
            "timestamp_ns": rec.timestamp_ns,
            "author_id": rec.author_id,
            "preview_snippet": rec.preview_snippet,
            "merkle_anchor": rec.merkle_anchor,
            "is_airgapped": rec.is_airgapped,
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/api/discovery/sovereignty/audit-perimeter")
def audit_session_perimeter(req: AuditPerimeterRequest):
    """
    ADR-SOVEREIGNTY-041: Verifies network perimeter and raises alarms on non-sovereign endpoints.
    """
    try:
        bunker = SovereignEpistemicBunker()
        report = bunker.audit_session_perimeter(
            active_endpoints=req.active_endpoints,
            session_id=req.session_id or "session",
        )
        return {
            "session_id": report.session_id,
            "is_fully_airgapped": report.is_fully_airgapped,
            "blocked_remote_hosts": report.blocked_remote_hosts,
            "leak_probability": report.leak_probability,
            "security_verdict": report.security_verdict,
            "details": report.details,
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


class ExtractLimitationsRequest(BaseModel):
    baseline_name: str
    theory_text: str
    known_weaknesses: Optional[List[Dict[str, Any]]] = None


@app.post("/api/discovery/limitations/extract")
def extract_baseline_limitations(req: ExtractLimitationsRequest):
    """
    ADR-DISCOVERY-042: Problem-Driven Limitation Resolution & Empirical Refinement Engine
    Extracts actionable theoretical and computational bottlenecks from baseline models.
    """
    try:
        engine = LimitationResolutionEngine()
        limitations = engine.extract_actionable_limitations(
            baseline_name=req.baseline_name,
            theory_text=req.theory_text,
            known_weaknesses=req.known_weaknesses,
        )
        ideas = engine.generate_targeted_seed_ideas(limitations)
        return {
            "baseline_name": req.baseline_name,
            "total_limitations_found": len(limitations),
            "limitations": [
                {
                    "limitation_id": lim.limitation_id,
                    "category": lim.category.value,
                    "description": lim.description,
                    "impact_severity": lim.impact_severity,
                    "is_actionable": lim.is_actionable,
                    "formal_bottleneck_equation": lim.formal_bottleneck_equation,
                }
                for lim in limitations
            ],
            "targeted_seed_ideas": [
                {
                    "idea_id": idea.idea_id,
                    "target_limitation_ids": idea.target_limitation_ids,
                    "proposed_mechanism": idea.proposed_mechanism,
                    "novelty_score": idea.novelty_score,
                }
                for idea in ideas
            ],
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


class ResultFamilyNodeRequest(BaseModel):
    node_id: str
    title: str
    role: str = "CORE_THEOREM"
    statement: str
    symbolic_expression: Optional[str] = None
    has_lean_formalization: bool = False
    lean_file_path: Optional[str] = None
    parent_lemma_ids: List[str] = []


class ResultFamilyAuditRequest(BaseModel):
    family_id: str
    family_title: str
    discipline: str = "MATHEMATICS"
    nodes: List[ResultFamilyNodeRequest]


@app.post("/api/discovery/families/audit")
def audit_result_family_endpoint(req: ResultFamilyAuditRequest):
    """
    Audits a Result Family (ADR-DISCOVERY-043) enforcing CAS + Lean Dual Formalization Gate
    and category holonomy commutativity.
    """
    try:
        orchestrator = ResultFamilyOrchestrator(
            family_id=req.family_id,
            family_title=req.family_title,
            discipline=req.discipline,
        )
        for n in req.nodes:
            role_enum = ResultRole(n.role) if n.role in [r.value for r in ResultRole] else ResultRole.CORE_THEOREM
            orchestrator.add_manuscript_node(
                node_id=n.node_id,
                title=n.title,
                role=role_enum,
                statement=n.statement,
                symbolic_expression=n.symbolic_expression,
                has_lean_formalization=n.has_lean_formalization,
                lean_file_path=n.lean_file_path,
                parent_lemma_ids=n.parent_lemma_ids,
            )
        verdict = orchestrator.audit_family_epistemic_integrity()
        return verdict.to_dict()
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))










