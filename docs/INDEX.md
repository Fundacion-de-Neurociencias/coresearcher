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

## Architecture

| Document | Purpose |
| --- | --- |
| [Architecture specification](architecture/ARCHITECTURE.md) | Canonical description of layers, engines and data flows |
| [Capability map](architecture/CAPABILITY_MAP.md) | Every discovery module by capability: what it does, ADR, maturity, API or MCP reach, backing claim, data flow, and integration fixes |
| [Functional review](architecture/FUNCTIONAL_REVIEW.md) | What CoResearcher is for, which pipelines exist in code, and what each module really does, with a keep, wire, merge or archive recommendation |
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
