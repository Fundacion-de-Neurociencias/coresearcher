# InstitutionalVision
## CoResearcher as Scientific Governance Layer

---

##The Core Insight

> **GitHub is not the model. Science doesn't need millions of repos. You need a canonical namespace.**

---

## Anti-Fragmentation Architecture

### The Problem with GitHublico

```text
100 repos sobre exactamente lo mismo
= Knowledge dispersed
= Taxonomy fights
= Lost network effects
```

### The CoResearcher Solution

```text
1 pregunta
1 lugar  
1 historial
1 grafo
= Knowledge unified
= Ontology crystallized
= Network effects compound
```

---

## Canonical Scientific Namespace

Every scientific object lives within a canonical namespace:

```text
Science
├── Medicine
│   ├── Neurology
│   │   ├── Neurodegenerative Diseases
│   │   │   ├── Alzheimer's Disease
│   │   │   │   ├── PROGRAM-000421 (Biomarkers)
│   │   │   │   ├── PROGRAM-000422 (Tau Pathology)
│   │   │   │   ├── PROGRAM-000423 (Therapeutics)
│   │   │   │   └── PROGRAM-000424 (Prevention)
│   │   │   ├── Parkinson Disease
│   │   │   │   └── PROGRAM-000425
│   │   │   └── ALS
│   │   │       └── PROGRAM-000426
```

They do not exist:
```text
❌ Alzheimer Biomarkers
❌ AD Biomarkers  
❌ Blood Biomarkers AD
```

There is one. And it's the official one.

---

##The Lock-in Asset

The ontology becomes a strategic asset not because it is difficult to build, but because:

```text
Cada claim queda anclado
Cada mechanism queda anclado  
Cada review queda anclado
Cada action queda anclado
Cada researcher queda anclado
```

When we get to:
```text
100M acciones
10M claims
1M mechanisms
```

You will not be able to migrate easily. Because:

- The production process is trained in the ontology
- Reputation is tied to specific programs
- Knowledge is hierarchically structured
- Strategic decisions are recorded

---

## Research Program as Institutional Primitive

### Who can create programs?

Answer: **Practically no one.**

Requirements:
1. Ontological authority
2. Scientific justification
3. Steward approval
4. Designated Lead researcher

### What is a program?

- **NOT** it is a repository
- **NOT** it is a temporary project
- **YES** it is a sustained intellectual commitment

### When is it divided?

- Clear methodological divergence
- >100 active investigators/agents
- Ontological clarity revealed

### When is it merged?

- >80% mission overlap
- Converging evidence
- Resource efficiency

---

## From Product to Institution

### Sprint 1-22: Knowledge Infrastructure
```text
Paper → Claim → Graph
```

### Sprint 23+: Institutional Infrastructure
```text
Question → Program → Activity → Consensus
```

### Sprint 37: Citable Scientific Objects
```text
Evidence
    ↓
Scientific Activity Ledger
    ↓
Zenodo DOI
    ↓
Persistent Citable Object
```

CoResearcher no longer only manages programs. It now also **publishes verifiable scientific traceability** as a citable object.

That turns the ledger into an institutional asset, not just a technical one.

---

## The Moat Strategy

| Asset Type | Timescale | Defensibility |
|---------|-----------|---------------|
| Code/LLM | 2-5 years | None - easily copied |
| Standard | 5-10 years | Medium - requires adoption |
| **Program Registry** | **Decades** | **High - crystallized process** |

The Program Registry with 1M+ actions will be unbeatable because it represents:
- History of verifiable scientific production
- Recorded strategic decisions
- Hybrid teams that generated knowledge
- Questions that guided investigations

---

## Implementation Priority

1. **PROGRAM_CONSTITUTION** - ✅ COMPLETE
   - Formal program definition
   - Creation authority
   - Lifecycle and transitions
   - Multi-domain policies

2. **Program Registry** - ✅ IMPLEMENTED
   -`python/ecosystem/program_registry.py`
   - Ontological anchoring enforcement
   - Duplication prevention

3. **Scientific Activities** - In design
   - Actions within programs
   - Trust scores by program
   - Knowledge strategies

4. **Ecosystem Extensions** - After
   - MCP integrations
   - Semantic compiler
   -Einstein v2

---

## The Canonical Structure

```text
CoResearcher
│
├── Ontology (CSO)              ← Ancla todo
│
├── Programs                    ← Unidad organizativa
│   └── PROGRAM-XXXXXX
│       ├── Lead: RES-XXXXXX
│       ├── Team: [RES, AGENT...]
│       ├── Mission: QUESTION-XXXXXX
│       ├── Activity: [ACTION...]
│       └── Knowledge: [CLAIM...]
│
├── Ledgers                     ← Trazabilidad citable
│   └── LEDGER-XXXXXX → DOI
│       ├── scientific_unit
│       ├── unit_rationale
│       ├── Artifacts
│       ├── Workstreams
│       └── Contributors
│
├── Questions                  ← Norte estratégico
│   └── QUESTION-XXXXXX → PROGRAM-XXXXXX
│
├── Claims                     ← Producción verificable
│   └── CLAIM-XXXXXX → PROGRAM-XXXXXX
│
├── Mechanisms                 ← Explicaciones causales
│   └── MECH-XXXXXX → PROGRAM-XXXXXX
│
├── Actions                    ← Evidencia de actividad
│   └── ACTION-XXXXXX → PROGRAM-XXXXXX
│
└── Reviews                    ← Validación externa
    └── REVIEW-XXXXXX → PROGRAM-XXXXXX
```

---

*This institutional vision guides all architectural decisions. Any proposal that does not fit into this structure must be reformulated or rejected.*