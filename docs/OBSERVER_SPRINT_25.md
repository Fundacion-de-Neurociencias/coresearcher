# Sprint 25: Neurodiagnoses Activity Observer
## Reconstruct scientific history, don't ask for registration

---

## Objective

Build an observer that reconstructs the complete scientific activity history of Neurodiagnoses automatically.

```bash
npx coresearcher-observer --repo Fundacion-de-Neurociencias/neurodiagnoses
```

Delivers: Navigable ledger of 6+ months of scientific activity.

Success metric: Can a third party understand the scientific journey without reading commits?

---

## Input Sources

- GitHub Issues → Questions
- Pull Requests → Actions
- Commits → Evidence
- Releases → Artifacts
- Discussions → Reviews

---

## Output Structure

```
ledger/
├── questions/
│   ├── QUESTION-000001.json (from Issue #1)
│   └── ...
├── actions/
│   ├── ACTION-000001.json (from PR #1)
│   └── ...
├── reviews/
│   ├── REVIEW-000001.json (from Discussion #1)
│   └── ...
└── artifacts/
    ├── ARTIFACT-000001.json (from Release v1.0)
    └── ...
```

---

## Entity Resolution Priority

The core technical challenge: link related activity across time.

Questions to resolve:
- Does Issue #45 connect to PR #12?
- Did the same agent make commits in June and December?
- Is "APOE4 mechanism" in 2024 the same as "APOE4 biology" in 2025?

---

## Key Queries to Answer

- How many questions emerged?
- How many became artifacts?
- Actions per question ratio?
- Which agents participated?
- What decisions changed direction?

---

## Implementation Steps

1. **Git Scanner** - Extract all issues, PRs, commits, releases
2. **NLP Parser** - Convert text to scientific objects
3. **Entity Resolver** - Link fragmented activity
4. **Ledger Builder** - Create navigable structure
5. **Validation** - Show to 3 researchers unfamiliar with project

---

## No More Constitutions Until...

This works for both Neurodiagnoses and GeneForge.

Proof comes from evidence, not theory.

---

## The Shift

From:
> "We have a theory about agentic science coordination"

To:
> "Here is the complete reconstructed history of two real scientific programs"

This is demonstration. Not speculation.