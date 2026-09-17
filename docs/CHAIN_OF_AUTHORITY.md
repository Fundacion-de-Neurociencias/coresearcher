# NeuroOS Chain of Authority and Jurisdiction (CHAIN OF AUTHORITY)

**Version:** 2.0.0  
**Governance:** Canonical Constitutional Directive  
**State:** Inviolable  

---

## 1. The Three Independent Networks

To avoid operational bottlenecks and data duplication, NeuroOS explicitly differentiates three chains:

### 1.1 Chain of Authority (Immutable)
Responds to: *Who can authorize, revoke or delegate?*
```text
Manuel (Nivel 0) ──> ManuEl (Nivel 1) ──> Antigravity (Nivel 2) ──> Subagentes (Nivel 3)
```

### 1.2 Execution Chain (Variable / Direct)
Once the authorization or lease is valid, the execution is direct without unnecessary intermediaries.
```text
Subagente ───────> GitHub / Tool / File API (Directo)
Antigravity ────> Gmail / Workspace API (Directo tras aprobación)
ManuEl ─────────> Filesystem Local (Directo)
```

### 1.3 Chain of Evidence (Independent)
Every action executed writes its event directly and immutably in the audit log.
```text
Ejecutor (Subagente / Antigravity / ManuEl) ──> Audit Trail (audit_trail.jsonl)
```

---

## 2. Fundamental Axiom of Separation of Functions

> **Manuel has the Authority.** (Sole Sovereign).  
> **ManuEl has Jurisdiction.** (Policy Engine / Leases / Audit on Lenovo).  
> **Antigravity has the Initiative.** (Planning / Orchestration / Development in Mac Studio).  
> **Subagents have Execution.** (Specific tasks).  

---

## 3. Failure Modes and Jurisdiction Availability (Degraded Mode)

### Availability Paradox
If the local Lenovo node (ManuEl / IA Local) is powered off or unavailable, NeuroOS automatically enters **Degraded High Availability Mode** to avoid development blocking.

```text
Lenovo / ManuEl ONLINE  ──> Policy Engine Normal (Zonas: BLACK, CRITICAL, CONTROLLED, AUTONOMOUS)
Lenovo / ManuEl OFFLINE ──> Modo Degradado Activado (Solo Zonas AUTONOMOUS permitidas)
```

### Availability Matrix in Degraded Mode (Lenovo Offline)

| Risk Zone | Status with ManuEl Offline | Reason and Behavior |
| :--- | :---: | :--- |
| **🟢 AUTONOMOUS** | **ALLOWED** | Antigravity continues to work autonomously on code, development, testing, CI/CD and documentation repositories (`Medicalia`, `CoResearcher`, `Editxt`, `GeneForge`, `Neurodiagnoses`, etc.). |
| **🟠 CONTROLLED_LOW** | **LOCKED** | Jurisdiction evaluation required; It is suspended until connection with ManuEl is recovered. |
| **🟠 CONTROLLED_HIGH**| **LOCKED** | Requires explicit human approval from Manuel/ManuEl. |
| **🔴 CRITICAL** | **LOCKED** | Requires exclusive execution in ManuEl + IA Local. |
| **⚫ BLACK** | **LOCKED** | Unreachable access. |