# SPRINT 60C: TRAJECTORY RECONSTRUCTION
**Objetivo**: Validar empíricamente la reconstrucción de trayectorias de decisión desde repositorios reales de GitHub

**Status**: Ready for Execution  
**Próximo Sprint**: Sí - Arquitectura estabilizada, pasar a validación empírica

---

## 1. Hipótesis a Validar

### Hipótesis Principal

> Podemos reconstruir decisiones de investigación con la misma precisión con la que reconstruimos claims, extrayendo señales inequívocas de:
> - Issues abandonados
> - PRs cerrados sin merge
> - Branches eliminados
> - Comits que revertieron cambios
> - Experimentos documentados pero no productivos

### Hipótesis Secundarias

1. **Hipótesis de Abandono**: Los abandonment signals (issues cerrados, PRs no mergeados) pueden clasificarse como `DECISION` con `outcome: abandoned` con >80% precisión.

2. **Hipótesis de Éxito**: Los eventos que terminan en release/tag pueden clasificarse como `DECISION` con `outcome: success` con >80% precisión.

3. **Hipótesis de Trajectory**: La secuencia `DECISION-A → abandoned_for → DECISION-B → success` es detectable automáticamente en >60% de los casos donde existe evidencia textual de "We tried X but switched to Y".

---

## 2. Estado de la Evidencia (Pre-Sprint)

| Hipótesis | Estado Actual | Evidencia |
|-----------|---------------|-----------|
| Claims reconstruibles | ✅ **DEMOSTRADO** | Sprint 27-59: 20 repos, reconstrucción validada |
| EvidenceGraph útil | ✅ **PARCIALMENTE DEMOSTRADO** | langchain-ai/langgraph audit completada |
| Decision trajectories reconstruibles | ⚠️ **MODELADO** | Schemas definidos, sin validación empírica |
| Failure modes detectables | ⚠️ **HIPOTÉTICO** | Paper Princeton/Stanford/Berkeley proporciona marco teórico |
| Aprendizaje entre proyectos | ❌ **NO DEMOSTRADO** | Sin ejecución |

**Conclusión**: No más arquitectura. Necesitamos datos.

---

## 3. Metodología de Extracción

### 3.1 Repositorios Objetivo

Seleccionar 10-20 repositorios reales con:

**Criterios de inclusión**:
- Repositorios activos (>1 año de historia)
- >100 commits
- >50 issues cerrados
- >20 PRs mezclados
- Presencia de "research decisions" evidentes (cambios deapproach, abandonados, experimentos)

**Candidatos**:
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

### 3.2 Señales de Decisión a Extraer

**Explicit Decisions** (alta confianza):
```yaml
Tipo: DECLARATION
Señales:
  - Issue: "We decided to..."
  - PR description: "This PR implements decision #123"
  - Commit: "decision: switch to X"
  - Comment: "After discussion, we chose..."
Extracción: Regex + LLM classification
```

**Implicit Decisions** (media confianza):
```yaml
Tipo: INFERENCE
Señales:
  - Issue cerrado sin merge → abandoned_for
  - PR rechazado con comentario específico → chosen_over
  - Branch deleted sinmerge → abandoned_for
  - Revert commit → superseded_by
  - Issue reabierto con diferente título → abandoned_for + nueva decisión
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

## 4. Pipeline de Extracción

### 4.1 Fase 1: Recolección de Señales

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

### 4.2 Fase 2: Clasificación

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

### 4.3 Fase 3: Vinculación (Linking)

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

### 4.4 Fase 4: Reconstrucción de Trayectoria

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

## 5. Criterios de Éxito

### 5.1 Métricas Cuantitativas

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

### 5.2 Constitutional Validation: Decision Traceability Principle ⭐ **CRÍTICO**

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

### 5.2 Métricas Cualitativas

```yaml
Utilidad:
  - ¿La trayectoria reconstruida cuenta una historia coherente?
  - ¿Se pueden identificar los puntos de divergencia clave?
  - ¿La evidencia soporta las decisiones registradas?

Insights:
  - ¿Podemos detectar patrones de abandono?
  - ¿Podemos identificar decisiones exitosas replicables?
  - ¿La longitud de trayectoria correlaciona con éxito/fracaso?
```

---

## 6. Entregables

### 6.1 Scripts de Extracción

```bash
scripts/
├── extract_decisions.py          # Main extraction pipeline
├── classify_decisions.py         # Decision classifier
├── link_decisions.py             # Decision linker
├── reconstruct_trajectory.py     # Trajectory builder
├── evaluate_extraction.py        # Metrics calculator
└── visualize_trajectory.py       # Graph visualization
```

### 6.2 Datos Extraídos

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

### 6.3 Informe de Validación

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

## 7. Criterios de Parada

| Condición | Acción |
|-----------|--------|
| Precisión <70% en explicit decisions | Revisar metodología de extracción |
| Cobertura <50% | Ampliar ventana temporal o repositorios |
| No se detectan patrones de abandono | Revisar criterios de implicit decision |
| Tiempo >2 semanas | Reducir scope a 5 repositorios |

---

## 8. Riesgos

### 8.1 Ruido en Señales Implícitas

**Riesgo**: Muchos falsos positivos en abandoned_for

**Mitigación**: 
- Usar múltiples señales (issue + PR + branch)
- Establecer confidence thresholds
- Validación humana en muestra de 20 casos

### 8.4 Violación del Principio de Decision Traceability ⭐ **CRÍTICO**

**Riesgo**: Extraer campos que representan estados psicológicos inferidos

**Ejemplo de violación**:
```json
{
  "decision": "The team believed X was better",
  "rationale": "They thought it would be faster",
  "confidence": 0.6
}
```

**Mitigación**:
- Implementar validator que rechaza campos como `belief`, `opinion`, `thought`, `assumption`, `felt`
- Marcar como `inferred` cualquier rationale no directamente citado de artifacts
- Establecer confidence=1.0 solo para texto literal, confidence=0.7-0.9 para inferido
- Bloquear generación de DecisionNodes sin evidencia asociada

### 8.2 Subjetividad en Rationale

**Riesgo**: Rationale extraído de texto no es la decisión real

**Mitigación**:
- Marcar como `inferred` si no hay declaración explícita
- Usar LLM para generar hipótesis de rationale
- No usar rationale para evaluación, solo para contexto

### 8.3 Sesgo de Supervivencia

**Riesgo**: Solo vemos decisions exitosas (las que llegaron a código)

**Mitigación**:
- Incluir explícitamente issues cerrados sin merge
- Incluir branches eliminados
- Incluir reverts

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

**Critically**: Este sprint NO construye nada nuevo en arquitectura. Solo valida lo existente contra datos reales.

---

## 10. Success Looks Like

Al final de SPRINT 60C, podemos decir:

✅ "Hemos extraído 247 decisiones de 15 repositorios con 78% precisión"
✅ "Hemos reconstruido 23 trayectorias completas con éxito"
✅ "Hemos detectado 89 abandonamientos con 72% recall"
✅ "La trayectoria promedio tiene 4.2 decisiones, 1.3 abandonamientos"

Y más importante:

✅ **Hemos demostrado que CoResearcher puede reconstruir trayectorias, no solo claims.**

---

## 11. Non-Goals (Scope Guard)

❌ NO construir Decision Quality Engine (no evaluar decisiones)
❌ NO construir motor de predicción (no predecir éxito/fracaso)
❌ NO construir sistema de recomendación (no sugerir decisiones)
❌ NO ampliar arquitectura (schemas están estables)

✅ SOLO extraer, clasificar, y reconstruir trayectorias desde GitHub
✅ SOLO validar si el modelo funciona contra datos reales

---

## 12. Immediate Next Steps

1. **Day 1**: Seleccionar 10 repositorios candidatos
2. **Day 2**: Implementar `extract_decisions.py` (señales básicas: issues, PRs, commits)
3. **Day 3**: Implementar `classify_decisions.py` (heurísticas + regex)
4. **Day 4**: Implementar `link_decisions.py` (edges básicos)
5. **Day 5**: Ejecutar pipeline en 1 repositorio piloto (langgraph)
6. **Day 6**: Validación manual de muestra (20 decisiones)
7. **Day 7**: Ajustar thresholds y parámetros
8. **Day 8-14**: Ejecutar en 9-19 repositorios restantes
9. **Day 15**: Generar `SPRINT_60C_VALIDATION_REPORT.md`
10. **Day 16**: Presentar resultados y decidir SPRINT 61

---

*Este sprint es la validación empírica que necesita CoResearcher para demostrar que puede reconstruir trayectorias de investigación, no solo claims aislados.*