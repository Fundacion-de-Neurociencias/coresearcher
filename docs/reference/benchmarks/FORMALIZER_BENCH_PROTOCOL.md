# Formalizer benchmark protocol

**Status:** Pre-registered draft, round 0 (seed dataset). Freeze before the first model run.
**Script:** [`scripts/benchmarks/formalizer_bench.py`](../../../scripts/benchmarks/formalizer_bench.py)
**Module:** [`python/discovery/formalizer.py`](../../../python/discovery/formalizer.py) (ADR-DISCOVERY-061)
**Dataset:** [`formalizer_dataset.json`](formalizer_dataset.json)

## 1. Question

When a local language model translates a hypothesis written in prose into the formal object of ADR-DISCOVERY-059/060,
how often does it produce a valid object, and how often does that object mean the same as a careful human
formalization? A formalizer that silently turns a testable hypothesis into an untestable one, or the reverse, would
make every later verdict wrong while looking exact.

## 2. Dataset

21 prose hypotheses across 13 domains (`formalizer_dataset.json`), each with a variable schema and a gold
formalization written by the maintainers. Gold verdicts: 14 `FALSIFIABLE`, 4 `UNFALSIFIABLE`, 2 `SELF_CONTRADICTORY`,
1 `VACUOUS`. The defective items are deliberate: the formalizer must preserve the defect, not repair it.

F21 (added 2026-10-15, after round 0) is a mathematical claim, the smallest instance of the Error Diffusion
polarity invariance from Sakana's Agentic Scientist ([SAKANA_ED_POLARITY.md](../cases/SAKANA_ED_POLARITY.md)). Being a
theorem given its definitions, its gold verdict is `UNFALSIFIABLE`; a formalization that drops one of its assumptions
becomes `FALSIFIABLE` and `STRONGER` than gold (it forbids states the gold allows). Round 0 ran on F01-F20 only.

`formalizer_bench.py gold-check` verifies that every gold formalization has its intended verdict. Before round 1,
two scientists from the Fundación review the gold formalizations; disagreements are resolved by discussion and
recorded in the dataset. The dataset is frozen by recording its SHA-256 in section 7.

## 3. Conditions

- **With schema (primary).** The model receives the prose and the gold variable schema (names, domains, bounds). Its
  output can then be compared with the gold formalization over the same state space.
- **Without schema (secondary).** The model chooses its own variables. Only parse rate and verdicts are measured,
  because logical equivalence needs a shared state space.

Decoding is deterministic (temperature 0, seed 0). One output per item per model; no retries, no prompt changes after
the first run. The frozen prompt is `formalizer-v1` (`python/discovery/formalizer.py`); its SHA-256 is printed by
`gold-check` and stored in every run file.

The predicate language reads `true` and `false` as the constants `True` and `False`, unless a variable has that name
(decided on 2026-10-16, before the freeze). Round 0 showed models writing the JSON forms. Accepting them changes no
meaning, so the prompt is not changed and stays `formalizer-v1`. Round 0 outputs are not re-scored with this rule:
the decision was taken from those items, and only the frozen dataset measures its effect.

## 4. Metrics

Over all 21 items:

| Metric | Definition |
| --- | --- |
| Parse rate | Fraction of outputs that yield a valid formal object matching the schema (`PARSED`) |
| Status counts | `NO_JSON`, `INVALID` (malformed or unsafe predicates), `SCHEMA_MISMATCH`, `PARSED` |
| Vacuous, unfalsifiable and self-contradictory rates | Fraction of evaluated outputs with each verdict |
| Verdict agreement | Fraction of evaluated outputs whose content verdict equals the gold verdict |
| Spurious defects | Outputs with a defect verdict where the gold is `FALSIFIABLE` (translation broke the hypothesis) |
| Missed defects | Outputs whose verdict differs from a defective gold verdict (translation repaired the hypothesis) |
| Equivalence to gold (primary) | Fraction of all items whose output is logically `EQUIVALENT` to the gold, decided by `HypothesisEvaluator.compare` |

`compare` is exact (enumeration or SMT), so equivalence is a proof, not a similarity score. A `STRONGER` or `WEAKER`
output is a different hypothesis and counts as a failure for the primary metric; the report lists the relation per
item so reviewers can see the direction of the error.

## 5. Models

Round 1 runs on the Lenovo Legion with Ollama or LM Studio, so no hypothesis text leaves the Fundación. Candidate
models are fixed before the run and recorded with their exact tags (for example `qwen2.5:14b-instruct-q4_K_M`). Laya
is included if it is served through an OpenAI-compatible endpoint. See
[LEGION_RUNBOOK.md](LEGION_RUNBOOK.md).

## 6. Interpretation

- The benchmark measures translation fidelity on 21 items. It does not measure whether a hypothesis is true or
  whether the gold variables are the right model of the phenomenon.
- With n = 21, a single item moves each rate by about 0.05. Results are descriptive; no model is declared better unless the
  difference survives an exact McNemar test on paired items at alpha 0.05.
- Until a model reaches equivalence to gold of at least 0.80 with no spurious defects, formalizer output is shown in
  the UI as a draft that the researcher must confirm before it is evaluated.

## 7. Freeze record

| Field | Value |
| --- | --- |
| Prompt version | `formalizer-v1` |
| Prompt SHA-256 | recorded at freeze |
| Dataset SHA-256 | recorded at freeze, after the scientists' review |
| Reviewers | to be named |
| Freeze date | pending |
