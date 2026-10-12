# Archive Decisions - CoResearcher Architecture Correction

## Components Archived (Sprint 29-32)

Moved to `archive/experimental/` because they attempt to infer non-observable entities:

### Program Resolver (⚠️ Archivado)
- `program.py` - "Program" is not objectively observable (software + community + ecosystem = ambiguous)
- `program_resolver.py` - Cannot resolve what cannot be strictly defined
- `cross_repo_program_resolver.py` - Same problem across repositories

### Initiative Resolver (⚠️ Archivado)
- `initiative.py` - "Initiative" is management language, not scientific
- `initiative_resolver.py` - Cannot validate intangible constructs

### Workstream (⚠️ Redefinido)
- `workstream.py` - Kept but redefined as observable cluster
- `workstream_resolver.py` - Archived pending observability criterion

---

## New Definition: Observable Workstream

A workstream is valid only if it represents an observable cluster of activity:

```text
Observable Workstream = {
  artifacts: [dataset, paper, code],
  evidence: [measurements, protocols],
  endpoints: [publications, DOIs]
}
```

Example valid workstreams:
- `APOE4`: datasets + papers + code related to APOE4
- `Biomarker_cascade`: CSF + plasma + imaging biomarkers

---

## Core Pipeline Validation Status

### ✅ Validated (Observable → Observable)
```text
Source Asset
    ↓
Observations (structured)
    ↓
Evidence Quality (ranking)
    ↓
Contradictions (documented)
```

### ⏳ Pending Validation (Observable → Interpretation)
```text
Observations
    ↓
Learnings (inferred)
    ↓
Patterns (generalized)
    ↓
Cross-Asset Synthesis (compared)
```

---

## Reproducibility Check Results

- Total observations: 20
- Total learnings: 10  
- All learnings trace to existing observations: TRUE
- Evidence strength distribution: foundational(1), strong(5), suggestive(6), moderate(7), preliminary(1)

**Status**: Partial - traceable but not yet independently validated

---

## Next Critical Question

> Can two independent reviewers reach the same learnings, patterns, and contradictions from the same ledger?

This is the boundary between:
- **Observation**: Verifiable, reproducible
- **Interpretation**: Requires review and validation layers