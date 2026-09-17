# Scientific Primitives Audit
## Universality vs Specificity

---

## Golden Rule

> "**If it does not exist in physics, chemistry, biology, mathematics, economics and engineering, it is NOT core.**"

Every primitive must pass this universality filter.

---

## Table of Primitives - AGGRESSIVE AUDIT

| Primitive | Universal | Core Status | Justification |
|-----------|-----------|-------------|---------------|
| **Question** | ✅ Yes | ✅ CORE | Because? existing in all science |
| **Observation** | ✅ Yes | ✅ CORE | Direct observation is universal |
| **Measurement** | ✅ Yes | ✅ CORE | Measurement is a basic scientific activity |
| **Evidence** | ✅ Yes | ✅ CORE | Evidence supports claims |
| **Claim** | ✅ Yes | ✅ CORE | Atomic affirmation: existing in all science |
| **Finding** | ❌ No | 📦 DOMAIN PACK | In mathematics/theory it does not exist - it is synthesis |
| **Mechanism** | ✅ Yes | ✅ CORE | Universal causal explanation |
| **Model** | ✅ Yes | ✅ CORE | Existing integrative model |
| **Theory** | ✅ Yes | ✅ CORE | Universal explanatory framework |
| **Researcher** | ✅ Yes | ✅ CORE | Research scientist exists everywhere |
| **Biomarker** | ❌ No | 📦 DOMAIN PACK | Biology/medicine specific |
| **Gene** | ❌ No | 📦 DOMAIN PACK | Specific to genetics |
| **Drug** | ❌ No | 📦 DOMAIN PACK | Specific to pharmacology |
| **Patient** | ❌ No | 📦 DOMAIN PACK | Specific to clinical medicine |
| **Trial** | ❌ No | 📦 DOMAIN PACK | Specific to clinical research |

---

## Core Primitives (Universal)

###Question
- Physics: "Why does light bend?"
- Chemistry: "Why is this reaction exothermic?"
- Biology: "Why does APOE4 cause AD?"
- Mathematics: "Is there a pattern here?"
- Economy: "Why is inflation rising?"
- Engineering: "Why did this material fail?"

### Observation
- Physics: "Light bends 1.75 in the eclipse"
- Chemistry: "The pH decreased to 3.2"
- Biology: "APOE4 homozygotes have more plaques"
- Mathematics: "This series converges to π"
- Economy: "Unemployment rose to 8%"
- Engineering: "The temperature reached 150°C"

### Measurement
- Physics: "mass = 9.11e-31 kg"
- Chemistry: "pH = 7.4"
- Biology: "pTau217 = 23.5 pg/mL"
- Mathematics: "error < 0.05"
- Economy: "GDP = 1.2 trillion"
- Engineering: "stress = 250 MPa"

###Evidence
- Physics: "3 independent experiments coincide"
- Chemistry: "spectrum shows peak at 340nm"
- Biology: "p < 0.001 in 5 cohorts"
- Mathematics: "theorem proven by 3 methods"
- Economics: "correlation r = -0.78"
- Engineering: "fatigue confirmed in cycle 10,000"

### Claim
- Physics: "mass → space curvature → orbit"
- Chemistry: "pH → reaction rate → product"
- Biology: "APOE4 → amyloid → deterioration"
- Mathematics: "n → series → convergence"
- Economy: "types → capital → investment"
- Engineering: "temperature → fatigue → failure"

### Finding
- Physics: "mass-orbit relationship (r²=0.99)"
- Chemistry: "pH-product relationship (k=0.45)"
- Biology: "APOE4-plate relationship (OR=3.2)"
- Mathematics: "series converges to π/4"
- Economy: "type-investment relationship (β=-0.3)"
- Engineering: "temperature-failure relationship (N=5000)"

**Note**: Finding seems universal as a "distilled pattern". Review with more examples.

###Mechanism
- Physics: "mass → curvature → geodesic path"
- Chemistry: "pH → concentration → velocity"
- Biology: "stress → pTau217 → amyloid"
- Mathematics: "derivative → integral → function"
- Economy: "types → capital → investment → employment"
- Engineering: "temperature → microcracks → failure"

### Model
- Physics: "Relativity + gravitation model"
- Chemistry: "Kinetic + thermodynamic model"
- Biology: "Amyloid + neuroinflammation model"
- Mathematics: "Statistical model + series"
- Economy: "IS-LM model + growth"
- Engineering: "Fatigue + creep model"

### Theory
- Physics: "General relativity + field theory"
- Chemistry: "Quantum chemistry + kinetics"
- Biology: "Proteostasis + neurodegeneration theory"
- Mathematics: "Number theory + group theory"
- Economics: "Macro theory + micro theory"
- Engineering: "Materials theory + structure theory"

---

## Domain Pack Primitives (Specific)

### Biomarker
- Medicine/biology only
- Use: Observation + Universal Claim

###Gene
- Genetics only
- Use: Entity + Claim universal

###Drug
- Pharmacology only
- Use: Entity + Claim universal

###Patient
- Clinical medicine only
- Use: Entity + Observation

---

## Core API (Simplified) - Finding moved to Domain Pack

```python
# Universal scientific objects (CORE)
QUESTION.create(text, domain)
OBSERVATION.record(entities, values, units)
MEASUREMENT.capture(entity, value, uncertainty)
EVIDENCE.record(source_claims, replication_count)
CLAIM.assert(subject, predicate, object, evidence_refs)
MECHANISM.propose(entities, arrows, type)
MODEL.integrate(mechanisms)
THEORY.unify(models)
RESEARCHER.register(name, institution, expertise)

# Participation actions
SUPPORT(object_id, researcher_id, evidence=None)
CHALLENGE(object_id, researcher_id, reasoning)
REPLICATE(object_id, researcher_id, method)
CONFIRM(object_id, researcher_id, data)
REJECT(object_id, researcher_id, counterevidence)
FORK(object_id, variants)
```

### Domain Pack API (specific)

```python
# Para biología/medicina
Finding.distill_claims(claims) → Finding
Biomarker.register(name, associated_conditions)
Gene.link_to_phenotype(gene, phenotype)
```

---

## Recommended Implementation

1. **Sprint 23A**: Scientific Semantic Compiler (translates human language into objects)
2. **Sprint 23B**: Universal Object Registry (core primitives only)
3. **Sprint 24**: Domain Pack Framework (for biomarkers, genes, drugs)
4. **Sprint 25**: Einstein v2 (operates on real mechanisms)

---

## The Final Identity

CoResearcher is not:
- An AI engine
- A paper system
- A knowledge graph

CoResearcher is:
- **The Scientific Interaction Layer**
- **The Scientific State Machine**
- **The Global Scientific Ledger**

Where scientific knowledge lives with its history of participation.