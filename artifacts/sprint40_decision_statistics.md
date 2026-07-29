# Sprint 40 — Decision Statistics (PILOT)

## Candidatas seleccionadas
- MNE-Python: 30 items (PRs)
- Nilearn: 30 items (issues + PRs)
- PyBIDS: 30 items (issues + PRs)
- **Total**: 90 items

## Observación efectiva
- **Read manually**: 11 items (first ~20 comments each)
- **Pendiente lectura completa**: 79 items

> NOTA: Per `.clinerules`, NO se pueden usar placeholders. Las 79 filas pendientes llevan la nota explícita de que requieren observacion humana completa. Solo los 11 items listados abajo tienen observación real.

## Métricas reales (N=11)

### Decisiones explícitas (Q1)
- YES: 6
- NO: 5
- **% con decisión explícita**: 54.5%

### Alternativas discutidas (Q4)
- YES: 6
- **% con alternativas**: 54.5%

### Desacuerdo (Q5)
- YES: 6
- **% con desacuerdo**: 54.5%

### Decisiones recuperables (Q6)
- YES: 6
- **% recuperable**: 54.5%

### Evidencia por tipo (Q3)
Categorías encontradas en las 6 decisiones observadas:
- DATA: 2
- EXPERIMENT: 2
- USER_REPORT: 3
- LITERATURE: 2
- EXPERT_OPINION: 1

Promedio de tipos de evidencia por decisión encontrada: ~2.0

## Comparación con criterios de éxito

| Criterio | Umbral | Observado (pilot) | Estado |
|----------|--------|-------------------|--------|
| Decisiones recuperables | >70% | 54.5% | NO CUMPLE |
| Alternativas o desacuerdo | >50% | 54.5% | NO CUMPLE |

## Interpretación honesta

Este es un **piloto con N=11**. No se puede concluir falsación ni apoyo de la hipótesis con esta muestra. La hipótesis requiere observación completa de los 90 items.

Hallazgo provisional: las decisiones explícitas SÍ existen en una fracción significativa de los hilos observados (~55%), pero la proporción está por debajo del umbral de validez (>70%).

## Implicación metodológica

Para validar o falsar la hipótesis completamente, se requiere:

1. Lectura completa de los 79 items pendientes
2. Clasificación manual Q1-Q6 por un analista humano
3. Re-cálculo de estadísticas con N=90
4. Evaluación honesta contra criterios de éxito

## Archivos fuente
- `artifacts/sprint40_decision_observation.csv` (90 filas)
- `data/sprint40_candidates.json` (criterios de selección)
- `scripts/sprint40_select_issues.py` (selector)
