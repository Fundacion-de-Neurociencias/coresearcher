# ADR-DISCOVERY-083: Cited-results registry and premise retraction

**Status:** Accepted
**Date:** 2026-10-31

**Modules:**
- [`python/discovery/cited_registry.py`](../../python/discovery/cited_registry.py)
- [`api/routers/registry.py`](../../api/routers/registry.py) (`/api/registry/*`)
- [`python/cli/registry.py`](../../python/cli/registry.py) (`coresearcher registry …`)
- [`api/routers/manuscripts.py`](../../api/routers/manuscripts.py) (`use_registry` option)

**Builds on:**
- ADR-DISCOVERY-059: formal hypothesis objects and entailment;
- ADR-DISCOVERY-066: provenance never decides validity;
- ADR-DISCOVERY-068: status, provenance;
- ADR-DISCOVERY-076: obligation ledger;
- ADR-DISCOVERY-077 and ADR-DISCOVERY-082: import obligations and the manuscript audit;
- ADR-DISCOVERY-080: trust ladder.

**Methodology:** block B of [`VERIFICATION_METHODOLOGY.md`](../architecture/VERIFICATION_METHODOLOGY.md), methods
M6 (errors live at the seams) and M11 (when a premise falls, re-examine everything built on it).

## Context

The openai/math time-travel benchmark (ADR-077) found that real corrected errors sit where a proof imports
something from a cited source. The three withdrawals imported a trace sign from a cited lemma under the opposite
orientation convention. Other corrections applied a cited theorem without one of its hypotheses. The import
obligations of ADR-077 make each such import visible as an OPEN obligation. A registry entry there, however, was a
per-request list. Its hypotheses were matched only as phrases, and nothing recorded what depends on what.

The refutation of the Exponential Time Hypothesis showed the second gap. One premise, assumed by hundreds of
conditional results, fell. A verifier needs to know which of its claims rested on it.

## Decision

1. **A persistent, versioned registry of cited results and premises.** Each entry has:
   - an id and a source reference (provenance only);
   - a statement, with an optional ADR-059 formal statement;
   - hypotheses, each with an optional formal predicate and optional literal phrases (never regular expressions);
   - conventions as typed tags. Known kinds include sign, normalization, units, scale direction, validated assay,
     validated population and computation model;
   - a trust-ladder rung and a status (ACTIVE, DOWNGRADED, RETRACTED).

   Re-registering an id creates a new version. Every mutation appends to a hash-chained event log, and a store whose
   chain was edited is refused on load.
2. **Citation checks that never pass by default.** `cite_check(entry, context)` compares:
   - **Each convention with the citing context:** MATCH, MISMATCH, or UNSPECIFIED when the context is silent.
   - **Each hypothesis:**
     - DISCHARGED only when the citing context's assumptions entail it formally (enumeration or z3);
     - NOT_DISCHARGED, with counterexamples, when they do not;
     - STATED_IN_TEXT for a phrase match, which is not a discharge;
     - UNDECIDED otherwise.

   The outcome is:
   - CLEAR: entry active, all hypotheses discharged, all conventions matched;
   - FINDINGS: a mismatch, an undischarged hypothesis, or a non-active entry;
   - INCOMPLETE: anything undecided or unspecified. Its ADR-068 status is UNDECIDED, a non-verdict.

   Every check carries ADR-068 provenance.
3. **Ledger integration.** `to_obligation()` turns a check into an ADR-076 obligation of kind `import`. Only a CLEAR
   check whose hypotheses were all formally discharged becomes DISCHARGED_SYMBOLIC. A convention mismatch keeps the
   obligation OPEN: it is a defect in the transfer, not a refutation of the citing claim.
4. **Dependency propagation.**
   - Edges run from a claim or an entry to what it uses. Edges that would close a cycle are refused.
   - `retract()` retracts an entry, or downgrades it to a lower rung, and flags every transitive dependent. While
     a dependent is flagged, its effective rung is capped at CLAIMED.
   - `reevaluated()` clears a flag, with a note saying how the dependent was re-checked.
   - Both are events in the log.
5. **Manuscript audit.** `POST /api/manuscripts/audit` with `use_registry: true` adds the stored entries that have a
   bibliography key and locator to the request's cited results. They travel in the ADR-077 phrase form.
6. **Exposure.**
   - API: `POST /api/registry/entries`, `GET /api/registry/entries/{id}`, `POST /api/registry/cite-check`,
     `POST /api/registry/dependencies`, `POST /api/registry/entries/{id}/retract`, `GET /api/registry/impact/{node}`
     and `POST /api/registry/flags/{node}/reevaluated`.
   - CLI: `coresearcher registry register|show|cite-check|depend|retract|impact|reevaluated`. `cite-check` exits
     with 0 for CLEAR, 1 for FINDINGS and 10 for INCOMPLETE.
   - The store is `CORESEARCHER_REGISTRY_PATH`. The CLI defaults to `.coresearcher/registry.json`, and the API
     keeps the registry in memory when the variable is unset.

## Calibration

The tests in [`tests/test_cited_registry.py`](../../tests/test_cited_registry.py) include three calibration
fixtures.

- **The withdrawal pattern.** A cited trace lemma whose sign convention assumes matching source orientations,
  applied where the orientations are opposite, yields a MISMATCH finding. Retracting the lemma flags the manuscript
  that used it and the two that adapted its step.
- **ETH as a premise.** Retracting it flags the transitive dependents and only those. Their effective rung drops to
  CLAIMED until they are re-evaluated, and any later citation of the retracted premise is a finding.
- **A biomarker cutoff.** An illustrative pTau217 threshold validated under assay A, applied under assay B, yields a
  `validated_assay` MISMATCH. An age range outside the validated one is NOT_DISCHARGED, with a counterexample.

## Consequences

- Imported conventions and hypotheses of cited results can now be checked at each use, and a fallen premise is
  traced to every claim built on it. Before this change, both depended on a human noticing.
- Entering conventions and formal hypotheses remains manual. The registry decides nothing about an import it does
  not know, and such imports stay OPEN or UNDECIDED.
- Convention comparison is by normalized string equality. Semantically equivalent conventions written differently
  are reported as MISMATCH. That is the safe direction, and the finding is cleared by re-registering the entry with
  a canonical tag.
- The API registry is process-wide. Concurrent writers are serialized by a lock, and a multi-process deployment
  should point all processes at different stores or put a database behind this interface.
