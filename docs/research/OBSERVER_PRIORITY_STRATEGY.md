# Observer Priority Strategy

## Core Principle

> **Observe the most influential science first**, not all science.

The scarcity of CoResearcher is not storage but **computational attention** for entity resolution and reconstruction. Prioritization must happen from day one.

---

## Priority Score Formula

```text
Priority Score =
0.4 × Citations (scientific impact)
+ 0.3 × GitHub stars (adoption signal)
+ 0.2 × Contributors (community)
+ 0.1 × Recent activity (momentum)
```

This weights scientific influence above technical metrics.

---

## Acquisition Strategies (3-Tier Integration)

### Tier 1: OpenAlex → Code (Paper-Driven Discovery)

**Flow:** Paper → GitHub → Zenodo → Dataset

```
Paper (OpenAlex DOI)
    ↓
GitHub repository (from paper "Code availability")
    ↓
Zenodo release (DOI-linked artifacts)
    ↓
Dataset/Workflow/Model
```

**Why OpenAlex:**
- ~250M works indexed
- Citation counts included
- Concepts taxonomy (Alzheimer's, Parkinson's, etc.)
- Open API, no rate limits
- DOI-first approach aligns with scientific artifacts

**Query Examples:**
```
Top cited works in:
- Alzheimer's disease
- Parkinson's disease
- Neuroimaging
- Bioinformatics
- Genetics
```

---

### Tier 2: Zenodo First (Artifact-First Discovery)

**Flow:** DOI → Software/Dataset → Repository

Zenodo records are closer to scientific artifacts than commits:
- datasets
- software
- workflows
- models

All with DOIs for traceability. DOI + version + files are strong signals.

**Scoring factors:**
- Has DOI: +0.4 (primary scientific artifact)
- Has version: +0.2 (indicates maturity)
- Has files: +0.2 (actual artifact present)
- Recent (<= 5 years): +0.2

---

### Tier 3: Ecosystem Foci (Pre-Validated Discovery)

Scientific domains with strong open science culture. These are **pre-validated** for scientific impact:

#### Neurociencia
- **BIDS** - Brain Imaging Data Standard
- **OpenNeuro** - Neuroscience data archive
- **NeuroVault** - Neuroimaging results
- **Nilearn** - Machine learning for neuroimaging
- **MNE-Python** - EEG/MEG analysis

#### Bioinformática
- **Bioconductor** - Bioinformatics packages
- **Scanpy** - Single-cell analysis
- **AnnData** - Annotated data structures
- **Nextflow** - Scientific workflows

#### IA biomédica
- **MONAI** - Medical Open Network for AI
- **DeepChem** - Deep learning for chemistry/biology

---

## Implementation Architecture

### `python/observer/priority_discovery.py`

Three discovery functions:

```python
# discover_from_openalex() - Paper-driven with citations
# discover_from_zenodo() - Artifact-driven with DOI signals
# discover_from_ecosystems() - Pre-validated reference projects
```

All objects are scored with unified `priority_score()` formula.

### Output

```python
generate_top_100_priority_list() → {
    "strategy": "Observe the most influential science first",
    "total_queued": N,
    "top_enriched": [...],
    "by_source": {...}
}
```

---

## Selective Observation Protocol

**Observe ONLY the top 100 priority-scored objects.**

Do NOT attempt to observe everything. Focus on reconstruction quality, not quantity.

### Validation Target

Reconstruct correctly only:
- **Neurodiagnoses** - Core project
- **GeneForge** - Core project
- **20 reference scientific repositories** - Quality targets

This is more useful than observing 100,000 mediocre repositories.

---

## Scientific Activity Graph Vision

The goal is to reconstruct:

```
Paper
→ Dataset
→ GitHub repo
→ Zenodo release
```

This creates a **Scientific Activity Graph** where:
- Papers are the primary nodes
- Code repositories are secondary
- Datasets/workflows are tertiary artifacts
- All linked by DOI and traceability

---

## Next Actions

- [x] Implement OpenAlex connector
- [x] Implement Zenodo connector
- [x] Create unified scoring mechanism
- [x] Generate priority list (top 100)
- [ ] Run selective observation
- [ ] Validate reconstruction quality