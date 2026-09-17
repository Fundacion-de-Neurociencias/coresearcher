# SPRINT 62 — Operationalization of Constraints

**Date**: 2026-08-01
**Status**: IN EXECUTION
**Predecessor**: SPRINT 61 (H7 FALSIFIED detector)
**Goal**: Operationally define what a constraint is before trying to reconstruct it

---

## 1. Motivation

SPRINT 61 revealed three problems:

1. **FALSIFIED detector**: 70% false positive rate in synthetic convergences
2. **κ = -0.030**: agreement between reviewers worse than chance
3. **Conceptual drift**: we said "the concept is valid, the detector fails" — that is not rigorous

The most profound finding of SPRINT 61 is not that the detector failed.
The thing is that **perhaps the variable we are trying to identify is not well defined**.

### Analogy with Neurodiagnoses

If 3 neurologists classify patients and obtain κ = 0.05, the explanations are:

- H1: Neurologists are bad
- H2: The diagnostic criteria are ambiguous
- H3: The disease is not a natural entity

The same thing happens here. Maybe "shared constraint" is not yet
a variable sufficiently operationalized for two people
recognize it independently.

**That is a scientific result.**

---

## 2. Main question

```text
What exactly is a restriction?
```

Not philosophically. Operationally.

We currently have:

```text
technical restriction
conceptual constraint
historical constraint
mathematical constraint
ontological constraint
```

But that seems more like an intuitive taxonomy than an operational definition.

---

## 3. Proposed operational definition

A **constraint** exists if and only if it meets **all four criteria**:

### Criterion 1: Generate observable predictions

```text
If the constraint R exists, then we would observe P.
Si no observamos P, R está debilitada o falsada.
```

A constraint that does not generate observable predictions is not
a restriction — is a speculation.

### Criterion 2: Explains more than one trajectory

```text
R explica las decisiones D1, D2, ..., Dn
donde n ≥ 2 y las trayectorias son independientes.
```

A constraint that explains a single trajectory is not a
shared constraint — is an ad hoc justification.

### Criterion 3: Its elimination changes the decision space

```text
Si eliminamos R, las decisiones D1, ..., Dn cambiarían.
Counterfactual: without R, would you have made the same decision?
```

A constraint that changes nothing when removed is not
a restriction — it is a narrative decoration.

### Criterion 4: Can be falsified

```text
Existe una observación O tal que, si se observa,
R queda falsada.
```

A restriction that cannot be falsified is not scientific —
It is a belief.

---

## 4. Taxonomy vs operational definition

The current taxonomy (technical/conceptual/historical/mathematical/ontological)
classifies restrictions by their **origin**.

The operational definition classifies them by their **epistemological status**:

| Taxonomy (origin) | Operational definition (status) |
|---------------------|---------------------------------|
| technique | Does it generate observable predictions? |
| conceptual | Does it explain more than one trajectory? |
| historical | Does removing it change the space? |
| mathematics | Can it be falsified? |
| ontological | Can it be falsified? |

Both are compatible. But the operational definition is **previous**:
Without it, the taxonomy has no empirical basis.

---

## 5. Experiment: evaluate hypotheses against criteria

For each of the 12 SPRINT 61 hypotheses (3 by convergence × 4),
evaluate whether they meet the 4 operational criteria.

**Deliverable**: `artifacts/constraint_operationalization.json`

---

## 6. What we will discover

### If the hypotheses meet the 4 criteria

→ The operational definition works
→ We can improve the detector with objective criteria
→ κ should improve

### If the hypotheses do not meet the 4 criteria

→ "Constraint" is not yet an operational variable
→ We need conceptual refinement
→ κ will remain low until we define the variable better

### If some comply and others do not

→ We have a filter: only those who comply are candidates
→ The detector can use the criteria as validation
→ Incremental progress

---

## 7. Connection with LRM Reasoning

LRMs produce *chains of thought* and humans invent
*explanations* about those traces.

CoResearcher produces *convergences* and humans invent
*restrictions* to explain them.

The symmetry is almost perfect.

And the same warning applies:

> A plausible explanation is not evidence of mechanism.

The operational definition is precisely what separates
a plausible explanation of a proven explanation.

---

## 8. Non-Goals

- ❌ DO NOT upgrade the detector yet
- ❌ DO NOT open H8, H9 or EHG
- ❌ DO NOT create new schemas
- ❌ DO NOT assume that restrictions exist
- ❌ DON'T assume they don't exist

---

## 9. Success criteria

| Criterion | Green | Yellow | Red |
|----------|-------|-----------|------|
| Hypotheses that meet 4 criteria | ≥50% | 25-50% | <25% |
| Observable predictions generated | ≥8 | 4-7 | <4 |
| Counterfactuals defined | ≥8 | 4-7 | <4 |

---

*Before reconstructing constraints, define what a constraint is.*
*Before defining what it is, verify that the definition works.*
*A non-operationalized variable cannot be measured.*