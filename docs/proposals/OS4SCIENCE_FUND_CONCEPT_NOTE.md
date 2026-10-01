# CoResearcher: Open Epistemic Verification & Physical Invariant Audit Stack for Scientific Foundation Models

**An Infrastructure Project by Fundación de Neurociencias (FdN)**  
*Prepared for the Open Source for Science Fund (Renaissance Philanthropy / Hugging Face / Wellcome / Biohub)*  
**Date:** October 2026  
**License:** MIT / Apache-2.0 Open Source  
**Repository:** [github.com/Fundacion-de-Neurociencias/coresearcher](https://github.com/Fundacion-de-Neurociencias/coresearcher)

---

## 1. Executive Summary

As AI foundation models expand into biology, chemistry, materials science, and physics, over 200 new open-weight scientific models are released monthly on Hugging Face, totaling over 40 million downloads. However, the critical bottleneck across the AI-for-Science ecosystem is **epistemic integrity and reality grounding**:
- LLMs and foundation models frequently hallucinate physically impossible dynamics (e.g., negative thermodynamic entropy, dimensional incoherence, violation of conservation laws).
- Existing evaluation benchmarks measure lexical similarity or narrow benchmark accuracy rather than formal mathematical consistency and empirical grounding.
- Scientific codebases lack automated continuous verification gates to audit model claims against physical laws and empirical datasets before deployment.

**CoResearcher** is a robust, modular, open-source verification and continuous-auditing stack built to solve this bottleneck. Acting as an epistemic firewall and physical consistency layer, CoResearcher bridges empirical scientific data, physical theorem proving, and scientific AI model weights.

---

## 2. The Core Problem: The Unglamorous Plumbing of Scientific AI

Scientific open-source models (such as ESM, AlphaFold derivatives, OpenFold, ChemBERTa, and neural ODE solvers) depend heavily on hundreds of unmaintained utility packages, numerical integrators, and unit converters. When downstream models fail or generate hallucinatory scientific claims:
1. **No Falsification Pipeline**: Generative systems create plausible-sounding theories without automated Popperian stress-testing.
2. **Duhem-Quine Ambiguity**: When a simulation or prediction diverges from reality, developers cannot determine whether the neural surrogate, the auxiliary numerical assumptions, or the underlying dataset failed.
3. **Absence of CI/CD for Physical Laws**: Traditional software CI tests unit logic, but scientific AI requires CI gates that enforce energy conservation, dimensional homogeneity ($[M][L][T]^{-1}$), and topological boundary conditions.

---

## 3. The CoResearcher Solution

CoResearcher introduces four fundamental infrastructure components for open science:

```
+-------------------------------------------------------------------------------+
|                        Hugging Face Hub / Model Pipeline                      |
+---------------------------------------+---------------------------------------+
                                        | (Model Weights & Scientific Code)
                                        v
+-------------------------------------------------------------------------------+
|                          CoResearcher Verification Stack                      |
|                                                                               |
|  1. Physical Invariant Firewall: Conservation laws, dimensional analysis,      |
|     holonomy & symplectic structure validation.                               |
|                                                                               |
|  2. Reality Contact Score (RCS): Formal ratio of empirical data grounding     |
|     to unverified generative assertions (Mandate: RCS >= 2.0).               |
|                                                                               |
|  3. Duhem-Quine Fault Isolator: Automated disambiguation of neural core       |
|     vs auxiliary numerical integration errors.                                |
|                                                                               |
|  4. Epistemic Git / Stigmergy Engine: Cryptographic audit trails of hypotheses,|
|     falsification records, and hypothesis graveyards.                         |
+---------------------------------------+---------------------------------------+
                                        | (Audited Verdicts & Artifacts)
                                        v
+-------------------------------------------------------------------------------+
|                       Open Science Community & Maintainers                    |
+-------------------------------------------------------------------------------+
```

### Key Pillars:
1. **Automated Hugging Face Model Auditing Action (`hf-science-audit-action`)**:
   - A drop-in GitHub Action / PR bot that scans scientific model cards, code, and sample outputs against physical conservation laws and dimensional rigor.
2. **Standardized Reality Contact Metric ($RCS$)**:
   - A reproducible scoring standard ($RCS \ge 2.0$) that measures genuine empirical grounding (actual biological cooler/PDB/ChEMBL/UniProt matrices) versus simulated synthetic outputs.
3. **Model-Agnostic Core CLI & API**:
   - Standalone CLI (`coresearcher audit`, `coresearcher verify`) and high-throughput FastAPI service compatible with any local or cloud runner.

---

## 4. Alignment with Open Source for Science Fund & Hugging Face

- **Targeted Infrastructure**: Directly addresses the "software stack behind open source science" that Renaissance Philanthropy, Biohub, Wellcome, and Hugging Face aim to sustain.
- **Institutional Governance**: Hosted by **Fundación de Neurociencias**, a registered non-profit research foundation dedicated to open-source neurocomputational, biomedical, and scientific rigor.
- **Ecosystem Multiplication**: Benefits thousands of scientific repositories on Hugging Face by providing maintainers with automated scientific verification tooling.

---

## 5. Work Plan & Deliverables (12-Month Scope)

| Phase | Milestone | Objective | Deliverables |
|---|---|---|---|
| **Phase 1** | **Hub Integration & Dataset Connectors** | Direct Hugging Face Hub integration for scientific model card auditing. | `hf-coresearcher` library, connectors to ChEMBL, UniProt, PDB, NCBI. |
| **Phase 2** | **Physical Invariant CI Gate** | Reusable GitHub Action for scientific model and simulation repositories. | `.github/workflows/science-gate.yml`, PR auditor bot. |
| **Phase 3** | **Interactive Hugging Face Space** | Public web-based epistemic audit workbench with Mol* 3D visualization. | Hugging Face Space (Gradio + Mol* + CoResearcher Engine). |
| **Phase 4** | **Benchmark Suite & Community Grants** | Standardized benchmark for physical invariant compliance in AI-for-Science models. | EpistemicBench-AI4S, documentation, developer workshop. |

---

## 6. Budget & Resource Allocation ($150,000 - $250,000)

- **Core Maintainers & Scientific Software Engineers (65%)**: Continuous maintenance, package updates, and community support for open scientific tooling.
- **Compute & Continuous Integration Infrastructure (20%)**: Hardware instances for empirical benchmark runs and testing across diverse scientific models.
- **Documentation, Tutorials & Community Workshops (15%)**: Comprehensive developer guides, tutorials for Hugging Face model creators, and open webinars.

---

## 7. Contact & Organization Information

- **Host Institution:** Fundación de Neurociencias (FdN)
- **Principal Investigator / Lead:** Dr. Manuel Menéndez González
- **Project URL:** `https://github.com/Fundacion-de-Neurociencias/coresearcher`
- **Email:** `contacto@fneurociencias.org`
