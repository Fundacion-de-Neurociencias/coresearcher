# Handoff: CoResearcher → EditXT Traceability Contract

**Version 1.0.0** - Inter-Service Protocol  
**Status**: Operational Document

---

## Flujo de Trazabilidad entre Capas

```
Capa 1: CoResearcher (Traceability Engine)
    │
    ├── Escanea fuentes observables
    ├── Genera ACTION-XXXXXX
    ├── Genera CLAIM-XXXXXX
    ├── Responde EvidenceRequest
    └── Produce EvidenceGraph
         │
         │ [HANDOFF]
         ▼
Capa 2: EditXT (Scientific Audit)
    │
    ├── Recibe EvidenceGraph como input
    ├── Audita: evidencia experimental, código, dataset, benchmark, reproducibilidad
    ├── Genera ReviewGraph, ReviewFinding, ReviewSeverity
    └── Produce recomendaciones editoriales estructuradas
         │
         │ [PROHIBITED FEEDBACK]
         ▼
Capa 1: CoResearcher
    │
    └── NO recibe output evaluativo de EditXT
```

---

## EvidenceRequest (CoResearcher Input)

```json
{
  "request_id": "ER-000001",
  "target_claim": "CLAIM-000321",
  "evidence_scope": "supporting|contradicting|methodological",
  "minimum_confidence": 0.8,
  "provenance_required": true,
  "timestamp": "2026-07-28T10:00:00Z"
}
```

---

## EvidenceGraph (CoResearcher Output)

```json
{
  "graph_id": "EG-000001",
  "request_id": "ER-000001",
  "nodes": [
    {"id": "CLAIM-000321", "type": "Claim", "text": "...", "confidence": 0.92},
    {"id": "QUOTE-000001", "type": "Quote", "text": "...", "confidence": 0.95},
    {"id": "SOURCE-000001", "type": "Source", "text": "PMID-12345", "confidence": 0.95},
    {"id": "URL-000001", "type": "URL", "text": "https://...", "confidence": 0.95}
  ],
  "edges": [
    {"from": "CLAIM-000321", "to": "QUOTE-000001", "type": "supported_by", "hops": 1},
    {"from": "QUOTE-000001", "to": "SOURCE-000001", "type": "sourced_from", "hops": 1},
    {"from": "SOURCE-000001", "to": "URL-000001", "type": "resolves_to", "hops": 1}
  ],
  "summary": {
    "total_claims": 24,
    "total_nodes": 96,
    "total_edges": 72,
    "max_hops": 1,
    "coverage": 1.0,
    "metric_pass": true
  },
  "provenance": {
    "generated_by": "CoResearcher",
    "generated_at": "2026-07-28T10:05:00Z",
    "methodology": "LangGraph trajectory extraction",
    "sources": ["GitHub Issues", "PRs", "Releases"]
  }
}
```

---

## ReviewGraph (EditXT Input → Output)

EditXT consume EvidenceGraph y produce:

```json
{
  "review_id": "REVIEW-000001",
  "input_evidence_graph": "EG-000001",
  "findings": [
    {"claim_id": "CLAIM-000321", "evidence_present": true, "code_present": true, "dataset_present": false, "reproducibility": "partial"}
  ],
  "severity": "minor|major|critical",
  "recommendation": "address_dataset_availability"
}
```

---

## Reglas de Separación Estricta

1. CoResearcher no recibe ReviewGraph ni recomendaciones como input
2. EditXT no modifica CLAIM-XXXXXX ni ACTION-XXXXXX
3. No hay feedback loop evaluativo desde EditXT a CoResearcher
4. La única comunicación es EvidenceRequest → EvidenceGraph

---

## Responsabilidades por Capa

### CoResearcher
- Maximizar trazabilidad
- Responder "¿Dónde está la evidencia?"
- Nunca responder "¿Es cierto?" o "¿Es bueno?"

### EditXT
- Maximizar auditabilidad científica
- Responder "¿Qué problemas tiene este manuscrito/claim?"
- Evaluar evidencia experimental, código, dataset, benchmark, reproducibilidad

---

*Este handoff garantiza separación estricta de responsabilidades. CoResearcher es infraestructura de trazabilidad. EditXT es capa de auditoría científica. Nunca se mezclan.*
</parameter>
<task_progress>
- [x] Explore existing docs for conventions
- [x] Draft boundary documents
- [x] SPRINT 59D: Fix LlamaIndex
- [ ] SPRINT 59E: Benchmark with 20 repositories
  - Running; rate-limited, awaiting completion
- [x] SPRINT 60: Build EvidenceGraph v0
  - Created artifacts/langgraph_evidence_graph.json (24 claims, 96 nodes, 72 edges, max_hops=1, coverage=1.0, metric_pass=true)
- [x] Created handoff protocol document
</parameter>
</write_to_file>