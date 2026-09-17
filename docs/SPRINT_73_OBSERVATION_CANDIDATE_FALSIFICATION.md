# SPRINT 73 (REVISED) — Observation-Candidate Falsification

**Sprint**: SPRINT 73 (REVISED) — Observation-Candidate Falsification
**Fecha**: 2026-08-03
**Status**: COMPLETADO
**Veredicto**: YELLOW — Observation-candidate UNDETERMINED (revised from initial RED)

---

## Contexto

An observation-candidate was submitted:

```text
Systems that operate in regulated or scientific domains
appear to be moving from:
    model-centric architectures
toward:
    constraint + skill + execution trace architectures

Evidence:
- ClawBio
- COrigami
- Existing CoResearcher traceability engine

Status: CANDIDATE
Predictive power: NONE
Falsification: NOT ATTEMPTED
```

This sprint attempts to DESTROY the observation-candidate. Not improve. Not build. Only falsify.

---

## Revision History

### Initial version (RED — FALSIFIED)

The initial version produced a RED (FALSIFIED) verdict based on:
1. ClawBio classified as UNANCHORED (0 references in CoResearcher codebase)
2. "skill" classified as ABSENT (not found in COrigami or CoResearcher docs)

### Revised version (YELLOW — UNDETERMINED)

The initial RED verdict was challenged. Re-examination found two errors:

**FASE 1 ERROR**: ClawBio was classified as UNANCHORED because it was not found in the CoResearcher codebase. This was an error: ClawBio is an **external system**. GitHub search (`gh search repos ClawBio`) confirmed it exists as a real organization (github.com/ClawBio) with 18 repositories. The main repo description: *"The first bioinformatics-native AI agent skill library. Local-first. Reproducible. Open. Free."* Reclassified from UNANCHORED to **INFERRED** (exists externally, verifiable via GitHub, but no specific evidence anchor provided in the observation-candidate).

**FASE 2 ERROR**: "skill" was classified as ABSENT because it was not found in COrigami or CoResearcher docs. This was an error:
- (a) ClawBio is literally described as an **"AI agent skill library"**
- (b) GeneForge (`agents/gene-forge-tmp/`) has **"Bio-Skills clínicas"** (PharmGx, NutriGx, Geriatric Risk) in ADR-001 line 78

Reclassified from ABSENT to **PRESENT**.

Both errors were due to searching only the CoResearcher codebase, missing external systems and the GeneForge ecosystem.

---

## Metodología

5-phase falsification following the pattern established in `scripts/sprint72_audit_ag005_falsification.py`:

1. **Evidence Anchor Verification** — check each cited source for traceability (SC-001)
2. **Component Verification** — does "constraint + skill + execution trace" match?
3. **Trend Verification** — is there evidence of "moving from... toward..."?
4. **Alternative Explanations** — competing hypotheses
5. **Predictive Test** — can an observable prediction be formulated?

Special rule: No new architecture, no new entities, no new hypotheses. Only falsification.

---

## FASE 1 (REVISED) — Evidence Anchor Verification

| Source | Classification | Evidence Anchor | Status |
|--------|---------------|-----------------|--------|
| ClawBio | INFERRED | GitHub: github.com/ClawBio (18 repos) | Exists externally. Described as "AI agent skill library". Citation incomplete (no URL/DOI in observation-candidate). |
| COrigami | ANCHORED_SINGLE_INSTANCE | `docs/CORIGAMI_DISCOVERY_PATTERN.md` | Documented in SPRINT 70. Zahavy et al., 2024. |
| CoResearcher traceability engine | ANCHORED | `docs/TRACEABILITY_API.md`, `docs/HANDOFF_TRACEABILITY.md` | 426 edges, 301 nodes, 155 gaps. |
| GeneForge (BONUS) | ANCHORED_BONUS | `agents/gene-forge-tmp/docs/decisions/ADR-001` | Discovered during re-examination. Has Bio-Skills clínicas + evidence_registry.py. |

**Summary (revised)**: 3/4 anchored, 1/4 inferred, 0/4 unanchored.

**Critical finding**: ClawBio is INFERRED — it exists externally (GitHub org, 18 repos, described as "AI agent skill library") but the observation-candidate does not provide a specific evidence anchor. Per .clinerules, inferred claims must be explicitly marked. The observation-candidate does not mark ClawBio as inferred.

---

## FASE 2 (REVISED) — Component Verification

| Component | COrigami | CoResearcher | ClawBio | GeneForge | Verdict |
|-----------|----------|-------------|---------|-----------|---------|
| constraint | YES — Packing Constraints | YES — SC-001 to SC-020 | INFERRED — "Reproducible" + audit suite | YES — evidence_registry.py | PRESENT |
| skill | NO — uses "foldability solver" | NO — uses "traceability engine" | **YES — "AI agent skill library"** | **YES — "Bio-Skills clínicas"** | **PRESENT** |
| execution trace | PARTIAL — "folded objects" | YES — "Immutable execution trace tracking" | INFERRED — "Reproducible" + audit | YES — evidence_adapters/ | PRESENT |

**Summary (revised)**: 3/3 present, 0/3 absent.

**Critical finding**: All 3 components are present. "skill" is present in ClawBio (described as "AI agent skill library") and GeneForge (Bio-Skills clínicas: PharmGx, NutriGx, Geriatric Risk). The terminology mismatch identified in the initial version was due to incomplete search scope.

---

## FASE 3 — Trend Verification (unchanged)

| Check | Verdict | Detail |
|-------|---------|--------|
| N sufficient for trend claim | INSUFFICIENT | N=3 cited (2 anchored, 1 inferred) + 1 bonus. All match components. N=4 insufficient for broad trend. |
| Temporal data showing transition | NO_TEMPORAL_DATA | No system shown to transition from model-centric to constraint-based |
| "model-centric" defined | UNDEFINED_TERM | "model-centric" is used but never defined |
| "regulated or scientific domains" verified | PRESENT | 3/3 cited + 1 bonus in scientific domains |

**Critical finding**: The "to" state (constraint + skill + execution trace) is well-supported. The "from" state (model-centric) remains UNDEFINED with NO temporal data showing any transition. The observation describes a destination but not a journey.

---

## FASE 4 — Alternative Explanations (revised)

| ID | Name | Strength | Detail |
|----|------|----------|--------|
| A | Constraint-first architecture (not a trend) | STRONG | No evidence any system was previously model-centric. All designed with constraints from start. |
| B | Domain-specific requirement (not a trend) | STRONG | Scientific reproducibility requires constraints. This is a prerequisite, not a trend. |
| C | Selection bias | MODERATE (weakened) | ClawBio is independent, reducing bias. But N=1 independent system is small. |
| D | Terminology drift | WEAK (largely refuted) | "skill" IS present in ClawBio and GeneForge. Terminology matches evidence. |
| E | Original observation-candidate | MODERATE (strengthened) | All components present, all in scientific domains. But no temporal data, "model-centric" undefined. |

---

## FASE 5 — Predictive Test (unchanged)

| ID | Prediction | Status |
|----|------------|--------|
| P1 | New scientific/regulated domain systems should adopt constraint + execution trace architectures | NOT_TESTED |
| P2 | Systems that previously used model-centric should show transitioning | NOT_TESTED |
| P3 | If false (selection bias), random sample of N>=10 should show NO preference | NOT_TESTED |

**Overall status**: UNDETERMINED — 0/3 predictions tested.

---

## Veredicto: YELLOW — UNDETERMINED (revised from RED)

The observation-candidate is **NOT FALSIFIED** but remains **UNDETERMINED**.

**Revision**: Initial RED → Revised YELLOW

**Reasons for revision**:
1. ClawBio EXISTS externally (GitHub org, 18 repos, described as "AI agent skill library") — reclassified from UNANCHORED to INFERRED
2. "skill" IS present in ClawBio (skill library) and GeneForge (Bio-Skills clínicas) — reclassified from ABSENT to PRESENT

**Remaining issues** (why YELLOW, not GREEN):
1. No temporal data supports "moving from... toward..." — no system shown to have been previously "model-centric"
2. "model-centric" is UNDEFINED
3. N=4 is insufficient for a broad trend claim
4. 0/3 predictions tested

**Evidence for** (3 signals):
1. All 3 components (constraint, skill, execution trace) are present in cited systems
2. All cited systems are in scientific domains
3. ClawBio is a real, verifiable system described as "skill library"

**Evidence against** (4 signals):
1. ClawBio citation is INFERRED (not fully anchored) — WEAK
2. No temporal data — STRONG
3. "model-centric" is UNDEFINED — STRONG
4. 0/3 predictions tested — MODERATE

**Rationale**: The "to" state (constraint + skill + execution trace) is well-supported. The "from" state (model-centric) and the "moving" claim are not. The observation-candidate remains CANDIDATE, not established.

---

## Connection to MAXIM-001

The observation-candidate is **partially explanation-first**: the "to" state is observation-grounded, but the "from" state and "moving" claim are explanation-first (no temporal data). Per MAXIM-001, the observation-grounded parts survive; the explanation-grounded parts remain untested.

---

## Connection to MAXIM-003

Per MAXIM-003: "When a hypothesis appears obvious, do not build the architecture. Define first an observable prediction." The observation admits "Predictive power: NONE". Three predictions can be formulated but none tested. Without a tested prediction, the observation remains UNDETERMINED.

---

## Freeze compliance

- ✅ No new schemas created
- ✅ No new graphs created
- ✅ No new layers introduced
- ✅ EHG not modified (congelado)
- ✅ No new entities created
- ✅ No new hypotheses proposed (only competing explanations for falsification)
- ✅ Analysis read-only over existing artifacts + external GitHub search
- ✅ Produces real data artifacts (JSON)

---

## Artifacts produced

| Artifact | Sprint | Content |
|----------|--------|---------|
| `scripts/sprint73_observation_candidate_falsification.py` | SPRINT 73 (REVISED) | Falsification script: 5-phase audit with revision history |
| `artifacts/sprint73_observation_candidate_falsification.json` | SPRINT 73 (REVISED) | Falsification results with evidence anchors, revision history, YELLOW verdict |
| `docs/SPRINT_73_OBSERVATION_CANDIDATE_FALSIFICATION.md` | SPRINT 73 (REVISED) | This document: revised falsification report |

---

## Referencias (evidencia anclada)

| Fuente | Tipo | Uso en este sprint |
|--------|------|---------------------|
| `docs/CORIGAMI_DISCOVERY_PATTERN.md` | Doc | FASE 1: COrigami evidence anchor. FASE 2: component verification |
| `docs/AUDIT_AG_006_SURVIVING_CONSTRAINTS.md` | Doc | FASE 2: SC-001 to SC-020 surviving constraints |
| `docs/OPERATIONAL_MAXIMS.md` | Doc | FASE 4: MAXIM-001, MAXIM-003 connection |
| `docs/OBSERVATORY_POSITION.md` | Doc | FASE 4: domain-specific requirement hypothesis |
| `docs/SHARED_SERVICES.md` | Doc | FASE 2: execution trace evidence |
| `docs/ARCHITECTURE_MAP.md` | Doc | FASE 2: execution trace evidence |
| `agents/gene-forge-tmp/docs/decisions/ADR-001-arquitectura-gfl-geneforge.md` | Doc | FASE 2: Bio-Skills clínicas (PharmGx, NutriGx, Geriatric Risk) |
| `agents/gene-forge-tmp/evidence_registry.py` | Code | FASE 2: constraint mechanism in GeneForge |
| `artifacts/sprint70_survival_table.json` | Dato | FASE 1: COrigami mapping, survival rates |
| `artifacts/observation_explanation_differential.json` | Dato | FASE 4: MAXIM-001 connection |
| `scripts/sprint72_audit_ag005_falsification.py` | Código | Methodology pattern for 5-phase falsification |
| GitHub: `ClawBio/ClawBio` | External | FASE 1: ClawBio verification — "AI agent skill library" |
| GitHub: `biostochastics/clawbio_bench` | External | FASE 2: third-party audit suite for ClawBio |

---

## Estado final del observation-candidate

```text
Status: CANDIDATE (UNDETERMINED)
Predictive power: NONE (0/3 predictions tested)
Falsification: ATTEMPTED — YELLOW verdict
Verdict: The observation-candidate is NOT falsified but NOT established.
         The 'to' state is well-supported. The 'from' state and 'moving' claim are not.
```

The observation-candidate is not promoted. It is not converted to an observation. It is not added to the surviving constraints inventory (AUDIT-AG-006). It remains CANDIDATE with status UNDETERMINED.

---

> **Veredicto (revised)**: YELLOW — UNDETERMINED. Initial RED verdict was revised after discovering that (1) ClawBio exists externally on GitHub as an "AI agent skill library" and (2) "skill" is present in ClawBio and GeneForge (Bio-Skills clínicas). The "to" state (constraint + skill + execution trace) is well-supported across all cited systems. The "from" state (model-centric) and the "moving" claim remain unsupported — no temporal data, "model-centric" undefined, N=4 insufficient for trend, 0/3 predictions tested. The observation-candidate remains CANDIDATE.