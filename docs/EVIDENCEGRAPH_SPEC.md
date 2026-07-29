# EvidenceGraph Specification
**Version 1.0.0** - Core Data Contract  
**Status**: Canonical Reference

## 1. Concepto Central
El `EvidenceGraph` es un Directed Acyclic Graph (DAG) diseñado exclusivamente para proveer trazabilidad auditable de aserciones científicas. No es un Knowledge Graph general. Está estrictamente limitado a demostrar de dónde proviene una afirmación sin emitir juicios sobre su veracidad.

## 2. Tipología de Nodos

### `Claim` (Aserción)
- **Prefijo:** `CLAIM-XXXXXX`
- **Definición:** Una unidad atómica de conocimiento extraída o formulada a partir del contexto observable.
- **Atributos obligatorios:** `id`, `text`, `evidence_descriptors` (estructural, sin scoring de evaluación).

### `Artifact` (Artefacto Científico Multimodal)
- **Prefijo:** `ART-XXXXXX`
- **Definición:** Un fragmento inmutable extraído de una fuente documental primaria. Puede ser texto (quote), imagen, tabla, matriz (e.g. ChIP-seq), estructura (e.g. AlphaFold), dataset o grafo.
- **Atributos obligatorios:** `id`, `artifact_type`, `data` (contenido o referencia inmutable).

### `Source` (Fuente Primaria)
- **Prefijo:** `SOURCE-XXXXXX`
- **Definición:** El identificador del contenedor documental que alberga la cita (ej. PMID, DOI, Issue de GitHub).
- **Atributos obligatorios:** `id`, `text`.

### `URL` (Resolución)
- **Prefijo:** `URL-XXXXXX`
- **Definición:** La dirección web física y determinista donde reside la fuente.
- **Atributos obligatorios:** `id`, `text`.

## 3. Topología de Aristas (Edges)

Las aristas en el `EvidenceGraph` son estrictamente semánticas y limitadas.

1. **`supported_by`** (`Claim` → `Artifact`)
   - Significado: "Esta aserción se fundamenta en este artefacto".
2. **`derived_from`** (`Artifact` → `Source`)
   - Significado: "Este artefacto se extrajo íntegramente de este documento".
3. **`resolves_to`** (`Source` → `URL`)
   - Significado: "Este documento se localiza físicamente aquí".

## 4. Restricciones y Reglas Estructurales

1. **Aislamiento de Claims:** Un nodo `Claim` no puede tener una arista hacia otro nodo `Claim`. Si un claim deriva de otro claim, significa que se está generando nueva ciencia y se viola la directiva `BOUNDARY_WITH_AI_SCIENTISTS.md`.
2. **Ciclos Prohibidos:** El grafo debe ser 100% acíclico.
3. **Anclaje Obligatorio:** Todo nodo `Claim` debe tener al menos un path válido que lo conecte a un nodo `Source`. Un Claim huérfano (sin soporte) es una violación constitucional.
4. **Límite de Saltos (Hops):** La distancia máxima desde un `Claim` a un `Source` no debe superar los 3 hops (Típicamente 2: Claim -> Artifact -> Source).

## 5. Esquema JSON Canónico

```json
{
  "graph_id": "EG-000001",
  "request_id": "ER-000001",
  "nodes": [
    {"id": "CLAIM-001", "type": "Claim", "text": "...", "evidence_descriptors": {"source_count": 1, "support_depth": 1}},
    {"id": "ART-001", "type": "Artifact", "artifact_type": "quote", "data": "..."}
  ],
  "edges": [
    {"from": "CLAIM-001", "to": "ART-001", "type": "supported_by", "hops": 1}
  ],
  "provenance": {
    "generated_by": "CoResearcher",
    "timestamp": "2026-07-28T00:00:00Z"
  }
}
```
