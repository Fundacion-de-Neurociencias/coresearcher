# ADR-DISCOVERY-076: Obligation ledger for claimed mathematical results

**Status:** Accepted (2026-10-28)
**Context:** The openai/math release case studies were LOCAL_SMOOTHING_STATEMENT_FIDELITY (ADR-070) and the
strategy analysis of the release. In the ten released reasoning summaries, every run ends with a claim that rests on
named open obligations, and the only checks recorded are the model's own re-derivations. Some manuscripts add
author-written certificate programs. Others add Lean statements, which cover part of the corpus.
**Module:** [`python/discovery/obligation_ledger.py`](../../python/discovery/obligation_ledger.py)
**Pilot:** [`python/discovery/mahler_obligations.py`](../../python/discovery/mahler_obligations.py),
case [MAHLER_SCALAR_OBLIGATIONS.md](../reference/cases/MAHLER_SCALAR_OBLIGATIONS.md)

## Decision

1. **A claimed result is checked through its obligations.** An obligation is an identity, a pointwise or segment
   inequality, an analytic step or an imported theorem. Each one records every discharge: its status, method, scope,
   who produced it and, for numeric checks, its smallest margin.
2. **Statuses are kept apart.** In decreasing strength they are DISCHARGED_FORMAL (kernel-checked),
   DISCHARGED_SYMBOLIC (exact CAS/SMT), DISCHARGED_INTERVAL (rigorous interval arithmetic with outward rounding over
   the obligation's whole stated domain), CHECKED_NUMERIC (bounded-sample evidence, with a mandatory scope),
   CERTIFIED_BY_AUTHOR (the source's own certificate, not re-run) and OPEN. REFUTED dominates everything. Only the
   first three count as proofs. The ledger never converts numeric evidence or an author's certificate into a proof.
   A proof on part of a domain (a bounded window) is recorded by splitting the obligation into the proved part and
   the rest; the window proof never discharges the original, unrestricted statement.
3. **A claim takes the status of its weakest obligation.** A claim is never reported as stronger than its
   least-checked obligation.
4. **Checks are independent of the source's own code.** Third-party verification programs are read as data and not
   executed. CoResearcher re-implements each check from the statement, which serves two purposes: the check is
   independent of the authors' code, and no untrusted code runs here. The authors' programs appear in the ledger as
   CERTIFIED_BY_AUTHOR.
5. **Scope is unchanged.** The ledger judges formal and mathematical soundness. It does not grade sources, credit or
   announcements. Hypothesis generation stays outside this public module: generators (for example the private
   Einstein generator, ADR-059) emit hypotheses that this verifier checks, and a generator never assigns its own
   verdict (ADR-002).

## Consequences

- The first application covers the scalar input of the Mahler conjecture for general convex bodies, which is the
  obligation that the released summary left conditional:
  - its three identities are DISCHARGED_SYMBOLIC;
  - all ten of its inequalities are CHECKED_NUMERIC on bounded ranges, with recorded margins;
  - the claim is therefore CHECKED_NUMERIC and not proved. The unbounded tails remain covered only by the
    authors' appendices and programs.
- An obligation moves from CHECKED_NUMERIC to DISCHARGED_SYMBOLIC only through rigorous interval enclosures with
  tail bounds of our own, or through a Lean proof.
- The ledger can be joined with the ADR-070 coverage map and with the citation graph of a corpus. A withdrawal can
  then be propagated to every claim that depends on it.
