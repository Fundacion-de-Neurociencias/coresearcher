# ADR-DISCOVERY-084: Benchmarks as regression tests

**Status:** Accepted
**Date:** 2026-11-01

**Modules:**
- [`python/discovery/capability_regression.py`](../../python/discovery/capability_regression.py)
- [`python/discovery/openai_math_time_travel.py`](../../python/discovery/openai_math_time_travel.py) (scoring and offline replay)
- [`python/discovery/asymptotic_forms.py`](../../python/discovery/asymptotic_forms.py) (o(1) readings, uniformity)
- [`python/cli/regression.py`](../../python/cli/regression.py) (`coresearcher regression list|check|update`)
- [`api/routers/regression.py`](../../api/routers/regression.py) (`/api/regression/*`)
- [`tests/test_capability_regression.py`](../../tests/test_capability_regression.py)

**Builds on:**
- ADR-DISCOVERY-077: the openai/math time-travel benchmark and import obligations;
- ADR-DISCOVERY-070: statement fidelity and the coverage map;
- ADR-DISCOVERY-081: the Yang–Mills pre-registration and the O(3) rehearsal;
- ADR-DISCOVERY-082: the manuscript audit;
- ADR-DISCOVERY-083: the cited-results registry;
- ADR-DISCOVERY-068: a non-answer never becomes an answer.

**Methodology:** block C of [`VERIFICATION_METHODOLOGY.md`](../architecture/VERIFICATION_METHODOLOGY.md), method M9
(measure on real errors).

**Numbering:** 083 is the latest record on master, so this record is 084.

## Context

The October 2026 exercises left benchmarks whose results lived in reports and in case tests:
- the time-travel benchmark on real openai/math corrections;
- the coverage-map calibration;
- the Sakana Error Diffusion case;
- the local-smoothing fidelity case;
- the Yang–Mills and O(3) rehearsals;
- the manuscript audit and the cited-results registry calibrations.

The time-travel benchmark needed a network clone of openai/math and four and a half minutes, so it never ran in CI. A
change that lost a HIT, or doubled the false alarms, would have gone unnoticed. A change that gained a HIT would have
gone unrecorded. Method M9 asks that every change be measured against these real errors.

## Decision

1. **One registry of regression cases.** Each case re-runs one benchmark offline from vendored fixtures. It returns
   flat observations, each with a direction:
   - `verdict`: HIT is better than MISS and NOT_ENCODABLE;
   - `higher` or `lower`: for counts;
   - `exact`: for calibrated answers.

   The eight cases are listed in [`REGRESSION_BENCHMARKS.md`](../reference/REGRESSION_BENCHMARKS.md).
2. **Frozen, hashed expectations.** `benchmarks/regression/expectations.json` holds:
   - the observations of each case;
   - the SHA-256 of each fixture (of its LF bytes, so a Windows checkout gives the same digest);
   - a version number;
   - a history of reasons.

   `expectations.sha256` pins the SHA-256 of its canonical JSON. A file that does not match is refused.
3. **Both directions fail.** `check()` reports, per case, the worst of these classes: ERROR, REGRESSION,
   FIXTURE_CHANGED, CHANGED and IMPROVEMENT. Any of them fails the test. An improvement fails until its expectation is
   frozen in the same change, so a gain in capability always appears as a reviewed diff. A case that cannot run is
   ERROR, never a pass (ADR-068).
4. **Deliberate updates only through the CLI.** `coresearcher regression update --reason TEXT [--case ID]` freezes
   fresh observations. It bumps the version, records the reason and the changed keys, and rewrites the hash. It
   refuses an empty reason and a case that errors. The API serves the expectations
   (`GET /api/regression/cases`) and a fresh check (`POST /api/regression/check`, API key, read-only). It cannot
   update them.
5. **Offline time travel from verified excerpts.** The scoring of ADR-077 moved from the benchmark script into
   `openai_math_time_travel`, and the script now imports it. A new `fixture` command of the script writes, for each
   of the 47 manuscripts and both versions, an excerpt. The excerpt keeps:
   - every flagged math segment or citation, closed under whole segments;
   - every relation that the numeric identity check evaluates, because its random points come from one generator
     shared across the manuscript;
   - every defect location with its tolerance, the paragraphs around it and the enclosing environment markers, for
     the import scan;
   - the bibliography as its keys, and the manuscript snapshot as the names that the excerpt links to.

   Lines keep their original numbers, and blank lines fill the gaps. The builder refuses to write the fixture unless
   each excerpt reproduces the full sources' flags exactly, and the import obligations at each defect location as
   well. At the initial freeze the offline replay gave the same summary as the committed full run
   (`openai_math_revision_results.json`), and the same obligations at the defect locations as
   `openai_math_revision_posthoc.json`. The fixture is 148 KB compressed. It contains openai/math material under
   Apache-2.0, with attribution in `benchmarks/regression/fixtures/README.md`.
6. **ETH as a positive fidelity control.** The Comparator statement of family 378 is vendored. The control checks
   four things:
   - the range of `k` is EQUIVALENT to the headline claim;
   - the machine is bound by ∃ before every ∀ over inputs (`asymptotic_forms.uniformity`);
   - the space bound quantifies over every execution prefix;
   - the o(1) subtlety (`asymptotic_forms.little_o_exponent`).

   For the last check, the headline n/(log n)^{1/2+o(1)} is read in two explicit forms. In the signed form, some
   eps(n) → 0 of any sign. In the nonnegative form, eps(n) ≥ 0, which is the same as a bound by n/√(log n). The
   check substitutes n = exp(exp(t)), and sympy limits decide each form. The Lean exponent
   A·n·(log log(n+16))²/√(log(n+16)) and the manuscript's A·n·log log n/√(log n) both FIT the signed reading and do
   NOT FIT the nonnegative one. A limit that sympy cannot decide is UNDECIDED.
7. **Speed.** `manuscript_checks` memoizes `sympy.simplify(a - b) == 0`. This is a pure function, and a corrected
   manuscript repeats most identities of its earlier version. The memo cut the replay from 54 s to 11–14 s, and the
   flags are unchanged. The whole set runs in about 25 s on a laptop.

## Consequences

- Every pull request is measured against the 17 real corrections, the false-alarm counts and the calibrations. A
  loss fails CI. A gain must be frozen, with a reason, in the same pull request.
- The full online run remains the reference measurement. The offline replay covers only the lines the current checks
  look at. A future check that reads other lines will see blank lines there. The fixture must then be rebuilt with the
  new check's lines, through the same verification, before its gains can be measured. The builder's exact-match rule
  keeps that rebuild honest.
- The expectations are only as good as the reviews of their history. The tool records each reason, but it cannot
  judge whether a frozen trade-off was justified.
- Scope stays formal soundness: the cases measure detection of internal and formal defects, never the quality of
  sources or evidence.
