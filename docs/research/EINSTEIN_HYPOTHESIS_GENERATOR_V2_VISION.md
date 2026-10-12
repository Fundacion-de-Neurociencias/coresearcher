# EINSTEIN HYPOTHESIS GENERATOR V2: RESEARCH CARTOGRAPHER
**Status**: VISION DOCUMENT — Post-SPRINT 60C Roadmap  
**Constraint**: No until implementation H6 validated  
**Relationship**: Natural evolution of EHG v1, aligned with CoResearcher mission

---

## 1. Context: Why it is not time to implement

### Frozen Architecture
- **H6**: Decision reconstruction — PENDING EMPIRICAL VALIDATION
- **H7**: Branch detection — EXPLORED, NOT EXECUTED (depends on H6)
- **H8**: Convergence detection — EXPLORATORY (depends on H6 + H7)

### Current Risk
> "The biggest risk is not falling short. It is continuing to design when there is already an experiment capable of answering the important question."

**True bottleneck**: Data.

### Conclusion
This documentation is **strategic exploration**, not an implementation plan. Serves for:
1. Capture the vision before it is lost
2. Prepare the ground for SPRINT 61+ if H6 is validated
3. Avoid reinvention when the time comes

---

## 2. Key Observation: Science is a Graph

### Official History (Incorrect)
```
Newton → Einstein → Relatividad
```

### True Story
```
                Éter
               /
Maxwell ------
               \
                Relatividad especial
                         \
                          Einstein
                         /
Mercurio --------------
                         \
                          Geometría diferencial
```

**Pattern**: Science is a decision tree, not a line.

Each "paradigm" is:
- A chosen branch
- Multiple abandoned forks
- Connections between separate branches

---

## 3. Limitation of EHG v1

### Original Problem
The Einstein Hypothesis Generator v1 operated in a vacuum:

```
Input: "Espacio-tiempo discreto"
Output: Hypotheses without historical context
```

**Criticism**: Could generate:
- "Discreet time"
- "Emerging gravity"

No evidence that those routes had been considered historically.

**Too free. Not connected to real evidence.**

---

## 4. New Formulation: Research Cartographer

### Question Change

**EHG v1** (AI Scientist approach):
> "What should we find out?"

**EHG v2** (CoResearcher approach):
> "What plausible paths were left untrodden, what do we know today that we didn't know then, and how would those paths change if we took them up now?"

### Fundamental Principle
> **Does not invent. Browse.**

An LLM is the engine, but the architecture is the plane, and the **terrain** is the knowledge space.

Today's AI Scientists try: more powerful engine.  
CoResearcher can make: **map better**.

---

## 5. Proposed Architecture (Post-H6)

### Layers

```
EvidenceGraph (v1.1.0 — STABLE)
        ↓
DecisionGraph (Post-H6 validation)
        ↓
BranchGraph (Post-H7)
        ↓
Einstein Hypothesis Generator v2
        ↓
Candidate Hypothesis
```

### New Component: PossibilityGraph

**Not DecisionGraph. Not EvidenceGraph.**

It is a graph of **epistemic bifurcations**:

```yaml
PossibilityGraph:
  nodes:
    - branch_id
    - hypothesis (adopted)
    - alternative (abandoned)
    - evidence_available_then
    - exploration_cost
    - historical_exploration_degree
    - future_connection_potential
  
  edges:
    - diverged_from
    - converged_with
    - reopens_via
```

### Concrete Example: Space-Time

```
1905
|
+-- gravedad = geometría
|       |
|       +-- continuo      ✓ Einstein (exploración: 95%)
|       |
|       +-- discreto      ✗ abandonada (exploración: 5%)
|           |
|           +-- Causal Sets (años 80)
|           +-- Loop Quantum Gravity (años 90)
|
+-- gravedad = fuerza cuántica ✗ (exploración: 2%)
```

**Node "discrete space-time" is not false. It is little explored.**

---

## 6. EHG v2 process

### Step 1: Detect Fork
```yaml
Input: DecisionGraph, EvidenceGraph
Output: BranchNode
  axiom: "Continuidad del espacio-tiempo"
  adopted_path: "Continuo → Relatividad General"
  abandoned_path: "Discreto → ?"
```

### Step 2: Analyze Historical Context
```yaml
abandonment_signals:
  - "Sin evidencia experimental disponible"
  - "Limitaciones matemáticas de la época"
  - "No contradictorio, solo no explorado"
  
exploration_barriers:
  - Computacional: "No había formalismos matemáticos"
  - Tecnológico: "No había datos a esa escala"
  - Conceptual: "Paradigma dominante no lo permitía"
```

### Step 3: Seek Further Knowledge
```yaml
modern_knowledge:
- Quantum field theory
  - Computación cuántica
  - Información física
- Network theory
  
relevant_connections:
  - "Loop Quantum Gravity retoma discretización"
  - "Causal Sets formaliza espacio-tiempo discreto"
  - "Holographic Principle sugiere emergencia"
```

### Step 4: Generate Structured Hypotheses

**DOES NOT generate:**
```json
{
  "hypothesis": "Espacio-tiempo discreto"
}
```

**GENERATES:**
```json
{
  "hypothesis": "El espacio-tiempo podría emerger de una red discreta de información",
  
  "parent_branch": "Relatividad General",
  "historical_decision": "Continuidad asumida (1905)",
  
  "modified_assumption": "Continuidad → Discretización",
  "preserved_assumptions": ["Covariancia", "Equivalencia", "Causalidad"],
  
  "historical_context": {
    "abandoned_in": 1905,
    "reason": "Sin formalismos matemáticos disponibles",
    "barrier_type": "tecnológico"
  },
  
  "modern_foundations": {
    "theories": ["Loop Quantum Gravity", "Causal Sets"],
    "evidence": ["Planck scale discreteness", "Holographic bounds"],
    "experiments": ["Gamma-ray burst delays", "Gravitational wave decoherence"]
  },
  
  "expected_consequences": [
    "Modificación de geodésicas a escala Planck",
    "Reformulación de singularidades",
    "Nueva fenomenología en cosmological constant"
  ],
  
  "conflicts": [
    "Contradice asunción de continuidad en RG",
    "Requiere reformulación matemática completa"
  ],
  
  "supporting_evidence": [...],
  "missing_evidence": [...],
  "falsification_paths": [...]
}
```

---

## 7. Structured Output: Hypothesis Candidate

```yaml
HypothesisCandidate:
  id: "HC-000001"
  
  parent_branch: "Relatividad General"
  historical_context: "Branch abandoned in 1905 due to computational limitations"
  
  preserved_assumptions:
    - "Covariance principle"
    - "Equivalence principle"
    - "Causality"
  
  modified_assumptions:
    - axiom: "Space-time continuity"
      original: "Continuous manifold"
      proposed: "Discrete network emerging at Planck scale"
  
  modern_knowledge_integration:
    - field: "Quantum Gravity"
      contribution: "Mathematical formalisms for discrete geometry"
    - field: "Information Theory"
      contribution: "Holographic bounds suggest finite information content"
  
  evidence_requirements:
    - "Planck-scale deviations from geodesics"
    - "Quantum decoherence in gravitational waves"
  
  falsification_criteria:
    - "Continuous manifold confirmed at all scales"
    - "No deviations from GR predictions"
  
  exploration_priority:
    rationale: "Historical abandonment due to technology, not evidence"
    score: 0.75
    comparable_branches: ["Causal Sets", "Loop Quantum Gravity"]
```

---

## 8. Applications

### 8.1 Detection of Historical Bifurcations
```python
# No implementar hasta H7 validado
branches = PossibilityGraph.detect_bifurcations(
    source=EvidenceGraph,
    criteria={
        "abandonment_signals": ["wontfix", "closed_no_merge", "revert"],
        "barrier_type": ["technological", "computational", "conceptual"]
    }
)
```

### 8.2 Detection of Latent Opportunities
```python
# Futuro
opportunities = PossibilityGraph.find_latent_opportunities(
    filters={
        "historical_exploration": "<20%",
        "modern_relevance": ">0.7",
        "evidence_not_against": True
    }
)
```

**Output**:
```
Branch: "Discrete space-time"
Historical exploration: 5%
Modern relevance: 0.85
Reason abandoned: "No mathematical formalisms available in 1905"
Current status: "LQG and Causal Sets provide formalism"
Opportunity score: HIGH
```

### 8.3 Detection of Future Convergences
```python
# Futuro
convergence_candidates = PossibilityGraph.predict_convergence(
    branches=["Quantum Information", "Gravitational Physics"],
    time_horizon="10 years"
)
```

**Real example**:
```
Branch A: Neuroscience + AI → NeuroAI (recent convergence)
Branch B: Thermodynamics + Information → Landauer (convergence 60s)
Branch C: Genetics + Evolution → Modern Synthesis (1940s convergence)
```

---

## 9. Comparison: AI Scientist vs Research Cartographer

| Appearance | AI Scientist | Research Cartographer |
|---------|--------------|----------------------|
| Question | "What to discover?" | "What paths were left untrodden?" |
| Method | Generation from scratch | Reconstruction + projection |
| Evidence | You can ignore history | Requires historical evidence |
| Output | New hypotheses | Contextualized hypotheses |
| Traceability | Low (black box) | High (each node has artifact) |
| Risk | Scientific hallucination | Low: everything is anchored to real evidence |

---

## 10. Reconciliation with CoResearcher Philosophy

### Evidence, Traceability, Reconstruction

✓ **Evidence**: Each fork has artifacts (issues, PRs, commits)  
✓ **Traceability**: Each hypothesis tracks observable historical decisions  
✓ **Reconstruction**: Do not invent, recover what existed

### Not an AI Scientist
- Does not generate knowledge from scratch
-Does not make claims without evidence
- It does not predict the future, it only maps the epistemic space

### It is a Map of the Scientific Territory
```
Territory: Scientific knowledge (existing + possible)
Mapa: PossibilityGraph
Cartógrafo: EHG v2
Usuario: Investigador humano (decision final)
```

---

## 11. Relationship with Einstein in the Original Conversation

### Original Interpretation (Rejected)
```
Observations → Abduction → New hypothesis
Einstein como generador de ideas
```

### New Interpretation (Adopted)
```
Trajectory Graph → Detectar bifurcaciones → Detectar regiones poco exploradas → Priorizar exploración
Einstein como explorador del espacio de trayectorias
```

### Correct Questions

1. **Why did Einstein find relativity?**
   → Because it transited a specific region of the graph.

2. **What other roads were available in 1905?**
   → Curved + discrete space-time (abandoned)

3. **What discarded paths could be fertile today?**
   → Discretization of space-time (revisited by LQG/Causal Sets)

4. **What separate paths might converge later?**
   → Neuroscience + AI → NeuroAI
   → Thermodynamics + Information → Landauer

---

## 12. Integration with Original User Vision

> "Einstein could become something like: Exploration Engine that asks: What are the branches with high historical evidence and low subsequent exploration?"

**Answer**: Yes, exactly. This is the **Latent Opportunity Detector**.

> "Which hypotheses were abandoned because of technological limitations and not because of negative evidence?"

**Answer**: This is the **main filter** of the Opportunity Detector.

> "A better map can be more valuable than a more powerful engine."

**Answer**: This is the fundamental difference between:
- Competitors: "AI Scientists" (more powerful engines)
- CoResearcher: "Research Cartographer" (better maps)

---

## 13. Next Steps (Conditional)

### If H6 is validated (≥70% reconstruction):
1. **Immediate**: Document DecisionGraph as a separate layer
2. **SPRINT 61**: Design Branch Detection protocol (H7)
3. **SPRINT 62**: Prototype PossibilityGraph with 2-3 repositories
4. **SPRINT 63**: Implement EHG v2 as an experimental module

### If H6 fails (<70% rebuild):
1. Refocus on claims reconstruction (core mission)
2. DO NOT run H7/H8
3. Delay EHG v2 indefinitely

---

## 14. Non-Goals (Scope Guard)

❌ DO NOT generate new scientific hypotheses without historical anchoring  
❌ DO NOT predict which branch will be successful  
❌ DO NOT replace human judgment  
❌ DO NOT execute until H6 validated  
❌ DO NOT add new schemas until SPRINT 61+

✅ Only map existing epistemic territory  
✅ Only detect latent opportunities  
✅ Only provide full traceability  

---

## 15. Concrete Use Case

### Scenario
A quantum computing researcher wants to know:
> "What approaches to quantum computing were abandoned before 1990 and could be revisited today?"

### What EHG v2 Provides
```json
{
  "query": "Quantum computing approaches abandoned before 1990",
  
  "branches_found": [
    {
      "decision": "Quantum cellular automata (1980s)",
      "abandoned": 1987,
      "reason": "No error correction schemes available",
      "modern_relevance": {
        "error_correction": "Surface codes now available",
        "relevance_score": 0.82
      },
      "status": "Revisitable with current technology"
    },
    {
      "decision": "Analog quantum computation",
      "abandoned": 1992,
      "reason": "Decoherence too fast",
      "modern_relevance": {
        "decoherence_control": "Improved by 3 orders of magnitude",
        "relevance_score": 0.65
      },
      "status": "Marginal improvement, still challenging"
    }
  ],
  
  "confidence": 0.78,
  "evidence_sources": ["arXiv:quant-ph/8507002", "PRL-1987-59"],
  "reconstruction_method": "backward"
}
```

### What it DOES NOT Provide
- "You should investigate quantum cells"
- "This approach will be successful"
- Any claim without evidence

---

## 16. Conclusion

EHG v2 is not a hypothesis generator.

It is a **Research Cartographer** who:

1. Reconstruct historical branches (Evidence → Decision → Branch)
2. Identify abandoned roads with specific reasons
3. Evaluate modern relevance with current knowledge
4. Project possibilities without stating certainties

**Philosophy**:
> "I'm not telling you what to discover. I'm showing you the map of what already existed but was forgotten."

This is:
- More humble than "AI Scientist"
- More consistent with CoResearcher
- More aligned with traceability
- Potentially more valuable: **better map > more powerful engine**

---

## 17. Current Status

**Today**: SPRINT 60C running  
**Tomorrow**: Results from real repositories  
**Future**: If H6 validates, this vision becomes SPRINT 61+

**Next conversation should start with**:
- "We run SPRINT 60C on 20 repositories"
- "H6 validated with 78% accuracy"
- "Proceed to H7: Branch Detection"

**NOT with**:
- New architectural ideas
- New graphs
- New schemas

---

*This is a trajectory time machine. But at each fork we must leave a milestone: Einstein assumed that time and space were not linear but could be curved. He also assumed that time and space were continuous. He made a paradigm shift regarding the status of prior knowledge regarding linear space-time, but maintained another front: continuity.*

*The "curved but discrete space-time" path was left unexplored.*

*That unexplored landmark is exactly what EHG v2 would detect.*