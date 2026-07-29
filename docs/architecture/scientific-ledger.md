# Scientific Activity Ledger

## What It Is

A **Scientific Activity Ledger** is CoResearcher's core scientific object.

It is a verifiable, navigable reconstruction of how a scientific investigation happened, not just a summary of its outputs.

## What It Represents

A ledger represents **one investigatable claim or question** within a project.

That unit is encoded in the ledger as:

- `scientific_unit`: the kind of scientific unit represented.
- `unit_rationale`: why this ledger was bounded this way.

This is looser than a paper and tighter than a repository. It maps to:

- a workstream + its evidence + its artifact set + its contributors.
- the minimal traceable unit of scientific activity.

## What It Does NOT Represent

It does **not** claim:

- What the overarching "program" is
- What the governance structure is
- What the mission is
- Administrative boundaries that are not present in evidence

Those are inferences beyond evidence, and Sprints 27-32 showed they are not reliably reconstructable from public signals alone.

## Relation to Artifacts

```text
Evidence (GitHub, Zenodo, OpenAlex, Crossref)
    ↓
Artifacts
    ↓
Workstream inference
    ↓
ScientificLedger
```

A ledger bundles artifacts. It does not replace them.

Artifacts remain the atomic outcomes. The ledger is the traceable context around them.

## Relation to Zenodo

A ledger can be deposited in Zenodo and receive a DOI.

That DOI makes the ledger:

- persistent
- versioned
- citable
- discoverable via Crossref/DataCite

The scientific unit semantics are preserved in Zenodo metadata (`keywords`, `notes`) so downstream readers can interpret what the ledger was intended to represent.

## Scope

A ledger:

- includes canonical artifacts from GitHub, Zenodo, OpenAlex, Crossref
- includes inferred workstreams with signal evidence
- includes contributors with GitHub/ORCID when available
- includes a timeline from artifact dates and release dates

A ledger does **not** include:

- full paper texts
- code structure and API docs
- issue/PR discussions
- build/test status
- governance/mission statements

Whether those are required for comprehension is left to the consumer.

## Versioning

Each published ledger snapshot is a new Zenodo deposit with its own DOI.

Future runs can compare against the cited ledger snapshot to detect changes in:

- evidence set
- artifact set
- contributor set
- workstream inference
- scientific_unit assignment