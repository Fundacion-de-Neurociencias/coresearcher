# openai/math time-travel benchmark: case-scoped hypotheses (ADR-089), results

Protocol: [`OPENAI_MATH_CASES_PROTOCOL.md`](OPENAI_MATH_CASES_PROTOCOL.md), SHA-256 `af694c6b…`. It was frozen at
2026-11-01T21:43:45Z, before any hypothesis was tagged.

Input: [`openai_math_cases_registry.json`](openai_math_cases_registry.json) (`25b2c7c3…`, frozen 23:32:18). The
citing contexts are the frozen constrained ones. Results are in
[`openai_math_cases_results.json`](openai_math_cases_results.json). The implementation is
[ADR-089](../../decisions/ADR-DISCOVERY-089-CASE-SCOPED-HYPOTHESES.md).

## 1. Question and answer

The constrained re-measure left two artefacts:

- hypotheses of one case of a cited result checked against citations of another case;
- conditions written as field atoms.

**Answer.** Both are gone. The alarm load away from the defect locations falls again. No decided detection is gained
or lost.

`CHAIN_SEAMS` flags, by run:

| Run | At defect locations | Off-location, pre-fix | Corrected versions | FINDINGS, all 69 uses |
| --- | --- | --- | --- | --- |
| Chain re-run, strings | 11/28 | 6/17 | 5/24 | 22 |
| Typed (ADR-087) | 6/28 | 3/17 | 3/24 | 12 |
| Constrained (ADR-088) | 7/28 | 4/17 | 4/24 | 15 |
| Case-scoped (ADR-089, this protocol) | 7/28 | 3/17 | 2/24 | 12 |

- **Per-defect verdicts are unchanged.** The three withdrawals are still protocol HITs, from the input artefact
  described in the constrained results: `homotopy_direction` typed as a field. They are adjudicated as not the defect.
- **Decided detections that reflect a defect: 1/17** (0.01–0.27).

## 2. What changed, use by use

- **Case scoping.** The blind tagger scoped:
  - Aru–Sepúlveda–Werner's two hypotheses to parts (1) and (2);
  - the "loose link" hypothesis of Ekholm–Eliashberg–Murphy–Smith, Lemma 3.4, to the loose sign option.

  Four citations of that proposition name part (2). In each, the part (1) hypothesis is now NOT_APPLICABLE. The three
  "not discharged" findings these citations carried before are gone.
- **Conditional atoms (post hoc).** At *Products of K3*, Theorem 2.3, the field `index_group` is cited as "Z if n even
  and orientable, else Z/2" and cited as "Z". It is now UNCOMPARED, not a decided MISMATCH. The use is still flagged,
  by the "n ≥ 3 not discharged" artefact of the citing context's representative range. This rule was written after
  reading the constrained results, so its effect is reported apart. It removes one decided convention mismatch at a
  defect location, and no other.

## 3. What remains, and the next gaps

The decided findings that remain are all labelled.

- **At the defect locations**
  - **`homotopy_direction` at the three withdrawals.** A case typed as a field in the registry input.
  - **Three "n ≥ 3 / n > 2 not discharged" findings.** Representative ranges in the citing contexts.
  - **The boundary-coefficient field at *Finite ordinary MMP*.** It persists after the fix, so it is not the defect.
- **Elsewhere**
  - **Three decided field mismatches:**
    - the Beauville–Bogomolov–Fujiki scaling;
    - the reflected first-passage construction, which the passage itself states;
    - the definition of T in the Kuga–Satake corollary.

    None is a corrected defect.
  - **One representative-range artefact.**

Ranked gaps:

1. **Unbounded integer variables in citing contexts.** The "n > 2" findings are now the largest group of artefacts at
   the defect locations. The citing contexts should declare an unbounded integer (decided by z3), not a range starting
   at 0.
2. **Refusing a case recorded as a field.** A registry field whose name the citing side uses as a case, or whose
   values describe alternatives the statement covers, should become a case. This needs the field and case vocabulary
   to be declared once per entry, with the registration refusing duplicates.
3. **A local formal check of the orientation computation in the citing construction.** The withdrawals now come down
   to the branch order and orientation that the citing passages leave unstated (constrained results, section 3).
4. **A chain input kind for a citation inside a proof**, and **a premise-status feed** (unchanged).

## 4. Deviations

- **The conditional-atom rule is post hoc** (section 2).
- **The registry for this run is the constrained registry plus the blind case scopes.** Nothing else changed. The
  citing contexts are the frozen constrained ones, by design.

Regression expectations are now version 7. They include the `cases/*` observations.
