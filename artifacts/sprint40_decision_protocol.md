# Sprint 40 — Decision Observatory Protocol

## Evidence, not inference.

## Selection

**90 items selected** (30 per repo) from:
- MNE-Python (`mne-tools/mne-python`)
- Nilearn (`nilearn/nilearn`)
- PyBIDS (`bids-standard/pybids`)

### Criteria
- Closed
- ≥ 10 comments  
- Duration > 7 days
- ≥ 2 participants
- PRs included: Yes (GitHub treats PRs as issues in the API)

### Reality check
- MNE-Python: 30 items selected (all PRs — high discussion volume occurs in PRs)
- Nilearn: 30 items selected (mix of issues and PRs)
- PyBIDS: 30 items selected (mix of issues and PRs)

## Workflow

For each item:

1. Read the body
2. Scan the conversation for:
   - Explicit decision statements ("we decided", "I'll go with", "the approach is", "final", conclusion markers)
   - Evidence presented (data, benchmarks, experiments, user reports, literature citations, expert opinions)
   - Alternatives discussed (counterproposals, competing approaches)
   - Disagreement markers (conflict, pushback, different opinions)
   - Final recoverable outcome

3. Classify using **only** direct evidence from the thread

## Q-Questions (Spanish, as specified)

### Q1: ¿Existe una decisión explícita?

Values: YES / NO

Explicit means: the text directly states a decision or choice was made.

### Q2: ¿Qué decisión fue tomada?

Max 50 words. Summarize the actual decision using exact language from the thread.

### Q3: ¿Qué evidencia se utilizó?

Categories (select all that apply):
- DATA
- BENCHMARK  
- EXPERIMENT
- USER_REPORT
- LITERATURE
- EXPERT_OPINION
- OTHER

### Q4: ¿Existieron alternativas discutidas?

Values: YES / NO

### Q5: ¿Hubo desacuerdo?

Values: YES / NO

### Q6: ¿La decisión final es recuperable leyendo el hilo?

Values: YES / NO

## Deliverables

- `artifacts/sprint40_decision_observation.csv` — observations per item
- `artifacts/sprint40_decision_statistics.md` — aggregate statistics
- `artifacts/sprint40_decision_examples.md` — 10 best examples

## Success Criteria

Hypothesis is supported ONLY if:
- >70% of issues have recoverable decisions  
- >50% contain alternatives OR disagreement

Otherwise: **Decision ≠ unit of comprehension** — hypothesis must be revised.

## Notes on Scope

This sprint originally aimed for 30 standalone issues per repo (90 total). After selection, the actual breakdown was:
- MNE-Python: 30 PRs (no standalone issues ≥10 comments exist)
- Nilearn: 30 items (issues + PRs)  
- PyBIDS: 30 items (issues + PRs)

Given the `.clinerules` constraint against placeholders and for verifiable data, this is the actual observational pool. Any generalization to "issues per repo" is limited by repository-specific discussion norms.
