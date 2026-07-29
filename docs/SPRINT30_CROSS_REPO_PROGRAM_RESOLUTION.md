# Sprint 30: Cross-Repository Program Resolution
## Distributed Scientific Programs Across Organizations

---

## Strategic Context

Sprint 29 proved: Program Resolver works within a single repository/organization.

Current architecture:
```
Level 0: Evidence Sources
    ↓
Level 1: Scientific Artifact Resolver
    ↓
Level 2: Program Resolver (within one repo/org)
    ↓
Level 3: Scientific Activity Ledger
```

The next threshold is cross-repository program resolution.

Science is not organized in single repositories.
Science is organized in distributed programs spanning:

* Multiple repositories
* Multiple DOIs
* Multiple organizations/universities
* Multiple datasets
* Multiple researchers/agents

Examples:
- Alzheimer's Disease Neuroimaging Initiative (ADNI)
- Human Cell Atlas
- Allen Brain Atlas
- BIDS ecosystem
- OpenNeuro ecosystem

---

## Sprint 30 Objective

Build a **Cross-Repository Program Resolver** that discovers scientific programs spanning heterogeneous evidence sources without central authority.

Success criterion:
Can CoResearcher discover that artifacts from different repositories, DOIs, and organizations belong to the same scientific program?

Question:
> ¿Puede CoResearcher descubrir que estos artefactos pertenecen al mismo programa sin que nadie se lo diga?

---

## Input

List of ScientificArtifact objects from multiple repositories.

Example: artifacts from:
- github.com/mne-tools/mne-python
- github.com/bids-standard/bids-specification
- github.com/OpenNeuroDatasets/ds000117
- zenodo.org/records/...
- api.openalex.org/works/...
- api.crossref.org/works/...

---

## Output

```json
{
  "program_id": "adni",
  "name": "Alzheimer's Disease Neuroimaging Initiative",
  "description": "Longitudinal multimodal study of Alzheimer's disease progression",
  "timeline": {
    "start_year": 2004,
    "latest_activity": "2026-07-17",
    "key_milestones": ["ADNI-1", "ADNI-GO", "ADNI-3"]
  },
  "artifacts": {
    "software_releases": [...],
    "papers": [...],
    "datasets": [...]
  },
  "contributors": [...],
  "workstreams": [...],
  "repositories": [
    "github:org/repo1",
    "github:org/repo2",
    "zenodo:record1"
  ],
  "comprehension_summary": "..."
}
```

---

## Scope

What Sprint 30 does NOT do:
- No new connectors
- No new NLP models
- No new artifact types
- No manual labeling

What Sprint 30 DOES do:
1. Extend ProgramResolver to group by semantic similarity beyond single GitHub repo
2. Build cross-repository linking heuristics:
   - shared DOI citations
   - shared contributor identities
   - shared named entities in titles/notes
   - shared grant/project identifiers if present
3. Generate cross-repository Program objects
4. Validate on at least 2 known distributed programs

---

## Cross-Repository Resolution Logic

Given: N ScientificArtifact objects from diverse repositories.

Steps:
1. Group by exact `github_repo` if present.
2. For ungrouped artifacts, build similarity graph:
   - DOI overlap → strongly related
   - Shared contributor names/ORCIDs → related
   - Title/notes keyword overlap → potentially related
3. Cluster similarity graph into candidate programs.
4. Merge clusters that share:
   - same DOI
   - same contributor + overlapping temporal window
   - high title/note similarity
5. Output one Program per cluster.
6. Attach all contributing repositories to the program.

Output:
- Programs spanning multiple repositories.
- Evidence links explaining why artifacts were grouped.

---

## Validation Targets

Known distributed scientific programs with public artifacts:

1. **BIDS ecosystem**
   - Repos: bids-standard/bids-specification, bids-standard/pybids, bids-standard/bids-examples
   - Artifacts: papers, datasets, software releases
   - Expected: one Program for "BIDS"

2. **OpenNeuro datasets**
   - Repos: OpenNeuroDatasets/ds000117, OpenNeuroDatasets/ds000248, etc.
   - Artifacts: datasets, papers
   - Expected: one Program per dataset, or one Program for "OpenNeuro platform"

Selection rationale:
- Public visibility
- Multiple repositories with shared DOI/contributor/topic signals
- Experts can judge grouping correctness

Validation protocol:
1. Fetch artifacts from 3+ BIDS/OpenNeuro repos.
2. Run Cross-Repository Program Resolver.
3. Inspect resulting programs and rationale.
4. Record:
   - Did the resolver group BIDS repos together?
   - Did it correctly separate OpenNeuro datasets?
   - Are the workstreams coherent?
   - Is the comprehension summary accurate?

---

## Deliverables

1. `python/observer/cross_repo_program_resolver.py` — Cross-repository grouping logic
2. `python/observer/validate_sprint30.py` — Validation script
3. `artifacts/sprint30_cross_repo_validation.md` — Validation report

No new connectors.
No redesign of existing pipeline.
Evidence-first.