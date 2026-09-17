#ADR-DISCOVERY-001: Epistemic Trajectory Framework & Representation Primitives

**Version 1.1.0** - Architecture Decision Record  
**Status**: Canonical Standard - Epistemological Foundation  
**Domain**: Scientific Discovery Core & Representation Theory

---

## 1. Context and Critical Diagnosis

Traditionally, AI systems for science (including early iterations of CoResearcher) have operated under an eminently **documentary and cumulative** paradigm:
```
Paper → Extraction → Claim → Evidence Score
```
In this model, the atomic unit of knowledge is the static `Claim` supported by literature.

However, the great historical scientific advances (Euclid, Euler-Lagrange, Einstein, Schrödinger, Marr, or the transition from biomarkers to *Biological Programs*) **never** begin by simply formulating an isolated hypothesis. They begin by creating a **new representation** (a new observational and conceptual language):

```
Newton          → Representación: Espacio de estados mecánico
Einstein        → Representación: Espacio-tiempo pseudoriemanniano
Schrödinger     → Representación: Espacio de Hilbert / Función de onda
Marr            → Representación: Jerarquía Tri-Nivel (Computacional / Algorítmico / Implementacional)
Neurodiagnoses  → Representación: Biological Programs
```

The value does not reside in the isolated terminal response, but in the **representation** and the **epistemological trajectory** traveled in the face of real unknowns ("*We only care about the unknowns*").

---

## 2. Architectural Decision

### 2.1. The Authentic Chain of Discovery
The canonical epistemological chain is formally established:
$$\mathbf{Constraint} \longrightarrow \mathbf{Representation} \longrightarrow \mathbf{Hypothesis} \longrightarrow \mathbf{Prediction} \longrightarrow \mathbf{Evidence}$$

The same mass of empirical evidence can give rise to radically different hypotheses depending on the representational space on which it is projected.

### 2.2. First Level Primitive: `Representation`
`Representation` is introduced as a first-order entity in the knowledge graph:
- `representation_id`: Canonical identifier (e.g. `REP-GRAPH-TOPOLOGY-001`, `REP-BIOLOGICAL-PROGRAM-042`).
- `name`: Name of the observational/conceptual formalism.
- `observables_space`: Space of variables and patterns that this framework makes **visible** (and what it leaves **invisible** according to [REP-001](file:///c:/Users/usuario/coresearcher/docs/REP-001_REPRESENTATION_AND_OBSERVABILITY.md)).
- `invariant_principles`: Preserved physical, biological or mathematical invariants.
- `marr_level`: Marr's explanatory level (`COMPUTATIONAL`, `ALGORITHMIC`, `IMPLEMENTATIONAL`).

### 23. Canonical Structure of the Trajectory (`HypothesisTrajectory`)
Each hypothesis is necessarily formalized as a living trajectory that contains:
- `hypothesis_id`: Unique canonical identifier.
- `representation_id`: Identifier of the representation that generates the space of observables.
- `marr_explanation_level`: Marr's explanatory level (`COMPUTATIONAL`, `ALGORITHMIC`, `IMPLEMENTATIONAL`).
- `originating_constraints`: Physical, biological or logical restrictions from which it emerges.
- `alternatives`: Explicit space of competing alternative hypotheses or explanations (ADR-DISCOVERY-003).
- `predictions`: Testable and falsifiable predictions generated deductively.
- `failed_predictions`: Predictions that collapsed empirically (revision catalysts).
- `survived_predictions`: Predictions that withstood falsification experiments.
- `revisions`: Immutable history of mutations and hypothesis refinements.
- `supporting_evidence`: Empirical and experimental evidence that supports it.
- `scope_conditions`: Explicit domain of validity and boundary conditions (ADR-DISCOVERY-004).
- `discovery_value`: Target discovery value (ADR-DISCOVERY-005).

---

## 3. Integrated TRACES Ontology

CoResearcher adopts the 6 ontological axes of the discovery trajectory:
- **T (Tools)**: Instrumentation and empirical interfaces used.
- **R (Repair)**: Adjustment mechanisms for failed predictions.
- **A (Alternatives / Alternatives)**: Simultaneous contrast against competing hypotheses.
- **C (Coherence / Coherence)**: Theoretical consistency and not systemic contradiction.
- **E (Evidence / Evidence)**: Real biological and physical data (zero simulation).
- **S (Scope / Scope)**: Precise definition of the limits of applicability.

---

## 4. Consequences

### Positive
- Definitive transition from bibliographic engine to **representational scientific discovery engine**.
- Prevents the mixing of Marr levels of analysis and decouples the formulation of hypotheses from the bias of the previous observable space.
- Complete epistemological traceability: the chosen representation, the discovered restrictions and the falsification trajectory are audited.

### Negatives / Trade-offs
- Greater expressiveness required in the ontological record.