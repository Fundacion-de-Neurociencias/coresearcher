# Case: obligation ledger for the scalar input of the general Mahler conjecture

**Date:** 2026-10-28. **Status:** case study by the CoResearcher maintainers. This is the first application of
[ADR-DISCOVERY-076](../../decisions/ADR-DISCOVERY-076-OBLIGATION-LEDGER.md).
**Scope:** the formal and mathematical soundness of one input of a claimed proof. The case makes no judgement on the
rest of the proof, nor on credit, novelty or announcements.
**Modules:** [`obligation_ledger.py`](../../../python/discovery/obligation_ledger.py),
[`mahler_obligations.py`](../../../python/discovery/mahler_obligations.py)
**Report:** [`ledger.json`](../../../examples/mahler-obligations/ledger.json). Regenerate it with
`python scripts/cases/mahler_obligations_report.py`, which takes several minutes.
**Tests:** [`tests/test_obligation_ledger.py`](../../../tests/test_obligation_ledger.py) use coarse grids.

## 1. Why this input

The released reasoning summary for family 087 (Mahler, Part III) ends with a proof that is conditional on uniform
scalar inequalities. The manuscript "The Mahler Conjecture for General Convex Bodies" (openai/math, commit
`7ef5c0cc`) collects these inequalities in one place. They are Lemma *Profile identities* and Proposition *Scalar
inequalities*, `prop:scalar-input` in `build/sections/01-cones.tex`. The inequalities involve fixed one-variable
profiles built from the Gaussian distribution function, and fixed parameters that do not depend on the body or the
dimension. The parameters (b = .602, c = .365, r = .22, s = 3.6, …) are the same as in the summary.

The current formal and computational coverage of this input is as follows:

- **Lean.** Family 087's Lean targets cover only the symmetric case and its equality classification
  (`symmetric_mahler`, `symmetric_mahler_equality`). The general case is not formalized.
- **Author certificates.** Appendices 7–8, plus ten Python programs in `verification/` (interval enclosures and
  Bernstein bounds).
- **Our checks.** We did not run those programs. Under ADR-076 they are read as data and not executed. Our checks
  below are re-implemented from the statements.

## 2. Ledger

The scalar input has 11 obligations. Values come from `ledger.json`.

| Obligation | Status | Smallest margin | Scope of our check |
|---|---|---|---|
| (N+2)g = d; d′ = 2xd − v′ − 2g′; Nd − v″ = −(N+2)(d + g″) | **DISCHARGED_SYMBOLIC** | exact | any p with p′ = φ |
| b − r² − d > 0 | CHECKED_NUMERIC | ≈ 0.055 (at x = ±20) | x ∈ [−20, 20], step 0.02 |
| \|v′ − x\| ≤ .319 | CHECKED_NUMERIC | ≈ 0.001 | same |
| C ≤ −.341 | CHECKED_NUMERIC | ≈ 3.4·10⁻⁴ (at x = 0) | same |
| S_q > 0 | CHECKED_NUMERIC | ≈ 0.116 (at x = 0) | same |
| λt₋² + t₋C + K > 0 | CHECKED_NUMERIC | ≈ 9·10⁻⁴ | same |
| λt₊² + t₊C + K < 0 | CHECKED_NUMERIC | ≈ 7.5·10⁻⁴ | same |
| 2(−.37)C − .37² − 4λK > m*² | CHECKED_NUMERIC | ≈ 0.009 | same |
| (3), first inequality | CHECKED_NUMERIC | ≈ 0.024 (at z = x = 0) | (z, x) ∈ [−12, 12]², step 0.02 |
| (3), second inequality | CHECKED_NUMERIC | ≈ 1.0 | same |
| (4), the segment inequality | CHECKED_NUMERIC | ratio of the two sides ≤ 0.73 | all segments with endpoints in [−12, 12] every 0.04 |

Every inequality also carries a CERTIFIED_BY_AUTHOR discharge for all x: the appendices and the programs.

**Claim status: CHECKED_NUMERIC. It is not a proof.** The identities are proved. Each inequality holds at every point
we evaluated, at high precision, with the margins shown. Three things in this input are not discharged by
CoResearcher:

1. the unbounded tails;
2. the continuum between grid points;
3. segments longer than our window.

These rest only on the authors' appendices and programs.

The ledger shows where the real risk sits. Several margins are of order 10⁻³–10⁻⁴: C ≤ −.341 at x = 0, and the two
quadratic conditions near x ≈ 0 and x ≈ 3.4. A rounding slip in a constant would break them first. Two negative
controls in the tests confirm this: tightening the constants to −.342 or to .317 makes the check fail.

## 3. Method notes

- **Precision.** The profile X = p/φ grows like e^{x²/2} and multiplies quantities of size e^{−x²}. Evaluation
  therefore uses 60 + 0.9x² decimal digits, and 1 − p is computed as erfc(x/√2)/2 rather than by subtraction. A
  first attempt at fixed precision produced values of order 10⁴⁰, which come from the arithmetic and not from the
  profiles.
- **Derivatives.** They are exact symbolic derivatives (SymPy), evaluated in mpmath. Segment averages use the
  trapezoid rule on the 0.02 grid.
- **Encoding check.** The identities first failed because p and 1 − p had been encoded as independent functions. They
  are proved once 1 − p is substituted back. That was an encoding error on our side, not a defect of the paper.

## 4. What would move the status to a proof

There are two routes:

- interval enclosures of our own for every inequality on a bounded window, plus our own tail bounds;
- a Lean formalization of the proposition.

Either would turn each CHECKED_NUMERIC row into DISCHARGED_SYMBOLIC or DISCHARGED_FORMAL. The rest of the proof, the
cone, entropy and quadratic arguments of Sections 1–6, is outside this ledger and is still covered by the manuscript
alone.
