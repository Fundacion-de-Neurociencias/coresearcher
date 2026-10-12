#AUDIT-AG-006—Surviving Constraints Inventory

**Date**: 2026-08-02
**Status**: CLOSED — Mature. No follow-up unless new tested entities appear.
**Objective**: List all constraints, maxims, freezes, prohibitions, invariants and operational rules that have survived falsification. No new hypotheses. No new entities. Without architecture. Only cartography.

---

## 1. Executive Summary

The evidence accumulated from SPRINT 60C to AUDIT-AG-005 points to something curious:

```text
Las explicaciones construidas dentro de CoResearcher
han mostrado una tasa de supervivencia inferior
a las restricciones observacionales.
```

We do not claim that it is a law. But there are enough observations to justify a systematic inventory of everything that has survived while other buildings were destroyed.

This audit does not create anything new. Just classify.

---

## 2. Inventory of Surviving Constraints

### SC-001: Evidence Anchor Constraint

| Field | Value |
|-------|-------|
| **ID** | SC-001 |
| **Type** | Schema constraint |
| **Origin** | SPRINT 60C, `schemas/evidence_graph.schema.json` |
| **Evidence** | Every claim must anchor to evidence_anchor observable (URL/SOURCE/ARTIFACT). 841 claims in cross-repo, 241 observable + 350 derivable = 591 anchored. |
| **EpistemicStatus** | OBSERVED |
| **Failure prevented** | Claims without verifiable source promoted to fact |

---

### SC-002: DecisionNode Classification Constraint

| Field | Value |
|-------|-------|
| **ID** | SC-002 |
| **Type** | Schema constraint |
| **Origin** | SPRINT 60C, `scripts/classify_decisions.py` |
| **Evidence** | classification = "observable" if confidence >= 0.9 else "derivable". The "inferred" classification is never assigned. `inferred_claims: 0` in all analyzed repos. |
| **EpistemicStatus** | OBSERVED |
| **Failure prevented** | Inferred decisions without observable evidence treated as valid |

---

### SC-003: Trajectory DAG Constraint

| Field | Value |
|-------|-------|
| **ID** | SC-003 |
| **Type** | Schema constraint |
| **Origin** | SPRINT 60C, `schemas/decision_trajectory.schema.json` |
| **Evidence** | Every Trajectory must be a chronologically ordered DAG of DecisionNodes connected by typed edges. 426 reconstructed edges (231 explicit + 195 temporary). Edge types: led_to, abandoned_for, superseded_by, chosen_over, supported_by, contradicted_by, resulted_in. |
| **EpistemicStatus** | OBSERVED |
| **Failure prevented** | Non-chronological sequences, connections without causal/documentary relationship |

---

### SC-004: Convergence Detection Constraint

| Field | Value |
|-------|-------|
| **ID** | SC-004 |
| **Type** | Schema constraint |
| **Origin** | SPRINT 60C, `python/discovery/epistemic_gap_detector.py` |
| **Evidence** | All Convergence requires >=2 independent actors, same topic, same outcome, and >=3 competing hypotheses with operational definition and falsification criteria. 4 convergences of 301 nodes (1.33%). All UNDETERMINED. |
| **EpistemicStatus** | OBSERVED |
| **Failure prevented** | "Convergences" without independent actors, without competitors, without operational definition |

---

### SC-005: Epistemic Gap Constraint

| Field | Value |
|-------|-------|
| **ID** | SC-005 |
| **Type** | Schema constraint |
| **Origin** | SPRINT 60C+, `python/discovery/epistemic_gap_detector.py` |
| **Evidence** | Every Gap must anchor to evidence_anchor observable and be classified as empirical/mathematical/causal with A/B/C/D characterization. 155 gaps detected, gap_density=0.515. |
| **EpistemicStatus** | OBSERVED |
| **Failure prevented** | Gaps without observable anchor, hypotheses disguised as gaps |

---

### SC-006: EHG Freeze Constraint

| Field | Value |
|-------|-------|
| **ID** | SC-006 |
| **Type** | Freeze |
| **Origin** | `docs/EPISTEMIC_GAP_CONCEPT.md`, `python/discovery/epistemic_gap_detector.py` |
| **Evidence** | EHG status: "FROZEN — requires audit precision >=80%". Gap -> hypothesis blocked. 0 restriction hypotheses promoted to fact. |
| **EpistemicStatus** | OBSERVED |
| **Failure prevented** | Promotion of gaps to hypotheses without empirical validation |

---

### SC-007: Architecture Freeze

| Field | Value |
|-------|-------|
| **ID** | SC-007 |
| **Type** | Freeze |
| **Origin** | `docs/ARCHITECTURE_FREEZE.md` |
| **Evidence** | "STOP adding architecture. The bottleneck of CoResearcher is no longer conceptual. It is empirical." No new schemas, no new documents, no new layers, no new graphs. |
| **EpistemicStatus** | OBSERVED |
| **Failure prevented** | Premature optimization, architecture without empirical validation |

---

### SC-008: EvidenceGraph v1.1.0 Freeze

| Field | Value |
|-------|-------|
| **ID** | SC-008 |
| **Type** | Freeze |
| **Origin** | `docs/STOP_REPORT.md` |
| **Evidence** | EvidenceGraph Spec & Ontology (v1.1.0) frozen. No new node types will be added (Claim, Artifact, Source, URL are final). No evaluation fields, scores, or intention states will be added. |
| **EpistemicStatus** | OBSERVED |
| **Failure prevented** | Ontological modification of the core without validation |

---

### SC-009: DecisionGraph v1.0.0 Freeze

| Field | Value |
|-------|-------|
| **ID** | SC-009 |
| **Type** | Freeze |
| **Origin** | `docs/STOP_REPORT.md`, `docs/ADR-DEC-001.md` |
| **Evidence** | DecisionGraph Spec & Ontology (v1.0.0) frozen. Governance relationships will not be modified. DecisionGraph will not be allowed to directly execute or store evidence. |
| **EpistemicStatus** | OBSERVED |
| **Failure prevented** | DecisionGraph converted into executing entity or evidence store |

---

### SC-010: MissionGraph v1.0.0 Freeze

| Field | Value |
|-------|-------|
| **ID** | SC-010 |
| **Type** | Freeze |
| **Origin** | `docs/STOP_REPORT.md`, `docs/ADR-EXE-001.md` |
| **Evidence** | MissionGraph Spec & Ontology (v1.0.0) frozen. Triada Mission -> Brief -> Execution fixed. No sub-types of missions or alternative delivery contracts will be created. |
| **EpistemicStatus** | OBSERVED |
| **Failure prevented** | Proliferation of non-validated mission types and contracts |

---

### SC-011: CoResearcher Boundary — No Manuscripts

| Field | Value |
|-------|-------|
| **ID** | SC-011 |
| **Type** | Boundary |
| **Origin** | `docs/BOUNDARY_WITH_EDITXT.md` |
| **Evidence** | CoResearcher does not review manuscripts. It does not generate editorial recommendations. Does not assign severity. Respond exclusively to EvidenceRequests. |
| **EpistemicStatus** | OBSERVED |
| **Failure prevented** | CoResearcher converted into editorial system or correction evaluator |

---

### SC-012: CoResearcher Boundary — No AI Scientist

| Field | Value |
|-------|-------|
| **ID** | SC-012 |
| **Type** | Boundary |
| **Origin** | `docs/ARCHITECTURE_MAP.md`, `docs/BOUNDARY_WITH_AI_SCIENTISTS.md` |
| **Evidence** | CoResearcher is not an AI Scientist: it does not generate hypotheses, experiments, or discoveries. Not a peer review system. Not an editorial assistant. Not a LIMS/ELN. Not a chatbot. Not a paper manager. |
| **EpistemicStatus** | OBSERVED |
| **Failure prevented** | CoResearcher turned into a science generator or conversational assistant |

---

### SC-013: CoResearcher Boundary — No Evaluative Output from EditXT

| Field | Value |
|-------|-------|
| **ID** | SC-013 |
| **Type** | Boundary |
| **Origin** | `docs/BOUNDARY_WITH_EDITXT.md` |
| **Evidence** | EditXT and CoResearcher coexist as separate applications. They never mix. EditXT consumes EvidenceGraphs as input, but CoResearcher never receives editorial or evaluative output from EditXT. |
| **EpistemicStatus** | OBSERVED |
| **Failure prevented** | Cross-evaluative contamination between layers |

---

### SC-014: MAXIM-001 — Observation vs Explanation Survival

| Field | Value |
|-------|-------|
| **ID** | SC-014 |
| **Type** | Operational maxim |
| **Origin** | SPRINT 70, `artifacts/sprint70_survival_table.json` |
| **Evidence** | 6/6 OBSERVED+DERIVED claims survived (100%); 0/9 HYPOTHESIZED claims survived (0%). SPRINT 67B adversarial OED: OED holds under HIGH complexity; HYPOTHESIZED collapses under LOW complexity. |
| **EpistemicStatus** | OBSERVED |
| **Failure prevented** | Promotion of claims based on explanation without falsification |

---

### SC-015: MAXIM-002 — Empirical Bottleneck

| Field | Value |
|-------|-------|
| **ID** | SC-015 |
| **Type** | Operational maxim |
| **Origin** | `docs/ARCHITECTURE_FREEZE.md`, SPRINT 60C, SPRINT 61-67A |
| **Evidence** | "The bottleneck of CoResearcher is no longer conceptual. It is empirical." H6 validation required 20+ real repositories. Multiple architectural hypotheses falsified; observation-first claims survived. |
| **EpistemicStatus** | OBSERVED |
| **Failure prevented** | Adding architecture without empirical validation |

---

### SC-016: MAXIM-003 — Prediction Before Architecture

| Field | Value |
|-------|-------|
| **ID** | SC-016 |
| **Type** | Operational maxim |
| **Origin** | SPRINT 61 (H7 falsification), SPRINT 66B/66C (Instrumentability Index falsification), AUDIT-AG-005 (Context Bottleneck YELLOW) |
| **Evidence** | H7 seemed obvious; falsified (FPR=70%, kappa=-0.030). Instrumentability Index seemed obvious; falsified (collapses 6 entities to 0.60). Context Bottleneck seemed obvious; UNDETERMINED (non-predictive test). |
| **EpistemicStatus** | DERIVED |
| **Failure prevented** | Premature construction of infrastructure without observable prediction |

---

### SC-017: EpistemicStatus Classification System

| Field | Value |
|-------|-------|
| **ID** | SC-017 |
| **Type** | Operational invariant |
| **Origin** | SPRINT 64R |
| **Evidence** | EpistemicStatus used consistently in subsequent audits (SPRINT 61, 64R, 67A, 67B). Enum: OBSERVED/DERIVED/HYPOTHESIZED/FALSIFIED/UNDETERMINED. |
| **EpistemicStatus** | DERIVED |
| **Failure prevented** | Epistemic ambiguity in claims classification |

---

### SC-018: Constitutional Principles Freeze

| Field | Value |
|-------|-------|
| **ID** | SC-018 |
| **Type** | Freeze |
| **Origin** | `docs/ARCHITECTURE_FREEZE.md` |
| **Evidence** | Constitutional Principles frozen: Observable, Derivable, Inferred (restricted), Unknown. |
| **EpistemicStatus** | OBSERVED |
| **Failure prevented** | Modification of constitutional principles without formal review |

---

### SC-019: AUDIT-AG-004/005 Freeze — No Context Engine

| Field | Value |
|-------|-------|
| **ID** | SC-019 |
| **Type** | Freeze |
| **Origin** | AUDIT-AG-004, AUDIT-AG-005 |
| **Evidence** | AUDIT-AG-004: FROZEN. AUDIT-AG-005: FROZEN, verdict YELLOW. No Context Engine, Context Graph, Memory Layer, or Knowledge Layer shall be built based on the hypothesis that context fragmentation causes deficient behavior. The causal link is UNDETERMINED. |
| **EpistemicStatus** | OBSERVED |
| **Failure prevented** | Construction of context infrastructure without causal evidence |

---

### SC-020: ARCH-001 — EditXT External Dependency Candidate

| Field | Value |
|-------|-------|
| **ID** | SC-020 |
| **Type** | Boundary |
| **Origin** | `docs/ARCH-001_EditXT_Potential_Runtime_Note.md` |
| **Evidence** | EditXT is external dependency candidate. No API, no contract, no operational flow, no real use case. No action required. Trigger for reevaluation: real integration requirement appears. |
| **EpistemicStatus** | OBSERVED |
| **Failure prevented** | Premature construction of EditXT integration without empirical requirement |

---

## 3. Population Reconstruction (Survivorship Bias Audit)

### 3.1 Motivation

Section 2 lists 20 surviving and 7 falsified constraints. But that doesn't tell us anything about survival rates without knowing the total population.

Risk: If we only count survivors, we may be observing survivorship bias disguised as discovery.

### 3.2 Distinction: Tested vs Declared

The 20 restrictions in section 2 are NOT equivalent:

| Category | Definition | Attempted falsification? |
|-----------|-----------|---------------------|
| **Tested** | Claims subjected to empirical falsification | Yes — they survived or died |
| **Declared** | Freezes, boundaries, declared bans | No — they survive by default, not by test |

Only the **tested** restrictions allow us to calculate real survival rates.

### 3.3 Complete population of tested restrictions

Source: `artifacts/sprint70_survival_table.json` (SPRINT 70 PHASE 2)

| ID | Entity | Claim | EpistemicStatus | Type | Result |
|----|--------|-------|-----------------|------|-----------|
| T-01 | DecisionNode | fully researchable | OBSERVED | Delimiting | SURVIVED |
| T-02 | Trajectory | inferable from DecisionNodes | OBSERVED | Delimiting | SURVIVED |
| T-03 | Trajectory | replicable (kappa >= 0.8) | DERIVED | Delimiting | SURVIVED |
| T-04 | Convergence | detectable | OBSERVED | Delimiting | SURVIVED |
| T-05 | Gap | detectable | OBSERVED | Delimiting | SURVIVED |
| T-06 | EpistemicStatus | operational classification | DERIVED | Delimiting | SURVIVED |
| T-07 | Theory | instrumentable by predictions | DERIVED | Delimiting | SURVIVED |
| T-08 | H7 | constraint detector v1 valid | HYPOTHESIZED | Explanatory | FALSIFIED |
| T-09 | Convergence | replicable (kappa >= 0.4) | HYPOTHESIZED | Explanatory | FALSIFIED |
| T-10 | Convergence | real vs synthetic distinguishable | HYPOTHESIZED | Explanatory | FALSIFIED |
| T-11 | Restriction | instrumentable by manipulation | HYPOTHESIZED | Explanatory | FALSIFIED |
| T-12 | Paradigm | instrumentable by shared assumptions | HYPOTHESIZED | Explanatory | FALSIFIED |
| T-13 | Instrumentability Index | calibrated | HYPOTHESIZED | Explanatory | FALSIFIED |
| T-14 | Instrumentability Index | useful metric | HYPOTHESIZED | Explanatory | FALSIFIED |

### 3.4 Survival rates by type

| Type | Population | Survivors | Counterfeit | Survival rate |
|------|-----------|-------------|--------------|---------------------|
| Delimiting | 7 | 7 | 0 | 100% |
| Explanatory | 7 | 0 | 7 | 0% |
| **Total tested** | **14** | **7** | **7** | **50%** |

### 3.5 Limitations of this reconstruction

1. **Small population**: 14 entities tested. Not sufficient for robust statistical inference.
2. **Possible selection bias**: the delimiting restrictions may not have been subjected to falsification with the same intensity as the explanatory ones.
3. **Declared untested restrictions**: The 20 restrictions in section 2 include freezes and boundaries that were never formally falsified. They survive by declaration, not by proof.
4. **Single scope**: all observations come from a single project (CoResearcher). There is no external replication.

### 3.6 Language correction

The phrase "explanations die" is too strong for the current state of evidence.

What is actually observed is:

```text
Las explicaciones construidas dentro de CoResearcher
han mostrado una tasa de supervivencia inferior
a las restricciones observacionales.
```

That's close to the data. The other is a generalization.

---

## 4. Falsified Restrictions (for contrast)

These restrictions did NOT survive. They are listed here to contrast with the survivors.

| ID | Restriction | EpistemicStatus | Result |
|----|-------------|-----------------|-----------|
| F-001 | H7 — Constraint detector v1 valid | HYPOTHESIZED | FALSIFIED (FPR=70%, kappa=-0.030) |
| F-002 | Replicable convergence (kappa >= 0.4) | HYPOTHESIZED | FALSIFIED (kappa=-0.094) |
| F-003 | Real convergence vs distinguishable synthetic | HYPOTHESIZED | FALSIFIED (70% synthetic FPR) |
| F-004 | Restriction implementable by manipulation | HYPOTHESIZED | FALSIFIED (no published metrics) |
| F-005 | Paradigm instrumentable by shared assumptions | HYPOTHESIZED | FALSIFIED (no metric, index=0.40) |
| F-006 | Calibrated Instrumentability Index | HYPOTHESIZED | FALSIFIED (9 attacks, collapses to 0.60) |
| F-007 | Instrumentability Index as a useful metric | HYPOTHESIZED | FALSIFIED (does not separate groups, does not predict) |

---

## 5. Structural Observation

### 5.1 Who survives

The surviving constraints share a common structure:

```text
No hagas X sin Y
```

where Y is an observable or empirical condition.

Examples:
- No claims promotions without evidence_anchor (SC-001)
- Do not classify decisions as inferred (SC-002)
- Do not add architecture without empirical validation (SC-007)
- Don't build Context Engine without observable prediction (SC-019)
- Do not integrate EditXT without real requirement (SC-020)

### 5.2 Who dies

Forged constraints share another structure:

```text
X es instrumentable por Y
```

where Y is a conceptual explanation without direct measurement.

Examples:
- Restriction implementable by manipulation (F-004)
- Paradigm instrumentable by shared assumptions (F-005)
- Instrumentability Index as a useful metric (F-007)

### 5.3 Emerging pattern

```text
Las restricciones que delimitan (que NO hacer)
han mostrado mayor tasa de supervivencia.

Las restricciones que explican (como funciona algo)
han mostrado tasa de supervivencia inferior.
```

We do not claim that it is a law. It is a recurring observation on a small population (14 entities tested). See section 3 for limitations.

---

## 6. Quantitative Summary

### 6.1 Three category partition

The phrase "19 surviving constraints" is potentially misleading. The correct partition is:

| Category | Total | Definition |
|-----------|-------|------------|
| SURVIVED_TESTING | 7 | Subjected to empirical falsification and survived (T-01 to T-07) |
| DECLARED_AND_NOT_TESTED | 12 | Freezes, boundaries, prohibitions declared but never formally falsified |
| FALSIFIED | 7 | Subjected to empirical falsification and did not survive (F-001 to F-007) |
| **Total** | **26** | |

### 6.2 Tested restrictions (attempted falsification)

| Type | Population | Survivors | Counterfeit | Survival rate |
|------|-----------|-------------|--------------|---------------------|
| Delimiting | 7 | 7 | 0 | 100% |
| Explanatory | 7 | 0 | 7 | 0% |
| **Total tested** | **14** | **7** | **7** | **50%** |

### 6.3 Declared restrictions (no attempted falsification)

| ID | Restriction | Note |
|----|-------------|------|
| SC-006 | EHG Freeze | Survive by declaration |
| SC-007 | Architecture Freeze | Survive by declaration |
| SC-008 | EvidenceGraph v1.1.0 Freeze | Survive by declaration |
| SC-009 | DecisionGraph v1.0.0 Freeze | Survive by declaration |
| SC-010 | MissionGraph v1.0.0 Freeze | Survive by declaration |
| SC-011 | No Manuscripts boundary | Survive by declaration |
| SC-012 | No AI Scientist boundary | Survive by declaration |
| SC-013 | No EditXT evaluative output | Survive by declaration |
| SC-016 | MAXIM-003 (DERIVED) | Not directly tested |
| SC-018 | Constitutional Principles Freeze | Survive by declaration |
| SC-019 | AUDIT-AG-004/005 Freeze | Survive by declaration |
| SC-020 | ARCH-001 EditXT boundary | Survive by declaration |
| **Total** | **12** | Not formally tested |

---

## 7. Open Observation

### 7.1 Common operational structure in survivors

The tested survivors seem to share a common operational structure:

```text
PROHIBITION + OBSERVABLE PRECONDITION
```

Examples:

- Do not create convergences without >=2 observable actors
- Do not create restrictions without competing hypotheses
- Do not build architecture without observable prediction
- Do not create evidence without observable anchor
- Do not promote gaps to hypotheses without audit >=80%

While counterfeit ones usually have this shape:

```text
X existe porque Y.
X es medible porque Y.
X funciona mediante Y.
```

where Y is an explanation not yet observed.

### 7.2 Status

```text
CANDIDATE
```

This observation has not been subjected to falsification. Remains CANDIDATE.

Not promoted to max.
It does not become law.
No infrastructure is built on it.

It just registers.

---

## 8. Epistemic Note

This inventory does not create new entities, hypotheses, or architecture. It only classifies what already exists.

The observation that explanations built within CoResearcher have shown a lower survival rate than observational constraints is not promoted into law. It is recorded as a pattern observed on a small population (14 entities tested). If someone wants to make an observable prediction and falsify it, that would be legitimate. Building a theory on this pattern without falsification would be to violate MAXIM-003.

---

## 9. Audit Recursion Discipline

### 9.1 Risk

A potential pattern begins to appear:

```text
observacion
→ auditoria

auditoria
→ auditoria de la auditoria

auditoria de la auditoria
→ auditoria de la auditoria de la auditoria
```

So far it's been useful because each level found real bugs:

```text
SPRINT 66 → AUDIT 66
AUDIT-AG-004 → AUDIT-AG-005
AUDIT-AG-006 → survivorship audit
```

But there is a point where the audit stops producing new observations and begins to produce only linguistic refinements.

### 9.2 Future discipline

New audit allowed only if:

1. There is a new observable prediction
2. Or there is an unexplored risk of falsification
3. Or there is a new observational population

Do not open audits just because an audit exists.

---

## 10. Final Classification

| Field | Value |
|-------|-------|
| **Purpose** | Cartography |
| **Status** | Mature |
| **Evidence** | Adequate |
| **Action Required** | None |
| **Follow-up** | Only if new tested entities appear |

---

## 11. Generated Artifacts

| Artifact | Type |
|-----------|------|
| `docs/AUDIT_AG_006_SURVIVING_CONSTRAINTS.md` | Inventory document |

---

*Inventory completed. No new hypotheses. No new entities. Without architecture. Only cartography. AUDIT-AG-006 closed.*