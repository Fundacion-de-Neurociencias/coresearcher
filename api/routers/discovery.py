"""Discovery campaigns, benchmarks, git-agora, constraints and state endpoints."""

from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Security  # noqa: F401

from api.schemas import (
    CherryPickClaimRequest,
    ClusterAnomaliesRequest,
    CreateBranchRequest,
    DebateMatchRequest,
    DiagnoseFailureRequest,
    DiscoveryHistoryNodeInput,
    EpistemicSearchRequest,
    EvaluateBayesianSurpriseRequest,
    EvaluateRealityContactRequest,
    EvaluateRealityDistanceRequest,
    EvaluateTracesEpistemicRequest,
    GroundedSearchRequest,
    LabRecipeRequest,
    LaunchWorkbenchRequest,
    MathematicalFlywheelCycleRequest,
    MineConstraintRequest,
    PaperAgentExecuteRequest,
    PaperAgentQueryRequest,
    RegisterForecastRequest,
    RunCampaignRequest,
    RunConstraintBoxRequest,
    RunEmpiricalDiscoveryRequest,
    RunLongHorizonCampaignRequest,
    RunTournamentRequest,
)
from api.security import require_api_key
from api.state import (
    biological_programs_list,
    campaigns_registry,
    decomposed_dv,
    discriminative_predictions,
    epistemic_git_repo,
    hypothesis_graveyard,
    implications_registry,
    representation_ledger,
    rival_hypotheses,
    state_space_omega,
    workbenches_registry,
)
from python.discovery import (
    AdversarialDestructionEngine,
    AnomalyDiscoveryEngine,
    AutoExplicabilityEngine,
    BayesianSurpriseEngine,
    ConstraintBoxBenchmark,
    ConstraintCourt,
    ConstraintDiscoveryEngine,
    ConstraintSourceBridge,
    DiscoveryTeamOrchestrator,
    EpistemicTreeSearch,
    GroundedSearchSensor,
    LabInTheLoopAdapter,
    LongHorizonCampaignEngine,
    MarrTranslationEngine,
    MathematicalFlywheelRunner,
    RealCohortDiscoveryRunner,
    RealCohortEmpiricalPipeline,
    RealityContactEvaluator,
    RealityContactEvidence,
    RealityDistanceEvaluator,
    ReliabilityAuditor,
    RetrospectiveTimeSplitBenchmark,
    ScientificFailureEngine,
    SubstrateTier,
    SubstrateValidationRecord,
    TracesEpistemicAdapter,
    TrajectoryEvolutionEngine,
    UniversalLatentDiscoveryEngine,
    UnknownMechanismBenchmark,
    WorkbenchRunner,
)
from python.discovery.discovery_forecast_registry import (
    DiscoveryForecastRegistry,
    ProspectiveForecastEntry,
    QuantitativePredictionWindow,
)
from python.discovery.hakken_dream_rsi_engine import (
    DiscoveryHistoryNode,
)
from python.discovery.hypothesis_tournament_arena import (
    HypothesisEloTournamentOrchestrator,
    PairwiseDebateEngine,
    TournamentHypothesis,
)

router = APIRouter()


def parse_history_node(inp: DiscoveryHistoryNodeInput) -> DiscoveryHistoryNode:
    return DiscoveryHistoryNode(
        node_id=inp.node_id,
        hypothesis_id=inp.hypothesis_id,
        branch_depth=inp.branch_depth,
        compute_tokens_cost=inp.compute_tokens_cost,
        wet_lab_euro_cost=inp.wet_lab_euro_cost,
        time_spent_hours=inp.time_spent_hours,
        outcome_reward=inp.outcome_reward,
        failure_category=inp.failure_category,
        is_terminal=inp.is_terminal,
        children=[parse_history_node(c) for c in inp.children],
    )


@router.post("/api/discovery/retrospective/run-time-split-benchmark", dependencies=[Depends(require_api_key)])
def run_retrospective_time_split_benchmark():
    """Executes the Retrospective Time-Split Benchmark with strict data quarantine at Cutoff <= 2018."""
    report = RetrospectiveTimeSplitBenchmark.run_benchmark()
    return report.to_dict()


@router.post("/api/discovery/unknown-mechanism/run-100-worlds-benchmark", dependencies=[Depends(require_api_key)])
def run_unknown_mechanism_100_worlds_benchmark():
    """Executes the 100-World Unknown Mechanism Discovery Challenge evaluating autonomous abduction."""
    summary = UnknownMechanismBenchmark.run_100_worlds_benchmark()
    return summary.to_dict()


@router.post("/api/discovery/adversarial/run-destruction-test", dependencies=[Depends(require_api_key)])
def run_adversarial_destruction_test():
    """Executes the 50-Case Adversarial Epistemic Destruction Suite to stress-test mortality and error detection."""
    report = AdversarialDestructionEngine.run_50_case_destruction_suite()
    return report.to_dict()


@router.post("/api/discovery/traces/evaluate-epistemic-rigor", dependencies=[Depends(require_api_key)])
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
        state_space_pruned_fraction=req.state_space_pruned_fraction or 0.3958,
    )
    return report.to_dict()


@router.post("/api/discovery/campaigns/long-horizon-run", dependencies=[Depends(require_api_key)])
def run_long_horizon_campaign(req: RunLongHorizonCampaignRequest):
    """Executes closed-loop test-time science across multiple iterative research cycles with budget allocation."""
    state = LongHorizonCampaignEngine.run_multi_cycle_campaign(
        research_question=req.research_question
        or "How do connectome topological hubs buffer against cortical tau pathology?",
        target_cycles=req.target_cycles or 4,
    )
    return state.to_dict()


@router.post("/api/discovery/bayesian-surprise/evaluate", dependencies=[Depends(require_api_key)])
def evaluate_bayesian_surprise(req: EvaluateBayesianSurpriseRequest):
    """Computes Bayesian belief updating and Expected Information Gain (EIG)."""
    eval_res = BayesianSurpriseEngine.evaluate_experiment_surprise(
        hypothesis_id=req.hypothesis_id,
        hypothesis_statement=req.hypothesis_statement,
        prior_p=req.prior_probability,
        empirical_p_value=req.empirical_p_value,
        effect_size=req.effect_size or 0.8,
        sample_size=req.sample_size or 50,
        is_falsified=req.is_falsified or False,
    )
    return eval_res.to_dict()


# -----------------------------------------------------------------------------
# 1. Universal Cross-Domain Benchmark Endpoints
# -----------------------------------------------------------------------------


@router.post("/api/discovery/universal/cross-domain-benchmark", dependencies=[Depends(require_api_key)])
def run_universal_cross_domain_benchmark():
    """Executes the universal latent discovery circuit across 4 domains (Neuroscience, Astronomy, Macroeconomics, Marine Ecology)."""
    results = UniversalLatentDiscoveryEngine.run_all_domains_benchmark()
    return [r.to_dict() for r in results]


# -----------------------------------------------------------------------------
# 2. 100% Empirical Real-Cohort Pipeline Endpoints
# -----------------------------------------------------------------------------


@router.post("/api/discovery/real-cohort/run-empirical-discovery", dependencies=[Depends(require_api_key)])
def run_real_cohort_empirical_discovery(req: RunEmpiricalDiscoveryRequest):
    try:
        report = RealCohortEmpiricalPipeline.run_pipeline(file_path=req.file_path)
        return report.to_dict()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Empirical pipeline error: {str(e)}")


# -----------------------------------------------------------------------------
# 3. Real Cohort Heterogeneous Campaign Suite Endpoints
# -----------------------------------------------------------------------------


@router.post("/api/discovery/campaigns/run-heterogeneous-suite", dependencies=[Depends(require_api_key)])
def run_heterogeneous_discovery_suite():
    outcomes = RealCohortDiscoveryRunner.run_suite()
    return [o.to_dict() for o in outcomes]


# -----------------------------------------------------------------------------
# 4. Defeated Hypotheses Graveyard Endpoints
# -----------------------------------------------------------------------------


@router.get("/api/discovery/graveyard/list")
def list_defeated_hypotheses():
    records = hypothesis_graveyard.get_all_records()
    return [r.to_dict() for r in records]


# -----------------------------------------------------------------------------
# 5. Anomaly Discovery Engine Endpoints
# -----------------------------------------------------------------------------


@router.post("/api/discovery/anomalies/detect-and-cluster", dependencies=[Depends(require_api_key)])
def detect_and_cluster_anomalies(req: ClusterAnomaliesRequest):
    clusters = AnomalyDiscoveryEngine.detect_and_cluster_anomalies(
        cohort_name=req.cohort_name or "ADNI-ROSMAP-COMBINED", sample_size=req.sample_size or 250
    )
    return [c.to_dict() for c in clusters]


# -----------------------------------------------------------------------------
# 6. Scientific Failure Engine Endpoints
# -----------------------------------------------------------------------------


@router.post("/api/discovery/failure/diagnose-root-cause", dependencies=[Depends(require_api_key)])
def diagnose_prediction_failure(req: DiagnoseFailureRequest):
    autopsy = ScientificFailureEngine.diagnose_failure(
        hypothesis_id=req.hypothesis_id,
        prediction_id=req.prediction_id,
        observed_outcome=req.observed_outcome,
        predicted_outcome=req.predicted_outcome,
        auxiliary_assumptions=req.auxiliary_assumptions or [],
        scope_conditions=req.scope_conditions or [],
        statistical_p_value=req.statistical_p_value or 0.01,
    )
    return autopsy.to_dict()


# -----------------------------------------------------------------------------
# 7. ConstraintBox Benchmark Endpoints
# -----------------------------------------------------------------------------


@router.post("/api/discovery/constraint-box/run-benchmark", dependencies=[Depends(require_api_key)])
def run_constraint_box_benchmark(req: RunConstraintBoxRequest):
    res = ConstraintBoxBenchmark.run_benchmark(num_interventions=req.num_interventions or 40)
    return res.to_dict()


# -----------------------------------------------------------------------------
# 8. Reality Distance Multi-Substrate Endpoints
# -----------------------------------------------------------------------------


@router.post("/api/discovery/reality-distance/evaluate", dependencies=[Depends(require_api_key)])
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
                cryptographic_evidence_hash=r.get("evidence_hash", "sha256:custom_evidence"),
            )
            for r in req.custom_records
        ]
    report = RealityDistanceEvaluator.evaluate_reality_distance(entity_id=req.target_entity_id, records=records)
    return report.to_dict()


# -----------------------------------------------------------------------------
# 9. Grounded Search Sensor Endpoints
# -----------------------------------------------------------------------------


@router.post("/api/discovery/search/grounded-ingest", dependencies=[Depends(require_api_key)])
def ingest_grounded_search(req: GroundedSearchRequest):
    sources = GroundedSearchSensor.query_structured_sources(
        query_topic=req.query_topic, target_disease=req.target_disease or "ALZHEIMER_DISEASE"
    )
    bridge_result = ConstraintSourceBridge.mine_constraints_from_sources(sources)
    return {"sources": [s.to_dict() for s in sources], "bridge_result": bridge_result}


@router.post("/api/discovery/paper-agent/query", dependencies=[Depends(require_api_key)])
def query_paper_agents_endpoint(req: PaperAgentQueryRequest):
    """
    Paper2Agent (Nature 2026) MCP Adapter:
    Queries connected external virtual author paper agents matching a research topic.
    """
    agents = GroundedSearchSensor.query_paper_agents(topic=req.topic)
    return {"query_topic": req.topic, "matched_agents_count": len(agents), "agents": [a.to_dict() for a in agents]}


@router.post("/api/discovery/paper-agent/execute", dependencies=[Depends(require_api_key)])
def execute_paper_agent_endpoint(req: PaperAgentExecuteRequest):
    """
    Paper2Agent (Nature 2026) MCP Adapter:
    Executes an analytical method exposed by a virtual author paper agent.
    """
    try:
        result = GroundedSearchSensor.execute_paper_agent_method(
            agent_id=req.agent_id, tool_name=req.tool_name, arguments=req.arguments or {}
        )
        return result.to_dict()
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


# -----------------------------------------------------------------------------
# 10. Reality Contact Score (RCS) Endpoints
# -----------------------------------------------------------------------------


@router.post("/api/discovery/reality-contact/evaluate", dependencies=[Depends(require_api_key)])
def evaluate_reality_contact(req: EvaluateRealityContactRequest):
    evidence = RealityContactEvidence(
        literature_citations_count=req.literature_citations_count or 0,
        retrospective_cohorts_validated=req.retrospective_cohorts or [],
        prospective_holdout_datasets=req.prospective_holdouts or [],
        physical_experiment_runs=req.physical_experiment_runs or [],
        promoted_invariant_constraint_id=req.promoted_invariant_constraint_id,
        state_space_omega_pruned_fraction=req.state_space_omega_pruned_fraction or 0.0,
    )
    report = RealityContactEvaluator.evaluate_rcs(hypothesis_id=req.hypothesis_id, evidence=evidence)
    return report.to_dict()


# -----------------------------------------------------------------------------
# 11. Constraint Discovery Engine Endpoints
# -----------------------------------------------------------------------------


@router.post("/api/discovery/constraints/mine-and-verify", dependencies=[Depends(require_api_key)])
def mine_and_verify_constraint(req: MineConstraintRequest):
    candidate = ConstraintDiscoveryEngine.discover_and_stress_test_constraint(
        candidate_hypothesis_statement=req.statement,
        threshold_cutoff=req.threshold_cutoff or 0.65,
        state_space=state_space_omega,
    )
    return candidate.to_dict()


# -----------------------------------------------------------------------------
# 12. Constraint Court Endpoints
# -----------------------------------------------------------------------------


@router.post("/api/discovery/court/adjudicate", dependencies=[Depends(require_api_key)])
def adjudicate_constraint_court():
    verdict = ConstraintCourt.adjudicate_canonical_neurodegeneration_clash()
    return verdict.to_dict()


# -----------------------------------------------------------------------------
# 13. Scientific Git History Endpoints
# -----------------------------------------------------------------------------


@router.get("/api/discovery/history/commits")
def get_scientific_commit_history(entity_id: Optional[str] = "HYP-TAU-CONNECTOME"):
    history = epistemic_git_repo.get_entity_history(entity_id or "HYP-TAU-CONNECTOME")
    return [c.to_dict() for c in history]


@router.get("/api/discovery/git/open-branches")
def get_agora_open_branches():
    """
    Agora Shared Memory: Returns active open exploration branches across all autonomous agents.
    Prevents parallel agents from repeating existing research directions.
    """
    branches = epistemic_git_repo.agora_index.get_open_branches()
    return {"open_branches_count": len(branches), "branches": [b.to_dict() for b in branches]}


@router.get("/api/discovery/git/verified-claims")
def get_agora_verified_claims():
    """
    Agora Shared Memory: Returns verified claims and invariant constraints (RCS >= 2).
    Allows agents to build upon solid verified foundations without repeating base experiments.
    """
    claims = epistemic_git_repo.agora_index.get_verified_claims()
    return {"verified_claims_count": len(claims), "claims": [c.to_dict() for c in claims]}


@router.get("/api/discovery/git/dead-ends")
def get_agora_dead_ends():
    """
    Agora Shared Memory: Returns falsified hypotheses and dead-end boundary conditions.
    """
    dead_ends = epistemic_git_repo.agora_index.get_dead_ends()
    return {"dead_ends_count": len(dead_ends), "dead_ends": dead_ends}


@router.post("/api/discovery/git/branch/create", dependencies=[Depends(require_api_key)])
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
            tags=req.tags or [],
        )
        return branch.to_dict()
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/api/discovery/git/branch/cherry-pick", dependencies=[Depends(require_api_key)])
def cherry_pick_agora_claim(req: CherryPickClaimRequest):
    """
    Agora Shared Memory: Adopts a verified claim from another branch as a parent edge in the target branch.
    """
    try:
        commit = epistemic_git_repo.cherry_pick_claim(
            target_branch_id=req.target_branch_id,
            source_claim_id=req.source_claim_id,
            author_role=req.author_role or "Autonomous Worker",
        )
        return commit.to_dict()
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


# -----------------------------------------------------------------------------
# 14. Discovery Workbench & Legacy Endpoints
# -----------------------------------------------------------------------------


@router.post("/api/discovery/workbench/launch", dependencies=[Depends(require_api_key)])
def launch_discovery_workbench(req: LaunchWorkbenchRequest):
    wb = WorkbenchRunner.run_question(
        question_statement=req.question,
        topic=req.topic or "Preclinical Neurodegeneration",
        disease=req.disease or "ALZHEIMER_DISEASE",
        iterations=req.iterations or 10,
    )
    workbenches_registry[wb.workbench_id] = wb
    result = wb.to_dict()
    result["formal"] = _workbench_formal(req)
    return result


def _workbench_formal(req: LaunchWorkbenchRequest):
    """ADR-DISCOVERY-061: evaluate the hypothesis as a formal object against the formal Alzheimer rivals.

    None when the request carries no formal hypothesis and does not ask to formalize the question.
    """
    from api.routers.hypotheses import _to_hypothesis, formal_block, gated_payload, run_formalizer
    from python.discovery import alzheimer_formal_scenario
    from python.discovery.formal_hypothesis import FormalHypothesisError

    rivals = alzheimer_formal_scenario.rival_hypotheses()
    base = {"rivals_status": alzheimer_formal_scenario.STATUS}
    try:
        if req.formal_hypothesis is not None:
            return {**base, "source": "request", **formal_block(_to_hypothesis(req.formal_hypothesis), rivals)}
        if req.formalize_question:
            # ADR-DISCOVERY-064: the formal block only carries an evaluation when the self-consistency gate passes.
            result = run_formalizer(
                req.question, "H-WORKBENCH", alzheimer_formal_scenario.variable_schema(), req.formalizer_samples
            )
            return {**base, "source": "formalizer", **gated_payload(result, rivals)}
    except FormalHypothesisError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    return None


@router.get("/api/discovery/workbench/{workbench_id}")
def get_discovery_workbench(workbench_id: str):
    wb = workbenches_registry.get(workbench_id)
    if not wb:
        raise HTTPException(status_code=404, detail=f"Workbench {workbench_id} not found")
    return wb.to_dict()


@router.post("/api/discovery/inference-scaling/search", dependencies=[Depends(require_api_key)])
def search_inference_scaling_tree(req: EpistemicSearchRequest):
    search_result = EpistemicTreeSearch.search_optimal_trajectory(
        question=req.question, state_space=state_space_omega, beam_width=req.beam_width or 4
    )
    return search_result


@router.post("/api/discovery/lab-in-the-loop/ground-recipe", dependencies=[Depends(require_api_key)])
def ground_lab_recipe(req: LabRecipeRequest):
    recipe = LabInTheLoopAdapter.generate_grounded_recipe(
        prediction_id=req.prediction_id,
        hypothesis_statement=req.hypothesis_statement,
        target_instrument=req.target_instrument or "SPARSE_IMAGING",
    )
    ingestion_result = None
    if req.raw_measurements:
        ingestion_result = LabInTheLoopAdapter.ingest_real_world_measurements(recipe, req.raw_measurements)
    return {"recipe": recipe.to_dict(), "ingestion": ingestion_result}


@router.post("/api/discovery/reliability/audit", dependencies=[Depends(require_api_key)])
def audit_reliability():
    marr_audit = MarrTranslationEngine.audit_tri_level_alignment(
        computational_goal="Maintain cognitive stability across preclinical phase",
        algorithmic_mechanism="Tau propagation on connectome graph",
        implementational_biomarkers=["pTau217", "PET SUVR"],
    )
    audit_res = ReliabilityAuditor.audit_scientific_output(
        hypothesis_statement="Tau pathology propagates along trans-synaptic functional connectome pathways.",
        modus_tollens_deductions=[{"falsification_blame": "NONE"}, {"falsification_blame": "CORE_HYPOTHESIS"}],
        som_hashes=["sha256:adni_cohort_v3_98a72b", "sha256:crs_normalized_87f12e"],
        marr_audit_result=marr_audit,
    )
    return audit_res


@router.post("/api/discovery/campaign/run", dependencies=[Depends(require_api_key)])
def run_discovery_campaign(req: RunCampaignRequest):
    campaign = DiscoveryTeamOrchestrator.initialize_and_run_campaign(
        question=req.question, iterations=req.iterations or 10
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
        "ledger_entries_count": len(campaign.ledger_entries),
    }


@router.get("/api/discovery/state-space")
def get_state_space():
    return {
        "domain": state_space_omega.domain_name,
        "total_combinatorial_states": state_space_omega.total_volume,
        "axes": [
            {
                "name": ax.name,
                "description": ax.description,
                "domain_values": ax.domain_values,
                "cardinality": ax.cardinality,
            }
            for ax in state_space_omega.axes
        ],
    }


@router.get("/api/discovery/biological-programs")
def list_biological_programs():
    programs = [bp.to_dict() for bp in biological_programs_list]
    for p in programs:
        p["auto_explanation"] = AutoExplicabilityEngine.explain_biological_program(p)
    return programs


@router.get("/api/discovery/representations")
def list_representations():
    reps_data = representation_ledger.to_dict()
    reps_data["auto_explanation"] = AutoExplicabilityEngine.explain_representation_space(
        reps_data["candidate_representations"]
    )
    return reps_data


@router.get("/api/discovery/trajectory-evolution")
def get_trajectory_evolution():
    traj_data = TrajectoryEvolutionEngine.run_canonical_tau_trajectory()
    traj_data["auto_explanation"] = AutoExplicabilityEngine.explain_state_space_omega(traj_data["state_space_analysis"])
    return traj_data


@router.get("/api/discovery/questions")
def list_research_questions():
    reps_list = representation_ledger.to_dict()["candidate_representations"]
    hyps_list = [
        {
            "hypothesis_id": h.hypothesis_id,
            "statement": h.statement,
            "representation_id": h.representation_id,
            "marr_level": h.marr_level.value,
            "status": h.status.value,
            "biological_program_id": h.biological_program_id,
        }
        for h in rival_hypotheses
    ]
    preds_list = [
        {
            "prediction_id": dp.prediction_id,
            "statement": dp.statement,
            "favors": dp.favors_hypothesis_id,
            "contradicts": dp.contradicts_hypothesis_ids,
            "threshold": dp.falsification_threshold,
        }
        for dp in discriminative_predictions
    ]
    dv_dict = decomposed_dv.to_dict()
    dv_dict["auto_explanation"] = AutoExplicabilityEngine.explain_decomposed_dv(dv_dict)

    question_statement = "Does pTau217 drive longitudinal cognitive decline via connectome-mediated hub propagation, or via independent vascular/cell-intrinsic collapse?"

    return [
        {
            "question_id": "RQ-2026-004",
            "statement": question_statement,
            "candidate_representations": reps_list,
            "biological_programs": [bp.to_dict() for bp in biological_programs_list],
            "rival_hypotheses": hyps_list,
            "formal_implications": [imp.to_dict() for imp in implications_registry],
            "discriminative_predictions": preds_list,
            "scope_conditions": {
                "valid_domain": ["Preclinical to MCI", "Braak III-IV", "Amyloid positive"],
                "boundary_conditions": ["Severe vascular leucoaraiosis co-pathology"],
            },
            "decomposed_discovery_value": dv_dict,
            "auto_explanation": AutoExplicabilityEngine.explain_research_question(
                question_statement=question_statement, hypotheses=hyps_list, discriminative_pred=preds_list[0]
            ),
        }
    ]


@router.get("/api/discovery/forecasts/list")
def list_prospective_forecasts():
    registry = DiscoveryForecastRegistry()
    audit = registry.audit_integrity()
    return {
        "status": "success",
        "total_forecasts": len(registry.entries),
        "merkle_root_sha256": audit["merkle_root_sha256"],
        "audit_passed": audit["audit_passed"],
        "forecasts": [e.to_dict() for e in registry.entries.values()],
    }


@router.post("/api/discovery/forecasts/register", dependencies=[Depends(require_api_key)])
def register_prospective_forecast(req: RegisterForecastRequest):
    try:
        registry = DiscoveryForecastRegistry()
        pred = QuantitativePredictionWindow(
            target_metric=req.target_metric,
            predicted_interval=req.predicted_interval,
            predicted_point_estimate=req.predicted_point_estimate,
            standard_error_tolerance=req.standard_error_tolerance,
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
            discovery_value=req.discovery_value,
        )
        registry.register_forecast(entry)
        return {
            "status": "sealed_successfully",
            "forecast_id": entry.forecast_id,
            "cryptographic_seal_sha256": entry.cryptographic_seal_sha256,
            "merkle_root_sha256": registry.compute_merkle_root(),
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/api/discovery/forecasts/audit-integrity")
def audit_forecast_integrity():
    registry = DiscoveryForecastRegistry()
    return registry.audit_integrity()


@router.post("/api/discovery/flywheel/cycle", dependencies=[Depends(require_api_key)])
def run_flywheel_cycle_endpoint(req: MathematicalFlywheelCycleRequest):
    """
    Algebraic Structure Compiler & Mathematical Flywheel Engine (ADR-DISCOVERY-046).
    Functorially compiles verified mathematical theorems into executable AI operators
    and calculates auto-bootstrapping flywheel velocity.
    """
    try:
        flywheel = MathematicalFlywheelRunner()
        result = flywheel.run_flywheel_cycle(
            cycle_id=req.cycle_id,
            input_theorems=req.theorems,
        )
        return result.to_dict()
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/api/discovery/tournament/debate-match", dependencies=[Depends(require_api_key)])
def debate_match_endpoint(req: DebateMatchRequest):
    """
    Hypothesis Tournament Arena: Pairwise Debate Match (ADR-DISCOVERY-058).
    Evaluates 2 competing hypotheses along evidence, physical, omega, and falsifiability axes.
    """
    try:
        h_a = TournamentHypothesis(
            hypothesis_id=req.hypothesis_a.hypothesis_id,
            title=req.hypothesis_a.title,
            statement=req.hypothesis_a.statement,
            domain=req.hypothesis_a.domain,
            evidence_score=req.hypothesis_a.evidence_score,
            physical_consistency_score=req.hypothesis_a.physical_consistency_score,
            delta_omega_potential=req.hypothesis_a.delta_omega_potential,
            falsifiability_score=req.hypothesis_a.falsifiability_score,
            elo_rating=req.hypothesis_a.elo_rating,
        )
        h_b = TournamentHypothesis(
            hypothesis_id=req.hypothesis_b.hypothesis_id,
            title=req.hypothesis_b.title,
            statement=req.hypothesis_b.statement,
            domain=req.hypothesis_b.domain,
            evidence_score=req.hypothesis_b.evidence_score,
            physical_consistency_score=req.hypothesis_b.physical_consistency_score,
            delta_omega_potential=req.hypothesis_b.delta_omega_potential,
            falsifiability_score=req.hypothesis_b.falsifiability_score,
            elo_rating=req.hypothesis_b.elo_rating,
        )
        res = PairwiseDebateEngine.debate(
            hyp_a=h_a,
            hyp_b=h_b,
            match_id=req.match_id,
            k_factor=req.k_factor,
        )
        return {
            "match": res.to_dict(),
            "updated_hypothesis_a": h_a.to_dict(),
            "updated_hypothesis_b": h_b.to_dict(),
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/api/discovery/tournament/run-tournament", dependencies=[Depends(require_api_key)])
def run_tournament_endpoint(req: RunTournamentRequest):
    """
    Hypothesis Tournament Arena: Round-Robin Tournament (ADR-DISCOVERY-058).
    Runs multi-agent pairwise debates and produces an Elo-ranked leaderboard.
    """
    try:
        candidates = [
            TournamentHypothesis(
                hypothesis_id=c.hypothesis_id,
                title=c.title,
                statement=c.statement,
                domain=c.domain,
                evidence_score=c.evidence_score,
                physical_consistency_score=c.physical_consistency_score,
                delta_omega_potential=c.delta_omega_potential,
                falsifiability_score=c.falsifiability_score,
                elo_rating=c.elo_rating,
            )
            for c in req.candidates
        ]
        orchestrator = HypothesisEloTournamentOrchestrator()
        report = orchestrator.run_round_robin_tournament(
            tournament_id=req.tournament_id,
            domain=req.domain,
            candidates=candidates,
            rounds=req.rounds,
            k_factor=req.k_factor,
        )
        return report.to_dict()
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
