# Local smoothing statement-fidelity case

Inputs and outputs of the case described in
[`docs/reference/cases/LOCAL_SMOOTHING_STATEMENT_FIDELITY.md`](../../docs/reference/cases/LOCAL_SMOOTHING_STATEMENT_FIDELITY.md)
(ADR-DISCOVERY-070).

| File | What it is |
|---|---|
| `LocalSmoothing.lean` | Comparator reference statements, copied unmodified from openai/math |
| `LocalSmoothing.json` | Comparator config (six targets, permitted axioms), copied unmodified from openai/math |
| `fidelity_report.json` | Range equivalence, mutants, lint findings and coverage map; regenerate with `python scripts/cases/local_smoothing_fidelity_report.py` |
| `lean_check.txt` | Record of the kernel check: NOT RUN, with the reason |

## Third-party files

`LocalSmoothing.lean` and `LocalSmoothing.json` are from
[github.com/openai/math](https://github.com/openai/math), commit `7ef5c0cc5ca4b0e072b7a050fca09ab24bc6fa3a`, paths
`lean/ComparatorChallenges/LocalSmoothing.lean` and `lean/ComparatorChallenges/LocalSmoothing.json`, licensed under the
Apache License 2.0 (`lean/LICENSE` in that repository). They are reproduced byte for byte; their SHA-256 hashes are
pinned in `python/discovery/local_smoothing_case.py` and checked by the tests. They are audited here as data. Nothing in
them is executed.
