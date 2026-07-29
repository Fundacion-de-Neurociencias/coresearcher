# Sprint 40 — Decision Examples (PILOT)

## Nota previa

Se solicitaron 10 ejemplos. Solo se pudieron extraer **6 ejemplos genuinos** de los 11 items observados manualmente. Los 5 items restantes en la muestra observada no contenían decisiones explícitas (NO en Q1). Proveer 10 ejemplos honestos requeriría fabricar observaciones de items no leídos, lo cual viola las reglas de honestidad científica del proyecto (`NO placeholders`, `All content must be real, verifiable data`).

Los 6 ejemplos que siguen corresponden a items con Q1=YES clasificados tras lectura real del hilo (primeros ~20 comentarios).

---




## Ejemplo 1

**Issue**: MNE-Python #4414 — MRG+4: Epochs metadata  
**URL**: https://github.com/mne-tools/mne-python/pull/4414

**Decision**: Remove the `regress` function from Epochs metadata. The decision was explicit: "It seems like if we remove the `regress` function, then we have already converged, no?" → "ok then :) let's remove regress"

**Evidence used**: 
- DATA: testing rendered output 
- USER_REPORT: developer testing of pandas query integration

**Alternatives considered**: Keep regress vs remove. Discussion about whether regress conflicts with pandas query approach.

**Why it mattered**: This was about whether Epochs metadata would support both pandas-style queries and a separate regress method. The decision to drop regress simplified the API and enabled the feature merge.

---





## Ejemplo 2

**Issue**: MNE-Python #3728 — [MRG+2] adding receptive field module  
**URL**: https://github.com/mne-tools/mne-python/pull/3728

**Decision**: Add receptive field module as smaller focused PR instead of tackling the general encoding model problem. Explicit statement: "we decided tackling the general encoding model problem is probably too much to bite off in one PR".

**Evidence used**:
- LITERATURE: reference to sklearn-style API
- EXPERIMENT: testing the API approach

**Alternatives considered**: General encoding model PR (larger scope) vs receptive field module (smaller, focused PR). Discussion about which was more achievable.

**Why it mattered**: This decision shaped MNE's approach to encoding models for years. The choice to scope down enabled iterative progress rather than a massive risky PR.

---





## Ejemplo 3

**Issue**: nilearn/nilearn #2019 — [ENH] Initial visual reports  
**URL**: https://github.com/nilearn/nilearn/pull/2019

**Decision**: Move HTMLDocument and reporting functionality into a separate `nilearn.reporting` subpackage. Keep core nilearn free of matplotlib dependency.

**Evidence used**:
- USER_REPORT: testing in Jupyter notebooks
- EXPERT_OPINION: GaelVaroquaux and jeromedockes architectural opinions

**Alternatives considered**: Keep reporting code inside `nilearn.plotting` vs separate subpackage. Discussion about importing matplotlib in core.

**Why it mattered**: This was an architectural decision that determined whether reporting features would affect the core API and dependencies. The separate subpackage preserved backward compatibility.

---





## Ejemplo 4

**Issue**: nilearn/nilearn #1766 — switch from papaya to brainsprite  
**URL**: https://github.com/nilearn/nilearn/pull/1766

**Decision**: Switch from papaya to brainsprite for the 3D viewer in `plotting.view_stat_map`.

**Evidence used**:
- DATA: memory savings comparison (papaya ~2MB vs brainsprite ~15kb)
- USER_REPORT: testing rendered output in notebooks
- LITERATURE: reference to other projects using similar approaches

**Alternatives considered**: Keep papaya vs switch to brainsprite. Discussion about iframe sizing and JS dependencies.

**Why it mattered**: Papaya was producing 12MB notebooks. The switch to brainsprite made interactive plotting practical for real scientific workflows.

---





## Ejemplo 5

**Issue**: bids-standard/pybids #369 — REFACTOR: 0.8 [WIP]  
**URL**: https://github.com/bids-standard/pybids/pull/369

**Decision**: Drop grabbit dependency and port its functionality directly into pybids. Maintain pybids independently.

**Evidence used**:
- USER_REPORT: testing compatibility with fitlins and neuroscout

**Alternatives considered**: Keep grabbit dependency vs remove and port. Discussion about where to maintain the code.

**Why it mattered**: This was a fundamental dependency decision. Removing grabbit simplified the pybids roadmap and gave maintainers full control over the core layout API.

---





## Ejemplo 6

**Issue**: bids-standard/pybids #356 — ENH: Dynamically update convolution sampling rate  
**URL**: https://github.com/bids-standard/pybids/pull/356

**Decision**: Dynamically adjust oversampling rate in Convolve based on shortest event duration. Reject exposing the parameter in the BIDS spec API.

**Evidence used**:
- DATA: performance measurements with different sampling rates
- EXPERIMENT: testing regressor outputs for short-duration events

**Alternatives considered**: Three explicit alternatives debated: (1) user calls ToDense manually, (2) auto-upsample inside Convolve, (3) automatic 2-step ToDense inside Convolve.

**Why it mattered**: This determined how pybids would handle short events without breaking spec compliance or degrading performance.

---





## Nota metodológica

Estos 6 ejemplos fueron extraídos de los únicos 11 items que recibieron observación manual real en este piloto. Los 79 items restantes de la muestra de 90 no fueron leídos en detalle y no pueden clasificarse honestamente sin observacion humana completa.
