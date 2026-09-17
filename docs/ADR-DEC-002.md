#ADR-DEC-002: Evidence Never Contains Intent

**Version 1.0.0** - Architecture Decision Record  
**Status**: Canonical Reference - Ontological Governance

## 1. Context

During the adversarial review of phase ARQ-002, a serious semantic vulnerability was detected when linking `DecisionGraph` to `EvidenceGraph`. By allowing decisions to route future investigation toward potential assertions, there was a risk that `EvidenceGraph` would begin to absorb intent metadata (e.g., `selected_because`, `priority`,

The `EvidenceGraph` was designed strictly as a retrospective immutable record (what is known empirically and where it came from). Mixing work in progress (intention) with demonstrated knowledge (evidence) erodes the ontological purity of the system and degrades it to a simple task manager.

## 2. Decision

We formalize the fundamental constitutional rule: **Evidence never contains intent.**

1. A node `Claim` or `Artifact` within the `EvidenceGraph` exists solely and exclusively to describe the state of knowledge and its empirical anchoring.
2. It is strictly prohibited to include fields such as `priority`, `intent`, `hypothesis`, `selected_because`, or
3. Any representation of future work, directional intent, or governance will reside exclusively in the `DecisionGraph` or the `MissionGraph`.

## 3. Consequences

### Positive
- Preserves the immutability and purity of `EvidenceGraph` as a data structure suitable for pure scientific auditing.
- Avoids semantic leakage where the "urgency" or "strategic direction" of a research program corrupts the algorithmic interpretation of the evidence itself.

### Negatives / Restrictions
- Increases the complexity of the query engine. To answer the question *"What evidence did we validate last week because of strategic decision

## 4. Reference Implementation
The rule is linked to constitutional policies through `schemas/constitution_rules.yaml`. Any evidence graph containing intent fields will be automatically rejected.