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

## 2b. After round 0: shape-directed default tactic (2026-10-15)

The fixed default tactic was replaced by a proof script built from the shape of the consequence
(`default_tactic` in `formal_lean.py`): premises are split into cases (`casesm*`), conjunctions are proved part by
part, negations (`¬`, `≠`, `not in`) are introduced and refuted, and disjunctions are tried side by side, by
contradiction, and, for a disjunction of equalities, through a vanishing product
(`(a₁ - b₁) * … * (aₙ - bₙ) = 0`). Six checks (C11–C16) were added to cover more goal shapes.

Run on Lean 4 v4.35.0 with Mathlib at its `v4.35.0` tag, on a Linux cloud container. The Mathlib cache was not
reachable there, so Mathlib was built from source for the modules the script uses, and each file imported those
modules instead of the whole of `Mathlib`. The same tactics are in `import Mathlib`; the Legion run (runbook,
job 4) confirms with the full import.

| Check | z3 | Round 0 tactic | New default tactic |
| --- | --- | --- | --- |
| C01, C03, C06 | entailed | PROVED | PROVED |
| C05, C07, C09, C10 | entailed | NOT_PROVED | PROVED |
| C11 (3-value domain), C12 (cubic roots), C13 (`≠`), C14 (`not in`), C15 (chained bounds) | entailed | not run | PROVED |
| C02, C04, C08, C16 | not entailed | NOT_PROVED | NOT_PROVED |

- **12 of 12 z3 entailments are kernel-checked**, and no theorem z3 rejected was proved (no soundness discrepancy).
  The round 0 tactic, re-run in the same environment, reproduced the round 0 table exactly (3 of 7).
- Three Lean pitfalls found while doing this, now handled in the generator: `norm_num` can succeed without closing
  the goal (it is now followed by `done`); a failure inside a nested `by` term is logged, not raised, so an
  enclosing `first` does not try its next alternative (the script uses `refine … ?_` instead); and `push_neg` is
  deprecated in Mathlib for v4.35 (the script uses `simp only [not_or, not_and_or, not_le, not_lt]`).
- The checks are still small, constructed cases. Passing them shows that the export and the tactic work on these
  shapes, not that every z3 entailment of a real hypothesis will be kernel-checked.

## 3. Not run

- **Lean oracle for the openai/math pilot (71 challenges):** Comparator sandboxes with `landrun`, which needs Linux.
  It waits for the Legion. The setup was prepared and checked on a Linux container: `prepare` on the real pinned
  checkout (71 challenges, no problems), the three tools built with the project toolchain, and Comparator with the
  real `landrun` accepting and rejecting its own test examples as a non-root user. See section 5 of
  [LEAN_ORACLE_PROTOCOL.md](LEAN_ORACLE_PROTOCOL.md).
- **Concordance LLM arm:** needs the 20 frozen pilot tasks, which the scientists write.
