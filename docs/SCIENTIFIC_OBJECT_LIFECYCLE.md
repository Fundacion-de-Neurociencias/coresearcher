# Scientific Object Lifecycle
## From Observation to Theory in CoResearcher

## El Camino del Conocimiento

```
Observation → Claim → Finding → Mechanism → Model → Theory
     ↓          ↓       ↓         ↓        ↓       ↓
   (cruda)   (atómica) (estruct.) (explic.) (conjunto) (paradigma)
```

---

## 1. Observation (No registrada)

Dato crudo sin estructura:
- Texto de paper
- Resultado de experimento
- Imagen médica
- Señal genómica

---

## 2. Claim (CLAIM-XXXXXX)

### Nacimiento
```
Paper extraído → Claim identificado
```

### Atributos
- `text`: afirmación literal
- `entities`: entidades involucradas
- `evidenceScore`: confianza en la observación
- `supportingPapers`: [PMID-XXXXXX, ...]
- `domain`: área de conocimiento

### Operaciones
- `SUPPORT` - reforzar la claim
- `CHALLENGE` - cuestionar la claim
- `RETRACT` - retirar la claim

### Ciclo de vida
Baja mutabilidad. Pasa a archived.

---

## 3. Finding (FIND-XXXXXX)

### Nacimiento
```
Claim + Claim + Claim → Finding distilado
(o
Paper → KnowledgeDistillationEngine → Finding)
```

### Atributos
- `subject`: entidad principal
- `predicate`: relación (predicts, causes, associated)
- `object`: entidad relacionada
- `effect_size`: magnitud
- `p_value`: significancia
- `derivedFrom`: [CLAIM-XXXXXX, ...]
- `quality_score`: 0.0-1.0

### Operaciones
- `CONFIRM` - evidencia adicional
- `REJECT` - refutación empírica
- `REPLICATE` - replicación independiente

### Ciclo de vida
```
created → validated → replicated → challenged → merged → archived
```

---

## 4. Mechanism (MECH-XXXXXX)

### Nacimiento
```
Anomaly + Finding → Mechanism proposito
(o
Finding + Finding → Mechanism inferido)
```

### Atributos
- `name`: nombre descriptivo
- `description`: explicación detallada
- `entities`: [entidad, ...]
- `arrows`: path causal
- `type`: causal_chain/feedback/threshold/compensatory/emergent
- `confidence`: 0.0-1.0
- `derived_from`: [FIND-XXXXXX, CLAIM-XXXXXX]
- `contradicts`: [MECH-XXXXXX, ...]
- `supports`: [MECH-XXXXXX, ...]

### Operaciones (Participation Layer)
- `SUPPORT` - evidencia a favor
- `CHALLENGE` - análisis crítico
- `REPLICATE` - replicación mecanismo
- `REJECT` - refutación
- `FORK` - variante mecanismo
- `MERGE` - combinación mecanismos

### Ciclo de vida crítico
```
proposed (confidence=0.1)
    ↓
explored (challenges, forks)
    ↓
validated (replications, confirms)
    ↓
adopted (high trust_score, institution_count)
    ↓
refuted OR remains dominant
```

---

## 5. Model (MODEL-XXXXXX)

### Nacimiento
```
Mechanism + Mechanism + Mechanism → Model integrador
```

### Atributos
- `name`: nombre del modelo
- `mechanisms`: [MECH-XXXXXX, ...]
- `boundaries`: scope del modelo
- `assumptions`: supuestos clave
- `predictions`: predicciones derivadas

### Operaciones
- `FIT_TEST` - qué tan bien explica datos
- `CROSS_VALIDATE` - predicciones nuevas
- `EXTEND` - ampliar scope

---

## 6. Theory (THEORY-XXXXXX)

### Nacimiento
```
Model + Model + Model → Theory unificadora
```

### Atributos
- `name`: nombre de la teoría
- `models`: [MODEL-XXXXXX, ...]
- `domain_coverage`: áreas cubiertas
- `explanatory_power`: 0.0-1.0
- `consilience`: grado de unificación

---

## Relaciones de Confianza

```
CLAIM.trust = evidenceScore
FINDING.trust = avg(claims.trust) + replications
MECHANISM.trust = participation_signals(support, challenge, replicate)
MODEL.trust = mechanisms.trust_avg
THEORY.trust = models.trust_avg + consilience
```

---

## Participation Signals Matrix

| Acción | Objeto | Efecto en Trust |
|--------|---------|-----------------|
| SUPPORT | CLAIM | +0.1 |
| CHALLENGE | CLAIM | -0.1 |
| REPLICATE | FINDING | +0.2 |
| CONFIRM | MECHANISM | +0.3 |
| REJECT | MECHANISM | -0.5 |
| FORK | MECHANISM | +0.1 (variante) |

---

## La Regla de Oro

**Un objeto científico no existe para el descubrimiento hasta que puede ser refutado.**

- Claim: difícil de refutar (es observación)
- Finding: refutable (predicción cuantitativa)
- Mechanism: altamente refutable (predicciones específicas)
- Model: refutable (restricciones predictivas)
- Theory: más fácil de refutar (muchas predicciones)

---

## El Motor de Mejora

```
MECHANISM.trust_low
      ↓
"Can this be refuted?"
      ↓
YES → Predictions generated
      ↓
Predictions tested
      ↓
Trust evolves (up/down)
      ↓
Survives OR dies
```

Este es el ciclo que hace que CoResearcher sea un OS de descubrimiento, no una base de datos.