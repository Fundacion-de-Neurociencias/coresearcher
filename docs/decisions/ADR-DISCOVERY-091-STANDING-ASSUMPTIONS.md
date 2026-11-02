# ADR-DISCOVERY-091: Standing assumptions inherited by citing contexts

**Status:** Accepted
**Date:** 2026-11-02

**Modules:**
- [`python/discovery/cited_registry.py`](../../python/discovery/cited_registry.py) (`with_standing`, used by
  `cite_check`)
- [`python/discovery/hypothesis_ledger.py`](../../python/discovery/hypothesis_ledger.py) (a chain citation carries
  `standing`)
- [`api/schemas.py`](../../api/schemas.py) (`standing` on citing contexts and on chain citations)

**Builds on:** ADR-DISCOVERY-083, ADR-090.

**Measured by:** [`OPENAI_MATH_STANDING_RESULTS.md`](../reference/benchmarks/OPENAI_MATH_STANDING_RESULTS.md).

## Context

A citing context was the local passage alone. Measured on the openai/math real errors with exact integer arithmetic
(ADR-090), most remaining undischarged hypotheses failed for one reason: the passage did not restate a bound that the
manuscript fixes once, such as "throughout, n = 2k with k ≥ 2".

## Decision

1. **A standing context.** A citing context may carry `standing: {variables, assumptions, conventions}`, the facts its
   manuscript fixes for all of its uses.
2. **Merging with the passage.** `with_standing` merges them before the citation check:
   - **The passage wins.** A variable or convention the passage declares is kept as the passage declares it. Standing
     variables are added only under new names.
   - **No new names.** A standing assumption is inherited only when every name in it is a variable of the merged
     context. A standing fact never introduces an undeclared name.
   - **The record.** The inherited assumptions and variables are recorded in `standing_inherited`, so a reviewer sees
     what came from outside the passage.
3. **Exposure.** Chain citations carry `standing` to the seams step. The API accepts `standing` on citing contexts
   (`/api/registry/cite-check`) and on chain citations.

## Consequences

- **Measured effect.** On the standing re-measure, inherited standing assumptions discharged 7 more cited hypotheses
  and removed two findings at defect locations. No outcome moved the other way.
- **Extraction stays an input.** The standing context is extracted by a reader, here a blind agent following a frozen
  instruction. A wrong standing fact would discharge a hypothesis wrongly. That is why it is recorded separately
  (`standing_inherited`), and why the passage always wins.
- **Section-local facts are not covered.** A fact fixed for one section is neither standing nor passage, and was left
  out by rule. The next step is a context hierarchy: manuscript, section, passage.
