# Competitive Landscape
## Institutional Infrastructure Mapping

**Version 1.0.0** - Strategic Positioning Analysis  
**Status**: Active Investigation

---

## The Core Question

> **¿Qué espacio institucional sigue vacío?**

Antes de diseñar más arquitectura, debemos identificar con precisión qué necesidad real no está siendo atendida por sistemas existentes.

---

## Evolution Arc

```text
Paper-centric
        ↓
Artifact-centric
        ↓
Activity-centric
        ↓
Agent-centric (CoResearcher target)
```

OSF está entre los dos primeros niveles. CoResearcher salta directamente al cuarto.

---

## Platform Analysis Matrix

| Platform | Coordinates | Fundamental Unit | Main Identifier | Network Effect | Does NOT Coordinate |
|----------|-------------|------------------|-----------------|----------------|---------------------|
| **OSF** | Research lifecycle | Project/container | Node/DOI | Connected artifacts | Agent-native activity, real-time collaboration, immutable activity record |
| **OpenAlex** | Scholarly metadata | Paper/work | OpenAlex ID | Citation graph | Research process, activity provenance, agent coordination |
| **ORCID** | Researcher identity | Person | ORCID iD | Identity linking | Activity coordination, knowledge objects, collaboration workflows |
| **Crossref** | Publication metadata | DOI reference | DOI | Citation linking | Activity graph, researcher provenance (beyond authorship), process tracking |
| **Zenodo** | Research artifacts | File/package | DOI | Dataset versioning | Scientific process, review coordination, hypothesis tracking |
| **GitHub** | Code development | Repository | Repo URL | Collaboration network | Scientific review, claim verification, research activity beyond code |
| **Wikipedia** | Human knowledge | Article | Page title/namespace | Crowdsourced consensus | Scientific provenance, agent contribution, temporal scientific process |
| **OpenReview** | Peer review | Review/comment | Submission ID | Transparent review | Full research lifecycle, artifact coordination beyond papers |

---

## Detailed Platform Analysis

### 1. OSF (Open Science Framework)

**Qué coordina:**
- Preregistration
- Data
- Código
- Materiales
- Preprints
- Publicaciones

**Unidad fundamental:** El "research object" / project container

**Identificador principal:** Node ID + DOI para registros

**Efecto red:** Conecta artefactos dentro de un proyecto de investigación

**Qué NO coordina:**
- Actividad en tiempo real de agentes
- Historial inmutable de decisiones
- Trazabilidad de preguntas → investigación → revisión
- Colaboración híbrida humano-agente
- Consenso evolutivo visible

**Modelo de grafo:**
```
Researcher
    ↓
Dataset
    ↓
Preprint
    ↓
Paper
```

Grafo de **artefactos**, no de **actividad**.

---

### 2. OpenAlex

**Qué coordina:**
- Metadata de literatura académica
- Conceptualización de campos y subcampos
- Citaciones y referencias
- Autores y afiliaciones

**Unidad fundamental:** Trabajo académico (paper)

**Identificador principal:** OpenAlex ID

**Efecto red:** Grafo de conocimiento académico basado en citaciones

**Qué NO coordina:**
- Proceso de investigación
- Hipótesis y preguntas
- Acciones de agentes
- Revisiones y validaciones intermedias
- Actividad exploratoria no publicada

---

### 3. ORCID

**Qué coordina:**
- Identidad de investigadores
- Afiliciones institucionales
- Contribuciones y publicaciones

**Unidad fundamental:** Persona investigadora

**Identificador principal:** ORCID iD

**Efecto red:** Identidad verificable vinculada a publicaciones

**Qué NO coordina:**
- Actividad científica misma
- Preguntas y hipótesis
- Revisiones de pares
- Proceso de investigación
- Colaboración activa

---

### 4. Crossref

**Qué coordina:**
- Metadatos de publicación
- Sistema de citas
- Relaciones entre objetos

**Unidad fundamental:** Publicación con DOI

**Identificador principal:** DOI

**Efecto red:** Enlaces de citación entre publicaciones

**Qué NO coordina:**
- Proceso previo a la publicación
- Datos y código asociados
- Revisión y validación
- Identidad de investigadores en detalle
- Actividad científica exploratoria

---

### 5. Zenodo

**Qué coordina:**
- Almacenamiento de artefactos de investigación
- Versionado de datasets y software
- Asignación de DOIs

**Unidad fundamental:** Archivo/depósito

**Identificador principal:** DOI (Zenodo)

**Efecto red:** Descubrimiento y citación de artefactos

**Qué NO coordina:**
- Proceso de investigación
- Revisiones y comentarios estructurados
- Preguntas de investigación
- Actividad de agentes
- Consenso científico

---

### 6. GitHub

**Qué coordina:**
- Desarrollo colaborativo de código
- Issues y pull requests
- Workflows automatizados
- Versionado distribuido

**Unidad fundamental:** Commit/Repository

**Identificador principal:** URL del repositorio

**Efecto red:** Colaboración entre desarrolladores

**Qué NO coordina:**
- Actividad científica (más allá del código)
- Preguntas y hipótesis científicas
- Revisiones de ciencia
- Trazabilidad de experimentos
- Integración con sistemas académicos

---

### 7. Wikipedia

**Qué coordina:**
- Conocimiento humano estructurado
- Edición colaborativa
- Versionado de artículos
- Consenso comunitario

**Unidad fundamental:** Artículo/wiki page

**Identificador principal:** Título + namespace

**Efecto red:** Consenso a través de edición abierta

**Qué NO coordina:**
- Proceso de descubrimiento científico
- Revisión por pares formal
- Trazabilidad de evidencia
- Actividad de agentes especializados
- Ontología científica formal

---

### 8. OpenReview

**Qué coordina:**
- Revisión por pares transparente
- Discusión de papers
- Decisiones editoriales visibles

**Unidad fundamental:** Submission/review

**Identificador principal:** Submission ID

**Efecto red:** Calidad a través de revisión abierta

**Qué NO coordina:**
- Ciclo de vida completo de investigación
- Preguntas y planes de investigación
- Actividad de agentes
- Metadatos ontológicos
- Integración con artefactos de datos/código

---

## Synthesis: The Empty Space

### Lo que está cubierto:

| Necesidad | Plataforma(s) que la cubre |
|-----------|---------------------------|
| ✅ Identidad investigadores | ORCID |
| ✅ Permanencia artefactos | DOI/Crossref/Zenodo |
| ✅ Gestión proyectos | OSF |
| ✅ Desarrollo colaborativo | GitHub |
| ✅ Metadatos académicos | OpenAlex |
| ✅ Revisión transparente | OpenReview |
| ✅ Almacenamiento datos | Zenodo |

### Lo que NO está cubierto:

| Necesidad | Por qué está vacía | CoResearcher puede llenar |
|-----------|-------------------|--------------------------|
| ❌ Registro de actividad científica | Nadie registra el proceso completo | ✅ Scientific Activity Ledger |
| ❌ Coordinación humano-agente | Sin infraestructura existente | ✅ Agent Actions + Reviews + Decisions |
| ❌ Consenso evolutivo visible | Wikipedia abierta, OpenReview limitado | ✅ Snapshots + Trust scores |
| ❌ Preguntas verificables | Sin identidad propia | ✅ QUESTION-XXXXXX como primitivo |
| ❌ Trazabilidad de dirección cambiada | No existe | ✅ Evidence-driven redirection tracking |
| ❌ Namespace canónico científico | Fragmentación masiva | ✅ Ontological anchoring |

---

## CoResearcher's Unique Territory

```
COMPUTABLE SCIENTIFIC RECORD
```

**No es:**
- Knowledge Graph
- Artifact Repository
- Project Management Tool
- Identity Provider
- Publication Platform

**Es:**
- Ledger de actividad científica verificable
- Coordinación de investigación híbrida
- Historial inmutable de decisiones
- Consenso evolutivo computable

---

## Integration Strategy

### Identificadores desde el día 1:

```text
ORCID    ↔ Researcher identity (RES-XXXXXX)
ROR      ↔ Institution identity (INST-XXXXXX)
DOI      ↔ Artifact permanence (ARTIFACT-XXXXXX)
Zenodo   ↔ Dataset/software permanence
GitHub   ↔ Development provenance
```

### Federar, no inventar

CoResearcher no necesita:
- Identity management (ORCID)
- Storage infrastructure (Zenodo/GitHub)
- Publication pipeline (Crossref/DOI)
- Metadata harvesting (OpenAlex)

CoResearcher necesita:
- Activity coordination layer
- Agent-native protocols
- Scientific consensus machinery
- Canonical namespace enforcement

---

## The Real Competitive Advantage

### No es técnico, es institucional

El valor no está en:
- Mejor LLM
- Mejor UI
- Mejor arquitectura

El valor está en:
- **Network effect de actividad acumulada**
- **Historia inmutable de producción científica**
- **Consenso verificable evolutivo**
- **Reputación trazable por contribución real**

```text
100K claims
+
1M SUPPORT actions
+
300K REPLICATE actions  
+
50K CHALLENGE actions
+
RES/INST identities linked
=
Scientific Coordination Infrastructure
```

---

## Recommendation: Stop Designing, Start Integrating

### No añadir más constituciones

### Crear COMPETITIVE_LANDSCAPE.md ✅ (este documento)

### Para cada plataforma identificar:

1. Qué coordina
2. Cuál es su unidad fundamental
3. Cuál es su identificador principal
4. Cuál es su efecto red
5. Qué NO coordina

### Objetivo:

Identificar qué espacio institucional sigue realmente vacío.

Porque ahora mismo el mayor peligro no es técnico.

Es estar reinventando parcialmente algo que sistemas existentes ya resuelven por separado sin haber identificado todavía **qué pieza del rompecabezas sigue realmente sin dueño**.

---

## The Activity-Centric Innovation

### OSF model (artifact-centric):
```
Plan
  ↓
Execution
  ↓
Outputs
  ↓
Publication
```

### CoResearcher model (activity-centric):
```
Question
  ↓
Investigation
  ↓
Claim
  ↓
Verification
  ↓
Publication
  ↓
Adoption
  ↓
Impact
```

La diferencia es enorme: un grafo de actividad vs un grafo de artefactos.

---

## Próximos pasos

1. Validar que el "Scientific Activity Ledger" es el espacio único realmente vacío
2. Priorizar integraciones con sistemas existentes
3. Definir primitivos mínimos para ocupar ese espacio
4. No construir nada que pueda consumirse de sistemas existentes