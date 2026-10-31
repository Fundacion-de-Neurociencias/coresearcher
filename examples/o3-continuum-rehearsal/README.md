# O(3) continuum-limit rehearsal (openai/math family 215)

Inputs and outputs of the rehearsal described in
[`docs/reference/cases/YANG_MILLS_PREREGISTRATION.md`](../../docs/reference/cases/YANG_MILLS_PREREGISTRATION.md),
section 3 (ADR-DISCOVERY-081).

| File | What it is |
|---|---|
| `o3_continuum_claim.v1.json` (+ `.lock.json`) | The paper's claims (Theorems 1.1, 1.2, Corollary 1.3) as obligations, with a witness catalogue |
| `ClassicalON.lean` | Comparator reference statement, copied unmodified from openai/math |
| `ClassicalON.json` | Comparator config, copied unmodified from openai/math |
| `rehearsal_report.json` | Coverage map, probes, exclusion lint, family coverage; regenerate with `python scripts/cases/o3_rehearsal_report.py` |

## Third-party files

`ClassicalON.lean` and `ClassicalON.json` are from [github.com/openai/math](https://github.com/openai/math), commit
`4eaee87548250b2682affda7d05d947c05554bae`, paths `lean/ComparatorChallenges/ClassicalON.lean` and
`lean/ComparatorChallenges/ClassicalON.json`, licensed under the Apache License 2.0 (`lean/LICENSE` in that
repository). They are reproduced byte for byte; their SHA-256 hashes are pinned in
`python/discovery/o3_continuum_case.py` and checked by the tests. They are audited here as data. Nothing in them is
executed.
