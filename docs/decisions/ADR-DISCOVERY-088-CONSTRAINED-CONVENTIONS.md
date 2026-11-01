# ADR-DISCOVERY-088: Constrained parameters, cases and partial matches in typed conventions

**Status:** Accepted
**Date:** 2026-11-01

**Modules:**
- [`python/discovery/typed_conventions.py`](../../python/discovery/typed_conventions.py)
- [`python/discovery/cited_registry.py`](../../python/discovery/cited_registry.py)

**Builds on:**
- ADR-DISCOVERY-087: typed conventions;
- ADR-DISCOVERY-083: the cited-results registry;
- ADR-DISCOVERY-068: a non-answer never becomes an answer.

**Measured by:** [`OPENAI_MATH_CONSTRAINED_RESULTS.md`](../reference/benchmarks/OPENAI_MATH_CONSTRAINED_RESULTS.md).

## Context

The typed re-measure (ADR-087) left two kinds of artefacts at the openai/math withdrawals:

- **A sign compared outside the citing domain.** At n = 3, while the passage works with n = 2k. Typed parameters had
  ranges but no conditions.
- **A field that recorded which case of a lemma a citation used.** A case is a property of the use, not a convention,
  so comparing it as a field gave a meaningless MISMATCH.

## Decision

1. **`where`.**
   - A typed convention may carry conditions on its parameters, for example `n % 2 == 0` or `k >= 2`.
   - Conditions are parsed into a restricted AST: integer arithmetic, comparisons, and `and`, `or`, `not`.
   - A sign quantity is compared only on the points that satisfy both sides' conditions, inside the intersection of
     both sides' ranges.
   - A shared domain with no points is UNCOMPARED.
2. **`cases` and `case`.**
   - The cited side lists the cases its statement covers.
   - The citing side names the case it uses.
   - A case the cited result does not cover is a decided MISMATCH ("the cited result does not cover this case"). A
     covered case is a MATCH.
   - A case named against a cited side that lists none is unspecified.
3. **`PARTIAL`.**
   - **When.** The typed items compared agree, but an item typed on one side is silent on the other.
   - **What it is.** A non-verdict. The citation check is INCOMPLETE, and each silent item is listed in `open`. It is
     no longer a MATCH.
   - **Why.** Under M8, a partial comparison must not pass as a full one: the silent item may be exactly where the
     conventions differ.

## Consequences

- **The parity artefact is gone.** On the constrained re-measure, every imported sign at the three withdrawals is a
  decided MATCH on the passage's own domain. The signs taken from the cited lemmas agree with the citing papers.
- **PARTIAL points at the right question, but does not answer it.** At the uses of the trace-sign lemma it leaves open
  which branch comes first and against which orientation the sign is read. The withdrawal notices put the error in
  exactly that place. PARTIAL is as frequent elsewhere, so it is a pointer, not a detection.
- **Separating cases from fields relies on typists following instructions.** One did not. The next step is to refuse,
  at registration, a field named like a declared case or a field value that encodes a condition. Cases should also
  select which hypotheses are checked.
- **PARTIAL was added after the pre-registered run.** It changes no per-defect verdict, alarm count or seams outcome
  of that run. It is reported apart in the results.
