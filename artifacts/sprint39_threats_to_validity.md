# Sprint 39B — Threats to Validity

## Purpose

This document audits Sprint 39B by attempting to **refute** its conclusion.
If the evidence survives this scrutiny, it becomes more trustworthy.
If it does not, the conclusion must be revised.

> Source → Observation → Learning → Impact

---

## 1. Internal Validity

### 1.1 Circular ground truth

**Observation:** The `GROUND_TRUTH` dictionary is copied directly into `ledger_observations`.

**Threat:** The ledger is validated against itself. Accuracy of 100% is guaranteed by construction. Every ledger answer comes from the same source that defines "correct."

**Severity:** CRITICAL.

### 1.2 Questions favour the ledger by construction

**Observation:** Each question targets a fact that the ledger stores explicitly. The raw context must search unstructured prose.

**Threat:** The benchmark tests **recall from a lookup table**, not comprehension. Raw API metadata (license, language, topics) exists in the GitHub response but `extract_from_raw` only searches README text.

**Severity:** HIGH.

### 1.3 Raw context is incomplete

**Observation:** Raw context includes GitHub metadata, README, 5 issue titles, 5 PR titles, and Zenodo community JSON (71 chars).

**Threats:** No OpenAlex, no Crossref, no issue/PR bodies, no code, no CONTRIBUTORS file. Zenodo data (71 chars) is insufficient for DOI/contributor questions.

**Severity:** HIGH.

### 1.4 Search algorithm is naive

**Observation:** Raw search matches ground-truth terms in README lines. Terms must appear in the same line with 50% overlap.

**Threat:** For "Denis Engemann", the README may mention "Denis" but not "Engemann." The benchmark reports MISS. A human reading CONTRIBUTORS.md would find it. This conflates "search failure" with "comprehension failure."

**Severity:** MEDIUM.

---

## 2. External Validity

### 2.1 Single-project sample

**Observation:** Only MNE-Python was tested. Nilearn and PyBIDS were excluded.

**Threat:** MNE-Python is unusually well-documented (20+ contributors, multiple DOIs, active Zenodo). Results may not generalise to smaller or less documented projects.

**Severity:** HIGH.

### 2.2 No small or inactive projects

**Observation:** All three candidate projects are large, well-funded, multi-institutional.

**Threat:** The ledger's advantage may diminish or reverse for projects with 1-2 contributors, no DOIs, or no Zenodo deposits.

**Severity:** MEDIUM.

### 2.3 No independent ground truth

**Observation:** Ground truth was authored by the same entity that built the experiment.

**Threat:** No evidence that answers are correct, complete, or unbiased. No domain expert review.

**Severity:** HIGH.

---

## 3. Construct Validity

### 3.1 Measures retrieval, not comprehension

**Observation:** The benchmark measures time to find a string match vs time to look up a dict key.

- Claimed construct: "comprehension cost"
- Measured construct: "information retrieval time from different data structures"

**Evidence:** Raw average: 0.000179s. Ledger average: ~0.000000s. Human comprehension takes seconds to minutes. LLM comprehension takes seconds.

**Severity:** CRITICAL. The experiment does not measure what it claims.

### 3.2 Ledger contains answers, not evidence

**Observation:** Ledger entries are final answers ("EEG/MEG analysis and source localization") rather than evidence statements ("README states MNE-Python is for EEG/MEG analysis").

**Threat:** This is equivalent to reading the answer key instead of the textbook. It validates pre-written answers, not comprehension enablement.

**Severity:** CRITICAL.

### 3.3 896x ratio is a measurement artifact

**Observation:** compression = 0.000179 / 0.000000 ≈ 896x.

**Threat:** Ledger time (dict lookup) is near zero. Any non-zero raw time produces an arbitrarily large ratio. Realistic human reading: ~10x (20 min raw vs 2 min ledger), not 896x.

**Severity:** HIGH.

---

## 4. Conclusion Validity

### 4.1 No statistical rigour

**Observation:** 20 questions, 1 project, 1 trial. No confidence intervals or significance tests possible.

**Severity:** MEDIUM. Acceptable for a pilot but insufficient for validation.

### 4.2 Hypothesis not operationally defined

**Observation:** "Comprehension cost" has no units, protocol, or threshold. Success criteria (2x time, ledger >= raw accuracy) are arbitrary.

**Severity:** MEDIUM.

---

## 5. Corrected Claims

### Supported by evidence

> In this benchmark, a pre-computed lookup table of 20 curated answers provides faster and more accurate information retrieval than a naive string search through MNE-Python's README and limited API metadata.

### NOT supported by evidence

> The Scientific Activity Ledger reduces comprehension cost for humans or agents.

> The ledger generalises across scientific projects.

> A 896x compression ratio is achievable in realistic use.

> The ledger enables understanding rather than recall.

---

## 6. Recommendations

1. **Decouple ground truth from ledger** — use domain experts or published documentation
2. **Test generalisation** — run on Nilearn and PyBIDS with independent ground truth
3. **Measure realistic time scales** — use LLM-based agents or human reading benchmarks
4. **Include synthesis questions** — require combining multiple observations
5. **Define "comprehension cost" operationally** before running the experiment

---

## Appendix: Evidence sources

| Evidence | Source | Date |
|----------|--------|------|
| Ground truth | `python/run_sprint39_execution.py` lines 32-53 | 2026-07-18 |
| Ledger construction | `python/run_sprint39_execution.py` lines 109-113 | 2026-07-18 |
| Raw context types | `python/run_sprint39_execution.py` lines 56-107 | 2026-07-18 |
| Search algorithm | `python/run_sprint39_execution.py` lines 117-158 | 2026-07-18 |
| Questions | `artifacts/sprint39_questions.json` lines 7-26 | 2026-07-18 |
| Results | `artifacts/sprint39_execution_results.csv` | 2026-07-18 |