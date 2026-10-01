# ADR-EPISTEMIC-029: GUEST Framework Compliance & Methodological Transparency for Systematic Literature Reviews

- **Status**: Accepted
- **Date**: 2026-10-01
- **Author**: Dr. Manuel Menéndez González / Fundación de Neurociencias (FdN)
- **Reference**: Kitchenham et al. (2026), *GUEST: GenAI Use and Evaluation in Systematic Literature Review Tasks* (arXiv:2607.24991).
- **Applies to**: CoResearcher (`LiteratureReviewer`, `GroundedSearchSensor`, `EvidenceGraph`, `SubmissionBundle`) & EdiTXT (`ReviewGraph`, `ReviewSwarm`, `ArbitrationRoom`).

---

## 1. Context and Problem Statement

Systematic Literature Reviews (SLRs) represent the highest standard of evidence synthesis in empirical science and software engineering. The emergence of Generative AI (GenAI) introduces immense potential for literature retrieval, extraction, and synthesis, but simultaneously poses existential risks of citation hallucination, selection bias, and non-reproducible black-box filtering.

Barbara Kitchenham et al. (2026) formulated the **GUEST framework** (*GenAI Use and Evaluation in SLR Tasks*), demonstrating that:
1. Purely unsupervised GenAI automation in SLRs is fundamentally unsound and scientifically unacceptable.
2. Human-in-the-Loop oversight is mandatory across search formulation, candidate selection, quality assessment, and data extraction.
3. Automated tools must provide rigorous transparency, reproducibility trails, and verifiable prompt/trace logs.

CoResearcher and EdiTXT already incorporate Human-in-the-Loop gates (such as the `ArbitrationRoom` and cryptographic `OnTrack` trace contracts), but require a standardized, machine-verifiable compliance export to certify that literature analyses meet the rigorous standards established by Kitchenham et al.

---

## 2. Decision: GUEST-Compliance Architecture

We adopt GUEST as the institutional quality standard for all literature synthesis and evidence retrieval operations within the Neurodiagnoses and CoResearcher ecosystems.

```
+-----------------------------------------------------------------------------------+
|                            CoResearcher Literature Review                         |
|  (GroundedSearchSensor -> OpenAlex / PubMed / CrossRef -> Candidate Ingestion)   |
+-----------------------------------------+-----------------------------------------+
                                          |
                                          v
+-----------------------------------------------------------------------------------+
|                        OnTrack Execution Contract (ADR-001)                       |
|   - Cryptographic SHA-256 trace_id & immutable prompt registry                    |
|   - Deterministic schema validation & raw API payload archiving                   |
+-----------------------------------------+-----------------------------------------+
                                          |
                                          v
+-----------------------------------------------------------------------------------+
|                             GUEST Compliance Gate & Audit                         |
|                                                                                   |
|  1. Citation Grounding Auditor: Verifies 100% DOI/PMID existence (zero halluc.)   |
|  2. Human Oversight Gate: Mandates explicit author sign-off on inclusion/exclusion|
|  3. Metric Thresholds (DeepEval): Completeness >= 0.95, Precision >= 0.98         |
|  4. Automated Methodological Appendix: Generates 'GUEST_COMPLIANCE_REPORT.md'     |
+-----------------------------------------+-----------------------------------------+
                                          |
                                          v
+-----------------------------------------------------------------------------------+
|                         SubmissionBundle / EvidenceGraph                          |
+-----------------------------------------------------------------------------------+
```

---

## 3. Concrete Architectural Specifications

### 3.1. The Four GUEST Pillars in CoResearcher

1. **Human-in-the-Loop Verification (HITL Invariant)**:
   - No literature review or systematic study can transition to `VERIFIED` state without human sign-off in the `ArbitrationRoom`.
   - The user must explicitly inspect and accept inclusion/exclusion boundaries.

2. **Zero-Hallucination Citation Verification**:
   - Every cited entity in `EvidenceGraph` must resolve against official biological/bibliographic indices (OpenAlex, PubMed, CrossRef, EuropePMC).
   - Any unresolvable reference raises a fatal `EpistemicCitationFault` and halts publication.

3. **OnTrack Cryptographic Traceability**:
   - Every prompt, model version, temperature parameter, and retrieved context is sealed under an immutable SHA-256 hash `trace_id`.
   - The methodology section reproduces exact query strings and execution timestamps.

4. **Automated `GUEST_COMPLIANCE_REPORT.md` Generation**:
   - Any synthesized manuscript or `SubmissionBundle` automatically includes an appendix detailing:
     - Search strings and targeted database APIs.
     - Number of initial candidates vs. filtered candidates.
     - Inter-rater agreement between agentic First Readers and the human principal.
     - DeepEval score for epistemic completeness and citation grounding.

---

## 4. Evaluation and CI Integration (NeuroOS Layer 5)

We define a dedicated GUEST evaluation suite in `tests/test_guest_compliance.py`:
- `test_guest_zero_hallucination`: Asserts zero fabricated citations in generated evidence graphs.
- `test_guest_human_arbitration_gate`: Asserts that unapproved reviews fail submission.
- `test_guest_ontrack_reproducibility`: Asserts valid cryptographic provenance hashes for all extracted claims.

Any PR lowering the GUEST compliance score below `0.95` is blocked by CI.

---

## 5. Consequences

### Positive:
- Institutional stamp of methodological rigor based on the preeminent SLR authority (Kitchenham).
- Transparent, audit-proof submission bundles for academic journals and grant bodies.
- Seamless synergy between `OnTrack`, `EvidenceGraph`, and EdiTXT's `ReviewSwarm`.

### Negative / Trade-offs:
- Minor additional latency during literature review execution to perform full CrossRef/PubMed round-trip validation and generate compliance reports.
