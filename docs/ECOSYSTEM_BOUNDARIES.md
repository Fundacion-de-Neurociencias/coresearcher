# ECOSYSTEM BOUNDARIES: The Computable Scientific Trinity

**Version 1.0.0** - Cross-Platform Constitutional Boundary  
**Status**: Canonical Standard - Inter-Platform Governance  
**Foundation**: Fundación de Neurociencias  
**Ecosystem**: CoResearcher · DataAILab · EdiTXT · GeneForge · Neurodiagnoses

---

## 1. The Ecosystem Trinity

The scientific ecosystem is formally organized as an immutable value chain of three specialized core platforms, eliminating functional duplication and "epistemic spaghetti":

```
┌─────────────────────────────────────────────────────────────────────────────┐
│ 1. CORESEARCHER: Epistemic Discovery & Governance Engine                     │
│    • Role: Epistemic Theorist & Auditor (Traceability Engine)               │
│    • Domain: Constraints, Representations, Biological Programs,             │
│      Hypothesis Trajectories, Unknowns Graphs, and Falsification.           │
│    • Question: "What is the conceptual framework and where is the evidence?"│
└──────────────────────────────────────┬──────────────────────────────────────┘
                                       │ (ResearchQuestionContract: RQ-XXXX)
                                       ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│ 2. DATAAILAB: Biomedical Discovery OS & Empirical Research Workspace        │
│    • Role: In-Silico Laboratory & Autonomous Executor                       │
│    • Domain: Cohorts, Datasets (ADNI/PPMI), BranchManager, SOM,             │
│      Reproducible pipelines (SDUHE, CRS, SIR, SVE, SOM).                    │
│    • Question: "How do we generate deterministic statistical evidence?"     │
└──────────────────┬───────────────────────────────────┬──────────────────────┘
                   │ (EmpiricalEvidenceContract)       │ (ReleaseManifest / SOM Artifacts)
                   ▼                                   ▼
[ CoResearcher: Falsification & Audit ]          ┌────────────────────────────────┐
                                                 │ 3. EDITXT: Computable Press    │
                                                 │    • Role: Scientific Press    │
                                                 │      & Peer Review             │
                                                 │    • Domain: Manuscripts,      │
                                                 │      ReviewGraphs, Inconsis-   │
                                                 │      tency Detection.          │
                                                 │    • Question: "What method-   │
                                                 │      ological/editorial flaws  │
                                                 │      does the paper have?"     │
                                                 └────────────────────────────────┘
```

---

## 2. Strict Territorial Demarcation

| Dimension | **CoResearcher** | **DataAILab** | **EdiTXT** |
|---|---|---|---|
| **Primary Mission** | Epistemic Discovery & Traceability | Empirical Experimentation & Compute | Computable Publishing & Peer Review |
| **Central Entity** | `Representation`, `BiologicalProgram`, `HypothesisTrajectory` | `ResearchWorkspace`, `ResearchQuestion`, `SnapshotStore`, `Branch` | `Manuscript`, `ReviewGraph`, `ReleaseManifest` |
| **Main Input** | Literature, constraints, anomalies, biological programs | `ResearchQuestionContract`, clinical cohorts (OMOP, DICOM, Parquet) | Manuscript + `EvidenceGraph` (from CoResearcher) + `ReleaseManifest` (from DataAILab) |
| **Main Output** | `EvidenceGraph`, `ResearchQuestionContract`, Trajectory Reports | `EmpiricalEvidenceContract`, SOM Artifacts with cryptographic hashes | `ReviewGraph`, Certified Computable Manuscript, DOI / Zenodo release |
| **Non-Negotiable Guarantee** | **Epistemological Auditability & Falsification** | **Reproducibility by Design** (Determinism) | **Editorial Integrity & Reproducible Publishing** |

---

## 3. Inter-Platform Handshake Contracts

### Contract A: CoResearcher $\longrightarrow$ DataAILab (`ResearchQuestionContract`)
CoResearcher formalizes the scientific question, exposure/outcome variables, falsification thresholds, and boundary conditions (*Scope Conditions*).
* Schema: [`schemas/research_question_contract.schema.json`](file:///c:/Users/usuario/coresearcher/schemas/research_question_contract.schema.json)

### Contract B: DataAILab $\longrightarrow$ CoResearcher (`EmpiricalEvidenceContract`)
DataAILab executes pipelines and returns empirical results with the complete cryptographic SOM lineage (`DatasetSnapshot`, `CRSSnapshot`, `SIRSnapshot`, `ExecutionSnapshot`).
* Schema: [`schemas/empirical_evidence_contract.schema.json`](file:///c:/Users/usuario/coresearcher/schemas/empirical_evidence_contract.schema.json)

### Contract C: DataAILab + CoResearcher $\longrightarrow$ EdiTXT (`ReleaseManifest` + `EvidenceGraph`)
* **DataAILab** provides the `ReleaseManifest` with data artifacts, reproducible figures, and statistical tables.
* **CoResearcher** provides the `EvidenceGraph` to verify that every claim in the paper has immutable provenance support.
* **EdiTXT** compiles the computable manuscript and generates the publication audit `ReviewGraph`.

---

## 4. Cross-Platform Constitutional Invariants (Non-Negotiables)

1. **CoResearcher**:
   - ❌ NEVER processes heavy raw imaging or genomic sequence data.
   - ❌ NEVER writes editorial manuscript prose or renders stylistic judgments.
2. **DataAILab**:
   - ❌ NEVER self-audits the epistemic value or theoretical novelty of its findings.
   - ❌ NEVER invents ontologies or assertions unsupported by deterministic execution.
3. **EdiTXT**:
   - ❌ NEVER calculates statistics, ML models, or \(p\)-values from scratch.
   - ❌ NEVER invents evidence chains without querying CoResearcher's `EvidenceRegistry`.

---

*This architecture definitively seals the epistemological, empirical, and editorial coherence across the scientific ecosystem.*\n