# Action Constitution
## Verifiable Scientific Operations as Institutional Primitive

**Version 1.0.0** - Verifiable Activity Unit  
**Status**: Constitutional Document - Core Governance

---

## Article I: The Nature of a Scientific Action

### Section 1. Definition

An **ACTION** is a verifiable operation performed within a Research Program that produces scientific artifacts.

It is NOT:
- ❌ A generic event (log entry without meaning)
- ❌ A tool call (mere API invocation)
- ❌ A chat message (informal communication)
- ❌ A paper publication (artifact, not operation)

It IS:
- ✅ A scientific operation with traceable methodology
- ✅ A repeatable procedure with documented steps
- ✅ A contribution to program objectives
- ✅ An immutable record of scientific work

### Section 2. Canonical Identity

Every Action receives a permanent identifier:

```
ACTION-XXXXXX
```

Actions are semantically typed:

```
ACTION-SUP-000123  # SUPPORT claim
ACTION-CHAL-000456 # CHALLENGE claim  
ACTION-REP-000789  # REPLICATE claim
ACTION-PROPOSE-001 # PROPOSE mechanism
ACTION-GEN-002     # GENERATE hypothesis
ACTION-DESIGN-003  # DESIGN experiment
ACTION-ANALYZE-004 # ANALYZE results
ACTION-PUBLISH-005 # PUBLISH findings
ACTION-REVIEW-006  # REVIEW work
```

---

## Article II: Action Types and Semantics

### Section 1. Core Action Types

| Type | Description | Produces |
|------|-------------|----------|
| **SUPPORT** | Endorse a claim with evidence | EVIDENCE-XXXXXX |
| **CHALLENGE** | Question a claim's validity | CONTRADICTION-XXXXXX |
| **REPLICATE** | Repeat previous work | REPLICATION-XXXXXX |
| **PROPOSE** | Suggest a mechanism | MECHANISM-XXXXXX |
| **GENERATE** | Create a hypothesis | HYPOTHESIS-XXXXXX |
| **DESIGN** | Plan an experiment | EXPERIMENT-XXXXXX |
| **ANALYZE** | Process results | ANALYSIS-XXXXXX |
| **PUBLISH** | Make knowledge public | PUBLICATION-XXXXXX |
| **REVIEW** | Validate work quality | REVIEW-XXXXXX |

### Section 2. Action Format

```json
{
  "action_id": "ACTION-SUP-000123",
  "type": "SUPPORT",
  "actor": "RES-000456",
  "program": "PROGRAM-000123",
  "target": "CLAIM-000789",
  "evidence": ["PMID-12345", "PMID-67890"],
  "method": "literature_review",
  "confidence": 0.92,
  "timestamp": "2026-07-13T18:00:00Z",
  "provenance": {
    "model": "claude-3-opus",
    "prompt": "sip_support_v2",
    "tool_calls": [...],
    "code_version": "atlas/extractor.py@abc123"
  }
}
```

---

## Article III: Action Attribution and Reputation

### Section 1. Actor Types

Actions can be performed by:

- **Human Researchers** (RES-XXXXXX)
- **AI Agents** (AGENT-XXXXXX) - always delegated to human oversight
- **Hybrid Teams** - actions show primary and contributing actors

### Section 2. Reputation Impact

Each action contributes to:

- **Actor reputation score** (accumulated quality)
- **Program activity metrics** (research velocity)
- **Trust signals** (support/challenge balance)
- **Contribution history** (permanent record)

---

## Article IV: Action Lifecycle

### Section 1. Action States

| State | Meaning |
|-------|---------|
| **Proposed** | Action plan submitted |
| **Executing** | In progress |
| **Completed** | Finished with outputs |
| **Verified** | Peer/independent validation |
| **Published** | Made permanent in registry |

---

## Article V: Integration with Programs and Questions

### Section 1. Action Ownership

Every action belongs to exactly one Program but can relate to multiple Questions:

```
ACTION-SUP-000123
  └── program: PROGRAM-000456
  └── questions: [QUESTION-000111, QUESTION-000222]
  └── target_claim: CLAIM-000789
```

### Section 2. Action Chains

Actions form verifiable chains:

```
QUESTION
  └── GENERATE → HYPOTHESIS
      └── DESIGN → EXPERIMENT
          └── ANALYZE → RESULTS
              └── PROPOSE → MECHANISM
                  └── SUPPORT → CLAIM
```

Each link is an ACTION-XXXXXX.

---

## Article VI: The Activity Graph Advantage

### Section 1. Lock-in Through Actions

After 1M+ actions accumulated:

- **Cannot reverse**: History is computationally verified
- **Cannot replicate**: Specific actor combinations unique
- **Cannot migrate**: Provenance chains too complex
- **Cannot falsify**: Blockchain-like immutability

This creates the **scientific moat**.

---

*Esta constitución establece ACTION como la unidad verificable de trabajo científico. Donde la reputación se gana y se prueba.*