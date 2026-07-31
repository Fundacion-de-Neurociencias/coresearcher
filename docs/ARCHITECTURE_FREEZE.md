# ARCHITECTURE FREEZE
**Effective Date**: 2026-07-30  
**Status**: ACTIVE — No new schemas, documents, or layers without explicit supervisor approval  
**Authority**: Manuel (Project Supervisor)

---

## Directive

**STOP adding architecture.**

The bottleneck of CoResearcher is no longer conceptual. It is empirical.

All schemas, documents, and layer definitions produced during SPRINT PLATFORM-01, SPRINT 60A, SPRINT 60B, and SPRINT 60D are **STABLE** and **FROZEN**.

No new schemas.
No new documents.
No new layers.
No new graphs.

---

## What is Stabilized (Do Not Modify)

### Constitutional Principles
- Observable
- Derivable  
- Inferido (restricted)
- Desconocido

### Mission
> Reconstruir la fracción auditablemente recuperable de la historia de un proyecto.

### Boundaries
- CoResearcher ≠ AI Scientist
- CoResearcher ≠ Reviewer
- CoResearcher ≠ Manuscript Assistant

### Core Artifact
- EvidenceGraph (v1.1.0)

### Approved Extension
- DecisionNode (with Decision Traceability Principle: Observable or Derivable, never Inferido)

---

## What is NOT Stabilized (Requires Empirical Validation)

### H6: Decision Reconstruction
> Las decisiones son reconstruibles.

**Status**: Modelado, no demostrado  
**Action**: SPRINT 60C — Validar con 20+ repositorios reales

### H7: Branch Detection  
> Las bifurcaciones son reconstruibles.

**Status**: Exploratorio (SPRINT 60D documentado, no ejecutado)  
**Action**: Depende de H6. No ejecutar hasta validar H6.

### H8: Convergence Detection
> Las convergencias son reconstruibles.

**Status**: Exploratorio  
**Action**: Depende de H6 y H7. No ejecutar hasta validar H6 y H7.

### H9: Trajectory Value
> La trayectoria aporta más valor que la evidencia simple.

**Status**: Hipótesis  
**Action**: Evaluar después de SPRINT 60C

---

## Active Sprint: SPRINT 60C

### Objective
Falsar o validar H6 mediante análisis de repositorios reales.

### Targets
- Mínimo 20 repositorios
- Extraer DecisionNodes observables
- Medir: decision_reconstruction_rate, decision_source_distribution, trajectory_completeness

### Questions to Answer
1. ¿Cuántas decisiones observables aparecen?
2. ¿Cuántas decisiones pueden reconstruirse?
3. ¿Dónde aparecen? (Issue, PR, Commit, Release, Discussion, Zenodo)
4. ¿Qué porcentaje queda desconocido?

### Success Criteria
- decision_reconstruction_rate ≥ 70%
- Identificación de fuentes primarias (issues vs PRs vs commits)
- Dataset público reproducible para futuros sprints

---

## Post-SPRINT 60C Decision Tree

```
Si H6 se valida (≥70% reconstrucción):
  → Considerar DecisionGraph como capa separada
  → Evaluar H7 (Branch Detection) en SPRINT 61
  → Evaluar H8 (Convergence Detection) en SPRINT 62

Si H6 falla (<70% reconstrucción):
  → DecisionNode queda como metadato secundario
  → No ejecutar H7/H8
  → Reenfocar en reconstrucción de claims (core mission)
```

---

## Prohibited Activities (During Freeze)

❌ Añadir nuevos nodos a EvidenceGraph  
❌ Añadir nuevos grafos  
❌ Añadir nuevas capas arquitectónicas  
❌ Crear nuevos schemas  
❌ Modificar schemas existentes sin bug fix explícito  
❌ Escribir documentos de arquitectura teórica  
❌ Planificar sprints beyond SPRINT 61  
❌ Ejecutar SPRINT 60D (Branch Detection)

---

## Permitted Activities

✅ Ejecutar SPRINT 60C (análisis empírico)  
✅ Escribir scripts de extracción  
✅ Escribir scripts de validación  
✅ Escribir informes de resultados  
✅ Corregir bugs en schemas existentes  
✅ Mejorar algoritmos de extracción (no cambiar schemas)  
✅ Documentar hallazgos empíricos

---

## Exit Conditions from Freeze

El freeze se levanta cuando:

1. **SPRINT 60C completado** con métricas cuantitativas
2. **H6 validada o falsada** empíricamente
3. **Decisión tomada** sobre continuar con DecisionGraph o mantener DecisionNode como extensión

Solo después de esas 3 condiciones, se puede reconsiderar arquitectura.

---

## Motivation

El objetivo de CoResearcher no es construir el grafo más elegante.

Es demostrar empíricamente que puede reconstruir trayectorias de investigación a partir de evidencia pública.

Hasta que eso no se demuestre, cualquier capa adicional es premature optimization.

---

## Version History

- v1.0 (2026-07-30): Architecture freeze declared. SPRINT 60C as priority.

---

*This directive is effective immediately. All team members must comply. Violations require explicit supervisor approval.*