# Diffusion Discovery Theory
## Scientific Creativity Through Manifold Interpolation

---

## The central insight

> **Creativity emerges when the system DOES NOT exactly memorize reality.**

This insight from Google's diffusion models applies directly to the epistemology of scientific discovery:

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

**Creativity = structured interpolation**

Not magic. Not inspiration. Not consciousness.

---

## The analogy with CoResearcher

### Memory system (current in medical AI)

```text
Claim A: GFAP ↑
Claim B: NfL ↑

Predicción:
GFAP
o
NfL
```

### Interpolator system (CoResearcher)

```text
Claim A: GFAP ↑
Claim B: NfL ↑
Finding: trayectoria temporal asociada

Interpolación estructurada:
- GFAP + NfL combinados
- ratio GFAP/NfL
- trayectoria temporal combinada
- unified causal mechanism
```

**Not in the data. But it doesn't come out of nowhere either.**

---

## The Scientific Manifold

### The underlying geometry of knowledge

Google says: *"Score smoothing facilitates manifold recovery"*

Scientific translation:

```text
Datos científicos
     ↓
Claims y Findings
     ↓
Mechanisms (geometría)
     ↓
Scientific Manifold
```

The mechanisms are geometry, not biomarkers (dots).

---

## Interpolation vs. Manifold Change

### The fundamental limitation

| Type | Description | Historical examples | Limitation |
|------|-------------|-------------------|------------|
| **Interpolation within the manifold** | Combine existing knowledge in new ways | Combined hypotheses, repurposing drugs | Bounded by current paradigm |
| **Manifold change** | Create new conceptual paradigms | CRISPR, PCR, Relativity, Transformers | Requires manifold rupture |

### Discovery types in classification

| Metric | Type A | Type B | Type C (Interpolation) | Type D (Manifold Change) |
|---------|-----|--------|-------------|---------|
| Surprise | 0% | 20% | 60% | 90% |
| Explanatory Power | Low | Medium | High | Very High |
| Manifold Change | None | None | Implicit | Explicit |

---

## The INTERPOLATION primitive

### A new computable scientific object

Based on the discovery pipeline:

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

### Formal definition

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

## Connection with Einstein Generator v2

### Operating on mechanisms

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

## Manifold rupture detection

### The constitutional problem

> Is science primarily interpolation within a known manifold or creation of new manifolds?

### Manifold output signals

```text
Manifold Change Indicators:
├── Concepts from unrelated domains
├── Predictions that contradict established paradigms
├── Claims requiring new ontological categories
├── Mechanisms with no precedent in literature
└── Terminology not found in current vocabulary
```

### Proposed implementation

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

## Connection with Scientific Semantic Compiler

### The compiler detects interpolations

```python
# Input: "What would happen if we combined the synaptic and protein pruning mechanisms?"

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

## The improved Scientific Interaction Graph

### Each interpolation is now explicit

```text
Researcher: "What if we combined X and Y?"
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

## Integration roadmap

### Sprint 24.5: Discovery Detection (IMPLEMENTED ✓)

- [x] `INTERPOLATION` as primitive in Scientific Semantic Compiler
- [x] `manifold_distance()` function in python/discovery/
- [x] Automatic manifold rupture detection
- [x] New "surprise through interpolation" metrics

### Sprint 25: Einstein v3

- [ ] Explicit interpolation operation between mechanisms
- [ ] Synthesis of cross mechanisms

---

## Implementation audit

### Level 1: Useful metaphor ✅

The analogy with diffusion models is valid as a design intuition:

```text
Biomarcadores (puntos)
    ↓
Mecanismos (estructura)
    ↓
Scientific Manifold
    ↓
Hypotheses in little explored regions
```

### Level 2: Computational Heuristics ⚠️

Implemented as `NoveltyDetector` - detects anomalies with respect to existing knowledge:

- **ontological_distance** - How far entities are from known categories
- **bibliographic_distance** - Whether the mechanisms have been connected before in literature
- **mechanism_gap** - What known mechanisms might be missing

### Level 3: Theory of scientific discovery ❓

The key question is not "is discovery = interpolation?" but:

> **How do we detect when a hypothesis proposes connections that have never been explored?**

This is more defensible than detecting "manifold ruptures" because:
- We do not assume that a target manifold exists
- We measure distance to existing institutional knowledge
- We identify opportunities for structured interpolation

---

## Current implementation

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

### The crucial distinction:

**Novelty ≠ Potential Impact**

A very novel hypothesis may simply be wrong.
Impact should be inferred from the accumulation of evidence, not from initial unusualness.

---

## Discovery cycle with NoveltyDetector

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

Einstein Generator is no longer just a creation engine.
It becomes an engine for **scientific space exploration**.

---

## Conclusion

This integration reinforces the core architectural decision of CoResearcher:

> **Mechanisms > Findings > Claims**

Because mechanisms are the structure on which a discovery system can operate, while findings are just scattered points.

The fundamental question that remains:

> **How far is this hypothesis from established scientific connections?**

This is a much more useful metric than any "manifold rupture" measurement.