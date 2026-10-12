# Domain Pack Extensions

This document shows how each domain pack extends the universal knowledge infrastructure.

---

## Neurodiagnoses Pack

### Extended Primitives

```python
# Entity Extension
class Biomarker(Entity):
    def __init__(self):
        self.type = "Biomarker"
        self.subtype = "Protein|Biospecimen|Genetic"
        self.threshold = "pathological value"
        self.modality = "CSF|PET|Plasma|MRI"

# Finding Extension for Diagnostics
class DiagnosticFinding(Finding):
    def __init__(self):
        self.predicate_options = [
            "predicts",
            "diagnoses", 
            "differentiates",
            "correlates_with"
        ]
        self.context = {
            "population": "preclinical|MCI|AD|Dementia",
            "clinical_stage": "0|1|2|3",
            "auc": "area under curve",
            "sensitivity": "at threshold",
            "specificity": "at threshold"
        }

# Model Extension for Biomarker Panels
class BiomarkerPanel(Model):
    def __init__(self):
        self.entities = ["biomarker1", "biomarker2", ...]
        self.combined_auc = 0.0
        self.combined_sensitivity = 0.0
        self.combined_specificity = 0.0
```

### Frameworks

```python
ATN_FRAMEWORK = {
    "amyloid": {"PET|CSF": "Aβ42/40 ratio, centiloid"},
    "tau": {"PET|CSF": "pTau181, pTau217, pTau231"},
    "neurodegeneration": {"PET|MRI|Plasma": "NfL, GFAP, tTau"}
}

NIA_AA_2018 = {
    "criteria": "biological definition of AD",
    "evidence_levels": "high|moderate|low supporting"
}
```

---

## GeneForge Pack

### Extended Primitives

```python
# Entity Extension
class Gene(Entity):
    def __init__(self):
        self.symbol = "APP|PSEN1|MAPT|..."
        self.entrez_id = 1234
        self.ensembl_id = "..."
        self.associated_traits = [...]

# Finding Extension for Genetics
class GeneticFinding(Finding):
    def __init__(self):
        self.predicate_options = [
            "associated_with",
            "causes",
            "increases_risk",
            "reduces_risk",
            "mediates"
        ]
        self.context = {
            "odds_ratio": 0.0,
            "rr": 0.0,
            "population_attributable_risk": 0.0,
            "penetrance": 0.0
        }
```

---

## Medicalia Pack

### Extended Primitives

```python
# Entity Extension
class Intervention(Entity):
    def __init__(self):
        self.type = "Drug|Procedure|Behavioral|Lifestyle"
        self.indication = "..."
        self.contraindication = "..."
        self.evidence_grade = "A|B|C|D"

# Finding Extension for Clinical
class ClinicalFinding(Finding):
    def __init__(self):
        self.predicate_options = [
            "treats",
            "prevents",
            "improves",
            "worsens",
            "safe_in"
        ]
        self.context = {
            "nnt": "number needed to treat",
            "nnh": "number needed to harm",
            "number_treated": 0,
            "clinical_significance": "meaningful|marginal"
        }
```

---

## Vademecum Pack

### Extended Primitives

```python
# Entity Extension
class Drug(Entity):
    def __init__(self):
        self.name = "..."
        self.indications = [...]
        self.mechanism = "..."
        self.fda_status = "approved|investigational"

# Framework Extension
class RegulatoryFramework(Framework):
    def __init__(self):
        self.jurisdiction = "FDA|EMA|WHO"
        self.guidelines = "..."
        self.approval_pathway = "..."
```

---

## Separation Principle

**Universal (Core)**: Entity, Measurement, Claim, Evidence, Finding, Model, Prediction, Recommendation

**Domain-Specific (Extensions)**:
- Biomarker = Entity + clinical context
- APOE4 risk = Finding + genetic context  
- ATN framework = Framework + neurodegeneration context
- NNT = Metric + clinical context

This ensures knowledge portability while enabling domain-specific interpretation.