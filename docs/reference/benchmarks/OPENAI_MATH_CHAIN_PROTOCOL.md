# openai/math time-travel benchmark, re-run with the full verification chain: pre-registered protocol

Status: frozen before any registry entry was written and before any new check was run on the corpus. Its SHA-256 is
stored in `OPENAI_MATH_CHAIN_PROTOCOL.sha256` and in the ADR-085 freeze log `openai_math_chain_freezes.json`. The
runner (`scripts/benchmarks/openai_math_revision_bench.py`, commands `chain-select` and `chain`) refuses to start if
the file has changed. Every result records the hash.

## 1. Question

The first run of this benchmark (`OPENAI_MATH_REVISION_PROTOCOL.md`, ADR-077) found that the checks CoResearcher had
on 2026-10-30 caught **1 of the 17** real defects corrected in the October 7, 2026 release of `openai/math`. The
post-hoc import obligations of ADR-077 then put an OPEN obligation at 6 of the 17 defect locations, in-sample.

Since then, blocks A to E of `docs/architecture/VERIFICATION_METHODOLOGY.md` were merged:

| Block | ADR | Capability |
| --- | --- | --- |
| A | 080 | Vacuity probe, trust ladder, fidelity and Lean-lint services |
| — | 082 | Manuscript audit as a service: citation gate and import obligations |
| B | 083 | Cited-results registry with typed hypotheses and conventions, checked at each use; premise retraction |
| C | 084 | Benchmarks as regression tests |
| D | 085 | Freeze service, obligation ledger, the composed 8-step chain |
| E | 086 | Biomedical transfer |

**Question.** With registry entries for the cited results the defects involve, written blind from the cited sources,
does the full chain flag more of the 17 defects on the pre-fix sources, and at what alarm load?

Scope: formal soundness only. The run judges no source, credit or priority, and generates nothing.

## 2. Frozen inputs

- The dataset of the first run, unchanged: `openai_math_revision_dataset.json` (units, commits, defect locations,
  ±2-line tolerance, controls).
- The first run's results, unchanged, as the baseline: `openai_math_revision_results.json`.
- The ADR-077 import scan (`python/discovery/cited_import_ledger.py`), unchanged.

## 3. Selection of cited results (mechanical)

A **cited result** is a pair: a source, identified by its bibliography title normalized to lower-case letters and
digits (first 60 characters), and a numbered Theorem, Lemma, Corollary, Proposition, Claim or Definition named in a
citation's locator. A locator that names several (`Lemma~3.2 and proof of Lemma~3.4`) names each of them. Sections,
pages, equations and unnumbered results are not cited results.

An **occurrence** is a citation site that the ADR-077 scan reports as CONVENTION_TRANSFER or HYPOTHESIS_MATCH, with a
key that resolves to a bibliography entry, for one cited result its locator names.

1. **Involved results.** Every cited result with an occurrence at a defect location (with the tolerance) of a pre-fix
   source of the 17 defects. This selection uses the defect locations, which is declared here: the question is
   whether the chain recognizes the defect *given* an entry for the result used there, as the task that commissioned
   this run asks. The selection never uses the defects' descriptions.
2. **Decoy results.** The pool is every other cited result with an occurrence in the 17 pre-fix sources. Twelve are
   drawn with `random.Random(20261101).sample(sorted(pool), 12)`. The writers handle them in draw order. The first
   eight whose source a writer obtains are registered; the others are recorded as not used.
3. **Occurrences scored.** Every occurrence of a registered result in any version of the 47 units: pre-fix and
   corrected sources of the revised manuscripts, pre-fix sources of the withdrawals, both versions of the 13
   citation-update pairs and the 17 never-revised controls.

## 4. Blind inputs

### 4.1 Registry entries (ADR-083), written blind

- **Writers.** Fresh agent sessions that know nothing of this benchmark. Each receives only: the bibliography entries
  that cite the source (as the manuscripts give them) and the result's locator. The instructions are recorded
  verbatim in `openai_math_chain_procedure/WRITER_INSTRUCTIONS.md` before any writer starts.
- **What they may read.** The cited work itself, in the version the bibliography names (arXiv first, then the
  publisher). For a source that is itself an `openai/math` manuscript, only that manuscript's `.tex` files at the
  `PRE` commit, never its README, version notes, `history.md` or any later edition.
- **What they may not read.** Anything in `openai/math` except that case, anything in this repository, and any text
  about the citing manuscripts, their corrections or their withdrawals.
- **What they write.** For each result: the statement; each hypothesis as text, with literal phrases (for the
  ADR-082 audit) and, where the hypothesis is arithmetic in named integer or real quantities, a formal predicate in
  the ADR-059 language; and the conventions the statement depends on (sign, orientation, normalization, grading,
  indexing), as typed tags with the source's value. A source that cannot be obtained is recorded as UNAVAILABLE.
- **No edits.** The coordinator may only repair JSON syntax or the schema (field names), never content. Each repair
  is listed in the results.

The entries are committed in `openai_math_chain_registry.json` and frozen in the freeze log before any citing context
is encoded.

### 4.2 Citing contexts, encoded blind

- **Encoders.** Fresh agent sessions that know nothing of this benchmark. The instructions are recorded verbatim in
  `openai_math_chain_procedure/ENCODER_INSTRUCTIONS.md` before any encoder starts.
- **Packets.** One per occurrence, in an order shuffled with seed 20261102, under an opaque id. Each holds: the cited
  key and locator, the result used, the passage of the citing file (40 lines before the citation to 15 after,
  comments removed) and the registry entry's statement, hypotheses and conventions. A packet names no manuscript, no
  version and no role, so an encoder cannot tell a defect location from a decoy, a corrected version or a control.
- **What they write.** For each packet: the citing context's variables (the quantities that the entry's formal
  predicates name, with the ranges the passage or its statement gives them), the assumptions the passage states about
  them, and for each convention tag of the entry either the passage's own convention (the entry's value verbatim if
  the passage adopts it, its own words if it states a different one) or nothing when the passage does not state one.
  Only what the passage states is encoded; nothing is inferred from outside it.

The encodings are committed in `openai_math_chain_contexts.json` and frozen in the freeze log before the run.

## 5. Checks

The six checks of the first run are not re-scored: their code is unchanged, and the ADR-084 regression replay
reproduces their results on every pull request. Their verdicts are the baseline. The run adds:

| Check | What it does | Flag |
| --- | --- | --- |
| `REGISTRY_AUDIT` | The ADR-082 manuscript audit (`manuscript_audit.audit`) with the registry entries as its cited results (one copy per bibliography key the manuscripts use). | A HYPOTHESIS_MATCH import with outcome UNMATCHED: a registered hypothesis has none of its phrases in the citing statement and proof. |
| `CHAIN_SEAMS` | The ADR-085 chain (`verification_chain.run`) on each encoded occurrence: the citing context is the hypothesis (its variables and assumptions), the registry entry is cited with the context's conventions. The chain freezes, evaluates, builds the ledger and runs `cite_check` in its seams step. | Seams outcome FINDINGS: a convention MISMATCH, a hypothesis NOT_DISCHARGED with a counterexample, or a cited entry that is not ACTIVE. |

A context with no variable gets one placeholder variable (`cited_use`, domain {1}), because the chain needs a variable
to freeze and evaluate. It constrains nothing. The chain's other steps (fidelity, vacuity, discharge, trust ladder)
are recorded per occurrence and reported, not scored: a citing context has no fidelity specification or declared
non-witness in this corpus.

Not part of the scored run:

- Block A's fidelity and Lean-lint services wrap the `statement_fidelity` and `lean_junk_lint` checks of the first
  run; their verdicts are the baseline's.
- Block E's units, biomedical conventions and domain probes have no input in a mathematics corpus.
- Premise retraction (ADR-083) is reported separately: seeds are manuscripts where `CHAIN_SEAMS` raised a flag
  anywhere, never the ground truth, and the dependents reached through collection links are listed.

### Pre-registered encodability

Judged from `history.md` and the version notes, before any entry was written. A defect is encodable for both new
checks when the authors describe an imported convention or an unmet hypothesis of a cited result, and a numbered cited
result is used at the defect location:

- the three withdrawals (a sign imported from a cited trace lemma);
- *Taming implies compatibility* (cone equality asserted beyond a cited corollary's hypothesis);
- *Conditional good minimal models* (remaining hypotheses of the inputs stated explicitly);
- *The Gaussian free field limit of integer Lipschitz heights with two-arc boundary data* (estimates re-derived from a
  cited companion theorem at a stated parameter).

The other eleven are NOT_ENCODABLE for the new checks: argument gaps (Lipschitz, Ashkin–Teller, *Finite ordinary
MMP*, *Log abundance*), clarified dependencies or inputs with no numbered cited result at the location (*Numerical
semiampleness*, both *Termination* papers, *Deforming*), an unresolved citation (*Exact BSD*, already caught) and
effective constants (*Incompressible*). A flag on a NOT_ENCODABLE defect still scores a HIT.

## 6. Scoring

Per defect and new check:

- **HIT**: on the pre-fix source, an occurrence at a defect location raises a flag whose key (check, result,
  hypotheses missing or findings) is absent from every occurrence of the corrected source. For a withdrawal, the flag
  at the location suffices.
- **MISS**: no HIT, and the defect is encodable for the check.
- **NOT_ENCODABLE**: otherwise.

The defect's chain verdict is HIT if either new check hits, else MISS if either misses, else NOT_ENCODABLE. The
**combined** verdict joins it with the baseline the same way. Each HIT carries the chance expectation: (flags on the
pre-fix source) × (location lines with tolerance) / (source lines).

Every HIT is then read by hand and labelled *reflects the defect* or *coincidence*, as in the first run. The label
is reported next to the protocol verdict and never replaces it.

## 7. Alarm load

Flags at occurrences off any defect location are unconfirmed alarms, reported per check as counts over occurrences and
manuscripts: off-location on the 17 pre-fix sources, on the corrected sources (and which persist from the pre-fix
version), on the citation-update pairs and on the never-revised controls. Seams outcomes (CLEAR, FINDINGS,
INCOMPLETE) are reported for all occurrences, since INCOMPLETE is a non-verdict that a reviewer still has to close.

## 8. Reporting and regression

- `openai_math_chain_selection.json` (results and occurrences, no source text), `openai_math_chain_registry.json`,
  `openai_math_chain_contexts.json`, `openai_math_chain_freezes.json`, `openai_math_chain_results.json` and
  `OPENAI_MATH_CHAIN_RESULTS.md`, with a table side by side with the 1/17 baseline, what the blocks did not change,
  and the next capability gaps ranked by the defects still missed.
- If detection changes, the ADR-084 expectations for this benchmark are updated in the same pull request, through
  `coresearcher regression update` with a reason.
- With 17 defects, every rate is a count with its Wilson 95% interval, not a performance claim.
- No selection rule, encodability judgement, scoring rule, entry or encoding is changed after the run. Any deviation
  is reported as a deviation.
