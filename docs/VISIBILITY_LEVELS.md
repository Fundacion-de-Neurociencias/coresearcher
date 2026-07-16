# Visibility Levels
## Privacy-first Scientific Observation

---

## The Trust Problem

CoResearcher cannot act as an aggressive crawler of private information.

Trust must be built before adoption.

---

## Four Visibility Levels

### Level 1: PUBLIC
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

### Level 2: DISCOVERABLE
**Owner permission required**

What's visible:
- Project exists
- Domain/tags

What's private:
- Everything else

Example output:
```
Program: ND-001

Domain:
- Neurodegenerative diagnostics

Status:
- Active

Contact:
- Available
```

No objectives. No artifacts. No activity. Only presence.

---

### Level 3: CONNECTED
**Owner permission required - aggregated only**

What's visible:
- Questions count
- Artifacts count
- Contributors count (humans/agents)
- Last activity date
- Domains

What's private:
- Code
- Manuscripts
- Data
- Prompts
- Discussions

Example output:
```
Program:
Neurodiagnoses

Questions:
54

Artifacts:
12

Contributors:
4 humans
9 agents

Last activity:
2 days ago

Domains:
- Neurodegeneration
- Diagnostics
- Biomarkers
```

---

### Level 4: PRIVATE
**Owner permission required**

What's visible:
- NOTHING externally

What happens internally:
- Full ledger generated
- Private activity tracked
- Complete reconstruction available to owner

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

## Visibility Filter Configuration

Each project has a configurable visibility level:

```yaml
visibility:
  - private      # Nothing external
  - discoverable # Only existence
  - connected    # Aggregates only
  - public       # Full transparency
```

Can change without modifying internal ledger.

---

## Scientific Presence Protocol

CoResearcher becomes:
- Scientific DNS
- Activity Directory

Enables discovery:
> "Is someone working on diagnostic ontologies for neurodegeneration?"

Answer:
```
Yes. 4 active programs in this domain.
```

Without exposing IP.

---

## Industrial Compatibility

Essential for adoption by:
- Pharma companies
- Biotech startups
- Competitive research teams

Connect repositories for internal tracking while only exposing presence-level metadata.