# DOMAIN MODULES
**Version 1.0.0** - Specialized Scientific Applications  
**Status**: Canonical Reference  
**Platforms**: CoResearcher, GeneForge, Neurodiagnoses, PharmaOracle, EdiTXT, DataAILab

---

## 1. Module Catalog

### 1.1 CoResearcher

**Domain**: General Scientific Traceability  
**Status**: Production  
**Language**: TypeScript + Python  
**Primary Responsibility**: Transform observable scientific artifacts into auditable EvidenceGraph

#### Core Components

**Observer System**:
```yaml
Location: python/observer/
Responsibilities:
  - Scan GitHub (issues, PRs, commits, releases)
  - Observe Zenodo deposits
  - Monitor PubMed/CrossRef/OpenAlex
  - Extract raw scientific activity

Outputs:
  - OBS-XXXXXX (raw observations)
  - Raw JSON dumps
```

**Semantic Compiler**:
```yaml
Location: python/semantic_compiler/
Responsibilities:
  - Transform raw observations → primitives
  - Classify epistemic types (observable, derivable, inferred)
  - Assign confidence scores
  - Enforce constitutional rules

Outputs:
  - QUESTION-XXXXXX
  - ACTION-XXXXXX
  - CLAIM-XXXXXX
```

**Ledger Normalizer**:
```yaml
Location: python/observer/ledger_normalizer.py
Responsibilities:
  - Reconstruct Scientific Activity Graph
  - Build EvidenceGraph from primitives
  - Compute Evidence Descriptors
  - Detect failures and contradictions

Outputs:
  - EvidenceGraph (EG-XXXXXX)
  - Trajectory Report
  - Failure Taxonomy
```

**Key Differentiators**:
- Domain-agnostic (works with any scientific domain)
- Emphasis on traceability, not evaluation
- Constitutional compliance enforced at compiler level
- MCP Server as primary integration point

---

### 1.2 GeneForge

**Domain**: Genomics & Gene Editing  
**Status**: Active Development  
**Language**: Python  
**Primary Responsibility**: DSL for genomic workflows with full evidence traceability

#### Core Components

**GeneForge Language (GFL)**:
```yaml
Location: gfl_core/
Responsibilities:
  - Parse GFL scripts (genomic workflow DSL)
  - Validate genomic operations
  - Execute workflows (CRISPR, alignment, variant calling)
  - Emit provenance records

Syntax:
  edit target=BRCA1 site=exon_11 method=prime_editor
  align reference=hg38 reads=sample_R1.fastq.gz
  annotate vcf=output.vcf database=gnomAD
```

**Evidence Adapters**:
```yaml
Location: evidence_adapters/
Responsibilities:
  - Map genomic tool outputs → EvidenceGraph primitives
  - Link artifacts to published literature
  - Track workflow provenance

Adapters:
  - bowtie2_adapter
  - bwa_adapter
  - gatk_adapter
  - crispr_offtarget_adapter
```

**CRISPR Optimizer**:
```yaml
Location: GeneForge/optimizers/
Responsibilities:
  - Optimize guide RNA sequences
  - Predict off-target effects
  - Score editing efficiency
  - Generate evidence chains for optimization decisions

Outputs:
  - Optimized guide sequences
  - Off-target predictions with evidence
  - Efficiency scores with supporting literature
```

**Key Differentiators**:
- Domain-specific DSL for genomics
- Tight integration with Evidence Registry
- Native support for genomic file formats (FASTA, FASTQ, BAM, VCF)
- Evidence-backed optimization (not black-box)

**Dependencies**:
- Shared: Provenance Engine, Evidence Registry, MCP Protocol
- External: Biopython, pysam, CRISPR scan tools

---

### 1.3 Neurodiagnoses

**Domain**: Neuroscience & Neuroimaging  
**Status**: Active Development  
**Language**: TypeScript  
**Primary Responsibility**: Neuroimaging biomarker detection and clinical simulation

#### Core Components

**Clinical Simulation Engine**:
```yaml
Location: packages/clinical-simulation-engine/
Responsibilities:
  - Simulate neurodegenerative disease progression
  - Generate synthetic neuroimaging data
  - Model biomarker trajectories (amyloid, tau, atrophy)
  - Produce evidence-linked simulations

Outputs:
  - Synthetic MRI/PET scans
  - Biomarker time series
  - EvidenceGraph for simulation parameters
```

**Biomarker Detector**:
```yaml
Responsibilities:
  - Detect biomarkers from imaging data
  - Correlate with clinical outcomes
  - Link detections to literature evidence

Biomarkers:
  - Amyloid-beta (PET)
  - Tau (PET, CSF)
  - Hippocampal atrophy (MRI)
  - Cortical thickness (MRI)
```

**Evidence Integration**:
```yaml
Responsibilities:
  - Link detections to published papers (DOI, PMID)
  - Track validation studies
  - Build EvidenceGraph for each biomarker claim
```

**Key Differentiators**:
- Clinical simulation before real data
- Standard neuroimaging formats (DICOM, NIfTI)
- Biomarker-specific evidence chains
- Regulatory compliance (FDA, CE marks)

**Dependencies**:
- Shared: MCP Protocol, Evidence Registry
- External: Numpy, Scipy, NiBabel, DCMQI

---

### 1.4 PharmaOracle

**Domain**: Pharmacology & Drug Discovery  
**Status**: Strategic Planning  
**Language**: Python (planned)  
**Primary Responsibility**: Drug repurposing and molecular optimization

#### Planned Components

**Molecular Docking Engine**:
```yaml
Responsibilities:
  - Perform molecular docking simulations
  - Predict binding affinities
  - Generate pose ensembles with evidence

Outputs:
  - Docking scores with confidence intervals
  - Binding poses (PDB files)
  - EvidenceGraph linking to literature
```

**ADMET Predictor**:
```yaml
Responsibilities:
  - Predict Absorption, Distribution, Metabolism, Excretion, Toxicity
  - Train on curated datasets
  - Provide evidence for predictions

Outputs:
  - ADMET profiles
  - Evidence chains for each prediction
  - Comparison to known drugs
```

**Drug Repurposing Engine**:
```yaml
Responsibilities:
  - Scan approved drugs for new indications
  - Analyze drug-disease networks
  - Suggest repurposing candidates with evidence

Outputs:
  - Repurposing candidates ranked by evidence strength
  - EvidenceGraph for each candidate
  - Clinical trial suggestions
```

**Key Differentiators**:
- Emphasis on explainability (evidence-backed predictions)
- Integration with clinical trial databases (ClinicalTrials.gov)
- Safety-first approach (toxicity prioritized)

**Dependencies**:
- Shared: Evidence Registry, Provenance Engine, MCP Protocol
- External: RDKit, OpenBabel, AutoDock, DeepChem

---

### 1.5 EdiTXT

**Domain**: Scientific Editing & Peer Review  
**Status**: Strategic Planning  
**Language**: TypeScript (planned)  
**Primary Responsibility**: Systematic peer review with auditable revision tracking

#### Planned Components

**ReviewGraph Generator**:
```yaml
Responsibilities:
  - Accept manuscript submissions
  - Orchestrate multi-reviewer process
  - Generate structured ReviewGraph

Nodes:
  - FINDING: "Methodology lacks statistical power analysis"
  - ISSUE: "Statistical power"
  - REVISION: "Added power analysis (α=0.05, 1-β=0.8)"
  - RECOMMENDATION: "Minor revision required"
```

**Revision Tracker**:
```yaml
Responsibilities:
  - Track author responses
  - Verify issue resolution
  - Update ReviewGraph with revisions

Outputs:
  - Revision diff
  - Issue resolution status
  - Updated ReviewGraph
```

**Evidence Linker**:
```yaml
Responsibilities:
  - Link review findings to EvidenceGraph claims
  - Validate author citations
  - Check for contradictory evidence

Outputs:
  - Linked EvidenceGraph + ReviewGraph
  - Citation validation report
```

**Key Differentiators**:
- Structured, machine-readable reviews (not PDF)
- Evidence-linked findings (not subjective opinions)
- Revision transparency (full audit trail)
- Author-researcher identity (ORCID integration)

**Dependencies**:
- Shared: Evidence Registry, Graph Runtime, MCP Protocol
- External: PDF parsers, diff engines, LaTeX processors

---

### 1.6 DataAILab

**Domain**: Data Science & Machine Learning  
**Status**: Strategic Planning  
**Language**: Python (planned)  
**Primary Responsibility**: Experiment tracking with evidence-based model selection

#### Planned Components

**Experiment Tracker**:
```yaml
Responsibilities:
  - Log ML experiments (hyperparameters, data splits, metrics)
  - Track model versions and artifacts
  - Link experiments to EvidenceGraph

Outputs:
  - Experiment Graph
  - Model registry with evidence
  - Comparison matrices
```

**Model Registry**:
```yaml
Responsibilities:
  - Register trained models (immutable)
  - Track deployment history
  - Link models to training data and code

Outputs:
  - MODEL-XXXXXX identifiers
  - Lineage chains (data → model → deployment)
```

**Evidence-Based Model Selection**:
```yaml
Responsibilities:
  - Compare models using statistical evidence
  - Generate EvidenceGraph for model comparisons
  - Provide auditable selection rationale

Outputs:
  - EvidenceGraph of model comparisons
  - Significance tests with citations
  - Recommended model with justification
```

**Key Differentiators**:
- MLflow-like tracking with EvidenceGraph integration
- Evidence-based model selection (not just metrics)
- Full reproducibility (code + data + model + provenance)
- Bridge between CoResearcher and ML workflows

**Dependencies**:
- Shared: Evidence Registry, Provenance Engine, Graph Runtime
- External: MLflow, Weights & Biases, scikit-learn, PyTorch

---

## 2. Module Comparison Matrix

| Feature | CoResearcher | GeneForge | Neurodiagnoses | PharmaOracle | EdiTXT | DataAILab |
|---------|--------------|-----------|----------------|--------------|--------|-----------|
| **Primary Graph** | EvidenceGraph, Activity Graph | EvidenceGraph | EvidenceGraph | EvidenceGraph | ReviewGraph | EvidenceGraph, Experiment Graph |
| **Evidence Registry** | ✅ | ✅ | ✅ | 🔜 | 🔜 | 🔜 |
| **Provenance Engine** | ✅ | ✅ | ✅ | 🔜 | 🔜 | 🔜 |
| **MCP Server** | ✅ | ✅ | ✅ | 🔜 | 🔜 | 🔜 |
| **Domain DSL** | ❌ | ✅ (GFL) | ❌ | 🔜 | ❌ | 🔜 |
| **Clinical Simulation** | ❌ | ❌ | ✅ | 🔜 | ❌ | ❌ |
| **Molecular Modeling** | ❌ | Partial | ❌ | 🔜 | ❌ | ❌ |
| **Review Workflows** | ❌ | ❌ | ❌ | ❌ | 🔜 | ❌ |
| **ML Experiment Tracking** | ❌ | ❌ | ❌ | ❌ | ❌ | 🔜 |
| **Status** | Production | Active Dev | Active Dev | Planning | Planning | Planning |

Legend: ✅ Implemented | 🔜 Planned | ❌ Not Applicable

---

## 3. Module Interaction Patterns

### 3.1 Evidence Sharing

```
CoResearcher builds EvidenceGraph from literature (PubMed)
    ↓
Neurodiagnoses consumes EvidenceGraph for biomarker validation
    ↓
Neurodiagnoses adds imaging evidence
    ↓
EdiTXT reviews combined evidence for publication
```

### 3.2 Provenance Chaining

```
GeneForge executes GFL workflow
    ↓
Provenance Engine records tool calls
    ↓
Evidence Registry registers genomic artifacts
    ↓
CoResearcher links genomic artifacts to published papers
    ↓
EvidenceGraph spans multiple platforms
```

### 3.3 Cross-Module Queries

```typescript
// Query: "Find all evidence for CRISPR off-target effects"
const evidence = await mcpServer.query({
  request_type: 'EVIDENCE_GRAPH',
  target: { type: 'QUESTION', id: 'QUESTION-000042' },
  scope: { depth: 5, filters: { domains: ['genomics', 'neurodegeneration'] }}
})

// Result combines:
// - CoResearcher literature evidence
// - GeneForge experimental evidence
// - Neurodiagnoses imaging evidence (if applicable)
```

---

## 4. Module Extension Points

### 4.1 Adding a New Platform

To integrate a new domain module:

```yaml
Steps:
  1. Identify domain-specific primitives (nodes, edges)
  2. Implement Evidence Registry adapter
  3. Integrate Provenance Engine
  4. Expose MCP tools for coordination
  5. Define EvidenceGraph extensions (if needed)
  6. Add to platform matrix

Example: PharmaOracle
  - Primitives: MOLECULE-XXXXXX, TARGET-XXXXXX, BINDING-XXXXXX
  - Adapter: maps docking outputs → ART-XXXXXX
  - MCP tools: search_drugs, predict_admet, dock_molecule
```

### 4.2 Extending Graph Schemas

To add new node/edge types:

```yaml
Process:
  1. Propose change to architecture review board
  2. Update evidence_graph.schema.json (add optional fields first)
  3. Update GRAPH_ECOSYSTEM.md documentation
  4. Implement in Graph Runtime
  5. Migration guide for existing graphs
  6. Version bump (minor for additions, major for breaking changes)

Example: Add EXPERIMENT-XXXXXX node for DataAILab
  - Add EXPERIMENT to node type enum
  - Define required/optional fields
  - Update validation rules
```

---

## 5. Module Governance

### 5.1 Ownership Model

```yaml
Platform Ownership:
  CoResearcher: Platform team (Fundación de Neurociencias)
  GeneForge: GeneForge team
  Neurodiagnoses: Neurodiagnoses team
  PharmaOracle: Future team (TBD)
  EdiTXT: Future team (TBD)
  DataAILab: Future team (TBD)

Shared Layer Ownership:
  Infrastructure: Platform team
  Graph Ecosystem: Architecture review board
  Shared Services: Service owners
```

### 5.2 Contribution Model

```yaml
Internal Platforms:
  - Full commit access to shared packages
  - Participate in architecture reviews
  - Responsible for domain module quality

External Platforms:
  - API access via MCP
  - Schema proposals via RFC process
  - No direct shared package access (integration via MCP)
```

---

## 6. Platform Roadmap

### Phase 1: Foundation (Current)
- ✅ CoResearcher: Production
- ✅ GeneForge: Active development
- ✅ Neurodiagnoses: Active development
- 🔜 Shared packages: Provenance, Evidence Registry, MCP Server

### Phase 2: Expansion (Next 6 months)
- 📋 PharmaOracle: Initial scaffold
- 📋 EdiTXT: ReviewGraph implementation
- 📋 DataAILab: Experiment tracking

### Phase 3: Federation (Next 12 months)
- 📋 Cross-platform graph merging
- 📋 NeuroOS Brain integration
- 📋 Company Brain for institutional knowledge

---

## 7. Strategic Context

### 7.1 The Platform Vision

The CoResearcher platform is not a single product. It is an **ecosystem of interoperable scientific applications** united by:

1. **Shared evidence model** (EvidenceGraph)
2. **Common provenance layer** (Provenance Engine)
3. **Unified integration protocol** (MCP Server)
4. **Identity federation** (ORCID/ROR)

### 7.2 Competitive Advantage

Unlike point solutions:
- **CoResearcher**: Provides traceability backbone
- **GeneForge**: Brings genomic expertise
- **Neurodiagnoses**: Brings clinical neuroscience
- **PharmaOracle**: Will bring drug discovery
- **EdiTXT**: Will bring peer review
- **DataAILab**: Will bring ML experimentation

**Together**: Form an end-to-end scientific workflow platform with auditable evidence chains from hypothesis to publication.

### 7.3 Knowledge OS Pivot

As outlined in NeuroOS Brain strategy:

```
Current: Tool coordination platform
Future: Knowledge OS (computable institutional knowledge)

Transition:
  - Agents remain (ManuEl, Antigravity)
  - Knowledge layer added (NeuroOS Brain)
  - All agents feed into Brain
  - Brain provides context to agents

Components:
  - Intent Registry
  - Decision Ledger
  - Asset Map
  - Protocol Engine
  - Relation Graph
```

The domain modules are **consumers of the Knowledge OS**, providing:
- Domain-specific evidence (EvidenceGraphs)
- Scientific workflows (actions)
- Research artifacts (publications, data, models)

---

## 8. Module Development Standards

### 8.1 Required Standards

All domain modules must:

1. **Use Shared Services**:
   - Integrate Provenance Engine
   - Register artifacts in Evidence Registry
   - Expose MCP tools for coordination

2. **Conform to Schemas**:
   - Use EvidenceGraph for evidence chains
   - Use standard node/edge types
   - Extend schemas via RFC process

3. **Maintain Provenance**:
   - Record all actions (ACTION-XXXXXX)
   - Track tool calls and data transformations
   - Provide immutable audit trails

4. **Respect Boundaries**:
   - No claim evaluation (CoResearcher's job)
   - No hypothesis generation (AI Scientists' job)
   - Focus on domain execution and evidence collection

### 8.2 Quality Gates

```yaml
Before production:
  - Integration tests with shared services
  - EvidenceGraph validation (100% pass)
  - Provenance completeness audit
  - MCP tool documentation
  - Performance benchmarks (<100ms p95 for MCP tools)

Ongoing:
  - Weekly integration tests
  - Monthly schema compliance checks
  - Quarterly architecture reviews
```

---

*This document defines the canonical domain module layer. Each module is a specialized application built on shared services, contributing domain-specific evidence to the unified Graph Ecosystem.*