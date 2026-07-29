# Sprint 41 — Conceptual Research: Comprehension Model

## Objective

Define operacionalmente qué significa "comprender un proyecto científico" basado en evidencia acumulada desde Sprint 27 hasta Sprint 40.

---

## Evidence Base

### Sprint 27 — Public Observatory Validation
- Artifacts pueden ser localizados vía repositorios, DOIs, APIs
- Pero: Artifact Similarity ≠ Program Membership
- Limitación: Metadata enriquecido requiere trabajo manual

### Sprint 30 — Artifact Resolver
- Entity Resolution con DOI funciona para papers
- Pero: Artifact Similarity ≠ Program Membership
- Limitación: Los artefactos no indican relación causal entre proyectos

### Sprint 31 — Network Resolution
- Network Similarity ≠ Program Membership
- Limitación: Los enlaces no capturan relación intencional

### Sprint 39B — Scientific Activity Ledger
- Time-to-comprehension measurado para Q&A sobre MNE-Python
- Ledger acelera búsqueda de información
- Pero: Information Retrieval ≠ Comprehension
- Limitación: La comprensión sigue requiriendo más que localizar artefactos

### Sprint 40 — Decision Observatory
- Trade-offs resueltos son una unidad observable (6/11 casos)
- Otros patrones de coordinación son igualmente observables (5/11 casos):
  - Iterative Implementation Discussion
  - Technical Q&A / Knowledge Exchange
  - Bug Investigation Coordination
  - Status / Progress Update
  - Implementation Detail Negotiation

---

## Comprehension Dimensions

### 1. Qué produce el proyecto

**Componentes observables:**
- Artifacts (código, papers, datasets)
- Workstreams (roadmap implícito)
- Contributors (actores)

**Evidencia:** Alta disponibilidad en repositorios, Zenodo, APIs

**Reconstructibilidad:** HIGH

**Contribución a comprensión:** PARCIAL — conoce output pero no proceso

---

### 2. Por qué existe el proyecto

**Componentes observables:**
- Issues iniciales
- README / documentación de motivación
- Discussions iniciales

**Evidencia:** Media disponibilidad

**Reconstructibilidad:** MEDIA

**Contribución a comprensión:** MODERADA — conoce intención pero no evolución

---

### 3. Cómo funciona el proyecto

**Componentes observables:**
- Codebase estructura
- API design
- Ejemplos / tutorials
- Tests

**Evidencia:** Alta disponibilidad

**Reconstructibilidad:** HIGH

**Contribución a comprensión:** PARCIAL — conoce mecanismo pero no razonamiento

---

### 4. Por qué tomó ciertas decisiones

**Componentes observables:**
- Trade-offs resueltos (6 casos observados)
- Failures / pivots (evidencia de previos intentos)
- Reviews de código
- Discusiones críticas

**Evidencia:** Baja disponibilidad — requiere lectura de hilos

**Reconstructibilidad:** BAJA — fragmentaria

**Contribución a comprensión:** ALTA — expone razonamiento intencional

---

## Comprehension Model Schema

```
Comprehension = f(
    What: Artefactos + Workstreams + Contributors
    Why_Exist: Motivation + Intención inicial  
    How_Works: Mecanismo + API + Estructura
    Why_Decided: Trade-offs + Failures + Reviews
)
```

### Prioridad de observación (basada en Sprint 40)

1. **Trade-offs resueltos** (55% de observados) — Razonamiento explícito
2. **Knowledge exchange** (Q&A técnico) — Contexto implícito
3. **Investigation coordination** (bugs) — Contexto limitado
4. **Status updates** — Contexto mínimo
5. **Implementation negotiation** — Detalles técnicos

---

## Operational Definition

**Comprender un proyecto científico** implica poder responder:

1. **¿Qué hace?** — Artefactos + Funcionalidad
2. **¿Por qué existe?** — Motivación + Problema abordado
3. **¿Cómo funciona?** — Mecanismo + Uso
4. **¿Por qué se diseñó así?** — Trade-offs considerados + Decisiones

Esta definición es operativa porque cada dimensión puede ser verificada con evidencia observable.

---

## Sprint 40 Key Finding

Los trade-offs resueltos son una **unidad observable** pero no necesariamente la **única** contribuyente a comprensión. La coordinación científica es multiparadigma:

```
Coordination Patterns:
├── Trade-off Resolution (decisiones arquitectónicas)
├── Knowledge Exchange (Q&A, soporte técnico)
├── Bug Investigation (diagnóstico)
├── Status Synchronization (progreso)
└── Implementation Negotiation (detalles)
```

---

## Recommendation Before Next Architecture Layer

Antes de construir infraestructura adicional, CoResearcher debe:

1. **Especificar** qué componentes del modelo de comprensión serán reconstruidos
2. **Validar** que cada componente es observable y reconstructible
3. **Priorizar** según contribución a comprensión real

Sin esta especificación, cualquier nueva capa arquitectónica corre el riesgo de sobreajuste a un modelo incompleto.