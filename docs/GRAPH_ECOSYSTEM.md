# GRAPH ECOSYSTEM
**Version 1.0.0** - Scientific Knowledge Representation  
**Status**: Canonical Reference  
**Platforms**: CoResearcher, GeneForge, Neurodiagnoses, PharmaOracle, EdiTXT, DataAILab

---

## 1. Graph Taxonomy

The Graph Ecosystem defines **three canonical graph types** used across all research platforms:

---

### 1.1 EvidenceGraph

**Purpose**: Auditable claim traceability - the primary graph for scientific evidence chains

**Structure**: Directed Acyclic Graph (DAG)

**Node Types**:
```
CLAIM-XXXXXX    // Atomic scientific assertion (observable, derivable, inferred)
ART-XXXXXX      // Immutable artifact (quote, image, table, dataset, structure)
SOURCE-XXXXXX   // Primary identifier (PMID, DOI, Issue URL, commit hash)
URL-XXXXXX      // Physical resolution (https://..., doi.org/..., ftp://...)
```

**Edge Types**:
```
supported_by    // CLAIM → ART (0.9 confidence)
derived_from    // ART → SOURCE (0.95 confidence)
resolves_to     // SOURCE → URL (0.95 confidence)
```

**Constraints**:
- Acyclic (no cycles)
- Claim isolation (no Claim → Claim edges)
- Anchoring (every Claim must reach a Source within 3 hops)
- Maximum path length: Claim → ART → SOURCE → URL (3 hops)

**Schema**: `schemas/evidence_graph.schema.json`

**Primary Builder**: CoResearcher (EvidenceGraph constructor)
**Primary Consumers**: EditXT, DataAILab, external agents via MCP

---

### 1.2 ReviewGraph

**Purpose**: Peer review findings and revision tracking (EditXT-specific)

**Structure**: Directed Graph (allows cycles for revision loops)

**Node Types**:
```
FINDING-XXXXXX     // Individual review observation
REVISION-XXXXXX    // Author response/update
ISSUE-XXXXXX       // Problem identification
RECOMMENDATION-XXXXXX // Suggested action
```

**Edge Types**:
```
identifies      // FINDING → ISSUE
addresses       // REVISION → ISSUE
confirms        // FINDING → FINDING (agreement)
contradicts     // FINDING → FINDING (disagreement)
triggers        // ISSUE → REVISION
```

**Constraints**:
- No self-loops
- FINDING nodes cannot be orphaned
- REVISION chains must terminate

**Schema**: `schemas/review_graph.schema.json` (planned)

**Primary Builder**: EditXT
**Primary Consumers**: CoResearcher (evidence linking), journal workflows

---

### 1.3 Scientific Activity Graph

**Purpose**: Temporal tracking of research workflow (Question → Action → Artifact)

**Structure**: Temporal DAG with timestamps

**Node Types**:
```
QUESTION-XXXXXX  // Strategic research direction
ACTION-XXXXXX    // Executable scientific activity
ARTIFACT-XXXXXX  // Generated scientific output
RESEARCHER-XXXXXX // ORCID-identified researcher
INSTITUTION-XXXXXX // ROR-identified institution
```

**Edge Types**:
```
addresses        // ACTION → QUESTION
produces         // ACTION → ARTIFACT
performed_by     // ACTION → RESEARCHER
affiliated_with  // RESEARCHER → INSTITUTION
cites            // ARTIFACT → ARTIFACT
```

**Constraints**:
- Temporal ordering (actions occur after questions)
- ARTIFACT nodes immutable after creation
- Cycles allowed only in cites edges (citation networks)

**Schema**: `schemas/activity_graph.schema.json` (planned)

**Primary Builder**: CoResearcher (Observer + Semantic Compiler)
**Primary Consumers**: All platforms (activity reconstruction)

---

## 2. Graph Relationships

### 2.1 Inter-Graph Dependencies

```
EvidenceGraph depends on:
  ├── Scientific Activity Graph (for ACTION context)
  └── ReviewGraph (optional, for review evidence)

ReviewGraph depends on:
  ├── EvidenceGraph (for claim evidence)
  └── Scientific Activity Graph (for revision history)

Scientific Activity Graph depends on:
  └── Identity Registry (for RESEARCHER, INSTITUTION resolution)
```

### 2.2 Evidence Chain

```
Question (strategic)
    ↓ addresses
Action (executable)
    ↓ produces
Artifact (immutable output)
    ↓ derived_from
Source (primary identifier)
    ↓ resolves_to
URL (physical location)

Evidence chain observed by:
Evidence Graph ← Review Graph (optional evaluation layer)
```

### 2.3 Graph Merging

When merging graphs from multiple platforms:

```typescript
interface GraphMergePolicy {
  // Conflict resolution
  nodeConflict: 'source_of_truth' | 'merge_metadata' | 'preserve_both'
  edgeConflict: 'union' | 'most_recent' | 'highest_confidence'
  
  // Identity resolution
  deduplication: 'id_match' | 'content_hash' | 'external_id'
  
  // Provenance preservation
  mergeProvenance: boolean // Track which graph contributed which nodes
}
```

**Merging rules**:
1. Same IDs → single node (merge metadata)
2. Different IDs, same content hash → deduplicate
3. Different content → preserve both (partial merge)

---

## 3. Graph Construction Patterns

### 3.1 CoResearcher Pattern: Observer → Primitives → EvidenceGraph

```
Observer (GitHub, Zenodo, PubMed)
    ↓ raw data
Semantic Compiler
    ↓ structured primitives
  QUESTION-XXXXXX
  ACTION-XXXXXX
  CLAIM-XXXXXX
  ART-XXXXXX
    ↓
Ledger Normalizer
    ↓
EvidenceGraph (with Evidence Descriptors)
```

**Key component**: `python/observer/ledger_normalizer.py` transforms raw observations into structured primitives.

### 3.2 GeneForge Pattern: Workflow Execution → Evidence Graph

```
GFL (GeneForge Language) execution
    ↓
CRISPR optimization, alignment, variant calling
    ↓
Genomic artifacts (BAM, VCF, sequences)
    ↓
Evidence Registry (register ART-XXXXXX)
    ↓
EvidenceGraph (genomic workflow traceability)
```

**Key feature**: Evidence adapters map genomic tools to EvidenceGraph primitives.

### 3.3 EditXT Pattern: Review Process → Review Graph

```
Manuscript submission
    ↓
Peer review (multiple reviewers)
    ↓
Findings, issues, recommendations
    ↓
Author revisions
    ↓
ReviewGraph (revision history + evidence)
```

**Key feature**: ReviewGraph links back to EvidenceGraph for claim validation.

### 3.4 DataAILab Pattern: Experiments → Experiment Graph

```
ML experiment configuration
    ↓
Model training, evaluation, hyperparameter search
    ↓
Model artifacts, metrics, plots
    ↓
Evidence Registry
    ↓
Experiment Graph + EvidenceGraph
```

**Key feature**: Experiment tracking integrated with EvidenceGraph for reproducibility.

---

## 4. Graph Storage & Serialization

### 4.1 Storage Formats

**Primary**: JSON Schema Draft 2020-12
```json
{
  "graph_id": "EG-000001",
  "nodes": [...],
  "edges": [...],
  "provenance": {...}
}
```

**Secondary formats**:
- **GraphML**: For network analysis tools (Gephi, Cytoscape)
- **JSON-LD**: For semantic web integration
- **Protobuf**: For high-performance transmission

**Canonical serializer**: `packages/graph-runtime/src/serializers/json.ts`

### 4.2 Graph Database Options

**Development**:
- **SQLite** with JSON blobs
- **Neo4j** (for complex queries)

**Production**:
- **Neo4j** (primary graph DB)
- **PostgreSQL** with `ltree` (hierarchical queries)
- **Redis** (caching frequently accessed subgraphs)

### 4.3 Indexing Strategies

```yaml
Required indexes:
  - Primary key: graph_id
  - Secondary: request_id, created_at
  - Node type: type field for filtering
  - Edge index: composite (from, to, type)

Optional indexes:
  - Confidence: for filtering by quality
  - Classification: for filtering by epistemic type
  - Timestamps: for temporal queries
```

---

## 5. Graph Validation Framework

### 5.1 Validation Phases

**Phase 1: Structural**
```typescript
interface StructuralValidation {
  // Syntax
  validJSON: boolean
  schemaConformant: boolean
  
  // Topology
  noCycles: boolean
  connectedComponents: number
  isolatedNodes: string[]
  
  // Integrity
  allNodeIdsUnique: boolean
  allEdgeReferencesValid: boolean
  noOrphanedEdges: boolean
}
```

**Phase 2: Semantic**
```typescript
interface SemanticValidation {
  // Claim anchoring
  allClaimsAnchored: boolean
  maxSupportDepth: number // ≤3
  
  // Classification
  validClassificationTypes: boolean
  
  // Constraints
  noClaimToClaimEdges: boolean
  edgeTypesCorrect: boolean
}
```

**Phase 3: Provenance**
```typescript
interface ProvenanceValidation {
  provenanceFieldPresent: boolean
  requiredProvenanceFields: string[]
  signaturesValid: boolean
  timestampsConsistent: boolean
}
```

### 5.2 Validation Tool

```bash
# CLI validation
npx @coresearcher/cli validate-graph evidence_graph.json

# API validation
POST /v1/validate/graph
{
  "graph_id": "EG-000001"
}

# MCP tool
tool validate_graph { graph_id: string }
```

---

## 6. Graph Queries

### 6.1 Standard Queries

```typescript
interface GraphQueries {
  // Path queries
  getPathsToSource(claimId: string): Promise<EvidencePath[]>
  getShortestPath(from: string, to: string): Promise<GraphPath>
  
  // Neighborhood queries
  getNeighbors(nodeId: string, depth: number): Promise<GraphNode[]>
  getSubgraph(centerNodeId: string, radius: number): Promise<EvidenceGraph>
  
  // Aggregation queries
  getClaimCount(graphId: string): Promise<number>
  getSupportDepth(claimId: string): Promise<number>
  getSourcesForClaim(claimId: string): Promise<SourceNode[]>
  
  // Filtering queries
  filterByConfidence(graph: EvidenceGraph, min: number): Promise<EvidenceGraph>
  filterByType(nodes: GraphNode[], types: NodeType[]): Promise<GraphNode[]>
}
```

### 6.2 Query Optimization

```yaml
Caching strategy:
  - Cache subgraphs for 1 hour
  - Cache metrics for 24 hours
  - Invalidate on new artifact registration

Indexing:
  - B-tree on node IDs
  - GIN index on edge relationships
  - Full-text search on node text content
```

---

## 7. Graph Evolution

### 7.1 Versioning

```
EvidenceGraph v1.0.0
    ↓ v1.1.0 (add optional fields)
    ↓ v2.0.0 (breaking changes, new node types)

Version tracking:
  - graph_schema_version field in provenance
  - Migration tools for upgrading
```

### 7.2 Mutation Operations

```typescript
interface GraphMutation {
  addNode(node: GraphNode): Promise<void>
  addEdge(edge: GraphEdge): Promise<void>
  removeNode(nodeId: string): Promise<void> // Marks as deprecated
  updateNode(nodeId: string, updates: Partial<GraphNode>): Promise<void>
  
  // All mutations are provenance-tracked
  provenance: ScientificEvent
}
```

**Immutable rules**:
- Node content cannot change once created
- Only metadata can be updated
- Deletion is soft (deprecated flag)
- All mutations recorded in Provenance Engine

---

## 8. Multi-Platform Graph Integration

### 8.1 Graph Federation

```
CoResearcher EvidenceGraph
    ├── shared nodes/edges
    └── platform-specific nodes/edges

GeneForge EvidenceGraph
    ├── shared nodes/edges
    └── genomic workflow nodes

Neurodiagnoses EvidenceGraph
    ├── shared nodes/edges
    └── neuroimaging nodes

Federation layer merges graphs based on:
  - Shared artifact IDs
  - Cross-referenced sources
  - Provenance chains
```

### 8.2 Cross-Platform Linking

```typescript
interface CrossPlatformLink {
  sourceGraph: string // Platform ID
  sourceNodeId: string
  targetGraph: string // Platform ID
  targetNodeId: string
  relation: RelationType
  confidence: number
}

// Example: GeneForge links to CoResearcher
const link: CrossPlatformLink = {
  sourceGraph: 'geneforge',
  sourceNodeId: 'ART-000042', // Genomic variant
  targetGraph: 'coresearcher',
  targetNodeId: 'ART-000123', // Published paper figure
  relation: RelationType.SUPPLEMENTS,
  confidence: 0.9
}
```

---

## 9. Graph Ecosystem Standards

### 9.1 Naming Conventions

```yaml
IDs:
  - Graph: EG-XXXXXX (EvidenceGraph), RG-XXXXXX (ReviewGraph), AG-XXXXXX (Activity Graph)
  - Nodes: TYPE-XXXXXX (where TYPE = CLAIM, ART, SOURCE, URL, FINDING, REVISION, etc.)
  - Edges: N/A (referenced by from/to node IDs)

Files:
  - JSON: {graph_type}_{identifier}.json
  - GraphML: {graph_type}_{identifier}.graphml
  - Protobuf: {graph_type}_{identifier}.pb
```

### 9.2 Metadata Requirements

```typescript
interface GraphMetadata {
  schema_version: string
  generated_by: string // Platform ID
  generated_at: Date
  corpus_version?: string // Optional, for reproducibility
  processing_notes?: string[]
  cross_platform_links?: CrossPlatformLink[]
}
```

---

## 10. Future Graph Types (Planned)

### 10.1 Experiment Graph (DataAILab)

```yaml
Purpose: ML experiment tracking
Nodes:
  - EXPERIMENT-XXXXXX
  - MODEL-XXXXXX
  - DATASET-XXXXXX
  - METRIC-XXXXXX
Edges:
  - trained_on
  - evaluated_on
  - produces
```

### 10.2 Collaboration Graph

```yaml
Purpose: Researcher collaboration network
Nodes:
  - RESEARCHER-XXXXXX (ORCID)
  - INSTITUTION-XXXXXX (ROR)
  - PROJECT-XXXXXX
Edges:
  - collaborates_with
  - funded_by
  - part_of
```

### 10.3 Provenance Graph

```yaml
Purpose: Complete artifact lineage across platforms
Nodes:
  - PROV-XXXXXX (provenance record)
  - TOOL-XXXXXX
  - DATA-XXXXXX
Edges:
  - generated_by
  - used_tool
  - transformed_into
```

---

*This document defines the canonical graph ecosystem. All platforms must use these graph types and conform to these standards for interoperability.*