# ADR-DISCOVERY-064: Self-consistency gate on the formalizer

**Status:** Accepted
**Date:** 2026-10-15
**Module:** [`python/discovery/formalization_gate.py`](../../python/discovery/formalization_gate.py)
**API:** `POST /api/hypotheses/formalize` (new `samples` field, new `formalization_gate` block),
`POST /api/discovery/workbench/launch` (new `formalizer_samples` field)
**Results:** [FORMALIZER_GATE_RESULTS.md](../reference/benchmarks/FORMALIZER_GATE_RESULTS.md)

## Context

The formalizer (ADR-DISCOVERY-061) is the weakest link of the formal pipeline. In round 0 it produced an object
logically equivalent to the gold formalization for 0.15 of the items with Laya (`llama3.2:3b`) and 0.50 with
`qwen2.5:14b-instruct-q4_K_M` ([round 0](../reference/benchmarks/ROUND0_EXPLORATORY_RESULTS.md)). Every later verdict
(z3, enumeration, Lean) is exact about the object and says nothing about whether the object is what the prose meant.
A wrong translation that parses is therefore the most dangerous failure: it is judged with full rigour and looks
verified.

Sakana AI's Agentic Scientist work found that checking each stage of a pipeline matters as much as the base model. The
formalization stage had no check of its own beyond parsing.

## Decision

1. **Sample, then compare exactly.** For each prose hypothesis the formalizer draws N independent formalizations.
   Sample 0 uses the frozen decoding (temperature 0, seed 0), so N = 1 reproduces the ungated formalizer exactly;
   samples 1, 2, ... use a positive temperature (default 0.7) and seeds 1, 2, ... Optionally the samples cycle over
   several models served at the same endpoint (`FORMALIZER_GATE_MODELS`). The prompt stays `formalizer-v1`:
   paraphrased prompts would change the frozen prompt that the benchmark pre-registers.
2. **The verifier decides agreement, not a model.** Two samples are in the same class only when
   `HypothesisEvaluator.compare` proves them `EQUIVALENT` (exhaustive enumeration on finite variables, z3 when a
   variable is continuous, ADR-DISCOVERY-060). Pairs over different variables, or pairs the solver cannot decide, are
   `UNDECIDED` and never count as agreement. No language model judges equivalence (ADR-DISCOVERY-002).
3. **Strict majority over all samples drawn.** Samples that fail to parse, violate the variable schema or are rejected
   by the evaluator count in N and join no class. The status is:
   - `CONSISTENT`: one class holds more than N/2 samples and every pair inside it was proved equivalent. Its
     lowest-indexed member is accepted (sample 0 when it is in the majority).
   - `FORMALIZATION_AMBIGUOUS`: no such class. Nothing is accepted.
   - `FORMALIZATION_FAILED`: no sample produced a valid object.
   - `SINGLE_SAMPLE`: N = 1 and the sample parsed. No evidence either way; accepted as before the gate.
4. **Nothing ambiguous reaches the court.** The API evaluates and compares with rivals only a formalization that passes.
   On `FORMALIZATION_AMBIGUOUS` the response has `status: FORMALIZATION_AMBIGUOUS`, an empty `formal_hypothesis`, no
   `evaluation` and no `comparisons`; `formalization_gate.classes` lists the rival readings with their content
   verdicts and `pairwise` lists the exact relation between every pair, so the researcher sees where the readings
   differ. The gate has no `VERIFIED` status, and an accepted formalization stays `draft: true`: agreement between
   samples shows a stable reading, not that the reading is the prose's meaning. This follows the false-verification
   fixes of PR #1.
5. **Default N = 5 in the API**, from the request (`samples`, 1 to 7), else `FORMALIZER_SAMPLES`, else 5. The
   ablation below chose 5 over 3: fewer false acceptances at the same coverage.
6. **No back-translation signal.** A formal-to-prose round trip judged by a model would be an LLM verdict on the
   decisive question. It was left out; if added later it may only annotate, never change the gate status.

## Consequences

- The cost of a formalization grows linearly with N (N model calls plus at most N(N-1)/2 exact comparisons, which
  are cheap next to the model calls on the benchmark's state spaces).
- Some correct formalizations are blocked when the other samples disagree. The ablation measures this cost
  (`baseline_correct_blocked`).
- Consistency cannot catch a wrong reading that the model produces reliably. Errors that are systematic in the model
  pass the gate; only errors that vary between samples are caught. Equivalence to a human gold formalization remains
  the measure of fidelity.
- `formalizer_bench.py` gains `run --samples N` and a `gate` command that replays stored samples offline for any N up
  to the samples drawn, per model and mixed across models.

## Results

On the 20-item seed dataset, Mac Studio, 5 samples per item ([details](../reference/benchmarks/FORMALIZER_GATE_RESULTS.md)):

| Condition | Coverage | Ambiguous | Equivalent among accepted | Equivalent over all items | False acceptances |
| --- | --- | --- | --- | --- | --- |
| qwen2.5:14b, gate off (round 0) | 0.80 | 0.00 | 0.625 | 0.50 | 6 |
| qwen2.5:14b, N=5 | 0.75 | 0.20 | 0.733 | 0.55 | 4 |
| Laya, gate off (round 0) | 0.30 | 0.00 | 0.50 | 0.15 | 3 |
| Laya, N=5 | 0.10 | 0.35 | 1.00 | 0.10 | 0 |
| Both models mixed, N=5 | 0.50 | 0.50 | 0.80 | 0.40 | 2 |

The gate removed false acceptances (accepted but not equivalent to gold) in every condition and introduced none; with
n = 20 no difference is significant (exact McNemar p >= 0.125). Errors the model makes reliably pass the gate, as
expected. Formalizer output stays a draft.

## Limits

- The benchmark is the 20-item seed dataset, not yet frozen or reviewed by the Fundación's scientists, and the
  results are exploratory in the sense of round 0.
- Without a variable schema, samples rarely share variable names, so they are rarely comparable and the gate mostly
  answers `FORMALIZATION_AMBIGUOUS`. This is conservative by design.
