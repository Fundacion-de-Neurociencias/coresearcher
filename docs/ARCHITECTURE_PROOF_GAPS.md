# Evidence Gap Audit (Architecture Proof Gaps)

**Status:** Architecture Freeze (ARQ-001 → ARQ-003)  
**Objective:** Identify which CoResearcher claims remain empirically unproven hypotheses.

| Affirmation | Existing Evidence | Missing Evidence |
| :--- | :--- | :--- |
| **"EvidenceGraph is self-sufficient to reconstruct Claims"** | Simulated blind reconstruction with a deterministic script that validates Precision/Recall on synthetic test data. | Empirical validation with double-blind human evaluators and multiple independent LLM models (Claude 3.5, Llama 3) without access to pre-prepared phrases. |
| **"DecisionGraph improves governance and prevents drift"** | Definition of the `decision_graph.yaml` scheme and registration of ADR-DEC-001. | Test real autonomous agents making sequential decisions in a continuous research environment for >48h without human supervision. |
| **"MissionGraph avoids ontological contamination"** | Constitutional rules in YAML and 7 chaos test cases executed locally in memory. | Real distributed asynchronous execution with network failures, daemon restarts, and external agents failing and retrying without corrupting state. |
| **"The Constitution detects all relevant violations"** | 7 synthetic chaos tests that pass deterministically (100% success in the 7 predetermined cases). | Massive probabilistic fuzzing generating thousands of random synthetic graphs with permutations not manually foreseen. |
| **"The Artifact supertype replaces Quote without loss of precision"** | Updated `EVIDENCEGRAPH_SPEC.md` specification to v1.1.0 accepting multimodal types. | Ingestion parsers and real validators for expression matrices, histology images, and AlphaFold PDB files. |
| **"CoResearcher is agnostic to the LLM model"** | None (current tests run with Python test scripts and static simulations). | Cross-platform comparative benchmark running the same missions with OpenAI Codex, Claude Code, Gemini and Local Llama. |
| **"Tri-graph separation does not degrade maintainability"** | Three independent YAML schemas (`constitution_rules`, `decision_graph`, `mission_graph`). | Measurement of the time and cognitive effort of an external developer to implement a new flow without violating boundaries. |