# Sprint 48 — Transformation Inventory

## Pregunta

> ¿Qué transformaciones observables aparecen en un proyecto científico?

## Pregunta revisada tras feedback

La pregunta inicial era "qué transformaciones aparecen". El feedback de Sprint 47 refina aún más:

> **Pregunta anterior**: ¿Qué información falta?
> **Pregunta segunda**: ¿Qué operación transforma información en explicación?
> **Pregunta actual**: ¿Cuál es la mínima transformación observable que añade capacidad explicativa respecto a un estado aislado?

Porque si las transformaciones son la unidad explicativa candidata, lo relevante no es listarlas sino determinar cuál es la **más pequeña** que aporta capacidad explicativa no contenida en el estado solo.

### Implicación

No interesa construir taxonomía de transformaciones. Interesa saber:

```
A                → explicación = ?
A → B            → explicación = ?
A → crítica → B  → explicación = ?
A → B → C        → explicación = ?
```

La pregunta no es "cuántas transformaciones hay", sino "a partir de cuánta historia observable empieza a aparecer información explicativa que no está en los estados aislados".

### Regularidad empírica acumulada

| Sprint | Hallazgo |
|--------|----------|
| 27 | Actividad ≠ Ciencia |
| 30 | Artefactos ≠ Programa |
| 31 | Redes ≠ Programa |
| 39B | Retrieval ≠ Comprensión |
| 40 | Decisiones ≠ Coordinación |
| 47 | Estados ≠ Procesos (hipótesis) |

**Patrón emergente**: Encontrar información no equivale a explicar información. Esto es una regularidad empírica, no una hipótesis — está apoyada por 6 falsaciones independientes.

### Riesgo metodológico reconocido

La afirmación "Critic y Revision Loop preservan proceso" debe matizarse:

Un Revision Loop conserva errores detectados, cambios realizados, intentos sucesivos. Pero **no** conserva necesariamente motivaciones reales, contexto organizativo, conversaciones privadas, restricciones no verbalizadas, razones cognitivas profundas.

Por tanto: **Revision history ≠ Complete process**, del mismo modo que Artifact ≠ Explanation y Decision ≠ Coordination. La historia de revisiones podría ser otra aproximación parcial.

---

## Método

Sin categorías previas. Sin taxonomía. Sin entidades. Solo observación.

Para cada uno de los 11 casos de Sprint 40/42C:

```
Estado inicial
↓
Qué cambió
↓
Por qué cambió
↓
Qué fue descartado
↓
Estado final
```

Lenguaje libre. Sin modelado. Solo lo observado en los hilos reales.

La unidad de análisis no es el contenido del cambio (restricción, incertidumbre, alternativa) sino la **operación de transformación** que ocurre entre estado inicial y estado final.

---

## Caso 1: MNE-Python #4414 — Epochs metadata (regress removal)

**URL**: https://github.com/mne-tools/mne-python/pull/4414

**Estado inicial**: PR abierto que introduce Epochs metadata con función `regress` incluida.

**Qué cambió**: Se eliminó la función `regress` del PR.

**Por qué cambió**: Un revisor señaló que mantener `regress` y el enfoque pandas-query generaba redundancia y complejidad de API. Discusión: "parece que si eliminamos `regress`, ya convergemos, ¿no?" → "ok entonces :) eliminemos regress".

**Qué fue descartado**:
- Mantener ambas funciones (regress + pandas-query) — descartado por duplicación de API.
- Modificar regress para trabajar con pandas-query — descartado por complejidad.
- El enfoque general de PR grande — descartado implícitamente al converger en una solución más simple.

**Estado final**: PR mergeado sin `regress`, con Epochs metadata basado en pandas-query.

**Transformación observada**: API simplificada por detección de redundancia durante revisión.

---

## Caso 2: MNE-Python #3728 — Receptive field module

**URL**: https://github.com/mne-tools/mne-python/pull/3728

**Estado inicial**: Intención de añadir encoding models a MNE.

**Qué cambió**: Se redujo el alcance del PR de "encoding model general" a solo "receptive field module".

**Por qué cambió**: Decisión explícita: "we decided tackling the general encoding model problem is probably too much to bite off in one PR". Miedo comprensible a un PR inmanejable para revisión.

**Qué fue descartado**:
- Implementar encoding model completo en un solo PR — descartado por tamaño/riesgo.
- Dividir en múltiples PRs parciales — se eligió esta ruta pero con un primer paso muy acotado.

**Estado final**: PR mergeado con módulo receptive field, encoding model general postergado.

**Transformación observada**: Scope reduction por restricción de capacidad de revisión.

---

## Caso 3: nilearn/nilearn #2019 — Visual reports

**URL**: https://github.com/nilearn/nilearn/pull/2019

**Estado inicial**: HTMLDocument y reporting dentro de `nilearn.plotting`, que importa matplotlib.

**Qué cambió**: Se movió toda la funcionalidad de reporting a un subpaquete separado `nilearn.reporting`.

**Por qué cambió**: Decisión arquitectónica explícita de mantener el núcleo libre de dependencia matplotlib. GaelVaroquaux y jeromedockes opinaron que separar concerns era mejor a largo plazo.

**Qué fue descartado**:
- Mantener reporting dentro de `nilearn.plotting` — descartado por acoplamiento con matplotlib.
- Eliminar reporting completamente — descartado por utilidad para usuarios.
- Dependencia matplotlib en núcleo — descartado por restricción arquitectónica.

**Estado final**: PR mergeado con subpaquete separado.

**Transformación observada**: Separación arquitectónica por restricción de dependencias.

---

## Caso 4: nilearn/nilearn #1766 — papaya → brainsprite

**URL**: https://github.com/nilearn/nilearn/pull/1766

**Estado inicial**: Visor 3D implementado con papaya. Notebooks de ~12MB.

**Qué cambió**: Se reemplazó papaya por brainsprite como motor de visualización 3D.

**Por qué cambió**: Datos concretos: papaya ~2MB vs brainsprite ~15KB. Los notebooks eran impracticables para el trabajo científico real. La evidencia era medible e incontrovertible.

**Qué fue descartado**:
- Mantener papaya a costa de notebooks de 12MB — descartado por insostenible.
- Optimizar papaya internamente — descartado implícitamente (sin intento).

**Estado final**: PR mergeado con brainsprite. Notebooks ahora viables.

**Transformación observada**: Sustitución tecnológica forzada por restricción de tamaño (métrica objetiva).

---

## Caso 5: bids-standard/pybids #356 — Oversampling rate

**URL**: https://github.com/bids-standard/pybids/pull/356

**Estado inicial**: Convolve con tasa de oversampling fija.

**Qué cambió**: Se implementó ajuste dinámico de oversampling basado en duración más corta del evento.

**Por qué cambió**: Eventos cortos producían artefactos. Tres alternativas explícitamente debatidas en el hilo:
1. Usuario llama ToDense manualmente — descartado por mala UX.
2. Auto-upsample dentro de Convolve — elegido.
3. ToDense automático en dos pasos — descartado por complejidad.

**Qué fue descartado**:
- Exponer parámetro de oversampling en API pública — descartado por restricción de diseño (no contaminar API).
- Enfoque manual — descartado por UX.
- Enfoque de dos pasos — descartado por complejidad.

**Estado final**: PR mergeado con ajuste automático, API limpia.

**Transformación observada**: Decisión entre tres alternativas explícitas, resuelta por trade-off entre simplicidad de API y corrección técnica.

---

## Caso 6: bids-standard/pybids #369 — Grabbit removal

**URL**: https://github.com/bids-standard/pybids/pull/369

**Estado inicial**: pybids depende de grabbit como librería externa para layout/core.

**Qué cambió**: Se eliminó la dependencia grabbit y se portó su funcionalidad a pybids.

**Por qué cambió**: Mantener grabbit como dependencia externa creaba riesgos de roadmap. Los mantenedores querían control total sobre el core API de layout. Compatibilidad con fitlins y neuroscout requería mantener funcionalidad.

**Qué fue descartado**:
- Mantener grabbit como dependencia externa — descargado por pérdida de control de roadmap.
- Actualizar grabbit en lugar de portar — descartado implícitamente.

**Estado final**: PR mergeado. pybids ahora autónomo.

**Transformación observada**: Internalización de dependencia por restricción de control de roadmap.

---

## Caso 7: MNE-Python #2154 — Epochs concatenated plots

**URL**: https://github.com/mne-tools/mne-python/issues/2154

**Estado inicial**: Usuario solicita gráficos de epochs concatenados.

**Qué cambió**: Discusión iterativa. No hubo una decisión explícita ni merge.

**Por qué cambió**: El hilo muestra exploración de posibilidades técnicas pero sin convergencia a una solución. La discusión se diluye sin resolución.

**Qué fue descartado**: N/A — no se documentaron alternativas explícitas. La discusión nunca llegó al punto de tener que descartar opciones porque no se alineó una solución.

**Estado final**: Issue abierto, no resuelto. Sin merge.

**Transformación observada**: Exploración sin convergencia. No hubo transformación de estado del proyecto.

---

## Caso 8: MNE-Python #766 — tDCS GUI

**URL**: https://github.com/mne-tools/mne-python/issues/766

**Estado inicial**: Solicitud de GUI para estimulación transcraneal.

**Qué cambió**: Discusión de implementación. Sin decisión explícita ni merge.

**Por qué cambió**: Restricciones de recursos. La feature existía en otros tools. No hubo suficiente tracción.

**Qué fue descartado**: N/A — no se documentaron alternativas. El issue simplemente no progresó.

**Estado final**: Issue abierto, no resuelto.

**Transformación observada**: No hubo transformación. Recurso limitado → estancamiento.

---

## Caso 9: MNE-Python #2676 — EEGLAB reader

**URL**: https://github.com/mne-tools/mne-python/issues/2676

**Estado inicial**: Solicitud de lector de archivos EEGLAB.

**Qué cambió**: Discusión de implementación. Sin decisión explícita ni merge.

**Por qué cambió**: Complejidad del formato EEGLAB (múltiples variantes). Recursos limitados.

**Qué fue descartado**: N/A — no se documentaron alternativas.

**Estado final**: Issue abierto.

**Transformación observada**: No hubo transformación del proyecto. Complejidad del dominio → bloqueo.

---

## Caso 10: nilearn/nilearn #1016 — Surface plotting

**URL**: https://github.com/nilearn/nilearn/issues/1016

**Estado inicial**: Solicitud de mejoras en surface plotting.

**Qué cambió**: Discusión técnica sobre librerías 3D. Sin decisión explícita ni merge.

**Por qué cambió**: Limitaciones de librerías de plotting 3D disponibles. Múltiples backends con diferentes capacidades.

**Qué fue descartado**: N/A — no se documentaron alternativas.

**Estado final**: Issue abierto.

**Transformación observada**: No hubo transformación. Restricción técnica externa → bloqueo.

---

## Caso 11: bids-standard/pybids #451 — List metadata bug

**URL**: https://github.com/bids-standard/pybids/issues/451

**Estado inicial**: Bug reportado en list metadata.

**Qué cambió**: Reporte y discusión del bug. Sin decisión explícita ni merge documentado en el hilo observado.

**Por qué cambió**: Bug reportado. Se discutió alcance e impacto.

**Qué fue descartado**: N/A — no se documentaron alternativas en el fragmento observado.

**Estado final**: Bug reportado, estado de resolución no documentado en la ventana observada.

**Transformación observada**: Reporte de bug sin transformación observada en la ventana.

---

## Patrones crudos (sin modelado)

Lo que aparece al leer los 11 casos sin categorías previas:

### Patrón 1: Transformación por detección de redundancia
Caso 1. Alguien señala que dos cosas hacen lo mismo. El grupo elimina una.

### Patrón 2: Transformación por restricción de capacidad
Caso 2, 8, 9, 10. Algo no se hace porque requiere más recursos de los disponibles. A veces hay decisión explícita (scope reduction), a veces solo abandono silencioso.

### Patrón 3: Transformación por restricción técnica medible
Caso 4. Una métrica objetiva (tamaño del notebook) fuerza un cambio. La evidencia es incontrovertible.

### Patrón 4: Transformación por restricción arquitectónica
Caso 3, 5, 6. Restricciones de diseño (no contaminar API, no duplicar dependencias, separar concerns) fuerzan una reorganización.

### Patrón 5: No-transformación (exploración sin convergencia)
Casos 7, 8, 9, 10, 11. El hilo existe, hay discusión, pero no hay cambio de estado del proyecto. No hay merge.

### Patrón 6: Transformación por trade-off explícito
Caso 5. Tres alternativas claras, debatidas explícitamente, resueltas por criterios de simplicidad + corrección.

---

## Observaciones sobre los patrones

### Lo que NO se observó
- "Comprensión profunda del dominio"
- "Razonamiento científico completo"
- "Proceso cognitivo reconstruible"

Nada de eso aparece en los hilos. Lo que aparece son **acciones localizadas** con **justificaciones parciales**.

### Lo que SÍ se observó
- **Cambios de estado del proyecto**: merge, no-merge, scope change, dependency change.
- **Restricciones**: técnicas, de recursos, de diseño, de API.
- **Evidencia**: a veces métrica y reproducible (Caso 4), a veces opinión de experto (Caso 3), a veces ninguna.
- **Alternativas**: explícitamente documentadas solo en Caso 5. En el resto, implícitas o ausentes.

### Distribución cruda

| Tipo de transformación | Casos | Frecuencia |
|------------------------|-------|------------|
| Merge con cambio significativo | 1, 2, 3, 4, 5, 6 | 6/11 |
| Sin merge / sin cambio de estado | 7, 8, 9, 10, 11 | 5/11 |
| Alternativas explícitas documentadas | 5 | 1/11 |
| Decisión por métrica objetiva | 4 | 1/11 |
| Decisión por opinión de experto | 2, 3 | 2/11 |
| Decisión por consenso sin evidencia fuerte | 1, 6 | 2/11 |
| Estancamiento por recursos | 8, 9, 10 | 3/11 |

---

## Lo que esto sugiere para la pregunta de CoResearcher

Si observamos los 6 casos donde SÍ hubo transformación (merge):

### Información preservada en el merge (estado final)
- Qué cambió (diff del código)
- Quién cambió (autor del merge)
- Cuándo cambió (timestamp)

### Información perdida en el merge (no visible en el artefacto)
- **Por qué se eligió esa alternativa sobre otras** — visible en el hilo, no en el commit.
- **Qué alternativas se consideraron** — visible en el hilo (cuando se documentaron), invisible en el artefacto.
- **Qué evidencia pesó en la decisión** — a veces visible en el hilo, a veces no.
- **Qué restricciones operaban** — inferible del hilo, no del artefacto.
- **Qué incertidumbres quedaron sin resolver** — casi nunca visible en el merge.

### En los 5 casos sin transformación
No hay nada que perder porque no hubo cambio de estado. Pero el hilo contiene información sobre **por qué no ocurrió nada**, que también es información de proceso.

---

## Pregunta para Sprint 49

Si agrupamos los patrones observados:

```
Transformaciones observadas:
  - scope reduction (Caso 2)
  - dependency removal (Caso 1, 6)
  - architecture separation (Caso 3)
  - technology substitution (Caso 4)
  - parameter automation (Caso 5)

No-transformaciones observadas:
  - resource stall (Caso 8, 9, 10)
  - exploration without convergence (Caso 7, 11)
```

La pregunta natural es:

> ¿Estos tipos de transformación agotan lo observable
> o aparecerán otros tipos en una muestra más grande?

Pero eso requeriría más casos. Y antes de eso, la prioridad metodológica debería ser:

> ¿El observador B, aplicando el mismo método sin categorías,
> identifica las mismas transformaciones en los mismos casos?

Es decir: ¿esto es reproducible?

---

## Transformaciones primitivas emergentes

Si dejamos de buscar *contenido* (restricciones, incertidumbres, alternativas) y observamos solo *operaciones entre estados*, aparecen transformaciones que se repiten:

### T1: Alternativa → Selección
Ocurre cuando un conjunto de opciones se reduce a una. Se observa en:
- **Caso 5** (3 alternativas explícitas → 1 elegida)
- **Caso 1** (2 opciones → 1 elegida)
- **Caso 2** (scope reduction, 2 alcances → 1)

La operación de selección es observable porque las alternativas se documentan en el hilo y luego se resuelven. Pero esto solo ocurre en 3/11 casos.

### T2: Problema → Solución
Ocurre cuando un issue (un problema reportado) produce un PR (una solución). Se observa en:
- **Caso 4**: notebook grande → cambiar visor
- **Caso 5**: artefactos en eventos cortos → ajuste automático
- **Caso 3**: dependencia matplotlib en núcleo → separar subpaquete

En los casos sin transformación (7, 8, 9, 10, 11), esta operación **no ocurre**. El problema no genera solución. Eso también es información observable.

### T3: Error → Corrección
Ocurre cuando un revisor detecta un problema en un PR y se modifica antes del merge. Se observa en:
- **Caso 1**: redundancia detectada por revisor → corrección
- **Caso 4**: notebooks impracticables → sustitución de tecnología
- **Caso 5**: artefactos detectados → corrección de algoritmo

Es la operación básica del Revision Loop. El patrón es: estado A → crítica → estado B.

### T4: Incertidumbre → Confirmación
Ocurre cuando algo que no se sabía se resuelve mediante evidencia o discusión. Se observa en:
- **Caso 4**: ¿brainsprite sirve? → pruebas → confirmación
- **Caso 2**: ¿encoding model completo es viable? → se determina que no

Esta transformación es más rara y menos documentada. En muchos hilos la incertidumbre simplemente permanece.

### T5: Bloqueo → Desbloqueo
Ocurre cuando una restricción que impedía avanzar se resuelve. Se observa en:
- **Caso 6**: dependencia externa bloquea roadmap → se internaliza
- **Caso 3**: matplotlib bloquea separación → se crea subpaquete

En los casos 7-11 el bloqueo **no se desbloquea**. Eso diferencia transformación de no-transformación.

### T6: Idea → Implementación
Ocurre cuando una propuesta conceptual se convierte en código mergeado. Se observa en:
- **Caso 2**: idea de receptive field → PR mergeado
- **Caso 3**: idea de reporte visual → implementación separada
- **Caso 6**: idea de eliminar dependencia → implementación

En los casos sin merge (7-11), la idea nunca cruza el umbral de implementación.

---

### Presencia de transformaciones primitivas por caso

| Caso | T1: Alt→Sel | T2: Prob→Sol | T3: Err→Corr | T4: Inc→Conf | T5: Blq→Desbl | T6: Idea→Impl | Merge |
|------|:-----------:|:------------:|:------------:|:------------:|:-------------:|:-------------:|:----:|
| 1    | ✅          | ✅           | ✅           | ❌           | ❌            | ✅            | ✅   |
| 2    | ✅          | ✅           | ❌           | ✅           | ❌            | ✅            | ✅   |
| 3    | ❌          | ✅           | ❌           | ❌           | ✅            | ✅            | ✅   |
| 4    | ❌          | ✅           | ✅           | ✅           | ❌            | ✅            | ✅   |
| 5    | ✅          | ✅           | ✅           | ❌           | ❌            | ✅            | ✅   |
| 6    | ❌          | ✅           | ❌           | ❌           | ✅            | ✅            | ✅   |
| 7    | ❌          | ❌           | ❌           | ❌           | ❌            | ❌            | ❌   |
| 8    | ❌          | ❌           | ❌           | ❌           | ❌            | ❌            | ❌   |
| 9    | ❌          | ❌           | ❌           | ❌           | ❌            | ❌            | ❌   |
| 10   | ❌          | ❌           | ❌           | ❌           | ❌            | ❌            | ❌   |
| 11   | ❌          | ❌           | ❌           | ❌           | ❌            | ❌            | ❌   |

### Observaciones sobre la tabla

1. **Los 6 casos con merge tienen al menos T2 y T6 activas**. T2 (Problema→Solución) e T6 (Idea→Implementación) son las únicas transformaciones que aparecen en todos los casos con merge.

2. **Ninguna transformación aparece en todos los 6 casos con merge**. Cada transformación está ausente en al menos 2 casos mergeados. Esto sugiere que **no hay una transformación única necesaria** para que ocurra un cambio de estado.

3. **Las transformaciones no tienen una frecuencia homogénea**:
   - T2 y T6: 6/6 en casos con merge
   - T1: 3/6
   - T3: 3/6
   - T5: 2/6
   - T4: 2/6

4. **Los 5 casos sin merge tienen 0/6 transformaciones activas**. La ausencia de transformación es un predictor perfecto de no-cambio (en esta muestra).

---

### Lo que NO son estas transformaciones

Estas 6 operaciones NO son:

- **Entidades del sistema**: no son "components" ni "modules" que un pipeline deba implementar.
- **Categorías de contenido**: no describen lo que *contiene* un hilo, sino lo que *ocurre* en él.
- **Taxonomía cerrada**: es posible que aparezcan otras en una muestra mayor.
- **Proceso completo**: la presencia de estas transformaciones no implica que el proceso esté íntegramente capturado.

Son **operaciones observables entre estados del proyecto**. Su ventaja sobre entidades como Constraint, Uncertainty o Alternative es que:

1. **Son observables directamente** en los hilos: se puede señalar "aquí ocurrió una selección entre alternativas".
2. **Son falsables**: si un observador B no identifica la misma transformación en el mismo caso, la operación no es reproducible.
3. **No presuponen modelo cognitivo**: no requieren saber qué pensaba el desarrollador, solo qué cambió en el artefacto y qué lo precedió.

---

### Conexión con mecanismos humanos de comprensión

El feedback señalaba que cuando una persona comprende algo, utiliza mecanismos como:

| Mecanismo humano | Transformación análoga | ¿Observada en los casos? |
|-----------------|------------------------|--------------------------|
| Analogía | Estado A → Estado B por similitud con caso conocido | No observada explícitamente |
| Causalidad | Problema → Solución (T2) | ✅ 6/11 |
| Contrafactual | Alternativa descartada → Alternativa elegida (T1) | ✅ 3/11 |
| Restricción | Bloqueo → Desbloqueo (T5) | ✅ 2/11 |
| Composición | Idea → Implementación (T6) | ✅ 6/11 |
| Descomposición | (no observada como transformación unitaria) | ❌ |
| Temporalidad | Error → Corrección (T3) | ✅ 3/11 |

**Observación**: Las transformaciones análogas a mecanismos humanos aparecen exactamente en los casos donde hay merge (cambio de estado). En los casos sin merge, ningún mecanismo humano análogo se manifiesta como transformación observable.

Esto no prueba que los mecanismos humanos de comprensión estén operando. Solo muestra que ciertos patrones de cambio de estado son análogos a patrones de razonamiento humano. La diferencia es la misma que entre:
- "Encontrar que un PR contiene una decisión entre alternativas" (observación)
- "Reconstruir el razonamiento que llevó a esa decisión" (inferencia)

Sprint 48 se limita a lo primero.

---

## Nota metodológica

Este inventario NO propone categorías. Los "patrones crudos" y las "transformaciones primitivas" listadas arriba son descripciones de lo observado, no una taxonomía. La prueba de que no son categorías impuestas es que surgen directamente de los datos:

- Caso 1: "eliminar función redundante" no es "Constraint" ni "Alternative" — es una acción observada. Tampoco es "T1: Alternativa→Selección" como entidad — es una operación que se observa ocurrir en el hilo.
- Caso 5: "elegir entre 3 opciones con criterios explícitos" no es "Decision" como entidad — es una secuencia observada. Tampoco es "T1" como componente — es una transformación que se manifiesta en ese caso.

La diferencia es sutil pero crucial:
- Sprint 42C: Constraint, Uncertainty, Alternative como **categorías de contenido** → modelado.
- Sprint 48: T1-T6 como **operaciones observables** → observación previa al modelado.

El riesgo de confundir las T1-T6 con "componentes arquitectónicos" o "entidades del sistema" es el mismo que con Program, Decision, Understanding. Por ahora son solo **descripciones de lo que ocurre en los hilos**.

---

## Resumen del Sprint 48

### Hallazgos

1. **De 11 casos, 6 presentan transformaciones observables** (merge que cambia el estado del proyecto) y **5 presentan no-transformaciones** (exploración sin convergencia).

2. **En los 6 casos con transformación, aparecen al menos 2 de 6 operaciones primitivas** (T2: Problema→Solución y T6: Idea→Implementación son las únicas universales en esa muestra).

3. **En los 5 casos sin transformación, ninguna operación primitiva está activa**. La ausencia de transformación es un predictor perfecto de no-cambio.

4. **Las transformaciones observables son operaciones, no entidades**. No presuponen un modelo cognitivo. Solo describen lo que ocurre entre un estado inicial y un estado final del proyecto.

### Lo que NO se ha demostrado

- Que estas transformaciones capturen el "proceso completo" de un proyecto.
- Que sean suficientes para reconstruir comprensión.
- Que sean generalizables más allá de los 11 casos.
- Que un observador B las identifique de forma reproducible.

### Pregunta abierta para Sprint 49

La pregunta que emerge de Sprint 48 no es taxonómica (¿cuántas transformaciones hay?) sino de umbral:

```
Dado un estado aislado A
y una transformación A → B,
¿cuánta capacidad explicativa añade
conocer A → B respecto a conocer solo B?
```

Y, más específicamente:

```
¿Existe una transformación mínima
por debajo de la cual
no hay ganancia explicativa?
```

Ejemplo con los datos disponibles:

- **Caso 5**: la transformación incluye 3 alternativas explícitas + 3 criterios + decisión. Eso añade mucha capacidad explicativa respecto al merge solo.
- **Caso 1**: la transformación incluye 2 alternativas + crítica del revisor. Menos rica que Caso 5, pero más que el merge solo.
- **Caso 7**: no hay transformación. El estado final es "issue abierto". No hay ganancia explicativa porque no hubo cambio.

La pregunta real para Sprint 49 sería:

```
¿En qué punto de la secuencia
A → (crítica) → B → (crítica) → C
empieza a aparecer información
que no está en C solo?
```

Eso es más preciso que preguntar "¿qué tipos de transformación existen?".
