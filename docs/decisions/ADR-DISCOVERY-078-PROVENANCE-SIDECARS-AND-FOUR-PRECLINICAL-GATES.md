# ADR-DISCOVERY-078: Provenance Sidecars & Four Pre-Clinical Gates Governance (OASE Engine Integration)

**Status**: PROPOSED & RATIFIED  
**Date**: 2026-10-26  
**Author**: CoResearcher Epistemic Architecture Board  
**Cross-References**: `ADR-DISCOVERY-017` (Physical Theorem Court), `ADR-EPISTEMIC-032` (Terence Tao Invariant), `ADR-EPISTEMIC-033` (Post-PDF Computable Science), `ADR-EPISTEMIC-034` (Exact Symbolic Dual-Verification), `ADR-MECH-001` (Biological Mechanism Layer)

---

## 1. Context and Problem Statement

Scientific agentic systems in life sciences and computational drug discovery face an acute epistemic trust crisis:
1. **Unverifiable Generative Narratives**: Multi-agent LLM systems routinely generate convincing pre-clinical hypotheses and pharmacological summaries without providing an auditable provenance trail linking claims back to raw computational or experimental oracle outputs.
2. **Epistemic Dishonesty via Fallback Prior Hallucination**: When upstream biological datasets, structural oracles (e.g., AlphaFold, AlphaGenome), or bioactivity databases (ChEMBL, ClinVar, GTEx) are unreachable or missing, typical agents fabricate plausible binding affinities, p-values, and druggability metrics from parametric weights rather than halting.
3. **Unversioned Subjective Gate Evaluation**: Target hypotheses are evaluated against loose, shifting qualitative criteria written in natural language prompts rather than immutable, versioned, programmatic thresholds.
4. **"In pharma, a result you cannot trace is a result you cannot trust"**: Google Cloud's Open Agentic Science Engine (OASE v0.1) demonstrates that advancing an agentic system from a tech demo to an enterprise-grade discovery engine requires hard provenance sidecars, sovereign IAM execution, and reproducible execution contracts.

---

## 2. Decision and Epistemic Invariants

CoResearcher ratifies **ADR-DISCOVERY-078**, formalizing the **Provenance Sidecar Engine** (`ProvenanceSidecarEngine`) and the **Four Pre-Clinical Gates Validator** (`PreClinicalGatesValidator`), fully arbitrated by the `PhysicalCoherenceCourt`.

### Invariant 1: Radical Epistemic Honesty (`BLOCKED_MISSING_DATA` Invariant)
If an upstream tool, structural model, or biological dataset is unavailable, the agent is strictly prohibited from substituting parametric priors or generating plausible synthetic approximations:
$$\text{State}(Tool, Data) = \emptyset \implies \text{Status} = \text{BLOCKED\_MISSING\_DATA}$$
The system halts execution for that branch, records the exact missing resource dependency, and issues a non-negotiable blocking verdict in the passport.

### Invariant 2: Cryptographic Provenance Sidecars (`.sidecar.json`)
Every computational or oracle tool execution MUST emit an immutable companion `.sidecar.json` document containing:
- Unique deterministic sidecar ID.
- Exact git commit SHA of the running codebase.
- Canonical JSON SHA-256 digest of input parameters: $H_{\text{input}} = \text{SHA256}(\text{JSON}_{\text{sorted}}(inputs))$.
- SHA-256 digest of raw tool outputs: $H_{\text{output}} = \text{SHA256}(\text{JSON}_{\text{sorted}}(outputs))$.
- Standalone CLI command string allowing third-party reviewers to reproduce the exact computation on their own infrastructure.
- Cryptographic verification seal:
$$H_{\text{sidecar}} = \text{SHA256}(id \parallel tool \parallel timestamp \parallel sha \parallel H_{in} \parallel H_{out} \parallel status)$$

### Invariant 3: The Four Pre-Clinical Gates Architecture
Every target or chemical hypothesis advancing toward pre-clinical validation must satisfy four canonical gates:
1. **Gate 1: Genetic Causality Gate**: Audits human genetic association, odds ratio ($OR \ge 1.30$), GWAS/PheWAS significance ($p \le 5 \times 10^{-8}$), or ClinVar pathogenic concordance.
2. **Gate 2: Structural Druggability Gate**: Evaluates AlphaFold/cryo-EM pocket volume ($V_{\text{pocket}} \ge 250\text{ \AA}^3$), druggability score ($D \ge 0.65$), and structural resolution ($RMSD \le 2.50\text{ \AA}$).
3. **Gate 3: Biophysical Mechanism Gate**: Confirms binding affinity ($K_D \le 10\text{ }\mu\text{M}$ or $-\Delta G \ge 6.8\text{ kcal/mol}$), teleonomic selectivity ratio ($S \ge 100$), and lack of competitive ionic collapse.
4. **Gate 4: Safety & Off-Target Counter-Screening Gate**: Evaluates off-target selectivity ($\ge 50\times$ window against hERG, CYP450 isoforms, and essential kinases) and lack of pan-assay interference (PAINS).

Only candidates that satisfy all four gates with verified empirical evidence are granted a `PreClinicalPassport` with verdict `PASSED_ALL_GATES`.

### Invariant 4: Versioned Programmatic Threshold Configurations
Gate thresholds are never embedded in free-form LLM prompts. They are instantiated as versioned programmatic schemas (`GateThresholdsConfig`), e.g., `v1.0.0-canonical`, with explicit program overrides permitted only via transparent, version-controlled configuration objects.

### Invariant 5: Sovereign Physical Court Arbitration
`PhysicalCoherenceCourt` enforces two new conservation laws:
- `PRECLINICAL_FOUR_GATES_COHERENCE`: Enforces that no candidate is certified without passing all four gates or with unverified/blocked status.
- `PROVENANCE_SIDECAR_VALIDITY`: Enforces that every tool invocation includes a valid cryptographic verification hash matching the input and output digests.

---

## 3. Architecture & Data Flow

```
[System 1 Candidate Generator / Target Hypothesis]
                      │
                      ▼
          [PreClinicalGatesValidator]
    ┌─────────────────┴─────────────────┐
    │                                   │
[Gate 1: Genetic Causality]   [Gate 2: Structural Druggability]
    │                                   │
[Gate 3: Biophysical Mechanism] [Gate 4: Safety & Off-Target]
    └─────────────────┬─────────────────┘
                      ▼
          [PreClinicalPassport]
           (Cryptographic Hash)
                      │
                      ▼
          [ProvenanceSidecarEngine]
      (Emits *.sidecar.json per tool)
                      │
                      ▼
          [PhysicalCoherenceCourt]
   (Arbitrates PRECLINICAL_FOUR_GATES_COHERENCE
    and PROVENANCE_SIDECAR_VALIDITY)
                      │
                      ▼
        [Interactive Evidence Portal]
   (Displays 4-Gate Badges, Sidecar Link)
```

---

## 4. Verification and Empirical Metrics

1. **Unit Test Suite**: `tests/test_provenance_and_preclinical_gates.py` exercises 7 comprehensive test vectors:
   - `test_provenance_sidecar_generation_and_serialization`: Verified tool wrapping, hash computation, and file persistence.
   - `test_provenance_sidecar_blocked_missing_data`: Verified that unavailable resources generate valid `BLOCKED_MISSING_DATA` sidecars without hallucination.
   - `test_provenance_sidecar_reproducibility_verification`: Verified independent re-execution against raw digests.
   - `test_four_preclinical_gates_candidate_all_pass`: Verified complete passport pass for Troponin C Site II candidate.
   - `test_four_preclinical_gates_candidate_fails_safety_offtarget`: Verified gate 4 failure detection when hERG liability is present.
   - `test_four_preclinical_gates_missing_evidence_triggers_blocked`: Verified that absent evidence triggers `PassportVerdict.BLOCKED_MISSING_DATA`.
   - `test_preclinical_gates_versioned_threshold_override`: Verified program-specific threshold tuning.
2. **Regression Suite**: All 19 existing discovery tests (`test_cartan_dec_and_evidence_portal.py`, `test_structure_property_purpose_engine.py`, `test_continuum_and_multibody_physics_adapters.py`) pass with 100% concordance.
3. **Evidence Portal Integration**: `python/discovery/evidence_portal.py` generates `web/discovery_portal/index.html` with interactive 4-Gate badges, sidecar deep links, and cryptographic passport hashes.

---

## 5. Consequences

- **Positive**: Complete compliance with industrial biopharma standards. Hypotheses cannot advance without verifiable provenance. Zero hallucination when data is missing.
- **Negative**: Adds rigid verification constraints that reject hypotheses lacking complete 4-domain multi-scale experimental/computational evidence.
- **Security & Sovereignty**: All calculations and sidecars execute locally or in sovereign GCP projects with IAM-based identity, strictly maintaining local data governance.
