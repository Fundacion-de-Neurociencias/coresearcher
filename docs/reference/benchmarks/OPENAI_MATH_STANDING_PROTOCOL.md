# openai/math time-travel benchmark: standing assumptions (ADR-091), pre-registered protocol

Status: frozen before any standing text was extracted or read. Its SHA-256 is stored in
`OPENAI_MATH_STANDING_PROTOCOL.sha256` and in the ADR-085 freeze log. The runner
(`openai_math_revision_bench.py typed --variant standing`) refuses to start if the file has changed.

## 1. Question

The unbounded re-measure (`OPENAI_MATH_UNBOUNDED_RESULTS.md`) found that the remaining undischarged hypotheses have
counterexamples the citing passage allows. The passage window, 55 lines around the citation, does not state the
bounds the cited results need, such as n ≥ 3. A manuscript usually fixes such bounds once, as standing assumptions.

ADR-091 lets a citing context inherit the standing variables and assumptions of its manuscript. The passage wins where
both speak, and a standing assumption is inherited only when every name in it is a variable of the merged context.

**Questions.**

1. With standing assumptions extracted blind for each manuscript version, which remaining "not discharged" findings
   are discharged?
2. Which remain, and why?
3. Does any finding appear or disappear at a defect location?

Scope: formal soundness only.

## 2. Inputs

- **Unchanged.** The case-scoped registry and the unbounded citing contexts.
- **The only new input.** A standing context (variables, assumptions) for each manuscript version that uses a
  registered result whose hypotheses have formal predicates.

## 3. Standing text (mechanical) and blind extraction

- **Standing text.** For each such version, every paragraph of its `.tex` sources (comments removed, in file order)
  that contains one of these markers:
  - "throughout";
  - "we assume";
  - "standing";
  - "unless otherwise";
  - "we fix";
  - "we always assume";
  - "conventions";
  - "notation".

  The text is capped at 400 lines. It has no line numbers and no file names.
- **Variables of interest.** The names used in the formal predicates of the registered results that the version
  cites, with the registry writers' one-line meanings.
- **The extractors.**
  - Fresh agent sessions. Their instructions are recorded verbatim in
    `openai_math_chain_procedure/STANDING_INSTRUCTIONS.md` before any extractor starts.
  - Packets have opaque ids and are shuffled with seed 20261103. Every third packet goes to the same extractor.
  - An extractor sees no citation passage and no defect location.
- **What they return.** For each packet, standing `variables` and `assumptions` about the variables of interest (and
  auxiliary variables such as k in n = 2k), only as the standing text states them, with unbounded integers where the
  text gives no bound.
- **Assembly.** `standing-contexts` attaches each record to every citing context of its version and writes
  `openai_math_standing_contexts.json`. That file is frozen before the run. The coordinator may repair JSON syntax
  only.

## 4. Run and scoring

- **The run.** `typed --variant standing` writes `openai_math_standing_results.json`.
- **Scoring and adjudication.** As in the earlier protocols, next to the unbounded re-measure. Every hypothesis that
  changes outcome is listed.
- **Regression.** The regression expectations are updated in the same pull request.
