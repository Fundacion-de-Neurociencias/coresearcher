# ADR-DISCOVERY-075: NVIDIA Isaac Sim Multi-Body Grounding Adapter

## Status
ACCEPTED / IMPLEMENTED

## Date
2026-10-24

## Context
Symbolic mechanical engines such as `LagrangianEpistemicEngine` model smooth, holonomic dynamics ($L(q, \dot{q})$). However, real-world biophysical systems, laboratory automation, and robotic manipulation involve non-smooth mechanics: frictional contact, impacts, joint limits, and Linear Complementarity Problems (LCP). Furthermore, searching for adversarial counterexamples to dynamical stability requires massively parallel multi-body simulation.

## Architectural Decision
We implement **`IsaacSimGroundingAdapter`** in `python/discovery/isaac_sim_grounding_adapter.py`:
1. **OpenUSD Stage Synthesis**:
   - Synthesizes valid USDA physical stages with `PhysicsScene`, `PhysicsRigidBodyAPI`, `PhysicsMassAPI`, `PhysicsCollisionAPI`, and articulated kinematic joints.
2. **NVIDIA Warp Kernel Synthesis**:
   - Generates standalone `@wp.kernel` scripts for differentiable GPU-accelerated forward integration on CUDA, CPU, and Metal backends.
3. **Rigorous Non-Smooth Invariant Auditing**:
   - Total mechanical energy conservation: $E(t) = T(t) + V(t) - W_{\text{fric}}$.
   - Coulomb friction cone bounds: $\|\vec{F}_{\text{tangent}}\| \le \mu \|\vec{F}_{\text{normal}}\|$.
   - Contact non-penetration complementarity: gap $\ge 0$, $F_{\text{normal}} \ge 0$.
4. **Hardware-Agnostic Backend Topology**:
   - Ready for live Omniverse/CUDA dispatch on NVIDIA RTX hardware.
   - Operates natively on Apple Silicon (M4 Max) via 40-core GPU Metal/MPS and multi-threaded ARM64 execution.
5. **Court Arbitration**:
   - Arbitrated by `PhysicalCoherenceCourt.audit_isaac_sim_grounding_report()` under invariant `ISAAC_SIM_CONTACT_DYNAMICS`.

## Consequences
- Enables non-smooth multi-body physical grounding for CoResearcher.
- Supports high-throughput adversarial singularity sweeps across parallel physical environments.
