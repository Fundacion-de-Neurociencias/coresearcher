# Sprint 24 Roadmap
## One Working Template, Used By Real Researchers

**No more architecture. Only implementation.**

---

## The Only Truth: 10 Investigators This Week

If 10 researchers prefer this workflow over folders+PDFs+chats, we have a project.

If not, all 24 constitutions are irrelevant.

---

## What We Build (Total: ~500 lines)

### The Template Repository

```text
github.com/coresearcher/alzheimer-biomarker-research
├── question.md           # The research question
├── actions/              # AUTO-generated execution logs
├── artifacts/            # AUTO-generated outputs
├── .github/workflows/
│   ├── research-agent.yml     # Literature extraction
│   ├── review-agent.yml       # Quality assessment
│   └── publish.yml            # Zenodo preprint
└── README.md             # Instructions (copy-paste friendly)
```

**Key**: Everything in `actions/` and `artifacts/` is AUTOMATIC. No manual filling.

---

## The 3 Workflows (Copy-Paste Ready)

### Workflow 1: Literature Extraction

```bash
# Researcher runs ONE command:
gh workflow run research-agent.yml \
  --field question="What blood biomarkers predict Alzheimer's?" \
  --field query="plasma pTau217 NfL GFAP biomarker alzheimer"

# Result: Auto-generated files
# actions/action-001.json - complete execution metadata
# artifacts/claims.json - extracted claims with evidence
```

### Workflow 2: Review + Validation

```bash
# Researcher runs ONE command:
gh workflow run review-agent.yml \
  --field artifact=claims.json

# Result: Auto-generated files  
# actions/action-002.json - review metadata
# artifacts/review-scores.json - quality scores
```

### Workflow 3: Publish with DOI

```bash
# Researcher runs ONE command:
gh workflow run publish.yml

# Result: 
# DOI: 10.5281/zenodo.XXXXXXXX
# All files + complete provenance
```

---

## The Researcher Experience (Explicitly Simple)

```text
Day 1: Fork repository
  ↓
Copy question template
  ↓
Edit: "My research question here"
  ↓
gh workflow run research-agent.yml --field question="..." --field query="..."
  ↓
GitHub Actions execute automatically
  ↓
Results appear in artifacts/claims.json
  ↓
gh workflow run review-agent.yml
  ↓
Review scores in artifacts/review-scores.json
  ↓
gh workflow run publish.yml
  ↓
Preprint with DOI on Zenodo
```

**No forms to fill. No IDs to manage. No registries to understand.**

---

## What We Don't Build

- ❌ PROGRAM registry
- ❌ Ontology constitution portal  
- ❌ Curator hierarchy
- ❌ Steward council
- ❌ Trust engine dashboard
- ❌ Scientific graphs
- ❌ Coordination networks
- ❌ Identity systems

Anything that requires explanation beyond "fork, run, get DOI" waits.

---

## Success Criteria (The Only Metrics)

### Week 1 Test

Ten researchers complete:
- [ ] Fork repository
- [ ] Run 3 workflows
- [ ] Receive preprint DOI
- [ ] Report "this saved me time compared to my current workflow"

If 7+ say YES → continue development

If < 7 say YES → pivot or stop

---

## The Learning Questions (Observational, Not Architectural)

1. What questions do researchers actually ask?
2. Which agents do they actually use?
3. What provenance do they actually value?
4. When do they actually want to publish?
5. What metadata helps them reproduce?

These questions get answered by watching real usage, not writing more documents.

---

*Sprint 24 delivers working code to real researchers. Everything else is noise.*