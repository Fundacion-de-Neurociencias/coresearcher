"""
Tests for Result Family Orchestrator & Dual Formalization Gate (ADR-DISCOVERY-043).
"""

import pytest
from python.discovery.result_family_orchestrator import (
    FamilyManuscriptNode,
    FormalizationTier,
    ResultFamilyAuditVerdict,
    ResultFamilyOrchestrator,
    ResultRole,
)


def test_result_family_creation_and_audit():
    orchestrator = ResultFamilyOrchestrator(
        family_id="FAM-003",
        family_title="The Quasi-Riemann Hypothesis",
        discipline="ANALYTIC_NUMBER_THEORY",
    )

    # 1. Add core theorem with Lean proof
    orchestrator.add_manuscript_node(
        node_id="NODE-CORE",
        title="Zero-Free Half-Plane Re(s) > 7/8",
        role=ResultRole.CORE_THEOREM,
        statement="Every Dirichlet L-function is zero-free in Re(s) > 7/8",
        symbolic_expression="Re(s) > 7/8",
        has_lean_formalization=True,
        lean_file_path="lean/003.lean",
    )

    # 2. Add companion bridge lemma
    orchestrator.add_manuscript_node(
        node_id="NODE-LEMMA-1",
        title="Uniform exclusion of Landau-Siegel zeros",
        role=ResultRole.BRIDGE_LEMMA,
        statement="Landau-Siegel zeros do not exist for conductor q >= 3",
        has_lean_formalization=True,
        parent_lemma_ids=["NODE-CORE"],
    )

    # 3. Add alternative unformalized preprint
    orchestrator.add_manuscript_node(
        node_id="NODE-ALT-PROOF",
        title="Alternative 11/12 contour proof",
        role=ResultRole.ALTERNATIVE_PROOF,
        statement="Contour shift integral bound yields zero-free Re(s) > 11/12",
        has_lean_formalization=False,
        parent_lemma_ids=["NODE-LEMMA-1"],
    )

    verdict = orchestrator.audit_family_epistemic_integrity()

    assert isinstance(verdict, ResultFamilyAuditVerdict)
    assert verdict.total_nodes == 3
    assert verdict.core_theorems_count == 1
    assert verdict.formalized_nodes_count >= 1
    assert verdict.holonomy_defect < 1e-3
    assert verdict.is_epistemically_sound is True
    assert "PARTIALLY_FORMALIZED_FAMILY" in verdict.editorial_judgment
    assert len(verdict.som_family_merkle_hash) > 10


def test_empty_family_audit_rejected():
    orchestrator = ResultFamilyOrchestrator("EMPTY-FAM", "Empty Family")
    verdict = orchestrator.audit_family_epistemic_integrity()
    assert verdict.is_epistemically_sound is False
    assert verdict.total_nodes == 0
    assert "EMPTY_FAMILY_REJECTED" in verdict.editorial_judgment
