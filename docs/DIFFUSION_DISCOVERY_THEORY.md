# Diffusion Discovery Theory
## Scientific Creativity Through Manifold Interpolation

---

## El insight central

> **La creatividad emerge cuando el sistema NO memoriza exactamente la realidad.**

Este insight de los diffusion models de Google aplica directamente a la epistemología del descubrimiento científico:

```text
Datos observados
     ↓
Regularización
     ↓
Suavizado
     ↓
Interpolación
     ↓
Nuevas configuraciones plausibles
```

**Creatividad = interpolación estructurada**

No magia. No inspiración. No conciencia.

---

## La analogía con CoResearcher

### Sistema memorístico (actual en IA médica)

```text
Claim A: GFAP ↑
Claim B: NfL ↑

Predicción:
GFAP
o
NfL
```

### Sistema interpolador (CoResearcher)

```text
Claim A: GFAP ↑
Claim B: NfL ↑
Finding: trayectoria temporal asociada

Interpolación estructurada:
- GFAP + NfL combinados
- ratio GFAP/NfL
- trayectoria temporal combinada
- mecanismo causal unificado
```

**No está en los datos. Pero tampoco sale de la nada.**

---

## El Scientific Manifold

### La geometría subyacente del conocimiento

Google dice: *"Score smoothing facilitates manifold recovery"*

Traducción científica:

```text
Datos científicos
     ↓
Claims y Findings
     ↓
Mechanisms (geometría)
     ↓
Scientific Manifold
```

Los mecanismos son la geometría, no los biomarcadores (puntos).

---

## Interpolación vs. Cambio de Manifold

### La limitación fundamental

| Tipo | Descripción | Ejemplos históricos | Limitación |
|------|-------------|-------------------|------------|
| **Interpolación dentro del manifold** | Combinar conocimiento existente de formas nuevas | Hipótesis combinadas, fármacos repurposing | Bounded by current paradigm |
| **Cambio de manifold** | Crear nuevos paradigmas conceptuales | CRISPR, PCR, Relatividad, Transformers | Requires manifold rupture |

### Tipos de discovery en la clasificación

| Métrica | Tipo A | Tipo B | Tipo C (Interpolación) | Tipo D (Manifold Change) |
|---------|--------|--------|----------------------|------------------------|
| Surprise | 0% | 20% | 60% | 90% |
| Explanatory Power | Low | Medium | High | Very High |
| Manifold Change | None | None | Implicit | Explicit |

---

## La primitiva INTERPOLATION

### Un nuevo objeto científico computable

Basado en el pipeline de descubrimiento:

```text
Question
   ↓
Evidence (claims, papers)
   ↓
Finding (distilled patterns)
   ↓
ANOMALY (trust gaps, contradictions)
   ↓
Mechanism (explanatory hypothesis)
   ↓
INTERPOLATION ← NUEVO OBJETO
   ↓
Hypothesis (reframing or novel connection)
   ↓
Prediction (testable consequences)
```

### Definición formal

```yaml
interpolation:
  id: INTERP-000001
  inputs:
    - CLAIM-00123  # GFAP ↑
    - CLAIM-00456  # NfL ↑
    - MECH-00789    # Neuroinflammatory cascade
  operation: "structured_interpolation"
  method: "geometric_synthesis"
  outputs:
    - HYPOTHESIS-000001  # Combined trajectory hypothesis
    - MECHANISM-000002   # Integrated inflammatory mechanism
  confidence: 0.65
  manifold_distance: LOW  # Dentro del manifold existente
```

---

## Conexión con Einstein Generator v2

### Operando sobre mecanismos

```python
# Antes (claims):
for claim in claims:
    if claim.entity == "amyloid":
        generate_hypothesis("reduce amyloid")

# Después (interpolation sobre mechanisms):
for mech_a in mechanisms:
    for mech_b in mechanisms:
        if find_structural_analogy(mech_a, mech_b):
            distance = manifold_distance(mech_a, mech_b)
            if distance < threshold:
                interpolation = synthesize_mechanisms(mech_a, mech_b)
                hypothesis = derive_hypothesis(interpolation)
```

---

## Detección de manifold rupture

### El problema constitucional

> ¿La ciencia es principalmente interpolación dentro de un manifold conocido o creación de nuevos manifolds?

### Señales de salida del manifold

```text
Manifold Change Indicators:
├── Concepts from unrelated domains
├── Predictions that contradict established paradigms
├── Claims requiring new ontological categories
├── Mechanisms with no precedent in literature
└── Terminology not found in current vocabulary
```

### Implementación propuesta

```python
def detect_manifold_break(hypothesis):
    """Detect when a hypothesis is outside current conceptual space."""
    return {
        "novel_concepts": count_unprecedented_entities(hypothesis),
        "paradigm_shift": assess_paradoxical_predictions(hypothesis),
        "ontological_need": detect_missing_categories(hypothesis),
        "semantic_distance": measure_from_known_mechanisms(hypothesis)
    }
```

---

## Conexión con Scientific Semantic Compiler

### El compiler detecta interpolaciones

```python
# Input: "¿Qué pasaría si combináramos los mecanismos de pruning sináptico y proteico?"

# Compiler infiere:
ScientificIntent(
    objects=[
        Question(id="Q-001", text="..."),
        MechanismReference(id="MECH-001"),
        MechanismReference(id="MECH-002"),
        InterpolationIntent(id="INTERP-001")  ← NUEVO
    ],
    actions=["INTERPOLATE"]
)
```

---

## La Scientific Interaction Graph mejorada

### Cada interpolación es ahora explícita

```text
Investigador: "¿Y si combináramos X y Y?"
    ↓
Compiler: INTERPOLATION + MECHANISM_X + MECHANISM_Y
    ↓
Registry: INTERP-XXXXXX
    ↓
Participation Layer calcula manifold_distance
    ↓
Si distance > threshold: ALERTA - manifold rupture detection
    ↓
Oportunidad: nueva área ontológica a explorar
```

---

## Roadmap de integración

### Sprint 24.5: Discovery Detection (IMPLEMENTADO ✓)

- [x] `INTERPOLATION` como primitiva en Scientific Semantic Compiler
- [x] `manifold_distance()` función en python/discovery/
- [x] Detección automática de manifold rupture
- [x] Nuevas métricas de "surprise through interpolation"

### Sprint 25: Einstein v3

- [ ] Operación de interpolación explícita entre mecanismos
- [ ] Síntesis de mecanismos cruzados

---

## Auditoría de implementación

### Nivel 1: Metáfora útil ✅

La analogía con diffusion models es válida como intuición de diseño:

```text
Biomarcadores (puntos)
    ↓
Mecanismos (estructura)
    ↓
Manifold científico
    ↓
Hipótesis en regiones poco exploradas
```

### Nivel 2: Heurística computacional ⚠️

Implementado como `NoveltyDetector` - detecta anomalías respecto al conocimiento existente:

- **ontological_distance** - Qué tan lejos están las entidades de categorías conocidas
- **bibliographic_distance** - Si los mecanismos han sido conectados antes en literatura
- **mechanism_gap** - Qué mecanismos conocidos podrían estar faltando

### Nivel 3: Teoría del descubrimiento científico ❓

La pregunta clave no es "¿es descubrimiento = interpolación?" sino:

> **¿Cómo detectamos cuando una hipótesis propone conexiones que nunca han sido exploradas?**

Esto es más defendible que detectar "rupturas de manifold" porque:
- No asumimos que existe un manifold objetivo
- Medimos distancia al conocimiento institucional existente
- Identificamos oportunidades de interpolación estructurada

---

## Implementación actual

```python
# NoveltyDetector en python/discovery/novelty_detector.py
detector = NoveltyDetector(domain="neurodegeneration")

result = detector.assess_novelty({
    "statement": "Hypothesis statement",
    "entities": ["tau", "proteostasis", ...],
    "predictions": [...]
})

# Returns:
# - ontological_distance: 0.0-1.0 (distancia ontológica)
# - bibliographic_distance: 0.0-1.0 (combinaciones existentes)
# - institutional_distance: 0.0-1.0 (comunidades investigadoras)
# - novelty_score: 0.0-1.0 (medida de unusualness, NO impacto)
```

### La distinción crucial:

**Novelty ≠ Impacto potencial**

Una hipótesis muy novedosa puede ser simplemente incorrecta.
El impacto debe inferirse de la acumulación de evidencia, no de la unusualness inicial.

---

## Ciclo de descubrimiento con NoveltyDetector

```text
Question
    ↓
Mechanisms
    ↓
Hypothesis generation
    ↓
Novelty assessment ← NUEVO
    ↓
Prioritization (basado en novelty + plausibility)
    ↓
Review
```

Einstein Generator deja de ser solo un motor de creación.
Se convierte en un motor de **exploración del espacio científico**.

---

## Conclusión

Esta integración refuerza la decisión arquitectónica central de CoResearcher:

> **Mecanismos > Findings > Claims**

Porque los mecanismos son la estructura sobre la que puede operar un sistema de descubrimiento, mientras que los findings son solo puntos dispersos.

La pregunta fundamentacional que queda:

> **¿Qué tan lejos está esta hipótesis de las conexiones científicas establecidas?**

Esta es una métrica mucho más útil que cualquier medida de "ruptura de manifold".
