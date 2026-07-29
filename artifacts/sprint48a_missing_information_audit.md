# Sprint 48A — Missing Information Audit

## Pregunta

> Para cada uno de los 11 casos:
> ¿Qué información sería necesaria para explicar por qué ocurrió lo que ocurrió, pero no está presente en el registro?

## Método

Sin categorías previas. Sin taxonomía. Sin vocabulario controlado. Solo observación libre.

Para cada caso: leer el hilo observado y preguntar: **si tuviera que explicar por qué pasó esto, ¿qué me falta?**

La ausencia de información también es información.

---

## Caso 1: MNE-Python #4414 — Epochs metadata (regress removal)

**Qué ocurrió**: Se eliminó `regress` por redundancia con pandas-query.

**Información presente en el registro**:
- La redundancia fue detectada por un revisor
- Hubo un intercambio que llevó a consenso ("ok then :)")
- El PR se mergeó sin `regress`

**Información ausente**:

1. **¿Quién propuso originalmente incluir `regress` y por qué?** El PR inició con `regress` incluido. El registro no dice si fue una decisión consciente o un arrastre de código previo.

2. **¿Hubo discusión previa fuera del PR?** La conversación que llevó a abrir el PR no está documentada. Puede haber Slack, email, reunión. El registro empieza con el PR ya abierto.

3. **¿Había usuarios usando `regress` en desarrollo?** La incertidumbre documentada era "impacto en usuarios existentes". Pero el registro no dice si alguien verificó eso, ni cómo.

4. **¿El autor del PR estaba de acuerdo con eliminar o cedió por presión social?** Dice "ok then :)" — puede ser acuerdo genuino o fatiga de revisión. No hay forma de distinguirlo desde el registro.

5. **¿Qué peso tuvo la relación personal entre revisor y autor?** El tono es informal, colaborativo. Eso pudo facilitar el consenso. Pero no está documentado.

**Tipo de ausencia**: Información pre-decisional, no registrada por naturaleza (conversaciones offline, estado mental).

---

## Caso 2: MNE-Python #3728 — Receptive field module

**Qué ocurrió**: Scope reduction de encoding model general a receptive field module.

**Información presente en el registro**:
- Decisión explícita: "too much to bite off in one PR"
- Alternativa: hacer PR más pequeño

**Información ausente**:

1. **¿Quién decidió el alcance inicial?** El PR empezó con alcance general. ¿Era una decisión del autor o venía de una discusión previa no registrada?

2. **¿Presión externa?** ¿Había una conferencia, deadline, o necesidad de un user que forzara entregar algo rápido? El registro no lo dice.

3. **¿Qué se perdió al reducir alcance?** El encoding model general se postergó. ¿Se retomó? ¿Hay issues posteriores? ¿O se abandonó permanentemente?

4. **¿Hubo desacuerdo no documentado?** Aparece como decisión unánime, pero el registro puede estar sesgado hacia el consenso público.

5. **¿Recursos reales del equipo?** No sabemos cuántos revisores había, cuánto tiempo podían dedicar, si había urgencia.

**Tipo de ausencia**: Contexto organizativo no documentado (recursos, presión externa, timeline).

---

## Caso 3: nilearn/nilearn #2019 — Visual reports

**Qué ocurrió**: Separación de reporting en subpaquete independiente.

**Información presente en el registro**:
- Opinión de GaelVaroquaux y jeromedockes sobre separación arquitectónica
- Restricción: mantener núcleo libre de matplotlib

**Información ausente**:

1. **¿Por qué se decidió incluir reporting en `nilearn.plotting` originalmente?** La decisión inicial de ponerlo ahí no está documentada. Puede haber sido pragmatismo inicial.

2. **¿Quién impulsó el cambio?** GaelVaroquaux es figura influyente en nilearn. ¿El cambio ocurrió porque él lo propuso, o porque había evidencia técnica? El registro sugiere lo primero, pero no lo confirma.

3. **¿Hubo usuarios afectados?** Mover código de un subpaquete a otro rompe imports. El registro no documenta si se contactó a usuarios, si hubo periodo de deprecación, o si simplemente se asumió el breaking change.

4. **¿Cuánto esfuerzo real implicaba?** Portar HTMLDocument a subpaquete separado tiene un costo. El registro no dice cuánto tiempo tomó, ni si ese esfuerzo fue considerado en la decisión.

5. **¿Alternativas reales no documentadas?** Mantener en `plotting` con import condicional de matplotlib, o extraer solo el reporting HTML. El registro solo documenta dos alternativas, pero pudieron haber más.

**Tipo de ausencia**: Racional de decisiones previas, esfuerzo real, alternativas no verbalizadas.

---

## Caso 4: nilearn/nilearn #1766 — papaya → brainsprite

**Qué ocurrió**: Sustitución de visor 3D por restricción de tamaño de notebook.

**Información presente en el registro**:
- Datos concretos: papaya ~2MB vs brainsprite ~15KB
- Notebooks de 12MB eran impracticables

**Información ausente**:

1. **¿Por qué se eligió papaya originalmente?** Era la decisión inicial. No está documentado si fue la mejor opción disponible en ese momento o simplemente la primera que funcionó.

2. **¿Quién descubrió brainsprite?** Alguien propuso la alternativa. El registro no dice cómo llegó esa opción al grupo — ¿búsqueda activa, casualidad, recomendación externa?

3. **¿Hubo pruebas comparativas completas?** El registro menciona memoria, pero no funcionalidad, compatibilidad, mantenimiento futuro. ¿Se evaluaron todos los criterios o solo el tamaño?

4. **¿Había usuarios dependiendo de papaya?** Cambiar un visor puede romper notebooks existentes. El registro no documenta discusión sobre backward compatibility.

5. **¿Costo de migración?** Portar de papaya a brainsprite requiere reescribir la integración. El registro no documenta si ese costo fue considerado o si se asumió porque el beneficio era claro.

**Tipo de ausencia**: Historia de decisiones previas, origen de alternativas, costo de migración no cuantificado.

---

## Caso 5: bids-standard/pybids #356 — Oversampling rate

**Qué ocurrió**: Implementación de ajuste dinámico de oversampling con decisión entre 3 alternativas explícitas.

**Información presente en el registro**:
- 3 alternativas explícitamente debatidas
- Criterios: UX, simplicidad, corrección técnica
- Decisión documentada

**Información ausente**:

1. **¿Qué casos de prueba se usaron?** El registro menciona eventos cortos, pero no especifica la batería de pruebas que validó la solución elegida. ¿Cuántos casos de borde?

2. **¿Hubo datos de rendimiento?** Se eligió ajuste automático. ¿Se midió overhead? ¿Hay benchmarks?

3. **¿Quién definió los criterios de evaluación?** UX, simplicidad, corrección. ¿Fueron criterios explícitos del equipo o implícitos del dominio?

4. **¿La alternativa no documentada?** El registro muestra 3 opciones. Podría haber más (cambiar spec BIDS, ignorar eventos cortos, pedir al usuario que remuestree). ¿Se consideraron y descartaron sin documentar?

5. **¿Quién tomó la decisión final?** Aparece como consenso, pero ¿hubo un maintainer que resolvió el empate técnico?

**Tipo de ausencia**: Evidencia técnica incompleta (pruebas, benchmarks), alternativas no documentadas, proceso decisional interno.

---

## Caso 6: bids-standard/pybids #369 — Grabbit removal

**Qué ocurrió**: Se eliminó dependencia grabbit portando su funcionalidad a pybids.

**Información presente en el registro**:
- Restricción: dependencia externa bloqueaba roadmap
- Alternativa: mantener vs eliminar
- Decisión: eliminar y portar

**Información ausente**:

1. **¿Qué problemas específicos causaba grabbit?** Se menciona "riesgos de roadmap" pero no hay ejemplos concretos de bugs, delays, o incompatibilidades causadas por grabbit.

2. **¿Se contactó a los mantenedores de grabbit?** Antes de decidir portar, ¿se exploró la opción de contribuir a grabbit o pedir cambios? El registro no lo documenta.

3. **¿Costo real del port?** Portar una dependencia completa requiere tiempo de desarrollo significativo. El registro no dice cuánto tomó, quién lo hizo, ni si hubo regressiones.

4. **¿Compatibilidad con fitlins y neuroscout?** Se menciona que había que mantenerla. ¿Se hicieron pruebas de integración? ¿Hay evidencia de que funcionó?

5. **¿Había desacuerdo interno?** La decisión aparece como obvia, pero eliminar una dependencia es una decisión costosa. ¿Hubo discusión no documentada?

**Tipo de ausencia**: Evidencia del problema que motivó el cambio, costo real, procesos de validación posteriores.

---

## Caso 7: MNE-Python #2154 — Epochs concatenated plots

**Qué ocurrió**: Discusión sin convergencia, issue abierto sin resolver.

**Información presente en el registro**:
- Solicitud de usuario
- Exploración técnica sin resolución

**Información ausente**:

1. **¿Por qué no se implementó?** No hay decisión explícita de abandonar. Simplemente se diluyó. ¿Falta de prioridad, complejidad técnica, falta de mantenedor interesado?

2. **¿Había recursos para implementarlo?** No sabemos si alguien del equipo central podía dedicarle tiempo, o si se esperaba un contribuidor externo.

3. **¿Existía un workaround?** Quizás los usuarios podían hacerlo con matplotlib directamente. El registro no lo menciona.

4. **¿Cuántos usuarios lo pedían?** Un solo issue no indica demanda generalizada. No se documenta si había más usuarios afectados.

5. **¿Se abandonó o se pospuso?** La diferencia entre "no ahora" y "nunca" no está en el registro.

**Tipo de ausencia**: Intención, prioridad, demanda real. La ausencia misma es informativa: la falta de decisión es una decisión implícita.

---

## Caso 8: MNE-Python #766 — tDCS GUI

**Qué ocurrió**: Solicitud de GUI sin implementación, estancamiento por recursos.

**Información presente en el registro**:
- Solicitud de feature
- La feature existía en otros tools

**Información ausente**:

1. **¿Alguien del equipo consideró que merecía la pena?** Sin defensor interno, las features raramente se implementan en proyectos open-source. El registro no muestra si alguien hizo advocacy.

2. **¿Había funding?** Una GUI requiere diseño, implementación, testing. No sabemos si había recursos asignados o se esperaba contribución voluntaria.

3. **¿Competencia con otros tools?** Se menciona que existía en otros tools. ¿Eso fue razón para no implementarlo ("ya existe") o para implementarlo ("necesitamos competir")?

4. **¿Discusiones offline?** Proyectos con reuniones periódicas pueden haber discutido esto sin dejar rastro público.

5. **¿El issue murió por inanición?** A veces los issues simplemente se olvidan. El registro no permite distinguir abandono activo de abandono pasivo.

**Tipo de ausencia**: Advocacia, recursos, competición, proceso decisional invisible.

---

## Caso 9: MNE-Python #2676 — EEGLAB reader

**Qué ocurrió**: Solicitud de lector EEGLAB, complejidad del formato bloqueó avance.

**Información presente en el registro**:
- Complejidad del formato EEGLAB documentada
- Recursos limitados

**Información ausente**:

1. **¿Hubo intento de implementación parcial?** No se documenta si alguien empezó a codificar y encontró problemas concretos, o si solo se discutió teóricamente.

2. **¿Qué variantes de EEGLAB había que soportar?** El formato tiene múltiples versiones. El registro no especifica cuáles eran críticas.

3. **¿Existía un workaround?** ¿Podían los usuarios convertir EEGLAB a otro formato? No se documenta.

4. **¿Quién decidió no priorizarlo?** No aparece una decisión explícita. El issue simplemente no progresó.

5. **¿Documentación de errores previos?** Quizás intentos anteriores de implementar el lector habían fallado, y ese conocimiento no está en el issue.

**Tipo de ausencia**: Conocimiento técnico específico no transferido, decisión implícita de abandono, historia de fracasos previos.

---

## Caso 10: nilearn/nilearn #1016 — Surface plotting

**Qué ocurrió**: Discusión sobre mejoras en surface plotting sin implementación.

**Información presente en el registro**:
- Limitaciones de librerías 3D
- Múltiples backends considerados

**Información ausente**:

1. **¿Se intentó implementar?** No hay evidencia de código, error concreto, o prototipo. La discusión se mantuvo en abstracto.

2. **¿Quién tenía el conocimiento técnico?** Surface plotting en 3D es especializado. El registro no muestra si alguien del equipo tenía la experiencia necesaria.

3. **¿Dependencias externas bloqueantes?** Mayavi, VTK, matplotlib 3D — cada backend tiene limitaciones. No se documenta si se evaluaron sistemáticamente.

4. **¿La comunidad lo pedía activamente?** Un issue con discusión técnica no implica demanda generalizada. Quizás era un problema de un usuario con un caso muy específico.

5. **¿Prioridad relativa?** nilearn tiene muchos frentes abiertos. No sabemos dónde estaba surface plotting en la lista de prioridades del equipo.

**Tipo de ausencia**: Experiencia técnica no disponible, demanda real no cuantificada, priorización invisible.

---

## Caso 11: bids-standard/pybids #451 — List metadata bug

**Qué ocurrió**: Bug reportado en list metadata, discusión de alcance sin resolución documentada.

**Información presente en el registro**:
- Bug reportado
- Alcance discutido

**Información ausente**:

1. **¿Se reprodujo el bug?** No hay confirmación de que alguien del equipo haya reproducido el comportamiento.

2. **¿Había un fix conocido?** Quizás alguien sabía cómo arreglarlo pero no tenía tiempo. O quizás nadie sabía.

3. **¿Impacto real?** El registro discute alcance pero no cuantifica usuarios afectados, severidad, o workaround disponible.

4. **¿Se resolvió después?** La ventana observada no captura el desenlace. El bug pudo haberse resuelto en un PR posterior no registrado en este hilo.

5. **¿Por qué no se priorizó?** Bugs en list metadata suenan menores. Pero sin contexto, no sabemos si era crítico para algún flujo de trabajo.

**Tipo de ausencia**: Ventana de observación incompleta, severidad no cuantificada, resolución posterior no documentada.

---

## Patrones de ausencia (sin modelado)

Al leer los 11 casos preguntando "¿qué falta?", aparecen patrones:

### Ausencia 1: Racional pre-decisional
**Casos**: 1, 2, 3, 4, 6
**Descripción**: Las decisiones que llevaron al estado inicial no están documentadas. Sabemos qué se decidió, pero no por qué se llegó a esa decisión previa.
**Relevancia**: Sin esto, no se puede evaluar si la nueva decisión es una mejora o un retroceso.

### Ausencia 2: Contexto organizativo
**Casos**: 2, 8, 9, 10
**Descripción**: Recursos disponibles, prioridades del equipo, deadlines externos, funding. Nada de eso está en los issues/PRs.
**Relevancia**: Explica por qué algo no ocurrió, que es tan importante como por qué ocurrió.

### Ausencia 3: Evidencia técnica completa
**Casos**: 4, 5, 6, 11
**Descripción**: Pruebas, benchmarks, casos de borde, criterios de evaluación. La evidencia presentada es fragmentaria.
**Relevancia**: Decisiones basadas en evidencia incompleta pueden ser correctas por azar, no por buen razonamiento.

### Ausencia 4: Alternativas no verbalizadas
**Casos**: 3, 5, 6
**Descripción**: Las alternativas documentadas son las que se discutieron. Las que nadie mencionó pero existían no están.
**Relevancia**: La comprensión de una decisión requiere saber qué se descartó, no solo qué se eligió.

### Ausencia 5: Estado mental / social
**Casos**: 1, 2, 3, 6
**Descripción**: Acuerdo genuino vs fatiga de revisión, presión social, relaciones personales, jerarquía.
**Relevancia**: El registro público tiende al consenso aparente. Lo que realmente ocurrió puede ser diferente.

### Ausencia 6: Decisión implícita
**Casos**: 7, 8, 9, 10, 11
**Descripción**: Ausencia de merge no es lo mismo que decisión de no mergear. Puede ser abandono, postergación, olvido.
**Relevancia**: El registro no distingue entre "decidimos no hacerlo" y "no decidimos hacerlo".

### Ausencia 7: Trazabilidad posterior
**Casos**: 2, 7, 11
**Descripción**: Lo que ocurrió después de la ventana observada — issues vinculados, PRs derivados, reaperturas.
**Relevancia**: Sin trazabilidad, no se sabe si la transformación fue terminal o parte de una cadena más larga.

---

## Distribución de ausencias por caso

| Caso | Pre-decisional | Contexto org. | Evidencia técnica | Alternativas no verb. | Estado social | Decisión implícita | Trazabilidad post. |
|------|:--------------:|:-------------:|:-----------------:|:--------------------:|:-------------:|:------------------:|:------------------:|
| 1    | ✅             | ❌            | ❌                | ❌                   | ✅            | ❌                 | ❌                 |
| 2    | ✅             | ✅            | ❌                | ❌                   | ✅            | ❌                 | ✅                 |
| 3    | ✅             | ❌            | ❌                | ✅                   | ✅            | ❌                 | ❌                 |
| 4    | ✅             | ❌            | ✅                | ❌                   | ❌            | ❌                 | ❌                 |
| 5    | ❌             | ❌            | ✅                | ✅                   | ❌            | ❌                 | ❌                 |
| 6    | ✅             | ❌            | ✅                | ✅                   | ✅            | ❌                 | ❌                 |
| 7    | ❌             | ✅            | ❌                | ❌                   | ❌            | ✅                 | ✅                 |
| 8    | ❌             | ✅            | ❌                | ❌                   | ❌            | ✅                 | ❌                 |
| 9    | ❌             | ✅            | ❌                | ❌                   | ❌            | ✅                 | ❌                 |
| 10   | ❌             | ✅            | ❌                | ❌                   | ❌            | ✅                 | ❌                 |
| 11   | ❌             | ❌            | ✅                | ❌                   | ❌            | ✅                 | ✅                 |

### Frecuencia

| Tipo de ausencia | Casos | Frecuencia |
|------------------|-------|------------|
| Decisión implícita | 7, 8, 9, 10, 11 | 5/11 |
| Racional pre-decisional | 1, 2, 3, 4, 6 | 5/11 |
| Contexto organizativo | 2, 8, 9, 10 | 4/11 |
| Evidencia técnica incompleta | 4, 5, 6, 11 | 4/11 |
| Estado mental / social | 1, 2, 3, 6 | 4/11 |
| Alternativas no verbalizadas | 3, 5, 6 | 3/11 |
| Trazabilidad posterior | 2, 7, 11 | 3/11 |

---

## Observaciones

### 1. La ausencia más frecuente es la decisión implícita

5/11 casos (los 5 sin merge) no se sabe si la falta de acción fue una decisión consciente o abandono pasivo. Esto es cualitativamente diferente del resto de ausencias: no es que falte un dato, es que **no hay evidencia de que ocurriera un proceso decisional**.

### 2. Los casos con merge tienen diferentes tipos de ausencia que los casos sin merge

- Casos con merge (1-6): las ausencias son principalmente **pre-decisionales** y **sociales** — información que existió pero no se registró.
- Casos sin merge (7-11): la ausencia principal es **decisión implícita** — información que quizás nunca existió.

Esto sugiere dos problemas distintos:
- Para cambios ejecutados: la información se pierde porque no se documenta.
- Para cambios no ejecutados: la información nunca llega a generarse.

### 3. Siete tipos de ausencia

No es una taxonomía. Es lo que aparece al leer los casos preguntando "¿qué falta?". Otros observadores podrían identificar tipos diferentes.

Lo relevante no es la lista, sino el patrón: **en todos los 11 casos hay información ausente que sería necesaria para explicar por qué ocurrió lo que ocurrió**. No hay ni un solo caso donde el registro sea completo.

### 4. Relación con las transformaciones de Sprint 48

Las 6 transformaciones primitivas (T1-T6) describen **lo que ocurre** entre estados. Las 7 ausencias describen **lo que falta** para explicar por qué ocurrió.

| Pregunta | Responde |
|----------|----------|
| ¿Qué transformación ocurrió? | T1-T6 (Sprint 48) |
| ¿Qué falta para entender por qué? | Ausencias (Sprint 48A) |

Una no reemplaza a la otra. Son complementarias:
- Las transformaciones son observables directamente en el registro.
- Las ausencias son inferidas de lo que el registro no contiene.

---

## Conexión con Metacheck y Sprints 45-46

Metacheck introduce una idea: **la ausencia de información también es información**.

En los 11 casos, esto se manifiesta de dos formas:

### Ausencia como señal activa
Cuando un issue no tiene resolución tras meses de discusión, esa ausencia es informativa: indica falta de prioridad, recursos, o consenso. No es un "dato faltante" — es un dato sobre el proceso.

### Ausencia como límite epistemológico
Cuando una decisión se tomó en una conversación offline (Slack, reunión), no hay forma de recuperarla desde los artefactos públicos. La ausencia no es accidental — es estructural.

La pregunta para CoResearcher es:

```
Dado que la ausencia es inevitable,
¿qué fracción de la información necesaria
es recuperable?
```

Si la respuesta es "una fracción pequeña", entonces la reconstrucción de procesos tiene un límite fundamental, y el sistema debe operar reconociendo que parte de la explicación es inherentemente inalcanzable.

---

## Implicación para la arquitectura

| Tipo de ausencia | Recuperable desde el registro | Ejemplo de lo que se pierde |
|------------------|:----------------------------:|----------------------------|
| Racional pre-decisional | ❌ Parcial | Por qué se incluyó `regress` originalmente |
| Contexto organizativo | ❌ Rara vez | Recursos, deadlines, funding |
| Evidencia técnica | ✅ A veces | Benchmarks no publicados |
| Alternativas no verb. | ❌ Casi nunca | Lo que nadie mencionó |
| Estado mental/social | ❌ Nunca | Fatiga de revisión, presión social |
| Decisión implícita | ❌ Depende | Abandono vs postergación |
| Trazabilidad posterior | ✅ Siempre | Issues vinculados, PRs derivados |

**Ratio aproximado**: de los 7 tipos de ausencia identificados, solo 2 son recuperables desde el registro público (evidencia técnica y trazabilidad posterior). Los otros 5 requieren fuentes que el sistema no tiene (conversaciones offline, estado mental, recursos).

Esto no es un problema técnico. Es un **límite fundamental** de lo que un sistema como CoResearcher puede reconstruir a partir de artefactos públicos.

---

## Resumen del Sprint 48A

### Hallazgos

1. **En los 11 casos, hay información ausente necesaria para explicar el "por qué"**. No hay ningún caso con registro completo.

2. **Aparecen 7 tipos de ausencia**, desde racional pre-decisional (5/11) hasta trazabilidad posterior (3/11).

3. **Los casos con merge y sin merge tienen perfiles de ausencia diferentes**: merge → ausencia pre-decisional y social; no-merge → ausencia de decisión implícita.

4. **Solo 2/7 tipos de ausencia son recuperables desde el registro público** (evidencia técnica y trazabilidad posterior). Los otros 5 son límites fundamentales.

### Lo que NO se ha demostrado

- Que estos 7 tipos agoten las ausencias posibles en proyectos científicos.
- Que la clasificación sea reproducible por un observador B.
- Que la ausencia recuperable sea suficiente para explicar el "por qué".

### Pregunta abierta para Sprint 49

```
Dado que ~5/7 tipos de ausencia
son estructuralmente irrecuperables,
¿qué tipo de "comprensión"
puede alcanzar un sistema
que solo ve artefactos públicos?
```

Esta pregunta no tiene respuesta en Sprint 48A. Pero es la consecuencia natural de observar lo que falta en los 11 casos.