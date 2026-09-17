#CompetitiveLandscape
## Institutional Infrastructure Mapping

**Version 1.0.0** - Strategic Positioning Analysis  
**Status**: Active Investigation

---

##The Core Question

> **What institutional space is still empty?**

Before designing further architecture, we must identify precisely what real need is not being served by existing systems.

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

OSF is between the first two levels. CoResearcher jumps right into the room.

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

**What coordinates:**
- Preregistration
- Data
- Code
- Materials
- Preprints
- Publications

**Fundamental unit:** The "research object" / project container

**Primary identifier:** Node ID + DOI for records

**Network effect:** Connect artifacts within a research project

**What does NOT coordinate:**
- Real-time activity of agents
- Immutable decision history
- Question traceability → investigation → review
- Hybrid human-agent collaboration
- Visible evolutionary consensus

**Graph model:**
```
Researcher
    ↓
Dataset
    ↓
Preprint
    ↓
Paper
```

Graph of **artifacts**, not **activity**.

---

### 2. OpenAlex

**What coordinates:**
- Academic literature metadata
- Conceptualization of fields and subfields
- Citations and references
- Authors and affiliations

**Fundamental unit:** Academic work (paper)

**Primary identifier:** OpenAlex ID

**Network effect:** Academic knowledge graph based on citations

**What does NOT coordinate:**
- Research process
- Hypotheses and questions
- Agent actions
- Intermediate reviews and validations
- Unpublished exploratory activity

---

### 3. ORCID

**What coordinates:**
- Identity of researchers
- Institutional affiliations
- Contributions and publications

**Fundamental unit:** Research person

**Primary identifier:** ORCID iD

**Network effect:** Verifiable identity linked to publications

**What does NOT coordinate:**
- Scientific activity itself
- Questions and hypotheses
- Peer reviews
- Research process
- Active collaboration

---

### 4. Crossref

**What coordinates:**
- Post metadata
- Appointment system
- Relationships between objects

**Fundamental unit:** Publication with DOI

**Primary identifier:** DOI

**Network effect:** Citation links between publications

**What does NOT coordinate:**
- Pre-publication process
- Associated data and code
- Review and validation
- Identity of researchers in detail
- Exploratory scientific activity

---

### 5. Zenodo

**What coordinates:**
- Storage of research artifacts
- Versioning of datasets and software
- DOI assignment

**Fundamental unit:** Archive/repository

**Primary identifier:** DOI (Zenodo)

**Network effect:** Discovery and citation of artifacts

**What does NOT coordinate:**
- Research process
- Structured reviews and comments
- Research questions
- Agent activity
- Scientific consensus

---

### 6. GitHub

**What coordinates:**
- Collaborative code development
- Issues and pull requests
- Automated workflows
- Distributed versioning

**Fundamental unit:** Commit/Repository

**Primary identifier:** Repository URL

**Network effect:** Collaboration between developers

**What does NOT coordinate:**
- Scientific activity (beyond the code)
- Scientific questions and hypotheses
- Science Reviews
- Experiment traceability
- Integration with academic systems

---

### 7. Wikipedia

**What coordinates:**
- Structured human knowledge
- Collaborative editing
- Versioning of articles
- Community consensus

**Fundamental unit:** Article/wiki page

**Primary identifier:** Title + namespace

**Network effect:** Consensus through open editing

**What does NOT coordinate:**
- Scientific discovery process
- Formal peer review
- Evidence traceability
- Activity of specialized agents
- Formal scientific ontology

---

### 8. OpenReview

**What coordinates:**
- Transparent peer review
- Discussion of papers
- Visible editorial decisions

**Fundamental unit:** Submission/review

**Primary identifier:** Submission ID

**Network effect:** Quality through open review

**What does NOT coordinate:**
- Complete research life cycle
- Research questions and plans
- Agent activity
- Ontological metadata
- Integration with data/code artifacts

---

## Synthesis: The Empty Space

### What's covered:

| Need | Platform(s) that covers it |
|-----------|---------------------------|
| ✅ Identity researchers | ORCID |
| ✅ Permanence artifacts | DOI/Crossref/Zenodo |
| ✅ Project management | OSF |
| ✅ Collaborative development | GitHub |
| ✅ Academic metadata | OpenAlex |
| ✅ Transparent review | OpenReview |
| ✅ Data storage | Zenodo |

### What is NOT covered:

| Need | Why is it empty | CoResearcher can fill |
|-----------|--------|--------------------------|
| ❌ Scientific activity record | Nobody records the entire process | ✅ Scientific Activity Ledger |
| ❌ Human-agent coordination | No existing infrastructure | ✅ Agent Actions + Reviews + Decisions |
| ❌ Visible evolutionary consensus | Open Wikipedia, Limited OpenReview | ✅ Snapshots + Trust scores |
| ❌ Verifiable questions | Without own identity | ✅ QUESTION-XXXXXX as primitive |
| ❌ Changed address traceability | Does not exist | ✅ Evidence-driven redirection tracking |
| ❌ Scientific canonical namespace | Mass fragmentation | ✅ Ontological anchoring |

---

## CoResearcher's Unique Territory

```
COMPUTABLE SCIENTIFIC RECORD
```

**Not:**
- Knowledge Graph
- Artifact Repository
- Project Management Tool
- Identity Provider
- Publication Platform

**It is:**
- Ledger of verifiable scientific activity
- Hybrid research coordination
- Immutable decision history
- Computable evolutionary consensus

---

## Integration Strategy

### Identifiers from day 1:

```text
ORCID    ↔ Researcher identity (RES-XXXXXX)
ROR      ↔ Institution identity (INST-XXXXXX)
DOI      ↔ Artifact permanence (ARTIFACT-XXXXXX)
Zenodo   ↔ Dataset/software permanence
GitHub   ↔ Development provenance
```

### Federate, not invent

CoResearcher does not need:
- Identity management (ORCID)
- Storage infrastructure (Zenodo/GitHub)
- Publication pipeline (Crossref/DOI)
- Metadata harvesting (OpenAlex)

CoResearcher needs:
- Activity coordination layer
- Agent-native protocols
- Scientific consensus machinery
- Canonical namespace enforcement

---

## The Real Competitive Advantage

### It's not technical, it's institutional

The value is not in:
- Best LLM
- Better UI
- Better architecture

The value is in:
- **Network effect of accumulated activity**
- **Immutable history of scientific production**
- **Evolutionary verifiable consensus**
- **Reputation traceable by real contribution**

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

### Do not add more constitutions

### Create COMPETITIVE_LANDSCAPE.md ✅ (this document)

### For each platform identify:

1. What coordinates
2. What is its fundamental unit
3. What is your primary identifier
4. What is its network effect
5. What does NOT coordinate

### Objective:

Identify which institutional space is still really empty.

Because right now the greatest danger is not technical.

It is partially reinventing something that existing systems already solve separately without having yet identified **which piece of the puzzle is really still without an owner**.

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

The difference is enormous: an activity graph vs an artifact graph.

---

## Next steps

1. Validate that the "Scientific Activity Ledger" is the only truly empty space
2. Prioritize integrations with existing systems
3. Define minimal primitives to occupy that space
4. Don't build anything that can consume existing systems