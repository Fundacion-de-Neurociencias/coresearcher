# ADR-DISCOVERY-093: Formalizer v2

**Status:** Accepted
**Date:** 2026-11-02

**Modules:**
- [`python/discovery/formalizer.py`](../../python/discovery/formalizer.py): `formalize_v2`, `repair_predicate`, `repair_data`, `draw`, `rederive`, `active_pipeline`
- [`python/discovery/formalization_gate.py`](../../python/discovery/formalization_gate.py) and [`python/discovery/formal_pipeline.py`](../../python/discovery/formal_pipeline.py): they draw and re-derive through the active pipeline
- [`scripts/benchmarks/formalizer_bench.py`](../../scripts/benchmarks/formalizer_bench.py): `run --pipeline v1|v2`

**Builds on:**
- ADR-DISCOVERY-059: the formal object;
- ADR-DISCOVERY-061: the formalizer;
- ADR-DISCOVERY-064: the self-consistency gate;
- ADR-DISCOVERY-068: provenance;
- ADR-DISCOVERY-084: regression;
- ADR-DISCOVERY-085: the verification chain.

## Context

The formalizer turns a scientist's prose into the formal object that every later step judges. It was the weakest link
of the chain: in round 0 its equivalence to gold was 0.15 (3B model) and 0.50 (14B model). Its failures fell into a
few kinds:
- the direction of "only if";
- strictness;
- roles (scope or assumption);
- invented claims;
- "fixing" contradictory text;
- notation the evaluator rejects, such as `implies`.

## Decision

1. **The v2 path** keeps the model as a translator and the evaluator as the judge. It adds:
   - translation rules for the failing phrasings and three worked examples on topics outside every benchmark set;
   - JSON mode where the endpoint supports it;
   - a deterministic surface repair that only rewrites rejected notation into the accepted one. It never adds, drops
     or reorders a claim and never changes a comparison. With a schema whose names the model kept, the schema's
     domains are restored.
   - one self-repair round that sends the validator's exact error back once.
2. **v2 is the default** of the API formalizer, the gate and the chain (`active_pipeline()`).
   `FORMALIZER_PIPELINE=v1` reproduces round 0. Gate provenance records the pipeline, the prompt version and its
   SHA-256.
3. **Offline re-derivation.** A v2 sample stores the model's last raw answer. `rederive()` applies the same surface
   repair and validation, so phase 2 of the two-phase CLI reproduces the object without the model.
4. **Measurement under a frozen protocol** ([FORMALIZER_V2_PROTOCOL.md](../reference/benchmarks/FORMALIZER_V2_PROTOCOL.md)),
   with a held-out set written before any v2 output. Results are in
   [FORMALIZER_V2_RESULTS.md](../reference/benchmarks/FORMALIZER_V2_RESULTS.md). On the held-out set, v2 beats v1 on
   all four local models: 17→67%, 67→92%, 58→92% and 92→100%. That meets the pre-registered rule for making v2 the
   default.
5. **Regression.** The new case `formalizer_v2` re-scores the vendored raw outputs offline, with expectations v10.

## Consequences

- The chain receives correct formal objects far more often, and every downstream verdict benefits.
- Remaining failure kinds are named: inverted "Q whenever P", definitional equations put in the wrong role, residual
  "fixing", and an invented variable. A v3 must be measured on a new held-out set.
- Surface repair is a trust boundary. Its rewrites are pinned by tests, and any extension needs the same "notation
  only" argument.
