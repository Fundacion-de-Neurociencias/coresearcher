# First Artifact
## The Promise: QUESTION → ARTIFACT

> **The only architecture document that matters: how to get a real research artifact from a real question in under one hour.**

---

## The User Experience (Invisible Complexity)

```text
Fork template
    ↓
Edit question.md
    ↓
Run research-agent.yml
    ↓
[Behind the scenes: extraction, review, iteration]
    ↓
Run publish.yml
    ↓
DOI assigned
```

**The user sees only:**
- Question → Artifact
- **Nothing more**

---

## The Contract (Minimal Specification)

### Input
```markdown
# My Research Question

[EDIT THIS FILE]

What blood biomarkers predict preclinical Alzheimer's disease?
```

### Output
```
DOI: 10.5281/zenodo.XXXXXXX
Contains:
- claims.json (extracted claims with evidence)
- provenance.json (complete methodology trace)
- report.md (human-readable summary)
```

### Promise
> Any scientific question asked → Any publishable artifact produced with complete provenance.

---

## The Real Test

### Not This (Architecture Without Execution)
- ❌ 15 constitution documents
- ❌ Ontology definitions without data
- ❌ Protocol specifications in theory
- ❌ Community surveys

### This (Execution Without Excuses)
- ✅ One question file editable
- ✅ Three workflows that run today
- ✅ One publish button
- ✅ One DOI received

---

## The Execution Path (What Actually Happens)

```
QUESTION-000001
    ↓
ACTION-000001 (EXTRACT_CLAIMS)
ACTION-000002 (REVIEW_VALIDATION)  
ACTION-000003 (GENERATE_REPORT)
    ↓
ART-000001 (PREPRINT with DOI)
```

### Internal Architecture (Hidden but Traceable)
- **QUESTION**: Input from researcher
- **ACTION**: Every verifiable step (logged, not shown)
- **REVIEW**: Quality check (embedded in workflow)
- **ARTIFACT**: Published output with DOI

---

## The Minimal Implementation

### Files Required
```
.github/workflows/
├── research-agent.yml    # Extract claims + evidence
├── review-agent.yml      # Validate quality
└── publish.yml         # Generate DOI

question.md             # Single editable question
actions/                # Auto-generated logs
artifacts/              # Auto-generated outputs
```

### Total Code
- **~600 lines of YAML** (workflows)
- **~100 lines of templates** (question format)
- **$0 infrastructure cost** (GitHub + Zenodo free tier)

---

## The Validation Loop

### Prove It Works
```
DAY 1:  Question → Run workflow → Get artifact
DAY 2:  Question → Run workflow → Get artifact  
...
DAY 100: Question → Run workflow → Get artifact
```

**If we use it 100 times, the architecture is proven.**  
**If we don't, no amount of documentation helps.**

---

## The README That Should Exist After First Artifact

```markdown
# CoResearcher

CoResearcher transforms a scientific question into a publishable research artifact using agent-based workflows and existing open infrastructure.

## Input
    Question

## Output  
    Research artifact with complete provenance

## Built on
    GitHub • ORCID • Zenodo • OpenScience
```

---

## The First Artifact Checklist

- [ ] **Question defined** (question.md edited)
- [ ] **Claims extracted** (research-agent.yml run)
- [ ] **Evidence validated** (review-agent.yml run)
- [ ] **Artifact published** (publish.yml run)
- [ ] **DOI received** (Zenodo link)
- [ ] **Provenance complete** (all steps traceable)

---

## The Moment of Truth

**When a real question produces a real artifact with DOI, CoResearcher exists.**

Until then, it's just ideas.

---

*This document is executable. The next edit should be running a workflow, not writing another spec.*