# openai/math time-travel benchmark: constrained parameters and cases (ADR-088), results

Protocol: [`OPENAI_MATH_CONSTRAINED_PROTOCOL.md`](OPENAI_MATH_CONSTRAINED_PROTOCOL.md), SHA-256 `f333326a…`. It was
frozen at 2026-11-01T20:03:19Z in the ADR-085 freeze log, before any convention was typed under it.

Inputs, each frozen before the next step:

| Input | SHA-256 | Frozen at (UTC) |
| --- | --- | --- |
| [`openai_math_constrained_registry.json`](openai_math_constrained_registry.json) | `0ac377e3…` | 20:07:02 |
| [`openai_math_constrained_contexts.json`](openai_math_constrained_contexts.json) | `bc739699…` | 20:11:40 |

Results are in [`openai_math_constrained_results.json`](openai_math_constrained_results.json). The implementation is
[ADR-088](../../decisions/ADR-DISCOVERY-088-CONSTRAINED-CONVENTIONS.md).

## 1. Question and answer

The typed re-measure left decided mismatches at the three withdrawals. Both were artefacts:

- a sign compared outside the citing domain (n odd, where the passage has n = 2k);
- a field that recorded which case of a lemma was used.

ADR-088 adds `where` conditions to typed parameters, and keeps the case a citation uses (`case`) apart from the
conventions, checking it against the cases the cited result covers (`cases`).

**Answer.**

- **The parity artefact is gone.** Every imported sign at the withdrawals is now a decided MATCH, on the domain the
  passage uses:
  - Ekholm–Eliashberg–Murphy–Smith, Lemma 3.2: the reverse-homotopy factor −1 on even n, 20 points;
  - Lemma 3.4: (−1)^{k−1} and (−1)^k, 19 points, case covered.
- **This confirms, now as a decided result, what the typed re-measure concluded.** The signs imported from the cited
  lemmas agree with the citing papers. The withdrawals' error is not a mismatch of those signs.
- **The case artefact remains, through the inputs.** One registry typist recorded `homotopy_direction: forward` as a
  field, against the instructions, so the three withdrawals still carry a decided field MISMATCH (forward against
  reverse). The rule in the code works (tests). The typed input broke it.
- **Decided detections that reflect a defect: still 1/17** (0.01–0.27).

`CHAIN_SEAMS` flags, by run:

| Run | At defect locations | Elsewhere |
| --- | --- | --- |
| Chain re-run, string comparison | 11/28, 39% (0.24–0.58) | 11/41, 27% (0.16–0.42) |
| Typed (ADR-087) | 6/28, 21% (0.10–0.40) | 6/41, 15% (0.07–0.28) |
| Constrained (ADR-088, this protocol) | 7/28, 25% (0.13–0.43) | 8/41, 20% (0.10–0.34) |

Per-defect `CHAIN_SEAMS` verdicts are the same as in the typed re-measure:

- HIT on the three withdrawals, adjudicated as artefacts (section 2);
- MISS on *Taming*, conditional good minimal models and the two-arc GFF;
- NOT_ENCODABLE elsewhere.

## 2. Every decided mismatch, read

| Where | Mismatch | Label |
| --- | --- | --- |
| Three withdrawals, Lemma 3.2 | field `homotopy_direction`: cited forward, citing reverse | Artefact: a case typed as a field, against the instructions |
| Products of K3, Theorem 2.3 | field `index_group`: cited "Z if n even and orientable, else Z/2", citing "Z" | Artefact: a conditional value typed as an atom (the passage is in the even, orientable case) |
| Finite ordinary MMP, pre-fix and corrected | field `boundary_coefficient_range`: closed [0,1] against half-open [0,1) | Decided, not the defect: the same finding persists after the fix |
| Log abundance, pre-fix and corrected | field `bbf_scaling`: unnormalized against "up to positive rational scale" | Decided, not the defect: persists after the fix |
| Kuga–Satake, Corollary 1.3 | field `t_definition`: NS(S)⊥ in V against h⊥ | Decided, not the defect: off the defect location |
| Ashkin–Teller, Proposition 4.4 | fields `level`, `stopping_side`: −a from below against 2a from above | Decided, not the defect: the passage states that it uses the reflected construction |

The remaining FINDINGS are the undischarged-hypothesis artefacts of the earlier runs:

- representative ranges for an unbounded n;
- a condition attached to another part of a cited proposition. Three uses of Aru–Sepúlveda–Werner, Proposition 2, now
  name part (2) as their `case`. The hypothesis of part (1) is still checked against them, because cases do not yet
  select hypotheses (section 4, gap 1).

## 3. A post-hoc fix and what it shows (not pre-registered)

Reading the withdrawals' MATCHes showed a gap against M8 (a non-answer never becomes an answer). A convention whose
compared items agree counted as MATCH even when the cited side typed further items the citing side was silent on.

ADR-088 therefore adds PARTIAL. If the compared items agree but a typed item is silent on one side, the outcome is a
non-verdict, and the citation check lists the silent items as open. This change came after the run, so it is reported
here apart.

- **The pre-registered results are unchanged.** Per-defect verdicts, alarm loads and seams outcomes are identical
  before and after the fix; only per-convention labels move from MATCH to PARTIAL. The committed results file was
  produced with the fixed code.
- **What it shows at the withdrawals.** At all three uses of the trace-sign lemma (Lemma 3.4), the open items include:
  - `sign: field branch_order (citing side silent)`;
  - `sign: field intersection_sign_reference (citing side silent)`.

  The cited lemma fixes which branch comes first and against which orientation the double-point sign is read. The
  citing passages never say. The withdrawal notices put the error in exactly this place: the source orientations of
  the two branches of the standard cusp.
- **It is a pointer, not a detection.** PARTIAL conventions are as frequent away from the defect locations (14) as
  at them (14). The pointer is the right question for a reviewer, and nothing more.

## 4. Next gaps, re-ranked

1. **Cases that select hypotheses.** A citation that names part (2) of a result should be checked against part (2)'s
   hypotheses only.
2. **Compliance checks on typed inputs.** A field whose name matches a declared case name, or a field value that
   encodes a condition ("X if n even …"), should be refused at registration. The two remaining artefacts are of
   these kinds.
3. **Local formal checks of sign computations inside a construction.** The withdrawals are now narrowed to an
   orientation that the citing passage leaves unstated. Deciding it needs the construction itself, as a finite
   computation over the orientations of the two branches.
4. **A chain input kind for a citation inside a proof**, and **a premise-status feed** (unchanged).
5. **Unbounded integer ranges in citing contexts** (unchanged; the "n > 2" artefacts).

**Follow-up.** Gaps 1 and 2 were addressed by
[ADR-089](../../decisions/ADR-DISCOVERY-089-CASE-SCOPED-HYPOTHESES.md) and measured in
[`OPENAI_MATH_CASES_RESULTS.md`](OPENAI_MATH_CASES_RESULTS.md).

## 5. Deviations

- **The PARTIAL outcome** was added after the run (section 3). It does not change any pre-registered result.
- **A typist ran a script it did not write.** One context typist (c1) ran, by mistake, a build script written in an
  earlier run, which rewrote `scratchpad/typed/c1_typed.json`. The rewritten file is identical to the committed and
  frozen `openai_math_typed_contexts.json` (checked). The typist reports that it did not read the earlier encodings.
  Its own output was produced by its own script.
- **Entry typists did not download sources.** They typed from the entry texts, which their instructions allowed.

## 6. Reproduction

```bash
python scripts/benchmarks/openai_math_revision_bench.py typed --variant constrained
python -m python.cli.main regression check --case openai_math_time_travel
```

Regression expectations are now version 6. They include the `constrained/*` observations.
