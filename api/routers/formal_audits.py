"""Formal audit endpoints: symbolic, Lean, categorical, physical and domain engines."""

from pathlib import Path
from typing import Dict, List

from fastapi import APIRouter, Depends, FastAPI, HTTPException, Security  # noqa: F401

from api.routers.discovery import parse_history_node
from api.schemas import (
    AuditExactSymbolicRequest,
    AuditLagrangianProposalRequest,
    AuditMembraneDuhemQuineRequest,
    AuditPerimeterRequest,
    AuditRealityFirewallRequest,
    AuditTheoremRequest,
    AutopoieticSystemAuditRequest,
    BarrierAuditRequest,
    BijectivityAuditRequest,
    BiomacromolecularAuditRequest,
    CategoricalAuditRequest,
    ClaimEvidenceAuditRequest,
    CogenticProofDiscoveryRequest,
    CompileInstrumentRequest,
    CreateMembraneContractRequest,
    DreamFailureTriageRequest,
    DreamRSIReplayRequest,
    EnergyAuditRequest,
    ERAMutateCodeRequest,
    ERASearchCampaignRequest,
    ExtractLimitationsRequest,
    FastMarrRequest,
    FrontierMathTaskInput,
    HakkenEvidenceAuditRequest,
    HakkenLinkPredictionRequest,
    InTurnGoalVerificationRequest,
    LeanFormalizationRequest,
    MathFlywheelCycleRequest,
    MultiscalePredictRequest,
    NotarizeThoughtRequest,
    OversightAuditRequest,
    QueryPheromoneFieldRequest,
    ResultFamilyAuditRequest,
    RunAblationRebuttalRequest,
    ScienceIDEInvariantCheckRequest,
    SimulateWorldModelInterventionRequest,
    SynthesizeContractRequest,
    VegaDecisionRequest,
    VerifyMembraneInvariantsRequest,
)
from api.security import require_api_key
from api.state import (
    epistemic_git_repo,
)
from python.discovery import (
    AbstractionLevel,
    AsymptoticBarrierAuditor,
    AuditedHumanOversightEngine,
    AutopoieticSystemSpec,
    BiomacromolecularCoordinationAuditor,
    BiophysicalContractBuilder,
    BiophysicalDuhemQuineAuditor,
    CandidateEvidenceItem,
    CandidateLemmaStep,
    CatalyticProcess,
    CategoryMorphism,
    CategoryObject,
    CodeVariant,
    CogenticProofOrchestrator,
    CommutativeDiagramAuditor,
    CoordinationGeometry,
    DreamRSIStrategyGate,
    EpistemicCategory,
    EpistemicLemmaStatus,
    EpistemicPheromoneField,
    EpistemicTaskCriticality,
    ERAClosedLoopTreeSearch,
    ERAMethodologicalMutationGenerator,
    EvidencePolarity,
    ExactLemmaNode,
    ExactProofDAG,
    ExactSymbolicCourt,
    FastSystemOneClassifier,
    ForceFieldArchetype,
    HakkenEvidenceGate,
    HumanInteractionTelemetry,
    JevContinuousVerifier,
    LatentPhysicalState,
    LeanFormalizationEngine,
    LimitationResolutionEngine,
    MathematicalMethodFamily,
    MembraneInvariantVerifier,
    MembraneSimulationObservables,
    MetabolicComponent,
    MetalCoordinationCenter,
    MetalIonType,
    MetaRecursiveInstrumentCompiler,
    MorphismType,
    MultiscaleAbstractionEngine,
    MultiscaleStateNode,
    MutationStrategy,
    NonGenerativeEpistemicAuditor,
    PotentialValley,
    PressureCouplingScheme,
    ProtacTernaryComplexSpec,
    RealityContactFirewall,
    ResultFamilyOrchestrator,
    ResultRole,
    RosenAutopoieticClosureAuditor,
    ScienceIDEInvariantRunner,
    SemanticBijectivityAuditor,
    SovereignEpistemicBunker,
    SovereignEvidenceEngine,
    StudyDesignTier,
    VegaPhysicsDecisionEngine,
)
from python.discovery.ablation_rebuttal_engine import (
    AblationRebuttalEngine,
    SimulatedObjection,
)
from python.discovery.backward_execution_synthesizer import (
    BackwardContractSynthesizer,
)
from python.discovery.frontier_math_flywheel import (
    FrontierMathFlywheelEngine,
    FrontierMathProblemTask,
)
from python.discovery.hakken_dream_rsi_engine import (
    BranchOrderingHeuristic,
    DreamRSIOfflineReplayEngine,
    HakkenLiteratureLinkEngine,
    LiteratureHop,
    ScientificDomainType,
    SearchPolicyConfig,
)
from python.discovery.lagrangian_epistemic_engine import (
    DynamicalSystemType,
    LagrangianEpistemicEngine,
    LagrangianProposal,
)
from python.discovery.physical_theorem_court import (
    DeductionRule,
    PhysicalClaimSpec,
    PhysicalCoherenceCourt,
    ProofDependencyDAG,
    ProofLemmaNode,
)
from python.discovery.world_model_adapter import (
    GuardrailType,
    LatentInterventionSpec,
    SafetyConstraintSpec,
    WorldModelEpistemicAdapter,
)

router = APIRouter()

# -----------------------------------------------------------------------------
# 13b. Fast System One Typed Decision Endpoints (Jev Harness - ADR-DISCOVERY-024)
# -----------------------------------------------------------------------------


@router.post("/api/discovery/system-one/classify-marr", dependencies=[Depends(require_api_key)])
def classify_marr_system_one(req: FastMarrRequest):
    """
    Fast System 1 classification of a hypothesis into Marr tri-level hierarchy (<5ms, zero token cost).
    """
    res = FastSystemOneClassifier.classify_marr_level(req.statement)
    return res.to_dict()


@router.post("/api/discovery/system-one/triage-pr", dependencies=[Depends(require_api_key)])
def triage_pr_system_one(diff_text: str):
    """
    Fast System 1 guardrail triage for scientific code diffs (<1ms).
    """
    res = FastSystemOneClassifier.classify_pr_risk(diff_text)
    return res.to_dict()


# -----------------------------------------------------------------------------
# 13c. Twin-Gate Epistemic Harness Endpoints (ADR-DISCOVERY-025)
# -----------------------------------------------------------------------------


@router.post("/api/discovery/harness/verify-in-turn-goal", dependencies=[Depends(require_api_key)])
def verify_in_turn_goal(req: InTurnGoalVerificationRequest):
    """
    Fast System 1 continuous in-turn goal verification for long-horizon loops (<1ms).
    """
    res = JevContinuousVerifier.verify_turn_goal(
        goal_description=req.goal_description,
        action_history=req.action_history or [],
        current_state_payload=req.current_state_payload or {},
    )
    return res.to_dict()


@router.post("/api/discovery/harness/hakken-evidence-audit", dependencies=[Depends(require_api_key)])
def audit_hakken_evidence(req: HakkenEvidenceAuditRequest):
    """
    Hakken-inspired evidence path perturbation audit (PHELInE) evaluating sufficiency, necessity, and temporal drift.
    """
    res = HakkenEvidenceGate.audit_evidence_path(
        hypothesis_id=req.hypothesis_id, path_hops=req.path_hops, temporal_snapshots=req.temporal_snapshots
    )
    return res.to_dict()


@router.post("/api/discovery/harness/dream-classify-failure", dependencies=[Depends(require_api_key)])
def dream_classify_failure(req: DreamFailureTriageRequest):
    """
    Dream-RSI failure classification: distinguishes repairable code bugs from genuine epistemic refutations.
    """
    res = DreamRSIStrategyGate.classify_failure_nature(
        error_traceback=req.error_traceback, execution_context=req.execution_context
    )
    return res.to_dict()


@router.post("/api/discovery/science-ide/execute-invariant-check", dependencies=[Depends(require_api_key)])
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
        tolerance=req.tolerance or 1e-4,
    )
    return res.to_dict()


# -----------------------------------------------------------------------------
# 13d. Biophysical Membrane Dynamics & Duhem-Quine Endpoints (ADR-DISCOVERY-026)
# -----------------------------------------------------------------------------


@router.post("/api/discovery/membrane/create-simulation-contract", dependencies=[Depends(require_api_key)])
def create_membrane_simulation_contract(req: CreateMembraneContractRequest):
    """
    Creates a verifiable biophysical membrane simulation contract (BAX, Abeta42, Tau, TREM2).
    """
    ff = (
        ForceFieldArchetype(req.force_field)
        if req.force_field in [f.value for f in ForceFieldArchetype]
        else ForceFieldArchetype.CHARMM36M
    )
    pc = (
        PressureCouplingScheme(req.pressure_coupling)
        if req.pressure_coupling in [p.value for p in PressureCouplingScheme]
        else PressureCouplingScheme.SEMI_ISOTROPIC_PARRINELLO_RAHMAN
    )

    if req.system_type == "AMYLOID_BETA_PORE":
        contract = BiophysicalContractBuilder.create_amyloid_pore_contract(force_field=ff)
    else:
        contract = BiophysicalContractBuilder.create_bax_membrane_contract(
            force_field=ff,
            pressure_coupling=pc,
            waters_per_lipid=req.waters_per_lipid or 40.0,
            equilibration_length_ns=req.equilibration_length_ns or 100.0,
        )
    return contract.to_dict()


@router.post("/api/discovery/membrane/audit-duhem-quine", dependencies=[Depends(require_api_key)])
def audit_membrane_duhem_quine(req: AuditMembraneDuhemQuineRequest):
    """
    Executes formal Duhem-Quine failure attribution on membrane simulation anomalies (e.g. area per lipid mismatch).
    Differentiates between auxiliary parameter defects (force field, barostat, hydration) and hard-core refutations.
    """
    ff = (
        ForceFieldArchetype(req.force_field)
        if req.force_field in [f.value for f in ForceFieldArchetype]
        else ForceFieldArchetype.CHARMM36M
    )
    pc = (
        PressureCouplingScheme(req.pressure_coupling)
        if req.pressure_coupling in [p.value for p in PressureCouplingScheme]
        else PressureCouplingScheme.SEMI_ISOTROPIC_PARRINELLO_RAHMAN
    )

    if req.system_type == "AMYLOID_BETA_PORE":
        contract = BiophysicalContractBuilder.create_amyloid_pore_contract(contract_id=req.contract_id, force_field=ff)
    else:
        contract = BiophysicalContractBuilder.create_bax_membrane_contract(
            contract_id=req.contract_id,
            force_field=ff,
            pressure_coupling=pc,
            waters_per_lipid=req.waters_per_lipid or 40.0,
        )

    observables = MembraneSimulationObservables(
        observed_area_per_lipid_nm2=req.observed_area_per_lipid_nm2,
        observed_bilayer_thickness_nm=req.observed_bilayer_thickness_nm,
        observed_order_parameter_scd=req.observed_order_parameter_scd,
        observed_pore_radius_nm=req.observed_pore_radius_nm or 0.0,
        energy_drift_ratio=req.energy_drift_ratio or 1e-5,
        entropy_production_rate=req.entropy_production_rate or 0.002,
        equilibration_converged=req.equilibration_converged if req.equilibration_converged is not None else True,
        runtime_ns_completed=req.runtime_ns_completed or 200.0,
    )

    diag = BiophysicalDuhemQuineAuditor.diagnose_simulation_anomaly(contract, observables)
    return diag.to_dict()


@router.post("/api/discovery/membrane/verify-physical-invariants", dependencies=[Depends(require_api_key)])
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
        entropy_production_rate=req.entropy_production_rate or 0.002,
    )

    report = MembraneInvariantVerifier.verify_invariants(contract, observables)
    return report.to_dict()


# -----------------------------------------------------------------------------
# 13e. Epistemic Stigmergy & Meta-Recursive Instrument Engine (ADR-DISCOVERY-027)
# -----------------------------------------------------------------------------


@router.post("/api/discovery/stigmergy/query-pheromone-field", dependencies=[Depends(require_api_key)])
def query_pheromone_field(req: QueryPheromoneFieldRequest):
    """
    Scans the shared EpistemicGitRepo and emits active stigmergic pheromones
    (attractors and repulsors) that guide autonomous agent swarms without a central planner.
    """
    report = EpistemicPheromoneField.scan_git_repository(
        repo=epistemic_git_repo, uncertainty_threshold=req.uncertainty_threshold or 0.60
    )
    return report.to_dict()


@router.post("/api/discovery/stigmergy/compile-instrument", dependencies=[Depends(require_api_key)])
def compile_instrument(req: CompileInstrumentRequest):
    """
    Compiles a candidate hypothesis into an executable simulation world (Meta-Recursive Buehler Loop).
    """
    instrument = MetaRecursiveInstrumentCompiler.compile_hypothesis_into_world(
        representation_id=req.representation_id,
        hypothesis_statement=req.hypothesis_statement,
        key_variables=req.key_variables,
    )
    return instrument.to_dict()


@router.post("/api/discovery/stigmergy/audit-reality-firewall", dependencies=[Depends(require_api_key)])
def audit_reality_firewall(req: AuditRealityFirewallRequest):
    """
    Anti-Collective-Hallucination Firewall: blocks promotion of swarm-derived theories
    to invariant constraints unless RCS >= 2.0 (external empirical grounding).
    """
    report = RealityContactFirewall.audit_promotion_request(
        hypothesis_id=req.hypothesis_id,
        claimed_regularity=req.claimed_regularity,
        rcs_level=req.rcs_level,
        empirical_anchors=req.empirical_anchors,
    )
    return report.to_dict()


# -----------------------------------------------------------------------------
# 13f. Autonomous Physics Megarepo Epistemic Auditor (ADR-DISCOVERY-028)
# -----------------------------------------------------------------------------


@router.post("/api/discovery/physical-court/audit-theorem", dependencies=[Depends(require_api_key)])
def audit_physical_theorem(req: AuditTheoremRequest):
    try:
        court = PhysicalCoherenceCourt()
        dag = ProofDependencyDAG(theorem_id=req.claim_id)
        for lemma in req.lemmas:
            rule_enum = getattr(DeductionRule, lemma.deduction_rule, DeductionRule.ENERGY_ESTIMATE)
            node = ProofLemmaNode(
                lemma_id=lemma.lemma_id,
                title=lemma.title,
                premises=lemma.premises,
                deduction_rule=rule_enum,
                mathematical_statement=lemma.mathematical_statement,
                formal_expression=lemma.formal_expression,
            )
            dag.add_lemma(node)

        claim = PhysicalClaimSpec(
            claim_id=req.claim_id,
            physical_domain=req.physical_domain,
            target_equation=req.target_equation,
            proposed_regularity_class=req.proposed_regularity_class,
            proof_dag=dag,
            claimed_enstrophy_bound_func=lambda Re, t: 50000.0,
        )
        report = court.audit_physical_claim(claim, is_adversarially_singular=req.is_adversarially_singular)
        return report.to_dict()
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/api/discovery/contracts/synthesize-backward", dependencies=[Depends(require_api_key)])
def synthesize_backward_contract(req: SynthesizeContractRequest):
    try:
        custom_path = Path(req.dataset_path) if req.dataset_path else None
        synthesizer = BackwardContractSynthesizer(physical_dataset_path=custom_path)
        traj = synthesizer.execute_ground_truth_trajectory(
            exposure_col=req.exposure_variable, outcome_col=req.outcome_variable
        )
        if not traj.is_fully_executable:
            raise HTTPException(
                status_code=422, detail=f"Trajectory execution failed: {traj.steps[-1].execution_error}"
            )
        contract = synthesizer.invert_trajectory_to_contract(trajectory=traj, marr_level=req.marr_explanation_level)
        return {
            "status": "success",
            "execution_verified": True,
            "contract": contract,
            "som_execution_hash": traj.som_execution_hash,
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/api/discovery/categorical/audit-diagram", dependencies=[Depends(require_api_key)])
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
                symbolic_rule="Tau -> Glycolytic_Failure",
            )
            m_fdg_moca = CategoryMorphism(
                morphism_id="g_fdg_moca",
                domain=obj_fdg,
                codomain=obj_moca,
                morphism_type=MorphismType.CAUSAL_TRANSITION,
                transformation_matrix=np.array([[0.7, 0.0], [0.3, 0.85]]),
                symbolic_rule="Glycolytic_Failure -> Synaptic_Decay",
            )
            direct_comp = np.dot(m_fdg_moca.transformation_matrix, m_tau_fdg.transformation_matrix)
            m_direct = CategoryMorphism(
                morphism_id="h_direct_tau_moca",
                domain=obj_tau,
                codomain=obj_moca,
                morphism_type=MorphismType.EMPIRICAL_MEASUREMENT,
                transformation_matrix=direct_comp,
                symbolic_rule="Tau -> Synaptic_Decay (Direct)",
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
                    **o.get("attributes", {}),
                )
                cat.add_object(c_obj)
                obj_lookup[c_obj.object_id] = c_obj

            for m in req.morphisms:
                if m.domain not in obj_lookup or m.codomain not in obj_lookup:
                    raise ValueError(f"Domain '{m.domain}' or Codomain '{m.codomain}' not found in objects.")

                m_matrix = np.array(m.matrix) if m.matrix else np.eye(2)
                m_type = (
                    MorphismType(m.morphism_type)
                    if m.morphism_type in MorphismType.__members__
                    else MorphismType.CAUSAL_TRANSITION
                )
                cat_m = CategoryMorphism(
                    morphism_id=m.morphism_id,
                    domain=obj_lookup[m.domain],
                    codomain=obj_lookup[m.codomain],
                    morphism_type=m_type,
                    transformation_matrix=m_matrix,
                    symbolic_rule=m.symbolic_rule,
                )
                cat.add_morphism(cat_m)

            path_a = [cat.morphisms[mid] for mid in (req.path_a_morphism_ids or [])]
            path_b = [cat.morphisms[mid] for mid in (req.path_b_morphism_ids or [])]

        axioms_check = cat.verify_category_axioms()
        audit_res = CommutativeDiagramAuditor.audit_diagram_commutativity(
            path_a=path_a, path_b=path_b, tolerance=req.tolerance
        )

        return {"category_axioms": axioms_check, "diagram_audit": audit_res}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/api/discovery/exact-symbolic/audit", dependencies=[Depends(require_api_key)])
def audit_exact_symbolic(req: AuditExactSymbolicRequest):
    """
    ADR-EPISTEMIC-034: Exact Symbolic Dual-Verification & Obstacle-Driven Discovery Engine
    Audits candidate mathematical/physical proofs using SymPy and strict lemma purity checks.
    """
    try:
        dag = ExactProofDAG(theorem_id=req.theorem_id, target_statement=req.target_statement or "")
        for lemma in req.lemmas:
            status_str = lemma.get("status", "ESTABLISHED_AXIOM")
            status = (
                EpistemicLemmaStatus(status_str)
                if status_str in EpistemicLemmaStatus.__members__
                else EpistemicLemmaStatus.ESTABLISHED_AXIOM
            )
            dag.add_lemma(
                ExactLemmaNode(
                    lemma_id=lemma["lemma_id"],
                    statement=lemma.get("statement", ""),
                    status=status,
                    premises=lemma.get("premises", []),
                    symbolic_expression=lemma.get("symbolic_expression"),
                )
            )

        report = ExactSymbolicCourt.audit_exact_proof(
            dag=dag, lhs_target=req.lhs_target, rhs_target=req.rhs_target, sequence_benchmark=req.sequence_benchmark
        )
        return report.to_dict()
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/api/discovery/lagrangian/audit", dependencies=[Depends(require_api_key)])
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
            assumed_symmetries=req.assumed_symmetries or [],
        )
        report = LagrangianEpistemicEngine.audit_lagrangian_proposal(proposal)
        return report.to_dict()
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/api/discovery/ablation-rebuttal/run", dependencies=[Depends(require_api_key)])
def run_ablation_and_rebuttal(req: RunAblationRebuttalRequest):
    """
    ADR-DISCOVERY-037: Automated Theoretical Ablation & Simulated Peer-Review Rebuttal Loop
    Inspired by ScientistTwo (Google Cloud AI, 2026).
    """
    try:
        objs = []
        for o in req.objections or []:
            objs.append(
                SimulatedObjection(
                    reviewer_id=o.get("reviewer_id", "Reviewer-1"),
                    critique_point=o.get("critique_point", ""),
                    severity=o.get("severity", "MINOR"),
                    targeted_subexpression=o.get("targeted_subexpression"),
                )
            )
        dossier = AblationRebuttalEngine.generate_dossier(
            model_id=req.model_id,
            q_name=req.q_name,
            kinetic_str=req.kinetic_str,
            base_potential_str=req.base_potential_str,
            interaction_terms=req.interaction_terms,
            objections=objs,
        )
        return dossier.to_dict()
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/api/discovery/world-model/simulate", dependencies=[Depends(require_api_key)])
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
            constraints.append(
                SafetyConstraintSpec(
                    constraint_id=c.get("constraint_id", f"GUARD-{len(constraints)+1}"),
                    guardrail_type=g_type,
                    target_channel=c["target_channel"],
                    min_safe_value=c.get("min_safe_value"),
                    max_safe_value=c.get("max_safe_value"),
                )
            )

        intervention = LatentInterventionSpec(
            intervention_id=req.intervention_id,
            target_manifold_node=req.target_manifold_node,
            intervention_magnitude=req.intervention_magnitude,
            safety_constraints=constraints,
        )

        result = WorldModelEpistemicAdapter.simulate_latent_intervention(
            intervention=intervention, current_latent_state=req.current_latent_state, macro_subgoals=req.macro_subgoals
        )
        return result.to_dict()
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/api/discovery/multiscale/predict", dependencies=[Depends(require_api_key)])
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


@router.post("/api/discovery/energy-ebm/audit", dependencies=[Depends(require_api_key)])
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


@router.post("/api/discovery/sovereignty/notarize", dependencies=[Depends(require_api_key)])
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


@router.post("/api/discovery/sovereignty/audit-perimeter", dependencies=[Depends(require_api_key)])
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


@router.post("/api/discovery/limitations/extract", dependencies=[Depends(require_api_key)])
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


@router.post("/api/discovery/families/audit", dependencies=[Depends(require_api_key)])
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


@router.post("/api/discovery/evidence/audit", dependencies=[Depends(require_api_key)])
def audit_claim_evidence_endpoint(req: ClaimEvidenceAuditRequest):
    """
    Sub-second Jev-style Evidence Retrieval & Causal Weighting Engine (ADR-DISCOVERY-044).
    Decouples semantic topic relevance from objective epistemic strength and detects publication bias.
    """
    try:
        engine = SovereignEvidenceEngine()
        converted_items: List[CandidateEvidenceItem] = []
        for it in req.evidence_items:
            design_enum = (
                StudyDesignTier(it.study_design)
                if it.study_design in [d.value for d in StudyDesignTier]
                else StudyDesignTier.RETROSPECTIVE_OBSERVATIONAL
            )
            polarity_enum = (
                EvidencePolarity(it.polarity)
                if it.polarity in [p.value for p in EvidencePolarity]
                else EvidencePolarity.AMBIGUOUS
            )
            converted_items.append(
                CandidateEvidenceItem(
                    item_id=it.item_id,
                    title=it.title,
                    snippet=it.snippet,
                    study_design=design_enum,
                    polarity=polarity_enum,
                    sample_size=it.sample_size,
                    p_value=it.p_value,
                    effect_size=it.effect_size,
                    doi_or_source=it.doi_or_source,
                    rcs_level=it.rcs_level,
                    confounding_risk=it.confounding_risk,
                    is_pre_registered=it.is_pre_registered,
                )
            )
        verdict = engine.audit_claim_evidence(
            claim_id=req.claim_id,
            claim_text=req.claim_text,
            evidence_items=converted_items,
            force_system_two=req.force_system_two,
        )
        return verdict.to_dict()
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/api/discovery/barriers/audit", dependencies=[Depends(require_api_key)])
def audit_asymptotic_barrier_endpoint(req: BarrierAuditRequest):
    """
    Asymptotic Barrier Auditor & Parity Obstruction Gate (ADR-DISCOVERY-045).
    Audits proof strategies against proven mathematical No-Go theorems (Selberg parity,
    convexity ceilings, relativization) and prunes futile brute-force branches.
    """
    try:
        family_enum = (
            MathematicalMethodFamily(req.method_family)
            if req.method_family in [f.value for f in MathematicalMethodFamily]
            else MathematicalMethodFamily.CONTOUR_MOMENT_ESTIMATION
        )
        verdict = AsymptoticBarrierAuditor.audit_proof_strategy(
            strategy_id=req.strategy_id,
            target_hypothesis=req.target_hypothesis,
            method_family=family_enum,
            target_threshold=req.target_threshold,
            proposed_intermediate_result=req.proposed_intermediate_result,
        )
        return verdict.to_dict()
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/api/discovery/lean/audit", dependencies=[Depends(require_api_key)])
def audit_lean_theorem_endpoint(req: LeanFormalizationRequest):
    """
    Lean 4 Interactive Theorem Prover Gate & Formalization Engine (ADR-DISCOVERY-047).
    Audits Lean source code for absence of 'sorry', verifies kernel soundness,
    and synthesizes scaffolding if only prose is provided.
    """
    try:
        code_to_audit = req.lean_code or ""
        if not code_to_audit and req.hypothesis_statement:
            code_to_audit = LeanFormalizationEngine.synthesize_lean4_scaffolding(
                theorem_name=req.theorem_name,
                hypothesis_statement=req.hypothesis_statement,
                symbolic_identity=req.symbolic_identity,
            )
        report = LeanFormalizationEngine.audit_lean_source(
            theorem_name=req.theorem_name,
            lean_code=code_to_audit,
        )
        return report.to_dict()
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/api/discovery/lean/audit-bijectivity", dependencies=[Depends(require_api_key)])
def audit_bijectivity_endpoint(req: BijectivityAuditRequest):
    """
    Semantic Bijectivity & Formal Drift Gate (ADR-DISCOVERY-048).
    Audits claim-to-formal isomorphism between natural prose and Lean theorem.
    Detects goalpost shifting, Sobolev regularity drift, or assumption weakening.
    """
    try:
        prose_spec = SemanticBijectivityAuditor.extract_prose_specifications(
            prose_text=req.prose_statement,
            claim_name=req.claim_name,
        )
        lean_spec = SemanticBijectivityAuditor.extract_lean_specifications(
            lean_code=req.lean_code,
            expected_theorem_name=req.claim_name,
        )
        verdict = SemanticBijectivityAuditor.audit_bijective_alignment(
            prose_spec=prose_spec,
            lean_spec=lean_spec,
            frozen_signature_hash=req.frozen_signature_hash,
        )
        return verdict.to_dict()
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/api/discovery/oversight/audit", dependencies=[Depends(require_api_key)])
def audit_oversight_endpoint(req: OversightAuditRequest):
    """
    Audited Human Oversight & Anti-Rubber-Stamping Gate (ADR-DISCOVERY-049).
    Audits human interaction telemetry against passive automation bias,
    neutralizes consensus bias, and generates cryptographic Merkle proofs.
    """
    try:
        try:
            crit = EpistemicTaskCriticality[req.task_criticality]
        except KeyError:
            crit = EpistemicTaskCriticality.PARADIGMATIC_NOVELTY

        telemetry = HumanInteractionTelemetry(
            reviewer_id=req.reviewer_id,
            dwell_time_seconds=req.dwell_time_seconds,
            counterexamples_inspected=req.counterexamples_inspected,
            human_notes_length_chars=len(req.explicit_causal_rationale),
            substantive_modifications_made=bool(req.explicit_causal_rationale),
            explicit_causal_rationale=req.explicit_causal_rationale,
            answered_inspection_challenge=req.answered_inspection_challenge,
        )
        record = AuditedHumanOversightEngine.evaluate_oversight_integrity(
            claim_id=req.claim_id,
            task_criticality=crit,
            ai_recommendation=req.ai_recommendation,
            human_decision=req.human_decision,
            telemetry=telemetry,
            ai_critique_text=req.ai_critique_text,
            is_mathematically_sound=req.is_mathematically_sound,
            conserves_physical_invariants=req.conserves_physical_invariants,
        )
        return record.to_dict()
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/api/discovery/cogentic/run-proof-discovery", dependencies=[Depends(require_api_key)])
def run_cogentic_proof_discovery(req: CogenticProofDiscoveryRequest):
    """
    Automated Proof Discovery via Multi-Agent Prove-Verify Harness (ADR-DISCOVERY-050).
    Inspired by Google Research's Cogentic framework (arXiv:2609.40324, 2026).
    """
    try:
        orchestrator = CogenticProofOrchestrator(max_model_budget=req.max_model_budget)
        steps = None
        if req.candidate_steps:
            steps = [
                CandidateLemmaStep(
                    step_id=s.step_id,
                    target_conjecture_id=s.target_conjecture_id,
                    statement=s.statement,
                    symbolic_expression=s.symbolic_expression,
                    premises=s.premises,
                    unstated_assumptions=s.unstated_assumptions,
                    prover_direction=s.prover_direction,
                    round_index=s.round_index,
                )
                for s in req.candidate_steps
            ]
        report = orchestrator.run_proof_discovery(
            conjecture_id=req.conjecture_id,
            target_statement=req.target_statement,
            prover_directions=req.prover_directions,
            candidate_steps=steps,
        )
        return report.to_dict()
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/api/discovery/biomacromolecular/audit-complex", dependencies=[Depends(require_api_key)])
def audit_biomacromolecular_complex(req: BiomacromolecularAuditRequest):
    """
    Biomacromolecular & PROTAC Ternary Complex Coordination Audit (ADR-DISCOVERY-051).
    Evaluates steric clashes, metal coordination geometry, thermodynamic cooperativity,
    and H-JEPA latent world model physical invariants.
    """
    try:
        metal_centers = []
        if req.metal_centers:
            for mc in req.metal_centers:
                metal_type = MetalIonType[mc.metal_type]
                geom = CoordinationGeometry[mc.geometry]
                metal_centers.append(
                    MetalCoordinationCenter(
                        ion_id=mc.ion_id,
                        metal_type=metal_type,
                        coordinating_atom_count=mc.coordinating_atom_count,
                        geometry=geom,
                        observed_mean_bond_length_angstrom=mc.observed_mean_bond_length_angstrom,
                        expected_bond_length_angstrom=mc.expected_bond_length_angstrom,
                        tolerance_angstrom=mc.tolerance_angstrom,
                    )
                )

        spec = ProtacTernaryComplexSpec(
            complex_id=req.complex_id,
            target_protein=req.target_protein,
            e3_ligase=req.e3_ligase,
            linker_length_atoms=req.linker_length_atoms,
            warhead_kd_nm=req.warhead_kd_nm,
            e3_kd_nm=req.e3_kd_nm,
            ternary_kd_nm=req.ternary_kd_nm,
            min_atom_distance_angstrom=req.min_atom_distance_angstrom,
            metal_centers=metal_centers,
        )

        report = BiomacromolecularCoordinationAuditor.audit_complex(
            complex_spec=spec,
            latent_prior_state=req.latent_prior_state,
        )
        return report.to_dict()
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/api/discovery/autopoietic/audit-closure", dependencies=[Depends(require_api_key)])
def audit_autopoietic_system_closure(req: AutopoieticSystemAuditRequest):
    """
    Rosen Autopoietic Closure & Causal Organization Audit (ADR-DISCOVERY-052).
    Evaluates whether a living system is closed to efficient causation while remaining
    thermodynamically dissipative and open to material throughput.
    """
    try:
        comp_dict = {
            c.component_id: MetabolicComponent(
                component_id=c.component_id,
                name=c.name,
                is_external_nutrient=c.is_external_nutrient,
                is_dissipated_waste=c.is_dissipated_waste,
                molecular_mass_da=c.molecular_mass_da,
            )
            for c in req.components
        }

        proc_list = [
            CatalyticProcess(
                process_id=p.process_id,
                name=p.name,
                material_inputs=p.material_inputs,
                efficient_catalysts=p.efficient_catalysts,
                material_products=p.material_products,
                entropy_production_rate=p.entropy_production_rate,
            )
            for p in req.processes
        ]

        spec = AutopoieticSystemSpec(
            system_id=req.system_id,
            system_name=req.system_name,
            components=comp_dict,
            processes=proc_list,
        )

        report = RosenAutopoieticClosureAuditor.audit_system(spec)
        return report.to_dict()
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/api/discovery/vega/simulate-decision", dependencies=[Depends(require_api_key)])
def simulate_vega_decision(req: VegaDecisionRequest):
    """
    Simulate a physics-based typed decision using the Vega dynamical potential landscape (ADR-DISCOVERY-053).
    Rolls a particle through candidate outcome valleys with friction damping.
    """
    try:
        valleys = [
            PotentialValley(
                valley_id=v.valley_id,
                category_name=v.category_name,
                center_coordinate=v.center_coordinate,
                depth=v.depth,
                width_sigma=v.width_sigma,
                prior_weight=v.prior_weight,
            )
            for v in req.valleys
        ]

        res = VegaPhysicsDecisionEngine.simulate_decision(
            domain=req.domain,
            valleys=valleys,
            initial_position=req.initial_position,
            initial_velocity=req.initial_velocity,
            friction_gamma=req.friction_gamma,
            mass=req.mass,
            dt=req.dt,
            max_steps=req.max_steps,
            abstain_barrier_threshold=req.abstain_barrier_threshold,
        )
        return res.to_dict()
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/api/discovery/hakken/predict-links", dependencies=[Depends(require_api_key)])
def predict_hakken_links(req: HakkenLinkPredictionRequest):
    try:
        domain_enum = ScientificDomainType(req.domain)
        hops = [
            LiteratureHop(
                source_entity=h.source_entity,
                target_entity=h.target_entity,
                relation=h.relation,
                literature_citations_count=h.literature_citations_count,
                temporal_stability_score=h.temporal_stability_score,
                confidence_weight=h.confidence_weight,
            )
            for h in req.hops
        ]
        candidate = HakkenLiteratureLinkEngine.predict_undocumented_link(
            candidate_id=req.candidate_id,
            domain=domain_enum,
            source=req.source_entity,
            target=req.target_entity,
            predicted_relation=req.predicted_relation,
            hops=hops,
            direct_literature_hits=req.direct_literature_hits,
        )
        return candidate.to_dict()
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/api/discovery/dream-rsi/replay-policy", dependencies=[Depends(require_api_key)])
def replay_dream_rsi_policy(req: DreamRSIReplayRequest):
    try:
        root_node = parse_history_node(req.history_tree)
        policy_cfg = SearchPolicyConfig(
            policy_id=req.policy.policy_id,
            branch_ordering=BranchOrderingHeuristic(req.policy.branch_ordering),
            worker_concurrency=req.policy.worker_concurrency,
            pruning_reward_threshold=req.policy.pruning_reward_threshold,
            max_tokens_budget=req.policy.max_tokens_budget,
            stop_early_on_reward=req.policy.stop_early_on_reward,
        )
        result = DreamRSIOfflineReplayEngine.replay_policy_on_tree(root_node, policy_cfg)
        return result.to_dict()
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/api/discovery/math-flywheel/audit-admissibility", dependencies=[Depends(require_api_key)])
def audit_math_problem_admissibility(req: FrontierMathTaskInput):
    try:
        task = FrontierMathProblemTask(
            task_id=req.task_id,
            title=req.title,
            problem_statement_prose=req.problem_statement_prose,
            formal_lean_statement=req.formal_lean_statement,
            reference_solution_code=req.reference_solution_code,
            domain_topic=req.domain_topic,
            source_repository=req.source_repository,
            metadata=req.metadata,
        )
        report = FrontierMathFlywheelEngine.audit_problem_admissibility(task)
        return report.to_dict()
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/api/discovery/math-flywheel/run-cycle", dependencies=[Depends(require_api_key)])
def run_math_flywheel_cycle(req: MathFlywheelCycleRequest):
    try:
        engine = FrontierMathFlywheelEngine()
        tasks = [
            FrontierMathProblemTask(
                task_id=t.task_id,
                title=t.title,
                problem_statement_prose=t.problem_statement_prose,
                formal_lean_statement=t.formal_lean_statement,
                reference_solution_code=t.reference_solution_code,
                domain_topic=t.domain_topic,
                source_repository=t.source_repository,
                metadata=t.metadata,
            )
            for t in req.problem_tasks
        ]
        result = engine.execute_closed_loop_flywheel_cycle(
            cycle_id=req.cycle_id,
            problem_tasks=tasks,
            submitted_solutions=req.submitted_solutions,
        )
        return result.to_dict()
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/api/discovery/era/mutate-code", dependencies=[Depends(require_api_key)])
def mutate_era_code(req: ERAMutateCodeRequest):
    try:
        strat = MutationStrategy(req.mutation_strategy)
        parent = CodeVariant(
            variant_id=req.parent_variant_id,
            parent_id=None,
            generation_depth=req.generation_depth,
            mutation_strategy=strat,
            parameter_spec=req.parameter_spec,
            code_snippet=req.code_snippet,
        )
        mutated = ERAMethodologicalMutationGenerator.mutate_candidate(
            parent=parent,
            new_variant_id=req.new_variant_id,
            target_strategy=strat,
        )
        return mutated.to_dict()
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/api/discovery/era/run-search-campaign", dependencies=[Depends(require_api_key)])
def run_era_search_campaign(req: ERASearchCampaignRequest):
    try:
        searcher = ERAClosedLoopTreeSearch()
        report = searcher.run_campaign(
            campaign_id=req.campaign_id,
            dataset_name=req.dataset_name,
            ground_truth_time_series=req.ground_truth_time_series,
            time_step_days=req.time_step_days,
            surge_threshold_quantile=req.surge_threshold_quantile,
            max_iterations=req.max_iterations,
            beam_width=req.beam_width,
        )
        return report.to_dict()
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
