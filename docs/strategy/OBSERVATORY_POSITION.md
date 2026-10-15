# Scientific Observatorio Position

## Core Differentiator

CoResearcher no es:
- Un sistema de inferencia clínica
- Un motor de toma de decisiones médicas
- An AI application for diagnosis

CoResearcher es:
- **Infraestructura de trazabilidad científica**
- **Indexación reproducible de activos científicos**
- **Cadena verificable: Asset → Observation → Evidence**

---

## Arquitectura Separada

### 1. Capa Observable (Publicable)
```text
Scientific Activity Ledger
├─ Assets (datasets, papers, code)
├─ Observations (structured facts)
├─ Evidence (provenance + strength)
└─ Provenance (timestamps, contributors, sources)
```

### 2. Capa Interpretativa (Requiere revisión)
```text
Scientific Interpretation Layer
├─ Claims (based on evidence)
├─ Patterns (cross-asset clusters)
├─ Contradictions (documented conflicts)
└─ Reviews (pending human validation)
```

---

## Decisiones validadas

| Sprint | Status |
|--------|--------|
| 27 Artifact Observation | ✅ Observable |
| 28 Artifact Resolver | ✅ Observable |
| 29-32 Program/Initiative/Workstream | ⚠️ Archivado (no observables) |
| 33-36 Ledger/Benchmark/Onboarding | ✅ Observable |
| 38 Independent Reviewer | ✅ Separado (observación vs interpretación) |
| 39 Layer Separation | ✅ Implementado |

---

## Próximo paso crítico

Publish the ledger_base.json with DOI to validate that the observable layer is indeed reproducible and versionable.
