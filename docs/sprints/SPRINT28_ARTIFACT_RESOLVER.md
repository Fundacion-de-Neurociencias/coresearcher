# Sprint 28: Scientific Artifact Resolver
## From Repository-Centric to Artifact-Centric Observation

---

## Strategic Context

Sprint 27 proved: GitHub-only reconstruction yields development activity, not scientific activity.

Primary finding:
- Observer infrastructure: functional
- Scientific reconstruction: blocked
- Bottleneck: **Artifact Resolver**

The scientific asset does not live in GitHub.
It lives in:
- Papers
- Preprints
- Datasets
- Protocols
- Software Releases
- DOIs

GitHub is an evidence source, not the primary object.

---

## Sprint 28 Objective

Build a **Scientific Artifact Resolver** that can link heterogeneous evidence into traceable scientific artifacts.

Success criterion:
Can the system say:
> "This GitHub release produced this DOI, which corresponds to this paper, which was cited by these works."

---

## New Abstraction

```json
{
  "artifact_id": "string",
  "type": "software_release | paper | dataset | preprint | protocol | registered_study",
  "doi": "string | null",
  "title": "string",
  "github_repo": "string | null",
  "github_release": "string | null",
  "publication": "string | null",
  "contributors": [
    {
      "name": "string",
      "orcid": "string | null",
      "github": "string | null",
      "affiliation": "string | null"
    }
  ],
  "created_at": "ISO8601",
  "updated_at": "ISO8601",
  "evidence_sources": ["github", "zenodo", "openalex", "crossref", "arxiv", "osf"],
  "citations": "integer | null",
  "zenodo_record_id": "string | null",
  "openalex_work_id": "string | null"
}
```

This is the **primary scientific object**.

All connectors populate this object.
All downstream consumers (ledger, graph, priority coverage) consume this object.

---

## Scope

What Sprint 28 does NOT do:
- No new NLP models
- No new inference rules
- No new scientific hypotheses generation
- No Objective Hypotheses layer changes

What Sprint 28 DOES do:
1. Define ScientificArtifact schema
2. Build 4 connectors that return ScientificArtifact objects
3. Build resolver that merges/groups artifacts across sources
4. Validate against 2 real repositories

---

## Connectors to Build/Extend

### 1. GitHub Connector (extend existing)
Input: repo + release tag
Output: ScientificArtifact

Extract:
- Repository metadata
- Release tag and notes
- Contributor list
- Associated DOI from release notes/body if present
- Links to papers/protocols/datasets from README and release notes

Evidence signals:
- GitHub release → potential software_release artifact
- README citations section → potential paper artifact
- READMEdatasets section → potential dataset artifact

### 2. Zenodo Connector (extend existing)
Input: DOI or concept query
Output: ScientificArtifact

Extract:
- DOI
- creators
- publication_date
- version
- files
- related identifiers

Evidence signals:
- Zenodo record → primary artifact
- Concept DOI clusters versions

### 3. OpenAlex Connector (new minimal)
Input: DOI, title, or author search
Output: ScientificArtifact

Extract:
- Work ID
- DOI
- title
- authors (with orcid)
- publication_year
- cited_by_count
- concepts

### 4. Crossref Connector (new minimal)
Input: DOI or title search
Output: ScientificArtifact

Extract:
- DOI
- title
- authors
- published-print / published-online
- type (journal-article, dataset, software, etc.)
- references/citations count

---

## Artifact Resolver Logic

Given: N ScientificArtifact objects from different sources.

Resolve:
1. **Same artifact across sources**: DOI match → same artifact
2. **Derived artifacts**: GitHub release linked to Zenodo DOI via release notes text → same work
3. **Linked artifacts**: Paper DOI in README → paper artifact linked to software artifact
4. **Contributor identity**: Same GitHub handle + same ORCID → same contributor

Output:
- One canonical ScientificArtifact per DOI
- Linked-but-distinct artifacts per work that are related but not identical
- Contributor registry with canonical IDs

---

## Validation Targets (Public Repos)

1. MNE-Python/mne-python
2. nilearn/nilearn

Selection rationale:
- High public visibility
- Known releases with Zenodo deposits
- Known papers with DOIs
- Active community

Validation checks:
- Does resolver return >= 3 distinct artifacts per repo?
- Does resolver identify at least 1 software_release?
- Does resolver identify at least 1 paper if DOI present in README?
- Do contributors have GitHub handles?
- Does resolver merge Zenodo + GitHub for the same release?

---

## Deliverables

1. `python/observer/scientific_artifact.py` — Schema definition and validator
2. `python/observer/github_connector_extended.py` — GitHub -> ScientificArtifact mapper
3. `python/observer/zenodo_connector_extended.py` — Zenodo -> ScientificArtifact mapper
4. `python/observer/openalex_connector.py` — OpenAlex minimal connector
5. `python/observer/crossref_connector.py` — Crossref minimal connector
6. `python/observer/artifact_resolver.py` — Resolve and merge logic
7. `artifacts/sprint28_artifact_resolver_validation.md` — Validation report

No new constitutions.
No redesign of observer pipeline.
Evidence-first.