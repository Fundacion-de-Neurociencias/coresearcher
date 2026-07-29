# Scientific Observatorio Position

## Core Differentiator

CoResearcher no es:
- Un sistema de inferencia clínica
- Un motor de toma de decisiones médicas
- Una aplicación de IA para diagnóstico

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

Publicar el ledger_base.json con DOI para validar que la capa observable es ciertamente reproducible y versionable.