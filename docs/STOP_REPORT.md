# Freezing and Architectural Detention Report (STOP REPORT)

**Phase:** Closing of Audit ARQ-001 → ARQ-003  
**Validity:** Next 3 Sprints (Sprints 60, 61 and 62)

---

## 1. Explicit Response to the Freezing Directive

> **"Which parts of the architecture should remain frozen for the next 3 sprints?"**

The following pieces are **STRICTLY FROZEN** and closed to any ontological modification, addition of nodes, elimination of types or restructuring of borders:

### 1. Spec & Ontology of `EvidenceGraph` (v1.1.0)
- **Status:** Frozen.
- **Prohibitions:** New node types will not be added (`Claim`, `Artifact`, `Source`, `URL` are final). No evaluation fields, scores, or intention states will be added (`ADR-DEC-002`).

### 2. Spec & Ontology of `DecisionGraph` (v1.0.0)
- **Status:** Frozen.
- **Prohibitions:** Governance relationships will not be modified (`ADR-DEC-001`). DecisionGraph will not be allowed to directly execute or store evidence.

### 3. Spec & Ontology of `MissionGraph` (v1.0.0)
- **Status:** Frozen.
- **Prohibitions:** The triad `Mission → Brief → Execution` (`ADR-EXE-001`) is fixed. No mission sub-types or alternative delivery contracts will be created.

### 4. Constitutional Rules and System Boundaries
- **Status:** Frozen.
- **Prohibitions:** The `CoResearcher ↔ EditXT` and `CoResearcher ↔ AI Scientists` borders will not allow exceptions or "special modes". The rules `ARQ-EG-001` to `ARQ-BD-004` are consolidated as immutable laws.

---

## 2. Paradigm Shift: From "Design Properties" to "Demonstrate Properties"

During Sprints 60, 61 and 62, **designing new architecture is prohibited**.

100% of the team/agents' effort will be focused on:
1. **Execute the Empirical Validation Plan (`EMPIRICAL_VALIDATION_PLAN.md`).**
2. **Pay off Critical Technical Debt (`TECHNICAL_DEBT_REGISTER.md`), starting with validator scalability and real blind testing.**
3. **Generate Empirical Evidence that frozen architecture actually works under stress and uncertainty.**

If an architectural question or temptation arises during the next 3 sprints, the default answer will be:
> *"The architecture is frozen. Let's build the data and empirical testing to answer the question about the existing model."*