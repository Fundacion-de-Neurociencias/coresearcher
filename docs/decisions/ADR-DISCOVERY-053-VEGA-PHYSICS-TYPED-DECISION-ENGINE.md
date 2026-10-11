# ADR-DISCOVERY-053: Vega Physics-Based Typed Decision Engine & Continuous Potential Landscape

- **Status**: ACCEPTED
- **Date**: 2026-10-11
- **Domain**: Epistemic Decision Layer / Physical Verification / Fast System 1
- **Driver**: Nandakishor M (Vega open-source release, October 2026; successor to Laya / JEV)
- **Compliance**: 100% English Language Invariant, Zero Mocking, Deterministic Sov-Engine

---

## 1. Context & Problem Statement

Standard neuro-symbolic or LLM classification systems rely on discrete token output argmax or softmax categorical distributions ($P(y_i) = \frac{e^{z_i}}{\sum e^{z_j}}$). In adversarial epistemic boundary settings—such as ambiguous prompt injection detection, hypothesis acceptance, epistemic PR review risk scoring, or loop termination—softmax probability scores suffer from severe calibration drift, overconfidence on out-of-distribution inputs, and failure to model phase-transition dynamics.

Nandakishor M introduced **Vega** (October 2026), an 800M/4B parameter physics-based typed decision engine utilizing Test-Time Training (TTT) architectures and continuous dynamical energy landscapes. Instead of discrete label sampling, Vega represents potential outcomes as attractive potential wells $U(x)$, injects a test particle initialized from the question/last-token state vector, and simulates damped Newtonian mechanics:
$$m \frac{d^2 x}{dt^2} + \gamma \frac{dx}{dt} + \nabla U(x) = 0$$

The settled energy minimum determines the categorical decision, the depth and curvature determine confidence via Boltzmann statistics, and symmetric or shallow barriers enable principled conformal abstention (`is_abstain = True`).

---

## 2. Decision & Architectural Mechanics

We implement the complete **Vega Physics Decision Engine** in CoResearcher under `python/discovery/vega_decision_engine.py` with multi-level integration across the stack:

1. **Continuous Potential Energy Landscape ($U(x)$)**:
   $$U(x) = -\sum_{i} D_i \exp\left(-\frac{\|x - \mu_i\|^2}{2\sigma_i^2}\right) + \frac{1}{2} k_{\text{confine}} \|x\|^2$$
   Where $D_i$ denotes valley depth modulated by observational priors and token projections, $\mu_i$ represents the outcome center coordinate, and $k_{\text{confine}}$ ensures compact confinement.

2. **Semi-Implicit Euler Damped Dynamics**:
   Numerical time-stepping with friction coefficient $\gamma$ dissipates kinetic energy:
   $$a(t) = \frac{-\nabla U(x(t)) - \gamma v(t)}{m}$$
   $$v(t+\Delta t) = v(t) + a(t) \Delta t$$
   $$x(t+\Delta t) = x(t) + v(t+\Delta t) \Delta t$$

3. **Conformal Abstention & Boltzmann Confidence**:
   - Barrier height margin $\Delta U = U_2^* - U_1^*$. If $\Delta U < \theta_{\text{abstain}}$, the engine identifies a bistable ambiguity and emits `is_abstain = True` (`ABSTAIN_AMBIGUOUS`).
   - Probabilities are calibrated via effective Boltzmann thermalization:
     $$P_i = \frac{\exp(-(U_i - U_{\min}) / T_{\text{eff}})}{\sum_j \exp(-(U_j - U_{\min}) / T_{\text{eff}})}$$

4. **Fast System 1 & Twin Gate Harness Integration**:
   - `FastSystemOneClassifier.classify_marr_with_vega(statement)` evaluates Marr levels (Computational, Algorithmic, Implementational) using a continuous 3-well landscape.
   - `JevContinuousVerifier.verify_turn_goal(...)` in `python/discovery/twin_gate_harness.py` evaluates subgoal settlement to avoid infinite reasoning loops.

5. **REST API Endpoint**:
   - Exposed at `POST /api/discovery/vega/simulate-decision` accepting custom potential valleys, initial velocity/position, and friction damping.

6. **Cryptographic Proof & ScientificLedger**:
   - Every simulated settlement computes a SHA-256 Merkle seal `som_vega_hash` and appends an immutable epistemic verdict entry to `ScientificLedger`.

---

## 3. Verification & Acceptance Criteria

- **Unit & Integration Suite**: `tests/test_vega_decision_engine.py` passes all 6 tests:
  - Deep single well settlement with $>80\%$ confidence.
  - Symmetric bistability correctly triggering `is_abstain = True`.
  - Monotonic friction energy dissipation across trajectory steps.
  - Marr level classification via Vega tier.
  - Binary verification prompt decision (YES vs NO) with token boundaries.
  - FastAPI `/api/discovery/vega/simulate-decision` endpoint verification.
- **Language Policy**: `scripts/enforce_english_policy.py` confirms 100% compliance across all touched files.
