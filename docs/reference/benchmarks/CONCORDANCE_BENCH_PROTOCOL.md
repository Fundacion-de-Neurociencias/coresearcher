# Hypothesis Verification Concordance Benchmark: protocol

Status: draft for pre-registration. Fix sections 5 and 6 before the first judgment is collected, then record
the SHA-256 of this file with every result.

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
| Task reviewer | Checks the task is well posed and that the formal object faithfully encodes the prose (question Q5) | Yes |
| Judge (≥ 2 per task) | Answers Q1–Q4 independently, from prose and data only | **No** |
| Adjudicator | Resolves judge disagreements into a gold label; classifies CoResearcher disagreements | Yes, after unblinding |
| Maintainer | Runs CoResearcher; never edits tasks or judgments | Yes |

Nobody judges a task they proposed or reviewed. Judges do not discuss tasks before submitting.

## 4. Task format

One JSON file per task, valid against `schemas/hypothesis_verification_task.schema.json`. It has two parts:

**Shown to judges (prose arm):**
- `field`, `statement`: the hypothesis in natural language, as the proposer would write it in a paper.
- `rival_statement` (optional): a competing hypothesis in natural language.
- `observations_table` (optional): observations as a table, with column meanings and provenance (public dataset
  identifier, or "illustrative").
- `context`: the minimum domain background a judge needs; no hints about the expected answers.

**Hidden from judges (formal arm):**
- `formal_hypothesis` and optional `formal_rival`: ADR-059 objects (variables with finite domains, scope,
  assumptions, claims).
- `formal_observations`: the same observations as states over the declared variables.
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

For each answer judges also give a confidence from 1 to 5 and a one-sentence rationale.

**Q5, formalization fidelity** (task reviewers only, before judging starts): does the formal object express the
prose hypothesis? `YES`, `PARTIALLY`, `NO`, with the mismatch described. Tasks rated `NO` are fixed or withdrawn
before judging. Tasks rated `PARTIALLY` stay in and are analysed separately.

## 6. Collecting judgments

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
5. Results are reported separately for tasks rated Q5 = `YES` and Q5 = `PARTIALLY`.

## 8. Size

- **Pilot:** 20 tasks, 4–6 scientists, 2 judges per task. The goal is to test the forms, the timing and the
  disagreement taxonomy, not to estimate kappa precisely.
- **Main study:** about 100 tasks. With 2 judges per task, kappa intervals are then roughly ±0.10–0.15; fix the
  exact number after the pilot.

## 9. Credit, intellectual property and confidentiality

- Co-authorship on the benchmark paper for proposers of at least two accepted tasks and for judges of at least ten
  tasks.
- Hypotheses remain the intellectual property of their proposers.
- Confidential tasks are run on local hardware only (ADR-SOVEREIGNTY-030). They are reported only in aggregate.

## 10. Known limitations

- Only hypotheses whose variables can be given finite domains can be formalized (ADR-059).
- The proposer writes both arms, so formalization quality depends on them. Q5 review and the disagreement audit
  measure that effect but do not remove it.
- Kappa is unstable when one answer dominates, for example if almost every hypothesis is falsifiable. Raw agreement
  and confusion matrices are always reported next to it.
