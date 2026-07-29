# Mechanism Universality Test
## Validating MECH-XXXXXX as a Universal Scientific Primitive

## La Prueba de Fuego

Si `MECH-XXXXXX` es una primitiva universal, debe funcionar igual para:
- Biología
- Física
- Economía
- Ingeniería
- Ciencias Sociales

---

## Mecanismo 1: Biología (Neurodegeneración)

```
APOE4
  ↓
neuroinflamación
  ↓
tau hyperfosforilación
  ↓
deterioro cognitivo
```

**Tipo**: threshold
**Entidades**: ["APOE4", "microglía", "tau", "neuronas"]
**Predicción**: "APOE4 homocigóticos mostrarán inflamación + tau antes de síntomas"

---

## Mecanismo 2: Física (Relatividad)

```
masa
  ↓
curvatura espacio-temporal
  ↓
trayectoria geodésica
  ↓
órbita hacia el sol
```

**Tipo**: causal_chain
**Entidades**: ["masa", "espacio-tiempo", "órbita"]
**Predicción**: "La luz se desviará 1.75" en eclipses solares

---

## Mecanismo 3: Economía (Política Monetaria)

```
tipos de interés
  ↓
coste de capital
  ↓
inversión empresarial
  ↓
empleo
```

**Tipo**: causal_chain
**Entidades**: ["tipos", "capital", "inversión", "empleo"]
**Predicción**: "Incremento de 100pb en tipos reduce inversión en 2-3%"

---

## Mecanismo 4: Ingeniería (Fatiga de Materiales)

```
temperatura cíclica
  ↓
fatiga térmica
  ↓
microfissuras
  ↓
fallo estructural
```

**Tipo**: threshold
**Entidades**: ["temperatura", "material", "fissura", "fallo"]
**Predicción**: "Después de N ciclos termicos, fallo en carga X"

---

## Mecanismo 5: Ciencias Sociales (Adopción de Tecnología)

```
precio accesible
  ↓
adopción inicial
  ↓
red de efecto
  ↓
difusión masiva
```

**Tipo**: feedback
**Entidades**: ["precio", "adopción", "red", "difusión"]
**Predicción**: "Cuando adopción > 15%, crecimiento exponencial"

---

## Patrón Universal Detectado

```
ENTITY-A (estímulo)
  ↓
PROCESS-X (mecanismo)
  ↓
ENTITY-B (resultado intermedio)
  ↓
ENTITY-C (resultado final)
```

### Atributos universales:

| Atributo | Función |
|----------|---------|
| `entities` | Qué objetos están involucrados |
| `type` | Qué clase de relación causal |
| `arrows` | Secuencia de la causalidad |
| `confidence` | Cuán seguros estamos |
| `trust_score` | Participación científica |

---

## Estructura MECH-XXXXXX Universal

```json
{
  "id": "MECH-XXXXXX",
  "name": "string",
  "description": "string",
  "entities": ["any", "domain", "entities"],
  "arrows": ["step1 -> step2 -> step3"],
  "type": "causal_chain|feedback|threshold|compensatory|emergent",
  "confidence": 0.0-1.0,
  "derived_from": ["FIND/CLAIM IDs"],
  "contradicts": ["MECH IDs"],
  "trust_score": 0.0-1.0
}
```

**Esto es idéntico para todas las disciplinas.**

---

## Validación Cross-Domain

### Biología
- mechanism_type: threshold
- **¿threshold?** Sí - APOE4 solo patológico bajo estrés

### Física
- mechanism_type: causal_chain
- **¿causal_chain?** Sí - masa → curvatura → trayectoria

### Economía
- mechanism_type: causal_chain
- **¿causal_chain?** Sí - tipos → capital → inversión

### Ingeniería
- mechanism_type: threshold
- **¿threshold?** Sí - fatiga acumulativa lleva a fallo

### Social
- mechanism_type: feedback
- **¿feedback?** Sí - adopción genera más adopción

---

## Conclusión

**MECH-XXXXXX es una primitiva universal.**

La misma estructura concebía sea válida para:
- 5 disciplinas distintas
- 5 tipos de mecanismos
- 5 predicciones verificables

Esto confirma que el **Scientific State Machine** puede existir como un núcleo común.

---

## Implicación Estratégica

Todo lo específico de:
- Neurodiagnoses
- GeneForge
- Medicina

Va a **Domain Packs**.

El core es:
- CLAIM/FINDING/MECH/QUESTION/RESEARCHER
- Participation Layer
- Trust Layer

Con esta regla:
> "**Si no funciona para física, no entra en el core.**"

---

## Sprint 23B: La Validación Real

No escribiendo código.

Es demostrando que el mismo objeto MECH-XXXXXX puede:

1. Representar mecanismos en 5 disciplinas
2. Generar predicciones testables
3. Recibir participation signals
4. Evolucionar trust_score

Si funciona → Core universal.
Si no funciona → Back to the drawing board.