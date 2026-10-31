# Time travel on openai/math: would our checks have caught the real corrections?

This case explains, in context, what was done, why, how, what it found, what was built from it, and what it is
for. The technical records are:

- [the pre-registered protocol](../benchmarks/OPENAI_MATH_REVISION_PROTOCOL.md);
- [the results](../benchmarks/OPENAI_MATH_REVISION_RESULTS.md);
- [ADR-DISCOVERY-077](../../decisions/ADR-DISCOVERY-077-IMPORT-OBLIGATIONS.md), the decision taken from the
  results.

## 1. Why

CoResearcher judges the formal and mathematical soundness of claims. Its earlier measurements on the openai/math
corpus used **proxies**:

- The statement-fidelity pilot mutated Lean statements by hand (a changed constant, a swapped quantifier). It
  asked whether a detector notices. The first detector scored AUROC 0.52, near chance.
- Mutations show what a check can see in principle. They do not show whether it would find the errors that
  actually occur in research mathematics.

The openai/math release history contains **real errors with an independent ground truth**. On October 7, 2026 the
authors revised 14 manuscripts and withdrew 3. History.md, each revised edition's version note and each
withdrawal notice say what was wrong. The pre-fix and corrected sources are both in git.

So the question can be asked without proxies: **run our checks on the source as it stood before the fix, and see
whether they point at the defect the authors later corrected.**

## 2. What for

- **To measure real verification power**, not mutation sensitivity. A check that never fires at a real defect
  location is not protecting anyone, however well it detects synthetic mutants.
- **To decide what to build next from evidence.** The misses say which mechanism would have caught each defect.
  That gives a ranked list grounded in actual failures rather than in intuition.
- **To keep the false-alarm cost visible.** A check is only usable if a reviewer can afford to read its flags.
  Every rate is reported against corrected versions and never-revised manuscripts.
- **To prepare a prospective test.** The mechanisms built from this benchmark are frozen. Future corrections in
  the same corpus become out-of-sample ground truth.

The scope is verification only. Nothing here judges credit, priority or the release announcements, and no
hypothesis or proof is generated.

## 3. How

### 3.1 Recovering the ground truth

- `openai/math` has about 174k files, mostly Lean. It was read through a blobless clone with sparse worktrees,
  so only the 74 manuscript directories in the dataset were downloaded. All downloaded content was treated as
  untrusted data, and none of it was executed.
- The history has only 9 commits. All 17 fixes are in one commit, `3014888`. The pre-fix state is the initial
  commit, `adc7f12`.
- Revised manuscripts get a new, later-dated directory; the old edition stays in the tree unchanged. Pairs were
  matched by stripping the date from the directory name.
- The 27 new editions split into:
  - **14 substantive revisions**, the ones `history.md` lists;
  - **13 citation-only updates**, which became a near-null comparison group.
- **Defect locations:**
  - For revisions: the pre-fix lines the authors changed, computed with a line diff. Hunks that only touch a date
    or a companion-paper link were excluded.
  - For withdrawals: the stabilization-trace passage the withdrawal notice names, fixed by hand.
- **Controls:** 17 never-revised manuscripts, one per defect, drawn with a fixed seed and taken from the same
  result family where possible.

### 3.2 Pre-registration

The protocol was written and committed with its SHA-256 before any check touched the corpus. It fixed in advance:

- the checks;
- the definition of a HIT: a flag at the defect location that disappears in the corrected version;
- the false-alarm measures;
- for each defect and check, whether the defect even lies inside that check's language. This separates a MISS
  from NOT_ENCODABLE.

The runner refuses to start if the protocol's hash has changed. Code changes made after the freeze are listed as
deviations in the results. They fixed an exact-arithmetic hang and file line endings, and changed no rule.

### 3.3 The checks run

| Check | Idea |
| --- | --- |
| Statement fidelity and the Lean junk-value lint (ADR-070) | Compare the paper and the Lean statement |
| Citation resolution | Every `\cite` key resolves |
| Identity check, strict and context tiers | Obligation-ledger style: is a displayed equality actually true? |
| Exponent bookkeeping | Exponents agree across `\asymp`-type relations |

The Lean checks could run only where a Lean note exists. That was 2 of the 17 families, and neither Lean
statement covers the corrected claim.

## 4. What was found

- **1 of 17 defects detected for real.** The pre-fix *Exact BSD from low Selmer corank* cites `\cite{Dv}`, a key
  with no bibliography entry: the "obsolete citation to a removed manuscript" of the version note. The citation
  check flagged it with zero false alarms over all 47 manuscripts.
- **1 chance HIT.** A context-tier flag landed inside a large rewritten passage of *Uniform real Lipschitz
  surfaces*. It recalls a correct definition, and the chance baseline already expected at least one flag there.
- **15 NOT_ENCODABLE.** No existing check speaks the language these defects live in.
- **The identity and exponent checks found nothing real.** Every strict flag was notation the parser misread:
  - `H^0=0` read as a power rather than cohomology;
  - `-1=1` in characteristic 2;
  - `\simeq` meaning isomorphism.

  The context tier flags 4–6 conditional equations per 1000 lines.

The central finding is **where errors live in this corpus**. It is not in displayed algebra. It is where a proof
**imports** something from a cited source:

- **A sign imported under another convention.** The three withdrawals all rest on a sign taken from a cited
  stabilization-trace lemma. Under the paper's own orientation convention that sign is wrong. The displayed
  arithmetic, I(f₁) + m = 0, is perfectly consistent with the wrong sign, which is why no algebra check can see it.
- **A theorem applied beyond its hypotheses.** The taming paper's corollary applied Li–Zhang's cone comparison
  without that result's hypothesis. The correction restricts the claim and gives a four-torus counterexample.
- **Dependencies on companions that changed.** Two withdrawals inherit the error of the first. The hypersymplectic
  paper depended on the faulty taming corollary.
- **A citation to something that no longer exists** (Exact BSD).
- **An "effective" bound left without an effective constant** (Incompressible Box Transport).

## 5. What was built from it

ADR-DISCOVERY-077 turns that finding into mechanisms, ranked by the defects that motivate them:

1. **The citation gate** (`scripts/checks/citation_gate.py`) becomes a standing first step of any manuscript audit.
2. **Import obligations** (`python/discovery/cited_import_ledger.py`). Every import becomes an OPEN obligation in
   the ADR-076 ledger, with its file and line:
   - **convention transfer**: an imported sign, orientation or normalization;
   - **hypothesis match**: a cited theorem used in a proof, matched against a registry of cited results when one
     exists;
   - **dependency**: a link to a withdrawn or corrected companion, propagated transitively;
   - **effective constant**: an effective claim with an unspecified constant.

   The obligations prove nothing. They make the risky step visible and keep the claim from being reported as
   verified until someone discharges them.

Run on the same frozen dataset (in-sample, since the mechanisms were designed after reading the defects):

- **All three withdrawals** get an OPEN convention-transfer obligation exactly at the passage their withdrawal
  notice names. Chance would expect 0.02–0.06 per manuscript.
- **The taming corollary** gets an OPEN hypothesis-match obligation at the Li–Zhang citation it misapplied.
- **Propagation**, seeded with the Weil withdrawal and the taming correction, flags exactly the two dependent
  withdrawals and the hypersymplectic paper, and nothing else.
- **With the citation gate, 6 of 17 defects are covered beyond chance.** The other 11 are not:
  - 6 Kähler revisions, which need registry entries;
  - 4 probabilistic argument repairs, out of reach of any static mechanism;
  - the Incompressible estimate, which the sentence window missed.
- **The cost** on never-revised manuscripts is about 3 hypothesis-match, 0.85 convention-transfer and 0.7
  effective-constant obligations per 1000 lines. That is roughly 25 imports to review in a 5000-line paper,
  each a real import rather than a parser artefact.

## 6. Limits

- **17 defects is a small sample.** Every rate carries a wide interval: 1/17 detected is 0.01–0.27 at 95%.
- **The in-sample figures are not detection power.** Only a prospective run on future corrections, with the code
  frozen in ADR-077, can measure that.
- **Detection is lexical.** An obligation at the right line is a prompt for a reviewer, not a verdict.
- **Many obligations will be ordinary, correct imports.** The cited-result registry is empty, so a
  hypothesis-match obligation means "check this" rather than "this is wrong".
- **Locations come from the authors' own diffs.** A large rewrite produces a large location, and the chance
  baseline is reported for exactly that reason.

## 7. Next

- **Run the prospective test** when the next corrections appear.
- **Fill the cited-result registry** from reviews. Once a theorem is encoded, every later citation of it is
  matched automatically.
- **Build the remaining ranked mechanisms:**
  - small-instance counterexample search (the four-torus strict inclusion);
  - notation-aware identity checking;
  - a cross-paragraph window for effective constants.

## 8. Reproduce

```bash
python scripts/benchmarks/openai_math_revision_bench.py dataset   # ground truth from git history
python scripts/benchmarks/openai_math_revision_bench.py run       # pre-registered run (checks the protocol hash)
python scripts/benchmarks/openai_math_revision_bench.py posthoc   # ADR-077 mechanisms, in-sample
python scripts/checks/citation_gate.py path/to/manuscript/build   # the standing gate
python -m pytest tests/test_manuscript_checks.py tests/test_cited_import_ledger.py
```
