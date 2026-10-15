#ADR-MECH-001: Mechanism Layer & Biological Programs (Transversal Scientific Primitive)

**Version 1.0.0** - Architecture Decision Record  
**Status**: Canonical Standard - Cross-Repository Epistemic Convergence  
**Ecosystem**: GeneForge · Neurodiagnoses · CoResearcher · Medicalia  
**Domain**: Mechanism Representation & Tri-Level Modeling

---

## 1. Context and Architectural Diagnosis

In the evolution of the open scientific ecosystem (promoted by the Neurosciences Foundation), a critical asymmetry is observed:

- **Neurodiagnoses** evolved from static diagnoses towards:
  $$\text{Disease} \longrightarrow \text{State} \longrightarrow \text{Trajectory} \longrightarrow \text{Biological Program}$$
- **CoResearcher** remained anchored to document ingestion during early stages:
  $$\text{Paper} \longrightarrow \text{Extraction} \longrightarrow \text{Claim} \longrightarrow \text{Evidence}$$

### Claims Limit
Biomedical papers report genes, variants, p-values and individual biomarkers. However, authentic and cumulative scientific knowledge does not reside in isolated statements (*"pTau217 correlates with conversion"*), but in **causal mechanisms and reusable biological programs** that operate across multiple pathologies and phenotypes.

---

## 2. Architectural Decision

### 2.1. Institution of `BiologicalProgram` as a Transversal Primitive
`BiologicalProgram` (and its formal specification `Mechanism`) is defined as a first-order ontological entity shared transversally by:
1. **GeneForge**: Transcriptomic and mutational modeling of expression and splicing programs.
2. **Neurodiagnoses**: Mapping of decompensation of biological programs and pathophysiological stages.
3. **CoResearcher**: Extraction, causal inference, falsification and evolution of discovery trajectories.
4. **Medalia**: Clinical translation, stratification and therapeutic design aimed at modularizing programs.

### 2.2. The Integrated Knowledge Chain
The epistemological architecture of CoResearcher is reorganized under the canonical flow:
$$\text{Evidence} \longrightarrow \text{Claim} \longrightarrow \text{Mechanism / BiologicalProgram} \longrightarrow \text{Trajectory} \longrightarrow \text{Representation}$$

---

## 3. Integration of the Three Marr Levels (`ExplanationLevel`)

To eradicate the endemic confusion in biomedicine between observational descriptions, network algorithms and molecular kinetics, every `Mechanism` or `BiologicalProgram` entity must be explicitly typed according to David Marr's tri-level hierarchy:

```
┌────────────────────────────────────────────────────────────────────────┐
│ COMPUTATIONAL LEVEL                                                    │
│ What is the biological purpose/function? What invariant does it preserve?       │
│ Ej: Homeostasis de proteostasis, depuración de agregados tóxicos.      │
├────────────────────────────────────────────────────────────────────────┤
│ ALGORITHMIC / REPRESENTATIONAL LEVEL                                   │
│ What representations are used and what processes operate on them?       │
│ Ej: Propagación de tau tipo prion-like a lo largo del conectoma neural │
├────────────────────────────────────────────────────────────────────────┤
│ IMPLEMENTATIONAL / PHYSICAL LEVEL                                      │
│ How is it carried out physically and molecularly in the biological substrate?     │
│ Ej: Hiperfosforilación en Thr217, colapso de microtúbulos, fallo LTP.  │
└────────────────────────────────────────────────────────────────────────┘
```

---

## 4. Canonical Structure of `BiologicalProgram`

```yaml
biological_program:
  program_id: "BP-NEURODEGEN-0042"
  name: "Functional Connectome Trans-Synaptic Proteopathy Spreading"
  explanation_level: "ALGORITHMIC"  # COMPUTATIONAL | ALGORITHMIC | IMPLEMENTATIONAL
  computational_objective: "Non-autonomous pathological spread under homeostatic failure"
  key_entities:
    - "Tau / pTau217"
    - "Synaptic vesicles"
    - "Functional connectivity hubs"
  causal_chain:
    - step: 1
      description: "Local proteostatic threshold exceeded in transentorhinal nodes"
    - step: 2
      description: "Activity-dependent trans-synaptic release into synaptic cleft"
    - step: 3
      description: "Retrograde/anterograde uptake by connected vulnerable hub neurons"
  target_diseases:
    - "ALZHEIMER_DISEASE"
    - "FRONTOTEMPORAL_DEMENTIA"
    - "PROGRESSIVE_SUPRANUCLEAR_PALSY"
  cross_disease_transferability: 0.88  # Alto valor de transferencia
  marr_links:
    computational_parent: "BP-HOMEOSTASIS-0001"
    implementational_children: ["BP-TAU-PHOSPHORYLATION-010", "BP-LTP-SYNAPSE-022"]
```

---

## 5. Consequences

### Positive
- Unifies the epistemic vocabulary of `CoResearcher` with `Neurodiagnoses`, `GeneForge` and `Medicalia`.
- Prohibits the mixing of Marr explanatory levels, allowing the decoupling of network propagation logic (algorithmic) from specific biochemical phosphorylation (implementation).
- Facilitates the reuse of biological programs in multiple neurodegenerative diseases, drastically increasing the capacity for scientific transfer.

### Negatives / Trade-offs
- Requires rigorous ontological mapping and enrichment of literature extractors to categorize Marr level.