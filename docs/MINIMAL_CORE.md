# Minimal Core
## Irreducible Primitives for CoResearcher

**Version 2.0.0** - Researcher-Centric Model  
**Status**: Constitutional Document - Core Foundation

---

## The Single Question

> **¿Qué objetos son irreductiblemente necesarios para que un investigador obtenga trazabilidad completa hoy?**

---

## The Answer - 3 Primitive Objects (3, no 4)

### 1. QUESTION

La unidad estratégica más simple que permite coordinación.

```json
{
  "question_id": "QUESTION-000001",
  "text": "What blood biomarkers predict Alzheimer's disease?",
  "ontology_path": "Science/Medicine/Neurology/Alzheimer's Disease/Biomarkers",
  "created_by": "ORCID-0000-0002-1825-0097",
  "timestamp": "2026-07-13T00:00:00Z"
}
```

**Why irreducible**: Sin preguntas, no hay dirección científica.

---

### 2. ACTION

La unidad operativa más simple que puede verificarse.

**Incluye revisiones, decisiones y replicaciones.**

```json
{
  "action_id": "ACTION-000001",
  "type": "REVIEW_VALIDATION",  // o GENERATE_HYPOTHESIS, o EXTRACT_CLAIM, etc.
  "actor": "AGENT-CLAUDE-001",
  "target": "QUESTION-000001",
  "method": {
    "model": "claude-3-opus",
    "prompt": "review_scientific_claim_v2",
    "tools_used": ["pubmed_search", "zenodo_query"]
  },
  "confidence": 0.85,
  "outcome": "ACCEPTED",
  "timestamp": "2026-07-13T00:05:00Z"
}
```

**Types of ACTION**:
- `GENERATE_HYPOTHESIS`
- `EXTRACT_CLAIM`
- `REVIEW_VALIDATION` (formal review)
- `REVIEW_CHALLENGE` (challenge)
- `REVIEW_REPLICATE` (replication attempt)
- `DECIDE_PUBLISH` (publication decision)
- `TAKE_BLOOD_SAMPLE` (wet lab action)
- `OBTAIN_CONSENT` (ethical approval)
- `STATISTICAL_ANALYSIS` (data analysis)

**Why irreducible**: Sin acciones verificables, no hay trabajo científico trazable.

---

### 3. ARTIFACT

La salida más simple que puede publicarse.

```json
{
  "artifact_id": "ART-000001",
  "type": "PREPRINT",
  "question": "QUESTION-000001",
  "actions": ["ACTION-000001", "ACTION-000002", "ACTION-000003"],
  "doi": "10.5281/zenodo.12345678",
  "timestamp": "2026-07-13T00:10:00Z"
}
```

**Why irreducible**: Sin artefactos publicables, no hay resultado útil.

---

## The Scientific Intent Model

### What Researchers Actually Think:

```
Tengo una pregunta
  ↓
Lanzo agentes
  ↓
Recibo resultados
  ↓
Valido
  ↓
Escribo
  ↓
Publico
```

### What CoResearcher Makes Visible:

```
QUESTION-000001
  ↓
ACTION-000001 (generate)
ACTION-000002 (extract)
ACTION-000003 (review)
  ↓
ART-000001 (preprint)
```

---

## Infrastructure Agnosticism

### GitHub is Invisible

Los investigadores no ven:
- Issues, workflows, PRs

Los investigadores ven:
- Preguntas en su espacio de trabajo
- Acciones registradas automáticamente
- Artefactos publicados con DOI

El backend puede ser:
- ✅ GitHub (hoy)
- ✅ GitLab (mañana)
- ✅ Notion (alternativa)
- ✅ Local filesystem (offline)

---

## The Free Starting Stack

| Purpose | Free Tool | But Could Be |
|---------|-----------|--------------|
| Identity | ORCID | Email, any identifier |
| Questions | GitHub Issue | Any todo system |
| Actions | GitHub Actions | Any execution log |
| Artifacts | Zenodo | Any DOI system |
| Versioning | Git | Any versioning |
| Collaboration | GitHub Mentions | Slack, Email |

---

## The First Sprint Reality

```bash
# What we build:
1. Template repository with question/issue structure
2. Actions that log to questions automatically
3. Artifact publishing workflow
4. Metadata extraction from ORCID/GitHub/Zenodo

Total: ~500 lines of workflow + templates
Cost: $0
Value: Complete scientific traceability
```

---

## The One Week Test

Si un investigador puede pasar de:

```
Pregunta → Agent work → Preprint publicado
```

con trazabilidad completa en una semana, el modelo funciona.

Si no puede, ninguna constitución salva el proyecto.

---

*Este documento define el núcleo irreductible desde la perspectiva del investigador. Todo lo demás es implementación.*