# Architecture Map
## CoResearcher System Description

**Version 1.0.0** - Architecture Definition  
**Status**: Canonical Reference

---

## What is CoResearcher

CoResearcher is a **Scientific Traceability Engine**.

It is an infrastructure layer that observes, records, and reconstructs scientific activity with complete auditability. It transforms observable scientific artifacts into a structured, queryable Scientific Activity Graph.

Core value: **trazabilidad sin evaluación**. CoResearcher answers:
"¿Dónde está la evidencia?" — never "¿Es cierto?" or "¿Es bueno?".

---

## What CoResearcher is NOT

- ❌ An AI Scientist: does not generate hypotheses, experiments, or discoveries
- ❌ A peer review system: does not evaluate correctness or quality
- ❌ An editorial assistant: does not review manuscripts or assign severity
- ❌ A LIMS/ELN: not a laboratory information management system
- ❌ A chatbot: not a conversational scientific assistant
- ❌ A paper manager: not a bibliography or reference manager

---

## Internal Components

### Core Layer

| Component | Function | Output |
|-----------|----------|--------|
| Observer | Scans GitHub, Zenodo, Papers | Raw observations |
| Semantic Compiler | Translates activity to primitives | ACTION-XXXXXX, CLAIM-XXXXXX |
| Provenance Engine | Tracks execution traces | Provenance chains |
| Ledger Normalizer | Constructs Scientific Activity Graph | Trajectory Report |
| Evidence Descriptors | Computes structural metadata | source_count, contradiction_count, etc. |
| Failure Classifier | Documents extraction gaps | Failure Taxonomy |

### Registry Layer

| Registry | Pattern | Purpose |
|----------|---------|---------|
| Action Registry | ACTION-XXXXXX | Immutable record of operations |
| Claim Registry | CLAIM-XXXXXX | Asserted scientific findings |
| Evidence Registry | EVID-XXXXXX | Evidence artifacts |
| Researcher Registry | RES-XXXXXX | ORCID-federated identities |
| Institution Registry | INST-XXXXXX | ROR-federated identities |

### Integration Layer

| Integration | Direction | Content |
|-------------|-----------|---------|
| GitHub API | Inbound | Issues, PRs, Commits, Releases |
| Zenodo/DOI | Inbound | Deposits, metadata |
| PubMed/CrossRef/OpenAlex | Inbound | Papers, citations |
| MCP Server | Outbound | EvidenceRequest/EvidenceGraph API |

---

## External Components

### EditXT (Ecossystem App)

- **Boundary**: Separate application on CoResearcher core
- **Consumes**: EvidenceGraph, ACTION-XXXXXX, CLAIM-XXXXXX
- **Produces**: ReviewGraph, ReviewFinding, ReviewSeverity, ReviewRecommendation
- **Prohibited**: CoResearcher does not receive evaluative output from EditXT

### AI Scientists (External Consumers)

- **Examples**: Google DeepMind AI Scientist, FutureHouse, OpenAI Research, Anthropic Research
- **Boundary**: No integration. CoResearcher does not generate hypotheses or discoveries.
- **Consumes**: Can query EvidenceGraph for existing evidence chains
- **Produces**: New scientific claims outside CoResearcher scope

---

## Contracts Between Components

### Input/Output Contracts

```
Observer → Semantic Compiler
  Input: Raw GitHub/Zenodo/Pubmed data
  Output: OBS-XXXXXX, ACTION-XXXXXX

Semantic Compiler → Ledger Normalizer
  Input: Primitives
  Output: CLAIM-XXXXXX, EVID-XXXXXX, ACTION-XXXXXX, Failure Taxonomy

Ledger Normalizer → Evidence Descriptors
  Input: Graph Structure
  Output: Structural metrics (source_count, etc.) without evaluation

CoResearcher → EditXT
  Input: EvidenceRequest
  Output: EvidenceGraph

CoResearcher → AI Scientists
  Output: EvidenceGraph (read-only)
```

### Interface Contracts

| Contract | Direction | Protocol |
|----------|-----------|----------|
| EvidenceRequest | External → CoResearcher | Structured JSON |
| EvidenceGraph | CoResearcher → External | Structured JSON |
| ReviewGraph | EditXT external only | Structured JSON |
| MCP Tools | Agent → CoResearcher | Tool invocation |

---

## Dependencies

### Mandatory

- **GitHub API**: Primary source of observable scientific activity
- **Identifier Schemas**: ACTION-XXXXXX, CLAIM-XXXXXX, EVID-XXXXXX, RES-XXXXXX, INST-XXXXXX
- **ORCID**: Researcher identity federation (mandatory for RES-XXXXXX)
- **ROR**: Institution identity federation (mandatory for INST-XXXXXX)
- **Provenance model**: Complete execution traceability

### Optional

- **PubMed/NCBI**: Paper metadata (if available)
- **CrossRef**: DOI resolution (if available)
- **OpenAlex**: Bibliographic data (if available)
- **Zenodo**: Deposit observation (if available)
- **LangGraph**: Graph execution runtime for EvidenceGraph construction
- **Zenodo publishing**: Optional DOI for Scientific Activity Ledger

---

## System Boundaries

```
┌─────────────────────────────────────────┐
│ CoResearcher Core                        │
│                                          │
│  Observable → Primitives → Graph         │
│                                          │
│  NO evaluation                           │
│  NO generation                            │
│  NO opinion                               │
└─────────────────────────────────────────┘
          │                    │
          ▼                    ▼
┌─────────────────┐  ┌─────────────────────┐
│ EditXT           │  │ AI Scientists       │
│ Scientific Audit │  │ External Consumers  │
│ ReviewGraph      │  │ Read-only access    │
└─────────────────┘  └─────────────────────┘
```

---

*This map is the canonical description of the system. Any component, contract, or dependency not listed here is out of scope until added through a formal architecture review.*