# AI-expert concordance, round 1: freeze record

**Frozen:** 2026-11-02, before any judge saw a task. Owner decision of 2026-11-01: the expert arm is Claude Science, an
AI system, not human researchers. Results are reported as **AI-expert concordance, never as human validation**.

| Artifact | SHA-256 |
| --- | --- |
| 20 tasks (`tasks/*.json`, concatenated in name order) | `4cf04b185c907c7c44dcab515fc660a14275be800c06a294bb64942b258f543d` |
| Claude Science text (`claude_science_prompt.txt`, pack v1) | `8cb459ba1aa078215fd727aa39a089bfb595f344a633c574facd7cede4ac0090` |
| CoResearcher's sealed answers (`coresearcher_answers.json`) | `c1b2b5b132631ccb2c961d72143aa1eeb13ea95073182d5ef98507ecf9987132` |
| Judge instructions (LLM arm system prompt, `concordance-llm-arm-v1`) | `525db1a5926e51647d05ab269f98e66964faa729c0fb22e63c935a23f466864d` |
| Second-family judge answers (qwen2.5:14b, `local_llm_answers_qwen14.json`), sealed before any comparison | `4ae41a37fafb8de9dd6c708b3abb537c398b79bf33990e6e721d15ac627b4f6d` |

## Design

- **Tasks.** 20 tasks built from the formalizer benchmark sets: all 12 held-out items, plus 8 from the round-0 set
  chosen to cover every Q1 verdict. Each task has its gold formal object (gold-checked), labelled premises, one or two
  observation rows produced by the evaluator (order and presence randomized with seed 20261102), and, for 8 tasks, a
  hand-written rival with its formal object.
- **Arms.**
  - CoResearcher judges the formal objects (sealed above).
  - Claude Science reads only the prose: the owner pastes the text once and returns the reply verbatim.
  - A second judge from another model family, a local Ollama model, answers the same prose through
    `concordance_llm_arm.py` with the same instructions.
- **Metrics.** Agreement and Cohen's kappa per question between CoResearcher and each judge. Every disagreement is
  listed and classified by hand as a formalization gap, a judge error, ambiguous wording, or a CoResearcher error.
  A missing or malformed answer is INVALID and counts as a disagreement.

## Limitations, stated before the run

- AI judges, not humans. Claude Science and the maintainers' tooling share a model family, so agreement can be
  inflated by shared habits. The second-family judge is there to show how large that effect is.
- The tasks come from benchmark sets the maintainers wrote. The gold formal objects decide CoResearcher's answers,
  so this measures whether the formal reading matches an expert reading of the same words. It does not measure
  whether CoResearcher can formalize unseen prose (that is the formalizer benchmark, ADR-093).
- n = 20, so intervals are wide and the study is descriptive.
