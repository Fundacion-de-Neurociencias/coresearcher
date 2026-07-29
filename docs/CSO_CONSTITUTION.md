# CoResearcher Scientific Ontology (CSO) Constitution

**Version 0.1.0** - Epistemological Foundation

---

## Article I: The Nature of Scientific Knowledge

### Section 1. Observation

An **Observation** is a raw measurement reported in scientific literature without interpretation.

Examples:
- "pTau217 = 0.34 pg/mL in plasma"
- "SUVR = 1.42 in precuneous cortex"
- "Amyloid PET positive"

Observations are factual, measurable, and directly reported.

### Section 2. Evidence

**Evidence** is an observation with statistical or methodological backing that supports or contradicts a claim.

Requirements:
- Must have sample size (n ≥ 1)
- Must have quality score (0.0-1.0)
- Must be traceable to publication

Types of evidence:
- **Observational** (cohort, case-control)
- **Experimental** (RCT, preclinical)
- **Meta-analytic** (systematic review, meta-analysis)

### Section 3. Claim

A **Claim** is an assertion that can be evaluated as true, false, or uncertain based on evidence.

Format: `"[Entity] [Relationship] [Value] in [Context]"`

Examples:
- "pTau217 predicts amyloid positivity in cognitively unimpaired individuals"
- "APOE4 increases Alzheimer risk by 3-15x depending on population"

A claim is NOT:
- ❌ A hypothesis (testable prediction)
- ❌ An observation (raw measurement)
- ❌ A conclusion (interpretation)

A claim IS:
- ✅ A statement backed by evidence
- ✅ Falsifiable
- ✅ Comparable to other claims

### Section 4. Hypothesis

A **Hypothesis** is a proposed explanation that derives from claims but extends beyond current evidence.

Format: `"[Mechanism] explains [Phenomenon]"`

Example:
- "Tau propagation precedes measurable neurodegeneration in APOE4 carriers"

Hypotheses generate predictions, not just describe observations.

---

## Article II: Trust and Validation

### Section 1. Trust Index

The **Trust Index** (0-100) evaluates claim reliability across six dimensions:

| Dimension | Weight | Definition |
|-----------|--------|------------|
| Support Score | 30% | Number and quality of supporting papers |
| Contradiction Score | 20% | Inverse of contradicting papers |
| Recency Score | 15% | Age-adjusted evidence strength |
| Reproducibility | 20% | Independent replications |
| Evidence Quality | 10% | Average quality of supporting evidence |
| Community Score | 5% | Researcher endorsements |

Trust Index ≥ 80: **Strong consensus candidate**
Trust Index ≥ 50: **Preliminary support**
Trust Index < 50: **Unvalidated claim**

### Section 2. Consensus Levels

**Strong Consensus** (TI ≥ 90, 50+ researchers, 20+ institutions)
- Multiple high-quality studies agree
- Minimal contradiction
- Widely accepted by community

**Moderate Consensus** (TI ≥ 80, 20+ researchers, 10+ institutions)
- Good evidence base with some variation
- Minor contradictions resolved

**Emerging Consensus** (TI ≥ 70, 5+ researchers)
- Initial evidence accumulation
- Active investigation ongoing

### Section 3. Contradiction Resolution

Two claims contradict when they cannot both be true.

Resolution process:
1. Evidence comparison (quality, recency, sample)
2. Methodology review
3. Population stratification
4. Consensus declaration

---

## Article III: Interoperability

### Section 1. Measurement Normalization

All measurements must be stored in canonical units:

| Entity Type | Canonical Unit |
|-------------|---------------|
| Protein biomarkers | fg/mL |
| Nucleic acids | copies/mL |
| PET ratios | SUVR |
| Cognitive scores | native scale or Centiloid |

Conversion confidence must be recorded.

### Section 2. Framework Translation

Frameworks must be explicitly linked to standard ontologies:

| Framework | Maps To |
|-----------|---------|
| ATN | NIA-AA Research Framework |
| MMSE | Cognitive assessment standard |
| CDR | Dementia severity standard |
| HGVS | Genetic variant standard |

---

## Article IV: Identity and Contribution

### Section 1. Researcher Identity

Each validator receives a persistent Researcher ID: `RES-XXXXXX`

Contributions:
- SUPPORTS claim
- CHALLENGES claim  
- REPLICATES claim
- EXTENDS claim

Reputation scores (0-100) track contribution quality.

### Section 2. Institutional Endorsement

Institutions (INST-XXXXXX) can endorse claims collectively through researcher affiliations.

---

## Article V: Versioning and Evolution

### Section 1. Ontology Versions

- v0.x: Alpha - experimental frameworks
- v1.x: Beta - community reviewed
- v2.x: Stable - widely adopted

### Section 2. Claim Evolution

Claims can evolve through consensus:
- Claim status changes (unvalidated → supported)
- Evidence added/removed
- Trust recalculated

All changes are versioned and auditable.

---

*This constitution defines the epistemological foundation for scientific knowledge representation. Changes require community review.*