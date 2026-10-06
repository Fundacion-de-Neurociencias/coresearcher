# ADR-EPISTEMIC-040: Non-Generative Energy-Based Epistemics & Model-Predictive Scientific Auditing

## Status
ACCEPTED

## Context
Following the foundational thesis of Yann LeCun ("A Path Towards Autonomous Machine Intelligence", 2022-2026) and as explicitly formalized by the user:
> *"IF YOU ARE INTERESTED IN HUMAN-LEVEL AI, DON'T WORK ON LLMS"*
> 1. Abandon generative models in favor of joint-embedding architectures (JEPA).
> 2. Abandon probabilistic models in favor of energy-based models (EBMs).
> 3. Abandon contrastive methods in favor of regularized methods (VICReg / non-contrastive covariance regularizers).
> 4. Abandon Reinforcement Learning in favor of model-predictive control (MPC). Use RL only when planning does not yield the predicted outcome, to adjust the world model or the critic.

Mainstream scientific auditing tools mistakenly rely on autoregressive token likelihood, probabilistic generative scoring ($P(\text{paper} \mid \text{corpus})$), contrastive fine-tuning, or trial-and-error reinforcement loops. In the analysis of physical theories, mathematical proofs, and novel discoveries:
- Token-level autoregressive generation accumulates compounding errors exponentially.
- Normalized probabilities $P(y \mid x)$ are mathematically intractable over continuous manifolds and reward consensus over truth.
- Blind trial-and-error RL lacks biological and physical sample efficiency.

## Decision
We implement `NonGenerativeEpistemicAuditor` in `python/discovery/energy_predictive_auditor.py` based on four invariant operational pillars:

### 1. Joint-Embedding Latent Auditing (JEPA over Generative Re-synthesis)
The auditor never attempts to reconstruct or generate raw textual prose or verbatim equations. Instead, it extracts the abstract invariant vector $s_x = \text{Enc}_x(\text{Theory})$ and compares it directly against observable or experimental latent state $s_y = \text{Enc}_y(\text{Reality})$.

### 2. Energy-Based Compatibility Scoring (EBMs over Probabilities)
Instead of calculating normalized probabilities, theories are evaluated via unnormalized energy functions:
$$\mathcal{E}(x, y) = \mathcal{D}(\hat{s}_y, s_y) + \sum_i \lambda_i C_i(x)$$
where $C_i(x)$ are hard physical constraints (dimensional homogeneity, energy conservation, unitary bounds).
- $\mathcal{E}(x, y) \approx 0 \implies$ Mechanistically sound and physically compatible.
- $\mathcal{E}(x, y) = +\infty \implies$ Fatal physical violation (e.g. overunity, perpetual motion, causal cycle).

### 3. Non-Contrastive Information Regularization (VICReg Paradigm)
To prevent representation collapse without requiring computationally intractable negative sampling:
- **Variance Regularization**: Forces each latent feature dimension to maintain minimal spread:
  $$v(Z) = \frac{1}{d} \sum_{j=1}^d \max(0, 1 - \sqrt{\text{Var}(Z_j) + \epsilon})$$
- **Covariance Regularization**: Enforces decorrelation across orthogonal physical observables:
  $$c(Z) = \frac{1}{d} \sum_{i \neq j} \text{Cov}(Z)_{i,j}^2$$

### 4. Model-Predictive Epistemic Planning (MPC over Blind RL)
Counterfactual stress-testing and falsification discovery are driven by **Model-Predictive Control (MPC)**:
- At each deliberative step, the auditor formulates a sequence of theoretical interventions $\mathbf{a}_{t:t+H}$ that minimize/maximize invariant energy over an internal latent World Model.
- Trial-and-error RL is strictly quarantined to residual calibration: it is triggered only when empirical reality disconfirms the planned latent forecast, updating the world model transition tensors or the critic cost function.

## Consequences
- Physical corpus audits in `PhysicsCorpusAuditor v3.0` evaluate papers and discoveries by unnormalized physical energy minimization rather than text likelihood or popularity.
- Radical breakthroughs that deviate from mainstream consensus are not penalized if their internal invariant energy satisfies $\mathcal{E} \le \epsilon$.
