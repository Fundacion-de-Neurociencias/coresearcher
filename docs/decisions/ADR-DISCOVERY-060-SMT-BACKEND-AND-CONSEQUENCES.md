# ADR-DISCOVERY-060: SMT back end, continuous variables and consequence checking

**Status:** Accepted
**Date:** 2026-10-15
**Modules:** [`python/discovery/formal_smt.py`](../../python/discovery/formal_smt.py),
[`python/discovery/formal_lean.py`](../../python/discovery/formal_lean.py),
[`python/discovery/formal_hypothesis.py`](../../python/discovery/formal_hypothesis.py)
**API:** `POST /api/hypotheses/evaluate`, `POST /api/hypotheses/compare`, `POST /api/hypotheses/entails`

## Context

ADR-DISCOVERY-059 introduced the formal hypothesis object with exact evaluation by enumeration. It listed two limits:
continuous quantities had to be discretised, and formal consequences of a hypothesis could not be checked. Most
scientific hypotheses mention continuous quantities (concentrations, rates, thresholds), and checking what a
hypothesis entails is how its predictions are derived.

## Decision

1. **Continuous variables.** A variable is either finite (`domain`) or continuous (`continuous=True`, optional closed
   `lower` and `upper` bounds). A hypothesis with any continuous variable is evaluated by the z3 SMT solver over the
   reals. Nonlinear real arithmetic (products, constant natural powers) is decided by z3's complete procedure for
   that theory.
2. **Same verdicts, two back ends.** Content verdicts, minimal assumption conflicts, falsifiers, certain and possible
   counterexamples, and comparison relations are computed by SMT with the same definitions as by enumeration. State
   counts and excluded fractions are undefined over the reals and are reported as `null`; `claims_with_content`
   replaces per-claim counts. `backend="smt"` can be forced on finite hypotheses, and the test suite cross-checks both
   back ends on random finite hypotheses.
3. **Consequences.** `HypothesisEvaluator.entails(h, consequence)` checks that a predicate holds in every applicable
   state the hypothesis allows, and returns counterexamples when it does not. `follows_from_claims` is true only when
   the consequence needs the claims: a statement already implied by domains, scope and assumptions alone does not
   count as a prediction of the hypothesis. `vacuous` flags hypotheses that allow no state, which entail anything.
4. **Lean.** `formal_lean.consequence_theorem` states the same consequence as a Lean 4 theorem over ℝ, with a default
   tactic. This server never runs Lean, so the status is always `NOT_KERNEL_CHECKED` (ADR-DISCOVERY-059 fixes made
   that status mandatory). Kernel checking runs on a machine with Mathlib; see the Legion runbook. A tactic failure
   means "not proved by this tactic", not "false".
5. **CAS.** No separate SymPy step is added for consequences. For the predicate language (polynomial arithmetic over
   the reals) z3 is a decision procedure, so a CAS adds no checking power; it remains in use for identities in
   `exact_symbolic_court`.

## Limits

- Unsupported by SMT: `%`, `//`, powers with a variable or negative exponent, and ordering comparisons on string
  variables. Hypotheses using them are rejected at construction when they have continuous variables, and the SMT
  back end cannot be forced on them.
- Division is real division; a hypothesis that divides by an expression that can be zero gets z3's total-division
  semantics, which differs from enumeration (which raises an error). State the non-zero condition as an assumption.
- Each solver call has a 10-second timeout. A timeout is reported as an error, never as a verdict.
- Lean export rejects string and boolean variables.
