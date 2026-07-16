# Sprint 26: Entity Resolution & Real Validation

## Objective

Can CoResearcher reconstruct scientific history automatically?

Focus on verifiable reconstruction:
> "Here is Neurodiagnoses automatically reconstructed."

---

## The Reconstruction Hierarchy

```text
FACTS (high confidence)
  ↓
Artifacts
Workstreams
Timeline
Contributors
  ↓
INFERENCES (medium confidence)
Objectives
Hypotheses
Intentions
```

Validate from facts upward.

---

## Deliverables

### 1. Artifact Reconstructor
```
Input:
- Commits
- Files (papers, ontologies, datasets)
- Releases

Output:
- Detected artifacts with confidence
- Manuscripts detected: X
- Ontologies detected: Y
- Datasets detected: Z
- Software modules detected: W
```

### 2. Workstream Identifier
```
Input:
- Temporal activity
- Topic coherence

Output:
- Active workstreams
- Dormant workstreams
- Timeline segments
```

### 3. Evidence Metadata
Every inference must include:
```json
{
  "type": "objective_hypothesis",
  "statement": "X",
  "confidence": 0.75,
  "evidence": ["commit:abc123", "file:ontology.md"],
  "status": "unvalidated"
}
```

---

## Validation Tests

### Neurodiagnoses
Questions (verifiable):
- What manuscripts exist?
- What ontologies exist?
- What datasets exist?
- What workstreams are active?
- What is the timeline?

### GeneForge
Questions:
- What papers have been generated?
- What software modules exist?
- What is the genetic focus?

---

## Success Metrics

**Level 1 - Facts**: Artifact reconstruction accuracy
> 3 manuscripts detected, not "2-5"

**Level 2 - Workstreams**: Active/dormant identification
> "Ontology workstream active 2025-01 to 2025-03"

**Level 3 - Timeline**: Chronological accuracy
> Events in correct sequence

---

## The Key Principle

```text
Do NOT try to guess intentions.

Reconstruct facts, then infer.
```

Validate the observer on what can be audited:
- Files created
- Papers generated
- Datasets produced
- Releases made

Before attempting:
- Research objectives
- Scientific intentions
- Mental models