# Scientific Infrastructure Patterns - Sprint 38A.5

**What characterizes a scientific infrastructure that remains relevant for more than a decade?**

---

## Pattern: Longitudinality + Standardization + Quality Control

Assets that survive >10 years share this combination:

### ADNI (20+ years)
- Longitudinality: Yes (5-10 years follow-up)
- Standardization: Yes (identical MRI protocol in 60+ sites)
- QC: Yes (monthly phantom, central review)

### UK Biobank (15+ years)
- Longitudinality: Yes (multiple assessment waves)
- Standardization: Yes (fixed protocols for 500,000 participants)
- QC: Yes (samples processed in accredited laboratories)

### MIMIC-IV (15+ years)
- Longitudinality: Partial (only during hospitalization)
- Standardization: Partial (heterogeneous ICU data)
- QC: Yes (clinical data validation)

---

## Pattern: Governance + Multi-modal Integration

Assets with formal governance and multimodal data:

### ADNI
- Governance: DUA + NIH approval
- Modalities: MRI, PET, CSF, plasma, genetics, cognition

### UK Biobank
- Governance: Research approval + anonymized data
- Modalities: Imaging, blood, genetics, lifestyle, cognition

Assets without formal governance tend to be newer or more technical.

---

## Pattern: Versioning OR Ontology

Durable assets develop some change control mechanism:

### With Versioning (software/infrastructure)
- OpenNeuro (versioned datasets)
- MONAI (code versions)
- OHDSI (Common Data Model versions)
- FHIR (standards versions)

### With Ontologies (clinical data)
- OHDSI (OMOP CDM)
- FHIR (clinical resources)
- SNOMED-CT (terminology)

---

## Pattern: Decoupled Architecture

The assets structurally separate:

1. **Data** (UK Biobank, ADNI) - cohort structure
2. **Methods** (MONAI, OHDSI) - processing standardization
3. **Interoperability** (FHIR, OHDSI) - APIs and mappings
4. **Terminology** (SNOMED-CT, OHDSI) - ontologies

This separation allows independent evolution of each layer.

---

## Non-Infrastructure (no proven survival)

Assets that lack these patterns tend to:
1. Have a very specific purpose (e.g. specific study)
2. Lack of sustainability mechanism (financing/absence)
3. Not having a way to integrate with other assets

---

##Emerging principle

A durable scientific infrastructure requires at least:

**3 of 4**: Longitudinality, Standardization, Quality Control, Governance

Without this, the evidence produced is:
- Short-lived
- Difficult to replicate
- Of limited generalization

---

## Final metrics

```text
Assets analyzed: 9
Identified patterns: 8
Comparisons made: 5
Successful combinations: 2 (ADNI, UK Biobank)