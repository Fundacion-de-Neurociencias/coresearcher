# First Use Case
## One Researcher, One Question, Three Agents, One Week

**Objective**: Prove that CoResearcher solves a real, immediate problem better than current tools.

---

## The Researcher

**Dr. Elena Vasquez**  
Neurologist at Hospital Clínic Barcelona  
ORCID: 0000-0002-1825-0097  
Focus: Early biomarkers for Alzheimer's disease

---

## Today's Workflow (Without CoResearcher)

```
Monday:
├── Creates folder: biomarcadores_AD_2026/
├── Downloads 50 papers from PubMed
├── Saves PDFs in: papers/, analysis/, notes/
└── Uses Claude/ChatGPT for summary

Tuesday:
├── Opens 3 chats with Claude
│   ├── Chat 1: "Extract biomarkers mentioned"
│   ├── Chat 2: "Analyze p-tau217 data"
│   └── Chat 3: "Generate hypothesis about GFAP"
├── Copies results to notes/
└── Loses track of which paper sourced which claim

Wednesday:
├── Searches for more papers
├── Manually tracks citations in spreadsheet
├── Loses one result from Chat 1
└── Cannot reproduce Chat 2 analysis

Thursday:
├── Writes draft paper section
├── Cannot trace methodology
├── Unclear which AI assisted which claim
└── No systematic review performed

Friday:
├── Sends to colleague for feedback
├── Feedback arrives via email
├── No structured review recorded
└── No provenance of changes

Weekend:
├── Realizes lost 3 days of work
├── Cannot reproduce AI interactions
└── Paper draft lacks traceability
```

**Result**: Knowledge generated but not captured, not reproducible, not verifiable.

---

## With CoResearcher (GitHub Native)

```
Monday:
├── Creates GitHub Issue #123 in science/alzheimer-biomarkers
│   ├── Title: "¿Cuáles son los biomarcadores sanguíneos del Alzheimer precoz?"
│   ├── Labels: question-type::meso, domain::neurology
│   └── Assigns: self

├── Launches Agent Workflow:
│   ├── .github/workflows/extract-biomarkers.yml
│   ├── .github/workflows/analyze-ptau217.yml
│   └── .github/workflows/generate-gfap-hypothesis.yml
│
└── Each workflow run creates:
    ├── ACTION-XXXX entry in .cosearcher/actions/
    └── Provenance logged automatically
```

```
Tuesday:
├── Questions appear as Issues with full history
├── Actions are workflow runs with complete logs
├── Evidence sources tracked automatically
├── All interactions reproducible via Actions
└── No context lost between sessions
```

```
Wednesday:
├── New evidence triggers new Actions automatically
├── Trust scores updated from review Actions
├── Coordination via Issue comments
├── All methodology encoded in workflows
└── Results comparable with explicit provenance
```

```
Thursday:
├── Pull Request #45 for review of claim aggregation
├── Reviewer Actions score methodology/reproducibility
├── All changes tracked in git history
├── Review scores feed Trust Index
└── Ready for publication
```

```
Friday:
├── Zenodo release created from main branch
├── DOI assigned automatically
├── All provenance included in release
├── Researcher gets credit for:
│   ├── Original question
│   ├── Agent coordination
│   ├── Review facilitation
│   └── Artifact publication
└── Collaboration invited via @ mentions
```

---

## The Concrete Outputs

### 1. QUESTION-000123 (Issue #123)

```markdown
---
question_id: QUESTION-000123
ontological_path: "Science/Medicine/Neurology/Alzheimer's Disease/Biomarkers"
status: "active"
created_by: "ORCID-0000-0002-1825-0097"
---

# ¿Cuáles son los biomarcadores sanguíneos del Alzheimer precoz?

**Ontological anchor**: Science/Medicine/Neurology/Alzheimer's Disease/Biomarkers

**Activity**:
- Actions: 47
- Claims: 23
- Reviews: 12
- Status: Active
```

### 2. ACTION Entries (Workflow runs logged)

```yaml
ACTION-000456 (workflow run #8901)
type: EXTRACT_BIOMARKERS
actor: AGENT-CLAUDE-RESEARCHER
target: QUESTION-000123
provenance:
  model: claude-3-opus
  prompt: biomarker_extraction_v2
  evidence_sources: [PMID-34567890, PMID-34567891]
  code_version: extractor.py@v1.2.3
outcome: [CLAIM-000789, CLAIM-000790]
```

### 3. PROVENANCE Chain (Git + Actions)

Every result has:
- Exact prompt used
- Model version
- Evidence sources
- Code version
- Timestamp
- Workflow parameters

Reproducible by re-running the workflow.

### 4. ARTIFACT (Zenodo release)

```
DOI: 10.5281/zenodo.12345678
Contains:
- claims.json (all claims with evidence)
- actions.json (full execution history)
- provenance.json (complete methodology)
- review_scores.json (validation documented)
```

---

## The Improvement

| Aspect | Without CoResearcher | With CoResearcher |
|--------|-------------------|-------------------|
| **Traceability** | Lost in chat history | Complete provenance |
| **Reproducibility** | "Do it again" | Re-run workflow |
| **Credit** | Only paper authorship | Questions/Actions/Reviews |
| **Review** | Informal feedback | Structured scoring |
| **Coordination** | Manual file sharing | GitHub collaboration |
| **Artifact** | PDF file | DOI with provenance |

---

## The Validation

**The researcher gets**:

1. **Better science**: Reproducible workflows
2. **Better credit**: Credit for questions and coordination
3. **Better collaboration**: Structured agent + human work
4. **Better publication**: DOI with full methodology
5. **Zero cost**: Uses existing free infrastructure

**No setup required**: Just fork the template repository.

---

*Este caso de uso demuestra que CoResearcher resuelve un problema real INMEDIATO: coordinación y trazabilidad para investigación agentic. No requiere institucionalización masiva. Solo requiere 600 líneas de workflows que trabajan hoy mismo.*