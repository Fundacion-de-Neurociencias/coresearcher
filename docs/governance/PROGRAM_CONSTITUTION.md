# Research Program Constitution

**Version 1.0.0** - Foundational Organizational Primitive  
**Status**: Constitutional Document - Core Governance

---

## Article I: The Nature of a Research Program

### Section 1. Definition

A **Research Program** is the fundamental organizational unit of scientific production in CoResearcher.

It is NOT:
- ❌ A repository (storage artifact)
- ❌ A project (temporary initiative)
- ❌ A dataset (data collection)
- ❌ A paper (publication artifact)

It IS:
- ✅ A sustained intellectual commitment to a scientific question
- ✅ A structured approach to investigating a domain problem
- ✅ A lineage of claims, mechanisms, and evidence under unified direction
- ✅ An anchored entity in the canonical scientific ontology

### Section 2. Canonical Identity

Every Research Program receives a permanent, globally unique identifier:

```
PROGRAM-XXXXXX
```

This identifier is derived from and anchored to the **CoResearcher Scientific Ontology (CSO)** namespace:

```
Science/Medicine/Neurology/Alzheimer's Disease/Biomarkers → PROGRAM-000421
Science/Medicine/Neurology/Alzheimer's Disease/Tau Pathology → PROGRAM-000422
Science/Medicine/Neurology/Parkinson Disease → PROGRAM-000423
```

**No duplication**: There is only one canonical PROGRAM per ontological path.

---

## Article II: Authority and Creation

### Section 1. Creation Authority

**Who can create new Research Programs?**

- **Answer**: Only authorized ontological curators with explicit domain stewardship.

Creation requires:
1. **Ontological Placement**: The program must map to an existing CSO node or a proposed new node with justified scientific necessity.
2. **Non-Duplication Verification**: No existing program covers the same ontological ground.
3. **Domain Steward Approval**: A steward for the parent domain must approve the request.
4. **Lead Researcher Assignment**: A RES-XXXXXX identifier must be designated as program lead.

### Section 2. Creation Process

```
1. Proposal submitted with ontological justification
2. Steward review for domain alignment
3. Duplicate check against existing programs
4. Ontology curator approval for namespace placement
5. PROGRAM-XXXXXX issued with canonical URI
6. Team structure initialized under scientific namespace
```

### Section 3. Emergency Fork Protocol

When evidence reveals an existing program's scope was misaligned:

- New sub-program creation is allowed within the same parent domain
- Original program lead retains authority over primary trajectory
- Fork requires justification and documentation

---

## Article III: Program Lifecycle

### Section 1. Status States

| State | Meaning | Transition Criteria |
|-------|---------|-------------------|
| **Prospective** | Proposed, not yet active | Approved by steward |
| **Active** | Currently producing knowledge | Lead assigned, resources allocated |
| **Maintained** | Stable, ongoing monitoring | Continuous evidence flow |
| **Archived** | Completed or superseded | No activity for 12+ months |
| **Deprecated** | Scientifically invalidated | Contradicted by superior program |

### Section 2. Division Criteria

A program splits when:

- **Research divergence**: Two distinct approaches emerge that cannot share methodology
- **Scale threshold**: >100 active researchers/agents; coordination overhead exceeds benefit
- **Ontological clarity**: Evidence shows the original scope was two separate phenomena

Division process:
1. Ontological analysis to identify split points
2. Lead researcher consultation and assignment to each branch
3. Artifact migration with provenance preservation
4. Original program archived or deprecated

### Section 3. Fusion Criteria

Two programs merge when:

- **Overlapping mission**: >80% question overlap with complementary evidence
- **Resource efficiency**: Combined activity reduces duplication
- **Scientific convergence**: Evidence shows unified mechanism

Merge process:
1. Joint steward approval
2. Trust score reconciliation
3. Artifact deduplication with lineage preservation
4. New program-ontology node creation if needed

### Section 4. Discontinuation

A program may be archived when:
- Question answered to practical consensus (TI ≥ 90)
- Scientific field abandonment
- Resource reallocation by lead

Archived programs remain queryable but inactive.

---

## Article IV: Multi-Domain Membership

### Section 1. Poly-Domain Participation

**Can a program belong to multiple domains?**

Yes, with limitations:

- Primary domain: One canonical ontological parent
- Secondary domains: Up to 3 additional affiliations
- Each affiliation must have steward approval

Example:
```
PROGRAM-000421 (Alzheimer Biomarkers)
├── Primary: Science/Medicine/Neurology/Alzheimer's Disease
├── Secondary: Science/Medicine/Radiology  # amyloid PET
├── Secondary: Science/Life Sciences/Genomics  # APOE4 biomarkers
└── Secondary: Science/Methods/Statistics  # biomarker validation methods
```

### Section 2. Cross-Domain Conflict Resolution

When domain stewards disagree on program placement:
1. Ontological analysis by CSO curators
2. Scientific impact assessment
3. Lead researcher preference given weight
4. Appeal to Ontology Council if unresolved

---

## Article V: Relationship to Ontology

### Section 1. Ontological Anchoring

Every program MUST be anchored to an ontological node:

```text
Science
└── Medicine
    └── Neurology
        └── Alzheimer's Disease
            └── [PROGRAM HERE]
```

Benefits:
- Eliminates duplicate programs
- Enables discovery by ontological traversal
- Guarantees coherent scientific hierarchy
- Prevents taxonomy fragmentation

### Section 2. Ontology Evolution

When CSO evolves:

- Programs automatically inherit new parent-child relationships
- No program ID changes (permanent identity)
- Redirect mappings handled for deprecated nodes
- Historical queries preserved

---

## Article VI: Team Structure and Governance

### Section 1. Team Composition

```
PROGRAM-XXXXXX
├── Lead: RES-XXXXXX (1)
├── Co-Leads: RES-XXXXXX (0-3)
├── Researchers: RES-XXXXXX (unlimited)
├── Agents: AGENT-XXXXXX (unlimited)
└── Institutional Support: INST-XXXXXX (0-many)
```

### Section 2. Leadership Transitions

- Lead can designate successor from active researchers
- Steward approval required for external lead assignment
- Co-Leads can maintain continuity during transitions
- Former leads become Emeritus with read access

### Section 3. Activity Streams

All program activity is recorded as:

- **ACTIONS**: Verifiable operations (PROPOSE_MECHANISM, GENERATE_HYPOTHESIS, etc.)
- **CLAIMS**: Assertions produced under program auspices
- **MECHANISMS**: Proposed causal explanations
- **PREDICTIONS**: Testable expectations

Each links explicitly to PROGRAM-XXXXXX for provenance.

---

## Article VII: Knowledge Strategy Integration

### Section 1. Strategy States

Programs operate under one of four knowledge strategies:

```
Private → Protected → Patent Pending → Published → Consensus
```

Strategy governs:
- Who can view program artifacts
- What dissemination is permitted
- How contributions are credited
- When ontology updates cascade

### Section 2. Strategy Transitions

Managed by Lead with optional steward consultation:
- Private → Protected: When seeking selective collaboration
- Protected → Patent Pending: When commercial potential identified
- Patent Pending → Published: After filing (embargo lift)
- Published → Consensus: When TI ≥ 90 achieved

All transitions logged with justification.

---

## Article VIII: Lock-In Strategy

### Section 1. Strategic Asset Recognition

The program registry becomes the core lock-in because:

- **Claims** anchor to program lineage
- **Mechanisms** derive from program questions
- **Reviews** validate program outputs
- **Actions** execute under program authority
- **Researchers** build reputation within programs

### Section 2. Migration Constraints

After 1M+ actions accumulated:

- Scientific process history becomes non-portable
- Trust scores depend on program context
- Reputation is program-relative
- Ontology relationships crystallize

This is intentional. CoResearcher captures the scientific process, not just its output.

---

## Article IX: Implementation Requirements

### Section 1. Before Any Repository Design

All of the following MUST be defined:

- [x] PROGRAM identity and lifecycle
- [x] Ontology anchoring rules
- [x] Creation authority boundaries
- [x] Division/fusion criteria
- [x] Multi-domain policies
- [x] Team governance structure
- [x] Knowledge strategy integration

Only then can repositories, workflows, or MCP integrations be properly designed.

---

## Article X: Future Evolution

This constitution defines the organizational foundation. Changes require:

1. **Scientific impact assessment**
2. **Ontological consistency check**
3. **Steward council review**
4. **Community consultation (7 days)**

---

*This constitution establishes PROGRAM as the atomic unit of scientific organization in CoResearcher. Without this foundation, all downstream structures fragment and fail to capture the unity of scientific inquiry.*