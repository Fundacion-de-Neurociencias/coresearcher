# Learning from external AI-science results: the verification program

**Period:** 2026-10-15 to 2026-10-30. **Status:** living record, maintained by the CoResearcher maintainers.
**Scope:** formal and mathematical soundness only. Nothing here judges sources, evidence quality, credit, novelty
or announcements. Any hypothesis- or proof-generation code is kept out of this repository.

## 1. Why this program exists

Between mid-October and the end of October 2026, several AI systems published results that were relevant to
CoResearcher:

- Sakana AI's *Agentic Scientist* (arXiv:2610.18933), an orchestrator of coding agents that grades its own work
  against natural-language rubrics.
- Google's *Open Agentic Science Engine* (OASE, `GoogleCloudPlatform/LifeSciences`), a multi-agent drug-discovery
  engine with strong provenance machinery.
- OpenAI's `openai/math` release: 721 manuscripts in 373 families, about 42% of top-line results formalized in Lean,
  plus a still-unreleased claim of an existence proof for 4D quantum Yang–Mills.

All three show the same shift: **producing a result is getting cheap, and checking it is becoming the bottleneck.**
CoResearcher is a verifier. It is not a generator (ADR-002). So each external result was read with one question:
*what does this tell us about checking claims, and which mechanism should CoResearcher gain because of it?*

The program has two aims:

1. **Robustness.** Close every path by which CoResearcher could report a verdict it did not earn.
2. **Power.** Add checks that decide questions current agentic-science systems leave to an LLM judge.

## 2. What was done

Each entry states *what* was done, *how*, *why* and *what for*. A PR link means the work is merged unless noted.

### 2.1 Formal checks where others use rubrics (Sakana)

- **What.** The Error Diffusion "polarity invariance" constraint, which the Agentic Scientist states in prose and
  grades itself, was turned into a formal claim. z3 proves it at fixed sizes and the Lean kernel proves it for
  every depth and width. Variants that drop one assumption at a time show which assumptions are necessary.
  ([case](cases/SAKANA_ED_POLARITY.md), PR #5)
- **How.** A formal Hypothesis object (ADR-059), the z3 back end (ADR-060) and an exported Lean theorem, checked by the
  Lean kernel.
- **Why.** Sakana's own ablation (its Table 6) shows that a loosely worded rubric let the agent score best without
  implementing the method. Self-graded prose rubrics cannot catch an unstated or misread constraint.
- **What for.** It is the showcase for CoResearcher's role: a decidable check that sits under any agentic
  pipeline.

### 2.2 A gate on the weakest link: prose to formal

- **What.** A self-consistency gate on the LLM formalizer: N independent formalizations, pairwise equivalence decided
  by the exact evaluator, and `FORMALIZATION_AMBIGUOUS` when no strict majority exists.
  ([ADR-064](../decisions/ADR-DISCOVERY-064-FORMALIZER-SELF-CONSISTENCY-GATE.md), PR #6)
- **Why.** In round 0, formalizer equivalence was 0.15 (small model) and 0.50 (larger model). Every downstream verdict
  is only as good as the formalization it starts from.
- **What for.** It stops a mistranslated hypothesis from reaching the court as if it were the scientist's claim.

### 2.3 Auditable verdicts (inspired by OASE)

- **What.** Every formal report now carries a provenance block: engine and solver versions, the input and output
  digests and the threshold set it used. The pipeline has one vocabulary for non-verdicts (blocked, undecided, not
  kernel-checked, ambiguous). Thresholds are versioned, and an unset one raises instead of defaulting. Mandatory
  caveats ("relays") are attached to reports. A two-phase CLI provides `coresearcher formal run`, `analyze` and
  `doctor`. ([ADR-068](../decisions/ADR-DISCOVERY-068-AUDITABLE-FORMAL-VERDICTS.md), PR #12)
- **How.** The field names mirror OASE's sidecar and analysis records. `analyze` runs offline and re-derives the
  verdict from the stored formal object.
- **Why.** OASE showed what "a result you can trace" looks like in practice. CoResearcher's verdicts did not record
  how they were produced.
- **What for.** A reviewer can now re-run a verdict and diff it. A timeout or a missing tool can never turn into a
  verdict.

### 2.4 CoResearcher inside OASE

- **What.** An `oase formal` adapter, a skill and a demo on a hypothesis in hypex format. The adapter lives in
  `integrations/oase/`, and a CI job applies it to a pinned OASE commit and runs OASE's own conformance checks.
  ([ADR-069](../decisions/ADR-DISCOVERY-069-OASE-FORMAL-ADAPTER.md), PR #13)
- **Why.** OASE's hypotheses are prose with LLM scores and Elo ratings. No tool in it checks logical consistency,
  claim-vs-claim contradiction or falsifiability.
- **What for.** It is a concrete path for CoResearcher to act as the formal gate before a tournament and at Stage 1
  of such a pipeline.

### 2.5 Checking the statement, not only the proof (OpenAI local smoothing)

- **What.** OpenAI's "Local smoothing for the Euclidean wave equation" was audited at the level of its statements.
  For each of the six Lean Comparator targets, z3 decided whether the range in the paper and the range in Lean are
  the same. A lint lists every Lean total-function convention that could weaken a statement in silence, and a
  coverage map gives the formal status of each result in the paper.
  ([case](cases/LOCAL_SMOOTHING_STATEMENT_FIDELITY.md),
  [ADR-070](../decisions/ADR-DISCOVERY-070-STATEMENT-FIDELITY-AUDIT.md), PR #14)
- **Result.** All six ranges are equivalent to the paper's. The Lean versions of Theorem 1.2 and Corollary 7.1 are
  weaker than the paper. Several results are prose only. The kernel check was not run here.
- **Why.** Once a kernel check exists, trust moves from the proof to the statement: does the Lean statement say what
  the paper claims?
- **What for.** It is a reusable statement-fidelity audit for any Lean-backed claim.

### 2.6 Understanding how the proof was found

- **What.** An anatomy of the same paper:
  - a dependency DAG of its 39 lemmas and theorems and the 40 external results they import;
  - SymPy and z3 checks of the elementary identities the argument rests on (13 verified, 0 refuted, 6 not
    encodable);
  - a catalogue of the proof's reusable "moves", each tagged stated, checked or inferred.
  (PR #15, open)
- **Why.** The owner asked how the model reasoned, not only whether it is right. Seeing the moves (match the target
  exponent to a known inequality; make a tensor positive by lifting to auxiliary variables; reduce to a scalar
  differential inequality and count the losses) teaches us what to check and where.
- **What for.** It is a method for turning a proof into named obligations that can each be discharged on their own.

### 2.7 The obligation ledger

- **What.** A ledger of named obligations with independent discharge and a reproducible proof pipeline (one-command
  rerun, SHA-256 manifest, an audit that rejects stale proofs). Its pilot is the Mahler scalar input. All 24
  obligations are proved, so the claim is DISCHARGED_INTERVAL, and every proof step has been reproduced from
  scratch. Proof cases are registered once and served read-only at `/api/obligations/cases`, each together with
  its audit.
  ([ADR-076](../decisions/ADR-DISCOVERY-076-OBLIGATION-LEDGER.md),
  [case](cases/MAHLER_SCALAR_OBLIGATIONS.md), [pipeline](PROOF_PIPELINE.md), PR #18)
- **Why.** Long proofs fail at single steps. A ledger makes every step's status explicit and keeps it reproducible.
- **What for.** It is the backbone for checking long or machine-written arguments piece by piece.

### 2.8 A benchmark with real errors (time travel on openai/math)

- **What.** For the 17 manuscripts that OpenAI revised or withdrew, we ran today's checks on the source as it stood
  before each fix. A protocol frozen before the run fixes what counts as a hit. (PR #19, open)
- **Result.** One real detection out of 17: an unresolved citation. One further hit is attributable to chance. The
  other 15, including the three withdrawals caused by a sign error, are not encodable with current tools: in each
  case the error is a sign convention imported from a cited lemma.
- **Why.** The release's own corrections are the only real ground truth of errors in that corpus. Mutation tests
  only approximate it; the earlier mutation pilot reached an AUROC of about 0.52.
- **What for.** It gives an honest measure of current power and a ranked list of the next mechanisms. The top three:
  1. import cited lemmas with their conventions typed;
  2. keep a registry of cited theorems with their hypotheses, matched at each use;
  3. propagate dependencies across manuscripts.

### 2.9 Lessons 1, 3 and 4 as product features

- **What.** A hypothesis can declare intended non-witnesses; one that satisfies the claims gives the verdict
  VACUOUS_RELATIVE_TO_INTENT, with the witness. Every evaluated claim carries a trust-ladder rung computed by
  mechanical rules. The ADR-070 range comparison and junk-value lint are served by the API and the two-phase CLI.
  ([ADR-080](../decisions/ADR-DISCOVERY-080-INTENT-PROBE-TRUST-LADDER-FIDELITY-SERVICE.md))
- **Why.** These checks had been run by hand in single cases. As features, they apply to every claim CoResearcher
  evaluates.

### 2.10 In progress

- **Corpus-wide claim-vs-Lean coverage.** This is the mechanical version of the gap found by hand twice: in local
  smoothing, and in the O(3) continuum limit, where only lattice decay is formalized and the continuum limit, the
  Osterwalder–Schrader axioms and the mass gap are prose only.
- **A pre-registered checklist for 4D Yang–Mills existence.** The committee that holds OpenAI's unreleased proof
  will first check that the definitions and the problem statement match the standard ones. We freeze our own
  acceptance criteria now, from the Jaffe–Witten statement and constructive-QFT practice, so that the later audit
  is not anchored by the authors' definitions. The checklist also adds a *trivial-witness probe*: an existence
  statement that the free or the zero theory satisfies is vacuous relative to its intent. The claim is recorded at
  the first rung of the trust ladder below (CLAIMED), because no statement is public.

### 2.11 Addendum (2026-11-01): the time-travel benchmark re-run after blocks A–E

- **What.** The 17 real openai/math corrections were measured again with the full chain of
  [`VERIFICATION_METHODOLOGY.md`](../architecture/VERIFICATION_METHODOLOGY.md):
  - the manuscript audit with a cited-results registry;
  - the obligation ledger;
  - the 8-step chain.

  The registry entries for the cited results at each defect location were written by agents that saw only the
  bibliography entry and read the cited work. The citing contexts were encoded by other agents from shuffled, opaque
  passages. The procedure was pre-registered, and each input was frozen before the next step.
  ([`OPENAI_MATH_CHAIN_RESULTS.md`](benchmarks/OPENAI_MATH_CHAIN_RESULTS.md))
- **Result.** The protocol count rose from 2/17 to 11/17. Read by hand, the gain is small:
  - **Decided detections are still 1/17**, the unresolved citation.
  - **For the three withdrawals, the chain now shows the cited and the citing sign conventions side by side**, at the
    passage the withdrawal notice names. It compares them as strings, so it does not decide the sign.
  - **The other new hits are coincidences.** The chain flags about a third of all citations wherever they are, and
    the phrase-based registry audit flags most of them.
- **What it taught.** In order:
  1. **Conventions must be compared semantically, not as text.**
  2. **The chain needs an input kind for a citation inside a proof.**
  3. **A cited result can itself be the error.** The blind Li–Zhang entry supports the pre-fix *Taming* claim, so
     only premise status (M11) could flag that use.
- **Regression.** The block C regression case now replays this run offline and freezes its verdicts and alarm
  counts.

## 3. Lessons for reasoning and verification

1. **Check the question before the answer.** A proof assistant certifies that a conclusion follows from a statement.
   Whether the statement means what we intend is a separate check, and it is often the weaker link.
2. **Fix the acceptance criteria before seeing the work.** Pre-register protocols and definitions, freeze them with
   a hash, and count failures as failures.
3. **Existence claims can be vacuous.** Always try cheap witnesses: the zero object, the free theory, a lower
   dimension, a finite volume.
4. **"Formalized" is a per-claim status, not a label for a paper.** Use a coverage map, and record each claim at one
   of five rungs: CLAIMED, STATEMENT_PUBLIC, STATEMENT_AUDITED, KERNEL_CHECKED, INDEPENDENTLY_REPRODUCED.
5. **Self-grading is not verification.** Rubrics a system grades for itself catch only what they enumerate. A
   decidable check, or an independent party, is needed.
6. **Measure on real errors.** Mutation proxies overstate or understate power. Corrections that happened in real
   releases are the honest test.
7. **Most real errors live at the seams:** imported conventions and the hypotheses of cited theorems, not displayed
   arithmetic. That is where the next mechanisms must look.
8. **Never let a non-answer become an answer.** A timeout, a missing tool, ambiguity or an unrun kernel each keep
   their own status.

## 4. Operational notes

- **Memory.** Heavy runs on the openai/math corpus (174k files) must use blobless, sparse fetches and run one at a
  time. Several parallel sessions on an 8 GB machine exhausted memory and crashed together.
- **ADR numbering.** Two records share number 070: `ADR-DISCOVERY-070-STATEMENT-FIDELITY-AUDIT.md` and
  `ADR-DISCOVERY-070-CELLULAR-AUTOMATA-BARRIER-AUDITOR.md`. New records should take the next free number after
  checking `docs/decisions/`.

## 5. What comes next

- Merge the open PRs (#15, #19) once CI is green.
- Build the top mechanisms from the time-travel benchmark, in the order of section 2.8.
- Finish the corpus-wide coverage map and the Yang–Mills checklist. Apply both the day a Lean statement for
  Yang–Mills is published.
- Re-run every benchmark against each new pinned release of `openai/math`. Formalizations are added over time, so
  results must be dated and comparable.
