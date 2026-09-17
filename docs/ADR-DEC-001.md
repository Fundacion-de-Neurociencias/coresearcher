#ADR-DEC-001: Decision ≠ Action (The DecisionGraph)

**Version 1.0.0** - Architecture Decision Record  
**Status**: Canonical Reference - Ontological Governance

## 1. Context

Until version ARQ-001, CoResearcher operated as a pure *Traceability Engine*. The system efficiently modeled the "What" (via `ACTION-XXXXXX`) and the "Where" (via `EvidenceGraph` and `CLAIM-XXXXXX`).
However, the system suffered from a fundamental gap in its governance model: **it was blind to intentionality**. 

We could audit that agent X extracted claim Y from source Z, but we could not audit why agent

## 2. Decision

We formalize **Decision** as a first-order ontological primitive, strictly differentiated from **Action**.
- **Action (`ACTION-XXXXXX`)**: It is mechanistic. It is the physical execution of a task (e.g. reading a PDF, invoking an API, processing text).
- **Decision (`DECISION-XXXXXX`)**: It is teleological and directional. It is an act of governance that allocates resources, rules out alternatives, and provides a rational justification based on an existing state of evidence.

To support this primitive, the **DecisionGraph** is introduced.

## 3. Structural Relationship

The `DecisionGraph` does not replace the `EvidenceGraph`; wraps it.

1. A node `DECISION` is anchored to an evidence state in time (`based_on`: [EG-0001, EG-0002]).
2. An `DECISION` node produces research directives or priorities, which trigger quests (`directed_towards`: [CLAIM-XXXXXX]).
3. Crucially, an `DECISION` node permanently documents unexplored branches (`alternatives_discarded`), enabling counterfactual traceability.

## 4. Consequences

### Positive
- CoResearcher successfully transitions from being a traceability engine to a mature governance engine.
- Algorithmic responsibility becomes measurable. We can audit the quality of the "decider" by comparing the success rate of their historical decisions.
- Provides a high value training *log* ("Decision History Value") for future strategic decision making models.

### Negatives / Risks
- Adds structural complexity to the registration layer.
- Requires executing agents to be able to verbalize their *rationale* before forking expensive execution flows, which increases token consumption and latency on orchestration nodes.

## 5. Reference Implementation
The data schema that supports this decision is formalized in `schemas/decision_graph.yaml`.