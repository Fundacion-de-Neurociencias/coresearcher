# Operational Maxims Ledger

**Version 1.0.0** - Operational Governance Registry
**Status**: Active
**Date**: 2026-08-02

---

## Purpose

This ledger registers operational maxims derived from observed patterns in CoResearcher's history. Each maxim is grounded in evidence from specific sprints, audits, or falsification results.

Maxims are not theories. They are observed regularities that constrain future action.

---

## MAXIM-001

**Statement**: Claims based on observation survive; claims based on explanation do not.

**Status**: OBSERVED

**Evidence**:
- SPRINT 70 survival table: 6/6 OBSERVED+DERIVED claims survived (100%); 0/9 HYPOTHESIZED claims survived (0%)
- SPRINT 67B adversarial OED: OED holds under HIGH complexity; HYPOTHESIZED collapses under LOW complexity

**Implication**: Prefer observation-first claims. Do not promote explanation-first claims without falsification.

---

## MAXIM-002

**Statement**: The bottleneck of CoResearcher is empirical, not conceptual.

**Status**: OBSERVED

**Evidence**:
- ARCHITECTURE_FREEZE.md: "The bottleneck of CoResearcher is no longer conceptual. It is empirical."
- SPRINT 60C: H6 validation required 20+ real repositories, not more architecture
- SPRINT 61-67A: Multiple architectural hypotheses falsified; observation-first claims survived

**Implication**: Do not add architecture. Execute experiments that produce data.

---

## MAXIM-003

**Statement**: When a hypothesis appears obvious, do not build the architecture. Define first an observable prediction that the architecture should fulfill. If the prediction cannot be formulated, the architecture is premature.

**EpistemicStatus**: DERIVED

**Evidence**:
- H7 (SPRINT 61): Constraint detector hypothesis seemed obvious; falsified (FPR=70% synthetic, kappa=-0.030)
- Instrumentability Index (SPRINT 66B/66C): Seemed obvious as a metric; falsified (collapses 6 entities to 0.60, does not separate groups, does not predict)
- AUDIT-AG-005: Context fragmentation as causal bottleneck seemed obvious; verdict YELLOW (UNDETERMINED) — no predictive test instrumented

**Epistemic split**:
- Part 1 ("when a hypothesis seems obvious, do not build the architecture"): OBSERVED — backed by repeated falsation of H7, Instrumentability Index, Context Bottleneck
- Part 2 ("if the prediction cannot be formulated, the architecture is premature"): DERIVED — methodological rule inferred from the pattern, not directly measured by any experiment

**Pattern observed**:
```text
observation
→ explanation
→ infrastructure
→ falsation
```

This cycle repeated with:
- Constraint Reconstruction
- Instrumentability Index
- Context Bottleneck

**Implication**: Before building any architecture in response to an observation, require:
1. An explicit observable prediction
2. A falsification criterion
3. A measurement plan

If any of these three cannot be formulated, the architecture is premature.

**Prohibited by this maxim**:
- Building Context Engine based on AUDIT-AG-004/005
- Building Memory Layer based on context fragmentation observation
- Building Knowledge Graph based on compilability observation
- Creating new ontologies based on pattern recognition

**Permitted by this maxim**:
- Defining predictions (e.g., P1/P2/P3 in AUDIT-AG-005)
- Designing comparative experiments (e.g., two agents, same task, different context)
- Measuring observable metrics (BLOCKED_LOOP_COUNT, TASK_COMPLETION, POLICY_VIOLATIONS, TOOL_CALLS, REPEATED_REQUESTS, TERMINATION_CORRECTNESS)

---

## Connection to COrigami Pattern (SPRINT 70)

The COrigami pattern remains the most important finding of recent sprints — not because it explains anything, but because it describes an observed structure:

```text
constraint
→ search-space reduction
→ solver
→ critic
```

Robust results in CoResearcher consistently appeared when the system acted as a **constraint engine**, not as an **explanation engine**.

The correct question is not:

```text
Do we need more context?
```

The correct question is:

```text
What observable constraint reduces the behavior space?
```

This is coherent with:
- SPRINT 61 (constraint validation)
- SPRINT 63 (reality check)
- SPRINT 67A (observation-explanation differential)
- SPRINT 70 (COrigami pattern)
- AUDIT-AG-005 (context bottleneck falsification)

---

## Version History

- v1.0.0 (2026-08-02): Initial registry. MAXIM-001, MAXIM-002, MAXIM-003 registered.

---

*This ledger registers observed operational regularities. It does not propose architecture. It does not create infrastructure. It constrains future action based on evidence.*