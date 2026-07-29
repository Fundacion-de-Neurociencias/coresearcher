# Sprint 53 — Justification Audit

## Pregunta

> ¿Qué tipos de justificación aparecen realmente en los casos?

## Método

Sin taxonomía previa. Sin vocabulario controlado. Sin categorías heredadas.

Para cada uno de los 6 casos con merge, extraer el **texto literal** de la justificación de por qué se eligió la solución que se eligió.

Después, agrupación inductiva: leer todas las justificaciones y ver qué patrones emergen sin forzarlos a categorías preexistentes.

---

## Caso 1: MNE-Python #4414 — Epochs metadata (regress removal)

**Texto literal de la justificación**:

> "parece que si eliminamos `regress`, ya convergemos, ¿no?"
> "ok then :) eliminemos regress"

**Contexto**: El revisor detectó que mantener `regress` y el enfoque pandas-query generaba redundancia.

**Justificación subyacente**: **Eliminación por redundancia**. Dos mecanismos hacían lo mismo. Mantener ambos duplicaba la API sin beneficio.

---

## Caso 2: MNE-Python #3728 — Receptive field module

**Texto literal de la justificación**:

> "we decided tackling the general encoding model problem is probably too much to bite off in one PR"

**Contexto**: El PR original pretendía implementar encoding models completos. Se redujo el alcance a solo receptive field.

**Justificación subyacente**: **Reducción de alcance por capacidad de revisión**. El PR completo era demasiado grande para ser revisado. Se optó por un primer paso más pequeño.

---

## Caso 3: nilearn/nilearn #2019 — Visual reports

**Texto literal de la justificación**:

No hay una cita textual única. La justificación se infiere de la discusión entre GaelVaroquaux y jeromedockes sobre mantener el núcleo libre de matplotlib.

**Justificación subyacente**: **Separación arquitectónica por restricción de dependencias**. matplotlib no debía estar en el núcleo. La solución fue mover reporting a un subpaquete separado.

---

## Caso 4: nilearn/nilearn #1766 — papaya → brainsprite

**Texto literal de la justificación**:

No hay una cita textual única de la decisión. La justificación se basa en datos comparativos: papaya ~2MB vs brainsprite ~15KB.

**Justificación subyacente**: **Sustitución por métrica objetiva**. El tamaño de los notebooks (12MB) era impracticable. La evidencia era incontrovertible.

---

## Caso 5: bids-standard/pybids #356 — Oversampling rate

**Texto literal de la justificación**:

No hay una cita textual única. La decisión se tomó después de debatir tres alternativas explícitas con criterios documentados: UX, simplicidad, corrección técnica, pureza de API.

**Justificación subyacente**: **Selección por trade-off explícito**. Se documentaron 3 alternativas, se evaluaron contra criterios conocidos, y se eligió la que mejor balanceaba simplicidad y corrección.

---

## Caso 6: bids-standard/pybids #369 — Grabbit removal

**Texto literal de la justificación**:

No hay una cita textual única. La justificación se infiere de la discusión sobre control de roadmap y dependencias externas.

**Justificación subyacente**: **Internalización por control de roadmap**. Mantener grabbit como dependencia externa creaba riesgos. Portar la funcionalidad daba control total a los mantenedores de pybids.

---

## Agrupación inductiva de justificaciones

Leyendo las 6 justificaciones sin categorías previas, aparecen los siguientes tipos:

### Tipo A: Eliminación por redundancia
**Caso 1**. Dos cosas hacen lo mismo. Se elimina una.
**Mecanismo**: Detección de solapamiento funcional.

### Tipo B: Reducción por capacidad limitada
**Caso 2**. El alcance es demasiado grande para los recursos disponibles. Se reduce.
**Mecanismo**: Restricción de recursos humanos (revisores, tiempo).

### Tipo C: Separación por restricción arquitectónica
**Caso 3**. Una dependencia no debe estar en el núcleo. Se separa.
**Mecanismo**: Restricción de diseño arquitectónico.

### Tipo D: Sustitución por evidencia cuantitativa
**Caso 4**. Una métrica objetiva muestra que la alternativa es superior. Se reemplaza.
**Mecanismo**: Evidencia medible e incontrovertible.

### Tipo E: Selección por trade-off explícito
**Caso 5**. Múltiples alternativas con criterios conocidos. Se elige la que mejor balancea.
**Mecanismo**: Decisión multicriterio documentada.

### Tipo F: Internalización por control de dependencias
**Caso 6**. Una dependencia externa limita el control del roadmap. Se internaliza.
**Mecanismo**: Restricción de gobernanza del proyecto.

---

## Tabla de mecanismos de selección observados

| Mecanismo | Caso | Tipo de evidencia | ¿Cuantificable? |
|-----------|:----:|:-----------------:|:---------------:|
| Eliminación por redundancia | 1 | Cualitativa (revisor detecta solapamiento) | Parcial |
| Reducción por capacidad limitada | 2 | Cualitativa ("too much to bite off") | No |
| Separación por restricción arquitectónica | 3 | Cualitativa (opinión de mantenedores) | No |
| Sustitución por evidencia cuantitativa | 4 | **Cuantitativa** (12MB vs 15KB) | Sí |
| Selección por trade-off explícito | 5 | Cualitativa + criterios documentados | Parcial |
| Internalización por control de dependencias | 6 | Cualitativa (control de roadmap) | No |

### Observaciones

1. **Solo 1/6 mecanismos es cuantitativo**. El resto son cualitativos: juicios de expertos, restricciones de diseño, capacidad de equipo.

2. **5/6 mecanismos son variantes de "restricción"**. Redundancia, capacidad, arquitectura, control de dependencias — todos describen algo que *no se podía hacer* más que algo que *se quería hacer*.

3. **Solo 1/6 mecanismos (trade-off explícito) documenta múltiples alternativas con criterios**. Es el único que se aproxima a una "decisión racional" documentada.

4. **Los mecanismos no son entidades abstractas**. Son descripciones de lo que ocurrió: "alguien detectó solapamiento", "alguien dijo que era demasiado grande", "una métrica mostraba una diferencia abrumadora".

---

## Lo que NO se ha demostrado

1. **Que estos 6 mecanismos agoten los tipos posibles**. Otra muestra podría revelar mecanismos diferentes (conflicto, financiación, presión externa, etc.).

2. **Que los mecanismos sean generalizables**. Todos provienen de proyectos de software científico de código abierto.

3. **Que el mecanismo sea la causa de la explicación**. Podría ser un correlato: donde hay buena documentación, aparecen mecanismos claros; donde no la hay, no aparecen.

---

## Pregunta abierta para Sprint 54

```
¿Con qué frecuencia aparece
cada mecanismo de selección
en una muestra más amplia?
```

Esto requeriría ampliar la muestra más allá de los 11 casos actuales para medir frecuencias y determinar si algún mecanismo es dominante.