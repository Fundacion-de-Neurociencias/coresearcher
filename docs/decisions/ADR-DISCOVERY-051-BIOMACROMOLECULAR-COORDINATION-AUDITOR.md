# ADR-DISCOVERY-051: Biomacromolecular & Ternary Coordination Auditor (OpenMM / BlazeMD H-JEPA Physical Gate)

- **Status**: Implemented & Verified
- **Date**: 2026-10-10
- **Scope**: Chemical Physics, Biomacromolecular Complexes, Targeted Protein Degradation (PROTACs), H-JEPA Latent Simulation
- **Inspiration**: BlazeMD (Gleb Novikov, OpenMM, 2026), PROTAC Ternary Complexes, and the Physical Consistency Critique (Isaac Price / Shern Tee)

---

## 1. Context & Motivation

Frontier LLMs (such as Claude 3.7 / Opus 5.5, GPT-4o, etc.) are highly adept at reciting biochemical narratives, decomposing ligand structures, and proposing molecular dynamics (MD) workflows (PDBFixer, solvating periodic boxes, adding counterions). However, as highlighted in the critique by Isaac Price (Nøx) and Shern Tee:
> *The LLM does not calculate chemistry.* It reproduces text representations. Faced with perturbed $pK_a$ values, distorted non-natural coordination geometries, or strained PROTAC linkers, linguistic models hallucinate chemically impossible solutions.

Simulating full-atom systems in explicit water (OpenMM / BlazeMD) is computationally demanding ($2.5 \times 10^6$ integration steps for 10 ns of a 30,000-atom ternary complex), where 90% of compute is spent on stochastic brownian solvent noise.

## 2. Decision & Architectural Architecture

CoResearcher institutes **ADR-DISCOVERY-051**, deploying an autonomous **Physical Epistemic Court** that interfaces LLM script generation with strict physical invariant gates and H-JEPA latent pre-screening:

```
                  ┌─────────────────────────────────────────────────┐
                  │    LLM PROPOSAL / MOLECULAR DYNAMICS RECIPE     │
                  │        (Claude / Laya / Local IA Topologies)    │
                  └────────────────────────┬────────────────────────┘
                                           │
                                           ▼
                  ┌─────────────────────────────────────────────────┐
                  │     BIOMACROMOLECULAR COORDINATION AUDITOR      │
                  │         (Physical Invariants Court)             │
                  ├─────────────────────────────────────────────────┤
                  │ Gate 1: Van der Waals Hard Clashes (r < 1.20 Å) │
                  │ Gate 2: Catalytic Metal Coordination (Zn²⁺,Mg²⁺)│
                  │ Gate 3: Thermodynamic Cooperativity (α > 1.0)   │
                  └────────────────────────┬────────────────────────┘
                                           │
                                           ▼
                  ┌─────────────────────────────────────────────────┐
                  │     H-JEPA LATENT WORLD MODEL PRE-SCREENER      │
                  │           (world_model_adapter.py)              │
                  ├─────────────────────────────────────────────────┤
                  │ • Evaluates ΔG on continuous latent manifold    │
                  │ • Enforces Infinite Energy Guardrails (E = +inf)│
                  │ • Filters uncoupled stochastic solvent noise    │
                  └────────────────────────┬────────────────────────┘
                                           │
                       ┌───────────────────┴───────────────────┐
                       ▼                                       ▼
           [Physical Violation Trapped]             [Invariants Certified]
                       │                                       │
            Pruned: E = +inf                         Launch Full OpenMM / BlazeMD
            Recorded in HypothesisGraveyard           Production Run (4 fs HMR)
                       │                                       │
                       └───────────────────► Merkle Root ◄─────┘
                                   (som_biomacromolecular_hash)
                                   Stored in ScientificLedger
```

### Core Invariants:
1. **Van der Waals Hard Boundary**: Rejects any proposed conformation with interatomic distance $r < 1.20\,\text{Å}$, assigning instant infinite energy cost ($E = +\infty$).
2. **Metal Coordination Geometry Preservation**: Audits the coordination spheres of catalytic and structural ions ($\text{Zn}^{2+}$, $\text{Mg}^{2+}$, $\text{Ca}^{2+}$, $\text{Fe}^{2+}$). Any missing coordinating atom or bond distortion beyond $0.35\,\text{Å}$ tolerance is intercepted prior to simulation.
3. **Thermodynamic Cooperativity Gate**: Demands positive cooperativity ($\alpha = \frac{\bar{K}_{D,\text{binary}}}{K_{D,\text{ternary}}} > 1.0$) for PROTAC ternary complexes, preventing the promotion of antagonistic ligands.
4. **H-JEPA Latent Rollout**: Evaluates collective variables on the low-dimensional free-energy manifold ($\Delta G$) in milliseconds, preventing multi-day compute waste on doomed trajectories.
5. **Cryptographic Ledger Sealing**: Stools each verdict with a sovereign SHA-256 Merkle proof (`som_biomacromolecular_hash`) registered directly into `ScientificLedger`.

## 3. Verification & Compliance
- Test suite: `tests/test_biomacromolecular_auditor.py` (5/5 tests passing).
- API endpoint: `POST /api/discovery/biomacromolecular/audit-complex`.
- 100% English Compliance verified.
