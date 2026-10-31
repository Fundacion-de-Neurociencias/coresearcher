# Verification methodology: what the October 2026 exercises taught, and how CoResearcher absorbs it

**Status:** normative direction for new capabilities. **Date:** 2026-10-31.
**Companion record:** [External results program](../reference/EXTERNAL_RESULTS_PROGRAM.md) lists what was done.
This document keeps only the method behind it.

## 1. Purpose

From mid-October to the end of October 2026, the maintainers worked through a series of exercises on external
AI-science results: Sakana's Agentic Scientist, Google's OASE, OpenAI's `openai/math` release and the unreleased
Yang–Mills claim. **The results of those exercises are not the goal.** They were preparatory and demonstrative work,
meant to expose *methods* of verification and reasoning that make CoResearcher stronger.

This document names those methods. For each one it states:

- what it contributes, and why;
- how it works;
- how far it is integrated today;
- how it carries CoResearcher beyond mathematics into the domains it serves, starting with biomedical hypotheses.

The scope is unchanged: CoResearcher judges the formal and mathematical soundness of hypotheses. It does not grade
sources or evidence. Generation stays outside the public repository.

## 2. The methods

Each method is written as a reusable principle. The exercise it came from is noted, but the method is
domain-neutral.

### M1. Check the question before the answer

- **Contribution.** A verifier can certify that a conclusion follows from a statement. It cannot certify that the
  statement means what the scientist intended. That gap is where most "verified but wrong" outcomes hide.
- **How.**
  - Compare the intended claim (prose) with the formal claim through a decidable relation: equivalent, stronger,
    weaker, incomparable or undecided, with witnesses.
  - Lint the formal statement for conventions that silently weaken it, such as total functions returning default
    values.
- **Came from.** Local smoothing (ADR-070) and the Yang–Mills committee's first check.
- **Integration.** The library exists (`statement_fidelity.py`). Block A exposes it as API and CLI services.
- **Beyond mathematics.** Every hypothesis a scientist submits passes through the formalizer. The fidelity relation
  between the scientist's prose and the formal object should be a first-class output of every evaluation, not a
  side audit.

### M2. Independent readings must agree

- **Contribution.** When a translation step is unreliable (an LLM formalizer, a single human reader), one reading is
  not evidence.
- **How.** Draw N independent readings. Decide agreement with an exact equivalence check. When there is no
  majority, report `AMBIGUOUS` instead of picking one.
- **Came from.** The formalizer gate (ADR-064). The coverage map also had only a single reader, which its own PR
  lists as an open limitation.
- **Integration.** Done for the formalizer.
- **Beyond.** Apply the same rule to every judgement step that is not decidable: claim extraction, scope
  classification, convention tagging.

### M3. Fix the acceptance criteria before seeing the work

- **Contribution.** A verifier that reads the authors' definitions first gets anchored by them.
- **How.** Pre-register the protocol and the expected definitions, freeze them with a SHA-256 and a date, refuse to
  run if the hash changes, and count failures as failures.
- **Came from.** The formalizer benchmark, the time-travel benchmark and the Yang–Mills checklist.
- **Integration.** Partial. Lifecycle hashes exist (ADR-063). Freezing should be a reusable service.
- **Beyond.** Before evaluating a scientist's hypothesis, CoResearcher can freeze what would count as support or
  refutation (the discriminating states between rivals) before any data is examined.

### M4. Existence and generality claims can be vacuous

- **Contribution.** "There exists a model satisfying P" or "P holds for all cases" says nothing if a trivial object
  satisfies P.
- **How.** Probe the claim with cheap witnesses: the zero or null model, a free or degenerate model, the boundary
  values, an empty scope. A claim that a declared non-witness satisfies is *vacuous relative to intent*.
- **Came from.** Yang–Mills ("a free theory does not count").
- **Integration.** Block A adds it to the evaluator.
- **Beyond.** In biomedicine, a hypothesis that a null model already satisfies is the same failure. One example is
  a predicted effect that also holds when the biomarker is replaced by a constant. Another is a mechanism whose
  predictions are met by the untreated arm.

### M5. Decompose into named obligations and discharge each independently

- **Contribution.** Long arguments fail at single steps. A ledger makes every step's status explicit and keeps it
  reproducible.
- **How.**
  - Build a dependency DAG of obligations and check it is acyclic, with no missing premises.
  - Discharge each obligation with the strongest available tool: exact algebra, SMT, interval arithmetic, the Lean
    kernel.
  - Record a manifest with hashes and reject stale proofs.
- **Came from.** Proof anatomy (PR #15) and the Mahler ledger (ADR-076).
- **Integration.** The ledger exists. It is not yet the standard path for a submitted hypothesis.
- **Beyond.** A mechanistic hypothesis ("A raises B, which drives C, which predicts D") is an obligation chain. Each
  link can be checked for consistency, dimensional homogeneity and compatibility with the others.

### M6. Errors live at the seams

- **Contribution.** In the only real ground truth we have (17 corrections in `openai/math`), displayed arithmetic was
  almost never the problem. The defects came from:
  - sign or normalization conventions imported from a cited lemma;
  - hypotheses of a cited theorem that were not met where it was applied;
  - dependencies between manuscripts.
- **How.**
  - Keep a registry of cited results with their hypotheses and conventions as typed fields.
  - At each use, check that the hypotheses are discharged and that the conventions match.
  - Propagate a correction to every result that depends on the corrected one.
- **Came from.** The time-travel benchmark (PR #19).
- **Integration.** Not yet. This is block B.
- **Beyond.** Biomedical hypotheses import "lemmas" all the time: a biomarker cutoff validated under one assay and
  population, a scale with its own direction convention, a unit system. A cutoff applied outside its validated
  conditions is the same seam error. The pTau217 cutoff case is the natural first target.

### M7. "Formalized" and "verified" are per-claim states

- **Contribution.** A paper, a project or a hypothesis is never verified as a whole. Labels at that level
  overstate what was checked.
- **How.** Record every claim on a trust ladder:
  1. CLAIMED
  2. STATEMENT_PUBLIC
  3. STATEMENT_AUDITED
  4. KERNEL_CHECKED
  5. INDEPENDENTLY_REPRODUCED

  Each rung has a mechanical promotion rule. Keep a coverage map from claims to formal targets.
- **Came from.** The coverage maps (local smoothing, O(3), the whole corpus in PR #21).
- **Integration.** Block A adds the ladder to reports and to the evidence graph.
- **Beyond.** Every hypothesis report shows which of its claims reached which rung, so a scientist sees exactly what
  was checked and what was not.

### M8. A non-answer never becomes an answer

- **Contribution.** A timeout, a missing tool, ambiguity or an unrun kernel check silently turned into a verdict is
  the worst failure a verifier can have.
- **How.**
  - Use one vocabulary for non-verdicts, carry provenance on every report, and declare thresholds explicitly, so
    that an unset threshold blocks instead of defaulting.
  - Run in two phases, so that a reviewer can re-derive a verdict offline.
- **Came from.** The false-verification fixes and OASE (ADR-068).
- **Integration.** Done.
- **Beyond.** It applies unchanged to every new capability, and it is a hard requirement for any of them.

### M9. Measure on real errors, then rank the next mechanism

- **Contribution.** Mutation tests and synthetic benchmarks can overstate or understate power. Corrections that
  happened in real work are the honest test, and the misses tell you what to build next.
- **How.** For each real corrected defect, run the current checks on the pre-fix version and record HIT, MISS or
  NOT_ENCODABLE, along with false alarms on the corrected version. Rank new mechanisms by the defects they would have
  caught.
- **Came from.** The time-travel benchmark.
- **Integration.** Block C turns benchmarks into regression tests.
- **Beyond.** Retracted or corrected biomedical claims are the same kind of ground truth for formal checks. This is
  limited to defects in internal consistency or formal structure, never to judging the evidence itself.

### M10. Know how results are found, to know where they break

- **Contribution.** Reading how a proof was built shows which steps carry the weight and where a check is worth the
  most. Examples of such steps: matching a target exponent to a known inequality, lifting to auxiliary variables to
  restore positivity, reducing to a scalar inequality and counting the losses.
- **How.** Keep a catalogue of moves, each with its trigger, the move itself and its verification hook (the
  obligation it creates). Use it to place checks.
- **Came from.** The proof anatomy and the released reasoning summaries.
- **Integration.** Documentation only today. Any use for *generating* hypotheses or proofs belongs in the private
  package, not in this repository.
- **Beyond.** It works the same way for a mechanistic model: knowing which assumption a model's predictions rest on
  tells CoResearcher which obligation to check first.

## 3. How the methods compose

A hypothesis submitted to CoResearcher should pass through all of them in order:

1. Freeze the acceptance criteria. (M3)
2. Formalize, with independent readings that must agree. (M2)
3. Audit fidelity against the scientist's prose. (M1)
4. Probe for vacuity relative to intent. (M4)
5. Decompose into obligations. (M5)
6. Check the seams: imported conventions and the hypotheses of cited results. (M6)
7. Discharge each obligation with the strongest tool available, never converting a non-answer into an answer. (M8)
8. Report every claim on the trust ladder. (M7)

The whole chain is regression-tested on real corrected errors (M9). Checks are placed where the move catalogue says
the weight lies (M10).

## 4. Integration roadmap

| Block | Methods | Capability | State |
| --- | --- | --- | --- |
| A | M1, M4, M7 | Vacuity probe in the evaluator, trust ladder in reports and the evidence graph, fidelity compare and Lean lint as API/CLI services | In progress |
| B | M6 | Registry of cited results with typed hypotheses and conventions, checked at each use, with dependency propagation | Next |
| C | M9 | Benchmarks (time travel, coverage calibration, Sakana ED, local smoothing) as regression tests in CI | Next |
| D | M3, M5 | Freeze service, and the obligation ledger as the standard path for submitted hypotheses | After B and C |
| E | all | Domain transfer: run the full chain on biomedical hypotheses, starting with the pTau217 cutoff and the Alzheimer formal scenario | After D |

Blocks run one at a time. Each one lands as a module wired into the API and CLI, with tests and an ADR. It does not
land as a case study.
