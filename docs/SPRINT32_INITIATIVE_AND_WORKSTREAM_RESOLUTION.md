# Sprint 32: Initiative and Workstream Resolution
## Precise Terminology for Scientific Activity Reconstruction

---

## Why This Document Exists

Sprint 31 feedback identified a critical semantic ambiguity:

> "Program" can mean:
> - a scientific research program (ADNI, Human Cell Atlas)
> - a software program/package (MNE-Python)
> - an initiative/ecosystem (Neurodiagnoses, GeneForge, BIDS)

The current `Program` concept conflates these meanings.

This document proposes a cleaner hierarchy and replaces "Program Resolver" with **Initiative and Workstream Resolution**.

---

## Proposed Hierarchy

```text
Evidence
    ↓
Artifact
    ↓
Workstream
    ↓
Initiative / Ecosystem
```

### Workstream

Definition: A coherent line of scientific activity with a recognizable objective.

Examples:
- "EEG preprocessing in MNE"
- "APOE4 mechanism exploration"
- "Plasma biomarkers for Alzheimer's disease"
- "CRISPR guide optimization in GeneForge"

Properties:
- Observable through artifacts, commits, issues, papers
- May span multiple repositories
- May span multiple organizations
- Has a temporal dimension
- Is the primary unit scientists recognize as "what I am working on"

### Initiative / Ecosystem

Definition: A larger enterprise that contains multiple workstreams, often with:
- explicit mission/governance,
- named identity,
- funding,
- community.

Examples:
- Human Cell Atlas
- ADNI
- BIDS ecosystem
- OpenNeuro
- Allen Institute
- Neurodiagnoses
- GeneForge

Properties:
- Contains multiple workstreams
- Spans multiple repositories, datasets, papers
- Has public identity/mission/governance
- Longer-lived than individual workstreams

---

## What Changes

Terminology:
- `Program` → `Initiative`
- `Program Resolver` → `Initiative Resolver`
- Add `Workstream` as first-class object, not just a list of keywords

Architecture:
```text
Evidence Sources
    ↓
Artifacts
    ↓
Workstream Resolver
    ↓
Initiative Resolver
    ↓
Scientific Activity Ledger
```

Behavior:
- Workstreams are inferred from artifact clusters with shared signals.
- Initiatives are inferred from network-level structures: shared governance, shared standards, shared funding, shared community identity.

---

## What Remains

- Existing connectors unchanged.
- Existing artifact resolution unchanged.
- Existing network extraction unchanged.
- Only the grouping/abstraction layer changes.

---

## Sprint 32 Objective

Refactor Program Resolver into Workstream + Initiative Resolvers.

Success criterion:
Can CoResearcher produce:
1. A list of workstreams for a repository/ecosystem?
2. A list of initiatives those workstreams belong to?
3. A comprehension summary that uses this hierarchy?

Validation target:
- MNE-Python (workstreams expected: EEG, MEG, source localization, BIDS I/O)
- BIDS ecosystem (initiative expected: BIDS)

---

## Deliverables

1. `python/observer/workstream.py` — Workstream schema
2. `python/observer/initiative.py` — Initiative schema
3. `python/observer/workstream_resolver.py` — Workstream inference
4. `python/observer/initiative_resolver.py` — Initiative inference from workstreams/networks
5. `python/observer/validate_sprint32.py` — Validation script
6. `artifacts/sprint32_initiative_workstream_validation.md` — Validation report

No new connectors.
No redesign of existing pipeline.
Terminology clarification first. Evidence remains primary.