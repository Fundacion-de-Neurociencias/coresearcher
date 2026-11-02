# openai/math time-travel benchmark: unbounded integer variables (ADR-090), results

Protocol: [`OPENAI_MATH_UNBOUNDED_PROTOCOL.md`](OPENAI_MATH_UNBOUNDED_PROTOCOL.md), SHA-256 `3481e27d…`. It was frozen at
2026-11-02T05:04:42Z, before any context was re-encoded.

Input: [`openai_math_unbounded_contexts.json`](openai_math_unbounded_contexts.json) (`e024578e…`, frozen 05:07:06). It
holds the constrained contexts with blind re-encoded variables and assumptions. The registry is the case-scoped one.
Results are in [`openai_math_unbounded_results.json`](openai_math_unbounded_results.json). The implementation is
[ADR-090](../../decisions/ADR-DISCOVERY-090-UNBOUNDED-INTEGERS.md).

## 1. Question and answer

The case-scoped re-measure attributed its remaining "hypothesis not discharged" findings at defect locations to
representative ranges. Citing contexts had given unbounded integers a range 0..12, so counterexamples such as n = 0
came from the range, not from the passage.

**Answer.** The diagnosis was only half right.

- **The representative ranges are gone.** With unbounded integers, every counterexample is a value the passage's own
  stated conditions allow.
- **The findings stay.**
  - At the trace-lemma uses of the two K3 withdrawals, the cited hypothesis n ≥ 3 is still not discharged. The
    counterexample is n = 2 where the passage states "n even, 2n > 2", and n = 0 where it states only "n even".
  - Elsewhere, two hypotheses that a range starting at 0 had discharged by accident (a > 0 and b > 0; a ≥ 0) are now
    not discharged. The passage never states that λ or a is positive.
- **What the findings actually measure.** The citing passages, read within their 55-line window, do not state the
  bounds the cited results need. Those bounds are probably fixed elsewhere in each manuscript, as standing
  assumptions. The findings are therefore decided relative to the window, and they are not defects.
- **Decided detections that reflect a defect: 1/17** (0.01–0.27), unchanged.

`CHAIN_SEAMS` flags, by run:

| Run | At defect locations | Off-location, pre-fix | Corrected versions | FINDINGS, all 69 uses |
| --- | --- | --- | --- | --- |
| Case-scoped (ADR-089) | 7/28 | 3/17 | 2/24 | 12 |
| Unbounded (ADR-090, this protocol) | 7/28 | 4/17 | 4/24 | 15 |

Per-defect verdicts are unchanged. The three withdrawals are still protocol HITs, adjudicated as not the defect:

- the `homotopy_direction` input artefact;
- hypotheses decided relative to the passage window.

One context is still INVALID_INPUT, and the chain refuses it (M8).

## 2. What this teaches

1. **The integer back end works as intended.** Parity and bounds are decided over the integers, and the
   counterexamples are exact (n = 2, n = 0). Tests pin this.
2. **The limit is now the context, not the arithmetic.** A citing context made of one passage cannot carry a
   manuscript's standing assumptions:
   - "throughout, n = 2k with k ≥ 2";
   - "λ > 0 is the height gap".

   A cited hypothesis that depends on them can never be discharged from the window. An encoding that silently filled
   the gap with a range was hiding it, which is why the honest encoding raises the count.
3. **The next capability is standing assumptions.** A manuscript-level context of conventions and assumptions,
   extracted from the setup sections and inherited by every citing context of the manuscript. It must be extracted
   blind, like everything else here. A citing context would then be the passage plus the standing context.

## 3. Next gaps, re-ranked

1. **Standing assumptions per manuscript**, inherited by every citation of that manuscript.
2. **Refusing a case recorded as a field** (unchanged: the `homotopy_direction` artefact at the withdrawals).
3. **A local formal check of the orientation computation** in the citing construction (unchanged: the route to the
   withdrawals).
4. **A chain input kind for a citation inside a proof**, and **a premise-status feed** (unchanged).

## 4. Deviations

None. The re-encoding replaced only `variables` and `assumptions`. Conventions and cases are the frozen constrained
ones. Regression expectations are now version 8 (`unbounded/*` observations).
