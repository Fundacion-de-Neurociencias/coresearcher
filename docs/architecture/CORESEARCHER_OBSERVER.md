# CoResearcher Observer
## Automatic Scientific Activity Capture

## The Insight

Adoption doesn't happen when someone understands your vision.
Adoption happens when someone discovers they've already been using your system.

## Traditional Approach (Wrong)

```
CoResearcher
    ↓
Researcher changes workflow
    ↓
Creates Questions manually
    ↓
Creates Actions manually
```

Requires: intention + effort + learning

## Observer Approach (Right)

```
Researcher works (existing workflow)
    ↓
Agents work (existing agents)
    ↓
CoResearcher observes silently
    ↓
CoResearcher records automatically
```

Requires: zero change, zero effort

---

## The Command

```bash
npx coresearcher-observer
# or
uvx coresearcher-observer
```

Automatically detects and records:

1. Git repository
2. Issues → Questions
3. PRs → Actions
4. Commits → Evidence
5. Discussions → Reviews
6. Agents → Agent identities

---

## Example: Neurodiagnoses

Claude generates:

```
PR #142: Add ATN biomarker ontology support
```

Observer creates automatically:

```json
{
  "question": "Improve Alzheimer classification",
  "actions": [{
    "id": "ACTION-001",
    "description": "Added ATN ontology mapping",
    "executed_by": "Claude Code Agent"
  }],
  "repository": "neurodiagnoses",
  "timestamp": "2026-07-16"
}
```

---

## Value Proposition

### Before Observer

```text
Researcher thinks:
"I'd have to change my workflow to use this"
```

### After Observer

```text
Researcher thinks:
"I already have this, it captured my work automatically"
```

---

## Implementation Sketch

```
observer/
├── git_scanner.py      # Find .git directories
├── issue_parser.py     # Convert issues to questions
├── pr_parser.py        # Convert PRs to actions
├── commit_parser.py    # Extract evidence
├── agent_detector.py   # Identify AI contributors
└── ledger_exporter.py  # Push to CoResearcher
```

---

## First Target

Connect to existing repositories:
- Neurodiagnoses
- GeneForge
- Any scientific repo with agent contributions

Generate automatically:
- 47 Questions from issues
- 312 Actions from PRs/commits
- 8 Artifacts from releases

This proves the system works without asking anyone to change anything.