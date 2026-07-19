# Sprint 42D — Observer B Protocol

## Protocol for Independent Observer B

Este protocolo define exactamente cómo debe trabajar el Observador B para validar la fiabilidad inter-observador.

## Reglas ESTRICTAS

1. **NO puede leer observaciones previas**
   - Prohibido: artifacts/sprint42c_observations.json
   - Prohibido: artifacts/sprint42d_atomic_observation_schema.md
   - Prohibido: cualquier archivo con observaciones previas

2. **Solo puede leer el issue original**
   - Debe acceder directamente a los issues de GitHub referenciados
   - Los issues son: mne-python#4414, mne-python#3728, nilearn#2019, nilearn#1766, pybids#356, pybids#369, mne-python#2154, mne-python#766, mne-python#2676, nilearn#1016, pybids#451

3. **Debe usar el vocabulario controlado**
   - Solo categorías definidas en sprint42d_controlled_vocabulary.md
   - NO inventar nuevas categorías
   - Si no encuentra una coincidencia exacta, usar la más cercana o documentar el desvío

4. **Debe justificar cada selección**
   - Cada categoría elegida debe tener una justificación basada en evidencia textual del issue
   - Formato: "Seleccioné X porque el issue contiene la frase Y"

## Procedimiento Obligatorio

### Paso 1: Lectura del Issue
- Leer COMPLETO el issue original
- Identificar discusiones relevantes sobre restricciones, incertidumbres, alternativas

### Paso 2: Aplicación de Dimensiones
Para cada caso, extraer:

#### Dimensión 1: Qué ocurrió
- Texto narrativo del evento o decisión
- Máximo 1 oración factual

#### Dimensión 2: Motivación
- Razón explícita o evidencia que impulsó la acción
- Si no hay decisión explícita: "N/A - no hubo decisión explícita"

#### Dimensión 3: Restricciones
- Lista de objetos atómicos usando el formato: {"constraint": "nombre_categoria"}
- Cada restricción debe estar justificada con evidencia del issue

#### Dimensión 4: Incertidumbres
- Lista de objetos atómicos usando el formato: {"uncertainty": "nombre_categoria"}
- Cada incertidumbre debe estar justificada con evidencia del issue

#### Dimensión 5: Alternativas descartadas
- Lista de objetos atómicos usando el formato: {"alternative": "nombre_categoria"}
- Cada alternativa debe estar justificada con evidencia del issue

### Paso 3: Justificación Documentada
Para cada selección, agregar campo "justification" que indique:
- Texto textual del issue que soporta la categoría
- Timestamp o comentario específico si es relevante

## Formato de Salida

`json
{
  "case_id": "proyecto/numero",
  "dimension_1_what_happened": "texto narrativo",
  "dimension_2_motivation": "texto narrativo o N/A",
  "dimension_3_constraints": [
    {"constraint": "categoria", "justification": "texto evidencia"}
  ],
  "dimension_4_uncertainties": [
    {"uncertainty": "categoria", "justification": "texto evidencia"}
  ],
  "dimension_5_rejected_alternatives": [
    {"alternative": "categoria", "justification": "texto evidencia"}
  ]
}
`

## Advertencias

- Si hay dudas sobre una categoría, documentar la ambigüedad
- Si el issue no contiene evidencia suficiente, usar categoría específica para "insufficient_evidence"
- No inferir información que no esté explícita en el issue
- No añadir categorías no listadas en el vocabulario controlado
