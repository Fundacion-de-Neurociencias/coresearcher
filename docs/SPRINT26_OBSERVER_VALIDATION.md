# Sprint 26: Entity Resolution & Real Validation

## Objective

Can CoResearcher reconstruct scientific history automatically?

Not:
> "We have a theory about agentic science"

But:
> "Here is Neurodiagnoses reconstructed automatically. Does it save time to understand?"

---

## Entity Resolution Priority

The core competency: link related activity across sources.

Questions to answer:
- Does this paper belong to the same project as this repo?
- Is this dataset connected to this ontology?
- Are these 4 repos parts of Neurodiagnoses ecosystem?
- Is this agent contributing to the same program?

---

## Deliverables

### 1. Entity Resolver (Básico)
```
Input:
- Repo paths
- Paper references
- Dataset mentions

Output:
- Project ID
- Relationship confidence
- Evidence links
```

### 2. Visibility Filter
Configurable per project:
```yaml
visibility:
  - private      # Nothing external
  - discoverable # Only existence
  - connected    # Aggregates only
  - public       # Full transparency
```

### 3. Ledger Builder v2
Structure:
```
PROGRAM
├─ Objectives
├─ Evidence (commits grouped)
├─ Artifacts (auto-detected)
├─ Contributors (inferred)
└─ Timeline
```

---

## Validation Tests

### Neurodiagnoses
- Multiple repos
- Multiple domains
- Years of history

Questions:
- How many programs inside?
- Are objectives correctly identified?
- Timeline legible?

### GeneForge
- Different structure
- Genetic focus

Questions:
- Can external researcher understand in 1h vs 20h?
- Are scientific efforts separated from engineering?

---

## Success Metrics

**Level 0**: Observer runs without errors
**Level 1**: Reconstructs correct major artifacts
**Level 2**: Identifies correct objectives
**Level 3**: Saves comprehension time

If ledger doesn't save 19/20 hours → back to Entity Resolver.

No more constitutions until this works.