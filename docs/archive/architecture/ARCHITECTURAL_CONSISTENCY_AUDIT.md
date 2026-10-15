# Architectural Consistency Audit (ARQ-001)

This audit stresses the boundaries defined in the CoResearcher Constitution, destructively searching for contradictions, overlaps of responsibility, or ambiguities between canonical documents.

## Consistency Matrix

| Document A | Document B | Conflict? | Analysis / Justification | Resolution / Verdict |
| ----------- | ----------- | ----------- | ------------------------ | ---------------------- |
| `BOUNDARY_WITH_EDITXT` | `BOUNDARY_WITH_AI_SCIENTISTS` | **NO** | EditXT audits quality on existing graphs. AI Scientists generate new science. They both respect that CoResearcher simply plots evidence without making judgments or hypotheses. | **Consistent**. Boundaries 1 and 2 are orthogonal and well delineated in front of Layer 1 (CoResearcher). |
| `BOUNDARY_WITH_EDITXT` | `HANDOFF_TRACEABILITY` | **PARTIAL** | `BOUNDARY_WITH_EDITXT` indicates that EditXT consumes EvidenceGraphs to create ReviewGraphs. `HANDOFF_TRACEABILITY` strictly specifies that communication is one-way and CoResearcher **does not receive** evaluative output. | **Resolved**. `HANDOFF_TRACEABILITY` shields a possible contamination vector by explicitly detailing the Input/Output, but both documents are aligned in that there is no *feedback loop*. |
| `ARCHITECTURE_MAP` | `BOUNDARY_WITH_AI_SCIENTISTS` | **NO** | `ARCHITECTURE_MAP` places "AI Scientists" as *External Consumers* (Read-only access). The frontier agrees perfectly that CoResearcher does not have bidirectional integration with hypothesis generators. | **Consistent**. The map physically reflects the border ban 3. |
| `ARCHITECTURE_MAP` | `HANDOFF_TRACEABILITY` | **NO** | The map defines `EditXT` as an *Ecossystem App* that consumes `EvidenceGraph` and produces `ReviewGraph`. The *Handoff* document standardizes the exact JSON payloads (`EG-XXXXX`, `REVIEW-XXXXX`) for that flow. | **Consistent**. 1:1 technical traceability. |
| `BOUNDARY_WITH_EDITXT` | `ARCHITECTURE_MAP` | **POTENTIAL** | `BOUNDARY_WITH_EDITXT` (L150) mentions *GitHub Issues → QUESTION-XXXXXX*, but | **Minor Adjustment Required**. The Semantic Compiler in `ARCHITECTURE_MAP` must formally document the issuance of `QUESTION-XXXXXX` to align 100% with the EditXT topology. *Action: Documented and accepted as minor technical debt (does not break the contract).* |

## Evaluation of Graph Types (EvidenceGraph vs ReviewGraph)

There is a common architectural risk in confusing the evidence graph with the review graph. The audit confirms that the segregation is absolute:

1. **EvidenceGraph (CoResearcher Domain)**
   - Allowed nodes: `Claim`, `Quote`, `Source`, `URL`.
   - Allowed edges: `supported_by`, `sourced_from`, `resolves_to`.
   - **Strict limitation:** Does not contain "Quality", "Severity" or "Verdict" nodes.

2. **ReviewGraph (EditXT Domain)**
   - Allowed nodes: `ReviewFinding`, `ReviewSeverity`, `ReviewRecommendation`.
   - **Strict limitation:** Consumes an EvidenceGraph as a foreign ID (`input_evidence_graph`), but never overwrites its edges.

## Audit Verdict

**APPROVED.**  
There are no fatal contradictions. CoResearcher's boundaries as a pure *Traceability Engine* are shielded against editorial contamination (EditXT) and generative contamination (AI Scientists). The only minor debt is the explicit inclusion of the `QUESTION-XXXXXX` primitive in the `ARCHITECTURE_MAP` I/O diagrams.