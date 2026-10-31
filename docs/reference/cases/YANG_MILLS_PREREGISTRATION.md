# Yang–Mills existence: pre-registered acceptance criteria, and a rehearsal on the O(3) continuum limit

**ADR:** [ADR-DISCOVERY-077](../../decisions/ADR-DISCOVERY-077-PREREGISTERED-EXISTENCE-AUDIT.md)
**Status of the claim:** CLAIMED (statement not public), recorded 2026-10-30
**Checklist:** `ym4-existence` v1.0.0, frozen 2026-10-30, SHA-256
`2f899469928cf85a9c34ab19dd1dc73be45624a60b54253e727f61903bf3b353`
([JSON](../../../examples/yang-mills-preregistration/ym4_existence_checklist.v1.json),
[lock](../../../examples/yang-mills-preregistration/ym4_existence_checklist.v1.lock.json))
**Scope:** formal statement fidelity only. Nothing here assesses whether the proof is correct, credit, or the
announcement.

## 1. What is claimed, and what is public

On October 26, 2026 OpenAI announced an existence proof of quantum Yang–Mills theory. The shepherding committee's
statement ([PDF](https://www.kitp.ucsb.edu/sites/default/files/YM_working_group.pdf), 2 pages, SHA-256
`dbab31f0…bd12`, retrieved 2026-10-30) says:

- the proof covers quantum Yang–Mills theory "including coupling to fermions";
- the committee holds the manuscripts (1147 pages) and a Lean formalization; neither is released;
- its first objective is to check that the definitions and the problem statement correspond to the standard ones,
  and that the formalization aligns with the informal treatment; the Lean proof is released after that;
- confinement and the mass gap remain open.

The statement does not name the space-time dimension or the gauge groups covered. It mentions SU(3) with quarks as
QCD, as context. The [claim record](../../../examples/yang-mills-preregistration/ym_claim_record.json) is therefore
at **CLAIMED**, with the reason "statement not public", and moves to STATEMENT_PUBLIC only with a pinned location
and SHA-256 of the statement.

## 2. The pre-registered checklist

The obligations follow the Jaffe–Witten problem statement (Clay; read and pinned, SHA-256 `3558403c…3e09`) and
constructive-QFT practice. Each one has a formal clause over a small vocabulary, its sources with locators, and the
Lean markers the lint searches for.

| Obligation | Category | Clause | Main source |
|---|---|---|---|
| YM-GROUP-NONABELIAN | core | `gauge_group in (SU2, SU3, SUN_only, all_compact_simple)` | JW §4: any compact simple G |
| YM-GROUP-COVERAGE | scope | `gauge_group == all_compact_simple` | JW §4 |
| YM-SPACETIME-DIM4 | core | `dim == 4` | JW §4: on R⁴; §6: R² or R³ are the partial results |
| YM-SPACETIME-INFINITE | core | `volume == infinite` | JW §6: T⁴ → R⁴ open; committee p. 2 |
| YM-OS-REGULARITY | core | `os_regularity` | OS 1975 linear growth; JW §4 [45, 35] |
| YM-OS-EUCLIDEAN | core | `os_euclidean_invariance` (full E(4)) | OS 1973; committee p. 2 |
| YM-OS-RP | core | `os_reflection_positivity` | OS 1973; JW §3 |
| YM-OS-SYMMETRY | core | `os_symmetry` (antisymmetric in Fermi arguments) | OS 1973 |
| YM-OS-CLUSTER | core | `os_cluster` (unique vacuum) | OS 1973; JW §3 |
| YM-CONTINUUM | core | `spacing == 0 and continuum_limit == lattice_independent` | JW §6 lattice paragraph; committee p. 2 |
| YM-OBS-GAUGE-INVARIANT | core | Wilson loops or local gauge-invariant fields | JW §4; Wilson 1974 |
| YM-OBS-LOCAL-CURVATURE | core | local fields ~ gauge-invariant polynomials in F | JW §4 and footnote 1 |
| YM-NONTRIVIAL | core | `connected_4pt == nonzero` (non-Gaussian) | JW §4: non-trivial |
| YM-SHORT-DISTANCE | core | `short_distance == asymptotic_freedom` | JW §4; Gross–Wilczek, Politzer 1973 |
| QCD-FERMIONS | qcd | `fermions == quarks_fundamental` | committee p. 1; JW §3; Osterwalder–Seiler 1978 |
| QCD-GROUP-SU3 | qcd | SU(3) covered | committee p. 1 |
| OUT-MASS-GAP | out of claim | `mass_gap > 0` | JW §4; committee p. 2 |
| OUT-CONFINEMENT | out of claim | `confinement == area_law` | committee p. 2 |

Douglas's 2026 review (Nat. Rev. Phys. 8, 86–97), to which the committee points, was not accessible here. It is
cited as the committee's pointer, with `read: false`, and no obligation rests on it.

The **anchoring rule** is part of the frozen file: the audit translates the claimant's definitions into this
vocabulary, with the Lean text quoted, and reads definitions by their bodies, never by their names. The witness
catalogue is frozen too.

### Trivial witnesses

| Witness | Kind | Excluded by (YM claim) |
|---|---|---|
| zero_theory | trivial | YM-NONTRIVIAL, YM-SHORT-DISTANCE |
| free_scalar_4d | gaussian | group, gauge-invariant observables, local fields, non-triviality, short distance |
| free_nonabelian_gaussian_4d (YM at zero coupling) | gaussian | YM-NONTRIVIAL, YM-SHORT-DISTANCE |
| maxwell_u1_4d | abelian | group (both), non-triviality, short distance |
| ym_2d | lower dimension | dimension, local fields, short distance |
| ym_3d (hypothetical) | lower dimension | dimension, short distance |
| ym_torus_4d | finite volume | infinite volume, Euclidean invariance, cluster |
| lattice_ym_4d (strong coupling) | lattice only | Euclidean invariance, continuum, short distance |
| lattice_qcd_4d | lattice only | group coverage, Euclidean invariance, continuum, short distance |
| subsequential_limit_4d | weak limit | YM-CONTINUUM only |

The checklist excludes every witness, for the YM and the QCD claims. Two findings for the later audit:

- **Load-bearing clauses.** Only the lattice-independent continuum limit is a single barrier (against a limit point
  along a subsequence). Asymptotic freedom is the hardest clause to state in Lean. Without it, non-triviality is the
  only barrier against the zero theory and against Yang–Mills at zero coupling, and the dimension the only barrier
  against three-dimensional Yang–Mills. These are the clauses to look for first.
- **Scenarios.** A statement that says only "an OS theory on R⁴ with a compact simple group" is
  VACUOUS_RELATIVE_TO_INTENT: Yang–Mills at zero coupling satisfies it. With non-triviality stated only in prose,
  the outcome is POSSIBLY_VACUOUS (the zero theory and the zero-coupling theory are undetermined, because their group
  label is free).

Report: [preregistration_report.json](../../../examples/yang-mills-preregistration/preregistration_report.json).
Regenerate with `python scripts/cases/ym_preregistration_report.py`.

## 3. Rehearsal: openai/math family 215, the O(3) continuum limit

Sources pinned at openai/math commit `4eaee87548250b2682affda7d05d947c05554bae`: the paper
(`massive-continuum-o3.pdf`, SHA-256 `e75bfb35…27b2`), `CONTENTS.md`, `lean/docs/215.md`,
`lean/ComparatorChallenges/ClassicalON.{lean,json}` (vendored, Apache-2.0) and the solution's `Main.lean` and
`Model.lean`. The obligations are the paper's own claims (Theorem 1.1, Theorem 1.2, Corollary 1.3), in
[a checklist with the same schema](../../../examples/o3-continuum-rehearsal/o3_continuum_claim.v1.json).

The family's only Lean statement, `OAI.ClassicalON.main : ExponentialDecay`, says: for every n ≥ 3 and β > 0 there
are A and m > 0 such that, on every finite subgraph of ℤ² with edge strengths in [0, β], the spin correlation is
between 0 and A·exp(−m·|x − y|). Transcribed into the vocabulary (n = 3 instance, each fact quoting its Lean line)
and decided obligation by obligation:

| Obligation (paper) | Coverage | Why |
|---|---|---|
| O3-FIELD | COVERED | unit spins in `EuclideanSpace ℝ (Fin n)`, n ≥ 3 (stronger: every n) |
| O3-DIM2 | COVERED | `Site := ℤ × ℤ` |
| O3-INFINITE-VOLUME | OBJECT_DIFFERS | `vertices : Finset Site`; uniform over finite graphs, no infinite-volume object |
| O3-CONTINUUM | OBJECT_DIFFERS | unit lattice, no rescaled field, no β → ∞ limit |
| O3-OS-REGULARITY, -EUCLIDEAN, -RP, -SYMMETRY, -CLUSTER | NOT_ADDRESSED | no Schwinger function is defined |
| O3-INTERNAL-SYMMETRY | NOT_ADDRESSED | invariant by construction, not asserted |
| O3-NONTRIVIAL | NOT_ADDRESSED | no four-point function |
| O3-UNIQUE-VACUUM | NOT_ADDRESSED | no reconstruction |
| O3-MASS-GAP | NOT_ADDRESSED | lattice decay at fixed β is not the continuum gap |
| LAT-DECAY (companion paper) | COVERED | matches its abstract |

- **Probe of the paper's claim:** EXCLUDES_ALL_CATALOGUED. The free massive Gaussian vector field, for example,
  satisfies the OS axioms, a unique vacuum and a gap; only the nonzero connected four-point function (and the field)
  excludes it.
- **Probe of the part the Lean statement covers** (O3-FIELD and O3-DIM2): VACUOUS_RELATIVE_TO_INTENT. The lattice
  O(3) model on a finite graph at high temperature, a periodic lattice torus, and a continuum limit point along a
  subsequence all satisfy it. The Lean theorem is a real result about the lattice model at every temperature; it
  cannot certify the continuum theory.
- **Exclusion lint** on `ClassicalON.lean`: POSSIBLY_VACUOUS_RELATIVE_TO_INTENT. No marker of any OS axiom,
  non-triviality, vacuum or gap. Counter-markers `Finset` (lines 17–18), `ℤ × ℤ` (line 11) and `siteDistance`
  point at the finite lattice. Only the Gaussian field (excluded by the O(3) field markers) and the 3D lattice model
  (excluded by `ℤ × ℤ`) are addressed in the text.

Family coverage: of the four papers in family 215 (continuum limit, isolated particle pole, exact O(4) mass
asymptotics, sharp O(4) mass bounds) and the exponential-decay paper, only the last has a Comparator statement.
`lean/docs/215.md` states that the infinite-volume limit and the O(4) spectral-gap claim are not included. The
scope note is accurate; the gap is between the family headline in `CONTENTS.md` ("constructs the canonical
continuum limit … with a positive mass gap", with a Lean link) and what the Lean statement covers.

Kernel check: NOT RUN (Comparator needs landrun on Linux and a full openai/math build). Nothing above depends on it.

Report: [rehearsal_report.json](../../../examples/o3-continuum-rehearsal/rehearsal_report.json). Regenerate with
`python scripts/cases/o3_rehearsal_report.py`.

## 4. What happens when the Yang–Mills statement is released

1. Pin it; move the record to STATEMENT_PUBLIC.
2. Run `trivial_witness.lint_exclusions` with `ym4-existence` v1.0.0 on the main theorem. Every witness with
   NO_EXCLUDING_CLAUSE_FOUND goes to a human first.
3. Transcribe each definition the theorem uses into the vocabulary, quoting the Lean, and run
   `preregistration.coverage`. Probe the COVERED clauses with `trivial_witness.probe`.
4. Run the ADR-070 junk-value lint on the same closure.
5. Record the outcome and move to STATEMENT_AUDITED, whatever it is.

If the statement needs a feature the vocabulary lacks, that is recorded as a finding, and a v1.1.0 checklist with
a new lock may add it. Version 1.0.0 stays as frozen.
