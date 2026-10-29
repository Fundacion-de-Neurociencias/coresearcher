# SPRINT 60C BRIDGE: H6 → H7 → EHG v2
**Date**: 2026-07-31  
**Status**: SPRINT 60C completed; bridge to SPRINT 61+  
**Principle**: No architectural changes until H6 validated with authenticated data

---

## 1. Current Status

### H6 — Decision Reconstruction
- **Status**: PENDING
- **Evidence**: 301 decisions extracted offline from `data/langgraph_raw.json` with 426 edges
- **Validation pending**: Run authenticated pipeline against GitHub API to confirm accuracy ≥70%
- **Artifacts**: `data/trajectories/langchain_ai_langgraph/`

### H7 — Branch Detection
- **Status**: LOCKED until H6
- **Reason**: Branch detection requires operational DecisionGraph; DecisionGraph requires validated H6
- **Preparation**: `docs/BRANCH_DETECTION_FEASIBILITY.md` document ready

### H8 — Convergence Detection
- **Status**: LOCKED until H6+H7

### EHG v2 — Einstein Hypothesis Generator v2
- **Status**: EXPLORATORY
- **Document**: Einstein generator vision (private, not in this repository)
- **Activation**: Only after H7 validated

---

## 2. Frozen Architecture (Respected)

### Stable layers
- EvidenceGraph v1.1.0
- DecisionNode (already in schema)
- Edge types: chosen_over, abandoned_for, superseded_by

### Prohibited until further notice
- Add nodes to the schema
- Create BranchGraph/PossibilityGraph
- Modify architecture

### Allowed
- Improve extractors
- Fix bugs
- Write documentation

---

## 3. Generated Data

### Repository: langchain-ai/langgraph

```
data/trajectories/langchain_ai_langgraph/
├── decisions_classified.jsonl     # 301 DecisionNodes
├── trajectory_graph.json          # Grafo completo con edges
└── evaluation_metrics.json        # Métricas
```

### Offline metrics

| Indicator | Value |
|-----------|-------|
| Total decisions | 301 |
| Success | 122 |
| Abandoned | 129 |
| Failed | 40 |
| Pending | 10 |
| Total edges | 426 |
| Explicit ref edges | 231 |
| Temporal edges | 195 |

### Sample outputs

- decisions with `outcome: success`, `abandoned`, `failure`
- links `chosen_over`, `superseded_by`, `abandoned_for`
- traceability via `artifact_url` and `actor`

---

## 4. Bridge to SPRINT 61

### Step 1: Validate H6

```bash
# Ejecutar pipeline con token
python scripts/run_sprint60c_pipeline.py \
  --repo langchain-ai/langgraph \
  --output data/trajectories/langchain_ai_langgraph \
  --token $GITHUB_TOKEN
```

**Criteria**:
- Extraction ≥70% compared to real issues/PRs with signals
- Precision in manual sample ≥70%
- Evidence coverage ≥80%

**Human audit protocol**:
- Random sample of 50 DecisionNodes
- Evaluation: Is it really an observable decision?
- Categories: `true_decision`, `activity_no_decision`, `inferred_false_positive`
- Final metric: `precision_decision_nodes = true_decisions / sample_size`

### Step 2: If H6 validates → DecisionGraph

- Formalize DecisionGraph as a separate layer
- Maintain current scheme; add MCP queries
- Do not create new nodes or graphs

### Step 3: If H7 is addressed → Branch Detection

- Use protocol defined in `docs/BRANCH_DETECTION_FEASIBILITY.md`
- Extract observable branches (PRs closed without merge, issues wontfix, branches removed)
- Calculate precision/recall with human validation

### Step 4: If H8 is addressed → Convergence Detection

- Detect observable convergences (same artifact, merge commit, duplicate issues)
- Do not detect semantic convergences

### Step 5: EHG v2

- Input: DecisionGraph + BranchGraph + EvidenceGraph
- Process: detect abandoned branches; enrich with modern knowledge
- Output: Structured HypothesisCandidate
- Restriction: every statement must have an associated artifact

---

## 5. Reaffirmed Non-Goals

❌ Do not generate hypotheses without evidence  
❌ Do not create new schemas during freeze  
❌ Do not predict success/failure of branches  
❌ Do not execute H7/H8 without validated H6  
❌ Do not divert resources from SPRINT 60C

---

## 6. Next Conversation

It must be resumed with:
- Authenticated H6 results
- Real quantitative metrics
- Green/Yellow/Red Decision
- Yes Green: SPRINT 61 plan
- Yes Red: refocus on core mission

It should not start with:
- New graphs
- New schemas
- Architectural ideas without data

---

*SPRINT 60C closes tangible execution. H6 remains in Authenticated Validation. The path to EHG v2 remains defined but blocked until empirical evidence.*