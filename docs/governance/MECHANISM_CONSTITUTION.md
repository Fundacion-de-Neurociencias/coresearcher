# Mechanism Constitution
## CoResearcher Theory of Scientific Mechanisms

## Question 1: What is a mechanism?

A **mechanism** is a causal explanatory sequence that connects observations with phenomena, representing **how** something happens, not just **that** it happens.

### Formal Definition

```
A mechanism is a structured set of causal relationships
que explica el vínculo entre variables observables y fenómenos complejos,
y que puede ser puesto a prueba mediante predicciones empíricas.
```

### Fundamental Properties

1. **Explicit causality** - Relationships are oriented and explanatory
2. **Testability** - Generates verifiable predictions
3. **Modularity** - Can be combined with other mechanisms
4. **Evolution** - Can be modified with new evidence

---

## Question 2: What is the difference between?

### Claim vs Finding vs Mechanism vs Model vs Theory

| Level | What | Example | Mutability |
|-------|-----|---------|-------------|
| **Claim** | Atomic observation | "pTau217 predicts AD (r=0.78)" | Low - it is a reported fact |
| **Finding** | Structured distillation | "pTau217 → amyloid pathway (effect=0.78)" | Medium - can be re-evaluated with new evidence |
| **Mechanism** | Causal explanation | "pTau217 mediates stress response that triggers amyloid aggregation via MECH-X" | High - are refined with evidence |
| **Model** | Set of mechanisms | "Amyloid cascade + Tau propagation + Inflammation" | Medium - replaces if fails |
| **Theory** | Broad explanatory framework | "Proteostasis failure in neurodegeneration" | Very high - scientific paradigm |

---

## Question 3: Can there be a false mechanism?

**Yes.** A mechanism can be:
- Incorrect (refuted predictions)
- Incomplete (intermediate steps missing)
- Superficial (the actual mechanism is different)

### Validation Attributes

```yaml
mechanism:
  id: MECH-000001
  name: "Neuronal Stress-Mediated Amyloid Deposition"
  support:  # Evidencia a favor
    - CLAIM-00123
    - FIND-00456
    - REPLICATION-007
  contradictions:  # Evidencia en contra
    - CHALLENGE-008
  confidence: 0.3  # Basado en apoyo/refutación
  replications: 0
  challenges: 0
  institution_count: 0
  trust_score: 0.5  # Dinámico, de Participation Layer
```

---

## Question 4: How is a mechanism born?

### Bottom-up (Inductive)

```
Finding A    Finding B    Finding C
    ↓            ↓            ↓
   [ENTITY-X] → [ENTITY-Y] → [ENTITY-Z]
         ↓
   "Hay una relación causal oculta"
         ↓
MECHANISM (hypothesis)
```

### Top-down (Deductive)

```
Hypothesis: "pTau217 is protective response"
    ↓
What mechanism would explain this?
    ↓
MECH-X: stress → pTau217 upregulation → amyloid sequestration
    ↓
Predictions para test
    ↓
Predictions refuted → mechanism rejected
Predictions confirmed → reinforced mechanism
```

---

## Question 5: How does a mechanism die?

The mechanisms follow a scientific life cycle:

```
NACIMIENTO (birth)
    ↓
CREACIÓN → {support, confidence=0.1}
    ↓
CRECIMIENTO (growth) → CONFIRMACIONES, REPLICACIONES
    ↓
CONVERGENCE → high trust, multiple supports
    ↓
REFUTACIÓN o degradación progresiva
    ↓
MUERTE (death) → challenges > support, confidence → 0
```

### Operations on Mechanisms

| Operation | What does it do | Result |
|-----------|----------|-----------|
| **CONFIRM** | Evidence supports the mechanism | +confidence, +trust_score |
| **REJECT** | Evidence refutes the mechanism | -confidence, -trust_score |
| **FORK** | Create mechanism variant | MECH-fork (new route) |
| **MERGE** | Combine two mechanisms | MECH-combined (more general) |
| **SPLIT** | Split complex mechanism | MECH-A, MECH-B (more specific) |

---

## Participation Primitives for Mechanisms

```
MECH-000001
├── support (CLAIM/FINDING que lo respaldan)
├── contradict (CLAIM/FINDING que lo refutan)
├── replicate (evidencia de replicación)
├── challenge (análisis crítico)
├── fork (derivative mechanism)
└── merge_request (propuesta de combinación)
```

---

## Conclusion

Mechanisms are the **core of shared scientific discovery**. 

Not the claims. Not the papers. 

**Mechanisms are the explanations that scientists collectively discuss, defend, refute, and evolve.**

This is the asset that will generate the true moat of CoResearcher: a cumulative network of mechanisms with their history of scientific participation.