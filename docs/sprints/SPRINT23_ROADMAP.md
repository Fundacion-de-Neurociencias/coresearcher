# Sprint 24 Roadmap
## One Question, One Researcher, Complete Traceability

**From Theory to Reality in 7 Days**

---

## The Only Test That Matters

> Can Dr. Vasquez go from QUESTION to PREPRINT in one week with complete traceability?

If YES → everything else can be built on top
If NO → constitutional documents are irrelevant

---

## What We Build (Total: ~500 lines)

### Week 1: The Template Repository

```yaml
# Repository: coresearcher/template-alzheimer-biomarkers
structure:
  ontology.yaml      # Canonical scientific coordinates
  questions/         # Template for questions
  actions/           # Log of all executions
  artifacts/         # Published outputs
  workflows/         # GitHub Actions definitions
```

### Week 2: The researcher experience

Dr. Vasquez clones/forks template:
```
git clone github.com/coresearcher/template-alzheimer-biomarkers
cd alzheimer-biomarkers
```

She adds her question to `questions/question-001.md`:
```markdown
# QUESTION-000001
What blood biomarkers predict preclinical Alzheimer's disease?

Ontology: Science/Medicine/Neurology/Alzheimer Disease/Biomarkers

Actors:
- Elena Vasquez (ORCID-0000-0002-1825-0097)
```

### Week 3: Agent Execution

She runs agent workflows:
```bash
# Launch agent for claim extraction
gh workflow run extract-biomarkers.yml \
  --repo elena-v/alzheimer-biomarkers \
  --field query="plasma pTau217 biomarker alzheimer"

# Results automatically logged to actions/action-001.json
```

Every action gets:
- Model used
- Prompt version
- Evidence sources
- Timestamp
- Outcome

### Week 4: Review and Validation

Agent reviews are automatic:
```yaml
# Actions review each other
ACTION-00123 (generated claim)
  ↓
ACTION-00124 (review: score 0.85, accepted)
  ↓
ACTION-00125 (trust score updated)
```

Human review via comment on question:
```
@reviewer please validate claim-00123 methodology
```

### Week 5: Artifact Publication

When ready:
```bash
# Create preprint with complete provenance
gh workflow run publish-preprint.yml

Output:
DOI: 10.5281/zenodo.12345678
Contains:
- claims.json
- actions.json  
- methodology.md
```

### Week 6: Collaboration

Others can:
- Fork the repo
- Add their questions
- Replicate actions
- Merge results

### Week 7: Complete Traceability

Anyone can see:
```
QUESTION-000001
├── ACTION-00123 (extract)
├── ACTION-00124 (analyze)
├── ACTION-00125 (review)
├── ACTION-00126 (validate)
└── ART-000456 (preprint)
```

---

## The 3 Primitives in Action

### QUESTION
- "What blood biomarkers predict Alzheimer's disease?"
- Anchored to ontology path
- Created by ORCID identity

### ACTION
- "Extract biomarkers from literature"
- "Review methodology"
- "Generate preprint"
- All types unified under ACTION

### ARTIFACT
- "Preprint on Zenodo with DOI"
- Linked to all contributing actions

---

## The Free Stack (All Gratis)

| Component | Tool | Cost |
|-----------|------|------|
| Identity | ORCID | $0 |
| Ontology | GitHub + MeSH | $0 |
| Questions | GitHub Issues/Template | $0 |
| Actions | GitHub Actions | Free tier |
| Artifacts | Zenodo | $0 |
| Versioning | Git | $0 |

---

## Success Metrics (The One Week Test)

Dr. Vasquez can demonstrate:
- ✅ Complete question history
- ✅ All agent interactions logged
- ✅ Every action verifiable
- ✅ Preprint with DOI and full provenance
- ✅ All without custom infrastructure

If this works, we have proven:
- Researchers get value from traceability
- Zero-infrastructure is viable
- The model scales naturally

---

*Sprint 24 builds the minimal demonstrable reality. Everything else follows.*