# CoResearcher: Scientific Ecosystem Operating System

## What is CoResearcher?

**CoResearcher is the Scientific Ecosystem Operating System** - a modular platform where multiple scientific applications share a common core of knowledge, workflows and traceability.

It is not a bibliographic manager. It is not a scientific chatbot. It is not a LIMS or an ELN. It is an **operating system for AI-assisted scientific research**.

## Why does it exist?

Scientific research needs three things that generic LLMs cannot provide:

1. **Complete traceability**: Each claim, evidence and hypothesis must be able to trace its origin
2. **Structured reasoning**: Not information search, but inference about structured knowledge
3. **Shared ecosystem**: GeneForge, Medicalia, Neurodiagnoses, Vademecum, EditXT need the same core

## Primary user

**Biotech startup in preclinical phase**

Small team (2-10 researchers) you need:
- Identify emerging targets based on biomarkers
- Generate hypotheses with traced evidence
- Design experiments without reinventing the wheel
- Export proposals with full provenance

This user does not have access to Claude Enterprise or Google Co-Scientist. You need something more flexible and auditable.

## Star Workflow

```text
Pregunta científica
    ↓
Revisión literaria multi-fuente (PubMed + OpenAlex + Crossref)
    ↓
Extracción estructurada de Claims y Evidence
    ↓
Detección de knowledge gaps y contradicciones
    ↓
Hypothesis generation with quantified confidence
    ↓
Crítica automática (novedad, suficiencia, alternativas)
    ↓
Hypothesis Elo Ranking
    ↓
Validación por científicos (SUPPORTS/CHALLENGES/REPLICATES)
    ↓
Trust Score y Consensus Level
    ↓
Diseño experimental sugerido
    ↓
Propuesta de proyecto (Specific Aims + Approach)
    ↓
Paquete de provenance exportable
```

## Competitive advantage

### Option C: Scientific Ecosystem OS

Google has no ecosystem. Neither does Anthropic.

CoResearcher allows **GeneForge, Medicalia, Neurodiagnoses, Vademecum and EditXT to coexist on the same core**, sharing:
- Knowledge graph
- Provenance engine
- Model routing
- Reusable workflows

This means:
- Less code duplication
- More consistency in results
- Better maintainability
- Internal network effect

## Architecture

### Core (Shared by all applications)

```
Scientific Core
├── Claim (afirmaciones con evidenceScore, createdAt)
├── Evidence (evidencia con qualityScore, sampleSize, pValue)
├── Entity (entidad con canonicalName, aliases)
└── Provenance (trazabilidad completa)

Ecosystem Layer
├── Domain Pack Registry
├── Capability Registry
├── Dependency Engine
└── Project Container

Knowledge Network Layer
├── Claim Registry (CLAIM-000001)
├── Hypothesis Registry (HYP-000001)
├── Evidence Registry (EVID-000001)
├── Scientific Ontology (CSO) v0.1.0
├── Trust Framework (Trust Index 0-100)
├── Researcher Registry (RES-000001)
└── Consensus Engine
```

## Sprint 37: Citable Scientific Objects

CoResearcher now publishes the **Scientific Activity Ledger** as a first-class scientific object via Zenodo.

```text
Evidence
    ↓
Artifacts
    ↓
Scientific Activity Ledger
    ↓
Zenodo DOI
    ↓
Citable Scientific Object
```

This means that the scientific process itself—not just its outputs—can be:
- cited
- versioned
- audited
- mechanically reproduced

The ledger is the first CoResearcher scientific object with its own DOI.

---

## Sprint 8-11: Legitimacy Assets

### Sprint 8: Product Crystallization
- PRODUCT.md document ✅
- Defined star workflow ✅
- Main user defined ✅

### Sprint 9: Evidence Network
Creating cumulative assets with persistent IDs:
```
CLAIM-000001: "Plasma pTau217 predicts amyloid positivity..."
HYP-000001: "Tau propagation precedes measurable neurodegeneration..."
EVID-000001: "pTau217 correlates (r=0.78)"
```

### Sprint 10: Claim Trust Framework
Trust scores type PageRank:
- Support Score (30% weight)
- Contradiction Score (20% - inverse)
- Recency Score (15%)
- Reproducibility Score (20%)
- Evidence Score (10%)
- Community Score (5%)

### Sprint 11: Scientific Identity & Consensus
```
CLAIM-000001

Supported by:
  RES-000047 (UCSF)
  RES-000082 (MIT)
  RES-000123 (Oxford)

Trust Index: 94/100
Consensus Level: Moderate Consensus
```

## Roadmap: The scientific asset

The real value is not the software. It is the cumulative asset:

```
Claims registrados (CLAIM-XXXX)
Researchers validadores (RES-XXXX)
Institutions afiliadas
Trust scores calculados
Niveles de consenso
```

Goal 2029:
- 10,000,000 registered claims
- 500,000 researchers with contributions
- 20,000 affiliated institutions
- 100,000,000 validations
- CSO Ontology referenced by the scientific community

## Vision 2030

When Claude Science, Google Co-Scientist or any scientific agent asks:

> "What is the evidence for pTau217 in preclinical Alzheimer's?"

They will not look for papers. They will consult CoResearcher.

You will receive:

```json
{
  "claim": "CLAIM-003921",
  "text": "Plasma pTau217 predicts amyloid positivity in preclinical Alzheimer's disease",
  "trust_index": 97,
  "consensus_level": "Strong Consensus",
  "evidence_count": 84,
  "replications": 23,
  "contradictions": 2,
  "supporting_researchers": 147,
  "supporting_institutions": 39,
  "uri": "https://cso.coresearcher.org/claim/CLAIM-003921"
}
```

Or they will also consult the **Scientific Activity Ledger** of that research, which includes:

```json
{
  "ledger_id": "LEDGER-000042",
  "scientific_unit": "investigatable_claim",
  "unit_rationale": "validates pTau217 as preclinical biomarker",
  "doi": "10.5281/zenodo.1234567",
  "artifacts": [...],
  "workstreams": [...],
  "contributors": [...]
}
```

**That cited and referenced ID is the true asset.**

## Next Strategic Phase: Atlas + Interoperability

### Atlas Project (Focus: Validated claims, not mass extraction)

Goal: **10,000 high-quality claims in neurodegeneration**

Pipeline:
```
Paper
  ↓
Evidence (con quality score)
  ↓
Measurement (normalizado a unidades canónicas)
  ↓
Claim (backed by evidence)
  ↓
Contradictions (identificadas)
  ↓
Replications (registro)
  ↓
Consensus (Strong/Moderate/Emerging)
```

### Scientific Interoperability Network (80% effort)

The most difficult asset to copy:

```
MEAS-XXXXXX (mediciones normalizadas)
FRAME-XXXXXX (marcos canónicos)
CONV-XXXXXX (conversiones verificadas)
CONCEPT-XXXXXX (conceptos canónicos)
```

Features:
- pg/mL ↔ fg/mL
- SUVR ↔ Centiloid
- MMSE ↔ CDR
- pTau217 ↔ Phosphorylated Tau 217

### CSO v1.0 Public Release

Critical documents:
- **CSO.md** - Public Ontology
- **CSO_CONSTITUTION.md** - Formal epistemology
- Public URIs: `https://cso.coresearcher.org/`

**The asset is not the software. It is the scientific infrastructure recognized by the community.**