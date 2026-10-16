# ADR-DISCOVERY-063: Research lifecycle with stage gates

**Status:** Accepted (effect on reliability not measured)
**Date:** 2026-10-16
**Module:** [`python/discovery/research_lifecycle.py`](../../python/discovery/research_lifecycle.py)
**API:** `GET /api/lifecycle/template`, `POST /api/lifecycle/projects`, `GET /api/lifecycle/projects[/{id}]`,
`POST /api/lifecycle/projects/{id}/results`, `GET /api/lifecycle/projects/{id}/gate`,
`POST /api/lifecycle/projects/{id}/gate/pass`, `POST /api/lifecycle/projects/{id}/rework`,
`POST /api/lifecycle/projects/{id}/release`, `GET /api/lifecycle/watch`, `GET /api/lifecycle/ontrack`

## Context

CoResearcher already has the pieces of a disciplined research process, but nothing ties them together. The
formalizer benchmark has a protocol and a freeze rule, the formal evaluator, z3 and Lean act as independent
verifiers, and the claims register records each outcome. Whether a project followed that process lived in prose
and in the maintainers' memory. Two things in round 0 showed the cost: a prompt fix had to be held back because
applying it before the dataset freeze would overfit, and the exploratory results had to be labelled by hand as
"not the pre-registered round".

The Agentic Scientist work from Sakana AI (see the [reading note](../research/AGENTIC_SCIENTIST_READING_NOTE.md))
reports that reliable autonomy depends on an orchestration layer that checks every stage against a rubric, as well
as on the base model. OnTrack, the Fundación's control and development system, is building the product lifecycle
for every product (stage gates, versions, releases, policies). This ADR is the research-level counterpart inside
CoResearcher. OnTrack governs products from outside. This module governs research projects from inside and exports
their state to OnTrack.

## Decision

1. **Stages and gates.** A project moves through QUESTION, HYPOTHESIS, PROTOCOL, EXECUTION, CONTROLS, ANALYSIS and
   REPORT, in that order. Each stage ends at a gate with a checklist from a template (`default` today).
2. **Four kinds of check, and who may satisfy them.**
   - VERIFIER: only an independent tool (role `VERIFIER_TOOL`).
   - HUMAN: only a person (role `HUMAN`).
   - ARTIFACT: a path and its SHA-256.
   - RUBRIC: a number that meets the template's threshold.

   An agent's self-check is recorded but never satisfies a VERIFIER or HUMAN check. This is the main difference
   from self-checking agents: the producer of the work cannot certify it.
3. **Gate decisions.**
   - PASS: every required check is satisfied.
   - FAIL: a required check failed.
   - PENDING_HUMAN: only sign-offs are missing.
   - INCOMPLETE: anything else is missing.

   Only PASS advances the project.
4. **Versions.** Each passed gate creates a version whose digest is the SHA-256 of the previous digest, the stage
   and the accepted evidence. The history is tamper-evident.
5. **Rework.** Reopening a stage supersedes its gate and every later one and clears their results. The reason is
   required and appears in the release notes.
6. **Releases and policies.** A project can be released once its report gate passes. The kind is decided by policy,
   never by the caller:
   - PREREGISTERED only if the protocol gate held from before execution to the report.
   - EXPLORATORY if the protocol was reopened after execution. This rule is the round 0 lesson, now enforced.

   The release records the MET and NOT_MET criteria scored in the analysis stage.
7. **Agents, deterministic.**
   - `LifecycleWatcher` reports, without changing anything:
     - stalled stages;
     - gates waiting on a person;
     - reports passed but not released;
     - artifacts whose file no longer matches the hash a gate accepted (for example, a frozen dataset edited after
       the freeze).
   - `release_notes` writes the notes from the log: outcome first, criteria not met in bold, then gates with their
     verifiers and sign-offs, then reworks. No language model writes or judges anything here (ADR-DISCOVERY-002).
8. **Event log.**
   - Every change is an event, and the state is rebuilt by replaying the events.
   - With `CORESEARCHER_LIFECYCLE_LOG`, the events are appended to a JSON Lines file.
   - Events carry `schema_version` (1). A log with an unknown version is refused rather than misread. Future schema
     changes add an upgrade step in `_upgrade`, the migration point.
9. **OnTrack export.** `GET /api/lifecycle/ontrack` returns each project in the `coresearcher.lifecycle/v1` shape:
   stage, gate decision, checklist completion, version, digest, latest release and watcher findings. The shape is a
   draft until OnTrack's PLM model is published; field names follow the vocabulary OnTrack uses (stage gates,
   versions, releases, policies).

## Consequences

- The formalizer round 1, the concordance pilot and the Lean oracle can be run as lifecycle projects. A
  pre-registered result is then distinguishable from an exploratory one by construction, not by a sentence in a
  report.
- Rubric and artifact checks can be filled by agents, so most of a project can be automated. Verifier and human
  checks remain the bottleneck by design.
- OnTrack can read CoResearcher's research state without knowing its internals.

## Limits

- The default checklist is the maintainers' first version. It has not been tried on a real project yet; the first
  run (formalizer round 1) will show which checks are missing or useless.
- The module checks who submitted a result, not whether the result is true. A tool that reports success wrongly, or
  an actor who misstates their role, defeats it. The API key is the only authentication.
- Whether gates make the research more reliable is not measured. The Sakana ablation is evidence for their system,
  not for this one.
- The OnTrack export is unilateral until the two schemas are reconciled.
