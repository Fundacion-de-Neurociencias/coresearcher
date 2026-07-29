# Sprint 47 — Process Reconstruction Audit

## Pregunta

> ¿Qué partes del pipeline preservan información sobre el proceso y cuáles la destruyen?

---

## Corrección metodológica (post-feedback)

Este documento contenía originalmente dos afirmaciones que iban por delante de la evidencia:

1. **"State ≠ Process" como principio** — La evidencia solo muestra que *los estados finales pierden información explicativa*, no que "la comprensión reside en los procesos". Son afirmaciones distintas.

2. **"Critic y Revision Loop preservan proceso"** — Preservan *parte de la historia observable del cambio* (cambios, correcciones, objeciones, revisiones), no "el proceso" en sentido completo. No conservan objetivos reales, negociaciones privadas, presiones organizativas, incentivos, ni razonamiento interno.

3. **Uso de "razonamiento"** — Introduce cognición no observable. Lo observable en GitHub son cambios, revisiones, objeciones, alternativas, correcciones — es decir, transformaciones observables, no procesos mentales.

Este documento ha sido corregido para reflejar solo lo que la evidencia respalda.

---

## Tabla: Conservación de información por componente

| Componente | Conserva información explicativa adicional respecto al estado aislado | Conserva estado | Mecanismo de pérdida |
|------------|:---------------------------------------------------------------------:|:---------------:|----------------------|
| **Documents** | ❌ | ✅ | El documento es un *output* congelado. Las alternativas descartadas, las restricciones que moldearon su contenido, las objeciones durante su creación — todo eso queda fuera del artefacto. |
| **Vector DB** | ❌ | ✅ | Los embeddings capturan similitud semántica entre estados textuales. No hay rastro de *cómo* se llegó a esos textos. La distancia coseno mide proximidad de producto, no de trayectoria. |
| **Retrieval** | ❌ | ✅ | La recuperación selecciona fragmentos de estado por relevancia semántica. No distingue entre un hallazgo replicado 50 veces y uno que surgió de un único experimento crucial. |
| **Planner** | Parcial | Parcial | El plan contiene una secuencia de pasos prevista, que es una forma de trayectoria *proyectada*. Pero el plan no registra por qué se eligió esa secuencia sobre otras alternativas. |
| **Critic** | Trazas explícitas de revisión | Parcial | La crítica señala lagunas, inconsistencia lógica, evidencia faltante. Opera sobre la calidad del contenido, no solo sobre su presencia. Pero no captura el contexto completo de por qué se produjo ese contenido. |
| **Revision Loop** | Trazas explícitas de revisión | Parcial | El bucle de revisión genera trayectoria: estado inicial → crítica → modificación → nuevo estado. Cada iteración deja trazas de qué cambió. Pero no necesariamente de *por qué* cambió en el sentido profundo. |
| **Final Answer** | ❌ | ✅ | El output final es el estado terminal. Toda la historia de revisiones, críticas, alternativas consideradas y caminos descartados se colapsa en un único punto. |

**Nota**: "Conserva historia observable del cambio" no equivale a "preserva el proceso completo". La historia observable es una fracción del proceso real, y no se ha demostrado que sea una fracción suficiente para reconstruir comprensión.

---

## Observación central

El pipeline completo puede representarse así:

```
Documents ──→ Vector DB ──→ Retrieval ──→ Planner ──→ Critic ──→ Revision Loop ──→ Final Answer
   ❌H          ❌H           ❌H           ~H          ✅H          ✅H                ❌H
   ✅S          ✅S           ✅S           ~S          ~S           ~S                ✅S
```

**Patrón**: Los componentes que conservan historia de transformaciones observables (Critic, Revision Loop) conservan más información explicativa que los componentes que preservan únicamente estados finales. El resto opera sobre *instantáneas* de estado.

**Implicación**: Si el pipeline se ejecuta una sola vez (sin bucle de revisión), la historia observable del cambio es ~0. Si se ejecuta con múltiples iteraciones de crítica y revisión, la historia se acumula en las *diferencias entre iteraciones*, no en los estados individuales.

**Caveat**: Esto no demuestra que la historia acumulada sea suficiente para explicar el "por qué". Solo muestra que hay más información disponible que en los estados aislados.

---

## Regularidad empírica acumulada (Sprints 27-47)

| Sprint | Qué se conservaba | Qué faltaba |
|--------|-------------------|-------------|
| 27 | Actividad (GitHub metadata) | Ciencia (propósito científico) |
| 30 | Artefactos (DOIs, papers) | Programa (coherencia científica) |
| 31 | Red (conexiones entre nodos) | Propósito (programa científico) |
| 39B | Información (ledger de respuestas) | Comprensión (construct validity) |
| 40 | Decisiones (trade-offs explícitos) | Coordinación (patrones sin decisión) |
| 45-46 | Resultado (output final) | Por qué (explicación del resultado) |
| 47 | Estados (artefactos finales) | Historia observable del cambio |

**Patrón emergente**: Los estados finales parecen perder información explicativa. Esto es una regularidad observable, no una hipótesis — está apoyada por 7 observaciones independientes.

**Lo que NO se ha demostrado**: Que la historia observable del cambio sea suficiente para reconstruir la información perdida. Podría ocurrir que "estado final + historia observable" siguiera siendo insuficiente.

---

## Conexión con Grant Sanderson (3Blue1Brown)

Grant Sanderson demuestra que la comprensión matemática no se transmite mediante teoremas y demostraciones formales (estados finales), sino mediante la *reconstrucción visual del proceso* que lleva a esos teoremas.

**Analogía estructural** (no evidencia):

| Dimensión | 3Blue1Brown | CoResearcher (Sprint 43-47) |
|-----------|-------------|------------------------------|
| Lo que NO funciona | Teorema → comprensión | Documento → comprensión |
| Lo que SÍ funciona | Proceso visual → intuición | ¿Historia observable del cambio? |
| Unidad de análisis | La transformación, no el resultado | La diferencia entre iteraciones, ¿no el estado? |
| Riesgo evitado | "Entender = memorizar la fórmula" | "Entender = recuperar el documento correcto" |

**Caveat**: La analogía con 3Blue1Brown es estructural, no probatoria. El hecho de que la animación de transformaciones matemáticas genere comprensión en humanos no implica que el registro de transformaciones en GitHub genere comprensión en un sistema automatizado. Son dominios distintos con mecanismos diferentes.

---

## Los dos problemas

### Problema A: Knowledge Retrieval

```
Comprender = encontrar evidencia relevante + sintetizar evidencia relevante
```

Este es el problema que resuelven los pipelines RAG actuales. Asume que:

1. La evidencia relevante existe en documentos
2. La síntesis de esa evidencia produce comprensión
3. Más documentos → más evidencia → más comprensión

**Estado**: Falsado por Sprints 39B, 43.

### Problema B: Process Reconstruction (hipótesis)

```
Comprender = explicar por qué ocurrió algo
             y por qué no ocurrieron las alternativas posibles
```

Este es el problema hacia el que CoResearcher está convergiendo como hipótesis. Asume que:

1. La evidencia relevante está en las *transformaciones*, no solo en los estados
2. La comprensión requiere reconstruir la historia observable del cambio
3. Más trayectoria registrada → más información explicativa disponible

**Estado**: Hipótesis activa. NO ha sido falsada, pero TAMPOCO ha sido confirmada. La evidencia actual solo muestra que los estados finales pierden información, no que la historia observable sea suficiente.

### Comparación

| Dimensión | Knowledge Retrieval | Process Reconstruction |
|-----------|-------------------|----------------------|
| Unidad de análisis | Documento / Fragmento | Transformación / Diferencia |
| Fuente de información | Estado textual | Trayectoria entre estados |
| Mecanismo | Búsqueda semántica + síntesis | Trazado de historia observable del cambio |
| Riesgo principal | Confundir correlación con explicación | Confundir historia observable con proceso completo |
| Validado | ❌ Falsado | ⚠️ Hipótesis no falsada, no confirmada |
| Pipeline típico | RAG, Search-Augmented Generation | Revision Loop, Critic, Difference Tracking |

---

## Riesgo actual del proyecto

> **Más documentos → más comprensión**

Esta hipótesis ha sido falsada sistemáticamente (Sprints 27, 30, 31, 39B, 40). Sin embargo, el riesgo de recaer en ella es permanente porque:

1. **Es intuitiva**: "Si el agente lee más papers, entenderá mejor el problema" suena razonable.
2. **Es fácil de implementar**: Aumentar el corpus de documentos es trivial. Reconstruir trayectorias no.
3. **Es difícil de falsar en el corto plazo**: Una mejora marginal en recuperación puede confundirse con una mejora en comprensión.
4. **Está incrustada en la arquitectura actual**: Documents → Vector DB → Retrieval es el camino de menor resistencia.

**Nuevo riesgo**: Que "Process Reconstruction" se convierta en una nueva entidad mágica, como lo fueron Program, Decision, Understanding. La hipótesis es prometedora precisamente porque no ha sido falsada — pero eso no la convierte en un hallazgo.

---

## Hipótesis activa (no principio)

### Los estados finales pierden información explicativa

**Enunciado**: La información necesaria para explicar por qué existe un artefacto no está completamente contenida en el artefacto mismo. Parte de esa información reside en la historia observable de cambios que lo generaron.

**Corolario 1 (hipotético)**: Un sistema que solo opera sobre estados (Documents, Vector DB, Retrieval, Final Answer) podría estar perdiendo información explicativa disponible en las trayectorias entre estados.

**Corolario 2 (hipotético)**: Un sistema que opera sobre trayectorias (Critic, Revision Loop, Difference Tracking) podría, en principio, acceder a parte de esa información perdida.

**Corolario 3 (hipotético)**: La cantidad de explicación alcanzable estaría limitada por la fracción de la historia del cambio que es observable y registrable, no por la cantidad de documentos disponibles.

**Caveat**: Estos corolarios son hipótesis, no principios. La evidencia actual solo respalda la afirmación base: los estados finales pierden información. No respalda que la información en las trayectorias sea suficiente para recuperar lo perdido.

---

## Mapa del pipeline actual vs. pipeline hipotético

### Pipeline actual (Knowledge Retrieval)

```
Documents ──→ Chunking ──→ Embeddings ──→ Vector DB ──→ Retrieval ──→ Synthesis ──→ Answer
   estado       estado       estado         estado        estado        estado        estado
```

**Historia observable del cambio**: ~0. Todo son transformaciones de estado a estado, sin registro de por qué ocurrió cada transformación.

### Pipeline hipotético (Process Reconstruction)

```
Raw Process Data ──→ State Extraction ──→ Difference Detection ──→ History Assembly ──→ Trajectory Reconstruction ──→ ¿Explicación?
   trayectoria         estados             diferencias              historia            trayectoria reconstruida      hipótesis
```

**Historia observable del cambio**: Depende de la granularidad de captura. Máxima si se registran todas las transformaciones. Mínima si solo se tienen los estados finales.

**Caveat**: Este pipeline es hipotético. No se ha demostrado que la "Trajectory Reconstruction" produzca explicación. Es la pregunta abierta del proyecto.

### Dónde está CoResearcher hoy

```
Raw Process Data ──→ [Sprint 27-31: estados] ──→ [Sprint 40: decisiones] ──→ [Sprint 42C: restricciones/alternativas] ──→ [Sprint 47-48: transformaciones?]
   disponible           extracción básica         decisión como proxy          observables candidatos               observación de transformaciones
```

---

## Preguntas abiertas para Sprints 48+

1. **¿La historia observable del cambio es suficiente para explicar el "por qué"?** Esta es la pregunta central. Los Sprints 27-47 muestran que los estados finales pierden información. Falta demostrar que la historia observable la recupera.

2. **¿Qué fracción de la historia del cambio es observable?** No todo el proceso deja trazas en issues/PRs. Conversaciones offline, estado mental, contexto organizativo — nada de eso está en el registro público.

3. **¿Difference tracking es suficiente?** Si la unidad de análisis es la diferencia entre estados, ¿es posible reconstruir la trayectoria a partir de diferencias? ¿O hay información que se pierde irreversiblemente incluso entre estados consecutivos?

4. **¿Cómo se distingue una justificación post-hoc de una restricción real?** Los issues y PRs contienen ambas. El Critic puede detectar inconsistencia, pero ¿puede distinguir origen?

5. **¿Cuál es el límite superior de explicación alcanzable?** Si la historia observable es una fracción del proceso real, la reconstrucción tiene un techo. ¿Dónde está?

6. **¿La reconstrucción de trayectorias es generalizable?** Lo observado en proyectos de software científico (Sprints 27-43) ¿se aplica a papers, experimentos, laboratorios?

---

## Conclusión

El pipeline actual de CoResearcher (y de cualquier sistema RAG) está diseñado para **Knowledge Retrieval**: encontrar y sintetizar estados. La evidencia acumulada en Sprints 27-47 muestra que **los estados finales pierden información explicativa**.

La hipótesis de **Process Reconstruction** propone que la información perdida podría recuperarse parcialmente de la historia observable del cambio (diferencias entre iteraciones, correcciones, objeciones, alternativas documentadas).

Esta hipótesis es prometedora precisamente porque:
- No contradice ninguna de las 7 falsaciones previas
- Está alineada con la regularidad empírica emergente
- Propone una unidad de análisis (la transformación) diferente a las entidades ya falsadas (Program, Decision, Understanding como contenido)

Pero sigue siendo una hipótesis. No un hallazgo. No un principio. No una restricción arquitectónica.

El mayor riesgo del proyecto en este punto no es ignorar esta hipótesis, sino **tratarla como si ya estuviera demostrada** y construir arquitectura sobre ella antes de tener evidencia.

---

## Referencias

- Sprint 27: GitHub Activity ≠ Scientific Activity
- Sprint 30: Artifact Similarity ≠ Program Membership
- Sprint 31: Network Similarity ≠ Program Membership
- Sprint 39B: Information Retrieval ≠ Project Comprehension
- Sprint 40: Decisions ≠ Total Coordination
- Sprint 42C: Observability of Constraints, Uncertainties, Alternatives
- Sprint 43: Los estados finales pierden información explicativa (patrón transversal)
- Sprint 45-46: El "por qué" no es recuperable desde artefactos finales
- Grant Sanderson (3Blue1Brown): Analogía estructural sobre transformaciones como unidad explicativa