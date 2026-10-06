"""
tests/test_lagrangian_epistemic_engine.py - Test suite for ADR-DISCOVERY-036
Verifies:
1. Exact Euler-Lagrange derivation for simple pendulum: d^2 theta/dt^2 + g/l * sin(theta) = 0.
2. Elimination of string tension force through generalized coordinate theta.
3. Free scalar field Lagrangian density (Klein-Gordon equation).
4. Detection of equation of motion mismatch in flawed theoretical proposals.
"""

import pytest
import sympy as sp
from python.discovery.lagrangian_epistemic_engine import (
    LagrangianEpistemicEngine,
    LagrangianProposal,
    DynamicalSystemType,
    LagrangianVerificationVerdict,
)


def test_pendulum_euler_lagrange_derivation():
    """
    Tests exact derivation of the pendulum equation of motion:
    T = 1/2 * m * l**2 * theta_dot**2
    V = -m * g * l * cos(theta)
    L = T - V
    EOM: m*l**2*Derivative(theta(t), (t, 2)) + g*l*m*sin(theta(t)) = 0
    """
    eom_str, eom_expr = LagrangianEpistemicEngine.derive_discrete_euler_lagrange(
        q_name="theta",
        kinetic_str="1/2 * m * l**2 * theta_dot**2",
        potential_str="-m * g * l * cos(theta)"
    )

    assert "sin(theta(t))" in eom_str
    assert "Derivative(theta(t), (t, 2))" in eom_str

    proposal = LagrangianProposal(
        proposal_id="PROP-PENDULUM-01",
        system_type=DynamicalSystemType.MECHANICAL_DISCRETE,
        generalized_coordinates=["theta"],
        kinetic_term="1/2 * m * l**2 * theta_dot**2",
        potential_term="-m * g * l * cos(theta)",
        claimed_equation_of_motion=eom_str
    )

    report = LagrangianEpistemicEngine.audit_lagrangian_proposal(proposal)
    assert report.matches_claimed_dynamics is True
    assert report.verdict == LagrangianVerificationVerdict.VERIFIED_STATIONARY_DYNAMICS
    assert "Hamiltonian_Energy_H" in report.conserved_noether_charges
    assert report.som_audit_hash.startswith("sha256:")


def test_free_scalar_field_derivation():
    """
    Tests scalar field Lagrangian density in 1+1D:
    L = 1/2 * (dphi/dt)**2 - 1/2 * (dphi/dx)**2 - 1/2 * m**2 * phi**2
    EOM: Klein-Gordon wave equation
    """
    eom_str, eom_expr = LagrangianEpistemicEngine.derive_scalar_field_euler_lagrange(
        phi_name="phi",
        kinetic_density_str="1/2 * dphi_dt**2 - 1/2 * dphi_dx**2",
        potential_density_str="1/2 * m**2 * phi**2"
    )

    assert "m**2*phi(t, x)" in eom_str
    assert "Derivative(phi(t, x), (t, 2))" in eom_str
    assert "Derivative(phi(t, x), (x, 2))" in eom_str

    proposal = LagrangianProposal(
        proposal_id="PROP-SCALAR-KLEIN-GORDON",
        system_type=DynamicalSystemType.SCALAR_FIELD_CONTINUOUS,
        generalized_coordinates=["phi"],
        kinetic_term="1/2 * dphi_dt**2 - 1/2 * dphi_dx**2",
        potential_term="1/2 * m**2 * phi**2",
        claimed_equation_of_motion=eom_str
    )

    report = LagrangianEpistemicEngine.audit_lagrangian_proposal(proposal)
    assert report.matches_claimed_dynamics is True
    assert report.verdict == LagrangianVerificationVerdict.VERIFIED_STATIONARY_DYNAMICS
    assert "Energy_Momentum_Tensor_T_mu_nu" in report.conserved_noether_charges


def test_flawed_claimed_eom_interception():
    """
    Tests interception when an author claims an incorrect equation of motion
    (e.g., claiming a linear restoring force for large angle pendulum without sin(theta)).
    """
    proposal = LagrangianProposal(
        proposal_id="PROP-FLAWED-PENDULUM",
        system_type=DynamicalSystemType.MECHANICAL_DISCRETE,
        generalized_coordinates=["theta"],
        kinetic_term="1/2 * m * l**2 * theta_dot**2",
        potential_term="-m * g * l * cos(theta)",
        claimed_equation_of_motion="m*l**2*Derivative(theta(t), (t, 2)) + g*l*m*theta(t)" # Flawed linear claim
    )

    report = LagrangianEpistemicEngine.audit_lagrangian_proposal(proposal)
    assert report.matches_claimed_dynamics is False
    assert report.verdict == LagrangianVerificationVerdict.EQUATION_OF_MOTION_MISMATCH
    assert report.diagnostic_autopsy is not None
