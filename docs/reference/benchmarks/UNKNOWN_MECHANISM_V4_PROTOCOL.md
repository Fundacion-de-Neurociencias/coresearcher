# Unknown-mechanism benchmark v4: pre-registered protocol

Status: written on 2026-10-18, before any arm was run on the benchmark worlds. Generator settings (noise level and
recovery grid) were calibrated with the oracle arm O only, which knows the true form and measures whether the data
identify the law; no competing arm was run on any benchmark world. The script records this file's SHA-256 with
every raw result, and scoring refuses results produced under a different protocol hash.

## 1. Why a v4

v3 left requirement 2 of the v2 report open: the library contains the forms of five of the six generators, so
library selection chooses among premises it was given. In the terms of Zahavy's position paper
([*LLMs can't jump*](https://proceedings.mlr.press/v306/zahavy26a.html), ICML 2026), it does induction over supplied
hypotheses, not the abductive step of proposing a new premise.

v4 makes every generating law absent from the hypothesis space of the library arm, the ridge arm and the PySR grammar
used in v3. Then it asks two questions:

1. Can any arm still **recover the law**, functionally, over a range wider than the data it saw?
2. Does any arm **extrapolate** better than library selection?

v4 tests a necessary condition for the "jump", not the jump itself: proposing a functional form that is outside the
system's own hypothesis space and that the data then confirm. It does not test the invention of new concepts or
variables (section 8).

## 2. Worlds

100 worlds, `i = 0..99`, seed `41000 + i`. Archetype `i mod 4`, 25 worlds each. Each world has 240 rows.

| Archetype | Law g(X, Z1) | Parameters (uniform) |
| --- | --- | --- |
| LOG_SATURATION | a·log(1 + b·X²) + c·Z1 | a ∈ [1, 3], b ∈ [0.5, 2], c ∈ [0.5, 1.5] |
| FRACTIONAL_POWER | a·X^p + c·Z1 | p ∈ [0.3, 0.7] |
| ABS_KINK | a·\|X − t\| + c·Z1 | t ∈ [1, 2.5] |
| SAWTOOTH | a·frac(X / P) + c·Z1 | P ∈ [0.6, 1.2] |

- **Inputs.** X, Z1, Z2 and 20 background variables B. Z2 and B do not enter any law. Z1, Z2 and B are standard
  normal.
- **Splits.**
  - Discovery: rows 0-59. Validation: rows 60-119. In both, X is uniform on the observed range [0.5, 3].
  - Test: rows 120-239, with X uniform on the extrapolation range [3, 6].
- **Noise.** Gaussian, with standard deviation 5% of the law's standard deviation on the observed rows.
- **Hypothesis spaces.** None of these forms is in the library (v2 section 3). None is expressible exactly with PySR's
  v3 operators (`+ - * / sin cos exp square`), which have no logarithm, fractional power, absolute value or modulo.
- **Null control.** Y is permuted within each world with seed `47000 + i`.
- **Tests.** The unit tests use world indices 1000 and above, which are not part of the benchmark.

## 3. Recovery

The recovery grid has 400 evenly spaced X values on [0.5, 6], crossed with Z1 ∈ {−1, 0, 1}, with Z2 = 0 and B = 0.
It covers the observed and the extrapolation range.

For each arm, the predictor fitted on discovery ∪ validation is evaluated on the grid. The world counts as
**recovered** when at least 95% of grid points lie within 0.1 standard deviations (of the law on the grid) of the
noiseless law.

A share of points is used instead of an RMSE because the sawtooth is discontinuous. A period that is right to one
part in ten thousand still puts a few points on the wrong side of a jump, and those few points would dominate an RMSE.

## 4. Arms

All arms see only the discovery and validation rows until a single evaluation on the test rows.

- **O, oracle form (positive control).** The true form with unknown constants plus an intercept. Constants are fitted
  on discovery ∪ validation by least squares from starts 1.0, 0.5 and 2.0. For SAWTOOTH, the period comes from a grid
  search (0.3 to 2.0 in steps of 0.001, then a 401-point refinement within ±0.002), with the linear coefficients
  solved at each period. O measures what the data allow, not discovery.
- **L, library selection.** v3 arm L, unchanged.
- **R, tuned ridge.** v3 arm R, unchanged.
- **P, symbolic regression.** v3 arm P, unchanged: `pysr==2.7.0` with the v3 configuration, the selection rule and
  the constant refit. The seed is `43000 + i`.
- **E, local language model proposals.**
  - Model `qwen2.5:14b-instruct-q4_K_M` served by Ollama, with the OpenAI-compatible chat API, temperature 0.7.
  - 5 calls per world, with seeds `45000 + 10·i + k` for k = 0..4.
  - The prompt is the fixed text `LLM_SYSTEM` / `LLM_PROMPT` in the script. It contains the 60 discovery rows of
    X, Z1, Z2 and Y (3 decimals) and the largest absolute correlation between a background variable and Y. It asks
    for up to 4 formulas per call, in SymPy syntax, with free constants c0..c5. It does not name any function.
  - Parsing:
    - Only lines of the form `Y = <formula>` are read.
    - Formulas over 200 characters, or containing a name outside a fixed whitelist of elementary SymPy functions,
      X, Z1, Z2 and c0..c5, are dropped.
    - Duplicates are scored once.
  - Selection and refit:
    - Each formula's constants are fitted on discovery (starts 1.0, 0.5 and 2.0).
    - The formula with the highest validation R² is selected; ties go to the shorter formula.
    - Its constants are refitted on discovery ∪ validation.
    - It is then evaluated on test once.
    - If no formula is usable, the arm predicts the mean of discovery ∪ validation.

Arms O, L and R need only numpy and scipy. P (Julia) and E (local model) run on the Lenovo Legion
([runbook](LEGION_RUNBOOK.md), job 6).

## 5. Metrics

- **Test R²** on the extrapolation rows, not clipped at zero. A diverging prediction can give −∞, so means use a floor
  of −10 per world.
- **Recovery.** The number of recovered worlds per arm, with a 95% Wilson interval, overall and per archetype.
- **Extrapolation gain.** Paired `ΔR²(arm − L)` for R, P and E.
- **Uncertainty.** 95% percentile intervals from a paired bootstrap over worlds, 10,000 resamples, seed `20261018`.

## 6. Pre-registered criteria

- **Validity (V).** O's mean test R² is at least 0.9, and O recovers at least 90 of 100 worlds. If V is not met, the
  benchmark does not discriminate and no other criterion is read.
- **Null gate (G).** For each arm, on the null data, the upper bound of the 95% bootstrap interval of the mean test R²
  is at most 0.05.
- **Jump (J), per arm.** The lower bound of the 95% Wilson interval of the recovery rate is above 0.05. Roughly, the
  arm recovers a law it was not given in more than an occasional world.
- **Extrapolation (X), per arm.** The 95% bootstrap interval of the mean `ΔR²(arm − L)` is reported. A lower bound
  above 0 means the arm extrapolates better than library selection.

Expected in advance:

- L and R cannot meet J. Their hypothesis spaces do not contain these forms, and they are controls.
- J for P tests a generic symbolic searcher on forms outside its grammar.
- J for E is the test of the claim that a language model cannot propose the premise.

A criterion that is not met is reported as not met. Thresholds, configurations, prompts and selection rules do not
change after any result is seen.

## 7. Execution

`scripts/benchmarks/run_unknown_mechanism_v4.py`:

- `run --arm O|L|R|P|E [--null]` appends one JSON line per world to
  `docs/reference/benchmarks/unknown_mechanism_v4_raw.jsonl`. It is resumable.
- `score` writes `unknown_mechanism_v4_results.json`. Any arm that has not run is reported as not run.

## 8. Known limitations, stated in advance

- **Textbook forms.** Logarithmic saturation, power laws, kinks and sawtooth waves are common. A language model can
  propose them from memory of textbook forms rather than by reasoning from these data. A success for E shows that the
  form was reachable from E's prior, not that E invented it.
- **No new variables.** Every law uses only observed inputs. A mechanism that needs a new variable (memory, a hidden
  state, a conserved quantity) is the stronger test of the "jump". It is left for v5.
- **Synthetic worlds.** Each world follows a single law with low noise. Real data mix mechanisms and are noisier.
- **Unequal inputs.** E sees X, Z1, Z2 and Y but not the background variables. P sees all 23 inputs. L and R see what
  they saw in v3.
- **Determinism.** P's search and E's sampling are deterministic only with the fixed seeds, serial execution and the
  same versions. Ollama's seed handling can vary between versions, which are recorded with every raw record.
