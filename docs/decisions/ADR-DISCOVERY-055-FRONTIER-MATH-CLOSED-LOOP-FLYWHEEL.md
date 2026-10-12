# ADR-DISCOVERY-055: Frontier Math Ingestion & Epistemic Closed-Loop Flywheel

- **Status**: ACCEPTED
- **Date**: 2026-10-12
- **Domain**: Automated Mathematical Discovery / Closed-Loop AI Acceleration / Offline Policy Calibration
- **Compliance**: 100% English Language Invariant, Zero Mocking, Deterministic Sov-Engine

---

## 1. Context & Problem Statement

OpenAI's open mathematical release (`openai/math` with 369/722 Lean-formalized problems) and subsequent conversions into open-source reinforcement learning (RL) gym environments on Hugging Face (such as Harbor sandboxes) represent a significant milestone for AI research. However, community analysis and foundational mathematical critiques (e.g., Victor Martinsons, Yao Xiao, Rory O'Connor) highlighted three critical structural vulnerabilities:
1. **Lack of Structural Admissibility**: Environments and reward functions are frequently built around problems whose target formalization drifted from the natural mathematical conjecture (e.g. relaxing derivatives or restricting boundary conditions). Training agents against invalid targets yields optimization scaffolds without mathematical grounding.
2. **Brittle Exact-Formalization Verifiers**: Naïve RL environments award `1` only for the verbatim reference proof and `0` for distinct, valid mathematical derivations or intermediate lema progress. This trains models to mimic the author's idiosyncratic phrasing rather than deduce mathematical reality.
3. **Training Data Leakage vs. Reasoning**: Reference solutions are public in web-scraped git repositories, allowing models whose pretraining cutoff postdates the release to score `1` via memory recall rather than genuine mathematical deduction.

---

## 2. Decision & Architectural Mechanics

We implement **`FrontierMathFlywheelEngine`** in `python/discovery/frontier_math_flywheel.py`, closing the recursive auto-bootstrapping loop between external mathematical releases and CoResearcher:

### A. Structural Admissibility & Bijectivity Gate (`SemanticBijectivityAuditor`, ADR-048)
- Audits ingested problems before compute allocation: verifies that the formal Lean 4 proposition bijectively captures the natural mathematical prose claim without goalpost shifting or assumption weakening.
- Problems suffering from derivative order reduction or unwarranted domain restrictions are trapped in `AdmissibilityStatus.DRIFTED_GOAL` and quarantined.

### B. Proof Equivalence & Dense Progress Reward (`ProofEquivalenceAuditor`)
- Replaces binary `{0, 1}` exact string matching with an isomorphism and kernel acceptance evaluator.
- Evaluates whether an alternative derivation proves the target theorem without unproven `sorry` escapes or artificial axioms.
- Awards calibrated dense partial credit ($[0.0, 1.0]$) for sound intermediate bridge lemmas leading toward the goal.

### C. Result Family Lemma Harvesting (`ResultFamilyOrchestrator`, ADR-043)
- Decomposes verified or partial proofs into modular DAGs.
- Extracts sound bridge lemmas (`ExtractedBridgeLemma`) with kernel proof validation, preserving modular truths even when an overarching theorem remains open.

### D. Functorial Compilation into AI Acceleration Operators (`AlgebraicStructureCompiler`, ADR-046)
- Automatically compiles harvested mathematical structures into executable AI runtime operators:
  - **Clifford Geometric Algebras ($SO(p, q)$)**: Compiles exact matrix generators for equivariant latent representations.
  - **Toeplitz Spectral Operators**: Compiles FFT circulant kernels reducing quadratic attention $\mathcal{O}(N^2)$ to $\mathcal{O}(N \log N)$.
  - **Symplectic Flows**: Synthesizes energy-conserving Hamiltonian steppers for physics and membrane solvers.
- Injects active algebraic invariants directly into local System 1/System 2 prompt contexts.

### E. Offline Policy Calibration via Dream-RSI (ADR-054)
- Converts problem exploration histories into `DiscoveryHistoryNode` DAGs.
- Evaluates alternative MCTS, Greedy, and Vega search policies in $< 1\,\text{ms}$ offline, finding Pareto-optimal exploration rules without GPU burn.

### F. Cross-Domain Re-Investment & Cryptographic Provenance
- Directs accelerated operators and calibrated search policies into **MetaboAD / Neurodiagnoses** (clinical metabolomics and aging biology) and **PhysicsMegarepoAuditor** (fluid dynamics and field theories).
- Every flywheel cycle emits an immutable SHA-256 Merkle seal `som_math_flywheel_hash` registered in `ScientificLedger`.

---

## 3. Verification & Acceptance Criteria

- **Automated Test Suite**: `tests/test_frontier_math_flywheel.py` passes 6/6 tests:
  - Sound problem admissibility verification (`Riemann Zeta Bound`).
  - Detection and rejection of drifted/weakened goals (`Navier-Stokes Derivative Shift`).
  - Proof equivalence evaluation and dense partial credit for bridge lemmas.
  - Lemma harvesting and functorial compilation to Clifford/Toeplitz operators.
  - Full closed-loop flywheel cycle execution.
  - FastAPI endpoints `/api/discovery/math-flywheel/audit-admissibility` and `/api/discovery/math-flywheel/run-cycle`.
- **Language Policy**: `scripts/enforce_english_policy.py` confirms 100% English compliance across all 458 repository files.
