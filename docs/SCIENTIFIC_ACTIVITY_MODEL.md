# Scientific Activity Model
## GitHub-inspired Scientific Infrastructure

---

## Identificadores Importante (en orden de prioridad)

### Prioridad Máxima
```text
RES-XXXXXX - Researcher
    ↔ ORCID (identidad externa)
```
Toda actividad científica tiene autores.

### Prioridad Alta
```text
INST-XXXXXX - Institution
    ↔ ROR (identidad externa)
```
El consenso depende de diversidad institucional.

### Prioridad Media
```text
REPO-XXXXXX - Scientific Repository
```
Equivalante natural a repositorio GitHub.

### Prioridad Baja (futuros)
```text
TEAM-XXXXXX - Working Group
PROJ-XXXXXX - Project
ORG-XXXXXX - Organization/Consortium
```

---

## Scientific Repository Structure

```
REPO/alzheimer/
├── README.md (overview)
├── questions/ QUESTION-XXXXXX
├── claims/ CLAIM-XXXXXX
├── mechanisms/ MECH-XXXXXX
├── models/ MODEL-XXXXXX
├── theories/ THEORY-XXXXXX
├── branches/
│   ├── amyloid/
│   └── tau/
├── snapshots/
│   └── consensus-2028.md
└── team/
    └── curators
```

---

## Scientific Actions (Event Types)

### Core Actions
| Action | Description | Creates |
|--------|-------------|---------|
| **PROPOSE_QUESTION** | Formula pregunta | QUESTION-XXXXXX |
| **PROPOSE_CLAIM** | Formula afirmación | CLAIM-XXXXXX |
| **PROPOSE_MECHANISM** | Propone mecanismo | MECH-XXXXXX |
| **PROPOSE_MODEL** | Propone modelo | MODEL-XXXXXX |
| **PROPOSE_THEORY** | Propone teoría | THEORY-XXXXXX |

### Participation Actions
| Action | Description | Effect |
|--------|-------------|--------|
| **SUPPORT** | Apoyo explícito | +trust_score |
| **CHALLENGE** | Cuestionamiento | -trust_score |
| **REPLICATE** | Replicación | ++trust_score |
| **CONFIRM** | Confirmación empírica | +++trust_score |
| **REJECT** | Rechazo empírico | ---trust_score |
| **COMMENT** | Comentario | debate_score |
| **REVIEW** | Revisión | quality_signal |

### Evolution Actions
| Action | Description | Effect |
|--------|-------------|--------|
| **FORK** | Variante de objeto | new_object + lineage |
| **MERGE** | Integración de objetos | combined_object |
| **BRANCH** | Nueva línea investigación | RESEARCH_BRANCH |
| **PROPOSE_CONSENSUS** | Solicitud consenso | CONSENSUS_REQUEST |
| **ACCEPT_CONSENSUS** | Aceptación consenso | consensus_update |

---

## Scientific Activity Graph

No es un Knowledge Graph.

Es una **red de actividad verificable**:

```
RES-001 → PROPOSE_CLAIM → CLAIM-001
RES-002 → SUPPORT → CLAIM-001
RES-003 → CHALLENGE → CLAIM-001
RES-001 → PROPOSE_MECHANISM → MECH-001
RES-004 → REPLICATE → MECH-001
...
```

Esto crea:
- **Historial inmutable de actividad**
- **Reputación trazable por investigador**
- **Consenso evolutivo visible**

---

## Consensus Snapshots

Versiones congeladas del conocimiento:

```
alzheimer-consensus-2027
alzheimer-consensus-2028
alzheimer-consensus-2029
```

Cada snapshot:
- Contiene CLAIM/MECH/THEORY con trust_score > threshold
- Es citado como DOI/URI
- Representa consenso en momento dado

---

## Research Program = Branch

```
Alzheimer Research
├── amyloid branch
├── tau branch  
├── neuroinflammation branch
└── vascular branch
```

Cada branch:
- Tiene curador/es
- Tiene mecanismos propios
- Puede mergearse con otros

---

## The Moat

Software → copiable (2-5 años)
Standard → defensable (5-10 años)
Institution → imbatible (décadas)

El activo es la **red de actividad acumulada**:

```
100,000 claims
+
1,000,000 SUPPORT actions
+
300,000 REPLICATE actions
+
50,000 CHALLENGE actions
+
RES/INST identities linked
=
Scientific Coordination Infrastructure
```

---

## Priority Implementation Order

### Sprint 23A: Activity Model Foundation
- RES-XXXXXX + ORCID federation
- INST-XXXXXX + ROR federation
- ACTION-XXXXXX (tipo SIP actions)

### Sprint 23B: Repository Structure
- REPO-XXXXXX structure
- Branch/Merge workflow
- Consensus snapshots

### Sprint 23C: Compiler Integration
- Natural language → Scientific Actions
- Trust scores from actions

### Sprint 23D+: Growth
- TEAM/PROJ/ORG identifiers
- ScientificHub interface
- Advanced consensus algorithms

---

## No es un Knowledge Graph

GitHub no ganó por almacenar código.

Ganó por coordinar desarrolladores.

CoResearcher ganará por:
- Coordinar investigadores
- Versionar conocimiento científico
- Hacer visible el consenso
- Trackear reputación verificable

Este es el **Scientific Coordination Infrastructure** de la próxima década.