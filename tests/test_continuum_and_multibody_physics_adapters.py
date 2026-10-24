"""
tests/test_continuum_and_multibody_physics_adapters.py - Test Suite for OpenFOAM & Isaac Sim Physical Grounding
ADR-DISCOVERY-074 and ADR-DISCOVERY-075
"""

import os
import shutil
import tempfile
import numpy as np
import pytest

from python.discovery import (
    OpenFoamSolverType,
    OpenFoamExecutionMode,
    OpenFoamCaseConfig,
    OpenFoamVerificationReport,
    OpenFoamContinuumOracle,
    JointType,
    IsaacSimExecutionMode,
    ContactFrictionModel,
    RigidBodyDefinition,
    IsaacSimVerificationReport,
    IsaacSimGroundingAdapter,
    PhysicalCoherenceCourt,
    CourtVerdict,
    PhysicalConservationType,
)


def test_openfoam_case_bundle_synthesis():
    """Validates structural synthesis of all OpenFOAM dictionary and initial condition files."""
    temp_dir = tempfile.mkdtemp(prefix="test_openfoam_case_")
    try:
        config = OpenFoamCaseConfig(
            case_name="lid_driven_cavity_test",
            solver=OpenFoamSolverType.ICO_FOAM,
            dimensions=(1.0, 1.0, 0.1),
            grid_resolution=(10, 10, 1),
            kinematic_viscosity=0.01,
            delta_t=0.005,
            end_time=0.5,
            inlet_velocity=(1.0, 0.0, 0.0)
        )
        bundle = OpenFoamContinuumOracle.generate_case_bundle(config, temp_dir)

        assert "system/controlDict" in bundle
        assert "system/fvSchemes" in bundle
        assert "system/fvSolution" in bundle
        assert "system/blockMeshDict" in bundle
        assert "constant/transportProperties" in bundle
        assert "0/U" in bundle
        assert "0/p" in bundle

        for rel_path, abs_path in bundle.items():
            assert os.path.isfile(abs_path), f"File {rel_path} was not created"
            with open(abs_path, "r", encoding="utf-8") as f:
                content = f.read()
                assert "FoamFile" in content

        report = OpenFoamContinuumOracle.audit_case_directory(temp_dir, config)
        assert report.is_sound is True
        assert report.case_name == "lid_driven_cavity_test"
    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)


def test_openfoam_velocity_field_divergence_free_sound():
    """Validates physical conservation and BKM regularity on a discrete Taylor-Green vortex."""
    nx, ny, nz = 32, 32, 2
    x = np.linspace(0, 2 * np.pi, nx, endpoint=False)
    y = np.linspace(0, 2 * np.pi, ny, endpoint=False)
    z = np.array([0.0, 0.1])
    dx = float(x[1] - x[0])
    dy = float(y[1] - y[0])
    dz = float(z[1] - z[0])

    X, Y, Z = np.meshgrid(x, y, z, indexing="ij")

    # Incompressible 2D Taylor-Green vortex: div(U) = 0 analytically
    # ux = -cos(X) * sin(Y), uy = sin(X) * cos(Y), uz = 0
    u_grid = np.zeros((3, nx, ny, nz), dtype=np.float64)
    u_grid[0] = -np.cos(X) * np.sin(Y)
    u_grid[1] = np.sin(X) * np.cos(Y)
    u_grid[2] = 0.0

    nu = 0.01
    dt = 0.01

    report = OpenFoamContinuumOracle.audit_velocity_field_invariants(
        velocity_grid=u_grid,
        cell_sizes=(dx, dy, dz),
        nu=nu,
        dt=dt,
        prior_kinetic_energy=None,
        divergence_tolerance=0.15  # Discrete finite-difference grid truncation tolerance
    )

    assert report.is_sound is True
    assert report.divergence_passed is True
    assert report.bkm_regularity_passed is True
    assert report.enstrophy > 0.0
    assert report.kinetic_energy > 0.0
    assert report.som_audit_hash.startswith("sha256:")


def test_openfoam_velocity_field_divergence_breach():
    """Validates that unphysical divergent compressible fields are caught and rejected."""
    nx, ny, nz = 10, 10, 1
    u_grid = np.zeros((3, nx, ny, nz), dtype=np.float64)
    # Strongly divergent field: div(U) = 20
    x = np.linspace(0, 1, nx)
    y = np.linspace(0, 1, ny)
    X, Y, _ = np.meshgrid(x, y, [0], indexing="ij")
    u_grid[0] = 10.0 * X
    u_grid[1] = 10.0 * Y

    report = OpenFoamContinuumOracle.audit_velocity_field_invariants(
        velocity_grid=u_grid,
        cell_sizes=(0.1, 0.1, 0.1),
        nu=0.01,
        dt=0.01,
        divergence_tolerance=1e-3
    )

    assert report.is_sound is False
    assert report.divergence_passed is False
    assert report.max_divergence_residual > 5.0


def test_isaac_sim_usd_and_warp_synthesis():
    """Validates programmatic generation of USDA stages and NVIDIA Warp simulation kernels."""
    bodies = [
        RigidBodyDefinition(
            name="pendulum_bob",
            mass=2.5,
            inertia_diagonal=(0.1, 0.1, 0.1),
            collision_geometry="sphere",
            geometry_dimensions=(0.2, 0.0, 0.0),
            initial_position=(0.0, 1.5, 0.0),
            linear_velocity=(1.0, 0.0, 0.0)
        ),
        RigidBodyDefinition(
            name="base_anchor",
            mass=0.0,  # Static anchor
            inertia_diagonal=(0.0, 0.0, 0.0),
            collision_geometry="cube",
            geometry_dimensions=(0.1, 0.1, 0.1),
            initial_position=(0.0, 2.0, 0.0)
        )
    ]
    joints = [
        {"name": "revolute_joint_0", "type": "REVOLUTE", "body0": "base_anchor", "body1": "pendulum_bob"}
    ]

    usd_str = IsaacSimGroundingAdapter.generate_usd_stage(bodies, joints, "Test_Stage")
    assert "#usda 1.0" in usd_str
    assert "PhysicsScene" in usd_str
    assert "pendulum_bob" in usd_str
    assert "PhysicsJoint" in usd_str or "PhysicsRevoluteJoint" in usd_str

    warp_str = IsaacSimGroundingAdapter.generate_warp_kernel_script(bodies, dt=0.01, total_steps=50)
    assert "import warp as wp" in warp_str
    assert "@wp.kernel" in warp_str
    assert "integrate_rigid_bodies" in warp_str
    assert "wp.launch" in warp_str


def test_isaac_sim_trajectory_energy_and_contact_sound():
    """Validates conservative ballistic trajectory and compliant friction cone auditing."""
    t_steps = 100
    t = np.linspace(0, 1.0, t_steps)
    mass = 2.0
    gravity = 9.81
    y0 = 10.0
    vy0 = 5.0

    # Exact conservative ballistic motion under gravity:
    # y(t) = y0 + vy0*t - 0.5*g*t^2
    # vy(t) = vy0 - g*t
    # E(t) = 0.5*m*vy^2 + m*g*y = constant
    positions = np.zeros((t_steps, 1, 3))
    velocities = np.zeros((t_steps, 1, 3))
    positions[:, 0, 1] = y0 + vy0 * t - 0.5 * gravity * t**2
    velocities[:, 0, 1] = vy0 - gravity * t

    masses = np.array([mass])

    # Contact forces: Normal force = 10N, Tangent force = 2N, mu = 0.5 -> 2 <= 0.5 * 10 = 5 (Satisfied)
    fn = np.full((t_steps, 1), 10.0)
    ft = np.full((t_steps, 1), 2.0)

    report = IsaacSimGroundingAdapter.audit_trajectory_energy_and_contact(
        time_steps=t,
        positions=positions,
        velocities=velocities,
        masses=masses,
        contact_normal_forces=fn,
        contact_tangent_forces=ft,
        friction_mu=0.5,
        gravity=gravity,
        energy_drift_tolerance=1e-3
    )

    assert report.is_sound is True
    assert report.energy_conservation_passed is True
    assert report.friction_cone_passed is True
    assert report.contact_non_penetration_passed is True
    assert report.som_audit_hash.startswith("sha256:")


def test_isaac_sim_friction_cone_violation_caught():
    """Validates that slip/tangential breach exceeding the Coulomb cone is caught."""
    t_steps = 10
    t = np.linspace(0, 0.1, t_steps)
    positions = np.ones((t_steps, 1, 3))
    velocities = np.zeros((t_steps, 1, 3))
    masses = np.array([1.0])

    # Normal force = 10N, Tangent force = 8N, mu = 0.5 -> 8 > 0.5 * 10 = 5 (Breach!)
    fn = np.full((t_steps, 1), 10.0)
    ft = np.full((t_steps, 1), 8.0)

    report = IsaacSimGroundingAdapter.audit_trajectory_energy_and_contact(
        time_steps=t,
        positions=positions,
        velocities=velocities,
        masses=masses,
        contact_normal_forces=fn,
        contact_tangent_forces=ft,
        friction_mu=0.5
    )

    assert report.is_sound is False
    assert report.friction_cone_passed is False
    assert report.max_friction_cone_violation >= 2.9


def test_physical_coherence_court_synergistic_arbitration():
    """Validates end-to-end arbitration in PhysicalCoherenceCourt for both OpenFOAM and Isaac Sim."""
    court = PhysicalCoherenceCourt()

    # 1. OpenFOAM CFD Arbitration
    openfoam_sound_data = {
        "is_sound": True,
        "solver": "icoFoam",
        "max_divergence_residual": 1e-5,
        "enstrophy": 12.4,
        "bkm_integral": 45.0,
        "diagnostics": "Taylor-Green vortex verified"
    }
    foam_audit = court.audit_openfoam_cfd_report("CLAIM-CFD-001", openfoam_sound_data)
    assert foam_audit.verdict == CourtVerdict.VERIFIED_COHERENT
    assert foam_audit.conservation_audit[0]["satisfied"] is True

    openfoam_breach_data = {
        "is_sound": False,
        "solver": "icoFoam",
        "max_divergence_residual": 8.5,
        "enstrophy": 999.0,
        "bkm_integral": 1e7,
        "diagnostics": "Divergence blow-up"
    }
    foam_breach_audit = court.audit_openfoam_cfd_report("CLAIM-CFD-002", openfoam_breach_data)
    assert foam_breach_audit.verdict == CourtVerdict.REJECTED_CONSERVATION_VIOLATION
    assert "regularity breach" in foam_breach_audit.duhem_quine_autopsy

    # 2. Isaac Sim Arbitration
    isaac_sound_data = {
        "is_sound": True,
        "scene_name": "robotic_arm_lcp",
        "energy_drift_ratio": 0.001,
        "max_friction_cone_violation": 0.0,
        "max_penetration_depth": 0.0,
        "diagnostics": "LCP contact verified"
    }
    isaac_audit = court.audit_isaac_sim_grounding_report("CLAIM-ISAAC-001", isaac_sound_data)
    assert isaac_audit.verdict == CourtVerdict.VERIFIED_COHERENT

    isaac_breach_data = {
        "is_sound": False,
        "scene_name": "robotic_arm_lcp",
        "energy_drift_ratio": 0.25,
        "max_friction_cone_violation": 4.5,
        "max_penetration_depth": 0.1,
        "diagnostics": "Friction cone exceeded"
    }
    isaac_breach_audit = court.audit_isaac_sim_grounding_report("CLAIM-ISAAC-002", isaac_breach_data)
    assert isaac_breach_audit.verdict == CourtVerdict.REJECTED_CONSERVATION_VIOLATION
