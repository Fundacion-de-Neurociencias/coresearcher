# BRANCH & CONVERGENCE DETECTION FEASIBILITY
**SPRINT 60D — Exploratory Analysis**  
**Goal**: Determine whether GitHub and Zenodo contain sufficient signal to reconstruct path branches and convergences without unauditable inferences  
**Status**: Exploratory — No Implementation Yet  
**Next Sprint**: Conditional on empirical results

---

## 1. Strategic Context

Current CoResearcher reconstructs **observed trajectories**:

```text
Decision A → Decision B → Decision C
```

A new question arises:

```text
What alternatives were left unexplored?
Are there convergences between divergent trajectories?
```

This would be:

```text
Espacio de posibilidades
```

not only:

```text
Historia observada
```

**But**: CoResearcher should NOT infer hypothetical trails. Any bifurcation/convergence must be derived from public evidence.

---

## 2. Operational Definitions

### 2.1 Branch

**Branch Observable**: An alternative that was explicitly started but not completed.

```yaml
Tipos:
  - PR cerrado sin merge (issue, PR, commit evidences)
  - Rama eliminada (git branch evidence)
  - Issue abandonado (sin actividad >90 días)
  - RFC/Documento rechazado (explicit rejection)

Campos obligatorios:
  - branch_id: BRANCH-XXXXXX
- source_decision: DECISION-XXXXXX (the decision that originated the alternative)
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

**Branch Derivable**: An alternative inferred from patterns in the evidence.

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

**Constitutional restriction**:
- Every Branch must have ≥1 observable_signal
- Branches without GitHub/Git evidence are not allowed
- Confidence ≤ 0.8 for differentiable, =1.0 only for observable

---

### 2.2 Convergence

**Convergence Observable**: Two different trajectories that converge on the same artifact or decision, with explicit evidence.

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

**Convergence Derivable**: Pattern detected by algorithm without explicit declaration.

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

**Constitutional restriction**:
- Every convergence must have ≥2 branches with independent evidence
- Convergences inferred from a single artifact are not allowed
- Convergence point must be an artifact or observable decision

---

## 3. Hypotheses to Validate

### H7: Branch Detection

> Public trajectories contain enough information to identify real research forks.

**Predictions**:
1. ≥30% of active repositories have ≥1 observable branch (PR closed without merge)
2. ≥50% of discoverable branches have evidence (Issue + PR + branch_name)
3. ≥70% of approach change decisions generate branches

**Operationalization**:
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

> There are observable convergences between initially divergent trajectories.

**Predictions**:
1. ≥20% of repositories with ≥2 branches have ≥1 convergence
2. ≥60% of convergences are detectable by algorithm (do not require LLM)
3. Convergence point is a shared artifact (code, document, dataset)

**Operationalization**:
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

## 4. Analysis Methodology

### 4.1 Repositories to Analyze

**Criteria**:
- ≥1 year of history
- ≥100 commits
- ≥50 issues
- ≥20 PRs
- ≥5 branches (current or deleted)

**Suggested sample**:
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

### 4.2 Signs to Look For

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

### 4.3 Extraction Protocol

**Phase 1: Identify Branches** (days 1-3)
```bash
python scripts/identify_branches.py --repo langchain-ai/langgraph --output branches.jsonl
```

**Phase 2: Identify Convergences** (days 4-6)
```bash
python scripts/identify_convergences.py --repo langchain-ai/langgraph --branches branches.jsonl --output convergences.jsonl
```

**Phase 3: Manual Validation** (days 7-10)
- Random sample of 20 branches
- Random sample of 10 convergences
- Human verification: Are these bifurcations/convergences real?

**Phase 4: Metrics** (days 11-12)
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

## 5. Decision Criteria

### 5.1 Green Light (Implement in SPRINT 61)

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

### 5.2 Yellow Light (Requires further investigation)

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

### 5.3 Red Light (Do not implement)

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

## 6. Deliverables

### 6.1 Documents

```markdown
docs/BRANCH_DETECTION_FEASIBILITY.md     ← Este documento
docs/SPRINT_60D_BRANCH_ANALYSIS.md       ← Resultados del análisis manual
```

### 6.2 Data

```
data/branch_analysis/
├── branches.jsonl                         # Branches detectados
├── convergences.jsonl                     # Convergencias detectadas
├── validation_sample.json                 # Muestra para validación humana
└── metrics.json                           # Métricas cuantitativas
```

### 6.3 Scripts (exploratory)

```bash
scripts/exploratory/
├── identify_branches.py                   # Identificar branches
├── identify_convergences.py               # Identificar convergencias
├── validate_sample.py                     # Generar muestra para validación
└── calculate_metrics.py                   # Calcular precision/recall
```

**Note**: These scripts are NOT integrated into the product. They are analysis tools.

---

## 7. Constitutional Limitations

### 7.1 CoResearcher Restrictions

❌ **Prohibited**:
- Infer branches that have no GitHub/Git evidence
- Generate narratives about "why it was abandoned"
- Detect "missed opportunities" (that's evaluation, not traceability)
- Predict "what would have happened if" (counterfactuals)

✅ **Allowed**:
- Register closed PRs without merge
- Register deleted branches
- Detect convergences where two artifacts share commits or issues
- Mark as `inferred` when there is no explicit declaration

### 7.2 Epistemological Limits

CoResearcher can demonstrate:

```text
✅ "PR #8420 fue cerrado sin merge"
✅ "Branch feature/pydantic-v1 fue eliminada"
✅ "Los commits abc123 y def456 comparten ancestro común"
✅ "Issue #8415 fue marcado como wontfix"
```

CoResearcher CANNOT prove:

```text
❌ "El equipo abandonó pydantic v1 porque era lento"
❌ "La rama X era una mala idea"
❌ "Si hubieran elegido Y, habría funcionado mejor"
```

---

## 8. Success Metrics

### 8.1 Quantitative

| Metric | Target | Green Light | Yellow | Network |
|---------|--------|-------------|--------|-----|
| Branch Precision | ≥70% | ≥70% | 60-70% | <60% |
| Branch Recall | ≥50% | ≥50% | 40-50% | <40% |
| Convergence Precision | ≥70% | ≥70% | 60-70% | <60% |
| Convergence Recall | ≥40% | ≥40% | 30-40% | <30% |
| Repos with branches | ≥5 | ≥5 | 3-5 | <3 |
| Repos with convergences | ≥3 | ≥3 | 1-3 | <1 |

### 8.2 Qualitative

```yaml
Utilidad:
- Do the detected forks tell a coherent story?
- Are the convergences technically significant?
- Does the evidence support the detections?

Viabilidad:
- Can it be implemented with <3 months of development?
- Requires LLM for reliable detection?
- Is the maintenance sustainable?
```

---

## 9. Timeline

```yaml
Días 1-3: Identificación de branches en 10 repos
Días 4-6: Identificación de convergencias
Días 7-10: Validación manual (20 branches, 10 convergencias)
Días 11-12: Cálculo de métricas
Day 13: Green/Yellow/Red Decision
```

**Total**: 2 weeks maximum.

---

## 10. Risks

### 10.1 False Positives in Branches

**Risk**: Issues closed as "duplicate" are not branches, they are duplicate issues.

**Mitigation**: 
- Differentiate "wontfix/obsolete" (branch) vs "duplicate" (no branch)
- Human validation in sample

### 10.2 Convergences Require LLM

**Risk**: Detecting semantic convergences requires code understanding.

**Mitigation**:
- Limit to observable convergences (same artifact, same issue, same commit)
- Not detecting semantic convergences (that requires evaluation)

### 10.3 Scope Creep

**Risk**: Branch Detection becomes Decision Quality Engine.

**Mitigation**:
- Strict separation: record ≠ evaluate
- Do not add "branch success" metrics
- Do not suggest "what would have happened"

---

## 11. Expected Example

### Branch Example

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

### Convergence Example

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

## 12. Post-Sprint Decision

At the end of SPRINT 60D:

**Yes Green**:
→ Add Branch/Convergence to EvidenceGraph v1.2.0
→ Deploy extractors in production
→ Add MCP queries

**Yes Yellow**:
→ Research specific domains (genomics, neuroimaging)
→ Pro with alternative approaches
→ Reevaluate in SPRINT 62

**Yes Network**:
→ Cancel Branch Detection permanently
→ Maintain CoResearcher as trajectory reconstruction engine
→ Do not divert core mission resources

---

## 13. Non-Goals

❌ Detect semantic convergences (requires evaluating code)
❌ Predict success/failure of branches
❌ Suggest alternatives
❌ Generate "missed opportunities"
❌ Deploy to production without empirical validation

✅ ONLY determine if the signal exists and is recoverable
✅ ONLY validate against real data
✅ ONLY proceed if it meets epistemological criteria

---

*This document defines the exploratory scope to determine whether CoResearcher can detect trajectory bifurcations and convergences without violating its constitutional principles. Nothing will be implemented until this analysis is complete.*