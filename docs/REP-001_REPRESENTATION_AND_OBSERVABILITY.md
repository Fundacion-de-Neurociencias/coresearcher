# REP-001 — Representación y Observabilidad

**Status**: CANDIDATE  
**EpistemicStatus**: UNKNOWN  
**Evidencia**: Observación arquitectónica  

---

## Observación

Los grandes avances científicos históricos parecen coincidir con cambios de representación.

```text
Nueva representación
→ nuevo espacio observable
→ nuevas restricciones observables
→ nuevas preguntas falsables
```

### Ejemplos históricos

| Científico | Cambio de representación | Nuevo espacio observable |
|------------|--------------------------|-------------------------|
| Euclides | Axiomática geométrica | Relaciones deducibles, teoremas imposibles de ver sin axiomas |
| Euler-Lagrange | Física como optimización | Espacio de trayectorias, principio de mínima acción |
| Einstein | Fuerza gravitatoria → geometría del espacio-tiempo | Curvatura, agujeros negros, ondas gravitacionales |
| Schrödinger | Partículas → funciones de onda | Estados cuánticos, superposición, entrelazamiento |
| Yang-Mills | Campos aislados → simetrías gauge | Interacciones gauge, bosones de gauge, confinamiento |

**Lo común no es la ecuación. Lo común es:**

```text
Nueva representación
→ aparecen nuevas invariantes
→ aparecen nuevas restricciones
→ aparecen nuevas predicciones
```

---

## Pregunta abierta

¿Qué observaciones permanecen invisibles porque la representación actual de CoResearcher no las hace visibles?

---

## Inventario de visibilidad por artefacto

Para cada artefacto actual, documentar qué hace visible y qué hace invisible.

**Resultado permitido:** `VISIBLE`, `INVISIBLE`, `UNKNOWN`

### EvidenceGraph

| Dimensión | Estado | Nota |
|-----------|--------|------|
| Claims anclados a evidencia | VISIBLE | 591 claims anclados en artifacts |
| Cadenas de evidencia | VISIBLE | 426 edges reconstruidos |
| Confianzas | VISIBLE | trust scores por claim |
| Discontinuidades | INVISIBLE | No representa saltos cualitativos entre paradigmas |
| Restricciones subyacentes | INVISIBLE | No distingue entre convergencia por restricción real vs convergencia por ruido |
| Estructura profunda | UNKNOWN | No se han analizado patrones ocultos en la topología del grafo |

### DecisionGraph / Trajectory

| Dimensión | Estado | Nota |
|-----------|--------|------|
| Trayectorias reconstructibles | VISIBLE | 301 DecisionNodes reconstruidos |
| Secuencias temporales | VISIBLE | DAG cronológico con edges tipados |
| Convergencias | VISIBLE | 4 convergencias detectadas |
| Gaps epistémicos | VISIBLE | 155 gaps detectados |
| Contraejemplos | INVISIBLE | No se registran alternativas descartadas explícitamente |
| Estructura de bifurcaciones | INVISIBLE | Ramas no exploradas no son representadas |
| Direccionalidad profunda | UNKNOWN | No se ha medido la topología del espacio de decisiones |

### Convergence

| Dimensión | Estado | Nota |
|-----------|--------|------|
| Convergencias detectables | VISIBLE | 4 convergencias observadas |
| Actores independientes | VISIBLE | ≥2 actores por convergencia |
| Temas recurrentes | VISIBLE | Agrupación por Jaccard de títulos |
| Restricciones compartidas | INVISIBLE | 0/4 convergencias tienen restricción identificada |
| Éxito vs barrera | VISIBLE | 0/4 exitosas, 4/4 barrier convergences |
| Mecanismos causales | INVISIBLE | No se explica por qué convergen |

### Gap

| Dimensión | Estado | Nota |
|-----------|--------|------|
| Gaps detectables | VISIBLE | 155 gaps, gap_density=0.515 |
| Severidad | VISIBLE | high/medium/low clasificados |
| Tipo epistémico | VISIBLE | empirical/causal/mathematical |
| Estado de exploración | VISIBLE | explored_abandoned/explored_partial/unknown |
| Restricciones subyacentes | INVISIBLE | Gaps son síntomas, no causas |
| Estructura del espacio ignorado | UNKNOWN | No se ha mapeado la topología de la ignorancia |

### Freezes

| Dimensión | Estado | Nota |
|-----------|--------|------|
| Boundaries documentados | VISIBLE | BOUNDARY_WITH_EDITXT.md, BOUNDARY_WITH_AI_SCIENTISTS.md |
| Operational Maxims | VISIBLE | 10 maxims documentados |
| Architecture Freeze | VISIBLE | ARCHITECTURE_FREEZE.md |
| Lo que no está congelado | INVISIBLE | No se lista explícitamente qué queda abierto |
| Tensión entre capas | UNKNOWN | No se han medido fricciones entre boundaries |

### Operational Maxims

| Dimensión | Estado | Nota |
|-----------|--------|------|
| Reglas documentadas | VISIBLE | 10 maxims en OPERATIONAL_MAXIMS.md |
| Aplicación práctica | VISIBLE | Referenciadas en scripts y artefactos |
| Excepciones | INVISIBLE | No se registran violaciones o excepciones |
| Efectividad | UNKNOWN | No se ha medido impacto de cada maxim |

---

## Pregunta reformulada para el IDE

```text
¿Qué observables están ausentes no por imposibilidad lógica,
sino por elección de representación?
```

**No pedir:** Nueva representación.  
**No pedir:** Nuevo esquema.  
**Solo pedir:** Inventario de lo invisible.

---

## Acción

Ninguna.  
Estado CANDIDATE hasta que aparezcan múltiples casos donde distintas líneas de trabajo converjan sobre la misma observación de invisibilidad.

---

*Creado: 2026-08-06*  
*Evidence: Ninguna (observación arquitectónica)*