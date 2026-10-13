# openai/math statement-fidelity pilot: report

Protocol: [OPENAI_MATH_PILOT_PROTOCOL.md](OPENAI_MATH_PILOT_PROTOCOL.md)
Script: [`scripts/benchmarks/openai_math_pilot.py`](../../../scripts/benchmarks/openai_math_pilot.py)
Outputs: [dataset](openai_math_pilot_dataset.json), [results](openai_math_pilot_results.json)

Source material: prose scope notes and Lean statements from
[openai/math](https://github.com/openai/math) at commit `1581d4cb`, licensed under Apache-2.0.

## Provenance

- Protocol SHA-256: `bec987afae1de13a...`, unchanged across both runs.
- CoResearcher code under test: commit `a4b12d5`.
- Sample: 20 families drawn with seed `20261013` from the 242 families that have a Lean scope note.

## Deviation found during verification

The first run contained two implementation defects in the mutation operators. Both made the code
disagree with the protocol, so they were fixed and the pilot was re-run. The protocol was not changed.

1. **M2** also swapped `>` in Lean's `=>` (families 231 and 243), producing invalid mutants that are not
   order-relation changes.
2. **M4** removed the last explicit binder even when it was a variable such as `(x : ℝ)`, not a hypothesis.
   It now removes only binders named `h…`, following Lean convention.

First-run result for S1: sensitivity 8/54, specificity 17/19, AUROC 0.521. Conclusions are identical.

## Results (second run)

**Feasibility**

- Pairs extracted: 19/20. Family 066 failed: its first Comparator link is a supporting-result file with no
  `theorem` (`CartierChartCompactnessSupport.lean`).
- Mutation coverage over the 19 pairs: M1 9, M2 9, M3 10, M4 5, M5 19.
- Criterion "≥ 18 pairs": **met**. Criterion "≥ 3 mutation types on ≥ 15 pairs": **not met** (only M5).

**Detection**

| System | Mutants flagged | Originals passed | AUROC (family bootstrap 95%) | Null-control AUROC |
| --- | --- | --- | --- | --- |
| S1 CoResearcher `SemanticBijectivityAuditor` | 8/52 | 17/19 | 0.524 (0.500–0.561) | 0.524 |
| B0 always-match | 0/52 | 19/19 | 0.500 | 0.500 |
| B1 numeric consistency | 14/52 | 16/19 | 0.553 (0.519–0.588) | 0.522 |

Hypothesis H1 (S1 AUROC lower bound above 0.5): **not met.**

## Interpretation

1. **S1 does not respond to any mutation.** In all 19 families its score is identical for the original and
   for every mutant. Its 8 "flagged mutants" come from two families (238 and 331) where it flags everything,
   original included. These are family-level false alarms, not detections. The null control confirms it:
   permuting labels within families leaves S1's AUROC unchanged.
2. **Cause.** The auditor's extractors only recognise derivative orders, Sobolev spaces, dimensions and a
   few keywords (flux, energy, smooth, compact support). Its Lean pattern fails on statements that contain
   `:` or `=` in the conclusion, and then reads the whole file, so a one-token change does not alter
   the extracted features. This is a scope limitation, as stated in protocol §8.
3. **A trivial baseline is more informative.** B1 changes its score in 3 families, all through M1
   (numeric literal) mutants. Its interval barely clears 0.5, and its own null control drops to 0.522.
4. **The pilot works.** Pairs can be extracted reproducibly from a pinned commit with no manual curation.
   The pipeline is ready to scale.

## What this means for the full benchmark

- In its current form, `SemanticBijectivityAuditor` cannot be evaluated meaningfully on general
  mathematics. Scaling the benchmark up would only confirm a null result.
- Mutation coverage depends heavily on statement shape. M5 (negation) applies everywhere; M4 rarely does.
  The full benchmark needs at least 100 pairs to get ≥ 15 pairs for M1–M3, or more operators.
- Lean/Comparator confirmation of mutants remains to be done, on a Linux machine with the Lean toolchain.

## Status

The pilot meets its main feasibility goal and answers its first question: **the current auditor does not
detect statement-fidelity changes in this sample.** A full benchmark only makes sense after the auditor is
extended beyond its analysis vocabulary, or when an approach based on Lean itself is evaluated.
