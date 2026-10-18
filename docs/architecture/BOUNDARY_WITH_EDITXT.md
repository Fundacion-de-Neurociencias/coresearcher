# Boundary with EditXT
## CoResearcher Editorial Service Contract

**Version 1.0.0** - Boundary Definition  
**Status**: Constitutional Document - Core Governance

---

## Fundamental Principle

CoResearcher does not review manuscripts.

CoResearcher does not generate editorial recommendations.

CoResearcher does not assign severity.

CoResearcher responds exclusively to EvidenceRequests.

---

## Three Layer Architecture

### Layer 1 (Core): Traceability Engine
**This is CoResearcher.**

Input:
- GitHub (Issues, PRs, Commits, Releases)
- Zenodo (deposits, DOIs)
- Papers (PubMed, CrossRef, OpenAlex)
- Structured observations

Output:
- Trajectory Report
- Evidence Graph
- Failure Taxonomy
- ACTION-XXXXXX registry
- CLAIM-XXXXXX registry
- Provenance chains

Objective:
Reconstruct the auditably recoverable fraction of scientific history.

**This layer is completely independent of any text generation or content evaluation.**

Sole responsibility:
Maximize traceability and auditability.

Question answered:
"Where is the evidence?"

DOES NOT answer:
"Is it true?"
"It's good?"
"It's right?"

---

### Layer 2: Scientific Audit Module
**This is the natural extension for EditXT.**

Evidence-Based Scientific Auditor.

For a paper or claim:
- Observable: The paper states X
- Structured verification:
  - Is there experimental evidence?
  - Is there a code?
  - Is there a dataset?
  - Is there a benchmark?
  - Is there reproducibility?
- Result: Claim → Supporting Evidence → Audit Result

It does not generate science.
Audit science.

That difference is fundamental.

---

### Layer 3: PROHIBITED for CoResearcher

❌ Assertion correction evaluation
❌ Scientific review (peer review)
❌ Opinions on scientific quality
❌ Error classification or severity
❌ Editorial recommendations
❌ Generation of evaluative text

---

## CoResearcher Interface Contract

```
Input:  EvidenceRequest
Output: EvidenceGraph
```

> **Implemented contract (2026-10-18).** The fields below are the original design. The contract CoResearcher
> implements is `coresearcher.evidence/v1`: JSON Schemas in [`schemas/evidence/v1/`](../../schemas/evidence/v1),
> endpoint `POST /api/evidence/requests`, decision in
> [ADR-DISCOVERY-067](../decisions/ADR-DISCOVERY-067-EVIDENCE-CONTRACT-FOR-EDITXT.md). A request names a target
> CoResearcher holds (lifecycle project, research package, registered claim, formal hypothesis, formal case or free
> question) instead of `target_claim`, and the graph carries no confidence scores, because CoResearcher has no
> calibrated method that would produce them. Gaps and provenance are implemented as described.

### EvidenceRequest

Structured request for scientific evidence. Must include:

- **target_claim**: CLAIM-XXXXXX or canonical identifier
- **evidence_scope**: Type of evidence required (supporting, contradicting, methodological)
- **minimum_confidence**: Minimum confidence threshold (0.0 - 1.0)
- **provenance_required**: Boolean - if full traceability is required

### EvidenceGraph

Evidence graph with complete traceability. Must include:

- **nodes**: linked EVID-XXXXXX, CLAIM-XXXXXX, OBS-XXXXXX
- **edges**: Support/contradiction relations with weights
- **provenance_trail**: Full source chain (DOI, PMID, ACTION-XXXXXX)
- **confidence_distribution**: Distribution of scores per node
- **gaps_identified**: Missing or contradictory evidence

---

## CoResearcher Responsibility

**Maximize traceability and auditability.**

This means:

1. Every node in EvidenceGraph has at least one verifiable source
2. Every edge has documented justification
3. Every confidence score has an explicit methodology
4. Every gap is reported, not hidden
5. Provenance is traced from CLAIM/EVID to original source

---

## Non-Negotiable

1. **No manuscripts**: CoResearcher never receives full text as input
2. **No editorial recommendations**: Output is structured, not narrative
3. **No severity**: No error classification, only evidence traceability
4. **No correctness evaluation**: CoResearcher does not evaluate whether a statement is true
5. **EvidenceRequests only**: Any other type of request is rejected or mapped to EvidenceRequest

---

## Architectural Implications

EditXT and CoResearcher coexist as separate applications on the same core:

```
Capa 1: Traceability Engine (CoResearcher)
    │
    ├── GitHub Issues      → QUESTION-XXXXXX
    ├── PRs/Commits        → ACTION-XXXXXX
    ├── Zenodo/DOIs        → EVID-XXXXXX
    └── EvidenceRequest    → EvidenceGraph

Capa 2: Scientific Audit (EditXT)
    │
    ├── EvidenceGraph      → ReviewGraph
    ├── Manuscrito         → ReviewFindings
    └── Severidad          → ReviewSeverity

Capa 3: NUEVA CIENCIA (Prohibida para CoResearcher)
    │
    └── (No aplica)
```

**They are never mixed.** EditXT consumes EvidenceGraphs as input to its scientific audit process, but CoResearcher never receives editorial or evaluative output from EditXT.

---

## Sprint EDX-01 (EditXT)

Objective: Design ReviewGraph v0 for EditXT.

Deliverables:
1. docs/REVIEW_GRAPH_ARCHITECTURE.md
2. schemas/review_graph.schema.json
3. examples/alzheimer_review_graph.json

Restrictions:
- Do not deploy agents
- Do not integrate LLMs
- Do not integrate PubMed
- Do not integrate Paperpile
- Modeling only

Success Criterion:
Structuredly represent a review finding, its evidence, its severity and its recommendation.

Out of reach:
- manuscript generation
- automatic review
- peer review AI
- conversational assistants

---

*This boundary ensures that CoResearcher maintains its position as the Traceability Engine of the scientific ecosystem, not as an editorial service or as an evaluator of scientific correctness.*