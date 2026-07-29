# Sprint 35: Comprehension Experiment Protocol

Date: 2026-07-17
Hypothesis: A Scientific Activity Ledger reduces comprehension cost compared to raw repository access.
Success criterion: >=50% reduction in time with no significant loss of accuracy.

---

## Projects

- mne-python: MNE-Python/mne-python
- nilearn: nilearn/nilearn
- pybids: bids-standard/pybids

## Conditions

### Condition A: Raw Repository
- Participant accesses only the GitHub repository.
- Answers the 10 comprehension questions.
- Time and accuracy recorded.

### Condition B: Scientific Activity Ledger
- Participant accesses only the generated Ledger (no repository).
- Answers the same 10 comprehension questions.
- Time and accuracy recorded.

## Questionnaire

- What is the main purpose of this project?
- What problem does it solve?
- What artifacts exist? (papers, datasets, software releases)
- What workstreams or lines of activity are visible?
- Who are the main contributors?
- What changed recently (last 3 months)?
- What appears unfinished or in progress?
- What are the major outputs or results?
- What standards or protocols does it adopt?
- What should a newcomer read first?

## Metrics

- Time per question (seconds)
- Total time (seconds)
- Accuracy (0-1 per question)
- Confidence (1-5 Likert per question)

## Analysis

- Mean time delta (raw - ledger)
- Mean accuracy delta (ledger - raw)
- Statistical significance (t-test, n>=10 participants per condition)

## Required Participants

- At least 10 per condition per project.
- Total minimum: 60 participants across 3 projects and 2 conditions.

## Output

- Markdown report with delta table and statistical test results.
