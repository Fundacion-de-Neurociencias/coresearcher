# Unknown-mechanism benchmark v3: report (arms L, R and P)

Protocol: [UNKNOWN_MECHANISM_V3_PROTOCOL.md](UNKNOWN_MECHANISM_V3_PROTOCOL.md), committed in `d210bd7` before any run
(SHA-256 `cb61cdaca6aebf58...`). Raw records: [unknown_mechanism_v3_raw.jsonl](unknown_mechanism_v3_raw.jsonl).
Scores: [unknown_mechanism_v3_results.json](unknown_mechanism_v3_results.json).

Arms L (library selection) and R (validation-tuned ridge) ran on 2026-10-18 in a Linux cloud container. Arm P (PySR,
pysr 2.7.0) ran on 2026-10-18 on the Lenovo Legion (WSL2, runbook job 5), on the real and the null data. All three
arms are scored with the same protocol, so C1 and C2 are now both decided.

## Results

| | Real data: mean test R² (95% bootstrap) | Null data: mean test R² (95% bootstrap) | Null gate (upper bound ≤ 0.05) |
| --- | --- | --- | --- |
| L, library selection | 0.750 (0.680 to 0.816) | -0.063 (-0.075 to -0.053) | passed |
| R, tuned ridge | 0.718 (0.647 to 0.783) | -0.036 (-0.046 to -0.027) | passed |
| P, PySR | 0.848 (0.796 to 0.893) | -∞ (lower bound not defined; upper bound -0.065) | passed |

**C1 (L beats R): met.** Mean ΔR² +0.032, 95% bootstrap interval +0.017 to +0.047. Both arms pass the null gate, so
the comparison is interpretable.

**C2 (L beats P): not met.** Mean ΔR² (L − P) on real data is -0.097, 95% bootstrap interval -0.192 to -0.007. The
upper bound is below 0, so the reverse reading holds: **PySR is better than the library on real data**. L and P both
pass the null gate, so the comparison is interpretable.

**Null gate for P: passed on the protocol's rule, with one caveat.** The gate uses the upper bound of the interval,
which is -0.065. But one null world (index 18, HARMONIC_NONLINEAR) produced a selected equation whose predictions on
the test rows are not finite, so its test R² is recorded as -∞, as the protocol's rule requires (non-finite
predictions are scored as -∞). That single value makes the mean -∞ and the lower bound undefined. Excluding it is not
part of the protocol, so it is reported as it came out. One other null world of P also has a finite test R² below -5,
so the P null mean is driven by these two worlds.

## By archetype (real data)

| Archetype | L | R | P | L − R | L − P |
| --- | --- | --- | --- | --- | --- |
| HARMONIC_NONLINEAR | 0.976 | 0.922 | 0.964 | +0.055 | +0.012 |
| MULTIPLICATIVE_COUPLING | 0.990 | 0.989 | 0.990 | +0.001 | 0.000 |
| REGIME_PHASE_SHIFT | 0.861 | 0.753 | 0.412 | +0.108 | +0.449 |
| SIMPSONS_CAUSAL_INVERSION | 0.823 | 0.849 | 0.870 | -0.026 | -0.046 |
| THRESHOLD_INVARIANT_GATE | 0.863 | 0.851 | 0.860 | +0.012 | +0.003 |
| UNOBSERVED_LATENT_MANIFOLD | -0.001 | -0.038 | 0.992 | +0.037 | -0.993 |

## Reading

- **Against the tuned ridge (C1)**, selection wins on real data and finds nothing in noise. The advantage comes from
  REGIME_PHASE_SHIFT and HARMONIC_NONLINEAR, whose generating forms are in the library.
- **Against PySR (C2)**, the library loses on average. The gap is almost entirely one archetype:
  UNOBSERVED_LATENT_MANIFOLD, where the library scores R² ≈ 0 and PySR scores 0.99. On the other archetypes the two
  are close, except REGIME_PHASE_SHIFT, where PySR is much worse (0.41 against 0.86). PySR is therefore not uniformly
  better; it is better on the one archetype the library cannot express.
- The v2 report asked for evidence of discovery outside the library. This run shows that a free symbolic search can
  recover a law outside the five library forms (UNOBSERVED_LATENT_MANIFOLD). It does not show that our library
  method does, and the PySR result is a benchmark result on synthetic generators, not evidence about real discovery.
- Because the library is the prior knowledge that C1 measures, the honest summary is: with a tuned baseline, the
  library beats ridge; against a generic searcher, the library is worse on average and worse on the archetype that
  falls outside its forms.

## Limitations of this run

- Arms P ran only on the Legion, with pysr 2.7.0 and the protocol's settings; the version is recorded in every raw
  record.
- One null world gave a non-finite test R² for P (see above). The null gate uses the upper bound, which is finite, so
  the gate passes; a rule based on the mean would not be defined for P. Changing the rule would need a new protocol.
