# ADR-DISCOVERY-077: Import obligations and the citation gate for manuscript verification

**Status:** Accepted (2026-10-30)

**Context:**
- The openai/math revision benchmark
  ([protocol](../reference/benchmarks/OPENAI_MATH_REVISION_PROTOCOL.md),
  [results](../reference/benchmarks/OPENAI_MATH_REVISION_RESULTS.md)) used the 17 defects that the October 7,
  2026 release of openai/math corrected or withdrew as ground truth.
- The checks that existed before this ADR detected 1 of them. The other 15 were outside the language of every
  check.

**Narrative:** [OPENAI_MATH_TIME_TRAVEL.md](../reference/cases/OPENAI_MATH_TIME_TRAVEL.md)

**Modules:**
- [`python/discovery/cited_import_ledger.py`](../../python/discovery/cited_import_ledger.py)
- [`python/discovery/manuscript_checks.py`](../../python/discovery/manuscript_checks.py)
- [`scripts/checks/citation_gate.py`](../../scripts/checks/citation_gate.py)

## Problem

The corrected defects of that corpus do not sit in displayed algebra. Elementary identity and exponent checks,
run on 109,843 math segments, found no error. Every strict flag they raised was a notation artefact.

The defects sit where a proof **imports** something from a source it cites:

| Import | Defects |
| --- | --- |
| A sign taken from a cited lemma under another orientation convention | 3 withdrawals: Weil eightfolds, Kuga–Satake, products of K3 |
| A cited theorem applied without one of its hypotheses | Taming implies compatibility (Li–Zhang, Cor. 1.1); the Kähler inputs |
| A dependency on a companion manuscript that was later corrected or withdrawn | Kuga–Satake, products of K3 (on Weil); Deforming (on Taming) |
| A citation whose target does not exist | Exact BSD (`\cite{Dv}`) |
| A bound called effective while its constant is left unspecified | Incompressible Box Transport |

## Decision

1. **Citation resolution is a standing gate** (`scripts/checks/citation_gate.py`).
   - It runs first in any audit of a LaTeX manuscript.
   - It fails when a `\cite` key has no bibliography entry, or when a link to a collection manuscript names a
     directory that does not exist.
   - It is the only check that detected a real corrected defect, with zero false alarms over 47 manuscripts.
2. **Every import from a cited source is an obligation** of the ADR-076 ledger (`cited_import_ledger.scan`). There
   are four kinds:
   - **CONVENTION_TRANSFER**: a cited result is used in a passage that fixes a sign, orientation or
     normalization. The obligation is: "the imported value holds under this paper's conventions".
   - **HYPOTHESIS_MATCH**: a cited result with a locator (Theorem, Corollary, Lemma, ...) is used inside a proof or
     a result statement.
     - With a registry entry (`CitedResult` with `Hypothesis` patterns), each registered hypothesis is looked for
       in the citing statement and proof. Any hypothesis not found makes the obligation UNMATCHED.
     - Without an entry the obligation is NO_ENTRY.
   - **DEPENDENCY**: a link to a collection manuscript whose status is known (withdrawn, corrected).
     `propagate` follows such links transitively.
   - **EFFECTIVE_CONSTANT**: a passage calls a bound effective, explicit or computable while leaving a constant
     unspecified.
3. **These obligations are OPEN and never discharge themselves.** They are not discharged by detection, and a
   MATCHED hypothesis is a textual match, not a proof.
   - Discharge follows ADR-076: a reviewer's reading, a formal or symbolic check, or the author's certificate,
     each recorded with its status.
   - A claim keeps the status of its weakest obligation, so a manuscript with OPEN imports is not reported as
     verified.
4. **Detection is lexical, and every component says so.**
   - The module puts an obligation at the right line. It does not decide the mathematics.
   - Its alarm load is measured and published next to its detection.
5. **The cited-result registry starts empty in the public code.** No entry was written for the defects of the
   benchmark: that would only fit the test data. Entries are added when a reviewer encodes a cited result, with
   its source.
6. **Scope is unchanged.** These are verification mechanisms. They do not judge credit, sources or announcements,
   and they generate no hypothesis or proof.

## Evidence

The evidence is in-sample: the mechanisms were designed after reading the 17 defects. The figures below come from
`scripts/benchmarks/openai_math_revision_bench.py posthoc`, written to `openai_math_revision_posthoc.json`. They
show where obligations land and what they cost. They are not a measure of detection power.

**Where obligations land.** An obligation lands at the defect location, well above chance, for 4 of 17 defects:
- the stabilization-trace passage of all 3 withdrawals (CONVENTION_TRANSFER; chance expectation 0.02–0.06 each);
- the Li–Zhang citation that the taming corollary misapplied (HYPOTHESIS_MATCH; chance 0.46).

Six more revisions have obligations at their location. Their locations are large, so the chance expectation is
already at least 1 for most of them, and they are not counted.

**Propagation.** Seeding the Weil withdrawal and the Taming correction flags exactly Kuga–Satake, products of K3
and Deforming. No other manuscript among the 74 scanned is flagged.

**Coverage beyond chance, with the citation gate.** 6 of 17 defects:
- Weil, Kuga–Satake, products of K3, Taming (obligation at the defect location);
- Deforming (propagation);
- Exact BSD (citation gate).

**Not covered beyond chance: 11 of 17.**
- **Incompressible**: its effective-constant passage spans paragraphs that the sentence window does not join.
- **The 6 Kähler revisions.** Their fixes state the hypotheses of their inputs. A HYPOTHESIS_MATCH obligation
  could reach them only through registry entries, and the registry is empty.
- **The 4 Lipschitz/Ashkin–Teller revisions**: argument gaps that no import mechanism reaches.

**Cost per 1000 source lines on never-revised controls.**
- HYPOTHESIS_MATCH: 3.1
- CONVENTION_TRANSFER: 0.85
- EFFECTIVE_CONSTANT: 0.68

That is about 25 OPEN obligations for a 5000-line manuscript. Each one is a real import a reviewer can check. This
differs from the context identity flags, which reached a similar density but were all noise.

## Prospective test (pre-registered here)

This ADR freezes the mechanisms at these git blob ids (`git hash-object`):

| File | Blob id |
| --- | --- |
| `python/discovery/cited_import_ledger.py` | `f35e4f86fdbc08bf7b42b25f7996667ead1f0db4` |
| `python/discovery/manuscript_checks.py` | `69c6d65c43e180a92499dc4ea6294413582ce5a4` |
| `scripts/checks/citation_gate.py` | `80489bd8308ad715a7f244daaf72b8ee3b52a444` |

The next time openai/math, or any corpus with public corrections, records a fix after 2026-10-30, the frozen
mechanisms run on the pre-fix source with:
- the location rule and ±2 tolerance of the revision protocol;
- the same chance baseline.

The result counts as a test only if the code is unchanged or each change is listed as a deviation. Until then,
the in-sample figures above are the only evidence.

## Consequences

- An audit of a manuscript now produces, besides formal-statement checks, a list of OPEN imports with file and
  line. The three withdrawals of the release would have carried an OPEN convention-transfer obligation at
  exactly the passage their withdrawal notice names.
- The registry of cited results becomes the place where reviewer effort accumulates. Once a theorem is
  encoded, every later citation of it is matched automatically.
- Still to build, from the benchmark's ranking:
  - small-instance counterexample search (the four-torus strict inclusion);
  - notation-aware identity checking;
  - a cross-paragraph window for effective constants.
- The argument gaps of the probabilistic and birational revisions remain out of reach of static mechanisms.
