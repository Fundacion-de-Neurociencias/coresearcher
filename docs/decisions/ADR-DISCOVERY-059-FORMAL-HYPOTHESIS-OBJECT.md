# ADR-DISCOVERY-059: Formal hypothesis object and exact evaluation

**Status:** Accepted
**Date:** 2026-10-15
**Module:** [`python/discovery/formal_hypothesis.py`](../../python/discovery/formal_hypothesis.py)
**API:** `POST /api/hypotheses/evaluate`, `POST /api/hypotheses/compare`

## Context

The constitution defines CoResearcher as a court that reduces the space of possible states (Omega) through
constraints, predictions and falsification. ADR-DISCOVERY-006 defines a hypothesis as "a conjecture about what
constraints govern a phenomenon".

The code had no object that represents a hypothesis that way. Hypotheses were free text (`RivalHypothesis.statement`)
or sets of scores supplied by the caller. No pipeline turned a user's hypothesis into something that could be checked:
the workbench ignored the question text, modus tollens took a boolean argument, and the formal engines (SymPy, Lean,
proof DAGs) only ran on objects built by hand for each case.

## Decision

A hypothesis is a formal object:

- **Variables** with finite domains. Their product is Omega.
- **Scope** and **assumptions**: predicates that select the states the hypothesis speaks about. Assumptions play the
  role of Duhem-Quine auxiliaries.
- **Claims**: predicates that must hold in every state where the scope and all assumptions hold.

A state is *forbidden* when it is in scope, satisfies every assumption and violates at least one claim.

Every evaluation enumerates Omega exactly, so its results are proofs over Omega, not estimates:

| Evaluation | Result |
| --- | --- |
| Content | `VACUOUS` (no applicable state), `SELF_CONTRADICTORY` (every applicable state forbidden), `UNFALSIFIABLE` (nothing forbidden) or `FALSIFIABLE`, with the excluded fraction of Omega and per-claim exclusions |
| Assumption conflicts | Minimal sets of assumptions that no state satisfies together |
| Falsifiers | Example states that would refute the hypothesis if observed |
| Confrontation | Modus tollens against observations: a *certain* counterexample when every completion of the unobserved variables is forbidden, a *possible* one when only some are; each lists the violated claims and the auxiliaries in question |
| Comparison | `EQUIVALENT`, `STRONGER`, `WEAKER`, `INCOMPARABLE` or `CONTRADICTORY`, with discriminating states (ADR-DISCOVERY-003) |

Predicates use a restricted expression language: comparisons, `and`/`or`/`not`, arithmetic and membership in literal
collections. They are interpreted over the Python AST and never passed to `eval`.

## Consequences

- Hypotheses from any domain can be evaluated, provided their variables can be given finite domains.
- The verdicts are exact for the declared state space. They say nothing about whether the chosen variables and domains
  model reality well; that remains the researcher's responsibility.
- Other engines can now target this object instead of free text: a generator (for example the private Einstein
  generator) should emit hypotheses in this form so the verifier can check them (ADR-DISCOVERY-002).

## Limitations

- **Finite domains only.** Continuous quantities must be discretised. An SMT back end (for example z3) would lift this
  limit for linear arithmetic; it is not part of this decision.
- **Exhaustive enumeration** is capped at 2,000,000 states, and the conflict search at 12 assumptions.
- **Not yet wired:** CAS and Lean checks of formal consequences, and the conversion of `state_space.py`'s fixed
  neurodegeneration Omega and the existing `RivalHypothesis` records into this form.
