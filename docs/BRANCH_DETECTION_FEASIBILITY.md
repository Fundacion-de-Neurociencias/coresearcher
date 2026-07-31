# BRANCH & CONVERGENCE DETECTION FEASIBILITY
**SPRINT 60D — Exploratory Analysis**  
**Objetivo**: Determinar si GitHub y Zenodo contienen señal suficiente para reconstruir bifurcaciones y convergencias de trayectoria sin inferencias no auditables  
**Status**: Exploratory — No Implementation Yet  
**Próximo Sprint**: Conditional on empirical results

---

## 1. Contexto Estratégico

CoResearcher actual reconstruye **trayectorias observadas**:

```text
Decision A → Decision B → Decision C
```

Surge una nueva pregunta:

```text
¿Qué alternativas quedaron sin explorar?
¿Existen convergencias entre trayectorias divergentes?
```

Esto sería:

```text
Espacio de posibilidades
```

no solo:

```text
Historia observada
```

**Pero**: CoResearcher NO debe inferir senderos hipotéticos. Toda bifurcación/convergencia debe derivarse de evidencia pública.

---

## 2. Definiciones Operacionales

### 2.1 Branch (Bifurcación)

**Branch Observable**: Una alternativa que fue explícitamente iniciada pero no completada.

```yaml
Tipos:
  - PR cerrado sin merge (issue, PR, commit evidences)
  - Rama eliminada (git branch evidence)
  - Issue abandonado (sin actividad >90 días)
  - RFC/Documento rechazado (explicit rejection)

Campos obligatorios:
  - branch_id: BRANCH-XXXXXX
  - source_decision: DECISION-XXXXXX (la decisión que originó la alternativa)
  - evidence: [issue_number, pr_number, commit_hash, branch_name]
  - outcome: abandoned | rejected | superseded | merged_elsewhere
  - observable_signals: array de eventos GitHub verificables

Ejemplo válido:
  branch_id: BRANCH-000001
  source_decision: DECISION-000042
  evidence:
    - issue: "Consider using pydantic v1"
    - pr: 8420
    - branch: feature/pydantic-v1
  outcome: abandoned
  observable_signals:
    - "PR #8420 closed without merge"
    - "Branch feature/pydantic-v1 deleted"
    - "Issue #8415 closed as wontfix"
```

**Branch Derivable**: Una alternativa inferida de patrones en la evidencia.

```yaml
Campos condicionales:
  - inferred_from: descripción de la inferencia
  - confidence: 0.5-0.8 (siempre < 1.0)
  - reasoning: evidencia explícita que soporta la inferencia

Ejemplo:
  branch_id: BRANCH-000002
  source_decision: DECISION-000043
  inferred_from: "Después de 3 PRs attempting SQLite, equipo switch a PostgreSQL"
  confidence: 0.7
  reasoning:
    - "PR #8450 closed: SQLite concurrency issues"
    - "PR #8451 closed: SQLite performance"
    - "PR #8452 merged: PostgreSQL adapter"
  outcome: abandoned
```

**Restricción constitucional**:
- Todo Branch debe tener ≥1 observable_signal
- No se permiten branches sin evidencia GitHub/Git
- Confidence ≤ 0.8 para derivable, =1.0 solo para observable

---

### 2.2 Convergence (Convergencia)

**Convergence Observable**: Dos trayectorias distintas que convergen en un mismo artifact o decisión, con evidencia explícita.

```yaml
Tipos:
  - Dos features que se mergean en same branch
  - Dos PRs que resuelven el mismo issue
  - Dos experimentos que producen el mismo artifact
  - Issue con "duplicate" label apuntando a otro

Campos obligatorios:
  - convergence_id: CONV-XXXXXX
  - branch_a: DECISION-XXXXXX o BRANCH-XXXXXX
  - branch_b: DECISION-XXXXXX o BRANCH-XXXXXX
  - convergence_point: ART-XXXXXX o DECISION-XXXXXX
  - evidence: array de eventos verificables

Ejemplo:
  convergence_id: CONV-000001
  branch_a: DECISION-000045 (Use SQLite)
  branch_b: DECISION-000046 (Use PostgreSQL)
  convergence_point: ART-000089 (database_adapter.py)
  evidence:
    - "PR #8453: Abstract SQL adapter supporting both"
    - "Commit abc123: Merge SQLite + PostgreSQL adapters"
    - "Issue #8440: Unify database layer"
```

**Convergence Derivable**: Patrón detectado por algoritmo sin declaración explícita.

```yaml
Ejemplo:
  convergence_id: CONV-000002
  branch_a: BRANCH-000010 (feature/pydantic-v1)
  branch_b: BRANCH-000011 (feature/pydantic-v2)
  convergence_point: DECISION-000050 (Adopt pydantic v2 with v1 compatibility)
  confidence: 0.65
  reasoning:
    - "Both branches implemented validation"
    - "Both branches were abandoned"
    - "Final solution incorporates elements from both"
```

**Restricción constitucional**:
- Toda convergencia debe tener ≥2 branches con evidencia independiente
- No se permiten convergencias inferidas de un solo artifact
- Convergence point debe ser un artifact o decisión observable

---

## 3. Hipótesis a Validar

### H7: Branch Detection

> Las trayectorias públicas contienen suficiente información para identificar bifurcaciones reales de investigación.

**Predicciones**:
1. ≥30% de repositorios activos tienen ≥1 branch observable (PR cerrado sin merge)
2. ≥50% de branches detectables tienen evidenciaIssue + PR + branch_name)
3. ≥70% de decisiones de cambio de approach generan branches

**Operacionalización**:
```python
branch_signals = [
  issue_closed_with_label("wontfix", "obsolete", "duplicate"),
  pr_closed_without_merge(),
  branch_deleted(),
  revert_commit()
]

branch_candidate = any(branch_signals)
```

### H8: Convergence Detection

> Existen convergencias observables entre trayectorias inicialmente divergentes.

**Predicciones**:
1. ≥20% de repositorios con ≥2 branches tienen ≥1 convergence
2. ≥60% de convergencias son detectables por algoritmo (no requieren LLM)
3. Convergence point es un artifact compartido (código, documento, dataset)

**Operacionalización**:
```python
convergence_signals = [
  same_issue_referenced_in_multiple_prs(),
  artifact_has_multiple_parent_commits(),
  branch_merged_into_main_from_different_names(),
  duplicate_issue_resolution()
]

convergence_candidate = any(convergence_signals)
```

---

## 4. Metodología de Análisis

### 4.1 Repositorios a Analizar

**Criterios**:
- ≥1 año de historia
- ≥100 commits
- ≥50 issues
- ≥20 PRs
- ≥5 branches (actuales o eliminados)

**Muestra sugerida**:
```
1. langchain-ai/langgraph       (ya auditado)
2. langchain-ai/langchain        (similar)
3. tensorflow/tensorflow         (large-scale)
4. pytorch/pytorch               (research-oriented)
5. biopython/biopython          (genomics)
6. openscience/openscience       (if accessible)
7. nilearn/nilearn              (neuroimaging)
8. scikit-learn/scikit-learn    (scientific computing)
9. keras-team/keras             (ML framework)
10. jupyter/notebook           (data science)
```

### 4.2 Señales a Buscar

**Branch Observable**:
```yaml
GitHub signals:
  - PR.state == "closed" && PR.merged == false
  - branch.protected == false && branch.exists == false (eliminada)
  - issue.labels contains ["wontfix", "obsolete", "duplicate"]
  - commit.message contains "revert", "close", "abandon"

Git signals:
  - git log --all --grep="abandon"
  - git branch -a | grep "feature/"
```

**Convergence Observable**:
```yaml
GitHub signals:
  - Issue closes with reference to another issue (duplicate)
  - PR mentions "supersedes", "replaces", "builds on"
  - Commit merges two feature branches
  - Artifact (file) has multiple parent commits

Git signals:
  - git merge-base feature/A feature/B (common ancestor)
  - git log --all --merges
```

### 4.3 Protocolo de Extracción

**Fase 1: Identificar Branches** (días 1-3)
```bash
python scripts/identify_branches.py --repo langchain-ai/langgraph --output branches.jsonl
```

**Fase 2: Identificar Convergencias** (días 4-6)
```bash
python scripts/identify_convergences.py --repo langchain-ai/langgraph --branches branches.jsonl --output convergences.jsonl
```

**Fase 3: Validación Manual** (días 7-10)
- Muestra aleatoria de 20 branches
- Muestra aleatoria de 10 convergencias
- Verificación humana: ¿Son reales estas bifurcaciones/convergencias?

**Fase 4: Métricas** (días 11-12)
```yaml
Branch metrics:
  - branches_detected / branches_total (estimado): ?
  - precision_branch_detection: ?
  - recall_branch_detection: ?

Convergence metrics:
  - convergences_detected / convergences_total (estimado): ?
  - precision_convergence_detection: ?
  - recall_convergence_detection: ?
```

---

## 5. Criterios de Decisión

### 5.1 Green Light (Implementar en SPRINT 61)

```yaml
Condiciones:
  - Branch precision ≥70%
  - Branch recall ≥50%
  - Convergence precision ≥70%
  - Convergence recall ≥40%
  - ≥5 repositorios con ≥3 branches detectados
  - ≥3 repositorios con ≥1 convergence detectado

Si se cumplen:
  → Añadir BranchNode y ConvergenceNode a EvidenceGraph v1.2.0
  → Implementar extract_branches.py y detect_convergences.py
  → Añadir queries MCP: get_branches, get_convergences
```

### 5.2 Yellow Light (Requiere más investigación)

```yaml
Condiciones:
  - Branch precision ≥60% pero <70%
  - O: Convergence recall <40%
  - O: Muy pocos repositorios con evidencia suficiente

Si se cumple:
  → Reducir scope a 5 repositorios másricos
  → Probar con dominios específicos (genomics, neuroimaging)
  → Reevaluar en SPRINT 62
```

### 5.3 Red Light (No implementar)

```yaml
Condiciones:
  - Branch precision <60%
  - O: <3 repositorios con evidencia de branches
  - O: Convergencias requiren LLM para detectar (no escalable)

Si se cumple:
  → Cancelar Branch Detection
  → Mantener CoResearcher como trajectory reconstruction engine
  → Documentar hallazgos para futuros trabajos
```

---

## 6. Entregables

### 6.1 Documentos

```markdown
docs/BRANCH_DETECTION_FEASIBILITY.md     ← Este documento
docs/SPRINT_60D_BRANCH_ANALYSIS.md       ← Resultados del análisis manual
```

### 6.2 Datos

```
data/branch_analysis/
├── branches.jsonl                         # Branches detectados
├── convergences.jsonl                     # Convergencias detectadas
├── validation_sample.json                 # Muestra para validación humana
└── metrics.json                           # Métricas cuantitativas
```

### 6.3 Scripts (exploratorios)

```bash
scripts/exploratory/
├── identify_branches.py                   # Identificar branches
├── identify_convergences.py               # Identificar convergencias
├── validate_sample.py                     # Generar muestra para validación
└── calculate_metrics.py                   # Calcular precision/recall
```

**Nota**: Estos scripts NO se integran en el producto. Son herramientas de análisis.

---

## 7. Limitaciones Constitucionales

### 7.1 Restricciones de CoResearcher

❌ **Prohibido**:
- Inferir branches que no tienen evidencia GitHub/Git
- Generar narrativas sobre "por qué se abandonó"
- Detectar "oportunidades perdidas" (eso es evaluación, no trazabilidad)
- Predecir "qué habría pasado si" (contrafactuales)

✅ **Permitido**:
- Registrar PRs cerrados sin merge
- Registrar branches eliminadas
- Detectar convergencias当 dos artifacts comparten commits o issues
- Marcar como `inferred` cuando no hay declaración explícita

### 7.2 Límites Epistemológicos

CoResearcher puede demostrar:

```text
✅ "PR #8420 fue cerrado sin merge"
✅ "Branch feature/pydantic-v1 fue eliminada"
✅ "Los commits abc123 y def456 comparten ancestro común"
✅ "Issue #8415 fue marcado como wontfix"
```

CoResearcher NO puede demostrar:

```text
❌ "El equipo abandonó pydantic v1 porque era lento"
❌ "La rama X era una mala idea"
❌ "Si hubieran elegido Y, habría funcionado mejor"
```

---

## 8. Métricas de Éxito

### 8.1 Cuantitativas

| Métrica | Target | Green Light | Yellow | Red |
|---------|--------|-------------|--------|-----|
| Branch Precision | ≥70% | ≥70% | 60-70% | <60% |
| Branch Recall | ≥50% | ≥50% | 40-50% | <40% |
| Convergence Precision | ≥70% | ≥70% | 60-70% | <60% |
| Convergence Recall | ≥40% | ≥40% | 30-40% | <30% |
| Repos con branches | ≥5 | ≥5 | 3-5 | <3 |
| Repos con convergencias | ≥3 | ≥3 | 1-3 | <1 |

### 8.2 Cualitativas

```yaml
Utilidad:
  - ¿Las bifurcaciones detectadas cuentan una historia coherente?
  - ¿Las convergencias son técnicamente significativas?
  - ¿La evidencia soporta las detecciones?

Viabilidad:
  - ¿Se puede implementar con <3 meses de desarrollo?
  - ¿Requiere LLM para detección confiable?
  - ¿El mantenimiento es sostenible?
```

---

## 9. Timeline

```yaml
Días 1-3: Identificación de branches en 10 repos
Días 4-6: Identificación de convergencias
Días 7-10: Validación manual (20 branches, 10 convergencias)
Días 11-12: Cálculo de métricas
Día 13: Decisión Green/Yellow/Red
```

**Total**: 2 semanas máximo.

---

## 10. Riesgos

### 10.1 Falsos Positivos en Branches

**Riesgo**: Issues cerrados como "duplicate" no son branches, son issues duplicados.

**Mitigación**: 
- Diferenciar "wontfix/obsolete" (branch) vs "duplicate" (no branch)
- Validación humana en muestra

### 10.2 Convergencias Requieren LLM

**Riesgo**: Detectar convergencias semánticas requiere comprensión de código.

**Mitigación**:
- Limitar a convergencias observables (mismo artifact, mismo issue, mismo commit)
- No detectar convergencias semánticas (eso requiere evaluación)

### 10.3 Scope Creep

**Riesgo**: Branch Detection se convierte en Decision Quality Engine.

**Mitigación**:
- Estricta separación: registrar ≠ evaluar
- No añadir métricas de "éxito de branch"
- No sugerir "qué habría pasado"

---

## 11. Ejemplo Esperado

### Branch Ejemplo

```json
{
  "branch_id": "BRANCH-000001",
  "type": "Branch",
  "source_decision": "DECISION-000042",
  "outcome": "abandoned",
  "evidence": [
    {"type": "pr", "id": 8420, "state": "closed", "merged": false},
    {"type": "branch", "name": "feature/pydantic-v1", "deleted": true},
    {"type": "issue", "id": 8415, "state": "closed", "labels": ["wontfix"]}
  ],
  "observable_signals": [
    "PR #8420 closed without merge on 2026-05-15",
    "Branch feature/pydantic-v1 deleted on 2026-05-20",
    "Issue #8415 closed as wontfix on 2026-05-15"
  ],
  "confidence": 1.0,
  "classification": "observable"
}
```

### Convergence Ejemplo

```json
{
  "convergence_id": "CONV-000001",
  "type": "Convergence",
  "branch_a": "DECISION-000045",
  "branch_b": "DECISION-000046",
  "convergence_point": "ART-000089",
  "evidence": [
    {"type": "commit", "hash": "abc123", "message": "Merge SQL adapters"},
    {"type": "pr", "id": 8452, "title": "Abstract database adapter"}
  ],
  "observable_signals": [
    "PR #8452 merges SQLite and PostgreSQL adapters",
    "Commit abc123 has 2 parents (merge commit)"
  ],
  "confidence": 1.0,
  "classification": "observable"
}
```

---

## 12. Decisión Post-Sprint

Al final de SPRINT 60D:

**Si Green**:
→ Incorporar Branch/Convergence a EvidenceGraph v1.2.0
→ Implementar extractores en producción
→ Añadir queries MCP

**Si Yellow**:
→ Investigar dominios específicos (genomics, neuroimaging)
→ Pro con enfoques alternativos
→ Reevaluar en SPRINT 62

**Si Red**:
→ Cancelar Branch Detection permanentemente
→ Mantener CoResearcher como trajectory reconstruction engine
→ No desviar recursos de misión core

---

## 13. Non-Goals

❌ Detectar convergencias semánticas (requiere evaluar código)
❌ Predecir éxito/fracaso de branches
❌ Sugerir alternativas
❌ Generar "oportunidades perdidas"
❌ Implementar en producción sin validación empírica

✅ SOLO determinar si la señal existe y es recuperable
✅ SOLO validar contra datos reales
✅ SOLO proceder si cumple criterios epistemológicos

---

*Este documento define el alcance exploratorio para determinar si CoResearcher puede detectar bifurcaciones y convergencias de trayectoria sin violar sus principios constitucionales. No se implementará nada hasta completar este análisis.*