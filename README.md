# CoResearcher Protocol

**An open protocol for coordinating scientific work between humans and AI agents.**

---

## The Problem

Scientific production is exploding.

Human researchers and AI agents generate papers, code, datasets, analyses and hypotheses faster than the scientific community can coordinate them.

Existing tools (email, GitHub, Slack) don't track scientific lineage.

---

## The Solution

CoResearcher creates a Scientific Activity Ledger that captures how research actually happens.

```text
Question
    ↓
Evidence (code, experiments, analysis)
    ↓
Review (agent or human validation)
    ↓
Artifact (paper, dataset, model, finding)
```

Not memorization. Coordination.

---

## How It Works

**Public Science**: Automatically observed from GitHub, arXiv, Zenodo, OSF.

**Private Science**: Explicitly connected via `coresearcher connect` command.

Owner controls visibility level: public / discoverable / connected / private.

---

## Why Now

- AI agents are doing real research
- No way to coordinate agent/human collaboration
- Scientific reproducibility demands better provenance
- Teams waste hours understanding each other's work

---

## Quick Start

```bash
# Check if your project appears
# Visit coresearcher.org (coming soon)

# Connect private repository
python -m observer /path/to/your/repo

# Choose visibility level
visibility: connected
```

---

## Objects

- **Question** - Research direction
- **Evidence** - Executable activity (not raw commits)
- **Review** - Validation with provenance
- **Artifact** - Published outcome
- **Scientific Activity Ledger** - Traceable, versioned, citable record of scientific activity

---

## Scientific Activity Ledger

CoResearcher maintains a **Scientific Activity Ledger** that records:

- evidence acquisition
- artifact generation
- provenance chains
- contributor activity
- scientific units (`scientific_unit`, `unit_rationale`)

A ledger can be published to Zenodo and obtain its own DOI, making the research process itself a **first-class scientific object**:

```text
Question
    ↓
Evidence
    ↓
Artifacts
    ↓
Scientific Activity Ledger
    ↓
Zenodo deposit
    ↓
DOI
    ↓
Citable Scientific Object
```

This makes CoResearcher different from mere literature or commit scrapers: it does not just summarize science. It produces **verifiable, persistent, citable representations of scientific activity**.

---

## Status

Experimental. Building the first Scientific Activity Ledgers.

Join us in making agentic science coordination real.
