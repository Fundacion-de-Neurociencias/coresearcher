# Sprint 56 — Product Focus

## Contexto

Los Sprints 43-55 han producido hallazgos metodológicos valiosos.

Sin embargo, existe riesgo de deriva epistemológica.

Coresearcher NO se está construyendo para resolver el problema filosófico de la comprensión.

Coresearcher NO se está construyendo para modelar estados mentales.

Coresearcher NO se está construyando para demostrar una teoría general de la explicación.

El objetivo es construir un producto útil, factible y validable.

---

## Reafirmación de misión

Coresearcher existe para responder preguntas que los sistemas RAG convencionales responden mal:

* ¿Por qué se tomó esta decisión?
* ¿Qué alternativas se descartaron?
* ¿Qué evidencia provocó un cambio de dirección?
* ¿Qué restricciones condicionaron el resultado?
* ¿Qué ocurrió entre el problema inicial y la solución final?

En una frase:

> Coresearcher es un sistema de reconstrucción de trayectorias de decisión científica y técnica.

No es un sistema de comprensión artificial general.

---

## Congelación inmediata de investigación abstracta

Quedan congeladas hasta nueva evidencia:

| Concepto | Estado |
|----------|--------|
| Understanding | Congelado |
| Comprehension | Congelado |
| Mental Models | Congelado |
| Intent | Congelado |
| Insight | Congelado |
| Reasoning Reconstruction | Congelado |
| Theory of Explanation | Congelado |

Pueden mantenerse en `artifacts/`.

No pueden convertirse en arquitectura.

No pueden convertirse en entidades del sistema.

No pueden convertirse en requisitos de producto.

---

## Nueva pregunta rectora

Eliminar:

```text
¿Qué es comprender?
```

Sustituir por:

```text
¿Qué información necesita un usuario
para reconstruir una trayectoria de decisión?
```

---

## Definición de éxito del producto

### Producto

> Coresearcher reduce el tiempo necesario para entender por qué un proyecto terminó donde terminó.

Esa frase contiene:

* **usuario** — cualquiera que necesite entender un proyecto
* **problema** — el tiempo que cuesta reconstruir la historia de un proyecto
* **beneficio** — reducción de ese tiempo

No vende información.

Vende reducción de coste cognitivo.

### Validación

#### Test brutal

Dar a dos grupos la misma tarea:

**Grupo A**: lee README, documentación, últimos commits.

**Grupo B**: lee lo mismo más el Trajectory Report.

Después preguntar:

* ¿Cuál era el problema original?
* ¿Qué alternativas se discutieron?
* ¿Por qué se eligió esta solución?
* ¿Qué limitaciones condicionaron el diseño?
* ¿Qué preguntas siguen abiertas?

Si el Grupo B no supera claramente al Grupo A: Coresearcher no está resolviendo nada.

Si el Grupo B sí lo supera: ya hay evidencia de valor.

---

## Salida del producto

Un usuario selecciona un repositorio y obtiene un Trajectory Report con:

### Problema

¿Qué intentaban resolver?

### Alternativas

¿Qué opciones aparecen documentadas?

### Selección

¿Qué opción fue elegida?

### Justificación

¿Qué evidencia o criterio aparece asociado a la elección?

### Cronología

¿Cómo evolucionó la trayectoria?

### Vacíos

¿Qué partes de la trayectoria no son recuperables?
>>>>>>>


---

## Cambio de estrategia

### Hasta Sprint 55

Investigación orientada a teoría.

### Desde Sprint 56

Investigación orientada a producto.

Toda pregunta nueva deberá responder:

1. **¿Qué funcionalidad habilita?**
2. **¿Cómo se implementaría?**
3. **¿Cómo se valida?**
4. **¿Qué usuario la necesita?**
5. **¿Qué problema resuelve?**

Si no puede responderse, la pregunta pasa a `artifacts/` y no bloquea desarrollo.

---

## MVP propuesto

### Coresearcher v0.1

**Entrada:**

* GitHub repository
* Paper
* Issues
* Pull Requests
* Commits

**Salida:**

Trajectory Report

**Secciones:**

1. **Timeline** — eventos cronológicos clave
2. **Key Decisions** — decisiones documentadas
3. **Alternatives Mentioned** — alternativas explícitas
4. **Selection Criteria** — criterios asociados a decisiones
5. **Evidence Used** — evidencia citada o documentada
6. **Unresolved Questions** — preguntas sin respuesta
7. **Information Gaps** — vacíos en la trayectoria

Sin inferir comprensión.

Sin inferir intención.

Sin inferir estados mentales.

Solo observables.

---

## Métrica principal

Eliminar:

```text
¿Comprende el proyecto?
```

Sustituir por:

```text
¿Reconstruye más trayectoria que un RAG convencional?
```

### Métricas operativas

| Métrica | Descripción | Fuente |
|---------|-------------|--------|
| Decisiones recuperadas | Número de decisiones identificadas | Issues, PRs, commits |
| Alternativas recuperadas | Número de alternativas documentadas | Threads, comentarios |
| Criterios recuperados | Número de criterios asociados a decisiones | Comentarios, reviews |
| Evidencia recuperada | Número de pruebas/datos citados | Comentarios, papers |
| Vacíos identificados | Número de lagunas en la cronología | Análisis de gaps |

### Comparación directa

| Sistema | Decisiones | Alternativas | Criterios | Evidencia | Vacíos |
|---------|-----------|-------------|-----------|-----------|--------|
| RAG baseline | ? | ? | ? | ? | ? |
| Coresearcher v0.1 | ? | ? | ? | ? | ? |

---

## Regla fundacional

> Si una línea de investigación no acerca a Coresearcher a generar mejores Trajectory Reports, queda fuera del roadmap principal.

Artifacts pueden seguir explorándola.

El producto no.

---

## Qué se lleva del Sprint 55

El diseño experimental de Sprint 55 (5 niveles A-E, métrica de capacidad predictiva) no se ejecuta como experimento teórico.

Se reorienta como **benchmark de producto**:

| Nivel | Traducción a producto |
|-------|----------------------|
| A | Resultado final solo |
| B | + alternativas mencionadas |
| C | + alternativas descartadas |
| D | + justificación superficial |
| E | + justificación con criterios específicos |

La pregunta deja de ser:

```text
¿La justificación específica produce mayor capacidad predictiva?
```

y pasa a ser:

```text
¿Coresearcher v0.1 recupera niveles D y E
con frecuencia mayor que un RAG baseline?
```

Esto mantiene el diseño experimental pero lo ancla a una funcionalidad medible.

---

## Qué se deja en artifacts/

Estos documentos permanecen como investigación teórica pero NO bloquean el roadmap:

* `sprint49_explanatory_gain_audit.md` — análisis de transformaciones
* `sprint50_explanatory_sufficiency_audit.md` — diseño de experimento
* `sprint52_explanatory_mechanism_audit.md` — refinamiento de hipótesis
* `sprint53_justification_audit.md` — taxonomía de mecanismos
* `sprint54_explanatory_gain_per_mechanism.md` — evaluación por mecanismo
* `sprint55_justification_quality_audit.md` — diseño 5 niveles

Pueden servir como referencia para futuras iteraciones. No son requisitos.

---

## Roadmap Sprint 56

### Prioridad 1: Definir Trajectory Report schema

Especificar el formato de salida (JSON, markdown) con las 7 secciones.

**Criterio de éxito**: un usuario puede leer el reporte y responder las 6 preguntas de la definición de éxito.

### Prioridad 2: Implementar extracción básica

Extraer de GitHub: issues, PRs, commits, comentarios.

Identificar: menciones de alternativas, palabras clave de decisión ("decidimos", "descartamos", "cambiamos a").

**Criterio de éxito**: recupera al menos 1 decisión por repo de prueba.

### Prioridad 3: Validar contra RAG baseline

Comparar Coresearcher v0.1 contra un RAG convencional en los mismos repos.

**Criterio de éxito**: Coresearcher recupera más decisiones, alternativas y criterios que el baseline.

### Prioridad 4: Identificar vacíos

Implementar detección de lagunas cronológicas y temáticas.

**Criterio de éxito**: identifica al menos 1 vacío en cada repo de prueba.

---

## Pregunta abierta para Sprint 57

```text
¿Qué patrón de extracción
recupera más decisiones
de un repositorio GitHub
en el menor tiempo?
```

Opciones a evaluar:

* Keyword-based extraction
* Commit message analysis
* Issue/PR thread parsing
* Reviewer comment mining

Cada opción se mide contra: decisiones recuperadas / tiempo de procesamiento.

---

## Nota metodológica

Este sprint marca la transición de investigación teórica a desarrollo de producto.

Todos los artifacts anteriores (Sprint 43-55) son válidos como investigación.

A partir de ahora, toda pregunta nueva debe estar anclada a una funcionalidad del Trajectory Report.

La pregunta "¿qué es la comprensión?" se cierra.

La pregunta "¿qué información necesita un usuario para reconstruir una trayectoria?" abre el roadmap.
