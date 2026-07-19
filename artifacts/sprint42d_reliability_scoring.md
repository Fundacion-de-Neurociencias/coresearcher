# Sprint 42D — Reliability Scoring Metrics

Definición de métricas para calcular la concordancia entre Observador A y Observador B.

## Métricas por Dimensión

Para cada una de las 5 dimensiones:
- What happened (dimensión 1)
- Motivation (dimensión 2)
- Constraints (dimensión 3)
- Uncertainties (dimensión 4)
- Alternatives (dimensión 5)

Calcular las siguientes métricas:

## Jaccard Similarity

Métrica para conjuntos de categorías (dimensiones 3, 4, 5).

**Fórmula:**
`
J(A,B) = |A ∩ B| / |A ∪ B|
`

Donde:
- A = conjunto de categorías del Observador A
- B = conjunto de categorías del Observador B

**Interpretación:**
- 1.0 = concordancia perfecta
- 0.0 = concordancia nula
- Valores entre 0.8-1.0 = aceptable

## Precision

Proporción de categorías identificadas que son correctas.

**Fórmula:**
`
Precision = |A ∩ B| / |A|
`

Donde A es el conjunto del Observador A (referencia).

## Recall

Proporción de categorías reales que fueron identificadas.

**Fórmula:**
`
Recall = |A ∩ B| / |B|
`

Donde B es el conjunto del Observador B.

## Agreement Rate

Tasa de acuerdo simple (elemento a elemento).

**Fórmula:**
`
Agreement Rate = (número de coincidencias exactas) / (número total de observaciones)
`

Para dimensiones narrativas (1 y 2): comparar por igualdad textual.
Para dimensiones categóricas (3, 4, 5): comparar conjuntos.

## Agregación de Resultados

### Por Caso
Calcular todas las métricas para cada caso individualmente.

### Por Dimensión
Calcular promedio y desviación estándar de Jaccard Similarity para cada dimensión.

### Métrica Global
Promedio ponderado de Jaccard Similarity across todas las dimensiones.

## Categorías Especiales

### N/A Responses
Cuando una dimensión tiene "N/A - no hubo decisión explícita":
- Si ambos observadores marcan N/A: acuerdo perfecto
- Si solo uno marca N/A: acuerdo parcial (documentar discrepancia)

### No Alternative Discussed
- Categoría válida cuando no se discutieron alternativas
- Aplica solo a dimensión 5

## Success Criteria (Predefinidos)

| Métrica | Valor Mínimo | Interpretación |
|---------|--------------|----------------|
| Jaccard Similarity (promedio) | 0.8 | Categorías observables |
| Jaccard Similarity < 0.8 | - | Requiere revisión |
| Precision | 0.8 | No sobre-identificación |
| Recall | 0.8 | No sub-identificación |

## NOTA IMPORTANTE

**NO calcular todavía.** Solo definir las métricas que se usarán posteriormente.

