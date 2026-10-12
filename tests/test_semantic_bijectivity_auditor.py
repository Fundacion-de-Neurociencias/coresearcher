"""
tests/test_semantic_bijectivity_auditor.py - Tests for ADR-DISCOVERY-048
Verifies:
1. Extraction of mathematical invariants from natural prose (derivatives, Sobolev H^s, dimension, bounds).
2. Extraction of formal binders and propositions from Lean 4 source.
3. Detection of the Navier-Stokes derivative order shift (4 vs 5 derivatives -> EXTRA_REGULARITY_REQUIRED).
4. Detection of frozen signature tampering when tactic engines attempt to mutate goal signatures.
5. Exact bijective isomorphism verification when claim and Lean code perfectly align.
6. Integration with ResultFamilyOrchestrator preventing DUAL_VERIFIED_GROUND_TRUTH promotion on drifted formalizations.
"""

from python.discovery.result_family_orchestrator import (
    FormalizationTier,
    ResultFamilyOrchestrator,
    ResultRole,
)
from python.discovery.semantic_bijectivity_auditor import (
    DriftType,
    SemanticBijectivityAuditor,
)


def test_navier_stokes_derivative_mismatch_detected():
    """
    Simulates the exact Navier-Stokes discrepancy reported in literature:
    Paper claims 4 additional derivatives suffice, but Lean 4 formalization
    demands 5 derivatives (weakened proposition / shifted goalpost).
    """
    prose_claim = (
        "We prove global smooth regularity for 3D Navier-Stokes equations. "
        "Under mild initial vorticity, four additional derivatives suffice to ensure finiteness."
    )
    lean_thm = """
    theorem NavierStokesGlobalRegularity (u0 : SmoothVelocityField) (hd : contDiff 5 u0) :
        GlobalRegularity u0 := by
      intro h
      sorry
    """
    prose_spec = SemanticBijectivityAuditor.extract_prose_specifications(prose_claim, "NavierStokesClaim")
    lean_spec = SemanticBijectivityAuditor.extract_lean_specifications(lean_thm, "NavierStokesClaim")

    assert prose_spec.derivative_order == 4
    assert lean_spec.derivative_order == 5

    verdict = SemanticBijectivityAuditor.audit_bijective_alignment(prose_spec, lean_spec)
    assert not verdict.is_bijective
    assert verdict.drift_type == DriftType.EXTRA_REGULARITY_REQUIRED
    assert verdict.drift_score > 0.0
    assert any("derivatives" in m for m in verdict.mismatches)


def test_frozen_signature_tampering_detection():
    """
    Tests that mutating the theorem signature after it has been frozen
    results in SIGNATURE_TAMPERING rejection.
    """
    original_sig = "theorem EnergyConservation (H : Hamiltonian) : dH_dt = 0"
    frozen_hash = SemanticBijectivityAuditor.compute_signature_hash(original_sig)

    tampered_lean = """
    theorem EnergyConservation (H : Hamiltonian) (extra_friction : FrictionTerm = 0) : dH_dt = 0 := by
      rfl
    """
    prose_spec = SemanticBijectivityAuditor.extract_prose_specifications(
        "Energy is conserved under Hamiltonian flow.", "EnergyConservation"
    )
    lean_spec = SemanticBijectivityAuditor.extract_lean_specifications(tampered_lean, "EnergyConservation")

    verdict = SemanticBijectivityAuditor.audit_bijective_alignment(
        prose_spec, lean_spec, frozen_signature_hash=frozen_hash
    )
    assert not verdict.is_bijective
    assert verdict.drift_type == DriftType.SIGNATURE_TAMPERING
    assert not verdict.frozen_hash_valid


def test_exact_bijective_isomorphism():
    """
    Tests that a well-aligned proof without goalpost shifting achieves EXACT_ISOMORPHISM.
    """
    prose_claim = "For any 3D incompressible flow, C^4 smoothness guarantees boundedness of the pressure-flux."
    lean_code = """
    theorem PressureFluxEstimate (u : VelocityField) (hu : contDiff 4 u) (hdim : Fin 3) :
        PressureFluxBound u := by
      intros
      exact id
    """
    prose_spec = SemanticBijectivityAuditor.extract_prose_specifications(prose_claim, "PressureFlux")
    lean_spec = SemanticBijectivityAuditor.extract_lean_specifications(lean_code, "PressureFlux")

    verdict = SemanticBijectivityAuditor.audit_bijective_alignment(prose_spec, lean_spec)
    assert verdict.is_bijective
    assert verdict.drift_type == DriftType.EXACT_ISOMORPHISM
    assert verdict.drift_score < 0.1


def test_result_family_blocks_drifted_promotion():
    """
    Verifies that ResultFamilyOrchestrator assigns DRIFTED_FORMALIZATION_MISMATCH
    instead of DUAL_VERIFIED_GROUND_TRUTH when Lean drifts from prose.
    """
    orch = ResultFamilyOrchestrator(
        family_id="FAM-NS-DRIFT",
        family_title="Navier Stokes Regularity Family",
        discipline="Mathematical Physics",
    )
    orch.add_manuscript_node(
        node_id="NS-Core",
        title="Navier-Stokes Regularity",
        role=ResultRole.CORE_THEOREM,
        statement="4 additional derivatives guarantee regularity for the flow.",
        has_lean_formalization=True,
    )
    # Give it a Lean formalization that demands 5 derivatives and has a clean proof body
    clean_but_weakened_lean = """
    theorem NSCore (u : Flow) (h : contDiff 5 u) : Regular u := by
      intro h_flow
      exact h_flow
    """
    # Write to a temporary file
    import tempfile

    with tempfile.NamedTemporaryFile("w", suffix=".lean", delete=False) as f:
        f.write(clean_but_weakened_lean)
        lean_tmp_path = f.name

    orch.nodes["NS-Core"].lean_file_path = lean_tmp_path

    report = orch.audit_family_epistemic_integrity()
    assert orch.nodes["NS-Core"].formalization_tier == FormalizationTier.DRIFTED_FORMALIZATION_MISMATCH
    assert not report.is_epistemically_sound
