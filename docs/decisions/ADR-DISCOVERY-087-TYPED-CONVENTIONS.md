# ADR-DISCOVERY-087: Conventions compared by meaning, not by wording

**Status:** Accepted
**Date:** 2026-11-01

**Modules:**
- [`python/discovery/typed_conventions.py`](../../python/discovery/typed_conventions.py)
- [`python/discovery/cited_registry.py`](../../python/discovery/cited_registry.py) (`check_conventions`, `cite_check`)
- [`api/schemas.py`](../../api/schemas.py): registry entries, citing contexts and chain citations accept typed
  conventions

**Builds on:**
- ADR-DISCOVERY-083: the cited-results registry;
- ADR-DISCOVERY-085: the composed chain;
- ADR-DISCOVERY-086: biomedical conventions;
- ADR-DISCOVERY-068: a non-answer never becomes an answer.

**Measured by:**
- [`OPENAI_MATH_CHAIN_RESULTS.md`](../reference/benchmarks/OPENAI_MATH_CHAIN_RESULTS.md), which ranked this gap
  first;
- [`OPENAI_MATH_TYPED_RESULTS.md`](../reference/benchmarks/OPENAI_MATH_TYPED_RESULTS.md).

## Context

The full-chain re-run of the openai/math time-travel benchmark found that the seams step compared every convention
outside the biomedical vocabulary as a normalized string.

- **A rewording counted as a mismatch.** Two texts that named the same convention in different words were a MISMATCH.
- **The step could not separate defects from correct citations.** It flagged 39% of the citations at defect locations
  and 27% of the citations elsewhere.
- **A real mismatch looked the same as a rewording.** A reviewer could not tell them apart.

ADR-083 had called string inequality "the safe direction". On real data it was not safe: it buried the signal.

## Decision

1. **A convention value can be typed.** Besides its `text`, it may carry:
   - **`fields`**: named atoms, compared after normalization.
   - **`signs`**: named sign or normalization quantities. Each is an integer formula over parameters with declared
     integer ranges. Two formulas are compared by exhaustive evaluation, at most 20,000 points (default range 0..16).
   - **`params`**: the parameters' ranges.

   Formulas are parsed into a restricted AST:
   - integers, names, `+ - * // % **`;
   - exponents up to 512, and negative exponents only on ±1.

   They are never evaluated with `eval`.
2. **Typed outcomes are decided.**
   - **MISMATCH.** A shared field that differs, or a shared sign quantity that differs at some parameter point. The
     finding names the item and the counterexample.
   - **MATCH.** At least one typed item was compared and all of them agree.
   - **Unspecified.** Typed items present on one side only are listed as unspecified.
3. **A difference in wording is a non-verdict.** Two untyped texts that differ are UNCOMPARED. This is a new
   per-convention outcome. It makes the citation check INCOMPLETE (ADR-068 UNDECIDED), never FINDINGS.
   - Equal texts after normalization are still a MATCH.
   - The biomedical kinds keep their canonical-value and unit-algebra comparison (ADR-086).
4. **Validation and exposure.**
   - A malformed or unsafe typed value is refused when an entry is registered.
   - In the citing context, the same problem gives UNCOMPARED instead of an error.
   - The API accepts typed conventions for registry entries, citing contexts and chain citations.

## Consequences

- **Lexical alarms disappear.** On the frozen inputs of the chain re-run, the code change alone removes them:
  - flags off the defect locations go from 6 to 2;
  - flags on corrected versions go from 5 to 2;
  - the four lexical protocol HITs (Weil, *Taming*, conditional good minimal models, two-arc GFF) become MISS.

  That is the honest state: those hits were not detections.
- **Typing does not detect the withdrawals.** It was pre-registered and blind on both sides.
  ([`OPENAI_MATH_TYPED_RESULTS.md`](../reference/benchmarks/OPENAI_MATH_TYPED_RESULTS.md)) It produces decided
  mismatches at the three withdrawals, but on reading they are artefacts:
  - a sign compared outside the passage's parity domain (n odd, where the passage has n = 2k);
  - a field that records which case of a lemma is used, not a convention.

  On the shared domain the cited reversal rule agrees with the citing signs. The convention the withdrawal notices
  blame, the source orientations of the two branches of the standard cusp, is not part of the cited lemma's
  statement, and neither side typed it.
- **Next gaps.** Typed parameters need constraints (parity, conditions), not only ranges. A convention that lives in
  the citing paper's own construction cannot be checked at the seam. It needs the construction itself to be checked
  (formalization).
- **The calibration changed.** The ADR-083 withdrawal calibration now uses a typed field
  (`cusp_branch_source_orientations`: matching against opposite). The untyped version of the same pair is
  UNCOMPARED. A test pins both.
