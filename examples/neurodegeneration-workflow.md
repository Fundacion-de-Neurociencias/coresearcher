# Example: Plasma Biomarkers for Alzheimer Detection

Complete workflow demonstrating CoResearcher Protocol.

---

## QUESTION-000001

```markdown
# Can plasma pTau217 predict Alzheimer's disease before symptoms?

**Domain:** neurodegeneration
**Research Gap:** Blood biomarkers for preclinical AD
**Created:** 2024-01-15
**Created By:** researcher-001
```

---

## ACTION-000001: Literature Extraction

```json
{
  "id": "ACTION-000001",
  "question_id": "QUESTION-000001",
  "description": "Extract papers on plasma pTau217 for Alzheimer detection",
  "inputs": ["pubmed://alzheimer-biomarkers"],
  "outputs": ["CLAIM-000045", "CLAIM-000046", "CLAIM-000047"],
  "executed_at": "2024-01-16T10:30:00Z",
  "executed_by": "agent-literature-001",
  "provenance": {
    "model": "gpt-4-turbo",
    "prompt": "Extract biomarker claims with effect sizes...",
    "tools": ["pubmed-mcp", "pdf-extractor"],
    "code_version": "v0.1.0"
  }
}
```

**Generated Claims:**
- CLAIM-000045: pTau217 AUC=0.85 for AD detection (Jansen et al 2024)
- CLAIM-000046: NfL correlates with cognitive decline r=0.67 (Chen et al 2024)
- CLAIM-000047: GFAP elevated in APOE4 carriers (Gao et al 2023)

---

## ACTION-000002: Analysis Synthesis

```json
{
  "id": "ACTION-000002", 
  "question_id": "QUESTION-000001",
  "description": "Combine biomarker trajectory analysis",
  "inputs": ["CLAIM-000045", "CLAIM-000046", "CLAIM-000047"],
  "outputs": ["HYPOTHESIS-000012"],
  "executed_at": "2024-01-17T14:15:00Z",
  "executed_by": "agent-synthesis-001",
  "provenance": {
    "model": "claude-3-opus",
    "prompt": "Find temporal patterns in biomarker progression...",
    "tools": ["statistical-analyzer"],
    "code_version": "v0.1.0"
  }
}
```

**Generated Hypothesis:**
- HYPOTHESIS-000012: Combined pTau217+NfL trajectory predicts conversion from MCI to AD within 2 years

---

## REVIEW-000001: Agent Review

```json
{
  "id": "REVIEW-000001",
  "target_id": "HYPOTHESIS-000012",
  "reviewer": "agent-reviewer-001",
  "score": 0.78,
  "criteria": {
    "empirical_support": 0.85,
    "methodological_rigor": 0.72,
    "novelty": 0.65
  },
  "created_at": "2024-01-18T09:00:00Z"
}
```

---

## REVIEW-000002: Human Review

```json
{
  "id": "REVIEW-000002",
  "target_id": "HYPOTHESIS-000012",
  "reviewer": "researcher-002",
  "score": 0.82,
  "comments": "Trajectory analysis novel and clinically relevant",
  "created_at": "2024-01-20T16:30:00Z"
}
```

---

## ARTIFACT-000001: Preprint

```json
{
  "id": "ARTIFACT-000001",
  "type": "preprint",
  "title": "Plasma Biomarker Trajectories Predict Alzheimer Conversion",
  "content_hash": "sha256:abc123...",
  "derived_from": ["ACTION-000001", "ACTION-000002", "REVIEW-000001", "REVIEW-000002"],
  "doi": "10.5281/zenodo.1234567",
  "published_at": "2024-01-25T12:00:00Z"
}
```

---

## Flow Summary

```text
QUESTION-000001
    ↓
ACTION-000001 (Literature extraction)
    ↓
CLAIM-000045,46,47 (Extracted observations)
    ↓
ACTION-000002 (Synthesis)
    ↓
HYPOTHESIS-000012 (Combined trajectory)
    ↓
REVIEW-000001 (Agent validation)
REVIEW-000002 (Human validation)
    ↓
ARTIFACT-000001 (Preprint with DOI)
```

---

## Why This Beats Email + GitHub + Slack

| Traditional | CoResearcher |
|-------------|--------------|
| Email has no standard format | Structured JSON objects |
| GitHub comments are unstructured | Reviews have defined criteria |
| No provenance tracking | Full chain traceable |
| Manual coordination | Automated handoffs |
| Lost artifacts | Permanent artifacts |