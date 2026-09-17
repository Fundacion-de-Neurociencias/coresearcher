# ADR-DISCOVERY-005: Objective Discovery Value Metric

**Version 1.1.0** - Architecture Decision Record  
**Status**: Canonical Standard - Scientific Objective Function  
**Domain**: Discovery Optimization & Forgery Metrics

---

## 1. Context and Criticism of Subjectivity

If *Discovery Value* is defined merely as a subjective combination of "apparent novelty + mechanism + representation", it degenerates into an arbitrary score vulnerable to *hype*. 

In rigorous scientific epistemology, the fundamental question is not:
$$\text{What seems new?}$$
Otherwise:
$$\mathbf{What\ survives\ and\ how much\ does it\ compress\ reality?}$$

---

## 2. Architectural Decision: The 4 Objective Pillars of Discovery Value

The **Discovery Value ($DV$)** metric is formally redefined as an objective function based on epistemic survival, compression power (Kolmogorov / Minimum Description Length) and generalizability:

$$DV = w_1 \cdot \mathcal{C}_{disc} + w_2 \cdot \mathcal{F}_{index} + w_3 \cdot \mathcal{K}_{comp} + w_4 \cdot \mathcal{T}_{trans}$$

Where:

### 1. Constraint Discovery ($\mathcal{C}_{disc}$)
- **Have you discovered a non-trivial real constraint?**
- Measures whether the hypothesis/representation irreversibly reduces the space of biologically permissible configurations (e.g. 3D chromatin topology constraints, thermodynamic limits of aggregation, strict functional coupling).

### 2. Falsifiability ($\mathcal{F}_{index}$)
- **Can it be refuted empirically and is it subject to active falsification?**
- Measures the precision of the breaking conditions and the existence of direct empirical evidence capable of demolishing the hypothesis (Popperian discrimination criterion against null and alternative hypotheses).

### 3. Compression ($\mathcal{K}_{comp}$)
- **Do you explain more with less? (Compression Power / Ockham's Razor / Kolmogorov Complexity)**
- Measures the reduction of free parameters and *ad hoc* assumptions. A theory or representation with high compression explains a large volume of disparate empirical phenomena from a minimal and elegant causal core.

### 4. Transferability ($\mathcal{T}_{trans}$)
- **Does it work and remains invariant in different domains or diseases?**
- Measures structural generalizability. A construct like *Biological Programs* achieves an exceptionally high
  * Alzheimer's (AD)
  * Frontotemporal Lobar Degeneration (FTD)
  * Parkinson's disease (PD)
  * Amyotrophic Lateral Sclerosis (ALS)

---

## 3. Comparative Evaluation Matrix

| Dimension | Traditional Scoring (Documentary) | New Discovery Value ($DV$) Objective |
|---|---|---|
| **Focus** | Citation volume and previous consensus | Discovery of unknowns and restrictions |
| **Key Criteria** | How many papers say the same thing? | What falsifiable predictions resist empirical attack? |
| **Explanatory Power** | Local statistical correlation | Causal Invariant Compression ($\mathcal{K}_{comp}$) |
| **Scope** | Specific to a biomarker/disease | Trans-domain transferability ($\mathcal{T}_{trans}$) |

---

## 4. Consequences

### Positive
- Eliminates arbitrariness in the prioritization of hypotheses.
- Directly rewards unifying constructs with high transferability (such as *Biological Programs*).
- Aligns the incentives of research agents with the true economics of scientific discovery.