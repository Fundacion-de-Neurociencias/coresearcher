# Unknown-mechanism benchmark v4: interim report (arms O, L and R)

Protocol: [UNKNOWN_MECHANISM_V4_PROTOCOL.md](UNKNOWN_MECHANISM_V4_PROTOCOL.md), SHA-256
`22d1e1ee5641d0e27b4c50562362bcc54b10cea7e8cc1ed15cedfeeec625e9ee`. The arms ran on 2026-10-18, after the protocol
was merged. Raw records are in `unknown_mechanism_v4_raw.jsonl` and scores in `unknown_mechanism_v4_results.json`.

The PySR arm (P) and the language-model arm (E) have not run yet. They need the Lenovo Legion
([runbook](LEGION_RUNBOOK.md), job 6). The question v4 was built for (can P or E propose a law they were not given?)
is therefore still open.

## Results

All values are on the extrapolation rows (X in [3, 6]); each arm was fitted on X in [0.5, 3]. Intervals are 95%.

| Arm | Mean test R² (bootstrap CI) | Worlds recovered (Wilson CI) | Null: mean R² (upper bound) | Null gate | J |
| --- | --- | --- | --- | --- | --- |
| O, oracle form | 0.990 (0.985 to 0.993) | 98 / 100 (0.930 to 0.994) | −0.89 (−0.46) | passed | met |
| L, library selection | −2.46 (−3.27 to −1.68) | 6 / 100 (0.028 to 0.125) | −1.29 (−0.86) | passed | **not met** |
| R, tuned ridge | −3.48 (−4.42 to −2.57) | 4 / 100 (0.016 to 0.098) | −0.29 (−0.16) | passed | **not met** |

By archetype (mean test R², worlds recovered out of 25):

| Archetype | O | L | R |
| --- | --- | --- | --- |
| LOG_SATURATION | 0.994, 25 | −0.71, 1 | −0.85, 2 |
| FRACTIONAL_POWER | 0.993, 23 | 0.50, 5 | 0.50, 2 |
| ABS_KINK | 0.999, 25 | −7.49, 0 | −9.88, 0 |
| SAWTOOTH | 0.972, 25 | −2.15, 0 | −3.69, 0 |

- **Validity (V): met.** O has a mean R² of 0.990 and recovers 98 of 100 worlds, so the data identify the laws and
  the benchmark can discriminate.
- **Null gate (G): passed** by all three arms.
- **Jump (J): not met by L or R.** This was expected and stated in advance, because their hypothesis spaces do not
  contain these forms.
- **Extrapolation (X):** ridge extrapolates worse than library selection. ΔR²(R − L) is −1.02 (95% CI −1.78 to
  −0.26).

## Reading

- **Within the observed range the library looks adequate; outside it, it fails.** L picked the additive basis
  `X + Z1 + Z1² + sin(ωX)` in 92 of 100 worlds. That is the closest form it holds, and on the extrapolation rows it
  is worse than predicting the mean. Fitting the data and having the right premise are different things, and
  extrapolation is where the difference shows.
- **The six worlds L "recovered" are approximations, not the law.**
  - Five are fractional-power worlds and one is a log-saturation world. In all six, the selected sine basis stays
    within 0.1 standard deviations of a slowly curving law over [0.5, 6].
  - The recovery criterion is functional by design (protocol section 3), so a close approximation counts.
  - These six do not mean the library contains the law, and J correctly stays unmet.
- **Kinks and sawtooth waves are where a wrong premise costs most.** The mean R² for ABS_KINK is −7.5 (L) and −9.9
  (R). A smooth basis cannot continue a kink, and a periodic basis with the wrong shape does not continue a sawtooth.

## What remains

P and E, on real and null data, on the Legion. When they come back:

- J and X for P show whether a generic symbolic searcher recovers laws outside its grammar.
- J and X for E are the direct test, on our own data, of the claim that a language model cannot propose the
  premise.
- Either outcome is reported as it comes out, together with the limitations stated in protocol section 8.
