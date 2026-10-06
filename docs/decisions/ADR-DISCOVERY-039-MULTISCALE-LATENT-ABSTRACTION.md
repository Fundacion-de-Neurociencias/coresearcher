# ADR-DISCOVERY-039: Multiscale Latent Abstraction Hierarchy & Differentiable Action-Conditioned Epistemics

## Status
ACCEPTED

## Context
Traditional physical modeling and scientific computing often suffer from two extremes:
1. **Microscopic Over-Simulation / Digital Twins**: Attempting to simulate every microscopic degree of freedom (e.g., individual particle trajectories, atomistic collisions, pixel-level frames). This suffers from chaotic divergence (Lyapunov explosion), computational intractability, and compounding prediction error.
2. **Macroscopic Oversimplification / Static Regressions**: Fitting high-level empirical formulas that ignore internal causal structure and fail under counterfactual interventions.

As formulated by the user and aligned with Yann LeCun's AMI/H-JEPA paradigm:
> *"Learning a hierarchy of abstractions: lower levels make short-range predictions (representations contain more details); higher levels make long-range predictions (representations contain fewer details: can make accurate long-term predictions but with fewer details). Science and modelling are all about finding the right representation at the right level of abstraction! World Models should not be simulators or digital twins, but action-conditioned predictors in abstract representation space, preferably differentiable."*

## Decision
We implement `MultiscaleAbstractionEngine` in `python/discovery/multiscale_abstraction_engine.py` governed by the following core architectural pillars:

### 1. Hierarchy of Epistemic Abstractions
We partition representation spaces into three distinct abstraction levels:
- **`MICRO_IMPLEMENTATIONAL`**:
  - High dimensionality / granular detail (e.g., phase space positions $\mathbf{q}, \mathbf{p}$, microscopic coordinates).
  - Short-range prediction horizon $\tau_{\text{micro}} \in [1, 10]$ steps.
  - High susceptibility to noise and chaotic divergence.
- **`MESO_ALGORITHMIC`**:
  - Intermediate dimensionality (e.g., velocity fields, local order parameters, coarse-grained density).
  - Medium-range prediction horizon $\tau_{\text{meso}} \in [10, 100]$ steps.
- **`MACRO_COMPUTATIONAL_CONSERVATIVE`**:
  - Compact dimensionality / macroscopic invariants (e.g., total energy $E$, temperature $T$, entropy $S$, topological charges $Q$).
  - Long-range prediction horizon $\tau_{\text{macro}} \in [100, 10000]$ steps.
  - Highly robust to microscopic fluctuations.

### 2. Horizon vs. Detail Trade-Off Scaling Law
The maximum stable prediction horizon $\mathcal{H}(s)$ scales inversely with representation detail / effective dimensionality $D(s)$:
$$\mathcal{H}(s) = \frac{\kappa}{\max(1, D(s)) \cdot (1 + \sigma_{\text{noise}})}$$
where $\kappa$ is the epistemic horizon constant.

### 3. Differentiable Action-Conditioned Latent Predictor
World models operate not by pixel or state rendering, but by mapping latent representations under action interventions:
$$\hat{s}_{t+\Delta t} = \text{Pred}_\theta(s_t, a_t)$$
The prediction energy measures compatibility between predicted latent state $\hat{s}$ and empirical latent projection $s^*$:
$$E(s_t, a_t, s^*) = \frac{1}{2} \|\hat{s}_{t+\Delta t} - s^*\|_2^2$$
Transitions are fully differentiable with analytical or numerical gradients:
$$\nabla_{a_t} E = - (\hat{s}_{t+\Delta t} - s^*) \cdot \nabla_{a_t} \text{Pred}_\theta(s_t, a_t)$$

### 4. Representation Selection for Scientific Discovery
The engine evaluates candidate representations to discover the **optimal level of abstraction** for a target inquiry horizon:
$$\mathcal{L}_{\text{rep}} = | \tau_{\text{target}} - \mathcal{H}(s) | + \lambda \cdot E(s_t, a_t, s^*)$$

## Consequences
- The discovery pipeline can evaluate hypotheses and models by testing whether they select the correct level of abstraction rather than penalizing models for omitting micro-details unnecessary for macro-predictions.
- Full compatibility with the `PhysicsCorpusAuditor v3.0` and `WorldModelEpistemicAdapter`.
