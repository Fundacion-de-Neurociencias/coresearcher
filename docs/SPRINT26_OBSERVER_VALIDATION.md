# Sprint 26: Entity Resolution & Real Validation

## Objective

Can CoResearcher reconstruct scientific history automatically?

Not:
> "We have a theory about agentic science"

But:
> "Here is Neurodiagnoses reconstructed automatically."

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
- File content

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
- What are the 5 main scientific objectives?
- What 20 artifacts have been produced?
- Which workstreams are active vs dormant?

### GeneForge
- Different structure
- Genetic focus

Questions:
- Does it correctly separate papers from infrastructure?
- What are the key objectives?

---

## Success Metrics (Epistemological)

**Level 1**: Precision & Recall
> How many inferred objectives are real vs hallucinated?

Test:
```text
Top 20 inferred objectives
vs
Manuel's actual mental model
```

**Level 2**: Artifact Detection
> Manuscritos, figuras, ontologías, datasets, protocolos

**Level 3**: Active Workstream Identification
> What work is alive vs abandoned?

---

## The Key Test

Apply observer to Neurodiagnoses and compare:

```text
Generated Output:
1. Inference: "APOE4 mechanism exploration"
2. Precision: Correct / Incorrect
3. Evidence: Links to commits/artifacts
```

If objective ≠ real objective → back to Entity Resolver.

No more constitutions until this works.