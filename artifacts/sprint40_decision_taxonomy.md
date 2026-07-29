# Sprint 40A — Decision Taxonomy Validation

## Scope

**Dataset**: 11 casos observados manualmente (6 con decisión explícita, 5 sin decisión explícita)

No se expandió la muestra. No se inventaron categorías. Taxonomía 100% emergente.

---

## Casos con decisión explícita (Q1=YES)

### Caso 1: MNE-Python #4414 — Remove regress function

**Decision Object**: Public API

**Alternatives explicitly discussed**:
- KEEP: retain `regress` function alongside new pandas-query approach
- REMOVE: drop `regress` to avoid API conflict

**Chosen Alternative**: REMOVE

**Evidence Used**:
- DATA: testing of rendered output
- USER_REPORT: developer feedback on pandas integration

**Recoverable**: YES

---

### Caso 2: MNE-Python #3728 — Receptive field module as smaller PR

**Decision Object**: Feature Scope

**Alternatives explicitly discussed**:
- LARGE SCOPE: tackle entire encoding model problem in one PR
- SMALL SCOPE: add receptive field module first, defer general solution

**Chosen Alternative**: SMALL SCOPE

**Evidence Used**:
- LITERATURE: sklearn-style API reference
- EXPERIMENT: API testing feedback

**Recoverable**: YES

---

### Caso 3: Nilearn #2019 — Move HTMLDocument to reporting subpackage

**Decision Object**: Repository Structure

**Alternatives explicitly discussed**:
- STAY: keep HTMLDocument inside nilearn.plotting
- MOVE: relocate to separate nilearn.reporting subpackage

**Chosen Alternative**: MOVE

**Evidence Used**:
- USER_REPORT: testing in Jupyter notebooks
- EXPERT_OPINION: maintainer architectural preferences

**Recoverable**: YES

---

### Caso 4: Nilearn #1766 — Switch papaya to brainsprite

**Decision Object**: Dependency Management

**Alternatives explicitly discussed**:
- KEEP: retain papaya library for 3D viewing
- SWITCH: replace with brainsprite library

**Chosen Alternative**: SWITCH

**Evidence Used**:
- DATA: memory comparison (papaya ~2MB vs brainsprite ~15KB)
- USER_REPORT: notebook testing feedback
- LITERATURE: reference to other projects using similar approach

**Recoverable**: YES

---

### Caso 5: PyBIDS #356 — Dynamic oversampling in Convolve

**Decision Object**: Feature Scope / Performance

**Alternatives explicitly discussed** (3 opciones mencionadas explícitamente):
- OPTION 1: user calls ToDense manually before Convolve
- OPTION 2: auto-upsample inside Convolve
- OPTION 3: automatic 2-step ToDense inside Convolve

**Chosen Alternative**: OPTION 3 (auto-adjust based on shortest event duration)

**Evidence Used**:
- DATA: performance measurements
- EXPERIMENT: testing regressor outputs

**Recoverable**: YES

---

### Caso 6: PyBIDS #369 — Drop grabbit dependency

**Decision Object**: Dependency Management

**Alternatives explicitly discussed**:
- KEEP: retain grabbit as external dependency
- REMOVE: port grabbit functionality internally

**Chosen Alternative**: REMOVE

**Evidence Used**:
- USER_REPORT: compatibility testing with fitlins/neuroscout

**Recoverable**: YES

---

## Casos SIN decisión explícita (Q1=NO)

### Caso 7: MNE-Python #2154 — Concatenated epoch plot

**Decision Object**: N/A (no explicit decision found)

Observación: Discusión iterativa de features, bugs, y TODOs. Comentarios técnicos sin converger a una decisión explícita. "Let us decide whether we like it" es expresión de evaluación futura, no decisión actual.

---

### Caso 8: MNE-Python #766 — Trans GUI

**Decision Object**: N/A (no explicit decision found)

Observación: Discusión de implementación, no de alternativas arquitectónicas.

---

### Caso 9: MNE-Python #2676 — EEGLAB reader

**Decision Object**: N/A (no explicit decision found)

Observación: Discusión de implementación, no de alternativas de diseño.

---

### Caso 10: Nilearn #1016 — Surface plotting

**Decision Object**: N/A (no explicit decision found)

Observación: Discusión técnica sin alternativas explícitas.

---

### Caso 11: PyBIDS #451 — List metadata bug

**Decision Object**: N/A (no explicit decision found)

Observación: Bug report y discusión de fix. Sin alternativas de diseño explícitas.

---

## Trade-off Structure Analysis

Propuesta hipótesis emergente:

Las discusiones científicas de ingeniería contienen repetidamente:

1. **Alternative A** vs **Alternative B** (a veces más)
2. **Evidence** (DATA, EXPERIMENT, USER_REPORT, etc.)
3. **Chosen Alternative** (explicitly stated)
4. **Recoverability** (from thread)

Este patrón aparece en 6/6 de los casos con decisión explícita.

Patrón observable: **Resolved Trade-off**

---

## Interpretive Assessment (non-validated)

NOTA: Esta sección NO es evidencia. Es síntesis tentativa.

Los 6 resolved trade-offs parecen estar en dominio de **coordinación del proyecto**, no en decisión científica per se:

- Public API (API design)
- Feature Scope (roadmap)
- Repository Structure (organization)
- Dependency Management (maintenance)

Los 5 casos sin decisión explícita son principalmente discusiones técnicas/iterativas.

Esto sugiere que los trade-offs más observables pueden ser unidades de coordinación más que unidades de ciencia.
</tool_call>