# ADR-DISCOVERY-042: Problem-Driven Limitation Resolution & Empirical Refinement Engine

## Status
ACCEPTED

## Context
Following the breakthrough methodology established by Google Cloud AI's **ScientistTwo** (Nam, Meng, Pfister et al., ArXiv 2609.19644, 2026), scientific discovery should not proceed through unstructured, speculative brainstorming or trial-and-error metric hacking. Rather, expert-level research is strictly **problem-driven and cumulative**:
1. **Limitation Extraction & Verification**: Before generating novel hypotheses, an autonomous system must rigorously analyze the human state of the art ($\mathcal{G}$), isolate its theoretical, mathematical, and computational bottlenecks, and verify that these limitations are actionable and non-trivial.
2. **Subset-to-Full Empirical Screening**: Candidate solutions are first screened on cheap, representative data subsets (`Bad`, `Good`, `Engineer`) before allocating expensive full-scale compute resources.
3. **Ablation-Driven Component Refinement**: The agent autonomously executes component ablations to isolate the precise source of empirical gain, dynamically pruning ineffective terms.
4. **Active Supplementary Rebuttal**: When critiques arise, the system formulates and executes dedicated supplementary experiments rather than treating peer-review feedback as passive text editing.

Critically, while ScientistTwo relies on proprietary centralized cloud LLMs (Gemini / Claude Opus) that risk intellectual property leakage and lack formal CAS invariants, CoResearcher executes this workflow within the **Zero-Trust Sovereign Epistemic Bunker (ADR-041)**, validated by **Exact Symbolic Courts (ADR-034)** and **Non-Generative Energy Compatibility (ADR-040)**.

## Decision
We implement `LimitationResolutionEngine` in `python/discovery/limitation_resolution_engine.py` governed by the following core components:

### 1. Limitation Extraction & Verification Protocol
Given a baseline theory or codebase $\mathcal{G}$, the engine extracts a structured set of actionable limitations:
- `THEORETICAL_ASYMMETRY`: Inconsistencies under specific symmetries or gauge transformations.
- `EMPIRICAL_BOTTLENECK`: Saturation of accuracy, computational scaling limits, or out-of-distribution failure.
- `ASSUMPTION_OVEREXTENSION`: Auxiliary assumptions that break in realistic physical regimes.

### 2. Multi-Stage Seed Idea Formulation & Screening
Candidate hypotheses are generated to address verified limitations directly. Each idea undergoes multi-tier triage:
- `BAD`: Substantially worse than baseline; discarded.
- `ENGINEER`: Shows partial promise but requires hyperparameter/algebraic tuning.
- `GOOD`: Consistently outperforms baseline on representative subset; promoted to full-scale evaluation.

### 3. Closed-Loop Active Rebuttal Execution
When evaluated by simulated peer reviewers (such as ScholarPeer or automated adversarial courts), queries trigger targeted supplementary experiments that produce formal evidence packages before publication approval.

## Consequences
- Physical theories, computational simulations, and biomedical models in CoResearcher are developed by addressing verified limitations of existing state-of-the-art formulations.
- Rebuttal loops are strictly empirical and symbolic, preventing ungrounded prose hand-waving.
