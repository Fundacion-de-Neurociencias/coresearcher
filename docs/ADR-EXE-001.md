#ADR-EXE-001: Auditable Distributed Execution (MissionGraph)

**Version 1.0.0** - Architecture Decision Record  
**Status**: Canonical Reference - Distributed Execution

## 1. Context

The ARQ-001 architecture solved retrospective traceability (What do we know) with the `EvidenceGraph`.
The ARQ-002 architecture solved directional governance (Why we investigated) with the `DecisionGraph`.

However, to come full circle, we lacked a formal structure for “How we do it” in a multi-agent orchestration environment (NeuroOS). The absence of this structure forced `EvidenceGraph` to try to register the status of the "work in progress", generating temporal paradoxes (orphan claims).

## 2. Decision

We formalize the **Auditable Distributed Execution** ontology under the `Mission → Brief → Execution` pattern, consolidated in the **MissionGraph**.

1. **Mission (`MISSION-XXXXXX`)**: A bounded and trackable objective derived directly from an `DECISION`. Example: "Extract claims from recent literature on p-tau217".
2. **Brief (`BRIEF-XXXXXX`)**: A self-contained, deterministic, immutable contextual package that is delivered to the executing agent. Specifies instructions, allowed tools, and explicit success criteria. This allows the agent to operate stateless from the central orchestrator.
3. **Execution (`EXEC-XXXXXX` or `ACTION-XXXXXX`)**: The physical trace (logs, tool calls, retries) of the agent trying to fulfill the Brief. This trace will result in the creation of new `EvidenceGraph` components (such as Claims and Artifacts) if successful.

## 3. Consequences

### Positive
- **Strict Decoupling:** Protects the `EvidenceGraph` from any incomplete, speculative or ongoing states.
- **Massive Scalability:** Allows thousands of `Briefs` to be queued, distributed and parallelized across multiple agents without blocking, enabling a true asynchronous architecture.
- **Execution Traceability:** If a subagent fails, the failure is recorded in the `Execution` node associated with the `Brief`, allowing an "Agent Reliability" analysis without affecting the demonstrated scientific knowledge.

### Negatives
- Adds a third ontological layer to the system (Evidence, Decision, Mission), increasing the cognitive load for external developers and integrators.

## 4. Reference Implementation
The data and validation model is instantiated in the file `schemas/mission_graph.yaml`.