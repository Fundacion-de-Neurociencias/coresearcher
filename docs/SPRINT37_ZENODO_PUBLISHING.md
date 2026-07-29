# Sprint 37: Zenodo Publishing of Scientific Activity Ledger

## Hypothesis
> A Scientific Activity Ledger is itself a scientific artifact that can be deposited in Zenodo, yielding a citable, versioned, persistent object.

**Success criterion:**
- A `ScientificLedger` can be serialized and deposited in Zenodo.
- The resulting record receives a DOI.
- The DOI resolves to the ledger metadata.
- The versioned ledger is reproducible.

---

## Context

Sprint 33 built the **Scientific Activity Ledger** as an extraction artifact. It lives in-memory and on disk, but it is not a first-class scientific object.

Zenodo is a general-purpose scientific repository that accepts datasets, software, and other research artifacts. Depositing a ledger there gives it:
- A persistent DOI
- Versioned snapshots
- Metadata discovery via Crossref/DataCite
- Academic credibility

---

## Architecture: New Flow

**Old observer pipeline:**
```
GitHub → OpenAlex → Crossref → Zenodo (read-only)
        ↓
Artifact Resolver
        ↓
Ledger Generator
        ↓
JSON on disk
```

**Sprint 37 pipeline:**
```
Artifacts
    ↓
Ledger Generator
    ↓
ScientificLedger
    ↓
ZenodoPublisher.deposit()
    ↓
Zenodo Deposit (pending)
    ↓
Zenodo Doi (10.5281/zenodo.XXXXXX)
```

The ledger is no longer just an analysis output. It is a publishable scientific object.

---

## Components

### `python/observer/zenodo_connector.py` (already exists, read-only)

Retained for reading records. Not used for publishing.

### `python/observer/zenodo_publisher.py` (NEW)

Writes a ledger to Zenodo via the REST API.

Responsibilities:
1. Accept a `ScientificLedger` and serialize it.
2. Create a Zenodo deposit with metadata.
3. Upload the ledger JSON as a file.
4. Optionally publish the deposit (making the DOI live).
5. Return deposition metadata including DOI.

Public API:
- `ZenodoPublisher(api_token: str, use_sandbox: bool = True)`
- `deposit(ledger: ScientificLedger, publish: bool = False) -> dict` → returns deposition metadata.
- `publish(deposition_id: int) -> dict` → finalizes and returns DOI.
- `publish_and_get_doi(ledger: ScientificLedger) -> str` → one-shot deposit + publish.

### `python/observer/ledger_normalizer.py` (NEW)

Converts a `ScientificLedger` into the Zenodo-compatible metadata payload.

Responsibilities:
1. Map ledger fields to Zenodo metadata fields (title, description, creators, dates, keywords).
2. Validate that required fields are present.
3. Produce deterministic JSON for repeatable deposits.

Public API:
- `normalize_for_zenodo(ledger: ScientificLedger) -> dict` → Zenodo-compatible metadata dict.

---

## Zenodo Metadata Mapping

| Zenodo field | Source in ScientificLedger |
|---|---|
| `title` | `name` |
| `description` | `description` and `comprehension_summary` |
| `creators` | `contributors` (name + orcid if available) |
| `dates` | `generated_at` (issued) and `timeline.latest_activity` |
| `keywords` | derived from `workstreams.signals` |
| `related_identifiers` | artifact DOIs, GitHub URLs |
| `notes` | ledger_id, artifact count, workstream count |

Zenodo deposit file: `ledger-{ledger_id}.json` with full `ScientificLedger.to_dict()` payload.

---

## Sequencing (Publish Modes)

### Mode A: Dry-run (Sandbox, no publish)
```python
publisher = ZenodoPublisher(api_token=token, use_sandbox=True)
meta = publisher.deposit(ledger, publish=False)
# deposition_id = meta['id']
# No DOI yet. Record is "in progress".
```

### Mode B: Publish (Sandbox or Production)
```python
publisher = ZenodoPublisher(api_token=token, use_sandbox=True)
doi = publisher.publish_and_get_doi(ledger)
# DOI is live (or reserved in sandbox).
```

### Mode C: Two-step (publish later)
```python
meta = publisher.deposit(ledger, publish=False)
# ... do other things ...
publisher.publish(meta['id'])
# DOI is live.
```

---

## Scientific Semantics: The Unit Problem

Publishing to Zenodo is solved. The harder question is:

> ¿Qué representa científicamente un Scientific Activity Ledger?

Options:

1. **1 proyecto = 1 ledger**
   - Pro: Stable identifier for the whole project.
   - Con: Projects are fuzzy boundaries.

2. **1 investigación = 1 ledger**
   - Pro: Tighter scope; closer to a paper's unit of knowledge.
   - Con: Requires explicit "investigation" boundaries that may not exist in code.

3. **1 experimento = 1 ledger**
   - Pro: Maximum reproducibility.
   - Con: Explosion of ledgers; versioning nightmare.

**Working hypothesis for now:**
> A Scientific Activity Ledger represents **one investigatable claim or question** within a project.
>
> It is the unit that a human or agent would need to evaluate, reproduce, or extend.

This is intentionally looser than "paper" and tighter than "repo". It maps to:
- A workstream + its evidence + its artifact set + its contributors.
- The minimal traceable unit of scientific activity.

**This is the semantic layer that determines whether the ledger gets cited or ignored.**

---

## What Sprint 37 Does NOT Do
- Does not batch-upload files to Zenodo.
- Does not mirror artifacts.
- Does not sync Zenodo records back into the ledger.
- Does not replace GitHub/Zenodo as sources.
- Does not change Artifact Resolver or Workstream inference.
- Does **not** define the final scientific semantics of the ledger.

---

## What Sprint 37 DOES Do
1. Define `ZenodoPublisher` (publication, write-side).
2. Define `LedgerNormalizer` (schema mapping).
3. Add a CLI entrypoint: `python -m observer.zenodo_publisher <ledger.json> --publish`.
4. Validate end-to-end on a known ledger (MNE-Python or Nilearn).

---

## Deliverables
1. `python/observer/zenodo_publisher.py` — Zenodo REST publishing.
2. `python/observer/ledger_normalizer.py` — Ledger → Zenodo metadata mapping.
3. `python/observer/validate_sprint37.py` — Validation script (sandbox deposit, verify DOI fields).
4. `artifacts/sprint37_validation_report.md` — Validation evidence.

---

## Success Criteria
1. `ZenodoPublisher.deposit()` returns a valid Zenodo deposition dict with `id` and `status`.
2. `ZenodoPublisher.publish()` returns a DOI string of the form `10.5281/zenodo.XXXXXX`.
3. `LedgerNormalizer.normalize_for_zenodo()` produces a dict accepted by the Zenodo API.
4. End-to-end flow completes in < 30s for a ledger of ~50 artifacts.
5. The resulting Zenodo record reads as a **traceable scientific object**, not just a project dump.

If criteria 1–3 pass, the publishing hypothesis is supported.
Criterion 5 is a qualitative judgment that requires human review.
