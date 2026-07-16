# Visibility Levels
## Privacy-first Scientific Observation

---

## The Trust Problem

CoResearcher cannot act as an aggressive crawler of private information.

Trust must be built before adoption.

---

## Three Visibility Levels

### Level 0: PUBLIC
**No permission required**

What's visible:
- All Questions, Actions, Reviews, Artifacts
- Full scientific narrative
- Contributor identities
- Complete timeline

Sources:
- GitHub public repos
- arXiv
- Zenodo
- OSF public
- Open data

---

### Level 1: VISIBLE_METADATA
**Owner permission required**

What's visible:
- Project exists
- Domain/tags
- Last activity date
- Status: active/draft/completed

What's private:
- Questions
- Actual research content
- Contributors (unless opted-in)
- Artifacts details

Example output:
```
Program ID: ND-001

Status: Active

Domain:
- Neurodegeneration
- Diagnostic Ontologies

Activity:
- Active in last 30 days

Artifacts:
- Private (32)

Contact: Available
```

---

### Level 2: PRIVATE
**Owner permission required**

What's visible:
- NOTHING externally

What happens internally:
- Full ledger generated
- Private activity tracked
- Complete reconstruction available to owner

Owner can selectively publish:
- Specific objectives
- Certain artifacts
- Anonymized data
- Existence only

---

## The Flow

```text
Private Repository
    ↓
Private Observer
    ↓
Private Ledger (complete)
    ↓
Visibility Filter (owner-controlled)
    ↓
Public CoResearcher Graph (filtered)
```

---

## Trust Architecture

Default behavior:
```
Private repo connected → Nothing leaves without explicit permission
```

Owner controls:
- What gets published
- At what resolution
- Under what visibility level

---

## Collaboration Discovery

Value without exposing content:

```
Someone is working on:
- Blood Biomarkers for Alzheimer's Disease

Active programs in this domain: 3

Contact available for collaboration
```

This enables discovery while preserving intellectual property.

---

## Industrial Compatibility

Essential for adoption by:
- Pharma companies
- Biotech startups
- Competitive research teams

They can connect repositories for internal tracking while only exposing presence-level metadata.