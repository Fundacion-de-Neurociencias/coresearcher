#Boundary with AI Scientists
## Constitutional Directive Against Scope Expansion

**Version 1.0.0** - Boundary Definition  
**Status**: Constitutional Document - Core Governance

---

## DIRECTIVE: DO NOT BUILD AN AI SCIENTIST

CoResearcher does not:

- Generate scientific hypotheses
- Proposes discoveries
- Design experiments
- Optimize research pipelines
- Write original scientific contributions
- Evaluate whether a statement is correct
- Assigns severity or scientific quality
- Generate editorial recommendations

CoResearcher audits the traceability of existing artifacts.

Allowed question:
"How did we get here?"

Prohibited question:
"What should we find out next?"

---

## Strategic Context

There are three distinct trends in the scientific AI ecosystem:

### 1. Scientific Traceability (CoResearcher)
**Function**: Reconstruct and audit scientific history with complete traceability.

**Question answered**:
"Where is the evidence?"

**Method**:
- Scan repositories, issues, PRs, commits
- Extract ACTION-XXXXXX, CLAIM-XXXXXX, EVID-XXXXXX
- Build provenance chains
- Generate EvidenceGraphs

**Output**: Traceability graph, not content evaluations.

---

### 2. Scientific Review (PAT, Google)
**Function**: Evaluate quality of papers, reproducibility, methodology.

**Question answered**:
"Is this paper good?"

**Method**:
- Analyze paper structure
- Check appointments
- Evaluate methodology
- Test reproducibility

**Output**: Quality scores, recommendations, severity classifications.

**Border**: Do not build in CoResearcher. This is the natural extension for EditXT.

---

### 3. Scientific Discovery (AI Scientist, FutureHouse, OpenAI)
**Function**: Generate new hypotheses, design experiments, propose discoveries.

**Question answered**:
"What should we find out?"

**Method**:
- Generate hypotheses via LLM
- Design experimental protocols
- Optimize pipelines
- Propose new lines of research

**Output**: New scientific claims, proposed experiments.

**Border**: DO NOT build in CoResearcher. This would destroy competitive advantage.

---

## Frontier 3: AI Scientist

### Border Question

What should we discover?

### Response from CoResearcher

That question is beyond my reach.

My scope is:
"Where is the evidence for what we already claim?"

### If the border is crossed

If CoResearcher starts generating hypotheses, it is abandoning its position as a Traceability Engine to become another generic AI Scientist.

**Consequences**:
- Loses traceability (generation is less traceable than observation)
- Loses auditability (there is no provenance in LLM generation)
- Lose competitive advantage (Google and FutureHouse already do this better)
- Loses identity (becomes a commodity)

---

## Non-Negotiables (Border 3)

1. **No hypothesis generation**: CoResearcher does not create CLAIM-XXXXXX without observable source
2. **No design of experiments**: CoResearcher does not generate EXPERIMENT-XXXXXX
3. **No discovery proposal**: CoResearcher does not suggest new lines of research
4. **No pipeline optimization**: CoResearcher does not design research workflows
5. **No scientific writing**: CoResearcher does not generate original scientific text
6. **No correctness evaluation**: CoResearcher does not determine if a statement is true

---

## Empirical Validation > Conceptual Architecture

The current risk is not conceptual.

The architecture is stabilized from Sprint 55-59C.

The risk is that `observable_ratio ≈ 0.27` is an accidental property observed in 3 repositories.

**No more strategic documents will be resolved.**

They will resolve more data.

---

## Immediate Practical Implication

### SPRINT 59D: Correct LlamaIndex

Objective:
```
repository_resolution_rate = 1.0
```

Deliverable:
```
artifacts/llamaindex_retry_metrics.json
```

---

### SPRINT 59E: Benchmark with 20 Repositories

Objective:
```
20 repositorios reales procesados
```

Deliverables:
```
artifacts/cross_repo_20_complete.csv
artifacts/stability_metrics_20repos.json
```

Criterion:
```
>= 18 repos procesados
```

---

### SPRINT 60: EvidenceGraph v0

Input:
```
EvidenceRequest
```

Output:
```
EvidenceGraph
```

Minimum nodes:
- Claim
-Quote
-Source
- URL
-Classification
- Confidence

Deliverable:
```
artifacts/langgraph_evidence_graph.json
```

---

## Border Summary

```
Frontera 1: EditXT
  │
  └── Question: "What problems does this manuscript have?"
  └── Output: ReviewGraph, Recommendations, Severity
  └── Dirección: EditXT consume EvidenceGraph de CoResearcher

Frontera 2: AI Scientists (Google, FutureHouse, OpenAI, Anthropic)
  │
  └── Question: "What should we discover?"
  └── Output: New hypotheses, experiments, discoveries
  └── Dirección: No construir en CoResearcher

Frontera 1.5 (CoResearcher)
  │
  └── Question: "How did we get here?"
  └── Output: EvidenceGraph, Trajectory Report, Failure Taxonomy
  └── Dirección: Auditabilidad pura, sin evaluación de contenido
```

---

*This constitutional directive protects CoResearcher from the scope expansion it has eliminated for dozens of sprints. Not building an AI Scientist is not a limitation. It is the definition of competitive advantage.*