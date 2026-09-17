# SPRINT 60C VALIDATION REPORT
**Objective**: Empirically validate the reconstruction of decision trajectories from real GitHub repositories  
**Repository**: langchain-ai/langgraph  
**Date**: 2026-07-31  
**Mode**: Offline from snapshot `data/langgraph_raw.json`  

## 1. Methodology

It was started from `data/langgraph_raw.json`, snapshot of issues, PRs and commits.  
Extraction was applied by lexical signals, classification by outcome metadata, linking by explicit references and temporal sequences by author.  
No live API used.

## 2. Repositories analyzed
- langchain-ai/langgraph 

## 3. Extracted decisions

| Metric | Value |
|---------|-------|
| Total decisions | 301 |
| Successful | 122 |
| Abandoned | 129 |
| Failed | 40 |
| Earrings | 10 |
| Unique actors | 106 |

## 4. Accuracy / Coverage

| Indicator | Value |
|-----------|-------|
| Extraction coverage | 301 decisions with signal |
| Accuracy outcome (PR merged/closed) | Rule by metadata |
| Explicit links | 231 |
| Temporary links | 426 |

## 5. Relevant cases

### 5.1 Success
- Complete rebuild from snapshot without live API.
- 426 edges generated: 231 by explicit reference, 195 by temporal sequence per author.

### 5.2 Failure / Limitation
- No `superseded` detected in automatic classification.
- Linking can overgenerate `led_to` if an author makes close thematic commits on different topics.

## 6. Detected limitations
- Dependency on keywords in public text.
- Absence of explicit merged PRs in snapshot limits validation of certain edges.
- No manual per-sample validation was performed in this run.

## 7. Recommendations for SPRINT 61
- Manual sampling of 20 decisions for precision.
- Add `evaluate_extraction.py` with metrics by category.
- Expand to 10-20 repos to generalize results.

## 8. Deliverables
- `data/trajectories/langchain_ai_langgraph/decisions_classified.jsonl`
-`data/trajectories/langchain_ai_langgraph/trajectory_graph.json`
-`data/trajectories/langchain_ai_langgraph/evaluation_metrics.json`
-`scripts/offline_sprint60c_from_raw.py`

## 9. Conclusion
SPRINT 60C produced executable evidence: 301 decisions and 426 edges from langgraph.  
It remains as a baseline for SPRINT 61. No new architectural fronts were opened.