# ADR-DISCOVERY-081: Pre-registered acceptance checklists, a trivial-witness probe and a trust ladder for announced existence results

**Status:** Accepted
**Date:** 2026-10-31 (checklist frozen 2026-10-30)
**Modules:** [`python/discovery/preregistration.py`](../../python/discovery/preregistration.py),
[`python/discovery/trivial_witness.py`](../../python/discovery/trivial_witness.py),
[`python/discovery/trust_ladder.py`](../../python/discovery/trust_ladder.py),
[`python/discovery/yang_mills_case.py`](../../python/discovery/yang_mills_case.py),
[`python/discovery/o3_continuum_case.py`](../../python/discovery/o3_continuum_case.py)
**Builds on:** ADR-DISCOVERY-059 (formal hypotheses, `entails`), ADR-DISCOVERY-060 (z3 back end),
ADR-DISCOVERY-068 (non-verdict statuses, `NOT_KERNEL_CHECKED`), ADR-DISCOVERY-070 (statement fidelity, junk-value
lint, case-file practice), ADR-DISCOVERY-076 (obligation ledger)
**Case:** [`docs/reference/cases/YANG_MILLS_PREREGISTRATION.md`](../reference/cases/YANG_MILLS_PREREGISTRATION.md)
**Numbering:** first opened as ADR-077. 077 went to import obligations on master, and 078 to 080 are taken on other
branches, so this record takes 081.

## Context

On October 26, 2026 OpenAI announced an existence proof of quantum Yang–Mills theory, including coupling to
fermions. A committee (Douglas, Gross (chair), Jaffe, Klebanov, Nekrasov) holds a 1147-page manuscript and a Lean
formalization. Neither is public. The committee's stated first check is that the definitions and the problem
statement correspond to the standard ones. The mass gap and confinement are explicitly open.

Earlier openai/math cases show the risk. In local smoothing the Lean versions of the sharp results were weaker than
the paper (ADR-070). In the O(3) continuum-limit family the Lean statement covers only lattice exponential decay.
In both, the gap sat between the headline and the formal statement, not in the proof.

Two failure modes are specific to existence claims:

1. **Anchoring.** If the acceptance criteria are written after the claimant's definitions are seen, they tend to
   follow those definitions.
2. **Cheap witnesses.** A statement "there is a T with P(T)" can be proved because some cheap model satisfies P:
   the zero theory, a free field, abelian Maxwell theory, a two- or three-dimensional theory, a theory on a torus,
   or a lattice theory that never reaches the continuum. Jaffe and Witten list exactly these substitutions as the
   reason constructive results so far are partial.

Both questions are about formal statement fidelity, which is in CoResearcher's scope. Whether the proof is correct,
who deserves credit and how the result was announced are not.

## Decision

### 1. Frozen checklists (`preregistration`)

- A checklist is a JSON file with a **vocabulary** (the features of a theory, with finite domains or continuous
  ranges), **obligations** (a formal clause over the vocabulary, a category, the claims it applies to, cited sources
  with locators, and Lean markers for the lint), and a **catalogue of trivial witnesses** (facts over the same
  vocabulary; omitted features are free).
- Categories: `core` (part of the existence claim), `scope` (coverage, such as every compact simple group; a miss is
  a partial result, not vacuity), `qcd`, `companion`, and `out_of_claim` (mass gap, confinement: reported, never
  counted for or against the claim).
- It is frozen by the SHA-256 of its canonical JSON, written with the date to a lock file. `load` refuses a checklist
  whose hash differs from its lock. A change makes a new version with a new lock; a version is never edited. The
  witness catalogue is part of the frozen record, so witnesses cannot be adjusted after the statement is seen.
- Every source is marked `read: true` (pinned by SHA-256 and read in the session) or `read: false` (cited for a
  standard fact, not re-read). No obligation rests on a source that was not read.
- `coverage` maps a formal statement, transcribed by hand into the vocabulary with the source text quoted next to
  each fact, onto the obligations. Each obligation is decided through `HypothesisEvaluator.entails` (enumeration or
  z3): COVERED (the statement entails the clause), OBJECT_DIFFERS (it entails the negation: the statement is about
  another kind of object, such as a lattice or a torus), NOT_ADDRESSED. Contradictory facts are rejected rather than
  read as entailing everything.

### 2. Trivial-witness probe (`trivial_witness`)

- **Semantic probe.** For an existence statement given as named clauses, every catalogued witness is decided
  against every clause: the witness SATISFIES the statement, is EXCLUDED (and by which clauses), or is UNDETERMINED
  (no clause excludes it, but some depends on a feature it leaves free). The statement is VACUOUS_RELATIVE_TO_INTENT
  if a witness satisfies it, POSSIBLY_VACUOUS if one is undetermined, and EXCLUDES_ALL_CATALOGUED otherwise. The last
  outcome says only that no catalogued cheap model passes; it is not fidelity.
- **The covered part of a claim.** When a formal statement covers only some obligations, the probe runs on the
  COVERED clauses. If a cheap model satisfies them, the formal artifact cannot certify the claimed object, however
  strong the theorem is in its own terms.
- **Necessity.** For each clause, the witnesses that are no longer excluded when it alone is dropped. This tells an
  auditor which clauses must survive into the Lean statement.
- **Lean exclusion lint.** For a Lean file, the main theorem and every declaration it uses (by name, transitively;
  the ADR-070 parser extended to `structure`, `class` and `inductive`) are searched, comments removed, for the
  markers each obligation pre-registers. A witness is ADDRESSED_IN_TEXT when an obligation that excludes it has a
  marker in that text, and NO_EXCLUDING_CLAUSE_FOUND otherwise. Counter-markers (`Finset` of sites, `ℤ × ℤ`,
  `AddCircle`) are reported as text that suggests the object has the witness's feature. Every witness carries
  `semantic_confirmation: HUMAN_REQUIRED`: a marker shows the text mentions something, not that the clause means
  it (a definition named `ReflectionPositive` whose body is `True` passes the lint).
- This probe is complementary to `trivial_witness_probe` in PR #21, which checks the arithmetic consistency of
  Comparator hypotheses and tries cheap Lean tactics over the corpus. That probe asks whether a statement is easy to
  prove. This one asks whether a cheap model satisfies it, relative to the claim's intent.

### 3. Trust ladder (`trust_ladder`)

- Rungs: CLAIMED → STATEMENT_PUBLIC → STATEMENT_AUDITED → KERNEL_CHECKED → INDEPENDENTLY_REPRODUCED. A claim climbs
  one rung at a time, and each step needs named evidence (announcement hash; statement location and hash; checklist
  hash, audit report and outcome; toolchain, axioms, kernel-log hash and checker; reproducing party, method and
  record hash). Missing evidence is refused. Reproduction by the claimant is refused as not independent.
- STATEMENT_AUDITED records that the audit ran; its outcome travels with the step.
- Below KERNEL_CHECKED, any Lean theorem attached to the claim has ADR-068 status NOT_KERNEL_CHECKED, with the relay
  LEAN_NOT_KERNEL_CHECKED.
- A claim can move down with a reason; the history is replayed, never rewritten. The ladder is orthogonal to the
  obligation ledger (ADR-076): the ledger grades a proof's obligations, the ladder grades how far the formal claim
  has been checked.

### 4. Cases

- **Yang–Mills (pre-registration).** Checklist `ym4-existence` v1.0.0, frozen 2026-10-30, SHA-256
  `2f899469928cf85a9c34ab19dd1dc73be45624a60b54253e727f61903bf3b353`. The claim record is at CLAIMED because the
  statement is not public.
- **O(3) (rehearsal on public material).** The same tools run against openai/math family 215 at commit `4eaee875`.

## Consequences

- The Yang–Mills checklist excludes all ten catalogued witnesses, for the YM claim and for the QCD claim. The only
  single barrier is the lattice-independent continuum limit (against a subsequential limit point). Without the
  short-distance clause, which is the hardest to state in Lean, non-triviality becomes the only barrier against the
  zero theory and against Yang–Mills at zero coupling, and the dimension the only one against three-dimensional
  Yang–Mills. A statement that says only "an OS theory on ℝ⁴ labelled by a compact simple group" is
  VACUOUS_RELATIVE_TO_INTENT: Yang–Mills at zero coupling satisfies it.
- In the O(3) rehearsal, the Lean statement covers 3 of 14 obligations (the O(3) field, two dimensions, lattice
  decay). On two it is about a different object (a finite subgraph of ℤ², unit spacing, no limit). It leaves nine
  unaddressed: the five OS axioms, internal symmetry, non-triviality, the unique vacuum and the mass gap. The covered
  part of the paper's claim is satisfied by the lattice O(3) model at high temperature on a finite graph, so the
  formal artifact cannot certify the continuum theory. The paper's own claim excludes every catalogued witness.
  lean/docs/215.md states the scope correctly; the gap is between the family headline and the formal statement.
- Transcriptions into the vocabulary are by hand. The solver decides the transcription, not its faithfulness, so
  every fact quotes its source text, as in ADR-070.
- The vocabulary is coarse by design: features a checklist names, not a semantics of QFT. A witness's facts are
  standard results cited in the catalogue; features that are not established (for example the existence of
  three-dimensional Yang–Mills) are left free, which yields UNDETERMINED, never SATISFIES.
- The lint is syntactic. Its value is the list of witnesses with no excluding text, which a human must then read.

## Alternatives considered

- **Write the checklist after the statement is released.** Rejected: that is the anchoring this ADR exists to avoid.
- **Ask the claimant's definitions to be checked against a textbook by an LLM.** Rejected as the decision mechanism
  for the reason given in ADR-059: the answer cannot be checked.
- **A full formal semantics of the OS axioms in Lean, and the probe as Lean lemmas.** That would make the probe
  semantic in Lean. It needs the claimant's definitions to exist, and a Mathlib build. When the statement is public,
  the witnesses that the lint leaves without an excluding clause are the ones worth writing as Lean lemmas (as stage
  3 of PR #21 does for junk values).
