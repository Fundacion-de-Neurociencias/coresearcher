# Boundary with AI Scientists
## Constitutional Directive Against Scope Expansion

**Version 1.0.0** - Boundary Definition  
**Status**: Constitutional Document - Core Governance

---

## DIRECTIVA: NO CONSTRUIR UN AI SCIENTIST

CoResearcher no:

- Genera hipótesis científicas
- Propone descubrimientos
- Diseña experimentos
- Optimiza pipelines de investigación
- Redacta contribuciones científicas originales
- Evalúa si una afirmación es correcta
- Asigna severidad o calidad científica
- Genera recomendaciones editoriales

CoResearcher audita la trazabilidad de artefactos ya existentes.

Pregunta permitida:
"¿Cómo llegamos aquí?"

Pregunta prohibida:
"¿Qué deberíamos descubrir después?"

---

## Contexto Estratégico

Existen tres tendencias distintas en el ecosistema de IA científica:

### 1. Scientific Traceability (CoResearcher)
**Función**: Reconstruir y auditar la historia científica con trazabilidad completa.

**Pregunta que responde**:
"¿Dónde está la evidencia?"

**Método**:
- Escanear repositorios, issues, PRs, commits
- Extraer ACTION-XXXXXX, CLAIM-XXXXXX, EVID-XXXXXX
- Construir provenance chains
- Generar EvidenceGraphs

**Output**: Grafo de trazabilidad, no evaluaciones de contenido.

---

### 2. Scientific Review (PAT, Google)
**Función**: Evaluar calidad de papers, reproducibilidad, metodología.

**Pregunta que responde**:
"¿Es bueno este paper?"

**Método**:
- Analizar estructura del paper
- Verificar citas
- Evaluar metodología
- Probar reproducibilidad

**Output**: Quality scores, recommendations, severity classifications.

**Frontera**: No construir en CoResearcher. Esta es la extensión natural para EditXT.

---

### 3. Scientific Discovery (AI Scientist, FutureHouse, OpenAI)
**Función**: Generar nuevas hipótesis, diseñar experimentos, proponer descubrimientos.

**Pregunta que responde**:
"¿Qué deberíamos descubrir?"

**Método**:
- Generar hipótesis via LLM
- Diseñar protocolos experimentales
- Optimizar pipelines
- Proponer nuevas líneas de investigación

**Output**: Nuevas afirmaciones científicas, experimentos propuestos.

**Frontera**: NO construir en CoResearcher. Esto destruiría la ventaja competitiva.

---

## Frontera 3: AI Scientist

### Pregunta de Frontera

¿Qué deberíamos descubrir?

### Respuesta de CoResearcher

Esa pregunta está fuera de mi alcance.

Mi alcance es:
"¿Dónde está la evidencia para lo que ya afirmamos?"

### Si se cruza la frontera

Si CoResearcher comienza a generar hipótesis, está abandonando su posición como Traceability Engine para convertirse en otro AI Scientist genérico.

**Consecuencias**:
- Pierde trazabilidad (la generación es menos trazable que la observación)
- Pierde auditabilidad (no hay provenance en generación LLM)
- Pierde ventaja competitiva (Google y FutureHouse ya hacen esto mejor)
- Pierde identidad (se convierte en commodity)

---

## Non-Negotiables (Frontera 3)

1. **No generación de hipótesis**: CoResearcher no crea CLAIM-XXXXXX sin fuente observable
2. **No diseño de experimentos**: CoResearcher no genera EXPERIMENT-XXXXXX
3. **No propuesta de descubrimientos**: CoResearcher no sugiere nuevas líneas de investigación
4. **No optimización de pipelines**: CoResearcher no diseña workflows de investigación
5. **No redacción científica**: CoResearcher no genera texto científico original
6. **No evaluación de corrección**: CoResearcher no determina si una afirmación es verdadera

---

## Validación Empírica > Arquitectura Conceptual

El riesgo actual no es conceptual.

La arquitectura está estabilizada desde Sprint 55-59C.

El riesgo es que `observable_ratio ≈ 0.27` sea una propiedad accidental observada en 3 repositorios.

**No resolverán más documentos estratégicos.**

Resolverán más datos.

---

## Implicación Práctica Inmediata

### SPRINT 59D: Corregir LlamaIndex

Objetivo:
```
repository_resolution_rate = 1.0
```

Entregable:
```
artifacts/llamaindex_retry_metrics.json
```

---

### SPRINT 59E: Benchmark con 20 Repositorios

Objetivo:
```
20 repositorios reales procesados
```

Entregables:
```
artifacts/cross_repo_20_complete.csv
artifacts/stability_metrics_20repos.json
```

Criterio:
```
>= 18 repos procesados
```

---

### SPRINT 60: EvidenceGraph v0

Input:
```
EvidenceRequest
```

Output:
```
EvidenceGraph
```

Nodos mínimos:
- Claim
- Quote
- Source
- URL
- Classification
- Confidence

Entregable:
```
artifacts/langgraph_evidence_graph.json
```

---

## Resumen de Fronteras

```
Frontera 1: EditXT
  │
  └── Pregunta: "¿Qué problemas tiene este manuscrito?"
  └── Output: ReviewGraph, Recommendations, Severity
  └── Dirección: EditXT consume EvidenceGraph de CoResearcher

Frontera 2: AI Scientists (Google, FutureHouse, OpenAI, Anthropic)
  │
  └── Pregunta: "¿Qué deberíamos descubrir?"
  └── Output: Nuevas hipótesis, experimentos, descubrimientos
  └── Dirección: No construir en CoResearcher

Frontera 1.5 (CoResearcher)
  │
  └── Pregunta: "¿Cómo llegamos aquí?"
  └── Output: EvidenceGraph, Trajectory Report, Failure Taxonomy
  └── Dirección: Auditabilidad pura, sin evaluación de contenido
```

---

*Esta directiva constitucional protege a CoResearcher de la expansión de alcance que ha eliminado durante decenas de sprints. No construir un AI Scientist no es limitación. Es la definición de la ventaja competitiva.*