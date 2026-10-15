# DECISION & EXECUTION REGISTRY
**Version 1.0.0** - Semantic Traceability for Agent Actions  
**Status**: Strategic Component  
**Platforms**: NeuroOS (ManuEl, Antigravity, future agents)

---

## 1. Core Insight

Inspired by Paperclip's approach to agent governance, but elevated to the institutional knowledge level:

> **Every meaningful change has an actor, an intention, and evidence.**

This is not about multi-agent orchestration.

It is about **semantic traceability of decisions**.

---

## 2. The Problem It Solves

As organizations scale, documentation diverges from operational reality:

```
Documentation ≠ Operational Knowledge

What we document:
  - README files
  - Architecture diagrams
  - Policy documents

What actually happened:
  - Conversations
  - Pull requests
  - Commits
  - Tickets
  - Technical decisions
  - Historical corrections
  - Tacit knowledge
```

**The core issue**: AI systems only see documentation, not operational reality.

---

## 3. The Pattern: Action as Semantic Unit

### 3.1 From Commit to Decision

Traditional systems:
```
git commit -m "Enable Tailscale SSH"
```

NeuroOS pattern:
```yaml
decision_id: D-2026-0045

actor:
  agent: Antigravity
  authorized_by: ManuEl  # Chain of Authority

objective:
  Enable Tailscale SSH for remote development

jurisdiction:
  domain: infrastructure
  owned_by: ManuEl
  approved_by: Manuel

changes:
  - file: install_sshd.ps1
    action: created
  - file: firewall_rules.yaml
    action: modified
  - service: tailscale
    action: enabled

result:
  status: success
  completed_at: 2026-07-30T18:00:00Z

evidence:
  - type: commit
    hash: abc123def456
    repository: neuroos/infrastructure
  - type: logs
    source: antigravity_execution.log
    checksum: sha256:789abc...
  - type: screenshots
    - ssh_connection_test.png
  - type: audit_trail
    entry: AT-2026-07-30-001

artifacts:
  - install_sshd.ps1
  - firewall_rules.yaml
  - tailscale_config.json

policy_compliance:
  policy_id: INFRA-001
  status: compliant
  verification: automated_test_passed

related_decisions:
  - D-2026-0034  # Previous Tailscale installation
  - D-2026-0042  # Windows Server hardening
```

---

## 4. Registry Architecture

### 4.1 Two Registries, One Pattern

```
┌─────────────────────────────────────────────┐
│         Decision Registry                    │
│  - What we decided to do                    │
│  - Why we decided it                        │
│  - Who authorized it                        │
│  - What evidence supports it                │
└──────────────────┬──────────────────────────┘
                   │
                   │ spawns
                   ▼
┌─────────────────────────────────────────────┐
│        Execution Registry                    │
│  - How we executed it                       │
│  - What changed                             │
│  - What artifacts were produced             │
│  - What the result was                      │
└─────────────────────────────────────────────┘
```

### 4.2 Decision Registry Schema

```typescript
interface Decision {
  decision_id: string          // D-YYYY-NNNN
  timestamp: Date
  
  // Actors & Authority
  actor: {
    agent: string              // Antigravity, ManuEl, Manuel
    type: 'human' | 'agent'
    orcid?: string             // If human
  }
  
  authorized_by: {
    agent: string              // Chain of Authority
    role: 'owner' | 'approver' | 'reviewer'
    approval_timestamp?: Date
  }
  
  // Intent
  objective: string
  rationale: string
  
  // Context
  jurisdiction: {
    domain: string             // infrastructure, research, clinical
    scope: string[]            // Specific systems/artifacts
    authority_level: number    // 1-5
  }
  
  // Evidence of decision
  evidence: EvidenceReference[]
  
  // Policy compliance
  policy_compliance: PolicyCheck[]
  
  // Lifecycle
  status: 'proposed' | 'approved' | 'executing' | 'completed' | 'rejected' | 'superseded'
  superseded_by?: string      // D-YYYY-NNNN if superseded
  
  // Links
  related_decisions: string[]
  spawned_executions: string[] // EX-YYYY-NNNN
}

interface EvidenceReference {
  type: 'commit' | 'ticket' | 'conversation' | 'document' | 'screenshot' | 'test_result'
  identifier: string           // commit hash, ticket ID, message ID
  source: string               // Repository, system
  checksum?: string            // SHA-256 for integrity
  timestamp: Date
}
```

### 4.3 Execution Registry Schema

```typescript
interface Execution {
  execution_id: string         // EX-YYYY-NNNN
  decision_id: string          // Parent decision
  
  actor: {
    agent: string
    type: 'human' | 'agent'
  }
  
  // What changed
  changes: Change[]
  
  // What was produced
  artifacts: Artifact[]
  
  // Result
  result: {
    status: 'success' | 'partial' | 'failure'
    started_at: Date
    completed_at: Date
    duration_ms: number
    error?: string
  }
  
  // Evidence of execution
  evidence: ExecutionEvidence[]
  
  // Provenance
  tool_calls: ToolCall[]
  logs: LogReference[]
  
  // Links to decision
  decision: Decision
}

interface Change {
  target: {
    type: 'file' | 'service' | 'configuration' | 'database'
    path: string
    identifier: string
  }
  
  action: 'created' | 'modified' | 'deleted' | 'enabled' | 'disabled'
  
  diff?: string                // Patch or diff content
  before_checksum?: string
  after_checksum?: string
  
  timestamp: Date
}

interface Artifact {
  type: 'code' | 'document' | 'test' | 'configuration' | 'binary'
  path: string
  identifier: string           // SHA-256 hash
  
  metadata: Record<string, unknown>
}

interface ExecutionEvidence {
  type: 'log' | 'screenshot' | 'test_output' | 'metric' | 'verification'
  content: string              // Base64 for binary, text for logs
  checksum: string
  timestamp: Date
}
```

---

## 5. Integration with Existing Systems

### 5.1 Chain of Authority

```
Decision Registry ↔ Chain of Authority
  - Decision requires authorization
  - Authorization recorded in decision
  - Policy rules enforced before approval

Example:
  Decision: "Enable Tailscale SSH"
    ↓ requires authorization
  ManuEl approves (owner of infrastructure domain)
    ↓ recorded in
  authorized_by field
```

### 5.2 Audit Trail

```
Decision/Execution → Audit Trail
  - Every mutation is an audit event
  - Audit events reference decisions
  - Full replay possible from audit trail alone

Example:
  Execution: "Configure firewall"
    → emits audit event: AT-2026-07-30-001
    → audit event references: EX-2026-0045
    → audit event references: D-2026-0045
```

### 5.3 Evidence Registry

```
Decision/Execution → Evidence Registry
  - Artifacts registered in Evidence Registry
  - Evidence references link to EVID-XXXXXX
  - Cross-platform evidence linking

Example:
  Decision: "Enable Tailscale SSH"
    → produces artifact: firewall_rules.yaml
    → registered as: EVID-000042
    → referenced in: decision.evidence[]
```

### 5.4 Provenance Engine

```
Execution → Provenance Engine
  - Tool calls tracked
  - Data lineage computed
  - Cryptographic signatures

Example:
  Execution: "Configure firewall"
    → tool calls: [PowerShell, netsh]
    → data lineage: config_template → firewall_rules.yaml
    → signed provenance record
```

---

## 6. Workflow Pattern

### 6.1 Typical Flow

```
1. REQUEST (Manuel/ManuEl/Antigravity)
   ↓
2. DECISION CREATED
   - Objective defined
   - Evidence gathered
   - Rationale documented
   ↓
3. AUTHORIZATION (Chain of Authority)
   - Approver identified
   - Policy check
   - Approval recorded
   ↓
4. EXECUTION (Antigravity)
   - Plan created
   - Changes tracked
   - Artifacts produced
   - Evidence collected
   ↓
5. VERIFICATION (automated/test)
   - Tests run
   - Results recorded
   ↓
6. COMPLETION
   - Decision marked: completed
   - Execution marked: success
   - All evidence linked
   ↓
7. PUBLICATION (optional)
   - Zenodo DOI for decision+evidence
   - Cross-referenced in publications
```

### 6.2 Example: Gmail OAuth Implementation

```yaml
# Step 1: REQUEST
requestor: Manuel
request: "Implement Gmail OAuth for ManuEl"

# Step 2: DECISION
decision_id: D-2026-0046
actor: ManuEl
authorized_by: Manuel
objective: "Enable secure Gmail access via OAuth 2.0"

# Step 3: AUTHORIZATION
approved_by: Manuel
approval_timestamp: 2026-07-30T10:00:00Z

# Step 4: EXECUTION
execution_id: EX-2026-0047
actor: Antigravity
authorized_by: ManuEl

changes:
  - file: gmail_client.py
    action: created
    content: |
      class GmailOAuthClient:
          def authenticate(self):
              # OAuth flow
              ...
  
  - file: tests/test_gmail.py
    action: created
    content: |
      def test_oauth_flow():
          client = GmailOAuthClient()
          assert client.authenticate()
  
  - file: config/secrets.yaml
    action: modified
    changes:
      - added: gmail_client_id
      - added: gmail_client_secret

artifacts:
  - gmail_client.py
  - tests/test_gmail.py
  - config/secrets.yaml

evidence:
  - type: commit
    hash: def789abc123
    repository: neuroos/manuel
  - type: test_output
    content: "3 passed, 0 failed"
    timestamp: 2026-07-30T11:30:00Z
  - type: log
    source: antigravity_execution.log
    checksum: sha256:456def...

result:
  status: success
  duration_ms: 45000

# Step 5: VERIFICATION
policy_compliance:
  - policy: INFRA-003 (OAuth standards)
    status: compliant
  - policy: SEC-001 (Secrets management)
    status: compliant

# Step 6: COMPLETION
decision.status: completed
execution.status: success

# Step 7: PUBLICATION (optional)
published_to:
  zenodo: 10.5281/zenodo.1234568
  timestamp: 2026-07-30T12:00:00Z
```

---

## 7. Registry Storage & Queries

### 7.1 Storage Structure

```
decisions/
├── D-2026-0045.yaml
├── D-2026-0046.yaml
└── D-2026-0047.yaml

executions/
├── EX-2026-0045.yaml
├── EX-2026-0046.yaml
└── EX-2026-0047.yaml

index/
├── by_actor.json          # Who did what
├── by_domain.json         # What happened in domain X
├── by_date.json           # Timeline view
├── by_policy.json         # Compliance tracking
└── by_artifact.json       # What touched asset Y
```

### 7.2 Standard Queries

```typescript
interface DecisionQueries {
  // Actor queries
  getDecisionsByActor(actor: string, timeRange?: TimeRange): Promise<Decision[]>
  getAuthorizationsByApprover(approver: string): Promise<Decision[]>
  
  // Domain queries
  getDecisionsByDomain(domain: string): Promise<Decision[]>
  getExecutionsByJurisdiction(jurisdiction: string): Promise<Execution[]>
  
  // Artifact queries
  getDecisionHistory(artifactPath: string): Promise<Decision[]>
  getExecutionsTouchArtifact(artifactId: string): Promise<Execution[]>
  
  // Evidence queries
  getEvidenceChain(decisionId: string): Promise<EvidenceReference[]>
  getVerificationStatus(executionId: string): Promise<VerificationResult>
  
  // Temporal queries
  getTimeline(from: Date, to: Date): Promise<Decision[]>
  getLastChange(artifactPath: string): Promise<Decision>
  
  // Policy queries
  getPolicyViolations(): Promise<PolicyViolation[]>
  getComplianceRate(domain: string): Promise<number>
}
```

---

## 8. Integration with Agents

### 8.1 ManuEl Pattern

```
Objective received from Manuel
    ↓
ManuEl creates DECISION
  - objective: clear statement
  - evidence: gathered context
  - rationale: why this approach
    ↓
ManuEl requests authorization (if needed)
  - authorized_by: Manuel or delegated
    ↓
ManuEl authorizes EXECUTION
  - execution_id assigned
  - spawned for Antigravity
    ↓
ManuEl monitors execution
  - real-time updates
  - policy compliance checks
  - verification gates
    ↓
ManuEl completes DECISION
  - result: success/failure
  - evidence: all collected
  - artifacts: registered
```

### 8.2 Antigravity Pattern

```
Received: EXECUTION
  decision_id: D-2026-0046
  actor: Antigravity
  authorized_by: ManuEl
    ↓
Antigravity plans changes
  - file list
  - command list
  - rollback plan
    ↓
Antigravity executes (tracked)
  - each tool call logged
  - each change recorded
  - each artifact captured
  - each verification run
    ↓
Antigravity produces EXECUTION record
  - all changes listed
  - all evidence collected
  - result reported
    ↓
ManuEl verifies
  - automated tests
  - policy compliance
  - manual approval (if needed)
    ↓
EXECUTION marked: verified
DECISION marked: completed
```

### 8.3 Future Agents Pattern

Any future agent (e.g., Clinical Oracle, PharmaOracle) must:

1. **Request decisions** before making changes
2. **Track executions** with full evidence
3. **Record evidence** in Evidence Registry
4. **Respect Chain of Authority**
5. **Emit audit events** to Audit Trail

```typescript
// Agent template
class NeuroOSAgent {
  async execute(objective: string): Promise<void> {
    // 1. Request decision
    const decision = await this.requestDecision({
      objective,
      rationale: this.generateRationale(objective),
      evidence: await this.gatherEvidence(objective)
    })
    
    // 2. Wait for authorization
    await this.waitForAuthorization(decision.id)
    
    // 3. Execute with tracking
    const execution = await this.startExecution(decision.id)
    
    try {
      const changes = await this.planChanges(objective)
      await this.recordChanges(changes)
      
      const artifacts = await this.implementChanges(changes)
      await this.captureArtifacts(artifacts)
      
      const evidence = await this.collectEvidence(artifacts)
      await this.recordEvidence(evidence)
      
      await this.completeExecution(execution.id, { status: 'success' })
      await this.completeDecision(decision.id)
      
    } catch (error) {
      await this.failExecution(execution.id, error)
      await this.failDecision(decision.id)
    }
  }
}
```

---

## 9. Decision Registry Benefits

### 9.1 For Manuel (User)

```text
Q: "Why did we enable Tailscale SSH?"
A: Decision D-2026-0045, authorized by Manuel on 2026-07-30,
   evidence: commit abc123, logs: antigravity_execution.log
   rationale: "Enable remote development for Windows Server"
```

```text
Q: "What changed in infrastructure last month?"
A: 47 decisions, 23 executions, 100% compliance with INFRA policies
```

### 9.2 For ManuEl (Orchestrator)

```text
Q: "What have I delegated to Antigravity?"
A: 156 decisions, 94% success rate, avg 45s execution time
   Current status: 2 executing, 1 pending approval
```

### 9.3 For Antigravity (Agent)

```text
Q: "What is my context for this task?"
A: 
  - Related decisions: D-2026-0042, D-2026-0045
  - Similar executions: EX-2026-0046, EX-2026-0048
  - Evidence base: firewall_rules.yaml v2.3
  - Policy constraints: INFRA-003, SEC-001
```

### 9.4 For NeuroOS Brain (Company Brain)

```text
Q: "What does the organization know about Tailscale?"
A:
  Decisions: 12
  First: D-2025-0034 (pilot)
  Last: D-2026-0045 (production rollout)
  Artifacts: 34 files
  Evidence: 156 commits, 89 tests, 12 screenshots
  Authors: Manuel (5), ManuEl (12), Antigravity (34)
```

---

## 10. Implementation Roadmap

### Phase 1: Foundation (Sprint 61-62)

```yaml
Goals:
  - Define Decision/Execution schemas
  - Implement basic registry (JSON/YAML storage)
  - Integrate with Chain of Authority
  - Basic CLI tool
```

### Phase 2: Integration (Sprint 63-64)

```yaml
Goals:
  - Integrate with Audit Trail
  - Integrate with Evidence Registry
  - Integrate with Provenance Engine
  - ManuEl integration (decision creation)
  - Antigravity integration (execution tracking)
```

### Phase 3: Agentification (Sprint 65-66)

```yaml
Goals:
  - Generic agent SDK (requestDecision, recordExecution)
  - Policy engine integration
  - Automated verification
  - Zenodo publication (optional DOI per decision)
```

### Phase 4: Intelligence (Sprint 67-68)

```yaml
Goals:
  - Decision pattern detection
  - Similarity search (find similar past decisions)
  - Automated rationale generation
  - NeuroOS Brain integration (knowledge graph)
```

---

## 11. Relationship to Existing Documents

This registry pattern **unifies** existing NeuroOS components:

```
Decision Registry
  ├── Uses Chain of Authority (for authorization)
  ├── Uses Policy Engine (for compliance)
  ├── Uses Audit Trail (for mutations)
  ├── Uses Evidence Registry (for artifacts)
  ├── Uses Provenance Engine (for lineage)
  └── Feeds NeuroOS Brain (for organizational knowledge)

Execution Registry
  ├── Uses Decision Registry (parent record)
  ├── Uses Audit Trail (for change tracking)
  ├── Uses Evidence Registry (for artifacts)
  ├── Uses Provenance Engine (for tool calls)
  └── Feeds NeuroOS Brain (for operational reality)
```

---

## 12. The Strategic Win

**What we get:**

1. **Semantic Traceability**: Not just commits, but *intent*
2. **Institutional Memory**: Every decision preserved with context
3. **Accountability**: Clear Chain of Authority for every change
4. **Compliance**: Automated policy checking
5. **Knowledge OS**: Operational reality becomes computable
6. **Auditability**: Complete replay capability

**What we avoid:**

- ❌ Building yet another agent orchestration framework
- ❌ Reinventing multi-agent communication
- ❌ Creating siloed knowledge in each agent's memory

**What we achieve:**

- ✅ **NeuroOS Brain**: Institutional knowledge that persists beyond agents
- ✅ **Decision lineage**: Why we did what we did
- ✅ **Execution evidence**: How we did it
- ✅ **Verification trail**: Proof it worked

---

*This document defines the Decision & Execution Registry pattern. It is the semantic layer that transforms NeuroOS from a tool coordination platform into a Knowledge OS.*