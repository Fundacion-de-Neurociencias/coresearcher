"""
tests/test_exact_symbolic_court.py - Test suite for ADR-EPISTEMIC-034
Verifies:
1. Exact CAS Algebraic Identity Check via SymPy.
2. Strict Lemma Purity Invariant (Discarding proofs based on open conjectures).
3. Recurrence & Sequence Boundary Counterexample Detection (The k=27 / boundary invariant).
4. Obstacle-Driven Discovery Engine reporting.
"""

from python.discovery.exact_symbolic_court import (
    EpistemicLemmaStatus,
    ExactLemmaNode,
    ExactProofDAG,
    ExactSymbolicCourt,
    ExactSymbolicVerdict,
    ObstacleType,
)


def test_exact_algebraic_identity_verification():
    # True identity: (x + 1)^2 - (x^2 + 2x + 1) == 0
    is_valid, err = ExactSymbolicCourt.verify_algebraic_identity(
        lhs_expr_str="(x + 1)**2", rhs_expr_str="x**2 + 2*x + 1", variable_names=["x"]
    )
    assert is_valid is True
    assert err is None

    # False identity: (x + 1)^2 != x^2 + 1
    is_valid_false, err_false = ExactSymbolicCourt.verify_algebraic_identity(
        lhs_expr_str="(x + 1)**2", rhs_expr_str="x**2 + 1", variable_names=["x"]
    )
    assert is_valid_false is False
    assert err_false is not None


def test_strict_lemma_purity_discard_on_conjecture():
    dag = ExactProofDAG(theorem_id="THM-POINCARE-RECURRENCE")
    # Lemma 1: Established Axiom
    dag.add_lemma(
        ExactLemmaNode(
            lemma_id="LEMMA-1",
            statement="Energy is conserved in closed Hamiltonian systems.",
            status=EpistemicLemmaStatus.ESTABLISHED_AXIOM,
        )
    )
    # Lemma 2: Open Conjecture used in proof!
    dag.add_lemma(
        ExactLemmaNode(
            lemma_id="LEMMA-2",
            statement="All orbits are ergodic on the energy hypersurface (Unproven conjecture).",
            status=EpistemicLemmaStatus.OPEN_CONJECTURE,
            premises=["LEMMA-1"],
        )
    )

    report = ExactSymbolicCourt.audit_exact_proof(dag=dag)
    assert report.is_sound is False
    assert report.verdict == ExactSymbolicVerdict.DISCARDED_CONJECTURE_DEPENDENCY
    assert report.lemma_purity_passed is False
    assert "LEMMA-2" in report.conjecture_dependencies
    assert report.obstacle_report.obstacle_type == ObstacleType.UNPROVEN_INTERMEDIATE_CONJECTURE


def test_recurrence_boundary_counterexample_detection():
    dag = ExactProofDAG(theorem_id="THM-FIBONACCI-VARIANT")
    dag.add_lemma(
        ExactLemmaNode(
            lemma_id="LEMMA-BASE",
            statement="Linear recurrence holds by definition.",
            status=EpistemicLemmaStatus.PROVEN_LEMMA,
        )
    )

    # Real sequence: Fibonacci 1, 1, 2, 3, 5, 8, 13
    # Flawed recurrence: F_n = F_{n-1} + F_{n-2} BUT fails at index 4 (returns 6 instead of 5)
    sequence = [1, 1, 2, 3, 5, 8, 13]

    def buggy_recurrence(history, idx):
        if idx == 4:
            return 6  # Bug / boundary failure
        return history[-1] + history[-2]

    report = ExactSymbolicCourt.audit_exact_proof(
        dag=dag, sequence_benchmark=sequence, recurrence_evaluator=buggy_recurrence, recurrence_order=2
    )

    assert report.is_sound is False
    assert report.verdict == ExactSymbolicVerdict.FALSIFIED_BY_COUNTEREXAMPLE
    assert report.counterexample_found is True
    assert report.counterexample_index == 4
    assert report.observed_value == "6"
    assert report.expected_value == "5"
    assert report.obstacle_report.obstacle_type == ObstacleType.DOMAIN_BOUNDARY_FAILURE


def test_exact_sound_proof_verification():
    dag = ExactProofDAG(theorem_id="THM-SUM-OF-SQUARES")
    dag.add_lemma(
        ExactLemmaNode(
            lemma_id="LEMMA-BASE-CASE",
            statement="Base case holds for n=1: 1*(2)*(3)/6 = 1.",
            status=EpistemicLemmaStatus.ESTABLISHED_AXIOM,
        )
    )
    dag.add_lemma(
        ExactLemmaNode(
            lemma_id="LEMMA-INDUCTION-STEP",
            statement="Inductive step n*(n+1)*(2*n+1)/6 + (n+1)^2 = (n+1)*(n+2)*(2*n+3)/6.",
            status=EpistemicLemmaStatus.PROVEN_LEMMA,
            premises=["LEMMA-BASE-CASE"],
        )
    )

    report = ExactSymbolicCourt.audit_exact_proof(
        dag=dag, lhs_target="n*(n+1)*(2*n+1)/6 + (n+1)**2", rhs_target="(n+1)*(n+2)*(2*n+3)/6"
    )

    assert report.is_sound is True
    assert report.verdict == ExactSymbolicVerdict.VERIFIED_EXACT_THEOREM
    assert report.lemma_purity_passed is True
    assert report.obstacle_report.obstacle_type == ObstacleType.NONE
    assert report.som_audit_hash.startswith("sha256:")
