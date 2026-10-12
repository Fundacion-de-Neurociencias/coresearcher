# Observer Access Levels
## Public vs Private Scientific Activity

---

## Observer Level 0: Public Artifacts
**No permission required**

Sources:
- GitHub Public repos
- arXiv preprints
- PubMed papers
- Zenodo deposits
- OSF public projects
- Crossref metadata

Value:
- Scientific Search Engine
- Open Science Graph
- Basic coverage

Limitation:
- Catches only published outputs
- Misses process

---

## Observer Level 1: Private Repositories
**Owner permission required**

Sources:
- Private GitHub repos
- Internal documentation
- Project wikis
- Issues/PRs not public

Value:
- Development activity
- Feature evolution
- Technical decisions

Trigger:
```bash
coresearcher connect --repo user/private-repo
```

---

## Observer Level 2: Agent Sessions
**Owner permission required**

Sources:
- Claude Code sessions
- Cline traces
- Cursor history
- Prompts + responses
- Reasoning chains

Value:
- Scientific intent
- Hypothesis formation
- Decision logic
- Failed attempts (hidden in Git)

This is where the real narrative lives.

---

## Observer Level 3: Institutional Workflow
**Organization permission required**

Sources:
- Review systems
- Lab notebooks
- Meeting notes
- Grant proposals
- Internal datasets

Value:
- Full research process
- Team coordination
- Institutional memory

---

## The Adoption Path

```text
Phase 1
Public Observer
→ Builds coverage
→ No one needs to do anything

Phase 2
Someone searches their project name
→ Sees partial reconstruction
→ "I didn't sign up, but it has my work"

Phase 3
Connect private repos
→ Gain 10x value immediately
→ Full process captured
```

---

## Value Gradient

| Level | Sees | Missing |
|-------|------|---------|
| 0 | Outputs | Process |
| 1 | Code changes | Intent |
| 2 | Agent reasoning | Human context |
| 3 | Full workflow | - |

Level 2 is the inflection point: intent without effort.

---

## Architecture Principle

```text
Observer Level 0 must always work.

Higher levels are opt-in enrichment.

If Level 0 provides no value, no one opts into Level 2.