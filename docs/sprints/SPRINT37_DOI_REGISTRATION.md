ºblem# Sprint 37 - DOI Registration for Scientific Activity Ledger

**Objective**: Validate whether a Scientific Activity Ledger can become a citable scientific object.

---

## Falsable Question

Can a Scientific Activity Ledger be published, cited and versioned as a first-class scientific artifact?

---

## Entregable 1 - Ledger Review Model

```json
{
  "review_id": "ledger_review_001",
  "ledger_hash": "sha256:abc123...",
  "reviewer": "Cline Agent",
  "timestamp": "2026-07-18T16:00:00Z",
  "checks": {
    "evidence_traceability": true,
    "observation_hierarchy": true,
    "source_provenance": true,
    "timestamp_consistency": true
  },
  "signature": "verified"
}
```

---

## Entregable 2 - Governance Metadata Schema

```json
{
  "governance_id": "governance_001",
  "ledger_id": "adni_observations_2026",
  "access_control": "public",
  "license": "CC-BY-4.0",
  "version": "1.0.0",
  "publisher": "Fundacion Neurociencias",
  "zenodo_concept": "123456"
}
```

---

## Entregable 3 - Zenodo Publisher

Workflow:
1. Package Scientific Activity Ledger (JSON + metadata)
2. Generate checksum hash
3. Create deposition on Zenodo
4. Upload with metadata
5. Register DOI

---

## Entregable 4 - DOI Registration Workflow

```text
Ledger Generation
    ↓
Ledger Review
    ↓
Governance Metadata
    ↓
Zenodo Deposition
    ↓
DOI Assignment
    ↓
Publication Event
```

---

## Validation Target

Using the ADNI Scientific Activity Ledger generated in Sprint 38A:
- 20 observations traced to 10 learnings
- Evidence catalog with 20 records
- 4 contradictions identified
- Cross-asset patterns document

If successfully published with DOI:
- CoResearcher = Infrastructure for scientific traceability

If not:
- CoResearcher = Advanced indexing system with unresolved publication gap