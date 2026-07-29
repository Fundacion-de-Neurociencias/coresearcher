# Scientific Publication Model

## Core Idea

CoResearcher does not just observe science.

It can **publish the traceability of science** as a first-class scientific object.

## The Pipeline

```text
Evidence
    ↓
Artifacts
    ↓
ScientificLedger
    ↓
LedgerNormalizer
    ↓
Zenodo Metadata
    ↓
Deposit
    ↓
Publish
    ↓
DOI
```

## Components

### Evidence → Artifacts

Existing connectors gather signals from GitHub, Zenodo, OpenAlex, Crossref, OSF.

They produce `ScientificArtifact` objects:

- dataset
- software_release
- paper
- protocol
- model

### Artifacts → Ledger

`LedgerGenerator` aggregates artifacts into a `ScientificLedger`:

- deduplicates contributors
- infers workstreams from artifact signals
- builds a timeline
- writes a comprehension summary
- records `scientific_unit` and `unit_rationale`

The ledger is the **minimal traceable unit of scientific activity**.

### Ledger → Zenodo Metadata

`LedgerNormalizer` maps ledger fields to Zenodo-compatible metadata:

- title ← ledger.name
- description ← ledger.description + comprehension_summary
- creators ← contributors with ORCID
- dates ← generated_at
- keywords ← workstream signals + scientific_unit
- related_identifiers ← artifact DOIs, GitHub repos
- notes ← ledger_id, counts, scientific_unit, unit_rationale

### Deposit → DOI

`ZenodoPublisher` writes the ledger to Zenodo:

1. Creates a deposit with metadata.
2. Uploads the ledger JSON as a file: `ledger-{ledger_id}.json`.
3. Optionally publishes the deposit.
4. Returns the DOI: `10.5281/zenodo.XXXXXX`.

## Reproducibility Implications

A published ledger enables:

- **Temporal reproducibility**: future agents can compare against the cited snapshot.
- **Semantic reproducibility**: `scientific_unit` preserves the intended scientific meaning.
- **Provenance reproducibility**: contributors, evidence sources, and artifact lineage are recorded.

This is different from a paper's reproducibility, which usually describes methods.

A ledger's reproducibility is **mechanical**: the evidence set, artifact set, and inference parameters are preserved verbatim.

## Citation Model

A ledger can be cited as:

- a dataset
- a software release
- a research artifact

Zenodo assigns Crossref/DataCite metadata, so standard citation tools work.

## What Is Not Published

The ledger does **not** publish:

- raw code
- full paper texts
- issue discussions
- build logs

Those remain external. The ledger points to them via `related_identifiers`.

## Versioning

Each publish creates a new Zenodo deposit with a new DOI.

A project may have multiple ledgers over time:

```text
Project A
├── Ledger v1 → 10.5281/zenodo.12345
├── Ledger v2 → 10.5281/zenedo.12346
└── Ledger v3 → 10.5281/zenodo.12347
```

This makes the evolution of scientific activity traceable.