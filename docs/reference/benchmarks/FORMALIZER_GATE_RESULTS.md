# Formalizer self-consistency gate: results (round 0 dataset)

**Date:** 2026-10-15. **Status:** exploratory, on the same unfrozen 20-item seed dataset as
[round 0](ROUND0_EXPLORATORY_RESULTS.md). **Decision record:**
[ADR-DISCOVERY-063](../../decisions/ADR-DISCOVERY-063-FORMALIZER-SELF-CONSISTENCY-GATE.md). **Generated tables and
per-item rows:** [FORMALIZER_GATE_REPORT.md](FORMALIZER_GATE_REPORT.md).

## 1. Setup

- **Machine:** the Fundación's Mac Studio through Ollama, over an SSH tunnel. No text left the Fundación's network.
- **Models:** Laya (`llama3.2:3b`) and `qwen2.5:14b-instruct-q4_K_M`, prompt `formalizer-v1` (SHA-256
  `daa81130...`), variable schema given, dataset SHA-256 `a506a8cc...` (both unchanged from round 0).
- **Samples:** 5 per item per model. Sample 0 uses the frozen decoding (temperature 0, seed 0); samples 1 to 4 use
  temperature 0.7 and seeds 1 to 4. **Sample 0 reproduced round 0 exactly: 20 of 20 outputs identical for both
  models**, so the N = 1 rows below are the round 0 baseline.
- **Conditions:** each model with N = 1 (gate off), 3 and 5 (the first N samples), and both models mixed (samples
  alternate qwen, Laya, qwen, ...). All conditions are replayed offline from the same stored outputs with
  `formalizer_bench.py gate`.
- **Transport:** the tunnel dropped once during the Laya run; the samples lost to connection errors were drawn again
  with `run --resume`. Two Laya samples (F13 #0 and #4) timed out at 120 s and stay recorded as failures, as the one
  timeout of round 0 was.

Equivalence to gold is decided by `HypothesisEvaluator.compare` (exact). The gate itself never sees the gold.

## 2. Results

| Condition | Accepted (coverage) | Ambiguous | Failed | Equivalent among accepted | Equivalent over all 20 | False acceptances | Spurious defects accepted |
| --- | --- | --- | --- | --- | --- | --- | --- |
| qwen, gate off (N=1) | 16 (0.80) | 0.00 | 0.20 | 0.625 | **0.50** | 6 | 1 |
| qwen N=3 | 15 (0.75) | 0.10 | 0.15 | 0.667 | 0.50 | 5 | 1 |
| qwen N=5 | 15 (0.75) | 0.20 | 0.05 | **0.733** | **0.55** | **4** | 0 |
| Laya, gate off (N=1) | 6 (0.30) | 0.00 | 0.70 | 0.500 | **0.15** | 3 | 3 |
| Laya N=3 | 3 (0.15) | 0.25 | 0.60 | 0.667 | 0.10 | 1 | 1 |
| Laya N=5 | 2 (0.10) | 0.35 | 0.55 | 1.000 | 0.10 | **0** | 0 |
| mixed N=3 | 13 (0.65) | 0.25 | 0.10 | 0.692 | 0.45 | 4 | 1 |
| mixed N=5 | 10 (0.50) | 0.50 | 0.00 | **0.800** | 0.40 | **2** | 0 |

A **false acceptance** is an item whose accepted formalization is not equivalent to the gold: the failure that
reaches the court looking verified. Paired with the gate-off run of the same model (the first model for mixed), the
gate removed false acceptances and **introduced none** in every condition:

| Condition | False acceptances removed / introduced | Exact McNemar p |
| --- | --- | --- |
| qwen N=3 / N=5 | 1/0, 2/0 | 1.0, 0.5 |
| Laya N=3 / N=5 | 2/0, 3/0 | 0.5, 0.25 |
| mixed N=3 / N=5 (vs qwen N=1) | 2/0, 4/0 | 0.5, 0.125 |

## 3. Answers

**Does gating raise equivalence among accepted items?** Yes, in every condition: qwen 0.625 to 0.733 (N=5), Laya
0.50 to 1.00 (but on 2 accepted items), mixed 0.80 (N=5). With n = 20 none of the differences is significant
(protocol section 6); they are descriptive.

**Against the round 0 baseline as stated (equivalence over all 20 items: 0.15 Laya, 0.50 qwen):** qwen N=5 reaches
0.55, because the majority reading rescued two items whose frozen sample was wrong (F05, F11) and blocked one whose
frozen sample was right (F15). Laya drops to 0.10 and mixed to 0.40: the gate trades coverage for safety. It does not
make a model translate better; it withholds translations the model is not stable on.

**What fraction is flagged ambiguous?** qwen 0.10 (N=3) and 0.20 (N=5); Laya 0.25 and 0.35; mixed 0.25 and 0.50.
Failed (no valid sample at all) falls with N because one valid sample out of five is enough to avoid it.

**What the gate cannot catch.** Errors the model makes reliably pass it. With qwen alone at N=5 the four remaining
false acceptances are F06 (the same `WEAKER` reading in 5 of 5 samples) and F08, F12, F20 (`INCOMPARABLE`, majority
classes of 3). Mixing models catches F08 and F20, because Laya's samples do not join the qwen reading there, at the cost of
half the coverage. Spurious defects among accepted items (a testable hypothesis turned untestable or contradictory) go to 0 at
N=5 for every condition.

**Cost.** The correct frozen output was blocked on 1 of 10 items for qwen (F15, three distinct readings in five
samples), 1 of 3 for Laya and 2 of 10 for mixed N=5.

## 4. Decisions taken from these numbers

- The API default is **N = 5** with a single model: it removes more false acceptances than N = 3 for two more model
  calls (median 2.8 s per qwen call on the Mac Studio, about 16 s per hypothesis at N = 5), and keeps 0.75 coverage. Mixing models is available
  (`FORMALIZER_GATE_MODELS`) for callers who prefer fewer false acceptances to coverage.
- Formalizer output stays a **draft**. No condition reaches the protocol's bar (equivalence over all items >= 0.80
  with no spurious defects); the best equivalence among accepted items is 0.80, on half of the items.

## 5. Limits

- 20 items, not yet reviewed or frozen by the scientists; one temperature (0.7), not tuned. Re-run on the frozen
  dataset before citing these numbers as anything but exploratory.
- Raw outputs are kept on the development machine (`private/runs/gate/`) and can be re-scored with
  `formalizer_bench.py gate`.
