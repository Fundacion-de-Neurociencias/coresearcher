# ADR-EPISTEMIC-034: Exact Symbolic Dual-Verification & Obstacle-Driven Discovery Engine

**Status**: PROPOSED & RATIFIED  
**Date**: 2026-10-05  
**Author**: CoResearcher Epistemic Architecture Board  
**Cross-References**: `ADR-DISCOVERY-017` (Physical Theorem Court), `ADR-REASONING-031` (Decoupled Machine Reasoning), `ADR-EPISTEMIC-032` (Terence Tao Invariant), `ADR-EPISTEMIC-033` (Post-PDF Computable Science)

---

## 1. Context and Problem Statement

Recent empirical milestones in automated mathematical discovery (e.g., SyntheticMind resolving 80+ open conjectures in the OEIS, correcting indexing shifts, and independently verifying all linear recurrences in SymPy) expose a critical architectural vulnerability in generative AI applied to exact sciences:

1. **Floating-Point Drift and Probabilistic Hallucination**:
   Generative language models (LLMs) operate via probabilistic token prediction. They inherently suffer from hallucination and numerical rounding errors when manipulating discrete integer sequences, recurrence relations, rational fractions ($\mathbb{Q}$), differential identities, and tensor symmetries.
2. **Epistemic Debt Accumulation (Conjectures Built on Conjectures)**:
   In automated multi-step proofs, LLMs frequently invoke unproven lemmas or intermediate conjectures as established axioms. This causes cascading cascades of false theorems that mimic sound deductive chains.
3. **Premature Convergence vs. Stasis Diagnostics**:
   When an automated solver fails to close a proof, standard agentic loops repeat token variations without analyzing the underlying structural barrier.
4. **Boundary Blindness and Counterexample Neglect**:
   Orthodox consensus checks frequently overlook edge-case refutations (e.g., a recurrence failing at $k=27$ or off-by-one boundary conditions).

---

## 2. Decision and Epistemic Invariants

CoResearcher ratifies **ADR-EPISTEMIC-034**, establishing the **Exact Symbolic Dual-Verification & Obstacle-Driven Discovery Engine** (`ExactSymbolicCourt`).

### Invariant 1: Exact Symbolic Dual-Verification (Dual-Referee Protocol)
Every mathematical, physical, or recurrence identity proposed by a System 1 generator (e.g., LLM / heuristic search) MUST be independently audited by an exact Computer Algebra System (CAS, such as SymPy and exact rational arithmetic in $\mathbb{Q}$) before admission:
$$\text{Proposer}(S_1) \neq \text{Referee}(CAS_{exact})$$
Zero probabilistic verification is permitted for exact algebraic identities, tensor contractions, conservation balance laws, or discrete recurrence sequences.

### Invariant 2: Strict Lemma Purity Invariant (No Conjectures on Conjectures)
In the `ProofDependencyDAG`, every lemma is tagged as `AXIOM_KNOWN`, `PROVEN_LEMMA`, or `OPEN_CONJECTURE`.
- If any node in the deductive trail depends directly or transitively on an `OPEN_CONJECTURE`, its conclusion is strictly barred from promotion to `VERIFIED_COHERENT`.
- Such conclusions are classified as `PROVISIONAL_CONDITIONAL` or pruned entirely if absolute deductive closure is demanded.
- Self-discarding proofs: An engine must discard its own derivations whenever an underlying lemma relies on an unproven conjecture.

### Invariant 3: Obstacle-Driven Engine Expansion (Bottleneck Analysis)
When an epistemic trajectory halts or cannot close a proof DAG:
1. The system performs an **Obstacle Decomposition** (`ObstacleAnalysisReport`).
2. The exact barrier category is classified: `MISSING_ALGEBRAIC_IDENTITY`, `INDEX_SHIFT_DISCREPANCY`, `NON_COMMUTATIVE_OBSTRUCTION`, `DOMAIN_BOUNDARY_FAILURE`, or `SINGULARITY_CROSSING`.
3. The specific missing rule or transformation is surfaced to expand the system's rule library surgically, rather than relying on brute-force prompt reprompting.

### Invariant 4: Exact Boundary Counterexample Sweeps (The $k=27$ Invariant)
Every proposed recurrence or theorem must be subjected to bounded finite-order evaluation (e.g., checking up to $k=1000$ in exact integer arithmetic) and off-by-one shift audits ($n \pm 1, n \pm 2$).
Refuting an existing conjecture or identifying an off-by-one correction is treated as a first-class high-value scientific discovery (`REPUTABLE_FALSIFICATION` / `INDEX_CORRECTION`).

### Invariant 5: Computable Zenodo Dual-Check Artifact
Every settled conjecture or audited chapter must emit a standalone, deterministic executable verification package (Python/SymPy test script + exact rational data table) cryptographically bound by an `SOM-SHA256` hash.

---

## 3. Structural Specification

```
[System 1 Proposer: LLM / MCTS Proposal]
               │
               ▼
   [ProofDependencyDAG Builder]
               │
               ▼
┌──────────────────────────────────────────────┐
│  ExactSymbolicCourt (ADR-EPISTEMIC-034)      │
│  ├─ LemmaPurityChecker (Zero-conjecture DAG) │
│  ├─ SymPyCASReferee (Exact Rational CAS)     │
│  ├─ BoundaryCounterexampleAuditor (k sweep)  │
│  └─ ObstacleClassifier (Stasis Diagnostics)  │
└──────────────────────────────────────────────┘
         │                          │
   [Exact Match & Pure]      [Cycle / Counterex / Barrier]
         │                          │
         ▼                          ▼
 [VERIFIED_EXACT_THEOREM]    [FALSIFIED_COUNTEREXAMPLE /
                             OBSTACLE_EXPANSION_DISPATCH]
```

---

## 4. Architectural Boundaries

- **CoResearcher**: Houses `ExactSymbolicCourt`, evaluates Lemma Purity, checks exact algebraic identities via SymPy, classifies deduction obstacles, and issues the `ExactSymbolicVerdict`.
- **DataAILab**: Executes long-horizon empirical simulations, numerical PDE solver benchmarking, and big data regressions.
- **EdiTXT**: Packages verified proofs, SymPy execution scripts, and OEIS/Zenodo metadata into computable author manuscripts.
