# ADR-DISCOVERY-074: OpenFOAM Continuum Mechanics and CFD Empirical Oracle

## Status
ACCEPTED / IMPLEMENTED

## Date
2026-10-24

## Context
While CoResearcher provides formal mathematical and symbolic physics courts (`PhysicalTheoremCourt`, `LagrangianEpistemicEngine`), assessing continuum mechanics hypotheses (such as Navier-Stokes regularities, boundary layer separation, turbulent dissipation, and microfluidic transport) requires continuous numerical verification. Without an empirical PDE solver, theoretical bounds on enstrophy and vortex stretching cannot be checked against high-resolution continuum fields.

## Architectural Decision
We implement **`OpenFoamContinuumOracle`** in `python/discovery/openfoam_continuum_oracle.py`:
1. **Programmatic Case Bundle Synthesis**:
   - Synthesizes complete standard OpenFOAM cases (`system/controlDict`, `system/fvSchemes`, `system/fvSolution`, `system/blockMeshDict`, `constant/transportProperties`, `0/U`, `0/p`).
2. **Dual-Mode Execution & Zero Mocking**:
   - Dispatches live solver execution (`icoFoam`, `simpleFoam`, `pisoFoam`, `interFoam`) when native binaries or containerized environments exist.
   - Executes exact discrete tensor verification when external binaries are absent, explicitly reporting `DISCRETE_TENSOR_AUDIT`.
3. **Rigorous Invariant Auditing**:
   - Mass continuity divergence residual: $\max |\nabla \cdot \vec{U}| \le \varepsilon_{\text{div}}$.
   - Enstrophy integration: $\Omega(t) = \frac{1}{2} \int \|\nabla \times \vec{U}\|^2 dV$.
   - Beale-Kato-Majda (BKM) regularity criterion: $\|\vec{\omega}(t)\|_\infty < \infty$.
   - Leray-Hopf energy dissipation: $\frac{dE}{dt} \le -\nu \|\nabla \vec{U}\|^2$.
4. **Court Arbitration**:
   - Directly ingested by `PhysicalCoherenceCourt.audit_openfoam_cfd_report()` under invariant `OPENFOAM_CFD_REGULARITY`.

## Consequences
- Bridges symbolic analysis and continuous finite-volume CFD simulations.
- Provides rigorous empirical falsification for continuum fluid hypotheses.
