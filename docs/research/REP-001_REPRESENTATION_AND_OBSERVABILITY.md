#REP-001 — Representation and Observability

**Status**: CANDIDATE  
**EpistemicStatus**: UNKNOWN  
**Evidence**: Architectural observation  

---

## Observation

Great historical scientific advances seem to coincide with changes in representation.

```text
Nueva representación
→ nuevo espacio observable
→ nuevas restricciones observables
→ nuevas preguntas falsables
```

### Historical examples

| Scientist | Change of representation | New observable space |
|------------|--------------------------|-------------------------|
| Euclid | Geometric axiomatics | Deducible relations, theorems impossible to see without axioms |
| Euler-Lagrange | Physics as optimization | Trajectory space, principle of least action |
| Einstein | Gravitational force → geometry of space-time | Curvature, black holes, gravitational waves |
| Schrödinger | Particles → wave functions | Quantum states, superposition, entanglement |
| Yang-Mills | Isolated fields → gauge symmetries | Gauge interactions, gauge bosons, confinement |

**Common is not the equation. The common thing is:**

```text
Nueva representación
→ aparecen nuevas invariantes
→ aparecen nuevas restricciones
→ aparecen nuevas predicciones
```

---

## Open question

What observations remain invisible because the current CoResearcher representation does not make them visible?

---

## Visibility inventory per artifact

For each current artifact, document what it makes visible and what it makes invisible.

**Allowed result:** `VISIBLE`, `INVISIBLE`, `UNKNOWN`

###EvidenceGraph

| Dimension | State | Note |
|-----------|--------|------|
| Claims anchored to evidence | VISIBLE | 591 claims anchored in artifacts |
| Chains of evidence | VISIBLE | 426 edges reconstructed |
| Trusts | VISIBLE | trust scores by claim |
| Discontinuities | INVISIBLE | It does not represent qualitative leaps between paradigms |
| Underlying restrictions | INVISIBLE | Does not distinguish between convergence due to real constraint vs convergence due to noise |
| Deep structure | UNKNOWN | Hidden patterns in the graph topology have not been analyzed |

### DecisionGraph / Trajectory

| Dimension | State | Note |
|-----------|--------|------|
| Reconstructable trajectories | VISIBLE | 301 Rebuilt DecisionNodes |
| Temporal sequences | VISIBLE | Chronological DAG with typed edges |
| Convergences | VISIBLE | 4 convergences detected |
| Epistemic gaps | VISIBLE | 155 gaps detected |
| Counterexamples | INVISIBLE | No explicitly discarded alternatives are recorded |
| Branch structure | INVISIBLE | Unexplored branches are not represented |
| Deep directionality | UNKNOWN | The topology of the decision space has not been measured |

### Convergence

| Dimension | State | Note |
|-----------|--------|------|
| Detectable convergences | VISIBLE | 4 convergences observed |
| Independent actors | VISIBLE | ≥2 actors per convergence |
| Recurring themes | VISIBLE | Jaccard grouping of titles |
| Shared restrictions | INVISIBLE | 0/4 convergences have identified restriction |
| Success vs barrier | VISIBLE | 0/4 successful, 4/4 barrier convergences |
| Causal mechanisms | INVISIBLE | It is not explained why they converge |

### Gap

| Dimension | State | Note |
|-----------|--------|------|
| Detectable gaps | VISIBLE | 155 gaps, gap_density=0.515 |
| Severity | VISIBLE | high/medium/low classifieds |
| Epistemic type | VISIBLE | empirical/causal/mathematical |
| Scan Status | VISIBLE | explored_abandoned/explored_partial/unknown |
| Underlying restrictions | INVISIBLE | Gaps are symptoms, not causes |
| Structure of ignored space | UNKNOWN | The topology of ignorance has not been mapped |

### Freezes

| Dimension | State | Note |
|-----------|--------|------|
| Documented boundaries | VISIBLE | BOUNDARY_WITH_EDITXT.md, BOUNDARY_WITH_AI_SCIENTISTS.md |
| Operational Maxims | VISIBLE | 10 documented maxims |
| Architecture Freeze | VISIBLE | ARCHITECTURE_FREEZE.md |
| What is not frozen | INVISIBLE | What remains open is not explicitly listed |
| Tension between layers | UNKNOWN | Frictions between boundaries have not been measured |

### Operational Maxims

| Dimension | State | Note |
|-----------|--------|------|
| Documented rules | VISIBLE | 10 maxims in OPERATIONAL_MAXIMS.md |
| Practical application | VISIBLE | Referenced in scripts and artifacts |
| Exceptions | INVISIBLE | No violations or exceptions recorded |
| Effectiveness | UNKNOWN | The impact of each maxim has not been measured |

---

## Question reformulated for the IDE

```text
What observables are absent not because of logical impossibility,
sino por elección de representación?
```

**Do not ask for:** New representation.  
**Do not order:** New scheme.  
**Just ask for:** Inventory of the invisible.

---

## Action

None.  
CANDIDATE status until multiple cases appear where different lines of work converge on the same invisibility observation.

---

*Created: 2026-08-06*  
*Evidence: None (architectural observation)*