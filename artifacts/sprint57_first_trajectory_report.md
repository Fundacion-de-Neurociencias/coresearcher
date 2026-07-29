# Sprint 57 — First Working Trajectory Report

## Directiva

> No más auditorías conceptuales hasta que exista un Trajectory Report funcionando sobre un repositorio real.

El principal riesgo ya no es un error teórico.

Es un riesgo de ejecución.

---

## Principio fundacional

```text
Coresearcher no reconstruye lo que ocurrió.

Reconstruye la parte de lo ocurrido
que sigue siendo recuperable
desde evidencia pública.
```

Esa frase incorpora directamente la lección de los Sprints 43–55.

---

## Epistemic classification

Para evitar que "decisión" se convierta en la nueva "Program":

| Nivel | Estado |
|-------|--------|
| Observable | aparece literalmente en GitHub/Zenodo |
| Derivable | algoritmo explícito sobre datos observables |
| Inferido | hipótesis basada en datos observables |
| Desconocido | no recuperable desde evidencia pública |

Esta clasificación es obligatoria para todo elemento del Trajectory Report.

---

## Principios fundamentales

El objetivo original no era construir otro LangGraph + Vector DB + Ollama + infraestructura compleja.

Era:

> ¿Qué podemos reconstruir usando únicamente el registro público de la ciencia?
>>>>>>>


### Infraestructuras científicas públicas

#### GitHub

Observable gratuitamente:

* Issues, Pull Requests, Commits, Reviews, Discussions, Releases, Contributors, Timestamps

Además:

* API pública
* Sin costes de indexación propios
* Sin necesidad de instrumentación adicional

#### Zenodo

Observable gratuitamente:

* Versiones, DOI, Metadatos, Relaciones entre datasets, Software, Papers, Suplementos

Además:

* Persistencia científica
* Citable
* Abierto

### Restricción arquitectónica

> Ningún componente nuevo puede introducirse hasta demostrar que GitHub y Zenodo, por sí solos, son insuficientes para producir un Trajectory Report útil.

Esa regla protege contra construir una infraestructura enorme antes de demostrar que existe un problema real que lo requiera.

---

## Misión reescrita

> Coresearcher es un sistema que reconstruye y audita la trazabilidad explicativa disponible en repositorios científicos y técnicos públicos, identificando tanto la evidencia recuperable como los vacíos irreducibles de información.

Fíjate en la diferencia.

No dice:

```text
reconstruye la comprensión
```

ni

```text
reconstruye el razonamiento
```

ni

```text
explica completamente un proyecto
```

Dice:

```text
reconstruye la trazabilidad disponible
y señala lo que no puede reconstruirse.
```

Y añadido:

> No requiere instrumentación adicional por parte de los investigadores.
>>>>>>>


---

## Estado convergido

Después de 30 sprints de refinamiento, el proyecto ha convergido:

**Problema identificado**: Los artefactos finales (papers, commits, releases, repositorios) no explican suficientemente por qué terminaron existiendo.

**Necesidad del usuario**: Entender más rápido qué problema se intentaba resolver, qué alternativas se consideraron, qué se descartó, y por qué se eligió una trayectoria.

**Producto propuesto**: Trajectory Report.

**Métrica propuesta**: ¿Ayuda a reconstruir la trayectoria mejor que un RAG convencional?

Eso es suficiente para construir.
>>>>>>>


---

## Objetivo del Sprint 57

Generar un informe mediocre pero real.

No perfecto.

No inteligente.

No completo.

Real.

---

## Pregunta crítica

Antes de escribir una sola línea de arquitectura:

> ¿Puede un Trajectory Report útil construirse únicamente con GitHub y Zenodo?

Porque si la respuesta es NO:

Coresearcher probablemente no es viable bajo sus restricciones fundacionales.

Y es mejor descubrirlo ahora.

Si la respuesta es SÍ:

habéis encontrado algo muy valioso:

> una forma de recuperar parte de la trayectoria científica perdida usando únicamente evidencia pública, gratuita y reproducible.

---

## Entrada

Un único repositorio.

No diez.

No una muestra estadística.

Uno.

### Repositorios candidatos
>>>>>>>


| Proyecto | Ventaja | Consideración |
|----------|---------|---------------|
| LangGraph | Issues y PRs abundantes, decisiones arquitectónicas documentadas | Muy activo, mucho ruido |
| Haystack | Historia de decisiones de diseño, PRs con justificación | Documentación dispersa |
| Qdrant | Issues técnicos con alternativas explícitas | Menos PRs de arquitectura |
| Open Targets | Decisiones de roadmap documentadas | Proyecto grande, mucha documentación |

**Selección**: LangGraph (prioridad: issues y PRs con discusión explícita de alternativas).

---

## Salida mínima

```text
Trajectory Report — LangGraph

1. Timeline
2. Major Decisions
3. Alternatives Mentioned
4. Selection Criteria
5. Evidence Found
6. Missing Information
```

### Especificación de cada sección

#### 1. Timeline

Eventos cronológicos clave extraídos de:

- Releases (tags)
- PRs mergeados (título + fecha)
- Issues cerrados con resolución documentada

Formato: fecha + evento + tipo (release / decision / issue).

#### 2. Major Decisions

Decisiones identificadas por keywords en PRs y issues:

- "we decided to"
- "let's go with"
- "chose" / "opted for"
- "replaced" / "switched to"
- "removed" / "eliminated"

Cada decisión: contexto + elección + fecha.

#### 3. Alternatives Mentioned

Alternativas explícitas documentadas:

- "we could" / "we considered"
- "instead of" / "rather than"
- "option A" / "option B"

Cada alternativa: texto + decisión asociada (si la hay).

#### 4. Selection Criteria

Criterios asociados a decisiones:

- "because" / "since" / "due to"
- "for performance" / "for simplicity" / "for compatibility"
- métricas citadas (latencia, memoria, etc.)

#### 5. Evidence Found

Evidencia citada en discusiones:

- benchmarks
- pruebas
- referencias a papers
- métricas de uso

#### 6. Missing Information

Lagunas identificadas:

- periodos sin actividad documentada
- decisiones mencionadas sin justificación
- issues abiertos sin resolución

---

## Plan de ejecución

### Día 1: Extracción de datos

1. Clonar el repositorio `langchain-ai/langgraph`
2. Extraer:
   - Issues (título, cuerpo, comentarios, fecha, estado)
   - Pull Requests (título, cuerpo, comentarios, reviews, fecha, estado)
   - Commits (mensaje, fecha, hash)
   - Releases (tags, fecha)
3. Guardar como JSON estructurado.

### Día 2: Identificación de decisiones

1. Aplicar keyword patterns para identificar decisiones.
2. Extraer contexto (issue/PR padre, fecha).
3. Clasificar por tipo: arquitectura, API, dependencia, rendimiento, etc.

### Día 3: Extracción de alternativas y criterios

1. Para cada decisión, buscar alternativas mencionadas.
2. Extraer criterios de selección asociados.
3. Extraer evidencia citada.

### Día 4: Construcción del reporte

1. Generar el Trajectory Report en markdown.
2. Incluir las 6 secciones.
3. Anotar limitaciones y errores.

### Día 5: Documentación

1. Guardar el reporte en `data/trajectory_reports/langgraph_v0.1.md`.
2. Documentar el proceso en `docs/SPRiNT57_PROCESS.md`.
3. Listar limitaciones conocidas.

---

## Criterio de éxito

El Sprint 57 tiene éxito si:

1. Existe un archivo `langgraph_v0.1.md` con las 6 secciones.
2. El reporte contiene al menos 3 decisiones identificadas.
3. El reporte contiene al menos 1 alternativa documentada.
4. El reporte contiene al menos 1 criterio de selección.
5. El reporte contiene al menos 1 evidencia citada.
6. El reporte contiene al menos 1 vacío identificado.

No se requiere perfección.

Se requiere existencia.

---

## Roadmap posterior

### Sprint 58 — Auditoría de precisión

Tomar una muestra aleatoria de:

* decisiones
* alternativas
* criterios

Clasificarlas:

| Clase | Evidencia |
|-------|-----------|
| Directamente observable | explícita |
| Inferible | plausible |
| No respaldada | especulativa |

**Métrica principal**: `precision_observable`

No el número bruto extraído.

### Sprint 59 — Falsificación

Buscar repositorios donde el sistema fracase:

* pocos issues
* squash merges
* documentación pobre
* decisiones fuera de GitHub

Descubrir los límites reales.

### Sprint 60 — Zenodo

Cuando ya sepa qué tan fiable es la reconstrucción en GitHub.

Reconstruir la trayectoria conjunta GitHub + Zenodo:

```text
paper
↓
dataset
↓
software
↓
release
↓
nuevo paper
```
>>>>>>>

>>>>>>>


---

## Regla endurecida

> "Si no mejora un Trajectory Report, sale del roadmap."

Se endurece a:

> "Si no aumenta información relacional observable, sale del roadmap."

Porque el objetivo no es "mejorar la comprensión de usuarios".

Es:

> Reconstruir trazabilidad explicativa usando únicamente evidencia pública.
>>>>>>>


---

## Lo que se cierra

Este sprint cierra la fase de investigación teórica (Sprint 43-56).

Los siguientes conceptos quedan archivados en `artifacts/` y NO pueden bloquear el roadmap de producto:

* Understanding
* Comprehension
* Mental Models
* Intent
* Insight
* Reasoning Reconstruction
* Theory of Explanation
* Counterfactual Uncertainty
* Discriminación vs Explicación
* Calidad de la justificación

Pueden servir como referencia. No como requisitos.

---

## Lo que se abre

La pregunta de reconstrucción:

```text
¿Puede un sistema reconstruir
y auditar la trazabilidad
explicativa disponible
usando únicamente
evidencia pública?
```

Esa pregunta tiene:

* una métrica objetiva (`precision_observable`)
* una respuesta automática (comparar GitHub bruto vs Report)
* un límite claro (falsificación en repositorios difíciles)
* un output útil incluso si es incompleto (Information Gaps)

Ese cambio de marco es el avance más importante de los últimos diez sprints.
>>>>>>>


