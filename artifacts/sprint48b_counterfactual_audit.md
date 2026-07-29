# Sprint 48B — Counterfactual Audit

## Pregunta

> ¿Qué otra cosa pudo haber ocurrido y por qué NO ocurrió?

## Método

Para cada uno de los 11 casos de Sprint 40/42C:

```
Qué ocurrió
↓
¿Qué otra cosa pudo haber ocurrido?
↓
¿Por qué NO ocurrió?
```

Sin categorías previas. Sin taxonomía. Sin entidades. Solo observación del espacio de alternativas y las restricciones que hicieron que no se realizaran.

La hipótesis de fondo: comprender un artefacto no es saber que existe. Es entender por qué terminó existiendo **ese** artefacto y no otro. Esa diferencia solo aparece cuando observas restricciones, alternativas y consecuencias sobre un espacio de posibilidades, no sobre un único resultado final.

---

## Caso 1: MNE-Python #4414 — Epochs metadata (regress removal)

**Qué ocurrió**: Se eliminó `regress` del PR. El PR mergeó con pandas-query como único mecanismo.

**¿Qué otra cosa pudo haber ocurrido?**

1. **Mantener ambas funciones** (regress + pandas-query). Era la opción por defecto: el PR se abrió con ambas incluidas.
2. **Modificar regress para integrarlo con pandas-query**. En lugar de eliminar, adaptar.
3. **Deprecar regress en lugar de eliminarlo**. Mantenerlo con warning de deprecación para no romper a usuarios existentes.
4. **No mergear el PR**. Abandonar la feature de Epochs metadata por la controversia de diseño.
5. **Separar en dos PRs**: uno con pandas-query, otro con regress como alternativa.

**¿Por qué NO ocurrieron?**

- **Alternativa 1** (mantener ambas): Descartada explícitamente por el revisor: "parece que si eliminamos regress, ya convergemos, ¿no?" — la redundancia era detectable y eliminable.
- **Alternativa 2** (modificar regress): Descartada implícitamente — nadie propuso dedicar esfuerzo a adaptar una función que se solapaba con el nuevo enfoque.
- **Alternativa 3** (deprecar): No aparece en el registro. Pudo haberse considerado pero no se documentó. La cultura del proyecto parece favorecer eliminación directa sobre deprecación.
- **Alternativa 4** (no mergear): No ocurrió porque el consenso fue rápido y el autor aceptó ("ok then :)").
- **Alternativa 5** (separar en dos PRs): No aparece en el registro. El PR ya estaba abierto y la solución era simple.

**Evidencia observacional que explica por qué NO ocurrieron**: La crítica del revisor fue suficiente. No hubo desacuerdo. El autor aceptó. La decisión fue rápida y de bajo costo.

**Tipo de restricción**: Consenso rápido + redundancia detectable. No hay evidencia de restricciones más profundas.

---

## Caso 2: MNE-Python #3728 — Receptive field module

**Qué ocurrió**: Scope reduction de encoding model general a receptive field module.

**¿Qué otra cosa pudo haber ocurrido?**

1. **Implementar encoding model completo en un solo PR**. Era el plan original.
2. **Dividir en múltiples PRs paralelos** en lugar de secuenciales.
3. **No hacer nada**. Abandonar la feature por complejidad.
4. **Implementar solo una parte del encoding model** diferente al receptive field (ej. decoding, cross-validation).
5. **Esperar a tener más recursos** (más revisores, más tiempo) antes de abordar el encoding model.

**¿Por qué NO ocurrieron?**

- **Alternativa 1** (PR completo): Descartada explícitamente: "too much to bite off in one PR". La restricción era capacidad de revisión.
- **Alternativa 2** (PRs paralelos): No aparece en el registro. Requeriría coordinación entre múltiples autores.
- **Alternativa 3** (no hacer nada): Descartada implícitamente — el receptive field era valioso por sí mismo.
- **Alternativa 4** (otra parte del encoding model): No aparece en el registro. El receptive field era la parte más modular.
- **Alternativa 5** (esperar): No aparece en el registro. Sugiere que había urgencia o ventana de oportunidad.

**Evidencia observacional**: La decisión fue explícita y unánime. La restricción de capacidad de revisión es la única documentada.

**Tipo de restricción**: Capacidad de revisión (recurso humano limitado).

---

## Caso 3: nilearn/nilearn #2019 — Visual reports

**Qué ocurrió**: Separación de reporting en subpaquete independiente.

**¿Qué otra cosa pudo haber ocurrido?**

1. **Mantener reporting dentro de `nilearn.plotting`**. Era el estado inicial.
2. **Eliminar reporting completamente**. No implementar la feature.
3. **Mantener en `plotting` con import condicional de matplotlib**. Solución intermedia.
4. **Extraer solo HTMLDocument a subpaquete**, dejando el resto en plotting.
5. **Crear un paquete externo separado** (nilearn-reporting) con dependencia opcional.

**¿Por qué NO ocurrieron?**

- **Alternativa 1** (mantener): Descartada por restricción arquitectónica: matplotlib en núcleo era indeseable.
- **Alternativa 2** (eliminar): Descartada por utilidad para usuarios.
- **Alternativa 3** (import condicional): No aparece en el registro. Pudo ser técnicamente viable pero no se discutió.
- **Alternativa 4** (extracción parcial): No aparece en el registro. La decisión fue todo o nada.
- **Alternativa 5** (paquete externo): No aparece en el registro. Habría sido más costoso de mantener.

**Evidencia observacional**: La opinión de GaelVaroquaux y jeromedockes fue determinante. La restricción arquitectónica (no matplotlib en núcleo) operó como criterio principal.

**Tipo de restricción**: Arquitectónica + autoridad de mantenedores.

---

## Caso 4: nilearn/nilearn #1766 — papaya → brainsprite

**Qué ocurrió**: Sustitución de papaya por brainsprite.

**¿Qué otra cosa pudo haber ocurrido?**

1. **Mantener papaya**. Era el estado inicial. Los notebooks de 12MB eran el costo asumido.
2. **Optimizar papaya internamente** en lugar de reemplazarlo.
3. **Usar otra alternativa** diferente a brainsprite (plotly, bokeh, ipyvolume, etc.).
4. **Hacer el visor configurable** para que el usuario elija entre papaya y brainsprite.
5. **Eliminar el visor 3D completamente** y dejar solo visualización 2D.

**¿Por qué NO ocurrieron?**

- **Alternativa 1** (mantener): Descartada por métrica objetiva: 12MB vs 15KB. La evidencia era incontrovertible.
- **Alternativa 2** (optimizar): No aparece en el registro. Optimizar papaya internamente requería acceso a su código y podía no ser viable.
- **Alternativa 3** (otra alternativa): No aparece en el registro. brainsprite fue la alternativa propuesta y aceptada.
- **Alternativa 4** (configurable): No aparece en el registro. Habría duplicado el mantenimiento.
- **Alternativa 5** (eliminar): Descartada implícitamente — el visor 3D era una feature valorada.

**Evidencia observacional**: La métrica objetiva (tamaño) fue suficiente. No hubo controversia porque los datos eran claros.

**Tipo de restricción**: Técnica medible (tamaño de notebook). La más objetiva de todos los casos.

---

## Caso 5: bids-standard/pybids #356 — Oversampling rate

**Qué ocurrió**: Ajuste dinámico de oversampling. Decisión entre 3 alternativas explícitas.

**¿Qué otra cosa pudo haber ocurrido?**

1. **Usuario llama ToDense manualmente**. Alternativa 1 del hilo.
2. **Auto-upsample dentro de Convolve**. Alternativa 2 — la elegida.
3. **ToDense automático en dos pasos**. Alternativa 3.
4. **Exponer el parámetro de oversampling en la API pública**. Descartado por restricción de diseño.
5. **Cambiar el spec BIDS** para manejar eventos cortos de otra forma.
6. **Ignorar el problema** y documentar la limitación para eventos cortos.
7. **Pedir al usuario que remuestree manualmente** antes de llamar a Convolve.

**¿Por qué NO ocurrieron?**

- **Alternativa 1** (manual): Descartada por UX.
- **Alternativa 3** (dos pasos): Descartada por complejidad.
- **Alternativa 4** (exponer parámetro): Descartada por restricción de diseño (no contaminar API).
- **Alternativa 5** (cambiar BIDS): No aparece en el registro. Cambiar el estándar BIDS es un proceso largo y político.
- **Alternativa 6** (ignorar): No aparece en el registro. El bug era real y afectaba a usuarios.
- **Alternativa 7** (remuestreo manual): Similar a la 1, descartada por UX.

**Evidencia observacional**: Este es el único caso con alternativas explícitamente documentadas (3). Los criterios de decisión (UX, simplicidad, corrección técnica) también están documentados.

**Tipo de restricción**: Múltiple — UX, simplicidad, corrección técnica, pureza de API.

---

## Caso 6: bids-standard/pybids #369 — Grabbit removal

**Qué ocurrió**: Eliminación de dependencia grabbit, port de funcionalidad a pybids.

**¿Qué otra cosa pudo haber ocurrido?**

1. **Mantener grabbit como dependencia externa**. Era el estado inicial.
2. **Actualizar grabbit** en lugar de portar.
3. **Contribuir a grabbit** para resolver los problemas de roadmap desde dentro.
4. **Reemplazar grabbit por otra librería** diferente.
5. **Reescribir la funcionalidad desde cero** en lugar de portar.
6. **Hacer grabbit una dependencia opcional** para quienes la necesiten.

**¿Por qué NO ocurrieron?**

- **Alternativa 1** (mantener): Descartada por pérdida de control de roadmap.
- **Alternativa 2** (actualizar): No aparece en el registro. Quizás grabbit no tenía mantenimiento activo.
- **Alternativa 3** (contribuir): No aparece en el registro. Requeriría coordinación con mantenedores externos.
- **Alternativa 4** (reemplazar): No aparece en el registro. Habría requerido evaluar alternativas.
- **Alternativa 5** (reescribir): Similar a portar pero más costoso.
- **Alternativa 6** (opcional): No aparece en el registro. Habría complicado la gestión de dependencias.

**Evidencia observacional**: La decisión aparece como obvia en el registro, pero hay poca evidencia de por qué se descartaron las alternativas. La restricción principal (control de roadmap) es cualitativa, no cuantitativa.

**Tipo de restricción**: Control de roadmap (cualitativa, basada en experiencia de mantenedores).

---

## Caso 7: MNE-Python #2154 — Epochs concatenated plots

**Qué ocurrió**: Discusión sin convergencia. Issue abierto sin resolver.

**¿Qué otra cosa pudo haber ocurrido?**

1. **Implementar la feature**. Alguien escribe el código y se mergea.
2. **Cerrar el issue explícitamente** con decisión de no implementar.
3. **Derivar a un workaround documentado** (ej. usar matplotlib directamente).
4. **Convertir en enhancement request para roadmap** con milestone asignado.
5. **Que un contribuidor externo lo implemente** como PR.

**¿Por qué NO ocurrieron?**

- **Alternativa 1** (implementar): No ocurrió porque nadie del equipo central priorizó la feature ni un contribuidor externo la tomó.
- **Alternativa 2** (cerrar): No ocurrió porque no hubo decisión explícita de abandonar.
- **Alternativa 3** (workaround): No aparece en el registro. Quizás existía pero no se documentó.
- **Alternativa 4** (milestone): No ocurrió porque nadie hizo la gestión de priorización.
- **Alternativa 5** (contribuidor externo): No ocurrió — el issue no atrajo a nadie dispuesto a implementarlo.

**Evidencia observacional**: No hay evidencia de una decisión. La ausencia de transformación es el dato. El issue simplemente se diluyó.

**Tipo de restricción**: Ausencia de decisión. No es una restricción activa sino pasiva — falta de recursos, prioridad, o interés.

---

## Caso 8: MNE-Python #766 — tDCS GUI

**Qué ocurrió**: Solicitud de GUI sin implementación. Estancamiento.

**¿Qué otra cosa pudo haber ocurrido?**

1. **Implementar la GUI**. Alguien escribe el código.
2. **Integrar con herramienta existente** en lugar de crear GUI propia.
3. **Documentar cómo usar otras herramientas** para tDCS con MNE.
4. **Cerrar el issue** con decisión de no implementar.
5. **Convertir en proyecto de Google Summer of Code** o similar.

**¿Por qué NO ocurrieron?**

- **Alternativa 1** (implementar): No ocurrió por falta de recursos. Una GUI requiere diseño, implementación, testing.
- **Alternativa 2** (integrar): No aparece en el registro. Requeriría evaluar herramientas externas.
- **Alternativa 3** (documentar): No aparece en el registro. Sería lo más fácil pero nadie lo hizo.
- **Alternativa 4** (cerrar): No ocurrió — el proyecto evita cerrar issues sin resolución.
- **Alternativa 5** (GSoC): No aparece en el registro. Sería una decisión organizativa.

**Evidencia observacional**: La feature existía en otros tools, lo que pudo ser razón para no implementarla ("ya existe") o para implementarla ("necesitamos competir"). El registro no permite distinguir.

**Tipo de restricción**: Recursos + competencia externa (no documentada explícitamente).

---

## Caso 9: MNE-Python #2676 — EEGLAB reader

**Qué ocurrió**: Solicitud de lector EEGLAB bloqueada por complejidad del formato.

**¿Qué otra cosa pudo haber ocurrido?**

1. **Implementar lector parcial** que cubra las variantes más comunes de EEGLAB.
2. **Usar una librería existente** para leer EEGLAB (ej. eeglabio.py) como dependencia.
3. **Documentar el formato EEGLAB** para que otros puedan implementarlo.
4. **Colaborar con el proyecto EEGLAB** para estandarizar el formato.
5. **Convertir EEGLAB a otro formato** (ej. FIF) como workaround documentado.

**¿Por qué NO ocurrieron?**

- **Alternativa 1** (lector parcial): No aparece en el registro. La complejidad del formato desincentivaba soluciones parciales.
- **Alternativa 2** (librería existente): No aparece en el registro. Añadiría dependencia externa.
- **Alternativa 3** (documentar): No aparece en el registro. Sería útil pero nadie lo hizo.
- **Alternativa 4** (colaborar): No aparece en el registro. Requeriría coordinación inter-proyecto.
- **Alternativa 5** (convertir): No aparece en el registro. Sería un workaround para usuarios, no una solución en MNE.

**Evidencia observacional**: La complejidad del dominio (formato EEGLAB variable) es la única restricción documentada. No hay evidencia de que se exploraran alternativas.

**Tipo de restricción**: Complejidad técnica del dominio + recursos limitados.

---

## Caso 10: nilearn/nilearn #1016 — Surface plotting

**Qué ocurrió**: Discusión sobre mejoras en surface plotting sin implementación.

**¿Qué otra cosa pudo haber ocurrido?**

1. **Implementar surface plotting con un backend específico** (Mayavi, VTK, matplotlib 3D).
2. **Hacer surface plotting configurable** para que el usuario elija backend.
3. **Documentar limitaciones** y recomendar herramientas externas.
4. **Integrar con librería especializada** (ej. pyvista, fury).
5. **Eliminar surface plotting** y dejar solo volumen.

**¿Por qué NO ocurrieron?**

- **Alternativa 1** (implementar): No ocurrió porque cada backend tenía limitaciones y nadie del equipo tenía la experiencia para resolverlas.
- **Alternativa 2** (configurable): No aparece en el registro. Multiplicaría la complejidad de mantenimiento.
- **Alternativa 3** (documentar): No aparece en el registro. Sería lo más fácil pero nadie lo priorizó.
- **Alternativa 4** (integrar): No aparece en el registro. Añadiría dependencia externa.
- **Alternativa 5** (eliminar): No aparece en el registro. La feature era solicitada por usuarios.

**Evidencia observacional**: La discusión se mantuvo en abstracto. No hay evidencia de código, prototipo, o error concreto. La restricción principal era la falta de experiencia técnica disponible.

**Tipo de restricción**: Conocimiento técnico no disponible en el equipo.

---

## Caso 11: bids-standard/pybids #451 — List metadata bug

**Qué ocurrió**: Bug reportado, discusión de alcance sin resolución documentada.

**¿Qué otra cosa pudo haber ocurrido?**

1. **Reproducir el bug y crear un fix**. Alguien escribe el parche.
2. **Cerrar como "no reproducible"** si nadie puede confirmarlo.
3. **Documentar workaround** para usuarios afectados.
4. **Derivar a un issue más general** si el bug es síntoma de un problema mayor.
5. **Asignar a un milestone** para priorizarlo.

**¿Por qué NO ocurrieron?**

- **Alternativa 1** (fix): No ocurrió porque nadie reprodujo el bug o nadie tuvo tiempo de crear el parche.
- **Alternativa 2** (cerrar): No ocurrió porque no hubo confirmación de que no fuera reproducible.
- **Alternativa 3** (workaround): No aparece en el registro.
- **Alternativa 4** (derivar): No aparece en el registro.
- **Alternativa 5** (milestone): No ocurrió — el bug no fue priorizado.

**Evidencia observacional**: La ventana de observación es incompleta. El bug pudo haberse resuelto después en un PR no vinculado a este issue.

**Tipo de restricción**: Ventana de observación limitada + falta de priorización.

---

## Patrones de contrafactuales (sin modelado)

### Patrón 1: Alternativas no documentadas
En 10/11 casos, las alternativas que NO ocurrieron no están documentadas en el registro. Solo el Caso 5 tiene alternativas explícitas. En el resto, las alternativas deben inferirse del contexto del proyecto.

**Implicación**: El espacio de alternativas no es directamente observable. Hay que reconstruirlo desde el conocimiento del dominio.

### Patrón 2: Restricciones cualitativas dominan
En 8/11 casos, las restricciones que explican por qué no ocurrieron las alternativas son cualitativas (control de roadmap, capacidad de revisión, autoridad de mantenedores), no cuantitativas. Solo el Caso 4 tiene una métrica objetiva.

**Implicación**: La mayoría de las restricciones no son medibles. Son juicios de expertos.

### Patrón 3: Ausencia de decisión como restricción
En 5/11 casos (7, 8, 9, 10, 11), la razón por la que no ocurrieron las alternativas no es una decisión activa sino la ausencia de ella. No se decidió no implementar — simplemente no se decidió.

**Implicación**: El espacio de alternativas descartadas incluye tanto decisiones activas como no-decisiones. Ambas son informativas, pero tienen naturaleza diferente.

### Patrón 4: El espacio de alternativas es más grande que lo documentado
En todos los casos, el número de alternativas plausibles (4-7 por caso) supera ampliamente las alternativas documentadas (0-3). La mayoría de las alternativas nunca se verbalizan.

**Implicación**: Reconstruir el espacio de alternativas requiere inferencia, no solo observación. Eso introduce subjetividad.

---

## Distribución de contrafactuales por caso

| Caso | Alternativas plausibles | Alternativas documentadas | Ratio doc/plaus | Restricción principal |
|------|:----------------------:|:------------------------:|:---------------:|----------------------|
| 1    | 5                      | 2                        | 0.4             | Consenso rápido |
| 2    | 5                      | 2                        | 0.4             | Capacidad de revisión |
| 3    | 5                      | 2                        | 0.4             | Arquitectura + autoridad |
| 4    | 5                      | 2                        | 0.4             | Métrica objetiva |
| 5    | 7                      | 3                        | 0.43            | Múltiple (UX, simplicidad, API) |
| 6    | 6                      | 1                        | 0.17            | Control de roadmap |
| 7    | 5                      | 0                        | 0               | Ausencia de decisión |
| 8    | 5                      | 0                        | 0               | Recursos |
| 9    | 5                      | 0                        | 0               | Complejidad técnica |
| 10   | 5                      | 0                        | 0               | Conocimiento no disponible |
| 11   | 5                      | 0                        | 0               | Ventana incompleta |

### Observaciones

1. **El ratio de documentación de alternativas es bajo**: máximo 0.43 (Caso 5), mínimo 0 (Casos 7-11). En promedio, las alternativas documentadas son aproximadamente 3 de cada 10 plausibles inferidas. Pero este ratio compara documentado contra plausible inferido, no contra el espacio real de alternativas, que es desconocido.

2. **Los casos con merge tienen mejor documentación de alternativas** (0.17-0.43) que los casos sin merge (0). Esto sugiere que cuando hay transformación, parte del espacio de alternativas se documenta incidentalmente.

3. **Las restricciones cualitativas dominan**: solo 1/11 casos tiene una restricción cuantitativa. El resto son juicios, consensos, recursos, autoridad.

---

## Lo que esto sugiere para CoResearcher

### La información más valiosa es la que no está

El espacio de alternativas no documentadas es mayor que el documentado en todos los casos. Si la comprensión requiere saber por qué se eligió una trayectoria sobre otras, el sistema necesita acceder a alternativas que **nunca se verbalizaron** en el registro público.

Esto es cualitativamente diferente de los problemas anteriores:
- Sprint 27-47: la información existía pero en otro lugar (issues en lugar de artefactos, decisiones en lugar de datos).
- Sprint 48B: la información **nunca existió** en el registro público. Las alternativas no documentadas no están en issues, ni en PRs, ni en commits.

### Corrección: la cuantificación no está respaldada

La afirmación de que un porcentaje concreto del espacio de alternativas "no está documentado" no puede respaldarse con los datos actuales. El motivo: **no conocemos el denominador**.

Lo que se ha medido es:

```
Ratio = alternativas documentadas / alternativas plausibles inferidas por el observador
```

Pero "alternativas plausibles inferidas" no es equivalente a "alternativas posibles reales". El espacio real de alternativas podría ser mayor o menor que lo que un observador externo puede inferir. Sin acceso a las conversaciones del equipo, no sabemos cuántas alternativas se consideraron realmente.

Por tanto:

- **Afirmación no respaldada**: un porcentaje específico del espacio de alternativas es irrecuperable
- **Afirmación respaldada**: "en todos los casos, las alternativas documentadas son menos que las que un observador puede inferir como plausibles"
- **Afirmación posible pero no cuantificable**: "el espacio de alternativas real podría ser significativamente mayor que el documentado"

La intuición cualitativa es plausible. La cuantificación es prematura.

### La excepción que apunta a un patrón

El Caso 5 es el único con alternativas explícitas (3 de 7 plausibles inferidas). Es también el caso con la decisión más documentada. Pero incluso ahí, las alternativas no documentadas superan a las documentadas.

Esto sugiere, cualitativamente, que la documentación de alternativas es la excepción, no la regla. Pero no permite afirmar que "solo el 20% del espacio es recuperable".

---

## Tabla de síntesis: evidencia de alternativas descartadas

| Caso | Alternativas observables | Razón observable del descarte | Razón no recuperable |
|------|--------------------------|-------------------------------|----------------------|
| 1 | 2/5 (mantener ambas, modificar regress) | Consenso rápido: revisor detecta redundancia, autor acepta | Deprecación, no-merge, separación en PRs — no documentadas |
| 2 | 2/5 (PR completo, no hacer nada) | Capacidad de revisión: "too much to bite off" | PRs paralelos, otra parte del encoding model, esperar — no documentadas |
| 3 | 2/5 (mantener, eliminar) | Arquitectura + autoridad: matplotlib en núcleo indeseable | Import condicional, extracción parcial, paquete externo — no documentadas |
| 4 | 2/5 (mantener papaya, eliminar visor) | Métrica objetiva: 12MB vs 15KB | Optimizar papaya, otra alternativa, configurable — no documentadas |
| 5 | 3/7 (manual, dos pasos, exponer parámetro) | Múltiple: UX, simplicidad, pureza de API | Cambiar BIDS, ignorar, remuestreo manual — no documentadas |
| 6 | 1/6 (mantener grabbit) | Control de roadmap: cualitativo, experiencia de mantenedores | Actualizar, contribuir, reemplazar, reescribir, opcional — no documentadas |
| 7 | 0/5 | Ausencia de decisión: el issue se diluye sin resolución | Todas las alternativas son inferencia del observador |
| 8 | 0/5 | Recursos + competencia externa: no hay evidencia de decisión activa | Todas las alternativas son inferencia del observador |
| 9 | 0/5 | Complejidad técnica del dominio: formato EEGLAB variable | Todas las alternativas son inferencia del observador |
| 10 | 0/5 | Conocimiento técnico no disponible en el equipo | Todas las alternativas son inferencia del observador |
| 11 | 0/5 | Ventana de observación incompleta + falta de priorización | Todas las alternativas son inferencia del observador |

### Observaciones sobre la tabla

1. **En los 6 casos con merge, hay al menos 1 alternativa observable y una razón documentada del descarte**. La evidencia existe, aunque es parcial.

2. **En los 5 casos sin merge, no hay alternativas observables ni razón documentada**. La razón del descarte debe inferirse del contexto del proyecto, no del registro del issue/PR.

3. **Las razones no recuperables superan a las recuperables en todos los casos**. La información que permitiría distinguir la trayectoria elegida de las no-elegidas está mayoritariamente ausente. Sin embargo, no es posible cuantificar exactamente esta proporción porque el espacio real de alternativas es desconocido.

---

## Pregunta reformulada para Sprint 49

La pregunta que emerge de Sprint 48B no es:

```
¿Qué ocurrió?
```

Ni siquiera:

```
¿Por qué ocurrió?
```

Sino:

```
¿Qué evidencia permite distinguir
la trayectoria elegida
de las trayectorias que no ocurrieron?
```

Esta pregunta conecta directamente con:
- **Sprint 27-47**: todas las falsaciones muestran que los estados finales pierden información sobre por qué se eligió esa trayectoria.
- **Sprint 48A**: la información ausente es principalmente sobre alternativas no documentadas.
- **Sprint 48B**: en todos los casos, las alternativas documentadas son menos que las que un observador puede inferir como plausibles.

La pregunta no tiene respuesta en Sprint 48B. Pero es la consecuencia directa de observar que las alternativas no verbalizadas son la norma, no la excepción.

### Implicación cualitativa para CoResearcher

Si la evidencia que permite distinguir trayectorias está mayoritariamente ausente del registro público, entonces existe un **límite cualitativo** en lo que un sistema puede reconstruir desde artefactos públicos. La proporción exacta de ese límite no puede cuantificarse con los datos actuales, pero el patrón es consistente: en todos los casos observados, la información documentada sobre alternativas descartadas es menor que la información que un observador puede inferir como plausible.

Esto no es un problema de mejor recuperación. Es un límite epistemológico: las alternativas no verbalizadas no se pueden recuperar porque nunca se registraron.

La pregunta abierta para el proyecto es si la fracción de alternativas que sí está documentada es suficiente para algún tipo de explicación útil, o si la comprensión requiere inevitablemente acceder a información que los artefactos públicos no contienen.

---

## Nota metodológica

Este inventario de contrafactuales NO afirma que las alternativas listadas sean las únicas posibles. Otro observador podría identificar alternativas diferentes. La lista refleja lo que un observador con conocimiento del dominio del proyecto puede inferir.

La diferencia entre alternativas documentadas y plausibles no es un error de documentación. Es una propiedad fundamental de cómo funcionan los proyectos: la mayoría de las opciones consideradas (consciente o inconscientemente) nunca se verbalizan.

Eso no es un bug. Es una característica del proceso de toma de decisiones en equipos humanos.