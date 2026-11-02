# ADR-DISCOVERY-090: Integer variables, decided by z3 over the integers

**Status:** Accepted
**Date:** 2026-11-02

**Modules:**
- [`python/discovery/formal_hypothesis.py`](../../python/discovery/formal_hypothesis.py) (`Variable.integer`)
- [`python/discovery/formal_smt.py`](../../python/discovery/formal_smt.py) (z3 `Int`, `%` and `//`)
- [`api/schemas.py`](../../api/schemas.py) (`FormalVariableModel.integer`)

**Builds on:** ADR-DISCOVERY-059 (formal hypotheses), ADR-083 (cited registry), ADR-089.

**Measured by:** [`OPENAI_MATH_UNBOUNDED_RESULTS.md`](../reference/benchmarks/OPENAI_MATH_UNBOUNDED_RESULTS.md).

## Context

A formal variable was either finite (a domain) or a real number. An integer such as a dimension n = 2k, with no upper
bound, had to be given a finite representative range. On the openai/math re-measures this produced counterexamples
that came from the range, not from the hypothesis. It also silently satisfied lower bounds the citing text never
stated.

## Decision

1. **Integer variables.**
   - A variable can be an integer: `{"name": "n", "integer": true}`, with optional integer `lower` and `upper`.
   - It is a variable with an infinite state space, routed to the SMT back end like a continuous one.
   - z3 encodes it as `Int`.
   - Counterexamples decode to Python integers.
2. **Integer division.** On integer expressions, `%` and `//` by a positive integer constant are supported, which
   makes parity (`n % 2 == 0`) expressible. Any other use of `%` or `//` stays unsupported and is refused.
3. **Compatibility.** `integer` is written in the JSON form only when set, so the input digests of existing hypotheses
   do not change. The API variable model accepts `integer`, and integer bounds are kept as integers.

## Consequences

- **What the re-measure showed.** Encoded blind with unbounded integers, the citing contexts no longer produce range
  artefacts. Their remaining undischarged hypotheses have counterexamples that the passage's own stated conditions
  allow. The passage window does not state the bounds the cited results need.
- **The next limit is context, not arithmetic.** The next capability is a manuscript-level context of standing
  assumptions.
- **Deciding integer arithmetic.** Nonlinear integer arithmetic is undecidable in general. z3 may answer `unknown`,
  which the existing SMT path already reports as a non-verdict (`SolverUndecided`), never as a verdict.
