# SPRINT 60C BRIDGE: H6 → H7 → EHG v2
**Fecha**: 2026-07-31  
**Status**: SPRINT 60C completado; puente hacia SPRINT 61+  
**Principio**: Sin cambios arquitectónicos hasta H6 validada con datos autenticados

---

## 1. Estado Actual

### H6 — Decision Reconstruction
- **Estado**: PENDING
- **Evidencia**: 301 decisiones extraídas offline desde `data/langgraph_raw.json` con 426 edges
- **Validación pendiente**: Ejecutar pipeline autenticado contra GitHub API para confirmar precisión ≥70%
- **Artefactos**: `data/trajectories/langchain_ai_langgraph/`

### H7 — Branch Detection
- **Estado**: BLOQUEADO hasta H6
- **Razón**: Branch detection requiere DecisionGraph operativo; DecisionGraph requiere H6 validada
- **Preparación**: `docs/BRANCH_DETECTION_FEASIBILITY.md` documento listo

### H8 — Convergence Detection
- **Estado**: BLOQUEADO hasta H6+H7

### EHG v2 — Einstein Hypothesis Generator v2
- **Estado**: EXPLORATORIO
- **Documento**: `docs/EINSTEIN_HYPOTHESIS_GENERATOR_V2_VISION.md`
- **Activación**: Solo después de H7 validada

---

## 2. Arquitectura Congelada (Respetada)

### Capas estables
- EvidenceGraph v1.1.0
- DecisionNode (ya en schema)
- Edge types: chosen_over, abandoned_for, superseded_by

### Prohibido hasta nuevo aviso
- Añadir nodos al schema
- Crear BranchGraph/PossibilityGraph
- Modificar arquitectura

### Permitido
- Mejorar extractores
- Corregir bugs
- Escribir documentación

---

## 3. Datos Generados

### Repositorio: langchain-ai/langgraph

```
data/trajectories/langchain_ai_langgraph/
├── decisions_classified.jsonl     # 301 DecisionNodes
├── trajectory_graph.json          # Grafo completo con edges
└── evaluation_metrics.json        # Métricas
```

### Métricas offline

| Indicador | Valor |
|-----------|-------|
| Total decisions | 301 |
| Success | 122 |
| Abandoned | 129 |
| Failed | 40 |
| Pending | 10 |
| Edges totales | 426 |
| Explicit ref edges | 231 |
| Temporal edges | 195 |

### Muestra de outputs

- decisiones con `outcome: success`, `abandoned`, `failure`
- links `chosen_over`, `superseded_by`, `abandoned_for`
- trazabilidad via `artifact_url` y `actor`

---

## 4. Puente hacia SPRINT 61

### Paso 1: Validar H6

```bash
# Ejecutar pipeline con token
python scripts/run_sprint60c_pipeline.py \
  --repo langchain-ai/langgraph \
  --output data/trajectories/langchain_ai_langgraph \
  --token $GITHUB_TOKEN
```

**Criterios**:
- Extracción ≥70% respecto a issues/PRs reales con señales
- Precisión en muestra manual ≥70%
- Evidence coverage ≥80%

**Protocolo de auditoría humana**:
- Muestra aleatoria de 50 DecisionNodes
- Evaluación: ¿Es realmente una decisión observable?
- Categorías: `true_decision`, `activity_no_decision`, `inferred_false_positive`
- Métrica final: `precision_decision_nodes = true_decisions / sample_size`

### Paso 2: Si H6 valida → DecisionGraph

- Formalizar DecisionGraph como capa separada
- Mantener esquema actual; añadir queries MCP
- No crear nuevos nodos ni grafos

### Paso 3: Si H7 se aborda → Branch Detection

- Usar protocolo definido en `docs/BRANCH_DETECTION_FEASIBILITY.md`
- Extraer branches observables (PRs cerrados sin merge, issues wontfix, branches eliminadas)
- Calcular precisión/recall con validación humana

### Paso 4: Si H8 se aborda → Convergence Detection

- Detectar convergencias observables (mismo artifact, merge commit, duplicate issues)
- No detectar convergencias semánticas

### Paso 5: EHG v2

- Entrada: DecisionGraph + BranchGraph + EvidenceGraph
- Proceso: detectar ramas abandonadas; enriquecer con conocimiento moderno
- Salida: HypothesisCandidate estructurado
- Restricción: toda afirmación debe tener artifact asociado

---

## 5. Non-Goals Reafirmados

❌ No generar hipótesis sin evidencia  
❌ No crear nuevos schemas durante freeze  
❌ No predecir éxito/fracaso de branches  
❌ No ejecutar H7/H8 sin H6 validada  
❌ No desviar recursos de SPRINT 60C

---

## 6. Próxima Conversación

Debe reanudarse con:
- Resultados autenticados de H6
- Métricas cuantitativas reales
- Decisión Green/Yellow/Red
- Si Green: SPRINT 61 plan
- Si Red: reenfocar en misión core

No debe empezar con:
- Nuevos grafos
- Nuevos schemas
- Ideas arquitectónicas sin datos

---

*SPRINT 60C cierra ejecución tangible. H6 queda en Validación Autenticada. El camino a EHG v2 permanece definido pero bloqueado hasta evidencia empírica.*