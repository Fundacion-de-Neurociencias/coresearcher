# Sprint 39C — PyBIDS Replication Study

## Objective
Falsar la hipótesis: "Scientific comprehension depends primarily on recovering intellectual history."

## Selection criteria
Top 25 issues por número de comentarios.

## Data collected
| Source | Count | Method |
|--------|-------|--------|
| Issues (top comment) | 25 | GitHub API |
| Issue bodies analyzed | 8 | Manual reading |
| PR merge status | All | GitHub API |

---

## Analysis

### 1. Decision signals found: 4/25

| Issue | Type | Evidence |
|-------|------|----------|
| #369 REFACTOR 0.8 | Major refactor decision | "REFACTOR: 0.8 [WIP]" (36c). Explicit version-targeted refactoring. |
| #840 Update config for microscopy, qMRI, PET, ASL | Scope expansion decision | "[ENH] Update config to support microscopy, qMRI, PET, ASL" (7c) |
| #650 Add CLI to PyBIDS | Feature decision | "ENH: Add CLI to PyBIDS" (13c) |
| #863 BIDSLayoutV2 | Architecture decision | "[WIP] introduce BIDSLayoutV2" (12c, still open) |

### 2. Failure signals found: 2/25

| Issue | Evidence |
|-------|----------|
| #451 get_collections fails with lists | "get_collections fails when meta-data includes lists" — labeled as bug, explicit failure documentation |
| #426 Derivatives indexing fails silently | "Derivatives indexing fails silently for deriv directories that lack a dataset_description.json file" — bug with explicit failure mode |

### 3. Pivot signals found: 2/25

| Issue | Evidence |
|-------|----------|
| #122 Refactoring analysis module | "WIP: Refactoring of analysis module" (30c) — structural change mid-project |
| #617 Improve modularization of bids.reports | "[REF] Improve modularization of bids.reports" — modularization pivot |

### 4. Controversy signals found: 0/25

None of the top 25 issues exceed 54 comments. Max is #356 with 54c. No strong controversy signal.

### 5. Open Question signals found: 1/25

| Issue | Evidence |
|-------|----------|
| #487 Allow wildcard names for model variables | "Allow wildcard names for model variables" (28c) — unresolved design question |

---

## Coverage estimate

| Category | Found | Recoverable? | Notes |
|----------|-------|-------------|-------|
| Decisions | 4 | Yes | Visible in titles |
| Failures | 2 | Yes | Bug label + description of failure mode |
| Pivots | 2 | Yes | Visible in refactor labels |
| Controversies | 0 | No | Project scale may be too small |
| Open questions | 1 | Yes | Issues with discussion nature |

Total signals: 9/25 issues carry at least one intellectual history signal.

---

## Comparison with MNE-Python and Nilearn

| Dimension | MNE-Python | Nilearn | PyBIDS |
|-----------|-----------|---------|--------|
| Signal density | 17/15 (1.13) | 14/25 (0.56) | 9/25 (0.36) |
| Max comments | 303 | 172 | 54 |
| Failure visibility | High | Medium | Low |
| Controversy signals | Very high | Moderate | None detected |
| Open questions | Clear | Clear | Weak |
| Standardized prefixes | WIP/MRG/ENH | WIP/MRG/ENH | WIP/ENH/REF |

---

## Special observation: PyBIDS scale effect

PyBIDS is a smaller project than MNE-Python and Nilearn:
- Fewer contributors
- Shorter history
- More focused scope (BIDS standard implementation)
- Less design exploration

This means intellectual history signals are weaker NOT because the pattern is absent, but because there is less total history to observe.

---

## Verdict

> Intellectual history IS present in PyBIDS, but at significantly lower density.
> The project scale directly correlates with signal density.
> PyBIDS has more infrastructure signals (refactoring, modularization) and fewer design exploration signals.
> Controversies may not exist at all for a specification-implementation project like PyBIDS.
> The hypothesis "comprehension depends on intellectual history" may need qualification: it may depend on project type and scale.
