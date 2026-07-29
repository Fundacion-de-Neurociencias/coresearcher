# Scientific Execution Model
## The Atomic Unit of Scientific Work

**Version 1.0.0** - Foundational Execution Architecture  
**Status**: Constitutional Document - Core Architecture

---

## Article I: The Scientific Execution Question

### Section 1. The Fundamental Inquiry

> **¿Cuál es la unidad mínima de ejecución científica?**

No es el paper.
No es el claim.
No es la decisión.

---

## Article II: The Answer - Dual Atomic Units

### Section 1. Strategic Unit

```
QUESTION
```

La pregunta es la unidad estratégica porque:
- **Sobrevive** a claims, papers, agentes
- **Dirige** recursos y atención
- **Persistge** décadas sin cambiar
- **Genera** actividad continua

```
QUESTION-000123: "¿Cuáles son los biomarcadores sanguíneos del Alzheimer?"
├── 2020-2023: Claims sobre pTau217, NfL, GFAP
├── 2024-2025: Reviews validando eficacia
├── 2025-2026: Decisiones comerciales
```

La pregunta persiste. Los claims cambian.

### Section 2. Operational Unit

```
ACTION
```

La acción es la unidad operativa porque:
- **Verificable** inmediatamente
- **Atribuible** a un actor específico
- **Reproducible** con los mismos inputs
- **Governable** mediante políticas

```
ACTION-000456: SUPPORT CLAIM-000123
├── Actor: AGENT-000789
├── Evidence: [PMID-12345, PMID-67890]
├── Method: literature_review
├── Confidence: 0.92
└── Provenance: modelo, prompt, tool_calls
```

---

## Article III: The Scientific Execution Ledger

### Section 1. The Real Asset

No es el conocimiento.
No es el grafo.
Es el **ledger histórico completo de ejecución científica**.

```
Scientific Execution Ledger
```

Equivalente al historial de commits de Linux, pero para ciencia.

### Section 2. Ledger Structure

Cada entrada registra:

```
ENTRY-000001
├── timestamp: 2026-07-13T18:30:00Z
├── actor: AGENT-00456 (human: RES-00123)
├── action_type: SUPPORT
├── target: QUESTION-000123
├── artifacts: [CLAIM-000789, EVIDENCE-000456]
├── context: PROGRAM-000234
├── method: {
    "model": "claude-3-opus",
    "prompt": "sip_support_v3",
    "tools": ["pubmed_search", "neo4j_query"],
    "code": "atlas/extractor.py@def456"
}
├── confidence: 0.87
├── outcome: ACCEPTED
└── impact: {
    "trust_delta": +0.05,
    "citations": 12,
    "followup_actions": [ACTION-000789]
}
```

### Section 3. Why This is Unreplicable

Con 1M+ entradas:

- **Cannot reverse**: Historia computacionalmente verificada
- **Cannot extract**: Contexto único de cada ejecución
- **Cannot replicate**: Combinación específica de actores/evidencia
- **Cannot falsify**: Blockchain-like provenance
- **Cannot migrate**: Costo de recrear el ledger es prohibitivo

---

## Article IV: QUESTION as Execution Anchor

### Section 1. The Question-Centric Model

```
QUESTION
├── ACTIONS (verificables)
│   ├── ACTION-GEN → HYPOTHESIS
│   ├── ACTION-SUPPORT → CLAIM
│   ├── ACTION-CHALLENGE → CONTRADICTION
│   ├── ACTION-REPLICATE → REPLICATION
│   └── ACTION-REVIEW → REVIEW
├── CLAIMS (derivados)
├── REVIEWS (validaciones)
├── DECISIONS (direcciones tomadas)
└── ARTIFACTS (productos generados)
```

### Section 2. The Stability Hierarchy

| Stability | Unit |
|-----------|------|
| **Highest** | QUESTION (décadas) |
| High | Programs (años) |
| Medium | Claims/Reviews (años) |
| Low | Hypotheses/Papers (décadas) |
| Lowest | Evidence/Predictions (días) |

Los ledger entries apuntan a QUESTIONS, no a claims.

---

## Article V: ACTION as Verification Anchor

### Section 1. The Execution Chain

```
QUESTION-000123
  └── ACTION-000456 → HYPOTHESIS-000789 (confidence: 0.85)
      └── ACTION-000789 → EXPERIMENT-00123 (confidence: 0.92)
          └── ACTION-00123 → RESULTS-00456 (confidence: 0.88)
              └── ACTION-00456 → CLAIM-000789 (confidence: 0.95)
                  └── ACTION-00789 → REVIEW-000123 (confidence: 0.70)
                      └── DECISION-000456 → PUBLISH (human)
```

### Section 2. Verification Without Humans

Actions pueden verificarse automáticamente:

```
IF action.confidence > 0.70 THEN
  - Execute automatically
  - Log to ledger entry
  - Update QUESTION metrics
  - Notify stakeholders

IF action.confidence < 0.40 THEN
  - Flag for human review
  - Pause execution
  - Request intervention
```

---

## Article VI: The Scientific ERP Architecture

### Section 1. Resource Orchestration

```
CoResearcher = Scientific ERP
```

| Resource | Orchestration |
|----------|---------------|
| Humans (RES) | Strategic decisions, escalations |
| Agents (AGENT) | Operational execution |
| Questions | Work programs |
| Actions | Work execution |
| Reviews | Quality control |
| Artifacts | Outputs |

### Section 2. The Execution Flow

```
1. QUESTION proposed/received
2. RESOURCES allocated (humans + agents)
3. ACTIONS executed and logged
4. ARTIFACTS generated
5. REVIEWS performed
6. DECISIONS recorded
7. NEXT QUESTION identified
```

---

## Article VII: Implementation Requirements

### Section 1. Before Any Code

Must define:

- [x] **QUESTION** - Strategic anchor
- [x] **ACTION** - Operational unit
- [x] **LEDGER** - Execution history
- [x] **CONFIDENCE** - Agent decision thresholds
- [x] **ESCALATION** - Human intervention points

### Section 2. The Execution Stack

```
Execution Layer (ACTIONS)
  ↓
Coordination Layer (QUESTIONS + LEDGER)
  ↓
Governance Layer (ONTOLOGY + REVIEWS)
  ↓
Decision Layer (DECISIONS + HUMANS)
```

---

## Article VIII: The Scaling Guarantee

This architecture scales because:

1. **QUESTIONS persist** without human intervention
2. **ACTIONS execute** autonomously with confidence thresholds
3. **LEDGER grows** exponentially but is append-only
4. **HUMANS intervene** only for escalations (<1% of operations)
5. **ONTOLOGY stabilizes** the entire system

---

*Esta constitución establece que CoResearcher es un Scientific Execution Ledger donde cada operación científica verificable queda registrada permanentemente, anclada a preguntas estratégicas, y coordinada por agentes con intervención humana selectiva.*