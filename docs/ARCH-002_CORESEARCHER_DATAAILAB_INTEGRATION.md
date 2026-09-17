# ARCH-002: CoResearcher & DataAILab Territory Demarcation & Integration Contract

**Version 1.1.0** - Cross-Platform Architectural Specification  
**Status**: Canonical Standard - Inter-Platform Governance  
**Ecosystem**: CoResearcher (Epistemic Engine) ↔ DataAILab (Empirical Execution OS)

---

## 1. Vision & Core Thesis: Separation of Powers

To prevent the system from falling into the common trap of attempting to be simultaneously the theorist, data analyst, code runner, and evaluator of its own results (degenerating into an ungrounded script generator), a strict **Separation of Powers (Solver vs. Verifier)** is formalized:

```
┌─────────────────────────────────────────────────────────────────────────────┐
│ CORESEARCHER: Epistemic Discovery & Governance Engine                        │
│ • Role: Scientific Auditor & Epistemic Judge (Verifier)                      │
│ • Theoretical-Epistemological Layer                                         │
│ • Representations, Constraints, Biological Programs, Trajectories           │
│ • "Human judgment & theoretical framing"                                    │
└──────────────────────────────────────┬──────────────────────────────────────┘
                                       │ (ResearchQuestionContract: RQ-XXXX)
                                       ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│ DATAAILAB: Biomedical Discovery OS & Empirical Research Workspace           │
│ • Role: Autonomous Solver & In-Silico Laboratory (Solver)                    │
│ • Empirical-Computational Layer                                             │
│ • Datasets, Cohorts, Branches (BranchManager), Scientific Object Model (SOM) │
│ • "Autonomous execution & verified in-silico lab"                           │
└──────────────────────────────────────┬──────────────────────────────────────┘
                                       │ (EmpiricalEvidenceContract: EVID-XXXX + SOM Hashes)
                                       ▼
                     [ Audit & Falsification in CoResearcher ]
```

---

## 2. The 4 Architectural Pillars of Integration

### 2.1. Separation of Powers (Solver vs. Verifier)
- **DataAILab** acts as the *Autonomous Solver*: executes in-silico experiments, processes complex cohorts, trains models, and generates empirical statistical evidence.
- **CoResearcher** acts as the *Scientific Auditor / Epistemic Judge*: formulates discriminative predictions *a priori*, receives empirical results, and independently adjudicates whether the hypothesis is corroborated, refuted, or restricted in scope.
- **Principle**: Self-confirmation bias (implicit *p-hacking*) is eliminated by decoupling the engine framing the question from the engine generating and auditing the empirical test.

### 2.2. Synergy with the Scientific Object Model (SOM) and Branch Manager
The integration couples directly to DataAILab's immutability and lineage architecture:
```text
CoResearcher: ResearchQuestionContract (HypothesisTrajectory)
     │
     ▼ (Handshake API/MCP)
DataAILab: ResearchWorkspace
     ├─ SnapshotStore
     │   ├── DatasetSnapshot (SDUHE/OMOP cohort hashes)
     │   ├── CRSSnapshot (Causal Reasoning State)
     │   ├── SIRSnapshot (Scientific Inference Run)
     │   └── ExecutionSnapshot (Deterministic compute trace)
     └─ BranchManager (A/B branches of cohorts, imputations, and models)
     │
     ▼ (EmpiricalEvidenceContract: artifacts + cryptographic lineage hashes)
CoResearcher: Scientific Auditor (Update Discovery Value & Falsification)
```
CoResearcher does not merely receive an isolated number or \(p\)-value: it receives the **cryptographic hash of the complete SOM lineage**, guaranteeing deterministic *Reproducibility by Design*.

### 2.3. Zero Friction & Code Dis-synergies
- **CoResearcher** remains agile, lightweight, and focused on ontologies, unknowns graphs, theoretical representations, and literature. It does not handle heavy GPU/CUDA dependencies, massive 50 GB Parquet matrices, DICOM/NIfTI formats, or multivariate imputation.
- **DataAILab** focuses exclusively on biomedical data engineering, ontological harmonization (OMOP/SDUHE), formal modeling (CRS/SIR), experimental branching, and reproducible statistical computation.

### 2.4. Closed Falsification Loop
The discovery cycle operates as an asynchronous dialogue governed by structured contracts.

---

## 3. Strict Territorial Demarcation

| Dimension | CoResearcher (Epistemic Layer) | DataAILab (Empirical OS Layer) |
|---|---|---|
| **Identity** | *Epistemic Discovery Engine & Scientific Auditor* | *Biomedical Discovery Operating System & Workspace* |
| **Primary Entity** | `Representation`, `BiologicalProgram`, `HypothesisTrajectory` | `ResearchWorkspace`, `ResearchQuestion`, `Dataset`, `Branch` |
| **Abstraction Level** | Conceptual, epistemological, cross-repository | Empirical, statistical, computational, in-silico |
| **Input** | Literature, constraints, anomalies, biological programs | `ResearchQuestionContract`, cohorts (ADNI, PPMI, NACC, etc.) |
| **Output** | Falsifiable hypotheses, scientific audits, \(DV\) | `EmpiricalEvidenceContract`, SOM lineages, models, artifacts |
| **Key Guarantee** | **Epistemological Auditability & Falsification** | **Reproducibility by Design** (SDUHE, CRS, SIR, SOM, SVE) |

---

## 4. Formal Contract Schemas

1. **Downstream (`CoResearcher` $ightarrow$ `DataAILab`)**:
   - Defined in [`schemas/research_question_contract.schema.json`](file:///c:/Users/usuario/coresearcher/schemas/research_question_contract.schema.json).
2. **Upstream (`DataAILab` $ightarrow$ `CoResearcher`)**:
   - Defined in [`schemas/empirical_evidence_contract.schema.json`](file:///c:/Users/usuario/coresearcher/schemas/empirical_evidence_contract.schema.json).\n