# Mechanism Universality Test
## Validating MECH-XXXXXX as a Universal Scientific Primitive

## The Trial by Fire

If `MECH-XXXXXX` is a universal primitive, it should work the same for:
- Biology
- Physics
- Economy
- Engineering
- Social Sciences

---

## Mechanism 1: Biology (Neurodegeneration)

```
APOE4
  ↓
neuroinflamación
  ↓
tau hyperfosforilación
  ↓
deterioro cognitivo
```

**Type**: threshold
**Entities**: ["APOE4", "microglia", "tau", "neurons"]
**Prediction**: "APOE4 homozygotes will show inflammation + tau before symptoms"

---

## Mechanism 2: Physics (Relativity)

```
masa
  ↓
curvatura espacio-temporal
  ↓
trayectoria geodésica
  ↓
órbita hacia el sol
```

**Type**: causal_chain
**Entities**: ["mass", "space-time", "orbit"]
**Prediction**: "Light will deviate 1.75" in solar eclipses

---

## Mechanism 3: Economy (Monetary Policy)

```
tipos de interés
  ↓
coste de capital
  ↓
inversión empresarial
  ↓
empleo
```

**Type**: causal_chain
**Entities**: ["types", "capital", "investment", "employment"]
**Prediction**: "100bp increase in rates reduces investment by 2-3%"

---

## Mechanism 4: Engineering (Materials Fatigue)

```
temperatura cíclica
  ↓
fatiga térmica
  ↓
microfissuras
  ↓
fallo estructural
```

**Type**: threshold
**Entities**: ["temperature", "material", "crack", "fault"]
**Prediction**: "After N thermal cycles, failure at load X"

---

## Mechanism 5: Social Sciences (Technology Adoption)

```
precio accesible
  ↓
adopción inicial
  ↓
red de efecto
  ↓
difusión masiva
```

**Type**: feedback
**Entities**: ["price", "adoption", "network", "diffusion"]
**Prediction**: "When adoption > 15%, exponential growth"

---

## Universal Pattern Detected

```
ENTITY-A (estímulo)
  ↓
PROCESS-X (mechanism)
  ↓
ENTITY-B (resultado intermedio)
  ↓
ENTITY-C (resultado final)
```

### Universal attributes:

| Attribute | Function |
|----------|---------|
| `entities` | What objects are involved |
| `type` | What kind of causal relationship |
| `arrows` | Sequence of causality |
| `confidence` | How safe are we |
| `trust_score` | Scientific participation |

---

## MECH-XXXXXX Universal Structure

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

**This is identical for all disciplines.**

---

## Cross-Domain Validation

### Biology
- mechanism_type: threshold
- **threshold?** Yes - APOE4 only pathological under stress

### Physics
- mechanism_type: causal_chain
- **causal_chain?** Yes - mass → curvature → trajectory

### Economy
- mechanism_type: causal_chain
- **causal_chain?** Yes - types → capital → investment

### Engineering
- mechanism_type: threshold
- **threshold?** Yes - cumulative fatigue leads to failure

###Social
- mechanism_type: feedback
- **feedback?** Yes - adoption generates more adoption

---

## Conclusion

**MECH-XXXXXX is a universal primitive.**

The same structure was conceived to be valid for:
- 5 different disciplines
- 5 types of mechanisms
- 5 verifiable predictions

This confirms that the **Scientific State Machine** can exist as a common core.

---

## Strategic Implication

Everything specific to:
- Neurodiagnoses
- GeneForge
- Medicine

Goes to **Domain Packs**.

The core is:
- CLAIM/FINDING/MECH/QUESTION/RESEARCHER
- Participation Layer
- Trust Layer

With this rule:
> "**If it doesn't work for physics, it doesn't enter the core.**"

---

## Sprint 23B: The Real Validation

Not writing code.

It is by demonstrating that the same MECH-XXXXXX object can:

1. Represent mechanisms in 5 disciplines
2. Generate testable predictions
3. Receive participation signals
4. Evolve trust_score

If it works → Universal Core.
If it doesn't work → Back to the drawing board.