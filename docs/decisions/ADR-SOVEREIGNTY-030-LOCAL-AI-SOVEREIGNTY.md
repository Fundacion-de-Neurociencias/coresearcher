# ADR-SOVEREIGNTY-030: Sovereign Local AI Infrastructure & Epistemic Expropriation Resistance

- **Status**: Accepted
- **Date**: 2026-10-03
- **Author**: Dr. Manuel Menéndez González / Fundación de Neurociencias (FdN)
- **Applies to**: Full Ecosystem (CoResearcher, AIDataLab, GeneForge, Neurodiagnoses, EdiTXT, Vadimecum)

---

## 🏛️ Foundational Axioms and Manifestos

> ### *"Make sure you own the AI you consume."*
> ### *"Cloud AI is not aligned with you; it is aligned with the corporation that owns it."*

---

## 1. Context and Problem Statement: Epistemic Expropriation in Cloud AI

A critical debate has emerged across the international research community regarding the deployment of centralized proprietary cloud AI (OpenAI, Anthropic, Google, Microsoft) in scientific discovery. Multiple independent investigators and academic laboratories have reported instances of **epistemic expropriation**:
1. **Unsolicited Idea Mining & Training Ingestion**: Prompts, unpublished raw datasets, candidate hypotheses, novel mathematical derivations, and unpatented chemical/biological structures submitted to cloud APIs are ingested, logged, and periodically incorporated into internal model fine-tuning loops or used to inform the frontier labs' proprietary research directions.
2. **Confidentiality & Competitive Asymmetry**: Centralized frontier model providers operate commercial applied AI initiatives (e.g., drug discovery, materials science, quantum computing). Transmitting leading-edge scientific reasoning across remote cloud pipes creates an unacceptable vector for intellectual property loss, front-running of scientific breakthroughs, and preemptive patent filings.
3. **Misalignment of Objectives**: Cloud AI endpoints are governed by commercial terms of service, telemetric surveillance, censorship filters, and corporatist alignment goals. **Cloud AI is fundamentally aligned with the corporation that owns the weights and servers, not with the sovereign researcher or the independent scientific institution.**

---

## 2. Institutional Directive: The Sovereign Local AI Stack

To ensure that research institutions, hospitals, and independent scientists retain absolute sovereignty over their discoveries, Fundación de Neurociencias formally decrees:

> **All computational research, hypothesis formulation, dataset analysis, and manuscript synthesis across CoResearcher, AIDataLab, GeneForge, Neurodiagnoses, and EdiTXT must support and prioritize local, air-gapped GPU execution.**

```
+-----------------------------------------------------------------------------------------+
|                                THE SOVEREIGN LOCAL AI STACK                             |
+-----------------------------------------------------------------------------------------+
|                                                                                         |
|  [ EdiTXT ]          [ CoResearcher ]         [ AIDataLab ]         [ GeneForge ]       |
|  Manuscript Editor   Epistemic Verifier       Empirical OS          Splicing / Genomics |
|  & ReviewSwarm       & Physical Courts        & Cohort Pipelines    & Variant Discovery |
|                                                                                         |
+--------------------------------------------+--------------------------------------------+
                                             | Local Zero-Cloud Pipes (Unix / Loopback)
                                             v
+-----------------------------------------------------------------------------------------+
|                      LOCAL HARDWARE & ACCELERATION LAYER (AIR-GAPPED)                   |
|                                                                                         |
|   - Workstations / Nodes: NVIDIA RTX / Mac Studio / On-Premise DGX Cluster              |
|   - Runtime Adapters: LocalAIAdapter (v3.0) -> Ollama / LM Studio / vLLM               |
|   - Open Weight Engines: DeepSeek-R1 / LLaMA-3 / Mistral / Qwen / Gemma                 |
|   - Cryptographic Boundary: 100% Zero Outbound Cloud Telemetry                          |
|                                                                                         |
+-----------------------------------------------------------------------------------------+
                                             |
                                             v
+-----------------------------------------------------------------------------------------+
|                               PROTECTED SCIENTIFIC LEDGER                               |
|   - Local Git & OnTrack SHA-256 Provenance Contracts                                    |
|   - Zero Third-Party Expropriation Risk                                                 |
|   - Irrefutable Authorship & Intellectual Property Sovereignty                          |
+-----------------------------------------------------------------------------------------+
```

---

## 3. Concrete Architectural Invariants across Ecosystem Softwares

### 3.1. CoResearcher (The Epistemic Engine)
- **LocalAIAdapter First**: `PhysicsCorpusAuditor` and `PhysicalTheoremCourt` prioritize `System 1` (Laya / Ollama at `localhost:11434`) and `System 2` (Local IA / LM Studio at `localhost:1234`), falling back to deterministic local solvers rather than cloud endpoints.
- **Zero-Cloud Audit Trails**: When running exhaustive corpus audits (such as `audit_physics_megarepo_full.py`), no hypothesis text, proof step, or raw observation is ever transmitted to commercial third-party APIs.

### 3.2. AIDataLab (The Empirical OS)
- **Zero-Telemetry Patient Data**: Clinical data (e.g., `metaboad_atn_processed.csv`) and protected health information (PHI) remain strictly on-device. Neural differential equations and feature extractions execute over local CUDA/MPS acceleration.
- **Physical Invariant Enforcement**: Local execution eliminates the risk of cloud providers harvesting latent biological biomarkers or metabolic signatures.

### 3.3. GeneForge & Neurodiagnoses
- **Genomic & Proteomic Privacy**: Splice-site predictions, 3D structural folding, and variant pathogenicity scores run locally using quantized open-weight checkpoints.
- **EBRAINS / Open Science Compliance**: Ensures data protection mandates (GDPR, EU AI Act, DA 17ª) without vendor lock-in.

### 3.4. EdiTXT (The Scientific Authoring Environment)
- **Confidential Peer Review & Drafting**: `ReviewSwarm` and `LiteratureReviewer` execute against locally cached OpenAlex/PubMed snapshots or local embeddings.
- **Arbitration Room Sovereignty**: The human investigator maintains sole custody of the `ChangeSet` without drafts leaking to cloud LLM providers.

---

## 4. Strategic Positioning & Institutional Value Proposition

For universities, pharmaceutical departments, healthcare consortiums, and sovereign research foundations, our unified software stack delivers a decisive advantage:

1. **Guaranteed Intellectual Property Custody**: Discoveries remain mathematically quarantined inside institutional perimeter firewalls.
2. **Deterministic Reproducibility**: Local open weights eliminate model drift, silent API depreciation, and backend alterations by cloud vendors.
3. **Constitutional Alignment**: Aligns with the core motto:
   > *"Make sure you own the AI you consume. Cloud AI is not aligned with you; it is aligned with the corporation that owns it."*

---

## 5. Verification & Compliance Gate

- **CI Enforcement**: Automated checks verify that zero non-consensual outbound telemetry or cloud API dependencies exist in core audit loops.
- **Air-Gapped Tests**: Pytest suites must execute cleanly without internet connectivity using mock-free local runners.
