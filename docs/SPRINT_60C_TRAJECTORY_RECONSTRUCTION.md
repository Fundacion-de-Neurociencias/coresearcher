# SPRINT 60C: TRAJECTORY RECONSTRUCTION
**Objective**: Empirically validate the reconstruction of decision trajectories from real GitHub repositories

**Status**: Ready for Execution  
**Next Sprint**: Yes - Stabilized architecture, move to empirical validation

---

## 1. Hypotheses to Validate

### Main Hypothesis

> We can reconstruct research decisions with the same precision with which we reconstruct claims, extracting unequivocal signals from:
> - Abandoned issues
> - PRs closed without merge
> - Branches removed
> - Committees that reverted changes
> - Documented but non-productive experiments

### Secondary Hypotheses

1. **Abandonment Hypothesis**: Abandonment signals (closed issues, unmerged PRs) can be classified as `DECISION` with `outcome: abandoned` with >80% accuracy.

2. **Success Hypothesis**: Events ending in release/tag can be classified as `DECISION` with `outcome: success` with >80% accuracy.

3. **Trajectory Hypothesis**: The sequence `DECISION-A → abandoned_for → DECISION-B → success` is automatically detectable in >60% of cases where there is textual evidence of "We tried X but switched to Y".

---

## 2. Evidence Status (Pre-Sprint)

| Hypothesis | Current Status | Evidence |
|-----------|--------|-----------|
| Reconstructable claims | ✅ **PROVEN** | Sprint 27-59: 20 repos, rebuild validated |
| Useful EvidenceGraph | ✅ **PARTIALLY DEMONSTRATED** | langchain-ai/langgraph audit completed |
| Decision reconstructable trajectories | ⚠️ **MODELING** | Defined schemes, without empirical validation |
| Failure modes detectable | ⚠️ **HYPOTHETICAL** | Paper Princeton/Stanford/Berkeley provides theoretical framework |
| Learning between projects | ❌ **NOT SHOWN** | No execution |

**Conclusion**: No more architecture. We need data.

---

## 3. Extraction Methodology

### 3.1 Target Repositories

Select 10-20 real repositories with:

**Inclusion criteria**:
- Active repositories (>1 year history)
- >100 commits
- >50 issues closed
- >20 mixed PRs
- Presence of obvious "research decisions" (approach changes, abandoned, experiments)

**Candidates**:
```
1. langchain-ai/langgraph        (ya auditado en SPRINT 59)
2. langchain-ai/langchain         (similar a langgraph)
3. tensorflow/tensorflow          (large-scale, many abandoned features)
4. pytorch/pytorch                (research-oriented)
5. scikit-learn/scikit-learn      (scientific computing)
6. biopython/biopython            (genomics - GeneForge adjacent)
7. nilearn/nilearn                (neuroimaging - Neurodiagnoses adjacent)
8. nilearn/nilearn                (neuroimaging - Neurodiagnoses adjacent)
9. openscience/openscience        (if public)
10. neuroforgede/medicalia        (if accessible)
```

### 3.2 Decision Signals to Extract

**Explicit Decisions** (high confidence):
```yaml
Tipo: DECLARATION
Señales:
  - Issue: "We decided to..."
  - PR description: "This PR implements decision #123"
  - Commit: "decision: switch to X"
  - Comment: "After discussion, we chose..."
Extracción: Regex + LLM classification
```

**Implicit Decisions** (half confidence):
```yaml
Tipo: INFERENCE
Señales:
  - Issue cerrado sin merge → abandoned_for
  - PR rechazado con comentario específico → chosen_over
  - Branch deleted sinmerge → abandoned_for
  - Revert commit → superseded_by
- Issue reopened with different title → abandoned_for + new decision
Extracción: Heurísticas + patrones
```

**Outcome Signals**:
```yaml
success:
  - Tag/Release asociado
  - PR mergeado con tests passing
  - Issue cerrado como "fixed"
  
failure:
  - Revert commit
  - Issue cerrado como "wontfix" o "obsolete"
  - PR cerrado sin merge
  
abandoned:
  - Issue abandonado (sin actividad >90 días)
  - PR abandonado (sin merge, sin actividad >60 días)
  - Branch eliminado
  
superseded:
  - Commit message contiene "supersedes"
  - Issue reference: "Replaced by #456"
```

---

## 4. Extraction Pipeline

### 4.1 Phase 1: Signal Collection

```bash
# Para cada repositorio
python scripts/extract_decisions.py \
  --repo langchain-ai/langgraph \
  --since 2024-01-01 \
  --output decisions_raw.jsonl
```

**Output**:
```jsonl
{"type": "issue_closed", "issue_id": 8438, "state": "closed", "labels": ["wontfix"], "comments": 3}
{"type": "pr_merged", "pr_id": 8420, "title": "Switch to pydantic v2", "merge_commit": "abc123"}
{"type": "branch_deleted", "branch": "feature/old-auth", "commits": 15}
{"type": "revert_commit", "commit": "def456", "revert_of": "abc123"}
```

### 4.2 Phase 2: Classification

```python
class DecisionClassifier:
    def classify(self, signal) -> DecisionHypothesis:
        # Heurística
        if signal.type == "issue_closed" and signal.labels contains "wontfix":
            return DecisionHypothesis(
                decision_id=f"DECISION-{issue_id}",
                outcome="abandoned",
                confidence=0.7,
                actor=extract_actor(signal)
            )
        
        # LLM-assisted (para casos ambiguos)
        elif signal.needs_llm:
            return self.llm_classify(signal)
```

**Output**:
```json
{
  "decision_id": "DECISION-000001",
  "repository": "langchain-ai/langgraph",
  "actor": "hinthakka",
  "timestamp": "2026-05-15T10:30:00Z",
  "decision": "Switch from JSON to pydantic for configuration validation",
  "outcome": "success",
  "confidence": 0.85,
  "evidence": ["PR-8420", "commit-abc123", "release-0.1.95"],
  "rationale": "Pydantic provides better type safety and validation"
}
```

### 4.3 Phase 3: Linking

```python
class DecisionLinker:
    def link_decisions(self, decisions: List[Decision]) -> List[Edge]:
        edges = []
        
        # Detectar chosen_over
        for d1, d2 in self.find_alternatives(decisions):
            if d1.outcome == "success" and d2.outcome == "abandoned":
                edges.append(Edge(
                    from_=d1.id,
                    to=d2.id,
                    type="chosen_over"
                ))
        
        # Detectar superseded_by
        for d in decisions:
            if d.has_reference("supersedes"):
                edges.append(Edge(
                    from_=d.id,
                    to=extract_referenced_decision(d),
                    type="superseded_by"
                ))
        
        return edges
```

### 4.4 Phase 4: Trajectory Reconstruction

```python
class TrajectoryReconstructor:
    def reconstruct(self, root_decision_id: str) -> EvidenceGraph:
        # BFS/DFS para encontrar connected decisions
        decisions = self.get_connected_decisions(root_decision_id)
        
        # Obtener artifacts asociados (PRs, commits, issues)
        artifacts = self.get_artifacts_for_decisions(decisions)
        
        # Construir grafo
        graph = EvidenceGraph()
        for d in decisions:
            graph.add_node(DecisionNode.from_decision(d))
        for a in artifacts:
            graph.add_node(ArtifactNode.from_artifact(a))
        
        # Añadir edges
        for edge in self.linker.link_decisions(decisions):
            graph.add_edge(edge)
        
        return graph
```

---

## 5. Success Criteria

### 5.1 Quantitative Metrics

```yaml
Precisión de extracción:
  - Explicit decisions: ≥85%
  - Implicit decisions: ≥70%
  - Outcome classification: ≥80%

Cobertura:
  - Decisions detectadas / Decisions totales (estimadas): ≥60%
  - Abandonments detectados / Abandonments totales: ≥70%

Vinculación:
  - chosen_over accuracy: ≥75%
  - superseded_by accuracy: ≥80%
```

### 5.2 Constitutional Validation: Decision Traceability Principle ⭐ **CRITICAL**

```yaml
Decision Traceability Compliance:
  - 100% de DecisionNodes deben ser Observable o Derivable
  - 0% de campos con estados psicológicos inferidos (belief, opinion, thought)
  - 100% de decisiones tienen al menos un artifact de evidencia
  
Validación por campo:
  - decision: 100% observable o derivable
  - actor: 100% observable (GitHub username, commit author)
  - timestamp: 100% observable (issue/PR/commit date)
  - rationale: ≥80% observable/derivable, ≤20% inferred (marcado)
  - outcome: 100% derivable de eventos observables
  
Evidence Anchoring:
  - 100% de DecisionNodes tienen ≥1 artifact asociado
  - 100% de artifacts son trazables a GitHub (issue, PR, commit)
```

### 5.2 Qualitative Metrics

```yaml
Utilidad:
- Does the reconstructed trajectory tell a coherent story?
- Can you identify key points of divergence?
- Does the evidence support the recorded decisions?

Insights:
- Can we detect abandonment patterns?
- Can we identify successful replicable decisions?
- Does path length correlate with success/failure?
```

---

## 6. Deliverables

### 6.1 Extraction Scripts

```bash
scripts/
├── extract_decisions.py          # Main extraction pipeline
├── classify_decisions.py         # Decision classifier
├── link_decisions.py             # Decision linker
├── reconstruct_trajectory.py     # Trajectory builder
├── evaluate_extraction.py        # Metrics calculator
└── visualize_trajectory.py       # Graph visualization
```

### 6.2 Extracted Data

```
data/trajectories/
├── langchain-ai_langgraph/
│   ├── decisions.jsonl
│   ├── edges.jsonl
│   └── trajectory_graph.json
├── tensorflow_tensorflow/
│   ├── decisions.jsonl
│   ├── edges.jsonl
│   └── trajectory_graph.json
└── ... (10-20 repos)
```

### 6.3 Validation Report

```markdown
docs/SPRINT_60C_VALIDATION_REPORT.md

Secciones:
  1. Metodología
  2. Repositorios analizados
  3. Decisions extraídas (tabla)
  4. Precision/Recall por categoría
  5. Casos de éxito
  6. Casos de fallo
  7. Limitaciones detectadas
  8. Recomendaciones para SPRINT 61
```

---

## 7. Stopping Criteria

| Condition | Action |
|-----------|--------|
| Accuracy <70% in explicit decisions | Review extraction methodology |
| Coverage <50% | Expand temporary window or repositories |
| No abandonment patterns detected | Review implicit decision criteria |
| Time >2 weeks | Reduce scope to 5 repositories |

---

## 8. Risks

### 8.1 Noise in Implicit Signals

**Risk**: Many false positives in abandoned_for

**Mitigation**: 
- Use multiple signals (issue + PR + branch)
- Establish confidence thresholds
- Human validation in a sample of 20 cases

### 8.4 Violation of the Decision Traceability Principle ⭐ **CRITICAL**

**Risk**: Extracting fields that represent inferred psychological states

**Example of violation**:
```json
{
  "decision": "The team believed X was better",
  "rationale": "They thought it would be faster",
  "confidence": 0.6
}
```

**Mitigation**:
- Implement validator that rejects fields like `belief`, `opinion`, `thought`, `assumption`, `felt`
- Mark as `inferred` any rationale not directly cited from artifacts
- Set confidence=1.0 for literal text only, confidence=0.7-0.9 for inferred
- Block DecisionNodes generation without associated evidence

### 8.2 Subjectivity in Rationale

**Risk**: Rationale extracted from text is not the real decision

**Mitigation**:
- Mark as `inferred` if no explicit declaration
- Use LLM to generate rationale hypotheses
- Do not use rationale for evaluation, only for context

### 8.3 Survivorship Bias

**Risk**: We only see successful decisions (those that reached code)

**Mitigation**:
- Explicitly include closed issues without merge
- Include deleted branches
- Include reverts

---

## 9. Relationship to Existing Components

```
SPRINT 60C TRAJECTORY RECONSTRUCTION
    ↓ usa
EvidenceGraph (schemas/evidence_graph.schema.json)
    ↓ con DECISION nodes y edges
    
Decision Registry (docs/DECISION_EXECUTION_REGISTRY.md)
    ↓ alimenta
DecisionTrajectory (schemas/decision_trajectory.schema.json)
    ↓ alimenta
NeuroOS Brain (futuro)
```

**Critically**: This sprint does NOT build anything new in architecture. It only validates what exists against real data.

---

## 10. Success Looks Like

At the end of SPRINT 60C, we can say:

✅ "We have extracted 247 decisions from 15 repositories with 78% accuracy"
✅ "We have successfully rebuilt 23 complete trajectories"
✅ "We have detected 89 abandonments with 72% recall"
✅ "The average trajectory has 4.2 decisions, 1.3 abandonments"

And more importantly:

✅ **We have shown that CoResearcher can reconstruct trajectories, not just claims.**

---

## 11. Non-Goals (Scope Guard)

❌ DO NOT build Decision Quality Engine (do not evaluate decisions)
❌ DO NOT build prediction engine (do not predict success/failure)
❌ DO NOT build recommendation system (do not suggest decisions)
❌ DO NOT extend architecture (schemas are stable)

✅ ONLY extract, classify, and rebuild trajectories from GitHub
✅ ONLY validate if the model works against real data

---

## 12. Immediate Next Steps

1. **Day 1**: Select 10 candidate repositories
2. **Day 2**: Implement `extract_decisions.py` (basic signals: issues, PRs, commits)
3. **Day 3**: Implement `classify_decisions.py` (heuristics + regex)
4. **Day 4**: Implement `link_decisions.py` (basic edges)
5. **Day 5**: Run pipeline in 1 pilot repository (langgraph)
6. **Day 6**: Manual sample validation (20 decisions)
7. **Day 7**: Adjust thresholds and parameters
8. **Day 8-14**: Run on remaining 9-19 repositories
9. **Day 15**: Generate `SPRINT_60C_VALIDATION_REPORT.md`
10. **Day 16**: Present results and decide SPRINT 61

---

*This sprint is the empirical validation that CoResearcher needs to demonstrate that it can reconstruct research trajectories, not just isolated claims.*