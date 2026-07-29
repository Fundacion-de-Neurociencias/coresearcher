# Zero Infrastructure Constitution
## CoResearcher as Protocol Over Existing Primitives

**Version 1.0.0** - Zero-Cost Foundation  
**Status**: Constitutional Document - Survival Requirement

---

## Article I: The Zero-Infrastructure Principle

### Section 1. The Constraint

> CoResearcher cannot depend on any infrastructure requiring future funding to exist.

This is not a preference. This is a **survival constraint**.

### Section 2. What Dies Without Funding

| Infrastructure | Death Timeline |
|----------------|----------------|
| PostgreSQL server | 3-6 months |
| Neo4j database | 1-2 months |
| Kubernetes cluster | 2-4 weeks |
| Custom authentication | 1-3 months |
| Admin panels | 6-12 months |
| Dedicated hosting | 1-6 months |

### Section 3. What Survives Free

| Infrastructure | Survival |
|----------------|----------|
| ORCID identities | ✅ Free forever |
| GitHub repositories | ✅ Free for open source |
| ROR institutions | ✅ Free |
| Zenodo DOIs | ✅ Free |
| GitHub Actions | ✅ Free tier sufficient |
| MeSH/HGNC/ChEBI | ✅ Public |

---

## Article II: CoResearcher as Protocol

### Section 1. The Definition

CoResearcher is NOT a platform.

CoResearcher IS:
- ✅ A **Protocol** - conventions for scientific coordination
- ✅ An **Ontology** - canonical scientific taxonomy
- ✅ **Conventions** - agreed ways to represent work
- ✅ **Workflows** - reproducible scientific processes

Like Git, which existed before GitHub.

### Section 2. Protocol Primitives

| Primitive | GitHub Equivalent | Free Tool |
|-----------|-------------------|-----------|
| **Identity** | ORCID | ORCID |
| **Institution** | ROR | ROR |
| **Program** | Repository | GitHub Repo |
| **Question** | Issue | GitHub Issue |
| **Action** | Event/Commit | GitHub Actions |
| **Review** | PR Review | GitHub PR Review |
| **Artifact** | Release | Zenodo DOI |
| **Ontology** | Repo structure | GitHub + MeSH/HGNC |

---

## Article III: Object Mapping to Free Primitives

### Section 1. PROGRAM → GitHub Repository

```yaml
# .cosearcher/program.yaml (in repo)
program_id: "PROGRAM-000421"
ontology_path: "Science/Medicine/Neurology/Alzheimer's Disease/Biomarkers"
steward: "ORCID-0000-0002-1825-0097"  # Dr. X
strategy: "private|protected|published"
questions: ["QUESTION-000123", "QUESTION-000456"]
```

Repository name: `science/alzheimer-biomarkers`
Branch: `main` (canonical), feature branches for experiments

---

### Section 2. QUESTION → GitHub Issue

```markdown
# QUESTION-AD-BIOMARKERS

## Question
¿Cuáles son los biomarcadores sanguíneos del Alzheimer?

## Ontological Path
Science/Medicine/Neurology/Alzheimer's Disease/Biomarkers

## Status
- [x] Proposed
- [ ] Active
- [ ] Addressed
- [ ] Superseded

## Activity
- Actions: 47
- Claims: 23
- Reviews: 12
- Last activity: 2026-07-13
```

Labels: `question-type::meso`, `domain::neurology`, `status::active`

---

### Section 3. ACTION → GitHub Actions Run

```yaml
# .github/workflows/action-support.yml
name: Support Claim
on:
  workflow_dispatch:
    inputs:
      claim_id: {required: true}
      evidence_list: {required: true}
jobs:
  support:
    runs-on: ubuntu-latest
    steps:
      - name: Generate support review
        uses: coresearcher/review-action@v1
        with:
          actor: ${{ github.actor }}
          type: SUPPORT
          target: ${{ inputs.claim_id }}
          evidence: ${{ inputs.evidence_list }}
```

Action logs → ACTION-XXXXXX entry
Workflow runs → Immutable ACTION registry

---

### Section 4. REVIEW → GitHub PR Review

```json
// Pull request review comment
{
  "review_id": "REVIEW-000123",
  "score": 0.85,
  "dimensions": {
    "methodological": 0.75,
    "evidence": 0.90,
    "logical": 0.85
  },
  "basis": ["CLAIM-000456", "EVIDENCE-000789"]
}
```

PR review comments → REVIEW-XXXXXX
Review scores → Trust Index contribution

---

## Article IV: The Free Infrastructure Stack

### Section 1. What You Need

| Purpose | Tool | Cost |
|---------|------|------|
| Identity | ORCID | $0 |
| Institution | ROR | $0 |
| Ontology | GitHub + MeSH/HGNC | $0 |
| Questions | GitHub Issues | $0 |
| Actions | GitHub Actions | Free tier (2000 min/month) |
| Reviews | GitHub PR Reviews | $0 |
| Artifacts | Zenodo/Zenodo.GitHub | $0 |
| Versioning | Git | $0 |
| Collaboration | GitHub Discussions | $0 |
| Publication | arXiv/Zenodo/bioRxiv | $0 |

### Section 2. What You DON'T Need

- ❌ Custom database servers
- ❌ Custom authentication
- ❌ Custom UI framework
- ❌ Custom workflow engine
- ❌ Custom review system

---

## Article V: The Validation Test

### Section 1. The Thought Experiment

If tomorrow ALL our code disappears, can CoResearcher still exist?

```
YES if:
- Ontology lives in repository structure + MeSH alignment
- Programs live in GitHub repos with convention
- Questions live in GitHub Issues with labels
- Actions live in GitHub Actions logs
- Reviews live in GitHub PR reviews
- Artifacts live in Zenodo releases
- Identities live in ORCID
- Institutions live in ROR
```

### Section 2. The Current Status

We need to reduce dependencies on:

- [ ] Custom PostgreSQL schemas
- [ ] Custom Neo4j databases  
- [ ] Custom agent registries
- [ ] Custom MCP servers

To:

- [x] Ontology in repository structure
- [x] Questions as Issues
- [x] Actions as workflow logs
- [x] Reviews as PR comments
- [x] Artifacts as releases

---

## Article VI: The First 100 Lines

### Section 1. The Starting Point

```bash
# What you actually build:
1. GitHub Action that creates QUESTION entries from Issues with labels
2. GitHub Action that logs ACTION entries from workflow runs
3. GitHub Action that extracts REVIEW scores from PR reviews
4. GitHub App that maps repo structure to ontology
5. GitHub Action that publishes to Zenodo

Total: ~1000 lines of JavaScript/TypeScript
Cost: $0 (GitHub free tier)
Value: Scientific Coordination Protocol
```

---

## Article VII: Migration Path

### If GitHub-free validation works:
- Add Semantic Compiler (natural language → GitHub issues)
- Add Trust Engine (automated scoring)
- Add Einstein v2 (agentic hypothesis generation)
- Host on GitHub Pages for discovery

### If it doesn't work:
- Learned without burning 6 months of development
- Realized researchers don't want this
- No financial losses

---

*Esta constitución establece que CoResearcher es un Protocolo de Coordinación Científica que puede existir completamente sobre infraestructura gratuita existente. Sin esto, es solo una hipótesis de financiación.*