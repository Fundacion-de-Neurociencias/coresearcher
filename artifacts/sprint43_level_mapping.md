# Sprint 43 — Level Mapping Analysis

## Niveles observados

| Nivel | Observado / Conceptual | Evidencia del sprint |
|-------|------------------------|---------------------|
| Data | ✅ Observado | Características sin procesar (commits, issues, PRs, metadata) - Sprint 27 |
| Information | ✅ Observado | Datos con estructura (artefactos, DOIs, contributors) - Sprint 28 |
| Artifact | ✅ Observado | Unidades identificables (citas, software, datasets, papers) - Sprint 28 |
| Decision | ✅ Observado | Trade-offs resueltos con alternativas explícitas - Sprint 40 |
| Coordination | ✅ Observado | Patrones de interacción - Sprint 40B |
| Understanding | ⚠️ Hipótesis | Comprensión del propósito - Sprint 39B hipotético, NO validado |
 
---
 
## Mapeo de falsaciones a niveles
 
### Sprint 27 — GitHub Activity ≠ Scientific Activity
 
| Nivel origen | Nivel destino intentado | Resultado | Evidencia |
|--------------|------------------------|-----------|-----------|
| Data (GitHub metadata) | Scientific Activity | ❌ FALSADO | "reconstruction extracted development metadata (issues/PRs), not scientific artifacts" |
| Information (issues/PRs sin contexto) | Understanding | ❌ FALSADO | "Scientific evidence: 0" en todos los repos |
 
### Sprint 30 — Artifact Similarity ≠ Program Membership
 
| Nivel origen | Nivel destino intentado | Resultado | Evidencia |
|--------------|------------------------|-----------|-----------|
| Artifact (61 objetos con DOI) | Program | ❌ FALSADO | "All three candidate projects are large, well-funded, multi-institutional" pero programas incoherentes |
| Information (similitud) | Program | ❌ FALSADO | 57 programas distintos con mesas "spanning 0 repositories" |
 
### Sprint 31 — Network Similarity ≠ Program Membership
 
| Nivel origen | Nivel destino intentado | Resultado | Evidencia |
|--------------|------------------------|-----------|-----------|
| Network (808 nodos, 1011 edges) | Program | ❌ FALSADO | "bids-examples" asociado a papers irrelevantes ("Combinatorial Auctions") |
 
### Sprint 39B — Information Retrieval ≠ Project Comprehension
 
| Nivel origen | Nivel destino intentado | Resultado | Evidencia |
|--------------|------------------------|-----------|-----------|
| Information (ledger de 20 respuestas) | Comprehension | ❌ FALSADO | Construct validity CRITICAL: "measures time to find a string match vs time to look up a dict key" |
| Raw context (11547 caracteres) | Comprehension | ❌ FALSADO | 30% precisión vs 100% del ledger (que contiene respuestas prefabricadas) |
 
### Sprint 40 — Decisions ≠ Total Coordination
 
| Nivel origen | Nivel destino intentado | Resultado | Evidencia |
|--------------|------------------------|-----------|-----------|
| Decision (trade-offs explícitos) | Coordination | ❌ FALSADO | 5/11 casos sin decisión explícita pero con patrones observables |
 
---
 
## Scaffold conceptual de jerarquía
 
**Nota**: Esta jerarquía es un scaffold conceptual, NO un hallazgo empírico.
 
```
Data
    ↓
Information
    ↓
Artifact
    ↓
Decision
    ↓
Coordination
    ↓
Understanding
```
 
Lo único demostrado es:
 - Data → Scientific Activity falla
 - Artifact → Program falla
 - Network → Program falla
 - Information → Comprehension falla
 - Decision → Total Coordination falla
 
Eso no prueba que exista una escalera. Solo prueba que ciertas inferencias fallan.
 
---
 
## Inferencias intentadas y falsadas
 
| Inferencia intentada | Falsada | Evidencia |
| ------------------- | ------- | --------- |
| Data → Scientific Activity | ✅ Sprint 27 | Solo metadatos de desarrollo, sin evidencia científica |
| Artifact → Program | ✅ Sprint 30 y 31 | Clusters sin coherencia científica, papers irrelevantes mezclados |
| Network → Program | ✅ Sprint 31 | Patrones técnicos sin propósito científico |
| Information Retrieval → Comprehension | ✅ Sprint 39B | Mide búsqueda, no comprensión; construct validity CRITICAL |
| Decision → Total Coordination | ✅ Sprint 40 | 5/11 casos son coordinación sin decisión explícita |
 
---
 
## Implicación metodológica
 
Esta observación sugiere que el problema no es la cantidad de entidades, sino la dirección de inferencia:
 
- Sprint 27-42 buscó **inferir arriba** desde rastros inferiores
- Los resultados indican que podría requerirse **observar arriba directamente**
 
La comprensión podría ser un fenómeno observable de primer nivel, no derivable.
