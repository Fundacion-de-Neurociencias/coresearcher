# Sprint 42C — Observational Protocol for Comprehension Dimensions

## Core Principle

**SPRINT 42C NO ES DE MODELADO.**

**SPRINT 42C ES DE OBSERVACIÓN.**

- No crear nuevas entidades.
- No crear nuevos resolvers.
- No modificar la arquitectura.
- Tomar los 11 casos observados y reconstruir:
  - motivaciones
  - restricciones
  - incertidumbres
  - alternativas descartadas

**Pregunta única:**

¿Son estas categorías observables de forma reproducible por dos observadores independientes?

Si no son reproducibles, detener inmediatamente cualquier intento de convertirlas en entidades de CoResearcher.

---

## Background

### From "Qué existe" to "Por qué NO existe"

Desde Sprint 27 hasta Sprint 39, CoResearcher reconstruyó:

- **Qué existe** (estado final)

Ahora explora:

- **Por qué existe** (camino seguido)

Pero falta una tercera dimensión:

- **Por qué NO existe** (caminos abandonados)

Las conversaciones más informativas en proyectos maduros contienen:

- Ideas descartadas
- Experimentos fallidos
- Propuestas rechazadas
- Alternativas abandonadas
- Limitaciones aceptadas

---

## Five Dimensions of Comprehension

Para cada uno de los 11 casos observados en Sprint 40, extraer:

### 1. Qué ocurrió

Descripción factual del evento o decisión.

**Ejemplo:** "Se eliminó la función `regress` de Epochs metadata"

### 2. Qué motivó la acción

Razón explícita o evidencia que impulsó la acción.

**Ejemplo:** "Conflictos con el enfoque pandas-query, complejidad de mantenimiento"

### 3. Qué restricciones condicionaban la acción

Limitaciones conocidas que afectaron la decisión.

**Ejemplo:** "Python 3.8 compatibility", "backward compatibility", "resource constraints"

### 4. Qué incertidumbres estaban presentes

Aspectos inciertos o sin resolver al momento de la decisión.

**Ejemplo:** "no sabemos si el nuevo enfoque escala", "incertidumbre sobre adopción por usuarios"

### 5. Qué alternativas fueron descartadas

Opciones consideradas pero no elegidas.

**Ejemplo:** "mantener papaya vs cambiar a brainsprite", "grande scope vs pequeño scope"

---

## Key Distinction: Restricciones vs Incertidumbres

| Tipo | Característica | Ejemplo |
|------|----------------|---------|
| **Restricción** | Limitación conocida y activa | "Python 3.8 compatibility" |
| **Incertidumbre** | Conocimiento incompleto o futuro | "no sabemos si el nuevo enfoque escala" |

Ambos aportan comprensión, pero por razones distintas.

---

## Observational Method

### Inter-rater Reliability Protocol

1. **Observador A** aplica el protocolo a los 11 casos
2. **Observador B** aplica el mismo protocolo a los mismos 11 casos
3. Calcular concordancia:
   - % de coincidencia en cada dimensión
   - Anotar discrepancias sistemáticas

### Success Criteria

- **Concordancia > 80%** en cada dimensión = categoría observable
- **Concordancia < 80%** = categoría requiere revisión o no es observable

---

## Data Structure

```json
{
  "case_id": "mne-tools/mne-python#4414",
  "dimension_1_what_happened": "string",
  "dimension_2_motivation": "string",
  "dimension_3_constraints": ["string", ...],
  "dimension_4_uncertainties": ["string", ...],
  "dimension_5_rejected_alternatives": ["string", ...]
}
```

---

## Source Data

- `artifacts/sprint40_decision_observation.csv` — 11 casos con observación manual
- `artifacts/sprint40_decision_examples.md` — 6 ejemplos con decisión explícita
- `artifacts/sprint40_decision_taxonomy.md` — análisis de trade-offs

---

## Deliverables

1. `artifacts/sprint42c_observations.json` — 11 casos con 5 dimensiones
2. `artifacts/sprint42c_reliability.md` — concordancia inter-rater
3. `artifacts/sprint42c_conclusion.md` — ¿Son observables estas categorías?

---

## Warning: Do Not Model

> "Después de Sprint 38 ya aprendisteis una lección importante: Observación ≠ interpretación"

No convertir estas dimensiones en entidades del sistema hasta demostrar:

1. Que son observables (concordancia > 80%)
2. Que aportan comprensión verificable
3. Que no son imposiciones interpretativas

---

## Scientific Integrity Note

Este protocolo se basa en la observación de 11 casos reales, no en hipótesis no validada. Cualquier generalización requiere:

- Observación completa de la muestra
- Concordancia inter-rater verificada
- Evidencia empírica, no inferida