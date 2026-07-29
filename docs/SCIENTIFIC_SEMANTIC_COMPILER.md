# Scientific Semantic Compiler
## The Sensor for the Scientific State Machine

## El Problema

Los investigadores no piensan en JSON:

```json
{
  "type": "MECHANISM",
  "subject": "APOE4",
  "predicate": "modulates",
  "object": "microglial activation"
}
```

Piensan en lenguaje natural:

> "No termino de entender por qué algunos APOE4 siguen cognitivamente normales a pesar de tener mucho amiloide."

Esto contiene implícitamente:
- QUESTION
- OBSERVATION  
- CONTRADICTION
- MECHANISM_GAP

todos mezclados.

---

## Arquitectura Propuesta

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

## API Principal

```python
from semantic.scientific_compiler import ScientificCompiler

compiler = ScientificCompiler()

result = compiler.compile(
    text="¿Por qué algunos APOE4 con amiloide elevado no desarrollan deterioro cognitivo?"
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

## Primitivas Compilables

### Preguntas (Implicitas o Explícitas)

```text
"¿Por qué...?" → QUESTION
"Estaría bien saber..." → QUESTION
"Será posible que...?" → HYPOTHESIS
```

### Observaciones

```text
"Los datos muestran..." → CLAIM/OBSERVATION
"Vimos que..." → FINDING
"Parece indicar..." → CLAIM
```

### Contradicciones

```text
"Esto contradice..." → CHALLENGE
"No encaja con..." → CONTRADICTION
"Debería ocurrir X pero vemos Y" → CONTRADICTION
```

### Hipótesis

```text
"Creo que..." → HYPOTHESIS
"Podría ser que..." → HYPOTHESIS
"Sería interesante probar..." → HYPOTHESIS + PREDICTION
```

### Participación

```text
"Estoy de acuerdo con..." → SUPPORT
"Hemos replicado..." → REPLICATE
"Esto confirma..." → CONFIRM
"No podemos replicar..." → REJECT
```

---

## Mapeo Texto → Objetos

| Patrón | Intención | Objeto |
|--------|-----------|---------|
| "¿[Qué/Por qué/Cómo]?" | QUESTION | QUESTION-XXXXXX |
| "muestra que\|indica que\|aparece" | CLAIM | CLAIM-XXXXXX |
| "contradice\|no encaja\|debería" | CONTRADICTION | CONTR-XXXXXX |
| "creo\|podría\|sería" | HYPOTHESIS | HYP-XXXXXX |
| "estoy de acuerdo\|confirmado" | SUPPORT | SUPPORT action |
| "hemos replicado\|replicación" | REPLICATE | REPLICATE action |

---

## Sprint 23A: Scientific Semantic Compiler

### Entregables

```
python/semantic/
├── scientific_compiler.py     # Compiler engine
├── intent_patterns.py         # Regex patterns for each primitive
├── entity_extractor.py        # Named entity recognition
└── test_compiler.py          # Validation tests
```

### Objetivo

Que investigadores e Einstein hablen el mismo lenguaje científico computable.

---

## El Scientific Interaction Graph

Cada interacción humana se convierte en objetos computables:

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

## El Verdadero Activo

No es:
- Claim Registry
- Mechanism Registry

Sino:
- **Scientific Interaction Graph**

Una red donde cada intención humana se traduce en:
- OBJECT CREATION
- ACTION RECORDING
- TRUST EVOLUTION

---

## Regla de Universalidad

> "**Si no funciona para física, no entra en el core.**"

El Scientific Semantic Compiler debe reconocer:

### Física
> "La luz se curva al pasar cerca del sol"

→ CLAIM (masa → trayectoria)

### Biología
> "APOE4 aumenta riesgo de deterioro cognitivo"

→ CLAIM (APOE4 → cognición)

### Economía
> "Subir tipos reduce inversión empresarial"

→ CLAIM (tipos → inversión)

Mismo esquema, diferentes entidades.

---

## Conexión con Participation Layer

La Participation Layer deja de ser artificial cuando el compiler infiere automáticamente las intenciones:

```text
Antes: Formulario "Support this mechanism"
Después: Investigador escribe "Confirmamos este mecanismo en nuestro laboratorio"
         ↓
         Compiler: CONFIRM + REPLICATE + MECHANISM_ID
```

---

## Sprint 23B: Integration

Conectar el Scientific Semantic Compiler con:
- Mechanism Registry
- Trust Layer
- Participation Layer

Para crear el primer **Scientific State Machine** operativo.