#ADR-DISCOVERY-007: Constraint-Led Multi-Agent Discovery Teams

**Version 1.0.0** - Architecture Decision Record  
**Status**: Canonical Standard - Epistemic Multi-Agent Architecture  
**Domain**: Scientific Discovery, Multi-Agent Systems, Formal Epistemology

---

## 1. Context and Diagnosis

Common multi-agent architectures in scientific AI (including "Google Teamwork"-style patterns) are typically implemented as free conversational discussion:
```text
Agent A (Proposer) ──► propone texto
Agent B (Critic)   ──► critica texto
Agent C (Refiner)  ──► mejora texto
```
This approach suffers from three fundamental limitations:
1. **Debate not anchored to restrictions**: The agents debate "opinions" or "rhetorical style", falling into collective hallucination.
2. **Lack of specific epistemological functions**: There is no formal specialization between those who discover invariants, those who model biological mechanisms, those who formulate deducible predictions and those who audit by *Modus Tollens*.
3. **Lack of Ledger Memory**: Memory is stored in volatile chat histories rather than immutable records of decisions, refuted alternatives, and constraints used.

---

## 2. Maximum Constitutional Declaration

> **CoResearcher is NOT a response system.**  
> **CoResearcher is NOT a bibliographic search engine.**  
> **CoResearcher is NOT a hypothesis generator.**  
> **CoResearcher IS a system of progressive reduction of the space of possible scientific states (\(\Omega\)) through auditable constraints, predictions and falsifications.**

---

## 3. Architectural Decision: The Canonical Team of 9 Epistemic Agents

Free conversational debate is prohibited. Agents operate exclusively as **typed epistemological functions** on formal scientific objects:

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                 CONSTRAINT-LED MULTI-AGENT DISCOVERY TEAM                   │
├─────────────────────────────────────────────────────────────────────────────┤
│ 1. Constraint Miner Agent                                                   │
│    • Ingesta: Literatura, datos y evidencia empírica.                       │
│    • Función: Identifica invariantes, imposibilidades y condiciones         │
│      necessary/sufficient in the state space.                       │
│    • Prohibition: DOES NOT generate hypotheses. Just discover restrictions.         │
│    • Salida: Constraint (CONST-XXXXXX)                                      │
├─────────────────────────────────────────────────────────────────────────────┤
│ 2. Biological Program Mapper Agent                                          │
│    • Ingesta: Hallazgos moleculares y fenotípicos.                          │
│    • Función: Mapea a mecanismos biológicos causales reutilizables.         │
│    • Salida: BiologicalProgram (BP-XXXXXX)                                   │
├─────────────────────────────────────────────────────────────────────────────┤
│ 3. Hypothesis Generator Agent                                               │
│    • Ingesta: Constraints + Biological Programs + Evidencia conocida.       │
│    • Function: Formulates conjectural hypotheses compatible with the invariants│
│    • Strict Prohibition: You may NOT read or access your own           │
│      evaluaciones o auditorías posteriores (independencia Generator/Verifier│
│    • Salida: Hypothesis (HYP-XXXXXX)                                        │
├─────────────────────────────────────────────────────────────────────────────┤
│ 4. Alternative Generator Agent (Mandato ADR-003)                            │
│    • Ingesta: Hypothesis candidata.                                         │
│    • Función: Genera obligatoriamente un mínimo de 4 alternativas rivales   │
│      (Null, Competing Mechanism, Orthogonal Explanation, Technical Artifact)│
│    • Salida: AlternativeHypothesis[]                                        │
├─────────────────────────────────────────────────────────────────────────────┤
│ 5. Marr Classifier Agent                                                    │
│    • Ingesta: Hypothesis y sus componentes.                                 │
│    • Función: Clasifica en COMPUTATIONAL, ALGORITHMIC o IMPLEMENTATIONAL.   │
│      Audita y bloquea mezclas o errores de categoría (ej. confundir un      │
│      biomarcador correlacional con un proceso mecanístico).                 │
│    • Salida: MarrClassificationAudit                                        │
├─────────────────────────────────────────────────────────────────────────────┤
│ 6. Prediction Engine Agent                                                  │
│    • Ingesta: Hypothesis + Supuestos Auxiliares de Lakatos (A_i).           │
│    • Función: Transforma la conjetura en reglas formales deducibles:        │
│      ((H ∧ A_1 ∧ ... ∧ A_n) ⟹ P).                                          │
│    • Salida: FormalImplication (IMP-XXXXXX)                                 │
├─────────────────────────────────────────────────────────────────────────────┤
│ 7. Popper Auditor Agent                                                     │
│    • Ingesta: FormalImplication + Resultado empírico observado (P o ¬P).    │
│    • Función: Aplica Modus Tollens formal: ((H ∧ A) ⟹ P) ∧ ¬P ⟹ (¬H ∨ ¬A).  │
│      Determines whether the fault of falsification falls on the nucleus H or on A_i.      │
│    • Prohibition: Zero evaluation using natural language or fuzzy LLM.   │
│    • Salida: ModusTollensResult                                             │
├─────────────────────────────────────────────────────────────────────────────┤
│ 8. Scope Auditor Agent (Mandato ADR-004)                                    │
│    • Intake: Hypothesis that has survived falsification.                 │
│    • Function: Defines the valid domain and biological break boundaries.│
│    • Salida: ScopeCondition                                                 │
├─────────────────────────────────────────────────────────────────────────────┤
│ 9. Discovery Value Auditor Agent (Mandato ADR-005 & ADR-006)                │
│    • Ingesta: Estado del espacio de estados Ω y trayectoria epistémica.     │
│    • Función: Calcula el DV descompuesto y el CDV real (|Ω_exc| / |Ω_tot|). │
│      Blocks the promotion of hypotheses that increase complexity without      │
│      reducir el espacio de incertidumbre.                                   │
│    • Salida: DecomposedDiscoveryValueAudit                                  │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 4. New Fundamental Object: `DiscoveryCampaign`

The persistent science campaign structure is introduced:

```python
@dataclass
class DiscoveryCampaign:
    campaign_id: str
    question: str
    target_state_space: StateSpaceOmega
    constraints: List[Constraint]
    biological_programs: List[BiologicalProgram]
    hypotheses: List[Hypothesis]
    alternatives: List[Hypothesis]
    predictions: List[FormalImplication]
    experiments: List[Dict[str, Any]]
    falsifications: List[ModusTollensResult]
    trajectories: List[TrajectoryStep]
    discovery_value: float
    iteration_count: int
    max_iterations: int
    converged: bool
    ledger_entries: List[CampaignLedgerEntry]
```

---

## 5. Immutable Memory in `CampaignLedger`

Each agent is required to register their artifacts in a persistent ledger:
* **`DECISION`**: Ontological modifications or hypothesis promotions.
* **`REJECTED_ALTERNATIVE`**: Rival hypotheses discarded with their formal counterexample.
* **`FAILED_PREDICTION`**: Empirical predictions not met ($\neg P$).
* **`CONSTRAINT_USED`**: Invariance constraints applied to bound $\Omega$.

---

## 6. Consequences

### Positive
- Eliminates circular debates between LLMs; each agent has a mathematical and formal interface.
- The falsification is executed in a pure deductive way (Modus Tollens), protecting the Lakatosian integrity of the auxiliary assumptions.
- Allows long-term autonomous campaigns (10 to 100+ iterations) aimed at reducing the $\Omega$ state space.

### Negatives / Design Restrictions
- Requires that all generated hypotheses include auxiliary assumptions and predictions formalizable into deducible predicates.