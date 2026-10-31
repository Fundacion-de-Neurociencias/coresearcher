# ADR-DISCOVERY-072: Tri-Phase Reasoning Bridge (Wolfram AST to Lean 4 Microkernel)

## Status
ACCEPTED / IMPLEMENTED

## Date
2026-10-23

## Context
Formulating mathematical proofs for complex dynamical systems requires crossing the chasm between intuitive natural language claims, symbolic discrete exploration (Wolfram Language ASTs), and mechanical proof assistant kernels (Lean 4). Without an intermediate barrier filter, AI provers flood Lean 4 with false or unprovable conjectures.

## Architectural Decision
We implement **`Rule30ReasoningBridge`** in `python/discovery/rule30_reasoning_bridge.py`:
1. **Phase 1: Bitmask Strip Certificate Exploration**:
   - Parses candidates into binary bitmasks and evaluates spatial boundary extensions.
2. **Phase 2: Degenerate Realization Barrier Auditing**:
   - Applies `CellularAutomataBarrierAuditor` (ADR-DISCOVERY-070) to reject invariants shared with linear/additive rules (Rule 90, Rule 150).
3. **Phase 3: Automated Lean 4 Code Generation & Remote Replay**:
   - Generates machine-checkable Lean 4 code (`Rule30Submission.lean`) and invokes remote microkernel replay on Mac Studio node (`mac_studio`) via `Check.lean`.

## Consequences
- Guarantees that only structurally sound and non-trivial invariants reach the Lean 4 microkernel.
- Connects Wolfram Language ASTs directly to Mathlib formal proofs.
