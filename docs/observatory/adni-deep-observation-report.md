# ADNI Deep Observation Report - Sprint 38A.2

**Source**: ADNI public documentation and protocol papers

---

## Observed Facts

### Cohort Design (obs_001, obs_016)
- Age range: 55-90 years
- Three diagnostic categories: normal cognition (~200), MCI (~400), AD dementia (~200)
- Intentional oversampling of MCI cohort

### Follow Up (obs_002, obs_017)
- Duration: 5-10 years
- Visit frequency: annual for normal/AD, biannual for MCI
- Visit codes: baseline, month6, month12, year2, year3, year4, year5

### Biomarker (obs_003, obs_004, obs_018)
- CSF: Aβ42, Aβ40, total-tau, phosphorylated-tau-181
- Plasma: Aβ42/40 ratio, p-tau181, p-tau217, NfL, GFAP
- Genetic: ApoE genotyping required for all participants

### Imaging (obs_005, obs_006, obs_019)
- MRI: T1-weighted MP-RAGE, T2-weighted, FLAIR, functional sequences at 3T with phantom calibration
- PET: florbetapir (amyloid), flortaucipir (tau), FDG (metabolism)

### Assessment (obs_007, obs_008)
- Global: ADAS-Cog, MMSE, CDR-SB, FAQ
- Domain-specific: Rey Auditory Verbal Learning Test, Brief Visuospatial Memory Test

### Outcome (obs_009, obs_015, obs_020)
- Primary: AD dementia diagnosis
- Progression: CDR increase >=1 point OR clinical dementia diagnosis

### Data Model (obs_010, obs_011)
- Tabular CSV files
- Standardized variable names
- Explicit visit codes tied to calendar time points

### Governance (obs_012, obs_013, obs_014)
- Data access requires ADNI Data Use Agreement
- Requires NIH approval
- Exclusion criteria defined

---

## Learned Patterns

### learn_001 (methodological)
**ADNI stratified sampling**: Three diagnostic categories with unequal allocation (200/400/200) for conversion-focused study design.

### learn_002 (clinical)
**Biomarker cascade**: Both CSF and plasma biomarkers collected longitudinally for neurodegeneration tracking cross-validation.

### learn_003 (methodological)
**MRI standardization**: 3T protocol with phantom quality control enables multi-center data pooling.

### learn_004 (methodological)
**PET tracer strategy**: Dual-tracer approach (amyloid + tau) allows comprehensive pathology assessment.

### learn_005 (clinical)
**Assessment structure**: Combination of global and domain-specific cognitive tests captures AD progression patterns.

### learn_006 (outcome)
**Progression definition**: Composite outcome (CDR increase OR diagnosis) increases progression detection sensitivity.

### learn_007 (operational)
**Adaptive follow-up**: Visit frequency varies by diagnosis to optimize resource allocation while maintaining outcome power.

### learn_008 (data)
**Structured visit schema**: Explicit time-coded visits enable automated longitudinal analysis workflows.

### learn_009 (governance)
**Controlled access model**: Formal governance (DUA + NIH approval) protects privacy while enabling research.

### learn_010 (clinical)
**Genetic integration**: ApoE genotyping combined with biomarker thresholds enables precision cohort stratification.

---

## Open Questions

1. Quants los falsos positivos en conversión MCI-AD detectados con solo p-tau181 vs combinado con Aβ42/40?
2. Com queda la correlació entre NfL plasmàtic i atrofia cerebral en els primers 12 mesos?
3. Quina és la variabilitat inter-sit de les mesures de PET entre centres amb calibrat diferent?
4. Com es correlaciona el CDR-SB amb les proves de memòria específiques (RAVLT vs BVMT)?
5. Quins són els criteris exactes d'exclusió per "altres condicions neurodegeneratives"?

---

## Unresolved Contradictions

1. **Biomarker timing mismatch**: CSF collected at subset of visits, plasma at others - pattern unclear.
2. **PET accessibility**: Tracer-specific protocols may miss participants due to availability constraints.
3. **Cognitive battery redundancy**: Multiple memory tests may introduce practice effects not documented.
4. **Genetic stratification**: ApoE genotyping required but not all genetic data may be available for biomarker analysis.

---

## Further Investigation Needed

1. Detailed data dictionary for variable-to-protocol mapping.
2. Site-specific phantom calibration results and variance.
3. Missing data patterns in longitudinal biomarker collection.
4. Inter-rater reliability metrics for CDR-SB scoring.
5. ApoE4 carrier frequency stratified by diagnostic category and its interaction with biomarker trajectories.