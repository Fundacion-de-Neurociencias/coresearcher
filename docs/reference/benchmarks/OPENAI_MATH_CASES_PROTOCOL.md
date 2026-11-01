# openai/math time-travel benchmark: case-scoped hypotheses (ADR-089), pre-registered protocol

Status: frozen before any hypothesis was tagged. Its SHA-256 is stored in `OPENAI_MATH_CASES_PROTOCOL.sha256` and in
the ADR-085 freeze log. The runner (`openai_math_revision_bench.py typed --variant cases`) refuses to start if the
file has changed.

## 1. Question

The constrained re-measure (`OPENAI_MATH_CONSTRAINED_RESULTS.md`) left two kinds of artefacts.

- **Hypotheses from another case.** Three uses of a cited proposition that name its part (2) were still held to the
  hypothesis of its part (1), and flagged as "not discharged".
- **Conditions written as atoms.** A field value that encodes a condition ("Z if n even and orientable, else Z/2") was
  compared with the value of one branch and gave a decided MISMATCH.

ADR-089 changes two things:

1. **Case-scoped hypotheses.** A hypothesis can be scoped to cases of the result. A citation that names another case
   does not need it (NOT_APPLICABLE).
2. **Conditional atoms.** A field value that encodes a condition is not compared as an atom (UNCOMPARED). This rule
   was written after reading the constrained results. Its effect on the frozen constrained inputs is reported apart, as
   a post-hoc effect.

**Questions.**

1. With hypotheses scoped blind, do the other-case findings disappear?
2. Does anything else change: a decided finding gained or lost at a defect location, or in the alarm load?

Scope: formal soundness only.

## 2. Inputs

- **Unchanged.** Everything frozen for the constrained re-measure, including its citing contexts and the `case` each
  of them names.
- **The only new input.** For every constrained registry entry that declares `cases`, the case scope of each of its
  hypotheses.

## 3. Blind tagging

- **The tagger.** One fresh agent session. Its instructions are recorded verbatim in
  `openai_math_chain_procedure/CASES_INSTRUCTIONS.md` before it starts.
- **What it receives.** Each entry's statement, its declared cases and the list of its hypotheses. No citing text.
- **What it returns.** For each hypothesis, the cases it applies to (`{name: [cases]}`), or `{}` when it applies to
  every case.
- **Assembly.** `cases-registry` merges the tags into `openai_math_cases_registry.json`, which is frozen before the
  run. The coordinator may repair JSON syntax only.

## 4. Run and scoring

- **The run.** `typed --variant cases` writes `openai_math_cases_results.json`.
- **Scoring and adjudication.** As in the earlier protocols. Results are reported next to the constrained re-measure.
- **Regression.** The regression expectations are updated in the same pull request.
