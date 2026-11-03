# Formalizer v2: pre-registered measurement protocol

**Frozen:** 2026-11-02, before any formalizer-v2 output was produced. **ADR:** ADR-DISCOVERY-093.

## Question

Does formalizer v2 translate prose hypotheses into formal objects equivalent to the gold formalizations more often
than v1, on the same models? v2 adds translation rules, worked examples, JSON mode, surface-syntax repair and one
self-repair round.

## Frozen inputs

| Input | SHA-256 |
| --- | --- |
| `formalizer_dataset.json` (21 items, round 0) | `76d10aeda543b74372583318bb5384162b40552b4f744b35870ed49bcb5c7b4d` |
| `formalizer_dataset_heldout_v2.json` (12 items, written before any v2 output) | `6f0f06e4507dfa73c313f69d693ef80368babf1fa1317bb656116e71ebfc6008` |
| v2 prompt (`prompt_sha256_v2()`, rules and examples) | `cb6d3613672c7eba8efcfffe2d6dc29bd8bdd4155d2fc53eb26b8a4a9c47da5e` |

The v1 prompt is unchanged (round-0 fingerprint).

## Procedure

- **Models.** Every model served by the Foundation's local Ollama endpoint at freeze time: `llama3.2:3b`,
  `qwen2.5:14b-instruct-q4_K_M`, `carbon-x:14b` and `qwen2.5-coder:32b`.
- **Runs.** `formalizer_bench.py run --pipeline v1|v2` on both datasets, with the variable schema given (as in round
  0), sample 0 only (temperature 0, seed 0), then `score`.
- **Primary metric.** `equivalent_to_gold_rate`: the share of items whose formal object is EQUIVALENT to the gold
  one, decided by the exact evaluator (enumeration or z3). The denominator is every item. A transport error, an
  unparseable output or a timeout counts as not equivalent.
- **Secondary metrics.** Status counts (PARSED, INVALID, NO_JSON, SCHEMA_MISMATCH), verdict agreement with gold, and
  self-repair use.
- **Decision rule, fixed in advance.** v2 becomes the default path of `/api/hypotheses/formalize` and of the gate
  only if, on the held-out set, its equivalence rate is at least v1's for every model and strictly higher for at
  least one. Otherwise v1 stays the default and v2 stays available as an option.
- **Failure categories.** Each non-equivalent v2 output is classified by hand as syntax, role (scope or assumption),
  direction (only-if, monotonicity), strictness, invented or dropped claim, "fixed" text, or other.

## Limitations, stated before the run

- The v2 rules were written after reading the v1 round-0 failures on the 21-item set. Results on that set are
  therefore optimistic. The held-out set is the honest test.
- The held-out items and the v2 prompt have the same author, which can bias phrasing toward the rules.
- With 12 held-out items a one-item difference is about 8 points. Small differences are not evidence.
- The z3 equivalence check is the judge. No language model scores another.
