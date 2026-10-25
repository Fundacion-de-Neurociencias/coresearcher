# ADR-DISCOVERY-076: Structure-Property-Purpose (SPP) Teleonomic Mechanism Engine

## Status
ACCEPTED / IMPLEMENTED

## Date
2026-10-25

## Context
Traditional quantitative structure-property relationships (QSPR) in materials and computational chemistry model mappings from molecular structure to bulk physicochemical properties ($\text{Structure} \to \text{Property}$). However, in biological mechanisms and active biomimetic systems, properties exist to implement a **teleonomic purpose** ($\text{Structure} \to \text{Property} \to \text{Purpose}$), such as sensing, allosteric gating, force transduction, and homeostatic regulation.

Correlative machine learning fails in this regime because brute-force statistical prediction across massive data is blind to causal biological purposes and competitive physiological microenvironments (e.g., detecting nanomolar $\text{Ca}^{2+}$ signals in the presence of a 10,000-fold excess of background millimolar $\text{Mg}^{2+}$ in human cardiac Troponin C and neuronal synaptotagmin).

## Architectural Decision
We implement **`StructurePropertyPurposeEngine`** in `python/discovery/structure_property_purpose_engine.py`:
1. **Teleonomic Purpose Classification**:
   - Explicitly models purpose classes: `SENSING`, `GATING_ALLOSTERY`, `FORCE_TRANSDUCTION`, `HOMEOSTATIC_REGULATION`, `CATALYTIC_REPAIR`.
2. **Competitive Ionic Discrimination Auditing**:
   - Implements the exact two-ligand competitive Langmuir-Hill isotherm:
     $$\theta_{\text{target}} = \frac{[\text{target}] / K_D^{\text{target}}}{1 + [\text{target}] / K_D^{\text{target}} + [\text{competing}] / K_D^{\text{competing}}}$$
   - Evaluates the selectivity factor $S = K_D^{\text{competing}} / K_D^{\text{target}}$.
   - Enforces that sensory sites maintain basal silence ($\theta_{\text{basal}} \le 0.15$) and achieve robust stimulated activation ($\theta_{\text{stim}} \ge 0.60$) despite competitive background poisoning.
3. **Multiscale Triad Coupling**:
   - Harmonizes the causal biological cascade:
     Molecular Coordination (`BiomacromolecularCoordinationAuditor`) $\to$ Continuum Cytoplasmic Ion Diffusion (`OpenFoamContinuumOracle`) $\to$ Sarcomere Mechanical Force Generation (`IsaacSimGroundingAdapter`).
4. **Court Arbitration**:
   - Integrated into `PhysicalCoherenceCourt` under invariant `STRUCTURE_PROPERTY_PURPOSE_COHERENCE`.

## Consequences
- Elevates CoResearcher from correlative QSPR to causal, biomimetic structure-property-purpose modeling.
- Protects autonomous biomedical discovery pipelines from proposing receptors or sensors that competitively collapse in physiological ionic backgrounds.
