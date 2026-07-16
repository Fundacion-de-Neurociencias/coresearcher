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

---

## Status

Experimental. Building the first Scientific Activity Ledgers.

Join us in making agentic science coordination real.