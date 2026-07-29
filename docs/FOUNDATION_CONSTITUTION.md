# Foundation Constitution
## The Immutable Decisions for CoResearcher

---

## Decision 1: Capa Semántica sobre GitHub

**No construir ScientificHub como reemplazo de GitHub.**

CoResearcher es una **capa semántica** que da significado científico a la infraestructura existente.

```
GitHub Issue → Semantic Compiler → QUESTION-XXXXXX
GitHub Discussion → Semantic Compiler → CHALLENGE ACTION
GitHub PR → Semantic Compiler → HYPOTHESIS FORK
GitHub Commit → Semantic Compiler → SCIENTIFIC ACTION
```

GitHub = infraestructura. CoResearcher = significado.

---

## Decision 2: Identidades Externas de Primera Clase

**ORCID y ROR son ciudadanos de primera clase desde el día 1.**

No opcionales. No extensiones. Identidades fundamentales.

```json
Researcher {
  "res_id": "RES-XXXXXX",
  "orcid": "0000-0002-1825-0097",  // obligatorio
  "name": "...",
  "reputation": "..."
}

Institution {
  "inst_id": "INST-XXXXXX",
  "ror": "https://ror.org/...",  // obligatorio
  "name": "...",
  "trust_history": [...]
}
```

---

## Decision 3: ACTION-XXXXXX como Identificador Principal

**El activo principal no es el conocimiento. Es la actividad.**

ACTION es el identificador principal:

```
ACTION-000001  // SUPPORT
ACTION-000002  // CHALLENGE  
ACTION-000003  // REPLICATE
ACTION-000004  // FORK_HYPOTHESIS
ACTION-000005  // CONFIRM
ACTION-000006  // REJECT
```

Toda reputación, consenso y confianza deriva de acciones inmutables.

---

## Decision 4: Scientific Activity Graph es el Activo

**No Knowledge Graph. Scientific Activity Graph.**

```
Knowledge Graph:  qué sabemos
Activity Graph:   quién propuso, quién apoyó, quién replicó, quién desafió
```

GitHub no vale miles de millones por repositorios.
Valdrá miles de millones por la actividad acumulada.

---

## Decision 5: Agent First Principle

**Toda funcionalidad debe ser consumible por agente antes que por humano.**

El 95% de las interacciones futuras serán:

```
Agent → MCP → CoResearcher → Knowledge
```

No:

```
Human → UI → CoResearcher → Knowledge
```

### Agent Compiler Mode

```json
{
  "input": {
    "entity": "BIOMARKER-000342",
    "claims": ["CLAIM-000391", "CLAIM-000482"]
  },
  "output": {
    "consensus": 94,
    "support_actions": 15234,
    "challenge_actions": 234
  }
}
```

Los agentes aman IDs, URIs, schemas, graphs.

---

## Decision 6: AGENT-XXXXXX Identifier

Reservar desde el día 1:

```
AGENT-XXXXXX
```

Para consumidores automáticos:

| Agent ID | Consumer |
|----------|----------|
| AGENT-000001 | Claude Research |
| AGENT-000002 | Gemini Deep Research |
| AGENT-000003 | OpenAI Research |

Un claim usado por 50,000 agentes es tan importante como uno citado 300 veces.

---

## Decision 7: MCP First Over Web

**MCP/API/Protocol es más importante que UI.**

El moat verdadero:

> "La fuente de verdad científica más fácil de consumir por agentes"

---

## Identificadores Fundamentales (Congelados)

---

## Identificadores Fundamentales (Congelados)

### Ciudadanos de Primera Clase
```
RES-XXXXXX = Researcher (orcid obligatorio)
INST-XXXXXX = Institution (ror obligatorio)
REPO-XXXXXX = Scientific Repository
ACTION-XXXXXX = Scientific Action (inmutable)
```

### Objetos Científicos
```
QUESTION-XXXXXX
OBSERVATION-XXXXXX
MEASUREMENT-XXXXXX
CLAIM-XXXXXX
MECHANISM-XXXXXX
MODEL-XXXXXX
THEORY-XXXXXX
```

### Identificadores Externos Federados
```
DOI → CLAIM provenance
PMID → OBS provenance
arXiv → CLAIM provenance
ORCID → RES identity
ROR → INST identity
```

---

## Priority Implementation Order

### Sprint 23A: ACTION Foundation
- ACTION-XXXXXX registry (inmutable)
- ORCID federation (RES-XXXXXX)
- ROR federation (INST-XXXXXX)

### Sprint 23B: Compiler Integration
- Natural language → ACTION mapping
- Scientific Semantic Compiler v1

### Sprint 23C: Repository Structure
- REPO-XXXXXX structure
- Branch/Merge workflow
- Consensus snapshots

### Sprint 23D+: Growth
- CLAIM/MECH/QUESTION registries
- Trust scoring from actions
- ScientificHub interface

---

## Lo que NO se Debe Hacer

❌ No construir otro GitHub desde cero  
❌ No crear perfiles sin ORCID/ROR  
❌ No hacer CLAIM sin ACTION trazabilidad  
❌ No priorizar registries sobre actividad  
❌ No retrasar Scientific Semantic Compiler  

---

## Lo que SÍ se Debe Hacer

✅ Resolver la coordinación científica como prioridad  
✅ Federar con estándares externos desde el día 1  
✅ Capturar toda actividad como ACTION inmutable  
✅ Hacer visible el consenso evolutivo  
✅ Trackear reputación por acciones verificables  

---

## La Historia Importa

Los datos de conocimiento pueden replicarse.

La **actividad histórica verificable** no.

```
10 años de:
- quién propuso
- quién apoyó  
- quién replicó
- quién desafió
- cómo evolucionó
```

Esto crea décadas de ventaja competitiva.

---

## Scientific Coordination Infrastructure

No es un producto.

Es una **infraestructura de coordinación científica**.

ORCID coordinó identidades.
DOI coordinó artefactos.
CoResearcher coordinará **actividad científica**.

Este es el estándar que permitirá coordinar la producción de conocimiento científico del futuro.