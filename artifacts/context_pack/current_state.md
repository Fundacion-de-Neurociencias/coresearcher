# Current State — Context Pack
**Generated**: 2026-08-02T15:06:57.678791+00:00
**Compiled by**: `sprint72_context_pack_compiler.py`

---

## Epistemic Classification Legend

- **OBSERVED**: Direct, verifiable data from project artifacts
- **DERIVED**: Logically inferred from observed data
- **INFERRED**: Hypothesis beyond current evidence — explicitly marked
- **UNKNOWN**: Cannot be determined from available data

## Active Goals

- **H6**: Decision Reconstruction — validate ≥70% reconstruction rate on real GitHub repos via authenticated pipeline
  - Source: `docs/SPRINT_60C_BRIDGE_H6_H7_EHG.md`
  - Status: pending_validated

## Knowledge Registry

- **Claims**: 9 total
  - By status: {'unvalidated': 9}
  - By type: {'biomarker': 5, 'mechanism': 2, 'association': 2}
- **Findings**: 27 total
  - By quality: {'high (>=0.7)': 1, 'medium (0.4-0.7)': 26}
- **Questions**: 9 total (9 active)
- **Combined Models**: 4
- **Memory (Neurodegeneration)**:
  - Hypotheses: 4
  - Experiments: 0
  - Failures: 0
  - Lessons: 0

## Ecosystem

### Consumer Contracts
- **geneforge** (geneforge_consumer.json): domain=genomics, trust_threshold=N/A
- **medicalia** (medicalia_consumer.json): domain=clinical-practice, trust_threshold=N/A
- **neurodiagnoses** (neurodiagnoses_consumer.json): domain=neurodegeneration, trust_threshold=N/A
- **vademecum** (vademecum_consumer.json): domain=drug-reference, trust_threshold=N/A

- **Capability registrations**: 3

### Connector Sources
- clinicaltrials: 4 registration(s)
- opentargets: 1 registration(s)
- chembl: 1 registration(s)

## Active Session: VS001

- `claims.json` (7675 bytes)
- `findings.json` (4392 bytes)
- `hypotheses.json` (616 bytes)
- `predictions.json` (903 bytes)
- `provenance.json` (236 bytes)
- `question.json` (427 bytes)
- `report.md` (2096 bytes)
- `trust_scores.json` (210 bytes)

## Trajectory Data (langchain-ai/langgraph)

- Nodes: 301
- Edges: 426
- Total decisions: 301
- Outcomes: {}
- Avg confidence: N/A
- Evidence coverage: N/A

## Cross-Repository Metrics

| Repo | Total Claims | Observable Ratio | Evidence Coverage |
|------|-------------|-----------------|-------------------|
| langchain-ai/langgraph | 841 | 0.2866 | 0.7027 |
| langchain-ai/langchain | 953 | 0.2676 | 0.7377 |
| run-llama/LlamaIndex | 0 | 0.0 | 0.0 |
| deepset-ai/haystack | 655 | 0.2885 | 0.8168 |

## SPRINT 70 Survival Table Summary

- Total claims audited: 14
- Survived: 7
- Falsified: 7
  - OBSERVED: survival_rate=1.0, falsification_rate=0.0
  - DERIVED: survival_rate=1.0, falsification_rate=0.0
  - HYPOTHESIZED: survival_rate=0.0, falsification_rate=1.0

## Convergence Review Summary

- Total convergences: 0
- Classified as real: 4
- All have ≥3 competing hypotheses: True

## SPRINT 71 Compression Ledger

| Transformation | Input → Output | Ratio | Info Loss % |
|---------------|----------------|-------|-------------|
| Raw Evidence → DecisionNode | 0 → 301 | 0 | 3.32% |
| DecisionNode → Trajectory (edge reconstruction) | 301 → 426 | 1.4153 | -47.51% |
| Trajectory → Convergence (clustering) | 301 → 4 | 0.0133 | 96.35% |
| Evidence → Gap (detection) | 301 → 155 | 0.515 | 49.17% |

## Recent Git History

- `95c1afc` — feat: SPRINT 60C trajectory reconstruction pipeline, schemas, and bridge docs
- `3745833` — security(coresearcher): purge personal and operational NeuroOS inventory/policy docs
- `15c51cd` — docs(coresearcher): sync IDENTITY_DISCOVERY_PLAYBOOK
- `883f91b` — docs(coresearcher): sync physical ACCESS_INVENTORY, MFA_STATUS, RECOVERY_DEPENDENCIES CSVs and VAULT_MIGRATION_PLAN
- `9f2e77c` — docs(coresearcher): sync NEUROOS_ACCESS_ONBOARDING
- `21f5882` — docs(coresearcher): sync NEUROOS_OPERATIONAL_IDENTITY
- `99429f4` — docs(coresearcher): sync NEUROOS_IDENTITY_DEPENDENCY_GRAPH
- `1506d88` — docs(coresearcher): sync 3-Tier Identity Classification
- `55edda9` — docs(coresearcher): sync Sovereign Identity isolation spec
- `ca245b6` — docs(coresearcher): sync NEUROOS_ROOT_IDENTITIES

## Recent Artifacts

- `compression_ledger.json` (4846 bytes)
- `sprint70_survival_table.json` (10303 bytes)
- `observation_explanation_differential.json` (4176 bytes)
- `observable_signature.json` (2626 bytes)
- `meta_measurement_audit.json` (3138 bytes)
- `instrumentability_calibration_attack.json` (3964 bytes)
- `scientific_instrumentability_matrix.json` (12515 bytes)
- `operationalization_pathways.json` (10856 bytes)
- `operationalization_framework.json` (13636 bytes)
- `scientific_constructs_reality.json` (14926 bytes)
- `scientific_instrumentability_matrix.md` (3781 bytes)
- `operationalization_counterexamples.md` (3549 bytes)
- `operationalization_framework.md` (3325 bytes)
- `constraint_stability_report.md` (5564 bytes)
- `epistemic_gap_report.md` (8339 bytes)
- `failure_taxonomy_real.md` (5002 bytes)
- `sprint59a_repository_failure_audit.md` (1703 bytes)
- `cross_repo_comparison.md` (673 bytes)
- `langgraph_trajectory_report_v1.md` (448183 bytes)
- `sprint58a_evidence_audit.md` (11650 bytes)

---

> This Context Pack is compiled automatically from existing project artifacts.
> No new entities, schemas, or graphs are created. All data is OBSERVED or DERIVED from source files.
