# Ontology Constitution
## Taxonomic Authority and Scientific Classification Governance

**Version 1.0.0** - Foundational Classification System  
**Status**: Constitutional Document - Core Governance

---

## Article I: The Nature of Scientific Ontology

### Section 1. Definition

**Ontology** is the formal system of scientific classification that anchors all knowledge artifacts.

It is NOT:
- ❌ A tag system (folksonomy)
- ❌ A search index (keywords)
- ❌ A taxonomy of convenience (categorización informal)
- ❌ A static classification (árbol fijo e inmutable)

It IS:
- ✅ A governed scientific coordinate system
- ✅ A negotiated consensus on knowledge placement
- ✅ A multi-dimensional classification spectrum
- ✅ An actively maintained living structure

### Section 2. Constitutional Rule for Programs

**No se permite la creación libre de PROGRAMS.**

Todo PROGRAM debe estar anclado a un ONTOLOGY NODE existente.

```text
Science
├── Medicine
│   ├── Neurology
│   │   ├── Alzheimer Disease
│   │   │   ├── Biomarkers        ← NODE OFICIAL
│   │   │   ├── Early Diagnosis
│   │   │   ├── Therapeutics
│   │   │   └── Prevention
```

Cuando el nodo existe:
```
Dr. X solicita stewardship de "Biomarkers"
↓
Se crea PROGRAM-AD-BIOMARKERS
Steward: ORCID-XXXX
```

Cuando el nodo NO existe:
```
Dr. X propone investigación nueva
↓
Se crea INCUBATION-000123
↓
Si alcanza umbral: se incorpora a ONTOLOGY
↓
Se crea PROGRAM-XXXXXX
```

### Section 3. Ontological Multi-Membership

**Scientific entities can belong to multiple domains simultaneously.**

Example:
```
Alzheimer's Disease
```

Can belong to:
- Science/Medicine/Neurology
- Science/Medicine/Neurodegenerative Diseases
- Science/Life Sciences/Neuroscience
- Science/Aging Biology
- Science/Precision Medicine

This is not a bug. This is a **feature**.

---

## Article II: Incubation Nodes (Scientific Exploration)

### Section 1. Incubation Purpose

La ciencia no solo avanza dentro de categorías conocidas. A veces crea categorías nuevas.

Los **INCUBATION NODES** permiten exploración sin romper el namespace canónico.

```
INCUBATION-000123
├── Topic: "GFAP in tau propagation"
├── Principal: Dr. X (RES-000456)
├── Status: EXPERIMENTAL
└── Evidence threshold for promotion: 25 claims + 3 reviewers + 100 citations
```

### Section 2. Incubation Lifecycle

| State | Criteria | Path |
|-------|----------|------|
| **Proposed** | Researcher proposal | INCUBATION-XXXXXX |
| **Active** | Resources allocated | Can generate claims/actions |
| **Validating** | Threshold reached | Under review for promotion |
| **Promoted** | Accepted to ONTOLOGY | Becomes OFFICIAL NODE |
| **Archived** | Insufficient evidence | Preserved, no promotion |

### Section 3. Promotion Criteria

Para pasar de INCUBATION a ONTOLOGY OFICIAL:
- **Claims generadas**: ≥25 claims con TI ≥ 50
- **Research activity**: ≥15 researchers/agents activos
- **External validation**: ≥3 independent reviews
- **Community interest**: ≥100 cross-references/citations
- **Ontology fit**: Clear placement in CSO hierarchy

```
INCUBATION-000123 (Tau propagation biomarkers)
  ↓ alcanza umbral
OFFICIAL NODE: Science/Medicine/Neurology/Alzheimer's Disease/Tau Propagation Biomarkers
  ↓
PROGRAM-000427 can be created
```

---

## Article III: Ontological Authority

### Section 1. Curator Levels

| Level | Role | Authority |
|-------|------|-----------|
| **Level 1: Domain Stewards** | RES-XXXXXX with domain expertise | Create/move within domain |
| **Level 2: Ontology Curators** | Specialists in classification | Cross-domain placement |
| **Level 3: Steward Council** | Multi-domain experts | Root/structural decisions |
| **Level 4: Ontology Council** | Community-elected | Constitution-scale changes |

### Section 2. Classification Process

When placing a new entity:

```
1. Proposal with justification (scientific necessity)
2. Domain steward review (placement options)
3. Multi-membership analysis (2-5 possible locations)
4. Community consultation (21 days)
5. Curator decision with rationale
6. Permanent placement + redirect mappings
```

### Section 3. Classification Disputes

When scientists disagree on placement:

```
Conflict Resolution:
Alzheimer ∈ Neurology?  YES, Primary
Alzheimer ∈ Aging?      YES, Secondary  
Alzheimer ∈ Precision Medicine? YES, Secondary

NOT a winner-take-all.
NOT elimination of alternatives.
YES to multi-membership with primary designation.
```

---

## Article IV: Taxonomy Evolution

### Section 1. Evolution Events

Ontology changes through:

| Event Type | Trigger | Process |
|------------|---------|---------|
| **Refinement** | New evidence reveals substructure | Add child nodes |
| **Merge** | Two nodes revealed as same phenomenon | Create synonym mapping |
| **Split** | One node covers multiple phenomena | Divide with history |
| **Rescope** | Boundary shifts due to science | Renegotiate placement |

### Section 2. History Preservation

All changes create **redirect mappings**:

```
OLD: Science/Medicine/Neurodegeneration/Alzheimer
NEW: Science/Medicine/Neurology/Neurodegenerative Diseases/Alzheimer

Redirect: /neurodegeneration/alzheimer → /neurology/neurodegenerative-diseases/alzheimer
Status: MOVED (2026-07-13)
Reason: MeSH alignment
```

---

## Article V: Conflict Prevention Mechanisms

### Section 1. The Canonical Rule

> **There is only one canonical URI for each scientific entity.**

```
CORRECT: https://cso.coresearcher.org/alzheimer
WRONG:   https://cso.coresearcher.org/ad
WRONG:   https://cso.coresearcher.org/alzheimers-disease
WRONG:   https://cso.coresearcher.org/mild-cognitive-impairment-alzheimer
```

### Section 2. Disambiguation Protocol

When similar names cause confusion:

1. **Ontological context** - Which path does it belong to?
2. **Evidence precedence** - Which has stronger claims?
3. **Community usage** - Which do researchers actually use?
4. **Curator decision** - Final placement with documentation

---

## Article VI: Integration with Scientific Objects

### Section 1. Mandatory Anchoring

Every scientific object MUST declare ontological placement:

```json
{
  "claim_id": "CLAIM-000123",
  "ontological_path": "Science/Medicine/Neurology/Alzheimer's Disease/Biomarkers",
  "secondary_paths": [
    "Science/Life Sciences/Genomics/APOE4",
    "Science/Methods/Statistics/Biomarker Validation"
  ],
  "primary_domain": "Neurology",
  "canonical_uri": "https://cso.coresearcher.org/claim/CLAIM-000123"
}
```

### Section 2. Multi-Domain Resolution

For queries spanning domains:

```
Query: "APOE4 and aging biomarkers"

Resolution:
- Neurology domain: 47 claims
- Aging domain: 23 claims  
- Genomics domain: 12 claims

Present all. Cross-reference relationships.
Let researcher decide primary context.
```

---

## Article VII: External Ontology Alignment

### Section 1. Required Mappings

Every CSO node must map to at least one external standard:

| External System | Mapping Requirement |
|-----------------|---------------------|
| MeSH (PubMed) | Required for medical terms |
| HGNC | Required for genes/proteins |
| ChEBI | Required for chemicals |
| NCIT | Required for diseases |
| OBI | Required for methods/instruments |

### Section 2. Mapping Authority

Mappings are:

- **Provisional**: Initial alignment (Level 1 steward)
- **Confirmed**: Cross-validated (Level 2 curator)
- **Canonical**: Accepted community standard (Level 3 council)
- **Superseded**: Replaced by better mapping (documented)

---

## Article VIII: The Ontology as Moat

### Section 1. Why Ontology is Defensible

After 100K+ mappings accumulated:

```
Claim → Ontology path → Program → Question → Action → Review

Cannot migrate claim without:
- Re-establishing ontological justification
- Re-validating all cross-mappings
- Re-building all program relationships
- Re-generating all question linkages
- Re-verifying all action provenance
- Re-confirming all review contexts
```

This creates **computational lock-in**.

### Section 2. Competitive Barriers

| Competitor | Problem |
|-----------|---------|
| Basic search | No ontological anchoring |
| Tag systems | No governance authority |
| Simple graphs | No multi-membership semantics |
| AI assistants | No redirect/curation history |

---

*Esta constitución establece la ontología como sistema de coordenadas universal. Donde la ciencia se clasifica, se descubre, y se gobierna.*