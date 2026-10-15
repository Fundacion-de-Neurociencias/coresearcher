# Implementation Plan: ADR-DISCOVERY-049 Audited Human Oversight & Anti-Rubber-Stamping Gate

## Goal
Implement and verify **ADR-DISCOVERY-049: Audited Human Oversight & Anti-Rubber-Stamping Gate (HITL Epistemic Integrity Protocol)** in CoResearcher.
This engine responds directly to the empirical gaps exposed in the PRISMA scoping review on generative AI in scholarly communication:
1. Passive automation bias and rubber-stamping (approving AI verdicts without cognitive inspection).
2. Epistemic consensus bias (LLMs penalizing heterodox/novel scientific hypotheses simply because they depart from majority literature frequency).
3. Lack of cryptographically verifiable provenance between AI recommendations and human decisions in peer-review and editorial flows.

## Blocking Questions
None (0 blocking questions). All contracts are well-specified and integrate cleanly with existing CoResearcher engines (`ScientificLedger`, `EpistemicGitRepo`, `api/server.py`).

## Assumptions
1. *Data*: Editorial interactions consist of AI-generated assessment reports, proposed verdicts (accept/reject/revise), flagged anomalies/violations, and human interaction telemetry (dwell time, inspectable counterexamples examined, modification deltas).
2. *Failure Mode*: If an editorial decision is signed in trivial dwell time (< minimum cognitive threshold) without inspecting flagged discrepancies or providing causal rationale, the oversight gate flags `RUBBER_STAMPING_DETECTED` and demands explicit human counterexample adjudication before finalizing.
3. *Consensus Bias Protection*: When an AI recommendation rejects a claim solely due to divergence from consensus literature rather than physical/mathematical conservation violation, the gate forces human escalation with `CONSENSUS_BIAS_ALERT`.
4. *Language Invariant*: 100% English across code, comments, docstrings, and documentation. Zero Spanish in repository files.
5. *Testing*: 100% pass rate on test suites verifying rubber-stamp trapping, cognitive inspection proofs, consensus bias neutralization, and ledger Merkle hashing.

## Plan
1. **Document Architectural Decision**:
   - Create `docs/decisions/ADR-DISCOVERY-049-AUDITED-HUMAN-OVERSIGHT-GATE.md`.
   - Update `docs/CONSTITUTION_INDEX.md`.
2. **Implement Engine**:
   - Create `python/discovery/audited_human_oversight.py`:
     - `OversightVerdictStatus` enum (`ACTIVE_OVERSIGHT_VERIFIED`, `RUBBER_STAMPING_DETECTED`, `CONSENSUS_BIAS_INTERCEPTED`, `COGNITIVE_PROOF_REQUIRED`).
     - `HumanInteractionTelemetry` dataclass (dwell time seconds, counterexamples inspected, delta edits, rationale).
     - `OversightAuditRecord` dataclass with cryptographic Merkle proof.
     - `AuditedHumanOversightEngine` class:
       - `evaluate_oversight_integrity(...)`: audits human decision against AI recommendation.
       - `detect_consensus_bias(...)`: checks if AI rejection is ungrounded statistical frequency bias.
       - `generate_cognitive_inspection_challenge(...)`: creates targeted adversarial multiple-choice / counterexample verification challenge for human reviewers.
3. **Integrate with Existing Systems**:
   - Update `python/discovery/__init__.py`: export new symbols.
   - Add REST API endpoint in `api/server.py` (`POST /api/discovery/oversight/audit`).
4. **Verification & Testing**:
   - Create `tests/test_audited_human_oversight.py`.
   - Run tests with pytest.
   - Run `python scripts/enforce_english_policy.py`.
5. **Git Commit**: Commit directly to `master` with conventional message.
