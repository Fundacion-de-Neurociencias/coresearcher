# Unknown-mechanism benchmark v3: pre-registered protocol

Status: written on 2026-10-17, before the first run of any v3 arm. The script records this file's SHA-256 with every
raw result, and scoring refuses results produced under a different protocol hash.

## 1. Why a v3

The v2 report ([UNKNOWN_MECHANISM_V2_REPORT.md](UNKNOWN_MECHANISM_V2_REPORT.md)) ended in a negative methodological
finding. Its primary criterion was also met on permuted data, because the unselected 13-term flexible baseline
overfits 120 rows. It named three requirements for a valid successor:

1. a flexible baseline tuned by the same validation procedure;
2. generating laws absent from the library;
3. the null control as a pre-registered gate.

v3 addresses requirements 1 and 3. It adds two tuned baselines: a validation-tuned ridge regression and symbolic
regression with PySR. PySR is the strongest generic baseline available for "find a short equation that fits the
data". Requirement 2 is **not** addressed: the worlds are unchanged, so the library still contains the forms of five
of the six generators. This is a known limitation (section 8).

## 2. Question

On held-out data, does selection from CoResearcher's fixed hypothesis library predict better than two baselines?

- a validation-tuned ridge polynomial;
- symbolic regression (PySR) with validation-based model selection.

And does each method stay near zero R² when the data carry no signal?

## 3. Worlds, splits and null control

The worlds, seeds and splits are exactly those of v2, sections 2 and 5:

- 100 worlds, seed `1000 + i`, 240 rows;
- discovery rows 0-59, validation rows 60-119, test rows 120-239.

The **null control is part of this protocol**. Every arm also runs with Y permuted within each world (seed
`7000 + i`), and every arm faces the same null gate.

## 4. Arms

All arms see only the discovery and validation splits until a single final evaluation on the test split.

- **L, library selection.** The v2 procedure, unchanged (v2 sections 3 and 4).
- **R, tuned ridge.** The v2 13-term cubic design in (X, Z_1, Z_2):
  - Features are standardised with the discovery mean and standard deviation, and the intercept is not penalised.
  - Penalty α is chosen from {10⁻³, 10⁻², 10⁻¹, 1, 10, 10², 10³} by validation R² after fitting on discovery.
    Ties go to the larger α.
  - The model is refit on discovery ∪ validation with the chosen α and evaluated on test once.
- **P, symbolic regression (PySR).**
  - Version: `pysr==2.7.0`, which pins SymbolicRegression.jl ~2.7.0. The exact versions are recorded in every raw
    record.
  - Inputs: X, Z_1, Z_2 and the 20 background variables (23 inputs). Search on the discovery split only.
  - Configuration, fixed:
    - `niterations=40`, `populations=15`, `population_size=33`, `maxsize=20`;
    - binary operators `+ - * /`, unary operators `sin cos exp square`;
    - `deterministic=True`, `parallelism="serial"`, `random_state=3000 + i`.
  - Selection: from PySR's hall of fame (one equation per complexity), the equation with the highest validation R².
    Ties go to the lower complexity.
  - Final fit: the selected equation's numeric constants are re-estimated on discovery ∪ validation by
    nonlinear least squares, starting from PySR's values. If the refit fails or does not lower the squared error
    on those rows, PySR's constants are kept. The equation is then evaluated on test once.
  - Equations that cannot be compiled or evaluated are skipped. If none is usable, the arm predicts the mean of
    discovery ∪ validation for that world, and the world is flagged in the raw record.

## 5. Metrics

- Test R² for each arm, not clipped at zero.
- Paired differences per world: `ΔR²(L−R)` and `ΔR²(L−P)`.
- Per-archetype means, and the selected PySR equation for each world.
- Uncertainty: 95% percentile intervals from a paired bootstrap over worlds, 10,000 resamples, seed `20261017`.

## 6. Pre-registered criteria

- **Null gate (G).** For each arm, on the null data, the upper bound of the 95% bootstrap interval of the mean test
  R² is at most 0.05. An arm that fails G finds structure in noise; comparisons with it are reported but not read as
  evidence about discovery.
- **C1.** On the real data, the lower bound of the 95% bootstrap interval of the mean `ΔR²(L−R)` is greater than 0:
  library selection beats a tuned ridge.
- **C2.** On the real data, the lower bound of the 95% bootstrap interval of the mean `ΔR²(L−P)` is greater than 0:
  library selection beats symbolic regression.
- **Reverse readings, reported with the same intervals.** An upper bound below 0 means the baseline is better. An
  interval that contains 0 means no difference was shown.

A criterion that is not met is reported as not met. Thresholds, configurations and the selection rule do not
change after any result is seen. Arms may run on different machines, because each record carries its versions and
the protocol hash.

## 7. Execution

`scripts/benchmarks/run_unknown_mechanism_v3.py`:

- `run --arm L|R|P [--null]` appends one JSON line per world to
  `docs/reference/benchmarks/unknown_mechanism_v3_raw.jsonl`. It is resumable.
- `score` writes `unknown_mechanism_v3_results.json`. Any arm that has not run is reported as not run.

L and R need only numpy. P needs Julia and runs on the Lenovo Legion (see the
[runbook](LEGION_RUNBOOK.md)), where 200 searches (real and null) are expected to take several hours.

## 8. Known limitations, stated in advance

- The worlds are synthetic, and the library contains the forms of five of the six generators. A win for L can
  partly reflect that, so C2 is a test of the library against a generic searcher, not of discovery in the wild.
  Requirement 2 of the v2 report remains open.
- PySR's search is stochastic in general. Determinism holds only with the fixed seed, serial execution and the same
  versions.
- Samples are small: 60 discovery, 60 validation and 120 test rows.
