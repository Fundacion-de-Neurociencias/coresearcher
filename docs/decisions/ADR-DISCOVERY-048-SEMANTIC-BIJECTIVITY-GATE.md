# Implementation Plan: ADR-DISCOVERY-048 Semantic Bijectivity & Formal Drift Auditor

## Goal
Implement and integrate **ADR-DISCOVERY-048: Semantic Bijectivity & Formal Drift Auditor (Claim-to-Formal Isomorphism Gate)** in CoResearcher.

## Blocking Questions
None (0 blocking questions). All contracts and requirements are well-defined and derive directly from the discovery architecture.

## Assumptions
1. *Data*: Input manuscripts contain both natural language claims / mathematical prose (with premises, hypothesis statements, and target bounds) and candidate Lean 4 source definitions.
2. *Failure Mode*: If an assumption is weakened or extra derivatives/regularity hypotheses are inserted in Lean that were absent in the prose, the auditor must strictly flag `SEMANTIC_DRIFT_DETECTED` / `GOALPOST_SHIFTING_ALERT` and downgrade the tier from `DUAL_VERIFIED_GROUND_TRUTH` to `DRIFTED_FORMALIZATION_MISMATCH`.
4. *Language Policy*: Strict 100% English Compliance across all repository code, comments, docstrings, and markdown files. Zero Spanish in repo files.
5. *Testing*: 100% passed test suite verifying detection of assumption weakening, derivative order shifts, frozen signature tampering, and intact valid isomorphisms.

## Plan
1. **Document Architectural Decision**:
   - Create `docs/decisions/ADR-DISCOVERY-048-SEMANTIC-BIJECTIVITY-GATE.md`.
   - Update `docs/CONSTITUTION_INDEX.md`.
2. **Implement Engine**:
   - Create `python/discovery/semantic_bijectivity_auditor.py` with:
     - `DriftType` enum (`EXACT_ISOMORPHISM`, `ASSUMPTION_WEAKENING`, `EXTRA_REGULARITY_REQUIRED`, `SIGNATURE_TAMPERING`, `BOUND_DISCREPANCY`).
     - `BijectivityVerdict` dataclass.
     - `SemanticBijectivityAuditor` with methods:
       - `freeze_theorem_signature(name, type_signature)`: cryptographic Merkle-anchor locking the theorem type.
       - `extract_prose_specifications(prose_text)`: symbolic extractor of Sobolev orders $H^s$, derivative requirements $C^k$, norms, and bounds.
       - `extract_lean_specifications(lean_code)`: AST extractor of Lean 4 binders, assumptions, and target propositions.
       - `audit_bijective_alignment(prose_spec, lean_code, frozen_hash)`: evaluates alignment, computes drift score, and detects goalpost shifting.
3. **Integrate with Existing Engines**:
   - Update `python/discovery/lean_formalization_engine.py` to invoke bijectivity check.
   - Update `python/discovery/result_family_orchestrator.py` to prevent `DUAL_VERIFIED_GROUND_TRUTH` promotion whenever drift is detected.
   - Export new symbols in `python/discovery/__init__.py`.
   - Add REST API endpoint in `api/server.py` (`POST /api/discovery/lean/audit-bijectivity`).
4. **Verification & Testing**:
   - Create `tests/test_semantic_bijectivity_auditor.py`.
   - Run tests with pytest.
   - Run `python scripts/enforce_english_policy.py`.
5. **Git Commit**: Direct commit to `master` with conventional message.
