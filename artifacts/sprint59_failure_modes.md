# Sprint 59 — Falsification Repository Set

## Objetivo

Buscar repositorios donde Coresearcher fracase.

No buscar éxitos.

Buscar límites.

---

## Dataset de falsificación

Mínimo: 20 repositorios distribuidos en categorías de riesgo.

### Categorías

| Categoría | Característica | Riesgo |
|-----------|----------------|--------|
| Proyectos maduros | Mucha historia, muchos PRs | Ruido excesivo |
| Proyectos abandonados | Sin actividad reciente | Información incompleta |
| Proyectos personales | Sin issues, sin PRs | Sin trazabilidad |
| Repositorios científicos | Enfoque en datos, no código | Estructura no estándar |
| Sin issues | No hay discusión pública | Sin decisiones observables |
| Sin PRs | Sin revisión de código | Sin alternativas observables |
| Squash merges | Historia lineal, sin ramas | Sin contexto de decisión |
| Documentación pobre | Sin README, sin docs | Sin contexto declarado |

---

## Repositorios seleccionados

### Proyectos maduros
1. **tensorflow/tensorflow** — Mucha historia, muchos PRs
2. **numpy/numpy** — Proyecto estable, muchos issues
3. **pandas-dev/pandas** — Proyecto maduro, decisiones arquitectónicas

### Proyectos abandonados
4. **docker/docker** — Archivado, movido a moby/moby
5. **nodejs/node** — Antiguo, mucha historia migrada

### Proyectos personales
6. **karpathy/nn** — Proyecto personal de Andrej Karpathy
7. **fchollet/keras** — Antes personal, ahora corporativo

### Repositorios científicos
8. **scikit-learn/scikit-learn** — Enfoque científico, muchos PRs
9. **matplotlib/matplotlib** — Proyecto científico, historia larga

### Sin issues
10. **torvalds/subsurface-for-dirk** — Proyecto personal sin issues

### Sin PRs
11. **torvalds/linux** — Desarrollo monolítico, sin PRs tradicionales

### Squash merges
12. **facebook/react** — Usa squash merges extensivamente

### Documentación pobre
13. **catmeme/Collatz conjecture** — Proyecto personal sin docs

### Repositorios pequeños
14. **pallets/flask** — Proyecto pequeño pero activo
15. **django/django** — Proyecto maduro, estructura compleja

### Repositorios con decisiones fuera de GitHub
16. **apache/spark** — Discusión en mailing lists
17. **rust-lang/rust** — RFC process fuera de GitHub issues

### Proyectos con commits monolíticos
18. **torvalds/linux** — Commits grandes, poca división

### Proyectos con migración de plataforma
19. **jenkinsci/jenkins** — Migrado de Java.net a GitHub

### Proyectos con estructura no estándar
20. **git/git** — Desarrollo basado en patches, no PRs

---

## Métricas de falsificación

Para cada repositorio:

```json
{
  "repo": "...",
  "category": "...",
  "decisions_found": 0,
  "alternatives_found": 0,
  "criteria_found": 0,
  "gaps_found": 0,
  "precision_observable": 0.0,
  "failure_mode": "..."
}
```

---

## Modos de fallo esperados

### 1. Sin discusión pública
- **Patrón**: Sin issues, sin PRs, sin discusión
- **Resultado esperado**: 0 decisiones, 0 alternativas, 0 criterios
- **Ejemplo**: proyectos personales sin issues

### 2. Squash merge puro
- **Patrón**: Todos los PRs usan squash merge
- **Resultado esperado**: Historia lineal, sin contexto de iteración
- **Ejemplo**: facebook/react

### 3. Desarrollo monolítico
- **Patrón**: Commits grandes, sin división en PRs
- **Resultado esperado**: Decisiones no atribuibles a issues/PRs
- **Ejemplo**: torvalds/linux

### 4. Discusión externa
- **Patrón**: Decisiones en mailing lists, no en GitHub
- **Resultado esperado**: Trazabilidad rota
- **Ejemplo**: apache/spark, rust-lang/rust

### 5. Proyecto archivado
- **Patrón**: Sin actividad reciente, información incompleta
- **Resultado esperado**: Gaps masivos
- **Ejemplo**: docker/docker

---

## Resultado esperado

Identificar patrones de fracaso.

No todos los repositorios deben producir Trajectory Reports útiles.

El objetivo es encontrar dónde el sistema deja de funcionar.

---

## Entregable

```text
artifacts/sprint59_failure_modes.md
```

Este documento.

---

## Próximo paso

Si el sistema falla en más del 50% de los repositorios de alto riesgo, se necesita:

1. Mejorar la clasificación epistemológica (Sprint 58)
2. Añadir fuentes adicionales (Sprint 60: Zenodo)
3. Aceptar que GitHub solo no es suficiente

Si el sistema funciona en más del 70% de los repositorios, se puede escalar.
