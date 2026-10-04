# ADR-REASONING-031: Epistemic Search & Decoupled Machine Reasoning Architecture

- **Status**: Accepted
- **Date**: 2026-10-04
- **Author**: Dr. Manuel Menéndez González / Fundación de Neurociencias (FdN)
- **Reference**: Thore Graepel (DeepMind AlphaGo co-creator, 2026), *Don’t be fooled—LLMs don’t reason*; Yann LeCun & Subbarao Kambhampati (2026).
- **Applies to**: Full CoResearcher Discovery Pipeline (`LocalAIAdapter`, `EpistemicTreeSearch`, `PhysicalCoherenceCourt`, `PhysicalTheoremCourt`, `ConstraintLedger`).

---

## 🏛️ Foundational Manifesto

> ### *"Language models supply the hunches; algorithms, trees, and mathematics supply the reasoning."*
> ### *"Reasoning is not the generation of intermediate tokens; reasoning is an auditable search over an explicit state space evaluated by an unyielding reality judge."*

---

## 1. Context and Problem Statement

A fundamental misconception permeates modern artificial intelligence: the conflation of fluent text generation (System 1) with genuine deliberative reasoning (System 2). As articulated by Thore Graepel, the breakthrough of AlphaGo (specifically Move 37 against Lee Sedol) was not an act of intuitive token generation:
1. **The Policy Network (System 1)** evaluated Move 37 as having a probability of only ~1 in 10,000 based on human precedent.
2. **The Search Machinery (System 2)** constructed an explicit game tree, simulated counterfactual futures, weighed long-range territorial consequences, and **overrode the policy network's intuition** because mathematical search proved the move's superiority.

In contrast, contemporary LLMs (even when utilizing *Chain-of-Thought* or post-trained RLVR) suffer from three fatal structural limitations:
1. **No Explicit, Inspectable Epistemic State**: They do not maintain an external, revisable ledger of what is established, what is doubted, what is refutable, and what has been defeated.
2. **Inseparable Knowledge and Logic**: Facts and rules of inference are conflated within neural weights rather than separated into independent, verifiable systems.
3. **Post-Hoc Concoction**: Intermediate chains of thought are frequently generated after the conclusion has already been fixed by next-token distribution heuristics.

In high-stakes scientific discovery, medicine, and theoretical physics, unverified token generation produces hallucinations, $p$-hacking, and physical impossibility (e.g., negative thermodynamic entropy, dimensional incoherence). True scientific discovery requires a decoupled architecture where neural networks generate candidate hypotheses, but formal search engines and physical theorem courts arbitrate truth.

---

## 2. Decision: Decoupled Machine Reasoning Architecture

We formally architect CoResearcher into a strict **Two-Tier Decoupled Machine Reasoning Engine**:

```
+----------------------------------------------------------------------------------------------------+
|                                THE CORESEARCHER REASONING STACK                                    |
+----------------------------------------------------------------------------------------------------+
|                                                                                                    |
|  [ SYSTEM 1: Fast Heuristic Proposal Engine ]                                                     |
|  - Implemented in: LocalAIAdapter (Laya / Ollama / LM Studio local endpoints)                      |
|  - Role: Proposes candidate hypotheses, translates raw text into formal structures,               |
|          and estimates initial semantic priors (P(H)).                                             |
|  - Constraint: System 1 CANNOT write to the Epistemic Ledger or declare a theory sound.            |
|                                                                                                    |
+-------------------------------------------------+--------------------------------------------------+
                                                  | Proposes Branches & Lemmas
                                                  v
+----------------------------------------------------------------------------------------------------+
|  [ SYSTEM 2: Deliberative Epistemic Search & Falsification ]                                       |
|  - Implemented in: EpistemicTreeSearch (ETS) & LongHorizonCampaignEngine                          |
|  - Role: Explores candidate hypothesis-constraint trees, evaluates state-space Ω exclusion,       |
|          simulates counterfactual perturbations, and backtracks upon contradictions.               |
|                                                                                                    |
+-------------------------------------------------+--------------------------------------------------+
                                                  | Audited by Reality Courts
                                                  v
+----------------------------------------------------------------------------------------------------+
|  [ THE REALITY JUDGE: Physical & Categorical Invariant Courts ]                                    |
|  - Implemented in: PhysicalCoherenceCourt, PhysicalTheoremCourt & Buckingham Pi Homogeneity        |
|  - Role: Immutable mathematical validation:                                                        |
|     1. Physical Conservation Laws (Energy, Mass Continuity, 2nd Law Entropy non-decrease).         |
|     2. Dimensional Homogeneity ([M][L][T]^-1 compliance).                                          |
|     3. Categorical Commutativity: Zero holonomy defect (||ΔM||_F < 1e-3).                          |
|     4. Empirical Reality Contact Score (RCS >= 2.0 with zero stubs/mocking).                       |
|                                                                                                    |
+-------------------------------------------------+--------------------------------------------------+
                                                  | Commits Verified Invariants
                                                  v
+----------------------------------------------------------------------------------------------------+
|  [ EXPLICIT EPISTEMIC LEDGER & GRAVEYARD ]                                                         |
|  - Implemented in: ConstraintLedger, EpistemicGitRepo & DefeatedHypothesisGraveyard               |
|  - Invariants: Verified constraints become immutable axioms. Refuted hypotheses are logged with    |
|    Duhem-Quine blame records to permanently repel future search branches.                         |
+----------------------------------------------------------------------------------------------------+
```

---

## 3. Algorithmic Specifications

### 3.1. Dynamic System 1 Proposer (`LocalAIAdapter` / `FastSystemOneClassifier`)
The local LLM is invoked strictly as a bounded generator:
- Input: Research question $Q$, current constraint ledger $\mathcal{C}$, and state space bounds $\Omega$.
- Output: Candidate hypotheses $\mathcal{H}_{cand}$, auxiliary assumptions $\mathcal{A}$, and testable implications $\mathcal{I}$.
- The LLM never scores its own hypotheses.

### 3.2. Epistemic Tree Search (ETS) with Physical Scoring
The reasoning search explores paths using a rigorous mathematical evaluation function:
$$\text{Score}(\text{Node}) = \text{DV}(\text{Node}) \times \left(1 + \Delta \Omega_{\text{pruned}}\right) \times \mathbb{I}_{\text{Physical}}(\text{Node})$$
Where:
- $\text{DV}$ is the Decomposed Discovery Value (falsifiability, generality, compression, novelty).
- $\Delta \Omega_{\text{pruned}}$ is the fraction of possible parameter state space excluded by the branch.
- $\mathbb{I}_{\text{Physical}} \in \{0, 1\}$ is the binary invariant indicator issued by `PhysicalCoherenceCourt`. If a branch breaches conservation laws or dimensional homogeneity, $\mathbb{I}_{\text{Physical}} = 0$ and the branch is immediately pruned.

### 3.3. Duhem-Quine Backtracking and Autopsy
When an empirical or physical contradiction occurs:
- The search engine does not discard the core hypothesis blindly.
- The `ScientificFailureEngine` isolates whether the auxiliary assumptions $\mathcal{A}$ or the core hypothesis $\mathcal{H}$ failed.
- True refutations are inscribed into the `DefeatedHypothesisGraveyard`, generating negative pheromone attractors in `EpistemicPheromoneField`.

---

## 4. Invariants and Enforcement Rules

1. **Zero Unverified Inference**: No statement may be labeled as `VERIFIED` or `ESTABLISHED` solely based on LLM output. Every verified item must have a proof trace in `PhysicalTheoremCourt` or an empirical validation with $RCS \ge 2.0$.
2. **Move 37 Capability**: The search tree must be able to select low-probability hypotheses (by LLM prior) if their state-space exclusion and physical invariant consistency are superior.
3. **Air-Gapped Local Computation**: Search rollouts and System 1 queries execute strictly via local endpoints (`LocalAIAdapter`), preserving intellectual property and sovereign data governance (ADR-SOVEREIGNTY-030).

---

## 5. Consequences

### Positive:
- Bridges the fundamental gap identified by Graepel and LeCun: provides machine reasoning through search, explicit state, and independent verification.
- Eliminates AI hallucination of physical and biological laws.
- Transparent, auditable scientific decision trajectories with mathematical provenance.

### Trade-offs:
- Inference-time compute (ETS) requires additional CPU/GPU search iterations compared to raw next-token sampling.
