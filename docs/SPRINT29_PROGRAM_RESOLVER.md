# Sprint 29: Program Resolver
## From Artifacts to Scientific Programs

---

## Strategic Context

Sprint 28 proved: CoResearcher can resolve artifact identity across GitHub, Zenodo, OpenAlex, and Crossref.

Sprint 27 proved: GitHub-only reconstruction yields development activity, not scientific activity.

Current state:
- Observer infrastructure: functional
- Artifact resolution: functional
- Scientific reconstruction: **still blocked at the program level**

The next bottleneck is **Program Resolution**:

```text
Artifacts
    ↓
Program Resolver
    ↓
Scientific Program
```

Science is not organized in papers.
Science is organized in programs.

Example:

```text
MNE-Python
├── Software releases
├── Documentation
├── Papers
├── Datasets
├── Contributors
└── Workstreams (EEG, MEG, source localization, BIDS I/O)
```

Same for:
- Allen Brain Atlas
- BIDS ecosystem
- Human Cell Atlas
- Neurodiagnoses
- GeneForge

---

## Sprint 29 Objective

Build a **Program Resolver** that takes ScientificArtifacts and outputs coherent scientific programs.

Success criterion:
Can a human expert understand the project in 20 minutes by reading the Program Resolver output?

Metric:
> ¿Cuánto tiempo de comprensión eliminamos?

Not:
> ¿Cuántos artefactos resolvimos?

---

## Input

List of ScientificArtifact objects from multiple sources.

Example: 29 artifacts for MNE-Python after Sprint 28 validation.

---

## Output

```json
{
  "program_id": "mne-python",
  "name": "MNE-Python",
  "description": "Python package for EEG/MEG analysis",
  "timeline": {
    "start_year": 2012,
    "latest_activity": "2026-07-17",
    "key_milestones": ["v0.3", "v0.15", "v1.0"]
  },
  "artifacts": {
    "software_releases": [...],
    "papers": [...],
    "datasets": [...],
    "protocols": [...]
  },
  "contributors": [...],
  "workstreams": [
    {
      "name": "MEG/EEG analysis",
      "signals": ["evoked", "time-frequency", "ica"],
      "related_artifacts": [...]
    },
    {
      "name": "Source localization",
      "signals": ["mne", "beamforming", "cortical surfaces"],
      "related_artifacts": [...]
    }
  ],
  "comprehension_summary": "MNE-Python is an open-source Python package for MEG/EEG analysis..."
}
```

---

## Scope

What Sprint 29 does NOT do:
- No new connectors
- No NLP models
- No new artifact types
- No inference beyond grouping signals

What Sprint 29 DOES do:
1. Define Program schema
2. Build ProgramResolver that groups artifacts by:
   - repository
   - DOI
   - keyword clusters in titles/notes
3. Generate comprehension summary per program
4. Validate on MNE-Python only

---

## ProgramResolver Logic

Given: N ScientificArtifact objects.

Steps:
1. Group by `github_repo` if present.
2. Within each group, subtype by `type`:
   - software_release
   - paper
   - dataset
   - other
3. Extract workstream signals from:
   - titles
   - notes
   - keywords in paper concepts / Crossref subjects / OpenAlex concepts
4. Build timeline from:
   - `created_at`
   - `updated_at`
   - GitHub release `publishedAt`
5. Deduplicate contributors across all artifacts in the program.
6. Generate `comprehension_summary` from:
   - program description
   - repo description
   - first sentence of paper titles
   - workstream names

Output:
- One Program object per distinct scientific program.
- One comprehension summary per program.

---

## Validation Target

Single repository: **MNE-Python/mne-python**

Why:
- We already have 29 canonical artifacts from Sprint 28.
- It is publicly known.
- Experts can judge whether the summary captures the project's essence.

Validation protocol:
1. Run ProgramResolver on MNE-Python artifacts.
2. Read the resulting `comprehension_summary` and `workstreams` list.
3. Ask:
   - Does this describe MNE-Python accurately?
   - Can a newcomer understand what the project does?
   - Are the main workstreams correct?
   - Is the timeline coherent?
4. Record answers as manual precision/recall for programs.

---

## Deliverables

1. `python/observer/program.py` — Program schema and serializer
2. `python/observer/program_resolver.py` — ProgramResolver logic
3. `python/observer/validate_sprint29.py` — Validation script for MNE-Python
4. `artifacts/sprint29_program_resolver_validation.md` — Validation report

No new connectors.
No redesign of existing pipeline.
Evidence-first.