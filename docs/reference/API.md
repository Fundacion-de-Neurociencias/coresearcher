# REST API reference

> Generated from [`schemas/openapi.json`](../../schemas/openapi.json). Do not edit by hand.

Operations: 109. Interactive documentation is served at `/docs` when the API runs.

Authentication: write operations (`POST`, `PUT`, `DELETE`) require the `X-API-Key` header
matching `CORESEARCHER_API_KEY`. Read operations are public on the bound interface.
Webhooks are verified with the `X-Hub-Signature-256` header.

| Method | Path | Auth | Operation |
| --- | --- | --- | --- |
| `POST` | `/api/audit/evidence` | API key | Audit Empirical Evidence |
| `POST` | `/api/discovery/ablation-rebuttal/run` | API key | Run Ablation And Rebuttal |
| `POST` | `/api/discovery/adversarial/run-destruction-test` | API key | Run Adversarial Destruction Test |
| `POST` | `/api/discovery/anomalies/detect-and-cluster` | API key | Detect And Cluster Anomalies |
| `POST` | `/api/discovery/autopoietic/audit-closure` | API key | Audit Autopoietic System Closure |
| `POST` | `/api/discovery/barriers/audit` | API key | Audit Asymptotic Barrier Endpoint |
| `POST` | `/api/discovery/bayesian-surprise/evaluate` | API key | Evaluate Bayesian Surprise |
| `GET` | `/api/discovery/biological-programs` | Public | List Biological Programs |
| `POST` | `/api/discovery/biomacromolecular/audit-complex` | API key | Audit Biomacromolecular Complex |
| `POST` | `/api/discovery/campaign/run` | API key | Run Discovery Campaign |
| `POST` | `/api/discovery/campaigns/long-horizon-run` | API key | Run Long Horizon Campaign |
| `POST` | `/api/discovery/campaigns/run-heterogeneous-suite` | API key | Run Heterogeneous Discovery Suite |
| `POST` | `/api/discovery/categorical/audit-diagram` | API key | Audit Categorical Diagram |
| `POST` | `/api/discovery/cogentic/run-proof-discovery` | API key | Run Cogentic Proof Discovery |
| `POST` | `/api/discovery/constraint-box/run-benchmark` | API key | Run Constraint Box Benchmark |
| `POST` | `/api/discovery/constraints/mine-and-verify` | API key | Mine And Verify Constraint |
| `POST` | `/api/discovery/contracts/synthesize-backward` | API key | Synthesize Backward Contract |
| `POST` | `/api/discovery/court/adjudicate` | API key | Adjudicate Constraint Court |
| `POST` | `/api/discovery/dream-rsi/replay-policy` | API key | Replay Dream Rsi Policy |
| `POST` | `/api/discovery/energy-ebm/audit` | API key | Audit Theory Energy Ebm |
| `POST` | `/api/discovery/era/mutate-code` | API key | Mutate Era Code |
| `POST` | `/api/discovery/era/run-search-campaign` | API key | Run Era Search Campaign |
| `POST` | `/api/discovery/evidence/audit` | API key | Audit Claim Evidence Endpoint |
| `POST` | `/api/discovery/exact-symbolic/audit` | API key | Audit Exact Symbolic |
| `POST` | `/api/discovery/failure/diagnose-root-cause` | API key | Diagnose Prediction Failure |
| `POST` | `/api/discovery/families/audit` | API key | Audit Result Family Endpoint |
| `POST` | `/api/discovery/flywheel/cycle` | API key | Run Flywheel Cycle Endpoint |
| `GET` | `/api/discovery/forecasts/audit-integrity` | Public | Audit Forecast Integrity |
| `GET` | `/api/discovery/forecasts/list` | Public | List Prospective Forecasts |
| `POST` | `/api/discovery/forecasts/register` | API key | Register Prospective Forecast |
| `POST` | `/api/discovery/git/branch/cherry-pick` | API key | Cherry Pick Agora Claim |
| `POST` | `/api/discovery/git/branch/create` | API key | Create Agora Branch |
| `GET` | `/api/discovery/git/dead-ends` | Public | Get Agora Dead Ends |
| `GET` | `/api/discovery/git/open-branches` | Public | Get Agora Open Branches |
| `GET` | `/api/discovery/git/verified-claims` | Public | Get Agora Verified Claims |
| `GET` | `/api/discovery/graveyard/list` | Public | List Defeated Hypotheses |
| `POST` | `/api/discovery/hakken/predict-links` | API key | Predict Hakken Links |
| `POST` | `/api/discovery/harness/dream-classify-failure` | API key | Dream Classify Failure |
| `POST` | `/api/discovery/harness/hakken-evidence-audit` | API key | Audit Hakken Evidence |
| `POST` | `/api/discovery/harness/verify-in-turn-goal` | API key | Verify In Turn Goal |
| `GET` | `/api/discovery/history/commits` | Public | Get Scientific Commit History |
| `POST` | `/api/discovery/inference-scaling/search` | API key | Search Inference Scaling Tree |
| `POST` | `/api/discovery/lab-in-the-loop/ground-recipe` | API key | Ground Lab Recipe |
| `POST` | `/api/discovery/lagrangian/audit` | API key | Audit Lagrangian Proposal |
| `POST` | `/api/discovery/lean/audit` | API key | Audit Lean Theorem Endpoint |
| `POST` | `/api/discovery/lean/audit-bijectivity` | API key | Audit Bijectivity Endpoint |
| `POST` | `/api/discovery/limitations/extract` | API key | Extract Baseline Limitations |
| `POST` | `/api/discovery/math-flywheel/audit-admissibility` | API key | Audit Math Problem Admissibility |
| `POST` | `/api/discovery/math-flywheel/run-cycle` | API key | Run Math Flywheel Cycle |
| `POST` | `/api/discovery/membrane/audit-duhem-quine` | API key | Audit Membrane Duhem Quine |
| `POST` | `/api/discovery/membrane/create-simulation-contract` | API key | Create Membrane Simulation Contract |
| `POST` | `/api/discovery/membrane/verify-physical-invariants` | API key | Verify Membrane Invariants |
| `POST` | `/api/discovery/multiscale/predict` | API key | Predict Multiscale Latent Transition |
| `POST` | `/api/discovery/oversight/audit` | API key | Audit Oversight Endpoint |
| `POST` | `/api/discovery/paper-agent/execute` | API key | Execute Paper Agent Endpoint |
| `POST` | `/api/discovery/paper-agent/query` | API key | Query Paper Agents Endpoint |
| `POST` | `/api/discovery/physical-court/audit-theorem` | API key | Audit Physical Theorem |
| `GET` | `/api/discovery/questions` | Public | List Research Questions |
| `POST` | `/api/discovery/real-cohort/run-empirical-discovery` | API key | Run Real Cohort Empirical Discovery |
| `POST` | `/api/discovery/reality-contact/evaluate` | API key | Evaluate Reality Contact |
| `POST` | `/api/discovery/reality-distance/evaluate` | API key | Evaluate Reality Distance |
| `POST` | `/api/discovery/reliability/audit` | API key | Audit Reliability |
| `GET` | `/api/discovery/representations` | Public | List Representations |
| `POST` | `/api/discovery/retrospective/run-time-split-benchmark` | API key | Run Retrospective Time Split Benchmark |
| `POST` | `/api/discovery/science-ide/execute-invariant-check` | API key | Execute Science Ide Check |
| `POST` | `/api/discovery/search/grounded-ingest` | API key | Ingest Grounded Search |
| `POST` | `/api/discovery/sovereignty/audit-perimeter` | API key | Audit Session Perimeter |
| `POST` | `/api/discovery/sovereignty/notarize` | API key | Notarize Thought Claim |
| `GET` | `/api/discovery/state-space` | Public | Get State Space |
| `POST` | `/api/discovery/stigmergy/audit-reality-firewall` | API key | Audit Reality Firewall |
| `POST` | `/api/discovery/stigmergy/compile-instrument` | API key | Compile Instrument |
| `POST` | `/api/discovery/stigmergy/query-pheromone-field` | API key | Query Pheromone Field |
| `POST` | `/api/discovery/system-one/classify-marr` | API key | Classify Marr System One |
| `POST` | `/api/discovery/system-one/triage-pr` | API key | Triage Pr System One |
| `POST` | `/api/discovery/tournament/debate-match` | API key | Debate Match Endpoint |
| `POST` | `/api/discovery/tournament/run-tournament` | API key | Run Tournament Endpoint |
| `POST` | `/api/discovery/traces/evaluate-epistemic-rigor` | API key | Evaluate Traces Epistemic Rigor |
| `GET` | `/api/discovery/trajectory-evolution` | Public | Get Trajectory Evolution |
| `POST` | `/api/discovery/universal/cross-domain-benchmark` | API key | Run Universal Cross Domain Benchmark |
| `POST` | `/api/discovery/unknown-mechanism/run-100-worlds-benchmark` | API key | Run Unknown Mechanism 100 Worlds Benchmark |
| `POST` | `/api/discovery/vega/simulate-decision` | API key | Simulate Vega Decision |
| `POST` | `/api/discovery/workbench/launch` | API key | Launch Discovery Workbench |
| `GET` | `/api/discovery/workbench/{workbench_id}` | Public | Get Discovery Workbench |
| `POST` | `/api/discovery/world-model/simulate` | API key | Simulate World Model Intervention |
| `GET` | `/api/health` | Public | Health Check |
| `POST` | `/api/hypotheses/compare` | API key | Compare Formal Hypotheses |
| `POST` | `/api/hypotheses/entails` | API key | Check Formal Consequence |
| `POST` | `/api/hypotheses/evaluate` | API key | Evaluate Formal Hypothesis |
| `POST` | `/api/hypotheses/formalize` | API key | Formalize Hypothesis |
| `GET` | `/api/hypotheses/scenarios/alzheimer` | Public | Alzheimer Formal Scenario Report |
| `GET` | `/api/lifecycle/ontrack` | Public | Lifecycle Ontrack Status |
| `POST` | `/api/lifecycle/packages/inspect` | API key | Inspect Lifecycle Package |
| `GET` | `/api/lifecycle/projects` | Public | List Lifecycle Projects |
| `POST` | `/api/lifecycle/projects` | API key | Create Lifecycle Project |
| `GET` | `/api/lifecycle/projects/{project_id}` | Public | Get Lifecycle Project |
| `GET` | `/api/lifecycle/projects/{project_id}/gate` | Public | Evaluate Lifecycle Gate |
| `POST` | `/api/lifecycle/projects/{project_id}/gate/pass` | API key | Pass Lifecycle Gate |
| `GET` | `/api/lifecycle/projects/{project_id}/package` | Public | Export Lifecycle Package |
| `POST` | `/api/lifecycle/projects/{project_id}/release` | API key | Release Lifecycle Project |
| `POST` | `/api/lifecycle/projects/{project_id}/results` | API key | Submit Lifecycle Result |
| `POST` | `/api/lifecycle/projects/{project_id}/rework` | API key | Rework Lifecycle Stage |
| `GET` | `/api/lifecycle/template` | Public | Lifecycle Template |
| `GET` | `/api/lifecycle/watch` | Public | Watch Lifecycle |
| `GET` | `/api/observer/ledger` | Public | Get Activity Ledger |
| `POST` | `/api/ontology/apply` | API key | Apply Ontology Plan |
| `POST` | `/api/ontology/plan` | API key | Plan Ontology Change |
| `POST` | `/api/ontology/rollback` | API key | Rollback Ontology Transaction |
| `POST` | `/api/webhooks/github` | HMAC signature | Audit Pr Webhook |
| `POST` | `/api/zenodo/publish` | API key | Publish To Zenodo |
