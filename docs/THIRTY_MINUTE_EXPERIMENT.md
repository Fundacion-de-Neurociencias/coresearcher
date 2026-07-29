# Thirty Minute Experiment
## The Only Test That Matters

**Version 2.0.0** - Success Criterion with Reputation Metrics

---

## The Core Hypothesis

> A researcher can formulate a question on Monday and obtain by Friday a result they would sign with their ORCID.

If this works, CoResearcher has value.

If this doesn't work, no constitution matters.

---

## The Real Bottleneck

Not producing PDFs.

**Producing something scientists are willing to attach to their reputation.**

---

## The Four Success Metrics

| Metric | Target | Why It Matters |
|--------|--------|----------------|
| **Time** | < 30 minutes human time | Solves time scarcity |
| **Signature** | Will sign with ORCID | Generates scientific value |
| **Publication** | Would send as preprint | Validates quality |
| **Reuse** | Would use again | Product-market fit |

**All four must pass.**

---

## The Failure Mode

Scenario A - Fast but worthless:
- Time: 10 minutes
- Signature: NO ("too mediocre")
- Publication: NO
- Reuse: NO
**Result: Failure**

Scenario B - Fast and valuable:
- Time: 25 minutes
- Signature: YES ("saved me weeks")
- Publication: YES
- Reuse: YES
**Result: Success**

---

## The Real Researcher Problem

Nobody wakes up thinking:
> "I need a Scientific Execution Ledger"

Everyone wakes up thinking:
> "I have an interesting idea but no time to develop it"

---

## The Solution Statement

**Transform a scientific question into a publishable draft with complete traceability in under 30 minutes of human work.**

That's it. Nothing more.

---

## The Monday-Friday Flow

### Monday (5 minutes)
```bash
# Researcher asks:
"What blood biomarkers predict preclinical Alzheimer's?"
gh workflow run research-orchestrator.yml --field question="..."
```

### Monday-Friday (Autonomous)
```text
Agent 1: Literature extraction → claims
Agent 2: Evidence scoring → trust scores  
Agent 3: Hypothesis generation → hypotheses
Agent 4: Review coordination → validated claims
Agent 5: Draft assembly → preprint.md
```

### Friday (25 minutes)
Researcher reviews:
- Results (10 min) - "¿Esto es firmeable?"
- Decisions (5 min) - "¿Qué incluir?"
- Publish (5 min) - One-click DOI
- Credits (5 min) - Attribution checks

---

## The Reputation Test

If the researcher says:
> "No es perfecto, pero me ha ahorrado dos semanas de trabajo"

**SUCCESS** - They will sign + publish + reuse.

If they say:
> "Esto es mediocre, no lo firmo"

**FAILURE** - Fastness alone is worthless.

---

## The Implementation Target

```text
Question input (text box)
  ↓
5-agent autonomous chain
  ↓
Draft with DOI
  ↓
Researcher signature decision
```

**Total code**: ~300 lines

---

## The First Five Researchers

Find researchers who will honestly try and report:

```text
[Time spent: ___ minutes]
[Willing to sign: YES/NO]  
[Would publish: YES/NO]
[Would reuse: YES/NO]
```

If 4/5 say YES on signature → continue.

If not → back to drawing board.

---

## The Real Value

Not the ledger.

Not the graph.

The **compression of scientific work** into time that exists.

---

*La ciencia cambia cuando un investigador pasa menos tiempo trabajando, no cuando hay más constitutions.*