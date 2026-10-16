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
| 7 | 100-world unknown-mechanism benchmark (v1) | [`run_unknown_mechanism_benchmark.py`](../../scripts/run_unknown_mechanism_benchmark.py) | Synthetic | **WITHDRAWN** | v1 chose mechanisms on the test split, its library contained the true laws, and its relative gain divided by a near-zero baseline (the +33353% figure). Superseded by v2 (row 18). |
| 8 | 50-case adversarial stress suite | [`run_adversarial_destruction_suite.py`](../../scripts/run_adversarial_destruction_suite.py) | Constructed | PASS | Buries 21/50 flawed hypotheses (42%), unmasks 49/50 traps (98%), rejects 14/14 tautologies. Self-correction rate 40% with no printed denominator. |
| 9 | Universal cross-domain invariants (4 domains) | [`run_universal_cross_domain_suite.py`](../../scripts/run_universal_cross_domain_suite.py) | Constructed | PASS | Exit code only. |
| 10 | Paper2Agent MCP federation with SHA-256 provenance | [`run_paper_agent_mcp_suite.py`](../../scripts/run_paper_agent_mcp_suite.py) | Constructed | PASS | End-to-end run. |
| 11 | Agora shared memory: branch index and cherry-picking | [`run_agora_shared_memory_suite.py`](../../scripts/run_agora_shared_memory_suite.py) | Constructed | PASS | Exit code only. |
| 12 | Fast System One typed triage | [`run_fast_system_one_suite.py`](../../scripts/run_fast_system_one_suite.py) | Constructed | PASS (after fix) | The failure was a stale test expectation: the default tier is `SYSTEM_1_VEGA_PHYSICS` (ADR-DISCOVERY-053), and the test still expected `SYSTEM_1_LOCAL_FAST`. The tier test now sets each environment explicitly. The classifier was not changed. |
| 13 | Twin-gate epistemic harness (5 gates) | [`run_twin_gate_harness_suite.py`](../../scripts/run_twin_gate_harness_suite.py) | Synthetic | PASS | Reports 5/5 gates. |
| 14 | Membrane dynamics and Duhem–Quine attribution | [`run_membrane_dynamics_suite.py`](../../scripts/run_membrane_dynamics_suite.py) | Synthetic | PASS | Simulation contracts, no molecular dynamics run. |
| 15 | Epistemic stigmergy and reality firewall (RCS ≥ 2.0) | [`run_epistemic_stigmergy_suite.py`](../../scripts/run_epistemic_stigmergy_suite.py) | Synthetic | PASS | Exit code only. |
| 16 | Real-cohort suite with autopsy of failing hypotheses | [`run_real_cohort_discovery_suite.py`](../../scripts/run_real_cohort_discovery_suite.py) | External real data (to verify) | PARTIAL | One sub-check reports `FAILED (Non-Carrier Discrepancy)`, yet the suite prints a final "FULLY VALIDATED" and exits 0. The script should fail when a sub-check fails. |
| 18 | Unknown-mechanism v2, pre-registered ([protocol](benchmarks/UNKNOWN_MECHANISM_V2_PROTOCOL.md)) | [`run_unknown_mechanism_v2.py`](../../scripts/benchmarks/run_unknown_mechanism_v2.py) | Synthetic, with a permutation null | MIXED: primary criterion met on noise | Recovery 85.7% on real laws vs 15.5% on the null, but the flexible-baseline criterion also holds on permuted data. Not evidence of discovery. Full analysis in the [v2 report](benchmarks/UNKNOWN_MECHANISM_V2_REPORT.md). |
| 19 | Semantic bijectivity gate detects prose/Lean statement drift (ADR-DISCOVERY-048) | [`openai_math_pilot.py`](../../scripts/benchmarks/openai_math_pilot.py) | External: openai/math (Apache-2.0), synthetic mutants | NOT SUPPORTED (pilot) | On 19 formalized results, the auditor's score never changed between original and mutated statements (AUROC 0.524, null 0.524). See the [pilot report](benchmarks/OPENAI_MATH_PILOT_REPORT.md). |
| 20 | Formal and physical heuristics: partial proof progress, axiom hygiene, conformational RMSD bound | [`test_heuristic_physical_and_formal_invariants.py`](../../tests/test_heuristic_physical_and_formal_invariants.py) | Constructed | NOT VALIDATED | Hand-set constants (0.20 + 0.15 per lemma, 0.70 with `sorry`, 0.50 Å RMSD) with no calibration. They were first named after Gemini 4 Argon benchmarks (RiemannBench, GraphWalks, ERQA, xTB) without any relation to them; renamed as heuristics. Tests check the arithmetic, not scientific validity. Liouville phase-space conservation is standard physics and is not part of this row. |
| 21 | Formal hypotheses: exact content, assumption-conflict, counterexample and comparison verdicts over a finite state space (ADR-DISCOVERY-059) | [`test_formal_hypothesis.py`](../../tests/test_formal_hypothesis.py) | Constructed | PASS | Verdicts are exact by enumeration of the declared state space, and the tests check them against hand-computed results. They are correct for the declared variables and domains; whether those model a real phenomenon is outside this check. |
| 22 | Hypothesis Tournament Arena ranks hypotheses by pairwise debate and Elo (ADR-DISCOVERY-058) | [`test_hypothesis_tournament_arena.py`](../../tests/test_hypothesis_tournament_arena.py) | Caller-supplied scores | NOT VALIDATED | The four axis scores are inputs, not evaluations; a match is their weighted difference and Elo adds only order effects. Tests check the arithmetic. Endpoints were unauthenticated and unbounded until the 2026-10-15 review. |
| 23 | SMT back end for formal hypotheses with continuous variables, and consequence checking (ADR-DISCOVERY-060) | [`test_formal_smt.py`](../../tests/test_formal_smt.py) | Constructed | PASS | Verdicts are decided by z3 over the reals. On 60 random finite hypotheses the SMT and enumeration back ends agree on every verdict, conflict set, counterexample, comparison and entailment. Lean kernel cross-check: round 0 proved 3 of 7 z3 entailments; with the shape-directed default tactic, 12 of 12 (checks C01–C16), and no theorem z3 rejected was proved (no soundness discrepancy). Run with Lean v4.35.0 and Mathlib modules built from source, not yet with the full `import Mathlib` on the Legion. See [round 0 results](benchmarks/ROUND0_EXPLORATORY_RESULTS.md), section 2b. |
| 24 | A local model formalizes prose hypotheses faithfully (ADR-DISCOVERY-061) | [`test_formalizer.py`](../../tests/test_formalizer.py), [`ROUND0_EXPLORATORY_RESULTS.md`](benchmarks/ROUND0_EXPLORATORY_RESULTS.md) | Seed dataset, 20 items (exploratory, not frozen) | NOT MET | Round 0: equivalence to gold 0.15 for Laya (llama3.2:3b) and 0.50 for qwen2.5:14b, below the 0.80 threshold. Formalizer output stays a draft confirmed by the researcher. The pre-registered round runs after the scientists review and freeze the dataset. |
| 25 | Formal versions of the Alzheimer demo rivals (ADR-DISCOVERY-061) | [`test_formal_workbench.py`](../../tests/test_formal_workbench.py) | Constructed | DRAFT | Verdicts and comparisons are exact for the formal objects. The objects are the maintainers' reading of one-sentence statements, pending review by neuroscientists; statistical and causal parts of the prose are listed as not formalized. |
| 26 | Research projects pass stage gates; an agent cannot certify its own work, and a release is pre-registered only if its protocol held (ADR-DISCOVERY-063) | [`test_research_lifecycle.py`](../../tests/test_research_lifecycle.py) | Constructed | PASS | The tests check the rules: self-checks never satisfy verifier or human checks, gates refuse to pass early, rework supersedes later gates, a protocol reopened after execution makes the release exploratory, digests chain, the log replays to the same state, and the watcher detects artifacts changed after a gate. Whether gates make research more reliable is not measured, and no real project has run through them yet. |
| 27 | A self-consistency gate (N samples, exact z3/enumeration equivalence) keeps unstable formalizations out of the court (ADR-DISCOVERY-064) | [`test_formalization_gate.py`](../../tests/test_formalization_gate.py), [`FORMALIZER_GATE_RESULTS.md`](benchmarks/FORMALIZER_GATE_RESULTS.md) | Seed dataset, 20 items (exploratory, not frozen) | PARTIAL | False acceptances fall from 6 to 4 (qwen2.5:14b, N=5), 3 to 0 (Laya) and 6 to 2 (both models mixed), none introduced; equivalence among accepted items 0.625 to 0.733 for qwen. Not significant at n = 20. Systematic translation errors pass the gate. |

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
