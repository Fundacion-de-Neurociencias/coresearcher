# Round 0: exploratory results (formalizer and Lean cross-check)

**Date:** 2026-10-15. **Status:** exploratory. These runs used the seed dataset before the scientists' review and
before the freeze required by [FORMALIZER_BENCH_PROTOCOL.md](FORMALIZER_BENCH_PROTOCOL.md), so they are not the
pre-registered round. They show whether the pipeline works and how far current local models are from the target.

**Machine:** the Fundación's Mac Studio (Apple Silicon, 64 GB), through Ollama, reached over an SSH tunnel. The Lenovo
Legion was not reachable from the development laptop. No text left the Fundación's network.

## 1. Formalizer benchmark (prompt `formalizer-v1`, variable schema given)

| Metric | Laya (`llama3.2:3b`) | `qwen2.5:14b-instruct-q4_K_M` |
| --- | --- | --- |
| Parse rate | 0.30 | 0.80 |
| Status counts | 6 parsed, 7 invalid, 4 schema mismatch, 3 no JSON | 16 parsed, 4 invalid |
| Verdict agreement with gold (evaluated outputs) | 0.30 | 0.81 |
| Spurious defects (testable hypothesis turned untestable or contradictory) | 6 | 1 |
| Missed defects (defective hypothesis repaired) | 1 | 2 |
| **Equivalent to gold (primary)** | **0.15** | **0.50** |

Observations:

- Laya at 3B parameters is not usable as a formalizer: most outputs are malformed, and those that parse are often
  weaker than the prose (claims dropped, so 7 of 10 come out unfalsifiable). One item timed out (300 s) and was not
  retried.
- The 14B model reaches 0.50 equivalence, below the 0.80 threshold that protocol section 6 sets for leaving draft
  mode. Formalizer output therefore stays a draft that the researcher confirms.
- 3 of its 4 invalid outputs wrote JSON-style `true`/`false` inside predicates, where the language uses `True`/`False`.
  This is a candidate change for `formalizer-v2`: state the capitalisation in the prompt, or accept the lowercase
  forms in the predicate language. It must be decided **before** the freeze and then measured on the frozen dataset;
  changing it now and re-running on the same items would overfit.
- Its other errors are the instructive kind: an implication written with `implies` (F01), a VACUOUS hypothesis
  formalized without its impossible premise pair (F05), a self-contradiction lost by turning an assumption into scope
  (F20), and a dose threshold turned into a contradiction (F02).
- The guardrails worked in both runs: no malformed or unsafe output reached the evaluator; every failure is reported
  with its reason.

Raw outputs and per-item reports are kept on the development machine (`private/runs/`) and can be re-scored with
`formalizer_bench.py score`.

## 2. Lean kernel cross-check of z3 entailments (`formal_lean_check.py`)

Lean 4 v4.35.0 with Mathlib, default tactic of `formal_lean.py`.

| Check | z3 | Lean kernel |
| --- | --- | --- |
| C01, C03, C06 | entailed | PROVED |
| C05, C07, C09, C10 | entailed | NOT_PROVED (tactic: disjunctions and case splits) |
| C02, C04, C08 | not entailed | NOT_PROVED |

- **No soundness discrepancy:** Lean proved nothing that z3 rejected.
- 3 of 7 z3 entailments are now kernel-checked. The 4 others failed in the tactic (`not a positivity goal` after
  `linarith` and `nlinarith`), not in elaboration, so the exported theorems are well formed. A stronger default tactic
  (splitting conjunctions, case analysis on disjunctive and finite-domain premises) is the next improvement.

## 3. Not run

- **Lean oracle for the openai/math pilot (71 challenges):** Comparator sandboxes with `landrun`, which needs Linux.
  It waits for the Legion or another Linux host.
- **Concordance LLM arm:** needs the 20 frozen pilot tasks, which the scientists write.
