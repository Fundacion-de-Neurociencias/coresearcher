# ADR-DISCOVERY-036: Generalized Lagrangian Epistemics & Principle of Stationary Action for Scientific Theories

**Status**: PROPOSED & RATIFIED  
**Date**: 2026-10-06  
**Author**: CoResearcher Epistemic Architecture Board  
**Target Modules**: `python/discovery/lagrangian_epistemic_engine.py`, `python/discovery/physical_theorem_court.py`, `python/discovery/physics_corpus_auditor.py`, `api/server.py`  
**Cross-References**: `ADR-DISCOVERY-001` (Epistemic Trajectory & Representation), `ADR-DISCOVERY-017` (Physical Theorem Court), `ADR-DISCOVERY-028` (Universal Physics Auditor), `ADR-EPISTEMIC-034` (Exact Symbolic Dual-Verification)

---

## 1. Context and Problem Statement

From the harmonic pendulum to quantum field theory and the Standard Model, physics describes disparate physical systems using a universal language: **the Principle of Stationary Action ($\delta S = 0$)**.

1. **Coordinate Choice and Constraint Elimination**:
   In a pendulum, choosing the generalized coordinate (angle $\theta$) automatically absorbs the fixed length constraint, rendering internal constraint forces (string tension) redundant.
2. **Lagrangian Formulation as a Physical Proposal**:
   A proposed physical theory is rigorously formalized by specifying its Lagrangian $L = T - V$ or spacetime Lagrangian density $\mathcal{L}(\phi, \partial_\mu \phi)$. Equations of motion are not ad-hoc assertions; they are derived consequences of the Euler-Lagrange equations:
   $$\frac{\partial \mathcal{L}}{\partial \phi} - \partial_\mu \left( \frac{\partial \mathcal{L}}{\partial (\partial_\mu \phi)} \right) = 0$$
3. **The Epistemic Parallel**:
   In AI-driven scientific discovery, naive models attempt to describe complex systems (e.g. cellular pathways or astrophysics) using high-dimensional Euclidean coordinate systems full of redundant constraints. Conversely, deep scientific discovery consists of:
   - Discovering generalized coordinates that eliminate internal constraint forces.
   - Formulating an explicit Lagrangian proposal that compresses complex interactions into an action integral.
   - Subjecting derived Euler-Lagrange equations to empirical measurement ($RCS \ge 2.0$).

---

## 2. Decision and Epistemic Invariants

CoResearcher ratifies **ADR-DISCOVERY-036**, establishing the **Generalized Lagrangian Epistemic Engine** (`LagrangianEpistemicEngine`):

### Invariant 1: First-Class Lagrangian Field Specification
Any physical theory or formal dynamical claim evaluated by CoResearcher can be specified as a Lagrangian density $\mathcal{L}(q, \dot{q})$ or $\mathcal{L}(\phi, \partial_\mu \phi)$.
- Theoretical chapters in the physics megarepository are parsed for their explicit kinetic terms ($T$), potential terms ($V$), and interaction terms ($\mathcal{L}_{\text{int}}$).

### Invariant 2: Symbolic Euler-Lagrange Automated Derivation
Using exact Computer Algebra Systems (SymPy, per `ADR-EPISTEMIC-034`), the engine derives the exact equations of motion analytically:
$$E_L(q) = \frac{d}{dt}\left(\frac{\partial L}{\partial \dot{q}}\right) - \frac{\partial L}{\partial q} = 0$$
The derived equation of motion is cross-checked against the author's stated equations to verify mathematical integrity and detect missing interaction terms or sign errors.

### Invariant 3: Noether Invariant Auditing (Symmetries $\iff$ Conservation Laws)
For any proposed continuous symmetry transformation of the Lagrangian (e.g., time translation $\to$ energy, space translation $\to$ momentum, global phase $U(1) \to$ charge conservation):
$$\delta \mathcal{L} = \partial_\mu J^\mu \implies \partial_\mu j^\mu = 0$$
The engine audits whether the proposed Lagrangian mathematically guarantees the claimed conservation invariants without ad-hoc auxiliary assumptions.

### Invariant 4: Epistemic Action Parsimony ($\delta S_{\text{epistemic}} = 0$)
The trajectory score of competing candidate representations is evaluated by the epistemic action:
$$S_{\text{epistemic}} = \int \left( \mathcal{T}_{\text{empirical explanatory power}} - \mathcal{V}_{\text{epistemic complexity / auxiliary debt}} \right) dt$$
A valid physical proposal must survive contact with real-world measurement ($RCS \ge 2.0$), fulfilling the invariant: *"A beautifully written Lagrangian is a physical proposal; its consequences still have to survive measurement."*

---

## 3. Structural Specification

```
[Physical Theory / Corpus Chapter]
                 │
                 ▼
┌────────────────────────────────────────────────────────┐
│  LagrangianEpistemicEngine (ADR-DISCOVERY-036)         │
│  ├─ GeneralizedCoordinateExtractor (Angle / Field)     │
│  ├─ SymbolicEulerLagrangeDeriver (Exact SymPy CAS)     │
│  ├─ NoetherSymmetryAuditor (Conserved Currents j^μ)    │
│  └─ StationaryActionEvaluator (δS = 0)                 │
└────────────────────────────────────────────────────────┘
                 │
                 ▼
[Derived Equations of Motion vs. Text Claim Verification]
                 │
                 ▼
[Empirical Reality Contact Gate (RCS >= 2.0)]
```

---

## 4. Architectural Boundaries

- **`python/discovery/lagrangian_epistemic_engine.py`**: Handles symbolic Euler-Lagrange derivations, Noether current audits, and generalized coordinate transformations.
- **`python/discovery/physical_theorem_court.py`**: Interacts with the court to check derived equations against conservation invariants.
- **`api/server.py`**: Exposes `/api/discovery/lagrangian/audit` for automated verification.
