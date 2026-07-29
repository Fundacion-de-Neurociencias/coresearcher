# Sprint 36: Agent Onboarding Benchmark

Date: 2026-07-17
Hypothesis: A Scientific Activity Ledger reduces agent onboarding cost compared to raw sources.
Success criterion: >=50% reduction in time-to-first-output with <=10% drop in completeness/accuracy.

---

## Projects

- mne-python: MNE-Python/mne-python
- nilearn: nilearn/nilearn
- pybids: bids-standard/pybids

## Conditions

### Condition A: Raw Sources
- Full repository access (README, issues, PRs, releases, papers)

### Condition B: Scientific Activity Ledger
- Ledger only (no direct repo access)

## Task


You are joining this project. Based on the provided materials, produce a concise onboarding brief that covers:
1. What the project does
2. Key artifacts and where to find them
3. Active workstreams
4. Main contributors
5. Recent changes
6. Suggested first steps for a newcomer


## Metrics

- Time to first useful output (seconds)
- Completeness (0–1)
- Accuracy (0–1)
- Actionability (0–1)

## Analysis Plan

- Mean time delta (raw - ledger)
- Mean completeness delta (ledger - raw)
- Statistical significance (t-test, n>=10 per condition)

## Required Participants

- At least 10 agent runs per condition per project.
- Total minimum: 60 runs across 3 projects and 2 conditions.

## Next Steps

1. Prepare raw-source bundles and ledgers.
2. Run agent benchmark.
3. Analyze deltas.
4. Report statistical significance and practical impact.
