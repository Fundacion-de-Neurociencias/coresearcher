# ADR-EPISTEMIC-032: Open Explanation Invariant & Oracular Falsification Court (The Terence Tao Invariant)

- **Status**: Accepted
- **Date**: 2026-10-04
- **Author**: Dr. Manuel Menéndez González / Fundación de Neurociencias (FdN)
- **Reference**: Terence Tao & 27 Fields Medalists Open Letter (2026); Codin Mathematics & AI Ethics Manifesto (2026).
- **Applies to**: Full Ecosystem (`PhysicalTheoremCourt`, `ProofDependencyDAG`, `AutoExplicabilityEngine`, `AgoraSharedIndex`, EdiTXT `ReviewSwarm`).

---

## 🏛️ Foundational Axiom: The Terence Tao Invariant

> ### *"Solving mathematical problems is a means to achieve human scientific understanding, not the terminal goal itself."*
> ### *"An oracular assertion without an inspectable, acyclic lemma DAG and an educational decomposition produces zero verified scientific knowledge."*

---

## 1. Context and Problem Statement: The Oracular Avalanche

In Autumn 2026, centralized AI frontier laboratories began claiming mass solutions to longstanding open mathematical problems (e.g., hundreds of unsolved conjectures, millenium problems including 3D Navier-Stokes smoothness) by deploying private, opaque reasoning clusters. This oracular output has inundated academic literature with thousands of pages of unstructured, machine-generated candidate text:
1. **Asymmetry of Cognitive Burden**: Commercial vendors capture financial valuation and headlines by announcing "solved problems", while the exhausting cognitive labor of reviewing, verifying, understanding, and translating these opaque claims into human pedagogy is externalized onto unpaid researchers and peer reviewers.
2. **The "Oracular Box" Pathology**: Modern AI models frequently declare an answer without publishing an independently inspectable proof graph, concealing hidden axiomatic leaps, circular definitions, or unstated boundary conditions.
3. **Decoupling of Solution from Understanding**: True scientific progress requires that a solution not only be correct, but explain *why* it holds, isolating the pivotal geometric or algebraic obstruction that previous generations failed to overcome.

---

## 2. Decision: Open Explanation Invariant & Oracular Court

CoResearcher and the Fundación de Neurociencias formally codify the **Open Explanation Invariant (ADR-EPISTEMIC-032)**:

```
+----------------------------------------------------------------------------------------------------+
|                                THE TERENCE TAO EPISTEMIC GATE                                      |
+----------------------------------------------------------------------------------------------------+
|                                                                                                    |
|  [ INCOMING MATHEMATICAL / PHYSICAL CLAIM ]                                                        |
|  - e.g., Navier-Stokes Global Smoothness, Riemann Hypothesis, Yang-Mills Mass Gap                  |
|                                                                                                    |
+-------------------------------------------------+--------------------------------------------------+
                                                  |
                                                  v
+----------------------------------------------------------------------------------------------------+
|  [ TIER 1: THE ORACULAR REJECTION FILTER ]                                                         |
|  - Check: Does the submission contain an explicit, machine-readable ProofDependencyDAG?            |
|  - REJECT IF: Claim is a monolithic prose block or bare token trace without distinct lemmas.       |
|  - Status: REJECTED_ORACULAR_OPAQUE_CLAIM                                                         |
+-------------------------------------------------+--------------------------------------------------+
                                                  | Passed: Explicit Lemmas Present
                                                  v
+----------------------------------------------------------------------------------------------------+
|  [ TIER 2: AUTOMATED TAO REVIEWER (PhysicalCoherenceCourt) ]                                      |
|  - 1. Topological Acyclicity: Proves lemma graph is a strict DAG (Zero circular reasoning).         |
|  - 2. Hidden Axiom Detection: Flags any unproved "sorry" steps or ungrounded axiomatic leaps.      |
|  - 3. Invariant Conservation: Verifies Leray-Hopf dissipation, Beale-Kato-Majda regularity bounds. |
|  - 4. Adversarial Singularity Hunter: Hunts for Hou-Luo collapse counterexamples.                  |
+-------------------------------------------------+--------------------------------------------------+
                                                  |
                                                  v
+----------------------------------------------------------------------------------------------------+
|  [ TIER 3: AUTO-EXPLICABILITY & MARR TRI-LEVEL DECOMPOSITION ]                                     |
|  - Translates abstract proof DAG into human-comprehensible pedagogical steps:                      |
|     Level 1 (Computational): What is the core obstruction overcome?                                |
|     Level 2 (Algorithmic): What sequence of Sobolev embeddings & energy estimates was used?        |
|     Level 3 (Implementational): Reproducible symbolic/numerical Python/Lean verification code.     |
+-------------------------------------------------+--------------------------------------------------+
                                                  |
                                                  v
+----------------------------------------------------------------------------------------------------+
|  [ REGISTRATION IN AGORA SHARED INDEX ]                                                            |
|  - Verified claims earn a cryptographic SOM-SHA256 signature and are registered as open public     |
|    human knowledge, accompanied by an automated 'PROOF_EXPLANATION_DOSSIER.md'.                   |
+----------------------------------------------------------------------------------------------------+
```

---

## 3. Concrete Architectural Implementations

### 3.1. Prohibition of Unstructured Oracular Claims
No claim submitted to CoResearcher or audited from external sources can be promoted to `VerifiedClaimEntry` if it lacks:
1. An explicit `ProofDependencyDAG` enumerating premises, deduction rules, and formal expressions.
2. A reproducible check in `ScienceIDEInvariantRunner`.
3. An explicit declaration of the mathematical regularities and constraints enforced.

### 3.2. Automated Tao Reviewer (`audit_oracular_proof`)
The `PhysicalTheoremCourt` is enhanced with a dedicated entry point:
```python
def audit_oracular_proof(claim_spec: PhysicalClaimSpec) -> OracularProofAuditReport
```
This engine autonomously audits external AI-generated manuscripts, outputting an itemized balance sheet of verified deductions, circular loops, and unproven lemmas to protect human reviewers from cognitive exhaustion.

---

## 4. Institutional & Ethical Commitments

1. **Defending the Human Scientific Vocation**: CoResearcher views computation as an amplifier of human clarity, not as a replacement for human comprehension.
2. **Open Science Imperative**: All verified lemmas and explanation dossiers are released under open-access licenses (MIT / Apache-2.0 / CC-BY), ensuring that mathematical breakthroughs remain shared human heritage rather than closed corporate assets.
3. **No Hype, Pure Verification**: CoResearcher refuses to publish marketing announcements without releasing the full, verifiable verification artifact simultaneously.

---

## 5. Verification & Testing

Tested in `tests/test_tao_invariant.py`:
- `test_oracular_claim_rejected_without_dag`: Asserts that raw oracular prose without a proof DAG is rejected.
- `test_circular_proof_detected_by_tao_reviewer`: Asserts that circular reasoning loops in candidate proofs are flagged and blocked.
- `test_verified_claim_includes_marr_explanation`: Asserts that any verified theorem exports a multi-level educational explanation report.
