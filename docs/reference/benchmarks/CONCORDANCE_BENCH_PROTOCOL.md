# Hypothesis Verification Concordance Benchmark: protocol

Status: draft for pre-registration (round 1). Fix sections 5, 6 and 7 before the first judgment is collected,
then record the SHA-256 of this file with every result (section 9).

Related: [ADR-DISCOVERY-059](../../decisions/ADR-DISCOVERY-059-FORMAL-HYPOTHESIS-OBJECT.md) (formal hypothesis
object), task and judgment schemas in [`schemas/`](../../../schemas/), scorer in
[`scripts/benchmarks/concordance_score.py`](../../../scripts/benchmarks/concordance_score.py).

## 1. Purpose

CoResearcher's formal verdicts are exact for the state space a hypothesis declares. Nothing yet shows that they
agree with how domain scientists judge the *scientific* hypothesis behind that formal object. This benchmark measures
that agreement. It is an external validation of the formal layer, not a leaderboard.

## 2. Design principle: two arms, one blinded

- **Scientists** judge the hypothesis **as a scientist would**, from its prose statement, its rival and the
  observations presented as a data table. They never see the formal object or CoResearcher's output.
- **CoResearcher** judges the **formal object** that encodes the same hypothesis.
- A disagreement therefore means one of: the formal object does not capture the hypothesis (formalization gap), the
  finite model cannot express it (model limitation), the scientists erred, or the question is genuinely ambiguous.
  Section 7 classifies every disagreement into one of these.

If scientists judged the formal object instead, CoResearcher would agree by construction and the benchmark would only
measure human error.

## 3. Roles

| Role | Task | Sees the formal object? |
| --- | --- | --- |
| Proposer | Submits a task from their own field (section 4) | Writes it |
| Task manager | Helps the proposer encode the formal object; does not judge or review that task | Helps write it |
| Task reviewer | Checks the task is well posed and that the formal object faithfully encodes the prose (question Q5) | Yes |
| Judge (≥ 2 per task) | Answers Q1–Q4 independently, from prose and data only | **No** |
| Adjudicator | Resolves judge disagreements into a gold label; classifies CoResearcher disagreements | Yes, after unblinding |
| Maintainer | Runs CoResearcher; never edits tasks or judgments | Yes |

Nobody judges a task they proposed, helped formalize or reviewed. Judges do not discuss tasks before submitting.
Judges are assigned to tasks in or near their own field, recorded at sign-up with their ORCID and sub-fields.

**Eligibility.** Proposers, reviewers and judges have published research in the task's field and have peer-review
experience. Their seniority is recorded so agreement can be analysed by experience.

**Independence.** The proposer nominates task reviewers but must not discuss the task with them before review.
Proposers and task managers must not run CoResearcher on a task before it is sealed: a proposer who tunes a task
against CoResearcher's answers would bias the benchmark towards or against it.

## 4. Task format

One JSON file per task, valid against `schemas/hypothesis_verification_task.schema.json`. It has two parts:

**Shown to judges (prose arm):**
- `field`, `statement`: the hypothesis in natural language, as the proposer would write it in a paper.
- `rival_statement` (optional): a competing hypothesis in natural language.
- `observations_table` (optional): observations as a table, with column meanings and provenance (public dataset
  identifier, or "illustrative").
- `context`: the minimum domain background a judge needs; no hints about the expected answers.
- `premises`: the hypothesis's premises as labelled sentences (`P1`, `P2`, ...), so judges can cite them.

**Hidden from judges (formal arm):**
- `formal_hypothesis` and optional `formal_rival`: ADR-059 objects (variables with finite domains, scope,
  assumptions, claims).
- `formal_observations`: the same observations as states over the declared variables, in table-row order.
- `assumption_labels`: the premise label of each formal assumption, so itemised answers can be compared.
- `proposer_expected` (optional): the proposer's own answers. Recorded, but never used as the gold label.

Metadata: `task_id`, `proposer_orcid`, `licence`, and `confidential` (if true, the task is run locally and never
published).

## 5. Questions (fixed before collection)

Judges and CoResearcher answer the same four questions. Judges may answer `CANNOT_JUDGE`.

| ID | Question to judges | Answer set | CoResearcher source |
| --- | --- | --- | --- |
| Q1 | As stated, is the hypothesis empty, self-contradictory, untestable, or testable? | `VACUOUS`, `SELF_CONTRADICTORY`, `UNFALSIFIABLE`, `FALSIFIABLE` | `content_verdict` |
| Q2 | Are the hypothesis's premises compatible with each other? | `COMPATIBLE`, `CONFLICTING` | `conflicting_assumption_sets` empty or not |
| Q3 | Do the observations refute the hypothesis? | `REFUTED`, `POSSIBLY_REFUTED`, `NOT_REFUTED` (ordered) | certain / possible counterexamples |
| Q4 | How does the hypothesis relate to its rival? | `EQUIVALENT`, `STRONGER`, `WEAKER`, `INCOMPARABLE`, `CONTRADICTORY` | `compare` relation |

Q3 is asked only when the task has observations, and Q4 only when it has a rival.

**Itemised answers.** A verdict alone can agree for the wrong reason. Judges therefore also say *where* the
problem is, and CoResearcher's answer is compared item by item:

| ID | Question to judges | Answer | CoResearcher source |
| --- | --- | --- | --- |
| Q2_items | Which premises conflict? | Set of premise labels (empty if none) | Union of the minimal conflicting assumption sets |
| Q3_items | Which observations refute the hypothesis? | Set of table row numbers (empty if none) | Certain counterexamples |

For each answer judges also give a confidence from 1 to 5 and a one-sentence rationale.

**Q5, formalization fidelity** (task reviewers only, before judging starts): does the formal object express the
prose hypothesis? `YES`, `PARTIALLY`, `NO`, with the mismatch described. Tasks rated `NO` are fixed or withdrawn
before judging. Tasks rated `PARTIALLY` stay in and are analysed separately.
This review runs in rounds: the reviewer rates fidelity at every turn and closes the review with an explicit
`ACCEPTED` statement; the proposer revises in between.

**Q6, open critique** (judges): weaknesses of the hypothesis that Q1–Q4 do not cover, each citing premise labels or
table rows where possible. Q6 is not scored. It shows what the fixed questions miss and feeds section 9.

## 6. Collecting judgments

0. **Preflight.** `concordance_score.py validate` must pass for every task: the formal objects build, the
   rival shares the state space, premise labels match the formal assumptions, and the prose table matches the
   formal observations row by row. Failing tasks go back to the proposer and task manager.
1. Judges receive only the prose arm, through a form that writes a JSON file valid against
   `schemas/scientist_judgment.schema.json`. One file per judge per task.
2. **Commitment before unblinding.** At submission, the SHA-256 of each judgment file is recorded with a timestamp
   in the ledger. The maintainer runs CoResearcher on all tasks and records the SHA-256 of its outputs **before**
   any judgment is opened. Neither side can change its answers after seeing the other's.
3. **Gold label.** If the judges agree, their answer is gold. If not, the adjudicator decides, and both raw answers
   are kept. `CANNOT_JUDGE` answers are excluded from the gold label and counted separately.
4. Time spent per task is recorded, to estimate the real cost of verification.

## 7. Measuring agreement

All analyses are run by `concordance_score.py`. Uncertainty comes from a bootstrap over tasks, clustered by
proposer (2,000 resamples), because tasks by one proposer are not independent.

1. **Human ceiling first.** Judge–judge agreement per question: Cohen's kappa (unweighted for Q1, Q2 and Q4; linear
   weighted for the ordered Q3), with a 95% interval. CoResearcher cannot be expected to agree with the gold label
   more than scientists agree with each other.
2. **CoResearcher vs gold.** Per question: raw agreement, the same kappa, its 95% interval, and the confusion matrix.
3. **Pre-registered criterion (non-inferiority).** For each question, the lower bound of the CoResearcher–gold kappa
   interval is at most 0.10 below the judge–judge kappa point estimate. Report the result whichever way it goes.
4. **Disagreement audit.** The adjudicator classifies every CoResearcher–gold disagreement as:
   - **formalization gap:** the formal object does not encode the hypothesis;
   - **model limitation:** finite domains or discretisation cannot express it;
   - **human error:** the gold label is wrong on reflection;
   - **genuine ambiguity:** reasonable scientists could answer either way.

   The distribution of these categories is the main qualitative result. Formalization gaps are also cross-checked
   against the Q5 ratings.
5. **Itemised agreement.** For Q2_items and Q3_items, per-task Jaccard overlap between CoResearcher's set and the
   gold set (1.0 when both are empty), averaged over tasks, with the same clustered bootstrap and the judge-judge
   value as ceiling. Every mismatch is listed for the disagreement audit.
6. Results are reported separately for tasks rated Q5 = `YES` and Q5 = `PARTIALLY`.

## 7a. Third arm: a local language model judging from the prose

The benchmark asks whether CoResearcher's formal checks add something beyond reading the prose carefully. A
language model that reads the same prose as the judges is the natural comparison: if it agrees with the gold labels as
well as CoResearcher does, the formal object adds little for these questions.

- **Model.** Laya, or another model served locally (Ollama or LM Studio on the Lenovo Legion), so confidential tasks
  never leave the Fundación. The exact model tag is fixed before round 1 and recorded with the results.
- **Input.** Only the prose arm: statement, context, premises, observation table and rival. Never the formal arm or
  the proposer's expected answers. The prompt (`concordance-llm-arm-v1` in `concordance_llm_arm.py`) gives the same
  definitions the judges receive, and its SHA-256 is recorded.
- **Decoding.** Temperature 0, seed 0, one output per task, no retries. An answer that is missing or outside the
  answer set is scored as `INVALID` (a disagreement); it is never dropped or re-asked.
- **Sealing.** The LLM answers are sealed and their SHA-256 recorded in the ledger before any judgment is opened,
  exactly like CoResearcher's. `concordance_score.py score --llm-answers ... --llm-sha256 ...` refuses a file whose
  hash differs.
- **Analysis.** For every question, the LLM–gold kappa with its clustered interval and the LLM–gold Jaccard for
  itemised answers, reported next to the CoResearcher–gold values. This comparison is descriptive; the
  pre-registered criterion of section 7 applies to CoResearcher only. The LLM arm is not a judge and never
  contributes to the gold label.

## 8. What makes a good task, and balance across answers

A task is accepted when it is:

- **Real:** a hypothesis that could appear in the proposer's field, not a puzzle written for the benchmark.
- **Formalizable:** its variables can be given finite domains or real ranges without losing what the hypothesis says
  (checked by Q5).
- **Discriminating:** it includes a rival, or observations, or both, so that Q3 or Q4 can be asked.

Kappa is unstable when one answer dominates. Proposers are therefore asked to include some flawed hypotheses as
they really occur in their field: premises that cannot hold together, claims nothing could refute, rivals that
are in fact equivalent. The maintainers track the answer distribution expected by proposers and invite tasks for
under-represented answers before judging begins. Proposer expectations are never used as gold labels.

## 9. Rounds and evolving criteria

The questions, the answer sets and the disagreement taxonomy may need to change as experience accumulates. They
change only **between rounds**:

- Each round has its own protocol version and SHA-256, fixed before its first judgment.
- Nothing changes within a round. Results are reported per round and never pooled across protocol versions.
- Changes for the next round come from the disagreement audit of the previous one, and are recorded with the reason.
- **What the questions missed.** Q6 critiques are grouped by the adjudicator. A recurring weakness becomes a
  candidate question for the next round only if it can be stated as a check on the formal object; otherwise it is
  recorded as outside CoResearcher's formal scope.
- **Saturation.** If CoResearcher matches the gold label on nearly every task of a round while judges also agree
  with each other, the tasks were too easy for the formal layer to be tested. The next round asks proposers for
  harder cases: more variables, subtler premise conflicts, rivals that differ in few states.

## 10. Size

- **Pilot:** 20 tasks, 4–6 scientists, 2 judges per task. The goal is to test the forms, the timing and the
  disagreement taxonomy, not to estimate kappa precisely.
- **Main study:** about 100 tasks. With 2 judges per task, kappa intervals are then roughly ±0.10–0.15; fix the
  exact number after the pilot.

## 11. Credit, intellectual property and confidentiality

- Co-authorship on the benchmark paper for proposers of at least two accepted tasks and for judges of at least ten
  tasks.
- Hypotheses remain the intellectual property of their proposers.
- Confidential tasks are run on local hardware only (ADR-SOVEREIGNTY-030). They are reported only in aggregate.
  Unlike benchmarks that publish every accepted task and review thread, publication here is opt-in per task.

## 12. Out of scope

The benchmark does not ask scientists or CoResearcher to rate how important, novel or interesting a hypothesis is.
CoResearcher judges the formal soundness of a hypothesis: whether it can be refuted, whether its premises hold
together, whether data refute it, and how it relates to its rivals. Judging scientific value or "taste" is the
scientists' role, and other benchmarks measure it.

## 13. Known limitations

- Only hypotheses whose variables can be given finite domains can be formalized (ADR-059).
- The proposer writes both arms, so formalization quality depends on them. Q5 review and the disagreement audit
  measure that effect but do not remove it.
- Kappa is unstable when one answer dominates, for example if almost every hypothesis is falsifiable. Raw agreement
  and confusion matrices are always reported next to it.
