# ARCH-003: Full Ecosystem Integration & EdiTXT Computable Living Editor

**Version 1.0.0** - Cross-Platform Integration & Frontend Specification  
**Status**: Canonical Standard - Tripartite Implementation Plan  
**Ecosystem**: CoResearcher · DataAILab · EdiTXT

---

## 1. Global Vision: The Computable Science Triangle

The infrastructure of Fundación de Neurociencias unifies its three platforms into a seamless value chain:

```
┌─────────────────────────────────────────────────────────────────────────────┐
│ 1. CORESEARCHER (The Epistemic Engine & Scientific Auditor)                 │
│    • Formulates ResearchQuestions, detects EpistemicGaps, defines           │
│      falsification thresholds.                                              │
│    • Publishes the ScientificLedger to Zenodo with an immutable DOI.        │
└──────────────────────────────────────┬──────────────────────────────────────┘
                                       │ (ResearchQuestionContract: RQ-XXXX)
                                       ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│ 2. DATAAILAB (The In-Silico Laboratory & Discovery OS)                      │
│    • Executes deterministic pipelines over cohorts and manages branches.    │
│    • Produces immutable SOM Snapshots (Dataset, CRS, SIR, Execution, Art).   │
│    • Exposes live API: /api/workspace/summary, /api/checkout/{id}.          │
└──────────────────┬───────────────────────────────────┬──────────────────────┘
                   │ (EmpiricalEvidenceContract)       │ (ReleaseManifest + API)
                   ▼                                   ▼
[ CoResearcher: Falsification & Audit ]          ┌────────────────────────────────┐
                                                 │ 3. EDITXT (The Computable      │
                                                 │    Living Press Frontend)      │
                                                 │    • Living Document (TipTap)  │
                                                 │    • Epistemic Inspector       │
                                                 │    • Live Claim Binding        │
                                                 │    • Reactive Stale Figure     │
                                                 │      Detection                 │
                                                 └────────────────────────────────┘
```

---

## 2. EdiTXT Frontend Specification

### 2.1. Editor Architecture
The EdiTXT frontend is not a traditional word processor (Word/Google Docs), but a **Structured Computable Writing Canvas**:
* **Central Panel (*The Living Document*)**: Rich-text editor based on *TipTap / ProseMirror* supporting semantic text blocks, mathematical equations (KaTeX), dynamic tables, and figures anchored to SOM hashes.
* **Right Side Panel (*The Epistemic Inspector*)**: Reactive inspector auditing in real time:
  - **Claim Registry**: List of manuscript assertions bound to DataAILab executions.
  - **EvidenceGraph Viewer**: Support/contradiction graph retrieved from CoResearcher.
  - **Integrity Findings**: Discrepancy alerts between textual numbers and `ReleaseManifest` hashes.

---

## 3. Real-Time Integration Protocol: DataAILab $\longleftrightarrow$ EdiTXT

### 3.1. Computable Claim Binding
1. The researcher writes in EdiTXT: *"The treatment reduces the annualized hippocampal atrophy rate (\(\beta = -0.42, p = 0.001\))."*
2. Selects text $ightarrow$ Right-click: **"Bind to DataAILab Execution"**.
3. EdiTXT queries live `GET /api/workspace/summary` and presents active branches (`main`, `apoe4_stratified`, etc.) and their `execution` commits.
4. The user selects the execution $ightarrow$ EdiTXT calls `GET /api/checkout/{exec_id}` and extracts mathematical metrics (`metrics.slope_per_time`, `metrics.p_value`).
5. The text is sealed with the immutable hash. If an author manually alters the text number, violating empirical truth, EdiTXT's **Integrity Engine** flags the claim as `CRITICAL_INCONSISTENCY`.

### 3.2. Living Figures and Stale Figure Detection
1. The user inserts a figure block in EdiTXT.
2. EdiTXT consumes DataAILab's `ArtifactSnapshot` (`art_fig_...`) and renders the live image (`figure.png`).
3. **Lineage Reactivity**: If DataAILab re-runs the pipeline with updated data or a new covariate, a new commit with a new hash is generated. EdiTXT detects the divergence in the `CommitGraph` and badges the figure as **`STALE_FIGURE`**, allowing the author to update with a single click.

### 3.3. Asynchronous Hypothesis Forking (*Request Hypothesis Fork*)
If during writing the author requires a statistical variant (e.g., sex stratification or adding a covariate):
* Clicks **"Request Hypothesis Fork"** in EdiTXT.
* EdiTXT dispatches a `POST /api/pipeline/run` to DataAILab with requested parameters.
* DataAILab generates the experimental branch in the background, produces new SOM snapshots, and returns the new `ReleaseManifest` directly to EdiTXT.

---

## 4. Zenodo Publication and Closing the Loop (Zenodo / DOI)

Once the manuscript in EdiTXT reaches approval:
1. EdiTXT compiles the **Certified Computable Manuscript**.
2. Requests CoResearcher to issue the final deposit.
3. CoResearcher combines the `EvidenceGraph` + DataAILab artifacts and triggers `ZenodoPublisher` to mint the **official DOI (`10.5281/zenodo.XXXXXX`)**.
4. The DOI is permanently embedded into the paper header.\n