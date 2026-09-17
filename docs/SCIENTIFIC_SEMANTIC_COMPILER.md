#Scientific Semantic Compiler
## The Sensor for the Scientific State Machine

## The Problem

Researchers don't think about JSON:

```json
{
  "type": "MECHANISM",
  "subject": "APOE4",
  "predicate": "modulates",
  "object": "microglial activation"
}
```

They think in natural language:

> "I don't quite understand why some APOE4 people remain cognitively normal despite having a lot of amyloid."

This implicitly contains:
- QUESTION
- OBSERVATION  
- CONTRADICTION
- MECHANISM_GAP

all mixed.

---

## Proposed Architecture

```
Human Language Layer
      ↓
Scientific Semantic Compiler
      ↓
Scientific Object Layer
      ↓
Reasoning Layer
      ↓
Discovery Layer
      ↓
Scientific State Machine
```

---

## Main API

```python
from semantic.scientific_compiler import ScientificCompiler

compiler = ScientificCompiler()

result = compiler.compile(
text="Why do some APOE4 with elevated amyloid not develop cognitive impairment?"
)

# Output:
ScientificIntent(
    objects=[
        Question(id="Q-001", text="..."),
        Observation(entities=["APOE4", "amyloid", "cognitive decline"]),
        Contradiction(id="CONTR-001"),
        MechanismGap(id="MECHGAP-001")
    ],
    actions=["QUESTION"],
    entities=["APOE4", "amyloid", "cognitive decline"],
    confidence=0.85
)
```

---

## Compilable Primitives

### Questions (Implicit or Explicit)

```text
"Because...?" → QUESTION
"Estaría bien saber..." → QUESTION
"Será posible que...?" → HYPOTHESIS
```

### Observations

```text
"Los datos muestran..." → CLAIM/OBSERVATION
"Vimos que..." → FINDING
"Parece indicar..." → CLAIM
```

### Contradictions

```text
"Esto contradice..." → CHALLENGE
"No encaja con..." → CONTRADICTION
"Debería ocurrir X pero vemos Y" → CONTRADICTION
```

### Hypothesis

```text
"Creo que..." → HYPOTHESIS
"Podría ser que..." → HYPOTHESIS
"Sería interesante probar..." → HYPOTHESIS + PREDICTION
```

### Participation

```text
"Estoy de acuerdo con..." → SUPPORT
"Hemos replicado..." → REPLICATE
"Esto confirma..." → CONFIRM
"No podemos replicar..." → REJECT
```

---

## Mapping Text → Objects

| Pattern | Intent | Object |
|--------|------------|---------|
| "[What/Why/How]?" | QUESTION | QUESTION-XXXXXX |
| "shows that\|indicates that\|appears" | CLAIM | CLAIM-XXXXXX |
| "contradicts\|doesn't fit\|should" | CONTRADICTION | CONTR-XXXXXX |
| "I think\|could\|would be" | HYPOTHESIS | HYP-XXXXXX |
| "I agree\|confirmed" | SUPPORT | SUPPORT action |
| "we have replicated\|replication" | REPLICATE | REPLICATE action |

---

## Sprint 23A: Scientific Semantic Compiler

### Deliverables

```
python/semantic/
├── scientific_compiler.py     # Compiler engine
├── intent_patterns.py         # Regex patterns for each primitive
├── entity_extractor.py        # Named entity recognition
└── test_compiler.py          # Validation tests
```

### Objective

That researchers and Einstein speak the same computable scientific language.

---

## The Scientific Interaction Graph

Every human interaction becomes computable objects:

```
Investigador: "Creo que..."
    ↓
Compiler: HYPOTHESIS
    ↓
Registry: HYP-XXXXXX
    ↓
Participation Layer actualiza trust_score
    ↓
Otro investigador: "Estoy de acuerdo"
    ↓
Compiler: SUPPORT
    ↓
Trust score ↑
```

---

## The True Asset

It is not:
- Claim Registry
-Mechanism Registry

Otherwise:
- **Scientific Interaction Graph**

A network where every human intention translates into:
- OBJECT CREATION
- ACTION RECORDING
- TRUST EVOLUTION

---

## Universality Rule

> "**If it doesn't work for physics, it doesn't enter the core.**"

The Scientific Semantic Compiler must recognize:

### Physics
> "Light bends as it passes near the sun"

→ CLAIM (mass → trajectory)

### Biology
> "APOE4 increases the risk of cognitive impairment"

→ CLAIM (APOE4 → cognition)

### Economy
> "Raising rates reduces business investment"

→ CLAIM (types → investment)

Same scheme, different entities.

---

## Connection with Participation Layer

The Participation Layer is no longer artificial when the compiler automatically infers the intentions:

```text
Antes: Formulario "Support this mechanism"
After: Researcher writes "We confirm this mechanism in our laboratory"
         ↓
         Compiler: CONFIRM + REPLICATE + MECHANISM_ID
```

---

## Sprint 23B: Integration

Connect the Scientific Semantic Compiler with:
-Mechanism Registry
- Trust Layer
- Participation Layer

To create the first operational **Scientific State Machine**.