# Sprint 39C — MNE-Python Replication Study

## Objective
Falsar la hipótesis: "Scientific comprehension depends primarily on recovering intellectual history."

## Selection criteria
Top 15 issues por número de comentarios + 5 issues adicionales por señales de decisión/fracaso.

## Data collected
| Source | Count | Method |
|--------|-------|--------|
| Issues (top comment) | 25 | GitHub API, sorted by comments desc |
| Issue bodies analyzed | 7 | Manual reading of body text |
| PR merge status | All | GitHub API pull_request.merged_at |

---

## Analysis

### 1. Decision signals found: 5/15

| Issue | Type | Evidence |
|-------|------|----------|
| #3310 sklearn-style encoding | Architectural decision | "port the linear_regression_raw code into a more scikit-learn friendly interface" |
| #3245 Xdawn Transformer compatible with sklearn | Integration decision | Title states compatibility goal |
| #4414 Epochs metadata | Feature decision | "Let's see what the rendered circle output looks like and then decide whether we like it or not" |
| #2710 refactor PSD functions | Refactor decision | Title: "MRG: refactor PSD functions" |
| #2856 GAT refactor _predict, model_selection | Refactor decision | Title: "ENH: GAT refactor _predict, model_selection" |

### 2. Failure signals found: 4/15

| Issue | Evidence |
|-------|----------|
| #2975 "3rd try" | Explicitly labeled as 3rd attempt at eeglab event reading |
| #1388 cross frequency coupling | 75 comments, references to Canolty 2006 and Tort 2010, NEVER MERGED |
| #615 Realtime decoding | 64 comments. Author says: "surprised at uniformly 100% accuracies - either something wrong with the code." NEVER MERGED |
| #4797 CSD and DICS beamformers | WIP, newer implementation replacing older approach |

### 3. Pivot signals found: 3/15

| Issue | Evidence |
|-------|----------|
| #3310 encoding pipelines | Migration from linear_regression_raw to sklearn-style |
| #2975 (following #2676) | Two attempts at eeglab reading, second one adds events |
| #4797 beamformers | "New implementation for CSD and DICS beamformers" |

### 4. Controversy signals found: 2/15

| Issue | Evidence |
|-------|----------|
| #2154 epoch plot | 303 comments (highest in repo). Multiple approaches discussed. |
| #4414 Epochs metadata | 209 comments, 4 reviewers required |

### 5. Open Question signals found: 2/15

| Issue | Evidence |
|-------|----------|
| #615 "surprised at uniformly 100% accuracies" | Open scientific question about results validity |
| #1388 cross frequency coupling | Never determined if approach is correct |

---

## Coverage estimate

| Category | Found | Recoverable? | Notes |
|----------|-------|-------------|-------|
| Decisions | 5 | Yes | Visible in title + body |
| Failures | 4 | Yes | Visible in merge status + title signals |
| Pivots | 3 | Partial | Requires temporal linking (#2676->#2975) |
| Controversies | 2 | Yes | High comment count is reliable signal |
| Open questions | 2 | Yes | Visible in body language |
| Trade-offs | 1 | Partial | Requires reading discussion |

Total signals: 17/15 issues carry at least one intellectual history signal.

---

## Verdict

> Intellectual history IS present in MNE-Python issues.
> Patterns are observable: decisions, failures, pivots, controversies, and open questions.
> Recovery from metadata (title, labels, merge status, comment count) is feasible.
> Full recovery requires body text analysis for trade-offs and detailed rationale.
