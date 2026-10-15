# Concordance benchmark: pilot, round 1 (pre-registration)

**Status:** Draft. Becomes binding when the freeze record (section 8) is filled in, before the first task is sent to
a judge.
**Protocol:** [CONCORDANCE_BENCH_PROTOCOL.md](CONCORDANCE_BENCH_PROTOCOL.md) (round 1 version, hash in section 8)

## 1. Objectives

The pilot is small on purpose. With 20 tasks the confidence intervals for kappa will be wide, so the
non-inferiority criterion of protocol section 7 is computed and reported but **cannot be confirmed or rejected with
useful precision**. The pilot's primary objectives are about feasibility and about where disagreements come from:

1. Time per task for judges and proposers, and the `CANNOT_JUDGE` rate per question.
2. Formalization fidelity (Q5): how often a proposer's formal object says what the prose says.
3. Judge–judge agreement per question, as a first estimate of the human ceiling and an input to the sample size of
   round 2.
4. The disagreement audit (protocol section 7.4): how CoResearcher–gold disagreements split into formalization gaps,
   model limitations, human errors and genuine ambiguity.
5. CoResearcher–gold and LLM–gold agreement (section 7a), reported descriptively.

## 2. Participants

4 to 6 scientists from the Fundación de Neurociencias, recruited by the maintainers. Everyone signs the
participation note in section 6. Roles:

| Role | Who | Load |
| --- | --- | --- |
| Proposer | Every participant | 3 to 5 tasks each, 20 in total |
| Fidelity reviewer (Q5) | One participant per task, not its proposer | About 4 tasks each |
| Judge | Two per task, neither the proposer nor the reviewer | About 8 tasks each with 5 participants |
| Adjudicator | One person outside the judge pool (a maintainer if needed), named before judging | Disagreements only |
| Task manager | A maintainer | Runs `validate`, assigns tasks, seals answers |

Assignment is random, with the constraints above, using seed 20261015 and the script call recorded in the ledger.

## 3. Tasks

- 20 tasks in the format of `schemas/hypothesis_verification_task.schema.json`, each passing
  `concordance_score.py validate`.
- Fields: hypotheses from the proposers' own research areas. A task may be confidential; confidential tasks are run
  only on the Legion and never published.
- Balance targets, tracked with proposer expectations (never used as gold): at least 5 tasks whose expected Q1 is not
  `FALSIFIABLE`, at least 4 with conflicting premises, at least 8 with observations, at least 8 with a rival.
- The example task (`concordance_example_task.json`) is used for training only and is not one of the 20.

## 4. Instructions for judges

Judges receive these instructions with the first task, and nothing else about CoResearcher's method:

1. Read the hypothesis, its context, the labelled premises, the observation table and the rival. Judge only what is
   written. Do not look things up, and do not judge whether the hypothesis is true or well supported.
2. Answer the questions in the form. Use `CANNOT_JUDGE` when the text does not let you decide; it is a valid answer,
   not a failure.
3. For each answer, give a confidence from 1 to 5 and one sentence of rationale.
4. For conflicting premises, list the labels of the premises that cannot hold together. For refuting observations,
   list the table row numbers.
5. Q6: note any weakness of the hypothesis that the questions did not cover, citing premise labels or table rows.
6. Record the minutes you spent. Do not discuss tasks with other participants until the round is closed.

Definitions given to judges are the ones in protocol section 5, worded identically to the LLM arm prompt so both arms
answer the same questions.

## 5. Timeline

| Week | Step |
| --- | --- |
| 1 | Recruitment; training session with the example task; proposers draft tasks |
| 2 | Q5 fidelity review in rounds until each task is `ACCEPTED`; `validate` passes for all 20 |
| 3 | Freeze: protocol, tasks and this document hashed (section 8). CoResearcher arm sealed (`seal`), LLM arm sealed (`concordance_llm_arm.py run`), both hashes in the ledger |
| 3 to 4 | Judging. Each judgment file is hashed at submission |
| 5 | Unblinding, adjudication, scoring (`score`), disagreement audit |
| 6 | Report, including everything listed in section 1, whatever the results |

## 6. Participation note

Participation is voluntary and unpaid. Judgments are attributed by ORCID in the internal ledger and anonymised
(judge A, judge B) in any publication. Task text is published only with the proposer's licence and never when the task
is marked confidential. Participants may withdraw their tasks or judgments before unblinding.

## 7. Outputs

- `RESULTS.json` from `concordance_score.py score`, with both sealed hashes and the protocol hash.
- A round report in `docs/reference/benchmarks/` with the metrics of section 1, the confusion matrices, every
  disagreement with its audit category, and the Q6 critiques grouped.
- The list of protocol changes proposed for round 2, each with the disagreement or critique that motivated it.

## 8. Freeze record

| Item | SHA-256 | Date |
| --- | --- | --- |
| Protocol (round 1) | pending | pending |
| This document | pending | pending |
| Task set (20 files, sorted, concatenated) | pending | pending |
| CoResearcher sealed answers | pending | pending |
| LLM arm sealed answers (model tag: pending) | pending | pending |
| Participants and roles | recorded in the internal ledger | pending |
