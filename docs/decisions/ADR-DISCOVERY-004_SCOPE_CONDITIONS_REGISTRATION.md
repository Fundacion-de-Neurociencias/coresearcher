# ADR-DISCOVERY-004: Mandatory Registration of Scope and Boundary Conditions

**Version 1.0.0** - Architecture Decision Record  
**Status**: Canonical Standard - Boundary Epistemology  
**Domain**: Scientific Validity & Reproducibility

---

## 1. Context

Most erroneous scientific claims fail not because they are completely false, but because they **overgeneralize** beyond their domain of validity. A model that works in young rodents may radically fail in aged human cortical tissue; a valid biomarker in prodromal phases may lose specificity in established dementia.

---

## 2. Architectural Decision

1. **Explicit Scope Definition**:
   - Every result, hypothesis, mechanism or prediction must exhaustively record its **Scope Conditions (`Scope Conditions`)**.
   - The scope record must specify in a bimodal and unambiguous way:
     * **Valid Domain (Where it works)**: Cell types, disease stages, concentration ranges, tissue conditions, demographic covariates or genomic architectures where the relationship holds.
     * **Boundary / Invalidation Domain (Where it does NOT work)**: Breaking limits, excluded phenotypes, drug interactions that nullify the effect or biological contexts where the mechanism collapses.

2. **Border Verification**:
   - Auditing agents must proactively search for the limits of the validity domain by performing tests under boundary conditions (*stress testing the boundaries*).

---

## 3. Consequences

### Positive
- Avoid premature and invalid clinical transfers.
- Makes failure conditions explicit, turning apparent exceptions into new opportunities for theory refinement.
- Direct alignment with the 'S' (Scope) pillar of the TRACES framework.

### Negatives / Trade-offs
- Requires more detailed ontological modeling of tissues, experimental models and clinical contexts in data schemas.