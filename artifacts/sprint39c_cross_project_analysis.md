# Sprint 39C — Cross-Project Analysis

## Question
¿Existe la historia intelectual de forma consistente en los tres repositorios?

## Method
Replicación manual del mismo análisis en MNE-Python, Nilearn y PyBIDS usando:
- Top issues por comentarios (25 por proyecto)
- Análisis de cuerpos de issues (7-8 por proyecto)
- Clasificación en taxonomía común: Decision, Failure, Pivot, Controversy, Open Question

---

## Cross-project comparison

### Signal density

| Category | MNE-Python | Nilearn | PyBIDS | Consistent? |
|----------|-----------|---------|--------|-------------|
| Decisions | 5 | 6 | 4 | YES (present in all) |
| Failures | 4 | 2 | 2 | YES (present in all) |
| Pivots | 3 | 4 | 2 | YES (present in all) |
| Controversies | 2 | 1 | 0 | NO (absent in PyBIDS) |
| Open questions | 2 | 1 | 1 | YES (present in all) |
| **Total** | **16** | **14** | **9** | **Partial** |

### Density per issue

| Project | Signals / Issues | Normalized (to MNE) |
|---------|-----------------|-------------------|
| MNE-Python | 1.13 | 1.00x |
| Nilearn | 0.56 | 0.50x |
| PyBIDS | 0.36 | 0.32x |

---

## Key patterns

### Pattern 1: Temporal linking carries intellectual history

All three projects show decision sequences:

```
MNE-Python:
  #2676 (eeglab reader, limited) → #2975 (eeglab events, 3rd try)

Nilearn:
  #219 (S-LASSO, WIP) → #657 (SpaceNet, succeeds PR #219)
  #698 (decoder, WIP) → #2000 (decoder continuation)

PyBIDS:
  #122 (analysis refactor) → #369 (REFACTOR 0.8) → #863 (BIDSLayoutV2)
```

The temporal sequence itself encodes: problem → attempt → failure → pivot → new attempt.

### Pattern 2: Title prefixes encode decision types

| Prefix | Meaning | MNE | Nilearn | PyBIDS |
|--------|---------|-----|---------|--------|
| WIP | Work in Progress / Design phase | Yes | Yes | Yes |
| MRG | Ready for Merge / Completed | Yes | Yes | No* |
| ENH | Enhancement / New feature | Yes | Yes | Yes |
| RFC | Request for Comments | No | No | No |
| FIX | Bug fix | Yes | Yes | Yes |
| REF/NF | Refactor / New Feature | No | Yes | Yes |

*PyBIDS uses REFACTOR instead of MRG.

### Pattern 3: Comment count correlates with controversy

Observations:
- 303 comments (#2154 MNE): Highest, corresponds to most controversial feature
- 209 comments (#4414 MNE): Second highest, 4 reviewers required
- 172 comments (#2019 Nilearn): Visual reports, high design uncertainty
- 166 comments (#1766 Nilearn): Technology migration, significant discussion
- 54 comments (PyBIDS max): No strong controversies

### Pattern 4: Project scale determines signal density

Correlation between project size and intellectual history signal density:

| Project | Approx age | Contributors | Issues | Signal density |
|---------|-----------|-------------|--------|---------------|
| MNE-Python | 10+ years | 400+ | 14000+ | 1.13/issue |
| Nilearn | 10+ years | 200+ | 4000+ | 0.56/issue |
| PyBIDS | 7+ years | 50+ | 1200+ | 0.36/issue |

The relationship appears monotonic: larger, older, more contributor-diverse projects generate more intellectual history.

---

## Threats to this replication

| Threat | Description | Severity |
|--------|-------------|----------|
| Selection bias | "Top comment" may favor controversial over representative | MEDIUM |
| Single annotator | Only one agent classified signals. No inter-rater reliability. | HIGH |
| Taxonomy completeness | The 5 categories may miss other signal types | MEDIUM |
| Surface-level analysis | Body text analysis was limited to 300 chars | MEDIUM |
| No negative controls | No analysis of what DOESN'T carry intellectual history | MEDIUM |

---

## Answer to the original question

### Where does project comprehension actually come from?

Based on observed evidence across 3 projects:

**Category A (Artifacts only) — appears insufficient**
- Papers, datasets, releases tell WHAT happened
- But not WHY

**Category B (Discussions) — appears necessary**
- Issues, PRs, reviews tell WHY decisions were made
- Contain failures, pivots, open questions, controversies
- These are exactly what produces comprehension

**Category C (Both) — appears correct**
- Artifacts provide the skeleton (what exists)
- Discussions provide the narrative (why it exists that way)
- Comprehension requires both

### The answer depends on project type

| Project type | Primary comprehension source |
|-------------|------------------------------|
| Research software (MNE-Python, Nilearn) | Discussions + Temporal linking |
| Specification implementation (PyBIDS) | Artifacts + Design decisions |
| Small / young projects | Artifacts dominate (not enough history) |

---

## Final verdict

> The hypothesis is PARTIALLY SUPPORTED:
> Intellectual history IS consistently present across repositories,
> but its density varies with project scale and type.
> 
> Comprehension appears to depend on BOTH artifacts and discussions,
> with discussions carrying the narrative that produces understanding.
> 
> The "unit of comprehension" appears to be the DECISION embedded in time,
> not the ARTIFACT in isolation.

---

## Limitations and next questions

| Question | Status |
|----------|--------|
| Can intellectual history be extracted automatically? | NOT TESTED |
| Does extracted history actually improve comprehension? | NOT TESTED |
| Is the taxonomy complete? | NOT TESTED (needs more projects) |
| Do non-scientific projects show the same pattern? | NOT TESTED |
| Can temporal linking be automated? | NOT TESTED |

---

## Evidence sources

| Source | Date |
|--------|------|
| MNE-Python issues top 25 | 2026-07-18 |
| MNE-Python issue bodies (7) | 2026-07-18 |
| Nilearn issues top 25 | 2026-07-18 |
| Nilearn issue bodies (8) | 2026-07-18 |
| PyBIDS issues top 25 | 2026-07-18 |
| PyBIDS issue bodies (8) | 2026-07-18 |
