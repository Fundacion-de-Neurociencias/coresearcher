# Sprint 52 — Explanatory Mechanism Audit

## Pregunta

> ¿La capacidad explicativa reside en la reducción del espacio de posibilidades o en los criterios mediante los cuales se descartaron las alternativas?

## Hipótesis a refinar

La hipótesis de Sprint 49 era:

```
Reduction of possibility space → Explanatory gain
```

El feedback de Sprint 51 señala un contraejemplo potencial:

```
El jefe decide A. B, C, D quedan prohibidas.
→ Reduce posibilidades
→ No explica nada
```

La diferencia no es la reducción, sino **qué información provoca la reducción**.

## Método

Separar tres elementos que antes se trataban juntos:

| Elemento | Observable | Explicativo (hipótesis) |
|----------|:----------:|:----------------------:|
| Existían alternativas | ✅ Sí | Bajo |
| Fueron descartadas | ✅ Sí | Medio |
| Sabemos por qué fueron descartadas (criterio) | ✅ Sí | Alto |

Repetir el análisis de ganancia explicativa de Sprint 49, pero separando cada elemento.

## Evaluación por caso

Para cada uno de los 6 casos con merge, evaluar tres niveles:

### Nivel 1: Existían alternativas
¿El registro documenta que había más de una opción posible?

### Nivel 2: Fueron descartadas
¿El registro documenta que algunas opciones fueron rechazadas?

### Nivel 3: Sabemos por qué fueron descartadas
¿El registro documenta el criterio, evidencia o restricción que llevó al descarte?

---

## Caso 1: MNE-Python #4414 — Epochs metadata (regress removal)

**Alternativas existentes**: Sí. Mantener ambas, modificar regress, eliminar regress, deprecar, no mergear.

**Fueron descartadas**: Sí. Mantener ambas y modificar regress fueron explícitamente descartadas.

**Sabemos por qué**: Sí. "Redundancia" fue el criterio. El revisor detectó que regress y pandas-query hacían lo mismo.

**Ganancia explicativa por nivel**:
- Nivel 1 (existen alternativas): Baja. Saber que había opciones no dice cuál se eligió ni por qué.
- Nivel 2 (fueron descartadas): Media. Saber que algunas se descartaron reduce el espacio, pero no explica el criterio.
- Nivel 3 (criterio de descarte): Alta. "Redundancia" es el mecanismo que explica por qué se eliminó regress.

---

## Caso 2: MNE-Python #3728 — Receptive field module

**Alternativas existentes**: Sí. PR completo, PR parcial, no hacer nada, esperar.

**Fueron descartadas**: Sí. PR completo y no hacer nada fueron descartados.

**Sabemos por qué**: Sí. "Too much to bite off in one PR" — capacidad de revisión como criterio.

**Ganancia explicativa por nivel**:
- Nivel 1: Baja.
- Nivel 2: Media.
- Nivel 3: Alta. El criterio "capacidad de revisión" explica por qué el resultado es un PR pequeño.

---

## Caso 3: nilearn/nilearn #2019 — Visual reports

**Alternativas existentes**: Sí. Mantener, eliminar, mover a subpaquete, import condicional, paquete externo.

**Fueron descartadas**: Sí. Mantener y eliminar fueron explícitamente descartados.

**Sabemos por qué**: Sí. "No matplotlib en el núcleo" fue el criterio arquitectónico.

**Ganancia explicativa por nivel**:
- Nivel 1: Baja.
- Nivel 2: Media.
- Nivel 3: Alta. El criterio arquitectónico explica la dirección del cambio.

---

## Caso 4: nilearn/nilearn #1766 — papaya → brainsprite

**Alternativas existentes**: Sí. Mantener papaya, cambiar a brainsprite, optimizar, otra alternativa, eliminar visor.

**Fueron descartadas**: Sí. Mantener papaya fue descartado.

**Sabemos por qué**: Sí. Métrica objetiva: 12MB vs 15KB.

**Ganancia explicativa por nivel**:
- Nivel 1: Baja.
- Nivel 2: Media.
- Nivel 3: Alta. La métrica objetiva es el criterio más claro de todos los casos.

---

## Caso 5: bids-standard/pybids #356 — Oversampling rate

**Alternativas existentes**: Sí. 3 explícitas + varias implícitas.

**Fueron descartadas**: Sí. 2 alternativas explícitamente descartadas (manual, dos pasos) más la restricción de no exponer parámetro.

**Sabemos por qué**: Sí. Criterios documentados: UX, simplicidad, corrección técnica, pureza de API.

**Ganancia explicativa por nivel**:
- Nivel 1: Baja.
- Nivel 2: Media.
- Nivel 3: Alta. Es el caso con criterios más explícitos y diversos.

---

## Caso 6: bids-standard/pybids #369 — Grabbit removal

**Alternativas existentes**: Sí. Mantener, portar, actualizar, contribuir, reemplazar, opcional.

**Fueron descartadas**: Sí. Mantener fue descartado.

**Sabemos por qué**: Parcialmente. "Control de roadmap" es el criterio, pero es cualitativo y no verificable desde el registro público.

**Ganancia explicativa por nivel**:
- Nivel 1: Baja.
- Nivel 2: Media.
- Nivel 3: Media-Alta. El criterio existe pero es menos sólido que en otros casos.

---

## Tabla de ganancia explicativa por nivel

| Caso | Nivel 1: Existen alternativas | Nivel 2: Fueron descartadas | Nivel 3: Criterio de descarte |
|:----:|:----------------------------:|:---------------------------:|:-----------------------------:|
| 1 | Baja | Media | **Alta** |
| 2 | Baja | Media | **Alta** |
| 3 | Baja | Media | **Alta** |
| 4 | Baja | Media | **Alta** |
| 5 | Baja | Media | **Alta** |
| 6 | Baja | Media | **Media-Alta** |

### Observaciones

1. **Nivel 1 (existen alternativas) tiene ganancia baja en todos los casos**. Saber que había opciones no explica por qué se eligió una. Es información necesaria pero no suficiente.

2. **Nivel 2 (fueron descartadas) tiene ganancia media**. Saber qué se descartó reduce el espacio de posibilidades, pero sin el criterio no se puede distinguir entre una decisión informada y una arbitraria.

3. **Nivel 3 (criterio de descarte) tiene ganancia alta en 5/6 casos**. El criterio es la información que realmente explica por qué se eligió esa trayectoria y no otra.

4. **Caso 6 es la excepción parcial**: el criterio ("control de roadmap") existe pero es cualitativo y no verificable. La ganancia es media-alta, no alta.

---

## Conclusión

La hipótesis de Sprint 49 debe refinarse:

```
Reduction of possibility space
→
NO es suficiente para ganancia explicativa
```

```
Criterio de descarte documentado
→
SÍ correlaciona con ganancia explicativa alta
```

El contraejemplo del feedback ("el jefe decide A") queda explicado: la reducción de espacio sin criterio documentado no añade explicación. En los 6 casos con merge, el criterio de descarte está documentado (aunque con diferente calidad).

### Hipótesis refinada

```
La información explicativa se concentra
en los criterios de selección y descarte
que transforman múltiples posibilidades
en un resultado concreto.
```

### Lo que NO se ha demostrado

1. Que el criterio de descarte sea suficiente para la comprensión completa. Añade más explicación que la reducción sola, pero no se ha medido si alcanza.

2. Que el criterio de descarte sea necesario. Podría haber casos donde la reducción sin criterio documentado sí añada explicación (aunque no se han encontrado en esta muestra).

3. Que el criterio de descarte sea generalizable. La muestra son 6 casos de 3 proyectos.

---

## Pregunta abierta para Sprint 53

```
Si el criterio de descarte es
el principal predictor de ganancia explicativa,
¿es posible extraerlo automáticamente
del registro público (issues, PRs, commits)?
```

Esto desplazaría la pregunta de:

```
¿Qué añade explicación?
```

a:

```
¿Podemos extraerlo automáticamente?
```

La segunda requiere ingeniería, no solo observación.