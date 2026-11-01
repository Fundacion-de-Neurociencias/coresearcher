# ADR-DISCOVERY-089: Case-scoped hypotheses and conditional atoms

**Status:** Accepted
**Date:** 2026-11-02

**Modules:**
- [`python/discovery/cited_registry.py`](../../python/discovery/cited_registry.py) (`CitedHypothesis.case`,
  `cases_used`, `check_hypothesis`)
- [`python/discovery/typed_conventions.py`](../../python/discovery/typed_conventions.py) (`is_conditional`)
- [`api/schemas.py`](../../api/schemas.py) (registry hypotheses accept `case`)

**Builds on:** ADR-DISCOVERY-083, 087 and 088.

**Measured by:** [`OPENAI_MATH_CASES_RESULTS.md`](../reference/benchmarks/OPENAI_MATH_CASES_RESULTS.md).

## Context

The constrained re-measure (ADR-088) showed two remaining kinds of false findings.

- **Hypotheses from another case.** A cited proposition with two parts carried the hypothesis of part (1). Citations
  that state they use part (2) were held to it.
- **Conditions written as atoms.** A typed field value such as "Z if n even and orientable, else Z/2" was compared
  with the value of one branch, as if both were atoms.

## Decision

1. **Case-scoped hypotheses.**
   - A cited hypothesis may carry `case: {name: [cases]}`.
   - When the citing context names a case of that name (through a typed convention's `case`) that is not in the
     list, the hypothesis is NOT_APPLICABLE: it is neither a finding nor an open item.
   - When the citing context names no case, the hypothesis is checked as before.
   - A citation check whose only non-discharged hypotheses are NOT_APPLICABLE can be CLEAR. Its ledger obligation can
     be discharged.
2. **Conditional atoms.** A field value that contains a condition word (if, unless, when, otherwise, else, iff) is
   not an atom. If it differs from the other side's value, the item is UNCOMPARED, with the detail "a field value
   encodes a condition; use `where`". It is not a decided MISMATCH.

## Consequences

- **Case scoping.** On the case-scoped re-measure, scoping removed the three other-case findings.
  ([`OPENAI_MATH_CASES_RESULTS.md`](../reference/benchmarks/OPENAI_MATH_CASES_RESULTS.md))
- **Conditional atoms.** The rule removed one decided convention mismatch at a defect location. It was an input
  artefact, not a detection. The rule was written after reading the constrained results, and its effect is reported
  as post hoc.
- **What did not change.** No decided detection was gained or lost: still 1/17.
- **What now dominates the remaining findings.** Representative ranges in citing contexts, and a case recorded as a
  field in one registry input. Those are the next gaps.
- **The lexical part.** Condition words are detected lexically on a structured, typed value. A typist who writes a
  condition without those words still produces an atom. The safe direction is the one taken here: UNCOMPARED is a
  non-verdict.
