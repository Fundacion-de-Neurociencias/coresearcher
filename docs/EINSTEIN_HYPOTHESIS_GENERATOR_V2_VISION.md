# EINSTEIN HYPOTHESIS GENERATOR V2: RESEARCH CARTOGRAPHER
**Status**: VISION DOCUMENT — Post-SPRINT 60C Roadmap  
**Constraint**: No implementation until H6 validated  
**Relationship**: Evolución natural del EHG v1, alineada con CoResearcher mission

---

## 1. Contexto: Por qué no es momento de implementar

### Arquitectura Congelada
- **H6**: Decision reconstruction — PENDIENTE DE VALIDACIÓN EMPÍRICA
- **H7**: Branch detection — EXPLORADO, NO EJECUTADO (depende de H6)
- **H8**: Convergence detection — EXPLORATORIO (depende de H6 + H7)

### Riesgo Actual
> "El mayor riesgo no es quedarse corto. Es seguir diseñando cuando ya existe un experimento capaz de responder la pregunta importante."

**Verdadero cuello de botella**: Datos.

### Conclusión
Esta documentación es **exploración estratégica**, no plan de implementación. Sirve para:
1. Capturar la visión antes de que se pierda
2. Preparar el terreno para SPRINT 61+ si H6 se valida
3. Evitar reinvención cuando llegue el momento

---

## 2. Observación Clave: La Ciencia es un Grafo

### Historia Oficial (Incorrecta)
```
Newton → Einstein → Relatividad
```

### Historia Real
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

**Patrón**: La ciencia es un árbol de decisiones, no una línea.

Cada "paradigma" es:
- Una bifurcación elegida
- Múltiples bifurcaciones abandonadas
- Conexiones entre ramas separadas

---

## 3. Limitación del EHG v1

### Problema Original
El Einstein Hypothesis Generator v1 operaba en el vacío:

```
Input: "Espacio-tiempo discreto"
Output: Hipótesis sin contexto histórico
```

**Crítica**: Podía generar:
- "Tiempo discreto"
- "Gravedad emergente"

Sin evidencia de que esas rutas hubieran sido consideradas históricamente.

**Demasiado libre. No conectado con evidencia real.**

---

## 4. Nueva Formulación: Research Cartographer

### Cambio de Pregunta

**EHG v1** (AI Scientist approach):
> "¿Qué deberíamos descubrir?"

**EHG v2** (CoResearcher approach):
> "¿Qué senderos plausibles quedaron sin recorrer, qué sabemos hoy que entonces no sabíamos, y cómo cambiarían esos senderos si los retomáramos ahora?"

### Principio Fundamental
> **No inventa. Navega.**

Un LLM es el motor, pero la arquitectura es el avión, y el **terreno** es el espacio de conocimiento.

Los AI Scientists actuales intentan: motor más potente.  
CoResearcher puede hacer: **mapa mejor**.

---

## 5. Arquitectura Propuesta (Post-H6)

### Capas

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

### Componente Nuevo: PossibilityGraph

**No es DecisionGraph. No es EvidenceGraph.**

Es un grafo de **bifurcaciones epistémicas**:

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

### Ejemplo Concreto: Espacio-Tiempo

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

**Nodo "espacio-tiempo discreto" no es falso. Es poco explorado.**

---

## 6. Proceso EHG v2

### Paso 1: Detectar Bifurcación
```yaml
Input: DecisionGraph, EvidenceGraph
Output: BranchNode
  axiom: "Continuidad del espacio-tiempo"
  adopted_path: "Continuo → Relatividad General"
  abandoned_path: "Discreto → ?"
```

### Paso 2: Analizar Contexto Histórico
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

### Paso 3: Buscar Conocimiento Posterior
```yaml
modern_knowledge:
  - Teoría cuántica de campos
  - Computación cuántica
  - Información física
  - Teoría de redes
  
relevant_connections:
  - "Loop Quantum Gravity retoma discretización"
  - "Causal Sets formaliza espacio-tiempo discreto"
  - "Holographic Principle sugiere emergencia"
```

### Paso 4: Generar Hipótesis Estructurada

**NO genera:**
```json
{
  "hypothesis": "Espacio-tiempo discreto"
}
```

**GENERA:**
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

## 7. Output Estructurado: Hypothesis Candidate

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

## 8. Aplicaciones

### 8.1 Detección de Bifurcaciones Históricas
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

### 8.2 Detección de Oportunidades Latentes
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

### 8.3 Detección de Convergencias Futuras
```python
# Futuro
convergence_candidates = PossibilityGraph.predict_convergence(
    branches=["Quantum Information", "Gravitational Physics"],
    time_horizon="10 years"
)
```

**Ejemplo real**:
```
Branch A: Neurociencia + IA → NeuroAI (convergencia reciente)
Branch B: Termodinámica + Información → Landauer (convergencia años 60)
Branch C: Genética + Evolución → Síntesis Moderna (convergencia años 40)
```

---

## 9. Comparación: AI Scientist vs Research Cartographer

| Aspecto | AI Scientist | Research Cartographer |
|---------|--------------|----------------------|
| Pregunta | "¿Qué descubrir?" | "¿Qué senderos quedaron sin recorrer?" |
| Método | Generación desde cero | Reconstrucción + proyección |
| Evidencia | Puede ignorar historia | Requiere evidencia histórica |
| Salida | Hipótesis nuevas | Hipótesis contextualizadas |
| Trazabilidad | Baja (black box) | Alta (cada nodo tiene artifact) |
| Riesgo | Alucinación científica | Bajo: todo está anclado a evidencia real |

---

## 10. Reconciliación con Filosofía CoResearcher

### Evidencia, Trazabilidad, Reconstrucción

✓ **Evidencia**: Cada bifurcación tiene artifacts (issues, PRs, commits)  
✓ **Trazabilidad**: Cada hipótesis rastrea a decisiones históricas observables  
✓ **Reconstrucción**: No inventa, recupera lo que existió

### No es un AI Scientist
- No genera conocimiento desde cero
- No hace afirmaciones sin evidencia
- No predice el futuro, solo mapea el espacio epistémico

### Es un Mapa del Territorio Científico
```
Territorio: Conocimiento científico (existente + posible)
Mapa: PossibilityGraph
Cartógrafo: EHG v2
Usuario: Investigador humano (decision final)
```

---

## 11. Relación con Einstein en la Conversación Original

### Interpretación Original (Rechazada)
```
Observaciones → Abducción → Nueva hipótesis
Einstein como generador de ideas
```

### Interpretación Nueva (Adoptada)
```
Trajectory Graph → Detectar bifurcaciones → Detectar regiones poco exploradas → Priorizar exploración
Einstein como explorador del espacio de trayectorias
```

### Preguntas Correctas

1. **¿Por qué Einstein encontró la relatividad?**
   → Porque transitó una región concreta del grafo.

2. **¿Qué otros caminos estaban disponibles en 1905?**
   → Espacio-tiempo curvo + discreto (abandonado)

3. **¿Qué caminos descartados podrían ser fértiles hoy?**
   → Discretización del espacio-tiempo (revisitado por LQG/Causal Sets)

4. **¿Qué caminos separados podrían converger más adelante?**
   → Neurociencia + IA → NeuroAI
   → Termodinámica + Información → Landauer

---

## 12. Integración con Visión Original del Usuario

> "Einstein podría convertirse en algo como: Exploration Engine que pregunte: ¿Cuáles son las ramas con alta evidencia histórica y baja exploración posterior?"

**Respuesta**: Sí, exactamente. Esto es el **Latent Opportunity Detector**.

> "¿Qué hipótesis fueron abandonadas por limitaciones tecnológicas y no por evidencia negativa?"

**Respuesta**: Esto es el **filtro principal** del Opportunity Detector.

> "Un mapa mejor puede ser más valioso que un motor más potente."

**Respuesta**: Esta es la diferencia fundamental entre:
- Competidores: "AI Scientists" (motores más potentes)
- CoResearcher: "Research Cartographer" (mapas mejores)

---

## 13. Próximos Pasos (Condicionales)

### Si H6 se valida (≥70% reconstrucción):
1. **Inmediato**: Documentar DecisionGraph como capa separada
2. **SPRINT 61**: Diseñar Branch Detection protocol (H7)
3. **SPRINT 62**: Prototipar PossibilityGraph con 2-3 repositorios
4. **SPRINT 63**: Implementar EHG v2 como módulo experimental

### Si H6 falla (<70% reconstrucción):
1. Reenfocar en reconstrucción de claims (misión core)
2. NO ejecutar H7/H8
3. Postergar EHG v2 indefinidamente

---

## 14. Non-Goals (Scope Guard)

❌ NO generar hipótesis científicas nuevas sin anclaje histórico  
❌ NO predecir qué rama will be successful  
❌ NO reemplazar juicio humano  
❌ NO ejecutar hasta H6 validada  
❌ NO agregar schemas nuevos hasta SPRINT 61+

✅ Únicamente mapear territorio epistémico existente  
✅ Únicamente detectar oportunidades latentes  
✅ Únicamente proporcionar trazabilidad completa  

---

## 15. Caso de Uso Concreto

### Escenario
Un investigador en computación cuántica quiere saber:
> "¿Qué enfoques para computación cuántica fueron abandonados antes de 1990 y podrían ser revisitados hoy?"

### Lo que EHG v2 Proporciona
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

### Lo que NO Proporciona
- "Deberías investigar células cuánticas"
- "Esta aproximación will be successful"
- Cualquier afirmación sin evidencia

---

## 16. Conclusión

EHG v2 no es un generador de hipótesis.

Es un **Research Cartographer** que:

1. Reconstruye bifurcaciones históricas (Evidence → Decision → Branch)
2. Identifica caminos abandonados con razones específicas
3. Evalúa relevancia moderna con conocimiento actual
4. Proyecta posibilidades sin afirmar certezas

**Filosofía**:
> "No te digo qué descubrir. Te muestro el mapa de lo que ya existía pero fue olvidado."

Esto es:
- Más humilde que "AI Scientist"
- Más coherente con CoResearcher
- Más alineado con trazabilidad
- Potencialmente más valioso: **un mapa mejor > motor más potente**

---

## 17. Estado Actual

**Hoy**: SPRINT 60C en ejecución  
**Mañana**: Resultados de repositorios reales  
**Futuro**: Si H6 valida, esta visión se convierte en SPRINT 61+

**Siguiente conversación debe empezar con**:
- "Ejecutamos SPRINT 60C en 20 repositorios"
- "H6 validada con 78% precisión"
- "Proceder a H7: Branch Detection"

**NO con**:
- Nuevas ideas arquitectónicas
- Nuevos grafos
- Nuevos schemas

---

*Esta es una máquina del tiempo de trayectorias. Pero en cada bifurcación hemos de dejar plantado un hito: Einstein asumió que el tiempo y el espacio no eran lineales sino que se podían curvar. También asumió que el tiempo y el espacio eran continuos. Hizo un cambio de paradigma frente al status del conocimiento previo respecto al espacio-tiempo lineal, pero mantuvo otro frente: la continuidad.*

*El camino "espacio-tiempo curvo pero discreto" quedó sin explorar.*

*Ese hito no explorado es exactamente lo que EHG v2 detectaría.*