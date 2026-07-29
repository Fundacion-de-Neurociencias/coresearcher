# Review Constitution
## Scientific Validation as Institutional Primitive

**Version 1.0.0** - Validation Governance  
**Status**: Constitutional Document - Core Governance

---

## Article I: The Nature of Scientific Review

### Section 1. Definition

A **REVIEW** is a formal validation operation that assesses scientific artifacts against quality criteria.

It is NOT:
- ❌ A casual opinion (chat comment)
- ❌ A star rating (Amazon-style scoring)
- ❌ A simple thumbs up/down (binary validation)
- ❌ An editorial process (publication gatekeeping)

It IS:
- ✅ A structured evaluation against scientific criteria
- ✅ A traceable assessment with documented methodology
- ✅ A consensus-seeking operation between reviewers
- ✅ A permanent artifact in the scientific record

### Section 2. Review Canonical Identity

Every Review receives a permanent identifier:

```
REVIEW-XXXXXX
```

Reviews are typed:

| Type | Description |
|------|-------------|
| **VALIDATION** | Check correctness of claims/evidence |
| **REPRODUCTION** | Attempt to replicate findings |
| **CONTRADICTION** | Identify conflicting evidence |
| **SUPPORT** | Confirm evidence quality |
| **QUALITY** | Assess methodology rigor |
| **STAKEHOLDER** | Domain/expert evaluation |

---

## Article II: Review Authority and Process

### Section 1. Review Authority Levels

| Level | Who | Scope |
|-------|-----|-------|
| **Level 1** | Peer Researchers (RES) | Direct claim/hypothesis review |
| **Level 2** | Program Leads (RES) | Full program artifact review |
| **Level 3** | Stewards | Cross-program validation |
| **Level 4** | Review Board | System-wide quality assurance |

### Section 2. Review Process

```
1. REVIEW request (claim/mechanism/question)
2. Reviewer assignment (qualified RES or agent)
3. Evidence assessment (methodology, data, logic)
4. Contradiction check (cross-reference existing)
5. Consensus signal (support/challenge level)
6. REVIEW-XXXXXX issued with assessment
```

---

## Article III: Review Criteria

### Section 1. Universal Quality Dimensions

| Dimension | Weight | Assessment Criteria |
|-----------|--------|-------------------|
| **Methodological Rigor** | 25% | Study design, sample size, controls |
| **Evidence Quality** | 20% | Data provenance, statistical validity |
| **Logical Consistency** | 20% | Reasoning, assumptions, conclusions |
| **Ontological Alignment** | 15% | Taxonomy fit, duplication check |
| **Reproducibility** | 10% | Clarity for replication attempts |
| **Novelty Assessment** | 10% | Original contribution vs. restatement |

### Section 2. Review Score

```json
{
  "review_id": "REVIEW-000123",
  "target": "CLAIM-000456",
  "reviewer": "RES-000789",
  "scores": {
    "methodological": 0.85,
    "evidence": 0.78,
    "logical": 0.92,
    "ontological": 0.88,
    "reproducibility": 0.75,
    "novelty": 0.65
  },
  "overall": 0.81,
  "recommendation": "ACCEPT_WITH_MINOR",
  "contradictions_found": 2,
  "supporting_evidence": ["PMID-12345"]
}
```

---

## Article IV: Review Lifecycle

### Section 1. Review States

| State | Meaning |
|-------|---------|
| **Requested** | Review needed |
| **Assigned** | Reviewer allocated |
| **In Progress** | Evaluation underway |
| **Completed** | Results recorded |
| **Challenged** | Review itself questioned |
| **Final** | Accepted as authoritative |

---

## Article V: Review Impact on Trust

### Section 1. Trust Score Modification

Each review modifies the target's trust trajectory:

- **Positive review** (+0.1 to +0.5 trust points)
- **Negative review** (-0.1 to -0.3 trust points)
- **Contradiction found** (-0.2 to -0.4 trust points)
- **Replication confirmed** (+0.3 to +0.7 trust points)

### Section 2. Review Network Effects

Reviews create connections:

```
REVIEW-000123
  └── validates: CLAIM-000456
  └── references: [PMID-123, PMID-456]
  └── authored_by: RES-000789
  └── program_context: PROGRAM-000123
```

Multiple reviews → Trust Index convergence.

---

## Article VI: Review as Institutional Memory

### Section 1. Why Reviews Lock In Value

After 100K+ reviews accumulated:

- **Cannot falsify**: Multiple reviewers witnessed
- **Cannot reframe**: Methodology documented
- **Cannot ignore**: Linked to program reputation
- **Cannot replicate**: Unique reviewer combinations

Reviews become the **trust graph foundation**.

---

*Esta constitución establece REVIEW como la capa de gobernanza que mantiene la integridad científica. Sin ella, el conocimiento se convierte en ruido.*