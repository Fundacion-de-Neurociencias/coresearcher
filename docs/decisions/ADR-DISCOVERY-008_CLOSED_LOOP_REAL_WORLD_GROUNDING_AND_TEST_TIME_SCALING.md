#ADR-DISCOVERY-008: Closed-Loop Real-World Grounding and Inference-Time Epistemic Scaling

**Version 1.0.0** - Architecture Decision Record  
**Status**: Canonical Standard - Real-World Epistemic Grounding & Search  
**Reference**: Google DeepMind Co-Scientist Real-World (arXiv:2608.26701)

---

## 1. Context and Opportunity

The milestone presented by Google DeepMind in *"Accelerating Scientific Research with Gemini in the Real-World"* (Schmidgall et al., arXiv:2608.26701) establishes two critical scientific lessons for multi-agent research systems:
1. **Real value comes from closing the loop with real-world experiments**: The transition from pure *in-silico* simulation towards tailoring reactor recipes (MXenes, MoS2) in minutes and predicting complex biological phenotypes from sparse wet image data.
2. **Inference-Time Scaling**: Exploring multiple reasoning and search paths during inference outperforms standard frontier models in demanding benchmarks (HealthBench Hard).
3. **Reliability and blind review modules**: The elimination of hallucinations and plagiarism requires specialized audit modules subjected to multi-expert scrutiny.

---

## 2. Architectural Decision

CoResearcher adopts a deep and formal synergy in 3 key components:

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                 ADR-DISCOVERY-008 ARCHITECTURAL TRIAD                       │
├─────────────────────────────────────────────────────────────────────────────┤
│ 1. Inference-Time Epistemic Scaling (Epistemic Tree Search)                 │
│    • Explore K trajectories of hypotheses and restrictions in tree.          │
│    • Select the branch that maximizes the mathematical reduction of Ω and the DV. │
├─────────────────────────────────────────────────────────────────────────────┤
│ 2. Closed-Loop Lab-in-the-Loop Grounding Adapter                            │
│    • Convierte predicciones abstractas en protocolos de laboratorio         │
│      físicos y ajustables a restricciones de reactores / ensayos.           │
│    • Ingesta datos de microscopía, citometría y metabolómica vinculándolos   │
│      a hashes criptográficos SOM.                                           │
├─────────────────────────────────────────────────────────────────────────────┤
│ 3. Multi-Expert Reliability & Hallucination Elimination Auditor             │
│    • Audita deducción por Modus Tollens, coherencia Marr tri-nivel y        │
│      trazabilidad de datos para garantizar cero alucinaciones.              │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 3. Component Specification

### 3.1. Inference-Time Epistemic Scaling
Unlike a simple probabilistic Beam Search on text tokens, **Epistemic Tree Search (ETS)** evaluates complete scientific trajectories:
$$\text{Score}(T) = \mathcal{DV}(T) \times \left(1 + \frac{|\Omega_{\text{excluded}}|}{|\Omega_{\text{total}}|}\right)$$
where hypotheses that increase complexity without excluding volume in the state space are penalized.

### 3.2. Lab-in-the-Loop Protocol Grounding Contract
Defines the `LabProtocolRecipe` schema:
```python
@dataclass
class LabProtocolRecipe:
    recipe_id: str
    target_prediction_id: str
    instrument_type: str  # "CVD_REACTOR" | "SPARSE_IMAGING" | "MASS_SPEC" | "ASSAY_MIXER"
    parameters: Dict[str, Any]
    hardware_constraints: List[str]
    readout_metric: str
    falsification_cutoff: float
```

### 3.3. Multi-Expert Reliability Auditor
Run 4 independent checks:
1. **Modus Tollens Validity**: Strict mathematical deduction without fallacy of affirmation of the consequent.
2. **Marr Tri-Level Non-Confabulation**: Prohibition of confusing implementational measurements with algorithmic processes.
3. **SOM Lineage Integrity**: Validation that all data used has an unaltered SHA-256 hash.
4. **Circularity Prevention**: Verification that the premises do not assume the conclusion as already proven.