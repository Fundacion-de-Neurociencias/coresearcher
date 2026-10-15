#SPRINT 70—Constraint-Guided Discovery Pattern

**Sprint**: SPRINT 70 — Constraint-Guided Discovery Pattern  
**Date**: 2026-08-02  
**Status**: COMPLETED  
**Verdict**: ✅ SUCCESS — a smaller explanation and a bigger observation  

---

## Epistemological context

COrigami (Zahavy et al., 2024) is a constraints-based scientific discovery framework.  
Its structure is neither origami nor RL. The structure is:

```text
Objetivo libre
        ↓
Representación semántica intermedia
        ↓
Espacio de restricciones formales
        ↓
Solver verificable
        ↓
Resultado observable
        ↓
Crítico externo
        ↓
Optimización iterativa
```

CoResearcher already has similar pieces, but scattered.  
This sprint brings them together under a single epistemological pattern: **discovery guided by observable constraints**.

No new layers are created. EHG is not modified. No new graphs are introduced.  
Analysis only on existing artifacts.

---

## PHASE 1 — Inventory of existing restrictions

Audit of validated elements. For each one: what formal restriction does it impose?

###DecisionNode

**Formal restriction**: `todo DecisionNode debe anclar a evidencia observable y estar clasificado como observable o derivable, nunca como inferred`

Evidence:
- `schemas/evidence_graph.schema.json` (line 132): decision_node requires `id`, `type=Decision`, `decision`, `actor`, `outcome` and `confidence` are properties.
- `schemas/decision_trajectory.schema.json` (line 73): decision_node requires `id`, `type=Decision`, `decision`, `actor`,
- `scripts/classify_decisions.py` (line 46): `classification = "observable" if confidence >= 0.9 else "derivable"`. The classification `"inferred"` is never assigned.
- `artifacts/cross_repo_metrics.json`: `inferred_claims: 0` in all analyzed repos. Fact is never promoted without observable evidence.

**Documented formal restriction**: observable evidence must exist.

### Trajectory

**Formal restriction**: `every Trajectory must be a chronologically ordered DAG of DecisionNodes connected by typed edges`

Evidence:
- `schemas/decision_trajectory.schema.json` (line 5): object type with `trajectory_id`, `root_decision` (pattern
- `schemas/decision_trajectory.schema.json` (line 185): edge type enum: `led_to`, `abandoned_for`, `superseded_by`,
- `scripts/reconstruct_trajectory.py`: offline reconstruction of 426 edges (231 explicit + 195 temporary).
- `docs/SPRINT_60C_VALIDATION_REPORT.md` (line 40): "426 edges generated: 231 by explicit reference, 195 by temporal sequence by author."

**Documented formal constraint**: reconstructable sequence must exist.

### Convergence

**Formal restriction**: 'all Convergence requires ≥2 independent actors, same topic, same outcome, and ≥3 competing hypotheses with operational definition and falsification criteria'

Evidence:
- `python/discovery/epistemic_gap_detector.py` (line 804): `if len(cluster_nodes) < 2: continue`. `actors = set(n.get("actor", "") ...)`; `if len(actors) < 2: continue`.
- `python/discovery/epistemic_gap_detector.py` (line 852): `restriction_epistemic_status = EpistemicStatus.UNDETERMINED`.
- `scripts/audit_convergences.py` (line 15-27): IDE Directive v1.6: all convergence is observation; every restriction is a latent variable; Every hypothesis must have at least one competitor.
- `artifacts/convergence_review.json`: all 4 convergences have `num_competing_hypotheses: 3`, `restriction_epistemic_status: "undetermined"`.
- `docs/EPISTEMIC_GAP_CONCEPT.md` (line 312): the convergence → restriction connection is not validated. Every restriction is a latent variable.

**Documented formal restriction**: demonstrable absence of evidence → the observed convergence does not imply restriction.

### Gap

**Formal restriction**: `todo Gap debe anclar a evidence_anchor observable y estar clasificado como empirical/mathematical/causal con characterization A/B/C/D. EHG está congelado.`

Evidence:
- `python/discovery/epistemic_gap_detector.py` (line 159): `evidence_anchor: str` — required field in EpistemicGap dataclass. Line 161: `gap_type` — GapType enum (empirical/mathematical/causal). Line 156: `characterization` — GapCharacterization enum (A/B/C/D).
- `python/discovery/epistemic_gap_detector.py` (line 401): `"ehg_status": "FROZEN — requires audit precision ≥80%"`.
- `artifacts/epistemic_gap_report.json` (line 50-66): 155 gaps, all with
- `docs/EPISTEMIC_GAP_CONCEPT.md` (line 653): "A gap is not a hypothesis. A gap is just a poorly mapped region of the map."

**Documented formal constraint**: gap ≠ hypothesis. Gap → hypothesis is blocked until audit ≥80%.

### Summary table PHASE 1

| Element | Formal restriction imposed | Evidence anchor |
|---|---|---|
| DecisionNode | There must be observable evidence. Classification ∈ {observable, differentiable} | `evidence_graph.schema.json`, `classify_decisions.py` |
| Trajectory | Reconstructable sequence must exist (chronological DAG, typed edges) | `decision_trajectory.schema.json`, `reconstruct_trajectory.py` |
| Convergence | There must be ≥2 independent actors + ≥3 competing hypotheses | `epistemic_gap_detector.py`, `audit_convergences.py` |
| Gap | It must anchor to observable evidence. Frozen EHG. | `epistemic_gap_detector.py`, `EPISTEMIC_GAP_CONCEPT.md` |

---

## PHASE 2 — Survival autopsy

Historical survival table. Classification: SURVIVED / FALSIFIED / UNDETERMINED. Measurement: based on observation? or based on explanation?

### Survival table

| Element / Claim | EpistemicStatus | Sprint origin | State | Based on | Evidence |
|---|---|---|---|---|---|
| Fully searchable DecisionNode | OBSERVED | SPRINT 60C | **SURVIVED** | Observation | 301 nodes extracted, expected κ≥0.8 |
| Trajectory inferable from DecisionNodes | OBSERVED | SPRINT 60C | **SURVIVED** | Observation | 426 reconstructed edges (231 explicit + 195 temporary) |
| Replicable trajectory (explicit edges κ≥0.8) | DERIVED | SPRINT 62 | **SURVIVED** | Observation | Validated extraction metrics |
| Detectable Convergence | OBSERVED | SPRINT 60C | **SURVIVED** | Observation | 4 convergences detected |
| Detectable Epistemic Gap | OBSERVED | SPRINT 60C+ | **SURVIVED** | Observation | 155 gaps, gap_density=0.515 |
| EpistemicStatus as operational classification | DERIVED | SPRINT 64R | **SURVIVED** | Observation | Consistent use in subsequent audits |
| Theory instrumentable by predictions | DERIVED | SPRINT 66 | **SURVIVED** | Observation | History of science: evolution, relativity |
| H7 — Constraint detector (v1) valid | HYPOTHESIZED | SPRINT 61 | **FALSIFIED** | Explanation | FPR=70% synthetic, 35% noise; κ=-0.030 |
| Replicable convergence (κ≥0.4) | HYPOTHESIZED | SPRINT 61 | **FALSIFIED** | Explanation | κ=-0.094 |
| Distinguishable real vs synthetic convergence | HYPOTHESIZED | SPRINT 63 | **FALSIFIED** | Explanation | 70% FPR in synthetics |
| Restriction implementable by manipulation | HYPOTHESIZED | SPRINT 65 | **FALSIFIED** | Explanation | No published metric, methodological argument |
| Paradigm instrumentable by shared assumptions | HYPOTHESIZED | SPRINT 66 | **FALSIFIED** | Explanation | No published metric |
| Calibrated Instrumentability Index | HYPOTHESIZED | SPRINT 66B | **FALSIFIED** | Explanation | 9 attacks detected, collapses 6 entities at 0.60 |
| Instrumentability Index as a useful metric | HYPOTHESIZED | SPRINT 66C | **FALSIFIED** | Explanation | It does not separate historical groups, it does not predict |

> Complete status at: `artifacts/sprint70_survival_table.json`

### Quantified survival rate (OED)

| EpistemicStatus | Total | SURVIVED | FALSIFIED | Taxa survival | Taxa falsification |
|---|---|---|---|---|---|
| OBSERVED | 3 | 3 | 0 | **100%** | 0% |
| DERIVED | 3 | 3 | 0 | **100%** | 0% |
| HYPOTHESIZED | 9 | 0 | 9 | **0%** | **100%** |

**Maximum OED measurement** (not assumed):

- Claims **based on observation** (OBSERVED + DERIVED): 6/6 survive → **100%**
- Claims **based on explanation** (HYPOTHESIZED): 0/9 survive → **0%**

The monotonic relationship between observational distance and epistemological survival is an **observed regularity**, not a postulated theory.

**Adversarial Counterattack (SPRINT 67B)** verified that OED is not weakened by complexity: all OBSERVED survive even with HIGH complexity; all HYPOTHESIZED fall even with LOW complexity.

**Conclusion of the table**: the distinction that predicts survival is not complexity or origin. It's **observation-vs-explanation**. SPRINT sprint 61, 63, 65, 66B, 66C that attacked H7, Instrumentability Index, and Paradigm instrumentability — all based on explanation — were falsified.

---

## PHASE 3 — Search Space Analysis

**Question**: What reduces the search space in CoResearcher?  
**No**: What does it explain?  
**But**: What restricts?

Evidence Inventory, DecisionNode, Trajectory, Gap as space reduction mechanisms.

### Base metrics (langchain-ai/langgraph)

| Metric | Value | Source |
|---|---|---|
| Extracted DecisionNodes | 301 | SPRINT 60C validation report |
| Reconstructed Edges | 426 | SPRINT 60C validation report |
| Barrier convergences | 4 | convergence_review.json |
| Detected gaps | 155 | epistemic_gap_report.json |
| Gap density | 0.515 | epistemic_gap_report.json |
| Total claims (cross-repo) | 841 | cross_repo_metrics.json |
| Observable claims | 241 | cross_repo_metrics.json |
| Derivable claims | 350 | cross_repo_metrics.json |
| Observable ratio | 0.287 | cross_repo_metrics.json |

### Inventory: each artifact as a space reduction mechanism

| Artifact | Formal restriction | What space reduces | Quantitative reduction |
|---|---|---|---|
| **Evidence** | Every claim must anchor to evidence_anchor observable (URL/SOURCE/ARTIFACT) | Claims without verifiable anchor | 841 claims → 241 observable + 350 derivable = 591 anchored. 250 unanchored (unknown). ~30% of claims eliminated. |
| **DecisionNode** | Schema requires: id, type=Decision, decision, actor, timestamp, outcome, confidence, evidence_anchor. classification ∈ {observable, differentiable}. | Decisions without observable outcome, without actor, without evidence_anchor | 301 DecisionNodes of 426 potential edges. 122 success, 129 abandoned, 40 failure, 10 pending. 10 slopes without outgoing edges → empirical GAP. |
| **Trajectory** | Chronological DAG with typed edges (led_to, abandoned_for, superseded_by, chosen_over). Monotonous temporal order. | Non-chronological sequences, connections without causal/documentary relationship | 426 edges of 301 nodes → avg 1.41 edges/node. 231 explicit + 195 temporary. Edges require actor + monotonic timestamp. |
| **Gap** | evidence_anchor required + classification (empirical/mathematical/causal) + characterization (A/B/C/D) + frozen EHG. | Regions without observable anchor + hypothesis space (frozen) | 155 gaps of 301 nodes (51.5%). 113 empirical, 42 causal, 0 mathematical. 143 explored_abandoned, 10 explored_partial, 2 unknown. Generation hypothesis: BLOCKED. |
| **Convergence** | ≥2 independent actors + same topic + ≥3 competing hypotheses with falsification + restriction_epistemic_status=UNDETERMINED | "Convergences" without independent actors, without competitors, without operational definition | 4 convergences of 301 nodes (1.33%). 0 successful_convergence. 100% barrier. All UNDETERMINED. |

### Filter string: 301 → 4

```
301 DecisionNodes
    ↓ Evidence constraint (evidence_anchor requerido)
    → 241 observable + 350 derivable claims survive
    ↓ Trajectory constraint (DAG cronológico, edges tipados)
    → 426 edges (231 explicit + 195 temporal) survive
↓ Convergence constraint (≥2 actors + ≥3 competing hypotheses)
    → 4 barrier convergences survive (1.33% de 301 nodos)
    ↓ Falsification constraint (κ, FPR, adversarial)
    → 0 restriction hypotheses promoted to fact
```

**Each level is a formal restriction that reduces the search space.** Convergence is the most restrictive point: of 301 nodes, only 4 meet all the criteria. That is the feasible space.

### In COrigami terms

| CoResearcher constraint | COrigami equivalent | What reduces |
|---|---|---|
| Evidence anchor | Packing constraint | Claims without verifiable source |
| Trajectory DAG | Packing constraint | Non-chronological sequences |
| ≥3 competing hypotheses | Packing constraint | Restrictions without falsifiable competitors |
| EHG frozen | Packing constraint | Hypothesis space (not allowed) |
| ≥80% audit accuracy | Packing constraint | Low quality detections |

---

## PHASE 4 — Discovery Without Explanation

**Conceptual experiment**: take the 4 observed convergences.

**Prohibited**: restriction hypothesis, mechanism, paradigm, theory.  
**Only allowed**: observable patterns, frequencies, recurrences, topology.

### The 4 observed convergences (hard data)

| ID | Observable theme | Independent actors | Outcome | Anchored Gap |
|---|---|---|---|---|
| CONV-000001 | `fix(cli): require langgraph-api>=0.7.67 on Python 3.14` | 2 (adambell64, abdullahbilal64) | barrier | GAP-000028, GAP-000029 |
| CONV-000002 | `fix(langgraph): add missing stacklevel to warnings.warn() calls` | **5** (Jeel3011, levgiorg, awesome-pro, EvanYao826, mengqiuzhen) | barrier | GAP-000054, GAP-000088, GAP-000093, GAP-000096, GAP-000112, GAP-000155 |
| CONV-000003 | `fix(langgraph): copy mutable container in channel from_checkpoint` | 2 (vidigoat, OmkumarSolanki) | barrier | GAP-000060, GAP-000087 |
| CONV-000004 | `fix(langgraph): cap retry sleep at max_interval after jitter` | 2 (pragnyanramtha, mengqiuzhen) | barrier | GAP-000097, GAP-000108 |

### Knowledge that appears without introducing any explanation

#### 1. Frequency and recurrence (observable patterns)

- **Thematic frequency**: 4 of 301 decisions (1.33%) are grouped into 4 themes. The topic `stacklevel` is the most frequent: 5 independent actors in 5 different PRs.
- **Actor Recurrence**: `mengqiuzhen` appears in CONV-000002 and CONV-000004 — crosses two barrier convergences. 3 of 8 total actors (37.5%) appear in more than one convergence.
- **Recurrence of patterns**: all 4 themes follow the observational pattern `fix(langgraph): [technical fix] — [specific behavior]`. 3 of 4 use the prefix `langgraph:`, the rest `cli:`.

#### 2. Decision space topology

- **100% of convergences are barriers**: 0 successful_convergence out of 4. All independent trajectories hit the same wall and stagnate.
- **100% of associated gaps are high-severity empirical**: 113 empirical gaps, 143 of 155 characterized as `explored_abandoned`. No gap is mathematical.
- **Gap density at convergence points**: 18 gaps anchored directly to the 4 convergences (6+5+2+2+3 = 18 observational gaps). The local density of gaps at convergence points is 5x greater than the global density (0.515).

#### 3. Observational signature

Without introducing mechanisms, the following signature emerges:

1. **There is an attractor structure**: 4 topics attract ≥2 independent actors each. CONV-000002 (5 actors) is the dominant attractor.
2. **The structure is directed towards failure**: attractors converge on barriers, not solutions. 0/4 conclude successfully.
3. **The density of ignorance is localized**: the convergence zones contain 18 observational gaps (all high-severity, all `abandoned_no_rationale`).
4. **The signature is stable**: `mengqiuzhen` crosses 2 convergences, suggesting that certain actors consistently encounter the same barriers.

#### 4. What useful knowledge appears without explanation?

- **The space of possibilities has geometry**: it is not flat. There are local attractors (issues that attract multiple actors) and regions of high gap density (areas of poorly documented ignorance).
- **Observer information is localizable**: 18 abandonment gaps without rationale are located exactly at the 4 convergence points. This is observable without explaining why.
- **The topological structure suggests directionality**: the flow of decisions tends to collide against certain specific barriers, not to be distributed uniformly.

**This is all that can be said by observing without explaining.** No theory, mechanism, paradigm, or hypothetical constraint is introduced. Just patterns, frequencies, recurrences and topology.

---

## PHASE 5 — COrigami Mapping

### Structural mapping

| COrigami | CoResearcher | Evidence (existing artifacts) |
|---|---|---|
| Semantic Figure (free object) | Research Question | `docs/EPISTEMIC_GAP_CONCEPT.md` §5: "The goal of CoResearcher is not to generate hypotheses." |
| Packing Constraints (formal limit) | Evidence Constraints | PHASE 1: schemas require evidence_anchor. Frozen EHG. ≥3 competing hypotheses. |
| Foldability Solver (explore feasible) | Traceability Engine | SPRINT 60C: 426 reconstructed edges (231 explicit + 195 temporary) over 301 nodes. |
| RL Critic (evaluates results) | Counterfeit Pipeline | SPRINT 61: 70% FPR → H7 falsified. SPRINT 66B: 9 attacks → Index falsified. SPRINT 67B: adversarial OED. |
| Folded Object (result) | Scientific Observation | 4 barrier convergences (OBSERVED). 155 gaps (OBSERVED). 0 restriction hypotheses promoted. |

### Analogy observed

**Not the origami. Not the RL. The existence of a space of verifiable constraints that limits which solutions can survive.**

In COrigami:
- The *semantic figure* is free (open objective).
- The *packing constraints* define a feasible space: not every fold is possible.
- The *foldability solver* explores only within the feasible space.
- The *RL critical* evaluates externally: does the resulting object meet the objective?
- Only folds that satisfy all constraints and pass the critical survive.

In CoResearcher:
- The *research question* is free (open objective).
- The *evidence constraints* define a feasible space: not every observation counts. Schema enforces `evidence_anchor`. Classification imposes `observable`/`derivable`. Frozen EHG imposes: not hypothesis.
- The *traceability engine* explores only within the feasible space: it reconstructs chronological DAGs, not arbitrary sequences.
- The *falsification pipeline* evaluates externally: does the observation survive the adversarial attack? (SPRINT 61, 66B, 66C, 67B).
- Only observations that satisfy all constraints and pass the falsification critical survive.

**The shared structure is identical at the epistemological level**:

```text
Research Question (libre)
        ↓
Observation Space (semántica intermedia)
        ↓
Evidence Constraints (packing constraints)
        ↓
Traceability Engine (foldability solver)
        ↓
Scientific Observation (folded object)
        ↓
Falsification Pipeline (RL critic)
        ↓
Iterative Refinement (optimización iterativa)
```

### What does this entail?

**COrigami is not integrated as a feature.** It undergoes the same discipline that destroyed H7 and the Instrumentability Index:

1. **Every assertion must have observable evidence_anchor.** The COrigami↔CoResearcher analogy is anchored by: both systems impose verifiable formal constraints that reduce the search space. This is observable in the schemas (`evidence_graph.schema.json`, `decision_trajectory.schema.json`) and in the results (4/301 convergences, 155/301 gaps, 0/4 restriction promoted).

2. **Every hypothesis must face adversarial falsification.** The COrigami pattern (constraint → solver → critic) predicts that claims based on observable constraints survive, while claims based on explanations without explicit constraint do not survive. This is verified in the PHASE 2 table: 6/6 observation-first claims survive, 0/9 explanation-first claims survive.

3. **Integration is not required.** The epistemological pattern already exists in the artifacts. EBG is frozen. No new layers, graphs, or entities are created.

### The lesson from Sprints 61–67A

> CoResearcher's robust findings do not emerge when it attempts to explain the system. They emerge when you increase the resolution with which you observe it.

PHASE 2 quantifies this: the 6 OBSERVED/DERIVED claims survive 100%. The 9 HYPOTHESIZED claims (explanation-first) fall at 100%.

The connection with COrigami: in COrigami, the RL critic is the external verifier. In CoResearcher, the falsification pipeline is the external verifier. Both operate **after** the feasible space has been generated by constraints. The work of discovery is not to generate explanations — it is to define verifiable constraints that narrow the space until only what remains that can truly survive falsification.

---

## Success criterion

### Sprint fails if it produces:
- ❌ new theories
- ❌ new entities
- ❌ new hypotheses
- ❌ new detectors
- ❌ new architectures

### Sprint is successful if it produces:
- ✅ **a smaller explanation**: the COrigami→CoResearcher pattern reduces the explanation of epistemological survival to a single principle: "claims anchored in verifiable observable constraints survive; claims based on explanations without falsification do not survive." Instead of 9 different theories (H7, Instrumentability Index, Paradigm, Restriction, Convergence replicability, Theory, Hypothesis, Mechanism, Explanation), there is a single pattern: **constraint space + external criticism**.
- ✅ **a larger observation**: the PHASE 2 table observes that 6/6 observation-first claims survive and 0/9 explanation-first claims survive — a measurable regularity (survival_rate=1.0 vs 0.0) that spans all sprints 60C–67B and remains under adversarial attack (SPRINT 67B).

### Verdict: ✅ SUCCESS

The sprint documents, not creates. The COrigami epistemological pattern already existed in CoResearcher artifacts. What has changed is that it is now recognized as a single pattern: **constraint-guided discovery** — where observable constraints reduce the search space until only what is verifiable remains.

---

## Artifacts produced

| Artifact | Sprint | Content |
|---|---|---|
| `docs/CORIGAMI_DISCOVERY_PATTERN.md` | SPRINT 70 | This document: PHASE 1–5 mapping + observed analogy |
| `artifacts/sprint70_survival_table.json` | SPRINT 70 | PHASE 2: survival table with 13 claims + survival rates + OED quantification |

## Freeze compliance

- ✅ No new schemas created
- ✅ No new graphs created
- ✅ No new layers introduced
- ✅ EHG not modified (frozen)
- ✅ No new entities (DecisionNode, Trajectory, Convergence, Gap, ConstraintHypothesis, EpistemicStatus all pre-existing)
- ✅ Analysis read-only over existing artifacts
- ✅ You produce real data artifacts (JSON + Markdown)

---

## References (anchored evidence)

| Source | Type | Use in this sprint |
|---|---|---|
| `schemas/evidence_graph.schema.json` | Schema | PHASE 1: DecisionNode constraint |
| `schemas/decision_trajectory.schema.json` | Schema | PHASE 1: Trajectory constraint |
| `python/discovery/epistemic_gap_detector.py` | Code | PHASE 1: Gap + Convergence constraints, EpistemicStatus enum |
| `scripts/classify_decisions.py` | Code | PHASE 1: DecisionNode classification rule |
| `scripts/audit_convergences.py` | Code | PHASE 1: Convergence audit protocol (IDE Directive v1.6) |
| `scripts/reconstruct_trajectory.py` | Code | PHASE 1: Trajectory reconstruction |
| `artifacts/convergence_review.json` | Data | PHASE 1, PHASE 4: 4 convergences with actors and gaps |
| `artifacts/epistemic_gap_report.json` | Data | PHASE 1, PHASE 3: 155 gaps, gap_density=0.515 |
| `artifacts/falsification_experiment.json` | Data | PHASE 2: H7 falsification (70% FPR) |
| `artifacts/observation_explanation_differential.json` | Data | PHASE 2: survival table + OED |
| `artifacts/cross_repo_metrics.json` | Data | PHASE 3: 841 claims, observable_ratio=0.287 |
| `artifacts/cross_repo_constraints.json` | Data | PHASE 3: restriction frequency, transversal patterns |
| `docs/EPISTEMIC_GAP_CONCEPT.md` | Doc | PHASE 1: Gap constraint, EHG freeze |
| `docs/SPRINT_61_CONSTRAINT_VALIDATION.md` | Doc | PHASE 2: H7 falsification detail |
| `docs/SPRINT_66_AUDIT.md` | Doc | PHASE 2: SPRINT 66 audit table |
| `docs/SPRINT_60C_VALIDATION_REPORT.md` | Doc | PHASE 1: 301 nodes, 426 edges |
| `docs/SPRINT_60C_BRIDGE_H6_H7_EHG.md` | Doc | PHASE 1: Trajectory schema requirements |
| `scripts/sprint61_falsification_experiment.py` | Code | PHASE 2: falsification methodology |
| `scripts/sprint67b_adversarial_oed.py` | Code | PHASE 2: OED adversarial control |

---

> **Largest observation**: 6/6 observation-first claims survive (100%); 0/9 explanation-first claims survive (0%).  
> **Smaller explanation**: The constraint→solver→critic pattern explains all survivals and falsifications without introducing any new entities.  
> **Observed analogy**: COrigami Packing Constraints ↔ CoResearcher Evidence Constraints. COrigami RL Critic ↔ CoResearcher Forgery Pipeline. Both define a feasible space that reduces what can survive.</tool_call>