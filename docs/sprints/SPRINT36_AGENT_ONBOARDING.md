# Sprint 36: Agent Onboarding Validation
## Can an Agent Become Productive Faster with a Scientific Activity Ledger?

---

## Strategic Context

Sprint 35 established the comprehension experiment protocol for humans.

Sprint 36 shifts focus to **AI agents**.

The central hypothesis:

> A Scientific Activity Ledger reduces onboarding cost for AI agents
> compared to raw scientific sources (GitHub repos, papers, datasets).

This is the product bet:

```text
CoResearcher = context layer for agentic science
```

Not just a human-readable documentation artifact.

---

## Experiment Design

### Projects

Select 3 public scientific software projects:
- MNE-Python
- Nilearn
- PyBIDS

### Conditions

**Condition A: Raw Sources**
- Agent receives:
  - GitHub repository access
  - README
  - Issues/PRs
  - Release notes
  - Linked papers (if any)

**Condition B: Scientific Activity Ledger**
- Agent receives:
  - Generated Scientific Activity Ledger only
  - No direct repository access
  - No paper bodies beyond titles/DOIs in ledger

### Task

Give the agent a fixed, realistic onboarding task:

> "You are joining this project. Based on the provided materials, produce a concise onboarding brief that covers:
> 1. What the project does
> 2. Key artifacts and where to find them
> 3. Active workstreams
> 4. Main contributors
> 5. Recent changes
> 6. Suggested first steps for a newcomer"

### Metrics

| Metric | Measurement |
|--------|-------------|
| Time to first useful output | seconds |
| Completeness | 0–1 score against rubric |
| Accuracy | factual correctness |
| Actionability | can a newcomer act on the brief? |

### Success Criterion

Ledger condition achieves:
- ≥50% reduction in time-to-first-output
- ≤10% drop in completeness/accuracy

If the ledger is slower or much less accurate, the hypothesis is falsified.

---

## Implementation

### What Sprint 36 Does

1. Define agent benchmark harness.
2. Generate ledgers for 3 projects.
3. Prepare raw-source bundles for same 3 projects.
4. Run agent tasks (automated or semi-automated).
5. Compare outputs.

### What Sprint 36 Does NOT Do

- No new connectors
- No new artifact types
- No new inference rules
- No manual ledger curation
- No ontology expansion

---

## Deliverables

1. `docs/SPRINT36_AGENT_ONBOARDING.md`
2. `python/observer/agent_onboarding_benchmark.py`
3. `artifacts/sprint36_agent_onboarding_benchmark.md`

---

## Rationale

The Scientific Activity Ledger only matters if it changes behavior.

For humans: faster comprehension.
For agents: faster orientation → earlier useful contribution.

This experiment tests the agent-side value directly.