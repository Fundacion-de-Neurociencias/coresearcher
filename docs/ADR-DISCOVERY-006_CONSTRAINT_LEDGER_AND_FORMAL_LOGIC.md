#ADR-DISCOVERY-006: Constraint-Centric Epistemology & Computable Popperian Logic

**Version 1.0.0** - Architecture Decision Record  
**Status**: Canonical Standard - Foundational Logic & Constraint Engine  
**Domain**: Scientific Epistemology, Formal Logic & Constraint Discovery

---

## 1. Philosophical and Architectural Diagnosis

Most AI systems for science try to find **answers** or collect **claims**. However, the most profound discoveries in the history of science do not uncover mere answers; they discover **invariant constraints** on reality:
- **Einstein**: *The speed of light in a vacuum is invariant in all inertial frames.* (Relativistic restriction).
- **Schrödinger / Von Neumann**: *The temporal evolution of the quantum state vector must be strictly unitary.* (Quantum constraint).
- **Neurodiagnoses**: *Not any biomarker can explain any temporal trajectory; there are prohibited homeostatic phase transitions.* (Biological restriction).
- **GeneForge**: *A splicing or expression effect is not universally permissible; is restricted by the cellular ContextState.* (Transcriptomic Constraint).

> **Thesis**: The fundamental unit of science is not `Claim`, not even `Hypothesis`. **It is the `Constraint` (Constraint)**.
> A hypothesis is a conjecture about what constraints govern a phenomenon.
> A mature scientific theory is a connected network of constraints that has survived systematic attempts at empirical demolition.

---

## 2. Architectural Decision

### 2.1. The 9-Level Epistemological Chain
The scientific production flow is formalized in CoResearcher:
```
Literature
   ↓
Findings
   ↓
Biological Programs (Representaciones reutilizables)
   ↓
Constraints (Restricciones invariantes del espacio de estados)
   ↓
Hypotheses (Conjeturas de frontera)
   ↓
Predictions (Deducción lógica formal)
   ↓
Experiments (DataAILab in-silico execution)
   ↓
Failed Predictions (Anomalías observadas)
   ↓
Revisions & Epistemic Trajectories (Supervivencia y refinamiento)
```

### 2.2. First Level Primitive: `Constraint`
The entity `Constraint` is formalized:
- `constraint_id`: Canonical identifier (e.g. `CONST-BIO-PROTEOSTASIS-01`).
- `statement`: Mathematical, physical or biological formulation of the restriction.
- `constraint_type`: `PHYSICAL`, `BIOLOGICAL`, `LOGICAL`, `CONTEXTUAL`,
- `invariance_domain`: Space of observables where the restriction remains constant.
- `falsification_conditions`: What observation would demolish this restriction.
- `epistemic_status`: `CONJECTURED`, `SURVIVED`, `CANONICAL`, `FALSIFIED`.

### 23. Computable Formal Logic Layer (Popper Engine)
The informal textual linking of predictions is replaced by a formal deduction engine based on implications and *Modus Tollens*:

$$\text{Fundamental Rule}: \quad (H \implies P) \land \neg P \implies \neg H \quad (\text{Falsification of } H)$$
$$\text{Atenuación con Auxiliares } (A): \quad ((H \land A) \implies P) \land \neg P \implies (\neg H \lor \neg A)$$

The system explicitly models:
- **`Assumptions`**: Auxiliary context or instrumentation assumptions.
- **`NecessaryConditions`**: Conditions $C$ without which the phenomenon cannot occur ($Phenomenon \implies C$).
- **`SufficientConditions`**: $S$ conditions whose presence guarantees the phenomenon ($S \implies Phenomenon$).
- **`FormalImplications`**: Strict deduction logic connectors ($H \vdash P$).
- **`Contradictions`**: Automatic detection of inconsistencies in the knowledge graph.

---

## 3. Metric: Constraint Discovery Value ($\mathcal{C}_{DV}$)

The value of a discovery is no longer measured by its "popularity" or "apparent novelty" and is now measured by the **irreversible reduction of the space of permissible hypotheses**:

$$\mathcal{C}_{DV} = \frac{\Delta \Omega_{excluded}}{\Omega_{total}} \times \text{FalsificationAttemptsSurvived}$$

Where $\Delta \Omega_{excluded}$ is the volume of the state space that the constraint eliminates as physically or biologically impossible.

---

## 4. Consequences

### Positive
- Popper becomes an algorithmic and computable data structure in real time.
- Exhaustive differentiation between correlational observations and mechanistic restrictions.
- Native integration with Marr's tri-level hierarchy and `BiologicalPrograms` from Neurodiagnoses and GeneForge.

### Negatives / Trade-offs
- Requires parsing and validation of formal logical predicates on evidentiary contracts.