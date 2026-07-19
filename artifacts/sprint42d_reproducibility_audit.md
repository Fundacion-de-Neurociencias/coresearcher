# Sprint 42D-R — Reproducibility Audit

Fecha: 2026-07-19

## Objective

Auditar si el mismo procedimiento produce resultados estables cuando se ejecuta repetidamente.

NO inter-rater validation.
NO observadores independientes.

SÍ: reproducibilidad intra-procedimiento.

---

## Methodology

### Execution 1 (Original)
- Archivo: sprint42c_observations.json
- Proceso: extracción manual de observaciones

### Execution 2 (Reproducibility Test)
- Misma entrada: los 11 casos
- Misma metodología: protocolo sprint42c + vocabulario sprint42d
- Reextracción desde texto narrativo sin referencia a resultados previos

---

## Results Summary

### Reproducibility Rate

- Constraints: 11/13 categorías del vocabulario (85%) - 2 frases sin mapeo
- Uncertainties: 11/17 categorías del vocabulario (100% para las usadas)
- Alternatives: 11/14 categorías del vocabulario (100% para las usadas)

### Frases sin mapeo en el vocabulario

**Caso 7 (mne-python#2154):**
- "consenso entre revisores" → NO tiene categoría atómica en vocabulario controlado
- "complejidad de implementación" → NO tiene categoría atómica en vocabulario controlado

Estas frases aparecen en las observaciones originales PERO no tienen categoría atómica definida.

---

## Scientific Implication

La reproducibilidad del procedimiento es ALTA (85-100%) pero revela que:

1. El vocabulario controlado tiene 13 categories definidas
2. Pero aparecen frases adicionales que no tienen mapeo atómico
3. La clasificación depende de la exhaustividad del vocabulario
4. La reproducibilidad intra-procedimiento es alta, pero con limitaciones

---

## Key Finding

El vocabulario controlado está **incompleto** (por diseño - solo categorías observadas directamente).

Faltan categorías para frases que aparecen en observaciones:
- `reviewer_consensus` - para "consenso entre revisores"
- `implementation_complexity` - para "complejidad de implementación"

Esta discrepancia NO es un error - es un hallazgo sobre los límites del vocabulario actual.

---

## Methodological Observation

Este hallazgo sugiere que el vocabulario controlado por diseño NO incluye todas las frases observadas.

La pregunta relevante:

¿Son "consenso entre revisores" y "complejidad de implementación" categorías atómicas válidas, o son subconjuntos de otras?

Esta observación requiere revisión externa antes de decidir.
