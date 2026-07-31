# SHARED SERVICES
**Version 1.0.0** - Cross-Platform Business Logic  
**Status**: Canonical Reference  
**Consumers**: CoResearcher, GeneForge, Neurodiagnoses, PharmaOracle, EdiTXT, DataAILab

---

## 1. Service Catalog

### 1.1 Provenance Engine (`@coresearcher/provenance`)

**Purpose**: Immutable execution trace tracking for all scientific activities

**Core responsibilities**:
1. Record tool calls, prompts, and data transformations
2. Compute artifact lineage (provenance chains)
3. Cryptographically sign provenance records
4. Provide immutable audit trails

**Public interface**:
```typescript
interface ProvenanceEngine {
  // Lifecycle
  initialize(sessionId: string): Promise<void>
  finalize(): Promise<ProvenanceRecord>
  
  // Event recording
  emitEvent(event: ScientificEvent): Promise<void>
  recordToolCall(call: ToolCall): Promise<void>
  recordDataLineage(lineage: DataLineage): Promise<void>
  
  // Querying
  getExecutionTrace(actionId: string): Promise<ExecutionTrace>
  getArtifactLineage(artifactId: string): Promise<LineageChain>
  verifyIntegrity(recordId: string): Promise<boolean>
}

interface ScientificEvent {
  timestamp: Date
  actor: string // Agent or researcher ID
  action: string // ACTION-XXXXXX
  eventType: 'start' | 'complete' | 'error' | 'intermediate'
  metadata: Record<string, unknown>
}
```

**Storage contract**:
```yaml
Interface: LedgerStorage
Methods:
  - append(record: ProvenanceRecord): Promise<void>
  - getBatch(ids: string[]): Promise<ProvenanceRecord[]>
  - query(filter: ProvenanceFilter): Promise<ProvenanceRecord[]>
  - export(format: 'json' | 'merkle'): Promise<Buffer>

Guarantees:
  - Append-only (no updates or deletes)
  - Cryptographic chaining (Merkle tree)
  - Tamper detection (SHA-256 checksums)
```

**Deployment**:
- **Package**: `packages/provenance/`
- **Port**: 3001
- **Protocol**: gRPC + REST
- **Storage**: SQLite (dev), PostgreSQL (prod)

**Consumers**:
- CoResearcher (primary)
- GeneForge (genomic workflow provenance)
- Neurodiagnoses (imaging pipeline provenance)
- PharmaOracle (drug discovery provenance)

---

### 1.2 Evidence Registry (`@coresearcher/evidence-registry`)

**Purpose**: Central registry for scientific evidence artifacts with lifecycle management

**Core responsibilities**:
1. Register immutable artifacts (EVID-XXXXXX)
2. Resolve artifact relationships (derived_from, supersedes)
3. Compute evidence descriptors for claims
4. Enforce immutability (no updates after registration)

**Public interface**:
```typescript
interface EvidenceRegistry {
  // Registration - idempotent
  register(artifact: Artifact): Promise<EvidenceId>
  registerBatch(artifacts: Artifact[]): Promise<EvidenceId[]>
  
  // Resolution
  resolve(id: EvidenceId): Promise<Artifact>
  resolveChain(id: EvidenceId): Promise<Artifact[]>
  
  // Relationships
  link(source: EvidenceId, target: EvidenceId, relation: RelationType): Promise<void>
  getRelated(id: EvidenceId, relation: RelationType): Promise<EvidenceId[]>
  
  // Descriptors
  computeDescriptors(claimId: ClaimId): Promise<EvidenceDescriptors>
  
  // Lifecycle
  isRegistered(id: EvidenceId): Promise<boolean>
  getCreationTimestamp(id: EvidenceId): Promise<Date>
}

interface EvidenceDescriptors {
  source_count: number
  support_depth: number // 1-3 hops
  artifact_count: number
  contradiction_count?: number
  supersedes_count?: number
}

enum RelationType {
  DERIVED_FROM = 'derived_from',
  SUPERSEDES = 'supersedes',
  CONTRADICTS = 'contradicts',
  SUPPLEMENTS = 'supplements'
}
```

**Immutability guarantee**:
```yaml
Rules:
  - Once registered, artifact content cannot change
  - Only metadata can be augmented (e.g., adding relationships)
  - Deletion is prohibited (only marked as deprecated)
  - All mutations are provenance-tracked
```

**Consumers**:
- CoResearcher (EvidenceGraph construction)
- EdiTXT (review evidence linking)
- DataAILab (experiment artifact tracking)

---

### 1.3 MCP Protocol Layer (`@coresearcher/mcp-server`)

**Purpose**: Model Context Protocol server for external agent integration

**Core responsibilities**:
1. Expose EvidenceRequest/EvidenceGraph API
2. Handle tool invocations from external agents
3. Rate limiting, authentication, validation
4. WebSocket support for real-time graph updates

**Exposed tools**:
```typescript
// tools/trace.ts
tool({
  name: 'trace_evidence',
  description: 'Request evidence graph for a scientific target',
  inputSchema: z.object({
    request_type: z.enum(['CLAIM_TRACE', 'EVIDENCE_GRAPH', 'REPOSITORY_AUDIT', 'ZENODO_CHAIN']),
    target: z.object({
      type: z.enum(['QUESTION', 'ACTION', 'ARTIFACT', 'REPOSITORY', 'DOI']),
      id: z.string()
    }),
    depth: z.number().min(1).max(10).default(3),
    filters: z.object({
      min_confidence: z.number().min(0).max(1).optional(),
      classification_types: z.array(z.enum(['observable', 'derivable', 'inferred'])).optional()
    }).optional()
  }),
  handler: async (params) => {
    const graph = await buildEvidenceGraph(params)
    return { graph_id, nodes, edges }
  }
})

// tools/validate.ts
tool({
  name: 'validate_graph',
  description: 'Validate EvidenceGraph constraints',
  inputSchema: z.object({
    graph_id: z.string()
  }),
  handler: async (params) => {
    const violations = await validateGraphConstraints(params.graph_id)
    return { valid: violations.length === 0, violations }
  }
})
```

**Deployment**:
- **Package**: `packages/mcp-server/`
- **Port**: 3000
- **Protocol**: MCP over stdio + HTTP
- **Authentication**: Bearer tokens (CR_API_KEY)

**Consumers**:
- All platforms (external integration point)

---

### 1.4 Graph Runtime (`@coresearcher/graph-runtime`)

**Purpose**: Graph construction, validation, and metrics computation

**Core responsibilities**:
1. Construct EvidenceGraph from primitives
2. Validate graph constraints (acyclic, ≤3 hops, anchored)
3. Compute graph metrics (centrality, path lengths)
4. Serialize/deserialize graph formats (JSON, GraphML)

**Interfaces**:
```typescript
interface GraphRuntime {
  // Construction
  buildGraph(primitives: ScientificPrimitive[]): Promise<EvidenceGraph>
  mergeGraphs(graphs: EvidenceGraph[]): Promise<EvidenceGraph>
  
  // Validation
  validate(graph: EvidenceGraph): Promise<ValidationResult>
  validateConstraints(graph: EvidenceGraph): Promise<Violation[]>
  
  // Metrics
  computeMetrics(graph: EvidenceGraph): Promise<GraphMetrics>
  computeCentrality(graph: EvidenceGraph): Promise<Map<string, number>>
  
  // Serialization
  toJSON(graph: EvidenceGraph): Promise<string>
  toGraphML(graph: EvidenceGraph): Promise<string>
  fromJSON(json: string): Promise<EvidenceGraph>
}

interface ValidationResult {
  valid: boolean
  violations: Violation[]
  warnings: string[]
}

interface Violation {
  type: 'CYCLE' | 'UNANCHORED_CLAIM' | 'HOP_LIMIT_EXCEEDED' | 'CLAIM_TO_CLAIM'
  nodeIds: string[]
  message: string
  severity: 'error' | 'warning'
}
```

**Enforced constraints**:
```yaml
Hard constraints (validation fails):
  - No cycles (asserted by topological sort)
  - No Claim → Claim edges
  - Every Claim has ≥1 path to Source within 3 hops

Soft constraints (warnings):
  - Artifact types properly classified
  - Confidence scores present
  - Provenance metadata complete
```

**Consumers**:
- CoResearcher (primary)
- DataAILab (experiment graph analysis)
- GeneForge (genomic workflow visualization)

---

## 2. Service Dependency Graph

```mermaid
graph TD
    A[Infrastructure Layer] --> D[Shared Services]
    B[Graph Ecosystem] --> D
    D --> E[Domain Modules]
    
    A1[Types/Zod] --> A
    A2[Identity/ORCID] --> A
    A3[Storage/Ledger] --> A
    
    B1[EvidenceGraph Schema] --> B
    B2[ReviewGraph Schema] --> B
    B3[Provenance Schema] --> B
    
    D1[Provenance Engine] --> D
    D2[Evidence Registry] --> D
    D3[MCP Protocol] --> D
    D4[Graph Runtime] --> D
    
    D1 --> A3
    D2 --> A3
    D3 --> B1
    D4 --> B1
    D4 --> B2
```

---

## 3. Integration Patterns

### 3.1 Domain Module → Provenance Engine

```typescript
// Initialize session
await provenanceEngine.initialize('ACTION-000042')

// Record events
await provenanceEngine.recordToolCall({
  tool: 'search_literature',
  inputs: { query: 'CRISPR off-target effects' },
  outputs: { paper_count: 42 },
  timestamp: new Date()
})

// Finalize
const record = await provenanceEngine.finalize()
// record contains: execution trace, data lineage, signatures
```

### 3.2 Domain Module → Evidence Registry

```typescript
// Register artifact
const evidenceId = await evidenceRegistry.register({
  artifact_type: 'quote',
  content: '"CRISPR-Cas9 off-target effects remain a concern..."',
  source: 'PMID-12345678',
  context: 'Literature review on gene editing safety'
})

// Link to claim
await evidenceRegistry.link('CLAIM-000001', evidenceId, RelationType.SUPPORTS)

// Compute descriptors
const descriptors = await evidenceRegistry.computeDescriptors('CLAIM-000001')
// { source_count: 3, support_depth: 2, artifact_count: 5 }
```

### 3.3 Domain Module → MCP Protocol

```typescript
// Domain module exposes MCP tool
server.tool('search_evidence', {
  query: z.string(),
  domain: z.string().optional()
}, async (params) => {
  // Internal logic
  const results = await internalSearch(params.query)
  
  // Emit provenance
  await provenanceEngine.recordToolCall({
    tool: 'search_evidence',
    inputs: params,
    outputs: { result_count: results.length }
  })
  
  return results
})
```

### 3.4 Domain Module → Graph Runtime

```typescript
// Build graph from primitives
const graph = await graphRuntime.buildGraph([
  { type: 'CLAIM', id: 'CLAIM-000001', ... },
  { type: 'ARTIFACT', id: 'ART-000001', ... },
  { type: 'SOURCE', id: 'SOURCE-000001', ... }
])

// Validate
const result = await graphRuntime.validate(graph)
if (!result.valid) {
  console.error('Violations:', result.violations)
}

// Compute metrics
const metrics = await graphRuntime.computeMetrics(graph)
// { node_count: 15, edge_count: 12, avg_path_length: 1.8 }
```

---

## 4. Service Contracts Summary

| Service | Protocol | Authentication | Rate Limit | SLA |
|---------|----------|----------------|------------|-----|
| Provenance Engine | gRPC + REST | Internal token | 10K req/s | 99.9% |
| Evidence Registry | gRPC + REST | Internal token | 5K req/s | 99.9% |
| MCP Protocol | MCP stdio + HTTP | Bearer token | 100 req/min/key | 99.5% |
| Graph Runtime | Library (TS/Py) | N/A (embedded) | N/A | N/A |

---

## 5. Versioning & Compatibility

### Service-Level Versioning

```
@coresearcher/provenance@1.2.3
  ↓
Major: Breaking API changes
Minor: New features, backward compatible
Patch: Bug fixes

@coresearcher/evidence-registry@2.0.0
  ↓
Independent versioning per service
```

### Schema-Level Versioning

```yaml
EvidenceGraph v1.0.0
  ↓
Minor: Add optional fields
Major: Remove/rename fields, change types
```

### Backward Compatibility Guarantees

1. **Shared Services**: 
   - Major version bumps for breaking changes
   - 6-month deprecation window
   - Migration guides provided

2. **Graph Schemas**:
   - Optional fields can be added in minor versions
   - Required fields can only be added in major versions
   - Deprecated fields marked for removal in next major

3. **Domain Modules**:
   - Independent versioning
   - No compatibility guarantees across modules
   - Integration tests per version pair

---

## 6. Deployment Architecture

### 6.1 Shared Services Monorepo

```
packages/
├── provenance/
│   ├── src/
│   ├── dist/
│   ├── package.json
│   └── Dockerfile
├── evidence-registry/
│   ├── src/
│   ├── dist/
│   ├── package.json
│   └── Dockerfile
├── mcp-server/
│   ├── src/
│   ├── dist/
│   ├── package.json
│   └── Dockerfile
└── graph-runtime/
    ├── src/
    ├── dist/
    ├── package.json
    └── Dockerfile
```

**Build**:
```bash
npm run bootstrap  # Install dependencies
npm run build      # Build all packages
npm run test       # Run test suites
```

### 6.2 Docker Deployment

```yaml
# docker-compose.shared.yml
version: '3.8'
services:
  provenance-engine:
    build: ./packages/provenance
    ports: ["3001:3001"]
    volumes:
      - ledger:/data
    environment:
      - DATABASE_URL=postgresql://ledger:ledger@postgres:5432/provenance
    depends_on:
      - postgres
  
  evidence-registry:
    build: ./packages/evidence-registry
    ports: ["3002:3002"]
    volumes:
      - registry:/data
    environment:
      - DATABASE_URL=postgresql://registry:registry@postgres:5432/registry
    depends_on:
      - postgres
  
  mcp-server:
    build: ./packages/mcp-server
    ports: ["3000:3000"]
    environment:
      - PROVENANCE_URL=http://provenance-engine:3001
      - EVIDENCE_REGISTRY_URL=http://evidence-registry:3002
    depends_on:
      - provenance-engine
      - evidence-registry
  
  postgres:
    image: postgres:16-alpine
    volumes:
      - postgres-data:/var/lib/postgresql/data
    environment:
      - POSTGRES_USER=coresearcher
      - POSTGRES_PASSWORD=coresearcher

volumes:
  ledger:
  registry:
  postgres-data:
```

### 6.3 Kubernetes Deployment

```yaml
# k8s/provenance-engine.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: provenance-engine
spec:
  replicas: 3
  selector:
    matchLabels:
      app: provenance-engine
  template:
    metadata:
      labels:
        app: provenance-engine
    spec:
      containers:
      - name: provenance-engine
        image: coresearcher/provenance:1.2.3
        ports:
        - containerPort: 3001
        env:
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: provenance-secret
              key: database-url
        resources:
          requests:
            memory: "256Mi"
            cpu: "250m"
          limits:
            memory: "512Mi"
            cpu: "500m"
---
apiVersion: v1
kind: Service
metadata:
  name: provenance-engine
spec:
  selector:
    app: provenance-engine
  ports:
  - port: 3001
    targetPort: 3001
```

---

## 7. Monitoring & Observability

### 7.1 Metrics

```typescript
// Per-service metrics
interface ServiceMetrics {
  request_count: Counter
  request_duration: Histogram
  error_count: Counter
  active_connections: Gauge
}

// Business metrics
interface BusinessMetrics {
  artifacts_registered: Counter
  evidence_graphs_built: Counter
  provenance_records_created: Counter
  validation_violations: Counter
}
```

### 7.2 Logging

```typescript
// Structured logging
interface LogContext {
  service: string
  requestId?: string
  actionId?: string
  artifactId?: string
  userId?: string
}

// Log levels
enum LogLevel {
  DEBUG = 'debug',
  INFO = 'info',
  WARN = 'warn',
  ERROR = 'error'
}
```

### 7.3 Tracing

```typescript
// Distributed tracing with OpenTelemetry
interface TraceContext {
  traceId: string
  spanId: string
  parentSpanId?: string
}

// Example: Evidence graph construction trace
const trace = startSpan('build_evidence_graph', {
  attributes: {
    'request_type': request.request_type,
    'target_id': request.target.id,
    'depth': request.scope.depth
  }
})

// ... build graph ...

trace.end()
```

---

## 8. Security Considerations

### 8.1 Authentication

```yaml
Internal services:
  - mTLS between services
  - Service mesh (Istio) for auth

External access (MCP):
  - Bearer tokens (CR_API_KEY)
  - Rate limiting per key
  - Scope restrictions (domain, repository allowlist)
```

### 8.2 Authorization

```typescript
interface AuthorizationPolicy {
  roles: ['admin', 'researcher', 'readonly']
  permissions: {
    read: ['evidence_graph', 'public_data']
    write: ['register_artifact', 'link_evidence']
    admin: ['delete_artifact', 'modify_schemas']
  }
  scopes: {
    domain: string[] // e.g., ['neurodegeneration', 'genomics']
    repositories: string[] // e.g., ['langchain-ai/langgraph']
  }
}
```

### 8.3 Data Protection

```yaml
At rest:
  - Encryption: AES-256
  - Key management: Google Cloud KMS

In transit:
  - TLS 1.3
  - Certificate pinning for critical services

Privacy:
  - No PII in provenance records (use ORCID references)
  - Audit logs anonymized for analytics
```

---

*This document defines the canonical shared services layer. All platform components must consume these services rather than reimplementing functionality.*