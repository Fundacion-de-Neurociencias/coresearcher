# Unknown-mechanism benchmark v3: report (arms L and R; arm P pending)

Protocol: [UNKNOWN_MECHANISM_V3_PROTOCOL.md](UNKNOWN_MECHANISM_V3_PROTOCOL.md), committed in `d210bd7` before any run
(SHA-256 `cb61cdaca6aebf58...`). Raw records: [unknown_mechanism_v3_raw.jsonl](unknown_mechanism_v3_raw.jsonl).
Scores: [unknown_mechanism_v3_results.json](unknown_mechanism_v3_results.json).

Arms L (library selection) and R (validation-tuned ridge) ran on 2026-10-18 in a Linux cloud container. Arm P (PySR)
needs Julia and waits for the Legion (runbook job 5), so criterion C2 is not yet scored.

## Results

| | Real data: mean test R² (95% bootstrap) | Null data: mean test R² (95% bootstrap) | Null gate (upper bound ≤ 0.05) |
| --- | --- | --- | --- |
| L, library selection | 0.750 (0.680 to 0.816) | -0.063 (-0.075 to -0.053) | passed |
| R, tuned ridge | 0.718 (0.647 to 0.783) | -0.036 (-0.046 to -0.027) | passed |

**C1 (L beats R): met.** Mean ΔR² +0.032, 95% bootstrap interval +0.017 to
+0.047. Both arms pass the null gate, so the comparison is interpretable. This is the result v2
could not give: against a baseline tuned the same way, selection still wins on real data and finds nothing in noise.

## By archetype (real data)

| Archetype | L | R | L − R |
| --- | --- | --- | --- |
| HARMONIC_NONLINEAR | 0.976 | 0.922 | +0.055 |
| MULTIPLICATIVE_COUPLING | 0.990 | 0.989 | +0.001 |
| REGIME_PHASE_SHIFT | 0.861 | 0.753 | +0.108 |
| SIMPSONS_CAUSAL_INVERSION | 0.823 | 0.849 | -0.026 |
| THRESHOLD_INVARIANT_GATE | 0.863 | 0.851 | +0.012 |
| UNOBSERVED_LATENT_MANIFOLD | -0.001 | -0.038 | +0.037 |

## Reading

- The advantage is small and comes mostly from the archetypes whose generating form is in the library
  (REGIME_PHASE_SHIFT, HARMONIC_NONLINEAR). R does better on SIMPSONS_CAUSAL_INVERSION, and neither method recovers
  UNOBSERVED_LATENT_MANIFOLD (R² near 0).
- Because the library contains the forms of five generators (protocol section 8), C1 shows that selection uses that
  prior knowledge without overfitting. It does not show discovery of laws outside the library; that requirement of
  the v2 report is still open.
- C2, against PySR, is the stronger test. PySR searches equations freely, so it could match or beat the library on
  the archetypes the library expresses, and it is the natural candidate for the archetypes the library cannot.
