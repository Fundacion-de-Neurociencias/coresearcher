# Sprint 43 — Counterevidence Analysis

## Objetivo

Buscar evidencia en los sprints que indique:
- que los artefactos sí bastan
- que las decisiones sí bastan
- que la coordinación sí basta

---

## 1. ¿Los artefactos sí bastan?

### Evidencia buscar: ¿Artefactos → Comprensión funciona?

**No se encontró evidencia que los artefactos por sí solos den comprensión.**

### Evidencia contraria documentada:

#### Sprint 27
- "reconstruction extracted development metadata (issues/PRs), not scientific artifacts"
- "Scientific evidence: 0" en todos los repos analizados
- Los artefactos sin contexto de evidencia científica no explican el proyecto

#### Sprint 30
- 61 artefactos produjeron 57 programas distintos
- program-0: "spanning 0 repositories" con 1 dataset - agrupación sin sentido
- Papers irrelevantes mezclados ("Market Microstructure Noise" en bids-examples)

#### Sprint 31
- El problema es el mismo que Sprint 30: el algoritmo cambió, pero la falta de comprensión persiste
- "bids-examples" asociado a papers no relacionados

#### Sprint 42 (project_state)
- "The artifacts themselves do not explain a project"
- "Los artefactos por sí solos no explican un proyecto"

### Conclusión parcial:
**No hay evidencia de que los artefactos por sí solos produzcan comprensión.**

---

## 2. ¿Las decisiones sí bastan?

### Evidencia buscar: ¿Decisiones → Coordinación total funciona?

**No se encontró evidencia de que las decisiones cubran toda la coordinación.**

### Evidencia contraria documentada:

#### Sprint 40
- 6/11 casos tienen "Resolved Trade-off" explícito
- 5/11 casos NO tienen decisión explícita pero son actividades reales:
  - Iterative Implementation Discussion
  - Technical Q&A / Knowledge Exchange
  - Bug Investigation Coordination
  - Status / Progress Update
  - Implementation Detail Negotiation

#### Sprint 40B (coordination_patterns)
- "Los 5 casos sin 'Resolved Trade-off' tampoco son 'ruido'"
- "La coordinación en proyectos científicos es multiparadigma, no monocausal"
- Los patrones no-decisionales representan formas diferentes de coordinación:
  - Status exchange
  - Knowledge exchange
  - Implementation negotiation

### Conclusión parcial:
**No hay evidencia de que las decisiones explícitas sean suficientes para comprender la coordinación total. Los 5 casos sin decisión explícita son actividades observables pero no capturadas por el foco en trade-offs.**

---

## 3. ¿La coordinación sí basta?

### Evidencia buscar: ¿Coordinación → Comprensión funciona?

**No se encontró evidencia de que la coordinación implique comprensión.**

### Evidencia contraria documentada:

#### Sprint 39B (threats_to_validity)
- Construct Validity CRITICAL: "measures retrieval, not comprehension"
- "This is equivalent to reading the answer key instead of the textbook"
- La coordinación observada (issues/PRs) no aporta comprensión, solo información

#### Sprint 42 (project_state)
- "Scientific Activity Reconstruction: Partially validated"
- "Project Comprehension: NOT validated"
- "Reasoning Reconstruction: Hypothesis"

### Evidencia limitada positiva:

#### Sprint 40B
- Los 11 casos observados muestran patrones de coordinación observables
- "This suggests that coordination in scientific projects is multiparadigm"
- PERO: no hay evidencia de que estos patrones sean suficientes para comprensión

### Conclusión parcial:
**No hay evidencia de que la coordinación observada sea suficiente para comprensión. Los patrones son observables, pero la relación causal con "entender el proyecto" no está establecida.**

---

## Evaluación global de contraejemplos

| Hipótesis | Contraejemplos encontrados | Evidencia que la confirma | Evidencia que la refuta |
|-----------|---------------------------|--------------------------|------------------------|
| Artefactos → Understanding | ❌ | - | "Scientific evidence: 0", "artifacts don't explain project" |
| Decisiones → Coordination | ❌ | - | "5/11 casos sin decisión explícita pero son coordinación" |
| Coordinación → Understanding | ❌ | - | "measures retrieval, not comprehension" |

---

## Contraejemplos significativos documentados

### Contraejemplo 1: Compression ≠ Comprehension (Sprint 39B)
- El ledger tiene 896x mejor tiempo que búsqueda raw
- Pero esto mide eficiencia de lookup, no comprensión
- Un diccionario es 896x más rápido que leer un libro, pero no te da comprensión

### Contraejemplo 2: Trade-off ≠ Única coordinación (Sprint 40)
- 5/11 casos (45%) de la muestra no tienen trade-off explícito
- Estos casos tienen patrones observables pero no son "decisiones"
- Si decisiones fueran suficientes, ¿por qué el 45% de actividad carece de ellas?

### Contraejemplo 3: Artefacto ≠ Propósito científico (Sprint 30/31)
- El mismo artefacto aparece en múltiples "programas" diferentes
- Papers irrelevantes aparecen como parte del programa científico
- Los artefactos no tienen capacidad intrínseca de agruparse en propósitos coherentes

---

## Nota sobre ausencia de evidencia positiva

**No se encontró evidencia en los sprints anteriores que respalde las hipótesis contrarias.**

Todas las falsaciones anteriores apuntan en la misma dirección:
- Los niveles inferiores (data, artifact, decision) no producen los niveles superiores (understanding, coordination, program)
- La relación no es causal sino que requiere información adicional
- Las categorías actuales (restricciones, incertidumbres, alternativas) también siguen sin validación inter-rater