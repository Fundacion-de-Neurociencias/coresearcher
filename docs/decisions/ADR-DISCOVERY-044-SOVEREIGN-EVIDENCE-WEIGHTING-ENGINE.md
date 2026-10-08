# ADR-DISCOVERY-044: Sovereign Evidence-Weighting Engine & Sub-Second Jev-Style Adversarial Claim Auditor

## Status
ACCEPTED / IMPLEMENTED

## Date
2026-10-08

## Context
Commercial AI platforms have begun publicizing "Evidence APIs" claiming to search 100M+ scientific papers in under one second to return the "strongest" evidence for and against any scientific claim. However, open technical inquiries from the scientific community (e.g., Christos Efthymiou, PhD; Eric Wu, GXL Paperclip co-founder; Murali D., MD; Matt David, MD) exposed a critical epistemic defect:
1. **Semantic Relevance vs. Epistemic Strength Conflation**: Commercial retrieval engines define "strongest" purely as *topical/semantic text relevance*, returning papers whose prose mentions the claim's keywords rather than studies providing high-fidelity causal evidence.
2. **Publication Bias Vulnerability ("The Unseen Mirror")**: Literature search alone is blind to the fact that negative data is routinely unpublished, and published positive literature in complex domains (such as nutritional epidemiology or preclinical biology) frequently suffers from selective data cuts and *p-hacking*.
3. **Misuse of Sub-Second "Jev-Style" Latency**: Using fast inference as the final epistemic judge turns science into an uncalibrated popularity contest of abstracts ("fast slop"). Fast System 1 models must instead serve as high-throughput extractors feeding deeper System 2 causal auditors.

CoResearcher requires an open, rigorous, and sovereign alternative that provides sub-second query speeds while enforcing a rigorous mathematical separation between semantic relevance, empirical ground truth (Reality Contact Score), and Duhem-Quine methodological confounding.

---

## Architectural Decision

We formalize and implement **`ADR-DISCOVERY-044: Sovereign Evidence-Weighting Engine & Sub-Second Jev-Style Adversarial Claim Auditor`**:

### 1. Dual-Metric Demarcation: Semantic Relevance vs. Epistemic Weight
Every candidate literature citation is assigned two decoupled coordinates:
- **`topical_relevance`** $\in [0, 1]$: Syntactic and semantic proximity of the passage to the scientific claim.
- **`epistemic_weight`** $\in [0, 1]$: Objective methodological strength computed as:
  $$W_{\text{epistemic}} = \text{StudyTypeBase} \times \left(1 + \frac{\text{RCS}}{4}\right) \times (1 - C_{\text{confounding}}) \times \text{ReplicationFactor}$$
  Where:
  - $\text{StudyTypeBase} \in [0.1, 1.0]$: Stratifies study designs (`IN_SILICO_UNVALIDATED`=0.1, `OBSERVATIONAL_EPIDEMIOLOGY`=0.3, `IN_VITRO_PRECLINICAL`=0.5, `MECHANISTIC_ANIMAL_MODEL`=0.7, `RANDOMIZED_CONTROLLED_TRIAL`=0.9, `PREREGISTERED_SYSTEMATIC_META_ANALYSIS`=1.0).
  - $\text{RCS} \in \{0, 1, 2, 3, 4\}$: Reality Contact Score ([ADR-DISCOVERY-010](file:///c:/Users/usuario/coresearcher/docs/decisions/ADR-DISCOVERY-010-REALITY-CONTACT-SCORE.md)).
  - $C_{\text{confounding}} \in [0, 1]$: Methodological vulnerability (unmeasured lifestyle confounders, selective subgroup reporting, lack of multiple comparison corrections).

### 2. Adversarial Evidence Balance & Publication Bias Penalty
Rather than simply counting pro vs. con papers, the engine audits the **Net Evidence Margin**:
$$\Delta_{\text{evidence}} = \sum_{e \in \mathcal{E}_{\text{FOR}}} W_{\text{epistemic}}(e) - \sum_{e \in \mathcal{E}_{\text{AGAINST}}} W_{\text{epistemic}}(e)$$
A **Publication Bias Estimator** computes an asymmetry penalty when a claim is flooded with low-weight observational positives lacking mechanistic or pre-registered negative counter-weights.

### 3. Sub-Second Jev-Style System 1 Extraction with System 2 Causal Escalation
- **System 1 (Jev-Style Sub-Second Filter)**: Executes sub-second regex and vector keyword triage, parsing claim entities, study types, sample sizes, and directional polarities (`SUPPORT`, `REFUTE`, `AMBIGUOUS`).
- **System 2 (Duhem-Quine & Hakken PHELInE Verification)**: If the claim is disputed or the net evidence margin is within ambiguity margins ($|\Delta_{\text{evidence}}| < 0.2$), escalates to the Hakken evidence path perturbation gate ([`EvidencePathPerturbationResult`](file:///c:/Users/usuario/coresearcher/python/discovery/twin_gate_harness.py)) and the Duhem-Quine blame isolation auditor ([`failure_engine.py`](file:///c:/Users/usuario/coresearcher/python/discovery/failure_engine.py)).

### 4. Zero-Cloud Sovereignty & Cryptographic Proof
Operates fully within the local environment ([`ADR-SOVEREIGNTY-041`](file:///c:/Users/usuario/coresearcher/docs/decisions/ADR-SOVEREIGNTY-041-ZERO-TRUST-EPISTEMIC-BUNKER.md)), generating an immutable SHA-256 Merkle stamp (`som_claim_hash`) to guarantee auditable reproducibility without leaking research hypotheses to third-party corporate APIs.

---

## Consequences & Guarantees
- **No False Equivalences**: An observational cohort with $N=500$ will never out-weigh a double-blind, randomized trial with verified mechanistic biomarkers, regardless of keyword frequency.
- **Transparency**: Returns both `topical_relevance` and `epistemic_weight` independently, eliminating developer subjectivity.
- **Sub-Second Performance**: Instantaneous triage suitable for live agent in-turn loops and IDE integrations.
