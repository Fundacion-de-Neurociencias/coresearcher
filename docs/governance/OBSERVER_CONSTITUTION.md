# Observer Constitution
## Passive Capture Architecture

## Core Principle

> **All CoResearcher objects must be generatable without explicit registration.**

This is not a feature. This is an architectural constraint.

---

## The Two Modes

### Active Registration (Optional)
```
Researcher/agent explicitly creates objects
```

### Passive Inference (Required)
```
CoResearcher observes existing activity and infers objects
```

---

## Object Inference Rules

### QUESTION
May be inferred from:
- GitHub Issues
- Paper queries ("we hypothesize", "we propose")
- Grant abstracts
- Pre-registrations
- Discussion forums

### ACTION  
May be inferred from:
- Git commits
- Pull requests
- Script executions
- Agent traces
- Experiment runs
- Deployment logs

### REVIEW
May be inferred from:
- Peer review records
- PR reviews
- Structured feedback
- Validation comments
- Rating systems

### CLAIM
May be inferred from:
- Paper assertions
- Experimental results
- Statistical outputs
- Dataset descriptions

### ARTIFACT
May be inferred from:
- Zenodo deposits
- arXiv papers
- GitHub Releases
- PubMed entries
- OSF registrations

### PROVENANCE
May be inferred from:
- Git metadata
- CI/CD logs
- Model API calls
- Tool execution traces

---

## Entity Resolution is Primary

When observing:
- Papers across multiple venues
- Authors with name variations
- Agents with different signatures
- Projects with cross-links

Entity resolution becomes the core competency:
```
Does this paper/repository/comment belong to 
the same questioning/action/researcher?
```

Not "how do we get them to register?"

---

## Economic Model Shift

### Traditional Platforms
```
Value = Number of users × Feature value
```

### CoResearcher Observer
```
Value = Scientific coverage × Resolution accuracy
```

A researcher who never signs up still benefits from:
- Related work discovery
- Impact tracking
- Collaboration opportunities

---

## Implementation Priority

1. **Observer Agent** - Scans existing repositories
2. **Entity Resolution** - Links fragmented activity
3. **Ledger Building** - Constructs Scientific Activity Graph
4. **Active Registration** - Optional human enhancement

---

## The Adoption Path

```text
Phase 1: Passive coverage
- GitHub + Zenodo → 1M actions
- No user intervention required

Phase 2: Discovery value
- Researchers find their work indexed
- "I didn't register, but it found me"

Phase 3: Active coordination
- Teams adopt for ongoing projects
- Based on proven utility, not promises
```

---

## Anti-Pattern Warning

**WRONG:**
```
Please register your project
Please create your question  
Please log your action
Please submit your review
```

**RIGHT:**
```
We observed your repository
We inferred this question
We linked these actions
We detected this review
Would you like to validate?
```

---

## Constitutional Requirement

Any CoResearcher primitive must support:
1. **Active creation** (if the user wants to)
2. **Passive inference** (must always work)

If an object cannot be inferred from existing scientific activity,
it requires explicit justification why registration is necessary.