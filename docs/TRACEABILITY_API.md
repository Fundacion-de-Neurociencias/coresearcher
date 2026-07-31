# TRACEABILITY API
**Version 1.0.0** - Public API Specification  
**Status**: Production Ready  
**Base URL**: `https://api.coresearcher.org/v1`

---

## 1. API Purpose

The Traceability API provides auditable scientific evidence chains without exposing internal implementation details. External agents can request, trace, and verify scientific claims through a unified interface.

### Design Principles

1. **Zero Internal Knowledge Required**: Consumers only need standard ontologies (DOI, GitHub issues, scientific identifiers)
2. **Evidence-First**: Every response includes complete provenance chains
3. **Minimal Surface Area**: Four request types cover all scientific traceability needs
4. **Constitutional Compliance**: All outputs respect CoResearcher's evidence graph rules (acyclic, ≤3 hops, anchored claims)

---

## 2. Request Types

### 2.1 CLAIM_TRACE

Trace a specific claim back to its original sources.

**Use Case**: "I need to verify where this assertion came from"

**Request**:
```json
{
  "request_id": "ER-000042",
  "request_type": "CLAIM_TRACE",
  "target": {
    "type": "ACTION",
    "id": "ACTION-000042"
  },
  "scope": {
    "depth": 3,
    "include_artifacts": true,
    "include_provenance": true
  }
}
```

**Response**: Evidence Graph with `CLAIM-*` nodes rooted at the target.

---

### 2.2 EVIDENCE_GRAPH

Generate a complete evidence graph for a research artifact.

**Use Case**: "Visualize all supporting evidence for this question"

**Request**:
```json
{
  "request_id": "ER-000043",
  "request_type": "EVIDENCE_GRAPH",
  "target": {
    "type": "QUESTION",
    "id": "QUESTION-000001"
  },
  "scope": {
    "depth": 5,
    "filters": {
      "min_confidence": 0.7,
      "classification_types": ["observable", "derivable"]
    }
  }
}
```

**Response**: Full Evidence Graph connecting claims, artifacts, sources, and URLs.

---

### 2.3 REPOSITORY_AUDIT

Audit a repository for scientific evidence artifacts (issues, PRs, commits).

**Use Case**: "Map all scientific artifacts in this GitHub repository"

**Request**:
```json
{
  "request_id": "ER-000044",
  "request_type": "REPOSITORY_AUDIT",
  "target": {
    "type": "REPOSITORY",
    "id": "https://github.com/langchain-ai/langgraph"
  },
  "scope": {
    "depth": 3,
    "filters": {
      "date_range": {
        "from": "2026-01-01T00:00:00Z",
        "to": "2026-12-31T23:59:59Z"
      }
    }
  }
}
```

**Response**: Evidence Graph with repository artifacts (SOURCES, URLs) and derived claims.

---

### 2.4 ZENODO_CHAIN

Trace a DOI publication chain across versions and citations.

**Use Case**: "Track all evidence linked to this Zenodo deposit"

**Request**:
```json
{
  "request_id": "ER-000045",
  "request_type": "ZENODO_CHAIN",
  "target": {
    "type": "DOI",
    "id": "10.5281/zenodo.1234567"
  },
  "scope": {
    "depth": 5,
    "include_provenance": true
  }
}
```

**Response**: Evidence Graph with DOI-linked artifacts, publication sources, and descendant claims.

---

## 3. Standard Response Format

All endpoints return a normalized structure:

```json
{
  "meta": {
    "request_id": "ER-000042",
    "request_type": "CLAIM_TRACE",
    "status": "completed",
    "timestamp": "2026-07-30T18:47:00Z"
  },
  "data": {
    "graph_id": "EG-000001",
    "nodes": [...],
    "edges": [...]
  }
}
```

---

## 4. Primitives (Request/Response Objects)

### 4.1 Evidence Request (`EvidenceRequest`)

```json
{
  "request_id": "ER-XXXXXX",
  "request_type": "CLAIM_TRACE | EVIDENCE_GRAPH | REPOSITORY_AUDIT | ZENODO_CHAIN",
  "target": {
    "type": "QUESTION | ACTION | ARTIFACT | REPOSITORY | DOI",
    "id": "string (identifier)"
  },
  "scope": {
    "depth": "integer (1-10)",
    "include_artifacts": "boolean",
    "include_provenance": "boolean",
    "filters": {
      "min_confidence": "number (0-1)",
      "classification_types": ["observable", "derivable", "inferred"],
      "date_range": {
        "from": "date-time",
        "to": "date-time"
      }
    }
  },
  "context": {
    "research_domain": "string",
    "tags": ["string"],
    "notes": "string"
  }
}
```

### 4.2 Evidence Graph (`EvidenceGraph`)

```json
{
  "graph_id": "EG-XXXXXX",
  "request_id": "ER-XXXXXX",
  "nodes": [
    {
      "id": "CLAIM-XXXXXX | ART-XXXXXX | SOURCE-XXXXXX | URL-XXXXXX",
      "type": "Claim | Artifact | Source | URL",
      "text": "string",
      "classification": "observable | derivable | inferred",
      "confidence": "number (0-1)",
      "evidence_descriptors": {
        "source_count": "integer",
        "support_depth": "integer (1-3)",
        "artifact_count": "integer"
      }
    }
  ],
  "edges": [
    {
      "from": "node_id",
      "to": "node_id",
      "type": "supported_by | derived_from | resolves_to",
      "weight": "number (0-1)",
      "hops": "integer (1-3)"
    }
  ],
  "provenance": {
    "generated_by": "CoResearcher",
    "timestamp": "date-time",
    "corpus_version": "string",
    "processing_notes": ["string"]
  }
}
```

---

## 5. Response Codes

| Code | Status | Meaning |
|------|--------|---------|
| 200 | OK | Request completed successfully |
| 202 | Accepted | Async job queued (large graphs) |
| 400 | Bad Request | Invalid schema/parameters |
| 404 | Not Found | Target identifier not in ledger |
| 429 | Rate Limited | Client exceeding quota |
| 500 | Internal Error | Server-side failure |

---

## 6. Request Semantics (Inferred Contracts)

### 6.1 Canonical Model

CoResearcher operates on four primitives, each with immutable identifiers:

```
QUESTION-[0-9]{6}  → Strategic research direction
ACTION-[0-9]{6}    → Executable scientific activity
ART-[0-9]{6}       → Scientific artifact (immutable output)
CLAIM-[0-9]{6}     → Atomic knowledge unit
```

### 6.2 Graph Constraints

1. **Directed Acyclic**: No cycles permitted
2. **Claim Isolation**: Claims cannot reference other claims directly
3. **Anchoring**: Every claim must connect to ≥1 source within 3 hops
4. **Weight Semantics**: `supported_by` (0.9), `derived_from` (0.95), `resolves_to` (0.95)

### 6.3 Classification Semantics

- `observable`: Present in source document verbatim
- `derivable`: Synthesized by agent from observable evidence
- `inferred`: Hypothesis beyond current evidence (requires flag in context)

---

## 7. Authentication

All requests require authentication via:

```
Authorization: Bearer <CR_API_KEY>
```

API keys are scoped to:
- Research domains (for `context.research_domain`)
- Quote limits per time window
- Repository allowlists (for `REPOSITORY_AUDIT`)

---

## 8. Rate Limits

- **Sync (200/400/404)**: 100 req/min per key
- **Async (202)**: 10 concurrent jobs per key
- **Large graphs (>1000 nodes)**: Always async with webhook callback

---

## 9. External Agent Integration Pattern

### Step 1: Define Context

```json
{
  "research_domain": "neurodegeneration",
  "tags": ["alzheimer", "biomarkers"]
}
```

### Step 2: Submit Request

```bash
curl -X POST https://api.coresearcher.org/v1/trace \
  -H "Authorization: Bearer $CR_API_KEY" \
  -H "Content-Type: application/json" \
  -d @evidence_request.json
```

### Step 3: Parse Response

```javascript
const graph = response.data;
const claimPaths = graph.edges.filter(e => e.type === 'supported_by');
```

---

## 10. Examples

See companion files:
- `examples/langgraph_evidence_request.json` - Concrete request example
- `examples/langgraph_evidence_graph.json` - Complete graph output

---

*API stability: 1.x - Semantic versioning applies. Breaking changes require new major version.*