# Internal First Validation
## Build → Use → Improve

**Version 1.0.0** - Validation Strategy  
**Status**: Execution Plan

---

## The Validation Mistake

Not surveys.
Not interviews.
Not "would you use this?"

People answer based on what they know, not what they'll do when they have the tool.

---

## The Real Validation

**Internal use by the builders themselves.**

You are the only guaranteed users.

---

## The Three-Phase Strategy

### Phase 1: Build (Weeks 1-2)
- ✅ Minimal template repository
- ✅ 3 workflows (research/review/publish)
- ✅ Automatic provenance capture
- ✅ One-click DOI generation

**Target**: Question → Report → DOI in < 30 minutes

---

### Phase 2: Use (Weeks 3-8)
**Internal challenge**: Use the system 100 times.

| Week | Target |
|------|--------|
| 3-4 | 20 questions researched |
| 5-6 | 50 questions researched |
| 7-8 | 100 questions researched |

**Single metric**: Are we using the system voluntarily?

---

### Phase 3: Improve (After Week 8)
IF we're still using it internally:

- Add more agents
- Improve quality
- Share with trusted researchers
- Build UI layer
- Scale

IF we abandoned it internally:

- Pivot or stop
- No external validation needed

---

## The Internal Question

> After 100 questions, do we prefer working inside or outside CoResearcher?

This proves or disproves product-market fit.

---

## What Internal Adoption Means

Success is:
```text
This week's question
├── ACTION-001 (literature)
├── ACTION-002 (claims)
├── ACTION-003 (review)
└── ART-001 (preprint with DOI)
```

And we choose this workflow over:
- ❌ Manual literature review
- ❌ ChatGPT sessions
- ❌ Note-taking apps
- ❌ Email collaboration

---

## The Real Experiment

Not "Would researchers use this?"

But "Do we use this?"

Because if we won't, nobody will.

---

## The Pragmatic Statement

> **Automate the path from scientific question to publishable artifact using only free existing tools.**

If this saves us time, it will save researchers time.

If it doesn't, we stop.

---

## The Build Checklist

```bash
# What we actually build:
1. Template repository ✓ (done)
2. question.md template ✓ (done)
3. research-agent.yml ✓ (done)
4. review-agent.yml ✓ (done)
5. publish.yml ✓ (done)
6. actions/ directory ✓ (done)
7. artifacts/ directory ✓ (done)
8. questions/ directory ✓ (done)

Total: ~500 lines, working now
```

---

## The Use Challenge

Starting Monday:
- Every research question goes through CoResearcher
- Every claim gets ACTION provenance
- Every review runs automatically
- Every result publishes with DOI

Track: Do we abandon the workflow?

If yes → problem not solved.

If no → validation achieved.

---

## The Success Signal

After 50 internal uses:

```text
"I keep forgetting things are tracked automatically"
"This saves me from re-explaining context"
"I can reproduce last month's work instantly"
"I got a DOI without leaving the workflow"
```

That's product-market fit.

---

*Internal first validation de-risks the project. If we won't use it, nobody will.*