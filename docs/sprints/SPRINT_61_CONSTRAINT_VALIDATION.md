#SPRINT 61—Constraint Reconstruction Validation

**Date**: 2026-08-01
**Status**: COMPLETED — H7 FORGED in its current form
**Objective**: Try to falsify H7. Not demonstrate it. Try to destroy it.
**Principle**: If you survive, you gain credibility. If not, we learn something more valuable.

---

## 1. Main Question

```text
Reconstructable shared constraints exist
a partir de convergencias observadas?
```

Not: "Can we imagine restrictions?"

But: "Can we reconstruct them in a reproducible way?"

---

## 2. Executive Summary

| Phase | Result | Verdict |
|------|-----------|-----------|
| PHASE 1 — Audit | 4/4 real convergences, 3 competing hypotheses each | ✅ Protocol works |
| PHASE 2 — Agreement | κ = -0.030 (is_real), κ = -0.067 (hypothesis) | 🔴 RED — poor agreement |
| PHASE 3 — Generalization | Only 1 repo with trajectory_graph | ⚪ UNDETERMINED |
| PHASE 4 — Recurrence | technical:5, conceptual:3, historical:3, mathematics:1 | 🟡 Preliminary |
| PHASE 5 — Counterfeiting | 70% FPR synthetic, 35% FPR noise | 🔴 FALSIFIED |

**Overall verdict**: 🔴 **RED — FAKE H7 in its current form**

The detector produces **hallucinated constraints**: it does not distinguish real convergences from synthetic ones.

---

## 3. PHASE 1 — Human audit of convergences

**Deliverable**: `artifacts/convergence_review.json`

### Results

- 4 audited convergences
- 4/4 classified as **real** (100%)
- All have ≥3 competing hypotheses
- They all have operational definition
- They all have falsification criteria
- All in state `UNDETERMINED` (multiple active hypotheses)

### Distribution of constraint types (hypothesized)

| Type | Frequency | As main |
|------|---------|----------------|
| technique | 5 | 0 |
| conceptual | 3 | 3 |
| historical | 3 | 1 |
| mathematics | 1 | 0 |

**Pattern**: Conceptual restrictions dominate as main hypotheses. The techniques appear as frequent competitors.

### Conclusion PHASE 1

The audit protocol works: it generates competing hypotheses with operational definition and falsification. But all constraints remain on `UNDETERMINED` — we cannot determine which hypothesis is correct without more evidence.

---

## 4. PHASE 2 — Agreement between reviewers

**Deliverable**: `artifacts/reviewer_agreement.json`

### Methodology

3 simulated reviewers with different perspectives:
- R1-CONSERVATIVE: requires strong evidence
- R2-LIBERAL: classifies as real with moderate evidence
- R3-SKEPTICAL: tends to classify as artifact

### Results

| Pair | κ (is_real) | κ (hypothesis) |
|-----|-------------|-------------|
| R1 vs R2 | 0.000 | 0.000 |
| R1 vs R3 | -0.091 | 0.000 |
| R2 vs R3 | 0.000 | -0.200 |
| **Average** | **-0.030** | **-0.067** |

**Verdict**: 🔴 **RED — poor agreement, strong reviewer dependence**

### Conclusion PHASE 2

The protocol is **highly sensitive to reviewer bias**. Two different scientists DO NOT reconstruct the same constraint. H7 is significantly weakened.

**Limitation**: These are simulated reviewers. Real human reviewers are needed for confirmation.

---

## 5. PHASE 3 — Cross-repo generalization

**Deliverable**: `artifacts/cross_repo_constraints.json`

### Status

- **Repos with trajectory_graph**: 1 (langchain-ai/langgraph)
- **Repos with metrics only**: 3 (langchain, haystack, LlamaIndex)
- **Repos required**: minimum 10

### Conclusion PHASE 3

**UNDETERMINED** — cannot evaluate generalization with 1 repo.

It is required to run SPRINT 60C pipeline in at least 10 more repositories (pandas, numpy, fastapi, django, scikit-learn, etc.).

---

## 6. PHASE 4 — Recurring restrictions

**Deliverable**: `artifacts/cross_repo_constraints.json`

### Frequency table

| Hypothetical constraint | Frequency | As main |
| ---------------------- | ---------- | -------------- |
| technique | 5 | 0 |
| conceptual | 3 | 3 |
| historical | 3 | 1 |
| mathematics | 1 | 0 |
| ontological | 0 | 0 |

### Preliminary cross pattern

Conceptual and historical restrictions dominate as main hypotheses. The techniques frequently appear as competitors. Mathematics and ontology are weird.

**Limitation**: Based on only 4 convergences — insufficient for robust conclusions.

---

## 7. PHASE 5 — Critical falsification experiment

**Deliverable**: `artifacts/falsification_experiment.json`

### Question

```text
The detector continues to find compelling constraints
cuando se inyectan convergencias sintéticas aleatorias?
```

### Method

1. Control: detector on real data (4 barrier convergences)
2. Synthetic: inject 5 synthetic themes with 2-5 actors each (10 repetitions)
3. Noise: inject 10 random noise tracks with 2-3 actors (10 repetitions)

### Results

| Condition | Detected convergences (avg) |
|-----------|------------------------|
| Control (real) | 4 |
| Synthetic injected | 3.5 (of 5 injected) |
| Random noise injected | 3.5 (of 10 injected) |

| Metric | Value |
|---------|-------|
| False positive rate (synthetic) | **70%** |
| False positive rate (noise) | **35%** |

### Verdict

🔴 **FALSIFIED — detector produces hallucinated constraints**

The detector finds "convergences" in synthetic and noise data. It does not distinguish between real and artificial convergences.

### Root cause

The detector uses **Jaccard title similarity** to group decisions. Any set of nodes with similar titles (even synthetic ones) will be detected as "converging". There is no validation that convergence corresponds to a real barrier.

### Conclusion PHASE 5

H7 is **FALSIFIED** in its current implementation. The detector produces hallucinated constraints.

**This does not mean that constraints do not exist.** It means that the current detector cannot distinguish real constraints from artifacts. A more robust validation mechanism is needed.

---

## 8. Global Verdict

### Success criteria

| Criterion | Necessary value | Obtained value | State |
|----------|----------------|----------------|--------|
| Real convergences | ≥80% | 100% | ✅ |
| Cohen kappa | ≥0.7 | -0.030 | 🔴 |
| Generalization | multiple repos | 1 repo | ⚪ |
| Robust falsification | FPR < 20% | 70% | 🔴 |

### Verdict: 🔴 RED

```text
κ < 0.4
explicaciones muy variables
dependencia fuerte del revisor
detector produce hallucinated constraints
```

**H7 DOES NOT survive the falsification attempt.**

---

## 9. What we learned

### Lesson 1: The epistemological protocol works

The system of competing hypotheses, operational definition and falsification criteria works correctly. All restrictions are in `UNDETERMINED` — the system honestly answers "we don't know."

### Lesson 2: The detector is vulnerable to hallucinated constraints

The convergence detector based on Jaccard of titles does not distinguish real from synthetic. This is a serious problem that must be resolved before trusting the detected convergences.

### Lesson 3: Agreement between reviewers is poor

Even with a structured protocol, reviewers with different perspectives classify very differently. H7 needs a more objective protocol or more evidence for convergence.

### Lesson 4: "We don't know" is more valuable than a false theory

The system correctly:
- Labeled all constraints as `UNDETERMINED`
- Did not promote any hypothesis to fact
- Detected its own vulnerability to false positives
- Produced evidence of his own limitation

---

## 10. Next steps

### Immediate

1. **Improve the convergence detector** to distinguish real from synthetic
   - Validate that the actors are real humans (not bots)
   - Validate that the PRs have real discussion
   - Validate that the topic is semantically coherent (not just lexical)
   - Consider code evidence (not just titles)

2. **Repeat PHASE 2 with real human reviewers**
   - Simulated reviewers measure sensitivity, not real agreement

3. **Run pipeline on 10+ repositories** for PHASE 3

### If the detector improves

1. Repeat PHASE 5 (falsification)
2. If FPR < 20% → H7 gains provisional credibility
3. If κ ≥ 0.7 with human reviewers → GREEN

### If the detector does not improve

1. H7 remains in state `FALSIFIED`
2. Rethink: perhaps the convergences are not detectable only from titles
3. Consider deeper semantic analysis

---

## 11. Deliverables

| Archive | Phase | Content |
|---------|------|-----------|
| `artifacts/convergence_review.json` | PHASE 1 | 4 convergences with 3 competing hypotheses each |
| `artifacts/reviewer_agreement.json` | PHASE 2 | Cohen kappa among 3 reviewers |
| `artifacts/cross_repo_constraints.json` | PHASE 3+4 | Cross-repo limitation + frequency table |
| `artifacts/falsification_experiment.json` | PHASE 5 | Falsification experiment (FALSIFIED) |
| `artifacts/constraint_stability_report.md` | Global | This document |

---

## 12. Epistemological status

```text
H7 (Constraint Reconstruction — detector):
  Estado: FALSIFIED
  Razón: 70% false positive rate en convergencias sintéticas
  kappa: -0.030 (poor agreement)

H7 (Constraint Reconstruction — theory):
  Estado: UNDETERMINED
Reason: The theory has not really been tested.
         Nunca llegamos a observar restricciones. Solo observamos convergencias.
The mechanism that connects convergence → restriction has turned out
         poco fiable. No podemos decir "el concepto es válido" — solo
         podemos decir "no sabemos".

Restricciones como variables latentes:
  Estado: UNDETERMINED (no "validadas")
  Razón: Nunca observamos restricciones directamente.
         Solo observamos convergencias.
The convergence → constraint connection is not validated.
```

**Important conceptual correction**:

We cannot say "the concept is still valid, the detector fails."
That would be making the same mistake that we criticize: confusing an explanation
plausible with a proven explanation.

The theory is UNDETERMINED. The detector is FALSIFIED.
They are different states and should not be confused.

**NOTE**: Falsifying the detector does not falsify the theory. But it doesn't validate it either.
The theory remains UNDETERMINED until we have a definition
operational "restriction" that allows it to be observed (or derived
reproducibly). That is the goal of SPRINT 62.

---

## 13. Non-Goals reaffirmed

- ❌ DO NOT open H8, H9 or EHG
- ❌ DO NOT create new schemas
- ❌ DO NOT declare victory
- ❌ DO NOT ignore the falsification
- ❌ DO NOT promote restrictions on facts

---

*A false theory is worse than admitting that we still have no theory.*
*H7 was falsified. That is scientific progress.*
*The system detected its own limitation. That is epistemological honesty.*