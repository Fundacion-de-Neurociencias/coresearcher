# CoResearcher: Scientific Ecosystem Operating System

## ¿Qué es CoResearcher?

**CoResearcher es el Scientific Ecosystem Operating System** - una plataforma modular donde múltiples aplicaciones científicas comparten un núcleo común de conocimiento, workflows y trazabilidad.

No es un gestor bibliográfico. No es un chatbot científico. No es un LIMS ni un ELN. Es un **sistema operativo para la investigación científica asistida por IA**.

## ¿Por qué existe?

La investigación científica necesita tres cosas que los LLMs genéricos no pueden proporcionar:

1. **Trazabilidad completa**: Cada claim, evidencia y hipótesis debe poder rastrear su origen
2. **Razonamiento estructurado**: No búsqueda de información, sino inferencia sobre conocimiento estructurado
3. **Ecosistema compartido**: GeneForge, Medicalia, Neurodiagnoses, Vademecum, EditXT necesitan el mismo núcleo

## Usuario principal

**Biotech startup en fase preclínica**

Equipo pequeño (2-10 investigadores) que necesita:
- Identificar targets emergentes basados en biomarcadores
- Generar hipótesis con evidencia trazada
- Diseñar experimentos sin reinventar la rueda
- Exportar propuestas con provenance completa

Este usuario no tiene acceso a Claude Enterprise ni Google Co-Scientist. Necesita algo más flexible y auditable.

## Workflow estrella

```text
Pregunta científica
    ↓
Revisión literaria multi-fuente (PubMed + OpenAlex + Crossref)
    ↓
Extracción estructurada de Claims y Evidence
    ↓
Detección de knowledge gaps y contradicciones
    ↓
Generación de hipótesis con confianza cuantificada
    ↓
Crítica automática (novedad, suficiencia, alternativas)
    ↓
Ranking Elo de hipótesis
    ↓
Validación por científicos (SUPPORTS/CHALLENGES/REPLICATES)
    ↓
Trust Score y Consensus Level
    ↓
Diseño experimental sugerido
    ↓
Propuesta de proyecto (Specific Aims + Approach)
    ↓
Paquete de provenance exportable
```

## Ventaja competitiva

### Opción C: Scientific Ecosystem OS

Google no tiene ecosistema. Anthropic tampoco.

CoResearcher permite que **GeneForge, Medicalia, Neurodiagnoses, Vademecum y EditXT coexistan sobre el mismo núcleo**, compartiendo:
- Knowledge graph
- Provenance engine
- Routing de modelos
- Workflows reutilizables

Esto significa:
- Menos duplicación de código
- Más coherencia en los resultados
- Mejor mantenibilidad
- Efecto de red interno

## Arquitectura

### Core (Compartido por todas las aplicaciones)

```
Scientific Core
├── Claim (afirmaciones con evidenceScore, createdAt)
├── Evidence (evidencia con qualityScore, sampleSize, pValue)
├── Entity (entidad con canonicalName, aliases)
└── Provenance (trazabilidad completa)

Ecosystem Layer
├── Domain Pack Registry
├── Capability Registry
├── Dependency Engine
└── Project Container

Knowledge Network Layer
├── Claim Registry (CLAIM-000001)
├── Hypothesis Registry (HYP-000001)
├── Evidence Registry (EVID-000001)
├── Scientific Ontology (CSO) v0.1.0
├── Trust Framework (Trust Index 0-100)
├── Researcher Registry (RES-000001)
└── Consensus Engine
```

## Sprint 37: Citable Scientific Objects

CoResearcher now publishes the **Scientific Activity Ledger** as a first-class scientific object via Zenodo.

```text
Evidence
    ↓
Artifacts
    ↓
Scientific Activity Ledger
    ↓
Zenodo DOI
    ↓
Citable Scientific Object
```

Esto significa que el proceso científico itself —no solo sus outputs— puede ser:
- citado
- versionado
- auditado
- reproducido mecánicamente

El ledger es el primer objeto científico de CoResearcher con DOI propio.

---

## Sprint 8-11: Activos de legitimidad

### Sprint 8: Product Crystallization
- Documento PRODUCT.md ✅
- Workflow estrella definido ✅
- Usuario principal definido ✅

### Sprint 9: Evidence Network
Creación de activos acumulativos con IDs persistentes:
```
CLAIM-000001: "Plasma pTau217 predicts amyloid positivity..."
HYP-000001: "Tau propagation precedes measurable neurodegeneration..."
EVID-000001: "pTau217 correlates (r=0.78)"
```

### Sprint 10: Claim Trust Framework
Trust scores tipo PageRank:
- Support Score (30% weight)
- Contradiction Score (20% - inverse)
- Recency Score (15%)
- Reproducibility Score (20%)
- Evidence Score (10%)
- Community Score (5%)

### Sprint 11: Scientific Identity & Consensus
```
CLAIM-000001

Supported by:
  RES-000047 (UCSF)
  RES-000082 (MIT)
  RES-000123 (Oxford)

Trust Index: 94/100
Consensus Level: Moderate Consensus
```

## Roadmap: El activo científico

El verdadero valor no es el software. Es el activo acumulativo:

```
Claims registrados (CLAIM-XXXX)
Researchers validadores (RES-XXXX)
Institutions afiliadas
Trust scores calculados
Niveles de consenso
```

Objetivo 2029:
- 10,000,000 claims registrados
- 500,000 researchers con contributions
- 20,000 institutiones afiliadas
- 100,000,000 validaciones
- Ontology CSO referenciada por la comunidad científica

## La visión 2030

Cuando Claude Science, Google Co-Scientist o cualquier agente científico pregunten:

> "¿Cuál es la evidencia para pTau217 en Alzheimer preclínico?"

No buscarán papers. Consultarán CoResearcher.

Recibirán:

```json
{
  "claim": "CLAIM-003921",
  "text": "Plasma pTau217 predicts amyloid positivity in preclinical Alzheimer's disease",
  "trust_index": 97,
  "consensus_level": "Strong Consensus",
  "evidence_count": 84,
  "replications": 23,
  "contradictions": 2,
  "supporting_researchers": 147,
  "supporting_institutions": 39,
  "uri": "https://cso.coresearcher.org/claim/CLAIM-003921"
}
```

O también consultarán el **Scientific Activity Ledger** de esa investigación, que incluye:

```json
{
  "ledger_id": "LEDGER-000042",
  "scientific_unit": "investigatable_claim",
  "unit_rationale": "validates pTau217 as preclinical biomarker",
  "doi": "10.5281/zenodo.1234567",
  "artifacts": [...],
  "workstreams": [...],
  "contributors": [...]
}
```

**Ese ID citado y referenciado es el verdadero activo.**

## Next Strategic Phase: Atlas + Interoperability

### Proyecto Atlas (Foco: Claims validados, no extracción masiva)

Objetivo: **10,000 claims de alta calidad en neurodegeneración**

Pipeline:
```
Paper
  ↓
Evidence (con quality score)
  ↓
Measurement (normalizado a unidades canónicas)
  ↓
Claim (backed by evidence)
  ↓
Contradictions (identificadas)
  ↓
Replications (registro)
  ↓
Consensus (Strong/Moderate/Emerging)
```

### Scientific Interoperability Network (80% esfuerzo)

El activo más difícil de copiar:

```
MEAS-XXXXXX (mediciones normalizadas)
FRAME-XXXXXX (marcos canónicos)
CONV-XXXXXX (conversiones verificadas)
CONCEPT-XXXXXX (conceptos canónicos)
```

Funciones:
- pg/mL ↔ fg/mL
- SUVR ↔ Centiloid
- MMSE ↔ CDR
- pTau217 ↔ Phosphorylated Tau 217

### CSO v1.0 Public Release

Documentos críticos:
- **CSO.md** - Ontología pública
- **CSO_CONSTITUTION.md** - Epistemología formal
- URIs públicas: `https://cso.coresearcher.org/`

**El activo no es el software. Es la infraestructura científica reconocida por la comunidad.**
