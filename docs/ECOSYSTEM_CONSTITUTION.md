# Scientific Knowledge Ecosystem Constitution

**Last Updated**: Sprint 18
**Status**: Foundation Document - Universal Primitives

---

## Universal Primitives Audit

Can science exist without this primitive? If no, it's universal.

| Primitive | Universal? | Notes |
|-----------|------------|-------|
| **Question** | ✅ Yes | Even mathematics asks "what if..." |
| **Hypothesis** | ✅ Yes | Conjecture, proposition, theory |
| **Prediction** | ✅ Yes | Expected outcome |
| **Evidence** | ✅ Yes | Support/data (proof, result, finding) |
| **Claim** | ✅ Yes | Assertion/conclusion |
| **Trust** | ✅ Yes | Credibility/quality assessment |
| **Provenance** | ✅ Yes | Source/traceability |

### Derived/Specialized Primitives

| Category | Primitives (Domain-specific) |
|----------|-------------------------------|
| Testing | Test, Result, Refutation, Replication |
| Quantitative | Measurement, Finding, Model, Theory, Mechanism |
| Action | Recommendation, Intervention, Action |

---

## Scientific Cycle (Universal)

```
Question
  ↓
Hypothesis
  ↓
Prediction
  ↓
Test (varies by domain)
  ↓
Evidence
  ↓
Claim
  ↓
Trust Assessment
```

Each step stores artifacts with full provenance.

---

## Knowledge Producer Contract

Components that generate universal knowledge:

```
Atlas Extractor → CLAIM, FINDING
Trust Framework → TRUST
Researcher Registry → RESEARCHER
```

### ID Formats

- `QUESTION-XXXXXX` - Scientific inquiries
- `HYPOTHESIS-XXXXXX` - Testable propositions
- `CLAIM-XXXXXX` - Assertions with evidence
- `EVIDENCE-XXXXXX` - Supporting data
- `TRUST-XXXXXX` - Quality assessments
- `PREDICTION-XXXXXX` - Expected outcomes

---

## Knowledge Consumer Contract

Consumers declare what knowledge they need:

```json
{
  "consumer_id": "neurodiagnoses",
  "requires": {
    "claim_types": ["biomarker", "genetic", "mechanistic"],
    "trust_threshold": 75,
    "evidence_required": true
  }
}
```

---

## Capability Registry

Universal capabilities any domain can implement:

| Capability | Universal? |
|------------|------------|
| Claim Extraction | ✅ |
| Evidence Assessment | ✅ |
| Trust Scoring | ✅ |
| Hypothesis Generation | ✅ |
| Prediction Generation | ✅ |
| Literature Review | ✅ |
| Ontology Mapping | ✅ |
| Provenance Tracking | ✅ |

---

## Future Evolution

This constitution defines the universal scientific process infrastructure.

Changes to universal primitives require broad consensus across all disciplines.