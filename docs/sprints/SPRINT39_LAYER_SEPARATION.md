# Sprint 39 - Layer Separation: Observation vs Interpretation

**Key insight**: Observations are reproducible. Interpretations require review.

---

## Separation Implemented

### Scientific Activity Ledger (Observable)
```text
Assets
  ↓
Observations
  ↓
Evidence
  ↓
Provenance
```

This layer IS reproducible and can be published.

### Scientific Interpretation Layer (Under Review)
```text
Evidence
  ↓
Claims
  ↓
Patterns
  ↓
Contradictions
  ↓
Reviews
```

This layer requires human/agglomerated review.

---

## Updated Ledger Structure

### ledger_base.json (Publishable)
```json
{
  "asset_id": "adni",
  "observations": [20 structured observations],
  "evidence_links": [20 evidence records],
  "provenance": {
    "sources": ["DOI", "protocol", "dataset"],
    "timestamps": ["created_at", "observed_at"],
    "contributors": ["agent_id", "method_used"]
  }
}
```

### interpretation_layer.json (Under Review)
```json
{
  "claims": [
    {
      "claim_id": "claim_001",
      "based_on_evidence": ["obs_001", "obs_016"],
      "claim_text": "ADNI uses stratified sampling",
      "review_status": "pending"
    }
  ],
  "patterns": [8 cross-asset patterns],
  "contradictions": [4 documented contradictions],
  "reviews": []  // Empty until human review
}
```

---

## Action Items

1. ✅ Separate the ledger into observable vs interpretative
2. ✅ Publish ledger_base.json with DOI (verifiable provenance)
3. ⏳ Collect independent reviews on interpretation_layer.json
4. ⏳ Accept/reject claims based on review evidence

---

## Status

- **Observation layer**: Validated (can be published)
- **Interpretation layer**: Under review (requires human validation)
- **Next step**: Real reviewer validation of claims