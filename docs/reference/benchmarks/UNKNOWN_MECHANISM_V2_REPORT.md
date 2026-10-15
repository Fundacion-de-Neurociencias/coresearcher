# Unknown-mechanism benchmark v2: report

Protocol: [UNKNOWN_MECHANISM_V2_PROTOCOL.md](UNKNOWN_MECHANISM_V2_PROTOCOL.md)
Script: [`scripts/benchmarks/run_unknown_mechanism_v2.py`](../../../scripts/benchmarks/run_unknown_mechanism_v2.py)
Raw outputs: [primary](unknown_mechanism_v2_results.json), [null control](unknown_mechanism_v2_null_control.json)

## Provenance

- Protocol SHA-256 before the post-hoc section was appended: `b67b8599ffe01d1d...` (the run that
  produced the primary numbers used this version).
- The primary file was regenerated after section 10 was appended. The numbers are identical; the file now
  records the SHA-256 of the extended protocol. Both values are stated here so the record stays traceable.
- Deterministic: seeds `1000 + i` for data, `7000 + i` for the null permutation, `20261012` for bootstrap.

## Results

| Quantity | Primary (real laws) | Null control (Y permuted) |
| --- | --- | --- |
| Recovery of expected family | 72/84 = 85.7% (Wilson 95%: 76.7–91.6%) | 13/84 = 15.5% (Wilson 95%: 9.3–24.7%) |
| Mean ΔR² vs flexible baseline | +0.046 (bootstrap 95%: +0.030 to +0.063) | +0.077 (bootstrap 95%: +0.061 to +0.093) |
| Mean ΔR² vs naive baseline | +0.667 (bootstrap 95%: +0.599 to +0.733) | −0.038 (bootstrap 95%: −0.048 to −0.028) |
| Worlds with ΔR² > 0 vs flexible | 84/100 | 87/100 |
| Pre-registered primary criterion | met | **met on noise** |
| Pre-registered secondary criterion | met | not met |

## Breakdown of the primary run by archetype

| Archetype | n | Recovered | Mean test R² (selected) | Mean ΔR² vs flexible | Selected families |
| --- | --- | --- | --- | --- | --- |
| HARMONIC_NONLINEAR | 17 | 17/17 | 0.976 | +0.057 | additive_basis ×17 |
| MULTIPLICATIVE_COUPLING | 17 | 17/17 | 0.990 | +0.001 | interaction_Z1 ×17 |
| UNOBSERVED_LATENT_MANIFOLD | 17 | 12/17 | −0.001 | +0.110 | latent_pc1 ×12, others ×5 |
| REGIME_PHASE_SHIFT | 17 | 15/17 | 0.861 | +0.116 | regime_Z1 ×15, interaction_Z1 ×2 |
| SIMPSONS_CAUSAL_INVERSION | 16 | 11/16 | 0.823 | −0.027 | regime_Z2 ×11, interaction_Z2 ×5 |
| THRESHOLD_INVARIANT_GATE | 16 | not scored | 0.863 | +0.013 | additive_basis ×10, interaction_Z1 ×6 |

## Interpretation

1. **The primary criterion does not discriminate signal from noise.** On permuted data it is still met,
   because the unregularised flexible baseline overfits 120 rows and the selected model does not. This is
   the most important result of this run. The v2 primary criterion is invalid as evidence of discovery.
2. **Recovery is partly built in.** The library contains the generating functional forms for the harmonic
   and multiplicative laws, so 34 of the 84 scored worlds are recovered by construction. The null control
   (15.5%) shows the recovery label is informative beyond chance, but this is not an independent test.
3. **The "recoveries" on the latent archetype are not predictive.** Their mean test R² is −0.001. The label
   "latent_pc1" was selected on validation noise, not on structure.
4. **Simpson's archetype is worse than the flexible baseline** (mean ΔR² −0.027), which the primary summary
   hides.
5. **v1 headline figures are withdrawn.** The +33,353% figure came from dividing by a near-zero naive R².
   Under v2 the mean test R² of the selected model is above the naive model's by about 0.67 absolute, but
   that is mostly the harmonic and regime archetypes, where the library contains the law.

## What a valid successor needs (pre-registration for v3)

- Generating laws that are **not** in the library (for example, saturating exponentials, logistic gates,
  and additive effects of unseen covariates), so recovery cannot be built in.
- A flexible baseline tuned by the same validation procedure (cross-validated ridge), not an untuned
  degree-3 polynomial.
- The null control as a pre-registered gate: the primary criterion must fail under permutation.
- Reporting per archetype, including archetypes where the method is worse than the baseline.

## Status

Benchmark v2 **does not establish** that the selection procedure discovers hidden mechanisms. It
establishes that (a) the v1 headline was an artefact, and (b) the v2 primary criterion cannot separate
signal from noise on this generator.
