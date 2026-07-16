# CoResearcher Protocol

**Git for scientific coordination between humans and AI agents.**

## The Flow

```
Question
    ↓
Action
    ↓
Review
    ↓
Artifact
```

## Example

```text
QUESTION-000001:
Can plasma GFAP predict MCI-to-AD conversion?

↓

ACTION-000001:
Literature extraction (agent)

ACTION-000002:
Trajectory analysis (agent)

↓

REVIEW-000001:
Validation (human)

↓

 artifact: Preprint with DOI
```

## Schemas

- `question.schema.json` - Research questions
- `action.schema.json` - Executable scientific activities  
- `review.schema.json` - Validation records

## Status

Experimental. Looking for 3 researchers to validate.

If you understand what QUESTION, ACTION, and REVIEW mean in 5 minutes, we're on the right track.

If not, the protocol needs work.