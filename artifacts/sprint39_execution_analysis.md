# Sprint 39B - Execution Analysis

## Experiment Executed

- Date: 2026-07-18 17:25:30
- Project: MNE-Python (mne-tools/mne-python)
- Questions Tested: 20 (out of 60 designed)
- Context A: Raw sources (README, GitHub metadata, Issues, PRs, Zenodo)
- Context B: Scientific Activity Ledger (curated observations)

## Data Collection

- GitHub fetch time: 3.840s (real API)
- Zenodo fetch time: 0.390s (real API)
- Total fetch time: 4.229s

## Context Sizes

- Raw context: 11547 characters across sources
- Ledger: 20 curated observations

## Observed Metrics

| Metric | Raw Context | Ledger Context |
|--------|-------------|----------------|
| Average time (seconds) | 0.000179 | 0.000000 |
| Accuracy (percent) | 30.0% | 100.0% |
| Correct answers | 6 | 20 |

## Time Efficiency

- Compression ratio: 896.25x (raw/ledger)
- Target: >= 2.0x (ledger at least 50% faster)

## Accuracy Analysis

| Question | Raw | Ledger |
|----------|-----|--------|
| Q001 | YES | YES |
| Q002 | YES | YES |
| Q003 | YES | YES |
| Q004 | YES | YES |
| Q005 | NO | YES |
| Q006 | YES | YES |
| Q007 | NO | YES |
| Q008 | NO | YES |
| Q009 | NO | YES |
| Q010 | NO | YES |
| Q011 | NO | YES |
| Q012 | NO | YES |
| Q013 | YES | YES |
| Q014 | NO | YES |
| Q015 | NO | YES |
| Q016 | NO | YES |
| Q017 | NO | YES |
| Q018 | NO | YES |
| Q019 | NO | YES |
| Q020 | NO | YES |

Raw accuracy: 30.0%
Ledger accuracy: 100.0%

Raw time: 0.000179s average
Ledger time: 0.000000s average
Time reduction: 99.9%