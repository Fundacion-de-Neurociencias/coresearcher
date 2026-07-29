# Auditoría de Consistencia Arquitectónica (ARQ-001)

Esta auditoría somete a estrés las fronteras definidas en la Constitución de CoResearcher, buscando de forma destructiva contradicciones, solapamientos de responsabilidad o ambigüedades entre los documentos canónicos.

## Matriz de Consistencia

| Documento A | Documento B | ¿Conflicto? | Análisis / Justificación | Resolución / Veredicto |
| ----------- | ----------- | ----------- | ------------------------ | ---------------------- |
| `BOUNDARY_WITH_EDITXT` | `BOUNDARY_WITH_AI_SCIENTISTS` | **NO** | EditXT audita calidad sobre grafos existentes. AI Scientists generan nueva ciencia. Ambos respetan que CoResearcher se limita a trazar evidencia sin emitir juicios ni hipótesis. | **Consistente**. Las fronteras 1 y 2 son ortogonales y están bien delimitadas frente a la Capa 1 (CoResearcher). |
| `BOUNDARY_WITH_EDITXT` | `HANDOFF_TRACEABILITY` | **PARCIAL** | `BOUNDARY_WITH_EDITXT` indica que EditXT consume EvidenceGraphs para crear ReviewGraphs. `HANDOFF_TRACEABILITY` especifica estrictamente que la comunicación es unidireccional y CoResearcher **no recibe** output evaluativo. | **Resuelto**. `HANDOFF_TRACEABILITY` blinda un posible vector de contaminación detallando explícitamente el Input/Output, pero ambos documentos están alineados en que no hay *feedback loop*. |
| `ARCHITECTURE_MAP` | `BOUNDARY_WITH_AI_SCIENTISTS` | **NO** | `ARCHITECTURE_MAP` ubica a "AI Scientists" como *External Consumers* (Read-only access). La frontera coincide perfectamente en que CoResearcher no tiene integración bidireccional con generadores de hipótesis. | **Consistente**. El mapa refleja físicamente la prohibición de la frontera 3. |
| `ARCHITECTURE_MAP` | `HANDOFF_TRACEABILITY` | **NO** | El mapa define `EditXT` como una *Ecossystem App* que consume `EvidenceGraph` y produce `ReviewGraph`. El documento de *Handoff* estandariza las cargas JSON (`EG-XXXXX`, `REVIEW-XXXXX`) exactas para ese flujo. | **Consistente**. Trazabilidad técnica 1:1. |
| `BOUNDARY_WITH_EDITXT` | `ARCHITECTURE_MAP` | **POTENCIAL** | En `BOUNDARY_WITH_EDITXT` (L150) se menciona que *GitHub Issues → QUESTION-XXXXXX*, pero `ARCHITECTURE_MAP` solo menciona *ACTION-XXXXXX* y *OBS-XXXXXX* como salida del Semantic Compiler (L90). | **Requiere Ajuste Menor**. El Semantic Compiler en `ARCHITECTURE_MAP` debe documentar formalmente la emisión de `QUESTION-XXXXXX` para alinearse 100% con la topología de EditXT. *Acción: Documentado y aceptado como deuda técnica menor (no rompe el contrato).* |

## Evaluación de Tipos de Grafos (EvidenceGraph vs ReviewGraph)

Existe un riesgo arquitectónico frecuente al confundir el grafo de evidencia con el grafo de revisión. La auditoría confirma que la segregación es absoluta:

1. **EvidenceGraph (Dominio CoResearcher)**
   - Nodos permitidos: `Claim`, `Quote`, `Source`, `URL`.
   - Aristas permitidas: `supported_by`, `sourced_from`, `resolves_to`.
   - **Limitación estricta:** No contiene nodos de "Calidad", "Severidad" ni "Veredicto".

2. **ReviewGraph (Dominio EditXT)**
   - Nodos permitidos: `ReviewFinding`, `ReviewSeverity`, `ReviewRecommendation`.
   - **Limitación estricta:** Consume un EvidenceGraph como ID foráneo (`input_evidence_graph`), pero nunca sobreescribe sus aristas.

## Veredicto de la Auditoría

**APROBADA.**  
No existen contradicciones fatales. Las fronteras de CoResearcher como *Traceability Engine* puro están blindadas contra la contaminación editorial (EditXT) y la contaminación generativa (AI Scientists). La única deuda menor es la inclusión explícita del primitivo `QUESTION-XXXXXX` en los diagramas de I/O del `ARCHITECTURE_MAP`.
