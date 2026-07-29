# Decision Constitution
## Scientific Choice as Institutional Primitive

**Version 1.0.0** - Governance and Choice Architecture  
**Status**: Constitutional Document - Core Governance

---

## Article I: The Nature of Scientific Decision

### Section 1. Definition

A **DECISION** is a recorded choice in the scientific process that directs resources and effort.

It is NOT:
- ❌ A casual preference (opinión personal)
- ❌ A workflow step (paso automático)
- ❌ A publication outcome (derivado de decisión)
- ❌ A funding choice (económico, no científico)

It IS:
- ✅ A deliberate scientific choice with documented rationale
- ✅ A resource allocation decision
- ✅ A risk/reward assessment
- ✅ A permanent record in the knowledge lifecycle

### Section 2. Decision Categories

| Category | Examples |
|----------|----------|
| **Research Direction** | Which question to pursue, which mechanism to test |
| **Knowledge Strategy** | Private → Protected → Published → Consensus |
| **Resource Allocation** | Compute time, researcher attention, funding priority |
| **Validation Priority** | Which claims need review, which reviews need escalation |
| **Dissemination Mode** | Publish paper, file patent, seek collaboration, withhold |
| **Program Evolution** | Split, merge, archive programs |

---

## Article II: Decision Authority

### Section 1. Decision Rights Hierarchy

| Level | Who | Domain |
|-------|-----|--------|
| **Level 1: Individual** | Any RES-XXXXXX | Within their own work |
| **Level 2: Program Lead** | PROGRAM leads | Within program scope |
| **Level 3: Steward** | Domain stewards | Cross-program within domain |
| **Level 4: Council** | Steward Council | System-wide impact |
| **Level 5: Assembly** | Community elected | Constitutional decisions |

### Section 2. Decision Recording

Every decision MUST be recorded:

```json
{
  "decision_id": "DECISION-000123",
  "type": "RESEARCH_DIRECTION",
  "decider": "RES-000456",  // may be individual or collective
  "program": "PROGRAM-000789",
  "question": "QUESTION-000123",
  "choice": "PURSUE",
  "alternatives_considered": ["QUESTION-000456", "QUESTION-000789"],
  "rationale": "Strongest evidence base and community interest",
  "resources_allocated": {"compute_hours": 1000, "agents": 5},
  "timestamp": "2026-07-13T18:00:00Z",
  "outcome_tracking": true
}
```

---

## Article III: Decision Types and Outcomes

### Section 1. Knowledge Strategy Decisions

```
DECISION: Knowledge Strategy Transition
Target: CLAIM-000123

Path: PRIVATE → PROTECTED
Rationale: Seeking external collaboration on biomarker validation
Evidence: Preliminary in vitro results promising
Risk: Premature disclosure before validation complete

Outcome tracking:
- Collaborations initiated: 2
- Additional evidence generated: 3 papers
- Trust score evolution: 0.45 → 0.67
- Final decision: PUBLISH or PATENT_PENDING
```

### Section 2. Research Direction Decisions

These are the MOST important decisions:

```
DECISION: Research Direction
Question: QUESTION-000123 (Tau pathology in APOE4)
Choice: HIGH_PRIORITY
Alternatives: 
  - QUESTION-000456 (General tau mechanisms) - considered
  - QUESTION-000789 (Therapeutic targets) - rejected (lower evidence)

Resources allocated:
- Lead researcher time: 6 months
- Agent resources: 3 specialized agents
- Compute budget: 5000 hours

Success metrics:
- New claims generated: target 50+
- Mechanisms proposed: target 5+
- Trust scores: average >70
```

### Section 3. Validation Priority Decisions

```
DECISION: Review Assignment
Claim: CLAIM-000789 (pTau217 predicts cognitive decline)
Priority: CRITICAL
Reason: 250M+ diagnostic market, claims need validation
Reviewer: RES-000234 (tau biomarker expert)
Deadline: 2026-08-15

Follow-up decision points:
- If TI < 50: CHALLENGE needed
- If TI > 80: SUPPORT confirmed
- If TI 50-80: ADDITIONAL_EVIDENCE required
```

---

## Article IV: Decision Traces and Outcomes

### Section 1. The Scientific Decision Graph

Decisions create traces:

```
DECISION-000123 (Research Direction)
  ├── ACTION-GEN-0001 → HYPOTHESIS-0001
  ├── ACTION-DESIGN-0002 → EXPERIMENT-0001  
  ├── ACTION-ANALYZE-0003 → RESULTS-0001
  ├── ACTION-SUPPORT-0004 → CLAIM-0001
  └── REVIEW-0001 → VALIDATED (TI: 85)
       └── DECISION-000124 (Knowledge Strategy: PUBLISH)
```

### Section 2. Decision Quality Metrics

| Metric | Meaning |
|--------|---------|
| **Decision Accuracy** | % of decisions that led to positive outcomes |
| **Resource Efficiency** | Cost per validated claim |
| **Outcome Velocity** | Time from decision to validation |
| **Conflict Resolution** | % of disputed decisions resolved |

---

## Article V: Decision vs. Review Separation

### Section 1. The Critical Distinction

```
ACTION: SUPPORT CLAIM-000123
- Performed by: RES-000456
- Evidence: Literature review
- Output: REVIEW-000567 (positive)

DECISION: Accept CLAIM-000123 as validated
- Made by: Program Lead (RES-000123)
- Based on: 3 positive reviews, no contradictions
- Impact: Trust score 78 → 82, included in consensus

The ACTION supports. The DECISION governs.
```

### Section 2. Escalation Paths

When reviews disagree:

```
REVIEW-A: SUPPORT (score: 85)
REVIEW-B: CHALLENGE (score: 42, contradiction found)

DECISION REQUIRED: How to proceed?
Options:
1. REQUEST_ADDITIONAL_EVIDENCE
2. CONSULT_THIRD_REVIEWER  
3. LOWER_TRUST_SCORE (78 → 65)
4. FLAG_CONTRADICTION (defer consensus)

Choice: CONSULT_THIRD_REVIEWER
DECISION-000125 records this governance act.
```

---

## Article VI: Decision as Economic Unit

### Section 1. Why Decisions are the Real Asset

After 10K+ decisions recorded:

```
DECISION-000001: Question prioritization
DECISION-000023: Resource allocation
DECISION-000156: Knowledge strategy
DECISION-000345: Validation outcome

Pattern emerges:
- Good decider = high-value outcomes
- Bad decider = wasted resources
- Collective decider = community alignment
```

### Section 2. Decision History Value

Decision histories become:

- **Training data** for AI decision making
- **Audit trails** for funding agencies
- **Reputation signals** for deciders
- **Process optimization** opportunities

---

## Article VII: The Decision Engine

### Section 1. Future Architecture

A true Decision Engine would:

```
Input: Research state + evidence landscape
↓
Decision Models (trained on historical DECISION records)
↓
Recommendation: Next decision opportunities
↓
DECISION-XXXXXX recorded with justification
↓
Resources automatically allocated via ACTION chains
```

### Section 2. Decision Prediction

```
Given:
- 15 similar decisions in neurodegeneration
- Pattern: claims with supporting evidence > 2 papers
- Outcome: 80% became consensus

Predict:
- CLAIM-000789 should receive HIGH_PRIORITY review
- Suggested: DECISION-000XXX to allocate resources
```

---

*Esta constitución establece DECISION como la unidad de gobernanza científica. Donde la reputación se demuestra no solo por el trabajo realizado, sino por las elecciones correctas que impulsan ese trabajo.*