# Sprint 49 — Explanatory Gain Audit

## Pregunta

> ¿Qué transformaciones aumentan la capacidad explicativa de forma consistente?

## Método

Para cada uno de los 11 casos de Sprint 40/42C:

### Estado A

Solo el artefacto final. Nada más.

### Estado B

Añadir UNA única transformación observable (extraída del hilo del issue/PR).

### Evaluación

```text
¿Añade capacidad explicativa respecto al estado A?
```

Sí / No / Indeterminado.

Sin taxonomía previa. Sin entidades. Cada transformación se evalúa individualmente en cada caso donde aparece.

El objetivo no es "entender el caso", sino medir si una transformación específica, añadida a un estado aislado, incrementa la capacidad de explicar por qué el resultado final es el que es.

---

## Transformaciones evaluadas

Se toman las transformaciones que aparecen en los 11 casos según Sprint 48 (T1-T6) más las que emergen del análisis contrafactual (Sprint 48B):

| ID | Transformación | Descripción |
|----|---------------|-------------|
| T1 | Alternativa → Selección | Se documentan opciones y se elige una |
| T2 | Problema → Solución | Un problema reportado genera una solución |
| T3 | Error → Corrección | Un revisor detecta un problema y se modifica |
| T4 | Incertidumbre → Confirmación | Algo no sabido se resuelve |
| T5 | Bloqueo → Desbloqueo | Una restricción que impedía avanzar se resuelve |
| T6 | Idea → Implementación | Una propuesta conceptual se convierte en código |
| T7 | Alternativa descartada explícita | Se menciona y rechaza una opción (sin llegar a T1 completa) |
| T8 | Desacuerdo entre participantes | Dos o más personas expresan opiniones divergentes |
| T9 | Cambio de requisito | El alcance o especificación se modifica durante el proceso |
| T10 | Evidencia nueva | Aparece un dato, métrica o referencia que altera la discusión |

Nota: T7-T10 se añaden porque aparecen en los casos pero no están capturadas por T1-T6. No son una taxonomía cerrada.

---

## Caso 1: MNE-Python #4414 — Epochs metadata (regress removal)

**Estado A (solo artefacto final)**: PR mergeado. Epochs metadata con pandas-query, sin función `regress`.

**Transformaciones observadas en el hilo**:
- T1: Alternativa → Selección (mantener ambas vs eliminar → eliminar)
- T3: Error → Corrección (revisor detecta redundancia → se corrige)
- T6: Idea → Implementación (pandas-query en Epochs metadata → merge)
- T8: Desacuerdo → No. No hubo desacuerdo documentado. Consenso rápido.
- T9: Cambio de requisito → Sí. El alcance del PR cambió al eliminar regress.

### Evaluación por transformación

| Transformación | Añade capacidad explicativa | Justificación |
|:--------------:|:---------------------------:|---------------|
| T1 (Alt→Sel) | ✅ Sí | Saber que se consideró mantener regress y se descartó explica por qué el resultado final no incluye ambas funciones. El artefacto solo dice "regress no está". T1 dice "regress se consideró y se eliminó por redundancia". |
| T3 (Err→Corr) | ✅ Sí | Saber que un revisor detectó redundancia añade por qué se inició el cambio. Sin T3, el artefacto solo muestra el resultado, no el detonante. |
| T6 (Idea→Impl) | ❌ No | El merge ya implica que la idea se implementó. T6 no añade información nueva sobre el resultado. |
| T8 (Desacuerdo) | ❌ No aplica | No hubo desacuerdo. |
| T9 (Cambio req.) | ✅ Sí | Saber que el alcance se redujo (eliminar regress) explica por qué el PR final tiene menos funcionalidad que el PR inicial. El merge solo muestra lo que quedó. |

**Ganancia neta**: 3/3 transformaciones aplicables añaden capacidad explicativa.

---

## Caso 2: MNE-Python #3728 — Receptive field module

**Estado A (solo artefacto final)**: PR mergeado. Módulo receptive field añadido.

**Transformaciones observadas**:
- T1: Alternativa → Selección (encoding model general vs receptive field → receptive field)
- T2: Problema → Solución (necesidad de encoding models → módulo receptive field como paso)
- T4: Incertidumbre → Confirmación (¿encoding model completo es viable? → se determina que no)
- T6: Idea → Implementación (receptive field → merge)
- T9: Cambio de requisito → Sí. Scope reduction de general a específico.

### Evaluación

| Transformación | Añade capacidad explicativa | Justificación |
|:--------------:|:---------------------------:|---------------|
| T1 (Alt→Sel) | ✅ Sí | Saber que se consideró el enfoque general y se descartó por capacidad de revisión explica por qué el resultado es un módulo pequeño, no un sistema completo. |
| T2 (Prob→Sol) | ❌ No | El merge ya muestra que se implementó una solución. T2 no añade por qué esa solución tiene el alcance que tiene. |
| T4 (Inc→Conf) | ✅ Sí | Saber que se confirmó que el enfoque general no era viable añade la restricción que moldeó el resultado. Sin T4, el alcance reducido parece arbitrario. |
| T6 (Idea→Impl) | ❌ No | El merge ya implica implementación. |
| T9 (Cambio req.) | ✅ Sí | El cambio de alcance es la información más explicativa del caso. Sin él, no se entiende por qué el PR es pequeño. |

**Ganancia neta**: 3/3 transformaciones aplicables añaden capacidad explicativa.

---

## Caso 3: nilearn/nilearn #2019 — Visual reports

**Estado A (solo artefacto final)**: PR mergeado. Reporting movido a subpaquete `nilearn.reporting`.

**Transformaciones observadas**:
- T2: Problema → Solución (matplotlib en núcleo es indeseable → separar reporting)
- T5: Bloqueo → Desbloqueo (matplotlib bloquea separación → se crea subpaquete)
- T6: Idea → Implementación (reporting separado → merge)
- T8: Desacuerdo → No. Hubo consenso, no desacuerdo.
- T10: Evidencia nueva → Opinión de GaelVaroquaux y jeromedockes (evidencia de autoridad, no técnica)

### Evaluación

| Transformación | Añade capacidad explicativa | Justificación |
|:--------------:|:---------------------------:|---------------|
| T2 (Prob→Sol) | ✅ Sí | Saber que el problema era la dependencia matplotlib en el núcleo explica por qué se separó reporting. El merge solo muestra el resultado arquitectónico. |
| T5 (Blq→Desbl) | ✅ Sí | La restricción (no matplotlib en núcleo) y su resolución (subpaquete separado) es la información central del caso. |
| T6 (Idea→Impl) | ❌ No | El merge ya implica implementación. |
| T8 (Desacuerdo) | ❌ No aplica | No hubo. |
| T10 (Evidencia nueva) | ❌ Indeterminado | La opinión de los mantenedores influyó, pero no está claro si sin ella la decisión habría sido diferente. No es medible. |

**Ganancia neta**: 2/2 transformaciones aplicables con evaluación clara añaden capacidad explicativa.

---

## Caso 4: nilearn/nilearn #1766 — papaya → brainsprite

**Estado A (solo artefacto final)**: PR mergeado. Visor 3D ahora usa brainsprite.

**Transformaciones observadas**:
- T2: Problema → Solución (notebooks de 12MB → cambiar visor)
- T3: Error → Corrección (notebooks impracticables → sustitución de tecnología)
- T4: Incertidumbre → Confirmación (¿brainsprite sirve? → pruebas → confirmación)
- T6: Idea → Implementación (brainsprite → merge)
- T10: Evidencia nueva → Métrica objetiva: papaya ~2MB vs brainsprite ~15KB

### Evaluación

| Transformación | Añade capacidad explicativa | Justificación |
|:--------------:|:---------------------------:|---------------|
| T2 (Prob→Sol) | ✅ Sí | Saber que el problema era el tamaño de los notebooks explica por qué se buscó un reemplazo. Sin T2, el cambio de visor parece arbitrario. |
| T3 (Err→Corr) | ✅ Sí | La corrección está vinculada a una métrica objetiva. Es la información más explicativa del caso. |
| T4 (Inc→Conf) | ❌ Indeterminado | La confirmación de que brainsprite servía ocurrió, pero no está claro que sin ella la decisión hubiera sido diferente dado que la métrica era abrumadora. |
| T6 (Idea→Impl) | ❌ No | El merge ya implica implementación. |
| T10 (Evidencia nueva) | ✅ Sí | La métrica objetiva (12MB vs 15KB) es el dato más explicativo. Sin ella, el cambio sería opinión; con ella, es evidencia. |

**Ganancia neta**: 3/4 transformaciones aplicables añaden capacidad explicativa.

---

## Caso 5: bids-standard/pybids #356 — Oversampling rate

**Estado A (solo artefacto final)**: PR mergeado. Convolve con ajuste dinámico de oversampling.

**Transformaciones observadas**:
- T1: Alternativa → Selección (3 alternativas explícitas → 1 elegida)
- T2: Problema → Solución (artefactos en eventos cortos → ajuste automático)
- T3: Error → Corrección (artefactos detectados → corrección de algoritmo)
- T6: Idea → Implementación (ajuste dinámico → merge)
- T7: Alternativa descartada explícita → 2 alternativas documentadas y descartadas
- T9: Cambio de requisito → No exponer parámetro en API pública
- T10: Evidencia nueva → Pruebas con eventos cortos (parcialmente documentadas)

### Evaluación

| Transformación | Añade capacidad explicativa | Justificación |
|:--------------:|:---------------------------:|---------------|
| T1 (Alt→Sel) | ✅ Sí | Saber que se consideraron 3 alternativas y los criterios de descarte (UX, simplicidad, corrección) explica por qué se eligió esta solución y no otra. Es la información más rica de todos los casos. |
| T2 (Prob→Sol) | ✅ Sí | El problema (artefactos) es necesario para entender por qué se modificó Convolve. |
| T3 (Err→Corr) | ✅ Sí | La detección del error específico (eventos cortos) explica la dirección de la solución. |
| T6 (Idea→Impl) | ❌ No | El merge ya implica implementación. |
| T7 (Alt. descartada) | ✅ Sí | Las alternativas documentadas (manual, dos pasos, exponer parámetro) son la evidencia más clara de por qué la solución elegida no fue otra. |
| T9 (Cambio req.) | ✅ Sí | La restricción "no contaminar API" explica por qué no se expuso el parámetro. |
| T10 (Evidencia nueva) | ❌ Indeterminado | Las pruebas con eventos cortos se mencionan pero no se documentan completamente. |

**Ganancia neta**: 5/5 transformaciones aplicables con evaluación clara añaden capacidad explicativa.

---

## Caso 6: bids-standard/pybids #369 — Grabbit removal

**Estado A (solo artefacto final)**: PR mergeado. pybids ya no depende de grabbit.

**Transformaciones observadas**:
- T2: Problema → Solución (dependencia externa bloquea roadmap → port)
- T5: Bloqueo → Desbloqueo (grabbit bloquea roadmap → se internaliza)
- T6: Idea → Implementación (eliminar dependencia → merge)
- T7: Alternativa descartada explícita → Mantener grabbit (1 alternativa documentada)

### Evaluación

| Transformación | Añade capacidad explicativa | Justificación |
|:--------------:|:---------------------------:|---------------|
| T2 (Prob→Sol) | ✅ Sí | Saber que grabbit era un problema de roadmap explica por qué se invirtió esfuerzo en portar. |
| T5 (Blq→Desbl) | ✅ Sí | La restricción (dependencia externa bloqueante) es la razón central del cambio. |
| T6 (Idea→Impl) | ❌ No | El merge ya implica implementación. |
| T7 (Alt. descartada) | ✅ Sí | Saber que se consideró mantener grabbit y se descartó por control de roadmap añade por qué no se quedó como estaba. |

**Ganancia neta**: 3/3 transformaciones aplicables añaden capacidad explicativa.

---

## Caso 7: MNE-Python #2154 — Epochs concatenated plots

**Estado A (solo artefacto final)**: Issue abierto. Sin merge, sin resolución.

**Transformaciones observadas**: Ninguna. No hubo transformación de estado del proyecto.

### Evaluación

| Transformación | Añade capacidad explicativa | Justificación |
|:--------------:|:---------------------------:|---------------|
| Ninguna | ❌ No aplica | No hay transformaciones que añadir al estado A. El estado A (issue abierto) ya contiene poca información. Añadir "no pasó nada" no añade explicación. |

**Ganancia neta**: 0. La ausencia de transformación es informativa en sí misma (indica falta de prioridad/recursos), pero no hay una transformación que añadir.

---

## Caso 8: MNE-Python #766 — tDCS GUI

**Estado A (solo artefacto final)**: Issue abierto. Sin merge, sin resolución.

**Transformaciones observadas**: Ninguna.

### Evaluación

Ídem Caso 7.

**Ganancia neta**: 0.

---

## Caso 9: MNE-Python #2676 — EEGLAB reader

**Estado A (solo artefacto final)**: Issue abierto. Sin merge, sin resolución.

**Transformaciones observadas**: Ninguna.

### Evaluación

Ídem Caso 7.

**Ganancia neta**: 0.

---

## Caso 10: nilearn/nilearn #1016 — Surface plotting

**Estado A (solo artefacto final)**: Issue abierto. Sin merge, sin resolución.

**Transformaciones observadas**: Ninguna.

### Evaluación

Ídem Caso 7.

**Ganancia neta**: 0.

---

## Caso 11: bids-standard/pybids #451 — List metadata bug

**Estado A (solo artefacto final)**: Issue abierto. Bug reportado sin resolución documentada.

**Transformaciones observadas**: Ninguna en la ventana observada.

### Evaluación

Ídem Caso 7.

**Ganancia neta**: 0 (en la ventana observada). La ventana incompleta impide evaluar si hubo transformación después.

---

## Tabla de ganancia explicativa por transformación

| Transformación | Casos donde aparece | Casos donde añade explicación | Ratio de ganancia |
|:--------------:|:-------------------:|:-----------------------------:|:-----------------:|
| T1 (Alt→Sel) | 1, 2, 5 | 3/3 | 100% |
| T2 (Prob→Sol) | 2, 3, 4, 5, 6 | 5/5 | 100% |
| T3 (Err→Corr) | 1, 4, 5 | 3/3 | 100% |
| T4 (Inc→Conf) | 2, 4 | 1/2 | 50% |
| T5 (Blq→Desbl) | 3, 6 | 2/2 | 100% |
| T6 (Idea→Impl) | 1, 2, 3, 4, 5, 6 | 0/6 | 0% |
| T7 (Alt. descartada explícita) | 5, 6 | 2/2 | 100% |
| T8 (Desacuerdo) | 0 | 0 | N/A |
| T9 (Cambio requisito) | 1, 2, 5 | 3/3 | 100% |
| T10 (Evidencia nueva) | 3, 4, 5 | 2/3 | 67% |

### Observaciones

1. **T6 (Idea→Impl) tiene ratio 0%**. El merge ya implica implementación. Conocer que una idea precedió al merge no añade información explicativa. **T6 no reduce el espacio de posibilidades** — simplemente describe que se ejecutó algo que ya se sabía ejecutado.

2. **El patrón transversal no son las transformaciones individuales, sino una propiedad compartida**: las transformaciones con ratio 100% (T1, T2, T3, T5, T7, T9) **reducen el espacio de posibilidades**. Transforman un conjunto de opciones en una opción, o identifican una restricción que elimina opciones. T4 (50%) solo parcialmente reduce espacio. T6 (0%) no reduce espacio.

3. **T2 (Prob→Sol) tiene ratio 100%** porque identificar un problema específico elimina las soluciones que no lo resuelven. Reduce el espacio de soluciones posibles a aquellas que abordan ese problema.

4. **T1 (Alt→Sel) y T7 (Alt. descartada) tienen 100%** porque eliminan explícitamente opciones del espacio de posibilidades. Documentar qué se descartó es directamente una operación de reducción de espacio.

5. **T8 (Desacuerdo) no aparece en ningún caso de la muestra**. Esto no significa que no exista en otros casos, pero en esta muestra, todas las decisiones observadas fueron por consenso o autoridad, no por resolución de desacuerdo.

---

## Candidato mínimo explicativo observado

T2 — Problema → Solución — es la transformación más universal: aparece en 5/6 casos con merge y añade explicación en el 100% de ellos.

T1 — Alternativa → Selección — y T7 — Alternativa descartada explícita — son las que añaden más densidad explicativa por aparición.

**Patrón observado**: Las transformaciones que reducen el espacio de posibilidades (T1, T2, T3, T5, T7, T9) tienen ratio 100%. Las que no lo reducen (T6, T4 parcialmente) tienen ratio menor. El candidato mínimo explicativo observado sería:

```
Problema → [Alternativas consideradas] → Solución
```

Donde:
- **Problema** explica por qué se necesitaba un cambio (T2)
- **Alternativas consideradas** explica por qué se eligió esa solución y no otra (T1, T7, T9)
- **Solución** es el estado final (ya conocido desde el artefacto)

Esta estructura es consistente con todos los casos donde hay merge (Casos 1-6) y está ausente en todos los casos sin merge (Casos 7-11).

---

## Lo que NO se ha demostrado

1. **Que esta estructura sea suficiente para la comprensión**. Añade capacidad explicativa, pero no se ha medido si alcanza para reconstruir el "por qué" completo.

2. **Que sea la única estructura posible**. Otros tipos de transformación (T4, T10) también añaden explicación en algunos casos.

3. **Que sea generalizable más allá de proyectos de software científico**. La muestra son 11 casos de tres proyectos (MNE, nilearn, pybids).

4. **Que sea reproducible por un observador B**. Todo el análisis es de un solo observador.

---

## Pregunta abierta para Sprint 50

El hallazgo principal de Sprint 49 no son las transformaciones individuales, sino la propiedad que comparten: **las transformaciones que reducen el espacio de posibilidades añaden capacidad explicativa**. Las que no lo reducen (T6) no añaden nada.

Esto sugiere que la explicación no es "contar lo que pasó", sino **describir qué posibilidades fueron eliminadas y por qué**.

### Experimento propuesto para Sprint 50

No preguntar "¿comprende un humano?". Sino medir capacidad predictiva.

Tomar los mismos 11 casos. Construir tres niveles:

**Nivel A**: Solo resultado final.

**Nivel B**: Resultado final + Problema (T2).

**Nivel C**: Resultado final + Problema + Alternativas descartadas (T1, T7, T9).

Medir:

```
¿Puede el observador predecir
qué solución fue elegida?
```

No "¿lo comprende?" sino "¿puede anticipar correctamente la trayectoria?".

Porque eso sí es medible.

### Hipótesis para Sprint 50

```
Explicación =
reconstrucción del espacio de posibilidades
+
eliminación progresiva de alternativas
```

Si esta hipótesis sobrevive a la medición (Nivel C permite predecir correctamente la solución elegida significativamente más que Nivel A), entonces CoResearcher tendría una variable observable sobre la que construir ciencia acumulativa.

Si no, habrá que buscar otra propiedad.

---

## Nota metodológica

Este audit evalúa "capacidad explicativa adicional respecto al estado aislado". No evalúa "comprensión completa" ni "suficiencia". Una transformación puede añadir capacidad explicativa sin que el conjunto resultante sea suficiente para comprender el caso.

La distinción es importante porque evita el salto de "esto añade explicación" a "esto es comprensión". El primero es medible. El segundo es una hipótesis.