# openai/math time-travel benchmark: typed conventions (ADR-087), results

Protocol: [`OPENAI_MATH_TYPED_PROTOCOL.md`](OPENAI_MATH_TYPED_PROTOCOL.md), SHA-256 `ca6a82fd…`. It was frozen at
2026-11-01T18:50:13Z in the ADR-085 freeze log, before any convention was typed.

Inputs, each frozen before the next step:

| Input | SHA-256 | Frozen at (UTC) |
| --- | --- | --- |
| [`openai_math_typed_registry.json`](openai_math_typed_registry.json) | `e21644c9…` | 18:53:57 |
| [`openai_math_typed_contexts.json`](openai_math_typed_contexts.json) | `6a5a765a…` | 19:00:05 |

Results are in [`openai_math_typed_results.json`](openai_math_typed_results.json). The implementation is
[ADR-087](../../decisions/ADR-DISCOVERY-087-TYPED-CONVENTIONS.md).

## 1. Question and answer

The full-chain re-run ranked first the semantic comparison of conventions. There, the seams step compared conventions
as strings, so it flagged citations at about the same rate wherever they were. ADR-087 makes conventions typed:
fields are compared as atoms, signs as integer formulas, and two texts that differ are a non-verdict instead of a
MISMATCH.

**Answer.** The noise falls by about half, but no defect is decided. The convention the withdrawals got wrong is not
in the cited lemma's statement.

`CHAIN_SEAMS` flags, by input:

| Input | At defect locations | Elsewhere | Defects with a protocol HIT |
| --- | --- | --- | --- |
| Chain re-run, string comparison (expectations v4) | 11/28, 39% (0.24–0.58) | 11/41, 27% (0.16–0.42) | 6 |
| Same frozen inputs, ADR-087 semantics (code change only) | 3/28, 11% (0.04–0.27) | 4/41, 10% (0.04–0.23) | 2 |
| Typed blind on both sides (this protocol) | 6/28, 21% (0.10–0.40) | 6/41, 15% (0.07–0.28) | 3 |

Decided detections that reflect a defect, all checks together: **1/17** (0.01–0.27). It is still the unresolved
citation found by the first run.

## 2. What ran

- **Typed registry conventions.** Two fresh agents typed all 26 registry entries. They saw only the entries, never a
  citing text.
  - 25 entries got at least one typed field or sign.
  - Five entries have integer sign formulas. Two of them:
    - Ekholm–Eliashberg–Murphy–Smith, Lemma 3.2: `reversal_sign = (-1)**(n+1)`, the factor relating a homotopy's
      index to its reverse;
    - Eliashberg–Murphy, Theorem 2.3: `branch_swap_sign = (-1)**(n*n)`.
- **Typed citing conventions.** Three fresh agents typed all 69 citing conventions, from the same shuffled, opaque
  packets as the chain re-run.
  - 21 packets state no convention for any tag of the entry.
- **The run.** Same flow as the chain re-run. Over all 69 uses:

  | Seams outcome | Uses |
  | --- | --- |
  | FINDINGS | 12 |
  | INCOMPLETE | 55 |
  | INVALID_INPUT | 2 (as before) |

  Per-convention outcomes:

  | Convention outcome | Count |
  | --- | --- |
  | MATCH | 43 |
  | MISMATCH | 5 |
  | UNCOMPARED | 25 |
  | Unspecified on the citing side | 76 |

## 3. Per-defect results (CHAIN_SEAMS)

| Defect | Chain re-run (strings) | Typed | Adjudication of the typed result |
| --- | --- | --- | --- |
| Weil eightfolds (withdrawn) | HIT | HIT | Decided, but not the defect: field `homotopy_direction` forward against reverse records which case of the lemma is used, not a convention |
| Kuga–Satake for K3 (withdrawn) | HIT | HIT | Decided, but not the defect (see below) |
| Products of K3 (withdrawn) | HIT | HIT | Decided, but not the defect (see below) |
| Taming implies compatibility | HIT | MISS | — |
| Conditional good minimal models | HIT | MISS | — |
| GFF limit, two-arc boundary data | HIT | MISS | — |
| The other 11 | NE | NE | — |

**Why the two K3 withdrawals' MISMATCH is an artefact.**

- **The finding.** `sign reversal_sign: cited (-1)**(n+1), citing -1 (at n = 3: 1 vs -1)`.
- **Why n = 3 does not count.** The citing passage works with n = 2k. On even n the cited reversal rule gives −1,
  exactly the citing value, so the counterexample lies outside the passage's domain. The typed schema has ranges but
  no parity constraint, and the typists could not express "n even".
- **What a constrained comparison would show.** On the shared domain the comparison is a MATCH. The cited lemma's
  reversal rule and the citing paper's trace signs agree.
- **Where the error is.** The withdrawal notices place the error in the source orientations of the two branches of
  the standard cusp. That is a property of the citing paper's construction, not a convention of the cited lemma's
  statement. Neither the registry typists nor the citing typists typed it, because neither text states it.
- **The remaining findings at the withdrawals.** They are the "n > 2 not discharged" artefacts of the chain re-run.
  The citing contexts give an unbounded n a representative range that starts at 0.

**Alarms elsewhere (6).**
- One decided field mismatch in a passage that states it uses the reflected construction: Aru–Lupu–Sepúlveda,
  first-passage sets from below against above.
- One decided field mismatch on the coefficient range of a boundary: Keel–Matsuki–McKernan, closed against half-open.
- Four undischarged hypotheses:
  - three from a condition that the registry entry attaches to another part of the cited proposition
    (Aru–Sepúlveda–Werner, part (1));
  - one from a representative range starting at 0.

None of the six is a defect the authors corrected.

`REGISTRY_AUDIT` does not read conventions, and its verdicts are unchanged.

## 4. What this teaches

1. **Typed comparison removes most of the lexical noise.**
   - It turns every UNCOMPARED convention into an explicit non-verdict instead of a finding.
   - Its decided mismatches are few (5 of 73 compared conventions). Each one names the field or the counterexample, so
     a reviewer can reject an artefact in seconds.
2. **Parameters need constraints, not only ranges.** Parity and side conditions such as "n = 2k" or "k ≥ 2" must
   travel with a typed sign. Without them, decided counterexamples come from outside the citing domain.
3. **A field must not record which case of a result is used.** Whether a citation uses a lemma for the forward or the
   reverse homotopy is a parameter of the use, not a convention. The schema should separate the two.
4. **The withdrawals' error is out of reach at the seam.**
   - The sign that went wrong comes from the citing paper's own construction: how the two branches of the standard
     cusp are oriented.
   - No convention of the cited lemma differs from the citing paper's on the shared domain.
   - Catching this class of error needs the construction itself to be checked. That means formalizing the local sign
     computation (the Lean route), not comparing conventions.

## 5. Next gaps, re-ranked

1. **Constraints on typed parameters**, and a separate slot for which case of a cited result is used. This is a small
   change to `typed_conventions`, and it removes the artefacts above.
2. **Local formal checks of sign computations inside a construction.** This is the only route found so far to the
   withdrawals. A first target: the signed double-point count of a stabilization trace, as a finite computation over
   orientations.
3. **A chain input kind for a citation inside a proof** (unchanged from the chain re-run).
4. **A premise-status feed for cited results** (unchanged; *Taming*).
5. **Unbounded integer ranges in citing contexts.** This removes the "n > 2" artefacts.

**Follow-up.** Gap 1 was built as [ADR-088](../../decisions/ADR-DISCOVERY-088-CONSTRAINED-CONVENTIONS.md) and
measured in [`OPENAI_MATH_CONSTRAINED_RESULTS.md`](OPENAI_MATH_CONSTRAINED_RESULTS.md).

## 6. Deviations

- **Entry packets.** Split in registry order between the two entry typists, not shuffled. The entries carry no
  citing text, so the order reveals nothing.
- **Coordinator repairs.** None to any typed record.
- **Typists did not download.** Both entry typists typed from the entry texts without re-reading the sources, which
  the instructions allowed.
- **Regression.** The `openai_math_time_travel` case now replays this run as well (`typed/*` observations). Its
  expectations are version 5, frozen in the same pull request together with the ADR-087 change to the chain re-run's
  replay.

## 7. Reproduction

```bash
python scripts/benchmarks/openai_math_revision_bench.py typed   # verifies the protocol and every freeze, then runs
python -m python.cli.main regression check --case openai_math_time_travel
```
