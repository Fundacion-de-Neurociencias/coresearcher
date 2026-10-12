# Claims register

Every quantitative or methodological claim made in the README is listed here with the
script or test that supports it, the data it runs on, and the result of the last run.

## How to read this register

| Status | Meaning |
| --- | --- |
| **PASS** | The script exits with code 0 and reports no failed gate. |
| **PARTIAL** | Exit code 0, but the output contains a sub-check that reports `FAILED`. |
| **FAIL** | Non-zero exit code or an assertion error. |
| **NOT RUN** | Not executed in this register. |

**Data origin** states what the claim is evaluated on:

- **Synthetic**: generated inside the repository by design.
- **Constructed**: hand-written cases or fixtures in the repository.
- **External real data**: a file outside the repository. It cannot be reproduced from a clean clone.

Results were produced on Windows 11, Python 3.13, with `PYTHONPATH` set to the repository root and
`PYTHONIOENCODING=utf-8`, on 2026-10-12. The exit code is the only automated signal. Narrative
verdicts were read from the logs by hand. Re-run the scripts to refresh them.

## Benchmark and suite claims

| # | Claim (README) | Script | Data origin | Status (2026-10-12) | Notes |
| --- | --- | --- | --- | --- | --- |
| 1 | Categorical reasoning: zero holonomy defect on sound paths | [`run_categorical_reasoning_suite.py`](../../scripts/run_categorical_reasoning_suite.py) | Constructed | PASS | Verifies category axioms on fixed diagrams. |
| 2 | Epistemic PR auditor intercepts leakage, conservation breaches and p-hacking | [`run_epistemic_pr_auditor_suite.py`](../../scripts/run_epistemic_pr_auditor_suite.py) | Constructed | PASS | Exit code only. Detection rate is not reported by the script. |
| 3 | Real-cohort discovery pipeline on MetaboAD (N=66) | [`run_empirical_cohort_discovery.py`](../../scripts/run_empirical_cohort_discovery.py) | External real data | PASS (external data) | Loads N=66 and uses n=50 complete cases. The script reports **0.0% out-of-sample error reduction**, which does not support a predictive claim. The dataset is not in this repository. |
| 4 | Physical coherence: DAG audit, second law, Navier–Stokes dissipation | [`run_physical_coherence_suite.py`](../../scripts/run_physical_coherence_suite.py) | Constructed | PASS | Exit code only. |
| 5 | ToolGrad backward inversion, deterministic contracts | [`run_toolgrad_backward_synthesis_suite.py`](../../scripts/run_toolgrad_backward_synthesis_suite.py) | Constructed | PASS | Backward pass 4/4; forward unverified pass 2/5. Small samples; see [confidence intervals](CONFIDENCE_INTERVALS.md). |
| 6 | Retrospective time split, quarantined at cutoff ≤ 2018 | [`run_retrospective_discovery_benchmark.py`](../../scripts/run_retrospective_discovery_benchmark.py) | Constructed | PASS | Exit code only. |
| 7 | 100-world unknown-mechanism benchmark | [`run_unknown_mechanism_benchmark.py`](../../scripts/run_unknown_mechanism_benchmark.py) | Synthetic | PASS | Recovers 87/100 mechanisms (95% CI 79.0–92.2%); wrongly buries 1/100. The reported **mean holdout gain of +33353.2%** is not plausible as a headline number and needs an audit before it is cited. |
| 8 | 50-case adversarial stress suite | [`run_adversarial_destruction_suite.py`](../../scripts/run_adversarial_destruction_suite.py) | Constructed | PASS | Buries 21/50 flawed hypotheses (42%), unmasks 49/50 traps (98%), rejects 14/14 tautologies. Self-correction rate 40% with no printed denominator. |
| 9 | Universal cross-domain invariants (4 domains) | [`run_universal_cross_domain_suite.py`](../../scripts/run_universal_cross_domain_suite.py) | Constructed | PASS | Exit code only. |
| 10 | Paper2Agent MCP federation with SHA-256 provenance | [`run_paper_agent_mcp_suite.py`](../../scripts/run_paper_agent_mcp_suite.py) | Constructed | PASS | End-to-end run. |
| 11 | Agora shared memory: branch index and cherry-picking | [`run_agora_shared_memory_suite.py`](../../scripts/run_agora_shared_memory_suite.py) | Constructed | PASS | Exit code only. |
| 12 | Fast System One typed triage | [`run_fast_system_one_suite.py`](../../scripts/run_fast_system_one_suite.py) | Constructed | **FAIL** | `AssertionError` on `system_tier`: the API returns a different tier than the script expects. Needs investigation. |
| 13 | Twin-gate epistemic harness (5 gates) | [`run_twin_gate_harness_suite.py`](../../scripts/run_twin_gate_harness_suite.py) | Synthetic | PASS | Reports 5/5 gates. |
| 14 | Membrane dynamics and Duhem–Quine attribution | [`run_membrane_dynamics_suite.py`](../../scripts/run_membrane_dynamics_suite.py) | Synthetic | PASS | Simulation contracts, no molecular dynamics run. |
| 15 | Epistemic stigmergy and reality firewall (RCS ≥ 2.0) | [`run_epistemic_stigmergy_suite.py`](../../scripts/run_epistemic_stigmergy_suite.py) | Synthetic | PASS | Exit code only. |
| 16 | Real-cohort suite with autopsy of failing hypotheses | [`run_real_cohort_discovery_suite.py`](../../scripts/run_real_cohort_discovery_suite.py) | External real data (to verify) | PARTIAL | One sub-check reports `FAILED (Non-Carrier Discrepancy)`, yet the suite prints a final "FULLY VALIDATED" and exits 0. The script should fail when a sub-check fails. |

## Unit and integration tests

The unit tests in [`tests/`](../../tests) cover the gates named in the README (Lean gate, semantic
bijectivity, oversight, Cogentic proof harness, biomacromolecular coordination, autopoietic closure,
Vega decision engine, Hakken/Dream-RSI, frontier math flywheel, result families, API security).

**Last run: 132 passed, 0 failed** (`python -m pytest tests -q`).

These tests check that the code behaves as specified. They do not validate the scientific content
of a claim. Use the benchmark rows above for that.

## Known gaps

- Sampling intervals for the internal outcomes are in [CONFIDENCE_INTERVALS.md](CONFIDENCE_INTERVALS.md). They are not a validation against external data.

- No claim has been validated against an external public dataset with confidence intervals.
- Claim 3 depends on a file outside the repository and cannot be reproduced from a clean clone.
- Claims 12 and 17 are open issues, not validated results.
- Benchmark scripts are not part of CI. They are run manually.
