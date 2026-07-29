# ADNI Evidence Quality Report - Sprint 38A.3

**Scientific Observatory Evidence Analysis**

---

## 1. What We Know

### High-confidence findings (ranking 80+):
- **MRI Protocol Standardization**: Foundational methods paper (obs_001) establishes 3T T1/FLAIR/T2 sequences with phantom calibration
- **Cohort Structure**: Three diagnostic categories (normal/MCI/AD) with intentional MCI oversampling (obs_002, obs_001)
- **PACC Validation**: Preclinical cognitive composite validated for early detection (obs_004)
- **Plasma Biomarkers**: Longitudinal studies demonstrate plasma NfL and p-tau trajectories (obs_005, obs_020)

### Moderate-confidence findings (ranking 50-79):
- **Biomarker Cascade**: CSF and plasma markers used in combination (obs_003, obs_004, obs_016)
- **Genetic Risk Modeling**: ApoE genotyping incorporated into progression models (obs_015)
- **Multiple ML Approaches**: Both transfer learning and standalone deep learning achieve ~85% accuracy (obs_003, obs_010)

### Low-confidence findings (ranking <50):
- **Metabolomics Signatures**: Small studies with limited generalizability (obs_014, obs_018)
- **Genomic Copy Number**: Early exploratory work with small samples (obs_008)

---

## 2. Evidence Strength Levels

### Strong Evidence (n=4):
1. obs_001 - MRI methods (ranking: 95)
2. obs_002 - Clinical characterization (ranking: 85)
3. obs_004 - PACC validation (ranking: 80)
4. obs_009 - Imaging review (ranking: 75)

### Moderate Evidence (n=6):
5. obs_005 - Plasma tau (ranking: 75)
6. obs_011 - MCI conversion (ranking: 70)
7. obs_015 - Genetic risk (ranking: 65)
8. obs_020 - Plasma NfL (ranking: 65)
9. obs_019 - CSF signature (ranking: 60)
10. obs_003 - Transfer learning (ranking: 55)

### Suggestive Evidence (n=6):
11. obs_010 - Deep learning prediction
12. obs_014 - Random forest MRI
13. obs_007 - Blood biomarkers
14. obs_018 - Metabolite signatures
15. obs_013 - MRI predictors
16. obs_006 - Neuropathologic correlation

### Preliminary Evidence (n=4):
17. obs_008 - Genomic copy number
18. obs_016 - Multianalyte profiling
19. obs_017 - Epidemiology review
20. obs_012 - ADNI review

---

## 3. Unresolved Uncertainty

### Temporal Uncertainty:
- Optimal timing for biomarker collection unclear
- PACC changes detectable at year 1, plasma tau at year 2, MRI at year 3+
- No standardized protocol for biomarker staging

### Methodological Uncertainty:
- Transfer learning vs standalone deep learning effectiveness not directly compared
- Sample overlap between biomarker studies undefined
- Review papers (obs_009, obs_012, obs_017) synthesize but do not provide new primary evidence

### Clinical Uncertainty:
- Surrogate biomarkers (NfL) correlation with clinical endpoints inconsistent
- Diagnostic accuracy of blood biomarkers not independently validated
- Genetic risk models require external validation

---

## 4. Contradictions Identified

### Contradiction 1 - Methodology Mismatch:
- obs_003 reports 85% accuracy with transfer learning
- obs_010 reports 85% accuracy with standalone deep learning
- No head-to-head comparison available

### Contradiction 2 - Biomarker Timing:
- obs_004: PACC detects changes at 1 year
- obs_005: Plasma tau changes at 2 years
- obs_003: MRI changes at 3+ years
- Optimal sampling window undefined

### Contradiction 3 - Sample Overlap:
- obs_014 (n=120), obs_015 (n=500), obs_018 (n=80) likely use overlapping ADNI subsets
- No cross-validation between biomarker modalities

### Contradiction 4 - Outcome Definition:
- obs_009: Primary outcome = AD dementia diagnosis
- obs_020: Surrogate outcome = plasma NfL levels
- Different endpoints may lead to different conclusions

---

## Metrics Summary

```text
Total observations: 20
High evidence: 4
Moderate evidence: 6
Suggestive evidence: 6
Preliminary evidence: 4
Contradictions found: 4
```

---

## Notes

- Evidence strength based on methodological quality, sample size, longitudinal duration, reproducibility, and clinical impact
- Citations NOT used as primary ranking factor
- All rankings reversible upon new primary evidence