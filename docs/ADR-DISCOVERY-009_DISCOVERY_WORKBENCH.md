#ADR-DISCOVERY-009: Discovery Workbench & Architecture Freeze

**Version 1.0.0** - Architecture Decision Record  
**Status**: Canonical Standard - Unified Epistemic Object & Architecture Freeze  
**Domain**: Scientific Discovery, Discovery Workbench, Epistemic Orchestration

---

## 1. Context and Diagnosis

As CoResearcher incorporated modules of epistemological rigor (Constraints, PopperEngine, EpistemicTrajectories, BiologicalPrograms, Marr, InferenceScaling, LabInTheLoop), the system was at risk of becoming a fragmented collection of components.

Inspired by the operational simplicity of *Rosalind* from OpenAI (*"move from a research question to evidence"*), but providing it with a rigorous formal epistemology, **`DiscoveryWorkbench`** is created.

The researcher is not interested in isolated pieces: he is interested in his **Research Question** and the resulting **State of Discovery**.

---

## 2. Architectural Decision: The Unifying Object `DiscoveryWorkbench`

`DiscoveryWorkbench` is established as the first level unified structure:

```python
@dataclass
class DiscoveryWorkbench:
    workbench_id: str
    question: ResearchQuestion
    campaign: DiscoveryCampaign
    constraint_ledger: List[Constraint]
    biological_programs: List[BiologicalProgram]
    hypothesis_space: List[RivalHypothesis]
    prediction_space: List[FormalImplication]
    experiments: List[LabProtocolRecipe]
    evidence: List[Dict[str, Any]]
    audits: List[ModusTollensResult]
    trajectories: List[TrajectoryStep]
    final_state: DiscoveryState
```

---

## 3. The Unified Epistemic Circuit

All research in CoResearcher flows through the 11-step deterministic loop:

```text
Research Question
↓
Constraints
↓
Biological Programs
↓
Hypotheses
↓
Alternative Hypotheses (>= 4 rivales obligatorios)
↓
Predictions ((H ∧ A) ⟹ P)
↓
Experiments (Recetas de Laboratorio / Ensayos)
↓
Evidence (Hashes criptográficos SOM)
↓
Falsification (Modus Tollens)
↓
Epistemic Trajectories (Poda de Ω)
↓
Discovery State (DV & CDV matemáticos)
```

---

## 4. Architecture Freeze Protocol

> **FREEZE MANDATE**:
> After the promulgation of ADR-DISCOVERY-009, the addition of new ADRs and new abstraction layers is strictly **FROZEN**.
> Development should focus exclusively on empirical execution and validation of **Real Discovery Campaigns** demonstrating that the system discovers invariant biological constraints that a traditional literature search cannot find.