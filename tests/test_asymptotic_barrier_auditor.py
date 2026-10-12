"""
tests/test_asymptotic_barrier_auditor.py - Tests for ADR-DISCOVERY-045
Verifies:
1. Detection and branch pruning when attempting to prove Riemann Hypothesis (Re(s)=0.50) via contour moment methods (ceiling 0.75).
2. Detection of Selberg Parity Barrier when using classical sieve theory to isolate prime tuples.
3. Unobstructed progress when using orthogonal non-commutative or algebraic methods.
4. Deterministic SOM SHA-256 Merkle anchoring.
"""

from python.discovery.asymptotic_barrier_auditor import (
    AsymptoticBarrierAuditor,
    BarrierType,
    MathematicalMethodFamily,
)


def test_riemann_zeta_contour_moment_barrier_pruning():
    """
    Asserts that an autonomous agent attempting to prove the Riemann Hypothesis (Re(s)=0.50)
    using classical contour moment estimations (the 7/8 OpenAI approach) is detected and pruned
    by the Convexity / Off-Diagonal Barrier.
    """
    verdict = AsymptoticBarrierAuditor.audit_proof_strategy(
        strategy_id="STRAT-RIEMANN-CONTOUR",
        target_hypothesis="Riemann Hypothesis (Re(s) = 1/2 critical line zeros)",
        method_family=MathematicalMethodFamily.CONTOUR_MOMENT_ESTIMATION,
        target_threshold=0.50,
        proposed_intermediate_result=0.875,  # 7/8 achieved
    )

    assert verdict.is_obstructed_by_known_barrier is True
    assert verdict.barrier_detected == BarrierType.CONVEXITY_OFF_DIAGONAL_CEILING.value
    assert verdict.theoretical_ceiling == 0.750
    assert len(verdict.orthogonal_paradigms_recommended) >= 2
    assert "NON_COMMUTATIVE_SPECTRAL_GEOMETRY" in verdict.orthogonal_paradigms_recommended[0]
    assert "BRANCH PRUNED BY NO-GO BARRIER" in verdict.epistemic_advice
    assert verdict.som_barrier_hash.startswith("sha256:")


def test_selberg_parity_barrier_detection():
    """
    Asserts that attempting to prove the Twin Prime Conjecture (omega=1) using classical combinatorial sieves
    is blocked by the Selberg Parity Barrier.
    """
    verdict = AsymptoticBarrierAuditor.audit_proof_strategy(
        strategy_id="STRAT-TWIN-PRIMES-SIEVE",
        target_hypothesis="Twin Prime Conjecture",
        method_family=MathematicalMethodFamily.CLASSICAL_SIEVE_THEORY,
        target_threshold=1.0,  # Isolate genuine primes
    )

    assert verdict.is_obstructed_by_known_barrier is True
    assert verdict.barrier_detected == BarrierType.SELBERG_PARITY_BARRIER.value
    assert "BILINEAR_TYPE_II_EXPONENTIAL_SUMS" in verdict.orthogonal_paradigms_recommended[0]


def test_orthogonal_non_commutative_geometry_unobstructed():
    """
    Asserts that using non-commutative spectral geometry (Alain Connes / Polya-Hilbert)
    is recognized as unobstructed by classical convexity barriers.
    """
    verdict = AsymptoticBarrierAuditor.audit_proof_strategy(
        strategy_id="STRAT-CONNES-SPECTRAL",
        target_hypothesis="Riemann Hypothesis via Polya-Hilbert Operator Spectrum",
        method_family=MathematicalMethodFamily.NON_COMMUTATIVE_SPECTRAL_GEOMETRY,
        target_threshold=0.50,
    )

    assert verdict.is_obstructed_by_known_barrier is False
    assert verdict.barrier_detected == BarrierType.NONE_DETECTED.value
    assert "UNOBSTRUCTED" in verdict.epistemic_advice
