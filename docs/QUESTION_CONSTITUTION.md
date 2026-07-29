# Question Constitution
## Scientific Inquiry as Institutional Primitive

**Version 1.0.0** - Foundational Inquiry Unit  
**Status**: Constitutional Document - Core Governance

---

## Article I: The Nature of a Scientific Question

### Section 1. Definition

A **Scientific Question** is a formal, persistent inquiry that guides research direction and organizes scientific activity.

It is NOT:
- ❌ A casual query ("¿Qué es...?" sin seguimiento)
- ❌ A search string (palabras clave para buscar papers)
- ❌ A subtask (paso en un workflow)
- ❌ An open-ended prompt (pregunta sin constraints)

It IS:
- ✅ A sustained intellectual commitment to unknown knowledge
- ✅ A bounded inquiry with scientific utility
- ✅ A coordination point for multiple researchers/agents
- ✅ An immutable entity once created (permanente e inmutable)

### Section 2. Canonical Identity

Every Question receives a permanent identifier within a Program context:

```
QUESTION-XXXXXX  (owned by PROGRAM-YYYYYY)
```

The question exists as a canonical entity:

```text
Science/Medicine/Neurology/Alzheimer's Disease/Biomarkers
  └── QUESTION-AD-BIOMARKERS
  └── QUESTION-AD-TAU-PATHOBIOLOGY  
  └── QUESTION-AD-PREVENTION
```

No existen:
```text
❌ Biomarkers
❌ Alzheimer Biomarkers
❌ Which biomarkers for AD
❌ AD blood markers prediction
```

Existe una. Y es la oficial.

---

## Article II: Question Authority and Creation

### Section 1. Creation Authority

**Who can create Questions?**

Multiple parties CAN create, with escalating authority levels:

| Level | Who | Approval Required |
|-------|-----|-------------------|
| **Level 1** | Any researcher (RES-XXXXXX) | Within existing PROGRAM |
| **Level 2** | Program Lead (RES) | Can refine within domain |
| **Level 3** | Ontology Curator | New QUESTION in existing PROGRAM |
| **Level 4** | Steward Council | Cross-program QUESTION boundaries |

### Section 2. Question Creation Process

```
1. QUESTION proposal with ontological path justification
2. Program lead or steward review
3. Duplicate check against existing questions
4. QUESTION-XXXXXX issued with canonical formulation
5. Question enters ACTIVE questioning state
```

### Section 3. Question Immutability

Once created, a Question is **immutable** in its canonical formulation.

Changes require:
1. **Refinement**: New QUESTION that references the original
2. **Supersession**: Original marked as "superseded by QUESTION-ZZZZZZ"
3. **Documentation**: Rationale for the evolution recorded

---

## Article III: Question Lifecycle

### Section 1. Question States

| State | Meaning | Entry Criteria |
|-------|---------|---------------|
| **Proposed** | Submitted for consideration | Within PROGRAM scope |
| **Active** | Research actively pursuing | Resources allocated |
| **Answered** | Sufficient evidence achieved | TI ≥ 80, consensus declared |
| **Superseded** | Replaced by better formulation | Explicit mapping required |
| **Dormant** | No current activity | No actions in 6+ months |

### Section 2. Question Subdivision

A Question splits when:

- **Granularity gap**: The inquiry contains ≥2 distinct unknowns
- **Methodological divergence**: Different approaches needed per sub-question
- **Ontological clarity**: Evidence reveals separate phenomena

Example split:
```
ORIGINAL: QUESTION-AD-BIOMARKERS
  ↓
SPLIT INTO:
  QUESTION-AD-BLOOD-BIOMARKERS       # Plasma, serum markers
  QUESTION-AD-CSF-BIOMARKERS         # CSF p-tau, Aβ42
  QUESTION-AD-PET-BIOMARKERS         # Amyloid, tau PET ratios
```

Split process:
1. Ontological analysis to identify distinct inquiry targets
2. PROGRAM lead decision or Steward review
3. New QUESTION-XXXXXX created with parent reference
4. Original QUESTION marked with sub-question links

### Section 3. Question Supersession

When a Question is superseded:

```
QUESTION-OLD (superseded)
  └── superseded_by: QUESTION-NEW
  └── reason: "Evidence shows narrower/more precise formulation needed"
```

The original remains queryable but inactive.

---

## Article IV: Question Granularity and Boundaries

### Section 1. Granularity Matrix

| Level | Example | Characteristic |
|-------|---------|--------------|
| **Macro** | "¿Qué factores predicen Alzheimer?" | Múltiples dominios, alta ambigüedad |
| **Meso** | "¿Cuáles son los biomarcadores sanguíneos del Alzheimer?" | Dentro de un PROGRAM, enfoque específico |
| **Micro** | "¿Puede la GFAP predecir Alzheimer precoz?" | Hipótesis con formulación precisa |
| **Nano** | "¿GFAP > 200 pg/mL predice APOE4 positivo?" | Claim testeable directamente |

Regla de oro:
- **Macro**: Usualmente demasiado amplio para convertirse en QUESTION
- **Meso**: Tamaño canónico ideal
- **Micro**: QUESTION válida si hay potencial de generalización
- **Nano**: Generalmente demasiado específica, convierte en CLAIM/HYPOTHESIS

### Section 2. Boundary Resolution

Cuando dos Questions parecen duplicadas:

1. **Ontological placement analysis** - ¿Mismo path en CSO?
2. **Investigation overlap** - ¿Evidence sets overlap >50%?
3. **Researcher consensus** - ¿Qué comunidad activa existe?
4. **Steward decision** - Merge, split, or maintain separation

---

## Article V: Relationship to Claims and Mechanisms

### Section 1. Question as Knowledge Organizer

```
QUESTION
  ├── Direct Claims (evidence addresses this question)
  ├── Indirect Claims (related knowledge)
  ├── Hypotheses (proposed explanations)
  ├── Mechanisms (causal models)
  └── Predictions (testable expectations)
```

### Section 2. Evidence Mapping

Every CLAIM that addresses the Question links to it:

```
CLAIM-XXXXXX
  └── addresses_question: QUESTION-YYYYYY
  └── evidence_strength: 0.85
  └── support_papers: [PMID-123, PMID-456]
```

Claims that CONTRADICT the Question's premise:
```
CLAIM-ZZZZZZ (contradicts)
  └── contradicts_question: QUESTION-YYYYYY
  └── implications: nullifies_key_assumption
```

---

## Article VI: Economic Unit of Scientific Work

### Section 1. Question as Resource Allocator

Research resources (time, compute, researcher attention) are allocated to Questions:

```
QUESTION-AD-BIOMARKERS
  ├── Active Researchers: 42
  ├── Active Agents: 15
  ├── Compute Hours: 12,340
  ├── Evidence Points: 247
  └── Trust Score: 78
```

### Section 2. Question Value Metrics

| Metric | Meaning |
|--------|---------|
| **Research Activity** | Acciones, claims, mecanismos generados |
| **Evidence Density** | Relación de claims por evidencia |
| **Trust Trajectory** | Evolución del trust score |
| **Researcher Engagement** | Número de investigadores activos |
| **Cross-Domain Links** | Referencias desde otros programas |

---

## Article VII: Integration with Knowledge Strategy

### Section 1. Question Visibility States

| Strategy | Question Visibility |
|----------|-------------------|
| Private | Solo miembros del PROGRAM |
| Protected | Colaboradores aprobados pueden ver |
| Published | Pública con DOI/URI canónico |
| Consensus | Pregunta considerada resuelta |

### Section 2. Strategic Evolution

Questions evolve through:

```
Private Question
  ↓
Protected Question (seeking collaboration)
  ↓
Published Question (community engagement)
  ↓
Consensus Question (actively answered)
```

Managed by PROGRAM Lead with steward oversight.

---

## Article VIII: Future Evolution

This constitution defines the question as institutional primitive. Changes require:

1. **Scientific impact assessment** - ¿Mejora la claridad o introduce ambigüedad?
2. **Ontological consistency check** - ¿Mantiene el namespace canónico?
3. **Steward council review** - ¿Implica nuevas reglas de autoridad?
4. **Community consultation (7 days)** - ¿Aceptación de la comunidad?

---

*Esta constitución establece QUESTION como la unidad económica del trabajo científico. Mientras que PROGRAM es el territorio, QUESTION es la energía que lo impulsa.*