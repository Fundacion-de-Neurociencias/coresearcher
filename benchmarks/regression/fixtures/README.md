# Regression fixtures (ADR-DISCOVERY-084)

Inputs of the offline regression cases. Each file's SHA-256 (of its LF bytes, raw bytes for `.gz`) is frozen in
`../expectations.json`. A changed fixture fails the check as FIXTURE_CHANGED until the expectation is updated.

| Path | Content | Source and licence |
| --- | --- | --- |
| `openai_math_time_travel.json.gz` | Excerpts of 47 manuscripts, pre-fix and corrected, at the benchmark commits `adc7f124` and `30148886`. Lines keep their original numbers. Bibliographies are reduced to their keys. | [openai/math](https://github.com/openai/math), Apache-2.0. Built by `scripts/benchmarks/openai_math_revision_bench.py fixture`. |
| `eth-378/SubexponentialSAT.lean`, `eth-378/SubexponentialSAT.json` | Comparator statement and configuration of family 378 (the ETH refutation), unmodified | openai/math at `4eaee87548250b2682affda7d05d947c05554bae`, `lean/ComparatorChallenges/`, Apache-2.0 |
| `manuscript-audit/calibration.json` | The ADR-082 calibration manuscript | Written for CoResearcher |
| `cited-registry/calibration.json` | The ADR-083 calibration entries and contexts | Written for CoResearcher |

The openai/math material is reproduced under the Apache License 2.0 (<http://www.apache.org/licenses/LICENSE-2.0>).
The excerpts are a modification: every line not needed by the checks is blank, and the bibliographies are replaced
by their keys.
