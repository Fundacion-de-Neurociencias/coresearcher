# ADR-DISCOVERY-061: Prose-to-formal formalizer and the formal workbench path

**Status:** Accepted (formalizer fidelity not yet measured)
**Date:** 2026-10-15
**Modules:** [`python/discovery/formalizer.py`](../../python/discovery/formalizer.py),
[`python/discovery/alzheimer_formal_scenario.py`](../../python/discovery/alzheimer_formal_scenario.py)
**API:** `POST /api/hypotheses/formalize`, `GET /api/hypotheses/scenarios/alzheimer`,
`POST /api/discovery/workbench/launch` (new `formal_hypothesis` and `formalize_question` fields)

## Context

ADR-DISCOVERY-059/060 give CoResearcher a formal hypothesis object and exact checks on it. Researchers write
hypotheses in prose, and until now nothing turned that prose into the object: the workbench ignored the question text
and the demo rivals were free-text records.

## Decision

1. **Formalizer.** A language model served through any OpenAI-compatible endpoint (Ollama, LM Studio, vLLM) translates
   prose into the formal object with a frozen prompt (`formalizer-v1`). The model is a translator, not a judge
   (ADR-DISCOVERY-002): its output is parsed, validated and evaluated by the formal evaluator, and nothing else it says
   is used. Outcomes are explicit: `NO_JSON`, `INVALID`, `SCHEMA_MISMATCH` or `PARSED`.
2. **Local first.** The default endpoint is a local Ollama server. Configuration is by environment
   (`FORMALIZER_BASE_URL`, `FORMALIZER_MODEL`, optional `FORMALIZER_API_KEY`). Without a configured model the API
   answers 503; it never falls back to a heuristic.
3. **Drafts.** Every formalizer output is marked `draft: true`. The verdicts are exact for the object, but whether the
   object says what the prose meant is what the formalizer benchmark measures
   ([protocol](../reference/benchmarks/FORMALIZER_BENCH_PROTOCOL.md)). Until a model passes it, the researcher confirms
   the object before relying on its verdicts.
4. **Formal Alzheimer scenario.** The canonical Omega and the three demo rivals are migrated to formal hypotheses.
   The canonical Omega lacked a white matter hyperintensity axis, which the vascular rival needs; it is added (192
   states). Prose that is statistical, causal or spatial cannot constrain a single state, so each rival lists it under
   `not_formalized` instead of approximating it. The formalizations are a draft pending scientist review.
5. **Workbench.** `POST /api/discovery/workbench/launch` accepts a `formal_hypothesis`, or `formalize_question: true`
   to formalize the question over the Alzheimer variables. The response gains a `formal` block: exact evaluation and
   comparison with each formal rival, with the states that discriminate them. The legacy workbench output is unchanged.

## Consequences

- A hypothesis typed by a researcher can now reach the exact evaluator in one call, with the translation step visible
  and auditable.
- The three rivals are pairwise `INCOMPARABLE`: each forbids states the others allow. The discriminating states are
  the observations that would separate them, which is the formal version of a discriminative prediction.
- The earlier claim that the demo prediction `PRED-DISCRIM-01` discriminates the rivals is about correlations across
  subjects and remains outside the formal object.

## Limits

- Formalizer fidelity is unmeasured until the benchmark runs on the Legion.
- The rivals' formal versions are the maintainers' reading of one-sentence statements.
