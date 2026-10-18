# EvidenceGraph Specification
**Version 1.1.0** - Core Data Contract  
**Status**: Canonical Reference  
**Extended**: SPRINT 60B - Decision Trajectory Tracking

> **Implemented contract.** This specification is the long-term design. The EvidenceGraph the API returns today is
> `coresearcher.evidence/v1` ([ADR-DISCOVERY-067](../decisions/ADR-DISCOVERY-067-EVIDENCE-CONTRACT-FOR-EDITXT.md),
> schemas in [`schemas/evidence/v1/`](../../schemas/evidence/v1)). The draft files
> `schemas/evidence_request.schema.json` and `schemas/evidence_graph.schema.json` are not implemented.

---

## 1. Central Concept

The `EvidenceGraph` is a Directed Acyclic Graph (DAG) designed exclusively to provide auditable traceability of scientific assertions and decision trajectories. It is not a general Knowledge Graph. It is strictly limited to demonstrating where a claim comes from and why one path was chosen over another.

---

## 2. Typology of Nodes

### `Claim` (Assertion)
- **Prefix:** `CLAIM-XXXXXX`
- **Definition:** An atomic unit of knowledge extracted or formulated from observable context.
- **Mandatory attributes:** `id`, `text`, `evidence_descriptors` (structural, without evaluation scoring).

### `Artifact` (Multimodal Scientific Artifact)
- **Prefix:** `ART-XXXXXX`
- **Definition:** An immutable fragment extracted from a primary documentary source. It can be text (quote), image, table, matrix (e.g. ChIP-seq), structure (e.g. AlphaFold), dataset or graph.
- **Required attributes:** `id`, `artifact_type`, `data` (immutable content or reference).

### `Source` (Primary Source)
- **Prefix:** `SOURCE-XXXXXX`
- **Definition:** The identifier of the document container that houses the citation (e.g. PMID, DOI, GitHub Issue).
- **Required attributes:** `id`, `text`.

### `URL` (Resolution)
- **Prefix:** `URL-XXXXXX`
- **Definition:** The physical and deterministic web address where the source resides.
- **Required attributes:** `id`, `text`.

### `Decision` (Decision Node) ⭐ **NEW v1.1.0**
- **Prefix:** `DECISION-XXXXXX`
- **Definition:** A point of choice in the research trajectory. It represents a decision made by an agent or human, with its justification, supporting evidence, and result.
- **Required attributes:** `id`, `decision`, `actor`, `timestamp`
- **Optional attributes:** `rationale`, `outcome`, `confidence`
- **Decision fields:**
  - `decision`: Text describing the decision
  - `actor`: Agent or human who made the decision
  - `timestamp`: When was it taken
  - `rationale`: Why it was taken
  - `outcome`: Result (success, failure, abandoned, superseded)
  - `confidence`: Confidence at the time of decision

**Example:**
```json
{
  "id": "DECISION-000001",
  "type": "Decision",
  "decision": "Use Dataset A for training",
  "actor": "Antigravity",
  "timestamp": "2026-07-30T10:00:00Z",
  "rationale": "Faster experiments, sufficient sample size",
  "outcome": "success",
  "confidence": 0.8
}
```

---

## 3. Edges Topology

The edges in the `EvidenceGraph` are strictly semantic and limited.

### 3.1 Edges of Evidence (Original)

1. **`supported_by`** (`Claim` → `Artifact`)
   - Meaning: "This assertion is based on this artifact."

2. **`derived_from`** (`Artifact` → `Source`)
   - Meaning: "This artifact was extracted entirely from this document."

3. **`resolves_to`** (`Source` → `URL`)
   - Meaning: "This document is physically located here."

### 3.2 Decision Edges ⭐ **NEW v1.1.0**

4. **`chosen_over`** (`Decision` → `Decision`)
   - Meaning: "This decision was chosen instead of another alternative"
   - Direction: From the winning decision to the discarded decision
   - Weight: 0.7 (uncertainty in the alternative)

5. **`led_to`** (`Decision` → `Claim` | `Artifact`)
   - Meaning: "This decision led directly to this assertion/artifact"
   - Direction: From the decision to its consequence
   - Weight: 0.9

6. **`abandoned_for`** (`Decision` → `Decision`)
   - Meaning: "This line of research was abandoned in favor of another"
   - Direction: From the abandoned decision to the decision that replaced it
   - Weight: 0.6

7. **`superseded_by`** (`Decision` → `Decision`)
   - Meaning: "This decision was replaced by an improved version"
   - Direction: From the old decision to the new
   - Weight: 0.8

**Example of trajectory:**
```
DECISION-000001 (Use Dataset A)
    ↓ led_to
CLAIM-000001 (Model trained on Dataset A shows 95% accuracy)
    ↓ supported_by
ART-000001 (Training results)
    ↓ derived_from
SOURCE-000001 (Experiment log)
    ↓ resolves_to
URL-000001 (https://github.com/repo/experiments/1)

DECISION-000002 (Try Dataset B)
    ↓ abandoned_for
DECISION-000001 (Use Dataset A)
    ↓ chosen_over
DECISION-000002 (Try Dataset B)
```

---

## 4. Constraints and Structural Rules

### 4.1 Original Restrictions

1. **Claims Isolation:** An `Claim` node cannot have an edge to another `Claim` node.
2. **Prohibited Cycles:** The graph must be 100% acyclic.
3. **Mandatory Anchoring:** Every `Claim` node must have at least one valid path that connects it to an `Source` node.
4. **Limit Hops:** The maximum distance from an `Claim` to an `Source` must not exceed 3 hops.

### 4.2 New Decision Constraints ⭐ **NEW v1.1.0**

5. **Decision Isolation:** A node `Decision` CANNOT have an edge `supported_by` towards an `Claim`. Decisions are based on evidence (Artifacts), not assertions.
   - ✅ Valid: `Decision → Artifact` (led_to)
   - ❌ Invalid: `Decision → Claim` (supported_by)

6. **Decision Cycles:** Cycles are allowed only between `Decision` nodes when the edge is `abandoned_for` or `superseded_by` in the opposite direction.
   - ✅ Valid: `DECISION-A → abandoned_for → DECISION-B` and `DECISION-B → chosen_over → DECISION-A`
   - ❌ Invalid: Cycles in evidence edges

7. **Decision Anchoring:** Every decision must have at least one of:
   - An `Artifact` of evidence that supports it (via `led_to` in reverse)
   - A documented `rationale`
   - A reference to `authorized_by` in metadata

8. **Outcome Tracking:** If a decision has `outcome: abandoned` or `outcome: failure`, it must have at least one connection to another decision (`abandoned_for` or `superseded_by`).

### 4.3 Decision Traceability Principle ⭐ **NEW v1.1.0 - CONSTITUTIONAL**

> **Every DecisionNode must be Observable or Derivable. Never Inferred.**

This principle is constitutional and cannot be violated. Its purpose is to prevent CoResearcher from becoming a psychological interpretation engine.

**Fundamental rule:**
- ✅ **Observable**: "The team closed issue #142 without merge" (direct evidence)
- ✅ **Derivable**: "The team discarded PR #142 after benchmark X" (evidence + reasoning)
- ❌ **Inferred**: "The team believed that..." (interpretation, not evidence)

**Implementation:**
```typescript
interface DecisionNode {
  // Campos obligatorios (observables)
  decision: string              // Derivado de: issue title, PR title, commit message
  actor: string                 // Derivado de: GitHub username, commit author
  timestamp: Date               // Observable: issue created_at, PR created_at, commit date
  
  // Campos condicionales (derivables)
  rationale?: string            // DERIVADO de: issue body, PR description, commit body
                                  // Marcar como "inferred" si no hay declaración explícita
  
  outcome: DecisionOutcome      // Derivado de: issue state, PR state, release tags
  
  confidence: number            // confidence: 1.0 para explícito, 0.7-0.9 para implícito
}
```

**Validation:**
```typescript
interface DecisionValidation {
  isObservableOrDerivable: boolean  // true si todos los campos son observable/derivable
  
  classification: {
    decision: 'observable' | 'derivable'
    actor: 'observable'
    timestamp: 'observable'
    rationale?: 'observable' | 'derivable' | 'inferred'
    outcome: 'derivable'
  }
  
  violations: string[]  // Debe estar vacío
}
```

**Valid examples:**
```json
{
  "id": "DECISION-000001",
  "type": "Decision",
  "decision": "Close issue #142: Switch to pydantic v2",
  "actor": "hinthakka",
  "timestamp": "2026-05-15T10:30:00Z",
  "outcome": "abandoned",
  "confidence": 0.85
}
```

**Invalid examples:**
```json
{
  "id": "DECISION-000002",
  "type": "Decision",
  "decision": "The team believed pydantic v2 was too complex",
  "actor": "Unknown",
  "timestamp": "2026-05-15T10:30:00Z",
  "outcome": "abandoned",
  "confidence": 0.6
}
// VIOLACIÓN: "creía" es interpretación psicológica (inferido)
```

**Architectural consequences:**
1. DecisionNode CANNOT contain fields such as `belief`, `opinion`, `thought`, `assumption`
2. Rationale should always be traceable to an artifact (issue, PR, commit)
3. Confidence should reflect available evidence, not subjective certainty
4. The system must mark as `inferred` any field that is not directly observable

**Relationship with other principles:**
- Complements: **Claims Isolation** (do not evaluate assertions)
- Complements: **No Evaluation** (CoResearcher does not judge decisions, it only records them)
- Reinforces: **Traceability without Judgment** (the "why" is evidence, not interpretation)

---

## 5. Canonical JSON Schema

### 5.1 Evidence Graph (Original)
```json
{
  "graph_id": "EG-000001",
  "request_id": "ER-000001",
  "nodes": [
    {"id": "CLAIM-001", "type": "Claim", "text": "...", "evidence_descriptors": {"source_count": 1, "support_depth": 1}},
    {"id": "ART-001", "type": "Artifact", "artifact_type": "quote", "data": "..."},
    {"id": "SOURCE-001", "type": "Source", "text": "..."},
    {"id": "URL-001", "type": "URL", "text": "https://..."}
  ],
  "edges": [
    {"from": "CLAIM-001", "to": "ART-001", "type": "supported_by", "hops": 1},
    {"from": "ART-001", "to": "SOURCE-001", "type": "derived_from", "hops": 1},
    {"from": "SOURCE-001", "to": "URL-001", "type": "resolves_to", "hops": 1}
  ],
  "provenance": {
    "generated_by": "CoResearcher",
    "timestamp": "2026-07-28T00:00:00Z"
  }
}
```

### 5.2 Decision Path Graph ⭐ **NEW v1.1.0**
```json
{
  "graph_id": "EG-000002",
  "request_id": "ER-000002",
  "nodes": [
    {
      "id": "DECISION-001",
      "type": "Decision",
      "decision": "Use Dataset A",
      "actor": "Antigravity",
      "timestamp": "2026-07-30T10:00:00Z",
      "rationale": "Faster experiments",
      "outcome": "success",
      "confidence": 0.8
    },
    {
      "id": "ART-002",
      "type": "Artifact",
      "artifact_type": "dataset",
      "data": "dataset_a_v1.csv"
    },
    {
      "id": "CLAIM-001",
      "type": "Claim",
      "text": "Model achieves 95% accuracy",
      "evidence_descriptors": {"source_count": 1, "support_depth": 1}
    },
    {
      "id": "DECISION-002",
      "type": "Decision",
      "decision": "Try Dataset B",
      "actor": "Antigravity",
      "timestamp": "2026-07-30T09:00:00Z",
      "outcome": "abandoned",
      "confidence": 0.5
    }
  ],
  "edges": [
    {
      "from": "DECISION-001",
      "to": "ART-002",
      "type": "led_to",
      "weight": 0.9
    },
    {
      "from": "ART-002",
      "to": "CLAIM-001",
      "type": "supported_by",
      "weight": 0.9
    },
    {
      "from": "DECISION-002",
      "to": "DECISION-001",
      "type": "abandoned_for",
      "weight": 0.6
    },
    {
      "from": "DECISION-001",
      "to": "DECISION-002",
      "type": "chosen_over",
      "weight": 0.7
    }
  ],
  "provenance": {
    "generated_by": "CoResearcher",
    "timestamp": "2026-07-30T12:00:00Z",
    "corpus_version": "sprint60b"
  }
}
```

---

## 6. Trajectory Reconstruction Pattern

### 6.1 Use Case: Discarded Hypothesis

**Objective:** Reconstruct the complete trajectory of a hypothesis that was abandoned.

**Entry:** `DECISION-000042` (abandoned)

**Process:**
1. Find all `abandoned_for` edges from this decision
2. Find all `chosen_over` edges towards this decision
3. Rebuild the sequence: `DECISION-A → abandoned_for → DECISION-B → chosen_over → DECISION-A`
4. Attach evidence: artifacts, claims, outcomes

**Output:** Subgraph focused on the abandoned decision with all its context.

### 6.2 Use Case: Success Path

**Objective:** Identify which decisions led to a successful outcome.

**Input:** `DECISION-000045` (outcome: success)

**Process:**
1. Go back along edges `superseded_by` and `chosen_over`
2. Rebuild tree of considered alternatives
3. Identify key points of divergence

**Output:** Decision tree with successful and failed paths.

### 6.3 Trajectory Metrics

```typescript
interface TrajectoryMetrics {
  decision_count: number
  abandoned_count: number
  success_rate: number
  avg_decision_depth: number  // Average path length from root decision
  evidence_strength: number   // Average confidence of supporting artifacts
  backtracking_frequency: number // How often decisions were abandoned
}
```

---

## 7. Integration with Decision Registry

### 7.1 Mapping

```
Decision Registry (decision_execution.schema.json)
    ↓
EvidenceGraph (evidence_graph.schema.json)

DECISION-XXXXXX (Decision Registry)
    → maps to DECISION-XXXXXX (EvidenceGraph node)

Execution record
    → maps to ART-XXXXXX (Artifact node, type: execution_log)

Policy compliance
    → maps to ART-XXXXXX (Artifact node, type: test_result)

Evidence references
    → maps to SOURCE-XXXXXX and URL-XXXXXX
```

### 7.2 Bidirectional Linking

```typescript
// From Decision Registry to EvidenceGraph
const decision = await decisionRegistry.get('D-2026-0045')
const graph = await evidenceGraphBuilder.buildFromDecision(decision.id)
// graph.nodes includes: DECISION-000001, ART-000042, CLAIM-000023

// From EvidenceGraph to Decision Registry
const graph = await evidenceGraphRepository.get('EG-000001')
const decisionNodes = graph.nodes.filter(n => n.type === 'Decision')
for (const node of decisionNodes) {
  const decision = await decisionRegistry.get(node.id)
  // Full decision record with execution details
}
```

---

## 8. Extended Validation

### 8.1 Phase 4: Decision Validation ⭐ **NEW v1.1.0**

```typescript
interface DecisionValidation {
  // Decision anchoring
  allDecisionsAnchored: boolean
  decisionsWithRationale: number
  decisionsWithOutcome: number
  
  // Decision graph properties
  decisionCycleCount: number // Should be 0 for evidence edges, allowed for decision cycles
  orphanedDecisions: string[]
  
  // Trajectory quality
  abandonedDecisionsLinked: boolean
  supersededDecisionsLinked: boolean
  outcomeDistribution: {
    success: number
    failure: number
    abandoned: number
    superseded: number
  }
}
```

### 8.2 Validation Tool

```bash
# Validate including decision nodes
npx @coresearcher/cli validate-graph --include-decisions evidence_graph.json

# Trajectory reconstruction
npx @coresearcher/cli reconstruct-trajectory DECISION-000001

# Decision path analysis
npx @coresearcher/cli analyze-decisions --outcome=success
```

---

## 9. Examples of Use

### 9.1 Example: Reconstruct Discarded Hypothesis Trajectory

```json
{
  "graph_id": "EG-000003",
  "request_id": "ER-000003",
  "nodes": [
    {
      "id": "DECISION-000010",
      "type": "Decision",
      "decision": "Test hypothesis: Amyloid-beta causes Alzheimer's",
      "actor": "Neurodiagnoses",
      "timestamp": "2026-06-01T00:00:00Z",
      "outcome": "abandoned",
      "rationale": "Insufficient evidence, conflicting results"
    },
    {
      "id": "ART-000010",
      "type": "Artifact",
      "artifact_type": "dataset",
      "data": "amyloid_study_2026.csv",
      "classification": "observable"
    },
    {
      "id": "CLAIM-000010",
      "type": "Claim",
      "text": "Amyloid-beta levels do not correlate with cognitive decline in this cohort",
      "classification": "derivable"
    },
    {
      "id": "DECISION-000011",
      "type": "Decision",
      "decision": "Switch to tau protein hypothesis",
      "actor": "Neurodiagnoses",
      "timestamp": "2026-06-15T00:00:00Z",
      "outcome": "success",
      "rationale": "Stronger evidence from recent literature"
    }
  ],
  "edges": [
    {
      "from": "DECISION-000010",
      "to": "ART-000010",
      "type": "led_to",
      "weight": 0.9
    },
    {
      "from": "ART-000010",
      "to": "CLAIM-000010",
      "type": "supported_by",
      "weight": 0.85
    },
    {
      "from": "DECISION-000010",
      "to": "DECISION-000011",
      "type": "abandoned_for",
      "weight": 0.7
    },
    {
      "from": "DECISION-000011",
      "to": "DECISION-000010",
      "type": "chosen_over",
      "weight": 0.6
    }
  ]
}
```

---

## 10. Supported Research Questions

This graph allows us to answer new questions:

1. **Why was this line of research abandoned?**
   - Search `DECISION` with `outcome: abandoned`
   - Rebuild your full context

2. **What alternatives were considered?**
   - Find edges `chosen_over` and `abandoned_for`

3. **How persistent was the team?**
   - Metric: `backtracking_frequency` = abandoned / total decisions

4. **What decisions led to successful results?**
   - Filter by `outcome: success` and rebuild tree

5. **Are there patterns in failed decisions?**
   - Analyze commonalities in `rationale` making with `outcome: failure`

---

*This version 1.1.0 extends EvidenceGraph to capture decision trajectories, addressing the need for semantic traceability of why one scientific path was chosen over others.*