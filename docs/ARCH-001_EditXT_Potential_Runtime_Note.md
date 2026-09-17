# ARCH-001: Potential External Scientific Runtime — EditXT

**Version 1.0.0** - Architectural Observation Note  
**Status**: Registered — No Action Required  
**Date**: 2026-06-02

---

## Observation

EditXT is formalizing Evidence, Review, and Publication as computable domains. This is an architectural observation about an external system's evolution, registered for future reference.

## Status

```text
External dependency candidate.
```

## Evidence of Integration

| Signal | Observed |
|--------|----------|
| EditXT consuming EvidenceGraph from CoResearcher | Defined (BOUNDARY_WITH_EDITXT.md, Layer 2) |
| Actual CoResearcher to EditXT integration | Not observed |
| EditXT API | Does not exist |
| Integration contract | Does not exist |
| Operational flow validated | Not observed |
| Real integration use case | Does not exist |

## Non-Negotiables

- CoResearcher does not consume evaluative output from EditXT (see BOUNDARY_WITH_EDITXT.md)
- CoResearcher produces EvidenceGraph; EditXT consumes it for scientific audit
- No evaluative, editorial, or generative boundaries cross this divide

## Action

**None.**

No CoResearcher changes are warranted based on the observation that EditXT is formalizing computable domains. The boundary is already fully documented and frozen per ARCHITECTURE_FREEZE.md.

## Prohibited Actions (Do NOT Create)

- PublicationNode
- ReviewNode
- EvidenceGraph to ReviewGraph integration
- EditXT adapters
- Manifest generators
- Publication workflows

These would constitute premature construction without empirical integration requirements.

## Trigger for Reevaluation

A real integration requirement appears — defined as at least one of:

1. An EvidenceRequest that can only be satisfied via an EditXT runtime dependency
2. An observed operational flow where CoResearcher consumes EditXT output
3. A validated use case requiring cross-system integration

## Decision Basis

Per ARCHITECTURE_FREEZE.md: "The bottleneck of CoResearcher is no longer conceptual. It is empirical."

Per BOUNDARY_WITH_EDITXT.md: "EditXT and CoResearcher coexist as separate applications on the same kernel."

Per sprint discipline (SPRINT 61–67A): No update to CoResearcher is made because a plausible integration exists. CoResearcher is updated only when an integration is necessary and observable.

---

*Observation registered. No architectural changes enacted. Awaiting empirical trigger.*
