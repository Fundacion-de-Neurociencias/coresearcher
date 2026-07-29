# Scientific Interaction Protocol (SIP)
## The Standard for Scientific Collaboration

---

## El Protocolo Científico

Como ORCID identifica investigadores y DOI identifica papers, el Scientific Interaction Protocol identifica:

> **El conocimiento científico computable y las acciones que sobre él se realizan.**

---

## Identificadores Canónicos

### External Identifiers (Interoperabilidad)

| Tipo | Ejemplo | Fuente |
|------|---------|--------|
| ORCID | 0000-0002-1825-0097 | ORCID API |
| DOI | 10.1038/s41591-024-xxxxx | Crossref |
| PMID | 38912345 | PubMed |
| PMCID | PMC1234567 | PubMed Central |
| arXiv | 2401.12345 | arXiv API |
| NCT | NCT01234567 | ClinicalTrials.gov |
| Patent | US123456789 | PatentsView |

### CoResearcher Identifiers (Activo Propio)

| Tipo | Patrón | Ejemplo |
|------|--------|---------|
| Question | QUESTION-XXXXXX | QUESTION-000123 |
| Observation | OBS-XXXXXX | OBS-000456 |
| Evidence | EVID-XXXXXX | EVID-000789 |
| Claim | CLAIM-XXXXXX | CLAIM-000321 |
| Mechanism | MECH-XXXXXX | MECH-000114 |
| Model | MODEL-XXXXXX | MODEL-000987 |
| Theory | THEORY-XXXXXX | THEORY-000654 |
| Researcher | RES-XXXXXX | RES-000234 |

### CSO URIs (Identificadores Públicos)

```
https://cso.coresearcher.org/question/QUESTION-000123
https://cso.coresearcher.org/claim/CLAIM-000321
https://cso.coresearcher.org/mechanism/MECH-000114
https://cso.coresearcher.org/hypothesis/HYP-000567
```

---

## Protocolo de Acciones (SIP)

### Formato Estándar

```json
{
  "actor": "RES-000123",
  "action": "SUPPORT|CHALLENGE|REPLICATE|...",
  "object": "CLAIM-000321",
  "provenance": ["doi:10.1038/s41591-024-xxxxx"],
  "timestamp": "2025-01-15T10:30:00Z",
  "evidence": "experimentos replicados en laboratorio X"
}
```

---

## Acciones del Protocolo

### Creación de Objetos

| Acción | Objeto Creado | Descripción |
|--------|---------------|-------------|
| SIP_QUESTION | QUESTION-XXXXXX | Formula pregunta científica |
| SIP_OBSERVE | OBS-XXXXXX | Registra observación |
| SIP_PROPOSE | HYP-XXXXXX | Propone hipótesis |
| SIP_MECHANIZE | MECH-XXXXXX | Propone mecanismo |

### Participación

| Acción | Efecto | Qué actualiza |
|--------|--------|---------------|
| SIP_SUPPORT | +trust | Soporte explícito |
| SIP_CHALLENGE | -trust | Cuestionamiento |
| SIP_REPLICATE | ++trust | Replicación |
| SIP_CONFIRM | +++trust | Confirmación |
| SIP_REJECT | ---trust | Rechazo |
| SIP_FORK | trust_variant | Variante creada |
| SIP_COMMENT | debate_score | Comentario |
| SIP_REVIEW | quality_score | Revisión |

---

## Federación con Estándares Externos

### Researcher ↔ ORCID

```json
{
  "res_id": "RES-000123",
  "orcid": "0000-0002-1825-0097",
  "name": "Juan Pérez",
  "affiliations": ["Universidad X", "Instituto Y"]
}
```

### Claim/Obs/Evidence ↔ DOI

```json
{
  "claim_id": "CLAIM-000321",
  "derived_from": ["doi:10.1038/s41591-024-xxxxx"],
  "evidence_refs": ["pmid:38912345", "pmc:PMC1234567"]
}
```

### External Connector Layer

```
Crossref Connector
DataCite Connector
ORCID Connector
PubMed Connector
OpenAlex Connector
Semantic Scholar Connector
```

---

## Scientific Ledger Structure

```
OBJECT REGISTRY
├── QUESTION/QUESTION-XXXXXX
├── OBS/OBS-XXXXXX
├── CLAIM/CLAIM-XXXXXX
├── MECH/MECH-XXXXXX
├── ACTION/ACTION-XXXXXX
└── RESEARCHER/RES-XXXXXX

PROVENANCE REGISTRY
├── DOI mappings
├── PMID mappings
├── ORCID mappings

TRUST REGISTRY
├── trust_score history
├── consensus evolution
└── reputation scores
```

---

## Protocolo vs Implementación

Esto no es código.

Es un **protocolo abierto** que cualquier sistema puede implementar.

Si GeneForge, Medicalia, Neurodiagnoses o un tercero usan:

```python
sip_support(claim_id, researcher_id, evidence)
sip_challenge(claim_id, researcher_id, reasoning)
sip_replicate(hypothesis_id, researcher_id, method)
```

Entonces están hablando el **Scientific Interaction Protocol**.

---

## Standard + Moat

El protocolo es abierto.

El **Scientific Activity Graph** (acciones + trust scores + consensus) es el activo propiedad.

Incluso si alguien copia el protocolo:
- No tienen el historial de interacciones
- No tienen el trust accumulated
- No tienen el reputation graph

---

## Sprint 23 Roadmap

1. **Congelar protocolo** - este documento constitucional
2. **Scientific Semantic Compiler** - interprete lenguaje natural → SIP
3. **Connector Federation** - ORCID, DOI, Crossref, PubMed
4. **Trust Engine** - calcula scores a partir de acciones
5. **Public URIs** - endpoints públicos para objeciones

---

## La Visión Final

ORCID identificó a los investigadores.

DOI identificó los papers.

CSO URI identificará:

> **El conocimiento científico computable y su evolución a través del tiempo.**

Por primera vez, el conocimiento científico podrá tener:
- Identidad única
- Historial trazable
- Reputación verificable
- Participación medible

Esto convierte a CoResearcher en la **capa de interacción científica de la próxima década**.