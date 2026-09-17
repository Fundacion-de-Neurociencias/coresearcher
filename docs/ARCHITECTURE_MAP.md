# Architecture Map: CoResearcher System Topology
**Version**: 4.0.0 (Canonical Reference Map)  
**Status**: Active System Topology  
**Last Updated**: September 2026

---

## 🗺️ System Overview & Dual Core Architecture

CoResearcher operates through a **Dual-Core Architecture**:
1. **The Open Protocol & Traceability Core (`python/observer/`)**: Observes, extracts, and normalizes public and private scientific activity into an immutable, citable Scientific Activity Ledger deposited to Zenodo with registered DOIs.
2. **The Autonomous Epistemic Discovery & Verification Engine (`python/discovery/`)**: Autonomously discovers invariants, prunes hypothesis state spaces (\(\Omega\)), validates against physical patient cohorts (Zero Mocking), audits physical conservation DAGs, and computes categorical holonomy invariance.

```
                                  ┌──────────────────────────────────────────────────────────┐
                                  │                  CORESEARCHER ECOSYSTEM                  │
                                  └────────────────────────────┬─────────────────────────────┘
                                                               │
                     ┌─────────────────────────────────────────┴─────────────────────────────────────────┐
                     ▼                                                                                   ▼
      ┌─────────────────────────────┐                                                     ┌─────────────────────────────┐
      │     CORESEARCHER PROTOCOL    │                                                     │      DISCOVERY ENGINE       │
      │   (Traceability & Ledger)   │                                                     │   (Epistemics & Invariants) │
      └──────────────┬──────────────┘                                                     └──────────────┬──────────────┘
                     │                                                                                   │
     ┌───────────────┴───────────────┐                                                   ┌───────────────┴───────────────┐
     ▼                               ▼                                                   ▼                               ▼
┌──────────────┐              ┌──────────────┐                                    ┌──────────────┐              ┌──────────────┐
│ Git Scanner  │              │ Zenodo       │                                    │ 9 Discovery  │              │ Categorical  │
│ & Primitives │              │ Publisher    │                                    │ Agents       │              │ & Physical   │
│ (ACTION,     │              │ (DOI Release)│                                    │ (Miner,      │              │ Courts       │
│ CLAIM, EVID) │              │              │                                    │ Popper, ...) │              │ (Leray, Hom) │
└──────────────┘              └──────────────┘                                    └──────────────┘              └──────────────┘
```

---

## 📦 Directory & Component Map

### 1. `python/discovery/` — Autonomous Epistemic Discovery Engine

| Component File | Primary Class / Interface | Responsibility | Key Invariant / Output |
| :--- | :--- | :--- | :--- |
| `categorical_epistemic_engine.py` | `CategoricalEpistemicEngine`, `CommutativeDiagramAuditor` | Category theory algebra of thought, functors, adjoints \(\mathcal{F} \dashv \mathcal{G}\) | Commutative diagrams, zero holonomy defect (\(\|\Delta M\| \le 10^{-5}\)) |
| `physical_theorem_court.py` | `PhysicalCoherenceCourt`, `AdversarialSingularitySearchEngine` | Deductive DAG proof audits against thermodynamic, mass-energy & Navier-Stokes bounds | Elimination of unphysical singularities |
| `epistemic_pr_auditor.py` | `ScientificEpistemicPRAuditor` | Self-hosted GitHub PR reviewer checking for data leakage and \(p\)-hacking | Blockage of methodological traps in scientific PRs |
| `backward_execution_synthesizer.py`| `BackwardContractSynthesizer` | ToolGrad-inspired analytical trajectory inversion from empirical datasets | Deterministic contracts with verified execution hashes |
| `real_cohort_empirical_pipeline.py`| `RealCohortEmpiricalPipeline` | Zero-mocking empirical discovery pipeline running on physical patient data | Direct OLS regression, residual anomaly extraction |
| `real_cohort_campaign_runner.py` | `RealCohortDiscoveryRunner` | Cross-cohort validation runner (MetaboAD \(N=66\) + ADNI holdouts) | Verification of metabolic gating invariance |
| `universal_discovery_engine.py` | `UniversalLatentDiscoveryEngine` | Invariant discovery across 4 physical regimes (Neuro, Astro, Econ, Ocean) | Universal mathematical scaling laws |
| `latent_factor_discovery.py` | `LatentFactorDiscoveryEngine` | Unsupervised latent decomposition and dimensionality reduction | Isolation of underlying hidden generative axes |
| `bayesian_surprise_engine.py` | `BayesianSurpriseEngine` | Quantifies information gain (KL divergence) over epistemic priors | Mathematical scoring of epistemic surprise |
| `research_budget_engine.py` | `ResearchBudgetLedger` | Tracks economic/computational costs with diminishing returns | Gated allocation of research resources |
| `long_horizon_campaign_engine.py` | `LongHorizonCampaignEngine` | Multi-cycle autonomous research campaigns with hypothesis branching | Autonomous scientific trajectory evolution |
| `traces_epistemic_adapter.py` | `TracesEpistemicAdapter` | Evaluates discovery trajectories across 5 rigor dimensions | Metrics: \(DV\), \(RCS\), \(FRI\), \(SG\), \(CSR\) |
| `adversarial_destruction_test.py` | `AdversarialDestructionEngine` | 50-case adversarial stress suite (Simpson's paradox, collider bias, circularity) | Interception rate \(> 95\%\) against deceptive data |
| `unknown_mechanism_benchmark.py` | `UnknownMechanismBenchmark` | 100-world blind abduction challenge without domain-specific priors | Pure abduction score from raw observables |
| `retrospective_time_split_benchmark.py`| `RetrospectiveTimeSplitBenchmark`| Historical discovery benchmark strictly quarantined at Cutoff \(\le 2018\) | Historical reproduction without temporal data leakage |
| `discovery_forecast_registry.py` | `DiscoveryForecastRegistry` | Pre-registered timestamped prospective discovery forecasts | Brier score tracking and calibration curves |
| `failure_engine.py` | `ScientificFailureEngine` | Duhem-Quine failure attribution (Auxiliary Assumption vs Hard Core) | Diagnostics of failed predictions and anomalies |
| `defeated_hypotheses_graveyard.py` | `HypothesisGraveyard` | Repository and registry of falsified hypotheses and autopsies | Prevention of redundant scientific dead-ends |
| `reality_distance.py` | `RealityDistanceEvaluator` | Hierarchical reality distance evaluation (Dry \(\to\) Damp \(\to\) Wet) | Substrate distance metrics |
| `reality_contact_score.py` | `RealityContactEvaluator` | Computes Reality Contact Score (\(RCS = 0 \dots 4\)) | Quantification of empirical grounding |
| `grounded_search_sensor.py` | `GroundedSearchSensor`, `PaperAgentMCPAdapter` | Cryptographic evidence source lineage with SHA-256 fingerprinting & Paper2Agent MCP client | Anti-hallucination source verification, virtual author discovery & analytical tool execution (\(RCS=2\)) |
| `constraint_box.py` | `ConstraintBoxBenchmark` | Benchmark for unknown ground-truth discovery in synthetic worlds | Disentangling discovery from biological memory |
| `constraint_court.py` | `ConstraintCourt` | Adversarial trial between Prosecutor and Defender agents | Invariant constraint promotion decisions |
| `constraint_discovery_engine.py` | `ConstraintDiscoveryEngine` | Extracts statistical boundaries from cross-cohort data | Boundary generation and stress testing |
| `scientific_git_history.py` | `EpistemicGitRepo` | Epistemic version control tracking scientific state mutations | Commits of hypotheses, evidence, and constraints |
| `discovery_workbench.py` | `DiscoveryWorkbench`, `WorkbenchRunner` | Unified object orchestrating a discovery from question to finding | End-to-end execution of discovery workflows |
| `discovery_teams.py` | 9 Canonical Discovery Agents | Constraint-led multi-agent collaboration team | Full cycle: Miner \(\to\) Popper \(\to\) Auditor |
| `inference_time_scaling.py` | `EpistemicTreeSearch` | Monte Carlo Tree Search over reasoning and experimental paths | Inference-time computational scaling for science |
| `lab_in_the_loop_adapter.py` | `LabInTheLoopAdapter` | Generates wet-lab experimental protocols and audits physical feasibility | Closed-loop wet-lab integration |
| `reliability_auditor.py` | `ReliabilityAuditor` | Evaluates reliability, consensus, and replicability across runs | Confidence and consensus scoring |
| `marr_engine.py` | `MarrTranslationEngine` | Tri-level translation (Computational, Algorithmic, Implementational) | Prevention of category errors in biological theories |
| `biological_programs_catalog.py` | `BiologicalProgram` | Library of reusable canonical biological programs | Standardized mechanistic building blocks |
| `scientific_logic.py` | `PopperEngine`, `DeductionEngine` | Modus Tollens deductive logic and implication matrices | Rigorous deductive falsification |
| `state_space.py` | `StateSpaceOmega` | Combinatorial hypothesis space with explicit volume pruning | Mathematical definition of scientific search volume |
| `epistemic_trajectory.py` | `Representation`, `EpistemicTrajectory` | Foundational representation primitives and trajectory ledger | First-class trajectory tracking |
| `trajectory_evolution.py` | `TrajectoryEvolutionEngine` | Multi-iteration evolution of scientific theories | Evolutionary trajectory optimization |
| `auto_explicability.py` | `AutoExplicabilityEngine` | Real-time dynamic self-explanation generation | Human-interpretable scientific narratives |
| `epistemic_gap_detector.py` | `EpistemicGapDetector` | Identifies gaps, omissions, and paradigm residues in literature | Target discovery opportunities |

---

### 2. `python/observer/` — Open Protocol & Scientific Traceability Core

| Component File | Primary Class / Interface | Responsibility | Key Output |
| :--- | :--- | :--- | :--- |
| `git_scanner.py` | `reconstruct_ledger` | Ingests git commits, branches, and PRs into an activity ledger | `ScientificLedger` |
| `intellectual_extractor.py` | `IntellectualExtractor` | Extracts scientific intent and units from commit messages and code | Scientific units and rationale |
| `scientific_ledger.py` | `ScientificLedger` | Append-only graph of scientific actions, workstreams, contributors | Audit-grade provenance records |
| `zenodo_publisher.py` | `ZenodoPublisher` | Packages and deposits scientific ledgers to Zenodo via REST API | Formal citable Zenodo **DOI** |
| `github_connector.py` | `GitHubConnector` | Ingests public and private GitHub activity | Raw repo event streams |
| `crossref_connector.py` | `CrossRefConnector` | Resolves DOIs and retrieves bibliographic metadata | CrossRef metadata records |
| `openalex_connector.py` | `OpenAlexConnector` | Connects to OpenAlex for academic graph exploration | OpenAlex entity nodes |
| `entity_resolver.py` | `EntityResolver` | Resolves ORCID (researchers) and ROR (institutions) | Disambiguated scientific identities |

---

### 3. `api/server.py` — Production REST Server & Webhook Gateway

| Endpoint Group | Method & Path | Backing Module | Purpose |
| :--- | :--- | :--- | :--- |
| **System Health** | `GET /api/health` | `server.py` | State space volume, representation ledger count, system status |
| **Categorical Engine**| `POST /api/discovery/categorical/audit-diagram` | `categorical_epistemic_engine.py` | Audits reasoning diagrams for holonomy defects and commutativity |
| **GitHub CI Webhook**| `POST /api/discovery/github/audit-pr-webhook` | `epistemic_pr_auditor.py` | Epistemic peer review of pull requests (data leakage, conservation) |
| **ToolGrad Inversion**| `POST /api/discovery/toolgrad/synthesize-contract` | `backward_execution_synthesizer.py`| Synthesizes research contracts from empirical data trajectories |
| **Physical Theorem** | `POST /api/discovery/physical/audit-claim` | `physical_theorem_court.py` | Audits claims against physical conservation laws and DAG proofs |
| **Real Cohort Disk** | `POST /api/discovery/cohorts/run-real-pipeline` | `real_cohort_empirical_pipeline.py`| Executes empirical discovery on physical patient data |
| **Universal Invariant**| `POST /api/discovery/universal/cross-domain-invariants`| `universal_discovery_engine.py` | Evaluates invariant scaling laws across 4 physical domains |
| **Long-Horizon** | `POST /api/discovery/campaign/run-long-horizon` | `long_horizon_campaign_engine.py` | Multi-cycle autonomous research campaign execution |
| **Bayesian Surprise** | `POST /api/discovery/bayesian/evaluate-surprise` | `bayesian_surprise_engine.py` | Quantifies KL divergence and information surprise |
| **Adversarial Stress**| `POST /api/discovery/adversarial/run-destruction-test` | `adversarial_destruction_test.py` | 50-case adversarial destruction suite |
| **Unknown Mechanism** | `POST /api/discovery/unknown-mechanism/run-100-worlds-benchmark`| `unknown_mechanism_benchmark.py` | 100-world blind abduction benchmark |
| **Retrospective** | `POST /api/discovery/retrospective/run-time-split-benchmark`| `retrospective_time_split_benchmark.py`| Historical discovery benchmark with temporal cutoff \(\le 2018\) |
| **TRACES Rigor** | `POST /api/discovery/traces/evaluate-epistemic-rigor` | `traces_epistemic_adapter.py` | Epistemic meta-metric evaluation (DV, RCS, FRI, SG, CSR) |

---

## 🔗 External Contracts & Ecosystem Boundaries

```
┌─────────────────────────────────────────────────────────────────────────────────────────────┐
│                                   THE SCIENTIFIC TRINITY                                    │
│                                                                                             │
│  ┌────────────────────────┐       ┌────────────────────────┐       ┌─────────────────────┐  │
│  │      CORESEARCHER      │       │       DATAAILAB        │       │       EDITXT        │  │
│  │   (Epistemic Reasoner  │◄─────►│    (Empirical Solver   │◄─────►│  (Editorial Press   │  │
│  │   & Theorem Verifier)  │       │       & GPU Worker)    │       │   & Peer Review)    │  │
│  └────────────────────────┘       └────────────────────────┘       └─────────────────────┘  │
│               │                                                               │             │
│               └─────────────────────── GitHub CI Webhook ─────────────────────┘             │
│                                (Code Audit + Manuscript Anchors)                            │
└─────────────────────────────────────────────────────────────────────────────────────────────┘
```

1. **CoResearcher $\leftrightarrow$ DataAILab Contract (`ARCH-002`)**:
   - **Boundary**: CoResearcher never performs raw GPU training, gradient descent, or heavy tensor simulations.
   - **Role**: CoResearcher sends analytical contracts (`ToolExecutionStep`, `StateSpaceOmega`) to DataAILab. DataAILab returns physical matrices, statistical parameters, and execution hashes.
2. **CoResearcher $\leftrightarrow$ EdiTXT Contract (`ARCH-003`)**:
   - **Boundary**: CoResearcher never edits prose manuscripts, formats typography, or generates paper styling.
   - **Role**: CoResearcher supplies verified claims, mathematical proofs, and cryptographic hashes (`SOM-SHA256`). EdiTXT binds manuscript sentences to these data anchors and flags stale claims when data changes.
3. **GitHub CI Handshake**:
   - Both platforms listen to the same PR webhooks: CoResearcher verifies code epistemic integrity; EdiTXT verifies manuscript claim stability.

---

## 📜 Architectural Governance & Self-Documentation Mandate

To maintain permanent alignment between the codebase and its architectural specifications:

> **Permanent Operational Rule**: Every agent or engineer who implements or modifies a substantial module, algorithm, benchmark, or API route in CoResearcher is **strictly obligated** to document the change in:
> 1. `docs/ARCHITECTURE.md` (Master architecture & layer specifications)
> 2. `docs/ARCHITECTURE_MAP.md` (System topology & component inventory)
> 3. `docs/CONSTITUTION_INDEX.md` (Constitutional and ADR index)
> 4. `README.md` (Repository overview and operational quick-start)
> 
> No feature is considered **Done** until all canonical documentation files reflect the changes.\n