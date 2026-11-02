# Formalizer v2: results

**Protocol:** [FORMALIZER_V2_PROTOCOL.md](FORMALIZER_V2_PROTOCOL.md), frozen before any v2 output (SHA-256
`a76fb44a0c61b874818f0c449c716ea64353ff1f6d173f9af6cac82206a109d0`). **ADR:** ADR-DISCOVERY-093.
**Run:** 2026-11-02, the Foundation's local Ollama endpoint, sample 0 (temperature 0, seed 0), variable schema
given. Raw outputs are vendored in `benchmarks/regression/fixtures/formalizer/formalizer_outputs.json` and re-scored
offline by the regression case `formalizer_v2`.

## Primary metric: equivalence to gold (decided by the evaluator)

| Model | v1 round-0 set (21) | v2 round-0 set (21) | v1 held-out (12) | v2 held-out (12) |
| --- | ---: | ---: | ---: | ---: |
| llama3.2:3b | 3 (14%) | 13 (62%) | 2 (17%) | 8 (67%) |
| qwen2.5:14b-instruct | 12 (57%) | 17 (81%) | 8 (67%) | 11 (92%) |
| carbon-x:14b | 10 (48%) | 11 (52%) | 7 (58%) | 11 (92%) |
| qwen2.5-coder:32b | 14 (67%) | 17 (81%) | 11 (92%) | 12 (100%) |

Every failure, including any unparseable output, counts as not equivalent. There were no transport errors.

**Decision rule.** On the held-out set, v2 is at least v1 for every model and strictly higher for all four, so v2 is
now the default path of `/api/hypotheses/formalize`, of the gate (ADR-064) and of the verification chain (ADR-085).
`FORMALIZER_PIPELINE=v1` reproduces round 0.

## Where v2 helps

- **Surface repair** rescues outputs the evaluator used to reject, such as `implies`, `== true` and `&&`. It
  changed 1–6 outputs per run and never changes a valid predicate (tests pin this).
- **The self-repair round** was used 0–5 times per run. It matters most for carbon-x:14b and llama3.2:3b.
- **The translation rules and worked examples** fix most role errors (scope vs assumption), the "never decreases"
  direction and strictness, and stop the model from "fixing" contradictory hypotheses.

## Remaining failures (v2, by category)

- **Direction of "Q whenever P" / "Q if P"**, where the condition comes after the consequence. The model reverses
  the implication: F17 for qwen 14b and qwen-coder 32b, H02 for qwen 14b. The v2 rules state "only if" and
  "if P then Q" but not the inverted word order.
- **Role confusion with definitional equations**, where a stated equation is put in scope or assumptions:
  F21 for every model, F13 for qwen 14b.
- **Fixing an impossible condition**: F20 and F15. The model still turns an impossible combination into a
  satisfiable one in a few cases.
- **Invented variable** (carbon-x, H11): it used `treated` where only `treated_rate` exists. Self-repair did not
  recover it.
- **Small-model errors** (llama3.2:3b): strictness (H04), extra claims (H01, H07) and the iff (H12).

## Honest reading

- The held-out set is small: one item is about 8 points. The direction of the effect is consistent across all four
  models and both sets.
- The v2 rules were written after reading round-0 failures. The round-0 set is therefore an optimistic estimate,
  and the held-out set is the honest one. Same-author bias between the held-out items and the rules remains
  possible.
- A v3 that adds a rule for "Q whenever P" must be measured on a new held-out set, not on this one, which has now
  been seen.
