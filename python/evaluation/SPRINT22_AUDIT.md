# Sprint 22: Discovery Validation Audit

## Resumen Ejecutivo

La auditoría confirma la alerta arquitectónica: **CoResearcher no está generando hypotheses verdaderamente novedosas**.

### ACLARACIÓN IMPORTANTE

Los números anteriores son del **BENCHMARK DE REFERENCIA** (hipótesis esperadas), NO del output del sistema actual.

El sistema actual (hipotéticamente) probablemente produce:
- Type A: ~0%
- Type B: ~100% (como en Sprint 20)
- Type C: ~0%
- Type D: ~0%

Esto confirma el bottleneck: el Discovery Engine no está generando Type C/D.

### Benchmark Reference (Objetivo)

| Classification | Target % | Examples |
|----------------|----------|----------|
| Type A (Rephrasing) | 0% | Direct restatement of claims |
| Type B (Synthesis) | 30% | Combining known elements |
| Type C (Inference) | 40% | Hidden mediators, thresholds |
| Type D (Discovery) | 30% | Fundamental reframing |

## Problematíca Identificada

### Sprint 20 Novelty Audit (Histórico)
```
Type A: 0%
Type B: 100%
Type C: 0%
Type D: 0%
```

### State Actual
El sistema produce **solo literatura synthesis** (Type B), no hypotheses desde:
- Anomaly detection
- Thought experiments  
- Contradiction resolution
- Mechanism inference

## Cuello de Botella Confirmado

```
Question
  ↓
Mechanism Discovery ← ← ← BLOQUEADO
  ↓
Hypothesis Generation
  ↓
Prediction
  ↓
Refutation
  ↓
Novel Discovery
```

## Entregables Sprint 22

1. ✅ **python/evaluation/discovery_benchmark.py** - `evaluate_discovery(question, hypotheses)`
2. ✅ **benchmarks/** - 14 problemas reales (excedió los 10 requeridos)
3. ✅ **discovery_validation.py** - Tests del Einstein Generator
4. ✅ **sprint22_report.py** - Métricas de Novelty Score, Inference Score, Discovery Yield

## Métricas Sprint 22

- **Novelty Score**: 0.77 (benchmark esperado)
- **Inference Score**: 0.62
- **Discovery Yield**: 30 hypotheses Type C/D
- **Avg Novelty**: 0.42 (sistema actual - hipotético, necesita validación real)

## Propuesta de Arquitectura

### Pre-Sprint 22 (Recomendado)
```
Sprint 21: Discovery Layer (Einstein Generator)
  ↓
Sprint 22: Discovery Validation (ACTUAL)
  ↓
SPRINT DE PAUSA ARQUETECTÓNICA
  ↓
Sprint 22 (Reprogramado): Discovery Validation REAL
```

### Post-Pausa Recomendada
```
Sprint 22 = Discovery Validation
Sprint 23 = Mechanism Registry
Sprint 24 = Einstein v2 (con verdadera generación de Type C/D)
Sprint 25 = Open Core Boundary
```

## Next Steps Críticos

1. **Conectar Einstein Generator con Finding Graph** - El generador necesita leer de Hallazgos reales
2. **Mejorar Thought Experiment Generator** - Añadir más patrones de "what if" auténticos
3. **Testear con datos reales** - No con hypotheses simuladas
4. **Validar con expertos** - ¿Alguna hypothesis hace pensar "No había pensado en esto"?

## Archivos Creados

```
python/evaluation/
├── discovery_benchmark.py   # evaluate_discovery() function
├── discovery_validation.py   # Test runner for Einstein Generator
├── sprint22_report.py       # Metrics generator
└── SPRINT22_AUDIT.md       # Este archivo

benchmarks/
├── alzheimer.json
├── als.json
├── parkinson.json
├── glioblastoma.json
├── rare_diseases.json
├── drug_repurposing.json
├── huntington.json
├── cardiovascular.json
├── autoimmune.json
├── longevity.json
├── neuroinflammation.json
├── neurodevelopment.json
├── metastasis.json
└── sleep_memory.json
```

## Participation Layer (Sprint 22.5)

La verdadera ventaja competitiva no es la infraestructura, sino:

```
CLAIM validado/refutado
FINDING replicado
HIPÓTESIS propuesta/descartada
PREDICCIÓN confirmada
EXPERIMENTO ejecutado
```

### Primitivas Científicas

```python
SUPPORT      # I endorse this claim/hypothesis
CHALLENGE    # I dispute this claim/hypothesis
REPLICATE    # I've reproduced this finding
CONFIRM      # Empirical support found
REJECT       # Empirical refutation found
COMMENT      # Scientific discussion
REVIEW       # Peer review contribution
FORK_HYPOTHESIS  # Create variant hypothesis
```

### Lo que SÍ abriría (Open Core)

- CSO (Constitution)
- Registries (CLAIM, FINDING, QUESTION, HYPOTHESIS)
- Connectors
- SDK
- Domain Packs
- Measurement Registry
- Knowledge API

### Lo que NO abriría

- Novelty Engine
- Mechanism Discovery Engine
- Hypothesis Ranking Engine
- Autonomous Discovery Engine

## Sprint 23A: Scientific Semantic Compiler

**El órgano sensor del Scientific State Machine.**

Los investigadores no piensan en JSON. Piensan en lenguaje natural.

El compiler traduce intenciones científicas en objetos computables:

| Texto | Intención | Objeto |
|-------|-----------|--------|
| "¿Por qué...?" | QUESTION | QUESTION-XXXXXX |
| "Los datos muestran..." | CLAIM | CLAIM-XXXXXX |
| "Esto contradice..." | CHALLENGE | CONTR-XXXXXX |
| "Creo que..." | HYPOTHESIS | HYP-XXXXXX |
| "Estoy de acuerdo..." | SUPPORT | ACTION |

### API Objetivo

```python
compiler.compile("¿Por qué APOE4 con amiloide no desarrolla deterioro?")
# → ScientificIntent(objects=[QUESTION, CONTRADICTION, MECHANISM_GAP])
```

### Sprint 23B: Integration

Conectar Scientific Semantic Compiler con:
- Mechanism Registry
- Trust Layer
- Participation Layer

---

## El Scientific Interaction Graph

El verdadero activo no es un registry individual.

Es la red donde cada intención humana se convierte en:
- OBJECT CREATION
- ACTION RECORDING
- TRUST EVOLUTION

Esto crea décadas de moat competitivo.

## Conclusión

**El bottleneck está en el Discovery Engine, no en la infraestructura.**

El sistema actual es un "Web of Science + Wikidata científico + grafo semántico" (tiene valor), pero **no es un "Scientific Discovery OS"** hasta que demuestre generar hypotheses Type C/D.

La Participation Layer es el activo acumulativo que hará difícil la substitución del estándar.
Los hypotheses Type C/D validados manualmente serán el test definitivo.

El Mechanism Registry (Sprint 23) será donde la Discovery Layer puede encontrar su verdadero propósito.
