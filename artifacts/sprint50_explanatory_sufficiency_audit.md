# Sprint 50 — Explanatory Sufficiency Audit

## Pregunta

> ¿Puede un observador predecir qué solución fue elegida a partir de la información disponible?

## Hipótesis

```
Explicación =
reconstrucción del espacio de posibilidades
+
eliminación progresiva de alternativas
```

Si esta hipótesis es correcta, entonces un observador que conozca el problema y las alternativas descartadas debería poder predecir qué solución fue elegida significativamente mejor que un observador que solo conoce el resultado final.

## Método

Tomar los mismos 11 casos de Sprint 40/42C.

Construir tres niveles de información para cada caso:

### Nivel A — Solo resultado final

```
Resultado: PR mergeado. Se eliminó la función `regress` de Epochs metadata.
```

Sin contexto. Sin problema. Sin alternativas.

### Nivel B — Resultado final + Problema

```
Resultado: PR mergeado. Se eliminó la función `regress` de Epochs metadata.

Problema: El PR incluía dos mecanismos (regress y pandas-query) que hacían lo mismo.
```

### Nivel C — Resultado final + Problema + Alternativas descartadas

```
Resultado: PR mergeado. Se eliminó la función `regress` de Epochs metadata.

Problema: El PR incluía dos mecanismos (regress y pandas-query) que hacían lo mismo.

Alternativas consideradas:
- Mantener ambas funciones — descartado por duplicación de API
- Modificar regress para integrarlo con pandas-query — descartado por complejidad
- Deprecar regress — no se documentó como opción viable
```

### Tarea del observador

Para cada caso, en cada nivel:

```
Dada esta información,
¿qué solución crees que fue elegida?
```

Opciones: una lista de 3-5 alternativas plausibles (incluyendo la correcta).

### Medición

- **Acierto en Nivel A**: línea base (solo resultado final, sin contexto)
- **Acierto en Nivel B**: ganancia por añadir el problema
- **Acierto en Nivel C**: ganancia por añadir alternativas descartadas

Si Nivel C produce acierto significativamente mayor que Nivel A, la estructura "Problema + Alternativas descartadas" es suficiente para predecir la trayectoria.

---

## Construcción de los niveles para cada caso

### Caso 1: MNE-Python #4414 — Epochs metadata (regress removal)

**Nivel A**:
```
Resultado: PR mergeado. Epochs metadata con pandas-query, sin función `regress`.
```

**Nivel B**:
```
Resultado: PR mergeado. Epochs metadata con pandas-query, sin función `regress`.

Problema: El PR original incluía dos mecanismos para consultar metadata (regress y pandas-query) que se solapaban funcionalmente. Un revisor señaló la redundancia.
```

**Nivel C**:
```
Resultado: PR mergeado. Epochs metadata con pandas-query, sin función `regress`.

Problema: El PR original incluía dos mecanismos para consultar metadata (regress y pandas-query) que se solapaban funcionalmente. Un revisor señaló la redundancia.

Alternativas consideradas (según el hilo):
- Mantener ambas funciones — descartado por duplicación de API
- Modificar regress para trabajar con pandas-query — descartado por complejidad
- Eliminar regress — elegido por consenso rápido
```

**Opciones para el observador**:
a) Mantener ambas funciones
b) Modificar regress para integrarlo con pandas-query
c) **Eliminar regress** ← correcta
d) Deprecar regress y mantenerlo con warning
e) No mergear el PR

---

### Caso 2: MNE-Python #3728 — Receptive field module

**Nivel A**:
```
Resultado: PR mergeado. Se añadió módulo receptive field a MNE.
```

**Nivel B**:
```
Resultado: PR mergeado. Se añadió módulo receptive field a MNE.

Problema: El equipo quería añadir encoding models a MNE, pero implementar el sistema completo en un solo PR era demasiado grande para revisarlo.
```

**Nivel C**:
```
Resultado: PR mergeado. Se añadió módulo receptive field a MNE.

Problema: El equipo quería añadir encoding models a MNE, pero implementar el sistema completo en un solo PR era demasiado grande para revisarlo.

Alternativas consideradas (según el hilo):
- Implementar encoding model completo en un solo PR — descartado por tamaño/riesgo
- Dividir en múltiples PRs parciales — elegido, con receptive field como primer paso
- No hacer nada — descartado porque la feature era valiosa
```

**Opciones para el observador**:
a) **Implementar solo receptive field como primer paso** ← correcta
b) Implementar encoding model completo en un solo PR
c) No implementar nada
d) Implementar otra parte del encoding model (ej. decoding)

---

### Caso 3: nilearn/nilearn #2019 — Visual reports

**Nivel A**:
```
Resultado: PR mergeado. Reporting movido a subpaquete `nilearn.reporting`.
```

**Nivel B**:
```
Resultado: PR mergeado. Reporting movido a subpaquete `nilearn.reporting`.

Problema: La funcionalidad de reporting visual estaba dentro de `nilearn.plotting`, que importaba matplotlib al núcleo. Los mantenedores querían mantener el núcleo libre de esa dependencia.
```

**Nivel C**:
```
Resultado: PR mergeado. Reporting movido a subpaquete `nilearn.reporting`.

Problema: La funcionalidad de reporting visual estaba dentro de `nilearn.plotting`, que importaba matplotlib al núcleo. Los mantenedores querían mantener el núcleo libre de esa dependencia.

Alternativas consideradas (según el hilo):
- Mantener reporting dentro de `nilearn.plotting` — descartado por acoplamiento con matplotlib
- Eliminar reporting completamente — descartado por utilidad para usuarios
- Mover a subpaquete separado `nilearn.reporting` — elegido
```

**Opciones para el observador**:
a) Mantener reporting dentro de `nilearn.plotting`
b) **Mover a subpaquete separado** ← correcta
c) Eliminar reporting completamente
d) Mantener con import condicional de matplotlib

---

### Caso 4: nilearn/nilearn #1766 — papaya → brainsprite

**Nivel A**:
```
Resultado: PR mergeado. Visor 3D cambiado de papaya a brainsprite.
```

**Nivel B**:
```
Resultado: PR mergeado. Visor 3D cambiado de papaya a brainsprite.

Problema: Los notebooks generados con papaya ocupaban ~12MB. brainsprite ocupaba ~15KB. La diferencia era de 2 órdenes de magnitud.
```

**Nivel C**:
```
Resultado: PR mergeado. Visor 3D cambiado de papaya a brainsprite.

Problema: Los notebooks generados con papaya ocupaban ~12MB. brainsprite ocupaba ~15KB. La diferencia era de 2 órdenes de magnitud.

Alternativas consideradas (según el hilo):
- Mantener papaya — descartado por notebooks impracticables
- Cambiar a brainsprite — elegido por métrica objetiva
- Optimizar papaya internamente — no se documentó como viable
```

**Opciones para el observador**:
a) Mantener papaya
b) **Cambiar a brainsprite** ← correcta
c) Optimizar papaya internamente
d) Eliminar el visor 3D completamente

---

### Caso 5: bids-standard/pybids #356 — Oversampling rate

**Nivel A**:
```
Resultado: PR mergeado. Convolve con ajuste dinámico de oversampling.
```

**Nivel B**:
```
Resultado: PR mergeado. Convolve con ajuste dinámico de oversampling.

Problema: Eventos cortos producían artefactos en Convolve. Había que decidir cómo manejarlos sin exponer parámetros complejos en la API.
```

**Nivel C**:
```
Resultado: PR mergeado. Convolve con ajuste dinámico de oversampling.

Problema: Eventos cortos producían artefactos en Convolve. Había que decidir cómo manejarlos sin exponer parámetros complejos en la API.

Alternativas consideradas (según el hilo, 3 explícitas):
- Usuario llama ToDense manualmente — descartado por mala UX
- Auto-upsample dentro de Convolve — elegido
- ToDense automático en dos pasos — descartado por complejidad
- Exponer parámetro de oversampling en API — descartado por restricción de diseño
```

**Opciones para el observador**:
a) Usuario llama ToDense manualmente
b) **Auto-upsample dentro de Convolve** ← correcta
c) ToDense automático en dos pasos
d) Exponer parámetro de oversampling en API
e) Cambiar el spec BIDS

---

### Caso 6: bids-standard/pybids #369 — Grabbit removal

**Nivel A**:
```
Resultado: PR mergeado. pybids ya no depende de grabbit. Funcionalidad portada.
```

**Nivel B**:
```
Resultado: PR mergeado. pybids ya no depende de grabbit. Funcionalidad portada.

Problema: pybids dependía de grabbit como librería externa para layout/core. Esto creaba riesgos de roadmap porque los mantenedores no controlaban el desarrollo de grabbit.
```

**Nivel C**:
```
Resultado: PR mergeado. pybids ya no depende de grabbit. Funcionalidad portada.

Problema: pybids dependía de grabbit como librería externa para layout/core. Esto creaba riesgos de roadmap porque los mantenedores no controlaban el desarrollo de grabbit.

Alternativas consideradas (según el hilo):
- Mantener grabbit como dependencia externa — descartado por pérdida de control de roadmap
- Portar funcionalidad de grabbit a pybids — elegido
- Actualizar grabbit — no se documentó como viable
```

**Opciones para el observador**:
a) Mantener grabbit como dependencia externa
b) **Portar funcionalidad de grabbit a pybids** ← correcta
c) Reemplazar grabbit por otra librería
d) Hacer grabbit una dependencia opcional

---

### Casos 7-11: Sin merge, sin transformación

Para estos casos, el Nivel A, B y C son equivalentes porque no hubo transformación. El resultado final es "issue abierto sin resolver".

**Nivel A, B, C** (idéntico):
```
Resultado: Issue abierto. Sin merge, sin resolución documentada.
```

**Opciones para el observador**:
a) La feature se implementó
b) **La feature no se implementó** ← correcta
c) La feature se implementó parcialmente

Estos casos sirven como control: si el observador acierta que "no pasó nada" en Nivel A, B y C por igual, confirma que la ausencia de transformación es detectable incluso sin contexto.

---

## Tabla de predicción esperada

| Caso | Nivel A (solo resultado) | Nivel B (+ problema) | Nivel C (+ alternativas) |
|:----:|:------------------------:|:--------------------:|:------------------------:|
| 1 | Aleatorio (~20%) | Mejor que aleatorio | Alta precisión |
| 2 | Aleatorio (~25%) | Mejor que aleatorio | Alta precisión |
| 3 | Aleatorio (~25%) | Mejor que aleatorio | Alta precisión |
| 4 | Aleatorio (~25%) | Alta precisión (métrica clara) | Alta precisión |
| 5 | Aleatorio (~20%) | Mejor que aleatorio | Alta precisión |
| 6 | Aleatorio (~25%) | Mejor que aleatorio | Alta precisión |
| 7 | Alta precisión (sin merge) | Alta precisión | Alta precisión |
| 8 | Alta precisión (sin merge) | Alta precisión | Alta precisión |
| 9 | Alta precisión (sin merge) | Alta precisión | Alta precisión |
| 10 | Alta precisión (sin merge) | Alta precisión | Alta precisión |
| 11 | Alta precisión (sin merge) | Alta precisión | Alta precisión |

### Predicciones

1. **Nivel A**: en los casos con merge, el observador no puede predecir qué solución fue elegida mejor que el azar. El resultado final no contiene información sobre el proceso de decisión.

2. **Nivel B**: añadir el problema mejora la predicción, pero no es suficiente para determinar la solución exacta porque varias soluciones podrían resolver el mismo problema.

3. **Nivel C**: añadir las alternativas descartadas permite predecir la solución elegida con alta precisión, porque el espacio de posibilidades se ha reducido hasta la solución real.

4. **Casos 7-11**: el observador acierta en todos los niveles porque "issue abierto sin merge" es detectable incluso sin contexto.

---

## Lo que mediría este experimento

| Medición | Responde |
|----------|----------|
| Acierto Nivel A vs Nivel C | ¿La estructura Problema + Alternativas es suficiente para predecir la trayectoria? |
| Diferencia Nivel B vs Nivel C | ¿Cuánto añaden las alternativas respecto al problema solo? |
| Casos 7-11 como control | ¿El método es sensible a la ausencia de transformación? |

### Criterios de éxito

- **Fuerte**: Nivel C produce acierto ≥80% en casos con merge, significativamente mayor que Nivel A (≤30%).
- **Moderado**: Nivel C produce acierto ≥60%, mayor que Nivel A pero no concluyente.
- **Débil**: Nivel C no mejora respecto a Nivel A. La estructura no es suficiente.

---

## Lo que NO mide este experimento

1. **Comprensión profunda**. Predecir la solución elegida no equivale a comprender el proyecto. Es una condición necesaria, no suficiente.

2. **Generalizabilidad**. La muestra son 11 casos de 3 proyectos de software científico. No cubre papers, experimentos, o laboratorios.

3. **Reproducibilidad inter-observador**. El experimento asume un observador con conocimiento del dominio. Otro observador podría tener resultados diferentes.

4. **Causalidad**. Incluso si Nivel C permite predecir, no demuestra que la estructura "Problema + Alternativas" sea la causa de la comprensión. Podría ser un correlato.

---

## Pregunta abierta para Sprint 51

```
Si Nivel C permite predecir la solución
significativamente mejor que Nivel A,
¿es posible automatizar la extracción
de la estructura Problema → Alternativas → Solución
desde el registro público (issues, PRs, commits)?
```

Esto desplazaría la pregunta de:

```
¿Podemos medir si lo añadido es suficiente?
```

a:

```
¿Podemos extraerlo automáticamente?
```

La segunda requiere ingeniería, no solo observación.

---

## Nota metodológica

Este experimento NO se ha ejecutado. Es un diseño propuesto para Sprint 50. Los valores en la tabla de predicción esperada son hipótesis, no resultados.

Si se ejecuta, debe hacerse con un observador ciego (que no conozca los casos) y con casos presentados en orden aleatorio para evitar sesgo de aprendizaje.

La distinción entre "predecir" y "comprender" es crucial: predecir es medible, comprender no lo es (todavía). Este experimento mide lo primero como proxy de lo segundo, con la advertencia de que el proxy podría ser insuficiente.