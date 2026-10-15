# ADR-DISCOVERY-037: Automated Theoretical Ablation & Simulated Peer-Review Rebuttal Loop

**Status**: PROPOSED & RATIFIED  
**Date**: 2026-10-06  
**Author**: CoResearcher Epistemic Architecture Board  
**Target Modules**: `python/discovery/ablation_rebuttal_engine.py`, `python/discovery/lagrangian_epistemic_engine.py`, `python/discovery/epistemic_pr_auditor.py`, `api/server.py`  
**Cross-References**: `ADR-DISCOVERY-003` (Hypothesis Alternatives), `ADR-DISCOVERY-019` (Scientific Epistemic PR Auditor), `ADR-EPISTEMIC-033` (Post-PDF Computable Science), `ADR-DISCOVERY-036` (Lagrangian Epistemics)

---

## 1. Context and Problem Statement

Recent breakthroughs in autonomous research frameworks (specifically Google Cloud AI's **ScientistTwo**, Nam, Meng et al., September 2026, arXiv:2609.19644) have demonstrated end-to-end multi-agent scientific discovery outperforming human baselines on top-tier ML benchmarks (ICLR, ICML, NeurIPS). Two critical architectural pillars distinguish this approach:
1. **Automated Ablation Studies**: Systematically turning off individual components, parameters, or theoretical terms to isolate the exact source of empirical gain, proving necessity and sufficiency.
2. **Closed-Loop Simulated Peer-Review & Rebuttal**: Submitting candidate findings to an adversarial peer-review panel, generating evidence-grounded rebuttals to objections, and synthesizing meta-review improvements.

However, frameworks like ScientistTwo operate primarily within machine learning in a closed loop (AI generating code, reviewed by AI). To exploit this methodology for **theoretical physics, mathematical discovery, and multi-domain empirical science** in CoResearcher, we must generalize these capabilities:
- **Theoretical Term Ablation**: Isolating individual interaction potentials, coupling constants, or auxiliary assumptions ($\mathcal{L} = \mathcal{L}_0 + \Delta \mathcal{L}_{\text{int}}$) to prove they are non-superfluous and recover the standard Newtonian/relativistic limit when ablated ($\Delta \mathcal{L}_{\text{int}} \to 0$).
- **Adversarial Rebuttal Grounding**: Ensuring rebuttals are not mere rhetorical prose, but executable proofs anchored in symbolic CAS invariants (`ADR-EPISTEMIC-034`), conservation laws, and empirical data ($RCS \ge 2.0$).

---

## 2. Decision and Epistemic Invariants

CoResearcher ratifies **ADR-DISCOVERY-037**, establishing the **Automated Theoretical Ablation & Simulated Rebuttal Engine** (`AblationRebuttalEngine`):

### Invariant 1: Symbolic & Parameter Ablation Protocol
Every candidate theoretical model, Lagrangian proposal, or empirical pipeline MUST undergo automated component-level ablation:
- **Term Ablation Matrix**: Each interaction term or auxiliary assumption is systematically set to zero or identity:
  $$\Delta \mathcal{L}_i = 0 \quad \forall i \in \{1, \dots, N\}$$
- **Asymptotic Limit Verification**: The engine verifies whether the ablated model cleanly recovers known baseline invariants (e.g., standard free-field propagation, harmonic oscillator, or standard cosmological constant $\Lambda = 0$).
- **Necessity & Sufficiency Score**: A term is certified as essential iff its removal degrades explanatory power or violates boundary conditions without introducing mathematical singularities.

### Invariant 2: Closed-Loop Simulated Rebuttal Loop
1. The system triggers the **Simulated Author Rebuttal Subsystem**.
2. The author agent formulates a formal mathematical defense or coordinate transformation demonstrating that the objection was an artifact of coordinate gauge, or that regularization suppresses the singularity.
3. The **Meta-Review Arbiter** evaluates the rebuttal against the exact symbolic engine.
4. If the defense holds, the item's verdict is promoted to `VERIFIED_WITH_REBUTTAL_ATTACHED`, preserving both the adversarial critique and the definitive proof in the citable ReviewGraph.

### Invariant 3: Zero-Slop Grounding Firewall
Simulated rebuttals are strictly forbidden from relying on plausible text justifications. Every rebuttal MUST link to:
- A symbolic identity verification (`ExactSymbolicCourt`),
- An invariant check (`PhysicalCoherenceCourt`), or
- Real empirical dataset coordinates ($RCS \ge 2.0$).

---

## 3. Structural Specification

```
[Candidate Physical Theory / Corpus Chapter]
                 │
                 ▼
┌────────────────────────────────────────────────────────┐
│  AblationRebuttalEngine (ADR-DISCOVERY-037)           │
│  ├─ AutomatedTermAblator (L_0 + sum Delta L_i)         │
│  ├─ AsymptoticLimitChecker (Recovers baseline physics) │
│  ├─ AdversarialReviewSimulator (Identifies objections) │
│  └─ ClosedLoopRebuttalSynthesizer (Proves defenses)    │
└────────────────────────────────────────────────────────┘
                 │
                 ▼
[AblationMatrixReport & VerifiedRebuttalDossier]
                 │
                 ▼
[Cryptographic ReviewGraph Inscription (SOM-SHA256)]
```

---

## 4. Architectural Boundaries

- **`python/discovery/ablation_rebuttal_engine.py`**: Coordinates term ablation runs, asymptotic limit checks, adversarial objection synthesis, and executable rebuttal evaluation.
- **`python/discovery/lagrangian_epistemic_engine.py`**: Provides the underlying symbolic Euler-Lagrange solver for ablated Lagrangians.
- **`api/server.py`**: Exposes `/api/discovery/ablation-rebuttal/run` for automated batch processing.
