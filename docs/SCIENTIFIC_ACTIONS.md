# Scientific Actions
## The Interaction Primitives for CoResearcher

---

## Separación Arquitectónica Clara

```
Human Language
     ↓
[Scientific Semantic Compiler]
     ↓                     (Interprets → Transforms to actions)
Scientific Language
     ↓
[Participation Layer]
     ↓                     (Registers → Creates action records)
ACTION-XXXXXX
     ↓
[Trust Layer]
     ↓                     (Evaluates → Updates scores)
trust_score, consensus_score
```

---

## Primitivas de Acción

### OBJECTO CREACIÓN

| Acción | Texto de Input | Output | Registry |
|------|---------------|--------|----------|
| **QUESTION** | "¿Por qué...?" | QUESTION-XXXXXX | Question Registry |
| **OBSERVATION** | "Se observa que..." | OBS-XXXXXX | Observation Registry |
| **PROPOSE** | "Propongo que..." | HYP-XXXXXX | Hypothesis Registry |
| **MECHANIZE** | "El mecanismo podría ser..." | MECH-XXXXXX | Mechanism Registry |

---

### VALIDACIÓN PARTICIPATIVA

| Acción | Texto de Input | Output | Layer |
|-------|---------------|--------|-------|
| **SUPPORT** | "Estoy de acuerdo" | SUPPORT action | Participation |
| **CHALLENGE** | "No estoy de acuerdo porque..." | CHALLENGE action | Participation |
| **REPLICATE** | "Hemos replicado..." | REPLICATE action | Participation |
| **CONFIRM** | "Esto confirma..." | CONFIRM action | Participation |
| **REJECT** | "No podemos replicar" | REJECT action | Participation |

---

### EVOLUCIÓN DE OBJETOS

| Acción | Texto de Input | Output | Registry |
|-------|---------------|--------|----------|
| **FORK** | "Una variante podría ser..." | MECH-FORK | Mechanism Registry |
| **MERGE** | "Estos dos mecanismos podrían unirse" | MECH-MERGE | Mechanism Registry |
| **EXTEND** | "Este modelo se extendería a..." | MODEL-EXTEND | Model Registry |

---

## API de Acciones

```python
# Object Creation Actions
ACTION_QUESTION.create(text, domain) → QUESTION-XXXXXX
ACTION_OBSERVATION.record(entities, values) → OBS-XXXXXX
ACTION_PROPOSE.hypothesis(statement, derived_from) → HYP-XXXXXX
ACTION_MECHANIZE.mechanism(name, entities, arrows) → MECH-XXXXXX

# Participation Actions
ACTION_SUPPORT.register(object_id, researcher_id, evidence=None) → ACTION-SUP-XXXX
ACTION_CHALLENGE.register(object_id, researcher_id, reasoning) → ACTION-CHAL-XXXX
ACTION_REPLICATE.register(object_id, researcher_id, method) → ACTION-REP-XXXX
ACTION_CONFIRM.register(object_id, researcher_id, data) → ACTION-CONF-XXXX
ACTION_REJECT.register(object_id, researcher_id, counterevidence) → ACTION-REJ-XXXX

# Evolution Actions
ACTION_FORK.create(variant_of, changes) → OBJECT-FORK-XXXX
ACTION_MERGE.propose(objects_to_merge) → OBJECT-MERGE-XXXX
ACTION_EXTEND.apply(object_id, extension) → OBJECT-EXT-XXXX
```

---

## Flujo Completo de Ejemplo

### Investigador escribe:
> "No estoy de acuerdo con esta hipótesis. Los datos de nuestro laboratorio no muestran esa relación."

### Scientific Semantic Compiler interpreta:
```json
{
  "action": "CHALLENGE",
  "target_object": "HYP-00456",
  "entities": ["laboratorio datos"],
  "type": "counterevidence"
}
```

### Participation Layer registra:
```json
{
  "id": "ACTION-CHAL-00123",
  "type": "CHALLENGE",
  "target": "HYP-00456",
  "researcher": "RESEARCHER-0789",
  "reasoning": "Datos no coinciden",
  "timestamp": "..."
}
```

### Trust Layer evalúa:
```json
{
  "HYP-00456": {
    "challenges": 1,
    "trust_score": 0.45,
    "down_from": 0.50
  }
}
```

---

## Separación de Responsabilidades

### Scientific Semantic Compiler
- **Responsabilidad ÚNICA**: Interpretar lenguaje natural → acciones estructuradas
- **No registra nada**
- **No actualiza scores**
- Solo traduce

### Participation Layer
- **Responsabilidad ÚNICA**: Registrar acciones con su contexto
- **No interpreta**
- **No evalúa**
- Solo persiste

### Trust Layer
- **Responsabilidad ÚNICA**: Calcular consecuencias de acciones
- **No interpreta**
- **No registra**
- Solo evalúa

---

## Scientific Action Registry

```
knowledge/registry/actions/
```

Estructura:
```json
{
  "actions": [
    {
      "id": "ACTION-XXXXXX",
      "type": "SUPPORT|CHALLENGE|REPLICATE|...",
      "target_object": "HYP-XXXXXX|MECH-XXXXXX|...",
      "researcher": "RESEARCHER-XXXXXX",
      "timestamp": "...",
      "metadata": {...}
    }
  ]
}
```

---

## El Activo Final

No es:
- El número de mecanismos
- El número de claims
- El número de hypotheses

Es:
- **Número de acciones científicas auténticas**
- **Número de investigadores que interactúan**
- **Número de trust signals acumulados**

Este es el **Scientific Activity Graph** - el moat que ningún competidor podrá replicar.