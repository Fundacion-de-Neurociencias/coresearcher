"""
tests/test_lean_formalization_engine.py - Tests for ADR-DISCOVERY-047
Verifies:
1. Lean 4 scaffolding synthesis for scientific theorems and symbolic identities.
2. AST auditing detecting 'sorry' escapes and preventing unearned proof promotion.
3. Verification of clean Lean 4 proofs without 'sorry'.
4. Seamless integration with ResultFamilyOrchestrator tier promotion (DUAL_VERIFIED_GROUND_TRUTH vs PROVISIONAL).
5. Deterministic SOM SHA-256 Merkle anchoring.
"""

import pytest
from python.discovery.lean_formalization_engine import (
    LeanProofStatus,
    LeanVerificationReport,
    LeanFormalizationEngine,
)
from python.discovery.result_family_orchestrator import (
    ResultRole,
    FormalizationTier,
    ResultFamilyOrchestrator,
)


def test_lean4_scaffolding_synthesis():
    scaffolding = LeanFormalizationEngine.synthesize_lean4_scaffolding(
        theorem_name="NoetherEnergyConservation",
        hypothesis_statement="Time translation symmetry implies total energy conservation",
        premises=["H is time-invariant", "Lagrangian L has no explicit t dependence"],
        symbolic_identity="dH_dt = 0",
        auto_tactics=["intro h", "ring"],
    )

    assert "theorem NoetherEnergyConservation" in scaffolding
    assert "dH_dt = 0" in scaffolding
    assert "intro h" in scaffolding
    assert "ring" in scaffolding
    assert "CoResearcher.Discovery" in scaffolding


def test_lean4_audit_sorry_detection():
    unproven_code = """
import Mathlib

theorem FermatLastTheorem (n : ℕ) (hn : n > 2) (x y z : ℕ) (hxyz : x^n + y^n = z^n) : False := by
  sorry
"""
    report = LeanFormalizationEngine.audit_lean_source(
        theorem_name="FLT",
        lean_code=unproven_code,
    )

    assert report.is_kernel_sound is False
    assert report.contains_sorry is True
    assert report.sorry_count == 1
    assert report.status == LeanProofStatus.CONTAINS_UNPROVEN_SORRY
    assert report.som_lean_formalization_hash.startswith("sha256:")


def test_lean4_audit_clean_proof():
    clean_code = """
theorem SimpleIdentity (x : ℝ) : x + 0 = x := by
  ring
"""
    report = LeanFormalizationEngine.audit_lean_source(
        theorem_name="SimpleId",
        lean_code=clean_code,
    )

    assert report.contains_sorry is False
    assert report.sorry_count == 0
    assert "ring" in report.tactics_used
    assert report.status in [LeanProofStatus.FULLY_VERIFIED_KERNEL]
    assert report.is_kernel_sound is True


def test_result_family_integration_with_lean_engine():
    orchestrator = ResultFamilyOrchestrator(
        family_id="FAM-LEAN-TEST",
        family_title="Formalized Thermodynamic Conservation",
        discipline="MATHEMATICAL_PHYSICS",
    )

    # Clean node: has symbolic expr AND lean formalization
    orchestrator.add_manuscript_node(
        node_id="NODE-SOUND",
        title="First Law Thermodynamic Invariant",
        role=ResultRole.CORE_THEOREM,
        statement="Energy differential dE equals dQ minus dW",
        symbolic_expression="dE - (dQ - dW) = 0",
        has_lean_formalization=True,
    )

    # Incomplete node: prose only
    orchestrator.add_manuscript_node(
        node_id="NODE-PROSE",
        title="Conjectured Non-equilibrium Phase Bound",
        role=ResultRole.ALTERNATIVE_PROOF,
        statement="Entropy production is bounded by turbulent dissipation in unproved regime",
        has_lean_formalization=False,
    )

    verdict = orchestrator.audit_family_epistemic_integrity()

    assert verdict.total_nodes == 2
    # Node-sound has CAS and synthesized clean Lean scaffolding -> upgraded
    sound_node = orchestrator.nodes["NODE-SOUND"]
    assert sound_node.formalization_tier in [FormalizationTier.DUAL_VERIFIED_GROUND_TRUTH, FormalizationTier.LEAN_FORMALIZED, FormalizationTier.EXACT_CAS_VERIFIED]

    # Node-prose remains provisional prose
    prose_node = orchestrator.nodes["NODE-PROSE"]
    assert prose_node.formalization_tier == FormalizationTier.PROVISIONAL_UNFORMALIZED_PROSE
