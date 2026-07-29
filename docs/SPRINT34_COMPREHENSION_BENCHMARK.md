# Sprint 34: Comprehension Benchmark
## Measuring Time-to-Understanding of Scientific Projects

---

## Strategic Context

Sprint 33 produced the Scientific Activity Ledger: a verifiable, navigable reconstruction of scientific project history.

The remaining empirical question is:

> Does the Ledger actually reduce the time required to understand a scientific project?

This is no longer an architectural question.
It is a product hypothesis to be falsified.

---

## Primary Metric

```text
time_to_understand(project)
```

Measured as:
- Time to answer a fixed set of newcomer questions.
- Condition A: raw repository access
- Condition B: Scientific Activity Ledger access

Success criterion:
Ledger users understand the project significantly faster than raw-repo users.

---

## Benchmark Protocol

### Step 1: Select Projects

Choose publicly known scientific software projects:
- MNE-Python
- Nilearn
- BIDS
- GeneForge (if public evidence available)

### Step 2: Define Question Set

For each project, prepare a standard questionnaire:

1. What is the main purpose of this project?
2. What are the primary artifacts? (papers, datasets, software releases)
3. Who are the main contributors?
4. What workstreams or lines of activity are visible?
5. When did the project start? What is the latest activity?
6. What happened in the last 3 months?
7. What appears to be unfinished or in progress?
8. How is the project organized? (if inferable)
9. What standards or protocols does it adopt?
10. What would you read first to understand the project?

### Step 3: Generate Ledger

Use the Sprint 33 pipeline:
- Evidence Sources → Artifacts → Workstreams → Ledger

### Step 4: Measure

Condition A (Raw Repository):
- Participant accesses the repository directly.
- Time to answer each question is recorded.
- Completeness of answers is scored.

Condition B (Ledger):
- Participant accesses only the Scientific Activity Ledger.
- Time to answer each question is recorded.
- Completeness of answers is scored.

### Step 5: Analyze

- Mean time per question.
- Total time to complete questionnaire.
- Completeness score (0–1).
- Delta between conditions.

Expected outcome:
- Ledger condition: shorter time, equal or higher completeness.
- Raw repo condition: longer time, variable completeness.

---

## What Sprint 34 Does NOT Do

- No new connectors
- No new artifact types
- No new inference rules
- No manual ledger curation
- No ontology expansion

---

## What Sprint 34 DOES Do

1. Define benchmark schema and questionnaire templates.
2. Build automated benchmark harness for pilot studies.
3. Run pilot on 1–2 projects (MNE-Python, GeneForge).
4. Report time-to-comprehension delta.

---

## Deliverables

1. `docs/SPRINT34_COMPREHENSION_BENCHMARK.md`
2. `python/observer/comprehension_benchmark.py`
3. `artifacts/sprint34_comprehension_benchmark.md`

Evidence-first.
Comprehension-first.
No new ontologies.