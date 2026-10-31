# Documentation index

Start with the [README](../README.md). This page maps the rest of the documentation.

## Reference (generated or verified)

| Document | Purpose |
| --- | --- |
| [REST API](reference/API.md) | Every endpoint, generated from the OpenAPI contract |
| [OpenAPI contract](../schemas/openapi.json) | Machine-readable contract shared with the TypeScript packages |
| [Claims register](reference/CLAIMS_REGISTER.md) | Each claim, its supporting script or test, data origin and last result |
| [Confidence intervals](reference/CONFIDENCE_INTERVALS.md) | 95% intervals for every benchmark proportion with printed counts |
| [Module maturity](reference/MODULE_MATURITY.md) | How each discovery module is used: integrated, tested, exercised or prototype |
| [Sakana ED polarity case](reference/cases/SAKANA_ED_POLARITY.md) | Showcase: an agentic-science rubric claim proved by z3 and Lean, with the necessity of each assumption |
| [Local smoothing statement fidelity](reference/cases/LOCAL_SMOOTHING_STATEMENT_FIDELITY.md) | Do six Lean Comparator statements say what the paper claims? Range equivalence by z3, junk-value lint, coverage map (ADR-070) |
| [Collatz: what is checkable](reference/cases/COLLATZ_CHECKABLE.md) | Partial-results DAG of the open 3x+1 problem, exact checks (Terras, 2-adic lift, cycle bound reproducing Eliahou) |
| [Mahler scalar obligations](reference/cases/MAHLER_SCALAR_OBLIGATIONS.md) | Obligation ledger pilot (ADR-076): identities and every pointwise inequality (first bullet on R, (3) on R^2) proved by interval arithmetic and Laurent-Taylor tail models; for the segment inequality, its reduction, the short-width inputs and the middle and large widths proved, the tails checked numerically; independent of the authors' programs |
| [External results program](reference/EXTERNAL_RESULTS_PROGRAM.md) | What was done in response to Sakana, OASE and openai/math (Oct 2026), how, why and what for; lessons and next mechanisms |
| [Proof pipeline](reference/PROOF_PIPELINE.md) | Reproducible obligation proofs: one-command rerun, SHA-256 manifest, fast audit that rejects stale or unverified proofs (ADR-076) |
| [openai/math time travel](reference/cases/OPENAI_MATH_TIME_TRAVEL.md) | Would our checks have caught the 17 real corrections of the openai/math release? Pre-registered benchmark (1 real hit, citation resolution), and the import obligations and citation gate built from its misses (ADR-077) |

## Architecture

| Document | Purpose |
| --- | --- |
| [Architecture specification](architecture/ARCHITECTURE.md) | Canonical description of layers, engines and data flows |
| [Ecosystem boundaries](architecture/ECOSYSTEM_BOUNDARIES.md) | Responsibilities of CoResearcher, DataAILab and EdiTXT |
| [Observer and ledger](architecture/scientific-ledger.md) | Scientific activity ledger and provenance |
| [Architecture folder](architecture/) | Supporting architecture notes |

Superseded architecture documents are kept in [archive/architecture](archive/architecture/).

## Decisions

Architecture decision records live in [decisions/](decisions/). Each one states context, decision and consequences.

## Governance

[Governance and policies](governance/): constitutions for each subsystem, the [language policy](governance/LANGUAGE_POLICY.md), visibility levels and the constitution index.

## Research and validation

[Research notes](research/): theory, validation plans and conceptual models behind the engines.

## Strategy

[Strategy](strategy/): product positioning, competitive landscape and institutional context.

## Sprint reports

[Sprints](sprints/): dated reports of individual development sprints. They record what was tried, not current behaviour.

## Public material

[Public overview](public/README.md): a non-technical description of the project.
