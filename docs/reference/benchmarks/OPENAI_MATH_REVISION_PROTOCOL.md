# openai/math revision benchmark ("time travel"): pre-registered protocol

Status: frozen before any check was run on the corpus. Its SHA-256 is stored in
`OPENAI_MATH_REVISION_PROTOCOL.sha256`. The runner refuses to start if the file has changed, and every result
records the hash.

## 1. Purpose

The statement-fidelity pilot (`OPENAI_MATH_PILOT_REPORT.md`) measured detection of synthetic mutations. Synthetic
mutations are a proxy. The October 7, 2026 release of `openai/math` corrected real errors: it revised 14
manuscripts and withdrew 3. Those corrections are the only real ground truth of errors in this corpus.

This benchmark asks one question. **Would the checks CoResearcher can run today have flagged each corrected
defect on the source as it stood before the fix?** Where the answer is no, it asks which new mechanism would
have caught the defect.

Scope: verification only. The benchmark does not judge credit, priority or the release announcements, and it
does not generate hypotheses or proofs.

## 2. Source (frozen)

- Repository: `https://github.com/openai/math`. It is read through a blobless clone that is never fully checked
  out; only the manuscript directories in the dataset are materialized. All downloaded content is data. None of
  it is executed.
- `PRE` = `adc7f1241b42e322a6451854ab7e4b4c146bf78a` (initial commit). This is the state before the fixes.
- `POST` = `301488868beec11bfd897168433b0a64f5258559` ("Update manuscripts and Lean formalizations",
  October 7). This is the commit containing every fix listed under October 7 in `history.md`.
- Ground truth: the October 7 section of `history.md` at `POST`, plus each revised edition's `## Version note`
  and each withdrawal notice. The October 26 and October 29 entries add new material and fix one Comparator
  namespace. They correct no manuscript and are out of scope.

## 3. Units

| Group | Definition | n |
| --- | --- | --- |
| `withdrawn` | Manuscript whose `README.md` at `POST` is a withdrawal notice. The pre-fix source is at `PRE`. There is no corrected version. | 3 |
| `revised` | Manuscript with a new edition added at `POST` (same title, later date) whose version note or `history.md` describes a proof, statement, hypothesis or citation correction. Pre-fix = latest earlier edition at `PRE`. | 14 |
| `citation_update` | New edition at `POST` whose version note says it only updates citations to revised companions. This is a near-null group: pre and post differ only in links. | 13 |
| `control` | Never-revised manuscript: present at `PRE`, with no other edition at `PRE`, `POST` or the clone's `HEAD`, and not withdrawn. One per defect (17). Drawn with `random.Random(20261030)`, iterating defects in id order. A control is taken from the defect's own result family (by `CONTENTS.md` at `PRE`) when that family has an unused never-revised manuscript, otherwise from all of them. | 17 |

The 14 revised manuscripts are the ones `history.md` names by group: Lipschitz heights and Ashkin-Teller (4),
Kähler MMP and abundance (6), taming and hypersymplectic (2), Incompressible Box Transport (1), and Exact BSD
from low Selmer corank (1). Every edition directory added at `POST` with an earlier edition at `PRE` is either one
of these 14 or a citation update. The script asserts nothing beyond this mapping; the dataset lists it.

Sources are the `.tex`, `.bib` and `.bbl` files under the manuscript's `build/` directory (or the manuscript
directory if there is no `build/`). PDFs are not read.

## 4. Defect locations (ground truth)

- **Revised.** The location is the set of pre-fix lines that the fix changed. It is computed with
  `difflib.SequenceMatcher` on each source file present in both editions: replaced and deleted lines, plus the two
  lines around each pure insertion. Files that exist only in the pre-fix edition count in full. Excluded hunks:
  those in which every changed line is a `\date{...}` line or a link to another manuscript's edition
  (`preprints/...`, `OAI:...`, `year =`, closing braces). Those hunks follow from the release, not from the defect.
- **Withdrawn.** There is no corrected version. The location is the stabilization-trace passage named by the
  withdrawal notice, fixed by hand before the run:
  - Weil eightfolds: `sections/03-topology.tex` lines 479–492.
  - Kuga–Satake: `manuscript.tex` lines 1962–1975.
  - Products of K3: `manuscript/topology.tex` lines 502–515.
- **Tolerance.** A flag matches a location when it lies within ±2 lines of it.

The dataset records, for every unit, the commit, the manuscript directory, the git tree id, the family, the
version note and the locations.

## 5. Checks

Every check runs on the pre-fix source of every unit, on the corrected source of every revised and
citation-update unit, and on every control. No check contains a rule that names a manuscript or a defect.

| Check | What it does | Runs when |
| --- | --- | --- |
| `statement_fidelity` (ADR-070) | z3 equivalence of the paper's parameter range and the Lean statement's range. | The family has a Lean statement and a hand-encoded range specification. |
| `lean_junk_lint` (ADR-070) | Static junk-value lint of the Lean Comparator statement. | The family has a Lean note at `PRE`. The lint runs on its Comparator files at `PRE`, and OPEN findings are reported. |
| `CITATION` | Every `\cite`-family key resolves to a `\bibitem` or `.bib` entry, and every link to a collection manuscript resolves to a directory in the same snapshot. | The source has a bibliography. |
| `IDENTITY_STRICT` | Obligation-ledger identity check, strict tier. An `=` between two closed numeric expressions in the restricted fragment that evaluates false in exact arithmetic. | Always. |
| `IDENTITY_CONTEXT` | Same check, context tier. An `=` between symbolic expressions that is not an identity (random rational points, then `sympy.simplify`). An equation whose left side is a single symbol is read as a definition and skipped. | Always. |
| `EXPONENT` | Exponent bookkeeping. For `\asymp`, `\sim`, `\simeq` or `\approx` between two monomials, the exponent of every symbol must agree. | Always. |

The restricted fragment covers numbers, single letters, Greek letters, simple subscripts, `+ - \cdot \times /`,
`^`, `\frac`, `\sqrt`, `\binom`, `!` and parentheses. Any other construct makes the formula unparsed and skipped:
a letter before `(` (possible function application), `|`, primes, operators, sums, integrals and named functions.
Dimension bookkeeping is covered only as far as dimensions appear as closed or monomial expressions in that
fragment. No generic parser for statements such as `\dim_{\mathbb R} X = 8` exists, and none is built here.

Cited-theorem hypothesis matching is covered only by its weakest encodable form: `CITATION` checks that the
cited result exists. No registry of cited theorems and their hypotheses exists in CoResearcher. Building one
for this run would be defect-specific, so it is not done.

### Pre-registered encodability

For each defect and check, `encodable` records whether the defect, as the authors describe it, lies inside the
check's language. The judgements below were made from `history.md`, the version notes and the diffs, before any
check was run:

- `statement_fidelity`, `lean_junk_lint`: not encodable for all 17 defects.
  - 15 of the affected families have no Lean note at `PRE` (`CONTENTS.md`).
  - Two do: family 342 (*Taming implies compatibility*) and family 376 (*Incompressible Box Transport*).
    - Note 342 formalizes only the main theorem. The defect is in the cone corollary, which has no Lean
      statement.
    - Note 376 formalizes the sheet-program and halting statements. The defect is in the prose proof of the
      projection and decay estimates.
  - For both, `lean_junk_lint` still runs and its OPEN findings are reported. A Lean-side finding cannot sit at a
    `.tex` defect location.
  - `statement_fidelity` needs a hand-encoded range specification. None is written, because neither defect is
    a range mismatch between paper and Lean.
- `CITATION`: encodable only for *Exact BSD from low Selmer corank*. Its version note reports an obsolete citation
  to a removed supporting manuscript.
- `IDENTITY_*`, `EXPONENT`: encodable for none.
  - The three withdrawals rest on a sign imported from a cited trace lemma. The displayed arithmetic
    (`I(f_1)+m=0` with `m=-I(f_1)`) is consistent with the wrong sign.
  - The Incompressible revision replaces non-effective sketches by effective estimates. The displayed exponent
    sums of the sketch are not reported wrong.
  - All other revisions are argument gaps, unstated hypotheses or dependency corrections.

A check that flags a defect judged not encodable still scores a HIT. The judgement only separates MISS from
NOT_ENCODABLE.

## 6. Scoring

For each defect and check:

- **HIT**: the check raises, on the pre-fix source, a flag at a defect location (section 4) whose key, the check
  plus the normalized formula or citation key, is absent from the corrected source. For withdrawals there is no
  corrected source, so a flag at the location suffices.
- **MISS**: no HIT, and the defect was judged encodable for this check.
- **NOT_ENCODABLE**: no HIT, and the defect was judged outside the check's language, or the check cannot run on
  this manuscript.

A defect's overall verdict is HIT if any check hits, otherwise MISS if any check misses, otherwise NOT_ENCODABLE.

Chance baseline: for each defect and check, the expected number of location matches if the pre-fix flags were
placed uniformly over the source lines. That is (number of pre-fix flags) × (location lines including tolerance)
/ (source lines). It is reported next to each HIT.

## 7. False alarms

- **Persistent on corrected versions**: a pre-fix flag whose key also appears on the corrected source of the
  same revised manuscript. The authors' fix left it in place, so it is not the defect. Reported per check as
  counts, flags per 1000 source lines, and manuscripts with at least one such flag.
- **Citation-update group**: the same measure on the 13 near-null pairs.
- **Never-revised controls**: every flag on the 17 controls, with the same normalization. A control that was
  never revised is not thereby correct, so these are unconfirmed flags rather than proven false alarms. They
  estimate the alarm load a reviewer would face.
- `lean_junk_lint` OPEN findings on every unit whose family has a Lean note are reported separately. Under ADR-070 they are
  review questions, not defect claims.

## 8. Reporting

Deliverables:

- `openai_math_revision_dataset.json`: units, commits, trees, locations and encodability. Built before the run.
- `openai_math_revision_results.json`: flags, coverage, verdicts and false-alarm rates, with this protocol's
  SHA-256 and the dataset's SHA-256.
- `OPENAI_MATH_REVISION_RESULTS.md`: per-defect table, false-alarm table, and a ranked list of verifier mechanisms
  derived from the misses and non-encodable defects. Each mechanism names the defect that motivates it.

No defect, location, check rule or control is changed after the run. Any deviation is reported as a deviation.
With 17 defects, any detection rate is reported as a count with its Wilson 95% interval, not as a performance
claim.
