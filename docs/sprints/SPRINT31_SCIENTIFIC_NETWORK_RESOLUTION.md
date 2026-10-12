# Sprint 31: Scientific Network Resolution
## Programs Emerge from Networks, Not Artifact Similarity

---

## Strategic Context

Sprint 30 produced a falsifiable negative result:

```text
Artifact similarity ≠ Program membership
```

Two artifacts can belong to the same scientific program and yet have:
- Different titles
- Different DOIs
- Different authors
- Different repositories

What they share is not semantic similarity.
What they share is **network relationships**:

- Shared contributors
- Shared organizations
- Shared standards
- Shared governance
- Shared citations/references

Therefore, the architecture must introduce a new layer:

```text
Evidence Sources
    ↓
Artifacts
    ↓
Scientific Networks
    ↓
Programs
```

Where Scientific Networks capture:
- People / Contributors
- Organizations / Institutions
- Standards / Ontologies
- Funding / Grants
- Datasets / Platforms
- Citations / References

---

## Sprint 31 Objective

Build a **Scientific Network Resolver** that infers program membership from network signals rather than artifact similarity.

Success criterion:
Can CoResearcher group BIDS ecosystem artifacts into one program using:
- shared contributors,
- shared organizations,
- shared standards/ontologies,
- shared governance,

without relying on title/DOI similarity?

---

## What Sprint 31 Does NOT Do

- No new connectors
- No new artifact types
- No manual labeling of programs
- No threshold tuning on artifact similarity

---

## What Sprint 31 DOES Do

1. Define ScientificNetwork schema:
   - nodes: contributors, organizations, standards, datasets
   - edges: contributor_to, affiliated_with, cites, governs, references
2. Build NetworkExtractor:
   - extracts network signals from existing ScientificArtifact objects
   - contributor names/ORCIDs
   - organizations from affiliations
   - standards from notes/titles
   - citations from OpenAlex/Crossref
3. Build NetworkResolver:
   - builds bipartite artifact-to-network-node graph
   - clusters artifacts by shared network neighborhoods
   - outputs Programs with network-derived rationale
4. Validate on BIDS ecosystem:
   - inputs: artifacts from bids-standard/bids-specification, bids-standard/pybids, bids-standard/bids-examples
   - expected: 1 Program for "BIDS"
   - metric: % of known ecosystem artifacts assigned to same inferred program

---

## ScientificNetwork Schema

```json
{
  "network_id": "bids",
  "nodes": [
    {"id": "contributor:xyz", "type": "contributor", "name": "..."},
    {"id": "org:abc", "type": "organization", "name": "..."},
    {"id": "standard:bids", "type": "standard", "name": "Brain Imaging Data Structure"}
  ],
  "edges": [
    {"source": "contributor:xyz", "target": "org:abc", "relation": "affiliated_with"},
    {"source": "artifact:doi", "target": "standard:bids", "relation": "references"},
    {"source": "contributor:xyz", "target": "artifact:doi", "relation": "authored"}
  ]
}
```

---

## Network Resolver Logic

Given: N ScientificArtifact objects.

Steps:
1. For each artifact, extract:
   - contributors
   - organizations from affiliations
   - standards/ontologies from notes/titles
   - citations from OpenAlex/Crossref
2. Build a graph:
   - Nodes: artifacts + contributors + organizations + standards
   - Edges: artifact→contributor, artifact→organization, artifact→standard, artifact→citation
3. For each artifact, compute network neighborhood:
   - {contributor names, org names, standard names, cited DOIs}
4. Compute artifact-to-artifact network similarity:
   - Jaccard similarity of neighborhoods
   - If similarity > 0, connect artifacts in program graph
5. Cluster program graph.
6. Output one Program per cluster, with network-derived evidence.

Key difference from Sprint 30:
- Sprint 30: artifact-to-artifact similarity
- Sprint 31: artifact-to-network-node similarity → program membership

---

## Validation Target

BIDS ecosystem.

Repositories:
- bids-standard/bids-specification
- bids-standard/pybids
- bids-standard/bids-examples

Success criterion:
At least 80% of manually known ecosystem artifacts are assigned to the same inferred program without hardcoded BIDS-specific relationships.

Manual review questions:
1. Did the resolver group BIDS repos together?
2. Are the inferred contributors/organizations correct?
3. Are the standards correctly identified?
4. Is the comprehension summary coherent?

---

## Deliverables

1. `python/observer/scientific_network.py` — Network schema and serializer
2. `python/observer/network_extractor.py` — Extract network signals from artifacts
3. `python/observer/network_resolver.py` — Cluster artifacts by network neighborhoods
4. `python/observer/validate_sprint31.py` — Validation script for BIDS
5. `artifacts/sprint31_network_resolution_validation.md` — Validation report

No new connectors.
No redesign of existing pipeline.
Evidence-first.