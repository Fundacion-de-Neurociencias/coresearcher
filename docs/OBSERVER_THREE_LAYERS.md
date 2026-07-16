# Observer: Three Layers of Scientific Activity

## The Architecture

```text
L1 - Git Observer
L2 - Artifact Observer  
L3 - Agent Observer

All feed into Scientific Activity Ledger
```

---

## Layer 1: Git Observer

**Source:** Repository commits, PRs, releases

**Captures:**
- Development activity
- Feature additions
- Bug fixes
- Refactors

**Limitation:** Sees results, not intentions

---

## Layer 2: Artifact Observer

**Source:** Generated files, datasets, papers, figures

**Captures:**
- Scientific outputs
- Data products
- Documentation
- Publications

**Limitation:** Sees artifacts, not processes

---

## Layer 3: Agent Observer (Most Valuable)

**Source:** Agent sessions, prompts, plans

**Captures:**
- Intentions (prompts)
- Reasoning (chains)
- Decisions (tradeoffs)
- Execution (plans)

**Advantage:** Has semantic context that Git lacks

---

## The Ledger Fusion

```text
Agent Session 1
    ├── Git commits (7)
    ├── Artifacts produced (3)
    └── Objective: "Develop tri-axial ontology"

Agent Session 2
    ├── Git commits (12)
    ├── Artifacts produced (2)
    └── Objective: "Validate biomarker extraction"
```

---

## Success Metric

Not:
> ¿Cuántos objetivos detectó?

But:
> ¿Cuántas horas ahorra un investigador entendiendo el proyecto?

Baseline: 20 hours reading repositories
Target: 1 hour with ledger

---

## Objective Hypotheses (Not Inference)

The observer should say:
> "Estos 143 commits parecen pertenecer al mismo esfuerzo intelectual."

Not:
> "Este es el objetivo científico."

Hypotheses are validated by humans/agents, not asserted.

---

## Next Step

Apply to neurodiagnoses-monorepo and measure actual comprehension improvement.