# ADR-DISCOVERY-070: Statement-fidelity audit — range equivalence with z3 and a junk-value lint for Lean statements

**Status:** Accepted
**Date:** 2026-10-27
**Modules:** [`python/discovery/statement_fidelity.py`](../../python/discovery/statement_fidelity.py),
[`python/discovery/lean_junk_lint.py`](../../python/discovery/lean_junk_lint.py),
[`python/discovery/local_smoothing_case.py`](../../python/discovery/local_smoothing_case.py)
**Builds on:** ADR-DISCOVERY-059 (formal hypotheses, `compare`), ADR-DISCOVERY-060 (z3 back end),
ADR-DISCOVERY-068 (thresholds: `solver_timeout_ms`; UNDECIDED is never a verdict)
**Case:** [`docs/reference/cases/LOCAL_SMOOTHING_STATEMENT_FIDELITY.md`](../reference/cases/LOCAL_SMOOTHING_STATEMENT_FIDELITY.md)

## Context

More mathematical claims now come with a formal statement and a kernel check: OpenAI's openai/math repository fixes
Lean "Comparator" reference statements for its preprints, and Comparator checks that a solution proves exactly those
statements using permitted axioms. Once that check exists, the proof is no longer where trust can fail. What remains is
**statement fidelity**: does the Lean statement say what the paper claims? Two failure modes are common and
mechanical:

1. **Range drift.** The hypothesis range in Lean differs from the paper's: a `≤` for a `<`, a missing `max(·, 0)`,
   an endpoint dropped or added, an `ℝ≥0∞` exponent re-encoded by hand. The ranges are semi-algebraic sets in a few
   real parameters and an integer dimension, which is exactly what the z3 back end of ADR-060 decides.
2. **Junk values.** Mathlib makes partial operations total. The Bochner `∫` of a non-integrable function is 0,
   `deriv` of a non-differentiable function is 0, `x / 0 = 0`, `ENNReal.toReal ∞ = 0`, a real `⨆` over an unbounded
   family is 0, `Real.rpow 0 0 = 1`, and `eLpNorm f ≤ C * ∞` holds for every `f`. A statement that lands on such a value
   can be weaker than it reads, or vacuous, and still be kernel-checked.

A manual read can catch both, but it does not scale and leaves no record. Both questions are formal, so they are in
CoResearcher's scope (formal soundness of claims; never sources, evidence or credit).

## Decision

### 1. Range equivalence (`statement_fidelity`)

- A `RangeSpec` holds the paper range and the formal range as predicates in the `formal_hypothesis` language, extended
  with `max`, `min` and `abs`, over typed `Parameter`s (real by default, `integer=True` for a dimension). A shared
  `domain` holds encoding facts (for example `q = 1/p ∈ [0, 1]`), and `encoding` notes record how each formal type was
  mapped.
- `max`, `min` and `abs` are rewritten into exact case splits (`φ[max(a, b)]` becomes
  `(a ≥ b ∧ φ[a]) ∨ (a < b ∧ φ[b])`), so the existing translator and solver are reused unchanged.
- `compare_ranges` asks z3 for a point in each difference. The relation is reported as the **strength of the formal
  statement**: EQUIVALENT, STRONGER (formal range strictly larger), WEAKER, INCOMPARABLE, or UNDECIDED. Every non-empty
  difference comes with a witness.
- Integer parameters are z3 `Int`s. When mixed integer/nonlinear arithmetic makes z3 give up, each direction is retried
  over the real relaxation: an empty real difference proves the integer one empty, and a real witness counts only if it
  is integral. Otherwise the answer is UNDECIDED, with the reasons. A timeout is never turned into a verdict.
- z3 treats `x / 0` as an arbitrary value, which is the same junk-value hazard on the SMT side. Before answering,
  every divisor is checked to be non-zero under the shared domain and the conjuncts to its left (Lean's
  short-circuit `if`). A reachable zero divisor makes the answer UNDECIDED.
- Derived quantities (a Sobolev order, an exponent) can be checked for equality on the common range (`Quantity`).
- `cross_check` re-decides a spec through `HypothesisEvaluator.compare` with the integer parameters fixed to a finite
  slice. Agreement is evidence that the case-split encoding is right; it proves nothing beyond the slice.

### 2. Junk-value lint (`lean_junk_lint`)

- A static pass over a Lean file. Comments are blanked with line numbers kept, the file is split into declarations,
  and every site of a total-function convention is listed: `BOCHNER_INTEGRAL`, `DERIV`, `DIVISION`, `INVERSE`,
  `TO_REAL`, `SUPREMUM`, `RPOW` (powers by an `ℕ` binder or numeral are skipped), and `INFINITE_RHS`.
- For each theorem, the definitions it uses are followed transitively by name. Each site is DISCHARGED only when the
  theorem's own text rules out the junk branch, and the finding names that text: Schwartz data, a `MemLp` premise or
  conclusion conjunct for the same function, a positivity premise on the divisor, an `if x = ∞` guard, an `ℝ≥0∞`
  codomain where the convention is exact, a positive exponent or base. Any other site is OPEN.
- OPEN means "a human decides", not "defect". A case file can attach a review note to each OPEN finding, keyed by
  (theorem, kind, line). The lint never edits the statement.

### 3. Case files

A case pins its sources (repository, commit, SHA-256 of every file it reads), vendors the statement file when the
licence allows (checked against the pinned hash before use), states the paper ranges with their source, and includes
mutated ranges as negative controls. Its report is regenerated by a script and compared with a fresh run in tests. A
kernel check is recorded only if it ran; otherwise the case says NOT RUN and why.

## Consequences

- First application: [Local smoothing for the Euclidean wave equation](../reference/cases/LOCAL_SMOOTHING_STATEMENT_FIDELITY.md).
  All six Comparator ranges are EQUIVALENT to the paper's for every integer `n ≥ 2`, decided exactly with no timeouts.
  All nine mutants are classified as expected. 45 of 48 lint findings are discharged by the statement text, and the 3
  open ones (all in `stein_square`) carry review notes, one of which (`deriv`) stays open for a human. The coverage map
  found Lean statements for Theorem 1.2 and Corollary 7.1 outside Comparator, and z3 shows them WEAKER than the paper
  (log powers `2n + 5` and `B > 2n + 6`).
- The audit is decidable only for ranges. Conclusions that involve logarithms against powers (`log^{4/pc}` against
  `δ^{-ε}`) are outside the fragment. The case argues them in prose and marks them as such.
- Range transcriptions are written by hand. The solver decides the encodings, not the transcription, so every row
  quotes both sources next to the formula.
- The lint is syntactic and can miss junk values hidden inside Mathlib definitions. It is a checklist generator for a
  reviewer, not a proof of fidelity.

## Alternatives considered

- **Elaborate the statements in Lean and lint the elaborated terms.** This would be more precise (it would see through
  `eLpNorm` and coercions). It needs the project's full toolchain and Mathlib build for every audit, and that is the
  step that could not run here. The syntactic pass runs anywhere in seconds. An elaborated lint can be added later
  behind the same `Finding` record.
- **Ask an LLM whether the statements match.** Rejected as the decision mechanism, for the same reason ADR-059 rejected
  rubric grading: the answer cannot be checked. LLMs may still draft range transcriptions, which the solver then
  decides.
