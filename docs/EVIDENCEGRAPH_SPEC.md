# EvidenceGraph Specification
**Version 1.1.0** - Core Data Contract  
**Status**: Canonical Reference  
**Extended**: SPRINT 60B - Decision Trajectory Tracking

---

## 1. Concepto Central

El `EvidenceGraph` es un Directed Acyclic Graph (DAG) diseñado exclusivamente para proveer trazabilidad auditable de aserciones científicas y trayectorias de decisión. No es un Knowledge Graph general. Está estrictamente limitado a demostrar de dónde proviene una afirmación y por qué se eligió un camino sobre otro.

---

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

### `Decision` (Nodo de Decisión) ⭐ **NUEVO v1.1.0**
- **Prefijo:** `DECISION-XXXXXX`
- **Definición:** Un punto de elección en la trayectoria de investigación. Representa una decisión tomada por un agente o humano, con su justificación, evidencia de apoyo, y resultado.
- **Atributos obligatorios:** `id`, `decision`, `actor`, `timestamp`
- **Atributos opcionales:** `rationale`, `outcome`, `confidence`
- **Campos de decisión:**
  - `decision`: Texto describiendo la decisión
  - `actor`: Agente o humano que tomó la decisión
  - `timestamp`: Cuándo se tomó
  - `rationale`: Por qué se tomó
  - `outcome`: Resultado (success, failure, abandoned, superseded)
  - `confidence`: Confianza en el momento de la decisión

**Ejemplo:**
```json
{
  "id": "DECISION-000001",
  "type": "Decision",
  "decision": "Use Dataset A for training",
  "actor": "Antigravity",
  "timestamp": "2026-07-30T10:00:00Z",
  "rationale": "Faster experiments, sufficient sample size",
  "outcome": "success",
  "confidence": 0.8
}
```

---

## 3. Topología de Aristas (Edges)

Las aristas en el `EvidenceGraph` son estrictamente semánticas y limitadas.

### 3.1 Aristas de Evidencia (Originales)

1. **`supported_by`** (`Claim` → `Artifact`)
   - Significado: "Esta aserción se fundamenta en este artefacto".

2. **`derived_from`** (`Artifact` → `Source`)
   - Significado: "Este artefacto se extrajo íntegramente de este documento".

3. **`resolves_to`** (`Source` → `URL`)
   - Significado: "Este documento se localiza físicamente aquí".

### 3.2 Aristas de Decisión ⭐ **NUEVO v1.1.0**

4. **`chosen_over`** (`Decision` → `Decision`)
   - Significado: "Esta decisión fue elegida en lugar de otra alternativa"
   - Dirección: De la decisión ganadora a la decisión descartada
   - Peso: 0.7 (incertidumbre en laalternativa)

5. **`led_to`** (`Decision` → `Claim` | `Artifact`)
   - Significado: "Esta decisión condujo directamente a esta aserción/artefacto"
   - Dirección: De la decisión a su consecuencia
   - Peso: 0.9

6. **`abandoned_for`** (`Decision` → `Decision`)
   - Significado: "Esta línea de investigación fue abandonada en favor de otra"
   - Dirección: De la decisión abandonada a la decisión que la reemplazó
   - Peso: 0.6

7. **`superseded_by`** (`Decision` → `Decision`)
   - Significado: "Esta decisión fue reemplazada por una versión mejorada"
   - Dirección: De la decisión antigua a la nueva
   - Peso: 0.8

**Ejemplo de trayectoria:**
```
DECISION-000001 (Use Dataset A)
    ↓ led_to
CLAIM-000001 (Model trained on Dataset A shows 95% accuracy)
    ↓ supported_by
ART-000001 (Training results)
    ↓ derived_from
SOURCE-000001 (Experiment log)
    ↓ resolves_to
URL-000001 (https://github.com/repo/experiments/1)

DECISION-000002 (Try Dataset B)
    ↓ abandoned_for
DECISION-000001 (Use Dataset A)
    ↓ chosen_over
DECISION-000002 (Try Dataset B)
```

---

## 4. Restricciones y Reglas Estructurales

### 4.1 Restricciones Originales

1. **Aislamiento de Claims:** Un nodo `Claim` no puede tener una arista hacia otro nodo `Claim`.
2. **Ciclos Prohibidos:** El grafo debe ser 100% acíclico.
3. **Anclaje Obligatorio:** Todo nodo `Claim` debe tener al menos un path válido que lo conecte a un nodo `Source`.
4. **Límite de Saltos (Hops):** La distancia máxima desde un `Claim` a un `Source` no debe superar los 3 hops.

### 4.2 Nuevas Restricciones para Decisiones ⭐ **NUEVO v1.1.0**

5. **Decision Aislamiento:** Un nodo `Decision` NO puede tener arista `supported_by` hacia un `Claim`. Las decisiones se apoyan en evidencia (Artifacts), no en aserciones.
   - ✅ Válido: `Decision → Artifact` (led_to)
   - ❌ Inválido: `Decision → Claim` (supported_by)

6. **Decision Cycles:** Se permiten ciclos solo entre nodos `Decision` cuando el edge es `abandoned_for` o `superseded_by` en dirección opuesta.
   - ✅ Válido: `DECISION-A → abandoned_for → DECISION-B` y `DECISION-B → chosen_over → DECISION-A`
   - ❌ Inválido: Ciclos en edges de evidencia

7. **Decision Anchoring:** Toda decisión debe tener al menos uno de:
   - Un `Artifact` de evidencia que la soporte (via `led_to` en reversa)
   - Un `rationale` documentado
   - Una referencia a `authorized_by` en metadatos

8. **Outcome Tracking:** Si una decisión tiene `outcome: abandoned` o `outcome: failure`, debe tener al menos una conexión a otra decisión (`abandoned_for` o `superseded_by`).

### 4.3 Principio de Decision Traceability ⭐ **NUEVO v1.1.0 - CONSTITUCIONAL**

> **Todo DecisionNode debe ser Observable o Derivable. Nunca Inferido.**

Este principio es constitucional y no puede ser violado. Su propósito es evitar que CoResearcher se convierta en un motor de interpretación psicológica.

**Regla fundamental:**
- ✅ **Observable**: "El equipo cerró el issue #142 sin merge" (evidencia directa)
- ✅ **Derivable**: "El equipo descartó PR #142 después del benchmark X" (evidencia + razonamiento)
- ❌ **Inferido**: "El equipo creía que..." (interpretación, no evidencia)

**Implementación:**
```typescript
interface DecisionNode {
  // Campos obligatorios (observables)
  decision: string              // Derivado de: issue title, PR title, commit message
  actor: string                 // Derivado de: GitHub username, commit author
  timestamp: Date               // Observable: issue created_at, PR created_at, commit date
  
  // Campos condicionales (derivables)
  rationale?: string            // DERIVADO de: issue body, PR description, commit body
                                  // Marcar como "inferred" si no hay declaración explícita
  
  outcome: DecisionOutcome      // Derivado de: issue state, PR state, release tags
  
  confidence: number            // confidence: 1.0 para explícito, 0.7-0.9 para implícito
}
```

**Validación:**
```typescript
interface DecisionValidation {
  isObservableOrDerivable: boolean  // true si todos los campos son observable/derivable
  
  classification: {
    decision: 'observable' | 'derivable'
    actor: 'observable'
    timestamp: 'observable'
    rationale?: 'observable' | 'derivable' | 'inferred'
    outcome: 'derivable'
  }
  
  violations: string[]  // Debe estar vacío
}
```

**Ejemplos válidos:**
```json
{
  "id": "DECISION-000001",
  "type": "Decision",
  "decision": "Close issue #142: Switch to pydantic v2",
  "actor": "hinthakka",
  "timestamp": "2026-05-15T10:30:00Z",
  "outcome": "abandoned",
  "confidence": 0.85
}
```

**Ejemplos inválidos:**
```json
{
  "id": "DECISION-000002",
  "type": "Decision",
  "decision": "The team believed pydantic v2 was too complex",
  "actor": "Unknown",
  "timestamp": "2026-05-15T10:30:00Z",
  "outcome": "abandoned",
  "confidence": 0.6
}
// VIOLACIÓN: "creía" es interpretación psicológica (inferido)
```

**Consecuencias arquitectónicas:**
1. DecisionNode NO puede contener campos como `belief`, `opinion`, `thought`, `assumption`
2. Rationale debe ser siempre rastreable a un artifact (issue, PR, commit)
3. Confidence debe reflejar evidencia disponible, no certeza subjetiva
4. El sistema debe marcar como `inferred` cualquier campo que no sea directamente observable

**Relación con otros principios:**
- Complementa: **Aislamiento de Claims** (no evaluar aserciones)
- Complementa: **No Evaluación** (CoResearcher no juzga decisiones, solo las registra)
- Refuerza: **Trazabilidad sin Juicio** (el "por qué" es evidencia, no interpretación)

---

## 5. Esquema JSON Canónico

### 5.1 Grafo de Evidencia (Original)
```json
{
  "graph_id": "EG-000001",
  "request_id": "ER-000001",
  "nodes": [
    {"id": "CLAIM-001", "type": "Claim", "text": "...", "evidence_descriptors": {"source_count": 1, "support_depth": 1}},
    {"id": "ART-001", "type": "Artifact", "artifact_type": "quote", "data": "..."},
    {"id": "SOURCE-001", "type": "Source", "text": "..."},
    {"id": "URL-001", "type": "URL", "text": "https://..."}
  ],
  "edges": [
    {"from": "CLAIM-001", "to": "ART-001", "type": "supported_by", "hops": 1},
    {"from": "ART-001", "to": "SOURCE-001", "type": "derived_from", "hops": 1},
    {"from": "SOURCE-001", "to": "URL-001", "type": "resolves_to", "hops": 1}
  ],
  "provenance": {
    "generated_by": "CoResearcher",
    "timestamp": "2026-07-28T00:00:00Z"
  }
}
```

### 5.2 Grafo de Trayectoria de Decisión ⭐ **NUEVO v1.1.0**
```json
{
  "graph_id": "EG-000002",
  "request_id": "ER-000002",
  "nodes": [
    {
      "id": "DECISION-001",
      "type": "Decision",
      "decision": "Use Dataset A",
      "actor": "Antigravity",
      "timestamp": "2026-07-30T10:00:00Z",
      "rationale": "Faster experiments",
      "outcome": "success",
      "confidence": 0.8
    },
    {
      "id": "ART-002",
      "type": "Artifact",
      "artifact_type": "dataset",
      "data": "dataset_a_v1.csv"
    },
    {
      "id": "CLAIM-001",
      "type": "Claim",
      "text": "Model achieves 95% accuracy",
      "evidence_descriptors": {"source_count": 1, "support_depth": 1}
    },
    {
      "id": "DECISION-002",
      "type": "Decision",
      "decision": "Try Dataset B",
      "actor": "Antigravity",
      "timestamp": "2026-07-30T09:00:00Z",
      "outcome": "abandoned",
      "confidence": 0.5
    }
  ],
  "edges": [
    {
      "from": "DECISION-001",
      "to": "ART-002",
      "type": "led_to",
      "weight": 0.9
    },
    {
      "from": "ART-002",
      "to": "CLAIM-001",
      "type": "supported_by",
      "weight": 0.9
    },
    {
      "from": "DECISION-002",
      "to": "DECISION-001",
      "type": "abandoned_for",
      "weight": 0.6
    },
    {
      "from": "DECISION-001",
      "to": "DECISION-002",
      "type": "chosen_over",
      "weight": 0.7
    }
  ],
  "provenance": {
    "generated_by": "CoResearcher",
    "timestamp": "2026-07-30T12:00:00Z",
    "corpus_version": "sprint60b"
  }
}
```

---

## 6. Trajectory Reconstruction Pattern

### 6.1 Caso de Uso: Hipótesis Descartada

**Objetivo:** Reconstruir la trayectoria completa de una hipótesis que fue abandonada.

**Entrada:** `DECISION-000042` (abandoned)

**Proceso:**
1. Buscar todas las aristas `abandoned_for` desde esta decisión
2. Buscar todas las aristas `chosen_over` hacia esta decisión
3. Reconstruir la secuencia: `DECISION-A → abandoned_for → DECISION-B → chosen_over → DECISION-A`
4. Adjuntar evidencia: artifacts, claims, outcomes

**Salida:** Subgrafo centrado en la decisión abandonada con todo su contexto.

### 6.2 Caso de Uso: Path de Éxito

**Objetivo:** Identificar qué decisiones llevaron a un resultado exitoso.

**Entrada:** `DECISION-000045` (outcome: success)

**Proceso:**
1. Retroceder por aristas `superseded_by` y `chosen_over`
2. Reconstruir árbol de alternativas consideradas
3. Identificar puntos de divergencia clave

**Salida:** Árbol de decisión con rutas exitosas y fallidas.

### 6.3 Métricas de Trayectoria

```typescript
interface TrajectoryMetrics {
  decision_count: number
  abandoned_count: number
  success_rate: number
  avg_decision_depth: number  // Average path length from root decision
  evidence_strength: number   // Average confidence of supporting artifacts
  backtracking_frequency: number // How often decisions were abandoned
}
```

---

## 7. Integración con Decision Registry

### 7.1 Mapping

```
Decision Registry (decision_execution.schema.json)
    ↓
EvidenceGraph (evidence_graph.schema.json)

DECISION-XXXXXX (Decision Registry)
    → maps to DECISION-XXXXXX (EvidenceGraph node)

Execution record
    → maps to ART-XXXXXX (Artifact node, type: execution_log)

Policy compliance
    → maps to ART-XXXXXX (Artifact node, type: test_result)

Evidence references
    → maps to SOURCE-XXXXXX and URL-XXXXXX
```

### 7.2 Bidirectional Linking

```typescript
// From Decision Registry to EvidenceGraph
const decision = await decisionRegistry.get('D-2026-0045')
const graph = await evidenceGraphBuilder.buildFromDecision(decision.id)
// graph.nodes includes: DECISION-000001, ART-000042, CLAIM-000023

// From EvidenceGraph to Decision Registry
const graph = await evidenceGraphRepository.get('EG-000001')
const decisionNodes = graph.nodes.filter(n => n.type === 'Decision')
for (const node of decisionNodes) {
  const decision = await decisionRegistry.get(node.id)
  // Full decision record with execution details
}
```

---

## 8. Validación Extendida

### 8.1 Phase 4: Decision Validation ⭐ **NUEVO v1.1.0**

```typescript
interface DecisionValidation {
  // Decision anchoring
  allDecisionsAnchored: boolean
  decisionsWithRationale: number
  decisionsWithOutcome: number
  
  // Decision graph properties
  decisionCycleCount: number // Should be 0 for evidence edges, allowed for decision cycles
  orphanedDecisions: string[]
  
  // Trajectory quality
  abandonedDecisionsLinked: boolean
  supersededDecisionsLinked: boolean
  outcomeDistribution: {
    success: number
    failure: number
    abandoned: number
    superseded: number
  }
}
```

### 8.2 Validación Tool

```bash
# Validate including decision nodes
npx @coresearcher/cli validate-graph --include-decisions evidence_graph.json

# Trajectory reconstruction
npx @coresearcher/cli reconstruct-trajectory DECISION-000001

# Decision path analysis
npx @coresearcher/cli analyze-decisions --outcome=success
```

---

## 9. Ejemplos de Uso

### 9.1 Ejemplo: Reconstruir Trayectoria de Hipótesis Descartada

```json
{
  "graph_id": "EG-000003",
  "request_id": "ER-000003",
  "nodes": [
    {
      "id": "DECISION-000010",
      "type": "Decision",
      "decision": "Test hypothesis: Amyloid-beta causes Alzheimer's",
      "actor": "Neurodiagnoses",
      "timestamp": "2026-06-01T00:00:00Z",
      "outcome": "abandoned",
      "rationale": "Insufficient evidence, conflicting results"
    },
    {
      "id": "ART-000010",
      "type": "Artifact",
      "artifact_type": "dataset",
      "data": "amyloid_study_2026.csv",
      "classification": "observable"
    },
    {
      "id": "CLAIM-000010",
      "type": "Claim",
      "text": "Amyloid-beta levels do not correlate with cognitive decline in this cohort",
      "classification": "derivable"
    },
    {
      "id": "DECISION-000011",
      "type": "Decision",
      "decision": "Switch to tau protein hypothesis",
      "actor": "Neurodiagnoses",
      "timestamp": "2026-06-15T00:00:00Z",
      "outcome": "success",
      "rationale": "Stronger evidence from recent literature"
    }
  ],
  "edges": [
    {
      "from": "DECISION-000010",
      "to": "ART-000010",
      "type": "led_to",
      "weight": 0.9
    },
    {
      "from": "ART-000010",
      "to": "CLAIM-000010",
      "type": "supported_by",
      "weight": 0.85
    },
    {
      "from": "DECISION-000010",
      "to": "DECISION-000011",
      "type": "abandoned_for",
      "weight": 0.7
    },
    {
      "from": "DECISION-000011",
      "to": "DECISION-000010",
      "type": "chosen_over",
      "weight": 0.6
    }
  ]
}
```

---

## 10. Preguntas de Investigación Sostenidas

Este grafo permite responder preguntas nuevas:

1. **¿Por qué se abandonó esta línea de investigación?**
   - Buscar `DECISION` con `outcome: abandoned`
   - Reconstruir su contexto completo

2. **¿Qué alternativas se consideraron?**
   - Buscar aristas `chosen_over` y `abandoned_for`

3. **¿Qué tan persistente fue el equipo?**
   - Métrica: `backtracking_frequency` = abandoned / total decisions

4. **¿Qué decisiones condujeron a resultados exitosos?**
   - Filtrar por `outcome: success` y reconstruir árbol

5. **¿Hay patrones en las decisiones fallidas?**
   - Analizar commonalities en `rationale` de decisiones con `outcome: failure`

---

*Esta versión 1.1.0 extiende EvidenceGraph para capturar trayectorias de decisión, respondiendo a la necesidad de trazabilidad semántica de por qué se eligió un camino científico sobre otros.*