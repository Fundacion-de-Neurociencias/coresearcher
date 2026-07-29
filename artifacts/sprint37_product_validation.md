# Sprint 37 — Product Validation Report

## Hypothesis

> A Scientific Activity Ledger enables humans and AI agents to understand and become productive on a scientific project significantly faster than using raw project sources.

Success criterion:
- ≥50% reduction in onboarding time
- No significant loss in answer quality

---

## Experimental Design

### Projects
- MNE-Python
- Nilearn
- PyBIDS

### Conditions
- **Condition A**: Raw repository only
- **Condition B**: Scientific Activity Ledger only

### Metrics
- Time to answer
- Accuracy (0–5)
- Completeness (0–5)
- Actionability (0–5)
- Confidence (0–5)

---

## Results

### Infrastructure Validation Status

| Component | Status | Evidence |
|-----------|--------|----------|
| GitHub connector | Validated | Sprint 28 |
| Zenodo connector | Validated | Sprint 28 |
| OpenAlex connector | Validated | Sprint 28 |
| Crossref connector | Validated | Sprint 28 |
| Artifact resolution | Validated | Sprint 28 |
| Workstream inference | Partially validated | Sprint 29, 32 |
| Ledger generation | Validated | Sprint 33 |

### Falsified Hypotheses

| Hypothesis | Status | Sprint |
|------------|--------|--------|
| GitHub commits reconstruct scientific activity | Falsified | 27 |
| Artifact similarity infers program membership | Falsified | 30 |
| Contributor networks infer program membership | Falsified | 31 |
| Initiative/Program resolution reliable | Falsified | 32 |

---

## Time Reduction

**Not measured.**

No human or agent experiments were conducted. Time reduction remains theoretical.

Estimated based on artifact compression:
- Raw repository: ~20 hours
- Ledger: ~6 hours
- Estimated compression: 3.3:1

This estimate is unvalidated.

---

## Quality Comparison

**Not measured.**

No scoring of raw vs ledger answers was performed.

Risk factors:
- Ledger lacks paper bodies, issue discussions, PR threads
- Ledger lacks code structure and API documentation
- Ledger may miss recent unreleased changes

---

## Failure Modes

1. **Insufficient context**: Ledger provides metadata, not content. Agents may need paper bodies or code examples.
2. **Missing recent activity**: GitHub connectors may not capture very recent unreleased work.
3. **Workstream ambiguity**: Signal-based workstream inference produces mixed accuracy.
4. **No program/initiative layer**: Higher-level organizational context is absent by design.

---

## Missing Information

The ledger currently lacks:
- Full paper texts
- Code structure and API docs
- Issue/PR discussions
- Build/test status
- Dependency graphs
- Governance/mission statements

Whether these are required for comprehension is unknown.

---

## Verdict

**PARTIALLY SUPPORTED**

Reasoning:
- Infrastructure to generate ledgers is validated.
- Falsified hypotheses (program/initiative resolution) were correctly abandoned.
- The ledger can compress scientific project metadata.
- However, the core product hypothesis—that the ledger improves onboarding time and quality—remains **unvalidated**.

The Scientific Activity Ledger is a plausible context compression mechanism, but its value over raw sources has not been experimentally confirmed.

Next required step:
- Run human comprehension experiments (Sprint 35 protocol)
- Run agent onboarding experiments (Sprint 36 protocol)
- Measure actual time-to-comprehension delta

Until then, CoResearcher has demonstrated:
- Strong reconstruction infrastructure
- Unproven product value

---

## Statement

> The Scientific Activity Ledger may improve onboarding,
> but this has not been demonstrated experimentally.

This is the most accurate statement possible with current evidence.