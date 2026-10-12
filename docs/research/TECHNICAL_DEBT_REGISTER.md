# Technical Debt Register

**Status:** Architecture Freeze (ARQ-001 → ARQ-003)  
**Objective:** Consolidate and prioritize by risk all warnings, limitations and inefficiencies identified in the system.

---

## Priority 1: Critical Risk (Impacts Scalability and Production)

### `DEBT-001`: Slow In-Memory Validation for Large Graphs
- **Description:** The `validate_constitution.py` validator processes JSON lists in memory using sequential iteration. In synthetic tests, 10,000 nodes required ~53 seconds. At 100,000 nodes the process fails due to timeout/memory.
- **Risk:** Severe bottleneck that prevents the use of the system on an industrial scale.
- **Planned Mitigation:** Migrate the validation execution to an indexed engine (SQLite / DuckDB / Graph engine) without changing the schema rules.

---

## Priority 2: High Risk (Impacts Rigor and Fidelity)

### `DEBT-002`: Blind Reconstruction Based on Deterministic Simulations
- **Description:** `advanced_claim_reconstruction.py` tests use simulated prompts and prefixed static phrases to validate Precision/Recall.
- **Risk:** False sense of security. It has not been tested whether a real non-deterministic LLM hallucinates when receiving the isolated text graph.
- **Planned Mitigation:** Replace the script mock with real calls in blind mode to LLM APIs in the empirical validation suite.

### `DEBT-003`: Multimodality of `Artifact` Not Implemented in Parsers
- **Description:** Although `EVIDENCEGRAPH_SPEC.md` v1.1.0 defines the `Artifact` supertype to support images, tables and 3D structures (PDBs), there are currently no actual parsers or converters for these types of objects in the code.
- **Risk:** Multimodal support is only theoretical in the specification and will fail if a real binary is ingested.
- **Planned Mitigation:** Build test parsers for biomedical artifacts (e.g. AlphaFold PDB files).

---

## Priority 3: Medium Risk (Impacts Coverage and Ergonomics)

### `DEBT-004`: Non-existent Constitutional Fuzzing
- **Description:** Chaos Tests consist of 7 manually written static test cases.
- **Risk:** An unanticipated edge case (e.g., combination of cycles with non-standard nodes) could bypass constitutional validation.
- **Planned Mitigation:** Implement a stochastic graph generator (fuzzer) to subject the validator to 10,000 random permutations.

### `DEBT-005`: No Persistence Queue for `MissionGraph`
- **Description:** The
- **Risk:** If the orchestrator restarts, missions in progress are lost.
- **Planned Mitigation:** Implement lightweight state storage for the execution layer.

---

## Priority 4: Low Risk (Hygiene and Compatibility)

### `DEBT-006`: `cp1252` Encoding Dependency on Windows
- **Description:** Scripts that print to the console (such as the scalability benchmark or the `skillspector` CLI) fail to render UTF-8 characters/emojis if `$env:PYTHONUTF8=1` is not forced.
- **Risk:** Annoying errors in CLI execution in Windows environments without UTF-8 by default.
- **Planned Mitigation:** Force explicit handling of `utf-8` encoding on all stream/console outputs.