# Sprint 55 — Justification Quality Audit

## Pregunta

> ¿La ganancia explicativa depende de la **calidad** de la justificación
> o solo de la **presencia** de alguna justificación?

Esta es una refinición de la pregunta de Sprint 54:

```text
¿La ganancia explicativa depende del tipo de mecanismo
o del hecho de que haya algún mecanismo documentado?
```

Sprint 54 confundió dos variables:

| Variable | Lo que mide | Ejemplo |
|----------|-------------|---------|
| **Presencia** | ¿Hay alguna justificación documentada? | "Se eliminó regress" |
| **Calidad** | ¿La justificación es específica o superficial? | "porque es mejor" vs "porque reduce O(n²)→O(n)" |

Dos casos pueden tener "justificación documentada" y aun así tener capacidad explicativa radicalmente distinta:

```text
Se eligió A porque es mejor.
```

vs

```text
Se eligió A porque:
- reduce complejidad O(n²)→O(n)
- elimina dependencia externa
- mantiene compatibilidad hacia atrás
```

Ambos tienen "justificación documentada". Sin embargo, su capacidad explicativa es radicalmente distinta.

---

## Contexto: la evolución Sprint 47-54

### Fase 1 (47-49) — Intento de inferir constructos

```text
Artifact → Program
Decision → Coordination
Retrieval → Comprehension
```

Fracaso sistemático. Los artefactos finales no contienen información suficiente para inferir los constructos que los produjeron.

### Fase 2 (48A-48B) — Identificación de pérdidas

```text
Resultado final
≠
Historia de cómo se llegó ahí
```

El espacio de alternativas no documentadas supera al documentado en todos los casos. Las alternativas plausibles (4-7 por caso) superan ampliamente las alternativas documentadas (0-3).

### Fase 3 (49-52) — Identificación de información explicativa

```text
Alternativas
↓
Descarte
↓
Justificación
```

Hallazgo de Sprint 49: las transformaciones que reducen el espacio de posibilidades (T1, T2, T3, T5, T7, T9) tienen ratio de ganancia 100%. T6 (Idea→Implementación) tiene ratio 0%.

Refinamiento de Sprint 52: no es la reducción en sí, sino **el criterio documentado** que la produce. Tres niveles:

| Nivel | Información | Ganancia |
|-------|-------------|----------|
| 1 | Existían alternativas | Baja |
| 2 | Fueron descartadas | Media |
| 3 | Sabemos el criterio de descarte | Alta |

### Fase 4 (53-54) — Taxonomía de mecanismos

Sprint 53 identificó 6 tipos de justificación (redundancia, capacidad, arquitectura, evidencia cuantitativa, trade-off, control de dependencias).

Sprint 54 evaluó la ganancia explicativa por mecanismo. **Hallazgo clave**: todos los mecanismos tienen ganancia alta o media-alta. El tipo de mecanismo importa menos que el hecho de que haya un mecanismo documentado.

**Pero**: Sprint 54 no distingue entre justificaciones de alta calidad (métrica objetiva: 12MB vs 15KB) y justificaciones de baja calidad ("control de roadmap", cualitativo no verificable).

---

## Hipótesis

### Hipótesis A (calidad de la justificación)

```text
Justificación específica
→
Mayor capacidad predictiva
que
Justificación superficial
```

Si se presenta la misma decisión con una justificación superficial ("porque es mejor") versus una justificación específica ("porque reduce O(n²)→O(n)"), la versión específica permitirá predecir la solución elegida significativamente mejor.

### Hipótesis B (principio más profundo)

```text
Toda explicación útil
reduce incertidumbre contrafactual.
```

Cuando leo una justificación válida, puedo responder mejor a preguntas del tipo:

```text
¿Por qué no B?
¿Por qué no C?
¿Qué habría pasado si...?
```

Si esto es cierto, entonces los mecanismos concretos (arquitectura, capacidad, trade-off, dependencia, etc.) podrían ser manifestaciones superficiales de una propiedad más profunda: **la capacidad de discriminar la trayectoria elegida de las trayectorias contrafactuales**.

#### Importante: dirección de la lógica

Lo que está respaldado es:

```text
Explicación útil
→
reduce incertidumbre contrafactual
```

**No** está demostrado todavía que:

```text
Reducir incertidumbre contrafactual
→
explicación útil
```

La segunda dirección es mucho más fuerte. Podría haber información que reduzca incertidumbre sin explicar realmente nada.

**Ejemplo**:

```text
Se eligió A porque el director lo ordenó.
```

Reduce incertidumbre. Ahora sabes por qué no ocurrió B.

Pero la explicación causal profunda puede seguir ausente. Por tanto, Sprint 56 debe intentar distinguir:

| Concepto | Pregunta |
|----------|----------|
| Discriminación | ¿Puedo distinguir A de B? |
| Explicación | ¿Sé por qué A sobrevivió? |

Podrían coincidir o no.

---

## Método

Reutilizar los 11 casos de Sprint 40/42C. Para cada caso, construir cinco niveles de información:

### Nivel A — Solo resultado

```text
Resultado: PR mergeado. Se eliminó la función `regress` de Epochs metadata.
```

Sin contexto. Sin problema. Sin alternativas. Sin justificación.

### Nivel B — Resultado + alternativas

```text
Resultado: PR mergeado. Se eliminó la función `regress` de Epochs metadata.

Alternativas consideradas:
- Mantener ambas funciones
- Modificar regress para integrarlo con pandas-query
- Deprecar regress
- No mergear el PR
```

Se documentan las alternativas, pero **no se indica cuál se descartó ni por qué**.

### Nivel C — Resultado + alternativas + descarte

```text
Resultado: PR mergeado. Se eliminó la función `regress` de Epochs metadata.

Alternativas consideradas:
- Mantener ambas funciones — descartado
- Modificar regress para integrarlo — descartado
- Eliminar regress — elegido
```

Se documenta qué se descartó, pero **no se indica el criterio del descarte**.

### Nivel D — Resultado + alternativas + descarte + justificación superficial

```text
Resultado: PR mergeado. Se eliminó la función `regress` de Epochs metadata.

Alternativas consideradas:
- Mantener ambas funciones — descartado
- Modificar regress para integrarlo — descartado
- Eliminar regress — elegido

Justificación: Se eliminó regress porque es mejor.
```

La justificación está presente pero es **vaga, circular, sin criterios concretos**. No permite distinguir por qué no se eligieron las otras alternativas.

### Nivel E — Resultado + alternativas + descarte + justificación específica

```text
Resultado: PR mergeado. Se eliminó la función `regress` de Epochs metadata.

Alternativas consideradas:
- Mantener ambas funciones — descartado por redundancia funcional
- Modificar regress para integrarlo — descartado por complejidad
- Eliminar regress — elegido

Justificación: Se eliminó regress porque:
- Redundancia funcional con pandas-query (ambas hacen lo mismo)
- Consenso rápido del revisor (bajo costo de decisión)
- No hay usuarios dependiendo de regress en desarrollo
```

La justificación es **específica, con criterios concretos, verificables, que discriminan claramente la trayectoria elegida de las contrafactuales**.

### Tarea del observador

Para cada caso, en cada nivel:

```text
Dada esta información,
¿qué solución crees que fue elegida?
```

Opciones: una lista de 3-5 alternativas plausibles (incluyendo la correcta).

### Medición

- **Acierto Nivel A**: línea base (solo resultado final)
- **Acierto Nivel B**: ganancia por añadir alternativas
- **Acierto Nivel C**: ganancia por añadir descarte
- **Acierto Nivel D**: ganancia por añadir justificación superficial
- **Acierto Nivel E**: ganancia por añadir justificación específica

La comparación clave es **D vs E**: si E produce acierto significativamente mayor que D, la calidad de la justificación es el factor determinante, no solo su presencia.

---

## Construcción de los niveles para cada caso

### Caso 1: MNE-Python #4414 — Epochs metadata (regress removal)

**Mecanismo**: Eliminación por redundancia

**Nivel A**:
```
Resultado: PR mergeado. Epochs metadata con pandas-query, sin función `regress`.
```

**Nivel B**:
```
Resultado: PR mergeado. Epochs metadata con pandas-query, sin función `regress`.

Alternativas consideradas:
- Mantener ambas funciones (regress + pandas-query)
- Modificar regress para integrarlo con pandas-query
- Deprecar regress con warning
- No mergear el PR
```

**Nivel C**:
```
Resultado: PR mergeado. Epochs metadata con pandas-query, sin función `regress`.

Alternativas consideradas:
- Mantener ambas funciones — descartado
- Modificar regress para integrarlo — descartado
- Eliminar regress — elegido
- Deprecar regress — no documentado como viable
```

**Nivel D** (justificación superficial):
```
Justificación: Se eliminó regress porque es mejor.
```

**Nivel E** (justificación específica):
```
Justificación: Se eliminó regress porque:
- Redundancia funcional: regress y pandas-query hacen lo mismo
- Consenso rápido del revisor: "parece que si eliminamos regress, ya convergemos"
- Bajo costo de eliminación: no hay usuarios dependiendo de regress
```

**Opciones para el observador**:
a) Mantener ambas funciones
b) Modificar regress para integrarlo con pandas-query
c) **Eliminar regress** ← correcta
d) Deprecar regress con warning
e) No mergear el PR

---

### Caso 2: MNE-Python #3728 — Receptive field module

**Mecanismo**: Reducción por capacidad limitada

**Nivel A**:
```
Resultado: PR mergeado. Se añadió módulo receptive field a MNE.
```

**Nivel B**:
```
Resultado: PR mergeado. Se añadió módulo receptive field a MNE.

Alternativas consideradas:
- Implementar encoding model completo en un solo PR
- Dividir en múltiples PRs parciales
- No hacer nada
- Implementar otra parte del encoding model (ej. decoding)
```

**Nivel C**:
```
Resultado: PR mergeado. Se añadió módulo receptive field a MNE.

Alternativas consideradas:
- Implementar encoding model completo — descartado
- Dividir en múltiples PRs — elegido (receptive field como primer paso)
- No hacer nada — descartado
```

**Nivel D** (justificación superficial):
```
Justificación: Se redujo el alcance porque es mejor.
```

**Nivel E** (justificación específica):
```
Justificación: Se redujo el alcance porque:
- "too much to bite off in one PR" — capacidad de revisión limitada
- receptive field es el módulo más modular del encoding model
- encoding model general se posterga a un PR futuro
```

**Opciones para el observador**:
a) **Implementar solo receptive field como primer paso** ← correcta
b) Implementar encoding model completo en un solo PR
c) No implementar nada
d) Implementar otra parte del encoding model (ej. decoding)

---

### Caso 3: nilearn/nilearn #2019 — Visual reports

**Mecanismo**: Separación por restricción arquitectónica

**Nivel A**:
```
Resultado: PR mergeado. Reporting movido a subpaquete `nilearn.reporting`.
```

**Nivel B**:
```
Resultado: PR mergeado. Reporting movido a subpaquete `nilearn.reporting`.

Alternativas consideradas:
- Mantener reporting dentro de `nilearn.plotting`
- Eliminar reporting completamente
- Mantener con import condicional de matplotlib
- Crear paquete externo separado
```

**Nivel C**:
```
Resultado: PR mergeado. Reporting movido a subpaquete `nilearn.reporting`.

Alternativas consideradas:
- Mantener en `nilearn.plotting` — descartado
- Eliminar reporting — descartado
- Mover a subpaquete separado — elegido
```

**Nivel D** (justificación superficial):
```
Justificación: Se separó reporting porque es mejor.
```

**Nivel E** (justificación específica):
```
Justificación: Se separó reporting porque:
- Restricción arquitectónica: matplotlib no debe estar en el núcleo
- nilearn.plotting importa matplotlib al núcleo, lo cual es indeseable
- Subpaquete separado mantiene el núcleo libre de dependencias pesadas
```

**Opciones para el observador**:
a) Mantener reporting dentro de `nilearn.plotting`
b) **Mover a subpaquete separado** ← correcta
c) Eliminar reporting completamente
d) Mantener con import condicional de matplotlib

---

### Caso 4: nilearn/nilearn #1766 — papaya → brainsprite

**Mecanismo**: Sustitución por evidencia cuantitativa

**Nivel A**:
```
Resultado: PR mergeado. Visor 3D cambiado de papaya a brainsprite.
```

**Nivel B**:
```
Resultado: PR mergeado. Visor 3D cambiado de papaya a brainsprite.

Alternativas consideradas:
- Mantener papaya
- Optimizar papaya internamente
- Usar otra alternativa (plotly, bokeh, ipyvolume)
- Hacer el visor configurable
- Eliminar el visor 3D completamente
```

**Nivel C**:
```
Resultado: PR mergeado. Visor 3D cambiado de papaya a brainsprite.

Alternativas consideradas:
- Mantener papaya — descartado
- Cambiar a brainsprite — elegido
- Optimizar papaya — no documentado como viable
```

**Nivel D** (justificación superficial):
```
Justificación: Se cambió a brainsprite porque es mejor.
```

**Nivel E** (justificación específica):
```
Justificación: Se cambió a brainsprite porque:
- Métrica objetiva: papaya ~12MB vs brainsprite ~15KB (2 órdenes de magnitud)
- Notebooks de 12MB eran impracticables
- brainsprite fue el único candidato evaluado con métrica cuantitativa
```

**Opciones para el observador**:
a) Mantener papaya
b) **Cambiar a brainsprite** ← correcta
c) Optimizar papaya internamente
d) Eliminar el visor 3D completamente

---

### Caso 5: bids-standard/pybids #356 — Oversampling rate

**Mecanismo**: Selección por trade-off explícito

**Nivel A**:
```
Resultado: PR mergeado. Convolve con ajuste dinámico de oversampling.
```

**Nivel B**:
```
Resultado: PR mergeado. Convolve con ajuste dinámico de oversampling.

Alternativas consideradas:
- Usuario llama ToDense manualmente
- Auto-upsample dentro de Convolve
- ToDense automático en dos pasos
- Exponer parámetro de oversampling en API
- Cambiar el spec BIDS
```

**Nivel C**:
```
Resultado: PR mergeado. Convolve con ajuste dinámico de oversampling.

Alternativas consideradas:
- Usuario llama ToDense manualmente — descartado
- Auto-upsample dentro de Convolve — elegido
- ToDense automático en dos pasos — descartado
- Exponer parámetro en API — descartado
```

**Nivel D** (justificación superficial):
```
Justificación: Se eligió auto-upsample porque es mejor.
```

**Nivel E** (justificación específica):
```
Justificación: Se eligió auto-upsample porque:
- UX: no requiere intervención manual del usuario
- Simplicidad: un solo paso vs dos pasos
- Corrección técnica: mantiene precisión en eventos cortos
- Pureza de API: no expone parámetro de oversampling en interfaz pública
```

**Opciones para el observador**:
a) Usuario llama ToDense manualmente
b) **Auto-upsample dentro de Convolve** ← correcta
c) ToDense automático en dos pasos
d) Exponer parámetro de oversampling en API
e) Cambiar el spec BIDS

---

### Caso 6: bids-standard/pybids #369 — Grabbit removal

**Mecanismo**: Internalización por control de dependencias

**Nivel A**:
```
Resultado: PR mergeado. pybids ya no depende de grabbit. Funcionalidad portada.
```

**Nivel B**:
```
Resultado: PR mergeado. pybids ya no depende de grabbit. Funcionalidad portada.

Alternativas consideradas:
- Mantener grabbit como dependencia externa
- Actualizar grabbit
- Contribuir a grabbit para resolver problemas
- Reemplazar grabbit por otra librería
- Hacer grabbit una dependencia opcional
```

**Nivel C**:
```
Resultado: PR mergeado. pybids ya no depende de grabbit. Funcionalidad portada.

Alternativas consideradas:
- Mantener grabbit — descartado
- Portar funcionalidad a pybids — elegido
- Actualizar grabbit — no documentado como viable
```

**Nivel D** (justificación superficial):
```
Justificación: Se eliminó grabbit porque es mejor.
```

**Nivel E** (justificación específica):
```
Justificación: Se eliminó grabbit porque:
- Control de roadmap: dependencia externa bloqueaba el roadmap de pybids
- Portar funcionalidad da control total a los mantenedores de pybids
- Riesgos de roadmap no controlables con grabbit como dependencia externa
```

**Opciones para el observador**:
a) Mantener grabbit como dependencia externa
b) **Portar funcionalidad de grabbit a pybids** ← correcta
c) Reemplazar grabbit por otra librería
d) Hacer grabbit una dependencia opcional

---

### Casos 7-11: Sin merge, sin transformación

Para estos casos, el Nivel A, B, C, D y E son equivalentes porque no hubo transformación. El resultado final es "issue abierto sin resolver".

**Nivel A, B, C, D, E** (idéntico):
```
Resultado: Issue abierto. Sin merge, sin resolución documentada.
```

**Opciones para el observador**:
a) La feature se implementó
b) **La feature no se implementó** ← correcta
c) La feature se implementó parcialmente

Estos casos sirven como control: si el observador acierta que "no pasó nada" en todos los niveles por igual, confirma que la ausencia de transformación es detectable incluso sin contexto.

---

## Tabla de predicción esperada

| Caso | Nivel A | Nivel B | Nivel C | Nivel D | Nivel E |
|:----:|:-------:|:-------:|:-------:|:-------:|:-------:|
| 1 | ~20% | ~30% | ~55% | ~55% | ~85% |
| 2 | ~25% | ~35% | ~55% | ~55% | ~80% |
| 3 | ~25% | ~35% | ~55% | ~55% | ~80% |
| 4 | ~25% | ~40% | ~60% | ~60% | ~90% |
| 5 | ~20% | ~40% | ~70% | ~70% | ~95% |
| 6 | ~25% | ~35% | ~55% | ~55% | ~75% |
| 7 | ~100% | ~100% | ~100% | ~100% | ~100% |
| 8 | ~100% | ~100% | ~100% | ~100% | ~100% |
| 9 | ~100% | ~100% | ~100% | ~100% | ~100% |
| 10 | ~100% | ~100% | ~100% | ~100% | ~100% |
| 11 | ~100% | ~100% | ~100% | ~100% | ~100% |

### Predicciones

1. **Nivel A**: en los casos con merge, el observador no puede predecir qué solución fue elegida mejor que el azar. El resultado final no contiene información sobre el proceso de decisión.

2. **Nivel B**: añadir las alternativas mejora la predicción parcialmente, pero sin saber cuál se descartó, el espacio de posibilidades sigue siendo amplio.

3. **Nivel C**: añadir el descarte reduce el espacio de posibilidades, pero sin el criterio, el observador no puede distinguir entre una decisión informada y una arbitraria.

4. **Nivel D ≈ Nivel C**: la justificación superficial ("porque es mejor") no añade capacidad predictiva significativa sobre el mero hecho de que se descartaron alternativas. La justificación es circular y no permite discriminar contrafactuales.

5. **Nivel E >> Nivel D**: la justificación específica (criterios concretos, evidencia medible, restricciones verificables) permite predecir la solución elegida con alta precisión, porque cada criterio elimina contrafactuales de forma discriminante.

6. **Casos 7-11**: el observador acierta en todos los niveles porque "issue abierto sin merge" es detectable incluso sin contexto.

---

## Lo que mediría este experimento

| Medición | Responde |
|----------|----------|
| Acierto Nivel A vs Nivel E | ¿La justificación específica es suficiente para predecir la trayectoria? |
| Acierto Nivel D vs Nivel E | ¿La calidad de la justificación importa más que su presencia? |
| Acierto Nivel C vs Nivel D | ¿La justificación superficial añade algo sobre el descarte sin criterio? |
| Gap D→E por mecanismo | ¿El efecto de calidad es consistente across todos los tipos de mecanismo? |
| Casos 7-11 como control | ¿El método es sensible a la ausencia de transformación? |

### Criterios de éxito

- **Fuerte (Hipótesis A confirmada)**: Nivel E produce acierto ≥80% en casos con merge, significativamente mayor que Nivel D (≤60%). El gap D→E es consistente across todos los mecanismos.
- **Moderado**: Nivel E produce acierto ≥60%, mayor que Nivel D pero no concluyente. El gap varía por mecanismo.
- **Débil**: Nivel E no mejora significativamente respecto a Nivel D. La calidad no importa; solo la presencia.

---

## Lo que NO mide este experimento

1. **Comprensión profunda**. Predecir la solución elegida no equivale a comprender el proyecto. Es una condición necesaria, no suficiente.

2. **Generalizabilidad**. La muestra son 11 casos de 3 proyectos de software científico. No cubre papers, experimentos, o laboratorios.

3. **Reproducibilidad inter-observador**. El experimento asume un observador con conocimiento del dominio. Otro observador podría tener resultados diferentes.

4. **Causalidad**. Incluso si Nivel E permite predecir, no demuestra que la justificación específica sea la causa de la comprensión. Podría ser un correlato.

5. **Construcción de los niveles D y E**. Los niveles D (superficial) y E (específico) son reconstrucciones del observador, no siempre coinciden con lo que está en el registro. Para algunos casos (Caso 4), la justificación real ya es específica; para otros (Caso 6), es más bien superficial. El experimento prueba la hipótesis de que la calidad importa, independientemente de lo que el registro contenga.

---

## El principio provisional

Si la Hipótesis B es confirmada — que toda explicación útil reduce incertidumbre contrafactual — entonces los mecanismos concretos (arquitectura, capacidad, trade-off, dependencia, redundancia, evidencia) podrían ser manifestaciones superficiales de una propiedad más profunda.

La diferencia entre:

```text
Se eligió A porque es mejor.
```

y

```text
Se eligió A porque:
- reduce complejidad O(n²)→O(n)
- elimina dependencia externa
- mantiene compatibilidad hacia atrás
```

no es que uno tenga "más mecanismos". Es que el segundo permite responder a:

```text
¿Por qué no B? → B no reduce complejidad
¿Por qué no C? → C no elimina dependencia
¿Qué habría pasado si mantuviéramos B? → tendríamos O(n²) y dependencia externa
```

El primero no permite ninguna de esas respuestas. La justificación es circular: "es mejor porque es mejor".

**La propiedad profunda no es el mecanismo, sino la discriminabilidad contrafactual.**

Esto conecta con toda la trayectoria:

| Sprint | Pregunta | Hallazgo | Conexión con discriminabilidad |
|--------|----------|----------|-------------------------------|
| 49 | ¿Qué transformaciones añaden explicación? | Las que reducen el espacio de posibilidades (100%) | Reducir espacio = aumentar discriminabilidad |
| 50 | ¿Se puede predecir la solución? | Nivel C (problema + alternativas) permite predecir | Predecir = discriminar trayectoria elegida |
| 52 | ¿Es el criterio lo que importa? | Sí, el criterio documentado es clave | El criterio es lo que discrimina |
| 54 | ¿Importa el tipo de mecanismo? | No, importa la presencia | La presencia activa la discriminación |
| 55 | ¿Importa la calidad de la justificación? | **Por probar** | La calidad determina cuán bien se discrimina |

---

## Patrón metodológico emergente

Si se toman todos los artefactos como válidos, se ve un desplazamiento metodológico saludable:

| Fase | Pregunta | Resultado |
|------|----------|-----------|
| 27-43 | ¿Qué entidad explica el sistema? | Falsaciones sucesivas |
| 44-52 | ¿Qué información falta? | Transformaciones observables |
| 53-55 | ¿Qué hace que una transformación sea explicativa? | Mecanismos de selección y descarte |

Ese desplazamiento abandona constructos mentales ("Program", "Understanding", "Reasoning") y se acerca a diferencias observables entre trayectorias.

---

## Riesgo actual

Se corre el riesgo de tratar:

> "criterio documentado de selección"

como antes se trató:

> "Program"

Es decir, como posible entidad privilegiada. Y aún no está demostrado.

Lo que Sprint 49-55 muestra realmente es algo más débil:

> La información que ayuda a distinguir una trayectoria de otras trayectorias plausibles produce ganancia explicativa.

Eso es distinto. Porque un criterio explícito es solo una forma de producir discriminación. Pueden existir otras:

* restricciones físicas
* costes
* dependencias temporales
* relaciones causales
* pruebas experimentales
* autoridad organizativa
* accidentes históricos

Todavía no se conoce la propiedad común.

---

## Hallazgo más fuerte hasta ahora

No es:

> State ≠ Process

porque sigue siendo una formulación abstracta.

El hallazgo más sólido parece ser:

> Un artefacto final admite múltiples historias compatibles con su existencia.

Y:

> La información adicional valiosa es aquella que elimina historias compatibles incorrectas.

Eso conecta:

* Sprint 44 (ausencias)
* Sprint 48B (contrafactuales)
* Sprint 49 (ganancia explicativa)
* Sprint 52 (criterios de descarte)
* Sprint 55 (calidad de la justificación)

sin introducir ninguna entidad cognitiva.

Ejemplo:

```text
Resultado: Merge #123
```

Historias compatibles:

* había tres alternativas y ganó A
* había un bug crítico
* había una restricción de memoria
* fue una orden del director
* fue casualidad
* fue un benchmark
* fue una presión regulatoria

El resultado final es compatible con todas. La explicación aparece cuando descartas historias. No necesariamente cuando introduces razonamiento. No necesariamente cuando introduces comprensión. Simplemente cuando reduces el conjunto de historias compatibles.

---

## Lo que NO se ha demostrado

1. **Que la calidad de la justificación sea el factor único**. Podría haber otros factores (profundidad del problema, número de alternativas, etc.) que también influyan en la capacidad predictiva.

2. **Que la discriminabilidad contrafactual sea generalizable**. La muestra son 11 casos de 3 proyectos de software científico.

3. **Que la Hipótesis B sea cierta**. Es una hipótesis profunda que requiere prueba empírica, no solo intuición.

4. **Que los niveles D y E sean reconstruibles de forma consistente**. La distinción entre "superficial" y "específico" puede ser subjetiva.

5. **Que el experimento sea ejecutable**. Sprint 50 propuso un experimento que no se ejecutó. Sprint 55 propone otro. La ejecución requiere un observador ciego, casos en orden aleatorio, y un protocolo de medición estandarizado.

---

## Afirmación de trabajo (congelada provisionalmente)

```text
Un artefacto final admite
múltiples historias compatibles
con su existencia.

La información adicional valiosa
es aquella que elimina
historias compatibles incorrectas.

La capacidad explicativa parece
correlacionarse con la cantidad
de historias compatibles
que se eliminan.

La relación exacta entre
eliminación de historias,
discriminación, explicación
y comprensión
permanece sin demostrar.
```

Esa formulación encaja con todos los hallazgos de Sprint 47–55 y, lo más importante, sigue siendo falsable. No convierte todavía "incertidumbre contrafactual", "comprensión" o "explicación" en entidades fundacionales del sistema.

---

## Pregunta abierta para Sprint 56

No mediría todavía "comprensión".

No mediría "explicación".

No mediría "incertidumbre contrafactual".

Todavía son términos demasiado cargados.

Mediría algo más simple.

### Variable observable

**Número de trayectorias plausibles restantes.**

Ejemplo:

| Estado | Trayectorias plausibles restantes |
|--------|----------------------------------|
| Estado final solamente | 100 |
| Resultado + problema | 40 |
| Resultado + problema + alternativas | 8 |
| Resultado + problema + alternativas + criterio | 2 |

La pregunta deja de ser:

> ¿Comprende?

y pasa a ser:

> ¿Cuánto se reduce el espacio de historias compatibles?

Eso es mucho más observable.

### Discriminación vs Explicación

Sprint 56 debe intentar distinguir estos dos conceptos, que podrían coincidir o no:

| Concepto | Pregunta | ¿Es operacionalizable? |
|----------|----------|------------------------|
| Discriminación | ¿Puedo distinguir A de B? | Sí — medir capacidad predictiva / número de historias restantes |
| Explicación | ¿Sé por qué A sobrevivió? | Parcialmente — medir reducción de espacio de historias |

**Ejemplo de divergencia**: "Se eligió A porque el director lo ordenó" permite discriminación (sabes que no fue B porque el director lo decidió) pero no explicación causal profunda.

La pregunta para Sprint 56 es: ¿en los 11 casos, la discriminación y la explicación coinciden siempre? Si no, ¿qué tipo de justificación produce discriminación sin explicación?

---

## Si esta línea sobrevive a falsaciones

Si la afirmación de trabajo — "un artefacto final admite múltiples historias compatibles; la información valiosa elimina historias compatibles incorrectas" — sobrevive a falsaciones en casos más amplios, entonces CoResearcher podría terminar fundado no sobre "comprensión", sino sobre algo mucho más operativo:

> reconstrucción progresiva del espacio de trayectorias compatibles con un resultado observado.

Esa formulación es medible, falsable, y no requiere estados mentales.

---

## Nota metodológica

Este experimento NO se ha ejecutado. Es un diseño propuesto para Sprint 55. Los valores en la tabla de predicción esperada son hipótesis, no resultados.

Si se ejecuta, debe hacerse con:

1. **Observador ciego**: que no conozca los casos ni la hipótesis.
2. **Orden aleatorio**: los casos deben presentarse en orden aleatorio para evitar sesgo de aprendizaje.
3. **Protocolo estandarizado**: las instrucciones para cada nivel deben ser idénticas, solo cambiando la información proporcionada.
4. **Justificación D y E como reconstrucciones**: para algunos casos, la justificación real en el registro es más específica (Caso 4) o más superficial (Caso 6) que los niveles D y E propuestos. El experimento prueba la hipótesis de que la calidad importa, presentando ambas versiones a todos los casos.

La distinción entre "predecir" y "comprender" es crucial: predecir es medible, comprender no lo es (todavía). Este experimento mide lo primero como proxy de lo segundo, con la advertencia de que el proxy podría ser insuficiente.

---

## Resumen del Sprint 55

### Hallazgos (propuestos)

1. **La pregunta de Sprint 54 necesita refinarse**: no es "¿importa el tipo de mecanismo?" sino "¿importa la calidad de la justificación?"

2. **La calidad de la justificación puede operacionalizarse**: superficial (circular, vaga) vs específica (criterios concretos, evidencia medible, discriminabilidad contrafactual).

3. **La Hipótesis B es un candidato a principio provisional**: "toda explicación útil reduce incertidumbre contrafactual". Si se confirma, los mecanismos concretos son manifestaciones superficiales de una propiedad más profunda.

4. **La pregunta ya no es "¿dónde está la explicación?"**: es "¿cuál es la información observable mínima que aumenta de forma reproducible la capacidad predictiva?"

### Lo que NO se ha demostrado

- Que la calidad de la justificación sea el factor determinante (por probar empíricamente).
- Que la Hipótesis B sea cierta (candidata a principio, no principio confirmado).
- Que el experimento sea ejecutable con los recursos disponibles.

### Pregunta abierta para Sprint 56

```text
¿Cuánto se reduce el espacio de historias compatibles
con un resultado observado,
a medida que se añade información?
```
>>>>>>>


