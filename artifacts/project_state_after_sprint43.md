# Project State After Sprint 43

## Estado actual

### Demostrado
- Los artefactos finales no contienen suficiente información para explicar su propia existencia.
- Los procesos de desarrollo contienen información explicativa ausente en los artefactos.

### No demostrado
- Qué propiedades de esos procesos son necesarias.
- Qué propiedades son suficientes.
- Si el razonamiento es observable.
- Si la comprensión puede reconstruirse.

---

## Patrón transversal identificado: State ≠ Process

Las cinco falsaciones comparten una forma más precisa que "Correlation ≠ Explanation":

| Falsación | Estado (observable) | Proceso (perdido) |
|-----------|---------------------|-------------------|
| Sprint 27 | GitHub metadata | Scientific activity |
| Sprint 30 | Artifact similarity | Program membership |
| Sprint 31 | Network similarity | Program membership |
| Sprint 39B | Information retrieval | Comprehension |
| Sprint 40 | Decision | Total coordination |

**Observación**: Intentar reconstruir procesos a partir de estados pierde información crítica.

---

## Tabla de evidencia consolidada

| Afirmación | Estado | Evidencia |
|------------|--------|-----------|
| Los artefactos no explican su propia existencia | Fuerte | Sprint 27, 30, 31 |
| Los procesos contienen información ausente en artefactos | Moderada | Sprint 40, 40B |
| Las decisiones son parte de esa información | Moderada | Sprint 40 (6/11 casos) |
| Las decisiones son suficientes para comprender | Falsado | Sprint 40 (5/11 casos sin decisión) |
| Restricciones/incertidumbres/alternativas son observables | No validado | Sprint 42C (pendiente inter-rater) |
| Understanding = Reasoning Reconstruction | No validado | Sprint 39B, 43 |

---

## Riesgo emergente

Antes: **Program** como entidad mágica (Sprint 30-31).
Ahora: **Reasoning** como nueva entidad mágica potencial.

No hay evidencia de que issues + PRs + discusiones contengan el razonamiento necesario para comprender un proyecto. Lo único observado es que contienen más información explicativa que los artefactos finales.

---

## Pregunta principal

```text
¿Qué información explicativa se pierde
cuando un proceso queda reducido
a sus estados finales?
```

Esta pregunta es más estrecha, más observable y más falsable que "¿qué es la comprensión?". No presupone que la respuesta sea "el proceso completo" ni "el razonamiento". Podría ser una fracción muy concreta del proceso.

---

## Regla metodológica

Ningún constructo nuevo puede convertirse en entidad del sistema hasta que exista evidencia observacional de que:

1. Es identificable de forma reproducible
2. Aporta información no contenida en entidades previas
3. Mejora una tarea medible

Actualmente, Process, Reasoning, Constraint, Uncertainty y Alternative siguen siendo candidatos de investigación, no componentes arquitectónicos.

---

## Dirección recomendada

Sprint 43 no produjo nueva arquitectura. Eso es una señal de madurez metodológica. La dirección más segura es seguir reduciendo el problema a preguntas observables antes de introducir nuevas entidades o modelos cognitivos.

Próximo paso lógico: auditar si los mecanismos de razonamiento humano dejan huellas observables en los 11 casos ya documentados (Sprint 43A - Reasoning Signal Audit).
