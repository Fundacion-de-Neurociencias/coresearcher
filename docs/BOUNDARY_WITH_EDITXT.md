# Boundary with EditXT
## CoResearcher Editorial Service Contract

**Version 1.0.0** - Boundary Definition  
**Status**: Constitutional Document - Core Governance

---

## Principio Fundamental

CoResearcher no revisa manuscritos.

CoResearcher no genera recomendaciones editoriales.

CoResearcher no asigna severidad.

CoResearcher responde exclusivamente a EvidenceRequests.

---

## Arquitectura de Tres Capas

### Capa 1 (Núcleo): Traceability Engine
**Esta es CoResearcher.**

Input:
- GitHub (Issues, PRs, Commits, Releases)
- Zenodo (deposits, DOIs)
- Papers (PubMed, CrossRef, OpenAlex)
- Observaciones estructuradas

Output:
- Trajectory Report
- Evidence Graph
- Failure Taxonomy
- ACTION-XXXXXX registry
- CLAIM-XXXXXX registry
- Provenance chains

Objetivo:
Reconstruir la fracción auditablemente recuperable de la historia científica.

**Esta capa es completamente independiente de cualquier generación de texto o evaluación de contenido.**

Responsabilidad única:
Maximizar trazabilidad y auditabilidad.

Pregunta que responde:
"¿Dónde está la evidencia?"

NO responde:
"¿Es cierto?"
"¿Es bueno?"
"¿Es correcto?"

---

### Capa 2: Scientific Audit Module
**Esta es la extensión natural para EditXT.**

Evidence-Based Scientific Auditor.

Para un paper o claim:
- Observable: El paper afirma X
- Verificación estructurada:
  - ¿Existe evidencia experimental?
  - ¿Existe código?
  - ¿Existe dataset?
  - ¿Existe benchmark?
  - ¿Existe reproducibilidad?
- Resultado: Claim → Supporting Evidence → Audit Result

No genera ciencia.
Audita ciencia.

Esa diferencia es fundamental.

---

### Capa 3: PROHIBIDA para CoResearcher

❌ Evaluación de corrección de afirmaciones
❌ Revisión científica (peer review)
❌ Opiniones sobre calidad científica
❌ Clasificación de errores o severidad
❌ Recomendaciones editoriales
❌ Generación de texto evaluativo

---

## Contracto de Interfaz CoResearcher

```
Input:  EvidenceRequest
Output: EvidenceGraph
```

### EvidenceRequest

Solicitud estructurada de evidencia científica. Debe incluir:

- **target_claim**: CLAIM-XXXXXX o identificador canónico
- **evidence_scope**: Tipo de evidencia requerida (supporting, contradicting, methodological)
- **minimum_confidence**: Umbral mínimo de confianza (0.0 - 1.0)
- **provenance_required**: Booleano - si se requiere trazabilidad completa

### EvidenceGraph

Grafo de evidencia con trazabilidad completa. Debe incluir:

- **nodes**: EVID-XXXXXX, CLAIM-XXXXXX, OBS-XXXXXX vinculados
- **edges**: Relaciones de soporte/contradicción con pesos
- **provenance_trail**: Cadena completa de fuentes (DOI, PMID, ACTION-XXXXXX)
- **confidence_distribution**: Distribución de scores por nodo
- **gaps_identified**: Evidencia faltante o contradictoria

---

## Responsabilidad CoResearcher

**Maximizar trazabilidad y auditabilidad.**

Esto significa:

1. Todo nodo en EvidenceGraph tiene al menos un source verificable
2. Todo edge tiene justificación documentada
3. Todo confidence score tiene metodología explícita
4. Todo gap es reportado, no ocultado
5. Provenance se rastrea desde CLAIM/EVID hasta fuente original

---

## Non-Negotiables

1. **Sin manuscritos**: CoResearcher nunca recibe texto completo como input
2. **Sin recomendaciones editoriales**: Output es estructurado, no narrativo
3. **Sin severidad**: No hay clasificación de errores, solo trazabilidad de evidencia
4. **Sin evaluación de corrección**: CoResearcher no evalúa si una afirmación es cierta
5. **Solo EvidenceRequests**: Cualquier otro tipo de request se rechaza o se mapea a EvidenceRequest

---

## Implicaciones Arquitectónicas

EditXT y CoResearcher coexisten como aplicaciones separadas sobre el mismo núcleo:

```
Capa 1: Traceability Engine (CoResearcher)
    │
    ├── GitHub Issues      → QUESTION-XXXXXX
    ├── PRs/Commits        → ACTION-XXXXXX
    ├── Zenodo/DOIs        → EVID-XXXXXX
    └── EvidenceRequest    → EvidenceGraph

Capa 2: Scientific Audit (EditXT)
    │
    ├── EvidenceGraph      → ReviewGraph
    ├── Manuscrito         → ReviewFindings
    └── Severidad          → ReviewSeverity

Capa 3: NUEVA CIENCIA (Prohibida para CoResearcher)
    │
    └── (No aplica)
```

**Nunca se mezclan.** EditXT consume EvidenceGraphs como input para su proceso de auditoría científica, pero CoResearcher nunca recibe output editorial o evaluativo de EditXT.

---

## Sprint EDX-01 (EditXT)

Objetivo: Diseñar ReviewGraph v0 para EditXT.

Entregables:
1. docs/REVIEW_GRAPH_ARCHITECTURE.md
2. schemas/review_graph.schema.json
3. examples/alzheimer_review_graph.json

Restricciones:
- No implementar agentes
- No integrar LLMs
- No integrar PubMed
- No integrar Paperpile
- Solo modelado

Criterio de éxito:
Representar estructuradamente un hallazgo de revisión, su evidencia, su severidad y su recomendación.

Fuera de alcance:
- generación de manuscritos
- revisión automática
- peer review AI
- asistentes conversacionales

---

*Esta boundaries garantiza que CoResearcher mantenga su posición como Traceability Engine del ecosistema científico, no como servicio editorial ni como evaluador de corrección científica.*