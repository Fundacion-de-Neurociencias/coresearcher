# Sprint 42D — Experiment Package

Paquete completo para realizar la validación de fiabilidad inter-observador.

## Contenido del Paquete

### 1. Protocolo de Observación
**Archivo:** `artifacts/sprint42d_observer_b_protocol.md`

Este documento define EXACTAMENTE cómo debe trabajar el Observador B:
- Qué puede y no puede leer
- Formato de salida obligatorio
- Justificación requerida para cada selección

### 2. Vocabulario Controlado
**Archivo:** `artifacts/sprint42d_controlled_vocabulary.md`

Lista COMPLETA y EXHAUSTIVA de categorías observadas:
- 13 categorías de Constraints
- 17 categorías de Uncertainties
- 14 categorías de Alternatives

**Regla:** SOLO usar estas categorías. NO inventar nuevas.

### 3. Esquema Atómico
**Archivo:** `artifacts/sprint42d_atomic_observation_schema.md`

Transformaciones de texto narrativo a observaciones atómicas:
- Ejemplos de cada categoría
- Formato JSON requerido

### 4. Métricas de Fiabilidad
**Archivo:** `artifacts/sprint42d_reliability_scoring.md`

Métricas predefinidas para evaluar concordancia:
- Jaccard Similarity
- Precision
- Recall
- Agreement Rate

### 5. Amenazas Identificadas
**Archivo:** `artifacts/sprint42d_threats_to_reliability.md`

Identificación de sesgos potenciales y mitigaciones.

## Casos a Observar (11 casos)

El Observador B debe observar EXACTAMENTE estos 11 casos:

| # | Issue | URL |
|---|-------|-----|
| 1 | mne-tools/mne-python#4414 | https://github.com/mne-tools/mne-python/issues/4414 |
| 2 | mne-tools/mne-python#3728 | https://github.com/mne-tools/mne-python/issues/3728 |
| 3 | nilearn/nilearn#2019 | https://github.com/nilearn/nilearn/issues/2019 |
| 4 | nilearn/nilearn#1766 | https://github.com/nilearn/nilearn/issues/1766 |
| 5 | bids-standard/pybids#356 | https://github.com/bids-standard/pybids/issues/356 |
| 6 | bids-standard/pybids#369 | https://github.com/bids-standard/pybids/issues/369 |
| 7 | mne-tools/mne-python#2154 | https://github.com/mne-tools/mne-python/issues/2154 |
| 8 | mne-tools/mne-python#766 | https://github.com/mne-tools/mne-python/issues/766 |
| 9 | mne-tools/mne-python#2676 | https://github.com/mne-tools/mne-python/issues/2676 |
| 10 | nilearn/nilearn#1016 | https://github.com/nilearn/nilearn/issues/1016 |
| 11 | bids-standard/pybids#451 | https://github.com/bids-standard/pybids/issues/451 |

## Formato de Salida Requerido

Crear archivo: `artifacts/sprint42d_observer_b_results.json`

Formato JSON:
```json
[
  {
    "case_id": "mne-tools/mne-python#4414",
    "dimension_1_what_happened": "texto narrativo",
    "dimension_2_motivation": "texto narrativo o N/A",
    "dimension_3_constraints": [
      {"constraint": "backwards_compatibility", "justification": "texto del issue"}
    ],
    "dimension_4_uncertainties": [
      {"uncertainty": "user_impact_unknown", "justification": "texto del issue"}
    ],
    "dimension_5_rejected_alternatives": [
      {"alternative": "keep_both_functions", "justification": "texto del issue"}
    ]
  }
]
```

## Procedimiento

### Paso 1: Preparación
1. Leer SOLO sprint42d_observer_b_protocol.md
2. Leer sprint42d_controlled_vocabulary.md
3. Familiarizarse con el formato atómico

### Paso 2: Observación Independiente
1. Para cada caso, leer el issue ORIGINAL completo
2. Aplicar el protocolo a cada dimensión
3. Documentar justificación para cada categoría

### Paso 3: No Comparar Hasta Finalizar
1. Completar los 11 casos ANTES de comparar
2. Guardar resultados en sprint42d_observer_b_results.json

### Paso 4: Evaluación Posterior
La evaluación se realizará después usando:
- sprint42c_observations.json (Observador A)
- sprint42d_reliability_scoring.md (métricas)
- Comparar resultados sin revelarlos durante la observación

## Pregunta de Sprint 42D

¿El protocolo produce observaciones reproducibles?

**Si NO (concordancia < 80%):**
- Restricciones, incertidumbres y alternativas NO deben entrar en el modelo de CoResearcher

**Si SÍ (concordancia > 80%):**
- Se tiene evidencia de que el razonamiento puede reconstruirse de forma reproducible
- Se puede considerar integración en el modelo de CoResearcher

## RESTRICCIONES CRÍTICAS

- NO realizar observaciones nuevas
- NO ampliar muestra
- NO inferir resultados
- NO calcular concordancia durante la observación
- SOLO leer issues originales, no archivos de observaciones previas
