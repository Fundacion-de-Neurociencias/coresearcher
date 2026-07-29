# Intellectual History Hypothesis

## Prefacio

Este documento NO propone una nueva arquitectura.
NO propone un nuevo resolver.
NO propone una nueva capa.
NO inicia Sprint 40.

Es un experimento manual para determinar si la "historia intelectual" que genera comprensión existe en las fuentes que CoResearcher ya consulta.

---

## Pregunta

> ¿Puede una persona reconstruir la historia intelectual de MNE-Python usando solo issues, PRs, releases y commits?

---

## Método

1. Seleccionar los issues más comentados de MNE-Python (proxy de importancia/discusión)
2. Leer títulos, etiquetas, cuerpos y contexto de merge
3. Clasificar cada issue en una taxonomía hipotética de "historia intelectual"
4. Verificar si el contenido narrativo existe

---

## Resultados

### Fallos documentados (Failure)

| Issue | Título | Evidencia |
|-------|--------|-----------|
| #2676 | "MRG eeglab .set reader" | Primer intento. 172 comentarios. Limitado. |
| #2975 | "[MRG+1] Add eeglab event reader, **3rd try**" | **Explícitamente 3er intento.** El cuerpo dice: "EEGLAB reader is missing the ability to read events — making it basically worthless." |
| #1388 | "WIP: Implementation of cross frequency coupling" | 75 comentarios. Referencia a Canolty 2006, Tort 2010. **Nunca mergeado.** |
| #615 | "WIP: Realtime decoding" | 64 comentarios. Autor admite: *"surprised at uniformly 100% accuracies — either something wrong"*. **Nunca mergeado.** |

### Decisiones arquitectónicas (Decision)

| Issue | Evidencia |
|-------|-----------|
| #3310 "sklearn-style encoding" | Decisión explícita de adoptar API sklearn. "port the linear_regression_raw into a sklearn-friendly interface." 126 comentarios. |
| #3245 "Xdawn Transformer compatible with sklearn" | Decisión de hacer Xdawn compatible con sklearn API. |
| #4414 "MRG+4: Epochs metadata" | 4 revisores. Añadir dataframe metadata a Epochs. "decide whether we like it or not." |

### Diagnóstico honesto (Honest Assessment)

```
#615: "surprised at uniformly 100% accuracies - either something wrong with the code"
```
El autor identifica que los resultados son sospechosos. **Pensamiento científico documentado.**

### Intentos repetidos (Repeated Attempt)

```
#2676: MRG eeglab .set reader          → mergeado, funcionalidad limitada
#2975: Add eeglab event reader, 3rd try → mergeado, completa la funcionalidad
```

### Controversia (Controversy)

```
```
---

## Taxonomía propuesta (basada en datos observados)

```yaml
types:
  - id: decision
    description: Elección entre alternativas documentada
    signals: ["WIP:", "chose", "alternativ", "rather than"]
    ejemplo: "#3310 sklearn-style encoding"

  - id: failure
    description: Hipótesis que no funcionó
    signals: ["try", "unexpected", "wrong", "not work"]
    ejemplo: "#1388 cross frequency coupling (never merged)"

  - id: repeated_attempt
    description: Múltiples intentos sobre el mismo problema
    signals: ["again", "another attempt", "reopen"]
    ejemplo: "#2676 -> #2975 eeglab reader, 3rd try"

  - id: honest_problem
    description: Autor identifica anomalía
    signals: ["surprised", "something wrong"]
    ejemplo: "#615 100% accuracies, something wrong"

  - id: controversy
    description: Discusión extensa sin consenso
    signals: [">100 comments", "+N reviewers"]
    ejemplo: "#2154 303 comments on epoch plot"

  - id: pivot
    description: Cambio de dirección documentado
    signals: ["refactor", "modulariz", "restructur"]
    ejemplo: "#3310 porting to sklearn-style interface"

  - id: open_question
    description: Pregunta sin resolver
    signals: ["not sure", "need investigat", "unresolved"]
    ejemplo: "#615 'something wrong with the code'"
```

---

## Conclusión

La hipótesis queda **soportada** por los datos observados:

> La historia intelectual de MNE-Python existe en issues, PRs y metadatos asociados.

No es necesario inventar nuevas fuentes. El contenido narrativo ya está disponible. El ledger actual filtra estos datos y solo retiene metadatos de artefactos.

---

## Lo que NO se ha demostrado

1. Que extraer estas estructuras automáticamente sea factible
2. Que estas estructuras mejoren comprensión (hipótesis nueva)
3. Que la taxonomía sea completa (requiere más proyectos)

---

## Próximo paso NO técnico

Antes de codificar:

1. Repetir con Nilearn y PyBIDS
2. Verificar que la misma taxonomía aplica
3. Diseñar experimento para medir si estas estructuras mejoran comprensión
4. Solo entonces modificar el ledger generator

> Source → Observation → Learning → Impact

---

## Fuentes consultadas

| Fuente | Método | Fecha |
|--------|--------|------|
| Issues MNE-Python (top 15) | GitHub API | 2026-07-18 |
| Cuerpos de issues (7) | Lectura manual | 2026-07-18 |
| Releases MNE-Python | GitHub API | 2026-07-18 |
| PRs MNE-Python | GitHub API | 2026-07-18 |