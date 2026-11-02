# openai/math time-travel benchmark: standing assumptions (ADR-091), results

Protocol: [`OPENAI_MATH_STANDING_PROTOCOL.md`](OPENAI_MATH_STANDING_PROTOCOL.md), SHA-256 `940171b5…`. It was frozen
at 2026-11-02T06:03:21Z, before any standing text was extracted.

Input: [`openai_math_standing_contexts.json`](openai_math_standing_contexts.json) (`6be76eef…`, frozen 06:06:23).
It holds the unbounded contexts, each with the blind standing context of its manuscript version, and the 17 standing
records. Results are in [`openai_math_standing_results.json`](openai_math_standing_results.json). The implementation
is [ADR-091](../../decisions/ADR-DISCOVERY-091-STANDING-ASSUMPTIONS.md).

## 1. Question and answer

The unbounded re-measure showed that the remaining undischarged hypotheses failed because the citing passage, read
within its window, does not state the bounds the cited results need. ADR-091 lets each citation inherit its
manuscript's standing assumptions, extracted blind from the paragraphs that state them.

**Answer.** Standing assumptions discharge hypotheses where the manuscript states them, and only there.

| | Unbounded (ADR-090) | Standing (ADR-091, this protocol) |
| --- | --- | --- |
| Hypotheses DISCHARGED, all 69 uses | 28 | **35** |
| Hypotheses NOT_DISCHARGED | 8 | **6** |
| `CHAIN_SEAMS` flags at defect locations | 7/28 | **5/28** |
| Off-location / corrected flags | 4/17, 4/24 | 4/17, 4/24 |
| FINDINGS, all 69 uses | 15 | 13 |

- **Products of K3, both trace-lemma uses.** The standing text fixes 2n = dim D with n ≥ 12. That discharges the cited
  "n ≥ 3" hypotheses at the trace lemma (Lemma 3.4) and the caps theorem (Theorem 2.3). Both uses go from FINDINGS to
  INCOMPLETE.
- **Ashkin–Teller, five uses of the cited six-vertex lemmas.** The standing parameter bound 1 < c ≤ 2 discharges the
  cited "c in [1, 2]" hypothesis. The uses stay INCOMPLETE because other cited hypotheses are not formal.
- **Kuga–Satake.** The extractor left n out, because n = 514 is fixed in one section only and the instructions say
  to leave section-local facts out. Its trace-lemma use keeps the "n ≥ 3 not discharged" finding. That is the honest
  outcome of the rule.
- **Per-defect verdicts are unchanged.** The three withdrawals are still protocol HITs. Two artefacts remain:
  - the `homotopy_direction` input artefact at Lemma 3.2;
  - the Kuga–Satake hypothesis above.
- **Decided detections that reflect a defect: 1/17** (0.01–0.27).

## 2. What this teaches

1. **Context is the lever for discharging hypotheses.** Seven hypotheses that were undecided or not discharged are now
   discharged, and none changed the other way. The rule that the passage wins and that a standing assumption never
   introduces a new name held. No standing fact contradicted a passage.
2. **Section-local facts are the next limit.** A fact fixed for "this section" sits between the passage and the whole
   manuscript. The Kuga–Satake case needs it: n = 514 is fixed in the section where the trace construction lives. A
   context hierarchy (manuscript, section, passage) with the section known for each citation would close it.
3. **No new defect is decided.** Standing assumptions remove false findings. They do not reach the corrected defects.
   Those still need either the case-as-field fix (an input problem) or the local orientation check (a new mechanism).

## 3. Next gaps, re-ranked

1. **Section-level context.** The section of each citation, and the facts fixed for that section.
2. **Refusing a case recorded as a field** in registry inputs. This is the last input artefact at the withdrawals.
3. **A local formal check of the orientation computation** in the citing construction. It is still the only route to
   the withdrawals that has been found.
4. **A chain input kind for a citation inside a proof**, and **a premise-status feed** (unchanged).

## 4. Deviations

None. Regression expectations are now version 9. For every typed variant they record the counts of discharged and
undischarged hypotheses as well.

## 5. Status: paused (decision of 2026-11-02)

The coordinating session paused this line of work after this pull request.

- **Where the work stands.** After six measured pull requests (#31–#35 and this one; ADR-087 to ADR-091), decided
  detections on the 17 real corrections are still 1/17.
- **What the pull requests did.** Each one after the first removed a class of false findings, and the alarm load
  fell.
- **Why the remaining defects are out of reach.** They sit in reasoning the passages never state:
  - the orientation computation inside the citing construction (the withdrawals);
  - argument gaps;
  - a possibly fallen premise of a cited result (*Taming*).

**Last decision.** Anyone who resumes this work starts from these ranked gaps, in this order:

1. **Section-level context.** The section of each citation, and the facts fixed for that section (Kuga–Satake:
   n = 514 in the trace construction).
2. **Refusing a case recorded as a field in registry inputs.** This is the last input artefact at the withdrawals
   (`homotopy_direction`).
3. **A local formal check of the orientation computation in the citing construction.** It is the only route to the
   withdrawals found so far: a finite computation over the source orientations of the two cusp branches.
4. **A chain input kind for a citation inside a proof.**
5. **A premise-status feed for cited results** (the *Taming* / Li–Zhang case).

Measure any resumed work against regression expectations version 9 and the frozen inputs listed in this series of
results documents.
