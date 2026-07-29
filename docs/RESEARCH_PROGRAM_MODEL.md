# Research Program Model
## From Knowledge Storage to Knowledge Production

---

## El Cambio de Paradigma

### Antes: Knowledge Storage
```
Researcher
↓
Knowledge
```

### Después: Knowledge Production
```
Research Program
↓
Knowledge
```

Donde:

```
TEAM-XXXXXX

Lead: RES-000123
Agents: [AGENT-000001, AGENT-000002, ...]
Mission: QUESTION-000456

Activities:
- PROPOSE_MECHANISM
- GENERATE_HYPOTHESIS  
- DESIGN_EXPERIMENT
- ANALYZE_RESULTS
- UPDATE_CONSENSUS
- DECIDE_PUBLICATION
```

---

## Research Program = TEAM + MISSION + ACTIVITY

### Estructura del Research Program

```json
{
  "team_id": "TEAM-000421",
  "lead": "RES-000012",
  "agents": ["AGENT-000001", "AGENT-000002"],
  "mission": "QUESTION-000192",
  "status": "active",
  "knowledge_strategy": "private|protected|published",
  "artifacts": ["MECH-001", "HYP-002", "PRED-003"]
}
```

---

## Knowledge Strategy Lifecycle

La pregunta no es solo "qué sabemos", sino "qué hacemos con el conocimiento".

```
Private
  ↓
Protected (embargo)
  ↓
Patent Pending
  ↓
Licensed
  ↓
Published
  ↓
Consensus
```

Esto es crucial porque:

```
Descubrimiento
↓
¿Publicar o proteger?
```

La decisión estratégica importa tanto como el descubrimiento.

---

## La Pregunta como Entidad Central

### Preguntas no Publicadas ≠ Preguntas Inútiles

Las preguntas guían la dirección científica:

```text
¿Qué problema merece perseguirse?
```

más que:

```text
¿Cómo resolverlo?
```

El Research Program se centra en:
- **Juicio**: ¿Qué preguntas son importantes?
- **Dirección**: ¿Qué camino tomar?
- **Selección**: ¿Qué hipótesis priorizar?
- **Priorización**: ¿Qué recursos asignar?

---

## Registro de Logros Reales

Hoy:

- **ORCID**: Quién eres
- **DOI**: Qué publicaste

Falta:

- **Quién descubrió**
- **Qué preguntas originaste**
- **Qué programas dirigiste**

CoResearcher puede registrar:

```
QUESTION-000123 → TEAM-000456
MECH-000789 → TEAM-000456  
ACTION-001234 → AGENT-000001
REPUTATION-000456 → TEAM-000456
```

---

## Research Program Registry

```
REPO/alzheimer-research/
├── program.json           # TEAM definition
├── lead/                  # RES-XXXXXX
├── agents/                # AGENT-XXXXXX
├── mission/               # QUESTION-XXXXXX
├── mechanisms/            # MECH-XXXXXX
├── hypotheses/            # HYP-XXXXXX
├── experiments/           # (external refs)
├── analysis/              # (external refs)
├── publications/          # (DOI refs)
├── strategy/              # private/protected/published
└── activity/              # ACTION-XXXXXX
```

---

## La Regla de Evaluación

Para cualquier decisión futura:

> ¿Esto ayuda a representar cómo se genera, valida, coordina y transfiere el conocimiento?

### Sí → Core
- Scientific Semantic Compiler
- ACTION-XXXXXX registry
- TEAM-XXXXXX structure
- Research Program workflows
- Knowledge Strategy states

### No → Periférico
- Solo almacenamiento de claims
- Solo graph de conocimiento
- UI fancy

---

## La Visión Final

No es:

```text
Knowledge Repository
```

Es:

```text
Scientific Production Infrastructure
```

Donde:

- El **Research Program** es el actor operativo
- El **Team** es la unidad de trabajo híbrida
- La **Question** es el norte estratégico
- La **Action** es la evidencia verificable
- La **Strategy** es el destino del conocimiento

---

## Sprint 23+ Roadmap

1. **Research Program Registry** - TEAM-XXXXXX structure
2. **Knowledge Strategy States** - private/protected/published
3. **Question-as-Hub** - Questions drive programs
4. **Hybrid Team Activity** - Humans + Agents coordination
5. **Production Tracking** - No solo conocimiento, proceso

---

## El Activo Diferencial

No es:
- Millones de claims
- Miles de mecanismos
- Biblioteca de papers

Es:
- **Historia de producción científica verificable**
- **Decisiones estratégicas registradas**
- **Equipos híbridos que generan conocimiento**
- **Preguntas que guiaron la investigación**

Esto es lo que ningún competidor tiene.

Y lo que ningún competidor podrá replicar fácilmente.

**CoResearcher no almacena conocimiento.**

**CoResearcher registra la producción de conocimiento.**