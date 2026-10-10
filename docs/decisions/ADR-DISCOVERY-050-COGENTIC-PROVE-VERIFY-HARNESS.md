# ADR-DISCOVERY-050: Cogentic Multi-Agent Prove-Verify Harness & Parallel Lemma Orchestrator

- **Status**: Implemented & Verified
- **Date**: 2026-10-10
- **Scope**: Mathematical & Physical Frontier Epistemics, Automated Proof Discovery
- **Inspiration**: Google Research & Yale University (Cai, Gupta, Liaw, Mehta et al., arXiv:2609.40324, September 2026)

---

## 1. Context & Motivation

Single-prompt Large Language Models, no matter how capable in isolated mathematical reasoning, fail systematically when confronted with open frontier research problems. Open problems require:
1. Long-horizon exploration across competing proof directions.
2. Active overcoming of subtle technical obstructions.
3. Retention and immutable composition of intermediate proven progress.

Google's **Cogentic** demonstrated that by structuring LLM inference into an iterative prove-verify loop—where an orchestrator deploys independent provers across distinct mathematical trajectories, subjects their output to adversarial multi-component verification, and promotes verified intermediate lemmas into a persistent ledger—unsolved problems in theoretical computer science and mathematics (such as online learning, auction theory, and mechanism design) can be settled in only ~100 model calls.

## 2. Decision & Architectural Architecture

CoResearcher adopts and enhances the Cogentic paradigm under **ADR-DISCOVERY-050**, seamlessly integrating it with the sovereign epistemic court:

```
                          ┌──────────────────────────────────────────────┐
                          │         TARGET CONJECTURE STATEMENT          │
                          └──────────────────────┬───────────────────────┘
                                                 │
                                                 ▼
                          ┌──────────────────────────────────────────────┐
                          │    COGENTIC POPULATION PROVER ORCHESTRATOR   │
                          │        (Bounded Budget ~50-100 Calls)        │
                          └──────┬───────────────┼───────────────┬───────┘
                                 │               │               │
                 Trajectory 1:   ▼               ▼               ▼  Trajectory 3:
                 Algebraic Decomposition   Boundary Expansion   Convex Duality Inversion
                                 │               │               │
                                 └───────────────┼───────────────┘
                                                 │ Candidate Lemma Steps
                                                 ▼
                          ┌──────────────────────────────────────────────┐
                          │       ADVERSARIAL MULTI-GATE VERIFIER        │
                          │   (Presumes every step false until proven)   │
                          ├──────────────────────────────────────────────┤
                          │ • Gate 1: Premise Grounding & Deductive Gap  │
                          │ • Gate 2: Implicit Assumption Detector       │
                          │ • Gate 3: Boundary & Counterexample Sweep    │
                          └──────────────────────┬───────────────────────┘
                                                 │
                       ┌─────────────────────────┴─────────────────────────┐
                       ▼                                                   ▼
            [Step Intercepted / Refuted]                        [Step Strictly Verified]
                       │                                                   │
          Emit Obstruction Pheromone to                         Register Immutable Lemma in
           HypothesisGraveyard & Agora                          VerifiedLemmaLedger & ScientificLedger
                       │                                                   │
                       └───────────────────► Merkle Root ◄─────────────────┘
                                            (som_cogentic_hash)
```

### Core Invariants:
1. **Adversarial Verification Posture**: Every candidate lemma is presumed false until passing all 3 specialized verification barriers (deductive validity, boundary counterexample sweep via SymPy, and implicit assumption detection).
2. **Persistent Verified Ledger (`VerifiedLemmaLedger`)**: Confirmed intermediate results are stamped with SHA-256 Merkle proofs (`som_cogentic_hash`) and registered as first-class `CLAIM`/`EVID` artifacts in `ScientificLedger`.
3. **Bounded Compute Scarcity**: Proof campaigns enforce strict model call limits (~50-100 calls) via `CogenticProofOrchestrator`, preventing token explosion and prioritizing verification quality over brute-force rollouts.
4. **Air-Gapped Sovereign Fallback**: Completely operable without cloud dependencies, leveraging local AI models (Laya/LocalIA) with deterministic symbolic degradation.

## 3. Verification & Compliance
- Test suite: `tests/test_cogentic_proof_orchestrator.py` (5/5 tests passing).
- API endpoint: `POST /api/discovery/cogentic/run-proof-discovery`.
- 100% English Compliance verified.
