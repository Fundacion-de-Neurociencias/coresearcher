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

## Role of GitHub and Zenodo in the Research Lifecycle

CoResearcher bridges real-time collaborative development and formal academic preservation:

```text
       [ GITHUB ]
 (Live telemetry: Issues, PRs, Commits, CI)
            │
            ▼ (Observer: Passive Inference)
     [ CoResearcher ]
  (Scientific Ledger: Question → Evidence → Review → Provenance)
            │
            ▼ (ZenodoPublisher: Normalization & REST API)
       [ ZENODO ]
 (Persistent DOI 10.5281/zenodo.*, citable in academic literature)
```

### 1. GitHub: Real-Time Telemetry & Passive Inference
GitHub serves as the active digital laboratory. Through passive inference (see [Observer Constitution](docs/OBSERVER_CONSTITUTION.md)), CoResearcher captures events without requiring manual data entry:

- **GitHub Issues** $\rightarrow$ Inferred as **`QUESTION`** (research directions, hypotheses, open problems).
- **Commits & Pull Requests** $\rightarrow$ Inferred as **`ACTION / EVIDENCE`** (verifiable units of scientific execution, scripts, reproducible data runs).
- **PR Reviews & Discussion Threads** $\rightarrow$ Inferred as **`REVIEW`** (peer validation, methodological checks, human-agent sign-offs).
- **Git Metadata & CI/CD Traces** $\rightarrow$ Inferred as **`PROVENANCE`** (model identities, environment configurations, execution hashes).

### 2. Zenodo: Dual Role (Discovery & Persistent Preservation)
Zenodo operates at both the input and output phases of research (see [Sprint 37 Zenodo Publishing](docs/SPRINT37_ZENODO_PUBLISHING.md)):

- **Inbound Discovery (Read-only):** The observer monitors existing Zenodo deposits (`zenodo_connector.py`) to connect baseline datasets, software releases, and external scientific outputs to the research graph.
- **Outbound Preservation & DOI Minting (Publishing):** When a milestone or ledger is finalized, `zenodo_publisher.py` serializes and normalizes the ledger (`ledger_normalizer.py`), uploads the artifact, and registers a permanent **DOI** (`10.5281/zenodo.*`). This makes the collaborative process fully citable, reproducible, and recognized across academic indexes (DataCite, Crossref).

---

## Key Documentation

- [Observer Constitution](docs/OBSERVER_CONSTITUTION.md) - Principles of passive capture and object inference
- [Zenodo Publishing & DOI Registration](docs/SPRINT37_ZENODO_PUBLISHING.md) - Pipeline for depositing ledgers and minting DOIs
- [Protocol vs Discovery Suite](docs/CORESEARCHER_PROTOCOL_VS_DISCOVERY_SUITE.md) - Core open infrastructure vs intelligence layers
- [Scientific Activity Model](docs/SCIENTIFIC_ACTIVITY_MODEL.md) - Representation of scientific actions and units

---

## Status

Experimental. Building the first Scientific Activity Ledgers.

Join us in making agentic science coordination real.
