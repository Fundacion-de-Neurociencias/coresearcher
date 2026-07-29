# Sprint 39C — Nilearn Replication Study

## Objective
Falsar la hipótesis: "Scientific comprehension depends primarily on recovering intellectual history."

## Selection criteria
Top 25 issues por número de comentarios + issues con señales de decisión/fracaso.

## Data collected
| Source | Count | Method |
|--------|-------|--------|
| Issues (top comment) | 25 | GitHub API, sorted by comments desc |
| Issue bodies analyzed | 8 | Manual reading |
| PR merge status | All | GitHub API |

---

## Analysis

### 1. Decision signals found: 6/25

| Issue | Type | Evidence |
|-------|------|----------|
| #1766 switch papaya to brainsprite | Technology decision | "switch from papaya to brainsprite in plotting.view_stat_map" (166c) |
| #2076 switch from Nose to Pytest | Infrastructure decision | "[MRG] Switch from Nose to Pytest" (76c) |
| #693 dictionary learning refactoring | Architecture decision | "[MRG] Dictionary learning + nilearn.decomposition refactoring" (51c) |
| #657 SpaceNet | Algorithm decision | "SpaceNet (this PR succeeds PR #219)" — explicit succession |
| #219 S-LASSO and TV-l1 | Algorithm decision | "(WIP) Sparse models: S-LASSO and TV-l1" (78c, never merged into master directly) |
| #2019 Initial visual reports | Feature decision | "[ENH] Initial visual reports" (172c) |

### 2. Failure signals found: 2/25

| Issue | Evidence |
|-------|----------|
| #219 S-LASSO and TV-l1 | WIP, succeeded by #657 SpaceNet. Original approach was replaced. |
| #698 Decoder: Metaestimator | WIP, never merged. Later continued by #2000 as "[ENH] Continuation of Decoder:Metaestimator" |
| #2000 Decoder continuation | Explicitly labeled as "Continuation" — implies prior attempt existed |

### 3. Pivot signals found: 4/25

| Issue | Evidence |
|-------|----------|
| #219 -> #657 | S-LASSO approach replaced by SpaceNet |
| #698 -> #2000 | Decoder metaestimator restarted as continuation |
| #1766 papaya to brainsprite | Direct technology migration |
| #2076 Nose to Pytest | Testing framework migration |

### 4. Controversy signals found: 1/25

| Issue | Evidence |
|-------|----------|
| #1766 switch papaya to brainsprite | 166 comments on a visualization library switch — significant discussion |
| #2019 visual reports | 172 comments — high engagement |

### 5. Open Question signals found: 1/25

| Issue | Evidence |
|-------|----------|
| #2567 innacurate z-values | "FIXUP: innacurate z-values for big p-values" — unresolved accuracy issue |

---

## Coverage estimate

| Category | Found | Recoverable? | Notes |
|----------|-------|-------------|-------|
| Decisions | 6 | Yes | Clearly stated in titles |
| Failures | 2 | Yes | Requires temporal linking (#219->#657, #698->#2000) |
| Pivots | 4 | Yes | Temporal linking between successive PRs |
| Controversies | 1 | Partial | High comment count is indicator only |
| Open questions | 1 | Yes | Bug labels + fixup titles |

Total signals: 14/25 issues carry at least one intellectual history signal.

---

## Comparison with MNE-Python

| Dimension | MNE-Python | Nilearn |
|-----------|-----------|---------|
| Signal density | 17/15 (1.13/issue) | 14/25 (0.56/issue) |
| Max comments | 303 | 172 |
| Failure visibility | High (merge status) | Medium (succession pattern) |
| Decision formality | WIP/MRG/ENH prefixes | Similar but less standardized |
| Temporal linking | Explicit (#2975 "3rd try") | Implicit (#698 continuation) |
| Controversy signals | Very high (303c, 209c) | Moderate (172c, 166c) |

---

## Verdict

> Intellectual history IS present in Nilearn, but at lower density than MNE-Python.
> The signal is more implicit — requires temporal linking between PRs.
> Failure signals are weaker (no explicit "failed" language).
> Decision signals are present in technology migrations (papaya->brainsprite, Nose->Pytest).
> Temporal sequences are the primary carrier of intellectual history.
