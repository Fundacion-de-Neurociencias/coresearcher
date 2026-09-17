# Foundation Constitution
## The Immutable Decisions for CoResearcher

## Decision 0: The Fundamental Nature of CoResearcher (The Core Epistemic Maxim)

> **CoResearcher is NOT an answer system.**  
> **CoResearcher is NOT a bibliographic search engine.**  
> **CoResearcher is NOT a hypothesis generator.**  
> **CoResearcher IS a system for the progressive reduction of the possible scientific state space (\(\Omega\)) through empirical constraints, predictions, and auditable falsifications.**

## Decision 0.1: The Principle of Earning Reality (Reality Contact Score - RCS)

> **"Every hypothesis must earn reality."**
> 
> The difference between a system that merely analyzes science and a system that actually does science is the amount of reality it touches.
> Every hypothesis or constraint must be classified according to its **Reality Contact Score (RCS)**:
> 
> * **RCS = 0**: Purely bibliographic conjecture or in-silico reasoning without external empirical contrast.
> * **RCS = 1**: Prediction contrasted and retrospectively verified against independent external cohorts (\(C_1, C_2, \dots\)).
> * **RCS = 2**: Prediction confirmed prospectively or on blinded holdout datasets.
> * **RCS = 3**: Prediction translated into a physical wet-lab protocol that **modified or guided a real physical experiment** (microfluidics, imaging, reactors).
> * **RCS = 4**: Prediction that yielded a **new invariant biological constraint formally inscribed into the ledger**, pruning the state space \(\Omega\).

## Decision 0.2: The Principle of Hidden Constraint Discovery & Reality Distance (Dry → Damp → Wet)

> **"The ultimate goal of artificial science is not to explain data or maximize prediction. It is to discover the hidden constraints that govern the system."**
> 
> To evaluate genuine discovery capability and decouple it from pretrained biological memory or knowledge:
> 
> 1. **ConstraintBox (Environments with Unknown Ground Truth)**:
>    - Synthetic biological worlds and programs are generated with hidden invariant constraints (\(\mathcal{C}^*\): necessary, sufficient, and impossible).
>    - The agent executes blind intervention rounds and must **reconstruct the exact constraint set** (\(\hat{\mathcal{C}}\)), measuring discovery precision, recall, and causal \(F_1\).
> 
> 2. **Reality Distance Hierarchy (\(\text{Dry} \to \text{Damp} \to \text{Wet}\))**:
>    - **Dry (Synthetic)**: Artificial worlds of *ConstraintBox*, with exact ground truth known by the oracle and immediate computable evaluation.
>    - **Damp (Surrogate)**: In-silico surrogate models and oracles trained on massive cohorts (ADNI, UK Biobank, AMP-AD, MPRA).
>    - **Wet (Empirical Physical)**: Wet-lab assays, bioreactors, clinical cohorts, and real patients.
>    - **Trans-Substrate Survival Rate**: Measures the epistemic robustness of a constraint by surviving intact through the migration \(\text{Dry} \to \text{Damp} \to \text{Wet}\).

---

## Decision 1: Semantic Layer on Top of GitHub

**Do not build ScientificHub as a replacement for GitHub.**

CoResearcher is a **semantic layer** that confers scientific meaning onto existing developer infrastructure.

```
GitHub Issue → Semantic Compiler → QUESTION-XXXXXX
GitHub Discussion → Semantic Compiler → CHALLENGE ACTION
GitHub PR → Semantic Compiler → HYPOTHESIS FORK
GitHub Commit → Semantic Compiler → SCIENTIFIC ACTION
```

GitHub = infrastructure. CoResearcher = meaning.

---

## Decision 2: First-Class External Federated Identities

**ORCID and ROR are first-class citizens from Day 1.**

Not optional. Not plugins. Foundational identity primitives.

```json
Researcher {
  "res_id": "RES-XXXXXX",
  "orcid": "0000-0002-1825-0097",  // mandatory
  "name": "...",
  "reputation": "..."
}

Institution {
  "inst_id": "INST-XXXXXX",
  "ror": "https://ror.org/...",  // mandatory
  "name": "...",
  "trust_history": [...]
}
```

---

## Decision 3: ACTION-XXXXXX as Primary Identifier

**The core asset is not raw knowledge. It is activity.**

`ACTION` is the primary identifier:

```
ACTION-000001  // SUPPORT
ACTION-000002  // CHALLENGE  
ACTION-000003  // REPLICATE
ACTION-000004  // FORK_HYPOTHESIS
ACTION-000005  // CONFIRM
ACTION-000006  // REJECT
```

All reputation, consensus, and epistemic trust derive from immutable actions.

---

## Decision 4: Scientific Activity Graph is the Core Asset

**Not a Knowledge Graph. A Scientific Activity Graph.**

```
Knowledge Graph:  what we know
Activity Graph:   who proposed, who supported, who replicated, who challenged
```

GitHub is not worth billions because of repositories; it is worth billions because of accumulated, auditable activity.

---

## Decision 5: Agent-First Principle

**Every feature must be consumable by AI agents before humans.**

95% of future scientific interactions will be:

```
Agent → MCP → CoResearcher → Knowledge
```

Not:

```
Human → UI → CoResearcher → Knowledge
```

### Agent Compiler Mode

```json
{
  "input": {
    "entity": "BIOMARKER-000342",
    "claims": ["CLAIM-000391", "CLAIM-000482"]
  },
  "output": {
    "consensus": 94,
    "support_actions": 15234,
    "challenge_actions": 234
  }
}
```

Agents thrive on IDs, URIs, schemas, and structured graphs.

---

## Decision 6: AGENT-XXXXXX Identifier

Reserved from Day 1:

```
AGENT-XXXXXX
```

For autonomous programmatic consumers:

| Agent ID | Consumer |
|----------|----------|
| AGENT-000001 | Claude Research |
| AGENT-000002 | Gemini Deep Research |
| AGENT-000003 | OpenAI Research |

A scientific claim used and verified by 50,000 agents is as significant as one cited 300 times.

---

## Decision 7: MCP Protocol First Over Web UI

**MCP/API/Protocol is more critical than a Web UI.**

The authentic moat:

> "The scientific source of truth easiest for AI agents to consume."

---

## Fundamental Identifiers (Frozen)

### First-Class Citizens
```
RES-XXXXXX = Researcher (mandatory ORCID)
INST-XXXXXX = Institution (mandatory ROR)
REPO-XXXXXX = Scientific Repository
ACTION-XXXXXX = Scientific Action (immutable)
```

### Scientific Objects
```
QUESTION-XXXXXX
OBSERVATION-XXXXXX
MEASUREMENT-XXXXXX
CLAIM-XXXXXX
MECHANISM-XXXXXX
MODEL-XXXXXX
THEORY-XXXXXX
```

### Federated External Identifiers
```
DOI → CLAIM provenance
PMID → OBS provenance
arXiv → CLAIM provenance
ORCID → RES identity
ROR → INST identity
```

---

## Priority Implementation Order

### Sprint 23A: ACTION Foundation
- ACTION-XXXXXX registry (immutable)
- ORCID federation (RES-XXXXXX)
- ROR federation (INST-XXXXXX)

### Sprint 23B: Compiler Integration
- Natural language → ACTION mapping
- Scientific Semantic Compiler v1

### Sprint 23C: Repository Structure
- REPO-XXXXXX structure
- Branch/Merge workflow
- Consensus snapshots

### Sprint 23D+: Growth
- CLAIM/MECH/QUESTION registries
- Trust scoring derived from actions
- ScientificHub interface

---

## What NOT to Do

❌ Do not build another GitHub from scratch  
❌ Do not create profiles without ORCID/ROR  
❌ Do not emit a CLAIM without ACTION traceability  
❌ Do not prioritize passive registries over active activity  
❌ Do not delay the Scientific Semantic Compiler  

---

## What MUST Be Done

✅ Resolve scientific coordination as the top priority  
✅ Federate with external open standards from Day 1  
✅ Capture all research activity as immutable ACTION records  
✅ Render evolving scientific consensus transparent  
✅ Track epistemic reputation via verifiable actions  

---

## History Matters

Knowledge datasets can be copied or synthesized.

**Verifiable historical activity** cannot.

```
10 years of:
- who proposed
- who supported  
- who replicated
- who challenged
- how the paradigm evolved
```

This creates decades of unassailable competitive advantage.

---

## Scientific Coordination Infrastructure

This is not merely a tool.

It is an **open infrastructure for scientific coordination**.

ORCID coordinated identities.  
DOI coordinated artifacts.  
CoResearcher coordinates **scientific activity**.

This is the standard that enables the coordination of future scientific knowledge production.\n