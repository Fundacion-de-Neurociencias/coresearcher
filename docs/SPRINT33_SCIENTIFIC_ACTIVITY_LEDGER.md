# Sprint 33: Scientific Activity Ledger
## Reconstruct Verifiable Scientific History

---

## Strategic Context

Sprints 27–32 demonstrated:

- Artifact resolution works.
- Workstream inference works.
- Cross-repository program/initiative resolution does **not** work with current heuristics.

Key negative results:
- Artifact similarity ≠ program membership
- Contributor networks ≠ program membership

Therefore, the architecture should stop trying to infer administrative/organizational structures.

Instead, CoResearcher should focus on what it can actually reconstruct:

```text
Evidence
    ↓
Artifact
    ↓
Workstream
    ↓
Scientific Activity Ledger
```

---

## What Is a Scientific Activity Ledger?

A verifiable, navigable reconstruction of a scientific project's history.

It answers:

- What artifacts exist?
- Who contributed?
- What workstreams are visible?
- What happened first, what happened later?
- How do artifacts relate?

It does **not** claim:
- What the "program" is
- What the "governance" structure is
- What the mission is

Those are inference beyond evidence.

---

## Success Criterion

Can a newcomer understand a scientific project in 20 minutes by reading the Ledger?

Metric:
> ¿Cuánto tiempo de comprensión eliminamos?

Not:
> How many programs did we infer?

---

## Ledger Schema (Minimal)

```json
{
  "ledger_id": "mne-python",
  "name": "MNE-Python",
  "description": "Python package for MEG/EEG analysis",
  "timeline": {
    "start_year": 2012,
    "latest_activity": "2026-07-17",
    "milestones": ["v0.3", "v0.15", "v1.0"]
  },
  "artifacts": [
    {
      "artifact_id": "github:mne-tools/mne-python:latest",
      "type": "software_release",
      "title": "MNE-Python",
      "doi": null,
      "created_at": "2026-07-17",
      "evidence_sources": ["github"]
    }
  ],
  "workstreams": [
    {
      "workstream_id": "workstream:eeg",
      "name": "EEG",
      "signals": ["eeg", "epochs", "ica"],
      "related_artifact_count": 12,
      "contributor_count": 5
    }
  ],
  "contributors": [
    {
      "name": "Denis Engemann",
      "github": "dengemann",
      "contributions": 3
    }
  ],
  "comprehension_summary": "MNE-Python is an open-source Python package for MEG/EEG analysis...",
  "generated_at": "2026-07-17T..."
}
```

---

## Sprint 33 Objective

Build a **Scientific Activity Ledger** generator that produces a navigable, verifiable Ledger from Evidence → Artifacts → Workstreams.

Success criterion:
1. Ledger includes all canonical artifacts from GitHub, Zenodo, OpenAlex, Crossref.
2. Ledger includes inferred workstreams with signal evidence.
3. Ledger includes contributor list with GitHub/ORCID when available.
4. Ledger includes timeline from artifact dates and release dates.
5. A human can read the Ledger and understand the project in 20 minutes.

---

## What Sprint 33 Does NOT Do

- No new connectors
- No new artifact types
- No program/initiative inference
- No organizational inference
- No governance inference
- No manual labeling

---

## What Sprint 33 DOES Do

1. Define `ScientificLedger` schema.
2. Build `LedgerGenerator` that:
   - takes a list of ScientificArtifact objects,
   - runs workstream inference,
   - deduplicates contributors,
   - builds timeline,
   - generates comprehension summary,
   - outputs navigable Markdown/JSON Ledger.
3. Validate Ledger on:
   - MNE-Python
   - BIDS ecosystem

Validation method:
- Human review of generated Ledger.
- Time-to-comprehension estimate.
- Completeness check: are all major artifact types present?

---

## Deliverables

1. `python/observer/scientific_ledger.py` — Ledger schema
2. `python/observer/ledger_generator.py` — Ledger generation logic
3. `python/observer/validate_sprint33.py` — Validation script
4. `artifacts/sprint33_scientific_ledger_validation.md` — Validation report

No new connectors.
No redesign of existing pipeline.
Evidence-first.
Comprehension-first.