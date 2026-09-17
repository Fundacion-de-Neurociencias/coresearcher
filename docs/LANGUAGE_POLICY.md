# Language Policy
## English as Canonical Protocol Language

**Version 1.0.0** - Architectural Standard  
**Status**: Mandatory Protocol Rule

---

## Single Rule

> **English is the canonical language of the CoResearcher protocol and all associated repositories.**

---

## Scope

All repository artifacts MUST be written in English:

| Artifact Type | Requirement |
|---------------|-------------|
| Documentation | English only |
| READMEs | English only |
| Markdown files | English only |
| Source code comments | English only |
| Commit messages | English preferred |
| Pull requests | English only |
| Issues | English only |
| Workflow descriptions | English only |
| Templates | English only |
| Configuration comments | English only |
| Variable names | English |
| Class names | English |
| Function names | English |
| Error messages | English |
| AI prompts | English |
| Generated artifacts | English |

---

## Reasons

### 1. Agent Performance
The vast majority of papers, documentation, GitHub repos, code examples, and datasets are in English. Non-English content introduces unnecessary friction for AI agents.

### 2. Future Translation Debt Avoidance
Translating 30+ constitutional documents later is wasted effort. Better to enforce English-first.

### 3. External Contributions
Researchers from Germany, Japan, US, India, China, France, Spain, etc. can immediately access the repository. Spanish-only documentation creates barriers.

### 4. Ecosystem Consistency
CoResearcher integrates with:
- ORCID
- Zenodo
- GitHub
- OpenScience
- OpenAlex
- Semantic Scholar
- PubMed

All function in English.

---

## Practical Application

### Zero Tolerance for Non-English
All documentation, source code, docstrings, inline comments, commit messages, and constitutional artifacts MUST be written exclusively in English.
- ❌ No legacy grandfathering: All existing Spanish files must be translated to English.
- ❌ No bilingual mixed text: Avoid mixing Spanish and English in schemas, tests, or docs.
- ✅ All new and existing documentation MUST be 100% English.

---

## Translation & Enforcement Clause

All non-English text across the repository (code, comments, markdown, and commit messages) must be fully translated. An automated enforcement check (`scripts/enforce_english_policy.py`) runs in CI to verify that no non-English tokens or comments are introduced into the codebase.

---

## Examples

### Correct Workflow Descriptions:
```yaml
name: Research Agent - Literature Extraction
#NOT: Research Agent - Literature Extraction
```

### Correct Variable Names:
```python
research_question = "What biomarkers predict Alzheimer?"
# NOT: research_question = "What biomarkers predict Alzheimer's?"
```

### Correct Commit Messages:
```text
Add ACTION-00123: Extract claims from literature
# NOT: Añadir ACCIÓN-00123: Extraer claims de literatura
```

---

## Rationale Priority

Language matters MORE than:
- UI design
- Feature completeness
- Aesthetics

Language matters LESS than:
- Working workflows
- Agent integration
- DOI publication

But it affects EVERYTHING.

---

## Historical Precedent

- Git uses English (global adoption)
- GitHub uses English (global adoption)
- Python uses English (global adoption)
- ORCID uses English (global adoption)

Protocol success requires universal language.

---

*This policy should outlive all other constitutions. Changing language in a growing architecture is vastly more costly than changing almost anything else.*