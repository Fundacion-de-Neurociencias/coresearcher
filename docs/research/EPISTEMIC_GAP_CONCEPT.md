# EPISTEMIC GAP: SCIENTIFIC CONCEPT
**Status**: Scientific concept (no schema, no graph, no architectural layer)
**Relationship**: Extends CoResearcher's mission without breaking the Architecture Freeze
**Date**: 2026-08-01 (v1.6 — Epistemic Status + IDE Directive + wishful mnemonic)
**Origin**: Epistemological Triumvirate (Evidence, Mathematics, Causality)

---

## 1. Reformulated Objective

The goal of CoResearcher is **not** to generate hypotheses.
Not even detecting gaps.
Not even detecting convergences.

The objective is:

> **Mapping the geometry of knowledge.**

And the central object of that geometry are the **constraints**:

> **What implicit constraints were shared by all trajectories that led to our current knowledge?**

### 1.1 Scientific Object Hierarchy (corrected)

```
Restriction → "Everyone assumed X" (THE CENTRAL OBJECT) ⭐
Convergence → "Many roads end here" (constraint footprint)
Gap          → "No sabemos X"           (ausencia de trabajo)
Residue → "No one questioned Y" (manifestation of restriction)
Bifurcation → "A was chosen over B" (paradigmatic decision)
```

**Convergences are traces. Restrictions are the object.**

> No convergence has scientific value by itself.
> Its value depends on the shared restriction that explains said convergence.

### 1.2 The definitive question

> **What implicit constraints were shared by all trajectories that led to our current knowledge?**

Scientific revolutions are born from identifying unquestioned assumptions and eliminating them.

---

## 2. Constraints: The Central Object

### 2.1 Concept

A **constraint** is an implicit assumption that limits the space of possibilities of a scientific trajectory.

Convergences are simply traces of constraints.

### 2.2 Example: Einstein

The observed convergence: Lorentz, Poincaré, Einstein, Minkowski — all find similar anomalies.

But that's not what's interesting.

The interesting thing is that everyone shared:
- constant speed of light ⭐
- space-time continuum ⭐

Einstein broke a restriction. It didn't follow a trajectory.

### 2.3 Example: Quantum Mechanics

Bohr, Heisenberg, Schrödinger, Dirac. Many trajectories. Many convergences.

But the revolution was not born of convergence. It was born when certain classical restrictions were no longer assumed.

### 2.4 Types of restrictions

| Type | Description | Question |
|------|-------------|----------|
| `technica` | Technical limitation | Does current technology not allow it? |
| `conceptual` | Conceptual assumption | Is something assumed without question? |
| `historica` | Historical dependence | Did the chosen path eliminate alternatives? |
| `matematica` | Mathematical constraint | Does the formulation prevent it? |
| `ontologica` | Ontological limitation | Does the model of the world not contemplate it? |

### 2.5 Fundamental conceptual rule

> **No convergence has scientific value by itself.**
> **Its value depends on the shared constraint that explains said convergence.**

### 2.6 Constraints are latent variables

> **No constraint is observable.**
> **Only its manifestations are observable.**

The constraints are much more similar to what in physics we would call a **latent variable**.

We observe:
- decisions
- forks
- dropouts
- convergences

But we never directly observe the constraint. We observe its effects.

Therefore, the correct pipeline is not:

```text
convergence → shared constraint (suggests direct causality)
```

Otherwise:

```text
observed convergence
    ↓
shared constraint hypothesis
    ↓
falsification attempts
    ↓
provisional restriction
```

Because if not, we would violate our own constitutional principle.

**Analogy with Einstein**: Einstein never observed curved space-time. What he observed were: perihelion of Mercury, deviation of light, mass-energy equivalence. The curvature was an explanatory hypothesis, not an observation.

**Analogy with CoResearcher**: We observe "5 teams → same barrier". That is observable. But "everyone shares constraint X" is a hypothesis. Still. And it should be labeled as such.

### 2.7 Causal structure

```
Restricciones (causa, no observada)
    ↓
Decisiones (observadas)
    ↓
Trayectorias (observadas)
    ↓
Convergencias (observadas)
```

We are traversing the graph backwards. We are doing **reverse inference**. And that is exactly what science does.

---

## 3. Epistemological Framework: The Source of Constraints

### 3.1 The corrected asymmetry

The above causal structure:

```text
Restricciones → Decisiones → Trayectorias → Convergencias
```

It is correct but incomplete.

Restrictions don't appear out of nowhere. They also have origins.

In science, restrictions usually come from three sources:

```text
Evidencia disponible
+
Matemática disponible
+
Ontología aceptada
```

Curiously, our own triumvirate.

### 3.2 The fundamental unit

> The fundamental unit is not the restriction. It is the **epistemological framework**.

A framework generates constraints.
Constraints generate decisions.
Decisions generate trajectories.
Trajectories generate convergences.

```text
Marco epistemológico
    ↓
Restricciones
    ↓
Decisiones
    ↓
Trayectorias
    ↓
Convergencias
```

### 3.3 Example: Einstein

Constraint: space-time continuum.

Where did it come from? Not from a divine law. Came from:
- differential mathematics available
- the available evidence
- the accepted physical ontology

### 3.4 Example: Quantum Mechanics

Restriction: classic trajectories.

Where did it come from? From an inherited ontology.

### 3.5 Manifestations of the same framework

Two seemingly different constraints can come from the same framework.

Historical example:
- continuity
- determinism
- locality

There are three independent restrictions. They are manifestations of a specific vision of the universe.

### 3.6 Implication for H7

Until now H7 seemed aimed at rebuilding restrictions.

But perhaps the real objective is:

> reconstruct epistemological frameworks

The object of audit is not only convergence, but the framework that generates it.

---

## 4. Inference Audit

### 4.1 The missing piece

We currently have:

```text
Observación
    ↓
Restriction hypothesis
```

But we do not have formalized:

```text
Why this hypothesis and not another?
```

### 4.2 Proposed new constitutional principle

> **Every constraint hypothesis must explicitly list competing alternative hypotheses.**

Example:

Remark:
> 5 teams crash with stacklevel warnings.

Hypothesis A:
> historical restriction (backwards compatibility)

Hypothesis B:
> technical limitation (poorly designed API)

Hypothesis C:
> linker artifact (false positive)

Until you try to falsify B and C, A is not an explanation. It's just a possibility.

### 4.3 Epistemological states

It is not enough to say "I know" / "I don't know."

You have to be able to say:

```text
observé esto       (observable)
infiero esto       (derivable)
I hypothesize this (hypothesis)
desconozco esto    (ignorancia explícita)
```

They are different epistemological states.

### 4.4 Implementation

Adding `desconocida` to the RestrictionType taxonomy is the first step.

The next step is for each convergence audit to require:
1. List competing alternative hypotheses
2. Designate one as primary
3. Define falsification criteria for alternatives

### 4.5 Epistemic Status (v1.6 — IDE Directive)

It is not enough to say "I know" / "I don't know."

You have to be able to say:

```text
OBSERVED       — observé esto directamente en evidencia
DERIVED        — derivé esto lógicamente de observaciones
HYPOTHESIZED   — propongo esto como explicación, no falsada
FALSIFIED — this hypothesis was falsified by evidence
UNDETERMINED — multiple hypotheses explain equally well
```

They are different epistemological states.

**Fundamental rule**:

> A false theory is worse than admitting that we still have no theory.

**Implementation**:

- `EpistemicStatus` enum in `python/discovery/epistemic_gap_detector.py`
- `ConstraintHypothesis` dataclass with competing hypotheses
- `determine_restriction_epistemic_status()` function
- All convergence tagged with `epistemic_status=OBSERVED`
- Any restriction tagged with `restriction_epistemic_status=UNDETERMINED` (pre-audit)
- The system can respond "we don't know" (`UNDETERMINED`) without degrading the evaluation

### 4.6 Banning "Wishful Mnemonic" (v1.6)

McDermott criticized calling:

```text
UNDERSTAND
GOAL
THINK
REASON
```

to modules that perhaps they do not understand, do not have goals and do not reason.

That is exactly the danger of:

```text
Constraint
Paradigm
Reasoning
Understanding
Discovery
```

if they are not operationally defined.

**Guideline for the IDE**:

> It is prohibited to introduce ontologically loaded terms without operational definition and falsification criteria.

For example:

❌ "restriction detected"

✔ "restriction hypothesis that explains the observed convergence"

### 4.7 Analogy with LRM Reasoning (article on chain-of-thought)

The article on LRM (Large Reasoning Models) separates three things that are normally mixed together:

1. **Result** — Did you arrive at a correct answer?
2. **Observable process** — What steps did you say you followed?
3. **Real mechanism** — What really happened within the system?

The central thesis is that chains of thought may not be a faithful description of the internal mechanism. They can be a useful after-story, but not necessarily a causal one.

That connects directly with CoResearcher's constitutional principle:

> Every DecisionNode must be Observable or Derivable. Never Inferred.

The article says:

> Don't confuse thinking tokens with real reasoning.

CoResearcher says:

> Don't confuse a later explanation with an observed decision.

They are the same warning applied to different domains.

**The structural analogy**:

```text
LRM:                                CoResearcher:
Internal mechanism (latent) ←→ Constraints (latent)
Activaciones                    ←→   Decisiones (observadas)
Thinking tokens (observables)  ←→   Trayectorias (observadas)
Respuesta (observable)         ←→   Convergencias (observadas)
```

A convergence in CoResearcher is conceptually equivalent to an emergent phenomenon observed in an LRM. You see the effect. You don't see the cause. The cause must be proposed as a hypothesis and then attempted to falsify it.

**"AI can be right for the wrong reasons"**:

A system can satisfy:
- Evidence (correct observation)
but fail at:
- Mathematics (incoherent mechanism)
or in:
- Causality (false explanation)

The result may still be correct. But not knowledge.

---

## 5. Convergence: Constraint Footprint

### 3.1 Why convergences matter

A gap can simply be absence of work.
A convergence implies that multiple independent trajectories hit the same wall.

But convergence is just the **symptom**. The restriction is the **disease**.

### 3.2 The correct scientific question

```
5 actores
↓
misma barrera
↓
convergence
↓
What restriction did those 5 actors share?
```

Because there may appear something like:
- a poorly designed API
- a conceptual limitation
- a historical dependency
- a wrong abstraction

### 3.3 Types of convergence

```
Case 1: Successful convergence
  → Trayectorias independientes → misma conclusión
  → Evidencia convergente

Case 2: Barrier convergence ⭐
  → Trayectorias independientes → misma barrera
→ Shared restriction
```

Barrier convergence is the most valuable because it points directly to a shared constraint.

### 3.4 Empirical results

4 barrier convergences detected in langchain-ai/langgraph:

| ID | Theme | Actors | Hypothetical constraint |
|----|------|---------|--------|
| CONV-000001 | langgraph-api Python 3.14 | 2 | Version dependency? |
| CONV-000002 | warnings.warn() stacklevel | **5** | Preservation of warnings semantics? |
| CONV-000003 | mutable container from_checkpoint | 2 | Mutability model? |
| CONV-000004 | retry sleep max_interval | 2 | Retry semantics? |

CONV-000002 is especially promising: 5 independent actors crashing into the same barrier.

---

## 4. From Gap to Restriction: Pipeline

### 4.1 Natural evolution

```
Fase 1 (conseguida): Reconstrucción de decisiones
Question: What did they do?
  Objeto: DecisionNode

Fase 2 (en marcha): Reconstrucción de trayectorias
Question: How did they get here?
  Objeto: TrajectoryGraph

Fase 3 (actual): Convergencias
Question: Where do they all collide?
Object: Convergence (footprint)

Fase 4 (futuro): Reconstrucción de restricciones ⭐
Question: What assumption did everyone share?
Object: Restriction (THE OBJECT)

Fase 5 (revolucionario): Eliminación sistemática de restricciones
Question: What happens if we eliminate this assumption?
Object: Counterfactual → Hypothesis
```

### 4.2 The bridge with EHG

Until now the EHG was aimed at:
```
gap → hypothesis (weak)
```

Now it could become:
```
convergence → shared constraint → counterfactual → hypothesis
```

**Example**:

Convergence:
> They all crash with stacklevel warnings.

Inferred constraint:
> Everyone assumes that the current semantics of warnings must be preserved.

Counterfactual:
> What if that semantics is wrong?

Hypothesis:
> A different traceability system eliminates the barrier.

That is already a scientifically defensible hypothesis.

---

## 5. Epistemic Gap: Secondary Object

### 5.1 Definition

An **Epistemic Gap** is a region of knowledge space where ignorance is classifiable.
It is a secondary item: useful but less valuable than restrictions.

### 5.2 Gap Characterization (A/B/C/D)

| Type | Description | Example |
|------|-------------|---------|
| **A** | Never explored | Discrete space-time (1905) |
| **B** | It was explored and abandoned | Luminiferous ether |
| **C** | It was partially explored | Quantum gravity |
| **D** | We do not know if it was explored | Documentary lagoon |

### 5.3 Empirical results

155 gaps detected:
- A (never_explored): 0
- B (explored_abandoned): 143
- C (explored_partial): 10
- D (unknown_exploration): 2

---

## 6. Paradigm Residue

### 6.1 Concept

What remained between paradigmatic transformations.

### 6.2 Documented limitation

**Result**: 0 paradigm residues detected.

**Diagnosis**: 0 edges `superseded_by`/`abandoned_for`/`chosen_over` in the data (0 of 426 edges).

**Three explanations**:
1. Shallow extraction: see file changes, not persistent assumptions
2. Implicit residues: residues are almost never explicit
3. Unit of analysis too small: residuals appear between trajectories, not between commits

**Conclusion**: A paradigm does not live in commits. It lives in assumptions, mental models, mathematical constraints, ontologies.

**Not a bug**: It is a known limitation that requires H7.

---

## 7. H7: Reconstruction of Possibility Spaces

### 7.1 The emerging hypothesis

```
H6 reconstruye trayectorias.
H7 reconstruye espacios de posibilidades.
```

### 7.2 The transformed EHG

The day we can reconstruct spaces of possibilities, the EHG stops being a hypothesis generator and becomes something much more interesting:

> a systematic detector of unquestioned restrictions.

### 7.3 Why it is revolutionary

The greatest scientific revolutions have been born exactly there:
not to find a new answer, but to identify the restriction that no one was questioning.

---

## 8. EHG: FROZEN

The connection → EHG is **frozen**.

No hypothesis is generated until:
1. Convergences are audited and their restrictions identified
2. Shared constraints are validated
3. H7 validate the reconstruction of possibility spaces

A gap is not a hypothesis. A convergence without identified restriction either.

---

## 9. Relationship with Architecture Freeze

### 9.1 What it does NOT do

- ❌ Does not add new nodes to EvidenceGraph
- ❌ Does not add new graphs
- ❌ Does not add new architectural layers
- ❌ Does not create new schemas
- ❌ Does not modify existing schemas
- ❌ Does not connect to EHG (frozen)

### 9.2 What it DOES do

- ✅ Place restrictions as the central object of knowledge
- ✅ Treat convergences as traces, not as final object
- ✅ Rephrase the central question towards shared constraints
- ✅ Mapping the geometry of knowledge
- ✅ Detects gaps (secondary object)
- ✅ Detects convergences (traces of restrictions)
- ✅ Documents paradigm residues limitation
- ✅ Prepare the ground for H7
- ✅ Produces derived (read-only) analysis on existing data

---

## 10. Implementation

### 10.1 Detector

Location: `python/discovery/epistemic_gap_detector.py`

Function: Detects gaps, convergences, paradigm residues from existing TrajectoryGraph.

### 10.2 CLI Script

Location: `scripts/detect_epistemic_gaps.py`

### 10.3 Audit Scripts

- `scripts/audit_convergences.py` — **Priority 1**: validate convergences and constraints
- `scripts/audit_paradigm_residues.py` — Diagnose 0 residues
- `scripts/detect_epistemic_gaps.py` — Generates gap sample (secondary priority)

### 10.4 Artifacts

- `artifacts/epistemic_gap_report.json` — Full report
- `artifacts/epistemic_gap_report.md` — Readable report
- `artifacts/epistemic_gap_audit_sample.json` — Gap sample
- `artifacts/epistemic_gap_convergence_audit.json` — **Priority 1**
- `artifacts/epistemic_gap_residue_audit.json` — Waste diagnostics

---

## 11. Non-Goals

- ❌ DO NOT generate hypotheses (frozen EHG)
- ❌ DO NOT treat convergences as final object (they are traces)
- ❌ DO NOT connect to EHG until validation
- ❌ DO NOT implement as JSON schema
- ❌ DO NOT add as node in EvidenceGraph
- ❌ DO NOT create new separate graph
- ❌ DO NOT rigidify the Triumvirate as an ontology
- ❌ DO NOT break the Architecture Freeze
- ❌ DO NOT declare victory without restrictions audit

---

## 12. Priorities

### Priority 1
Audit the 4 convergences. For each, identify the hypothetical shared constraint.

### Priority 2
Reconstruct shared constraints between trajectories.
Not decisions. Don't commit. Restrictions.
Questions: what was never questioned? What dependency always appears? What abstraction remains constant? What barrier reappears?

### Priority 3
Prepare the ground for H7.
H6 reconstructs trajectories. H7 reconstructs spaces of possibilities.

### The critical audit

> **Do the 4 convergences correspond to real shared constraints or are they simply statistical artifacts produced by the linker?**

Until that is answered, everything else remains an attractive hypothesis, not an observation. And precisely our constitutional principle requires distinguishing both things.

---

## 12.5 Constitutional Principle (SPRINT 63)

> No conceptual entity has the right to exist within CoResearcher.
> It must earn its existence through explanatory power, predictive capacity,
> stability between observers and resistance to falsification.

That applies the same to:
-DecisionNode
- Trajectory
- Convergence
- Restriction
-Hypothesis
- Epistemic Gap

or any other future entity.

**Current state of each entity** (SPRINT 63):

| Entity | State | Evidence |
|---------|--------|-----------|
| DecisionNode | VALIDATED | 301 decisions extracted, audited |
| Trajectory | PROMISING | 426 edges, functional reconstruction |
| Convergence | OBSERVED | 4 convergences detected |
| Restriction | UNDETERMINED | Variable PARTIALLY_OPERATIONAL (50%) |
| Hypothesis | FROZEN | EHG frozen until validation |
| Epistemic Gap | OBSERVED | 155 gaps detected |

---

## 13. Status

**Today** (v1.6):
- Constraints placed as a central object, recognized as latent variables
- Maxim: "No restriction is observable. Only its manifestations are observable."
- Correct pipeline: observed convergence → restriction hypothesis → falsification → provisional restriction
- Experimental taxonomy of restrictions added to the detector (RestrictionType enum)
- **EpistemicStatus** enum added (OBSERVED/DERIVED/HYPOTHESIZED/FALSIFIED/UNDETERMINED)
- **ConstraintHypothesis** dataclass with competing hypotheses + operational definition + falsification
- **determine_restriction_epistemic_status()** function to evaluate competing hypotheses
- All convergence tagged with `epistemic_status=OBSERVED`
- Any restriction labeled as `restriction_epistemic_status=UNDETERMINED` (pre-audit)
- **Ban on "wishful mnemonic"** (McDermott): ontologically charged terms require operational definition
- H7 reformulated: it is no longer just Branch Detection, it is **Constraint Reconstruction**
- 4 barrier convergences detected (pending audit with taxonomy)
- 155 gaps detected (secondary object)
- 0 paradigm residues (documented limitation, requires H7)
- Frozen EHG
- Defined critical audit

**Next steps** (in order):
1. **Audit 4 convergences** → for each one: restriction hypothesis + type (taxonomy) + falsification + competitor
2. Reconstruct shared constraints between trajectories (reverse inference)
3. Prepare H7 (Constraint Reconstruction — reconstruction of possibility spaces)
4. If H7 validates: systematic detector of unquestioned restrictions

**The definitive bridge with EHG**:
```
Observed convergence
    ↓
Restriction hypothesis
    ↓
Contrafactual
    ↓
Restriction removal
    ↓
Nuevo espacio de posibilidades
    ↓
Hypothesis
```

Einstein did not discover relativity by looking for answers.
He discovered relativity **by removing an inherited restriction**.

**Vision**:
> a systematic detector of unquestioned restrictions.
> The greatest scientific revolutions have been born exactly there.
> Not to find a new answer, but to identify the restriction that no one was questioning.

---

*The geometry of knowledge is more important than the catalog of ignorance.*
*Convergences are traces. Restrictions are the object.*
*Before theorizing, audit. Before declaring victory, distinguish observation from hypothesis.*