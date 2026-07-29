# Discovery Theory
## CoResearcher's Theory of Scientific Discovery

## El Problema Fundamental

¿Puede una máquina generar conocimiento científico real, o solo reprocesar lo existente?

## Teoría de los 3 Mecanismos de Descubrimiento

### 1. Análisis de Anomalías → Descubrimiento

```
Observación normal
      ↓
Anomaly detected (algo no encaja)
      ↓
Desconstrucción del modelo actual
      ↓
Necesidad de explicación nueva
      ↓
Hipótesis emergente
```

**Ejemplo**: "Amyloid hypothesis" funciona en animales pero falla en humanos → ¿Qué está mal?

### 2. Experimentación Mental (Einstein Style) → Descubrimiento

```
Assumption: X is true
    ↓
Extreme case: What if I push X to its limit?
    ↓
Contradiction found: This leads to impossibility
    ↓
New hypothesis: X must be false, Y is true
```

**Ejemplo**: "What if I could ride alongside a light beam?" → Special Relativity

### 3. Conexión entre Mecanismos → Descubrimiento

```
Mechanism A en dominio X
      ↓
Mechanism B en dominio Y
      ↓
Analogía estructural
      ↓
Mecanismo AB: conexión cruzada
      ↓
Predicción inesperada
```

**Ejemplo**: Mecanismo de pruning sináptico (neurociencia) + mecanismo de pruning proteico (cáncer)

## El Discovery Pipeline

```
Question
   ↓
Evidence (claims, papers)
   ↓
Finding (distilled patterns)
   ↓
ANOMALY (trust gaps, contradictions, boundaries)
   ↓
Mechanism (explanatory hypothesis)
   ↓
Thought Experiment (extreme case analysis)
   ↓
Hypothesis (reframing or novel connection)
   ↓
Prediction (testable consequences)
   ↓
Validation (empirical or logical)
```

## Qué Hace al Descubrimiento Valioso

### Surprise Factor
- La predicción no era obvia desde el conocimiento previo
- Un experto diría: "No había pensado en esto"

### Confidence Trajectory
```
Novel mechanism (confidence bajo)
    ↓
Predicciones confirmadas
    ↓
Confidence ↑
    ↓
Adopted by field
```

### Participation Signals
- Cuántos científicos lo exploran
- Cuántos intentos de replicación
- Cuántos desafíos
- Cuántas instituciones involucradas

---

## Einstein v2: Operando sobre Mecanismos

### Antes (claims):
```python
for claim in claims:
    if claim.entity == "amyloid":
        generate_hypothesis("reduce amyloid")
```
→ Type B synthesis

### Después (mechanisms):
```python
for mech in mechanisms:
    if mech.type == "threshold":
        extreme = push_to_limit(mech)
        contradiction = find_paradox(extreme)
        hypothesis = reframe(contradiction)
```
→ Type C/D discovery

---

## Métricas de Descubrimiento Auténtico

| Métrica | Tipo A | Tipo B | Tipo C | Tipo D |
|---------|--------|--------|--------|--------|
| Surprise | 0% | 20% | 60% | 90% |
| Explanatory Power | Bajo | Medio | Alto | Muy Alto |
| Testability | Alta | Alta | Media | Media-Alta |
| Confidence Trajectory | Plano | Plano | Creciente | Creciente |
| Participation Potential | Bajo | Medio | Alto | Muy Alto |

---

## El Motor de Descubrimiento como Sistema Económico

No es solo generar hypotheses. Es crear un **sistema donde:**

1. Los mecanismos nacen de anomalies
2. Las hypotheses emergen de mecanismos
3. Las predicciones prueban mecanismos
4. La participación acumula confianza
5. La confianza atrae más participación

Esto crea un **feedback loop científico positivo** que vale décadas.

---

## Roadmap de Implementación

### Sprint 22A: Validación
- discovery_benchmark.py ✓
- benchmarks/ ✓
- Participation Layer primitives ✓

### Sprint 23A: Constitución
- Mechanism Constitution ✓
- Discovery Theory ✓
- Object Lifecycle

### Sprint 23B: Registro
- Mechanism Registry (simple)
- Integración con Findings
- Conexión con Participation

### Sprint 24: Einstein v2
- Operación sobre mechanisms reales
- Thought experiments con datos reales
- Generación de Type C/D auténticos