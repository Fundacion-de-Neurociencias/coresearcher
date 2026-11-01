# Benchmarks as regression tests

ADR-DISCOVERY-084 (block C of [`VERIFICATION_METHODOLOGY.md`](../architecture/VERIFICATION_METHODOLOGY.md), method M9)
turns the October 2026 benchmarks and calibrations into regression tests. They run offline, in the normal test
suite (`tests/test_capability_regression.py`), on every change.

## What is measured

| Case | What it re-runs | Source |
| --- | --- | --- |
| `openai_math_time_travel` | HIT / MISS / NOT_ENCODABLE for each of the 17 real openai/math corrections, per check; false alarms on corrected, citation-update and never-revised manuscripts; ADR-077 import obligations at each defect location | ADR-077, [`OPENAI_MATH_REVISION_RESULTS.md`](benchmarks/OPENAI_MATH_REVISION_RESULTS.md) |
| `openai_math_coverage_calibration` | Range comparisons and automatic range checks for families 079 and 215; junk-value lint counts | ADR-070, coverage map |
| `eth_statement_fidelity` | Family 378 as a positive fidelity control: range EQUIVALENT, machine bound before inputs, space bound at every prefix, and the o(1) sign subtlety | ADR-084 |
| `sakana_ed_polarity` | The Error Diffusion polarity verdicts, necessity tables, rivals and replay witnesses | `ed_polarity_case` |
| `local_smoothing_fidelity` | Comparator ranges, development statements, mutants caught, open lint findings | ADR-070 |
| `yang_mills_o3_rehearsal` | Yang–Mills checklist probes and scenarios; O(3) coverage, probes and exclusion lint | ADR-081 |
| `manuscript_audit_calibration` | Citation gate, import counts and registry phrase matching | ADR-082 |
| `cited_registry_calibration` | Withdrawal sign mismatch, ETH retraction impact, biomarker cutoff outside validation | ADR-083 |
| `verification_chain` | The composed chain end to end on a math hypothesis (order and three predictions) and a biomedical-style one (pTau217 and decline, a cutoff cited outside its validated assay): every step's state, the ledger, the roll-up, the freeze digest, and BLOCKED for each hypothesis edited after its freeze | ADR-085 |

The whole set takes about 25 s on a laptop. The time-travel case dominates.

## Where things live

- `benchmarks/regression/expectations.json` holds the frozen observations of each case, the SHA-256 of each fixture,
  a version number and the history of updates.
- `benchmarks/regression/expectations.sha256` pins the SHA-256 of the canonical JSON of the expectations. An
  expectations file that was edited by hand is refused.
- `benchmarks/regression/fixtures/` holds the vendored inputs. See its README for sources and licences.

## How a check fails

Every observation has a direction:

- `verdict`: HIT is better than MISS and NOT_ENCODABLE;
- `higher` or `lower`: for counts;
- `exact`: for calibrated answers, where any change is a regression.

A case fails on any difference. The report names the class of the difference:

- **REGRESSION:** a capability got worse.
- **IMPROVEMENT:** a capability got better, but the expectation was not updated in the same change. The gain is
  real but not yet on record, so the check fails until the expectation is frozen.
- **CHANGED:** a value moved without an order (MISS against NOT_ENCODABLE), or an observation appeared or vanished.
- **FIXTURE_CHANGED:** a fixture's bytes differ from the hash frozen with its expectation.
- **ERROR:** the case could not run. A non-answer is never a pass.

## Updating expectations deliberately

1. Run the check and read the differences:

   ```bash
   python -m python.cli.main regression check
   ```

2. Decide whether each difference is intended. A REGRESSION is fixed in the code, not frozen. Freeze one only if it is
   a deliberate trade-off, and state that trade-off in the reason.
3. Freeze the new observations of the affected cases, with a reason:

   ```bash
   python -m python.cli.main regression update --case openai_math_time_travel --reason "EXPONENT check now resolves \simeq chains: one more HIT"
   ```

   This rewrites `expectations.json` and `expectations.sha256`. It bumps the version and appends the reason and the
   list of changed keys to the history.
4. Commit both files in the same pull request as the code change. The reviewer sees the change in capability as a
   diff of `expectations.json`.

The API serves the frozen expectations (`GET /api/regression/cases`) and a fresh check
(`POST /api/regression/check`). It never updates them.

## Rebuilding the time-travel fixture

The fixture holds excerpts of the openai/math sources at the two commits of the benchmark. It is rebuilt only when
the dataset or the excerpt rules change:

```bash
python scripts/benchmarks/openai_math_revision_bench.py fixture
```

This needs network access, because it makes a blobless clone of openai/math. The builder checks every excerpt against
the full sources before writing anything: the flags of each version must be identical, and so must the import
obligations at each defect location. The online run (`... run`) remains the reference measurement. At the initial
freeze, the offline replay reproduced its summary exactly.
