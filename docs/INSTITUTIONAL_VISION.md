# Institutional Vision
## CoResearcher as Scientific Governance Layer

---

## The Core Insight

> **GitHub no es el modelo. La ciencia no necesita millones de repos. Necesita un namespace canónico.**

---

## Anti-Fragmentación Architecture

### El Problema con GitHublico

```text
100 repos sobre exactamente lo mismo
= Knowledge dispersed
= Taxonomy fights
= Lost network effects
```

### La Solución CoResearcher

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

Todo objeto científico vive dentro de un namespace canónico:

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

No existen:
```text
❌ Alzheimer Biomarkers
❌ AD Biomarkers  
❌ Blood Biomarkers AD
```

Existe uno. Y es el oficial.

---

## The Lock-in Asset

La ontología se convierte en activo estratégico no por ser difícil de construir, sino por:

```text
Cada claim queda anclado
Cada mechanism queda anclado  
Cada review queda anclado
Cada action queda anclado
Cada researcher queda anclado
```

Cuando lleguemos a:
```text
100M acciones
10M claims
1M mechanisms
```

No podrás migrar fácilmente. Porque:

- El proceso de producción está entrenado en la ontología
- La reputación está ligada a programas específicos
- El conocimiento está estructurado jerárquicamente
- Las decisiones estratégicas están registradas

---

## Research Program as Institutional Primitive

### ¿Quién puede crear programas?

Respuesta: **Prácticamente nadie.**

Requisitos:
1. Autoridad ontológica
2. Justificación científica
3. Aprobación de steward
4. Lead researcher designado

### ¿Qué es un programa?

- **NO** es un repositorio
- **NO** es un proyecto temporal
- **SÍ** es un compromiso intelectual sostenido

### ¿Cuándo se divide?

- Divergencia metodológica clara
- >100 investigadores/agents activos
- Claridad ontológica revelada

### ¿Cuándo se fusiona?

- >80% solapamiento de misión
- Evidencia convergente
- Eficiencia de recursos

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

CoResearcher no longer solo administra programas. Ahora también **publica la trazabilidad científica verificable** como objeto citable.

Eso convierte el ledger en un asset institucional, no solo técnico.

---

## The Moat Strategy

| Asset Type | Timescale | Defensibility |
|------------|-----------|---------------|
| Code/LLM | 2-5 years | None - easily copied |
| Standard | 5-10 years | Medium - requires adoption |
| **Program Registry** | **Decades** | **High - crystallized process** |

El Program Registry con 1M+ acciones será imbatible porque representa:
- Historia de producción científica verificable
- Decisiones estratégicas registradas
- Equipos híbridos que generaron conocimiento
- Preguntas que guiaron investigaciones

---

## Implementation Priority

1. **PROGRAM_CONSTITUTION** - ✅ COMPLETO
   - Definición formal de programa
   - Autoridad de creación
   - Lifecycle y transiciones
   - Políticas de multi-domain

2. **Program Registry** - ✅ IMPLEMENTADO
   - `python/ecosystem/program_registry.py`
   - Ontological anchoring enforcement
   - Duplication prevention

3. **Scientific Activities** - En diseño
   - Actions dentro de programas
   - Trust scores por programa
   - Knowledge strategies

4. **Ecosystem Extensions** - Después
   - MCP integrations
   - Semantic compiler
   - Einstein v2

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

*Esta visión institucional guía todas las decisiones arquitectónicas. Cualquier propuesta que no encaje en esta estructura debe reformularse o rechazarse.*