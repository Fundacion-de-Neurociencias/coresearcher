# Reading note: Sakana AI, orchestrating coding agents for scientific research

**Status:** bookmark. Written on 2026-10-16 from a shared summary; the paper itself has not been read yet. Add the
reference and correct this note once it has.

## What the summary reports

- **System.** The Agentic Scientist splits a research project into stages: task drafting, ideation, planning,
  sandboxed experiments, baselines and ablations, analysis, and report writing.
- **Agents and controller.** Each stage runs on a coding agent that checks its own work. A meta-controller runs many
  of these agents in parallel and checks every stage against a rubric.
- **Result.** A development version helped write a paper accepted as a main-conference talk at ALIFE 2026, after
  human verification and edits.
- **Ablations.** Reliable autonomy depends on the orchestration layer as well as on the base model.

## What it means for CoResearcher

1. **Gate every stage.** CoResearcher had rubrics (the concordance protocol, the formalizer thresholds) but nothing
   that stopped a project from moving on without meeting them. This is now the research lifecycle of
   [ADR-DISCOVERY-063](../decisions/ADR-DISCOVERY-063-RESEARCH-LIFECYCLE-STAGE-GATES.md).
2. **Orchestration matters as much as the model.** Round 0 points the same way.
   - The Lean cross-check went from 3 of 7 to 12 of 12 entailments by changing the script around the prover, not the
     prover.
   - The formalizer's 0.50 may gain more from verification and retries around the model than from a larger model.
     That is a hypothesis to test in the formalizer protocol, not a conclusion.
3. **Independent verification over self-checking.** In the summary, each agent checks its own work. CoResearcher's
   gates do not accept that for verifier checks: z3, Lean and the formal evaluator are independent of the agent that
   produced the work. This is where the two designs differ, and it is worth keeping.
4. **Humans before publication.** The paper was published after human verification and edits. This matches the
   draft mode of the formalizer and the human sign-offs in the gates.

## What not to copy

- **End-to-end autonomy without pre-registration.** A system that drafts, runs and writes up its own studies can
  produce plausible results that nobody committed to in advance. The claims register and the PREREGISTERED or
  EXPLORATORY release kind exist to prevent this.
- **A conference acceptance as the measure of success.** It shows that reviewers accepted the paper, not that its
  findings hold.

## Relation to OnTrack

OnTrack governs the lifecycle of every product from outside (stage gates, versions, releases, policies). The
research lifecycle governs research projects inside CoResearcher and exports their state to OnTrack in the
`coresearcher.lifecycle/v1` shape. The vocabulary is shared so that the two can be reconciled.
