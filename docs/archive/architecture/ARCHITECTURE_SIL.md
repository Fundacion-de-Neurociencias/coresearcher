# Scientific Interaction Layer Architecture
## The Next Generation Architecture

## Evolution from v1

The original architecture focused on Knowledge Objects. This architecture focuses on Scientific Interaction.

---

## Four Fundamental Layers

```
Human Language
     ↓
Scientific Semantic Compiler
     ↓
Scientific Interaction Layer (Protocol)
     ↓
Trust + Consensus Layer
     ↓
Scientific Ledger
```

---

## Core Universal Primitives

| Primitive | Universal | Identifier Pattern |
|-----------|-----------|-------------------|
| **Question** | ✅ | QUESTION-XXXXXX |
| **Observation** | ✅ | OBS-XXXXXX |
| **Measurement** | ✅ | MEAS-XXXXXX |
| **Evidence** | ✅ | EVID-XXXXXX |
| **Claim** | ✅ | CLAIM-XXXXXX |
| **Mechanism** | ✅ | MECH-XXXXXX |
| **Model** | ✅ | MODEL-XXXXXX |
| **Theory** | ✅ | THEORY-XXXXXX |
| **Researcher** | ✅ | RES-XXXXXX |

---

## Scientific Actions (SIP)

### Object Creation
- SIP_QUESTION
- SIP_OBSERVE
- SIP_PROPOSE (hypothesis)
- SIP_MECHANIZE

### Participation
- SIP_SUPPORT
- SIP_CHALLENGE
- SIP_REPLICATE
- SIP_CONFIRM
- SIP_REJECT
- SIP_FORK
- SIP_COMMENT
- SIP_REVIEW

---

## Scientific Interaction Protocol Format

```json
{
  "actor": "RES-000123",
  "action": "SIP_SUPPORT",
  "object": "CLAIM-000321",
  "provenance": ["doi:10.1038/s41591-024-xxxxx"],
  "timestamp": "2025-01-15T10:30:00Z",
  "evidence": "replicated in our lab"
}
```

---

## External Identifiers (Federation)

| Standard | Use | Connector |
|----------|-----|-----------|
| ORCID | Researcher identity | ORCID Connector |
| DOI | Paper identification | Crossref/DataCite |
| PMID | Biomedical papers | PubMed Connector |
| arXiv | Preprints | arXiv Connector |
| NCT | Clinical trials | ClinicalTrials Connector |

---

## The Asset Shift

### Before: Knowledge Graph
- Nodes: Papers, Claims, Findings
- Edges: Relationships

### After: Scientific Activity Graph
- Nodes: Claims, Mechanisms, Researchers
- Edges: SUPPORT, CHALLENGE, REPLICATE, CONFIRM, REJECT
- Scores: trust_score, consensus_score, reputation

---

## Scientific Ledger Structure

```
OBJECT_REGISTRY/
├── QUESTION/
├── OBSERVATION/
├── CLAIM/
├── MECHANISM/
├── MODEL/
├── THEORY/
└── RESEARCHER/

ACTION_REGISTRY/
├── ACTION-SUP-XXXXXX
├── ACTION-CHAL-XXXXXX
├── ACTION-REP-XXXXXX
└── ACTION-CONF-XXXXXX

TRUST_REGISTRY/
├── trust_score history
├── consensus evolution
└── reputation scores
```

---

## Public Identifiers (CSO URIs)

```
https://cso.coresearcher.org/mechanism/MECH-000114
https://cso.coresearcher.org/claim/CLAIM-000321
https://cso.coresearcher.org/researcher/RES-000123
```

---

## The Moat

The protocol is open.

The **Scientific Activity Graph** is proprietary.

Even if competitors copy the protocol:
- They don't have the action history
- They don't have accumulated trust scores
- They don't have reputation graphs

---

## Sprint 23 Roadmap

1. **Constitution** - Freeze the protocol (this document)
2. **Compiler** - Natural language → SIP
3. **Connectors** - ORCID, DOI, Crossref federation
4. **Trust Engine** - Compute scores from actions
5. **Public URIs** - endpoints for objects

---

## The Vision

ORCID identified researchers.

DOI identified papers.

CSO URI will identify:

> **Computable scientific knowledge and its evolution over time.**

For the first time, scientific knowledge will have:
- Unique identity
- Traceable history
- Verifiable reputation
- Measurable participation

This makes CoResearcher the **scientific interaction layer of the next decade**.