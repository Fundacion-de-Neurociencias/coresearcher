# openai/math time-travel benchmark, re-run with the full verification chain: results

Protocol: [`OPENAI_MATH_CHAIN_PROTOCOL.md`](OPENAI_MATH_CHAIN_PROTOCOL.md), SHA-256
`0a0dc18aeda0b56ccc94a30b8f180ae368e5cc1cdce4c76ad9f36a87f303ae83`. It was frozen in commit `139019d` and in the ADR-085
freeze log ([`openai_math_chain_freezes.json`](openai_math_chain_freezes.json)) at 2026-11-01T09:38:38Z, before any
registry entry was written.

Inputs, each frozen before the next step:

| Input | SHA-256 | Frozen at (UTC) |
| --- | --- | --- |
| [`openai_math_chain_registry.json`](openai_math_chain_registry.json): blind registry entries | `57f1fa28…` | 2026-11-01 09:49:26 |
| [`openai_math_chain_contexts.json`](openai_math_chain_contexts.json): blind citing contexts | `7143c53a…` | 2026-11-01 09:54:20 |

Results are in [`openai_math_chain_results.json`](openai_math_chain_results.json). The runner is
`scripts/benchmarks/openai_math_revision_bench.py chain`.

## 1. Question and answer

Blocks A–E (ADR-080, 082, 083, 084, 085, 086) were built after the first run of this benchmark found that
CoResearcher caught **1 of the 17** real defects corrected in `openai/math`. The question here is how much they
improved that result.

**Answer: on the protocol's own count, a lot. On what the flags actually establish, not yet.**

| | First run (2026-10-30) | This run: protocol count | This run: adjudicated |
| --- | --- | --- | --- |
| Defects detected | 1 HIT that reflects the defect, plus 1 chance HIT. Total 2/17 (0.03–0.34) | **11/17** (0.41–0.83) | **1/17** decided (0.01–0.27), unchanged |
| Defects whose seam is flagged with both conventions side by side | 0 | — | **3/17** (0.06–0.41): the three withdrawals |
| Undetermined | — | — | 1: *two-arc GFF* |
| Coincidences | 1 | — | 6 |

Intervals are Wilson 95%. With 17 defects, none of these rates is a performance claim.

- **The protocol count rises from 2 to 11.** The rise is real under the pre-registered rules. Most of it is not
  detection.
- **The registry audit flags almost every use.** `REGISTRY_AUDIT` flags 86% of the uses at defect locations and 68% of
  the uses elsewhere.
- **The chain flags about one use in three, wherever it is.** `CHAIN_SEAMS` flags 39% of the uses at defect locations
  (11/28; 0.24–0.58) and 27% of the uses elsewhere (11/41; 0.16–0.42). That is not a separation.
- **What the blocks did add is a sharper pointer at the withdrawals.** At the stabilization-trace passage of all three
  withdrawals, the chain's seams step reports that the cited sign convention and the citing convention differ. It
  shows both texts:
  - The cited source defines the Whitney intersection sign and states that reversing the homotopy changes the sign.
  - The citing passage assigns trace signs (-1)^{k-1} and (-1)^k.

  A reviewer reading that finding looks exactly where the error was. The check does not decide the sign, though. It
  compares convention strings, and it raises the same finding at citations that are correct.

## 2. What ran

- **Selection.** The selection is mechanical (protocol, section 3):
  - **18 involved results.** Every numbered cited result used at a defect location.
  - **8 decoy results.** Drawn with seed 20261101. Two decoy sources could not be obtained: the Kollár–Mori book and
    the 1987 Kawamata–Matsuda–Matsuki chapter, which sits behind a bot wall. The next two in draw order replaced them,
    and the last two drawn were not used.
- **Uses.** 69 uses of the 26 registered results: 45 in 12 pre-fix sources (28 of them at defect locations) and 24
  in 7 corrected sources. No citation-update pair or never-revised control cites a registered result (the one control
  use found by the selection is of a decoy whose source was not obtained).
- **Registry entries (ADR-083).** Written by four fresh agents. Each saw only the bibliography entries and the
  locator, and read the cited work itself: arXiv sources, the authors' PDFs, or for collection companions the `.tex`
  at `PRE`. Their instructions are in
  [`openai_math_chain_procedure/WRITER_INSTRUCTIONS.md`](openai_math_chain_procedure/WRITER_INSTRUCTIONS.md). The
  coordinator made no content or schema repairs.
  - One writer at first skipped its seventh packet, a decoy. It was asked to finish it under the same instructions.
  - Entry numbering was checked against the counters of each LaTeX source. For example, the cited Li–Zhang result is
    Corollary 1.1 in the journal and Corollary 1.4 on arXiv.
- **Citing contexts.** Encoded by three fresh agents. Each saw shuffled, opaque packets and no manuscript names. Their
  instructions are in
  [`openai_math_chain_procedure/ENCODER_INSTRUCTIONS.md`](openai_math_chain_procedure/ENCODER_INSTRUCTIONS.md).
  - 27 of the 69 contexts declare variables.
  - 22 of the 69 contexts state a convention.
- **Checks on every use.**
  - The ADR-082 manuscript audit with the registry (`REGISTRY_AUDIT`).
  - The full ADR-085 chain (`CHAIN_SEAMS`): freeze, formalize (SUPPLIED), fidelity, vacuity, obligations, seams,
    discharge, trust ladder.

### Seams outcomes over the 69 uses

| Outcome | Uses |
| --- | --- |
| CLEAR | 0 |
| FINDINGS | 22: 28 convention-string findings and 7 undischarged hypotheses |
| INCOMPLETE | 45 |
| INVALID_INPUT | 2 |

- **INVALID_INPUT.** The two failing contexts used `**` and an undeclared constant. The chain refused them instead of
  guessing (M8).
- **No use came out CLEAR.** A citation cannot be cleared unless every hypothesis is formal and every convention is
  stated. Mathematical citations almost never meet that bar.

## 3. Per-defect results

Columns:

- **Baseline**: the first run's verdict.
- **Audit / Chain**: the two new checks.
- **Combined**: the protocol verdict over all checks.
- **Adjudication**: a reading by hand of each HIT, as in the first run.

| Defect | Baseline | Audit | Chain | Combined | Adjudication |
| --- | --- | --- | --- | --- | --- |
| Exact BSD from low Selmer corank | **HIT** | NE | NE | HIT | Reflects the defect (unresolved citation, first run) |
| Weil eightfolds (withdrawn) | NE | HIT | HIT | HIT | **Seam flagged**: sign-convention finding at the passage named in the withdrawal notice; lexical |
| Kuga–Satake for K3 (withdrawn) | NE | HIT | HIT | HIT | **Seam flagged**, as above |
| Products of K3 (withdrawn) | NE | HIT | HIT | HIT | **Seam flagged**, as above |
| Taming implies compatibility | NE | HIT | HIT | HIT | Coincidence (see below) |
| Conditional good minimal models | NE | MISS | HIT | HIT | Coincidence: both sides name κ_σ; only the wording differs |
| GFF limit, two-arc boundary data | NE | MISS | HIT | HIT | Undetermined (see below) |
| Finite ordinary MMP | NE | HIT | NE | HIT | Coincidence: phrase-match misses on 6 of 6 uses |
| Log abundance | NE | HIT | NE | HIT | Coincidence: phrase-match misses |
| Ashkin–Teller currents | NE | HIT | NE | HIT | Coincidence: phrase-match misses |
| Uniform real Lipschitz surfaces | HIT\* | NE | NE | HIT | Chance HIT of the first run; the new checks flag the location but the flags persist on the corrected version |
| Deforming hypersymplectic | NE | NE | NE | NE | No numbered cited result at the location |
| Weighted Lipschitz GFF | NE | NE | NE | NE | — |
| Incompressible Box Transport | NE | NE | NE | NE | — |
| Numerical semiampleness | NE | NE | NE | NE | No numbered cited result at the location |
| Termination, canonical flips | NE | NE | NE | NE | No numbered cited result at the location |
| Termination, log canonical flips | NE | NE | NE | NE | No numbered cited result at the location |

NE = NOT_ENCODABLE. No defect is a MISS overall.

### The withdrawals: the right seam, by string comparison

- **Where the findings land.** The stabilization-trace passage cites Ekholm–Eliashberg–Murphy–Smith, Lemmas 3.2 and
  3.4, and Eliashberg–Murphy, Theorem 2.3. At every one of these uses the seams step returns FINDINGS. Its main
  finding is `convention 'sign' differs`, and it puts the two texts next to each other:
  - **The cited lemma**, as the blind writer recorded it from arXiv:1303.0588v2: the index of a double point is the
    Whitney intersection sign, and for n even I({h_t}) = −I({h_{1−t}}).
  - **The citing passage**, as the blind encoder recorded it: the outward trace has sign (−1)^{k−1}, the reverse
    trace (−1)^k, and for k = 4 the reverse trace has sign +1.
- **What the finding does not do.** The defect named in the withdrawal notice is exactly a sign imported under the
  wrong orientation convention, and this is the comparison a reviewer needs. But nothing in the chain *decides*
  that the citing sign is wrong. It reports inequality of two strings. The same finding appears at the
  Eliashberg–Murphy citation outside the location in the Weil paper, and at 6 of 17 off-location uses in the defect
  manuscripts.
- **Spurious findings mixed in.**
  - Two "hypothesis not discharged: n > 2" findings come from the encoder's representative range 0–12 for an
    unbounded n. They are not about the defect.
  - Some convention findings (for example `dimension`) differ only in wording.
- **Compared with ADR-077.** The import obligations of ADR-077 already put an OPEN obligation at these passages
  (post hoc, in-sample). The chain turns it into a finding that shows both conventions. That is better than a bare
  OPEN obligation, but it is not a decision.

### Taming: the registry says the cited result supports the pre-fix claim

- **Why the HIT is a coincidence.** It comes from two convention strings, `grading` and `orientation`, that differ
  only in wording.
- **What the encoder found.** The passage applies Li–Zhang's b⁺ = 1 hypothesis only to the second assertion, so the
  hypothesis was DISCHARGED.
- **The more important finding.** The blind entry records Li–Zhang, Corollary 1.1, as
  K_J^t = K_J^c + H_J^- for *every* almost complex 4-manifold with nonempty K_J^c. The entry says this follows from
  their Theorem 1.1 and from the Drăghici–Li–Zhang result that every almost complex structure on a 4-manifold is C^∞
  pure and full.
- **Why the chain cannot catch it.** The corrected manuscript restricts the equality to h_J^- = b_2^+ − 1 and gives a
  four-torus example of strict inclusion. If both the entry and the corrected manuscript are right, then the error
  sits in the cited result or in its premise, not in the citing paper's use of it. Such an error is invisible to any
  check at the seam. It is the case premise retraction (ADR-083, M11) is meant for.
- **What would close it.** A retraction or downgrade of the registry entry, which needs someone to record the fallen
  premise. This benchmark does not judge which statement is correct. That would require reading the literature on
  fullness, which is outside formal soundness.

### Two-arc GFF: undetermined

- **The finding.** The pre-fix passage imports Glazman–Manolescu, Theorem 1.2(iv). It says itself that "the source's
  contour-distance convention differs by a bounded additive offset", and absorbs that offset by choosing ρ. The seams
  step flags exactly this normalization mismatch.
- **The fix.** The correction removed the import and re-derived the estimates from the companion annulus circuit
  theorem at x = 1.
- **Why it stays undetermined.** The flag sits on the import that the fix replaced. Neither the version note nor the
  diff says that the convention transfer was the error, so the hit is neither confirmed nor dismissed.

## 4. Alarm load

Flags on uses away from any defect location are unconfirmed alarms.

| Check | Off-location uses in the pre-fix sources | Uses in the corrected sources |
| --- | --- | --- |
| `REGISTRY_AUDIT` (phrase-matched hypotheses missing) | 10 of 17, in 6 manuscripts | 18 of 24, in 6 manuscripts |
| `CHAIN_SEAMS` (FINDINGS) | 6 of 17, in 5 manuscripts | 5 of 24, in 3 manuscripts |

- **The registry audit is unusable as a detector.** The writers' phrases are reasonable, but papers rarely restate a
  cited result's hypotheses in the same words, so UNMATCHED is the normal outcome. ADR-082 already says that a phrase
  match is not a discharge. The run shows that a phrase *miss* is not evidence either.
- **The chain's alarms are of two kinds.**
  - **Wording.** Convention strings that name the same convention in different words. ADR-083 calls this "the safe
    direction".
  - **Representative ranges.** Encoders bounded an unbounded quantity, which produced counterexamples outside the
    passage's real range.
- **No control and no citation-update pair uses a registered result**, so the run measures alarm load on the defect
  manuscripts and their corrected versions only, not on never-revised work.

## 5. Premise retraction (reported apart)

- **Seeds.** The 8 pre-fix manuscripts where `CHAIN_SEAMS` flagged any use. They were chosen from the flags, never
  from the ground truth.
- **What propagation reaches.** Collection links reach 7 dependents. All 7 are defect manuscripts, including:
  - *Deforming hypersymplectic*, through *Taming*: its real dependency;
  - the two K3 withdrawals, through *Weil*.
- **Why this is not evidence.** The seeds are noisy (section 4), and the revised manuscripts form a dense cluster of
  companions that cite one another. Propagation shows that the mechanism works end to end. It is not evidence of
  detection.

## 6. What the blocks did not change

1. **No new defect is decided.** The only decided detection is still the unresolved citation that the first run found.
2. **The other eleven defects are untouched.** None of the four argument-gap revisions in the probabilistic group,
   the two birational argument gaps, the effective-constants revision or the dependency clarifications is reached by
   any mechanism of blocks A–E.
3. **Block A (vacuity, trust ladder, fidelity services) has no input here.** Citing contexts declare no non-witnesses
   and no fidelity specification, so those steps are OPEN on every use.
   - The trust ladder keeps every manuscript claim at CLAIMED.
   - The ledger roll-up is REFUTED on every use. The adapter's placeholder claim forbids no state, so the
     falsifiability obligation (ADR-076, ADR-085) refutes it. This says nothing about the manuscript. It shows that
     the chain has no input kind for "a use of a cited result inside a proof": it expects a hypothesis with content.
4. **Block E (biomedical units, conventions, probes) does not apply to a mathematics corpus.**
5. **The Lean checks are unchanged.** The two families with Lean notes still do not formalize the corrected claims, and
   the Comparator kernel check is still not run in our environment.

## 7. Next capability gaps, ranked by the defects still missed or only flagged lexically

1. **Semantic comparison of conventions.**
   - *Defects it addresses*: the 3 withdrawals, the 2 coincidences from convention wording, and most of the chain's
     alarms.
   - *What it needs*: sign and orientation conventions as typed objects (orientation of each source branch, sign of
     a reversed homotopy, normalization of distance) and a decision procedure that says MATCH or MISMATCH from those
     objects instead of from text.
   - *What it would change*: the three withdrawals could become decided findings. In the Weil paper the needed fact
     is small: in the source's convention a reversed trace changes sign, and the citing paper's two branches carry
     opposite source orientations.
   - *Tractability*: highest of the list.
2. **A chain input kind for citations inside a proof.**
   - *What it needs*: the citing claim (what the proof derives from the cited result) and the cited statement, with
     the chain checking that the conclusion used is the conclusion stated.
   - *What it would fix*: today the chain needs a hypothesis with content, so the ledger roll-up for a citation is
     meaningless (section 6, point 3).
   - *Defects it addresses*: the 6 Kähler revisions whose fixes state which inputs are used.
3. **Premise status for cited results (M11 in practice).**
   - *Motivated by*: *Taming*, where the blind entry supports the pre-fix claim. Only a recorded downgrade of the
     cited result, or of its premise, would flag the use.
   - *What it needs*: a feed of corrections and errata for registered results, and dependency edges from a result to
     the premises it rests on, so that a fallen premise lowers its rung.
4. **Hypothesis extraction with ranges from context.**
   - *Motivated by*: the spurious NOT_DISCHARGED findings. Encoders bounded unbounded quantities by representative
     ranges, which produced counterexamples outside the real range.
   - *What it needs*: an encoding that allows an unbounded integer (z3) instead of a finite range.
5. **The mechanisms ranked by the first run that remain unbuilt:**
   - effective-constant obligations with a decision (*Incompressible*);
   - small-instance counterexample search for cone and lattice claims (*Taming*'s four-torus example);
   - an answer for argument gaps (Lipschitz, Ashkin–Teller, finite ordinary MMP, log abundance), which have no near-term
     static mechanism. The options are formalization (the Lean route) or adjudicated step-level critique.

Keep the citation gate. It is still the only decided detection on this corpus.

**Follow-up.** Gap 1 was built as [ADR-087](../../decisions/ADR-DISCOVERY-087-TYPED-CONVENTIONS.md) and measured
under its own pre-registered protocol in [`OPENAI_MATH_TYPED_RESULTS.md`](OPENAI_MATH_TYPED_RESULTS.md). It removed
most lexical noise and decided nothing new. The withdrawals' sign error lies in the citing construction, not in a
convention of the cited lemma. Since ADR-087, the regression replay of this run uses the new semantics (expectations
version 5).

## 8. Deviations from the protocol

- **Code added after the freeze.** The commands `chain-registry`, `chain-contexts` and `chain-fixture`, the offline
  replay, and the propagation report. The encodability table moved from the script to
  `python/discovery/openai_math_chain.py`, with identical content. No selection rule, encodability judgement, scoring
  rule, entry or encoding changed. Re-running `chain` after the propagation report was added gave identical scores,
  alarms and per-use records.
- **Encoder assignment.** The protocol did not say how packets were divided among encoders. They were split in
  shuffled order, every third packet to the same encoder.
- **Writer completion.** One writer skipped a decoy packet and was asked to complete it under the same instructions.
- **An added analysis.** The protocol's chance baseline is per source line. Because the selection concentrates the
  scored uses at defect locations, that baseline is close to zero for every HIT and says little here. The
  per-use comparison in sections 1 and 4 (flags at the location against flags elsewhere) was added after the run. It
  is reported next to the protocol verdicts and does not replace them.

## 9. Regression (ADR-084)

- **What the case replays.** The `openai_math_time_travel` regression case now replays this run offline from:
  - the frozen entries and contexts;
  - `benchmarks/regression/fixtures/openai_math_chain.json.gz`, the environments that the audit reads at each use. Its
    builder refuses to write it unless the audit on each excerpt reproduces the full sources' outcome at every use.
- **What it freezes.** Per-defect verdicts for both new checks and their alarm counts. Expectations version 4.
- **Check.** The offline replay reproduces the full run's per-defect verdicts and alarm load exactly.

## 10. Reproduction

```bash
python scripts/benchmarks/openai_math_revision_bench.py chain-select   # selection; refuses if the protocol changed
python scripts/benchmarks/openai_math_revision_bench.py chain          # verifies every freeze, then runs
python -m python.cli.main regression check --case openai_math_time_travel
```
