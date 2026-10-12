# ADR-DISCOVERY-043: Categorical Result Family Orchestration & Lean/CAS Dual Formalization Gate

## Status
ACCEPTED

## Context
In October 2026, OpenAI published the `openai/math` repository containing 722 autonomous research preprints across 372 result families (addressing milestones such as Milne's conjecture, Birch–Swinnerton-Dyer for low Selmer rank, the Quasi-Riemann Hypothesis, and the irrationality of Catalan's constant).

A critical finding from auditing this repository is OpenAI's explicit admission:
> *"This collection includes results at different stages of verification. Not all have accompanying Lean formalizations... Some of the unformalized results could have issues. We will endeavor to fix any such issues quickly."*

This empirically confirms three core tenets of CoResearcher:
1. **Unverified Prose is Epistemically Invalid**: Large language models generating dense LaTeX prose without interactive theorem proving (Lean 4) or exact Computer Algebra Systems (SymPy CAS) cannot be trusted for mathematical or physical ground truth. Textual plausibility $\neq$ formal proof.
2. **Organization into Result Families**: High-level discoveries cannot exist as isolated flat files. They require structured "Result Families":
   - **Core Theorem**: The primary breakthrough claim.
   - **Bridge Lemmas & Companion Arguments**: Necessary ancestor lemmas forming an acyclic dependency graph.
   - **Corollaries & Alternative Trajectories**: Parallel derivations, asymptotic limits, and dual representations.
   This maps directly onto **Category Theory** (objects, morphisms, commutative diagrams, and categorical adjunctions).
3. **Monopolistic Cloud Oracle vs. Sovereign Open Science**: Rather than requiring multi-million-dollar proprietary clusters that harvest scientific inputs, discovery engines must operate under zero-trust sovereign hardware (`ADR-SOVEREIGNTY-041`), unnormalized energy compatibility (`ADR-EPISTEMIC-040`), and transparent algebraic courts (`ADR-EPISTEMIC-034`).

## Decision
We implement `ResultFamilyOrchestrator` in `python/discovery/result_family_orchestrator.py` governed by the following architectural pillars:

### 1. Categorical Result Family Schema
Each scientific result is modeled as an interconnected epistemic family:
$$\mathcal{F} = \left( \mathcal{T}_{\text{core}}, \mathcal{L}_{\text{bridge}}, \mathcal{C}_{\text{corollaries}}, \mathcal{P}_{\text{alt\_proofs}} \right)$$
Modeled over an `EpistemicCategory` where:
- Theorems and lemmas are category objects.
- Deductive inferences and reduction morphisms are composable category morphisms.
- Holonomy defect $\oint \mathcal{M} = 0$ guarantees that alternative proof branches commute without logical divergence.

### 2. Dual Formalization Gate (Lean / Symbolic CAS)
Every claim within a family must pass the dual-gate:
1. **Exact CAS Referee**: Verified in exact rational arithmetic $\mathbb{Q}$ and symbolic substitution via SymPy CAS (`ExactSymbolicCourt`).
2. **Formal Verification Check**: Verifies whether an automated formal proof (Lean 4 theorem or verified proof script) exists. If unformalized, the claim is strictly tagged with `EpistemicStatus.PROVISIONAL_UNFORMALIZED_PROSE` and barred from becoming an invariant.

### 3. Merkle Lineage & Export
Each family is anchored cryptographically via `SOM-SHA256` in the local `EpistemicGitRepo`, allowing reproducible serialization to markdown catalogs (`CONTENTS.md` style) with complete dependency and formalization status.

## Consequences
- Guarantees that CoResearcher matches and exceeds the structural organization of OpenAI's 372 result families while maintaining 100% local mathematical sovereignty and zero risk of thought harvesting.
