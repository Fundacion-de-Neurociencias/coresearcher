"""
tests/test_tao_invariant.py - Tests for ADR-EPISTEMIC-032 The Terence Tao Open Explanation Invariant.
Verifies that:
1. Oracular opaque claims without a ProofDependencyDAG are rejected (REJECTED_ORACULAR_OPAQUE_CLAIM).
2. Proofs containing circular lemma loops are detected and rejected.
3. Rigorous, acyclic proofs are verified with formal SOM hashes.
"""

import pytest

from python.discovery.physical_theorem_court import (
    CourtVerdict,
    DeductionRule,
    PhysicalCoherenceCourt,
    ProofDependencyDAG,
    ProofLemmaNode,
)


@pytest.mark.epistemic
@pytest.mark.fast
def test_oracular_claim_rejected_without_dag():
    """Verifies that an opaque claim lacking an explicit ProofDependencyDAG is rejected under ADR-EPISTEMIC-032."""
    court = PhysicalCoherenceCourt()
    report = court.audit_oracular_proof(
        claim_id="OPENAI-ORACULAR-CLAIM-001",
        target_equation="3D Incompressible Navier-Stokes Global Smoothness",
        proof_dag=None,
    )

    assert report is not None
    assert report.verdict == CourtVerdict.REJECTED_ORACULAR_OPAQUE_CLAIM
    assert "Oracular Opaque Claim Rejected" in report.duhem_quine_autopsy
    assert "Terence Tao Invariant" in report.duhem_quine_autopsy
    assert report.som_audit_hash.startswith("sha256:")


@pytest.mark.epistemic
@pytest.mark.fast
def test_oracular_claim_rejected_with_empty_dag():
    """Verifies that an empty DAG with zero lemmas is also rejected."""
    court = PhysicalCoherenceCourt()
    empty_dag = ProofDependencyDAG(theorem_id="EMPTY-CLAIM")
    report = court.audit_oracular_proof(
        claim_id="OPENAI-ORACULAR-CLAIM-002",
        target_equation="Riemann Hypothesis",
        proof_dag=empty_dag,
    )

    assert report.verdict == CourtVerdict.REJECTED_ORACULAR_OPAQUE_CLAIM


@pytest.mark.epistemic
@pytest.mark.fast
def test_circular_proof_detected_by_tao_reviewer():
    """Verifies that the Tao Reviewer catches circular reasoning cycles in candidate proofs."""
    court = PhysicalCoherenceCourt()
    circular_dag = ProofDependencyDAG(theorem_id="CIRCULAR-PROOF")
    circular_dag.add_lemma(
        ProofLemmaNode(
            lemma_id="L1",
            title="Lemma 1",
            premises=["L2"],
            deduction_rule=DeductionRule.MODUS_PONENS,
            mathematical_statement="A -> B",
            formal_expression="A => B",
        )
    )
    circular_dag.add_lemma(
        ProofLemmaNode(
            lemma_id="L2",
            title="Lemma 2",
            premises=["L1"],
            deduction_rule=DeductionRule.MODUS_PONENS,
            mathematical_statement="B -> A",
            formal_expression="B => A",
        )
    )

    report = court.audit_oracular_proof(
        claim_id="CANDIDATE-CIRCULAR-003",
        target_equation="Energy bound inequality",
        proof_dag=circular_dag,
    )

    assert report.verdict == CourtVerdict.REJECTED_CIRCULAR_LEMMA
    assert "circular reasoning cycle" in report.duhem_quine_autopsy


@pytest.mark.epistemic
@pytest.mark.fast
def test_acyclic_decomposed_proof_verified_coherently():
    """Verifies that an open, decomposed acyclic proof passes with flying colors."""
    court = PhysicalCoherenceCourt()
    valid_dag = ProofDependencyDAG(theorem_id="TAO-VERIFIED-PROOF")
    valid_dag.add_lemma(
        ProofLemmaNode(
            lemma_id="LEMMA-0",
            title="Sobolev Embedding",
            premises=[],
            deduction_rule=DeductionRule.SOBOLEV_EMBEDDING,
            mathematical_statement="H1 embedding in L6",
            formal_expression="sobolev_h1_l6()",
        )
    )
    valid_dag.add_lemma(
        ProofLemmaNode(
            lemma_id="LEMMA-1",
            title="Gronwall Energy Estimate",
            premises=["LEMMA-0"],
            deduction_rule=DeductionRule.GRONWALL_INEQUALITY,
            mathematical_statement="d/dt E(t) <= C E(t)",
            formal_expression="gronwall(E, t)",
        )
    )

    report = court.audit_oracular_proof(
        claim_id="VERIFIED-NAVIER-LEMMA-004",
        target_equation="Navier-Stokes Subcritical Enstrophy Control",
        proof_dag=valid_dag,
    )

    assert report.verdict == CourtVerdict.VERIFIED_COHERENT
    assert report.duhem_quine_autopsy is None
    assert report.som_audit_hash.startswith("sha256:")
