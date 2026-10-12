# ADR-DISCOVERY-057: Google ERA Empirical Research Assistance & Code Search Calibration Engine

## Status
Accepted

## Context
Traditional epidemiological and clinical trajectory modeling often relies on manual code adjustments by human researchers exploring only a handful of hypotheses, constrained by human fatigue and intuition.
In 2026, Google Research and Harvard (*Nature*: "An AI system to help scientists write expert-level empirical software", by Michael Brenner and Lizzie Dorfman) demonstrated that **Empirical Research Assistance (ERA)** using closed-loop tree search over empirical code variants (up to 200,000 iterations) outperformed all CDC epidemiological consortia in forecasting hospital admissions for flu and RSV.

In our institutional ecosystem, there is an invariant separation of concerns ([`MEDICALIA_PRINCIPLES.md`](file:///c:/Users/usuario/medicalia/MEDICALIA_PRINCIPLES.md#L109-L122)):
- **CoResearcher**: *Generates, calibrates, and stress-tests empirical models* via high-throughput tree search over physical datasets, discovering optimal parameterizations, non-linear mechanisms, and clinical lead-time margins.
- **Medicalia OS**: *Executes verified knowledge* deterministically in asynchronous clinical practice under MDR Class IIa without online runtime code mutations.

## Decision
We implement `ERAClosedLoopTreeSearch` (`python/discovery/era_empirical_engine.py`) in CoResearcher:

1. **Structured Methodological Mutations**:
   - `ERAMethodologicalMutationGenerator` mutates code candidates across discrete strategies: `EXPONENTIAL_DECAY_LAG`, `SPLINE_WEIGHTING`, `BAYESIAN_HIERARCHICAL_SHRINKAGE`, `KALMAN_DYNAMIC_FILTER`, `COVARIATE_GATE_INTERACTION`, and `NONLINEAR_SATURATION_HILL`.
2. **Closed-Loop Empirical Tree Search**:
   - Evaluates code mutations directly against ground-truth time series and biomarker trajectories without mocks.
   - Computes RMSE, MAE, $R^2$, and BIC parsimony penalties, dynamically pruning inferior branches from the beam.
3. **Clinical Lead-Time Anticipation**:
   - `ClinicalLeadTimeEvaluator` measures `lead_time_anticipation_days` (early detection margin prior to clinical surge or decompensation).
   - Feeds directly into Medicalia's `lead_time_anticipation_days` contract fields (`trajectory.v1.json` / `health-state.v1.json`).
4. **Cryptographic Sealing & REST API**:
   - Seals each campaign with SHA-256 (`era_calibration_hash`) recorded into `ScientificLedger`.
   - Exposes `POST /api/discovery/era/mutate-code` and `POST /api/discovery/era/run-search-campaign`.

## Consequences
- **Positive**: Enables small research teams to explore high-dimensional code spaces and discover counter-intuitive biological/epidemiological dynamics.
- **Strict Compliance**: Strictly preserves the boundary between CoResearcher (discovery/calibration) and Medicalia (clinical execution).
