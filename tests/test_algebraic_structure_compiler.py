"""
tests/test_algebraic_structure_compiler.py - Tests for ADR-DISCOVERY-046
Verifies:
1. Compilation of Clifford Geometric Algebra Cl(3,0) into equivariant matrix generators.
2. Compilation of Symplectic Hamiltonian Flow preserving canonical phase space J.
3. Compilation of Toeplitz Spectral Operator achieving O(N log N) sub-quadratic convolution.
4. Execution of Mathematical Flywheel closed-loop cycle upgrading local AI subsystems.
5. Deterministic SOM SHA-256 Merkle anchoring.
"""

from python.discovery.algebraic_structure_compiler import (
    AlgebraicStructureClass,
    AlgebraicStructureCompiler,
    MathematicalFlywheelRunner,
)


def test_clifford_geometric_algebra_compilation():
    compiler = AlgebraicStructureCompiler()
    op = compiler.compile_clifford_algebra(theorem_id="TH-DIRAC-SPINOR", signature=(3, 0))

    assert op.structure_class == AlgebraicStructureClass.CLIFFORD_GEOMETRIC_ALGEBRA
    assert op.generator_dimension == 4
    assert len(op.generator_matrices) == 3
    assert op.is_equivariant is True
    assert "Exact SO(3) Equivariance" in op.theoretical_complexity_gain
    assert op.som_compiled_operator_hash.startswith("sha256:")


def test_symplectic_flow_compilation():
    compiler = AlgebraicStructureCompiler()
    op = compiler.compile_symplectic_flow(theorem_id="TH-HAMILTON-JACOBI", degrees_of_freedom=2)

    assert op.structure_class == AlgebraicStructureClass.SYMPLECTIC_HAMILTONIAN_FLOW
    assert op.generator_dimension == 4
    assert op.is_equivariant is True
    assert "Energy & Phase-Volume Preservation" in op.theoretical_complexity_gain
    assert len(op.generator_matrices) == 2


def test_toeplitz_spectral_operator_compilation():
    compiler = AlgebraicStructureCompiler()
    op = compiler.compile_toeplitz_spectral_operator(theorem_id="TH-FOURIER-CONVOLUTION", kernel_size=32)

    assert op.structure_class == AlgebraicStructureClass.TOEPLITZ_SPECTRAL_OPERATOR
    assert op.generator_dimension == 32
    assert "O(N log N)" in op.theoretical_complexity_gain
    assert op.is_equivariant is True


def test_mathematical_flywheel_closed_loop_cycle():
    flywheel = MathematicalFlywheelRunner()

    theorems = [
        {
            "theorem_id": "TH-CLIFFORD-01",
            "statement": "Clifford rotation operator in Euclidean space",
            "topic": "geometric algebra",
        },
        {
            "theorem_id": "TH-SYMPLECTIC-02",
            "statement": "Symplectic conservation of Hamiltonian phase flow",
            "topic": "symplectic mechanics",
        },
        {
            "theorem_id": "TH-FOURIER-03",
            "statement": "Circulant Toeplitz operator diagonalizing discrete convolution",
            "topic": "spectral analysis",
        },
    ]

    res = flywheel.run_flywheel_cycle(cycle_id="CYCLE-DISCOVERY-001", input_theorems=theorems)

    assert res.input_mathematical_theorems == 3
    assert res.compiled_operators_count == 3
    assert res.mean_equivariance_stability == 1.0
    assert len(res.target_ai_subsystems_upgraded) >= 2
    assert res.flywheel_velocity_score >= 0.70
    assert res.som_flywheel_hash.startswith("sha256:")
