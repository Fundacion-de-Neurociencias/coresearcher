# CoResearcher Master Architecture (2026 Canonical Specification)
**Version**: 4.0.0 (Epistemic Discovery, Physical Theorem Court & Categorical Algebra)  
**Status**: Canonical Reference Architecture  
**Scope**: Full Scientific System (`observer`, `discovery`, `api`, `benchmarks`, `ecosystem`)

---

## 🏛️ Executive Architectural Summary

**CoResearcher** is the **Autonomous Epistemic Discovery and Verification Engine** for open science. Unlike conventional "AI Scientist" tools that hallucinate ungrounded hypotheses or act as bibliometric aggregators:

> **CoResearcher is NOT an answer system.**  
> **CoResearcher is NOT a bibliographic search engine.**  
> **CoResearcher is NOT a generative text bot.**  
> **CoResearcher IS an auditable engine for the progressive reduction of the possible scientific state space (\(\Omega\)) through empirical constraints, deductive falsifications, multi-substrate reality contact, and categorical commutative invariance.**

```
                                    ┌─────────────────────────────────────────────────────────┐
                                    │               SCIENTIFIC STATE SPACE (Ω)                │
                                    │               (Combinatorial Hypothesis Volume)         │
                                    └───────────────────────────┬─────────────────────────────┘
                                                                │
                                                                ▼
┌─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│ LAYER 0: CONSTITUTIONAL & EPISTEMIC FOUNDATIONS                                                                         │
│ • Popperian Falsification (Modus Tollens)          • State Space Pruning (ΔVol)       • Marr Tri-Level Translation      │
│ • Discovery Value Metric (DV)                      • Reality Contact Score (RCS 0-4)  • Duhem-Quine Blame Attribution   │
└───────────────────────────────────────────────────────────────┬─────────────────────────────────────────────────────────┘
                                                                │
                                                                ▼
┌─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│ LAYER 1: PROTOCOL, OBSERVATORY & PROVENANCE                                                                             │
│ • Git Scanner & Semantic Compiler                 • Zenodo Publisher & DOI Engine    • CrossRef / PubMed / OpenAlex     │
│ • Scientific Activity Ledger (Audit Lineage)      • Cryptographic SOM Fingerprints   • MCP Evidence Protocol            │
└───────────────────────────────────────────────────────────────┬─────────────────────────────────────────────────────────┘
                                                                │
                                                                ▼
┌─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│ LAYER 2: AUTONOMOUS EPISTEMIC DISCOVERY & CONSTRAINTS                                                                   │
│ • 9 Canonical Discovery Agents                    • Epistemic Tree Search (MCTS)     • Constraint Court (Litigants)     │
│ • Real-Cohort Disk Pipeline (Neurodiagnoses)      • Universal Invariants (4 Domains) • Bayesian Surprise & Budget     │
│ • Long-Horizon Multi-Cycle Campaigns              • Substrate Distance (Dry→Damp→Wet)• Defeated Hypotheses Graveyard   │
└───────────────────────────────────────────────────────────────┬─────────────────────────────────────────────────────────┘
                                                                │
                                                                ▼
┌─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│ LAYER 3: FORMAL VERIFICATION, THEOREM COURTS & CATEGORICAL ALGEBRA                                                      │
│ • Physical Conservation DAGs (Leray-Hopf, Thermo) • ToolGrad Backward Inversion      • Epistemic PR Auditor (CI Webhook)│
│ • Epistemic Categories (Obs, Th)                  • Structure-Preserving Functors    • Commutative Holonomy Defect ||Δ||│
│ • Adjunction Duality (Abduction ⊣ Deduction)       • Strict Zero-Mocking Enforcement  • Adversarial Stress Traps         │
└───────────────────────────────────────────────────────────────┬─────────────────────────────────────────────────────────┘
                                                                │
                                                                ▼
┌─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│ LAYER 4: RUNTIME, REST API & ECOSYSTEM INTEROPERABILITY                                                                 │
│ • FastAPI Production Server (`api/server.py`)     • GitHub Webhook Receiver          • DataAILab Contract (ARCH-002)    │
│ • EdiTXT Text Anchor Handshake (ARCH-003)         • Benchmark Suite (TRACES, 100-W)  • Zenodo Sandbox / Release Engine  │
└─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┘
```

---

## 🔬 Layer 0: Constitutional & Epistemic Foundations

### 1. State Space \(\Omega\) & Volume Pruning
Scientific discovery is formulated as search and contraction over a high-dimensional combinatorial state space \(\Omega = \prod_{i=1}^k A_i\):
- **Axes (\(A_i\))**: Biomarker thresholds, kinetic rates, topological parameters, clinical endpoints.
- **Volume Metric**: Total volume \(V(\Omega) = \prod \text{range}(A_i)\).
- **Pruning Principle**: Any valid invariant constraint \(C\) excludes a subspace \(\Omega_{\text{excluded}} \subset \Omega\). The **Combinatorial Discovery Value** is measured by:
  $$\text{CDV} = \frac{V(\Omega_{\text{excluded}})}{V(\Omega_{\text{initial}})}$$

### 2. The Discovery Value Metric (\(DV\))
Defined in **ADR-DISCOVERY-005**, the epistemic value of a discovery is not subjective novelty, but an objective scalar:
$$DV = \alpha \cdot \text{Pruning}(\Omega) + \beta \cdot \text{Falsifiability} + \gamma \cdot \text{Compression} + \delta \cdot \text{Transferability}$$
Where:
- **\(\text{Pruning}(\Omega)\)**: Fraction of hypothesis space excluded (\([0, 1]\)).
- **\(\text{Falsifiability}\)**: Ratio of potential counterexamples to total state evaluations.
- **\(\text{Compression}\)**: Reduction in description length of observations (Kolmogorov proxy).
- **\(\text{Transferability}\)**: Cross-cohort or cross-domain survival rate without parameter inflation.

### 3. Reality Contact Score (\(RCS\))
Hypotheses must physically earn reality across 5 rigorous tiers:
- **\(RCS = 0\) (Bibliographic)**: Semantic derivation from literature without data contact.
- **\(RCS = 1\) (In Silico Replicated)**: Replicated across independent retrospective cohorts.
- **\(RCS = 2\) (Prospective Blind)**: Confirmed on pre-registered holdout data with timestamped lock.
- **\(RCS = 3\) (Empirical Perturbation)**: Validated against physical perturbation experiments or wet-lab measurements.
- **\(RCS = 4\) (Promoted Invariant)**: Inscribed into the permanent scientific ledger as a universal domain invariant.

### 4. Marr Tri-Level Epistemic Translation
Every biological or physical explanation must be decomposed into David Marr's three levels of analysis (`python/discovery/marr_engine.py`):
1. **Computational Level**: What is the goal of the process? What invariant problem is being solved?
2. **Algorithmic Level**: What representations and transformations compute this solution? (e.g., connectome graph diffusion).
3. **Implementational Level**: What physical substrate carries out the algorithm? (e.g., tau phospho-epitope folding, microglial phagocytosis).

---

## 📡 Layer 1: Protocol, Observatory & Provenance

Located in `python/observer/`, this layer coordinates verifiable scientific activity without third-party dependencies.

### 1. Git Scanner & Semantic Compiler
- **Module**: `python/observer/git_scanner.py`, `intellectual_extractor.py`.
- **Function**: Ingests raw Git commits, PRs, issues, and code diffs; compiles them into canonical scientific primitives:
  - `QUESTION-XXXXXX`: Strategic research inquiries.
  - `ACTION-XXXXXX`: Executable analytical steps and experimental runs.
  - `CLAIM-XXXXXX`: Atomic, falsifiable assertions.
  - `EVID-XXXXXX`: Verifiable data artifacts linked to claims.

### 2. Scientific Activity Ledger & Zenodo Engine
- **Module**: `python/observer/scientific_ledger.py`, `zenodo_publisher.py`.
- **Function**: Maintains an immutable, append-only graph of research progress. Allows exporting the entire trajectory as a citable research object deposited directly to **Zenodo** via REST API, obtaining a formal **DOI**.

### 3. Federated Connectors
- **Connectors**: GitHub, Zenodo, CrossRef, PubMed, OpenAlex.
- **Identity Federation**: ORCID (researchers) and ROR (research institutions) federated identifiers.

---

## 🔍 Layer 2: Autonomous Epistemic Discovery & Constraint Engine

Located in `python/discovery/`, this layer executes autonomous scientific discovery, falsification, and cohort validation.

### 1. The 9 Canonical Epistemic Discovery Agents
Defined in **ADR-DISCOVERY-007** (`python/discovery/discovery_teams.py`):
1. **Constraint Miner Agent**: Scans empirical datasets to extract raw statistical boundaries.
2. **Biological Program Mapper Agent**: Maps constraints to canonical mechanistic programs (`biological_programs_catalog.py`).
3. **Hypothesis Generator Agent**: Proposes mechanistic explanations satisfying active constraints.
4. **Alternative Generator Agent**: Obligatorily generates competing rival hypotheses (**ADR-DISCOVERY-003**).
5. **Marr Classifier Agent**: Decomposes hypotheses across Computational, Algorithmic, and Implementational levels.
6. **Prediction Engine Agent**: Formulates discriminative, quantitative predictions that tease apart rivals.
7. **Popper Auditor Agent**: Evaluates Modus Tollens falsification conditions (`scientific_logic.py`).
8. **Scope Auditor Agent**: Defines boundary rupture conditions and validity limits (**ADR-DISCOVERY-004**).
9. **Discovery Value Auditor Agent**: Calculates the multi-factorial \(DV\) score.

### 2. Epistemic Tree Search (Inference-Time Scaling)
- **Module**: `python/discovery/inference_time_scaling.py`.
- **Function**: Executes Monte Carlo Tree Search (\(MCTS\)) over scientific reasoning trajectories. Branches on experimental decisions, pruning paths that lead to low discovery value or unresolvable contradictions.

### 3. Adversarial Constraint Court
- **Module**: `python/discovery/constraint_court.py`.
- **Architecture**: A simulated judicial trial between two adversarial agents:
  - **Prosecutor**: Searches for counterexamples, subgroup failures, and data outliers to defeat the hypothesis.
  - **Defender**: Proposes auxiliary assumptions or scope boundaries that salvage the core invariant.
  - **Verdict**: `PROMOTED_INVARIANT`, `CONDITIONAL_SCOPE`, or `FALSIFIED_REJECTED` (Bayes Factor \(K \ge 3.0\)).

### 4. 100% Real-Cohort Empirical Discovery Pipeline
- **Module**: `python/discovery/real_cohort_empirical_pipeline.py`.
- **Dataset**: Direct empirical connection to physical patient files on disk (`C:\Users\usuario\Neurodiagnoses Ecosystem\data\metaboad_atn_processed.csv`, \(N=66\) patients).
- **Guarantee**: **Zero Mocking Directive**. Direct statistical regression, residual anomaly extraction, and cross-cohort holdout validation without synthetic stubs.

### 5. Universal Cross-Domain Invariant Discovery
- **Module**: `python/discovery/universal_discovery_engine.py`.
- **Domains**: Validates mathematical invariance across 4 diverse physical regimes:
  1. **Neuroscience**: Connectome diffusion & metabolic reserve gating.
  2. **Astrophysics**: Stellar degenerate cooling & Chandrasekhar mass limits.
  3. **Macroeconomics**: Sovereign debt spreads & inflation-liquidity coupling.
  4. **Marine Ecology**: Phytoplankton trophic transfer & thermal stratification.

### 6. Duhem-Quine Failure Engine & Hypotheses Graveyard
- **Modules**: `python/discovery/failure_engine.py`, `defeated_hypotheses_graveyard.py`.
- **Diagnostics**: When a prediction fails, the engine isolates whether the blame lies on the **Hard Core** (fatal falsification) or an **Auxiliary Assumption** (instrumental error, calibration drift). Failed hypotheses are embalmed in the Graveyard with complete autopsy records to prevent redundant rediscovery.

---

## ⚖️ Layer 3: Formal Verification, Theorem Courts & Categorical Algebra

This layer guarantees mathematical rigor, physical law conservation, and algebraic truth preservation.

### 1. Physical Theorem Court & Conservation DAGs
- **Module**: `python/discovery/physical_theorem_court.py`.
- **Function**: Audits scientific proposals against fundamental conservation laws:
  - **Mass-Energy Conservation**: \(\sum \Delta E = 0\).
  - **Thermodynamic Entropy**: \(dS \ge 0\).
  - **Leray-Hopf Navier-Stokes Bounds**: Energy dissipation \(\nu > 0\).
- **Adversarial Singularity Search**: Searches for unphysical singularities (\(t \to 0\), \(x \to \infty\)) where proposed theories collapse.

### 2. ToolGrad Backward Analytical Synthesizer
- **Module**: `python/discovery/backward_execution_synthesizer.py`.
- **Methodology**: Inverts empirical data into analytical tool-use chains. Executes forward empirical trajectories on physical datasets and synthesizes deterministic research contracts with cryptographically verified execution hashes.

### 3. Scientific Epistemic PR Auditor
- **Module**: `python/discovery/epistemic_pr_auditor.py`.
- **Role**: Automated, self-hosted GitHub Peer Review CI. Scans pull request diffs for:
  - **`DATA_LEAKAGE`**: Preprocessors fitted globally before cross-validation splits.
  - **`CONSERVATION_VIOLATION`**: Physical constants or boundaries violated in code.
  - **`STATISTICAL_P_HACKING`**: Multiple testing loops without FDR / Bonferroni corrections.

### 4. Categorical Epistemic Engine (The Algebra of Thought)
- **Module**: `python/discovery/categorical_epistemic_engine.py`.
- **Mathematical Framework**:
  - **Category of Observations (\(\mathbf{Obs}\))** & **Category of Theories (\(\mathbf{Th}\))**.
  - **Objects**: Invariant scientific states.
  - **Morphisms**: Causal transitions, proofs, and measurements with matrix representations.
  - **Axioms**: Identity (\(\text{id}_B \circ f = f = f \circ \text{id}_A\)) and Associativity (\(h \circ (g \circ f) = (h \circ g) \circ f\)).
  - **Diagram Commutativity & Holonomy Defect**:
    $$\text{Holonomy Defect} = \|\mathcal{P}_{\text{direct}} - \mathcal{P}_{\text{mediated}}\|_F$$
    A scientific reasoning diagram commutes iff holonomy defect \(\le 10^{-5}\). Non-zero defects objectively detect reverse-causality fallacies and omitted variable bias.
  - **Epistemic Adjunction**: Dual functor pair Abduction \(\mathcal{F} \dashv \mathcal{G}\) Deduction:
    $$\text{Hom}_{\mathbf{Th}}(\mathcal{F}(X), Y) \cong \text{Hom}_{\mathbf{Obs}}(X, \mathcal{G}(Y))$$

---

## 🌐 Layer 4: Runtime, REST API & Ecosystem Interoperability

Located in `api/server.py`, this layer exposes CoResearcher to the external world, agents, and paired platforms.

### 1. FastAPI REST Server Endpoints
- **Health & Metadata**: `GET /api/health` (Reports state space volume, representation ledger count, active domains).
- **Categorical Diagram Audit**: `POST /api/discovery/categorical/audit-diagram` (Computes holonomy defect across arbitrary reasoning graphs).
- **GitHub PR CI Webhook**: `POST /api/discovery/github/audit-pr-webhook` (Receives PR diffs and posts epistemic findings).
- **ToolGrad Contract Synthesis**: `POST /api/discovery/toolgrad/synthesize-contract` (Inverts datasets into verifiable contracts).
- **Physical Theorem Audit**: `POST /api/discovery/physical/audit-claim` (Validates claims against physical DAGs).
- **Real Cohort Pipeline**: `POST /api/discovery/cohorts/run-real-pipeline` (Executes disk-based clinical discovery).
- **Long-Horizon Campaign**: `POST /api/discovery/campaign/run-long-horizon` (Runs multi-cycle autonomous research).
- **Adversarial Destruction**: `POST /api/discovery/adversarial/run-destruction-test` (50-case stress test).
- **Unknown Mechanism Challenge**: `POST /api/discovery/unknown-mechanism/run-100-worlds-benchmark` (100 blind worlds).
- **Retrospective Time-Split**: `POST /api/discovery/retrospective/run-time-split-benchmark` (Historical discovery frontier).
- **TRACES Meta-Audit**: `POST /api/discovery/traces/evaluate-epistemic-rigor` (5-dimensional epistemic profile).
- **Paper2Agent MCP Query**: `POST /api/discovery/paper-agent/query` (Queries external virtual author paper agents by topic).
- **Paper2Agent MCP Execute**: `POST /api/discovery/paper-agent/execute` (Executes analytical methods on virtual author agents with cryptographic SOM hash and RCS = 2 promotion).
- **Agora Open Branches Index**: `GET /api/discovery/git/open-branches` (Inspects active parallel research frontiers).
- **Agora Verified Claims Index**: `GET /api/discovery/git/verified-claims` (Lists verified invariants available for cross-branch synthesis).
- **Agora Branch Creation**: `POST /api/discovery/git/branch/create` (Initializes an explicit branch rooted at an existing verified commit).
- **Agora Epistemic Cherry-Pick**: `POST /api/discovery/git/branch/cherry-pick` (Adopts verified claims across branches with parent DAG lineage).
- **Fast System One Marr Classifier**: `POST /api/discovery/system-one/classify-marr` (Sub-millisecond typed tri-level classification).
- **Fast System One PR Triage**: `POST /api/discovery/system-one/triage-pr` (Instant guardrail detection for data leakage and unphysical code).
- **Continuous In-Turn Goal Verification**: `POST /api/discovery/harness/verify-in-turn-goal` (Sub-millisecond Jev System 1 step verification for /goal agent loops).
- **Hakken Evidence Path Perturbation**: `POST /api/discovery/harness/hakken-evidence-audit` (PHELInE sufficiency, necessity, and temporal drift audit).
- **Dream-RSI Failure Classification**: `POST /api/discovery/harness/dream-classify-failure` (Isolates repairable code/OOM bugs from genuine epistemic refutations).
- **ScienceIDE Simulation Invariant Check**: `POST /api/discovery/science-ide/execute-invariant-check` (Verifies physical conservation laws and tolerances on executable patches).
- **Membrane Simulation Contract**: `POST /api/discovery/membrane/create-simulation-contract` (Formalizes biophysical lipid bilayer contracts with SOM-SHA256 provenance).
- **Membrane Duhem-Quine Audit**: `POST /api/discovery/membrane/audit-duhem-quine` (Decomposes simulation discrepancies into auxiliary parameter vs core refutations).
- **Membrane Physical Invariants**: `POST /api/discovery/membrane/verify-physical-invariants` (Audits Hamiltonian energy drift, incompressibility, and entropy).
- **Stigmergy Pheromone Field Query**: `POST /api/discovery/stigmergy/query-pheromone-field` (Scans git history to emit attractors and repulsors for autonomous agent swarms).
- **Meta-Recursive Instrument Compilation**: `POST /api/discovery/stigmergy/compile-instrument` (Compiles candidate hypotheses into executable simulation worlds).
- **Reality Contact Firewall Audit**: `POST /api/discovery/stigmergy/audit-reality-firewall` (Blocks promotion of swarm-derived theories to invariant laws unless RCS >= 2.0).
- **Physics Megarepo Peer Review**: `POST /api/discovery/physics/audit-megarepo` (Autonomous peer review of massive physics corpora across 8 subdisciplines).

### 2. Paper2Agent (Nature 2026) MCP Federation
Implemented in `python/discovery/grounded_search_sensor.py` (`PaperAgentMCPAdapter`), this subsystem enables active discovery campaigns to interact directly with external published research papers turned into virtual authors via the Model Context Protocol (MCP):
- **Live Tool Invocation**: Rather than treating published papers as inert PDF text, CoResearcher discovers papers exposing analytical tools (e.g. `compute_connectome_diffusion`, `score_genetic_perturbation`, `evaluate_metabolic_glycolytic_reserve`).
- **Cryptographic Provenance**: Every tool execution produces a reproducible payload and an immutable SHA-256 SOM execution hash.
- **Reality Contact Level**: Executing an external paper's verified analytical code on new data earns an empirical grounding level of \(RCS = 2\) (`EMPIRICAL_EXECUTION_GROUNDED`).
- **Ecosystem Trinity Demarcation**:
  - **EdiTXT**: Acts as the *Producer/Host* of the Paper Agent upon manuscript peer review and release.
  - **CoResearcher**: Acts as the *Consumer/Auditor* that queries and executes Paper Agents during autonomous discovery and falsification campaigns.

### 3. Agora Shared Memory & Epistemic Git Federation (ADR-DISCOVERY-023)
Inspired by NVIDIA Agora (2026), `python/discovery/scientific_git_history.py` (`AgoraSharedIndex`, `EpistemicGitRepo`) equips decentralized multi-agent teams with shared persistent memory over git commits:
- **Open-Branches Index**: Tracks all open hypothesis branches and exploration frontiers in real time, preventing concurrent workers from repeating identical or overlapping investigations.
- **Verified-Claims Index**: Catalogs all surviving empirical findings and invariant boundary conditions (\(RCS \ge 2\)), allowing new agents to inherit verified parents immediately.
- **Cross-Branch Epistemic Cherry-Picking**: Enables an agent exploring one physiological axis (e.g. vascular clearance) to cherry-pick an invariant constraint discovered by another agent on an orthogonal axis (e.g. microglial phagocytosis) and forge a unified hybrid model without re-running base experiments.

### 4. Fast System One Typed Decision Harness (ADR-DISCOVERY-024)
Inspired by TypeSafe AI's Jev model, `python/discovery/fast_system_one_classifier.py` introduces a ultra-fast, zero-cost System 1 decision tier into CoResearcher:
- **Zero-Cost Local Mode**: Executes typed, probabilistic classifications in \(< 1\text{ ms}\) using deterministic semantic heuristics, eliminating costly generative LLM calls for structured choices.
- **Optional Jev Cloud Integration**: Supports TypeSafe AI's unmetered-output Jev endpoint (\(\$0.042\) per million input tokens) if credentials are provided in `.env`.
- **System 1 / System 2 Division of Labor**:
  - **System 1 (Jev / Fast Classifier)**: Fast Marr classification, PR guardrail triage, branch action routing.
  - **System 2 (Deep Epistemic Core)**: Deductive Modus Tollens, Physical Conservation DAGs, Categorical Holonomy Defect calculation.

### 5. Twin-Gate Epistemic Harness & Continuous Verification (ADR-DISCOVERY-025)
Implemented in `python/discovery/twin_gate_harness.py`, this engine establishes a dual-gate defense and continuous verification pipeline:
- **Hakken Evidence Validity Gate (PHELInE & THiGERLLM)**: Audits proposed scientific relationships before allocating resources. Perturbs multi-step evidence paths to quantify **Sufficiency** (path alone supports prediction), **Necessity** (confidence drop upon path ablation), and **Temporal Stability Drift** across literature milestones.
- **Dream-RSI Strategy & Robustness Gate**: Prevents premature search tree pruning by rigorously classifying failures into `REPAIRABLE_CODE_ERROR` (tensor dimension mismatch, CUDA OOM, syntax bug) versus `GENUINE_EPISTEMIC_FALSIFICATION` (conservation breach, empirical refutation). Automatically adapts MCTS search breadth and stalling intervention.
- **ScienceIDE Invariant Sandbox**: Executes scientific patches against pinned simulation codebases, measuring physical conservation quantities (mass continuity, Leray-Hopf dissipation, thermodynamic entropy) instead of relying solely on unit test diffs.
- **Jev Continuous In-Turn Verifier**: Evaluates step completion, progress scoring, and loop stalling detection in \(< 0.01\text{ ms}\) per agent turn, enabling massively scalable test-time verification compute for `/goal` agent loops.

### 6. Biophysical Membrane Dynamics & Duhem-Quine Simulation Auditor (ADR-DISCOVERY-026)
Implemented in `python/discovery/membrane_dynamics_auditor.py`, this subsystem formalizes molecular dynamics (MD) workflows for membrane biophysics:
- **Target Systems**: BAX pro-apoptotic pore opening, Amyloid-\(\beta_{42}\) & Tau membrane permeabilization, and TREM2 microglial lipid raft dynamics.
- **Formal Duhem-Quine Root-Cause Diagnostics**: When simulation observables (e.g. area per lipid \(A_L\), bilayer thickness \(D_{HH}\), order parameter \(S_{CD}\)) diverge from experimental reference constraints, algebraically isolates whether the blame lies in:
  - Auxiliary simulation artifacts (`BAROSTAT_SURFACE_TENSION_MISCOUPLING`, `OSMOTIC_DEHYDRATION`, `EQUILIBRATION_TRUNCATION`, `FORCE_FIELD_VDW_OVERATTRACTION`).
  - Or genuine core refutations (`HARD_CORE_CONFORMATION_REFUTED` / `CORE_HYPOTHESIS_FATAL`).
- **Physical Invariant Auditing**: Verifies symplectic Hamiltonian energy conservation (\(\le 10^{-4}/\text{ns}\)), bilayer incompressibility, and thermodynamic entropy.
- **DataAILab Contract Demarcation (`ARCH-002`)**: Generates cryptographically verifiable `SOM-SHA256` simulation contracts, allowing DataAILab to execute heavy GPU molecular dynamics while CoResearcher acts strictly as the epistemic auditor and verifier.

### 7. Epistemic Stigmergy & Meta-Recursive Instrument Engine (ADR-DISCOVERY-027)
Implemented in `python/discovery/epistemic_stigmergy.py`, this engine draws inspiration from Markus Buehler's SwarmWorld (MIT, arXiv 2608.26081) and harmonizes with GeneForge's `StigmergicPheromoneField` and AIDataLab's `ExecutionSnapshot Lineage DAG`:
- **Epistemic Pheromone Field**: Transforms the shared scientific git history (`EpistemicGitRepo` / `AgoraSharedIndex`) into active stigmergic signals without requiring a central orchestrator:
  - `INVARIANT_CONSOLIDATION`: Attracts formalizer agents to cherry-pick verified claims into parent lineage trees.
  - `EPISTEMIC_GAP_EXPLORATION`: Attracts hypothesis explorers and miners toward unresolved open branch frontiers.
  - `ADVERSARIAL_ARBITRATION`: Attracts Popper agents to execute Modus Tollens refutation audits on high-uncertainty claims.
  - `REFUTATION_REPULSION`: Strongly repels all agents from re-traversing falsified hypothesis dead-ends recorded in the graveyard.
- **Meta-Recursive Instrument Compiler**: Implements the Buehler recursive loop (\(\text{Representation} \to \text{Instrument} \to \text{Simulated World} \to \text{Law}\)). Compiles candidate theoretical claims into executable `ConstraintBox` simulation worlds with formal logical rules (`NECESSARY_CONDITION`, `SUFFICIENT_TRIGGER`, `BOUNDARY_THRESHOLD`).
- **Reality Contact Firewall (Anti-Collective-Hallucination Gate)**: Strict guardrail forbidding closed-world simulation hallucinations. Blocks promotion of any emergent regularities derived by the agent swarm to active invariant constraints unless grounded with an empirical Reality Contact Score of \(RCS \ge 2.0\) (external physical anchors / prospective cohorts).

### 8. Universal Physics Megarepo Epistemic Auditor & Peer Review Engine (ADR-DISCOVERY-028 v2.0)
Implemented in `python/discovery/physics_corpus_auditor.py`, this engine instrumentalizes CoResearcher as an independent, objective expert scientific reviewer for massive, single-author physical corpora across **ALL 10 Major Divisions and 42 Canonical Subdisciplines of Physics**:
- **Universal Ontology Crawler & Classifier**: Recursively crawls repositories, categorizing chapters and multimodal artifacts across Fundamental High Energy, Gravitation/Cosmology, Quantum Optics/Info, Nuclear/Plasma, Condensed Matter, Thermodynamics/Complexity, Classical/Fluids, Astrophysics, Interdisciplinary Biophysics/Geophysics, and Technical Patents.
- **Multimodal Artifact Ingestion**: Handles theoretical LaTeX manuscripts, mathematical proofs, tabular and binary datasets (`.csv`, `.dat`, `.parquet`, `.h5`, `.fits`), simulation solvers (`.py`, `.jl`, `.cpp`), and technical patent claims.
- **Anti-Perpetuum-Mobile Patent Gate**: Strictly intercepts overunity assertions ($\text{COP} > 1.0$), propellantless/reactionless drives, and Carnot bound breaches in technical patent filings.
- **Dimensional Homogeneity Checker**: Applies the Buckingham $\Pi$ theorem to equations, catching dimensionally incompatible additions (e.g. Energy + Force).
- **Fast System 1 Triage Tier**: Delivers instant Marr level classification and code risk screening (unseeded stochasticity in simulations, NaN/Inf handling, lookahead bias) in \(< 1\text{ ms}\).
- **Deep System 2 Mathematical Proof Verification**: Employs `PhysicalCoherenceCourt` to audit `ProofDependencyDAG`s, intercepting circular lemma cycles (`REJECTED_CIRCULAR_LEMMA`) and unproven axiomatic assertions (`REJECTED_UNPROVEN_AXIOM`).
- **Deep System 2 Conservation & Reality Firewall**: Audits physical conservation laws (Hamiltonian energy drift, Leray-Hopf dissipation, thermodynamic entropy) and enforces `RealityContactFirewall` (\(RCS \ge 2.0\) with external physical anchors like NIST, CERN, CODATA) before certifying experimental claims.
- **Editorial Peer Review Dossier**: Synthesizes verified invariants vs rejected claims into a cryptographically anchored (`SOM-SHA256`) citable ReviewGraph and objective editorial publication readiness judgment.
- **(v3.0) LocalAIAdapter — Multi-Protocol Air-Gapped AI**: `call_laya()` (System 1) and `call_local_ia()` (System 2) auto-detect protocol (OpenAI-compat → Ollama-native → deterministic fallback). Zero cloud, 100% local. Configurable via `LAYA_ENDPOINT` / `LOCAL_IA_ENDPOINT` env vars.
- **(v3.0) `audit_chapter_deep()`**: Full Laya + MarrTranslationEngine + BayesianSurpriseEngine + CommutativeDiagramAuditor pipeline for theoretical chapters. Holonomy defect gate (\(\delta < 10^{-3}\)). NEVER penalizes novelty.
- **(v3.0) `audit_simulation_deep()`**: DreamRSIStrategyGate (bug vs. genuine falsification) + ScienceIDEInvariantRunner (mass/energy/entropy conservation) + HakkenEvidenceGate (PHELInE perturbation) for simulation solvers.
- **(v3.0) `run_adversarial_stress_test()`**: 50-case AdversarialDestructionEngine; genuinely falsified claims auto-logged to HypothesisGraveyard.
- **(v3.0) `prioritize_audit_by_pheromone()`**: EpistemicPheromoneField reorders audit queue by conflict intensity — high-dispute zones first.
- **(v3.0) Persistent Pipeline**: `scripts/audit_physics_megarepo_full.py` — checkpoint/resume, walks entire megarepo, Ctrl+C safe, writes per-item JSON verdicts + final report.

### 9. Ecosystem Demarcation (The Scientific Trinity)
Defined in `docs/ECOSYSTEM_BOUNDARIES.md`:
- **CoResearcher**: The **Epistemic Auditor & Reasoner** (Formal logic, constraints, theorem courts, categorical invariance, provenance).
- **DataAILab**: The **Empirical Solver & Executor** (High-performance GPU computing, heavy numerical training, raw data pipelines).
- **EdiTXT**: The **Editorial & Peer Review Press** (Manuscript generation, figure binding, text anchor verification, peer review workflows).

---

## 📊 Comprehensive Benchmarking Suite

| Benchmark Suite | Source File | Purpose | Key Metric |
| :--- | :--- | :--- | :--- |
| **Retrospective Time-Split** | `retrospective_time_split_benchmark.py` | Tests whether the engine reproduces historic discoveries with data cutoff \(\le 2018\) | Reproduction accuracy & zero temporal leakage |
| **100-World Unknown Mechanism** | `unknown_mechanism_benchmark.py` | Tests autonomous abduction across 100 blind worlds with hidden physical laws | Abduction recall without biological priors |
| **50-Case Adversarial Destruction** | `adversarial_destruction_test.py` | Attacks the engine with 10 trap archetypes (Simpson's paradox, collider bias, circularity) | Trap interception rate (\(> 95\%\)) |
| **TRACES Epistemic Meta-Audit** | `traces_epistemic_adapter.py` | Evaluates discovery trajectories across 5 rigor dimensions | \(DV\), \(RCS\), \(FRI\), \(SG\), \(CSR\) |
| **Categorical Reasoning Suite** | `categorical_epistemic_engine.py` | Verifies category axioms and holonomy defect across causal diagrams | Holonomy defect \(\le 10^{-5}\) on sound paths |

---

## 🔒 Permanent Architectural Invariants

1. **Zero-Mocking Mandate**: Biological and physical validation must run against real physical datasets on disk; mock objects are strictly forbidden in production pipelines.
2. **Generator \(\ne\) Verifier**: The generation of hypotheses must always remain decoupled from the verification and falsification engine.
3. **Mandatory Rivalry**: No hypothesis may be evaluated without at least one actively competing alternative hypothesis.
4. **Reality Contact Priority**: Mathematical elegance cannot substitute for empirical contact (\(RCS \ge 1\)).
5. **Continuous Self-Documentation Mandate**: Every substantial evolution, new engine, or architectural modification must be immediately and exhaustively recorded in the canonical documentation files (`docs/ARCHITECTURE.md`, `docs/ARCHITECTURE_MAP.md`, `docs/CONSTITUTION_INDEX.md`, `README.md`) as an integral part of completion.\n