"""Request models for the CoResearcher API."""

from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


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
    # ADR-DISCOVERY-061: the hypothesis as a formal object, or ask the formalizer to build one from `question`.
    formal_hypothesis: Optional["FormalHypothesisModel"] = None
    formalize_question: bool = False
    formalizer_samples: Optional[int] = Field(default=None, ge=1, le=7)  # ADR-DISCOVERY-064 gate size.


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


class SynthesizeContractRequest(BaseModel):
    exposure_variable: str
    outcome_variable: str
    marr_explanation_level: str = "ALGORITHMIC"
    dataset_path: Optional[str] = None


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


class MultiscalePredictRequest(BaseModel):
    node_id: str
    abstraction_level: str  # MICRO_IMPLEMENTATIONAL, MESO_ALGORITHMIC, MACRO_COMPUTATIONAL_CONSERVATIVE
    latent_vector: List[float]
    detail_dimension: int
    action_vector: List[float]
    expected_target: Optional[List[float]] = None
    noise_variance: float = 0.05
    conserved_quantities: Optional[Dict[str, float]] = None


class EnergyAuditRequest(BaseModel):
    theory_id: str
    theory_embedding: List[float]
    theory_conserved_quantities: Optional[Dict[str, float]] = None
    theory_hard_violations: Optional[List[str]] = None
    empirical_reference_embedding: List[float]
    empirical_conserved_quantities: Optional[Dict[str, float]] = None


class NotarizeThoughtRequest(BaseModel):
    hypothesis_content: str
    author_id: Optional[str] = None
    extra_metadata: Optional[Dict[str, Any]] = None


class AuditPerimeterRequest(BaseModel):
    active_endpoints: List[str]
    session_id: Optional[str] = "session"


class ExtractLimitationsRequest(BaseModel):
    baseline_name: str
    theory_text: str
    known_weaknesses: Optional[List[Dict[str, Any]]] = None


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


class CandidateEvidenceItemRequest(BaseModel):
    item_id: str
    title: str
    snippet: str
    study_design: str = "RETROSPECTIVE_OBSERVATIONAL"
    polarity: str = "SUPPORTS"
    sample_size: int = 0
    p_value: Optional[float] = None
    effect_size: Optional[float] = None
    doi_or_source: str = ""
    rcs_level: int = 0
    confounding_risk: float = 0.0
    is_pre_registered: bool = False


class ClaimEvidenceAuditRequest(BaseModel):
    claim_id: str
    claim_text: str
    evidence_items: List[CandidateEvidenceItemRequest]
    force_system_two: bool = False


class BarrierAuditRequest(BaseModel):
    strategy_id: str
    target_hypothesis: str
    method_family: str = "CONTOUR_MOMENT_ESTIMATION"
    target_threshold: float = 0.50
    proposed_intermediate_result: Optional[float] = None


class MathematicalFlywheelCycleRequest(BaseModel):
    cycle_id: str
    theorems: List[Dict[str, Any]]


class LeanFormalizationRequest(BaseModel):
    theorem_name: str
    lean_code: Optional[str] = None
    hypothesis_statement: Optional[str] = None
    symbolic_identity: Optional[str] = None


class BijectivityAuditRequest(BaseModel):
    claim_name: str
    prose_statement: str
    lean_code: str
    frozen_signature_hash: Optional[str] = None


class OversightAuditRequest(BaseModel):
    claim_id: str
    task_criticality: str = "PARADIGMATIC_NOVELTY"
    ai_recommendation: str = "ACCEPT"
    human_decision: str = "ACCEPT"
    reviewer_id: str = "human_reviewer_01"
    dwell_time_seconds: float = 30.0
    counterexamples_inspected: List[str] = []
    explicit_causal_rationale: str = ""
    answered_inspection_challenge: bool = True
    ai_critique_text: str = ""
    is_mathematically_sound: bool = True
    conserves_physical_invariants: bool = True


class CandidateLemmaStepInput(BaseModel):
    step_id: str
    target_conjecture_id: str
    statement: str
    symbolic_expression: Optional[str] = None
    premises: List[str] = []
    unstated_assumptions: List[str] = []
    prover_direction: str = "algebraic_decomposition"
    round_index: int = 1


class CogenticProofDiscoveryRequest(BaseModel):
    conjecture_id: str
    target_statement: str
    max_model_budget: int = 100
    prover_directions: Optional[List[str]] = None
    candidate_steps: Optional[List[CandidateLemmaStepInput]] = None


class MetalCoordinationCenterInput(BaseModel):
    ion_id: str
    metal_type: str = "ZN2"
    coordinating_atom_count: int = 4
    geometry: str = "TETRAHEDRAL"
    observed_mean_bond_length_angstrom: float = 2.05
    expected_bond_length_angstrom: float = 2.05
    tolerance_angstrom: float = 0.35


class BiomacromolecularAuditRequest(BaseModel):
    complex_id: str
    target_protein: str
    e3_ligase: str
    linker_length_atoms: int = 14
    warhead_kd_nm: float = 12.0
    e3_kd_nm: float = 25.0
    ternary_kd_nm: float = 4.5
    min_atom_distance_angstrom: float = 2.10
    metal_centers: Optional[List[MetalCoordinationCenterInput]] = None
    latent_prior_state: Optional[Dict[str, float]] = None


class MetabolicComponentInput(BaseModel):
    component_id: str
    name: str
    is_external_nutrient: bool = False
    is_dissipated_waste: bool = False
    molecular_mass_da: float = 100.0


class CatalyticProcessInput(BaseModel):
    process_id: str
    name: str
    material_inputs: List[str]
    efficient_catalysts: List[str]
    material_products: List[str]
    entropy_production_rate: float = 0.05


class AutopoieticSystemAuditRequest(BaseModel):
    system_id: str
    system_name: str
    components: List[MetabolicComponentInput]
    processes: List[CatalyticProcessInput]


class PotentialValleyInput(BaseModel):
    valley_id: str
    category_name: str
    center_coordinate: float
    depth: float
    width_sigma: float = 0.5
    prior_weight: float = 1.0


class VegaDecisionRequest(BaseModel):
    domain: str = "TYPED_DECISION"
    valleys: List[PotentialValleyInput]
    initial_position: float = 0.0
    initial_velocity: float = 0.0
    friction_gamma: float = 0.45
    mass: float = 1.0
    dt: float = 0.05
    max_steps: int = 200
    abstain_barrier_threshold: float = 0.08


class LiteratureHopInput(BaseModel):
    source_entity: str
    target_entity: str
    relation: str
    literature_citations_count: int = 1
    temporal_stability_score: float = 0.85
    confidence_weight: float = 0.85


class HakkenLinkPredictionRequest(BaseModel):
    candidate_id: str
    domain: str = "AGING_BIOLOGY"
    source_entity: str
    target_entity: str
    predicted_relation: str
    hops: List[LiteratureHopInput]
    direct_literature_hits: int = 0


class DiscoveryHistoryNodeInput(BaseModel):
    node_id: str
    hypothesis_id: str
    branch_depth: int = 0
    compute_tokens_cost: int = 1000
    wet_lab_euro_cost: float = 0.0
    time_spent_hours: float = 1.0
    outcome_reward: float = 0.5
    failure_category: Optional[str] = None
    is_terminal: bool = False
    children: List["DiscoveryHistoryNodeInput"] = []


DiscoveryHistoryNodeInput.model_rebuild()


class SearchPolicyInput(BaseModel):
    policy_id: str
    branch_ordering: str = "VALUE_GREEDY"
    worker_concurrency: int = 1
    pruning_reward_threshold: float = 0.20
    max_tokens_budget: int = 100_000
    stop_early_on_reward: float = 0.85


class DreamRSIReplayRequest(BaseModel):
    history_tree: DiscoveryHistoryNodeInput
    policy: SearchPolicyInput


class FrontierMathTaskInput(BaseModel):
    task_id: str
    title: str
    problem_statement_prose: str
    formal_lean_statement: str
    reference_solution_code: Optional[str] = None
    domain_topic: str = "ANALYSIS_NUMBER_THEORY"
    source_repository: str = "openai/math"
    metadata: Dict[str, Any] = {}


class MathFlywheelCycleRequest(BaseModel):
    cycle_id: str
    problem_tasks: List[FrontierMathTaskInput]
    submitted_solutions: Optional[Dict[str, str]] = None


class ERAMutateCodeRequest(BaseModel):
    parent_variant_id: str
    generation_depth: int = 0
    mutation_strategy: str = "EXPONENTIAL_DECAY_LAG"
    parameter_spec: Dict[str, float] = {"decay_alpha": 0.5}
    code_snippet: str = "y_pred[t] = 0.5 * y[t-1] + 0.5 * y_pred[t-1]"
    new_variant_id: str = "mutated-variant-1"


class ERASearchCampaignRequest(BaseModel):
    campaign_id: str
    dataset_name: str
    ground_truth_time_series: List[float]
    time_step_days: float = 7.0
    surge_threshold_quantile: float = 0.85
    max_iterations: int = 50
    beam_width: int = 4


class TournamentHypothesisInput(BaseModel):
    hypothesis_id: str
    title: str
    statement: str
    domain: str = "BIOMEDICINE"
    # Axis scores are supplied by the caller; the arena does not compute them.
    evidence_score: float = Field(0.5, ge=0.0, le=1.0)
    physical_consistency_score: float = Field(0.5, ge=0.0, le=1.0)
    delta_omega_potential: float = Field(0.5, ge=0.0, le=1.0)
    falsifiability_score: float = Field(0.5, ge=0.0, le=1.0)
    elo_rating: float = Field(1200.0, ge=0.0, le=4000.0)


class DebateMatchRequest(BaseModel):
    hypothesis_a: TournamentHypothesisInput
    hypothesis_b: TournamentHypothesisInput
    match_id: Optional[str] = None
    k_factor: float = Field(32.0, gt=0.0, le=100.0)


class RunTournamentRequest(BaseModel):
    tournament_id: str
    domain: str = "BIOMEDICINE"
    # Bounded: the cost grows with rounds x candidates^2.
    candidates: List[TournamentHypothesisInput] = Field(..., min_length=2, max_length=50)
    rounds: int = Field(1, ge=1, le=10)
    k_factor: float = Field(32.0, gt=0.0, le=100.0)


class FormalVariableModel(BaseModel):
    name: str
    domain: List[Any] = []
    continuous: bool = False
    lower: Optional[float] = None
    upper: Optional[float] = None


class NonWitnessModel(BaseModel):
    """A (partial) state the claims must NOT be satisfied by, such as the zero or the free model (ADR-080)."""

    label: str = ""
    state: Dict[str, Any]


class FormalHypothesisModel(BaseModel):
    hypothesis_id: str
    variables: List[FormalVariableModel]
    claims: List[str]
    assumptions: List[str] = []
    scope: Optional[str] = None
    statement: str = ""
    alternatives: List[str] = []
    non_witnesses: List[NonWitnessModel] = Field(default_factory=list, max_length=50)


class ClaimEvidenceModel(BaseModel):
    """Evidence recorded for one claim, graded by the trust ladder's mechanical rules (ADR-080)."""

    statement_audit: Optional[Dict[str, Any]] = None
    kernel_check: Optional[Dict[str, Any]] = None
    reproductions: List[Dict[str, Any]] = Field(default_factory=list, max_length=20)


class EvaluateFormalHypothesisRequest(BaseModel):
    hypothesis: FormalHypothesisModel
    observations: List[Dict[str, Any]] = []
    max_examples: int = 5
    # ADR-080: also probe generic trivial witnesses (numeric variables at zero or at a bound). Advisory only.
    default_probes: bool = False
    # ADR-080: evidence that can lift a claim above STATEMENT_PUBLIC, keyed by the claim's predicate text.
    claim_evidence: Dict[str, ClaimEvidenceModel] = Field(default_factory=dict)


class CompareFormalHypothesesRequest(BaseModel):
    a: FormalHypothesisModel
    b: FormalHypothesisModel
    max_examples: int = 5


class FormalizeHypothesisRequest(BaseModel):
    prose: str = Field(min_length=1, max_length=5000)
    hypothesis_id: str = "H-FORMALIZED"
    variable_schema: Optional[List[FormalVariableModel]] = None
    rivals: List[FormalHypothesisModel] = Field(default_factory=list, max_length=10)
    # ADR-DISCOVERY-064: number of independent formalizations for the self-consistency gate (default 5).
    samples: Optional[int] = Field(default=None, ge=1, le=7)


class FormalConsequenceRequest(BaseModel):
    hypothesis: FormalHypothesisModel
    consequence: str = Field(min_length=1, max_length=2000)
    max_examples: int = 5
    include_lean: bool = False


# --- Statement fidelity and the trust ladder (ADR-DISCOVERY-080) ----------------------------


class FidelityParameterModel(BaseModel):
    name: str
    integer: bool = False
    lower: Optional[float] = None
    upper: Optional[float] = None


class FidelityQuantityModel(BaseModel):
    name: str
    paper: str = Field(max_length=2000)
    lean: str = Field(max_length=2000)


class FidelityCompareRequest(BaseModel):
    """Paper range vs formal range of one theorem, in the predicate language plus max, min and abs (ADR-070)."""

    theorem: str = Field(min_length=1, max_length=200)
    parameters: List[FidelityParameterModel] = Field(min_length=1, max_length=20)
    paper: str = Field(min_length=1, max_length=4000)
    lean: str = Field(min_length=1, max_length=4000)
    domain: str = Field(default="True", max_length=4000)
    paper_source: str = Field(default="", max_length=2000)
    lean_source: str = Field(default="", max_length=2000)
    encoding: List[str] = Field(default_factory=list, max_length=50)
    quantities: List[FidelityQuantityModel] = Field(default_factory=list, max_length=20)
    # Optional cross-check through HypothesisEvaluator.compare with integer parameters fixed to these values.
    integer_values: Optional[Dict[str, List[int]]] = None


class LeanReviewModel(BaseModel):
    theorem: str
    kind: str
    line: int
    note: str = Field(max_length=4000)


class LeanLintRequest(BaseModel):
    source: str = Field(min_length=1, max_length=400_000)
    file: str = Field(default="<string>", max_length=300)
    reviews: List[LeanReviewModel] = Field(default_factory=list, max_length=500)


class TrustStatementModel(BaseModel):
    text: str = Field(min_length=1, max_length=400_000)
    location: str = Field(min_length=1, max_length=2000)
    sha256: str = Field(max_length=128)


class TrustEvidenceModel(BaseModel):
    claim: str = Field(min_length=1, max_length=4000)
    statement: Optional[TrustStatementModel] = None
    statement_audit: Optional[Dict[str, Any]] = None
    kernel_check: Optional[Dict[str, Any]] = None
    reproductions: List[Dict[str, Any]] = Field(default_factory=list, max_length=20)


class TrustAssessRequest(BaseModel):
    claims: List[TrustEvidenceModel] = Field(min_length=1, max_length=100)


# --- Manuscript audit: citation gate and import obligations (ADR-DISCOVERY-077, ADR-DISCOVERY-082) ---------------


class CitedHypothesisModel(BaseModel):
    text: str = Field(min_length=1, max_length=2000)
    # Literal phrases, any of which shows the hypothesis is stated where the result is used. Never regular expressions.
    phrases: List[str] = Field(min_length=1, max_length=20)


class CitedResultModel(BaseModel):
    key: str = Field(min_length=1, max_length=300)
    locator: str = Field(min_length=1, max_length=300)
    statement: str = Field(default="", max_length=4000)
    hypotheses: List[CitedHypothesisModel] = Field(default_factory=list, max_length=50)
    conventions: Dict[str, str] = Field(default_factory=dict)


class RegistryHypothesisModel(BaseModel):
    text: str = Field(min_length=1, max_length=2000)
    # Predicate in the ADR-059 language over the citing context's variables; empty when not formalized.
    formal: str = Field(default="", max_length=2000)
    # Literal phrases for lexical presence in a citing text. Never regular expressions; never a discharge.
    phrases: List[str] = Field(default_factory=list, max_length=20)


class RegistryEntryRequest(BaseModel):
    """A cited result or premise. `source` is provenance only and never decides validity (ADR-DISCOVERY-083)."""

    id: str = Field(min_length=1, max_length=120)
    source: str = Field(min_length=1, max_length=1000)
    statement: str = Field(min_length=1, max_length=4000)
    key: str = Field(default="", max_length=300)
    locator: str = Field(default="", max_length=300)
    kind: str = Field(default="result", max_length=40)
    formal_statement: Optional[Dict[str, Any]] = None
    hypotheses: List[RegistryHypothesisModel] = Field(default_factory=list, max_length=50)
    conventions: Dict[str, str] = Field(default_factory=dict)
    rung: str = "CLAIMED"


class CitingContextModel(BaseModel):
    """Where a registered result is used: declared variables, assumptions, conventions and optional text."""

    variables: List[Dict[str, Any]] = Field(default_factory=list, max_length=50)
    assumptions: List[str] = Field(default_factory=list, max_length=100)
    conventions: Dict[str, str] = Field(default_factory=dict)
    text: str = Field(default="", max_length=20000)


class CiteCheckRequest(BaseModel):
    entry_id: str = Field(min_length=1, max_length=120)
    version: Optional[int] = Field(default=None, ge=1)
    context: CitingContextModel


class RegistryDependencyRequest(BaseModel):
    node: str = Field(min_length=1, max_length=120)
    depends_on: str = Field(min_length=1, max_length=120)


class RegistryRetractRequest(BaseModel):
    reason: str = Field(min_length=1, max_length=2000)
    downgrade_to: Optional[str] = None
    date: Optional[str] = Field(default=None, max_length=10)


class RegistryReevaluatedRequest(BaseModel):
    note: str = Field(min_length=1, max_length=2000)


class ManuscriptAuditRequest(BaseModel):
    """LaTeX sources of one manuscript ({path: text}, .tex/.bib/.bbl) and optional context for the import checks."""

    files: Dict[str, str] = Field(min_length=1)
    registry: List[CitedResultModel] = Field(default_factory=list, max_length=500)
    # Also use the stored cited-results registry (ADR-DISCOVERY-083) for the hypothesis-match obligations.
    use_registry: bool = False
    manuscript_status: Dict[str, str] = Field(default_factory=dict)
    collection: Optional[List[str]] = Field(default=None, max_length=5000)
    claim: str = Field(default="", max_length=4000)


LaunchWorkbenchRequest.model_rebuild()


# --- Research lifecycle (ADR-DISCOVERY-063) ----------------------------------------


class CreateLifecycleProjectRequest(BaseModel):
    project_id: str = Field(..., max_length=64)
    title: str = Field(..., max_length=300)
    template: str = "default"


class LifecycleResultRequest(BaseModel):
    check_id: str = Field(..., max_length=100)
    ok: bool
    actor: str = Field(..., max_length=100)
    role: str = Field(..., description="AGENT, VERIFIER_TOOL or HUMAN")
    note: str = Field("", max_length=2000)
    value: Optional[float] = None
    artifact_path: Optional[str] = Field(None, max_length=500)
    sha256: Optional[str] = Field(None, max_length=64)
    criteria: Dict[str, str] = Field(default_factory=dict, description="Analysis: criterion id -> MET or NOT_MET")


class LifecycleActorRequest(BaseModel):
    actor: str = Field(..., max_length=100)


class LifecycleReworkRequest(BaseModel):
    stage: str
    actor: str = Field(..., max_length=100)
    reason: str = Field(..., max_length=2000)


class LifecycleReleaseRequest(BaseModel):
    actor: str = Field(..., max_length=100)
    summary: str = Field("", max_length=5000)
