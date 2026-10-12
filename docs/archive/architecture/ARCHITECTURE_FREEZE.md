# ARCHITECTURE FREEZE
**Effective Date**: 2026-07-30  
**Status**: ACTIVE — No new schemas, documents, or layers without explicit supervisor approval  
**Authority**: Manuel (Project Supervisor)

---

##Directive

**STOP adding architecture.**

The bottleneck of CoResearcher is no longer conceptual. It is empirical.

All schemas, documents, and layer definitions produced during SPRINT PLATFORM-01, SPRINT 60A, SPRINT 60B, and SPRINT 60D are **STABLE** and **FROZEN**.

No new schemas.
No new documents.
No new layers.
Not new graphs.

---

## What is Stabilized (Do Not Modify)

### Constitutional Principles
- Observable
- Derivable  
- Inferred (restricted)
- Unknown

### Mission
> Reconstruct the auditably recoverable fraction of a project's history.

### Boundaries
- CoResearcher ≠ AI Scientist
- CoResearcher ≠ Reviewer
- CoResearcher ≠ Manuscript Assistant

### Core Artifact
- EvidenceGraph (v1.1.0)

### Approved Extension
- DecisionNode (with Decision Traceability Principle: Observable or Derivable, never Inferred)

---

## What is NOT Stabilized (Requires Empirical Validation)

### H6: Decision Reconstruction
> Decisions are reconstructable.

**Status**: Modeled, not demonstrated  
**Action**: SPRINT 60C — Validate with 20+ real repositories

### H7: Branch Detection  
> The branches are rebuildable.

**Status**: Exploratory (SPRINT 60D documented, not executed)  
**Action**: Depends on H6. Do not execute until H6 is validated.

### H8: Convergence Detection
> The convergences are reconstructable.

**Status**: Exploratory  
**Action**: Depends on H6 and H7. Do not execute until H6 and H7 are validated.

### H9: Trajectory Value
> The track record provides more value than simple evidence.

**Status**: Hypothesis  
**Action**: Evaluate after SPRINT 60C

---

##Activate Sprint: SPRINT 60C

###Objective
False or validate H6 through analysis of real repositories.

###Targets
- Minimum 20 repositories
- Extract observable DecisionNodes
- Measure: decision_reconstruction_rate, decision_source_distribution, trajectory_completeness

### Questions to Answer
1. How many observable decisions appear?
2. How many decisions can be reconstructed?
3. Where do they appear? (Issue, PR, Commit, Release, Discussion, Zenodo)
4. What percentage remains unknown?

### Success Criteria
- decision_reconstruction_rate ≥ 70%
- Identification of primary sources (issues vs PRs vs commits)
- Public reproducible dataset for future sprints

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

❌ Add new nodes to EvidenceGraph  
❌ Add new graphs  
❌ Add new architectural layers  
❌ Create new schemas  
❌ Modify existing schemas without explicit bug fix  
❌ Write theoretical architecture documents  
❌ Plan sprints beyond SPRINT 61  
❌ Run SPRINT 60D (Branch Detection)

---

## Permitted Activities

✅ Run SPRINT 60C (empirical analysis)  
✅ Write extraction scripts  
✅ Write validation scripts  
✅ Write results reports  
✅ Correct bugs in existing schemas  
✅ Improve extraction algorithms (do not change schemas)  
✅ Document empirical findings

---

## Exit Conditions from Freeze

The freeze is lifted when:

1. **SPRINT 60C completed** with quantitative metrics
2. **H6 validated or falsified** empirically
3. **Decision made** whether to continue with DecisionGraph or keep DecisionNode as an extension

Only after those 3 conditions, architecture can be reconsidered.

---

##Motivation

The goal of CoResearcher is not to build the most elegant graph.

It is to empirically demonstrate that you can reconstruct research trajectories based on public evidence.

Until that is proven, any additional layer is premature optimization.

---

## Version History

- v1.0 (2026-07-30): Architecture freeze declared. SPRINT 60C as priority.

---

*This directive is effective immediately. All team members must comply. Violations require explicit supervisor approval.*